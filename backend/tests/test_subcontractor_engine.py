import pytest
from uuid import uuid4
from app.services.subcontractor_engine import subcontractor_engine


def test_subcontractor_engine_full_compliance():
    """
    Verifies that a contract with 60 days advance notice, customer veto rights,
    special termination on objection, strict vicarious liability, and audit flow-through
    scores AAA Full Compliance.
    """
    doc_id = uuid4()
    chunks = [
        {
            "chunk_id": "c1",
            "page_number": 1,
            "content": (
                "§ 5 Unterauftragsvergabe und Kaskadierungsrisiko: Der Auftragnehmer ist berechtigt, "
                "zertifizierte Unterauftragnehmer einzusetzen. Über den beabsichtigten Einsatz wird der Auftraggeber "
                "mindestens 60 Kalendertage im Voraus schriftlich informiert. Dem Auftraggeber steht ein ausdrückliches "
                "Widerspruchsrecht zu."
            ),
        },
        {
            "chunk_id": "c2",
            "page_number": 2,
            "content": (
                "§ 6 Kündigung bei Unterbeauftragung: Widerspricht der Auftraggeber der Weiterverlagerung, "
                "steht ihm ein außerordentliches Sonderkündigungsrecht zu. Der Hauptauftragnehmer haftet für Handlungen "
                "und Unterlassungen seiner Subunternehmer wie für eigenes Verschulden gem. BGB § 278."
            ),
        },
        {
            "chunk_id": "c3",
            "page_number": 3,
            "content": (
                "§ 7 Prüfrechte in der Kette: Der Auftragnehmer verpflichtet jeden Unterauftragnehmer zur lückenlosen "
                "Weitergabe aller aufsichtsrechtlichen Prüfrechte (Kaskadierungsgebot). Sämtliche Rechenzentren befinden sich "
                "in Frankfurt am Main, Deutschland (EWR)."
            ),
        },
    ]

    report = subcontractor_engine.audit_chunks(doc_id, chunks)

    assert report.document_id == doc_id
    assert report.overall_score >= 88.0
    assert "VOLLSTÄNDIG KONFORM" in report.compliance_rating
    assert len(report.checks) == 5
    assert report.concentration_risk_level == "NIEDRIG"
    assert len(report.cascading_nodes) >= 2

    # Check 1: Advance notice
    c1 = next(c for c in report.checks if c.rule_id == "DORA-SUBCONTRACT-01")
    assert c1.status == "COMPLIANT"
    assert c1.score == 1.0

    # Check 2: Termination on objection
    c2 = next(c for c in report.checks if c.rule_id == "DORA-SUBCONTRACT-02")
    assert c2.status == "COMPLIANT"
    assert c2.score == 1.0

    # Check 3: Vicarious liability
    c3 = next(c for c in report.checks if c.rule_id == "DORA-SUBCONTRACT-03")
    assert c3.status == "COMPLIANT"
    assert c3.score == 1.0

    # Check 4: Downstream audit rights
    c4 = next(c for c in report.checks if c.rule_id == "DORA-SUBCONTRACT-04")
    assert c4.status == "COMPLIANT"
    assert c4.score == 1.0


def test_subcontractor_engine_deficient_deemed_consent():
    """
    Verifies that a deemed consent trap (Zustimmungsfiktion within 5 days) or unannounced
    delegation is classified as critically deficient under DORA Art. 30(3).
    """
    doc_id = uuid4()
    chunks = [
        {
            "chunk_id": "c1",
            "page_number": 1,
            "content": (
                "Ziffer 14.3: Subunternehmer können vom Cloud-Anbieter ohne vorherige gesonderte Vorankündigung beauftragt werden. "
                "Eine Haftung für Subunternehmer ist ausgeschlossen."
            ),
        }
    ]

    report = subcontractor_engine.audit_chunks(doc_id, chunks)

    assert report.document_id == doc_id
    assert report.overall_score < 60.0
    assert "KRITISCH DEFIZITÄR" in report.compliance_rating

    c1 = next(c for c in report.checks if c.rule_id == "DORA-SUBCONTRACT-01")
    assert c1.status == "NON_COMPLIANT"
    assert c1.score == 0.0

    c3 = next(c for c in report.checks if c.rule_id == "DORA-SUBCONTRACT-03")
    assert c3.status == "NON_COMPLIANT"
    assert c3.score == 0.0


def test_subcontractor_engine_cross_border_cloud_act_risk():
    """
    Verifies that unmonitored fourth-party transfer to US nodes is flagged with KRITISCH concentration risk.
    """
    doc_id = uuid4()
    chunks = [
        {
            "chunk_id": "c1",
            "page_number": 1,
            "content": (
                "§ 4 Datenhaltung: Primärserver in Frankfurt. Die kryptographischen Schlüssel werden jedoch in Virginia (USA) "
                "beim US-Mutterkonzern verwaltet und unterliegen US CLOUD Act Zugriffen."
            ),
        }
    ]

    report = subcontractor_engine.audit_chunks(doc_id, chunks)

    assert report.concentration_risk_level == "KRITISCH"
    c5 = next(c for c in report.checks if c.rule_id == "DORA-SUBCONTRACT-05")
    assert c5.status == "NON_COMPLIANT"
    assert any(n.risk_level == "KRITISCH" for n in report.cascading_nodes)
