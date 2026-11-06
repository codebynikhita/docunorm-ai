import uuid

import pymupdf as fitz

from app.models.document import Document
from app.schemas.battlecard import (
    ConflictPillar,
    NegotiationBattlecardResponse,
    SlaSimulationRequest,
)
from app.services.battlecard_engine import BattlecardEngine
from app.services.battlecard_pdf_exporter import generate_battlecard_report_pdf


def test_battlecard_evaluation():
    doc_id = uuid.uuid4()
    chunks = [
        {
            "id": "c1",
            "page_number": 1,
            "content": (
                "This Master Cloud Services Agreement is entered into under the laws of Delaware, United States. "
                "The provider shall comply with any subpoena, court order, or lawful request from government agencies without notice. "
                "Upon termination, customer shall pay a data transfer fee of EUR 50,000 for data migration. "
                "All subcontractors shall be deemed approved unless customer objects within 14 days."
            ),
        }
    ]

    res = BattlecardEngine.evaluate_contract(
        document_id=doc_id,
        filename="AWS_US_Cloud_Agreement.pdf",
        chunks=chunks,
    )

    assert isinstance(res, NegotiationBattlecardResponse)
    assert res.overall_negotiation_posture == "UNACCEPTABLE_HIGH_RISK"
    assert res.critical_count >= 1
    assert res.tia_assessment.cloud_act_exposure is True
    assert res.tia_assessment.overall_transfer_risk == "CRITICAL"
    assert res.tia_assessment.transfer_risk_score > 80.0

    # Verify battlecard contents
    pillars = [b.pillar for b in res.battlecards]
    assert ConflictPillar.CLOUD_ACT_CONFLICT in pillars
    assert ConflictPillar.EXIT_LOCKIN in pillars
    assert ConflictPillar.SUBCONTRACTOR_CHAIN in pillars

    cloud_bc = next(b for b in res.battlecards if b.pillar == ConflictPillar.CLOUD_ACT_CONFLICT)
    assert "DSGVO Art. 48" in cloud_bc.statutory_reference
    assert "HYOK" in cloud_bc.non_negotiable_clause_de
    assert "BaFin" in cloud_bc.bafin_escalation_script


def test_sla_outage_simulation():
    # Scenario 1: Minor 1-hour outage on 99.95% SLA (tolerated: 4.38h)
    req1 = SlaSimulationRequest(downtime_hours=1.0, contract_value_eur=1000000.0, availability_target_pct=99.95)
    sim1 = BattlecardEngine.simulate_sla_outage(req1)
    assert sim1.dora_incident_classification == "NEGLIGIBLE"
    assert sim1.penalty_eur == 0.0
    assert sim1.statutory_extraordinary_termination_triggered is False

    # Scenario 2: Major 6-hour outage
    req2 = SlaSimulationRequest(downtime_hours=6.0, contract_value_eur=1000000.0, availability_target_pct=99.95)
    sim2 = BattlecardEngine.simulate_sla_outage(req2)
    assert sim2.dora_incident_classification == "MAJOR_INCIDENT"
    assert sim2.excess_downtime_hours > 0.0
    assert sim2.penalty_eur > 0.0
    assert "4 Stunden" in sim2.bafin_initial_notification_deadline
    assert sim2.statutory_extraordinary_termination_triggered is False

    # Scenario 3: Critical 48-hour outage
    req3 = SlaSimulationRequest(downtime_hours=48.0, contract_value_eur=1000000.0, availability_target_pct=99.95)
    sim3 = BattlecardEngine.simulate_sla_outage(req3)
    assert sim3.dora_incident_classification == "CRITICAL_SYSTEMIC_INCIDENT"
    assert sim3.statutory_extraordinary_termination_triggered is True
    assert sim3.penalty_eur == 50000.0  # Hit 5% max cap


def test_battlecard_pdf_generation(tmp_path):
    doc = Document(
        id=uuid.uuid4(),
        filename="Deutsche_Bank_Master_Cloud_Agreement_50P.pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    chunks = [
        {"id": "c1", "page_number": 1, "content": "Subpoena compliance under US law and exit toll of EUR 75,000."}
    ]
    data = BattlecardEngine.evaluate_contract(doc.id, doc.filename, chunks)
    pdf_path = generate_battlecard_report_pdf(doc, data, output_dir=tmp_path)

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 10000

    # Verify PDF layout with PyMuPDF
    pdf = fitz.open(str(pdf_path))
    assert len(pdf) >= 1
    page1 = pdf[0]
    rect = page1.rect
    assert rect.width == 595
    assert rect.height == 842
    text = page1.get_text()
    assert "DOCUNORM SOVEREIGN DEFENSE" in text
    assert "KRYPTOGRAPHISCHES PRÜFSIEGEL" in text
    pdf.close()
