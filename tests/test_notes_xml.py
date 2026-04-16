"""Tests for CreditNote and DebitNote XML structure."""

from lxml import etree

from xfep.models import Company, CreditNote, DebitNote
from xfep.xml import XmlBuilder
from xfep.xml.namespaces import NS_CBC, NS_CAC, NS_CREDIT_NOTE, NS_DEBIT_NOTE

NS_CN = {
    "cn": NS_CREDIT_NOTE,
    "cbc": NS_CBC,
    "cac": NS_CAC,
}

NS_DN = {
    "dn": NS_DEBIT_NOTE,
    "cbc": NS_CBC,
    "cac": NS_CAC,
}


def _parse(builder: XmlBuilder, doc, company: Company) -> etree._Element:
    xml_bytes = builder.build(doc, company)
    return etree.fromstring(xml_bytes)


class TestCreditNoteStructure:
    """REQ-10: CreditNote-specific elements."""

    def test_root_is_credit_note(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        root = _parse(builder, credit_note, company)
        assert root.tag == f"{{{NS_CREDIT_NOTE}}}CreditNote"

    def test_discrepancy_response(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        root = _parse(builder, credit_note, company)
        response_code = root.find("cac:DiscrepancyResponse/cbc:ResponseCode", NS_CN)
        assert response_code is not None
        assert response_code.text == "01"  # ANULACION

    def test_discrepancy_reference_id(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        root = _parse(builder, credit_note, company)
        ref_id = root.find("cac:DiscrepancyResponse/cbc:ReferenceID", NS_CN)
        assert ref_id is not None
        assert ref_id.text == "F001-123"

    def test_billing_reference(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        root = _parse(builder, credit_note, company)
        billing_ref = root.find(
            "cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID", NS_CN
        )
        assert billing_ref is not None
        assert billing_ref.text == "F001-123"

    def test_billing_reference_type(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        root = _parse(builder, credit_note, company)
        doc_type = root.find(
            "cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode",
            NS_CN,
        )
        assert doc_type is not None
        assert doc_type.text == "01"  # FACTURA

    def test_credit_note_lines(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        root = _parse(builder, credit_note, company)
        lines = root.findall("cac:CreditNoteLine", NS_CN)
        assert len(lines) == 2

    def test_credit_note_line_has_credited_quantity(
        self, builder: XmlBuilder, credit_note: CreditNote, company: Company
    ):
        root = _parse(builder, credit_note, company)
        qty = root.find("cac:CreditNoteLine/cbc:CreditedQuantity", NS_CN)
        assert qty is not None


class TestDebitNoteStructure:
    """REQ-10: DebitNote-specific elements."""

    def test_root_is_debit_note(
        self, builder: XmlBuilder, debit_note: DebitNote, company: Company
    ):
        root = _parse(builder, debit_note, company)
        assert root.tag == f"{{{NS_DEBIT_NOTE}}}DebitNote"

    def test_discrepancy_response(
        self, builder: XmlBuilder, debit_note: DebitNote, company: Company
    ):
        root = _parse(builder, debit_note, company)
        response_code = root.find("cac:DiscrepancyResponse/cbc:ResponseCode", NS_DN)
        assert response_code is not None
        assert response_code.text == "01"  # INTERESES_MORA

    def test_billing_reference(
        self, builder: XmlBuilder, debit_note: DebitNote, company: Company
    ):
        root = _parse(builder, debit_note, company)
        billing_ref = root.find(
            "cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID", NS_DN
        )
        assert billing_ref is not None
        assert billing_ref.text == "F001-123"

    def test_debit_note_lines(
        self, builder: XmlBuilder, debit_note: DebitNote, company: Company
    ):
        root = _parse(builder, debit_note, company)
        lines = root.findall("cac:DebitNoteLine", NS_DN)
        assert len(lines) == 2

    def test_requested_monetary_total(
        self, builder: XmlBuilder, debit_note: DebitNote, company: Company
    ):
        root = _parse(builder, debit_note, company)
        rmt = root.find("cac:RequestedMonetaryTotal", NS_DN)
        assert rmt is not None

    def test_debit_note_line_has_debited_quantity(
        self, builder: XmlBuilder, debit_note: DebitNote, company: Company
    ):
        root = _parse(builder, debit_note, company)
        qty = root.find("cac:DebitNoteLine/cbc:DebitedQuantity", NS_DN)
        assert qty is not None
