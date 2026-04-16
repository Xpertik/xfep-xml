"""UBL 2.1 namespace constants for SUNAT electronic invoicing."""

# Common namespaces used across all document types
NS_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NS_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
NS_EXT = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
NS_DS = "http://www.w3.org/2000/09/xmldsig#"
NS_SAC = "urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1"
NS_CCTS = "urn:un:unece:uncefact:documentation:2"
NS_QDT = "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2"
NS_UDT = "urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2"

# Document-type root namespaces
NS_INVOICE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
NS_CREDIT_NOTE = "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"
NS_DEBIT_NOTE = "urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2"
NS_DESPATCH_ADVICE = "urn:oasis:names:specification:ubl:schema:xsd:DespatchAdvice-2"
NS_SUMMARY = "urn:sunat:names:specification:ubl:peru:schema:xsd:SummaryDocuments-1"
NS_VOIDED = "urn:sunat:names:specification:ubl:peru:schema:xsd:VoidedDocuments-1"

NAMESPACES: dict[str, str] = {
    "cbc": NS_CBC,
    "cac": NS_CAC,
    "ext": NS_EXT,
    "ds": NS_DS,
    "sac": NS_SAC,
    "ccts": NS_CCTS,
    "qdt": NS_QDT,
    "udt": NS_UDT,
}
