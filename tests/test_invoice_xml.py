"""Tests for Invoice/Boleta XML structure — XPath assertions."""

from lxml import etree
import pytest

from xfep.models import Boleta, Company, Invoice
from xfep.xml import XmlBuilder
from xfep.xml.namespaces import NS_CBC, NS_CAC, NS_EXT, NS_INVOICE

NS = {
    "inv": NS_INVOICE,
    "cbc": NS_CBC,
    "cac": NS_CAC,
    "ext": NS_EXT,
}


def _parse(builder: XmlBuilder, doc, company: Company) -> etree._Element:
    xml_bytes = builder.build(doc, company)
    return etree.fromstring(xml_bytes)


class TestInvoiceHeader:
    """REQ-5: Document header fields."""

    def test_ubl_version(self, builder: XmlBuilder, invoice: Invoice, company: Company):
        root = _parse(builder, invoice, company)
        version = root.find("cbc:UBLVersionID", NS)
        assert version is not None
        assert version.text == "2.1"

    def test_customization_id(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        cust = root.find("cbc:CustomizationID", NS)
        assert cust is not None
        assert cust.text == "2.0"

    def test_document_id(self, builder: XmlBuilder, invoice: Invoice, company: Company):
        root = _parse(builder, invoice, company)
        doc_id = root.find("cbc:ID", NS)
        assert doc_id is not None
        assert doc_id.text == "F001-1"

    def test_issue_date(self, builder: XmlBuilder, invoice: Invoice, company: Company):
        root = _parse(builder, invoice, company)
        issue_date = root.find("cbc:IssueDate", NS)
        assert issue_date is not None
        assert issue_date.text == "2026-01-15"

    def test_invoice_type_code(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        type_code = root.find("cbc:InvoiceTypeCode", NS)
        assert type_code is not None
        assert type_code.text == "01"  # Factura
        assert type_code.get("listID") == "0101"

    def test_currency(self, builder: XmlBuilder, invoice: Invoice, company: Company):
        root = _parse(builder, invoice, company)
        currency = root.find("cbc:DocumentCurrencyCode", NS)
        assert currency is not None
        assert currency.text == "PEN"

    def test_boleta_type_code(
        self, builder: XmlBuilder, boleta: Boleta, company: Company
    ):
        root = _parse(builder, boleta, company)
        type_code = root.find("cbc:InvoiceTypeCode", NS)
        assert type_code is not None
        assert type_code.text == "03"  # Boleta


class TestUBLExtensions:
    """REQ-4: Signature placeholder."""

    def test_ubl_extensions_exist(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        ext = root.find("ext:UBLExtensions/ext:UBLExtension", NS)
        assert ext is not None


class TestParties:
    """REQ-6: Supplier and customer party mapping."""

    def test_supplier_ruc(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        supplier_id = root.find(
            "cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID", NS
        )
        assert supplier_id is not None
        assert supplier_id.text == "20123456789"
        assert supplier_id.get("schemeID") == "6"

    def test_supplier_name(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        name = root.find(
            "cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName",
            NS,
        )
        assert name is not None
        assert name.text == "EMPRESA TEST S.A.C."

    def test_customer_id(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        customer_id = root.find(
            "cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID", NS
        )
        assert customer_id is not None
        assert customer_id.text == "20987654321"

    def test_customer_name(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        name = root.find(
            "cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName",
            NS,
        )
        assert name is not None
        assert name.text == "CLIENTE PRUEBA S.R.L."


class TestInvoiceLines:
    """REQ-7: InvoiceLine count and structure."""

    def test_line_count(self, builder: XmlBuilder, invoice: Invoice, company: Company):
        root = _parse(builder, invoice, company)
        lines = root.findall("cac:InvoiceLine", NS)
        assert len(lines) == 2

    def test_line_ids_sequential(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        lines = root.findall("cac:InvoiceLine", NS)
        ids = [line.find("cbc:ID", NS).text for line in lines]
        assert ids == ["1", "2"]

    def test_line_has_quantity(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        qty = root.find("cac:InvoiceLine/cbc:InvoicedQuantity", NS)
        assert qty is not None
        assert qty.get("unitCode") == "NIU"

    def test_line_has_extension_amount(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        amount = root.find("cac:InvoiceLine/cbc:LineExtensionAmount", NS)
        assert amount is not None
        assert amount.get("currencyID") == "PEN"


class TestTaxSubtotals:
    """REQ-8: Tax subtotals grouped by scheme."""

    def test_tax_total_exists(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        tax_total = root.find("cac:TaxTotal", NS)
        assert tax_total is not None

    def test_igv_scheme_present(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        scheme_ids = root.findall(
            "cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID", NS
        )
        ids = [s.text for s in scheme_ids]
        assert "1000" in ids  # IGV


class TestMonetaryTotals:
    """REQ-9: LegalMonetaryTotal elements."""

    def test_line_extension_amount(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        lea = root.find("cac:LegalMonetaryTotal/cbc:LineExtensionAmount", NS)
        assert lea is not None

    def test_tax_inclusive_amount(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        tia = root.find("cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount", NS)
        assert tia is not None

    def test_payable_amount(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        pa = root.find("cac:LegalMonetaryTotal/cbc:PayableAmount", NS)
        assert pa is not None

    def test_amounts_have_two_decimals(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        root = _parse(builder, invoice, company)
        pa = root.find("cac:LegalMonetaryTotal/cbc:PayableAmount", NS)
        assert pa is not None
        # Must have exactly 2 decimal places
        assert "." in pa.text
        _, decimals = pa.text.split(".")
        assert len(decimals) == 2
