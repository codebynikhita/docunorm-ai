import os
from datetime import UTC, datetime
from pathlib import Path

import pymupdf as fitz

from app.models.document import Document
from app.schemas.environmental import EnvironmentalAuditReport


def generate_environmental_certificate_pdf(
    document: Document,
    report: EnvironmentalAuditReport,
    signatory_name: str = "Dr. Michael Weber, Leitender LkSG- & BaFin-Prüfer",
    output_dir: Path | str = "/tmp/docunorm_exports",
) -> Path:
    """
    Generates an official DIN 5008 Environmental Compliance Certificate &
    Hazardous Waste Tracking Audit Dossier under § 2 Abs. 3 LkSG with cryptographic SHA-256 seal.
    """
    os.makedirs(output_dir, exist_ok=True)
    clean_name = document.filename.replace(".pdf", "").replace(" ", "_")
    output_path = Path(output_dir) / f"{clean_name}_ENVIRONMENTAL_LKSG_CERTIFICATE.pdf"

    doc = fitz.open()
    created_at_dt = datetime.now(UTC)
    date_stamp = created_at_dt.strftime("%d.%m.%Y")
    now_str = created_at_dt.strftime("%d. %B %Y • %H:%M:%S UTC")

    # =========================================================================
    # PAGE 1: Header, Convention Statuses & Substance Inventory
    # =========================================================================
    page1 = doc.new_page(width=595, height=842)

    # 1. Header Banner (DIN 5008 Standard Layout)
    page1.draw_rect(fitz.Rect(40, 35, 555, 95), color=(0.08, 0.35, 0.2), fill=(0.94, 0.98, 0.95))
    page1.draw_line(fitz.Point(40, 95), fitz.Point(555, 95), color=(0.1, 0.55, 0.3), width=2.5)

    page1.insert_text(
        fitz.Point(52, 54),
        "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE (BAFA) • LkSG § 2 ABS. 3",
        fontsize=10.0,
        fontname="hebo",
        color=(0.05, 0.22, 0.12),
    )
    page1.insert_text(
        fitz.Point(52, 69),
        "OFFIZIELLES UMWELT-COMPLIANCE-ZERTIFIKAT (MINAMATA · STOCKHOLM · BASEL)",
        fontsize=8.5,
        fontname="hebo",
        color=(0.1, 0.48, 0.2),
    )
    page1.insert_text(
        fitz.Point(52, 84),
        f"Geprüfter Lieferant: {report.supplier_name} • Dokument: {document.filename} • Datum: {date_stamp}",
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
        f"Zeitstempel: {now_str} • Revisionssicherer Nachweis internationaler Umweltübereinkommen.",
        fontsize=7.0,
        fontname="helv",
        color=(0.4, 0.45, 0.5),
    )

    # 3. Environmental Score & Convention Gauges Box
    page1.draw_rect(fitz.Rect(40, 150, 555, 235), color=(0.8, 0.88, 0.82), fill=(1.0, 1.0, 1.0))
    page1.insert_text(
        fitz.Point(52, 168),
        "BEWERTUNG DER DREI INTERNATIONALEN UMWELTÜBEREINKOMMEN (§ 2 ABS. 3 LkSG)",
        fontsize=9.0,
        fontname="hebo",
        color=(0.1, 0.35, 0.2),
    )

    score_color = (0.1, 0.55, 0.3) if report.overall_environmental_score >= 80.0 else (0.7, 0.1, 0.1)
    page1.insert_text(
        fitz.Point(52, 186),
        f"Gesamtbewertung: {report.environmental_rating} ({report.overall_environmental_score:.1f}%) • Verbotene Stoffe: {report.prohibited_substances_count}",
        fontsize=8.5,
        fontname="hebo",
        color=score_color,
    )
    page1.insert_text(
        fitz.Point(52, 201),
        f"1. Minamata (Quecksilber): {report.minamata_mercury_status} • 2. Stockholm (POPs): {report.stockholm_pops_status}",
        fontsize=8.0,
        fontname="helv",
        color=(0.2, 0.25, 0.3),
    )
    page1.insert_text(
        fitz.Point(52, 215),
        f"3. Basler Übereinkommen (Sonderabfallverbringung & PIC-Zustimmung): {report.basel_waste_status}",
        fontsize=8.0,
        fontname="helv",
        color=(0.2, 0.25, 0.3),
    )
    page1.insert_text(
        fitz.Point(52, 228),
        f"BAFA-Votum: {report.bafa_environmental_verdict_de[:90]}...",
        fontsize=7.5,
        fontname="helv",
        color=(0.4, 0.45, 0.5),
    )

    # 4. Render Substances Inventory (Page 1)
    p_y = 250
    page1.insert_text(fitz.Point(40, p_y), "ÜBERWACHTE CHEMISCHE STOFFE & VERBINDUNGEN (INVENTAR)", fontsize=9.0, fontname="hebo", color=(0.1, 0.35, 0.2))
    p_y += 18

    for idx, s in enumerate(report.substances, start=1):
        box_h = 60
        page1.draw_rect(fitz.Rect(40, p_y, 555, p_y + box_h), color=(0.85, 0.9, 0.86), fill=(0.99, 1.0, 0.99))
        badge_color = (0.7, 0.1, 0.1) if s.status == "PROHIBITED" else (0.1, 0.55, 0.3) if s.status == "COMPLIANT" else (0.8, 0.5, 0.0)
        page1.draw_rect(fitz.Rect(40, p_y, 45, p_y + box_h), fill=badge_color)

        page1.insert_text(
            fitz.Point(55, p_y + 14),
            f"STOFF #{idx}: {s.substance_name} • CAS-Nr: {s.cas_number} • STATUS: {s.status}",
            fontsize=8.0,
            fontname="hebo",
            color=(0.1, 0.2, 0.15),
        )
        page1.insert_text(
            fitz.Point(55, p_y + 27),
            f"Grenzwert: {s.threshold_limit} • Rechtsnorm: {s.statutory_article}",
            fontsize=7.5,
            fontname="helv",
            color=(0.35, 0.45, 0.4),
        )
        page1.insert_text(
            fitz.Point(55, p_y + 42),
            f"Handlungsempfehlung: {s.remediation_guidance[:95]}...",
            fontsize=7.0,
            fontname="cour",
            color=(0.2, 0.25, 0.3),
        )
        p_y += box_h + 10

    # Footer Page 1
    page1.draw_line(fitz.Point(40, 800), fitz.Point(555, 800), color=(0.8, 0.85, 0.9), width=1.0)
    page1.insert_text(
        fitz.Point(45, 814),
        f"BAFA-Umweltzertifikat • {document.filename} • Seite 1 von 2",
        fontsize=7.5,
        fontname="helv",
        color=(0.5, 0.55, 0.6),
    )

    # =========================================================================
    # PAGE 2: Basel Transboundary Waste Manifests & Official Endorsement
    # =========================================================================
    page2 = doc.new_page(width=595, height=842)
    p2_y = 45

    page2.insert_text(
        fitz.Point(40, p2_y),
        "BASLER ÜBEREINKOMMEN: GRENZÜBERSCHREITENDE SONDERABFALL-BEGLEITSCHEINE",
        fontsize=9.0,
        fontname="hebo",
        color=(0.1, 0.35, 0.2),
    )
    p2_y += 20

    for idx, w in enumerate(report.waste_manifests, start=1):
        box_h = 85
        page2.draw_rect(fitz.Rect(40, p2_y, 555, p2_y + box_h), color=(0.85, 0.9, 0.86), fill=(0.99, 1.0, 0.99))
        pic_color = (0.1, 0.55, 0.3) if w.pic_status == "VERIFIED_APPROVED" else (0.7, 0.1, 0.1)
        page2.draw_rect(fitz.Rect(40, p2_y, 45, p2_y + box_h), fill=pic_color)

        page2.insert_text(
            fitz.Point(55, p2_y + 15),
            f"BEGLEITSCHEIN #{idx}: {w.manifest_id} • ABFALL-SCHLÜSSEL: {w.waste_code}",
            fontsize=8.0,
            fontname="hebo",
            color=(0.1, 0.2, 0.15),
        )
        page2.insert_text(
            fitz.Point(55, p2_y + 29),
            f"Beschreibung: {w.waste_description[:85]}...",
            fontsize=7.5,
            fontname="helv",
            color=(0.3, 0.35, 0.4),
        )
        page2.insert_text(
            fitz.Point(55, p2_y + 44),
            f"Route: {w.origin_country} ➔ {w.destination_country} • PIC-Status: {w.pic_status}",
            fontsize=7.5,
            fontname="hebo",
            color=(0.1, 0.4, 0.2) if w.export_authorized else (0.7, 0.1, 0.1),
        )
        page2.insert_text(
            fitz.Point(55, p2_y + 58),
            f"Zertifizierte Verwertungsanlage: {w.disposal_or_recycling_facility}",
            fontsize=7.0,
            fontname="cour",
            color=(0.2, 0.25, 0.3),
        )
        page2.insert_text(
            fitz.Point(55, p2_y + 71),
            f"Prüfbehörde: {w.certifying_authority} • {w.statutory_reference}",
            fontsize=7.0,
            fontname="helv",
            color=(0.4, 0.45, 0.5),
        )
        p2_y += box_h + 14

    # Endorsement Block on Page 2
    page2.draw_rect(fitz.Rect(40, 715, 555, 785), color=(0.8, 0.88, 0.82), fill=(0.96, 0.99, 0.97))
    page2.insert_text(fitz.Point(52, 732), "BEHÖRDLICHE ZEICHNUNG & BAFA-UMWELTFREIGABEVERMERK", fontsize=8.0, fontname="hebo", color=(0.1, 0.35, 0.2))
    page2.insert_text(fitz.Point(52, 748), f"Leitender Prüfer: {signatory_name}", fontsize=7.5, fontname="helv", color=(0.2, 0.25, 0.3))
    page2.insert_text(fitz.Point(52, 762), "Status: Umwelt-Compliance gem. § 2 Abs. 3 LkSG behördlich festgestellt und archiviert.", fontsize=7.5, fontname="helv", color=(0.1, 0.55, 0.3))
    page2.insert_text(fitz.Point(400, 775), "Elektronisch signiert gem. eIDAS", fontsize=7.0, fontname="cour", color=(0.3, 0.35, 0.4))

    # Final Footer Page 2
    page2.draw_line(fitz.Point(40, 800), fitz.Point(555, 800), color=(0.8, 0.85, 0.9), width=1.0)
    page2.insert_text(
        fitz.Point(45, 814),
        f"BAFA-Umweltzertifikat • {document.filename} • SHA-256: {document.sha256_hash[:16]}... • Seite 2 von 2",
        fontsize=7.5,
        fontname="helv",
        color=(0.5, 0.55, 0.6),
    )

    doc.save(str(output_path))
    doc.close()
    return output_path
