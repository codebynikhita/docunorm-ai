import pytest
import fitz
from app.services.zugferd import extract_embedded_zugferd_xml, parse_zugferd_xml_metadata


SAMPLE_ZUGFERD_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
                          xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">
    <rsm:ExchangedDocument>
        <ram:ID>INV-2026-DE-0042</ram:ID>
        <ram:IssueDateTime>
            <udt:DateTimeString xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">20261021</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:LineTotalAmount>1000.00</ram:LineTotalAmount>
                <ram:TaxBasisTotalAmount>1000.00</ram:TaxBasisTotalAmount>
                <ram:TaxTotalAmount currencyID="EUR">190.00</ram:TaxTotalAmount>
                <ram:GrandTotalAmount>1190.00</ram:GrandTotalAmount>
                <ram:DuePayableAmount>1190.00</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""


@pytest.fixture
def sample_zugferd_pdf(tmp_path):
    """Creates a temporary PDF with an embedded factur-x.xml attachment."""
    pdf_path = tmp_path / "zugferd_sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "Rechnung Nr. INV-2026-DE-0042\nGesamtbetrag: 1.190,00 EUR")
    
    # Embed the XML file into PDF/A-3
    doc.embfile_add(
        name="factur-x.xml",
        buffer_=SAMPLE_ZUGFERD_XML,
        filename="factur-x.xml",
        desc="ZUGFeRD / Factur-X EN16931 Invoice Data",
    )
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


@pytest.fixture
def regular_pdf_without_xml(tmp_path):
    """Creates a standard PDF with no embedded attachments."""
    pdf_path = tmp_path / "plain.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "Standard plain document without attachments.")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


def test_extract_zugferd_xml_finds_embedded_file(sample_zugferd_pdf):
    xml_content = extract_embedded_zugferd_xml(sample_zugferd_pdf)
    assert xml_content is not None
    assert "CrossIndustryInvoice" in xml_content
    assert "INV-2026-DE-0042" in xml_content


def test_extract_zugferd_xml_returns_none_for_plain_pdf(regular_pdf_without_xml):
    xml_content = extract_embedded_zugferd_xml(regular_pdf_without_xml)
    assert xml_content is None


def test_parse_zugferd_xml_metadata_extracts_correct_totals():
    data = parse_zugferd_xml_metadata(SAMPLE_ZUGFERD_XML.decode("utf-8"))
    assert data is not None
    assert data["invoice_id"] == "INV-2026-DE-0042"
    assert data["currency"] == "EUR"
    assert data["grand_total"] == 1190.00
    assert data["tax_total"] == 190.00
