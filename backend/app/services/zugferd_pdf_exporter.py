import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path

import pymupdf as fitz

from app.schemas.zugferd_invoice import ZugferdInvoiceExtraction


def _compute_gobd_sha256(extraction: ZugferdInvoiceExtraction) -> str:
    """Computes a canonical SHA-256 archival digest over the raw XML or extracted payload."""
    source_bytes = (
        extraction.raw_xml_content.encode("utf-8")
        if extraction.raw_xml_content
        else extraction.model_dump_json().encode("utf-8")
    )
    return hashlib.sha256(source_bytes).hexdigest()


def _safe_filename(raw: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in raw)
    return cleaned.strip("_") or "invoice"


def _draw_footer(page: fitz.Page, filename: str, sha256_hash: str, page_num: int, total_pages: int = 2) -> None:
    page.draw_line(fitz.Point(40, 800), fitz.Point(555, 800), color=(0.78, 0.84, 0.90), width=1.0)
    page.insert_text(
        fitz.Point(44, 814),
        f"GoBD E-Rechnungs-Zertifikat • {filename[:34]} • SHA-256: {sha256_hash[:16]}... • Seite {page_num} von {total_pages}",
        fontsize=7.3,
        fontname="helv",
        color=(0.45, 0.50, 0.56),
    )
    page.insert_text(
        fitz.Point(448, 814),
        "GoBD REVISIONSICHER",
        fontsize=7.5,
        fontname="hebo",
        color=(0.08, 0.48, 0.28),
    )


def generate_zugferd_reconciliation_pdf(
    extraction: ZugferdInvoiceExtraction,
    signatory_name: str = "DocuNorm Sovereign AI · ZUGFeRD 2.3 / GoBD Prüfstelle",
    output_dir: Path | str = "/tmp/docunorm_exports",
) -> Path:
    """
    Generates an official 2-page DIN 5008 E-Invoice Reconciliation & GoBD Audit Trail PDF
    covering EN 16931-1 conformance, Leitweg-ID ISO 7064 MOD-97-10 verification, and § 14 UStG audit results.
    """
    os.makedirs(output_dir, exist_ok=True)
    safe_inv = _safe_filename(extraction.invoice_number)
    output_path = Path(output_dir) / f"ZUGFERD_{safe_inv}_GOBD_ZERTIFIKAT.pdf"

    sha256_hash = _compute_gobd_sha256(extraction)
    created_at_dt = datetime.now(UTC)
    created_at_str = created_at_dt.strftime("%d.%m.%Y • %H:%M:%S UTC")
    date_stamp = created_at_dt.strftime("%d.%m.%Y")

    en_ok = extraction.validation_report.is_en16931_compliant
    vat_ok = extraction.vat_audit.is_ustg_compliant if extraction.vat_audit else True
    lw = extraction.leitweg_validation
    lw_ok = True if (lw is None or lw.is_valid) else False
    overall_ok = en_ok and vat_ok and lw_ok

    doc = fitz.open()

    # =========================================================================
    # PAGE 1: DIN 5008 Letterhead, GoBD Seal, Leitweg-ID Routing & Monetary Reconciliation
    # =========================================================================
    page1 = doc.new_page(width=595, height=842)

    # Header Block (DIN 5008)
    page1.draw_rect(fitz.Rect(40, 35, 555, 96), color=(0.12, 0.25, 0.45), fill=(0.95, 0.97, 1.0))
    page1.draw_line(fitz.Point(40, 96), fitz.Point(555, 96), color=(0.08, 0.50, 0.30), width=2.5)

    page1.insert_text(
        fitz.Point(52, 54),
        "PRÜFZERTIFIKAT E-RECHNUNG & GoBD-REVISIONSARCHIV (DIN 5008)",
        fontsize=10.5,
        fontname="hebo",
        color=(0.06, 0.14, 0.28),
    )
    page1.insert_text(
        fitz.Point(52, 69),
        "Konformitätsprüfung gemäß EN 16931-1, E-Rech-VO (§ 4 Leitweg-ID) & § 14 UStG",
        fontsize=8.5,
        fontname="hebo",
        color=(0.16, 0.30, 0.48),
    )
    page1.insert_text(
        fitz.Point(52, 84),
        f"Rechnung: {extraction.invoice_number} • Profil: {extraction.profile.value.upper()} • Datum: {date_stamp}",
        fontsize=7.5,
        fontname="helv",
        color=(0.35, 0.42, 0.50),
    )

    # Status Badge
    badge_bg = (0.91, 0.98, 0.94) if overall_ok else (1.0, 0.94, 0.94)
    badge_color = (0.08, 0.52, 0.26) if overall_ok else (0.78, 0.16, 0.16)
    page1.draw_rect(fitz.Rect(425, 45, 545, 86), color=badge_color, fill=badge_bg)
    page1.insert_text(fitz.Point(435, 60), "PRÜFSTATUS", fontsize=7.5, fontname="hebo", color=badge_color)
    page1.insert_text(
        fitz.Point(435, 76),
        "KONFORM" if overall_ok else "NACHPRÜFUNG",
        fontsize=10.5,
        fontname="hebo",
        color=badge_color,
    )

    # Section 1: Cryptographic GoBD Box
    page1.draw_rect(fitz.Rect(40, 108, 555, 178), color=(0.78, 0.84, 0.90), fill=(0.98, 0.99, 1.0))
    page1.insert_text(
        fitz.Point(52, 123),
        "1. KRYPTOGRAPHISCHE GoBD-VERSIEGELUNG & TECHNISCHE METADATEN (§§ 146, 147 AO)",
        fontsize=8.2,
        fontname="hebo",
        color=(0.08, 0.48, 0.28),
    )
    page1.insert_text(
        fitz.Point(52, 137),
        f"Quelldatei: {extraction.filename} • XML-Payload: {extraction.xml_filename or 'Embedded'} • PDF/A-3 Hybrid: {'Ja' if extraction.is_hybrid_pdf_a3 else 'Rein-XML'}",
        fontsize=7.8,
        fontname="helv",
        color=(0.12, 0.16, 0.24),
    )
    page1.insert_text(
        fitz.Point(52, 150),
        f"URN-Schema: {extraction.profile_urn[:72]} ({extraction.validation_report.syntax_format})",
        fontsize=7.5,
        fontname="helv",
        color=(0.20, 0.26, 0.34),
    )
    page1.insert_text(
        fitz.Point(52, 163),
        f"SHA-256 Prüfsiegel: {sha256_hash}",
        fontsize=7.3,
        fontname="helv",
        color=(0.14, 0.20, 0.30),
    )
    page1.insert_text(
        fitz.Point(52, 173),
        f"Revisionssicherer Zeitstempel: {created_at_str}",
        fontsize=7.2,
        fontname="helv",
        color=(0.40, 0.45, 0.52),
    )

    # Section 2: Seller & Buyer Party Blocks
    page1.insert_text(
        fitz.Point(40, 200),
        "2. VERTRAGSPARTEIEN & STEUERLICHE IDENTIFIKATION",
        fontsize=9.2,
        fontname="hebo",
        color=(0.08, 0.12, 0.22),
    )

    # Seller Box
    page1.draw_rect(fitz.Rect(40, 210, 290, 295), color=(0.84, 0.88, 0.92), fill=(0.98, 0.99, 1.0))
    page1.insert_text(fitz.Point(50, 225), "LEISTENDER / VERKÄUFER (BG-4)", fontsize=7.5, fontname="hebo", color=(0.18, 0.32, 0.52))
    page1.insert_text(fitz.Point(50, 240), extraction.seller.name[:38], fontsize=8.5, fontname="hebo", color=(0.08, 0.12, 0.20))
    seller_city = (
        f"{extraction.seller.postal_address.postcode or ''} {extraction.seller.postal_address.city_name or ''} ({extraction.seller.postal_address.country_id})"
        if extraction.seller.postal_address
        else "Keine Anschrift"
    )
    page1.insert_text(fitz.Point(50, 255), seller_city[:42], fontsize=7.8, fontname="helv", color=(0.25, 0.30, 0.38))
    page1.insert_text(
        fitz.Point(50, 270),
        f"USt-IdNr.: {extraction.seller.vat_id or '-'} • St-Nr.: {extraction.seller.tax_number or '-'}",
        fontsize=7.5,
        fontname="helv",
        color=(0.20, 0.25, 0.32),
    )
    page1.insert_text(
        fitz.Point(50, 284),
        f"IBAN: {extraction.iban or '-'}",
        fontsize=7.3,
        fontname="helv",
        color=(0.35, 0.40, 0.48),
    )

    # Buyer Box
    page1.draw_rect(fitz.Rect(305, 210, 555, 295), color=(0.84, 0.88, 0.92), fill=(0.98, 0.99, 1.0))
    page1.insert_text(fitz.Point(315, 225), "EMPFÄNGER / KÄUFER (BG-7)", fontsize=7.5, fontname="hebo", color=(0.18, 0.32, 0.52))
    page1.insert_text(fitz.Point(315, 240), extraction.buyer.name[:38], fontsize=8.5, fontname="hebo", color=(0.08, 0.12, 0.20))
    buyer_city = (
        f"{extraction.buyer.postal_address.postcode or ''} {extraction.buyer.postal_address.city_name or ''} ({extraction.buyer.postal_address.country_id})"
        if extraction.buyer.postal_address
        else "Keine Anschrift"
    )
    page1.insert_text(fitz.Point(315, 255), buyer_city[:42], fontsize=7.8, fontname="helv", color=(0.25, 0.30, 0.38))
    page1.insert_text(
        fitz.Point(315, 270),
        f"USt-IdNr.: {extraction.buyer.vat_id or '-'}",
        fontsize=7.5,
        fontname="helv",
        color=(0.20, 0.25, 0.32),
    )
    page1.insert_text(
        fitz.Point(315, 284),
        f"Leitweg/Ref (BT-10): {extraction.buyer_reference or '-'}",
        fontsize=7.3,
        fontname="helv",
        color=(0.35, 0.40, 0.48),
    )

    # Section 3: Day 23 Leitweg-ID & ISO 7064 MOD-97-10 Routing Registry
    page1.insert_text(
        fitz.Point(40, 318),
        "3. LEITWEG-ID & BEHÖRDEN-ROUTING (§ 4 E-Rech-VO · ISO 7064 MOD-97-10)",
        fontsize=9.2,
        fontname="hebo",
        color=(0.08, 0.12, 0.22),
    )
    lw_bg = (0.95, 0.99, 0.96) if lw_ok else (1.0, 0.95, 0.95)
    lw_col = (0.08, 0.52, 0.26) if lw_ok else (0.78, 0.16, 0.16)
    page1.draw_rect(fitz.Rect(40, 328, 555, 410), color=lw_col, fill=lw_bg)
    if lw is not None:
        lw_status = "VALIDIERT (ISO 7064 MOD-97-10)" if lw.is_valid else "FEHLERHAFT"
        page1.insert_text(fitz.Point(52, 344), f"Leitweg-ID: {lw.raw_id} • Status: {lw_status}", fontsize=8.5, fontname="hebo", color=lw_col)
        page1.insert_text(
            fitz.Point(52, 359),
            f"Grobaddressierung: {lw.coarse_address or '-'} • Feinaddressierung: {lw.fine_address or '-'} • Prüfziffer: {lw.check_digit or '-'} (Erwartet: {lw.expected_check_digit or '-'})",
            fontsize=7.8,
            fontname="helv",
            color=(0.15, 0.20, 0.28),
        )
        page1.insert_text(
            fitz.Point(52, 374),
            f"Körperschaft: {lw.federal_entity_type} — {lw.bundesland_or_authority}",
            fontsize=7.8,
            fontname="hebo",
            color=(0.12, 0.18, 0.26),
        )
        page1.insert_text(
            fitz.Point(52, 389),
            f"Zuständiges Portal: {lw.submission_portal[:78]}",
            fontsize=7.5,
            fontname="helv",
            color=(0.25, 0.30, 0.38),
        )
        err_note = f"Hinweise: {'; '.join(lw.errors)[:85]}" if lw.errors else f"Rechtsgrundlage: {lw.statutory_basis}"
        page1.insert_text(fitz.Point(52, 402), err_note, fontsize=7.3, fontname="helv", color=(0.35, 0.40, 0.48))
    else:
        page1.insert_text(
            fitz.Point(52, 352),
            "Keine Käuferreferenz / Leitweg-ID (BT-10) in dieser B2B-Rechnung übermittelt.",
            fontsize=8.0,
            fontname="helv",
            color=(0.35, 0.40, 0.48),
        )

    # Section 4: Monetary Summation & Tax Subtotals
    page1.insert_text(
        fitz.Point(40, 434),
        "4. MONETÄRE ABSTIMMUNG & STEUERAUFSCHLÜSSELUNG (BG-22 / BG-23)",
        fontsize=9.2,
        fontname="hebo",
        color=(0.08, 0.12, 0.22),
    )

    ms = extraction.monetary_summation
    cur = extraction.currency_code
    rows = [
        ("Summe Positionen Netto (BT-106)", f"{ms.line_total_amount_eur:,.2f} {cur}"),
        ("Zuschläge / Nachlässe (BT-108 / BT-107)", f"+{ms.charge_total_amount_eur:,.2f} / -{ms.allowance_total_amount_eur:,.2f} {cur}"),
        ("Steuerbemessungsgrundlage Netto (BT-109)", f"{ms.tax_basis_total_amount_eur:,.2f} {cur}"),
        ("Umsatzsteuer Gesamtbetrag (BT-110)", f"{ms.tax_total_amount_eur:,.2f} {cur}"),
        ("Brutto-Rechnungsbetrag (BT-112)", f"{ms.grand_total_amount_eur:,.2f} {cur}"),
        ("Bereits geleistete Vorauszahlungen (BT-113)", f"-{ms.prepaid_amount_eur:,.2f} {cur}"),
        ("Fälliger Zahlbetrag (BT-115)", f"{ms.due_payable_amount_eur:,.2f} {cur}"),
    ]

    y = 446
    for idx, (label, val) in enumerate(rows):
        is_total = idx in (4, 6)
        fill_col = (0.93, 0.96, 1.0) if is_total else ((0.98, 0.99, 1.0) if idx % 2 == 0 else (1.0, 1.0, 1.0))
        page1.draw_rect(fitz.Rect(40, y, 555, y + 22), color=(0.86, 0.89, 0.93), fill=fill_col)
        page1.insert_text(fitz.Point(50, y + 14), label, fontsize=8.0, fontname="hebo" if is_total else "helv", color=(0.10, 0.14, 0.22))
        page1.insert_text(fitz.Point(415, y + 14), val, fontsize=8.3, fontname="hebo", color=(0.08, 0.22, 0.42) if is_total else (0.15, 0.20, 0.28))
        y += 23

    # Tax subtotals mini strip
    y += 10
    page1.insert_text(fitz.Point(40, y + 8), "Umsatzsteuer-Teilbeträge nach Steuersatz & Kategorie (EN 16931 BG-23):", fontsize=8.0, fontname="hebo", color=(0.12, 0.18, 0.28))
    y += 16
    for sub in extraction.tax_subtotals[:5]:
        page1.draw_rect(fitz.Rect(40, y, 555, y + 20), color=(0.86, 0.89, 0.93), fill=(0.98, 0.99, 1.0))
        reason = f" · Grund: {sub.exemption_reason[:34]}" if sub.exemption_reason else ""
        page1.insert_text(
            fitz.Point(50, y + 13),
            f"Kat. {sub.tax_category_code.value} ({sub.tax_rate_percent:.1f}%): Bemessung {sub.taxable_amount_eur:,.2f} {cur} -> Steuer {sub.tax_amount_eur:,.2f} {cur}{reason}",
            fontsize=7.6,
            fontname="helv",
            color=(0.15, 0.20, 0.28),
        )
        y += 22

    _draw_footer(page1, extraction.filename, sha256_hash, 1, 2)

    # =========================================================================
    # PAGE 2: Line Items, § 14 UStG / § 13b Reverse-Charge Audit & EN 16931 Rules
    # =========================================================================
    page2 = doc.new_page(width=595, height=842)

    page2.draw_rect(fitz.Rect(40, 35, 555, 72), color=(0.12, 0.25, 0.45), fill=(0.95, 0.97, 1.0))
    page2.insert_text(
        fitz.Point(52, 52),
        "ABSCHNITT II: § 14 UStG STEUERPRÜFUNG, EN 16931 REGELN & GoBD ENDABNAHME",
        fontsize=9.5,
        fontname="hebo",
        color=(0.06, 0.14, 0.28),
    )
    page2.insert_text(
        fitz.Point(52, 65),
        f"Rechnung: {extraction.invoice_number} • Ausstellungsdatum: {extraction.issue_date or '-'} • Verkäufer: {extraction.seller.name[:35]}",
        fontsize=7.5,
        fontname="helv",
        color=(0.35, 0.42, 0.50),
    )

    # Section 5: Line Items Preview
    y2 = 90
    page2.insert_text(fitz.Point(40, y2), f"5. RECHNUNGSPOSITIONEN (BG-25 — {len(extraction.line_items)} POSITIONEN)", fontsize=9.0, fontname="hebo", color=(0.08, 0.12, 0.22))
    y2 += 10
    page2.draw_rect(fitz.Rect(40, y2, 555, y2 + 19), color=(0.75, 0.80, 0.88), fill=(0.91, 0.94, 0.98))
    page2.insert_text(fitz.Point(46, y2 + 13), "Pos.", fontsize=7.5, fontname="hebo", color=(0.10, 0.16, 0.26))
    page2.insert_text(fitz.Point(80, y2 + 13), "Leistungsbeschreibung", fontsize=7.5, fontname="hebo", color=(0.10, 0.16, 0.26))
    page2.insert_text(fitz.Point(310, y2 + 13), "Menge", fontsize=7.5, fontname="hebo", color=(0.10, 0.16, 0.26))
    page2.insert_text(fitz.Point(375, y2 + 13), "Einzelpreis", fontsize=7.5, fontname="hebo", color=(0.10, 0.16, 0.26))
    page2.insert_text(fitz.Point(445, y2 + 13), "USt", fontsize=7.5, fontname="hebo", color=(0.10, 0.16, 0.26))
    page2.insert_text(fitz.Point(490, y2 + 13), "Netto Gesamt", fontsize=7.5, fontname="hebo", color=(0.10, 0.16, 0.26))
    y2 += 20

    for item in extraction.line_items[:6]:
        page2.draw_rect(fitz.Rect(40, y2, 555, y2 + 19), color=(0.88, 0.90, 0.94), fill=(0.99, 0.99, 1.0))
        page2.insert_text(fitz.Point(46, y2 + 13), item.line_id[:6], fontsize=7.3, fontname="helv", color=(0.20, 0.25, 0.32))
        page2.insert_text(fitz.Point(80, y2 + 13), item.item_name[:38], fontsize=7.3, fontname="helv", color=(0.12, 0.16, 0.24))
        page2.insert_text(fitz.Point(310, y2 + 13), f"{item.billed_quantity:g} {item.unit_code}", fontsize=7.3, fontname="helv", color=(0.20, 0.25, 0.32))
        page2.insert_text(fitz.Point(375, y2 + 13), f"{item.net_price_eur:,.2f}", fontsize=7.3, fontname="helv", color=(0.20, 0.25, 0.32))
        page2.insert_text(fitz.Point(445, y2 + 13), f"{item.vat_rate_percent:.0f}%", fontsize=7.3, fontname="helv", color=(0.20, 0.25, 0.32))
        page2.insert_text(fitz.Point(490, y2 + 13), f"{item.line_total_eur:,.2f}", fontsize=7.3, fontname="hebo", color=(0.10, 0.16, 0.26))
        y2 += 20

    # Section 6: Day 24 § 14 UStG & Reverse-Charge Audit
    y2 += 14
    page2.insert_text(fitz.Point(40, y2), "6. UMSATZSTEUERRECHTLICHE TIEFENPRÜFUNG (§ 14, § 13b, § 6a UStG)", fontsize=9.0, fontname="hebo", color=(0.08, 0.12, 0.22))
    y2 += 10

    vat = extraction.vat_audit
    if vat is not None:
        v_col = (0.08, 0.52, 0.26) if vat.is_ustg_compliant else (0.78, 0.16, 0.16)
        v_bg = (0.95, 0.99, 0.96) if vat.is_ustg_compliant else (1.0, 0.95, 0.95)
        page2.draw_rect(fitz.Rect(40, y2, 555, y2 + 54), color=v_col, fill=v_bg)
        page2.insert_text(
            fitz.Point(50, y2 + 15),
            f"UStG-Ergebnis: {'KONFORM' if vat.is_ustg_compliant else 'DISKRAPENZ FESTGESTELLT'} • Pflichtangaben-Score: {vat.mandatory_fields_score_percent:.0f}%",
            fontsize=8.2,
            fontname="hebo",
            color=v_col,
        )
        page2.insert_text(
            fitz.Point(50, y2 + 30),
            f"Nachgerechnete Steuer: {vat.recalculated_tax_total_eur:,.2f} {cur} • Ausgewiesene Steuer: {vat.declared_tax_total_eur:,.2f} {cur} • Differenz: {vat.tax_discrepancy_eur:,.2f} {cur}",
            fontsize=7.6,
            fontname="helv",
            color=(0.15, 0.20, 0.28),
        )
        flags = []
        if vat.is_small_value_invoice:
            flags.append("Kleinbetragsrechnung (§ 33 UStDV)")
        if vat.reverse_charge_detected:
            flags.append("Reverse Charge (§ 13b UStG)")
        if vat.intra_community_supply_detected:
            flags.append("Innergem. Lieferung (§ 6a UStG)")
        flag_str = ", ".join(flags) if flags else "Regelbesteuerung Inland (§ 12 UStG)"
        page2.insert_text(fitz.Point(50, y2 + 44), f"Sonderstatuten: {flag_str}", fontsize=7.5, fontname="helv", color=(0.25, 0.30, 0.38))
        y2 += 62

        for finding in vat.findings[:4]:
            f_col = (0.78, 0.16, 0.16) if finding.severity == "CRITICAL" else ((0.80, 0.48, 0.0) if finding.severity == "WARNING" else (0.12, 0.34, 0.56))
            page2.draw_rect(fitz.Rect(40, y2, 555, y2 + 34), color=(0.86, 0.89, 0.93), fill=(0.99, 0.99, 1.0))
            page2.insert_text(
                fitz.Point(48, y2 + 13),
                f"[{finding.severity}] {finding.code} · {finding.statutory_reference}",
                fontsize=7.5,
                fontname="hebo",
                color=f_col,
            )
            page2.insert_text(
                fitz.Point(48, y2 + 26),
                finding.description_de[:92],
                fontsize=7.3,
                fontname="helv",
                color=(0.18, 0.22, 0.30),
            )
            y2 += 37

    # Section 7: EN 16931 Business Rule Evaluation
    y2 += 10
    vr = extraction.validation_report
    page2.insert_text(
        fitz.Point(40, y2),
        f"7. EN 16931-1 REGELWERK & XRECHNUNG B2G KONFORMITÄT ({vr.passed_rules_count}/{vr.total_rules_evaluated} REGELN ERFÜLLT)",
        fontsize=9.0,
        fontname="hebo",
        color=(0.08, 0.12, 0.22),
    )
    y2 += 8
    page2.draw_rect(fitz.Rect(40, y2, 555, y2 + 44), color=(0.82, 0.86, 0.90), fill=(0.98, 0.99, 1.0))
    page2.insert_textbox(
        fitz.Rect(48, y2 + 6, 545, y2 + 40),
        vr.validation_summary_de,
        fontsize=7.6,
        fontname="helv",
        color=(0.15, 0.20, 0.28),
    )
    y2 += 50

    for issue in vr.issues[:3]:
        i_col = (0.78, 0.16, 0.16) if issue.severity == "ERROR" else (0.80, 0.48, 0.0)
        page2.draw_rect(fitz.Rect(40, y2, 555, y2 + 24), color=(0.86, 0.89, 0.93), fill=(1.0, 0.98, 0.98))
        page2.insert_text(
            fitz.Point(48, y2 + 15),
            f"[{issue.severity}] {issue.code}: {issue.description[:82]}",
            fontsize=7.3,
            fontname="hebo",
            color=i_col,
        )
        y2 += 26

    # Final GoBD Endorsement Box anchored cleanly above footer
    endorse_y = max(y2 + 10, 695)
    if endorse_y > 715:
        endorse_y = 715
    page2.draw_rect(fitz.Rect(40, endorse_y, 555, endorse_y + 72), color=(0.08, 0.48, 0.28), fill=(0.96, 0.99, 0.97))
    page2.insert_text(
        fitz.Point(50, endorse_y + 16),
        "8. GoBD 10-JAHRES-ARCHIVIERUNGSFREIGABE & REVISIONSVERMERK (§ 147 AO)",
        fontsize=8.3,
        fontname="hebo",
        color=(0.08, 0.45, 0.25),
    )
    endorse_text = (
        f"Dieses ZUGFeRD / XRechnung Prüfzertifikat bestätigt die Unveränderlichkeit der strukturierten XML-Rechnungsdaten "
        f"durch SHA-256 Prüfsummenbindung ({sha256_hash[:24]}...) gemäß den Grundsätzen zur ordnungsmäßigen Führung und Aufbewahrung "
        f"von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form (GoBD, BMF-Schreiben)."
    )
    page2.insert_textbox(fitz.Rect(50, endorse_y + 22, 545, endorse_y + 56), endorse_text, fontsize=7.2, fontname="helv", color=(0.18, 0.22, 0.28))
    page2.insert_text(
        fitz.Point(50, endorse_y + 64),
        f"Elektronisch testiert: {signatory_name} • {created_at_str}",
        fontsize=7.5,
        fontname="hebo",
        color=(0.08, 0.48, 0.28),
    )

    _draw_footer(page2, extraction.filename, sha256_hash, 2, 2)

    doc.save(str(output_path))
    doc.close()
    return output_path
