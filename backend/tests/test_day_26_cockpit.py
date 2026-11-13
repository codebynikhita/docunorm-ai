from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.zugferd_extractor import zugferd_extractor_service
from app.services.zugferd_reconciliation import zugferd_visual_reconciler
from app.services.zugferd_samples import (
    SAMPLE_DISCREPANT_TAMPERED,
    SAMPLE_FACTURX_COMFORT,
    get_sample_profile_by_id,
    get_sample_profiles,
)


def test_sample_profiles_catalog():
    """Verifies retrieval of authentic statutory e-invoice sample profiles."""
    profiles = get_sample_profiles()
    assert len(profiles) == 5

    ids = [p.profile_id for p in profiles]
    assert "facturx-comfort" in ids
    assert "xrechnung-ubl" in ids
    assert "xrechnung-cii" in ids
    assert "reverse-charge-13b" in ids
    assert "discrepant-tampered" in ids

    # Test single retrieval
    comfort = get_sample_profile_by_id("facturx-comfort")
    assert comfort is not None
    assert comfort.name.startswith("Factur-X")
    assert "DE-84920" in comfort.raw_xml

    not_found = get_sample_profile_by_id("non-existent")
    assert not_found is None


def test_visual_xml_reconciler_perfect_match():
    """Verifies 100% reconciliation when visual text matches all core fields."""
    extraction = zugferd_extractor_service.parse_xml_invoice(
        raw_xml=SAMPLE_FACTURX_COMFORT,
        filename="facturx.xml",
    )

    visual_text = """
    DocuNorm Sovereign Systems AG
    Taunusanlage 8 · 60311 Frankfurt am Main
    USt-IdNr: DE329184910
    Rechnungsnummer: RE-2026-DE-84920
    Datum: 08.11.2026
    Käufer: Deutsche Bundesbank / Federal Procurement Dept
    Leitweg-ID: 04011000-12345-03
    Nettobetrag: 32.500,00 EUR
    USt 19%: 6.175,00 EUR
    Gesamtbetrag Brutto: 38.675,00 EUR
    IBAN: DE89370400440532013000
    """

    report = zugferd_visual_reconciler.reconcile(extraction, visual_text=visual_text)
    assert report.has_visual_layer is True
    assert report.is_reconciled is True
    assert report.discrepancy_count == 0
    assert report.reconciliation_score_percent == 100.0
    assert "100%" in report.summary_de


def test_visual_xml_reconciler_detects_tampered_total_and_missing_vat():
    """Verifies discrepancy detection when invoice amount or seller VAT ID differs."""
    extraction = zugferd_extractor_service.parse_xml_invoice(
        raw_xml=SAMPLE_DISCREPANT_TAMPERED,
        filename="tampered.xml",
    )

    # Visual text has 10.000,00 EUR, but XML claims 13.900,00 EUR
    visual_text = """
    Dubious Vendor Solutions Ltd
    Rechnung: INV-TAMPERED-991
    Gesamtbetrag: 10.000,00 EUR
    IBAN: DE89370400440532013000
    """

    report = zugferd_visual_reconciler.reconcile(extraction, visual_text=visual_text)
    assert report.has_visual_layer is True
    assert report.is_reconciled is False
    assert report.discrepancy_count > 0

    field_map = {f.field_key: f for f in report.fields}
    assert field_map["grand_total"].is_match is False
    assert field_map["grand_total"].discrepancy_type == "VALUE_MISMATCH"
    assert "KRITISCHE DISKREPANZ" in field_map["grand_total"].details_de


def test_day_26_api_endpoints():
    """Verifies FastAPI endpoints for sample profiles and visual reconciliation."""
    client = TestClient(app)

    # 1. List sample profiles
    r_list = client.get("/api/v1/zugferd/sample-profiles")
    assert r_list.status_code == 200
    profiles = r_list.json()
    assert len(profiles) == 5

    # 2. Get specific profile
    r_single = client.get("/api/v1/zugferd/sample-profiles/xrechnung-ubl")
    assert r_single.status_code == 200
    assert r_single.json()["profile_id"] == "xrechnung-ubl"

    r_404 = client.get("/api/v1/zugferd/sample-profiles/unknown-999")
    assert r_404.status_code == 404

    # 3. Document visual reconciliation endpoint
    doc_id = uuid4()
    r_rec = client.get(f"/api/v1/documents/{doc_id}/reconcile-visual-xml")
    assert r_rec.status_code == 200
    rec_body = r_rec.json()
    assert rec_body["has_visual_layer"] is True
    assert "fields" in rec_body
    assert len(rec_body["fields"]) >= 8

    # 4. Raw visual reconciliation endpoint
    visual_snippet = "Rechnungsnummer RE-2026-DE-84920 Brutto: 38.675,00 EUR USt-IdNr DE329184910"
    r_raw = client.post(
        f"/api/v1/zugferd/reconcile-visual-raw?visual_text={visual_snippet}",
        content=SAMPLE_FACTURX_COMFORT,
        headers={"Content-Type": "text/plain"},
    )
    assert r_raw.status_code == 200
    raw_body = r_raw.json()
    assert raw_body["total_fields_checked"] >= 8
