"""Shared test fixtures for xfep-xml tests."""

from datetime import date
from decimal import Decimal

import pytest

from xfep.models import (
    Boleta,
    Client,
    Company,
    CreditNote,
    DebitNote,
    Detalle,
    DailySummary,
    DispatchGuide,
    Invoice,
    VoidedDocument,
)
from xfep.models.detail import VoidedDetail
from xfep.models.dispatch import Conductor, DetalleGRE, DireccionGRE, Vehiculo
from xfep.models.enums import (
    Moneda,
    MotivoNC,
    MotivoND,
    TipoAfectacionIGV,
    TipoDocIdentidad,
    TipoDocumento,
    TipoOperacion,
    UnidadMedida,
)
from xfep.xml import XmlBuilder


@pytest.fixture
def builder() -> XmlBuilder:
    return XmlBuilder()


@pytest.fixture
def company() -> Company:
    return Company(
        ruc="20123456789",
        razon_social="EMPRESA TEST S.A.C.",
        nombre_comercial="TEST CORP",
        direccion="Av. Test 123, Lima",
        ubigeo="150101",
    )


@pytest.fixture
def client_ruc() -> Client:
    return Client(
        tipo_documento=TipoDocIdentidad.RUC,
        numero_documento="20987654321",
        razon_social="CLIENTE PRUEBA S.R.L.",
        direccion="Jr. Cliente 456, Lima",
    )


@pytest.fixture
def sample_detalles() -> list[Detalle]:
    return [
        Detalle(
            codigo="PROD001",
            descripcion="Producto de prueba 1",
            unidad=UnidadMedida.UNIDAD,
            cantidad=Decimal("2"),
            mto_precio_unitario=Decimal("118.00"),
            porcentaje_igv=Decimal("18"),
            tip_afe_igv=TipoAfectacionIGV.GRAVADO,
        ),
        Detalle(
            codigo="SERV001",
            descripcion="Servicio de prueba 2",
            unidad=UnidadMedida.SERVICIO,
            cantidad=Decimal("1"),
            mto_precio_unitario=Decimal("59.00"),
            porcentaje_igv=Decimal("18"),
            tip_afe_igv=TipoAfectacionIGV.GRAVADO,
        ),
    ]


@pytest.fixture
def invoice(client_ruc: Client, sample_detalles: list[Detalle]) -> Invoice:
    return Invoice(
        company_id=1,
        branch_id=1,
        serie="F001",
        fecha_emision=date(2026, 1, 15),
        moneda=Moneda.PEN,
        tipo_operacion=TipoOperacion.VENTA_INTERNA,
        client=client_ruc,
        detalles=sample_detalles,
    )


@pytest.fixture
def boleta(sample_detalles: list[Detalle]) -> Boleta:
    return Boleta(
        company_id=1,
        branch_id=1,
        serie="B001",
        fecha_emision=date(2026, 1, 15),
        moneda=Moneda.PEN,
        tipo_operacion=TipoOperacion.VENTA_INTERNA,
        client=Client(
            tipo_documento=TipoDocIdentidad.DNI,
            numero_documento="12345678",
            razon_social="JUAN PEREZ",
        ),
        detalles=sample_detalles,
    )


@pytest.fixture
def credit_note(client_ruc: Client, sample_detalles: list[Detalle]) -> CreditNote:
    return CreditNote(
        company_id=1,
        branch_id=1,
        serie="FF01",
        fecha_emision=date(2026, 1, 20),
        moneda=Moneda.PEN,
        tipo_operacion=TipoOperacion.VENTA_INTERNA,
        client=client_ruc,
        detalles=sample_detalles,
        tipo_doc_afectado=TipoDocumento.FACTURA,
        num_doc_afectado="F001-123",
        cod_motivo=MotivoNC.ANULACION,
        des_motivo="Anulación de la operación",
    )


@pytest.fixture
def debit_note(client_ruc: Client, sample_detalles: list[Detalle]) -> DebitNote:
    return DebitNote(
        company_id=1,
        branch_id=1,
        serie="FD01",
        fecha_emision=date(2026, 1, 20),
        moneda=Moneda.PEN,
        tipo_operacion=TipoOperacion.VENTA_INTERNA,
        client=client_ruc,
        detalles=sample_detalles,
        tipo_doc_afectado=TipoDocumento.FACTURA,
        num_doc_afectado="F001-123",
        cod_motivo=MotivoND.INTERESES_MORA,
        des_motivo="Intereses por mora",
    )


@pytest.fixture
def voided_document() -> VoidedDocument:
    return VoidedDocument(
        company_id=1,
        branch_id=1,
        fecha_referencia=date(2026, 1, 15),
        motivo_baja="Error en emisión",
        detalles=[
            VoidedDetail(
                tipo_documento=TipoDocumento.FACTURA,
                serie="F001",
                correlativo="100",
                motivo_especifico="Error en RUC del cliente",
            ),
            VoidedDetail(
                tipo_documento=TipoDocumento.FACTURA,
                serie="F001",
                correlativo="101",
                motivo_especifico="Documento duplicado",
            ),
        ],
    )


@pytest.fixture
def daily_summary() -> DailySummary:
    return DailySummary(
        company_id=1,
        branch_id=1,
        fecha_resumen=date(2026, 1, 15),
    )


@pytest.fixture
def dispatch_guide(client_ruc: Client) -> DispatchGuide:
    return DispatchGuide(
        company_id=1,
        branch_id=1,
        serie="T001",
        fecha_emision=date(2026, 1, 15),
        motivo_traslado="01",
        modalidad_transporte="02",
        peso_total=Decimal("150.5"),
        unidad_peso=UnidadMedida.KILOGRAMO,
        punto_partida=DireccionGRE(
            ubigeo="150101",
            direccion="Av. Origen 100, Lima",
        ),
        punto_llegada=DireccionGRE(
            ubigeo="150201",
            direccion="Av. Destino 200, Callao",
        ),
        destinatario=client_ruc,
        transportista=Client(
            tipo_documento=TipoDocIdentidad.RUC,
            numero_documento="20111222333",
            razon_social="TRANSPORTES XYZ S.A.",
        ),
        vehiculo=Vehiculo(placa="ABC-123"),
        conductor=Conductor(
            tipo_documento="1",
            numero_documento="44556677",
            nombres="Pedro",
            apellidos="Lopez Garcia",
            licencia="Q44556677",
        ),
        detalles=[
            DetalleGRE(
                codigo="PROD001",
                descripcion="Producto A",
                unidad=UnidadMedida.UNIDAD,
                cantidad=Decimal("10"),
            ),
            DetalleGRE(
                descripcion="Producto B",
                unidad=UnidadMedida.KILOGRAMO,
                cantidad=Decimal("50.5"),
            ),
            DetalleGRE(
                descripcion="Producto C",
                unidad=UnidadMedida.CAJA,
                cantidad=Decimal("5"),
            ),
        ],
    )
