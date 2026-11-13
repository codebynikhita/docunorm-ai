import re
from uuid import UUID

from app.schemas.zugferd_invoice import (
    ZugferdInvoiceExtraction,
    ZugferdVisualFieldReconciliation,
    ZugferdVisualReconciliation,
)


class ZugferdVisualReconcilerService:
    """
    Enterprise Sovereign Visual PDF vs. Structured XML Reconciliation Engine.
    Detects discrepancies between what is human-visible on the PDF invoice page and what
    is encoded in the embedded Factur-X / ZUGFeRD / XRechnung XML payload.
    Crucial for GoBD compliance and anti-fraud verification under § 14 UStG & §§ 146, 147 AO.
    """

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def _clean_alphanumeric(cls, text: str) -> str:
        return re.sub(r"[^A-Za-z0-9]", "", text).upper()

    @classmethod
    def _amount_variants(cls, amount: float) -> list[str]:
        """Generates common German and International formatting variants for an amount."""
        res = [
            f"{amount:.2f}",
            f"{amount:.2f}".replace(".", ","),
        ]
        # Thousands separator variants
        parts = f"{amount:,.2f}".split(".")
        int_comma = parts[0]
        cents = parts[1]
        int_dot = int_comma.replace(",", ".")
        res.append(f"{int_comma}.{cents}")
        res.append(f"{int_dot},{cents}")
        if amount.is_integer():
            res.append(str(int(amount)))
        return list(dict.fromkeys(res))

    @classmethod
    def reconcile(
        cls,
        extraction: ZugferdInvoiceExtraction,
        visual_text: str | None = None,
        document_id: UUID | None = None,
    ) -> ZugferdVisualReconciliation:
        """
        Compares core commercial fields between the XML extraction and human-readable visual text.
        """
        has_visual = bool(visual_text and visual_text.strip())
        norm_visual = cls._normalize_text(visual_text or "")
        clean_visual_upper = cls._clean_alphanumeric(visual_text or "")

        fields: list[ZugferdVisualFieldReconciliation] = []

        # -------------------------------------------------------------
        # Field 1: Rechnungsnummer (BT-1)
        # -------------------------------------------------------------
        inv_no = extraction.invoice_number.strip()
        inv_in_visual = inv_no.lower() in norm_visual.lower() if has_visual else False
        clean_inv = cls._clean_alphanumeric(inv_no)
        inv_clean_match = clean_inv in clean_visual_upper if has_visual and clean_inv else False
        is_inv_match = inv_in_visual or inv_clean_match

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="invoice_number",
                field_name_de="Rechnungsnummer (BT-1)",
                xml_value=inv_no,
                pdf_visual_value=inv_no if is_inv_match else (None if not has_visual else "Nicht nachgewiesen"),
                is_match=is_inv_match,
                discrepancy_type="EXACT_MATCH" if is_inv_match else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"Rechnungsnummer '{inv_no}' stimmt mit dem visuellen Belegtext überein."
                    if is_inv_match
                    else f"Rechnungsnummer '{inv_no}' konnte im sichtbaren PDF-Text nicht verifiziert werden."
                ),
            )
        )

        # -------------------------------------------------------------
        # Field 2: Ausstellungsdatum (BT-2)
        # -------------------------------------------------------------
        issue_date = extraction.issue_date
        date_str = str(issue_date) if issue_date else "Kein Datum"
        date_match = False
        if has_visual and issue_date:
            date_variants = [
                issue_date.strftime("%Y-%m-%d"),
                issue_date.strftime("%d.%m.%Y"),
                issue_date.strftime("%d/%m/%Y"),
                issue_date.strftime("%Y%m%d"),
            ]
            date_match = any(v in norm_visual for v in date_variants)

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="issue_date",
                field_name_de="Rechnungsdatum (BT-2)",
                xml_value=date_str,
                pdf_visual_value=date_str if date_match else (None if not has_visual else "Nicht nachgewiesen"),
                is_match=date_match,
                discrepancy_type="EXACT_MATCH" if date_match else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"Rechnungsdatum '{date_str}' ist im visuellen Beleg korrekt deklariert."
                    if date_match
                    else f"Datum '{date_str}' im visuellen Beleg nicht eindeutig lesbar."
                ),
            )
        )

        # -------------------------------------------------------------
        # Field 3: Gesamtbetrag Brutto (BT-112)
        # -------------------------------------------------------------
        ms = extraction.monetary_summation
        grand_total = ms.grand_total_amount_eur
        grand_variants = cls._amount_variants(grand_total)
        grand_match = any(v in norm_visual for v in grand_variants) if has_visual else False

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="grand_total",
                field_name_de="Rechnungsgesamtbetrag Brutto (BT-112)",
                xml_value=f"{grand_total:.2f} {extraction.currency_code}",
                pdf_visual_value=f"{grand_total:.2f} {extraction.currency_code}" if grand_match else (None if not has_visual else "Abweichend"),
                is_match=grand_match,
                discrepancy_type="EXACT_MATCH" if grand_match else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"Bruttobetrag {grand_total:,.2f} {extraction.currency_code} stimmt centgenau mit dem sichtbaren Rechnungsaufdruck überein."
                    if grand_match
                    else f"KRITISCHE DISKREPANZ: Bruttobetrag {grand_total:.2f} {extraction.currency_code} weicht vom visuellen Beleg ab (Integritätsprüfung fehlgeschlagen)."
                ),
            )
        )

        # -------------------------------------------------------------
        # Field 4: Nettobetrag / Steuerbemessungsgrundlage (BT-109)
        # -------------------------------------------------------------
        tax_basis = ms.tax_basis_total_amount_eur
        basis_variants = cls._amount_variants(tax_basis)
        basis_match = any(v in norm_visual for v in basis_variants) if has_visual else False

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="tax_basis_total",
                field_name_de="Nettobetrag (BT-109)",
                xml_value=f"{tax_basis:.2f} {extraction.currency_code}",
                pdf_visual_value=f"{tax_basis:.2f} {extraction.currency_code}" if basis_match else (None if not has_visual else "Abweichend"),
                is_match=basis_match,
                discrepancy_type="EXACT_MATCH" if basis_match else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"Nettobetrag {tax_basis:,.2f} {extraction.currency_code} im visuellen Layout bestätigt."
                    if basis_match
                    else f"Nettobetrag {tax_basis:.2f} {extraction.currency_code} weicht vom sichtbaren PDF ab."
                ),
            )
        )

        # -------------------------------------------------------------
        # Field 5: Gesamtsteuerbetrag (BT-110)
        # -------------------------------------------------------------
        tax_total = ms.tax_total_amount_eur
        tax_variants = cls._amount_variants(tax_total)
        tax_match = any(v in norm_visual for v in tax_variants) if has_visual else False

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="tax_total",
                field_name_de="Umsatzsteuer Gesamt (BT-110)",
                xml_value=f"{tax_total:.2f} {extraction.currency_code}",
                pdf_visual_value=f"{tax_total:.2f} {extraction.currency_code}" if tax_match else (None if not has_visual else "Abweichend"),
                is_match=tax_match,
                discrepancy_type="EXACT_MATCH" if tax_match else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"Gesamtsteuer {tax_total:,.2f} {extraction.currency_code} stimmt mit der visuellen Steueraufschlüsselung überein."
                    if tax_match
                    else f"Steuerbetrag {tax_total:.2f} {extraction.currency_code} weicht von sichtbaren Angaben ab."
                ),
            )
        )

        # -------------------------------------------------------------
        # Field 6: Verkäufer-Name (BT-27)
        # -------------------------------------------------------------
        seller_name = extraction.seller.name.strip()
        seller_tokens = [tok.lower() for tok in seller_name.split() if len(tok) > 2]
        seller_match = False
        if has_visual:
            if seller_name.lower() in norm_visual.lower():
                seller_match = True
            elif seller_tokens and sum(1 for tok in seller_tokens if tok in norm_visual.lower()) >= min(2, len(seller_tokens)):
                seller_match = True

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="seller_name",
                field_name_de="Rechnungssteller / Verkäufer (BT-27)",
                xml_value=seller_name,
                pdf_visual_value=seller_name if seller_match else (None if not has_visual else "Nicht lesbar"),
                is_match=seller_match,
                discrepancy_type="EXACT_MATCH" if seller_match else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"Verkäufer '{seller_name}' im Briefkopf des visuellen Belegs identifiziert."
                    if seller_match
                    else f"Verkäuferbezeichnung '{seller_name}' konnte nicht im Briefkopf gefunden werden."
                ),
            )
        )

        # -------------------------------------------------------------
        # Field 7: Verkäufer USt-IdNr. (BT-31)
        # -------------------------------------------------------------
        seller_vat = (extraction.seller.vat_id or "").strip()
        seller_vat_match = False
        if has_visual and seller_vat:
            clean_vat = cls._clean_alphanumeric(seller_vat)
            seller_vat_match = clean_vat in clean_visual_upper

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="seller_vat_id",
                field_name_de="Umsatzsteuer-Identifikationsnummer (BT-31)",
                xml_value=seller_vat or "—",
                pdf_visual_value=seller_vat if seller_vat_match else (None if not has_visual else "Nicht ausgewiesen"),
                is_match=seller_vat_match if seller_vat else True,
                discrepancy_type="EXACT_MATCH" if seller_vat_match or not seller_vat else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"USt-IdNr. '{seller_vat}' ist im visuellen Fußbereich ausgewiesen."
                    if seller_vat_match
                    else ("Keine USt-IdNr. im XML deklariert." if not seller_vat else f"USt-IdNr. '{seller_vat}' fehlt im sichtbaren Belegtext (§ 14 Abs. 4 Nr. 2 UStG).")
                ),
            )
        )

        # -------------------------------------------------------------
        # Field 8: Käuferreferenz / Leitweg-ID (BT-10)
        # -------------------------------------------------------------
        buyer_ref = (extraction.buyer_reference or "").strip()
        ref_match = False
        if has_visual and buyer_ref:
            clean_ref = cls._clean_alphanumeric(buyer_ref)
            ref_match = buyer_ref.lower() in norm_visual.lower() or (clean_ref in clean_visual_upper if clean_ref else False)

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="buyer_reference",
                field_name_de="Käuferreferenz / Leitweg-ID (BT-10)",
                xml_value=buyer_ref or "— (B2B Standard)",
                pdf_visual_value=buyer_ref if ref_match else (None if not has_visual else "Nicht gedruckt"),
                is_match=ref_match if buyer_ref else True,
                discrepancy_type="EXACT_MATCH" if ref_match or not buyer_ref else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"Leitweg-ID / Referenz '{buyer_ref}' ist im Beleg sichtbar aufgeführt."
                    if ref_match
                    else ("Keine Käuferreferenz deklariert." if not buyer_ref else f"Leitweg-ID '{buyer_ref}' ist im visuellen Dokument nicht auffindbar.")
                ),
            )
        )

        # -------------------------------------------------------------
        # Field 9: Bankverbindung IBAN (BT-84)
        # -------------------------------------------------------------
        iban = (extraction.iban or "").strip()
        iban_match = False
        if has_visual and iban:
            clean_iban = cls._clean_alphanumeric(iban)
            iban_match = clean_iban in clean_visual_upper

        fields.append(
            ZugferdVisualFieldReconciliation(
                field_key="iban",
                field_name_de="SEPA Bankverbindung IBAN (BT-84)",
                xml_value=iban or "—",
                pdf_visual_value=iban if iban_match else (None if not has_visual else "Nicht nachgewiesen"),
                is_match=iban_match if iban else True,
                discrepancy_type="EXACT_MATCH" if iban_match or not iban else ("MISSING_IN_VISUAL" if not has_visual else "VALUE_MISMATCH"),
                details_de=(
                    f"IBAN '{iban}' stimmt mit den visuellen Bankdaten überein."
                    if iban_match
                    else ("Keine IBAN angegeben." if not iban else f"SICHERHEITSRISIKO: XML-IBAN '{iban}' weicht von sichtbaren Bankdaten ab.")
                ),
            )
        )

        total_checked = len(fields)
        matched_count = sum(1 for f in fields if f.is_match)
        discrepancy_count = total_checked - matched_count
        score_percent = round((matched_count / total_checked) * 100.0, 1) if total_checked > 0 else 0.0
        is_reconciled = discrepancy_count == 0

        if not has_visual:
            summary = (
                f"Kein optischer Belegtext verfügbar (Rein-XML Beleg '{extraction.filename}'). "
                f"Strukturierte Validierung nach EN 16931-1 aktiv."
            )
        elif is_reconciled:
            summary = (
                f"Vollständiger visueller Belegabgleich erfolgreich ({matched_count}/{total_checked} Felder übereinstimmend, 100%). "
                f"Keine Abweichungen zwischen PDF-Sichtbeleg und XML-Rechnungsdatensatz festgestellt."
            )
        else:
            summary = (
                f"Visueller Belegabgleich ergab {discrepancy_count} Abweichung(en) ({score_percent:.0f}% Übereinstimmung). "
                f"Sichtbarer Beleg und strukturierte XML-Daten weichen voneinander ab (Prüfpflicht gem. GoBD)."
            )

        return ZugferdVisualReconciliation(
            document_id=document_id or extraction.document_id,
            filename=extraction.filename,
            has_visual_layer=has_visual,
            is_reconciled=is_reconciled,
            total_fields_checked=total_checked,
            matched_fields_count=matched_count,
            discrepancy_count=discrepancy_count,
            reconciliation_score_percent=score_percent,
            summary_de=summary,
            fields=fields,
        )


zugferd_visual_reconciler = ZugferdVisualReconcilerService()
