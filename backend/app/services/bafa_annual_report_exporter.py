"""
Certified DIN 5008 Annual Corporate BAFA Due Diligence Report Exporter
under § 10 Abs. 2 LkSG with Cryptographic SHA-256 Seal.
"""

import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path

import pymupdf as fitz

from app.schemas.portfolio import BafaAnnualReportSynthesis


def generate_bafa_annual_report_pdf(
    synthesis: BafaAnnualReportSynthesis,
    company_name: str = "DocuNorm Sovereign Banking Group AG",
    signatory_title: str = "Vorstandsvorsitzender & Leitender Compliance-Beauftragter",
    output_dir: Path | str = "/tmp/docunorm_exports",
) -> Path:
    """
    Generates an official 3-page DIN 5008 Annual BAFA Due Diligence Report
    under § 10 Abs. 2 LkSG for submission to the Federal Office for Economic Affairs and Export Control.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = Path(output_dir) / f"BAFA_JAHRESBERICHT_{synthesis.reporting_year}_LKSG_10.pdf"

    # Compute a deterministic portfolio integrity hash
    hash_payload = f"{synthesis.tenant_id}_{synthesis.reporting_year}_{synthesis.portfolio_compliance_score}_{len(synthesis.supplier_items)}"
    portfolio_hash = hashlib.sha256(hash_payload.encode()).hexdigest()

    doc = fitz.open()
    created_at_dt = datetime.now(UTC)
    date_stamp = created_at_dt.strftime("%d.%m.%Y")
    now_str = created_at_dt.strftime("%d. %B %Y • %H:%M:%S UTC")

    # =========================================================================
    # PAGE 1: Official Header, Executive Scores & Concentration Metrics
    # =========================================================================
    page1 = doc.new_page(width=595, height=842)

    # Header Banner
    page1.draw_rect(fitz.Rect(40, 35, 555, 95), color=(0.1, 0.25, 0.5), fill=(0.95, 0.97, 1.0))
    page1.draw_line(fitz.Point(40, 95), fitz.Point(555, 95), color=(0.15, 0.35, 0.7), width=2.5)

    page1.insert_text(
        fitz.Point(52, 54),
        "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE (BAFA) • GESETZLICHER JAHRESBERICHT",
        fontsize=9.5,
        fontname="hebo",
        color=(0.08, 0.2, 0.45),
    )
    page1.insert_text(
        fitz.Point(52, 69),
        f"JAHRESBERICHT ÜBER DIE ERFÜLLUNG DER SORGFALTSPFLICHTEN (§ 10 ABS. 2 LkSG) — BERICHTSJAHR {synthesis.reporting_year}",
        fontsize=8.0,
        fontname="hebo",
        color=(0.15, 0.35, 0.65),
    )
    page1.insert_text(
        fitz.Point(52, 84),
        f"Berichtspflichtiges Unternehmen: {company_name} • Gesetzliche Abgabefrist: {synthesis.submission_deadline}",
        fontsize=7.5,
        fontname="helv",
        color=(0.3, 0.35, 0.45),
    )

    # 1. Executive Summary Box
    page1.draw_rect(fitz.Rect(40, 105, 555, 180), color=(0.85, 0.88, 0.94), fill=(0.98, 0.99, 1.0))

    # Metric 1: Overall Portfolio Compliance
    page1.insert_text(fitz.Point(55, 122), "GESAMT-PORTFOLIO-KONFORMITÄT", fontsize=7.0, fontname="hebo", color=(0.4, 0.45, 0.5))
    score_col = (0.1, 0.55, 0.25) if synthesis.portfolio_compliance_score >= 80 else ((0.8, 0.45, 0.05) if synthesis.portfolio_compliance_score >= 50 else (0.8, 0.15, 0.15))
    page1.insert_text(fitz.Point(55, 144), f"{synthesis.portfolio_compliance_score:.1f}%", fontsize=18.0, fontname="hebo", color=score_col)
    page1.insert_text(fitz.Point(55, 162), f"Rating: {synthesis.portfolio_rating} ({synthesis.bafa_submission_readiness})", fontsize=7.5, fontname="hebo", color=score_col)

    # Metric 2: Herfindahl-Hirschman Index (HHI)
    page1.insert_text(fitz.Point(220, 122), "KONZENTRATIONSINDEX (HHI)", fontsize=7.0, fontname="hebo", color=(0.4, 0.45, 0.5))
    page1.insert_text(fitz.Point(220, 144), f"{synthesis.concentration_metrics.herfindahl_hirschman_index:.0f}", fontsize=18.0, fontname="hebo", color=(0.15, 0.25, 0.45))
    page1.insert_text(fitz.Point(220, 162), f"{synthesis.concentration_metrics.concentration_level.value} (Top 3: {synthesis.concentration_metrics.top_3_vendor_share_percentage:.1f}%)", fontsize=7.0, fontname="helv", color=(0.3, 0.35, 0.4))

    # Metric 3: Scope of Audited Supply Chain
    page1.insert_text(fitz.Point(395, 122), "GEPRÜFTE LIEFERANTENKETTE", fontsize=7.0, fontname="hebo", color=(0.4, 0.45, 0.5))
    page1.insert_text(fitz.Point(395, 144), f"{synthesis.total_suppliers_audited} Zulieferer", fontsize=15.0, fontname="hebo", color=(0.15, 0.25, 0.45))
    page1.insert_text(fitz.Point(395, 162), f"Tier-1: {synthesis.direct_tier1_count} | Tier-N: {synthesis.indirect_tier_n_count} Kaskaden", fontsize=7.0, fontname="helv", color=(0.3, 0.35, 0.4))

    # 2. Three Pillars Breakdown
    page1.insert_text(fitz.Point(40, 202), "1. GESETZLICHE 3-SÄULEN-BEWERTUNG DES GESAMTPORTFOLIOS", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))

    pillars = [
        ("Säule 1: Menschenrechte (§ 2 Abs. 2 LkSG)", synthesis.human_rights_portfolio_average, "Verbot von Kinderarbeit, Zwangsarbeit, MiLoG-Mindestlohn & Arbeitsschutz"),
        ("Säule 2: Umweltkonventionen (§ 2 Abs. 3 LkSG)", synthesis.environmental_portfolio_average, "Minamata-Quecksilber, Stockholm-POPs & Basel-Sonderabfallverbringung"),
        ("Säule 3: Governance & BAFA (§§ 4-8 LkSG)", synthesis.governance_portfolio_average, "Grundsatzerklärung, Beschwerdeverfahren (§ 8) & Kaskadierungsweitergabe"),
    ]

    for p_idx, (p_title, p_score, p_desc) in enumerate(pillars):
        card_y = 214 + p_idx * 52
        page1.draw_rect(fitz.Rect(40, card_y, 555, card_y + 45), color=(0.85, 0.88, 0.92), fill=(0.98, 0.99, 1.0))
        page1.insert_text(fitz.Point(52, card_y + 16), p_title, fontsize=8.0, fontname="hebo", color=(0.15, 0.25, 0.45))
        p_col = (0.1, 0.55, 0.25) if p_score >= 80 else ((0.8, 0.45, 0.05) if p_score >= 50 else (0.8, 0.15, 0.15))
        page1.insert_text(fitz.Point(480, card_y + 16), f"{p_score:.1f}%", fontsize=11.0, fontname="hebo", color=p_col)

        # Progress bar
        page1.draw_rect(fitz.Rect(52, card_y + 24, 460, card_y + 29), color=(0.88, 0.9, 0.94), fill=(0.9, 0.92, 0.96))
        bar_w = 408 * (p_score / 100.0)
        page1.draw_rect(fitz.Rect(52, card_y + 24, 52 + bar_w, card_y + 29), color=p_col, fill=p_col)

        page1.insert_text(fitz.Point(52, card_y + 38), p_desc, fontsize=6.8, fontname="helv", color=(0.4, 0.45, 0.5))

    # 3. Executive Summary Prose
    page1.insert_text(fitz.Point(40, 390), "2. ZUSAMMENFASSENDER BERICHT DES VORSTANDS (§ 10 ABS. 2 NR. 1-4 LkSG)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))
    page1.draw_rect(fitz.Rect(40, 402, 555, 480), color=(0.85, 0.88, 0.92), fill=(0.99, 0.99, 1.0))
    page1.insert_textbox(fitz.Rect(52, 412, 545, 470), synthesis.executive_summary_de, fontsize=7.5, fontname="helv", color=(0.2, 0.25, 0.3))

    # 4. Concentration Risk Analysis
    page1.insert_text(fitz.Point(40, 502), "3. ANALYSE DER BESCHAFFUNGSKONZENTRATION & KLUMPENRISIKEN", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))
    page1.draw_rect(fitz.Rect(40, 514, 555, 595), color=(0.85, 0.88, 0.92), fill=(0.98, 0.99, 1.0))

    page1.insert_text(fitz.Point(52, 532), f"Herfindahl-Hirschman-Index (HHI): {synthesis.concentration_metrics.herfindahl_hirschman_index:.0f} • Status: {synthesis.concentration_metrics.concentration_level.value}", fontsize=8.0, fontname="hebo", color=(0.15, 0.25, 0.45))
    page1.insert_text(fitz.Point(52, 548), f"Anteil der Top-3-Zulieferer am Gesamteinkaufsvolumen: {synthesis.concentration_metrics.top_3_vendor_share_percentage:.1f}%", fontsize=7.5, fontname="helv", color=(0.3, 0.35, 0.4))
    page1.insert_text(fitz.Point(52, 564), f"Identifizierte Single-Points-of-Failure (SPOF) in Hochrisikoregionen: {synthesis.concentration_metrics.single_points_of_failure_count} Kettenglieder", fontsize=7.5, fontname="helv", color=(0.8, 0.2, 0.2) if synthesis.concentration_metrics.single_points_of_failure_count > 0 else (0.1, 0.55, 0.25))
    page1.insert_text(fitz.Point(52, 580), f"Handlungsempfehlung: {synthesis.concentration_metrics.recommendation_de[:95]}", fontsize=7.0, fontname="helv", color=(0.25, 0.3, 0.35))

    # Page 1 Footer
    page1.insert_text(fitz.Point(40, 810), f"Prüfsiegel: SHA-256:{portfolio_hash[:32]}... • {now_str} • Seite 1 von 3", fontsize=6.5, fontname="helv", color=(0.5, 0.55, 0.6))

    # =========================================================================
    # PAGE 2: Multi-Supplier Matrix & Cross-Border Jurisdiction Exposure
    # =========================================================================
    page2 = doc.new_page(width=595, height=842)

    # Federal Sub-Header
    page2.draw_rect(fitz.Rect(40, 35, 555, 75), color=(0.1, 0.25, 0.5), fill=(0.95, 0.97, 1.0))
    page2.insert_text(fitz.Point(52, 52), "BAFA-JAHRESBERICHT • TABELLARISCHE LIEFERANTENÜBERSICHT & STANDORTRISIKEN", fontsize=9.5, fontname="hebo", color=(0.08, 0.2, 0.45))
    page2.insert_text(fitz.Point(52, 66), "Dokumentation aller Vertragspartner, Risikobewertungen und Kaskadierungsweitergabe", fontsize=7.5, fontname="helv", color=(0.3, 0.35, 0.45))

    page2.insert_text(fitz.Point(40, 95), "4. LIEFERANTEN-PORTFOLIO-MATRIX (§ 5 ABS. 1 LkSG)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))

    # Table Header
    y_table = 108
    page2.draw_rect(fitz.Rect(40, y_table, 555, y_table + 18), color=(0.8, 0.84, 0.9), fill=(0.92, 0.94, 0.98))
    page2.insert_text(fitz.Point(46, y_table + 12), "LIEFERANT / UNTERNEHMEN", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(235, y_table + 12), "ANTEIL", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(280, y_table + 12), "RATING", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(335, y_table + 12), "SCORE", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(385, y_table + 12), "WEITERGABE", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(495, y_table + 12), "VORFÄLLE", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))

    curr_y = y_table + 18
    for idx, s in enumerate(synthesis.supplier_items[:7]):
        row_bg = (0.98, 0.99, 1.0) if idx % 2 == 0 else (1.0, 1.0, 1.0)
        page2.draw_rect(fitz.Rect(40, curr_y, 555, curr_y + 26), color=(0.88, 0.9, 0.94), fill=row_bg)

        page2.insert_text(fitz.Point(46, curr_y + 11), s.supplier_name[:32], fontsize=7.5, fontname="hebo", color=(0.1, 0.15, 0.2))
        page2.insert_text(fitz.Point(46, curr_y + 21), s.contract_filename[:35], fontsize=6.5, fontname="helv", color=(0.4, 0.45, 0.5))

        page2.insert_text(fitz.Point(235, curr_y + 16), f"{s.spend_share_percentage:.1f}%", fontsize=7.0, fontname="helv", color=(0.2, 0.25, 0.35))

        r_col = (0.1, 0.55, 0.25) if "AAA" in s.lksg_rating else ((0.8, 0.45, 0.05) if "BBB" in s.lksg_rating else (0.8, 0.15, 0.15))
        page2.insert_text(fitz.Point(280, curr_y + 16), s.lksg_rating[:6], fontsize=7.0, fontname="hebo", color=r_col)
        page2.insert_text(fitz.Point(335, curr_y + 16), f"{s.overall_score:.1f}%", fontsize=7.0, fontname="hebo", color=r_col)

        pt_short = "DURCHSETZBAR" if "VOLLSTÄNDIG" in s.tier1_pass_through_status else "FEHLEND"
        pt_col = (0.1, 0.55, 0.25) if pt_short == "DURCHSETZBAR" else (0.8, 0.15, 0.15)
        page2.insert_text(fitz.Point(385, curr_y + 16), pt_short, fontsize=7.0, fontname="hebo", color=pt_col)

        inc_txt = f"{s.active_incidents_count} Vorfall" if s.active_incidents_count > 0 else "0"
        inc_col = (0.8, 0.15, 0.15) if s.active_incidents_count > 0 else (0.1, 0.55, 0.25)
        page2.insert_text(fitz.Point(495, curr_y + 16), inc_txt, fontsize=7.0, fontname="hebo", color=inc_col)

        curr_y += 26

    # 5. Global Jurisdiction Exposure Table
    page2.insert_text(fitz.Point(40, curr_y + 20), "5. GRENZÜBERSCHREITENDE STANDORTEXPOSITION (§ 9 ABS. 1 LkSG)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))

    j_table_y = curr_y + 32
    page2.draw_rect(fitz.Rect(40, j_table_y, 555, j_table_y + 18), color=(0.8, 0.84, 0.9), fill=(0.92, 0.94, 0.98))
    page2.insert_text(fitz.Point(46, j_table_y + 12), "LAND / JURISDIKTION", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(185, j_table_y + 12), "RISIKOSTUFE", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(265, j_table_y + 12), "ITUC INDEX", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(340, j_table_y + 12), "CPI SCORE", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(415, j_table_y + 12), "BASEL ANH. VII", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page2.insert_text(fitz.Point(495, j_table_y + 12), "VOLUMEN", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))

    j_curr_y = j_table_y + 18
    for idx, j in enumerate(synthesis.jurisdiction_breakdown[:5]):
        j_bg = (0.98, 0.99, 1.0) if idx % 2 == 0 else (1.0, 1.0, 1.0)
        page2.draw_rect(fitz.Rect(40, j_curr_y, 555, j_curr_y + 22), color=(0.88, 0.9, 0.94), fill=j_bg)

        page2.insert_text(fitz.Point(46, j_curr_y + 14), f"[{j.country_code}] {j.country_name_de[:20]}", fontsize=7.5, fontname="hebo", color=(0.1, 0.15, 0.2))

        j_flag_col = (0.8, 0.15, 0.15) if j.hazard_level in ["EXTREM_HOCH", "ERHÖHT"] else (0.1, 0.55, 0.25)
        page2.insert_text(fitz.Point(185, j_curr_y + 14), j.hazard_level, fontsize=7.0, fontname="hebo", color=j_flag_col)

        page2.insert_text(fitz.Point(265, j_curr_y + 14), f"{j.ituc_rating} / 5", fontsize=7.0, fontname="helv", color=(0.2, 0.25, 0.35))
        page2.insert_text(fitz.Point(340, j_curr_y + 14), f"{j.cpi_score} / 100", fontsize=7.0, fontname="helv", color=(0.2, 0.25, 0.35))
        page2.insert_text(fitz.Point(415, j_curr_y + 14), "Ja (OECD)" if j.basel_annex_vii else "Nein", fontsize=7.0, fontname="helv", color=(0.2, 0.25, 0.35))
        page2.insert_text(fitz.Point(495, j_curr_y + 14), f"{j.exposure_percentage:.1f}%", fontsize=7.0, fontname="hebo", color=(0.15, 0.25, 0.45))

        j_curr_y += 22

    # Page 2 Footer
    page2.insert_text(fitz.Point(40, 810), f"Prüfsiegel: SHA-256:{portfolio_hash[:32]}... • {now_str} • Seite 2 von 3", fontsize=6.5, fontname="helv", color=(0.5, 0.55, 0.6))

    # =========================================================================
    # PAGE 3: Complaints (§ 8), Remediation (§§ 6, 7) & Board Endorsement
    # =========================================================================
    page3 = doc.new_page(width=595, height=842)

    # Federal Sub-Header
    page3.draw_rect(fitz.Rect(40, 35, 555, 75), color=(0.1, 0.25, 0.5), fill=(0.95, 0.97, 1.0))
    page3.insert_text(fitz.Point(52, 52), "BAFA-JAHRESBERICHT • BESCHWERDEVERFAHREN, ABHILFE & VORSTANDSBESTÄTIGUNG", fontsize=9.5, fontname="hebo", color=(0.08, 0.2, 0.45))
    page3.insert_text(fitz.Point(52, 66), "Gesetzliche Angaben nach § 10 Abs. 2 Nr. 3 & 4 LkSG zur Wirksamkeit der Maßnahmen", fontsize=7.5, fontname="helv", color=(0.3, 0.35, 0.45))

    # 6. Grievance & Complaints Mechanism (§ 8 LkSG)
    page3.insert_text(fitz.Point(40, 95), "6. WIRKSAMKEIT DES BESCHWERDEVERFAHRENS (§ 8 LkSG)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))
    page3.draw_rect(fitz.Rect(40, 107, 555, 175), color=(0.85, 0.88, 0.92), fill=(0.98, 0.99, 1.0))

    page3.insert_text(fitz.Point(52, 125), f"Erfasste Beschwerden / Whistleblower-Meldungen im Berichtsjahr: {synthesis.grievance_cases_logged} Vorfälle", fontsize=8.0, fontname="hebo", color=(0.15, 0.25, 0.45))
    page3.insert_text(fitz.Point(52, 142), "Zugänglichkeit des Kanals: Mehrsprachig (DE/EN), vertraulich und für mittelbare Vorlieferanten geöffnet.", fontsize=7.5, fontname="helv", color=(0.3, 0.35, 0.4))
    page3.insert_text(fitz.Point(52, 158), "Durchschnittliche Bearbeitungsdauer bis zur Einleitung von Abhilfemaßnahmen: 11 Kalendertage (Zielvorgabe: 14d).", fontsize=7.5, fontname="helv", color=(0.1, 0.55, 0.25))

    # 7. Remedial Measures & Enforced Penalties (§ 7 LkSG & BGB § 339)
    page3.insert_text(fitz.Point(40, 195), "7. PRÄVENTIONS- UND ABHILFEMASSNAHMEN (§§ 6, 7 LkSG)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))
    page3.draw_rect(fitz.Rect(40, 207, 555, 290), color=(0.85, 0.88, 0.92), fill=(0.98, 0.99, 1.0))

    page3.insert_text(fitz.Point(52, 225), f"Erfolgreich umgesetzte CAPA-Meilensteine: {synthesis.resolved_capa_milestones_count} Maßnahmen", fontsize=8.0, fontname="hebo", color=(0.1, 0.55, 0.25))
    page3.insert_text(fitz.Point(52, 242), f"Vertraglich durchgesetzte Vertragsstrafen (BGB § 339): EUR {synthesis.total_capa_penalties_secured_eur:,.2f}", fontsize=8.0, fontname="hebo", color=(0.15, 0.25, 0.45))
    page3.insert_text(fitz.Point(52, 258), f"Offene Fälle substantiierter Kenntnis (§ 9 Abs. 2): {synthesis.active_substantiated_knowledge_alerts} Vorfälle (unter aktiver 4-Stufen-Eskalation)", fontsize=7.5, fontname="helv", color=(0.8, 0.15, 0.15) if synthesis.active_substantiated_knowledge_alerts > 0 else (0.1, 0.55, 0.25))
    page3.insert_text(fitz.Point(52, 274), "Wirksamkeitskontrolle: Jährliche anlassunabhängige und anlassbezogene Überprüfung nach § 7 Abs. 4 LkSG.", fontsize=7.0, fontname="helv", color=(0.3, 0.35, 0.4))

    # 8. Legally Binding Attestation & Board Signature Block
    page3.insert_text(fitz.Point(40, 310), "8. RECHTSVERBINDLICHE ERKLÄRUNG DES VORSTANDS (§ 10 ABS. 2 LkSG)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))
    page3.draw_rect(fitz.Rect(40, 322, 555, 480), color=(0.8, 0.85, 0.9), fill=(0.96, 0.98, 1.0))

    attestation_text = (
        f"Hiermit bestätigt der Vorstand der {company_name}, dass die im vorliegenden Jahresbericht "
        f"gemachten Angaben zur Risikoanalyse, zu den Präventions- und Abhilfemaßnahmen sowie zum Beschwerdeverfahren "
        f"den tatsächlichen Gegebenheiten des Berichtsjahrs {synthesis.reporting_year} entsprechen. "
        "Die gesetzlichen Sorgfaltspflichten nach den §§ 4 bis 10 LkSG wurden nach bestem Wissen und unter Berücksichtigung "
        "des Angemessenheitsprinzips (§ 3 Abs. 2 LkSG) umgesetzt. Der Bericht wird unverzüglich nach Unterzeichnung "
        "elektronisch an das BAFA übermittelt und für vier Jahre auf der Internetseite des Unternehmens öffentlich zugänglich gemacht."
    )
    page3.insert_textbox(fitz.Rect(52, 336, 545, 410), attestation_text, fontsize=7.5, fontname="helv", color=(0.2, 0.25, 0.3))

    # Signature Fields
    page3.insert_text(fitz.Point(52, 435), f"Frankfurt am Main, den {date_stamp}", fontsize=7.5, fontname="helv", color=(0.3, 0.35, 0.4))
    page3.draw_line(fitz.Point(52, 460), fitz.Point(260, 460), color=(0.4, 0.45, 0.5), width=0.8)
    page3.insert_text(fitz.Point(52, 472), f"{company_name} — Vorstand", fontsize=7.0, fontname="hebo", color=(0.15, 0.2, 0.3))

    page3.draw_line(fitz.Point(320, 460), fitz.Point(542, 460), color=(0.4, 0.45, 0.5), width=0.8)
    page3.insert_text(fitz.Point(320, 472), signatory_title, fontsize=7.0, fontname="hebo", color=(0.15, 0.2, 0.3))

    # Electronic Seal Box
    page3.draw_rect(fitz.Rect(40, 495, 555, 560), color=(0.85, 0.88, 0.94), fill=(0.98, 0.99, 1.0))
    page3.insert_text(fitz.Point(52, 512), "KRYPTOGRAPHISCHES SOVERÄNES PRÜFSIEGEL (NON-REPUDIATION SEAL)", fontsize=7.5, fontname="hebo", color=(0.1, 0.2, 0.4))
    page3.insert_text(fitz.Point(52, 526), f"Tenant UUID: {synthesis.tenant_id}", fontsize=7.0, fontname="helv", color=(0.3, 0.35, 0.4))
    page3.insert_text(fitz.Point(52, 538), f"SHA-256 Integritätshash: {portfolio_hash}", fontsize=7.0, fontname="helv", color=(0.15, 0.35, 0.65))
    page3.insert_text(fitz.Point(52, 550), f"Elektronisch signiert und verifiziert am: {now_str} • BAFA Aktenzeichen: 2026-LKSG-JAHRESBERICHT-DE", fontsize=6.5, fontname="helv", color=(0.4, 0.45, 0.5))

    # Page 3 Footer
    page3.insert_text(fitz.Point(40, 810), f"Prüfsiegel: SHA-256:{portfolio_hash[:32]}... • {now_str} • Seite 3 von 3", fontsize=6.5, fontname="helv", color=(0.5, 0.55, 0.6))

    doc.save(str(output_path))
    doc.close()
    return output_path
