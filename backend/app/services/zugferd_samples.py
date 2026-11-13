from app.schemas.zugferd_invoice import ZugferdProfile, ZugferdSampleProfile

SAMPLE_FACTURX_COMFORT = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>RE-2026-DE-84920</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">20261108</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>1</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:SellerAssignedID>PRD-CLOUD-ENTERPRISE</ram:SellerAssignedID>
                <ram:Name>DocuNorm AI Sovereign Cloud Enterprise Subscription</ram:Name>
                <ram:Description>Enterprise Dedicated Banking &amp; DORA In-Memory Tenant License Q4/2026</ram:Description>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:GrossPriceProductTradePrice>
                    <ram:ChargeAmount>25000.00</ram:ChargeAmount>
                </ram:GrossPriceProductTradePrice>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>25000.00</ram:ChargeAmount>
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
                    <ram:LineTotalAmount>25000.00</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>2</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:SellerAssignedID>PRD-AUDIT-LKSG-TIER</ram:SellerAssignedID>
                <ram:Name>LkSG § 10 Jahresbericht Synthese &amp; Tier-N Kaskaden-Auditierung</ram:Name>
                <ram:Description>Rechtssichere BAFA-Dossiererstellung und Lieferketten-Audit</ram:Description>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:GrossPriceProductTradePrice>
                    <ram:ChargeAmount>7500.00</ram:ChargeAmount>
                </ram:GrossPriceProductTradePrice>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>7500.00</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="HUR">10.0</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:TypeCode>VAT</ram:TypeCode>
                    <ram:CategoryCode>S</ram:CategoryCode>
                    <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>7500.00</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>04011000-12345-03</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>DocuNorm Sovereign Systems AG</ram:Name>
                <ram:DefinedTradeContact>
                    <ram:PersonName>Dr. Maximilian Becker</ram:PersonName>
                    <ram:EmailURIUniversalCommunication>
                        <ram:CompleteNumber>billing@docunorm.ai</ram:CompleteNumber>
                    </ram:EmailURIUniversalCommunication>
                </ram:DefinedTradeContact>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>60311</ram:PostcodeCode>
                    <ram:LineOne>Taunusanlage 8</ram:LineOne>
                    <ram:CityName>Frankfurt am Main</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE329184910</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>Deutsche Bundesbank / Federal Procurement Dept</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>60431</ram:PostcodeCode>
                    <ram:LineOne>Wilhelm-Epstein-Straße 14</ram:LineOne>
                    <ram:CityName>Frankfurt am Main</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE114104250</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeDelivery>
            <ram:ShipToTradeParty>
                <ram:Name>Deutsche Bundesbank Rechenzentrum Süd</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>80333</ram:PostcodeCode>
                    <ram:LineOne>Brienner Straße 18</ram:LineOne>
                    <ram:CityName>München</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
            </ram:ShipToTradeParty>
            <ram:ActualDeliverySupplyChainEvent>
                <ram:OccurrenceDateTime>
                    <udt:DateTimeString format="102">20261108</udt:DateTimeString>
                </ram:OccurrenceDateTime>
            </ram:ActualDeliverySupplyChainEvent>
        </ram:ApplicableHeaderTradeDelivery>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:PaymentReference>RE-2026-DE-84920</ram:PaymentReference>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:SpecifiedTradeSettlementPaymentMeans>
                <ram:TypeCode>58</ram:TypeCode>
                <ram:PayeePartyCreditorFinancialAccount>
                    <ram:IBANID>DE89370400440532013000</ram:IBANID>
                </ram:PayeePartyCreditorFinancialAccount>
                <ram:PayeeSpecifiedCreditorFinancialInstitution>
                    <ram:BICID>DBDDDEFFXXX</ram:BICID>
                </ram:PayeeSpecifiedCreditorFinancialInstitution>
            </ram:SpecifiedTradeSettlementPaymentMeans>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>6175.00</ram:CalculatedAmount>
                <ram:TypeCode>VAT</ram:TypeCode>
                <ram:BasisAmount>32500.00</ram:BasisAmount>
                <ram:CategoryCode>S</ram:CategoryCode>
                <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradePaymentTerms>
                <ram:Description>Zahlbar innerhalb von 14 Tagen mit 2% Skonto, oder 30 Tage netto kasse.</ram:Description>
                <ram:DueDateDateTime>
                    <udt:DateTimeString format="102">20261208</udt:DateTimeString>
                </ram:DueDateDateTime>
            </ram:SpecifiedTradePaymentTerms>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>32500.00</ram:LineTotalAmount>
                <ram:ChargeTotalAmount>0.00</ram:ChargeTotalAmount>
                <ram:AllowanceTotalAmount>0.00</ram:AllowanceTotalAmount>
                <ram:TaxBasisTotalAmount>32500.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">6175.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>38675.00</ram:GrandTotalAmount>
                <ram:TotalPrepaidAmount>0.00</ram:TotalPrepaidAmount>
                <ram:DuePayableAmount>38675.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

SAMPLE_XRECHNUNG_UBL = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</cbc:CustomizationID>
    <cbc:ProfileID>urn:fdc:peppol.eu:2017:poacc:billing:01:1.0</cbc:ProfileID>
    <cbc:ID>XR-2026-9901</cbc:ID>
    <cbc:IssueDate>2026-11-09</cbc:IssueDate>
    <cbc:DueDate>2026-12-09</cbc:DueDate>
    <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
    <cbc:BuyerReference>991-12345-73</cbc:BuyerReference>
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>Tech Innovations GmbH</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Technologiepark 1</cbc:StreetName>
                <cbc:CityName>Karlsruhe</cbc:CityName>
                <cbc:PostalZone>76131</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>DE</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>DE123456789</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>Bundesministerium des Innern / ZRE</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Alt-Moabit 140</cbc:StreetName>
                <cbc:CityName>Berlin</cbc:CityName>
                <cbc:PostalZone>10557</cbc:PostalZone>
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
        <cbc:TaxAmount currencyID="EUR">190.00</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="EUR">1000.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="EUR">190.00</cbc:TaxAmount>
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
        <cbc:LineExtensionAmount currencyID="EUR">1000.00</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="EUR">1000.00</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="EUR">1190.00</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="EUR">1190.00</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    <cac:InvoiceLine>
        <cbc:ID>1</cbc:ID>
        <cbc:InvoicedQuantity unitCode="C62">1.0</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="EUR">1000.00</cbc:LineExtensionAmount>
        <cac:Item>
            <cbc:Description>IT-Sicherheitsberatung DORA &amp; KRITIS</cbc:Description>
            <cbc:Name>IT Security Advisory</cbc:Name>
            <cac:ClassifiedTaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>19.00</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>VAT</cbc:ID>
                </cac:TaxScheme>
            </cac:ClassifiedTaxCategory>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="EUR">1000.00</cbc:PriceAmount>
        </cac:Price>
    </cac:InvoiceLine>
</Invoice>"""

SAMPLE_XRECHNUNG_CII = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>XR-2026-CII-0042</ram:ID>
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
                <ram:Name>KI-Governance Audit Bremen</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>2000.00</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="C62">1.0</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:CategoryCode>S</ram:CategoryCode>
                    <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>2000.00</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>04011000-998877-15</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Sovereign Solutions AG</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>10115</ram:PostcodeCode>
                    <ram:CityName>Berlin</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE998877665</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>Freie Hansestadt Bremen - Finanzsenat</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>28195</ram:PostcodeCode>
                    <ram:CityName>Bremen</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:SpecifiedTradeSettlementPaymentMeans>
                <ram:PayeePartyCreditorFinancialAccount>
                    <ram:IBANID>DE02100100100123456789</ram:IBANID>
                </ram:PayeePartyCreditorFinancialAccount>
            </ram:SpecifiedTradeSettlementPaymentMeans>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>380.00</ram:CalculatedAmount>
                <ram:BasisAmount>2000.00</ram:BasisAmount>
                <ram:CategoryCode>S</ram:CategoryCode>
                <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>2000.00</ram:LineTotalAmount>
                <ram:TaxBasisTotalAmount>2000.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">380.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>2380.00</ram:GrandTotalAmount>
                <ram:DuePayableAmount>2380.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

SAMPLE_REVERSE_CHARGE = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:extended</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>INV-RC-2026-44</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">20261111</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>1</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:Name>Grenzüberschreitende Softwarearchitektur (§ 13b UStG)</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>12500.00</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="C62">1.0</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:CategoryCode>AE</ram:CategoryCode>
                    <ram:RateApplicablePercent>0.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>12500.00</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>08-998877-16</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Alpine Sovereign Tech SARL</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>1000</ram:PostcodeCode>
                    <ram:CityName>Bruxelles</ram:CityName>
                    <ram:CountryID>BE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">BE0899123456</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>DocuNorm Sovereign Systems AG</ram:Name>
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
            <ram:SpecifiedTradeSettlementPaymentMeans>
                <ram:PayeePartyCreditorFinancialAccount>
                    <ram:IBANID>BE68539007547034</ram:IBANID>
                </ram:PayeePartyCreditorFinancialAccount>
            </ram:SpecifiedTradeSettlementPaymentMeans>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>0.00</ram:CalculatedAmount>
                <ram:BasisAmount>12500.00</ram:BasisAmount>
                <ram:CategoryCode>AE</ram:CategoryCode>
                <ram:RateApplicablePercent>0.00</ram:RateApplicablePercent>
                <ram:ExemptionReason>Steuerschuldnerschaft des Leistungsempfängers gem. § 13b UStG (Reverse Charge)</ram:ExemptionReason>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradePaymentTerms>
                <ram:Description>Steuerschuldnerschaft des Leistungsempfängers gem. § 13b UStG · Reverse charge applies.</ram:Description>
            </ram:SpecifiedTradePaymentTerms>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>12500.00</ram:LineTotalAmount>
                <ram:TaxBasisTotalAmount>12500.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">0.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>12500.00</ram:GrandTotalAmount>
                <ram:DuePayableAmount>12500.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

SAMPLE_DISCREPANT_TAMPERED = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>INV-TAMPERED-991</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">20261112</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:IncludedSupplyChainTradeLineItem>
            <ram:AssociatedDocumentLineDocument>
                <ram:LineID>1</ram:LineID>
            </ram:AssociatedDocumentLineDocument>
            <ram:SpecifiedTradeProduct>
                <ram:Name>Manipulierte Hardware-Lieferung</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>10000.00</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="C62">1.0</ram:BilledQuantity>
            </ram:SpecifiedLineTradeDelivery>
            <ram:SpecifiedLineTradeSettlement>
                <ram:ApplicableTradeTax>
                    <ram:CategoryCode>S</ram:CategoryCode>
                    <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
                </ram:ApplicableTradeTax>
                <ram:SpecifiedTradeSettlementLineMonetarySummation>
                    <ram:LineTotalAmount>10000.00</ram:LineTotalAmount>
                </ram:SpecifiedTradeSettlementLineMonetarySummation>
            </ram:SpecifiedLineTradeSettlement>
        </ram:IncludedSupplyChainTradeLineItem>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:BuyerReference>991-12345-99</ram:BuyerReference>
            <ram:SellerTradeParty>
                <ram:Name>Dubious Vendor Solutions Ltd</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>10115</ram:PostcodeCode>
                    <ram:CityName>Berlin</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE111222333</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>Bundesministerium der Verteidigung</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>10785</ram:PostcodeCode>
                    <ram:CityName>Berlin</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:SpecifiedTradeSettlementPaymentMeans>
                <ram:PayeePartyCreditorFinancialAccount>
                    <ram:IBANID>DE89370400440532013000</ram:IBANID>
                </ram:PayeePartyCreditorFinancialAccount>
            </ram:SpecifiedTradeSettlementPaymentMeans>
            <ram:ApplicableTradeTax>
                <ram:CalculatedAmount>1900.00</ram:CalculatedAmount>
                <ram:BasisAmount>10000.00</ram:BasisAmount>
                <ram:CategoryCode>S</ram:CategoryCode>
                <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
            </ram:ApplicableTradeTax>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>10000.00</ram:LineTotalAmount>
                <ram:TaxBasisTotalAmount>10000.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">1900.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>13900.00</ram:GrandTotalAmount>
                <ram:DuePayableAmount>13900.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

SAMPLE_PROFILES: list[ZugferdSampleProfile] = [
    ZugferdSampleProfile(
        profile_id="facturx-comfort",
        name="Factur-X 1.0 / ZUGFeRD 2.3 Comfort (B2B Standard)",
        profile_type=ZugferdProfile.EN16931,
        description_de="Authentische Handelsrechnung nach EN 16931-1 für Cloud-Infrastruktur & LkSG-Auditierung mit 19% Regelsteuersatz.",
        description_en="Authentic EN 16931-1 commercial invoice for cloud infrastructure & LkSG audit services with 19% standard VAT.",
        xml_filename="factur-x.xml",
        raw_xml=SAMPLE_FACTURX_COMFORT,
        simulated_discrepancy=False,
        statutory_focus="§ 14 Abs. 4 UStG · EN 16931-1 Comfort Profile · Bremen Leitweg-ID 04011000-12345-03",
    ),
    ZugferdSampleProfile(
        profile_id="xrechnung-ubl",
        name="KoSIT XRechnung 3.0 (OASIS UBL 2.1 · B2G Bund ZRE)",
        profile_type=ZugferdProfile.XRECHNUNG,
        description_de="Offizielle deutsche Bundesstandard-Rechnung im UBL-Format adressiert an das Bundesministerium des Innern via ZRE.",
        description_en="Official German Federal standard e-invoice in UBL syntax routed to the Federal Ministry of the Interior via ZRE.",
        xml_filename="xrechnung.xml",
        raw_xml=SAMPLE_XRECHNUNG_UBL,
        simulated_discrepancy=False,
        statutory_focus="§ 4 E-Rech-VO · XRechnung 3.0 · Bund ZRE Leitweg-ID 991-12345-73",
    ),
    ZugferdSampleProfile(
        profile_id="xrechnung-cii",
        name="KoSIT XRechnung 3.0 (UN/CEFACT CII · B2G Land Bremen)",
        profile_type=ZugferdProfile.XRECHNUNG,
        description_de="Amtliche XRechnung im UN/CEFACT CII-Format adressiert an die Freie Hansestadt Bremen (Finanzsenat).",
        description_en="Statutory XRechnung in UN/CEFACT CII syntax addressed to the Free Hanseatic City of Bremen (Finance Senate).",
        xml_filename="xrechnung.xml",
        raw_xml=SAMPLE_XRECHNUNG_CII,
        simulated_discrepancy=False,
        statutory_focus="§ 4 E-Rech-VO · Freie Hansestadt Bremen Leitweg-ID 04011000-998877-15",
    ),
    ZugferdSampleProfile(
        profile_id="reverse-charge-13b",
        name="Reverse-Charge B2B Grenzüberschreitend (§ 13b UStG · Extended)",
        profile_type=ZugferdProfile.EXTENDED,
        description_de="Grenzüberschreitende EU-Dienstleistung mit Steuerschuldnerschaft des Leistungsempfängers (0% Steuer, Kategorie AE).",
        description_en="Cross-border EU IT service with reverse charge taxation (§ 13b UStG, Category AE, 0% tax, statutory note).",
        xml_filename="factur-x.xml",
        raw_xml=SAMPLE_REVERSE_CHARGE,
        simulated_discrepancy=False,
        statutory_focus="§ 13b UStG · § 14a Abs. 5 UStG Pflichtvermerk · Steuerschuldnerschaft des Leistungsempfängers",
    ),
    ZugferdSampleProfile(
        profile_id="discrepant-tampered",
        name="Prüffall: Diskrepanz & Rechenabweichung (Simulierte Manipulation)",
        profile_type=ZugferdProfile.EN16931,
        description_de="Simulierter Rechnungsfehler: Netto 10.000 € + Steuer 1.900 €, aber Brutto manipuliert auf 13.900 € (+2.000 €) mit falscher Leitweg-Prüfziffer.",
        description_en="Simulated invoice tampering: Net 10,000 € + Tax 1,900 €, but declared Grand Total is 13,900 € with corrupted Leitweg-ID checksum.",
        xml_filename="factur-x.xml",
        raw_xml=SAMPLE_DISCREPANT_TAMPERED,
        simulated_discrepancy=True,
        statutory_focus="BR-CO-12 Summenfehler · BR-DE-15 Prüfziffernfehler · § 14c UStG Gefährdungshaftung",
    ),
]


def get_sample_profiles() -> list[ZugferdSampleProfile]:
    return SAMPLE_PROFILES


def get_sample_profile_by_id(profile_id: str) -> ZugferdSampleProfile | None:
    for p in SAMPLE_PROFILES:
        if p.profile_id == profile_id:
            return p
    return None
