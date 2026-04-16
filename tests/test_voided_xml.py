"""Tests for VoidedDocument, DailySummary, and DispatchGuide XML structure."""

from lxml import etree

from xfep.models import Company, DailySummary, DispatchGuide, VoidedDocument
from xfep.xml import XmlBuilder
from xfep.xml.namespaces import (
    NS_CBC,
    NS_CAC,
    NS_DESPATCH_ADVICE,
    NS_SAC,
    NS_SUMMARY,
    NS_VOIDED,
)

NS_V = {
    "v": NS_VOIDED,
    "cbc": NS_CBC,
    "cac": NS_CAC,
    "sac": NS_SAC,
}

NS_S = {
    "s": NS_SUMMARY,
    "cbc": NS_CBC,
    "cac": NS_CAC,
}

NS_D = {
    "d": NS_DESPATCH_ADVICE,
    "cbc": NS_CBC,
    "cac": NS_CAC,
}


def _parse(builder: XmlBuilder, doc, company: Company) -> etree._Element:
    xml_bytes = builder.build(doc, company)
    return etree.fromstring(xml_bytes)


class TestVoidedDocument:
    """REQ-11: VoidedDocument XML structure."""

    def test_root_is_voided_documents(
        self, builder: XmlBuilder, voided_document: VoidedDocument, company: Company
    ):
        root = _parse(builder, voided_document, company)
        assert root.tag == f"{{{NS_VOIDED}}}VoidedDocuments"

    def test_reference_date(
        self, builder: XmlBuilder, voided_document: VoidedDocument, company: Company
    ):
        root = _parse(builder, voided_document, company)
        ref_date = root.find("cbc:ReferenceDate", NS_V)
        assert ref_date is not None
        assert ref_date.text == "2026-01-15"

    def test_voided_lines_count(
        self, builder: XmlBuilder, voided_document: VoidedDocument, company: Company
    ):
        root = _parse(builder, voided_document, company)
        lines = root.findall("sac:VoidedDocumentsLine", NS_V)
        assert len(lines) == 2

    def test_voided_line_has_document_type(
        self, builder: XmlBuilder, voided_document: VoidedDocument, company: Company
    ):
        root = _parse(builder, voided_document, company)
        doc_type = root.find(
            "sac:VoidedDocumentsLine/cbc:DocumentTypeCode", NS_V
        )
        assert doc_type is not None
        assert doc_type.text == "01"  # FACTURA

    def test_voided_line_has_serie(
        self, builder: XmlBuilder, voided_document: VoidedDocument, company: Company
    ):
        root = _parse(builder, voided_document, company)
        serie = root.find(
            "sac:VoidedDocumentsLine/sac:DocumentSerialID", NS_V
        )
        assert serie is not None
        assert serie.text == "F001"

    def test_voided_line_has_reason(
        self, builder: XmlBuilder, voided_document: VoidedDocument, company: Company
    ):
        root = _parse(builder, voided_document, company)
        reason = root.find(
            "sac:VoidedDocumentsLine/sac:VoidReasonDescription", NS_V
        )
        assert reason is not None
        assert reason.text == "Error en RUC del cliente"


class TestDailySummary:
    """REQ-12: DailySummary XML structure."""

    def test_root_is_summary_documents(
        self, builder: XmlBuilder, daily_summary: DailySummary, company: Company
    ):
        root = _parse(builder, daily_summary, company)
        assert root.tag == f"{{{NS_SUMMARY}}}SummaryDocuments"

    def test_reference_date(
        self, builder: XmlBuilder, daily_summary: DailySummary, company: Company
    ):
        root = _parse(builder, daily_summary, company)
        ref_date = root.find("cbc:ReferenceDate", NS_S)
        assert ref_date is not None
        assert ref_date.text == "2026-01-15"

    def test_issue_date_exists(
        self, builder: XmlBuilder, daily_summary: DailySummary, company: Company
    ):
        root = _parse(builder, daily_summary, company)
        issue_date = root.find("cbc:IssueDate", NS_S)
        assert issue_date is not None

    def test_supplier_party(
        self, builder: XmlBuilder, daily_summary: DailySummary, company: Company
    ):
        root = _parse(builder, daily_summary, company)
        supplier = root.find(
            "cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID",
            NS_S,
        )
        assert supplier is not None
        assert supplier.text == "20123456789"


class TestDispatchGuide:
    """REQ-13: DispatchGuide (DespatchAdvice) XML structure."""

    def test_root_is_despatch_advice(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        root = _parse(builder, dispatch_guide, company)
        assert root.tag == f"{{{NS_DESPATCH_ADVICE}}}DespatchAdvice"

    def test_despatch_line_count(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        root = _parse(builder, dispatch_guide, company)
        lines = root.findall("cac:DespatchLine", NS_D)
        assert len(lines) == 3

    def test_shipment_exists(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        root = _parse(builder, dispatch_guide, company)
        shipment = root.find("cac:Shipment", NS_D)
        assert shipment is not None

    def test_origin_address(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        root = _parse(builder, dispatch_guide, company)
        origin = root.find("cac:Shipment/cac:OriginAddress/cbc:ID", NS_D)
        assert origin is not None
        assert origin.text == "150101"

    def test_delivery_address(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        root = _parse(builder, dispatch_guide, company)
        delivery = root.find(
            "cac:Shipment/cac:Delivery/cac:DeliveryAddress/cbc:ID", NS_D
        )
        assert delivery is not None
        assert delivery.text == "150201"

    def test_driver_info(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        root = _parse(builder, dispatch_guide, company)
        driver = root.find(
            "cac:Shipment/cac:ShipmentStage/cac:DriverPerson/cbc:FirstName", NS_D
        )
        assert driver is not None
        assert driver.text == "Pedro"

    def test_vehicle_plate(
        self, builder: XmlBuilder, dispatch_guide: DispatchGuide, company: Company
    ):
        root = _parse(builder, dispatch_guide, company)
        plate = root.find(
            "cac:Shipment/cac:ShipmentStage/cac:TransportMeans/cac:RoadTransport/cbc:LicensePlateID",
            NS_D,
        )
        assert plate is not None
        assert plate.text == "ABC-123"
