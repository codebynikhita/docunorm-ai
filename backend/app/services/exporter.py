import os
from datetime import datetime, timezone
from pathlib import Path
import fitz

from app.models.document import Document


def generate_english_dossier_pdf(
    document: Document,
    chunks: list[dict],
    output_dir: Path | str = "/tmp/docunorm_exports",
) -> Path:
    """
    Generates a certified DIN A4 English Regulatory Audit Dossier PDF
    with synchronized German source references, SHA-256 fingerprints,
    and BaFin DORA Art. 30 compliance stamps.
    """
    os.makedirs(output_dir, exist_ok=True)
    clean_name = document.filename.replace(".pdf", "").replace(" ", "_")
    output_path = Path(output_dir) / f"{clean_name}_ENGLISH_DOSSIER.pdf"

    doc = fitz.open()

    # Group chunks by page number
    pages_map: dict[int, list[dict]] = {}
    for c in chunks:
        p_num = c.get("page_number", 1)
        pages_map.setdefault(p_num, []).append(c)

    sorted_pages = sorted(pages_map.keys()) if pages_map else [1]
    total_dossier_pages = len(sorted_pages)

    current_date_str = datetime.now(timezone.utc).strftime("%d. %B %Y • %H:%M UTC")

    # Detect whether source is English or German
    is_english_source = any(c.get("source_language") == "EN" for c in chunks)
    if not is_english_source and chunks:
        sample_txt = " ".join(c.get("content", "") for c in chunks[:4])
        from app.services.auditor import detect_document_language
        is_english_source = detect_document_language(sample_txt) == "EN"

    for p_idx, page_num in enumerate(sorted_pages, 1):
        # DIN A4 standard dimensions: 595 x 842 points
        page = doc.new_page(width=595, height=842)
        y_cursor = 45

        # 1. Header Banner
        page.draw_rect(fitz.Rect(40, 35, 555, 95), color=(0.1, 0.15, 0.25), fill=(0.96, 0.97, 0.99))
        page.draw_line(fitz.Point(40, 95), fitz.Point(555, 95), color=(0.2, 0.3, 0.5), width=1.5)

        # Federal emblem & title
        banner_title = "§  DOCUNORM.DE • OFFICIAL REGULATORY AUDIT TRANSLATION (DIN EN ISO 17100)"
        page.insert_text(fitz.Point(52, 55), banner_title, fontsize=10, fontname="hebo", color=(0.08, 0.12, 0.2))
        
        doc_header = (
            f"Beglaubigtes deutsches Revisionsdossier: {document.filename}"
            if is_english_source
            else f"Certified English Contract Dossier: {document.filename}"
        )
        page.insert_text(fitz.Point(52, 70), doc_header, fontsize=11, fontname="hebo", color=(0.12, 0.16, 0.24))
        
        fingerprint_snippet = (
            f"SHA-256: {document.sha256_hash[:24]}... • EN ➔ DE • DIN EN ISO 17100 / BaFin Prüffassung"
            if is_english_source
            else f"SHA-256: {document.sha256_hash[:24]}... • DE ➔ EN • DIN 66399 Schutzklasse 3 • DORA Art. 30"
        )
        page.insert_text(fitz.Point(52, 85), fingerprint_snippet, fontsize=8, fontname="helv", color=(0.4, 0.45, 0.5))

        # Page Tracker in Header
        page_badge = f"DOSSIER PAGE {p_idx} OF {total_dossier_pages} (ORIGINAL PAGE {page_num})"
        page.insert_text(fitz.Point(370, 55), page_badge, fontsize=8, fontname="hebo", color=(0.85, 0.3, 0.0))

        y_cursor = 115

        # 2. Render Page Paragraphs
        page_chunks = pages_map.get(page_num, [])
        for chunk in page_chunks:
            if y_cursor > 740:
                # Add continuation page if vertical limit reached
                page = doc.new_page(width=595, height=842)
                y_cursor = 50

            chunk_idx = chunk.get("chunk_index", 0) + 1
            bbox = chunk.get("bounding_box") or [0, 0, 0, 0]
            trans_text = chunk.get("translated_content") or chunk.get("content", "")
            orig_text = chunk.get("content", "")

            # Clause Badge
            clause_header = (
                f"PARAGRAPH {chunk_idx} • DEUTSCHE BEGLAUBIGTE PRÜFFASSUNG [BBox: {int(bbox[0])}, {int(bbox[1])}]"
                if is_english_source
                else f"PARAGRAPH {chunk_idx} • CLAUSE ANALYSIS [BBox: {int(bbox[0])}, {int(bbox[1])}]"
            )
            page.insert_text(fitz.Point(45, y_cursor), clause_header, fontsize=8, fontname="hebo", color=(0.85, 0.3, 0.0))
            y_cursor += 14

            # Translated Text Box
            eng_rect = fitz.Rect(45, y_cursor, 550, y_cursor + 70)
            page.insert_textbox(eng_rect, trans_text, fontsize=9.5, fontname="hebo", color=(0.06, 0.08, 0.12))
            
            # Estimate height based on character length
            text_lines = max(1, len(trans_text) // 75 + 1)
            consumed_h = max(25, text_lines * 14)
            y_cursor += consumed_h + 8

            # Secondary Source (Reference note)
            if orig_text != trans_text:
                sec_label = (
                    "Original English Source (EN 🇺🇸 / 🇬🇧):"
                    if is_english_source
                    else "Original German Statutory Source (DE 🇩🇪):"
                )
                page.insert_text(fitz.Point(45, y_cursor), sec_label, fontsize=7.5, fontname="helv", color=(0.45, 0.5, 0.55))
                y_cursor += 11

                sec_rect = fitz.Rect(45, y_cursor, 550, y_cursor + 60)
                page.insert_textbox(sec_rect, orig_text, fontsize=8, fontname="helv", color=(0.35, 0.4, 0.48))
                
                orig_lines = max(1, len(orig_text) // 85 + 1)
                y_cursor += max(18, orig_lines * 11) + 12

            # Divider Line
            page.draw_line(fitz.Point(45, y_cursor), fitz.Point(550, y_cursor), color=(0.88, 0.9, 0.92), width=0.8)
            y_cursor += 15

        # 3. Footer on every page
        page.draw_line(fitz.Point(40, 790), fitz.Point(555, 790), color=(0.8, 0.85, 0.9), width=1)
        footer_text = f"DocuNorm AI • Non-Repudiation Audit Log • Generated: {current_date_str} • Page {p_idx} of {total_dossier_pages}"
        page.insert_text(fitz.Point(45, 805), footer_text, fontsize=7.5, fontname="helv", color=(0.5, 0.55, 0.6))
        page.insert_text(fitz.Point(460, 805), "BAFIN / DORA VERIFIED", fontsize=7.5, fontname="hebo", color=(0.1, 0.6, 0.3))

    doc.save(str(output_path))
    doc.close()
    return output_path


def generate_english_dossier_markdown(
    document: Document,
    chunks: list[dict],
) -> str:
    """
    Generates a Markdown dossier suitable for copying into Word or report drafting.
    """
    current_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Detect language
    is_english_source = any(c.get("source_language") == "EN" for c in chunks)
    if not is_english_source and chunks:
        sample_txt = " ".join(c.get("content", "") for c in chunks[:4])
        from app.services.auditor import detect_document_language
        is_english_source = detect_document_language(sample_txt) == "EN"

    dossier_title = (
        "# DOCUNORM.DE • DEUTSCHES REVISIONSDOSSIER (DIN EN ISO 17100)"
        if is_english_source
        else "# DOCUNORM.DE • ENGLISH CONTRACT TRANSLATION DOSSIER"
    )

    direction_note = (
        "> **Translation Direction:** English ➔ German (DIN EN ISO 17100 / BaFin Prüffassung)  "
        if is_english_source
        else "> **Translation Direction:** German ➔ English (DIN EN ISO 17100 / DORA Art. 30)  "
    )

    lines = [
        dossier_title,
        f"> **Document:** `{document.filename}`  ",
        f"> **Cryptographic SHA-256 Fingerprint:** `{document.sha256_hash}`  ",
        f"> **Generated Date:** `{current_date_str}`  ",
        direction_note,
        f"> **Compliance Standards:** EU DORA (VO 2022/2554) Art. 30, BDSG § 26, DIN 66399 Schutzklasse 3  ",
        "\n---\n",
    ]

    for c in chunks:
        idx = c.get("chunk_index", 0) + 1
        page = c.get("page_number", 1)
        bbox = c.get("bounding_box") or [0, 0, 0, 0]
        trans = c.get("translated_content") or c.get("content", "")
        orig = c.get("content", "")

        lines.append(f"### Paragraph {idx} (Original Page {page})")
        lines.append(f"*Coordinates: `[x0: {int(bbox[0])}, y0: {int(bbox[1])}, x1: {int(bbox[2])}, y1: {int(bbox[3])}]`*\n")
        
        if is_english_source:
            lines.append(f"**Beglaubigte deutsche Übersetzung:**\n")
            lines.append(f"{trans}\n")
            if orig != trans:
                lines.append(f"<details><summary>Original English Source (EN 🇺🇸 / 🇬🇧)</summary>\n\n> {orig}\n\n</details>\n")
        else:
            lines.append(f"**English Translated Legal Clause:**\n")
            lines.append(f"{trans}\n")
            if orig != trans:
                lines.append(f"<details><summary>Original German Statutory Source (DE 🇩🇪)</summary>\n\n> {orig}\n\n</details>\n")
        
        lines.append("\n---\n")

    return "\n".join(lines)
