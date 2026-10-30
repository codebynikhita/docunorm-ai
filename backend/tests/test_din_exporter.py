import pytest
from uuid import uuid4
from pathlib import Path
from app.models.document import Document
from app.services.exporter import generate_din_audit_report_pdf


def test_generate_din_audit_report_pdf():
    doc = Document(
        id=uuid4(),
        tenant_id=uuid4(),
        filename="Deutsche_Bank_SaaS_Service_Agreement.pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_path="/tmp/fake_test.pdf",
        total_pages=5,
    )

    findings = [
        {
            "clause": "DORA Art. 30 Abs. 2 (Ausstiegsfristen)",
            "status": "PASS",
            "statutory_ref": "DORA Art. 30(2)(e)",
            "finding": "Kündigungsfrist von 60 Tagen mit garantierter Datenmigration konform vereinbart.",
            "page_number": 1,
            "snippet": "Jede Partei kann mit 60 Tagen zum Quartalsende kündigen.",
        },
        {
            "clause": "KWG § 25b (Aufsichtliche Prüfrechte)",
            "status": "PASS",
            "statutory_ref": "KWG § 25b · BAIT 8.1",
            "finding": "Uneingeschränkte Vor-Ort-Zutrittsrechte ohne Kautionsbarrieren verifiziert.",
            "page_number": 2,
            "snippet": "Aufsichtsbehörden haben unbeschränkten Zutritt zu den Rechenzentren.",
        },
    ]

    pdf_path = generate_din_audit_report_pdf(
        document=doc,
        audit_findings=findings,
        signatory_name="Dr. Michael Weber, Leitender BaFin-Prüfer",
        output_dir="/tmp/docunorm_test_exports",
    )

    assert Path(pdf_path).exists()
    assert pdf_path.stat().st_size > 5000
    assert "DIN_AUDIT_REPORT.pdf" in str(pdf_path)
