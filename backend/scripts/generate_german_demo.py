import fitz
import os
from pathlib import Path

def generate_german_demo_pdf(output_path: str):
    """
    Generates a realistic, multi-page German Enterprise ICT Agreement
    tailored for BaFin DORA (EU 2022/2554), BDSG/GDPR, and ZUGFeRD 2.3 auditing.
    """
    doc = fitz.open()

    pages_data = [
        # PAGE 1: Master Header, Parties, and Scope
        [
            ("SIEMENS AG • RECHTSABTEILUNG COMPLIANCE", 10, True, fitz.Point(50, 50)),
            ("Dossier-Nr.: SIE-2026-DORA-0918-B", 9, False, fitz.Point(50, 65)),
            ("RAHMENVEREINBARUNG ÜBER INFORMATIONSTECHNOLOGIE-DIENSTLEISTUNGEN", 15, True, fitz.Point(50, 110)),
            ("Zwischen der Siemens AG (Auftraggeber) und der CloudScale GmbH, Frankfurt am Main (Auftragnehmer)", 10, False, fitz.Point(50, 135)),
            ("§ 1 Gegenstand der Vereinbarung und Leistungsumfang", 12, True, fitz.Point(50, 180)),
            (
                "Der Auftragnehmer erbringt für den Auftraggeber hochverfügbare Tier-3 Cloud-Infrastrukturdienste "
                "zur Abwicklung geschäftskritischer Finanz- und Logistikprozesse. Die garantierte jährliche "
                "Verfügbarkeit beträgt 99,95 % (ausgenommen vereinbarte Wartungsfenster gem. SLA-Katalog A).",
                10, False, fitz.Point(50, 205)
            ),
            ("§ 2 Regulatorische Einstufung nach EU DORA (VO 2022/2554)", 12, True, fitz.Point(50, 270)),
            (
                "Die Parteien stellen fest, dass die erbrachten IKT-Dienste eine kritische oder wichtige Funktion "
                "im Sinne von Art. 30 DORA darstellen. Der Auftragnehmer verpflichtet sich zur uneingeschränkten "
                "Einhaltung der aufsichtsrechtlichen Mindeststandards der Bundesanstalt für Finanzdienstleistungsaufsicht (BaFin).",
                10, False, fitz.Point(50, 295)
            ),
            ("Geprüftes Dokument gem. DIN 66399 Schutzklasse 3 • Vertraulich • Seite 1 von 3", 8, False, fitz.Point(50, 780)),
        ],

        # PAGE 2: DORA Art. 30 Exit Strategies and Penalties
        [
            ("SIEMENS AG • DORA ART. 30 AUDIT-DOSSIER", 10, True, fitz.Point(50, 50)),
            ("§ 3 Kündigung, Übergangsfristen und Ausstiegsstrategie (DORA Art. 30 Abs. 2)", 12, True, fitz.Point(50, 90)),
            (
                "Jede Vertragspartei kann diesen Vertrag mit einer ordentlichen Kündigungsfrist von sechzig (60) Tagen "
                "zum Quartalsende kündigen. Der Auftragnehmer garantiert im Falle der Beendigung eine umfassende "
                "Unterstützungspflicht bei der Migration von Datenbeständen und Anwendungen auf den Auftraggeber oder "
                "einen benannten Dritte-Dienstleister für mindestens neunzig (90) Tage ohne Unterbrechung des Geschäftsbetriebs.",
                10, False, fitz.Point(50, 115)
            ),
            ("§ 4 Haftungsobergrenzen und Verzugsstrafen", 12, True, fitz.Point(50, 200)),
            (
                "Bei schuldhafter Nichteinhaltung der vereinbarten Bereitstellungsfristen zahlt der Auftragnehmer "
                "eine Vertragsstrafe in Höhe von 0,2 % der jährlichen Vergütung pro Werktag des Verzugs, "
                "höchstens jedoch 5 % des jährlichen Gesamtauftragswerts. Schadensersatzansprüche wegen grober "
                "Fahrlässigkeit, Vorsatz oder Verletzung von Datenschutzgesetzen bleiben unberührt.",
                10, False, fitz.Point(50, 225)
            ),
            ("§ 5 Unterauftragsvergaben und Sub-Dienstleister (DORA Art. 30 Abs. 3)", 12, True, fitz.Point(50, 310)),
            (
                "Die Hinzuziehung wesentlicher Unterauftragnehmer bedarf der vorherigen schriftlichen Zustimmung "
                "des Auftraggebers. Der Auftraggeber hat ein Widerspruchsrecht mit einer Frist von dreißig (30) Tagen. "
                "Sämtliche Unterauftragnehmer sind denselben IKT-Sicherheits- und Audit-Verpflichtungen zu unterwerfen.",
                10, False, fitz.Point(50, 335)
            ),
            ("Geprüftes Dokument gem. DIN 66399 Schutzklasse 3 • Vertraulich • Seite 2 von 3", 8, False, fitz.Point(50, 780)),
        ],

        # PAGE 3: BDSG Data Privacy, Bank Details, and ZUGFeRD E-Invoice
        [
            ("SIEMENS AG • DATENSCHUTZ UND RECHNUNGSLEGUNG", 10, True, fitz.Point(50, 50)),
            ("§ 6 Datenschutz nach BDSG § 26 und EU-DSGVO", 12, True, fitz.Point(50, 90)),
            (
                "Der Auftragnehmer verarbeitet personenbezogene Daten ausschließlich im Rahmen einer geprüften "
                "Auftragsverarbeitungsvereinbarung (AVV). Serverstandort ist ausschließlich Frankfurt am Main (Bundesrepublik Deutschland).",
                10, False, fitz.Point(50, 115)
            ),
            ("Zahlungsverbindung und Steuerangaben (Geprüft):", 11, True, fitz.Point(50, 180)),
            ("Bankinstitut: Deutsche Bank AG, Frankfurt", 10, False, fitz.Point(50, 205)),
            ("IBAN: DE89 3704 0044 0532 0130 00  •  BIC: DEUTDEDDFXX", 10, True, fitz.Point(50, 225)),
            ("Umsatzsteuer-Identifikationsnummer (USt-IdNr.): DE812345678", 10, False, fitz.Point(50, 245)),
            ("Steuer-Nummer: 91/283/01824", 10, False, fitz.Point(50, 265)),
            ("§ 7 Elektronische Rechnungsstellung gem. ZUGFeRD 2.3 / EN 16931", 12, True, fitz.Point(50, 310)),
            (
                "Rechnungen sind verpflichtend als hybrides ZUGFeRD 2.3 / Factur-X PDF mit eingebettetem XML "
                "(CrossIndustryInvoice) zu übermitteln. Der monatliche Grundpreis beträgt EUR 48.500,00 zzgl. "
                "19 % MwSt. (EUR 9.215,00), Gesamtsumme EUR 57.715,00. Leitweg-ID: 04011000-12345-67.",
                10, False, fitz.Point(50, 335)
            ),
            ("Unterschriften der Parteien:", 11, True, fitz.Point(50, 420)),
            ("Frankfurt am Main, den 15. März 2026", 10, False, fitz.Point(50, 445)),
            ("Siemens AG (Bereichsleitung Recht)              CloudScale GmbH (Geschäftsführung)", 10, True, fitz.Point(50, 480)),
            ("gez. Dr. M. Weber, General Counsel             gez. T. Schneider, CEO", 9, False, fitz.Point(50, 500)),
            ("Geprüftes Dokument gem. DIN 66399 Schutzklasse 3 • Vertraulich • Seite 3 von 3", 8, False, fitz.Point(50, 780)),
        ]
    ]

    for page_items in pages_data:
        page = doc.new_page(width=595, height=842) # A4
        for text, size, is_bold, pt in page_items:
            fontname = "helv"
            if is_bold:
                fontname = "hebo" # Helvetica Bold
            
            # Wrap long text if needed
            if len(text) > 85 and pt.y > 100:
                rect = fitz.Rect(pt.x, pt.y, 545, pt.y + 120)
                page.insert_textbox(rect, text, fontsize=size, fontname=fontname, color=(0.1, 0.12, 0.15))
            else:
                page.insert_text(pt, text, fontsize=size, fontname=fontname, color=(0.08, 0.1, 0.14))

    # Embed real EN 16931 ZUGFeRD XML file into the PDF
    factur_x_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
  xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
  xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocumentContext>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>SIEMENS-2026-ICT-0089</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">20260315</udt:DateTimeString>
    </ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>48500.00</ram:LineTotalAmount>
        <ram:TaxTotalAmount currencyID="EUR">9215.00</ram:TaxTotalAmount>
        <ram:GrandTotalAmount>57715.00</ram:GrandTotalAmount>
        <ram:DuePayableAmount>57715.00</ram:DuePayableAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

    # Attach as embedded Factur-X file
    doc.embfile_add("factur-x.xml", factur_x_xml, filename="factur-x.xml", ufilename="factur-x.xml", desc="ZUGFeRD 2.3 Invoice Stream")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()
    print(f"Generated German Demo PDF with embedded ZUGFeRD XML at: {output_path}")

if __name__ == "__main__":
    out1 = "/Users/nikhitagp/.gemini/antigravity/scratch/docunorm-ai/Siemens_Master_IKT_Vertrag_2026.pdf"
    out2 = os.path.expanduser("~/Desktop/Siemens_Master_IKT_Vertrag_2026.pdf")
    generate_german_demo_pdf(out1)
    try:
        generate_german_demo_pdf(out2)
    except Exception as e:
        print(f"Desktop write warning: {e}")
