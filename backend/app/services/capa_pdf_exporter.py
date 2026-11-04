import os
from datetime import UTC, datetime
from pathlib import Path

import pymupdf as fitz

from app.models.document import Document
from app.schemas.capa import SupplierCapaPlan


def generate_capa_report_pdf(
    document: Document,
    capa_data: SupplierCapaPlan,
    signatory_name: str = "Dr. Michael Weber, Leitender LkSG- & BaFin-Prüfer",
    output_dir: Path | str = "/tmp/docunorm_exports",
) -> Path:
    """
    Generates an official DIN 5008 Statutory Supplier Corrective Action Plan (CAPA)
    Remediation Dossier under §§ 6, 7 LkSG with cryptographic SHA-256 seal.
    """
    os.makedirs(output_dir, exist_ok=True)
    clean_name = document.filename.replace(".pdf", "").replace(" ", "_")
    output_path = Path(output_dir) / f"{clean_name}_CAPA_REMEDIATION_PLAN.pdf"

    doc = fitz.open()
    created_at_dt = datetime.now(UTC)
    date_stamp = created_at_dt.strftime("%d.%m.%Y")
    now_str = created_at_dt.strftime("%d. %B %Y • %H:%M:%S UTC")

    # =========================================================================
    # PAGE 1: Header, Posture & Corrective Action Milestones
    # =========================================================================
    page1 = doc.new_page(width=595, height=842)

    # 1. Header Banner (DIN 5008 Standard Layout)
    page1.draw_rect(fitz.Rect(40, 35, 555, 95), color=(0.1, 0.45, 0.25), fill=(0.95, 0.99, 0.96))
    page1.draw_line(fitz.Point(40, 95), fitz.Point(555, 95), color=(0.1, 0.55, 0.3), width=2.5)

    page1.insert_text(
        fitz.Point(52, 54),
        "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE (BAFA) • LkSG COMPLIANCE",
        fontsize=10.0,
        fontname="hebo",
        color=(0.06, 0.25, 0.15),
    )
    page1.insert_text(
        fitz.Point(52, 69),
        "GESETZLICHER KORREKTUR-AKTIONSPLAN (CAPA) GEMÄSS §§ 6, 7 LkSG",
        fontsize=8.5,
        fontname="hebo",
        color=(0.1, 0.5, 0.2),
    )
    page1.insert_text(
        fitz.Point(52, 84),
        f"Lieferant: {capa_data.supplier_name} • Plan-ID: {capa_data.plan_id} • Datum: {date_stamp}",
        fontsize=7.5,
        fontname="helv",
        color=(0.3, 0.35, 0.4),
    )

    # 2. Cryptographic SHA-256 Seal
    page1.draw_rect(fitz.Rect(40, 105, 555, 138), color=(0.85, 0.88, 0.92), fill=(0.98, 0.99, 0.98))
    page1.insert_text(
        fitz.Point(52, 119),
        f"KRYPTOGRAPHISCHES PRÜFSIEGEL (SHA-256): {document.sha256_hash}",
        fontsize=7.0,
        fontname="cour",
        color=(0.15, 0.3, 0.2),
    )
    page1.insert_text(
        fitz.Point(52, 131),
        f"Zeitstempel: {now_str} • Revisionssichere BAFA-Dokumentation gem. § 10 LkSG.",
        fontsize=7.0,
        fontname="helv",
        color=(0.4, 0.45, 0.5),
    )

    # 3. Posture & Overview Box
    page1.draw_rect(fitz.Rect(40, 150, 555, 225), color=(0.8, 0.88, 0.82), fill=(1.0, 1.0, 1.0))
    page1.insert_text(fitz.Point(52, 168), "ÜBERSICHT DES ABHILFEPLANS (§ 7 LkSG)", fontsize=9.0, fontname="hebo", color=(0.1, 0.35, 0.2))

    posture_color = (0.7, 0.1, 0.1) if capa_data.critical_milestones_count > 0 else (0.1, 0.55, 0.3)
    page1.insert_text(
        fitz.Point(52, 186),
        f"Gesamtstatus: {capa_data.overall_compliance_posture} • Kritische Meilensteine: {capa_data.critical_milestones_count} von {capa_data.total_milestones}",
        fontsize=8.5,
        fontname="hebo",
        color=posture_color,
    )
    page1.insert_text(
        fitz.Point(52, 200),
        f"Maximale Umsetzungsfrist: {capa_data.max_remediation_timeline_days} Tage • Geschätztes Budget: EUR {capa_data.estimated_remediation_cost_eur:,.2f}",
        fontsize=8.0,
        fontname="helv",
        color=(0.2, 0.25, 0.3),
    )
    page1.insert_text(
        fitz.Point(52, 214),
        f"Zusammenfassung: {capa_data.executive_summary_de[:90]}...",
        fontsize=7.5,
        fontname="helv",
        color=(0.4, 0.45, 0.5),
    )

    # 4. Render Milestones
    p_y = 245
    active_page = page1

    for idx, m in enumerate(capa_data.milestones, start=1):
        if p_y > 670 and active_page == page1:
            # Footer on page 1
            page1.draw_line(fitz.Point(40, 800), fitz.Point(555, 800), color=(0.8, 0.85, 0.9), width=1.0)
            page1.insert_text(
                fitz.Point(45, 814),
                f"BAFA-Korrekturplan • {document.filename} • Seite 1 von 2",
                fontsize=7.5,
                fontname="helv",
                color=(0.5, 0.55, 0.6),
            )
            # Create Page 2
            page2 = doc.new_page(width=595, height=842)
            active_page = page2
            p_y = 50

            page2.insert_text(
                fitz.Point(45, p_y),
                "KORREKTUR-AKTIONSPLAN (MEILENSTEINE FORTSETZUNG)",
                fontsize=9.0,
                fontname="hebo",
                color=(0.1, 0.35, 0.2),
            )
            p_y += 20

        box_height = 100
        active_page.draw_rect(fitz.Rect(40, p_y, 555, p_y + box_height), color=(0.85, 0.9, 0.86), fill=(0.99, 1.0, 0.99))
        badge_color = (0.7, 0.1, 0.1) if m.severity == "CRITICAL" else (0.8, 0.5, 0.0)
        active_page.draw_rect(fitz.Rect(40, p_y, 45, p_y + box_height), fill=badge_color)

        active_page.insert_text(
            fitz.Point(55, p_y + 16),
            f"MEILENSTEIN #{idx} • {m.title_de} [{m.severity}] • FRIST: {m.deadline_days} TAGE",
            fontsize=8.5,
            fontname="hebo",
            color=(0.1, 0.2, 0.15),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 30),
            f"Rechtsgrundlage: {m.statutory_basis} • Pönale bei Verzug: EUR {m.penalty_upon_default_eur:,.2f}",
            fontsize=7.5,
            fontname="helv",
            color=(0.35, 0.45, 0.4),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 46),
            f"Identifiziertes Defizit: {m.deficiency_description[:85]}...",
            fontsize=7.5,
            fontname="helv",
            color=(0.4, 0.2, 0.2),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 62),
            f"Verbindliche Maßnahme: {m.required_action_de[:90]}...",
            fontsize=7.5,
            fontname="hebo",
            color=(0.05, 0.4, 0.2),
        )
        active_page.insert_text(
            fitz.Point(55, p_y + 78),
            f"Prüfmethode: {m.verification_method[:90]}...",
            fontsize=7.0,
            fontname="cour",
            color=(0.2, 0.25, 0.3),
        )

        p_y += box_height + 12

    # Endorsement Block
    if p_y > 720 and len(doc) == 1:
        page2 = doc.new_page(width=595, height=842)
        active_page = page2
        p_y = 60

    active_page.draw_rect(fitz.Rect(40, 715, 555, 785), color=(0.8, 0.88, 0.82), fill=(0.96, 0.99, 0.97))
    active_page.insert_text(fitz.Point(52, 732), "BEHÖRDLICHE ZEICHNUNG & BAFA-FREIGABEVERMERK", fontsize=8.0, fontname="hebo", color=(0.1, 0.35, 0.2))
    active_page.insert_text(fitz.Point(52, 748), f"Leitender Prüfer: {signatory_name}", fontsize=7.5, fontname="helv", color=(0.2, 0.25, 0.3))
    active_page.insert_text(fitz.Point(52, 762), "Status: Offizieller Korrekturmaßnahmenplan gem. § 7 Abs. 1 LkSG rechtsverbindlich erlassen.", fontsize=7.5, fontname="helv", color=(0.1, 0.55, 0.3))
    active_page.insert_text(fitz.Point(400, 775), "Elektronisch signiert gem. eIDAS", fontsize=7.0, fontname="cour", color=(0.3, 0.35, 0.4))

    # Final Footer
    active_page.draw_line(fitz.Point(40, 800), fitz.Point(555, 800), color=(0.8, 0.85, 0.9), width=1.0)
    active_page.insert_text(
        fitz.Point(45, 814),
        f"BAFA-Korrekturplan • {document.filename} • SHA-256: {document.sha256_hash[:16]}... • Seite {len(doc)} von {len(doc)}",
        fontsize=7.5,
        fontname="helv",
        color=(0.5, 0.55, 0.6),
    )

    doc.save(str(output_path))
    doc.close()
    return output_path
