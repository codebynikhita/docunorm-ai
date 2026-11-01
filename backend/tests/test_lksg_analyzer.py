from uuid import uuid4
import pytest

from app.schemas.lksg import LkSGRiskCategory, LkSGSeverity
from app.services.lksg_analyzer import LkSGAnalyzerService


def test_lksg_analyzer_compliant_supplier():
    """
    Validates that a compliant supplier contract with Code of Conduct,
    ILO labor standards, complaints procedure, and BAFA reporting receives an AAA/AA rating.
    """
    doc_id = uuid4()
    chunks = [
        {
            "page_number": 1,
            "content": (
                "Lieferanten-Rahmenvereinbarung mit Infineon Technologies AG.\n"
                "§ 1 Vertragsgegenstand & Menschenrechtskodex: Der Lieferant verpflichtet sich zur strikten "
                "Einhaltung des Menschenrechts-Verhaltenskodex (Code of Conduct) gem. § 6 LkSG. "
                "Kinderarbeit (ILO 138/182) sowie Zwangsarbeit (ILO 29) sind ausnahmslos verboten."
            ),
        },
        {
            "page_number": 2,
            "content": (
                "§ 5 Arbeitsschutz & Entlohnung: Alle Mitarbeiter erhalten kostenfreie persönliche Schutzausrüstung "
                "und eine Vergütung, die mindestens dem gesetzlichen Mindestlohn (MiLoG) entspricht. "
                "Die Koalitionsfreiheit und das Recht auf freie Gewerkschaftsbildung werden garantiert."
            ),
        },
        {
            "page_number": 3,
            "content": (
                "§ 8 Beschwerdeverfahren & Whistleblower: Der Lieferant richtet ein öffentlich zugängliches, "
                "vertrauliches Beschwerdeverfahren nach § 8 LkSG ein und publiziert eine Verfahrensordnung."
            ),
        },
        {
            "page_number": 4,
            "content": (
                "§ 10 BAFA-Berichterstattung: Der Lieferant übermittelt jährlich bis zum 31. März seinen geprüften "
                "BAFA-Menschenrechtsbericht und gewährt dem Auftraggeber jährliche Vor-Ort-Audits."
            ),
        },
    ]

    res = LkSGAnalyzerService.analyze_document(doc_id, "Infineon_Lieferantenvertrag_2026.pdf", chunks)
    assessment = res.assessment

    assert assessment.overall_compliance_score >= 90.0
    assert assessment.compliance_rating in ["AAA", "AA"]
    assert assessment.critical_risk_count == 0
    assert assessment.complaints_procedure_present is True
    assert assessment.bafa_report_compliant is True
    assert assessment.code_of_conduct_mandated is True
    assert assessment.audit_rights_granted is True
    assert "Infineon" in assessment.supplier_name


def test_lksg_analyzer_critical_indirect_supplier_exclusion():
    """
    Detects unlawful attempts to exclude indirect (Tier-N) suppliers permanently
    from risk analysis (§ 9 LkSG violation).
    """
    doc_id = uuid4()
    chunks = [
        {
            "page_number": 1,
            "content": (
                "Liefervertrag mit Global Sourcing Ltd.\n"
                "Ziffer 14.2 Mittelbare Zulieferer: Für mittelbare Zulieferer (Tier-2 bis Tier-N) entfällt die "
                "gesetzliche Risikoanalyse dauerhaft. Der Auftraggeber verzichtet auf anlassbezogene Sorgfaltspflichten."
            ),
        }
    ]

    res = LkSGAnalyzerService.analyze_document(doc_id, "Global_Sourcing_Contract.pdf", chunks)
    assessment = res.assessment

    assert assessment.critical_risk_count >= 1
    assert assessment.compliance_rating in ["B", "CCC"]
    critical_risks = [r for r in assessment.identified_risks if r.severity == LkSGSeverity.CRITICAL]
    assert any(r.category == LkSGRiskCategory.INDIRECT_SUPPLIER_CONTROL for r in critical_risks)


def test_lksg_analyzer_missing_complaints_channel():
    """
    Verifies that absence of a § 8 LkSG complaints procedure is flagged as a high severity risk.
    """
    doc_id = uuid4()
    chunks = [
        {
            "page_number": 1,
            "content": (
                "Liefervertrag § 4: Allgemeine Qualitätsanforderungen und Lieferfristen für Bauteile. "
                "Keine Angaben zu Hinweisgebersystemen oder Beschwerden."
            ),
        }
    ]

    res = LkSGAnalyzerService.analyze_document(doc_id, "Parts_Supply_Agreement.pdf", chunks)
    assessment = res.assessment

    assert assessment.complaints_procedure_present is False
    complaints_risks = [r for r in assessment.identified_risks if r.category == LkSGRiskCategory.COMPLAINTS_PROCEDURE]
    assert len(complaints_risks) == 1
    assert complaints_risks[0].severity == LkSGSeverity.HIGH


def test_lksg_analyzer_environmental_minamata_violation():
    """
    Detects hazardous substance non-compliance under § 2 Abs. 3 LkSG (Minamata / Mercury).
    """
    doc_id = uuid4()
    chunks = [
        {
            "page_number": 1,
            "content": (
                "Produktionsanlage Chemie:\n"
                "Industrielle Quecksilber-Verarbeitung erfolgt unbehandelt ohne nachgeschaltete Filtersysteme."
            ),
        }
    ]

    res = LkSGAnalyzerService.analyze_document(doc_id, "Chemical_Supply_Audit.pdf", chunks)
    assessment = res.assessment

    env_risks = [r for r in assessment.identified_risks if r.category == LkSGRiskCategory.ENVIRONMENT_MINAMATA]
    assert len(env_risks) == 1
    assert env_risks[0].severity == LkSGSeverity.HIGH
    assert assessment.environmental_score < 100.0
