# xfep-xml

Generación de XML UBL 2.1 para Facturación Electrónica Perú (SUNAT).

Parte del [ecosistema XFEP](https://github.com/xpertik). Depende de [`xfep-models`](https://github.com/xpertik/xfep-models).

## Instalación

```bash
pip install xfep-xml
```

## Uso

```python
from xfep.xml import XmlBuilder
from xfep.models import Invoice, Client, Detalle, Company

company = Company(
    ruc="20123456789",
    razon_social="MI EMPRESA S.A.C.",
    nombre_comercial="MI EMPRESA",
    direccion="Av. Principal 123",
    ubigeo="150101",
    distrito="Lima",
    provincia="Lima",
    departamento="Lima",
    usuario_sol="MODDATOS",
    clave_sol="MODDATOS",
)

invoice = Invoice(
    company_id=1,
    branch_id=1,
    serie="F001",
    fecha_emision="2026-02-10",
    moneda="PEN",
    tipo_operacion="0101",
    forma_pago_tipo="Contado",
    client=Client(
        tipo_documento="6",
        numero_documento="20987654321",
        razon_social="CLIENTE S.A.C.",
    ),
    detalles=[
        Detalle(
            codigo="PROD001",
            descripcion="Laptop HP",
            unidad="NIU",
            cantidad=1,
            mto_precio_unitario=2360,
            porcentaje_igv=18,
            tip_afe_igv="10",
        )
    ],
)

builder = XmlBuilder()
xml_bytes = builder.build(invoice, company)
# xml_bytes es UTF-8 encoded, listo para firmar con xfep-sign
```

## Documentos soportados

| Documento | Modelo | Template | Root XML |
|-----------|--------|----------|----------|
| Factura | `Invoice` | `invoice.xml.j2` | `<Invoice>` |
| Boleta | `Boleta` | `invoice.xml.j2` (compartido) | `<Invoice>` |
| Nota de Crédito | `CreditNote` | `credit_note.xml.j2` | `<CreditNote>` |
| Nota de Débito | `DebitNote` | `debit_note.xml.j2` | `<DebitNote>` |
| Comunicación de Baja | `VoidedDocument` | `voided.xml.j2` | `<VoidedDocuments>` |
| Resumen Diario | `DailySummary` | `summary.xml.j2` | `<SummaryDocuments>` |
| Guía de Remisión | `DispatchGuide` | `dispatch.xml.j2` | `<DespatchAdvice>` |

## API

### `XmlBuilder`

```python
from xfep.xml import XmlBuilder

builder = XmlBuilder()

# Generar XML para cualquier documento SUNAT
xml_bytes: bytes = builder.build(document, company)
```

**`build(document, company) -> bytes`**
- `document` — Instancia de cualquier modelo SUNAT (`Invoice`, `Boleta`, `CreditNote`, etc.)
- `company` — Instancia de `Company` (datos del emisor)
- Retorna XML como `bytes` (UTF-8 con declaración XML)
- Lanza `ValueError` si el tipo de documento no es soportado

## Características

- **UBL 2.1 compliant** — Namespaces correctos (cac, cbc, ext, ds, sac)
- **Declaración XML** — `<?xml version="1.0" encoding="UTF-8"?>`
- **Placeholder de firma** — `ext:UBLExtensions` con slot vacío para `ds:Signature` (firma real en xfep-sign)
- **Cálculo automático** — Subtotales, IGV, totales por línea y documento
- **Agrupación de impuestos** — TaxSubtotal agrupado por tipo (IGV=1000, ISC=2000, IVAP=1016, ICBPER=7152)
- **Precisión decimal** — Montos a 2 decimales, cantidades con precisión completa
- **Validación lxml** — XML generado es parseado con lxml para garantizar well-formedness

## Namespaces UBL 2.1

| Prefijo | URI |
|---------|-----|
| (default) | `urn:oasis:names:specification:ubl:schema:xsd:Invoice-2` |
| `cac` | `urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2` |
| `cbc` | `urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2` |
| `ext` | `urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2` |
| `ds` | `http://www.w3.org/2000/09/xmldsig#` |
| `sac` | `urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1` |

## Desarrollo

```bash
git clone https://github.com/xpertik/xfep-xml.git
cd xfep-xml

python3.13 -m venv .venv
source .venv/bin/activate

# Instalar xfep-models desde local (desarrollo)
pip install -e "../xfep-models"
pip install -e ".[dev]"

pytest -v
```

## Stack

- **Python** >= 3.13
- **Jinja2** >= 3.1 (templates XML)
- **lxml** >= 5.0 (parsing/validación)
- **xfep-models** >= 0.1.0
- **Build**: Hatchling
- **Tests**: pytest

## Parte del ecosistema XFEP

| Paquete | Estado | Descripción |
|---------|--------|-------------|
| [xfep-models](https://github.com/xpertik/xfep-models) | v0.1.0 | Modelos de datos |
| **xfep-xml** | **v0.1.0** | **Generación de XML UBL 2.1** |
| xfep-sign | pendiente | Firma digital XML |
| xfep-ws | pendiente | Cliente SOAP/REST para SUNAT |
| xfep-pdf | pendiente | Generación de PDF |
| xfep-parser | pendiente | Parseo de respuestas SUNAT |

## Licencia

Apache License 2.0 — ver [LICENSE](LICENSE).
