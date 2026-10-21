import xml.etree.ElementTree as ET
import fitz


def extract_embedded_zugferd_xml(pdf_path: str) -> str | None:
    """
    Checks if a PDF has an embedded ZUGFeRD / Factur-X / XRechnung XML invoice file.
    Returns the decoded XML string, or None if no such attachment exists.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return None

    try:
        # Check if there are any embedded files
        if doc.embfile_count() == 0:
            return None

        for name in doc.embfile_names():
            if name.lower().endswith(".xml"):
                raw_bytes = doc.embfile_get(name)
                return raw_bytes.decode("utf-8", errors="replace")
        return None
    finally:
        doc.close()


def parse_zugferd_xml_metadata(xml_string: str) -> dict | None:
    """
    Parses standard EN 16931 / CrossIndustryInvoice XML data to extract
    invoice number, currency, grand total, and tax total.
    """
    try:
        root = ET.fromstring(xml_string)
    except Exception:
        return None

    # Helper function to find a tag ignoring namespaces
    def find_tag_text(element, tag_name: str) -> str | None:
        node = element.find(f".//{{*}}{tag_name}")
        return node.text.strip() if (node is not None and node.text) else None

    invoice_id = find_tag_text(root, "ID")
    currency = find_tag_text(root, "InvoiceCurrencyCode")
    grand_total_str = find_tag_text(root, "GrandTotalAmount")
    tax_total_str = find_tag_text(root, "TaxTotalAmount")

    try:
        grand_total = float(grand_total_str) if grand_total_str else 0.0
    except ValueError:
        grand_total = 0.0

    try:
        tax_total = float(tax_total_str) if tax_total_str else 0.0
    except ValueError:
        tax_total = 0.0

    return {
        "invoice_id": invoice_id,
        "currency": currency or "EUR",
        "grand_total": grand_total,
        "tax_total": tax_total,
    }