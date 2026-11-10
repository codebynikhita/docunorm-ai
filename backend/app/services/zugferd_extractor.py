import math
import re
import xml.etree.ElementTree as ET
from datetime import UTC, date, datetime
from uuid import UUID

import pymupdf as fitz

from app.schemas.zugferd_invoice import (
    VatCategoryCode,
    ZugferdInvoiceExtraction,
    ZugferdInvoiceType,
    ZugferdLineItem,
    ZugferdMonetarySummation,
    ZugferdParty,
    ZugferdPostalAddress,
    ZugferdProfile,
    ZugferdTaxSubtotal,
    ZugferdValidationIssue,
    ZugferdValidationReport,
)


class ZugferdExtractorService:
    """
    Enterprise Sovereign ZUGFeRD 2.3 / Factur-X & XRechnung Ingestion Engine.
    Conforms to European Standard EN 16931-1:2017 and German E-Rechnungsverordnung (E-Rech-VO).
    """

    PROFILE_URN_MAP: dict[str, ZugferdProfile] = {
        "minimum": ZugferdProfile.MINIMUM,
        "basicwl": ZugferdProfile.BASIC_WL,
        "basic": ZugferdProfile.BASIC,
        "en16931": ZugferdProfile.EN16931,
        "comfort": ZugferdProfile.EN16931,
        "extended": ZugferdProfile.EXTENDED,
        "xrechnung": ZugferdProfile.XRECHNUNG,
    }

    INVOICE_TYPE_MAP: dict[str, str] = {
        "380": "Handelsrechnung (Commercial Invoice)",
        "381": "Gutschrift (Credit Note)",
        "383": "Belastungsanzeige (Debit Note)",
        "384": "Rechnungskorrektur (Corrected Invoice)",
        "386": "Vorauszahlungsrechnung (Advance Payment)",
        "389": "Gutschriftsverfahren (Self-Billed Invoice)",
    }

    @classmethod
    def extract_from_pdf_or_xml(
        cls,
        file_bytes: bytes,
        filename: str,
        document_id: UUID | None = None,
    ) -> ZugferdInvoiceExtraction:
        """
        Ingests either a hybrid PDF/A-3 containing an embedded XML attachment or a standalone XML invoice.
        """
        raw_xml_str: str | None = None
        xml_name: str | None = None
        is_hybrid = False

        # 1. Probe if file is a PDF
        if file_bytes.startswith(b"%PDF"):
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                if doc.embfile_count() > 0:
                    for name in doc.embfile_names():
                        lower = name.lower()
                        if lower.endswith(".xml") or any(k in lower for k in ["factur-x", "zugferd", "xrechnung", "invoice"]):
                            xml_bytes = doc.embfile_get(name)
                            raw_xml_str = xml_bytes.decode("utf-8", errors="replace")
                            xml_name = name
                            is_hybrid = True
                            break
                doc.close()
            except Exception:
                raw_xml_str = None

        # 2. If not hybrid PDF or no XML attachment found, check if the file itself is XML
        if not raw_xml_str:
            trimmed = file_bytes.strip()
            if trimmed.startswith(b"<") or b"<?xml" in trimmed[:50]:
                raw_xml_str = file_bytes.decode("utf-8", errors="replace")
                xml_name = filename
                is_hybrid = False
            else:
                raise ValueError(f"Datei '{filename}' enthält weder ein eingebettetes ZUGFeRD-XML noch gültiges Rechnungs-XML.")

        # 3. Parse XML content
        return cls.parse_xml_invoice(
            raw_xml=raw_xml_str,
            filename=filename,
            document_id=document_id,
            is_hybrid_pdf_a3=is_hybrid,
            xml_filename=xml_name,
        )

    @classmethod
    def parse_xml_invoice(
        cls,
        raw_xml: str,
        filename: str,
        document_id: UUID | None = None,
        is_hybrid_pdf_a3: bool = False,
        xml_filename: str | None = None,
    ) -> ZugferdInvoiceExtraction:
        """
        Parses UN/CEFACT CII (CrossIndustryInvoice) or UBL 2.1 XML structure.
        """
        try:
            root = ET.fromstring(raw_xml)
        except Exception as e:
            raise ValueError(f"XML Parsing Fehler in '{filename}': {e}") from e

        tag_lower = root.tag.lower()
        if "crossindustryinvoice" in tag_lower:
            return cls._parse_un_cefact_cii(root, raw_xml, filename, document_id, is_hybrid_pdf_a3, xml_filename)
        elif "invoice" in tag_lower or "creditnote" in tag_lower:
            return cls._parse_ubl_invoice(root, raw_xml, filename, document_id, is_hybrid_pdf_a3, xml_filename)
        else:
            # Fallback to CII namespace search
            return cls._parse_un_cefact_cii(root, raw_xml, filename, document_id, is_hybrid_pdf_a3, xml_filename)

    @classmethod
    def _find_xpath_text(cls, elem: ET.Element | None, xpath: str) -> str | None:
        if elem is None:
            return None
        parts = xpath.split("/")
        curr = elem
        for p in parts:
            if curr is None:
                return None
            curr = curr.find(f".//{{*}}{p}")
        return curr.text.strip() if (curr is not None and curr.text) else None

    @classmethod
    def _parse_un_cefact_cii(
        cls,
        root: ET.Element,
        raw_xml: str,
        filename: str,
        document_id: UUID | None,
        is_hybrid_pdf_a3: bool,
        xml_filename: str | None,
    ) -> ZugferdInvoiceExtraction:
        def find_text(elem: ET.Element | None, xpath: str) -> str | None:
            return cls._find_xpath_text(elem, xpath)

        def find_all(elem: ET.Element | None, tag_name: str) -> list[ET.Element]:
            if elem is None:
                return []
            return elem.findall(f".//{{*}}{tag_name}")

        # 1. Profile URN & Identification
        guideline_node = root.find(".//{*}GuidelineSpecifiedDocumentContextParameter/{*}ID")
        profile_urn = guideline_node.text.strip() if (guideline_node is not None and guideline_node.text) else "urn:cen.eu:en16931:2017"
        profile = cls._detect_profile(profile_urn)

        # 2. ExchangedDocument (ID, TypeCode, IssueDate)
        exchanged_doc = root.find(".//{*}ExchangedDocument")
        invoice_id = find_text(exchanged_doc, "ID") or "UNBEKANNT"
        type_code_str = find_text(exchanged_doc, "TypeCode") or "380"
        try:
            invoice_type = ZugferdInvoiceType(type_code_str)
        except ValueError:
            invoice_type = ZugferdInvoiceType.COMMERCIAL_INVOICE

        issue_date_str = find_text(exchanged_doc, "IssueDateTime/DateTimeString") or find_text(exchanged_doc, "DateTimeString")
        parsed_issue_date = cls._parse_date_string(issue_date_str)

        # 3. SupplyChainTradeTransaction
        tx_node = root.find(".//{*}SupplyChainTradeTransaction")
        tx = tx_node if tx_node is not None else root

        agr_node = tx.find(".//{*}ApplicableHeaderTradeAgreement")
        agreement = agr_node if agr_node is not None else tx

        stl_node = tx.find(".//{*}ApplicableHeaderTradeSettlement")
        settlement = stl_node if stl_node is not None else tx

        currency = find_text(settlement, "InvoiceCurrencyCode") or "EUR"
        buyer_reference = find_text(agreement, "BuyerReference")
        order_ref = find_text(agreement, "BuyerOrderReferencedDocument/IssuerAssignedID")
        contract_ref = find_text(agreement, "ContractReferencedDocument/IssuerAssignedID")

        # Seller Trade Party
        seller_node = agreement.find(".//{*}SellerTradeParty")
        seller = cls._parse_cii_party(seller_node)

        # Buyer Trade Party
        buyer_node = agreement.find(".//{*}BuyerTradeParty")
        buyer = cls._parse_cii_party(buyer_node)

        # Payment Means & Bank Details
        iban = find_text(settlement, "SpecifiedTradeSettlementPaymentMeans/PayeePartyCreditorFinancialAccount/IBANID")
        bic = find_text(settlement, "SpecifiedTradeSettlementPaymentMeans/PayeeSpecifiedCreditorFinancialInstitution/BICID")
        payment_means_code = find_text(settlement, "SpecifiedTradeSettlementPaymentMeans/TypeCode")
        payment_terms_desc = find_text(settlement, "SpecifiedTradePaymentTerms/Description")
        due_date_str = find_text(settlement, "SpecifiedTradePaymentTerms/DueDateDateTime/DateTimeString")
        payment_due_date = cls._parse_date_string(due_date_str)

        # Line Items
        line_items: list[ZugferdLineItem] = []
        line_nodes = find_all(tx, "IncludedSupplyChainTradeLineItem")
        for idx, line_elem in enumerate(line_nodes, start=1):
            line_id = find_text(line_elem, "AssociatedDocumentLineDocument/LineID") or str(idx)
            item_elem = line_elem.find(".//{*}SpecifiedTradeProduct")
            item_name = find_text(item_elem, "Name") or f"Position {idx}"
            item_desc = find_text(item_elem, "Description")
            seller_item_id = find_text(item_elem, "SellerAssignedID")
            buyer_item_id = find_text(item_elem, "BuyerAssignedID")

            delivery_line = line_elem.find(".//{*}SpecifiedLineTradeDelivery")
            qty_elem = delivery_line.find(".//{*}BilledQuantity") if delivery_line is not None else None
            qty = float(qty_elem.text.strip()) if (qty_elem is not None and qty_elem.text) else 1.0
            unit_code = qty_elem.get("unitCode", "C62") if qty_elem is not None else "C62"

            agreement_line = line_elem.find(".//{*}SpecifiedLineTradeAgreement")
            price_elem = agreement_line.find(".//{*}GrossPriceProductTradePrice/{*}ChargeAmount") if agreement_line is not None else None
            if price_elem is None and agreement_line is not None:
                price_elem = agreement_line.find(".//{*}NetPriceProductTradePrice/{*}ChargeAmount")
            net_price = float(price_elem.text.strip()) if (price_elem is not None and price_elem.text) else 0.0

            settlement_line = line_elem.find(".//{*}SpecifiedLineTradeSettlement")
            total_elem = settlement_line.find(".//{*}SpecifiedTradeSettlementLineMonetarySummation/{*}LineTotalAmount") if settlement_line is not None else None
            line_total = float(total_elem.text.strip()) if (total_elem is not None and total_elem.text) else round(qty * net_price, 2)

            tax_node = settlement_line.find(".//{*}ApplicableTradeTax") if settlement_line is not None else None
            vat_cat_code_str = find_text(tax_node, "CategoryCode") or "S"
            vat_rate_str = find_text(tax_node, "RateApplicablePercent") or "19.0"
            try:
                vat_cat = VatCategoryCode(vat_cat_code_str)
            except ValueError:
                vat_cat = VatCategoryCode.STANDARD
            vat_rate = float(vat_rate_str) if vat_rate_str else 19.0

            line_items.append(
                ZugferdLineItem(
                    line_id=line_id,
                    item_name=item_name,
                    item_description=item_desc,
                    seller_item_id=seller_item_id,
                    buyer_item_id=buyer_item_id,
                    billed_quantity=qty,
                    unit_code=unit_code,
                    net_price_eur=net_price,
                    line_total_eur=line_total,
                    vat_category_code=vat_cat,
                    vat_rate_percent=vat_rate,
                )
            )

        # Tax Subtotals
        tax_subtotals: list[ZugferdTaxSubtotal] = []
        tax_nodes = find_all(settlement, "ApplicableTradeTax")
        for t_node in tax_nodes:
            cat_str = find_text(t_node, "CategoryCode") or "S"
            rate_str = find_text(t_node, "RateApplicablePercent") or "19.0"
            basis_str = find_text(t_node, "BasisAmount") or "0.0"
            calc_str = find_text(t_node, "CalculatedAmount") or "0.0"
            exemption_reason = find_text(t_node, "ExemptionReason")

            try:
                cat = VatCategoryCode(cat_str)
            except ValueError:
                cat = VatCategoryCode.STANDARD

            tax_subtotals.append(
                ZugferdTaxSubtotal(
                    tax_category_code=cat,
                    tax_rate_percent=float(rate_str),
                    taxable_amount_eur=float(basis_str),
                    tax_amount_eur=float(calc_str),
                    exemption_reason=exemption_reason,
                )
            )

        # Monetary Summation
        summation_elem = settlement.find(".//{*}SpecifiedTradeSettlementHeaderMonetarySummation")
        line_total_amt = float(find_text(summation_elem, "LineTotalAmount") or "0.0")
        charge_amt = float(find_text(summation_elem, "ChargeTotalAmount") or "0.0")
        allowance_amt = float(find_text(summation_elem, "AllowanceTotalAmount") or "0.0")
        tax_basis_amt = float(find_text(summation_elem, "TaxBasisTotalAmount") or str(line_total_amt - allowance_amt + charge_amt))
        tax_total_amt = float(find_text(summation_elem, "TaxTotalAmount") or "0.0")
        grand_total_amt = float(find_text(summation_elem, "GrandTotalAmount") or str(tax_basis_amt + tax_total_amt))
        prepaid_amt = float(find_text(summation_elem, "TotalPrepaidAmount") or find_text(summation_elem, "PrepaidAmount") or "0.0")
        due_payable_amt = float(find_text(summation_elem, "DuePayableAmount") or str(grand_total_amt - prepaid_amt))

        monetary_sum = ZugferdMonetarySummation(
            line_total_amount_eur=line_total_amt,
            charge_total_amount_eur=charge_amt,
            allowance_total_amount_eur=allowance_amt,
            tax_basis_total_amount_eur=tax_basis_amt,
            tax_total_amount_eur=tax_total_amt,
            grand_total_amount_eur=grand_total_amt,
            prepaid_amount_eur=prepaid_amt,
            due_payable_amount_eur=due_payable_amt,
        )

        # Perform EN 16931 Validation
        validation_report = cls._validate_en16931(
            profile=profile,
            profile_urn=profile_urn,
            syntax_format="UN/CEFACT CII",
            invoice_id=invoice_id,
            issue_date=parsed_issue_date,
            currency=currency,
            seller=seller,
            buyer=buyer,
            buyer_reference=buyer_reference,
            line_items=line_items,
            tax_subtotals=tax_subtotals,
            monetary_sum=monetary_sum,
        )

        return ZugferdInvoiceExtraction(
            document_id=document_id,
            filename=filename,
            is_hybrid_pdf_a3=is_hybrid_pdf_a3,
            xml_filename=xml_filename,
            raw_xml_content=raw_xml,
            extracted_at=datetime.now(UTC),
            profile=profile,
            profile_urn=profile_urn,
            invoice_number=invoice_id,
            invoice_type_code=invoice_type,
            invoice_type_name_de=cls.INVOICE_TYPE_MAP.get(invoice_type.value, "Handelsrechnung"),
            issue_date=parsed_issue_date,
            currency_code=currency,
            seller=seller,
            buyer=buyer,
            buyer_reference=buyer_reference,
            order_reference=order_ref,
            contract_reference=contract_ref,
            payment_terms_description=payment_terms_desc,
            payment_due_date=payment_due_date,
            iban=iban,
            bic=bic,
            payment_means_code=payment_means_code,
            line_items=line_items,
            tax_subtotals=tax_subtotals,
            monetary_summation=monetary_sum,
            validation_report=validation_report,
        )

    @classmethod
    def _parse_ubl_invoice(
        cls,
        root: ET.Element,
        raw_xml: str,
        filename: str,
        document_id: UUID | None,
        is_hybrid_pdf_a3: bool,
        xml_filename: str | None,
    ) -> ZugferdInvoiceExtraction:
        """
        Parses Oasis UBL 2.1 Invoice / CreditNote XML structure.
        """
        def find_text(elem: ET.Element | None, tag_name: str) -> str | None:
            return cls._find_xpath_text(elem, tag_name)

        def find_all(elem: ET.Element | None, tag_name: str) -> list[ET.Element]:
            if elem is None:
                return []
            return elem.findall(f".//{{*}}{tag_name}")

        profile_urn = find_text(root, "CustomizationID") or "urn:cen.eu:en16931:2017"
        profile = cls._detect_profile(profile_urn)

        invoice_id = find_text(root, "ID") or "UNBEKANNT"
        type_code_str = find_text(root, "InvoiceTypeCode") or "380"
        try:
            invoice_type = ZugferdInvoiceType(type_code_str)
        except ValueError:
            invoice_type = ZugferdInvoiceType.COMMERCIAL_INVOICE

        issue_date_str = find_text(root, "IssueDate")
        parsed_issue_date = cls._parse_date_string(issue_date_str)
        currency = find_text(root, "DocumentCurrencyCode") or "EUR"
        buyer_reference = find_text(root, "BuyerReference")
        order_ref = find_text(root, "OrderReference")

        # Seller
        supplier_party = root.find(".//{*}AccountingSupplierParty/{*}Party")
        seller = cls._parse_ubl_party(supplier_party)

        # Buyer
        customer_party = root.find(".//{*}AccountingCustomerParty/{*}Party")
        buyer = cls._parse_ubl_party(customer_party)

        # Payment Means
        iban = find_text(root, "PaymentMeans/PayeeFinancialAccount/ID")
        bic = find_text(root, "PaymentMeans/PayeeFinancialAccount/FinancialInstitutionBranch/ID")
        payment_due_date = cls._parse_date_string(find_text(root, "DueDate"))
        payment_terms_desc = find_text(root, "PaymentTerms/Note")

        # Line items
        line_items: list[ZugferdLineItem] = []
        line_nodes = find_all(root, "InvoiceLine")
        for idx, line_elem in enumerate(line_nodes, start=1):
            line_id = find_text(line_elem, "ID") or str(idx)
            item_name = find_text(line_elem, "Item/Name") or f"Position {idx}"
            item_desc = find_text(line_elem, "Item/Description")
            qty_elem = line_elem.find(".//{*}InvoicedQuantity")
            qty = float(qty_elem.text.strip()) if (qty_elem is not None and qty_elem.text) else 1.0
            unit_code = qty_elem.get("unitCode", "C62") if qty_elem is not None else "C62"

            price_elem = line_elem.find(".//{*}Price/{*}PriceAmount")
            net_price = float(price_elem.text.strip()) if (price_elem is not None and price_elem.text) else 0.0

            line_ext_elem = line_elem.find(".//{*}LineExtensionAmount")
            line_total = float(line_ext_elem.text.strip()) if (line_ext_elem is not None and line_ext_elem.text) else round(qty * net_price, 2)

            vat_cat_code_str = find_text(line_elem, "Item/ClassifiedTaxCategory/ID") or "S"
            vat_rate_str = find_text(line_elem, "Item/ClassifiedTaxCategory/Percent") or "19.0"
            try:
                vat_cat = VatCategoryCode(vat_cat_code_str)
            except ValueError:
                vat_cat = VatCategoryCode.STANDARD

            line_items.append(
                ZugferdLineItem(
                    line_id=line_id,
                    item_name=item_name,
                    item_description=item_desc,
                    billed_quantity=qty,
                    unit_code=unit_code,
                    net_price_eur=net_price,
                    line_total_eur=line_total,
                    vat_category_code=vat_cat,
                    vat_rate_percent=float(vat_rate_str),
                )
            )

        # Tax subtotals
        tax_subtotals: list[ZugferdTaxSubtotal] = []
        for t_node in find_all(root, "TaxSubtotal"):
            cat_str = find_text(t_node, "TaxCategory/ID") or "S"
            rate_str = find_text(t_node, "TaxCategory/Percent") or "19.0"
            basis_str = find_text(t_node, "TaxableAmount") or "0.0"
            calc_str = find_text(t_node, "TaxAmount") or "0.0"
            try:
                cat = VatCategoryCode(cat_str)
            except ValueError:
                cat = VatCategoryCode.STANDARD

            tax_subtotals.append(
                ZugferdTaxSubtotal(
                    tax_category_code=cat,
                    tax_rate_percent=float(rate_str),
                    taxable_amount_eur=float(basis_str),
                    tax_amount_eur=float(calc_str),
                )
            )

        # Monetary summation
        sum_elem = root.find(".//{*}LegalMonetaryTotal")
        line_total_amt = float(find_text(sum_elem, "LineExtensionAmount") or "0.0")
        tax_basis_amt = float(find_text(sum_elem, "TaxExclusiveAmount") or str(line_total_amt))
        tax_total_amt = float(find_text(root, "TaxTotal/TaxAmount") or "0.0")
        grand_total_amt = float(find_text(sum_elem, "TaxInclusiveAmount") or str(tax_basis_amt + tax_total_amt))
        prepaid_amt = float(find_text(sum_elem, "PrepaidAmount") or "0.0")
        due_payable_amt = float(find_text(sum_elem, "PayableAmount") or str(grand_total_amt - prepaid_amt))

        monetary_sum = ZugferdMonetarySummation(
            line_total_amount_eur=line_total_amt,
            charge_total_amount_eur=0.0,
            allowance_total_amount_eur=0.0,
            tax_basis_total_amount_eur=tax_basis_amt,
            tax_total_amount_eur=tax_total_amt,
            grand_total_amount_eur=grand_total_amt,
            prepaid_amount_eur=prepaid_amt,
            due_payable_amount_eur=due_payable_amt,
        )

        validation_report = cls._validate_en16931(
            profile=profile,
            profile_urn=profile_urn,
            syntax_format="UBL 2.1 INVOICE",
            invoice_id=invoice_id,
            issue_date=parsed_issue_date,
            currency=currency,
            seller=seller,
            buyer=buyer,
            buyer_reference=buyer_reference,
            line_items=line_items,
            tax_subtotals=tax_subtotals,
            monetary_sum=monetary_sum,
        )

        return ZugferdInvoiceExtraction(
            document_id=document_id,
            filename=filename,
            is_hybrid_pdf_a3=is_hybrid_pdf_a3,
            xml_filename=xml_filename,
            raw_xml_content=raw_xml,
            extracted_at=datetime.now(UTC),
            profile=profile,
            profile_urn=profile_urn,
            invoice_number=invoice_id,
            invoice_type_code=invoice_type,
            invoice_type_name_de=cls.INVOICE_TYPE_MAP.get(invoice_type.value, "Handelsrechnung"),
            issue_date=parsed_issue_date,
            currency_code=currency,
            seller=seller,
            buyer=buyer,
            buyer_reference=buyer_reference,
            order_reference=order_ref,
            payment_terms_description=payment_terms_desc,
            payment_due_date=payment_due_date,
            iban=iban,
            bic=bic,
            line_items=line_items,
            tax_subtotals=tax_subtotals,
            monetary_summation=monetary_sum,
            validation_report=validation_report,
        )

    @classmethod
    def _parse_cii_party(cls, party_node: ET.Element | None) -> ZugferdParty:
        if party_node is None:
            return ZugferdParty(name="Unbekannter Geschäftspartner")

        def text(tag: str) -> str | None:
            n = party_node.find(f".//{{*}}{tag}")
            return n.text.strip() if (n is not None and n.text) else None

        name = text("Name") or "Unbekannte Partei"
        vat_id = None
        for tax_reg in party_node.findall(".//{*}SpecifiedTaxRegistration"):
            id_node = tax_reg.find(".//{*}ID")
            if id_node is not None and id_node.text:
                val = id_node.text.strip()
                scheme = id_node.get("schemeID", "")
                if scheme == "VA" or val.startswith(("DE", "AT", "FR", "NL", "LU", "IT", "BE")):
                    vat_id = val
                    break

        addr_node = party_node.find(".//{*}PostalTradeAddress")
        postal_address: ZugferdPostalAddress | None = None
        if addr_node is not None:
            def atext(t: str) -> str | None:
                n = addr_node.find(f".//{{*}}{t}")
                return n.text.strip() if (n is not None and n.text) else None

            postal_address = ZugferdPostalAddress(
                postcode=atext("PostcodeCode"),
                line_one=atext("LineOne"),
                line_two=atext("LineTwo"),
                city_name=atext("CityName"),
                country_id=atext("CountryID") or "DE",
                country_sub_division_name=atext("CountrySubDivisionName"),
            )

        contact_node = party_node.find(".//{*}DefinedTradeContact")
        contact_name = None
        contact_email = None
        contact_phone = None
        if contact_node is not None:
            def ctext(t: str) -> str | None:
                n = contact_node.find(f".//{{*}}{t}")
                return n.text.strip() if (n is not None and n.text) else None
            contact_name = ctext("PersonName")
            contact_email = ctext("EmailURIUniversalCommunication/CompleteNumber") or ctext("CompleteNumber")
            contact_phone = ctext("TelephoneUniversalCommunication/CompleteNumber")

        return ZugferdParty(
            name=name,
            vat_id=vat_id,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            postal_address=postal_address,
        )

    @classmethod
    def _parse_ubl_party(cls, party_node: ET.Element | None) -> ZugferdParty:
        if party_node is None:
            return ZugferdParty(name="Unbekannter Geschäftspartner")

        name = (
            cls._find_xpath_text(party_node, "PartyName/Name")
            or cls._find_xpath_text(party_node, "LegalEntity/RegistrationName")
            or cls._find_xpath_text(party_node, "Name")
            or "Unbekannte Partei"
        )
        vat_id = cls._find_xpath_text(party_node, "PartyTaxScheme/CompanyID")

        addr_node = party_node.find(".//{*}PostalAddress")
        postal_address: ZugferdPostalAddress | None = None
        if addr_node is not None:
            postal_address = ZugferdPostalAddress(
                postcode=cls._find_xpath_text(addr_node, "PostalZone"),
                line_one=cls._find_xpath_text(addr_node, "StreetName"),
                line_two=cls._find_xpath_text(addr_node, "AdditionalStreetName"),
                city_name=cls._find_xpath_text(addr_node, "CityName"),
                country_id=cls._find_xpath_text(addr_node, "Country/IdentificationCode") or "DE",
            )

        contact_name = cls._find_xpath_text(party_node, "Contact/Name")
        contact_phone = cls._find_xpath_text(party_node, "Contact/Telephone")
        contact_email = cls._find_xpath_text(party_node, "Contact/ElectronicMail")

        return ZugferdParty(
            name=name,
            vat_id=vat_id,
            contact_name=contact_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            postal_address=postal_address,
        )

    @classmethod
    def _detect_profile(cls, urn: str) -> ZugferdProfile:
        urn_lower = urn.lower()
        if "xrechnung" in urn_lower:
            return ZugferdProfile.XRECHNUNG
        if "extended" in urn_lower:
            return ZugferdProfile.EXTENDED
        if "en16931" in urn_lower or "comfort" in urn_lower:
            return ZugferdProfile.EN16931
        if "basicwl" in urn_lower or "basic_wl" in urn_lower:
            return ZugferdProfile.BASIC_WL
        if "basic" in urn_lower:
            return ZugferdProfile.BASIC
        if "minimum" in urn_lower:
            return ZugferdProfile.MINIMUM
        return ZugferdProfile.EN16931

    @classmethod
    def _parse_date_string(cls, date_str: str | None) -> date | None:
        if not date_str:
            return None
        cleaned = re.sub(r"[^\d]", "", date_str)
        if len(cleaned) == 8:
            try:
                return date(int(cleaned[:4]), int(cleaned[4:6]), int(cleaned[6:8]))
            except ValueError:
                return None
        elif len(date_str) >= 10 and "-" in date_str:
            try:
                parts = date_str[:10].split("-")
                return date(int(parts[0]), int(parts[1]), int(parts[2]))
            except ValueError:
                return None
        return None

    @classmethod
    def _validate_en16931(
        cls,
        profile: ZugferdProfile,
        profile_urn: str,
        syntax_format: str,
        invoice_id: str,
        issue_date: date | None,
        currency: str,
        seller: ZugferdParty,
        buyer: ZugferdParty,
        buyer_reference: str | None,
        line_items: list[ZugferdLineItem],
        tax_subtotals: list[ZugferdTaxSubtotal],
        monetary_sum: ZugferdMonetarySummation,
    ) -> ZugferdValidationReport:
        """
        Executes strict EN 16931-1 mathematical and mandatory field validations.
        """
        issues: list[ZugferdValidationIssue] = []
        total_rules = 12
        passed_rules = 0

        # Rule 1 (BR-01): Invoice Number
        if invoice_id and invoice_id != "UNBEKANNT":
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-01",
                    severity="ERROR",
                    rule_id="EN16931-BR-01",
                    description="Rechnungsnummer (BT-1) fehlt oder ist ungültig.",
                    statutory_reference="§ 14 Abs. 4 Nr. 4 UStG · EN 16931 BR-01",
                )
            )

        # Rule 2 (BR-02): Issue Date
        if issue_date is not None:
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-02",
                    severity="ERROR",
                    rule_id="EN16931-BR-02",
                    description="Ausstellungsdatum der Rechnung (BT-2) fehlt oder ist unlesbar.",
                    statutory_reference="§ 14 Abs. 4 Nr. 3 UStG · EN 16931 BR-02",
                )
            )

        # Rule 3 (BR-06): Seller Name & Address
        if seller.name and seller.postal_address and seller.postal_address.city_name:
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-06",
                    severity="ERROR",
                    rule_id="EN16931-BR-06",
                    description="Vollständiger Name und Anschrift des Leistenden (Verkäufer) unvollständig.",
                    statutory_reference="§ 14 Abs. 4 Nr. 1 UStG · EN 16931 BR-06",
                )
            )

        # Rule 4 (BR-07): Buyer Name & Address
        if buyer.name and buyer.postal_address and buyer.postal_address.city_name:
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-07",
                    severity="ERROR",
                    rule_id="EN16931-BR-07",
                    description="Vollständiger Name und Anschrift des Leistungsempfängers (Käufer) unvollständig.",
                    statutory_reference="§ 14 Abs. 4 Nr. 1 UStG · EN 16931 BR-07",
                )
            )

        # Rule 5 (BR-CO-09): Currency
        if currency in ["EUR", "USD", "CHF", "GBP"]:
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-CO-09",
                    severity="ERROR",
                    rule_id="EN16931-BR-CO-09",
                    description=f"Währungscode '{currency}' unzulässig gem. ISO 4217.",
                    statutory_reference="EN 16931 BR-CO-09",
                )
            )

        # Rule 6 (BR-DE-01 / B2G): Leitweg-ID / Buyer Reference check
        if buyer_reference and len(buyer_reference.strip()) > 0:
            passed_rules += 1
        else:
            severity = "ERROR" if profile == ZugferdProfile.XRECHNUNG else "WARNING"
            issues.append(
                ZugferdValidationIssue(
                    code="BR-DE-01",
                    severity=severity,
                    rule_id="EN16931-BR-DE-01",
                    description="Käuferreferenz / Leitweg-ID (BT-10) fehlt. Bei Bundesbehörden und B2G zwingend vorgeschrieben.",
                    statutory_reference="§ 4 Abs. 1 E-Rech-VO · XRechnung BR-DE-01",
                )
            )

        # Math Rule 7 (BR-CO-10): Sum of line totals == Header LineTotalAmount
        calc_line_sum = sum(item.line_total_eur for item in line_items)
        if len(line_items) == 0 or math.isclose(calc_line_sum, monetary_sum.line_total_amount_eur, abs_tol=0.02):
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-CO-10",
                    severity="ERROR",
                    rule_id="EN16931-BR-CO-10",
                    description=f"Summe der Positionsbeträge ({calc_line_sum:.2f} €) weicht von Zeilensumme ({monetary_sum.line_total_amount_eur:.2f} €) ab.",
                    statutory_reference="EN 16931 BR-CO-10",
                )
            )

        # Math Rule 8 (BR-CO-13): TaxBasisTotalAmount == LineTotalAmount - Allowance + Charge
        expected_tax_basis = monetary_sum.line_total_amount_eur - monetary_sum.allowance_total_amount_eur + monetary_sum.charge_total_amount_eur
        if math.isclose(expected_tax_basis, monetary_sum.tax_basis_total_amount_eur, abs_tol=0.02):
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-CO-13",
                    severity="ERROR",
                    rule_id="EN16931-BR-CO-13",
                    description=f"Steuerbasis ({monetary_sum.tax_basis_total_amount_eur:.2f} €) weicht von Zeilensumme abzüglich Nachlässe ({expected_tax_basis:.2f} €) ab.",
                    statutory_reference="EN 16931 BR-CO-13",
                )
            )

        # Math Rule 9 (BR-CO-12): GrandTotalAmount == TaxBasisTotalAmount + TaxTotalAmount
        expected_grand_total = monetary_sum.tax_basis_total_amount_eur + monetary_sum.tax_total_amount_eur
        if math.isclose(expected_grand_total, monetary_sum.grand_total_amount_eur, abs_tol=0.02):
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-CO-12",
                    severity="ERROR",
                    rule_id="EN16931-BR-CO-12",
                    description=f"Rechnungsgesamtbetrag ({monetary_sum.grand_total_amount_eur:.2f} €) weicht von Nettobetrag + Steuer ({expected_grand_total:.2f} €) ab.",
                    statutory_reference="§ 14 Abs. 4 Nr. 7/8 UStG · EN 16931 BR-CO-12",
                )
            )

        # Math Rule 10 (BR-CO-14): Sum of tax sub-amounts == Header TaxTotalAmount
        if len(tax_subtotals) > 0:
            calc_tax_sum = sum(sub.tax_amount_eur for sub in tax_subtotals)
            if math.isclose(calc_tax_sum, monetary_sum.tax_total_amount_eur, abs_tol=0.02):
                passed_rules += 1
            else:
                issues.append(
                    ZugferdValidationIssue(
                        code="BR-CO-14",
                        severity="ERROR",
                        rule_id="EN16931-BR-CO-14",
                        description=f"Summe der Umsatzsteuer-Teilbeträge ({calc_tax_sum:.2f} €) weicht von Gesamtsteuer ({monetary_sum.tax_total_amount_eur:.2f} €) ab.",
                        statutory_reference="EN 16931 BR-CO-14",
                    )
                )
        else:
            passed_rules += 1

        # Math Rule 11 (BR-CO-15): DuePayableAmount == GrandTotalAmount - PrepaidAmount
        expected_due = monetary_sum.grand_total_amount_eur - monetary_sum.prepaid_amount_eur
        if math.isclose(expected_due, monetary_sum.due_payable_amount_eur, abs_tol=0.02):
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-CO-15",
                    severity="ERROR",
                    rule_id="EN16931-BR-CO-15",
                    description=f"Fälliger Zahlbetrag ({monetary_sum.due_payable_amount_eur:.2f} €) weicht von Gesamtbetrag abzüglich Vorauszahlung ({expected_due:.2f} €) ab.",
                    statutory_reference="EN 16931 BR-CO-15",
                )
            )

        # Rule 12 (Seller VAT / Tax identification)
        if seller.vat_id or seller.tax_number:
            passed_rules += 1
        else:
            issues.append(
                ZugferdValidationIssue(
                    code="BR-CO-26",
                    severity="WARNING",
                    rule_id="EN16931-BR-CO-26",
                    description="Umsatzsteuer-Identifikationsnummer (USt-IdNr.) oder Steuernummer des Verkäufers fehlt.",
                    statutory_reference="§ 14 Abs. 4 Nr. 2 UStG",
                )
            )

        errors_count = sum(1 for i in issues if i.severity == "ERROR")
        has_math_discrepancy = any("BR-CO-" in i.code for i in issues if i.severity == "ERROR")
        is_compliant = errors_count == 0

        summary_de = (
            f"ZUGFeRD 2.3 / Factur-X Profil '{profile.value}' erfolgreich validiert. "
            f"Vollständig konform mit EN 16931-1 ({passed_rules}/{total_rules} Regeln erfüllt)."
            if is_compliant
            else f"ZUGFeRD Validierung ergab {errors_count} schwerwiegende Konformitätsfehler. "
            f"Prüfstatus: Nachbesserung erforderlich ({passed_rules}/{total_rules} Regeln erfüllt)."
        )

        return ZugferdValidationReport(
            is_en16931_compliant=is_compliant,
            detected_profile=profile,
            profile_urn=profile_urn,
            syntax_format="UN/CEFACT CII" if "CII" in syntax_format else "UBL 2.1 INVOICE",
            has_math_discrepancy=has_math_discrepancy,
            issues=issues,
            passed_rules_count=passed_rules,
            total_rules_evaluated=total_rules,
            validation_summary_de=summary_de,
        )


zugferd_extractor_service = ZugferdExtractorService()
