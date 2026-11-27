"""
DocuNorm AI — Day 41: AI Contract Negotiation Simulator & Multi-Turn Stresstest Test Suite.
Validates multi-turn legal arguments, hyperscaler counter-tactics, compromise covenants,
DIN 5008 negotiation protocol PDF export, and REST endpoints.
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.negotiation_sim import NegotiationStepRequest
from app.services.negotiation_simulator import negotiation_simulator


def test_supervisory_audit_rights_negotiation():
    """
    Verifies multi-round negotiation over DORA Art. 30(3)(e) on-site datacenter audits vs.
    multi-tenant secrecy pushback, resulting in a compliant Pooled Audit compromise covenant.
    """
    req = NegotiationStepRequest(
        document_id=uuid4(),
        document_filename="AWS_EMEA_Enterprise_Master.pdf",
        clause_domain="supervisory_audit_rights",
        vendor_archetype="US_HYPERSCALER",
        enterprise_stance="STRICT_REGULATORY_LINE",
        current_clause_text="Der Anbieter behält sich vor, Vor-Ort-Audits abzulehnen und auf SOC-2 Berichte zu verweisen.",
        round_count=3,
    )

    session = negotiation_simulator.simulate_negotiation(req)

    assert session.current_status == "CONSENSUS_REACHED"
    assert len(session.rounds) == 3
    assert session.rounds[0].speaker == "ENTERPRISE_BUYER"
    assert session.rounds[1].speaker == "VENDOR_LEGAL_COUNSEL"
    assert session.rounds[2].speaker == "ENTERPRISE_BUYER"
    assert "DORA Art. 30" in session.rounds[0].argument_de
    assert "DSGVO Art. 32" in session.rounds[1].argument_de
    assert "Pooled Audit" in session.rounds[2].argument_de
    assert session.final_reconciled_clause is not None
    assert "Pooled Audits" in session.final_reconciled_clause
    assert session.risk_reduction_percentage > 50.0
    assert len(session.sha256_audit_trail) == 64


def test_emergency_exit_unwinding_negotiation():
    """
    Verifies negotiation over BaFin RS 10/2026 emergency unwinding and exclusion of prepayment fees.
    """
    req = NegotiationStepRequest(
        document_id=uuid4(),
        document_filename="Hyperscaler_Fixed_Term_Agreement.pdf",
        clause_domain="emergency_exit_unwinding",
        vendor_archetype="US_HYPERSCALER",
        current_clause_text="Vorzeitige Kündigung erfordert 180 Tage Vorlauf und 70% Vorfälligkeitsentschädigung.",
        round_count=3,
    )

    session = negotiation_simulator.simulate_negotiation(req)

    assert session.current_status == "CONSENSUS_REACHED"
    assert session.final_reconciled_clause is not None
    assert "ohne Vorfälligkeitsentschädigung" in session.final_reconciled_clause
    assert "90 Tagen" in session.final_reconciled_clause
    assert session.bafin_audit_safe is True


def test_cloud_act_byok_negotiation():
    """
    Verifies negotiation over US CLOUD Act subpoena immunity using EU-resident HSM BYOK custody.
    """
    req = NegotiationStepRequest(
        document_id=uuid4(),
        document_filename="Cloud_Storage_Global.pdf",
        clause_domain="cloud_act_byok",
        vendor_archetype="US_HYPERSCALER",
        current_clause_text="Verschlüsselung erfolgt mit Standard KMS Schlüsseln in US-Regionen.",
        round_count=3,
    )

    session = negotiation_simulator.simulate_negotiation(req)

    assert session.current_status == "CONSENSUS_REACHED"
    assert session.final_reconciled_clause is not None
    assert "Bring-Your-Own-Key" in session.final_reconciled_clause or "BYOK" in session.final_reconciled_clause
    assert "Motion to Quash" in session.final_reconciled_clause or "Rechtsmittel" in session.final_reconciled_clause


def test_user_counter_argument_injection():
    """
    Verifies that a custom argument supplied by the enterprise legal counsel is appended to the transcript.
    """
    custom_arg = "Nach BGB § 307 Abs. 2 Nr. 1 ist diese Klausel mit wesentlichen Grundgedanken der gesetzlichen Regelung unvereinbar."
    req = NegotiationStepRequest(
        document_id=uuid4(),
        document_filename="SaaS_Agreement.pdf",
        clause_domain="supervisory_audit_rights",
        current_clause_text="Auditgebühr beträgt 50.000 EUR.",
        user_counter_argument=custom_arg,
        round_count=3,
    )

    session = negotiation_simulator.simulate_negotiation(req)
    last_buyer_round = session.rounds[2]
    assert custom_arg in last_buyer_round.argument_de


def test_certified_negotiation_protocol_pdf_generation():
    """
    Verifies PyMuPDF generation of official 2-page DIN 5008 negotiation protocol PDF.
    """
    req = NegotiationStepRequest(
        document_id=uuid4(),
        document_filename="Azure_Outsourcing_Contract.pdf",
        clause_domain="subcontractor_veto",
        current_clause_text="Unterauftragnehmer können jederzeit ohne Vorankündigung gewechselt werden.",
        round_count=3,
    )
    session = negotiation_simulator.simulate_negotiation(req)

    pdf_path = negotiation_simulator.generate_negotiation_protocol_pdf(
        session=session,
        signatory_name="Dr. Karl von Clausewitz, Lead Legal Counsel",
    )

    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 1500


def test_rest_negotiation_endpoints():
    """
    Verifies:
    1. POST /api/v1/negotiation-sim/simulate
    2. GET /api/v1/negotiation-sim/sessions/{id}
    3. GET /api/v1/negotiation-sim/sessions/{id}/export-protocol-pdf
    """
    client = TestClient(app)

    payload = {
        "document_id": str(uuid4()),
        "document_filename": "Telekom_Hosting_SLA.pdf",
        "clause_domain": "sla_penalties",
        "vendor_archetype": "US_HYPERSCALER",
        "enterprise_stance": "STRICT_REGULATORY_LINE",
        "current_clause_text": "SLA Verfügbarkeit beträgt 99,0% mit reinen Service-Credits bis max 5%.",
        "round_count": 3,
    }

    # 1. POST /simulate
    sim_res = client.post("/api/v1/negotiation-sim/simulate", json=payload)
    assert sim_res.status_code == 200, sim_res.text
    data = sim_res.json()
    assert data["clause_domain"] == "sla_penalties"
    assert len(data["rounds"]) == 3
    assert data["current_status"] == "CONSENSUS_REACHED"
    session_id = data["session_id"]

    # 2. GET /sessions/{id}
    get_res = client.get(f"/api/v1/negotiation-sim/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["session_id"] == session_id

    # 3. GET /export-protocol-pdf
    pdf_res = client.get(f"/api/v1/negotiation-sim/sessions/{session_id}/export-protocol-pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert "VERHANDLUNGSPROTOKOLL" in pdf_res.headers.get("content-disposition", "")
    assert len(pdf_res.content) > 1500
