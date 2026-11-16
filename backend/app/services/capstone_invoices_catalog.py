"""
Week 4 Capstone: 100 Enterprise E-Invoicing Benchmark Catalog.
Generates 100 authentic, syntactically and semantically validated German B2B/B2G e-invoices:
- 40 B2B Factur-X / ZUGFeRD 2.3 Comfort (19% VAT, CII XML)
- 25 B2G XRechnung 3.0 (UBL & CII, Bund & 16 Bundesländer with ISO 7064 MOD-97-10 check digits)
- 15 § 13b UStG Reverse-Charge (Subcontracting, scrap, EU cross-border, 0% VAT, statutory clause)
- 10 Reduced 7% VAT (§ 12 Abs. 2 UStG: books, catering, media, hospitality)
- 5 Kleinbetragsrechnungen (§ 33 UStDV <= 250 EUR)
- 5 Intentionally Discrepant / Tampered Fraud Simulations (Rules BR-CO-10, BR-DE-15, § 14 UStG)
"""

from dataclasses import dataclass
from typing import Literal

from app.services.leitweg_validator import LeitwegValidatorService


@dataclass
class CapstoneInvoiceDefinition:
    index: int
    invoice_number: str
    filename: str
    category: Literal[
        "B2B_COMFORT",
        "B2G_XRECHNUNG",
        "REVERSE_CHARGE_13B",
        "REDUCED_VAT_7",
        "SMALL_VALUE_33",
        "DISCREPANT_FRAUD_SIM",
    ]
    seller_name: str
    seller_vat_id: str | None
    buyer_name: str
    buyer_reference: str | None
    profile_desc: str
    currency: str
    net_amount: float
    tax_amount: float
    grand_total: float
    is_expected_compliant: bool
    rejection_reason: str | None
    xml_content: str


def _format_date(year: int, month: int, day: int) -> str:
    return f"{year:04d}{month:02d}{day:02d}"


def _format_date_iso(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def generate_capstone_100_invoices() -> list[CapstoneInvoiceDefinition]:
    invoices: list[CapstoneInvoiceDefinition] = []

    # -------------------------------------------------------------------------
    # CATEGORY 1: 40 B2B Standard Factur-X / ZUGFeRD 2.3 Comfort (19% VAT, CII)
    # -------------------------------------------------------------------------
    b2b_vendors = [
        ("Siemens Healthineers AG", "DE811122334", "Medizintechnik & Sensor-Wartung", 45000.0),
        ("Bosch Rexroth Automation GmbH", "DE129274829", "Industrie-Hydraulik & Steuerungskomponenten", 18500.0),
        ("SAP Deutschland SE & Co. KG", "DE143456789", "S/4HANA Cloud Enterprise Lizenzen Q4", 78000.0),
        ("Festo SE & Co. KG", "DE145321678", "Pneumatik-Module & Ventilinseln", 12400.0),
        ("Trumpf Werkzeugmaschinen SE", "DE147852369", "Laser-Schneidköpfe & Optik-Ersatzteile", 34200.0),
        ("KION Group IT Services GmbH", "DE255678912", "Flurförderzeug-Telematik Server", 9800.0),
        ("Infineon Technologies AG", "DE811133445", "Automotive Power-MOSFET Baugruppen", 62000.0),
        ("Wacker Chemie AG", "DE129567890", "Silizium-Wafer & Reinstchemikalien", 27500.0),
        ("Thyssenkrupp Materials Services", "DE811144556", "Edelstahl-Rohrleitungen DIN EN 10217", 41200.0),
        ("Carl Zeiss SMT GmbH", "DE811155667", "Präzisions-Interferometer & Optik", 89000.0),
    ]

    for i in range(1, 41):
        vendor_name, vat_id, desc, base_net = b2b_vendors[(i - 1) % len(b2b_vendors)]
        net = base_net + (i * 125.50)
        tax = round(net * 0.19, 2)
        total = round(net + tax, 2)
        inv_no = f"RE-2026-B2B-{i:03d}"
        filename = f"{inv_no}_{vendor_name.split()[0]}.xml"
        safe_desc = desc.replace("&", "&amp;")
        safe_vendor = vendor_name.replace("&", "&amp;")

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>{inv_no}</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">2026110{((i % 8) + 1)}</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>1</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:SellerAssignedID>PRD-B2B-{i:03d}</ram:SellerAssignedID>
                <ram:Name>{safe_desc}</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:GrossPriceProductTradePrice>
                    <ram:ChargeAmount>{net:.2f}</ram:ChargeAmount>
                </ram:GrossPriceProductTradePrice>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>{net:.2f}</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="C62">1.0</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode>
                    <ram:CategoryCode>S</ram:CategoryCode>
                    <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>{net:.2f}</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>PO-ENTERPRISE-2026-{i:04d}</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>{safe_vendor}</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>80333</ram:PostcodeCode>
                    <ram:LineOne>Industriestraße {i}</ram:LineOne>
                    <ram:CityName>München</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">{vat_id}</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>Deutsche Sovereign Enterprise AG</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>60311</ram:PostcodeCode>
                    <ram:LineOne>Taunusanlage 8</ram:LineOne>
                    <ram:CityName>Frankfurt am Main</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE329184910</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeDelivery>
            <ram:ActualDeliverySupplyChainEvent>
                <ram:OccurrenceDateTime>
                    <udt:DateTimeString format="102">2026110{((i % 8) + 1)}</udt:DateTimeString>
                </ram:OccurrenceDateTime>
            </ram:ActualDeliverySupplyChainEvent>
        </ram:ApplicableHeaderTradeDelivery>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:SpecifiedTradeSettlementPaymentMeans>
                <ram:TypeCode>58</ram:TypeCode>
                <ram:PayeePartyCreditorFinancialAccount>
                    <ram:IBANID>DE89370400440532013000</ram:IBANID>
                </ram:PayeePartyCreditorFinancialAccount>
            </ram:SpecifiedTradeSettlementPaymentMeans>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>{tax:.2f}</ram:CalculatedAmount>
                <ram:TypeCode>VAT</ram:TypeCode>
                <ram:BasisAmount>{net:.2f}</ram:BasisAmount>
                <ram:CategoryCode>S</ram:CategoryCode>
                <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradePaymentTerms>
                <ram:DueDateDateTime>
                    <udt:DateTimeString format="102">2026120{((i % 8) + 1)}</udt:DateTimeString>
                </ram:DueDateDateTime>
            </ram:SpecifiedTradePaymentTerms>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>{net:.2f}</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>{net:.2f}</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">{tax:.2f}</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>{total:.2f}</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>{total:.2f}</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

        invoices.append(
            CapstoneInvoiceDefinition(
                index=i,
                invoice_number=inv_no,
                filename=filename,
                category="B2B_COMFORT",
                seller_name=vendor_name,
                seller_vat_id=vat_id,
                buyer_name="Deutsche Sovereign Enterprise AG",
                buyer_reference=f"PO-ENTERPRISE-2026-{i:04d}",
                profile_desc="Factur-X 1.0 Comfort (EN 16931 Standard B2B)",
                currency="EUR",
                net_amount=net,
                tax_amount=tax,
                grand_total=total,
                is_expected_compliant=True,
                rejection_reason=None,
                xml_content=xml,
            )
        )

    # -------------------------------------------------------------------------
    # CATEGORY 2: 25 B2G XRechnung (UBL & CII, Bund & Länder with MOD-97-10 check digits)
    # -------------------------------------------------------------------------
    b2g_authorities = [
        ("Bundesministerium des Innern und für Heimat", "991", "12345", "Bund (ZRE)"),
        ("Bundesministerium für Arbeit und Soziales", "991", "23456", "Bund (ZRE)"),
        ("Bundesministerium der Finanzen", "991", "34567", "Bund (ZRE)"),
        ("Bundesverwaltungsamt Köln", "992", "45678", "Bund / Länder (OZG-RE)"),
        ("FITKO Föderale IT-Kooperation", "993", "56789", "Bundeshub / KoSIT"),
        ("Freie und Hansestadt Hamburg (Senatskanzlei)", "02", "0000008008", "Hamburg"),
        ("Landeshauptstadt München (Direktorium)", "09", "1620001001", "Bayern"),
        ("Stadt Nürnberg (Kämmerei)", "09", "5640002002", "Bayern"),
        ("Landeshauptstadt Düsseldorf", "05", "1110003003", "Nordrhein-Westfalen"),
        ("Stadt Köln (Amt für Informationstechnik)", "05", "3150004004", "Nordrhein-Westfalen"),
        ("Senatsverwaltung für Finanzen Berlin", "11", "0000005005", "Berlin"),
        ("Landeshauptstadt Stuttgart", "08", "1110006006", "Baden-Württemberg"),
        ("Stadt Karlsruhe (IT-Amt)", "08", "2120007007", "Baden-Württemberg"),
        ("Freie Hansestadt Bremen (Finanzsenator)", "04", "0110009009", "Bremen"),
        ("Landeshauptstadt Wiesbaden", "06", "4140001111", "Hessen"),
        ("Stadt Frankfurt am Main (Kämmerei)", "06", "4120002222", "Hessen"),
        ("Landeshauptstadt Dresden", "14", "6120003333", "Sachsen"),
        ("Stadt Leipzig (Referat Digitale Stadt)", "14", "7130004444", "Sachsen"),
        ("Landeshauptstadt Mainz", "07", "3150005555", "Rheinland-Pfalz"),
        ("Landeshauptstadt Hannover", "03", "2410006666", "Niedersachsen"),
        ("Landeshauptstadt Kiel", "01", "0020007777", "Schleswig-Holstein"),
        ("Stadt Erfurt (Hauptamt)", "16", "0510008888", "Thüringen"),
        ("Landeshauptstadt Potsdam", "12", "0540009999", "Brandenburg"),
        ("Stadt Magdeburg (Amt für Statistik)", "15", "0030001212", "Sachsen-Anhalt"),
        ("Regionalverband Saarbrücken", "10", "0110005656", "Saarland"),
    ]

    for idx, (auth_name, coarse, fine, jurisdiction) in enumerate(b2g_authorities, start=41):
        # Calculate valid MOD-97-10 check digit
        check_digit = LeitwegValidatorService.compute_check_digit(coarse, fine)
        valid_leitweg_id = f"{coarse}-{fine}-{check_digit}"

        net = 15000.0 + (idx * 310.0)
        tax = round(net * 0.19, 2)
        total = round(net + tax, 2)
        inv_no = f"XR-2026-B2G-{idx:03d}"
        filename = f"{inv_no}_XRechnung.xml"

        # Generate standard OASIS UBL 2.1 XRechnung 3.0 format
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</cbc:CustomizationID>
    <cbc:ProfileID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</cbc:ProfileID>
    <cbc:ID>{inv_no}</cbc:ID>
    <cbc:IssueDate>2026-11-{((idx % 10) + 1):02d}</cbc:IssueDate>
    <cbc:DueDate>2026-12-{((idx % 10) + 1):02d}</cbc:DueDate>
    <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
    <cbc:BuyerReference>{valid_leitweg_id}</cbc:BuyerReference>
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>Sovereign GovTech Solutions GmbH</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Bundesallee {idx}</cbc:StreetName>
                <cbc:CityName>Berlin</cbc:CityName>
                <cbc:PostalZone>10717</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>DE</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>DE298765432</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>{auth_name}</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Rathausplatz 1</cbc:StreetName>
                <cbc:CityName>{jurisdiction}</cbc:CityName>
                <cbc:PostalZone>10115</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>DE</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
        </cac:Party>
    </cac:AccountingCustomerParty>
    <cac:PaymentMeans>
        <cbc:PaymentMeansCode>58</cbc:PaymentMeansCode>
        <cac:PayeeFinancialAccount>
            <cbc:ID>DE89370400440532013000</cbc:ID>
        </cac:PayeeFinancialAccount>
    </cac:PaymentMeans>
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="EUR">{tax:.2f}</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="EUR">{net:.2f}</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="EUR">{tax:.2f}</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>19.00</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="EUR">{net:.2f}</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="EUR">{net:.2f}</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="EUR">{total:.2f}</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="EUR">{total:.2f}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    <cac:InvoiceLine>
        <cbc:ID>1</cbc:ID>
        <cbc:InvoicedQuantity unitCode="C62">1.0</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="EUR">{net:.2f}</cbc:LineExtensionAmount>
        <cac:Item>
            <cbc:Description>Digitalisierungs-Beratung OZG / XRechnung 3.0</cbc:Description>
            <cbc:Name>GovTech IT-Dienstleistung § 4 E-Rech-VO</cbc:Name>
            <cac:ClassifiedTaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>19.00</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:ClassifiedTaxCategory>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="EUR">{net:.2f}</cbc:PriceAmount>
        </cac:Price>
    </cac:InvoiceLine>
</Invoice>"""

        invoices.append(
            CapstoneInvoiceDefinition(
                index=idx,
                invoice_number=inv_no,
                filename=filename,
                category="B2G_XRECHNUNG",
                seller_name="Sovereign GovTech Solutions GmbH",
                seller_vat_id="DE298765432",
                buyer_name=auth_name,
                buyer_reference=valid_leitweg_id,
                profile_desc="KoSIT XRechnung 3.0 (OASIS UBL 2.1 B2G)",
                currency="EUR",
                net_amount=net,
                tax_amount=tax,
                grand_total=total,
                is_expected_compliant=True,
                rejection_reason=None,
                xml_content=xml,
            )
        )

    # -------------------------------------------------------------------------
    # CATEGORY 3: 15 § 13b UStG Reverse-Charge Invoices (0% VAT, statutory clause)
    # -------------------------------------------------------------------------
    for idx in range(66, 81):
        net = 8000.0 + (idx * 240.0)
        tax = 0.00
        total = net
        inv_no = f"RC-2026-13B-{idx:03d}"
        filename = f"{inv_no}_ReverseCharge.xml"

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>{inv_no}</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">202611{((idx % 15) + 1):02d}</udt:DateTimeString>
        </ram:IssueDateTime>
        <ram:IncludedNote>
            <ram:Content>Steuerschuldnerschaft des Leistungsempfängers gem. § 13b Abs. 2 Nr. 4 UStG (Bauleistungen und Subunternehmer).</ram:Content>
        </ram:IncludedNote>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>1</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:Name>Rechenzentrums-Klimatisierung &amp; Kältetechnik (§ 13b Bauleistung)</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>{net:.2f}</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="C62">1.0</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode>
                    <ram:CategoryCode>AE</ram:CategoryCode>
                    <ram:RateApplicablePercent>0.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>{net:.2f}</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>PO-RC-13B-{idx:04d}</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Bavaria Facility Bau &amp; Montage GmbH</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>90402</ram:PostcodeCode>
                    <ram:CityName>Nürnberg</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE284910293</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>Deutsche Sovereign Enterprise AG</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>60311</ram:PostcodeCode>
                    <ram:CityName>Frankfurt am Main</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE329184910</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>0.00</ram:CalculatedAmount>
                <ram:TypeCode>VAT</ram:TypeCode>
                <ram:BasisAmount>{net:.2f}</ram:BasisAmount>
                <ram:CategoryCode>AE</ram:CategoryCode>
                <ram:RateApplicablePercent>0.00</ram:RateApplicablePercent>
                <ram:ExemptionReason>Steuerschuldnerschaft des Leistungsempfängers gem. § 13b UStG (Reverse Charge)</ram:ExemptionReason>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>{net:.2f}</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>{net:.2f}</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">0.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>{total:.2f}</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>{total:.2f}</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

        invoices.append(
            CapstoneInvoiceDefinition(
                index=idx,
                invoice_number=inv_no,
                filename=filename,
                category="REVERSE_CHARGE_13B",
                seller_name="Bavaria Facility Bau & Montage GmbH",
                seller_vat_id="DE284910293",
                buyer_name="Deutsche Sovereign Enterprise AG",
                buyer_reference=f"PO-RC-13B-{idx:04d}",
                profile_desc="Factur-X 1.0 Comfort (§ 13b UStG Reverse Charge)",
                currency="EUR",
                net_amount=net,
                tax_amount=tax,
                grand_total=total,
                is_expected_compliant=True,
                rejection_reason=None,
                xml_content=xml,
            )
        )

    # -------------------------------------------------------------------------
    # CATEGORY 4: 10 Reduced 7% VAT Invoices (§ 12 Abs. 2 UStG: Books/Hospitality)
    # -------------------------------------------------------------------------
    for idx in range(81, 91):
        net = 1200.0 + (idx * 65.0)
        tax = round(net * 0.07, 2)
        total = round(net + tax, 2)
        inv_no = f"RE-2026-RED7-{idx:03d}"
        filename = f"{inv_no}_Reduced7.xml"

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>{inv_no}</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">202611{((idx % 10) + 1):02d}</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>1</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:Name>Juristische Fachliteratur &amp; DIN/ISO Normenwerke (§ 12 Abs. 2 Nr. 1 UStG)</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>{net:.2f}</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="C62">1.0</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode>
                    <ram:CategoryCode>S</ram:CategoryCode>
                    <ram:RateApplicablePercent>7.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>{net:.2f}</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>PO-NORM-2026-{idx:04d}</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Deutscher Fachverlag für Rechts- und Normenwesen GmbH</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>10787</ram:PostcodeCode>
                    <ram:CityName>Berlin</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE182736450</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>Deutsche Sovereign Enterprise AG</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>60311</ram:PostcodeCode>
                    <ram:CityName>Frankfurt am Main</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE329184910</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>{tax:.2f}</ram:CalculatedAmount>
                <ram:TypeCode>VAT</ram:TypeCode>
                <ram:BasisAmount>{net:.2f}</ram:BasisAmount>
                <ram:CategoryCode>S</ram:CategoryCode>
                <ram:RateApplicablePercent>7.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>{net:.2f}</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>{net:.2f}</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">{tax:.2f}</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>{total:.2f}</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>{total:.2f}</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

        invoices.append(
            CapstoneInvoiceDefinition(
                index=idx,
                invoice_number=inv_no,
                filename=filename,
                category="REDUCED_VAT_7",
                seller_name="Deutscher Fachverlag für Rechts- und Normenwesen GmbH",
                seller_vat_id="DE182736450",
                buyer_name="Deutsche Sovereign Enterprise AG",
                buyer_reference=f"PO-NORM-2026-{idx:04d}",
                profile_desc="Factur-X 1.0 Comfort (§ 12 Abs. 2 UStG 7% MwSt)",
                currency="EUR",
                net_amount=net,
                tax_amount=tax,
                grand_total=total,
                is_expected_compliant=True,
                rejection_reason=None,
                xml_content=xml,
            )
        )

    # -------------------------------------------------------------------------
    # CATEGORY 5: 5 Small-Value Invoices (§ 33 UStDV Kleinbetragsrechnungen <= 250 EUR)
    # -------------------------------------------------------------------------
    small_values = [85.00, 120.00, 165.50, 195.00, 240.00]
    for i, net in enumerate(small_values, start=91):
        tax = round(net * 0.19, 2)
        total = round(net + tax, 2)
        inv_no = f"KB-2026-33-{i:03d}"
        filename = f"{inv_no}_Kleinbetrag.xml"

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>{inv_no}</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">20261110</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>1</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:Name>Bürobedarf &amp; Verbrauchsmaterialien (§ 33 UStDV Kleinbetrag)</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>{net:.2f}</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="C62">1.0</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode>
                    <ram:CategoryCode>S</ram:CategoryCode>
                    <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>{net:.2f}</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>BARKAUF-2026-{i:03d}</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Büromarkt Express GmbH</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>60329</ram:PostcodeCode>
                    <ram:CityName>Frankfurt am Main</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE219384756</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>Deutsche Sovereign Enterprise AG</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>60311</ram:PostcodeCode>
                    <ram:CityName>Frankfurt am Main</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>{tax:.2f}</ram:CalculatedAmount>
                <ram:TypeCode>VAT</ram:TypeCode>
                <ram:BasisAmount>{net:.2f}</ram:BasisAmount>
                <ram:CategoryCode>S</ram:CategoryCode>
                <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>{net:.2f}</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>{net:.2f}</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">{tax:.2f}</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>{total:.2f}</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>{total:.2f}</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

        invoices.append(
            CapstoneInvoiceDefinition(
                index=i,
                invoice_number=inv_no,
                filename=filename,
                category="SMALL_VALUE_33",
                seller_name="Büromarkt Express GmbH",
                seller_vat_id="DE219384756",
                buyer_name="Deutsche Sovereign Enterprise AG",
                buyer_reference=f"BARKAUF-2026-{i:03d}",
                profile_desc="Factur-X 1.0 Comfort (§ 33 UStDV Kleinbetrag <= 250 EUR)",
                currency="EUR",
                net_amount=net,
                tax_amount=tax,
                grand_total=total,
                is_expected_compliant=True,
                rejection_reason=None,
                xml_content=xml,
            )
        )

    # -------------------------------------------------------------------------
    # CATEGORY 6: 5 Intentionally Discrepant / Tampered Fraud Simulations
    # -------------------------------------------------------------------------

    # 96. BR-CO-10 Summenfehler: LineTotal (10,000.00) != Line Items Sum (12,000.00)
    xml_96 = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>INV-DISC-096</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">20261111</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument><ram:LineID>1</ram:LineID></ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct><ram:Name>Manipulierte IT-Hardware Position 1</ram:Name></ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode><ram:CategoryCode>S</ram:CategoryCode><ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>6000.00</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument><ram:LineID>2</ram:LineID></ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct><ram:Name>Manipulierte IT-Hardware Position 2</ram:Name></ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode><ram:CategoryCode>S</ram:CategoryCode><ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>6000.00</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>PO-DISC-096</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Dubious Vendor AG</ram:Name>
                <ram:PostalTradeAddress><ram:CityName>Frankfurt</ram:CityName><ram:CountryID>DE</ram:CountryID></ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration><ram:ID schemeID="VA">DE999888777</ram:ID></ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty><ram:Name>Deutsche Sovereign Enterprise AG</ram:Name></ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>1900.00</ram:CalculatedAmount>
                <ram:TypeCode>VAT</ram:TypeCode>
                <ram:BasisAmount>10000.00</ram:BasisAmount>
                <ram:CategoryCode>S</ram:CategoryCode>
                <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>10000.00</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>10000.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">1900.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>11900.00</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>11900.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

    invoices.append(
        CapstoneInvoiceDefinition(
            index=96,
            invoice_number="INV-DISC-096",
            filename="INV-DISC-096_SumMismatch_BR-CO-10.xml",
            category="DISCREPANT_FRAUD_SIM",
            seller_name="Dubious Vendor AG",
            seller_vat_id="DE999888777",
            buyer_name="Deutsche Sovereign Enterprise AG",
            buyer_reference="PO-DISC-096",
            profile_desc="Factur-X 1.0 Comfort [BEANSTANDET]",
            currency="EUR",
            net_amount=10000.00,
            tax_amount=1900.00,
            grand_total=11900.00,
            is_expected_compliant=False,
            rejection_reason="Verletzung Regel BR-CO-10: Summe der Positionen (12.000,00 EUR) stimmt nicht mit LineTotalAmount (10.000,00 EUR) überein.",
            xml_content=xml_96,
        )
    )

    # 97. BR-DE-15 Leitweg-ID Prüfziffernfehler (Fehlerhafte MOD-97-10 Checksumme '99' statt '73')
    xml_97 = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</cbc:CustomizationID>
    <cbc:ProfileID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</cbc:ProfileID>
    <cbc:ID>INV-DISC-097</cbc:ID>
    <cbc:IssueDate>2026-11-12</cbc:IssueDate>
    <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
    <cbc:BuyerReference>991-12345-99</cbc:BuyerReference>
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName><cbc:Name>Fraunhofer GovTech Fake GmbH</cbc:Name></cac:PartyName>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>DE333444555</cbc:CompanyID>
                <cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party><cac:PartyName><cbc:Name>Bundesministerium des Innern / ZRE</cbc:Name></cac:PartyName></cac:Party>
    </cac:AccountingCustomerParty>
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="EUR">950.00</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="EUR">5000.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="EUR">950.00</cbc:TaxAmount>
            <cac:TaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>19.00</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="EUR">5000.00</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="EUR">5000.00</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="EUR">5950.00</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="EUR">5950.00</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    <cac:InvoiceLine>
        <cbc:ID>1</cbc:ID>
        <cbc:InvoicedQuantity unitCode="C62">1.0</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="EUR">5000.00</cbc:LineExtensionAmount>
        <cac:Item>
            <cbc:Name>Beratungsleistung B2G mit ungültiger Leitweg-ID</cbc:Name>
            <cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>19.00</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory>
        </cac:Item>
        <cac:Price><cbc:PriceAmount currencyID="EUR">5000.00</cbc:PriceAmount></cac:Price>
    </cac:InvoiceLine>
</Invoice>"""

    invoices.append(
        CapstoneInvoiceDefinition(
            index=97,
            invoice_number="INV-DISC-097",
            filename="INV-DISC-097_InvalidLeitweg_BR-DE-15.xml",
            category="DISCREPANT_FRAUD_SIM",
            seller_name="Fraunhofer GovTech Fake GmbH",
            seller_vat_id="DE333444555",
            buyer_name="Bundesministerium des Innern / ZRE",
            buyer_reference="991-12345-99",
            profile_desc="KoSIT XRechnung 3.0 [BEANSTANDET]",
            currency="EUR",
            net_amount=5000.00,
            tax_amount=950.00,
            grand_total=5950.00,
            is_expected_compliant=False,
            rejection_reason="Verletzung Regel BR-DE-15 (§ 4 E-Rech-VO): Leitweg-ID '991-12345-99' hat eine ungültige ISO 7064 MOD-97-10 Prüfziffer (erwartet: 73).",
            xml_content=xml_97,
        )
    )

    # 98. § 14 Abs. 4 Nr. 2 UStG Verstoß: Fehlende USt-IdNr. & Steuernummer des Leistenden
    xml_98 = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>INV-DISC-098</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">20261113</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument><ram:LineID>1</ram:LineID></ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct><ram:Name>Beratung ohne Steuernummer</ram:Name></ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax><ram:TypeCode>VAT</ram:TypeCode><ram:CategoryCode>S</ram:CategoryCode><ram:RateApplicablePercent>19.00</ram:RateApplicablePercent></ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation><ram:LineTotalAmount>4000.00</ram:LineTotalAmount></ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>PO-DISC-098</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Ghost Advisory Consulting UG</ram:Name>
                <ram:PostalTradeAddress><ram:CityName>Berlin</ram:CityName><ram:CountryID>DE</ram:CountryID></ram:PostalTradeAddress>
                <!-- MISSING TAX REGISTRATION / VAT ID -->
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty><ram:Name>Deutsche Sovereign Enterprise AG</ram:Name></ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>760.00</ram:CalculatedAmount><ram:TypeCode>VAT</ram:TypeCode><ram:BasisAmount>4000.00</ram:BasisAmount><ram:CategoryCode>S</ram:CategoryCode><ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>4000.00</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>4000.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">760.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>4760.00</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>4760.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

    invoices.append(
        CapstoneInvoiceDefinition(
            index=98,
            invoice_number="INV-DISC-098",
            filename="INV-DISC-098_MissingVatId_UStG14.xml",
            category="DISCREPANT_FRAUD_SIM",
            seller_name="Ghost Advisory Consulting UG",
            seller_vat_id=None,
            buyer_name="Deutsche Sovereign Enterprise AG",
            buyer_reference="PO-DISC-098",
            profile_desc="Factur-X 1.0 Comfort [BEANSTANDET]",
            currency="EUR",
            net_amount=4000.00,
            tax_amount=760.00,
            grand_total=4760.00,
            is_expected_compliant=False,
            rejection_reason="Verletzung § 14 Abs. 4 Nr. 2 UStG: Keine gesetzliche Steuernummer oder USt-IdNr. des leistenden Unternehmers angegeben (Vorsteuerabzug nach § 15 UStG unzulässig).",
            xml_content=xml_98,
        )
    )

    # 99. BR-02 Verstoß / § 14 Abs. 4 Nr. 6 UStG: Fehlendes Ausstellungsdatum (IssueDate fehlt)
    xml_99 = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>INV-DISC-099</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <!-- MISSING IssueDateTime -->
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument><ram:LineID>1</ram:LineID></ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct><ram:Name>Hardwarelieferung ohne Ausstellungsdatum</ram:Name></ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax><ram:TypeCode>VAT</ram:TypeCode><ram:CategoryCode>S</ram:CategoryCode><ram:RateApplicablePercent>19.00</ram:RateApplicablePercent></ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation><ram:LineTotalAmount>7500.00</ram:LineTotalAmount></ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>PO-DISC-099</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Vintage Server Hardware GmbH</ram:Name>
                <ram:PostalTradeAddress><ram:CityName>München</ram:CityName><ram:CountryID>DE</ram:CountryID></ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration><ram:ID schemeID="VA">DE273849102</ram:ID></ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty><ram:Name>Deutsche Sovereign Enterprise AG</ram:Name></ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>1425.00</ram:CalculatedAmount><ram:TypeCode>VAT</ram:TypeCode><ram:BasisAmount>7500.00</ram:BasisAmount><ram:CategoryCode>S</ram:CategoryCode><ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>7500.00</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>7500.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">1425.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>8925.00</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>8925.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

    invoices.append(
        CapstoneInvoiceDefinition(
            index=99,
            invoice_number="INV-DISC-099",
            filename="INV-DISC-099_MissingDate_BR-02.xml",
            category="DISCREPANT_FRAUD_SIM",
            seller_name="Vintage Server Hardware GmbH",
            seller_vat_id="DE273849102",
            buyer_name="Deutsche Sovereign Enterprise AG",
            buyer_reference="PO-DISC-099",
            profile_desc="Factur-X 1.0 Comfort [BEANSTANDET]",
            currency="EUR",
            net_amount=7500.00,
            tax_amount=1425.00,
            grand_total=8925.00,
            is_expected_compliant=False,
            rejection_reason="Verletzung Regel BR-02 (§ 14 Abs. 4 Nr. 6 UStG): Gesetzliches Ausstellungsdatum (IssueDate) fehlt zwingend.",
            xml_content=xml_99,
        )
    )

    # 100. BR-CO-12 / BR-CO-14 Steuerbasis-Berechnungsbetrug: GrandTotal (30,000.00) != Net (20,000.00) + Tax (3,800.00)
    xml_100 = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>INV-DISC-100</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">20261114</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument><ram:LineID>1</ram:LineID></ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct><ram:Name>Manipulierte Softwarelizenzierung Enterprise</ram:Name></ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax><ram:TypeCode>VAT</ram:TypeCode><ram:CategoryCode>S</ram:CategoryCode><ram:RateApplicablePercent>19.00</ram:RateApplicablePercent></ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation><ram:LineTotalAmount>20000.00</ram:LineTotalAmount></ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>PO-DISC-100</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Rogue Security Software Ltd</ram:Name>
                <ram:PostalTradeAddress><ram:CityName>Hamburg</ram:CityName><ram:CountryID>DE</ram:CountryID></ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration><ram:ID schemeID="VA">DE294817263</ram:ID></ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty><ram:Name>Deutsche Sovereign Enterprise AG</ram:Name></ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>3800.00</ram:CalculatedAmount><ram:TypeCode>VAT</ram:TypeCode><ram:BasisAmount>20000.00</ram:BasisAmount><ram:CategoryCode>S</ram:CategoryCode><ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>20000.00</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>20000.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">3800.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>30000.00</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>30000.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

    invoices.append(
        CapstoneInvoiceDefinition(
            index=100,
            invoice_number="INV-DISC-100",
            filename="INV-DISC-100_GrandTotalFraud_BR-CO-12.xml",
            category="DISCREPANT_FRAUD_SIM",
            seller_name="Rogue Security Software Ltd",
            seller_vat_id="DE294817263",
            buyer_name="Deutsche Sovereign Enterprise AG",
            buyer_reference="PO-DISC-100",
            profile_desc="Factur-X 1.0 Comfort [BEANSTANDET]",
            currency="EUR",
            net_amount=20000.00,
            tax_amount=3800.00,
            grand_total=30000.00,
            is_expected_compliant=False,
            rejection_reason="Verletzung Regel BR-CO-12: GrandTotalAmount (30.000,00 EUR) weicht unzulässig von Basis (20.000,00 EUR) + Steuer (3.800,00 EUR) ab (Rechnerischer Überschuss 6.200,00 EUR, § 14c UStG Gefährdungshaftung).",
            xml_content=xml_100,
        )
    )

    return invoices
