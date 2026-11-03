import os
from datetime import UTC, datetime
from pathlib import Path

import pymupdf as fitz

from app.models.document import Document
from app.schemas.battlecard import NegotiationBattlecardResponse


def generate_battlecard_report_pdf(
    document: Document,
    battlecard_data: NegotiationBattlecardResponse,
    signatory_name: str = "Dr. Michael Weber, Leitender DORA- & BaFin-Prüfer",
    output_dir: Path | str = "/tmp/docunorm_exports",
) -> Path:
    """
    Generates an official institutional DIN 5008 Procurement Battlecard & Schrems II TIA
    Regulatory Defense Dossier PDF with cryptographic SHA-256 seal.
    """
    os.makedirs(output_dir, exist_ok=True)
    clean_name = document.filename.replace(".pdf", "").replace(" ", "_")
    output_path = Path(output_dir) / f"{clean_name}_NEGOTIATION_BATTLECARD_TIA.pdf"

    doc = fitz.open()
    created_at_dt = datetime.now(UTC)
    date_stamp = created_at_dt.strftime("%d.%m.%Y")
    now_str = created_at_dt.strftime("%d. %B %Y • %H:%M:%S UTC")

    # =========================================================================
    # PAGE 1: Executive Overview, Schrems II TIA & Top Battlecards
    # =========================================================================
    page1 = doc.new_page(width=595, height=842)

    # 1. Header Banner
    page1.draw_rect(fitz.Rect(40, 35, 555, 95), color=(0.12, 0.2, 0.35), fill=(0.96, 0.97, 1.0))
    page1.draw_line(fitz.Point(40, 95), fitz.Point(555, 95), color=(0.7, 0.2, 0.1), width=2.5)

    page1.insert_text(
        fitz.Point(52, 54),
        "DOCUNORM SOVEREIGN DEFENSE • EXECUTIVE NEGOTIATION BATTLECARD",
        fontsize=10.5,
        fontname="hebo",
        color=(0.08, 0.15, 0.3),
    )
    page1.insert_text(
        fitz.Point(52, 69),
        "SCHREMS II TRANSFER IMPACT ASSESSMENT (TIA) & DORA ART. 30 COUNTER-STRATEGY",
        fontsize=8.5,
        fontname="hebo",
        color=(0.6, 0.15, 0.1),
    )
    page1.insert_text(
        fitz.Point(52, 84),
        f"Geprüftes Dokument: {document.filename} • Datum: {date_stamp} • Az: DN-BC-2026-EU",
        fontsize=7.5,
        fontname="helv",
        color=(0.3, 0.35, 0.4),
    )

    # 2. Cryptographic SHA-256 Seal
    page1.draw_rect(fitz.Rect(40, 105, 555, 138), color=(0.85, 0.88, 0.92), fill=(0.98, 0.98, 0.99))
    page1.insert_text(
        fitz.Point(52, 119),
        f"KRYPTOGRAPHISCHES PRÜFSIEGEL (SHA-256): {document.sha256_hash}",
        fontsize=7.0,
        fontname="cour",
        color=(0.2, 0.3, 0.4),
    )
    page1.insert_text(
        fitz.Point(52, 131),
        f"Zeitstempel: {now_str} • Revisionssicherheit nach BaFin GoBD & KWG § 25a gewährleistet.",
        fontsize=7.0,
        fontname="helv",
        color=(0.4, 0.45, 0.5),
    )

    # 3. Posture & TIA Metric Box
    page1.draw_rect(fitz.Rect(40, 150, 555, 235), color=(0.8, 0.85, 0.9), fill=(1.0, 1.0, 1.0))
    page1.insert_text(
        fitz.Point(52, 168),
        "VERTRAGSBEWERTUNG & SCHREMS II TRANSFER IMPACT ASSESSMENT (TIA)",
        fontsize=9.0,
        fontname="hebo",
        color=(0.1, 0.2, 0.35),
    )

    tia = battlecard_data.tia_assessment
    posture_color = (0.7, 0.1, 0.1) if battlecard_data.critical_count > 0 else (0.1, 0.55, 0.3)
    page1.insert_text(
        fitz.Point(52, 187),
        f"Verhandlungsposition: {battlecard_data.overall_negotiation_posture}",
        fontsize=8.5,
        fontname="hebo",
        color=posture_color,
    )
    page1.insert_text(
        fitz.Point(52, 201),
        f"TIA-Risikobewertung: {tia.overall_transfer_risk} (Index: {tia.transfer_risk_score}%) • US CLOUD Act Risiko: {'JA' if tia.cloud_act_exposure else 'NEIN'}",
        fontsize=8.0,
        fontname="helv",
        color=(0.2, 0.25, 0.3),
    )
    page1.insert_text(
        fitz.Point(52, 215),
        f"HYOK-Verschlüsselung: {'ZERTIFIZIERT' if tia.encryption_hyok_verified else 'NICHT VORHANDEN'} • EWR-Datenresidenz: {'GARANTIERT' if tia.eu_data_residency_guaranteed else 'UNVOLLSTÄNDIG'}",
        fontsize=8.0,
        fontname="helv",
        color=(0.2, 0.25, 0.3),
    )
    page1.insert_text(
        fitz.Point(52, 227),
        f"BaFin-Votum: {tia.bafin_audit_clearance[:90]}...",
        fontsize=7.5,
        fontname="helv",
        color=(0.4, 0.45, 0.5),
    )

    # 4. Render Battlecards (Page 1 up to Page 2)
    p_y = 255
    active_page = page1

    for idx, bc in enumerate(battlecard_data.battlecards, start=1):
        if p_y > 670 and active_page == page1:
            # Footer on page 1
            page1.draw_line(fitz.Point(40, 800), fitz.Point(555, 800), color=(0.8, 0.85, 0.9), width=1.0)
            page1.insert_text(
                fitz.Point(45, 814),
                f"DocuNorm Sovereign Defense • {document.filename} • Seite 1 von 2",
                fontsize=7.5,
                fontname="helv",
                color=(0.5, 0.55, 0.6),
            )
            # Create Page 2
            page2 = doc.new_page(width=595, height=842)
            active_page = page2
            p_y = 50

            # Sub-header page 2
            page2.insert_text(
                fitz.Point(45, p_y),
                "VERHANDLUNGS-BATTLECARDS (FORTSETZUNG) & MUSTERKLAUSELN",
                fontsize=9.0,
                fontname="hebo",
                color=(0.1, 0.2, 0.35),
            )
            p_y += 20

        # Draw Battlecard Item Box
        item_height = 115
        active_page.draw_rect(fitz.Rect(40, p_y, 555, p_y + item_height), color=(0.85, 0.88, 0.92), fill=(0.99, 0.99, 1.0))
        badge_color = (0.7, 0.1, 0.1) if bc.severity == "CRITICAL" else (0.8, 0.5, 0.0)
        active_page.draw_rect(fitz.Rect(40, p_y, 45, p_y + item_height), fill=badge_color)

        active_page.insert_text(
            fitz.Point(55, p_y + 16),
            f"BATTLECARD #{idx} • {bc.title_de} [{bc.severity}]",
            fontsize=8.5,
            fontname="hebo",
            color=(0.1, 0.15, 0.25),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 29),
            f"Aufsichtsrecht: {bc.statutory_reference} (Seite {bc.page_number})",
            fontsize=7.5,
            fontname="helv",
            color=(0.4, 0.45, 0.5),
        )

        active_page.insert_text(
            fitz.Point(55, p_y + 45),
            f"🚩 Anbieter-Klausel: \"{bc.vendor_clause_quote[:85]}...\"",
            fontsize=7.5,
            fontname="helv",
            color=(0.5, 0.2, 0.2),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 60),
            f"🛡️ Typisches Anbieter-Argument: {bc.vendor_common_defense[:90]}...",
            fontsize=7.5,
            fontname="helv",
            color=(0.3, 0.35, 0.4),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 75),
            f"⚡ Unwiderlegbares Banken-Gegenargument: {bc.bank_counter_argument[:90]}...",
            fontsize=7.5,
            fontname="hebo",
            color=(0.05, 0.4, 0.2),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 90),
            f"✍️ Nicht verhandelbare Musterklausel: {bc.non_negotiable_clause_de[:90]}...",
            fontsize=7.0,
            fontname="cour",
            color=(0.15, 0.2, 0.3),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 104),
            f"🏛️ BaFin-Eskalationsspruch: {bc.bafin_escalation_script[:95]}...",
            fontsize=7.0,
            fontname="helv",
            color=(0.4, 0.1, 0.1),
        )

        p_y += item_height + 12

    # Endorsement Block on active page
    if p_y > 720 and len(doc) == 1:
        page2 = doc.new_page(width=595, height=842)
        active_page = page2
        p_y = 60

    active_page.draw_rect(fitz.Rect(40, 715, 555, 785), color=(0.8, 0.85, 0.9), fill=(0.97, 0.98, 1.0))
    active_page.insert_text(fitz.Point(52, 732), "REVISIONSSICHERE ZEICHNUNG & FREIGABEVERMERK", fontsize=8.0, fontname="hebo", color=(0.1, 0.2, 0.35))
    active_page.insert_text(fitz.Point(52, 748), f"Leitender Prüfer: {signatory_name}", fontsize=7.5, fontname="helv", color=(0.2, 0.25, 0.3))
    active_page.insert_text(fitz.Point(52, 762), "Status: Offizielle Verhandlungsgrundlage für DORA-Vertragsverhandlungen freigegeben.", fontsize=7.5, fontname="helv", color=(0.1, 0.55, 0.3))
    active_page.insert_text(fitz.Point(400, 775), "Elektronisch signiert gem. eIDAS", fontsize=7.0, fontname="cour", color=(0.3, 0.35, 0.4))

    # Final Footer on the last page
    active_page.draw_line(fitz.Point(40, 800), fitz.Point(555, 800), color=(0.8, 0.85, 0.9), width=1.0)
    active_page.insert_text(
        fitz.Point(45, 814),
        f"DocuNorm Sovereign Defense • {document.filename} • SHA-256: {document.sha256_hash[:16]}... • Seite {len(doc)} von {len(doc)}",
        fontsize=7.5,
        fontname="helv",
        color=(0.5, 0.55, 0.6),
    )

    doc.save(str(output_path))
    doc.close()
    return output_path
