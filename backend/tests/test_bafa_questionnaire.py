import uuid
from pathlib import Path
import pytest
import fitz

from app.models.document import Document
from app.schemas.lksg import BafaComplianceStatus, BafaQuestionnaireResponse
from app.services.bafa_questionnaire import BafaQuestionnaireService
from app.services.bafa_pdf_exporter import generate_bafa_audit_report_pdf


def test_bafa_questionnaire_gold_standard():
    doc_id = uuid.uuid4()
    chunks = [
        {
            "id": "c1",
            "page_number": 1,
            "content": (
                "Siemens AG Rahmenvereinbarung über IT-Dienstleistungen. "
                "Der Auftragnehmer verpflichtet sich zur Einhaltung aller menschenrechtlichen Sorgfaltspflichten nach dem LkSG. "
                "Kinderarbeit gem. ILO 138 und 182 ist strikt untersagt. Mindestalter 15 Jahre. "
                "Freiwilligkeit der Arbeitsaufnahme und Verbot von Zwangsarbeit garantiert. "
                "Arbeits- und Gesundheitsschutz nach ISO 45001. "
                "Anerkennung der Koalitionsfreiheit und Tarifautonomie gem. ILO 87 und 98. "
                "Vergütung erfolgt mindestens in Höhe des gesetzlichen Mindestlohns (MiLoG). "
                "Vollständige Beachtung des Minamata-Übereinkommens über Quecksilber. "
                "Ausschluss persistenter organischer Schadstoffe (POPs) gem. Stockholmer Übereinkommen. "
                "Ausschluss illegaler grenzüberschreitender Abfalltransporte gem. Basler Übereinkommen. "
                "Einrichtung eines Whistleblower-Systems gem. § 8 LkSG mit Vertraulichkeitsgarantie. "
                "Vorlage des geprüften BAFA-Berichts und Audit-Rechte uneingeschränkt garantiert."
            ),
        }
    ]

    res = BafaQuestionnaireService.generate_questionnaire(
        document_id=doc_id,
        filename="Siemens_Gold_Standard_LkSG.pdf",
        chunks=chunks,
    )

    assert isinstance(res, BafaQuestionnaireResponse)
    assert res.supplier_name != ""
    assert res.total_questions == 12
    assert res.compliant_count >= 10
    assert res.overall_score >= 85.0
    assert res.compliance_rating in ["AAA", "AA", "A"]

    # Verify all 12 sections exist in sequence
    section_nums = [s.section_number for s in res.sections]
    assert section_nums == list(range(1, 13))


def test_bafa_questionnaire_environmental_violations():
    doc_id = uuid.uuid4()
    chunks = [
        {
            "id": "c1",
            "page_number": 1,
            "content": (
                "Hardware-Liefervertrag mit AsiaTech Hardware Ltd. "
                "Der Lieferant setzt quecksilberhaltige Schalter und Schmelzsicherungen zur Kostensenkung ein. "
                "Elektroschrott und Industrieabfälle werden zur Entsorgung in Nicht-OECD-Staaten ohne behördliche Genehmigung exportiert. "
                "Es besteht kein internes Beschwerdeverfahren oder Meldekanal für Arbeitnehmer."
            ),
        }
    ]

    res = BafaQuestionnaireService.generate_questionnaire(
        document_id=doc_id,
        filename="AsiaTech_Violations_Contract.pdf",
        chunks=chunks,
    )

    # Section 8 (Minamata) must be NON_COMPLIANT
    sec8 = next(s for s in res.sections if s.section_number == 8)
    assert sec8.compliance_status == BafaComplianceStatus.NON_COMPLIANT

    # Section 10 (Basel Waste) must be NON_COMPLIANT
    sec10 = next(s for s in res.sections if s.section_number == 10)
    assert sec10.compliance_status == BafaComplianceStatus.NON_COMPLIANT

    # Section 11 (Complaints) must be NON_COMPLIANT
    sec11 = next(s for s in res.sections if s.section_number == 11)
    assert sec11.compliance_status == BafaComplianceStatus.NON_COMPLIANT

    assert res.non_compliant_count >= 3
    assert res.overall_score < 80.0


def test_bafa_pdf_report_exporter(tmp_path):
    doc_id = uuid.uuid4()
    doc_model = Document(
        id=doc_id,
        tenant_id=uuid.uuid4(),
        filename="Deutsche_Bank_Master_Cloud_Agreement_50P.pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        total_pages=50,
        file_size_bytes=524288,
    )

    chunks = [
        {
            "id": "c1",
            "page_number": 46,
            "content": (
                "§ 46 Einhaltung des Lieferkettensorgfaltspflichtengesetzes (LkSG § 4 & § 5). "
                "Der Dienstleister verpflichtet sich zur Einhaltung aller menschenrechtlichen und umweltbezogenen Sorgfaltspflichten nach dem LkSG. "
                "Er führt jährliche Risikoanalysen in seiner gesamten Lieferkette durch und stellt dem Institut seinen geprüften BAFA-Bericht zur Verfügung."
            ),
        }
    ]

    q_data = BafaQuestionnaireService.generate_questionnaire(
        document_id=doc_id,
        filename=doc_model.filename,
        chunks=chunks,
    )

    pdf_out = generate_bafa_audit_report_pdf(
        document=doc_model,
        questionnaire=q_data,
        signatory_name="Dr. Michael Weber, Leitender BaFin-Prüfer",
        output_dir=tmp_path,
    )

    assert pdf_out.exists()
    assert pdf_out.stat().st_size > 5000

    # Validate PDF structure using PyMuPDF
    pdf_doc = fitz.open(str(pdf_out))
    assert len(pdf_doc) >= 2
    first_page_text = pdf_doc[0].get_text()
    assert "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE" in first_page_text
    assert "Lieferkettensorgfaltspflichtengesetz" in first_page_text
    assert "BAFA-STATUS" in first_page_text
    pdf_doc.close()
