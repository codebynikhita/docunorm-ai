from uuid import uuid4

import pymupdf as fitz
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.zugferd_invoice import (
    ZugferdInvoiceType,
    ZugferdProfile,
)
from app.services.zugferd_extractor import zugferd_extractor_service

SAMPLE_CII_EN16931 = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
                          xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>INV-2026-0091</ram:ID>
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
                <ram:Name>Enterprise Sovereign Cloud Audit Service</ram:Name>
            </ram:SpecifiedTradeProduct>
            <ram:SpecifiedLineTradeAgreement>
                <ram:NetPriceProductTradePrice>
                    <ram:ChargeAmount>1000.00</ram:ChargeAmount>
                </ram:NetPriceProductTradePrice>
            </ram:SpecifiedLineTradeAgreement>
            <ram:SpecifiedLineTradeDelivery>
                <ram:BilledQuantity unitCode="C62">2.0</ram:BilledQuantity>
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
                    <ram:LineOne>Friedrichstraße 100</ram:LineOne>
                    <ram:CityName>Berlin</ram:CityName>
                    <ram:CountryID>DE</ram:CountryID>
                </ram:PostalTradeAddress>
                <ram:SpecifiedTaxRegistration>
                    <ram:ID schemeID="VA">DE998877665</ram:ID>
                </ram:SpecifiedTaxRegistration>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>Bundesministerium für Digitales</ram:Name>
                <ram:PostalTradeAddress>
                    <ram:PostcodeCode>10117</ram:PostcodeCode>
                    <ram:LineOne>Invalidenstraße 44</ram:LineOne>
                    <ram:CityName>Berlin</ram:CityName>
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
</rsm:CrossIndustryInvoice>
"""

SAMPLE_UBL_INVOICE = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xoev-de:kosit:standard:xrechnung_3.0</cbc:CustomizationID>
    <cbc:ID>XR-2026-9901</cbc:ID>
    <cbc:IssueDate>2026-11-09</cbc:IssueDate>
    <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
    <cbc:BuyerReference>04011000-112233-13</cbc:BuyerReference>
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
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>Stadtverwaltung Karlsruhe</cbc:Name>
            </cac:PartyName>
            <cac:PostalAddress>
                <cbc:StreetName>Marktplatz 1</cbc:StreetName>
                <cbc:CityName>Karlsruhe</cbc:CityName>
                <cbc:PostalZone>76133</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>DE</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
        </cac:Party>
    </cac:AccountingCustomerParty>
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="EUR">190.00</cbc:TaxAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="EUR">1000.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="EUR">190.00</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>19.00</cbc:Percent>
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
            <cbc:Name>IT Consulting Services</cbc:Name>
            <cac:ClassifiedTaxCategory>
                <cbc:ID>S</cbc:ID>
                <cbc:Percent>19.00</cbc:Percent>
            </cac:ClassifiedTaxCategory>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="EUR">1000.00</cbc:PriceAmount>
        </cac:Price>
    </cac:InvoiceLine>
</Invoice>
"""


def test_cii_cross_industry_invoice_parsing():
    """Verifies UN/CEFACT CrossIndustryInvoice EN 16931 profile extraction and validation."""
    extraction = zugferd_extractor_service.parse_xml_invoice(
        raw_xml=SAMPLE_CII_EN16931,
        filename="test_invoice.xml",
    )

    assert extraction.invoice_number == "INV-2026-0091"
    assert extraction.profile == ZugferdProfile.EN16931
    assert extraction.invoice_type_code == ZugferdInvoiceType.COMMERCIAL_INVOICE
    assert extraction.currency_code == "EUR"
    assert extraction.buyer_reference == "04011000-998877-15"

    # Seller & Buyer
    assert extraction.seller.name == "Sovereign Solutions AG"
    assert extraction.seller.vat_id == "DE998877665"
    assert extraction.seller.postal_address.city_name == "Berlin"
    assert extraction.buyer.name == "Bundesministerium für Digitales"

    # Monetary sums & lines
    assert len(extraction.line_items) == 1
    assert extraction.line_items[0].billed_quantity == 2.0
    assert extraction.line_items[0].net_price_eur == 1000.00
    assert extraction.line_items[0].line_total_eur == 2000.00
    assert extraction.monetary_summation.line_total_amount_eur == 2000.00
    assert extraction.monetary_summation.tax_total_amount_eur == 380.00
    assert extraction.monetary_summation.grand_total_amount_eur == 2380.00

    # Validation
    assert extraction.validation_report.is_en16931_compliant is True
    assert extraction.validation_report.has_math_discrepancy is False
    assert extraction.validation_report.passed_rules_count >= 11


def test_ubl_xrechnung_parsing():
    """Verifies OASIS UBL 2.1 XRechnung profile extraction and German federal rule checks."""
    extraction = zugferd_extractor_service.parse_xml_invoice(
        raw_xml=SAMPLE_UBL_INVOICE,
        filename="xrechnung_ubl.xml",
    )

    assert extraction.invoice_number == "XR-2026-9901"
    assert extraction.profile == ZugferdProfile.XRECHNUNG
    assert extraction.buyer_reference == "04011000-112233-13"
    assert extraction.seller.name == "Tech Innovations GmbH"
    assert extraction.seller.vat_id == "DE123456789"
    assert extraction.buyer.name == "Stadtverwaltung Karlsruhe"

    # Amounts
    assert extraction.monetary_summation.line_total_amount_eur == 1000.00
    assert extraction.monetary_summation.tax_total_amount_eur == 190.00
    assert extraction.monetary_summation.grand_total_amount_eur == 1190.00

    # Validation
    assert extraction.validation_report.is_en16931_compliant is True
    assert extraction.validation_report.has_math_discrepancy is False


def test_hybrid_pdf_a3_attachment_extraction(tmp_path):
    """Verifies extraction from a true PDF/A-3 containing an embedded factur-x.xml attachment."""
    pdf_path = tmp_path / "hybrid_zugferd.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Rechnung INV-2026-0091")

    doc.embfile_add(
        name="factur-x.xml",
        buffer_=SAMPLE_CII_EN16931.encode("utf-8"),
        filename="factur-x.xml",
        desc="ZUGFeRD 2.3 / Factur-X Data",
    )
    doc.save(str(pdf_path))
    doc.close()

    extraction = zugferd_extractor_service.extract_from_pdf_or_xml(
        file_bytes=pdf_path.read_bytes(),
        filename="hybrid_zugferd.pdf",
    )

    assert extraction.is_hybrid_pdf_a3 is True
    assert extraction.xml_filename == "factur-x.xml"
    assert extraction.invoice_number == "INV-2026-0091"
    assert extraction.monetary_summation.grand_total_amount_eur == 2380.00


def test_math_discrepancy_detection():
    """Verifies that mathematical discrepancies (e.g. tax total mismatch) are flagged with errors."""
    corrupted_xml = SAMPLE_CII_EN16931.replace(
        "<ram:TaxTotalAmount currencyID=\"EUR\">380.00</ram:TaxTotalAmount>",
        "<ram:TaxTotalAmount currencyID=\"EUR\">999.00</ram:TaxTotalAmount>",
    )

    extraction = zugferd_extractor_service.parse_xml_invoice(
        raw_xml=corrupted_xml,
        filename="corrupted_invoice.xml",
    )

    assert extraction.validation_report.is_en16931_compliant is False
    assert extraction.validation_report.has_math_discrepancy is True
    issue_codes = [i.code for i in extraction.validation_report.issues]
    assert "BR-CO-12" in issue_codes or "BR-CO-14" in issue_codes


@pytest.mark.asyncio
async def test_zugferd_fastapi_endpoints():
    """Verifies REST endpoints /api/v1/documents/{id}/zugferd-extract and /api/v1/zugferd/validate-xml."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Validate raw XML string
        res = await client.post(
            "/api/v1/zugferd/validate-xml",
            content=SAMPLE_CII_EN16931,
            headers={"Content-Type": "text/plain"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["invoice_number"] == "INV-2026-0091"
        assert data["profile"] == "EN16931"
        assert data["validation_report"]["is_en16931_compliant"] is True

        # 2. Get extraction for document id (using sample fallback)
        test_uuid = uuid4()
        res_doc = await client.get(f"/api/v1/documents/{test_uuid}/zugferd-extract")
        assert res_doc.status_code == 200
        doc_data = res_doc.json()
        assert doc_data["currency_code"] == "EUR"
        assert "seller" in doc_data
        assert "buyer" in doc_data
        assert doc_data["monetary_summation"]["grand_total_amount_eur"] > 0
