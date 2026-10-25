import pytest
from uuid import uuid4
from app.services.dora_exit_engine import dora_exit_engine


def test_dora_exit_engine_full_compliance():
    """
    Verifies that an authentic German ICT contract with clear notice periods,
    90-day migration assistance, open format data restitution, SLA preservation,
    and liquidated delay penalties scores AAA Full Compliance.
    """
    doc_id = uuid4()
    chunks = [
        {
            "chunk_id": "c1",
            "page_number": 1,
            "content": "§ 1 Gegenstand: Der Auftragnehmer garantiert eine jährliche Verfügbarkeit von 99,95 % (unterbrechungsfrei).",
            "bounding_box": [50.0, 100.0, 500.0, 150.0],
        },
        {
            "chunk_id": "c2",
            "page_number": 2,
            "content": (
                "§ 8 Kündigung und Ausstiegsstrategie: Die ordentliche Kündigungsfrist beträgt 60 Tage. "
                "Der Auftragnehmer leistet eine garantierte Migrationsunterstützung für mindestens 90 Kalendertage. "
                "Sämtliche Datenbestände werden im interoperablen Standardformat (CSV/XML) ohne Zusatzkosten herausgegeben."
            ),
            "bounding_box": [50.0, 150.0, 500.0, 250.0],
        },
        {
            "chunk_id": "c3",
            "page_number": 3,
            "content": (
                "§ 12 Leistungsverzug und Vertragsstrafen: Die Vertragsstrafe beträgt 0,2 % pro Werktag, "
                "gedeckelt auf 5 % des jährlichen Auftragswertes. Ein Haftungsausschluss greift nicht bei grober Fahrlässigkeit oder Vorsatz."
            ),
            "bounding_box": [50.0, 200.0, 500.0, 300.0],
        },
    ]

    report = dora_exit_engine.audit_chunks(doc_id, chunks)

    assert report.document_id == doc_id
    assert report.overall_score == 100.0
    assert "VOLLSTÄNDIG KONFORM" in report.compliance_rating
    assert len(report.checks) == 5

    # Check 1: Notice period
    c1 = next(c for c in report.checks if c.rule_id == "DORA-30-2-TERM")
    assert c1.status == "COMPLIANT"
    assert c1.score == 1.0
    assert "[DORA_TERM_§8]" in c1.citation_tag

    # Check 2: Migration assistance
    c2 = next(c for c in report.checks if c.rule_id == "DORA-30-2-MIGR")
    assert c2.status == "COMPLIANT"
    assert c2.score == 1.0

    # Check 3: Data restitution
    c3 = next(c for c in report.checks if c.rule_id == "DORA-30-2-DATA")
    assert c3.status == "COMPLIANT"

    # Check 4: Service continuity
    c4 = next(c for c in report.checks if c.rule_id == "DORA-30-2-SLA")
    assert c4.status == "COMPLIANT"

    # Check 5: Liquidation penalties
    c5 = next(c for c in report.checks if c.rule_id == "DORA-30-2-PENALTY")
    assert c5.status == "COMPLIANT"


def test_dora_exit_engine_detects_missing_migration_and_penalties():
    """
    Verifies that a deficient contract missing migration terms and penalty clauses
    is flagged as critically deficient or partially compliant.
    """
    doc_id = uuid4()
    chunks = [
        {
            "chunk_id": "c1",
            "page_number": 1,
            "content": "Allgemeine Dienstleistungsvereinbarung. Kündigungsfrist von 30 Tagen.",
            "bounding_box": [50.0, 100.0, 500.0, 150.0],
        }
    ]

    report = dora_exit_engine.audit_chunks(doc_id, chunks)

    assert report.overall_score < 70.0
    assert "KRITISCH DEFIZITÄR" in report.compliance_rating

    # Migration assistance should be non-compliant
    c2 = next(c for c in report.checks if c.rule_id == "DORA-30-2-MIGR")
    assert c2.status == "NON_COMPLIANT"
    assert c2.score == 0.0
    assert "Fehlt" in c2.recommendation_de

    # Penalty should be non-compliant
    c5 = next(c for c in report.checks if c.rule_id == "DORA-30-2-PENALTY")
    assert c5.status == "NON_COMPLIANT"
    assert c5.score == 0.0
