import math
import re

from app.schemas.zugferd_invoice import (
    VatAuditReport,
    VatCategoryCode,
    VatFinding,
    ZugferdInvoiceExtraction,
)


class VatAuditorService:
    """
    German § 14 UStG & EU VAT Directive 2006/112/EC Tax Reconciliation Engine.
    Detects Reverse-Charge (§ 13b UStG), Intra-Community Supply (§ 6a UStG),
    Small-Value Invoices (§ 33 UStDV), and unauthorized VAT calculation discrepancies.
    """

    DE_VAT_ID_REGEX = re.compile(r"^DE[0-9]{9}$")
    EU_VAT_ID_REGEX = re.compile(r"^[A-Z]{2}[A-Z0-9]{2,12}$")

    EU_MEMBER_STATES = {
        "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR",
        "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
        "SE", "SI", "SK",
    }

    VALID_GERMAN_STANDARD_RATES = {19.0, 7.0, 0.0}

    @classmethod
    def audit_invoice(cls, extraction: ZugferdInvoiceExtraction) -> VatAuditReport:
        """
        Performs a comprehensive statutory VAT audit on an extracted ZUGFeRD / XRechnung invoice.
        """
        findings: list[VatFinding] = []
        ms = extraction.monetary_summation
        is_small_value = ms.grand_total_amount_eur <= 250.00

        # ------------------------------------------------------------------
        # 1. § 14 Abs. 4 UStG Mandatory Requisites Audit (6 Checkpoints)
        # ------------------------------------------------------------------
        mandatory_checks_total = 6
        mandatory_checks_passed = 0

        # Check 1: Seller Name & Address (§ 14 Abs. 4 Nr. 1 UStG)
        seller_addr_ok = bool(
            extraction.seller.name
            and extraction.seller.postal_address
            and extraction.seller.postal_address.city_name
            and extraction.seller.postal_address.postcode
        )
        if seller_addr_ok:
            mandatory_checks_passed += 1
        else:
            findings.append(
                VatFinding(
                    code="USTG-14-01",
                    severity="CRITICAL",
                    category="USTG_14_MANDATORY",
                    description_de="Vollständiger Name oder Anschrift des leistenden Unternehmers unvollständig.",
                    description_en="Seller full legal name or postal address is incomplete.",
                    statutory_reference="§ 14 Abs. 4 Satz 1 Nr. 1 UStG",
                )
            )

        # Check 2: Seller VAT ID or Tax Number (§ 14 Abs. 4 Nr. 2 UStG)
        seller_vat = (extraction.seller.vat_id or "").strip().upper()
        seller_tax = (extraction.seller.tax_number or "").strip()
        if seller_vat or seller_tax:
            if seller_vat and seller_vat.startswith("DE") and not cls.DE_VAT_ID_REGEX.match(seller_vat):
                findings.append(
                    VatFinding(
                        code="USTG-14-02-FMT",
                        severity="CRITICAL",
                        category="USTG_14_MANDATORY",
                        description_de=f"Ungültiges Format der deutschen USt-IdNr. '{seller_vat}' (erwartet: DE + 9 Ziffern).",
                        description_en=f"Invalid German VAT ID format '{seller_vat}' (expected DE + 9 digits).",
                        statutory_reference="§ 14 Abs. 4 Nr. 2 i.V.m. § 27a UStG",
                        expected_value="DE123456789",
                        found_value=seller_vat,
                    )
                )
            else:
                mandatory_checks_passed += 1
        elif is_small_value:
            # Small value invoices <= 250 EUR do not require seller VAT ID under § 33 UStDV
            mandatory_checks_passed += 1
        else:
            findings.append(
                VatFinding(
                    code="USTG-14-02",
                    severity="CRITICAL",
                    category="USTG_14_MANDATORY",
                    description_de="Steuernummer oder Umsatzsteuer-Identifikationsnummer (USt-IdNr.) des Ausstellers fehlt.",
                    description_en="Mandatory Seller VAT ID or Tax Number is missing.",
                    statutory_reference="§ 14 Abs. 4 Satz 1 Nr. 2 UStG",
                )
            )

        # Check 3: Issue Date (§ 14 Abs. 4 Nr. 3 UStG)
        if extraction.issue_date is not None:
            mandatory_checks_passed += 1
        else:
            findings.append(
                VatFinding(
                    code="USTG-14-03",
                    severity="CRITICAL",
                    category="USTG_14_MANDATORY",
                    description_de="Ausstellungsdatum der Rechnung fehlt.",
                    description_en="Invoice issue date is missing.",
                    statutory_reference="§ 14 Abs. 4 Satz 1 Nr. 3 UStG",
                )
            )

        # Check 4: Sequential Invoice Number (§ 14 Abs. 4 Nr. 4 UStG)
        if extraction.invoice_number and extraction.invoice_number != "UNBEKANNT":
            mandatory_checks_passed += 1
        elif is_small_value:
            mandatory_checks_passed += 1
        else:
            findings.append(
                VatFinding(
                    code="USTG-14-04",
                    severity="CRITICAL",
                    category="USTG_14_MANDATORY",
                    description_de="Fortlaufende Rechnungsnummer fehlt (für Kleinbetragsrechnungen <= 250 € entbehrlich).",
                    description_en="Consecutive invoice number missing.",
                    statutory_reference="§ 14 Abs. 4 Satz 1 Nr. 4 UStG",
                )
            )

        # Check 5: Buyer Name & Address (§ 14 Abs. 4 Nr. 1 UStG)
        buyer_addr_ok = bool(
            extraction.buyer.name
            and extraction.buyer.postal_address
            and extraction.buyer.postal_address.city_name
        )
        if buyer_addr_ok or is_small_value:
            mandatory_checks_passed += 1
        else:
            findings.append(
                VatFinding(
                    code="USTG-14-05",
                    severity="CRITICAL",
                    category="USTG_14_MANDATORY",
                    description_de="Name oder Anschrift des Leistungsempfängers (Käufer) fehlt bei Rechnung > 250 €.",
                    description_en="Buyer name or address missing for invoice exceeding 250 EUR.",
                    statutory_reference="§ 14 Abs. 4 Satz 1 Nr. 1 UStG · § 33 UStDV",
                )
            )

        # Check 6: Description & Quantity of Supply (§ 14 Abs. 4 Nr. 5 UStG)
        if len(extraction.line_items) > 0 and all(item.item_name for item in extraction.line_items):
            mandatory_checks_passed += 1
        else:
            findings.append(
                VatFinding(
                    code="USTG-14-06",
                    severity="WARNING",
                    category="USTG_14_MANDATORY",
                    description_de="Leistungsbeschreibung oder Mengenangabe in den Rechnungspositionen unvollständig.",
                    description_en="Line item descriptions or quantities are incomplete.",
                    statutory_reference="§ 14 Abs. 4 Satz 1 Nr. 5 UStG",
                )
            )

        # ------------------------------------------------------------------
        # 2. Tax Rate Validity & Mathematical Recalculation Audit
        # ------------------------------------------------------------------
        seller_country = (extraction.seller.postal_address.country_id if extraction.seller.postal_address else "DE") or "DE"
        buyer_country = (extraction.buyer.postal_address.country_id if extraction.buyer.postal_address else "DE") or "DE"

        recalculated_tax = 0.0
        if len(extraction.tax_subtotals) > 0:
            for sub in extraction.tax_subtotals:
                expected_sub_tax = round(sub.taxable_amount_eur * (sub.tax_rate_percent / 100.0), 2)
                recalculated_tax += expected_sub_tax

                # Individual subtotal check
                if not math.isclose(expected_sub_tax, sub.tax_amount_eur, abs_tol=0.02):
                    findings.append(
                        VatFinding(
                            code="USTG-CALC-SUB",
                            severity="CRITICAL",
                            category="RATE_DISCREPANCY",
                            description_de=f"Steuerberechnungsfehler bei {sub.tax_rate_percent:.1f}% (Kategorie {sub.tax_category_code}): Berechnet {expected_sub_tax:.2f} €, ausgewiesen {sub.tax_amount_eur:.2f} €.",
                            description_en=f"VAT calculation error at {sub.tax_rate_percent:.1f}%: Expected {expected_sub_tax:.2f} EUR, declared {sub.tax_amount_eur:.2f} EUR.",
                            statutory_reference="§ 14 Abs. 4 Nr. 8 UStG · EN 16931 BR-S-08",
                            expected_value=f"{expected_sub_tax:.2f} EUR",
                            found_value=f"{sub.tax_amount_eur:.2f} EUR",
                        )
                    )

                # Domestic German VAT Rate legality check (§ 12 UStG)
                if seller_country == "DE" and buyer_country == "DE" and sub.tax_category_code == VatCategoryCode.STANDARD:
                    if sub.tax_rate_percent not in cls.VALID_GERMAN_STANDARD_RATES:
                        findings.append(
                            VatFinding(
                                code="USTG-12-RATE",
                                severity="CRITICAL",
                                category="RATE_DISCREPANCY",
                                description_de=f"Unzulässiger deutscher Umsatzsteuersatz {sub.tax_rate_percent:.1f}% (zulässig gem. § 12 UStG: 19,0% oder 7,0%).",
                                description_en=f"Unauthorized German domestic VAT rate {sub.tax_rate_percent:.1f}% (statutory rates under § 12 UStG: 19.0% or 7.0%).",
                                statutory_reference="§ 12 Abs. 1 & 2 UStG",
                                expected_value="19.0% oder 7.0%",
                                found_value=f"{sub.tax_rate_percent:.1f}%",
                            )
                        )
        else:
            for item in extraction.line_items:
                recalculated_tax += round(item.line_total_eur * (item.vat_rate_percent / 100.0), 2)

        recalculated_tax = round(recalculated_tax, 2)
        tax_discrepancy = round(abs(recalculated_tax - ms.tax_total_amount_eur), 2)

        if tax_discrepancy > 0.02:
            findings.append(
                VatFinding(
                    code="USTG-CALC-TOTAL",
                    severity="CRITICAL",
                    category="RATE_DISCREPANCY",
                    description_de=f"Abweichung der Gesamtsteuer: Rechnerisch {recalculated_tax:.2f} €, ausgewiesen {ms.tax_total_amount_eur:.2f} € (Differenz: {tax_discrepancy:.2f} €).",
                    description_en=f"Total VAT mismatch: Recalculated {recalculated_tax:.2f} EUR vs. declared {ms.tax_total_amount_eur:.2f} EUR.",
                    statutory_reference="§ 14 Abs. 4 Nr. 8 UStG · § 14c UStG Risiko unrichtiger Steuerausweis",
                    expected_value=f"{recalculated_tax:.2f} EUR",
                    found_value=f"{ms.tax_total_amount_eur:.2f} EUR",
                )
            )

        # ------------------------------------------------------------------
        # 3. Reverse Charge (§ 13b UStG) & Intra-Community (§ 6a UStG) Checks
        # ------------------------------------------------------------------
        reverse_charge_detected = any(
            sub.tax_category_code == VatCategoryCode.REVERSE_CHARGE for sub in extraction.tax_subtotals
        ) or any(item.vat_category_code == VatCategoryCode.REVERSE_CHARGE for item in extraction.line_items)

        intra_community_detected = any(
            sub.tax_category_code == VatCategoryCode.INTRA_COMMUNITY for sub in extraction.tax_subtotals
        ) or any(item.vat_category_code == VatCategoryCode.INTRA_COMMUNITY for item in extraction.line_items)

        raw_lower = (extraction.raw_xml_content or "").lower()
        terms_lower = (extraction.payment_terms_description or "").lower()
        combined_notes = raw_lower + " " + terms_lower

        if reverse_charge_detected:
            # Under § 13b UStG, VAT must be 0% and statutory notice is mandatory (§ 14a Abs. 5 UStG)
            ae_with_tax = [
                sub for sub in extraction.tax_subtotals
                if sub.tax_category_code == VatCategoryCode.REVERSE_CHARGE and (sub.tax_rate_percent > 0 or sub.tax_amount_eur > 0)
            ]
            if ae_with_tax:
                findings.append(
                    VatFinding(
                        code="USTG-13B-TAX",
                        severity="CRITICAL",
                        category="REVERSE_CHARGE",
                        description_de="Unzulässiger Steuerausweis bei Reverse-Charge (AE): Bei § 13b UStG darf keine Umsatzsteuer berechnet werden (0,00 €).",
                        description_en="Illegal VAT charge under Reverse Charge (AE): § 13b UStG requires 0% tax on the invoice.",
                        statutory_reference="§ 13b UStG · § 14c Abs. 1 UStG",
                        expected_value="0.00 EUR (0%)",
                        found_value=f"{ae_with_tax[0].tax_amount_eur:.2f} EUR ({ae_with_tax[0].tax_rate_percent}%)",
                    )
                )

            has_rc_notice = any(
                phrase in combined_notes
                for phrase in ["steuerschuldnerschaft des leistungsempfängers", "reverse charge", "reverse-charge", "§ 13b"]
            )
            if not has_rc_notice:
                findings.append(
                    VatFinding(
                        code="USTG-14A-RC",
                        severity="WARNING",
                        category="REVERSE_CHARGE",
                        description_de="Hinweis 'Steuerschuldnerschaft des Leistungsempfängers' (§ 14a Abs. 5 UStG) im XML nicht explizit enthalten.",
                        description_en="Mandatory statutory notice 'Reverse Charge / Steuerschuldnerschaft des Leistungsempfängers' missing.",
                        statutory_reference="§ 14a Abs. 5 UStG",
                    )
                )

        if intra_community_detected:
            if not extraction.buyer.vat_id:
                findings.append(
                    VatFinding(
                        code="USTG-6A-BUYER-VAT",
                        severity="CRITICAL",
                        category="INTRA_COMMUNITY",
                        description_de="Steuerfreie innergemeinschaftliche Lieferung (K) ohne gültige USt-IdNr. des Käufers unzulässig.",
                        description_en="Tax-exempt intra-community supply (K) requires Buyer's valid EU VAT ID.",
                        statutory_reference="§ 6a Abs. 1 Nr. 4 UStG · § 14a Abs. 3 UStG",
                    )
                )

        # Cross-border warning: Seller DE, Buyer another EU country with EU VAT ID, yet charged 19% VAT
        if (
            seller_country == "DE"
            and buyer_country in cls.EU_MEMBER_STATES
            and buyer_country != "DE"
            and extraction.buyer.vat_id
            and ms.tax_total_amount_eur > 0
            and not reverse_charge_detected
            and not intra_community_detected
        ):
            findings.append(
                VatFinding(
                    code="USTG-CROSSBORDER-VAT",
                    severity="WARNING",
                    category="INTRA_COMMUNITY",
                    description_de=f"Grenzüberschreitende B2B-Leistung ({seller_country} ➔ {buyer_country}) mit USt-IdNr. '{extraction.buyer.vat_id}' enthält {ms.tax_total_amount_eur:.2f} € deutsche USt. Prüfen Sie Steuerbefreiung (§ 6a UStG) oder Reverse Charge (§ 13b UStG).",
                    description_en=f"Cross-border EU B2B supply ({seller_country} -> {buyer_country}) includes domestic VAT despite buyer VAT ID. Verify § 6a or § 13b exemption.",
                    statutory_reference="§ 4 Nr. 1b · § 6a · § 13b UStG",
                )
            )

        critical_count = sum(1 for f in findings if f.severity == "CRITICAL")
        is_ustg_compliant = critical_count == 0
        mandatory_score = round((mandatory_checks_passed / mandatory_checks_total) * 100.0, 1)

        if is_ustg_compliant:
            summary_de = (
                f"Rechnung '{extraction.invoice_number}' erfüllt sämtliche steuerrechtlichen Voraussetzungen nach § 14 UStG "
                f"(Pflichtangaben: {mandatory_score:.0f}%, rechnerische Steuerabweichung: {tax_discrepancy:.2f} €)."
            )
        else:
            summary_de = (
                f"Steuerprüfung ergab {critical_count} schwerwiegende Beanstandungen nach § 14 / § 13b UStG "
                f"(Vorsteuerabzug gefährdet; Steuerdifferenz: {tax_discrepancy:.2f} €)."
            )

        return VatAuditReport(
            is_ustg_compliant=is_ustg_compliant,
            is_small_value_invoice=is_small_value,
            reverse_charge_detected=reverse_charge_detected,
            intra_community_supply_detected=intra_community_detected,
            recalculated_tax_total_eur=recalculated_tax,
            declared_tax_total_eur=ms.tax_total_amount_eur,
            tax_discrepancy_eur=tax_discrepancy,
            mandatory_fields_score_percent=mandatory_score,
            findings=findings,
            audit_summary_de=summary_de,
        )


vat_auditor = VatAuditorService()
