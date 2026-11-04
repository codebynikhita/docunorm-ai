import uuid
from pathlib import Path
import pytest
import pymupdf as fitz

from app.models.document import Document
from app.schemas.capa import CapaSeverity, SupplierCapaPlan
from app.services.capa_engine import CapaEngine
from app.services.capa_pdf_exporter import generate_capa_report_pdf


def test_capa_plan_generation():
    doc_id = uuid.uuid4()
    chunks = [
        {
            "id": "c1",
            "page_number": 1,
            "content": (
                "Standard-Lieferantenvertrag für Beschaffungsteile ohne explizite Erwähnung der LkSG-Sorgfaltspflichten. "
                "Haftung für Unterlieferanten wird ausdrücklich abbedungen. "
                "Entsorgung industrieller Sonderabfälle erfolgt nach ortsüblichen Gepflogenheiten des Herstellerlandes."
            ),
        }
    ]

    res = CapaEngine.generate_plan(
        document_id=doc_id,
        filename="Lieferantenvertrag_Asien_Tier1.pdf",
        chunks=chunks,
    )

    assert isinstance(res, SupplierCapaPlan)
    assert res.overall_compliance_posture == "CRITICAL_ACTION_REQUIRED"
    assert res.total_milestones >= 4
    assert res.critical_milestones_count >= 1
    assert res.bafa_notification_required is True

    # Verify critical milestones
    milestone_ids = [m.id for m in res.milestones]
    assert "CAPA-01-CHILD-LABOR" in milestone_ids
    assert "CAPA-02-ENV-TREATIES" in milestone_ids
    assert "CAPA-03-FAIR-WAGE" in milestone_ids
    assert "CAPA-04-WHISTLEBLOWER" in milestone_ids

    child_labor_m = next(m for m in res.milestones if m.id == "CAPA-01-CHILD-LABOR")
    assert child_labor_m.severity == CapaSeverity.CRITICAL
    assert child_labor_m.deadline_days == 30
    assert child_labor_m.penalty_upon_default_eur > 0.0
    assert "TÜV" in child_labor_m.verification_method or "SGS" in child_labor_m.verification_method


def test_capa_pdf_export(tmp_path):
    doc = Document(
        id=uuid.uuid4(),
        filename="Lieferantenvertrag_Asien_Tier1.pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    chunks = [
        {"id": "c1", "page_number": 1, "content": "Defizitärer Zuliefervertrag ohne Kinderarbeits-Verbot und Mindestlohn."}
    ]
    data = CapaEngine.generate_plan(doc.id, doc.filename, chunks)
    pdf_path = generate_capa_report_pdf(doc, data, output_dir=tmp_path)

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 10000

    # Verify PDF structure with PyMuPDF
    pdf = fitz.open(str(pdf_path))
    assert len(pdf) >= 1
    page1 = pdf[0]
    rect = page1.rect
    assert rect.width == 595
    assert rect.height == 842
    text = page1.get_text()
    assert "KORREKTUR-AKTIONSPLAN" in text
    assert "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE" in text
    assert "KRYPTOGRAPHISCHES PRÜFSIEGEL" in text
    pdf.close()
