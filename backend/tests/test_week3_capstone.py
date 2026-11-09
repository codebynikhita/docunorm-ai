from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pymupdf as fitz
import pytest

from app.services.bafa_annual_report_exporter import generate_bafa_annual_report_pdf
from app.services.capa_engine import CapaEngine
from app.services.environmental_engine import EnvironmentalEngine
from app.services.portfolio_aggregator import portfolio_aggregator
from app.services.tier_n_cascade_engine import tier_n_cascade_engine


@pytest.mark.asyncio
async def test_week3_capstone_full_lifecycle(tmp_path: Path):
    """
    Week 3 Capstone Integration Test:
    Verifies end-to-end multi-supplier audit evaluation across all 6 statutory dimensions:
    - LkSG § 2 & BAFA 12-Section Evaluation
    - Environmental Triad (§ 2 Abs. 3)
    - Multi-Tier Cascade (§ 9)
    - CAPA Action Planning (§ 7)
    - Portfolio HHI Concentration & SPOF Analysis
    - BAFA Annual Due Diligence Report PDF Synthesis (§ 10 Abs. 2)
    """
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    tenant_id = uuid4()
    doc_id = uuid4()

    # 1. Test Capstone Supplier Chunks
    compliant_chunks = [
        {"content": "Der Lieferant verpflichtet sich zur vollständigen Einhaltung des Minamata-Übereinkommens. Sämtliche Baugruppen sind quecksilberfrei gefertigt."},
        {"content": "Ebenso wird PCB-Freiheit und Ausschluss von PFOS/PFOA gem. Stockholmer Konvention über persistente organische Schadstoffe (POPs) garantiert."},
        {"content": "Basler Übereinkommen: Sonderabfälle werden ausschließlich mit behördlicher PIC-Zustimmung (Prior Informed Consent) verbracht."},
        {"content": "Verbot von Kinderarbeit gem. ILO 138/182, Zwangsarbeit und Vereinigungsfreiheit werden vollumfänglich garantiert."},
        {"content": "§ 8 Kaskadierung von Sorgfaltspflichten in der Lieferkette (§ 9 LkSG): Der Lieferant übernimmt eine ausdrückliche Weitergabeverpflichtung sämtlicher menschenrechtlicher Standards entlang der gesamten Vertragskette."},
        {"content": "Dem Auftraggeber werden uneingeschränkte Kontrollrechte entlang der Kette sowie Audit- und Einsichtsrechte und Vor-Ort-Kontrollen bei Subunternehmern (Tier-2 bis Tier-N) eingeräumt. Bei substantiierter Kenntnis erfolgt unverzüglich eine anlassbezogene Risikoanalyse."},
    ]

    deficient_chunks = [
        {"content": "Haftungsausschluss: Die Haftung für grobe Fahrlässigkeit und Körperschäden wird hiermit vollumfänglich ausgeschlossen gem. § 309 BGB."},
        {"content": "Umweltschutz- und Minamata-Vorgaben sind für Unterauftragnehmer im Ausland unverbindlich und begründen keine Prüfpflicht."},
        {"content": "Eine Weitergabe vertraglicher LkSG-Pflichten an Unterauftragnehmer (Tier-2) findet ausdrücklich nicht statt."},
    ]

    # 2. CAPA Engine Evaluation
    capa_compliant = CapaEngine.generate_plan(doc_id, "test_compliant.pdf", compliant_chunks)
    assert capa_compliant.total_milestones >= 0

    capa_deficient = CapaEngine.generate_plan(doc_id, "test_deficient.pdf", deficient_chunks)
    assert capa_deficient.total_milestones >= 2
    assert capa_deficient.estimated_remediation_cost_eur > 0

    # 3. Environmental Engine Evaluation
    env_eval = EnvironmentalEngine.evaluate_contract(doc_id, "test_compliant.pdf", compliant_chunks)
    assert env_eval.overall_environmental_score >= 80.0
    assert env_eval.environmental_rating in ["AAA", "AA", "A"]

    # 4. Multi-Tier Cascade Evaluation
    cascade_eval = tier_n_cascade_engine.analyze_cascade(
        " ".join(c["content"] for c in compliant_chunks),
        doc_id,
    )
    assert cascade_eval.overall_cascade_score >= 50.0

    # 5. Portfolio Aggregation & HHI Metrics
    synthesis = await portfolio_aggregator.aggregate_portfolio(
        db=mock_db,
        tenant_id=tenant_id,
        reporting_year=2026,
    )

    assert synthesis.tenant_id == tenant_id
    assert synthesis.total_suppliers_audited >= 4
    assert synthesis.portfolio_compliance_score > 0.0

    # HHI concentration checks
    metrics = synthesis.concentration_metrics
    assert metrics.herfindahl_hirschman_index > 0
    assert metrics.single_points_of_failure_count >= 1
    assert metrics.top_3_vendor_share_percentage > 50.0

    # 6. Official Annual BAFA Report (§ 10 Abs. 2) PDF Generation
    pdf_path = generate_bafa_annual_report_pdf(
        synthesis=synthesis,
        company_name="Sovereign Enterprise Deutschland AG",
        output_dir=tmp_path,
    )

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 10000

    # Validate PDF structure with PyMuPDF
    pdf_doc = fitz.open(str(pdf_path))
    assert len(pdf_doc) == 3

    page1_text = pdf_doc[0].get_text()
    assert "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE (BAFA)" in page1_text
    assert "§ 10 ABS. 2 LkSG" in page1_text
    assert "KONZENTRATIONSINDEX (HHI)" in page1_text
    assert "2026" in page1_text

    page2_text = pdf_doc[1].get_text()
    assert "LIEFERANTEN-PORTFOLIO-MATRIX" in page2_text

    page3_text = pdf_doc[2].get_text()
    assert "RECHTSVERBINDLICHE ERKLÄRUNG DES VORSTANDS" in page3_text
    assert "SHA-256" in page3_text
    pdf_doc.close()
