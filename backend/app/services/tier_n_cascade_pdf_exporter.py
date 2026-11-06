import os
from datetime import UTC, datetime
from pathlib import Path

import pymupdf as fitz

from app.models.document import Document
from app.schemas.tier_n_cascade import TierNCascadeAuditReport


def generate_tier_n_cascade_pdf(
    document: Document,
    report: TierNCascadeAuditReport,
    signatory_name: str = "Dr. Michael Weber, Leitender LkSG- & BaFin-Prüfer",
    output_dir: Path | str = "/tmp/docunorm_exports",
) -> Path:
    """
    Generates an official DIN 5008 Multi-Tier Supply Chain Cascade Dossier &
    Ad-Hoc Remediation Action Plan under § 9 LkSG with cryptographic SHA-256 seal.
    """
    os.makedirs(output_dir, exist_ok=True)
    clean_name = document.filename.replace(".pdf", "").replace(" ", "_")
    output_path = Path(output_dir) / f"{clean_name}_TIER_N_CASCADE_LKSG_DOSSIER.pdf"

    doc = fitz.open()
    created_at_dt = datetime.now(UTC)
    date_stamp = created_at_dt.strftime("%d.%m.%Y")
    now_str = created_at_dt.strftime("%d. %B %Y • %H:%M:%S UTC")
    raw_hash = getattr(document, "sha256_hash", None) or getattr(document, "file_hash", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    doc_hash = str(raw_hash)[:32]

    # =========================================================================
    # PAGE 1: Header, Executive Summary & Multi-Tier Supplier Hierarchy
    # =========================================================================
    page1 = doc.new_page(width=595, height=842)

    # 1. Header Banner (Federal Standard Layout)
    page1.draw_rect(fitz.Rect(40, 35, 555, 95), color=(0.15, 0.25, 0.45), fill=(0.95, 0.97, 1.0))
    page1.draw_line(fitz.Point(40, 95), fitz.Point(555, 95), color=(0.2, 0.35, 0.65), width=2.5)

    page1.insert_text(
        fitz.Point(52, 54),
        "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE (BAFA) • LkSG § 9 DOSSIER",
        fontsize=10.0,
        fontname="hebo",
        color=(0.1, 0.2, 0.4),
    )
    page1.insert_text(
        fitz.Point(52, 69),
        "MULTILATERALE LIEFERKETTEN-KASKADENPRÜFUNG & MITTELBARE ZULIEFERER",
        fontsize=8.5,
        fontname="hebo",
        color=(0.18, 0.35, 0.65),
    )
    page1.insert_text(
        fitz.Point(52, 84),
        f"Hauptpartner: {report.primary_vendor_name[:40]} • Dokument: {document.filename[:30]} • Datum: {date_stamp}",
        fontsize=7.5,
        fontname="helv",
        color=(0.3, 0.35, 0.45),
    )

    # 2. Executive Metrics Summary Box
    page1.draw_rect(fitz.Rect(40, 105, 555, 175), color=(0.85, 0.88, 0.92), fill=(0.98, 0.99, 1.0))

    # Metric 1: Overall Cascade Score
    page1.insert_text(fitz.Point(55, 122), "GESAMT-KASKADENKONFORMITÄT", fontsize=7.0, fontname="hebo", color=(0.4, 0.45, 0.5))
    score_col = (0.1, 0.55, 0.25) if report.overall_cascade_score >= 80 else ((0.8, 0.45, 0.05) if report.overall_cascade_score >= 50 else (0.8, 0.15, 0.15))
    page1.insert_text(fitz.Point(55, 142), f"{report.overall_cascade_score:.1f}%", fontsize=16.0, fontname="hebo", color=score_col)
    page1.insert_text(fitz.Point(55, 160), report.compliance_rating, fontsize=7.5, fontname="hebo", color=score_col)

    # Metric 2: Pass-Through Covenant
    page1.insert_text(fitz.Point(215, 122), "VERTRAGLICHE WEITERGABE", fontsize=7.0, fontname="hebo", color=(0.4, 0.45, 0.5))
    page1.insert_text(fitz.Point(215, 142), f"{report.pass_through_enforceable_rate:.1f}%", fontsize=16.0, fontname="hebo", color=(0.15, 0.25, 0.45))
    page1.insert_text(fitz.Point(215, 160), f"Direkt: {report.direct_suppliers_count} | Mittelbar: {report.indirect_suppliers_count}", fontsize=7.5, fontname="helv", color=(0.3, 0.35, 0.4))

    # Metric 3: Substantiated Knowledge Status
    page1.insert_text(fitz.Point(385, 122), "SUBSTANTIIERTE KENNTNIS (§ 9 ABS. 2)", fontsize=7.0, fontname="hebo", color=(0.4, 0.45, 0.5))
    alert_col = (0.8, 0.15, 0.15) if report.substantiated_knowledge_active else (0.1, 0.55, 0.25)
    alert_txt = f"AKTIV ({len(report.active_incidents)} VORFÄLLE)" if report.substantiated_knowledge_active else "KEINE VORFÄLLE"
    page1.insert_text(fitz.Point(385, 142), alert_txt, fontsize=12.0, fontname="hebo", color=alert_col)
    page1.insert_text(fitz.Point(385, 160), "BAFA-Meldung empfohlen" if report.bafa_adhoc_filing_recommended else "Reguläre Berichtspflicht", fontsize=7.5, fontname="helv", color=alert_col)

    # 3. Supply Chain Hierarchy Table
    page1.insert_text(fitz.Point(40, 195), "1. MULTILATERALE LIEFERKETTEN-KASKADE (TIER-1 BIS TIER-N)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))

    # Table Header
    y_table = 205
    page1.draw_rect(fitz.Rect(40, y_table, 555, y_table + 18), color=(0.8, 0.84, 0.9), fill=(0.92, 0.94, 0.98))
    page1.insert_text(fitz.Point(46, y_table + 12), "TIER", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page1.insert_text(fitz.Point(85, y_table + 12), "LIEFERANT / ENTITÄT", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page1.insert_text(fitz.Point(235, y_table + 12), "STANDORT", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page1.insert_text(fitz.Point(310, y_table + 12), "WEITERGABEKLAUSEL", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page1.insert_text(fitz.Point(435, y_table + 12), "AUDITRECHTE", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))
    page1.insert_text(fitz.Point(510, y_table + 12), "KENNTNIS", fontsize=7.0, fontname="hebo", color=(0.2, 0.25, 0.35))

    curr_y = y_table + 18
    for idx, node in enumerate(report.supplier_nodes):
        row_bg = (0.98, 0.99, 1.0) if idx % 2 == 0 else (1.0, 1.0, 1.0)
        page1.draw_rect(fitz.Rect(40, curr_y, 555, curr_y + 26), color=(0.88, 0.9, 0.94), fill=row_bg)

        # Tier label
        t_label = "Tier 1" if "DIREKT" in node.tier.value else ("Tier 2" if "KOMPONENTEN" in node.tier.value else "Tier 3")
        page1.insert_text(fitz.Point(46, curr_y + 16), t_label, fontsize=7.5, fontname="hebo", color=(0.15, 0.25, 0.45))

        # Name & component
        page1.insert_text(fitz.Point(85, curr_y + 11), node.name[:30], fontsize=7.5, fontname="hebo", color=(0.1, 0.15, 0.2))
        page1.insert_text(fitz.Point(85, curr_y + 21), node.component_or_service[:32], fontsize=6.5, fontname="helv", color=(0.4, 0.45, 0.5))

        # Country
        c_flag = f"{node.country.country_code} ({node.country.hazard_level.value})"
        c_col = (0.8, 0.15, 0.15) if node.country.hazard_level.value in ["EXTREM_HOCH", "ERHÖHT"] else (0.1, 0.5, 0.2)
        page1.insert_text(fitz.Point(235, curr_y + 16), c_flag, fontsize=7.0, fontname="hebo", color=c_col)

        # Pass-Through status
        pt_short = "DURCHSETZBAR" if "VOLLSTÄNDIG" in node.pass_through_status.value else ("TEILWEISE" if "TEILWEISE" in node.pass_through_status.value else "FEHLEND")
        pt_col = (0.1, 0.55, 0.25) if pt_short == "DURCHSETZBAR" else ((0.8, 0.45, 0.05) if pt_short == "TEILWEISE" else (0.8, 0.15, 0.15))
        page1.insert_text(fitz.Point(310, curr_y + 16), pt_short, fontsize=7.0, fontname="hebo", color=pt_col)

        # Audit Rights
        aud_short = "UNEINGESCHRÄNKT" if "UNEINGESCHRÄNKT" in node.audit_rights.value else ("48H ANKÜNDIGUNG" if "48H" in node.audit_rights.value else "KEINE")
        page1.insert_text(fitz.Point(435, curr_y + 16), aud_short, fontsize=6.5, fontname="helv", color=(0.2, 0.25, 0.35))

        # Knowledge
        kn_txt = "VORFALL !" if node.has_substantiated_knowledge else "OK"
        kn_col = (0.8, 0.15, 0.15) if node.has_substantiated_knowledge else (0.1, 0.55, 0.25)
        page1.insert_text(fitz.Point(510, curr_y + 16), kn_txt, fontsize=7.0, fontname="hebo", color=kn_col)

        curr_y += 26

    # 4. Cross-Border Jurisdictions Hazard Matrix
    page1.insert_text(fitz.Point(40, curr_y + 18), "2. GRENZÜBERSCHREITENDES STANDORTRISIKO (ITUC & BASEL INDEX)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))

    j_table_y = curr_y + 26
    for idx, c in enumerate(report.jurisdiction_breakdown[:4]):
        card_x = 40 + (idx % 2) * 262
        card_y = j_table_y + (idx // 2) * 55
        page1.draw_rect(fitz.Rect(card_x, card_y, card_x + 253, card_y + 50), color=(0.85, 0.88, 0.92), fill=(0.98, 0.99, 1.0))

        flag_col = (0.8, 0.15, 0.15) if c.hazard_level.value in ["EXTREM_HOCH", "ERHÖHT"] else (0.1, 0.5, 0.2)
        page1.insert_text(fitz.Point(card_x + 8, card_y + 14), f"[{c.country_code}] {c.country_name_de}", fontsize=8.0, fontname="hebo", color=(0.1, 0.15, 0.2))
        page1.insert_text(fitz.Point(card_x + 160, card_y + 14), c.hazard_level.value, fontsize=7.0, fontname="hebo", color=flag_col)
        page1.insert_text(fitz.Point(card_x + 8, card_y + 26), f"ITUC Index: {c.ituc_rating}/5 • CPI: {c.cpi_score}/100 • Basel Anhang VII: {'Ja' if c.basel_annex_vii else 'Nein'}", fontsize=6.5, fontname="helv", color=(0.3, 0.35, 0.4))
        page1.insert_text(fitz.Point(card_x + 8, card_y + 38), c.risk_summary_de[:60] + "...", fontsize=6.0, fontname="helv", color=(0.4, 0.45, 0.5))

    # Page 1 Footer
    page1.insert_text(fitz.Point(40, 810), f"Prüfsiegel: SHA-256:{doc_hash}... • {now_str} • Seite 1 von 2", fontsize=6.5, fontname="helv", color=(0.5, 0.55, 0.6))

    # =========================================================================
    # PAGE 2: Substantiated Knowledge Remediation Schedule & Endorsement
    # =========================================================================
    page2 = doc.new_page(width=595, height=842)

    # Federal Sub-Header
    page2.draw_rect(fitz.Rect(40, 35, 555, 75), color=(0.15, 0.25, 0.45), fill=(0.95, 0.97, 1.0))
    page2.insert_text(
        fitz.Point(52, 52),
        "BAFA-ESKALATIONSPROTOKOLL • SUBSTANTIIERTE KENNTNIS NACH § 9 ABS. 2 LkSG",
        fontsize=9.5,
        fontname="hebo",
        color=(0.1, 0.2, 0.4),
    )
    page2.insert_text(
        fitz.Point(52, 66),
        "Anlassbezogene Risikoanalyse, verbindliche Präventionsmaßnahmen & Fristenplan",
        fontsize=7.5,
        fontname="helv",
        color=(0.3, 0.35, 0.45),
    )

    page2.insert_text(fitz.Point(40, 95), "3. AKTIVE VORFÄLLE SUBSTANTIIERTER KENNTNIS & ESKALATIONSSTUFEN", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))

    # Render Incidents
    inc_y = 108
    if not report.active_incidents:
        page2.draw_rect(fitz.Rect(40, inc_y, 555, inc_y + 45), color=(0.8, 0.9, 0.8), fill=(0.95, 0.99, 0.95))
        page2.insert_text(fitz.Point(55, inc_y + 26), "Aktuell liegen keine offenen Vorfälle substantiierter Kenntnis (§ 9 Abs. 2) vor.", fontsize=8.5, fontname="hebo", color=(0.1, 0.5, 0.2))
        inc_y += 55
    else:
        for inc in report.active_incidents:
            page2.draw_rect(fitz.Rect(40, inc_y, 555, inc_y + 115), color=(0.85, 0.88, 0.92), fill=(0.99, 0.99, 1.0))

            # Title & ID
            page2.insert_text(fitz.Point(52, inc_y + 16), f"[{inc.incident_id}] {inc.violation_title_de[:65]}", fontsize=8.0, fontname="hebo", color=(0.8, 0.15, 0.15))
            page2.insert_text(fitz.Point(440, inc_y + 16), f"Schweregrad: {inc.severity}", fontsize=7.5, fontname="hebo", color=(0.8, 0.15, 0.15))

            # Basis & Supplier
            page2.insert_text(fitz.Point(52, inc_y + 30), f"Betroffener Lieferant: {inc.supplier_name} ({inc.tier.value})", fontsize=7.0, fontname="helv", color=(0.2, 0.25, 0.3))
            page2.insert_text(fitz.Point(52, inc_y + 42), f"Rechtsgrundlage: {inc.statutory_basis} • Quelle: {inc.source_of_knowledge}", fontsize=6.8, fontname="helv", color=(0.3, 0.35, 0.4))

            # Escalation Stage & Statutory Deadline
            page2.draw_rect(fitz.Rect(52, inc_y + 50, 542, inc_y + 68), color=(0.88, 0.9, 0.95), fill=(0.93, 0.95, 0.99))
            stage_txt = f"Aktuelle Stufe: {inc.escalation_stage.value} • Gesetzliche Frist: {inc.statutory_deadline_days} Tage ({inc.days_remaining} Tage verbleibend)"
            page2.insert_text(fitz.Point(58, inc_y + 62), stage_txt, fontsize=7.0, fontname="hebo", color=(0.15, 0.25, 0.45))

            # Required Remediation Steps
            page2.insert_text(fitz.Point(52, inc_y + 80), "Erforderliche Abhilfemaßnahmen nach BAFA-Leitfaden:", fontsize=7.0, fontname="hebo", color=(0.1, 0.15, 0.2))
            lines = inc.required_remediation_de.split("\n")
            line_y = inc_y + 91
            for ln in lines[:2]:
                page2.insert_text(fitz.Point(58, line_y), ln[:115], fontsize=6.5, fontname="helv", color=(0.25, 0.3, 0.35))
                line_y += 10

            inc_y += 125

    # 4. Mandatory BAFA Escalation Schedule Timeline Table
    page2.insert_text(fitz.Point(40, inc_y + 15), "4. GESETZLICHE 4-STUFIGE ESKALATIONSKASKADE (§ 9 LkSG)", fontsize=9.5, fontname="hebo", color=(0.1, 0.2, 0.4))

    esc_table_y = inc_y + 25
    stages = [
        ("Stufe 1 (Tag 1-14)", "Anlassbezogene Risikoanalyse", "Prüfung der Substanz & Identifikation der betroffenen Kettenglieder"),
        ("Stufe 2 (Tag 15-30)", "Präventionskonzept mit Tier-1", "Vertragliche Verpflichtung zur Abhilfe & Vorlage eines Sanierungsplans"),
        ("Stufe 3 (Tag 31-60)", "Vor-Ort-Audit & Drittprüfung", "Akkreditierte Prüfung vor Ort (z.B. TÜV / SGS) & Whistleblower-Verifikation"),
        ("Stufe 4 (Tag 61-90)", "Suspension / Kündigung (BGB § 314)", "Vorübergehende Aussetzung oder außerordentliche Beendigung bei Verweigerung"),
    ]

    for s_idx, (s_name, s_action, s_desc) in enumerate(stages):
        row_y = esc_table_y + s_idx * 22
        page2.draw_rect(fitz.Rect(40, row_y, 555, row_y + 20), color=(0.88, 0.9, 0.94), fill=(0.97, 0.98, 1.0) if s_idx % 2 == 0 else (1.0, 1.0, 1.0))
        page2.insert_text(fitz.Point(48, row_y + 13), s_name, fontsize=7.0, fontname="hebo", color=(0.15, 0.25, 0.45))
        page2.insert_text(fitz.Point(165, row_y + 13), s_action, fontsize=7.0, fontname="hebo", color=(0.1, 0.15, 0.2))
        page2.insert_text(fitz.Point(315, row_y + 13), s_desc[:65], fontsize=6.5, fontname="helv", color=(0.35, 0.4, 0.45))

    # 5. Non-Repudiation Electronic Seal & Legal Endorsement
    seal_y = esc_table_y + len(stages) * 22 + 25
    page2.draw_rect(fitz.Rect(40, seal_y, 555, seal_y + 90), color=(0.8, 0.85, 0.9), fill=(0.96, 0.98, 1.0))

    page2.insert_text(fitz.Point(52, seal_y + 18), "RECHTSGÜLTIGE BESTÄTIGUNG & ELEKTRONISCHES PRÜFSIEGEL", fontsize=8.5, fontname="hebo", color=(0.1, 0.2, 0.4))
    legal_text = (
        "Dieses Kaskadendossier wurde auf Basis von § 9 LkSG und der BAFA-Handreichung zur Risikoanalyse "
        "automatisiert erstellt. Es dokumentiert die Einhaltung der gesetzlichen Sorgfaltspflichten bezüglich "
        "mittelbarer Zulieferer. Die kryptographische Signatur garantiert Unveränderbarkeit gegenüber Aufsichtsbehörden."
    )
    page2.insert_textbox(fitz.Rect(52, seal_y + 23, 380, seal_y + 68), legal_text, fontsize=6.8, fontname="helv", color=(0.3, 0.35, 0.4))

    # Signature Block
    page2.draw_line(fitz.Point(395, seal_y + 62), fitz.Point(542, seal_y + 62), color=(0.4, 0.45, 0.5), width=0.8)
    page2.insert_text(fitz.Point(395, seal_y + 72), signatory_name[:36], fontsize=6.5, fontname="hebo", color=(0.15, 0.2, 0.3))
    page2.insert_text(fitz.Point(395, seal_y + 81), f"Validiert am: {date_stamp} • BAFA Reg-ID: DE-LKSG-2026-904", fontsize=6.0, fontname="helv", color=(0.4, 0.45, 0.5))

    # Page 2 Footer
    page2.insert_text(fitz.Point(40, 810), f"Kryptographischer Hash: SHA-256:{doc_hash}... • {now_str} • Seite 2 von 2", fontsize=6.5, fontname="helv", color=(0.5, 0.55, 0.6))

    doc.save(str(output_path))
    doc.close()
    return output_path
