import pytest
from uuid import uuid4
from app.services.audit_rights_engine import audit_rights_engine


def test_audit_rights_full_compliance_aaa():
    """
    Verifies that a contract granting unrestricted on-site datacentre access,
    explicit direct BaFin/ECB supervisory audit rights, free-of-charge audits without deposits,
    collective pooled audits, and raw log / CISO interview rights achieves AAA Full Compliance.
    """
    doc_id = uuid4()
    chunks = [
        {
            "chunk_id": "c1",
            "page_number": 1,
            "content": (
                "§ 9 Vor-Ort-Prüfrechte und Datacenter-Zugang: Dem Auftraggeber sowie von ihm beauftragten "
                "Wirtschaftsprüfern wird uneingeschränkter physischer Zutritt zu allen Geschäftsräumen und Rechenzentren "
                "gewährt. Vor-Ort Prüfungen aus wichtigem Grund sind gestattet."
            ),
        },
        {
            "chunk_id": "c2",
            "page_number": 2,
            "content": (
                "§ 10 Aufsichtsrechtliche Sonderprüfungen: Der Bundesanstalt für Finanzdienstleistungsaufsicht (BaFin), "
                "der Europäischen Zentralbank (EZB) sowie der Deutschen Bundesbank stehen unmittelbare, eigene Auskunfts- "
                "und Prüfungsrechte gem. KWG § 25b Abs. 1 und DORA Art. 30 Abs. 3 lit. e zu."
            ),
        },
        {
            "chunk_id": "c3",
            "page_number": 3,
            "content": (
                "§ 11 Kostenfreiheit der Revision: Sämtliche Prüfungen und aufsichtsrechtliche Inspektionen sind "
                "vollständig kostenfrei durchzuführen. Eine Kostenerstattung oder die Hinterlegung einer Sicherheitskaution "
                "wird ausdrücklich ausgeschlossen."
            ),
        },
        {
            "chunk_id": "c4",
            "page_number": 4,
            "content": (
                "§ 12 Gemeinschaftsprüfungen und Nachweise: Der Auftraggeber ist berechtigt, sich an Pooled Audits "
                "mit anderen regulierten Instituten zu beteiligen. Dem Prüferteam ist vollständiger Zugang und Einsicht auf "
                "kryptographisch signierte Roh-Logs, Konfigurationsdateien und CISO-Interviews mit dem IT-Personal zu gewähren."
            ),
        },
    ]

    report = audit_rights_engine.audit_chunks(doc_id, chunks)

    assert report.document_id == doc_id
    assert report.overall_score >= 88.0
    assert "VOLLSTÄNDIG KONFORM (AAA)" in report.compliance_rating
    assert len(report.checks) == 5

    # Check 1: Onsite Access
    c1 = next(c for c in report.checks if c.rule_id == "BAFIN-AUDIT-01-ONSITE")
    assert c1.status == "COMPLIANT"
    assert c1.score == 1.0

    # Check 2: Regulatory Direct Access (BaFin / ECB)
    c2 = next(c for c in report.checks if c.rule_id == "BAFIN-AUDIT-02-REGULATOR-DIRECT")
    assert c2.status == "COMPLIANT"
    assert c2.score == 1.0

    # Check 3: Prohibition of fees / deposit bans
    c3 = next(c for c in report.checks if c.rule_id == "BAFIN-AUDIT-03-COST-FREE")
    assert c3.status == "COMPLIANT"
    assert c3.score == 1.0

    # Check 4: Collective / Pooled Audits
    c4 = next(c for c in report.checks if c.rule_id == "BAFIN-AUDIT-04-POOLED-AUDIT")
    assert c4.status == "COMPLIANT"
    assert c4.score == 1.0

    # Check 5: Raw logs and CISO interviews
    c5 = next(c for c in report.checks if c.rule_id == "BAFIN-AUDIT-05-LOGS-PERSONNEL")
    assert c5.status == "COMPLIANT"
    assert c5.score == 1.0

    # Letter verification
    assert report.notice_letter is not None
    assert "VOR-ORT-PRÜFUNG" in report.notice_letter.german_letter_content.upper()
    assert "BAFIN" in report.notice_letter.german_letter_content.upper()


def test_audit_rights_critical_deficiency_ccc():
    """
    Verifies that a contract with an obstructionist €50k audit deposit,
    exclusion of physical datacenter visits, and refusal of pooled audits
    is flagged as CCC Kritisch Defizitär.
    """
    doc_id = uuid4()
    chunks = [
        {
            "chunk_id": "c1",
            "page_number": 1,
            "content": (
                "Physischer Zutritt zu den Rechenzentren ist aus Sicherheitsgründen strengstens ausgeschlossen. "
                "Als Prüfnachweis genügt die Vorlage eines jährlichen SOC 2 Typ II Berichts."
            ),
        },
        {
            "chunk_id": "c2",
            "page_number": 2,
            "content": (
                "Für die Durchführung jeglicher Auditaktivitäten verlangt der Anbieter eine Aufwandsentschädigung "
                "sowie eine Sicherheitskaution in Höhe von 50.000 EUR. Pooled Audits sind ausgeschlossen."
            ),
        },
    ]

    report = audit_rights_engine.audit_chunks(doc_id, chunks)

    assert report.overall_score < 60.0
    assert "KRITISCH DEFIZITÄR (CCC)" in report.compliance_rating

    # c1: Onsite Access - Excluded
    c1 = next(c for c in report.checks if c.rule_id == "BAFIN-AUDIT-01-ONSITE")
    assert c1.status == "NON_COMPLIANT"
    assert c1.score == 0.0

    # c3: Fee prohibition violated
    c3 = next(c for c in report.checks if c.rule_id == "BAFIN-AUDIT-03-COST-FREE")
    assert c3.status == "NON_COMPLIANT"
    assert c3.score == 0.0


def test_audit_rights_din5008_letter_format():
    """
    Verifies that the generated DIN 5008 inspection notice letter
    includes statutory references to KWG § 25b, DORA Art. 30, and proper dispatch formatting.
    """
    doc_id = uuid4()
    chunks = [
        {
            "chunk_id": "c1",
            "page_number": 1,
            "content": "Cloud Service Provider: Amazon Web Services EMEA SARL. Die BaFin hat Prüfrechte.",
        }
    ]

    report = audit_rights_engine.audit_chunks(doc_id, chunks)
    letter = report.notice_letter

    assert letter.recipient_vendor is not None
    assert "Amazon Web Services" in letter.recipient_vendor or "Cloud Provider" in letter.recipient_vendor
    assert "§ 25b" in letter.legal_basis
    assert "DORA" in letter.legal_basis or "2022/2554" in letter.legal_basis
    assert len(letter.scope_of_inspection) >= 3
    assert "VOR-ORT-PRÜFUNG" in letter.german_letter_content.upper()
    assert "ON-SITE REGULATORY INSPECTION" in letter.english_letter_content.upper()
