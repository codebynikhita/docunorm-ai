from uuid import uuid4
import pytest
from app.services.remediation_engine import RemediationEngine, compute_word_diff


def test_compute_word_diff():
    orig = "Vor-Ort-Prüfungen sind ausgeschlossen."
    repl = "Vor-Ort-Prüfungen sind uneingeschränkt gestattet."
    tokens = compute_word_diff(orig, repl)
    assert len(tokens) > 0
    types = [t.type for t in tokens]
    assert "delete" in types
    assert "insert" in types


def test_remediation_engine_detects_critical_risks():
    doc_id = uuid4()
    chunks = [
        {
            "id": "c1",
            "page_number": 1,
            "bounding_box": [50.0, 50.0, 400.0, 100.0],
            "content": "Jede Vor-Ort-Prüfung oder Zutritt zu den Rechenzentren ist strengstens ausgeschlossen.",
        },
        {
            "id": "c2",
            "page_number": 2,
            "bounding_box": [50.0, 150.0, 400.0, 200.0],
            "content": "Für Prüfungen wird eine Kaution in Höhe von 50.000 € sowie eine Aufwandspauschale erhoben.",
        },
        {
            "id": "c3",
            "page_number": 3,
            "bounding_box": [50.0, 250.0, 400.0, 300.0],
            "content": "Eine Haftung für Subunternehmer ist vollumfänglich ausgeschlossen.",
        },
    ]

    heatmap = RemediationEngine.analyze_document_risk(doc_id, "test_contract.pdf", chunks)

    assert heatmap.critical_count >= 3
    assert heatmap.overall_risk_score >= 85.0
    assert heatmap.risk_rating in ["CCC", "B"]
    assert 1 in heatmap.page_scores
    assert 2 in heatmap.page_scores
    assert 3 in heatmap.page_scores


def test_remediation_engine_generates_bgb_proposal():
    proposal = RemediationEngine.generate_amendment_proposal(
        rule_id="BAFIN-AUDIT-01",
        original_clause="Vor-Ort-Prüfungen sind ausgeschlossen.",
    )

    assert "KWG § 25b" in proposal.title_de or "Prüf" in proposal.title_de
    assert "uneingeschränkten" in proposal.compliant_replacement_de
    assert "unrestricted" in proposal.compliant_replacement_en
    assert "BGB § 307" in proposal.bgb_statutory_basis
    assert len(proposal.diff_tokens) > 0


def test_remediation_engine_generates_amendment_pdf(tmp_path):
    proposal = RemediationEngine.generate_amendment_proposal(
        rule_id="BAFIN-AUDIT-01",
        original_clause="Vor-Ort-Prüfungen sind ausgeschlossen.",
    )

    pdf_path = RemediationEngine.generate_amendment_contract_pdf(
        document_filename="test_siemens.pdf",
        proposals=[proposal],
        output_dir=tmp_path,
    )

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000
