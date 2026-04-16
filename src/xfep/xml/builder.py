"""XmlBuilder — renders xfep-models documents to UBL 2.1 XML bytes."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from lxml import etree

from xfep.models import (
    Boleta,
    CreditNote,
    DailySummary,
    DebitNote,
    DispatchGuide,
    Invoice,
    VoidedDocument,
)
from xfep.models.detail import Detalle
from xfep.models.enums import TipoAfectacionIGV, TipoDocumento

from .utils import fmt_amount, fmt_date, fmt_quantity

# Template file mapping by model type
_TEMPLATE_MAP: dict[type, str] = {
    Invoice: "invoice.xml.j2",
    Boleta: "invoice.xml.j2",
    CreditNote: "credit_note.xml.j2",
    DebitNote: "debit_note.xml.j2",
    VoidedDocument: "voided.xml.j2",
    DailySummary: "summary.xml.j2",
    DispatchGuide: "dispatch.xml.j2",
}

# Tax scheme info by TipoAfectacionIGV
_TAX_INFO: dict[str, dict[str, str]] = {
    "IGV": {
        "scheme_id": "1000",
        "scheme_name": "IGV",
        "scheme_code": "VAT",
        "category_id": "S",
    },
    "IVAP": {
        "scheme_id": "1016",
        "scheme_name": "IVAP",
        "scheme_code": "VAT",
        "category_id": "S",
    },
    "EXO": {
        "scheme_id": "9997",
        "scheme_name": "EXO",
        "scheme_code": "VAT",
        "category_id": "E",
    },
    "INA": {
        "scheme_id": "9998",
        "scheme_name": "INA",
        "scheme_code": "FRE",
        "category_id": "O",
    },
    "GRA": {
        "scheme_id": "9996",
        "scheme_name": "GRA",
        "scheme_code": "FRE",
        "category_id": "Z",
    },
}


def _get_tax_group(tip_afe_igv: TipoAfectacionIGV) -> str:
    """Map TipoAfectacionIGV to tax group key."""
    if tip_afe_igv == TipoAfectacionIGV.GRAVADO:
        return "IGV"
    if tip_afe_igv == TipoAfectacionIGV.GRAVADO_GRATUITO:
        return "GRA"
    if tip_afe_igv == TipoAfectacionIGV.IVAP:
        return "IVAP"
    if tip_afe_igv == TipoAfectacionIGV.EXONERADO:
        return "EXO"
    if tip_afe_igv == TipoAfectacionIGV.INAFECTO:
        return "INA"
    return "IGV"


def _compute_line_amounts(detalles: list[Detalle]) -> list[dict[str, Any]]:
    """Compute per-line amounts for template rendering."""
    results = []
    for det in detalles:
        cantidad = Decimal(str(det.cantidad))

        if det.mto_valor_unitario is not None:
            valor_unitario = Decimal(str(det.mto_valor_unitario))
        else:
            # precio_unitario includes IGV, compute valor_unitario
            precio_unitario = Decimal(str(det.mto_precio_unitario))
            igv_rate = Decimal(str(det.porcentaje_igv)) / Decimal("100")
            valor_unitario = (precio_unitario / (Decimal("1") + igv_rate)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        line_extension = (cantidad * valor_unitario).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        igv_rate = Decimal(str(det.porcentaje_igv)) / Decimal("100")
        igv = (line_extension * igv_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if det.mto_precio_unitario is not None:
            precio_unitario_ref = Decimal(str(det.mto_precio_unitario))
        else:
            precio_unitario_ref = (valor_unitario * (Decimal("1") + igv_rate)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        tax_group = _get_tax_group(det.tip_afe_igv)
        tax_info = _TAX_INFO[tax_group]

        # Price type: 01 = precio con IGV, 02 = valor referencial (gratuito)
        is_free = det.tip_afe_igv == TipoAfectacionIGV.GRAVADO_GRATUITO
        price_type = "02" if is_free else "01"

        results.append(
            {
                "valor_unitario": valor_unitario,
                "precio_unitario": precio_unitario_ref,
                "line_extension": line_extension,
                "igv": igv,
                "percent": Decimal(str(det.porcentaje_igv)),
                "price_type": price_type,
                "tax_category_id": tax_info["category_id"],
                "tax_scheme_id": tax_info["scheme_id"],
                "tax_scheme_name": tax_info["scheme_name"],
                "tax_scheme_code": tax_info["scheme_code"],
                "tax_group": tax_group,
            }
        )
    return results


def _compute_tax_subtotals(
    detalles: list[Detalle], line_amounts: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], Decimal]:
    """Group taxes by scheme and compute subtotals."""
    groups: dict[str, dict[str, Any]] = {}

    for det, la in zip(detalles, line_amounts, strict=True):
        group = la["tax_group"]
        if group not in groups:
            tax_info = _TAX_INFO[group]
            groups[group] = {
                "base": Decimal("0"),
                "amount": Decimal("0"),
                "category_id": tax_info["category_id"],
                "scheme_id": tax_info["scheme_id"],
                "scheme_name": tax_info["scheme_name"],
                "scheme_code": tax_info["scheme_code"],
            }
        groups[group]["base"] += la["line_extension"]
        groups[group]["amount"] += la["igv"]

    subtotals = list(groups.values())
    total_tax = sum((s["amount"] for s in subtotals), Decimal("0"))
    return subtotals, total_tax


class XmlBuilder:
    """Renders xfep-models document instances to UBL 2.1 XML bytes.

    Usage::

        from xfep.xml import XmlBuilder
        from xfep.models import Invoice, Company

        builder = XmlBuilder()
        xml_bytes = builder.build(invoice, company)
    """

    def __init__(self) -> None:
        templates_dir = Path(__file__).parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,
            keep_trailing_newline=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._env.filters["fmt_amount"] = fmt_amount
        self._env.filters["fmt_date"] = fmt_date
        self._env.filters["fmt_quantity"] = fmt_quantity

    def build(
        self,
        document: Invoice | Boleta | CreditNote | DebitNote | VoidedDocument | DailySummary | DispatchGuide,
        company: Any,
        *,
        correlativo: int = 1,
    ) -> bytes:
        """Render document to UBL 2.1 XML bytes.

        Args:
            document: An xfep-models document instance.
            company: A Company instance (emisor).
            correlativo: Sequential number within the serie (default 1).

        Returns:
            UTF-8 encoded XML bytes with XML declaration.

        Raises:
            ValueError: If the document type is not supported.
        """
        doc_type = type(document)
        template_name = _TEMPLATE_MAP.get(doc_type)
        if template_name is None:
            raise ValueError(f"Unsupported document type: {doc_type.__name__}")

        template = self._env.get_template(template_name)
        context = self._build_context(document, company, correlativo)
        xml_str = template.render(**context)

        # Validate well-formedness with lxml
        root = etree.fromstring(xml_str.encode("utf-8"))

        # Return canonical bytes with XML declaration
        return etree.tostring(
            root,
            xml_declaration=True,
            encoding="UTF-8",
            pretty_print=True,
        )

    def _build_context(
        self,
        document: Any,
        company: Any,
        correlativo: int,
    ) -> dict[str, Any]:
        """Build Jinja2 template context from document + company."""
        ctx: dict[str, Any] = {
            "doc": document,
            "company": company,
            "correlativo": correlativo,
        }

        if isinstance(document, (Invoice, Boleta)):
            ctx["tipo_documento"] = (
                TipoDocumento.FACTURA.value
                if isinstance(document, Invoice)
                else TipoDocumento.BOLETA.value
            )
            self._add_cpe_amounts(document, ctx)

        elif isinstance(document, (CreditNote, DebitNote)):
            self._add_cpe_amounts(document, ctx)

        elif isinstance(document, VoidedDocument):
            ctx["voided_id"] = f"RA-{document.fecha_referencia:%Y%m%d}-{correlativo:05d}"
            ctx["issue_date"] = date.today()

        elif isinstance(document, DailySummary):
            ctx["summary_id"] = f"RC-{document.fecha_resumen:%Y%m%d}-{correlativo:05d}"
            ctx["issue_date"] = date.today()

        elif isinstance(document, DispatchGuide):
            pass  # dispatch template uses doc fields directly

        return ctx

    def _add_cpe_amounts(self, document: Any, ctx: dict[str, Any]) -> None:
        """Add computed line amounts, tax subtotals, and totals to context."""
        line_amounts = _compute_line_amounts(document.detalles)
        ctx["line_amounts"] = line_amounts

        tax_subtotals, total_impuestos = _compute_tax_subtotals(
            document.detalles, line_amounts
        )
        ctx["tax_subtotals"] = tax_subtotals
        ctx["total_impuestos"] = total_impuestos

        total_gravada = sum(
            (la["line_extension"] for la in line_amounts), Decimal("0")
        )
        ctx["total_gravada"] = total_gravada
        ctx["mto_imp_venta"] = total_gravada + total_impuestos
