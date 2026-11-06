import uuid

import pymupdf as fitz

from app.models.document import Document
from app.schemas.environmental import (
    EnvironmentalAuditReport,
    EnvironmentalConvention,
    PicProcedureStatus,
    SubstanceComplianceStatus,
)
from app.services.environmental_engine import EnvironmentalEngine
from app.services.environmental_pdf_exporter import (
    generate_environmental_certificate_pdf,
)


def test_environmental_engine_compliant():
    doc_id = uuid.uuid4()
    chunks = [
        {
            "id": "c1",
            "page_number": 1,
            "content": (
                "Der Lieferant verpflichtet sich zur vollständigen Einhaltung des Minamata-Übereinkommens. "
                "Sämtliche Baugruppen sind quecksilberfrei gefertigt. "
                "Ebenso wird PCB-Freiheit und Ausschluss von PFOS/PFOA gem. Stockholmer Konvention garantiert. "
                "Sonderabfälle werden ausschließlich mit behördlicher PIC-Zustimmung (Prior Informed Consent) verbracht."
            ),
        }
    ]

    res = EnvironmentalEngine.evaluate_contract(
        document_id=doc_id,
        filename="Green_Supplier_Germany.pdf",
        chunks=chunks,
    )

    assert isinstance(res, EnvironmentalAuditReport)
    assert res.overall_environmental_score >= 85.0
    assert res.environmental_rating in ["AAA", "AA", "A"]
    assert res.prohibited_substances_count == 0
    assert res.unauthorized_shipments_count == 0
    assert res.minamata_mercury_status == SubstanceComplianceStatus.COMPLIANT
    assert res.stockholm_pops_status == SubstanceComplianceStatus.COMPLIANT
    assert res.basel_waste_status == PicProcedureStatus.VERIFIED_APPROVED


def test_environmental_engine_prohibited():
    doc_id = uuid.uuid4()
    chunks = [
        {
            "id": "c1",
            "page_number": 1,
            "content": (
                "Herstellung unter Einsatz von elementarem Quecksilber (CAS 7439-97-6) im Chlor-Alkali-Verfahren. "
                "Abfallexport von elektronischem Sondermüll ohne gesonderte PIC-Genehmigung des Ziellandes."
            ),
        }
    ]

    res = EnvironmentalEngine.evaluate_contract(
        document_id=doc_id,
        filename="Dirty_Manufacturing_Facility.pdf",
        chunks=chunks,
    )

    assert isinstance(res, EnvironmentalAuditReport)
    assert res.overall_environmental_score < 60.0
    assert res.environmental_rating == "CCC"
    assert res.prohibited_substances_count >= 1

    hg = next(s for s in res.substances if s.convention == EnvironmentalConvention.MINAMATA_MERCURY)
    assert hg.status == SubstanceComplianceStatus.PROHIBITED
    assert "Membranverfahren" in hg.remediation_guidance


def test_environmental_pdf_generation(tmp_path):
    doc = Document(
        id=uuid.uuid4(),
        filename="Siemens_Environmental_Supply_Contract.pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    chunks = [
        {"id": "c1", "page_number": 1, "content": "Quecksilberfrei gem Minamata und notifizierte Sonderabfallentsorgung."}
    ]
    report = EnvironmentalEngine.evaluate_contract(doc.id, doc.filename, chunks)
    pdf_path = generate_environmental_certificate_pdf(doc, report, output_dir=tmp_path)

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 10000

    # Verify PDF layout with PyMuPDF
    pdf = fitz.open(str(pdf_path))
    assert len(pdf) == 2
    page1 = pdf[0]
    rect = page1.rect
    assert rect.width == 595
    assert rect.height == 842
    text1 = page1.get_text()
    assert "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE" in text1
    assert "KRYPTOGRAPHISCHES PRÜFSIEGEL" in text1
    assert "MINAMATA" in text1

    page2 = pdf[1]
    text2 = page2.get_text()
    assert "BASLER ÜBEREINKOMMEN" in text2
    assert "BEHÖRDLICHE ZEICHNUNG" in text2
    pdf.close()
