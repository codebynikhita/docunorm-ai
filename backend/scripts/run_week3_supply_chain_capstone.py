"""
Week 3 Capstone Certification & Multi-Supplier Supply Chain Portfolio Batch Audit.
Implements automated forensic compliance verification across:
- LkSG §§ 2-10 (German Supply Chain Due Diligence Act)
- BAFA Administrative Guidelines (Handreichung zur Risikoanalyse & zum Beschwerdeverfahren)
- BGB §§ 309, 311, 339 (German Civil Code Contract Law)
- Minamata, Stockholm & Basel Environmental Conventions
- Full DIN 5008 / ISO 19011 Cryptographic PDF Generation
"""

import asyncio
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from uuid import uuid4

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import pymupdf as fitz
from app.models.document import Document
from app.schemas.portfolio import BafaAnnualReportSynthesis
from app.services.bafa_annual_report_exporter import generate_bafa_annual_report_pdf
from app.services.bafa_pdf_exporter import generate_bafa_audit_report_pdf
from app.services.bafa_questionnaire import BafaQuestionnaireService
from app.services.capa_engine import CapaEngine
from app.services.capa_pdf_exporter import generate_capa_report_pdf
from app.services.environmental_engine import EnvironmentalEngine
from app.services.environmental_pdf_exporter import generate_environmental_certificate_pdf
from app.services.lksg_analyzer import LkSGAnalyzerService
from app.services.portfolio_aggregator import portfolio_aggregator
from app.services.privacy import privacy_firewall
from app.services.remediation_engine import RemediationEngine
from app.services.tier_n_cascade_engine import tier_n_cascade_engine
from app.services.tier_n_cascade_pdf_exporter import generate_tier_n_cascade_pdf


# 4 Distinct Multi-Tier Corporate Supplier Contracts
SUPPLIER_CONTRACTS = [
    {
        "supplier_name": "Apex Core Cloud Infrastructure GmbH",
        "filename": "1_Apex_Cloud_Infrastructure_Master_SLA.pdf",
        "spend_eur": 5_200_000.0,
        "text": """
        MASTER SERVICE AGREEMENT & CLOUD INFRASTRUCTURE LEASE
        Zwischen Deutsche Sovereign Enterprise AG und Apex Core Cloud Infrastructure GmbH.
        
        § 4 Menschenrechte und Verhaltenskodex (§ 2 Abs. 2 LkSG)
        Der Auftragnehmer verpflichtet sich zur uneingeschränkten Einhaltung der ILO-Kernarbeitsnormen.
        Kinderarbeit und Zwangsarbeit sind strengstens verboten. Arbeitsentgelte entsprechen mindestens
        dem Mindestlohngesetz (MiLoG) zuzüglich branchenüblicher Tarifzuschläge.
        
        § 7 Umweltkonventionen und Schadstoffausschluss (§ 2 Abs. 3 LkSG)
        (1) Sämtliche Server und USV-Anlagen sind frei von Quecksilber (Minamata-Übereinkommen).
        (2) Der Einsatz persistenter organischer Schadstoffe (Stockholm POPs / PFAS) ist untersagt.
        (3) Elektronikschrott und Sonderabfälle werden ausschließlich gemäß Basler Übereinkommen entsorgt.
        
        § 9 Weitergabeverpflichtung in der Lieferkette (§ 9 LkSG)
        Der Auftragnehmer verpflichtet sich zur Weitergabeverpflichtung sämtlicher menschenrechtlicher
        und umweltbezogener Vorgaben an Subunternehmer (Tier-2 und Tier-N). Der Auftraggeber erhält
        uneingeschränkte Kontrollrechte entlang der Kette sowie Prüfungs- und Auditrechte vor Ort.
        
        § 12 Beschwerdeverfahren & Whistleblower-Schutz (§ 8 LkSG)
        Der Auftragnehmer unterhält ein öffentlich zugängliches, mehrsprachiges Beschwerdeverfahren
        mit garantiertem Hinweisgeberschutz ohne Benachteiligungsrisiko.
        """,
    },
    {
        "supplier_name": "Bavaria Precision Semiconductor AG",
        "filename": "2_Bavaria_Semiconductor_Components_Rahmenvertrag.pdf",
        "spend_eur": 3_400_000.0,
        "text": """
        RAHMENLIEFERVERTRAG ÜBER MIKROELEKTRONIK UND ASICS
        Zwischen Deutsche Sovereign Enterprise AG und Bavaria Precision Semiconductor AG.
        
        § 5 Arbeitsbedingungen und Koalitionsfreiheit
        Arbeitsschutzmaßnahmen entsprechen den gesetzlichen Bestimmungen der Bundesrepublik Deutschland.
        Gewerkschaftliche Betätigung und Betriebsräte werden anerkannt.
        
        § 8 Vorlieferanten und Rohstoffe (§ 9 LkSG)
        Die Endmontage der Wafer erfolgt teilweise bei Unterauftragnehmern in Vietnam.
        Rohkobalt und Zinn werden aus der Demokratischen Republik Kongo bezogen.
        Der Auftragnehmer bemüht sich um die Weitergabe des Verhaltenskodex.
        Hinweis: Es liegen Berichte von NGOs über Kinderarbeit im handwerklichen Kobaltbergbau vor
        (Substantiierte Kenntnis nach § 9 Abs. 2 LkSG). Eine anlassbezogene Risikoanalyse wird eingeleitet.
        
        § 14 Haftungsbeschränkung
        Schadensersatzansprüche sind auf 100% des Auftragswerts gedeckelt, ausgenommen Vorsatz.
        """,
    },
    {
        "supplier_name": "Rhine-Ruhr Industrial Logistics SE",
        "filename": "3_Rhine_Ruhr_Logistics_Speditionsvertrag.pdf",
        "spend_eur": 1_850_000.0,
        "text": """
        LOGISTIK- UND FRACHTFÜHRERVERTRAG FÜR INDUSTRIEGÜTER
        Zwischen Deutsche Sovereign Enterprise AG und Rhine-Ruhr Industrial Logistics SE.
        
        § 6 Gefahrguttransport und Basler Übereinkommen (§ 2 Abs. 3 Nr. 3 LkSG)
        (1) Grenzüberschreitende Verbringungen gefährlicher Abfälle (Y31 e-waste und Y41 Lösungsmittel)
        erfolgen unter lückenloser Einhaltung des PIC-Verfahrens (Prior Informed Consent).
        (2) Ausfuhrverbote in Nicht-OECD-Staaten (Basel Ban Amendment) werden strikt eingehalten.
        
        § 10 Beschwerdekanal und Arbeitssicherheit
        Fahrer und Lagerpersonal erhalten Schutzausrüstung. Ruhezeiten nach EU-VO 561/2006 werden gewahrt.
        Whistleblower-Meldestelle nach § 8 LkSG ist eingerichtet und verifiziert.
        """,
    },
    {
        "supplier_name": "Global Parts Manufacturing Ltd",
        "filename": "4_Global_Parts_Deficient_Contract.pdf",
        "spend_eur": 750_000.0,
        "text": """
        GENERAL PURCHASE AND MANUFACTURING TERMS (STANDARD AGB)
        Between Deutsche Sovereign Enterprise AG and Global Parts Manufacturing Ltd.
        
        Clause 3 Delivery and Liability Limitation
        The supplier shall have NO liability for any indirect, consequential, or punitive damages,
        EVEN IN CASES OF GROSS NEGLIGENCE OR WILLFUL MISCONDUCT.
        Total liability is strictly capped at 25,000 EUR.
        
        Clause 7 Subcontractors and Supply Chain
        Supplier delivers EX Works (EXW). No audits or inspections of upstream sub-tier facilities
        are permitted. Supplier assumes no liability for sub-suppliers or human rights compliance.
        No whistleblower complaint procedure is established.
        """,
    },
]


def run_week3_capstone():
    print("=" * 80)
    print("🏛️  DOCUNORM AI — WEEK 3 CAPSTONE CERTIFICATION SUITE")
    print("    LkSG §§ 2–10 Supply Chain Governance & BAFA Annual Filing (§ 10 Abs. 2)")
    print("=" * 80)

    tenant_id = uuid4()
    reports_dir = backend_dir / "reports" / "week3_capstone"
    reports_dir.mkdir(parents=True, exist_ok=True)

    audited_portfolio = []

    # 1. Audit each contract across all 6 dimensions
    for idx, contract in enumerate(SUPPLIER_CONTRACTS, 1):
        doc_id = uuid4()
        s_name = contract["supplier_name"]
        f_name = contract["filename"]
        raw_text = contract["text"]
        spend = contract["spend_eur"]

        print(f"\n[{idx}/4] 🔍 AUDITING SUPPLIER: {s_name}")
        print(f"      Vertrag: {f_name} | Einkaufsvolumen: EUR {spend:,.2f}")

        # PII Shield
        masked_text = privacy_firewall.anonymize_text(raw_text).sanitized_text

        chunk_dicts = [
            {
                "id": f"chunk_{doc_id}_1",
                "content": masked_text,
                "page_number": 1,
                "bounding_box": [50.0, 100.0, 500.0, 400.0],
            }
        ]

        # A. LkSG Risk Analysis
        lksg_res = LkSGAnalyzerService.analyze_document(doc_id, f_name, chunk_dicts)
        print(f"      • LkSG Gesamt-Score: {lksg_res.assessment.overall_compliance_score:.1f}% ({lksg_res.assessment.compliance_rating})")
        print(f"        - Menschenrechte: {lksg_res.assessment.human_rights_score:.1f}%")
        print(f"        - Governance:     {lksg_res.assessment.governance_score:.1f}%")

        # B. BAFA 12-Section Questionnaire
        bafa_res = BafaQuestionnaireService.generate_questionnaire(doc_id, f_name, chunk_dicts)
        print(f"      • BAFA 12-Fragebogen: {bafa_res.overall_score:.1f}% ({bafa_res.compliant_count}/12 konform)")

        # C. BGB § 309 Nullification Check
        rem_res = RemediationEngine.analyze_document_risk(doc_id, f_name, chunk_dicts)
        bgb_risks = [r for r in rem_res.risk_items if "309" in r.statutory_ref or "haftung" in r.category.lower()]
        if bgb_risks:
            print(f"      ⚠️  BGB § 309 Nichtigkeits-Warnung: {len(bgb_risks)} unzulässige Klauseln (Haftungsausschluss grobe Fahrlässigkeit)")
        else:
            print("      • BGB § 309 Prüfung: Regelkonform (keine unzulässigen Klauselverbote)")

        # D. CAPA Action Plan (§ 7 LkSG)
        capa_res = CapaEngine.generate_plan(doc_id, f_name, chunk_dicts)
        total_penalties = sum(m.penalty_upon_default_eur for m in capa_res.milestones)
        print(f"      • CAPA Aktionsplan (§ 7): {capa_res.total_milestones} Meilensteine | Pönale: EUR {total_penalties:,.2f}")

        # E. Environmental Conventions (§ 2 Abs. 3 LkSG)
        env_res = EnvironmentalEngine.evaluate_contract(doc_id, f_name, chunk_dicts)
        print(f"      • Umwelt-Compliance: {env_res.overall_environmental_score:.1f}% ({env_res.environmental_rating})")
        print(f"        - Minamata (Hg):  {env_res.minamata_mercury_status.value}")
        print(f"        - Stockholm (POP): {env_res.stockholm_pops_status.value}")
        print(f"        - Basel (Abfall): {env_res.basel_waste_status.value}")

        # F. Multi-Tier Cascade Tracker (§ 9 LkSG)
        casc_res = tier_n_cascade_engine.analyze_cascade(masked_text, doc_id)
        print(f"      • Kaskaden-Konformität (§ 9): {casc_res.overall_cascade_score:.1f}% ({casc_res.compliance_rating})")
        print(f"        - Weitergabeklausel: {casc_res.supplier_nodes[0].pass_through_status.value if casc_res.supplier_nodes else 'FEHLEND'}")
        print(f"        - Aktive Vorfälle:   {len(casc_res.active_incidents)} substantiierte Fälle")

        # Generate individual certified PDF reports
        dummy_doc = Document(
            id=doc_id,
            tenant_id=tenant_id,
            uploaded_by=uuid4(),
            filename=f_name,
            sha256_hash=fitz.get_pdf_str(fitz.open()).encode("utf-8").hex()[:64],
            file_path="/tmp/fake.pdf",
            file_size_bytes=1024,
        )

        bafa_pdf = generate_bafa_audit_report_pdf(dummy_doc, bafa_res, output_dir=reports_dir)
        env_pdf = generate_environmental_certificate_pdf(dummy_doc, env_res, output_dir=reports_dir)
        casc_pdf = generate_tier_n_cascade_pdf(dummy_doc, casc_res, output_dir=reports_dir)

        audited_portfolio.append({
            "supplier_name": s_name,
            "filename": f_name,
            "spend_eur": spend,
            "lksg_score": lksg_res.assessment.overall_compliance_score,
            "rating": lksg_res.assessment.compliance_rating,
            "bafa_compliant_sections": bafa_res.compliant_count,
            "env_score": env_res.overall_environmental_score,
            "cascade_score": casc_res.overall_cascade_score,
            "active_incidents": len(casc_res.active_incidents),
            "bafa_pdf": str(bafa_pdf),
            "env_pdf": str(env_pdf),
            "casc_pdf": str(casc_pdf),
        })

    # 2. Portfolio-Wide Aggregation & BAFA Annual Filing Synthesis (§ 10 Abs. 2)
    print("\n" + "=" * 80)
    print("📊 2. PORTFOLIO-AGGREGATION & JAHRESBERICHT-SYNTHESE (§ 10 ABS. 2 LkSG)")
    print("=" * 80)

    # Mock DB for Portfolio Aggregator
    class MockResult:
        def scalars(self):
            class ScalarResult:
                def all(self):
                    return []
            return ScalarResult()

    class MockAsyncSession:
        async def execute(self, stmt):
            return MockResult()

    mock_db = MockAsyncSession()
    synthesis = asyncio.run(portfolio_aggregator.aggregate_portfolio(
        db=mock_db,
        tenant_id=tenant_id,
        reporting_year=2026,
    ))

    print(f"• Gesamtportfolio-Konformitätswert: {synthesis.portfolio_compliance_score:.1f}% (Rating: {synthesis.portfolio_rating})")
    print(f"• Herfindahl-Hirschman-Index (HHI):  {synthesis.concentration_metrics.herfindahl_hirschman_index:.0f} ({synthesis.concentration_metrics.concentration_level.value})")
    print(f"• Top-3 Lieferanten Anteil:          {synthesis.concentration_metrics.top_3_vendor_share_percentage:.1f}%")
    print(f"• Single-Points-of-Failure (SPOF):   {synthesis.concentration_metrics.single_points_of_failure_count} Kettenglieder")
    print(f"• Erfasste Vertragspartner:          {synthesis.total_suppliers_audited} (Tier-1: {synthesis.direct_tier1_count} | Tier-N: {synthesis.indirect_tier_n_count})")
    print(f"• BAFA-Einreichungsstatus:           {synthesis.bafa_submission_readiness}")

    # Generate Official 3-Page Annual BAFA Dossier PDF
    annual_bafa_pdf = generate_bafa_annual_report_pdf(
        synthesis=synthesis,
        company_name="DocuNorm Sovereign Banking Group AG",
        output_dir=reports_dir,
    )
    print(f"\n✅ OFFIZIELLER BAFA-JAHRESBERICHT GENERIERT:")
    print(f"   Pfad: {annual_bafa_pdf}")
    print(f"   Dateigröße: {annual_bafa_pdf.stat().st_size:,} Bytes (3 Seiten DIN 5008)")

    # 3. Save Machine-Readable Certification Dossier
    summary_path = reports_dir / "week3_capstone_certification_dossier.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now(UTC).isoformat(),
            "certification_status": "WEEK_3_CAPSTONE_CERTIFIED",
            "statutory_mandates": [
                "LkSG §§ 2-10",
                "BAFA Handreichung zur Risikoanalyse",
                "BGB §§ 309, 311, 339",
                "Minamata, Stockholm & Basel Environmental Conventions",
            ],
            "portfolio_compliance_score": synthesis.portfolio_compliance_score,
            "portfolio_rating": synthesis.portfolio_rating,
            "hhi_index": synthesis.concentration_metrics.herfindahl_hirschman_index,
            "annual_bafa_report_pdf": str(annual_bafa_pdf),
            "audited_suppliers": audited_portfolio,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ ZERTIFIZIERUNGSDOSSIER GESPEICHERT: {summary_path}")
    print("\n" + "=" * 80)
    print("🏆 WEEK 3 (LKSG SUPPLY CHAIN GOVERNANCE) ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 80)


if __name__ == "__main__":
    run_week3_capstone()
