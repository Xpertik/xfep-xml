"""Tests for XmlBuilder dispatch, well-formedness, and namespace validation."""

from lxml import etree
from pydantic import BaseModel
import pytest

from xfep.models import (
    Boleta,
    Company,
    CreditNote,
    DailySummary,
    DebitNote,
    DispatchGuide,
    Invoice,
    VoidedDocument,
)
from xfep.xml import XmlBuilder


class TestBuilderDispatch:
    """REQ-1: XmlBuilder dispatches to correct template for all 7 model types."""

    def test_invoice_returns_bytes(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        result = builder.build(invoice, company)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_boleta_returns_bytes(
        self, builder: XmlBuilder, boleta: Boleta, company: Company
    ):
        result = builder.build(boleta, company)
        assert isinstance(result, bytes)

    def test_credit_note_returns_bytes(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        result = builder.build(credit_note, company)
        assert isinstance(result, bytes)

    def test_debit_note_returns_bytes(
        self, builder: XmlBuilder, debit_note: DebitNote, company: Company
    ):
        result = builder.build(debit_note, company)
        assert isinstance(result, bytes)

    def test_voided_returns_bytes(
        self, builder: XmlBuilder, voided_document: VoidedDocument, company: Company
    ):
        result = builder.build(voided_document, company)
        assert isinstance(result, bytes)

    def test_daily_summary_returns_bytes(
        self, builder: XmlBuilder, daily_summary: DailySummary, company: Company
    ):
        result = builder.build(daily_summary, company)
        assert isinstance(result, bytes)

    def test_dispatch_returns_bytes(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        result = builder.build(dispatch_guide, company)
        assert isinstance(result, bytes)

    def test_unsupported_type_raises_value_error(
        self, builder: XmlBuilder, company: Company
    ):
        class FakeDoc(BaseModel):
            pass

        with pytest.raises(ValueError, match="Unsupported document type"):
            builder.build(FakeDoc(), company)  # type: ignore[arg-type]


class TestWellFormedness:
    """REQ-2: All generated XML must parse with lxml without errors."""

    def test_invoice_xml_parses(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        xml_bytes = builder.build(invoice, company)
        root = etree.fromstring(xml_bytes)
        assert root is not None

    def test_credit_note_xml_parses(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        xml_bytes = builder.build(credit_note, company)
        root = etree.fromstring(xml_bytes)
        assert root is not None

    def test_voided_xml_parses(
        self, builder: XmlBuilder, voided_document: VoidedDocument, company: Company
    ):
        xml_bytes = builder.build(voided_document, company)
        root = etree.fromstring(xml_bytes)
        assert root is not None

    def test_dispatch_xml_parses(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        xml_bytes = builder.build(dispatch_guide, company)
        root = etree.fromstring(xml_bytes)
        assert root is not None


class TestXmlDeclaration:
    """Output must start with XML declaration."""

    def test_xml_declaration_present(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        xml_bytes = builder.build(invoice, company)
        assert xml_bytes.startswith(b"<?xml version='1.0' encoding='UTF-8'?>")


class TestNamespaces:
    """REQ-3: CPE documents must declare cac, cbc, ext, ds, sac namespaces."""

    def _get_nsmap(self, xml_bytes: bytes) -> dict:
        root = etree.fromstring(xml_bytes)
        return root.nsmap

    def test_invoice_namespaces(
        self, builder: XmlBuilder, invoice: Invoice, company: Company
    ):
        nsmap = self._get_nsmap(builder.build(invoice, company))
        assert "cac" in nsmap
        assert "cbc" in nsmap
        assert "ext" in nsmap
        assert "ds" in nsmap
        assert "sac" in nsmap

    def test_credit_note_namespaces(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        nsmap = self._get_nsmap(builder.build(credit_note, company))
        assert "cac" in nsmap
        assert "cbc" in nsmap
        assert "ext" in nsmap
        assert "ds" in nsmap
        assert "sac" in nsmap

    def test_debit_note_namespaces(
        self, builder: XmlBuilder, debit_note: DebitNote, company: Company
    ):
        nsmap = self._get_nsmap(builder.build(debit_note, company))
        assert "cac" in nsmap
        assert "cbc" in nsmap
        assert "ext" in nsmap
        assert "ds" in nsmap
        assert "sac" in nsmap
