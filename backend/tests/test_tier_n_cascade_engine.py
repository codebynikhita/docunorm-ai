from pathlib import Path
from uuid import uuid4

import pymupdf as fitz

from app.models.document import Document
from app.schemas.tier_n_cascade import (
    AuditRightsCascade,
    EscalationStage,
    PassThroughClauseStatus,
    SupplyChainTier,
)
from app.services.tier_n_cascade_engine import tier_n_cascade_engine
from app.services.tier_n_cascade_pdf_exporter import generate_tier_n_cascade_pdf

SAMPLE_COMPLIANT_CONTRACT = """
HAUPTVERTRAG ÜBER HARDWARE-SYSTEME UND RECHENZENTRUMS-INFRASTRUKTUR
Zwischen Deutsche Cloud Systems AG und Alpha Server Components GmbH.

§ 8 Kaskadierung von Sorgfaltspflichten in der Lieferkette (§ 9 LkSG)
(1) Der Auftragnehmer verpflichtet sich zur Weitergabeverpflichtung sämtlicher menschenrechtlicher
und umweltbezogener Verhaltenskodizes entlang der gesamten Vertragskette.
(2) Der Auftragnehmer sichert dem Auftraggeber uneingeschränkte Kontrollrechte entlang der Kette sowie
Audit- und Einsichtsrechte und Vor-Ort-Kontrollen bei Subunternehmern (Tier-2 und Tier-N) zu.
(3) Bei Vorliegen substantiierter Kenntnis über mögliche Verletzungen leitet der Auftragnehmer
unverzüglich eine anlassbezogene Risikoanalyse ein und etabliert ein Beschwerdeverfahren für Subunternehmer.
"""

SAMPLE_DEFICIENT_CONTRACT = """
STANDARD-LIEFERVEREINBARUNG
Zwischen Global Parts Corp und Basic Manufacturing Ltd.

§ 4 Leistungsumfang
Die Lieferung erfolgt ab Werk (EXW). Keine Prüfung von Vorlieferanten erforderlich.
Der Auftragnehmer übernimmt keine Haftung für Subunternehmer dritter Stufen.
"""


def test_cascade_audit_compliant_contract():
    doc_id = uuid4()
    report = tier_n_cascade_engine.analyze_cascade(SAMPLE_COMPLIANT_CONTRACT, doc_id)

    assert report.document_id == doc_id
    assert report.overall_cascade_score >= 80.0
    assert "AAA" in report.compliance_rating
    assert report.pass_through_enforceable_rate >= 85.0
    assert report.substantiated_knowledge_active is False
    assert len(report.active_incidents) == 0

    t1_node = next(n for n in report.supplier_nodes if n.tier == SupplyChainTier.TIER_1_DIRECT)
    assert t1_node.pass_through_status == PassThroughClauseStatus.PRESENT_ENFORCEABLE
    assert t1_node.audit_rights == AuditRightsCascade.FULL_UNRESTRICTED


def test_cascade_audit_deficient_contract():
    doc_id = uuid4()
    report = tier_n_cascade_engine.analyze_cascade(SAMPLE_DEFICIENT_CONTRACT, doc_id)

    assert report.document_id == doc_id
    assert report.overall_cascade_score < 70.0
    assert report.pass_through_enforceable_rate <= 30.0
    assert report.substantiated_knowledge_active is True
    assert len(report.active_incidents) >= 1

    t1_node = next(n for n in report.supplier_nodes if n.tier == SupplyChainTier.TIER_1_DIRECT)
    assert t1_node.pass_through_status == PassThroughClauseStatus.MISSING_DEFICIENT
    assert t1_node.audit_rights == AuditRightsCascade.NO_RIGHTS

    # Check that incident contains § 9 Abs. 2 statutory escalation stages
    critical_inc = next(inc for inc in report.active_incidents if inc.severity == "KRITISCH")
    assert critical_inc.escalation_stage == EscalationStage.STAGE_1_AD_HOC_ANALYSIS
    assert critical_inc.statutory_deadline_days == 14
    assert critical_inc.bafa_notification_required is True


def test_tier_n_cascade_pdf_generation(tmp_path: Path):
    doc_id = uuid4()
    report = tier_n_cascade_engine.analyze_cascade(SAMPLE_DEFICIENT_CONTRACT, doc_id)

    dummy_doc = Document(
        id=doc_id,
        tenant_id=uuid4(),
        uploaded_by=uuid4(),
        filename="Test_Liefervertrag_TierN.pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_path="/tmp/fake.pdf",
        file_size_bytes=1024,
    )

    pdf_file = generate_tier_n_cascade_pdf(
        document=dummy_doc,
        report=report,
        output_dir=tmp_path,
    )

    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 1000

    # Verify PyMuPDF opens valid 2-page PDF
    pdf_doc = fitz.open(str(pdf_file))
    assert len(pdf_doc) == 2

    page1_text = pdf_doc[0].get_text()
    assert "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE (BAFA)" in page1_text
    assert "LkSG § 9 DOSSIER" in page1_text
    assert "MULTILATERALE LIEFERKETTEN-KASKADENPRÜFUNG" in page1_text

    page2_text = pdf_doc[1].get_text()
    assert "SUBSTANTIIERTE KENNTNIS NACH § 9 ABS. 2 LkSG" in page2_text
    assert "GESETZLICHE 4-STUFIGE ESKALATIONSKASKADE" in page2_text

    pdf_doc.close()
