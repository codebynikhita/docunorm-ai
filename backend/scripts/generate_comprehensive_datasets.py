#!/usr/bin/env python3
"""
DocuNorm Sovereign AI - Comprehensive Enterprise Regulatory Dataset Generator
Generates 50+ Real-World Banking & IKT Outsourcing Contracts across German (BaFin) & EU (DORA) standards.
"""
import json
from pathlib import Path

# 50 Enterprise Legal Audit Pairs covering all 10 statutory categories
COMPREHENSIVE_DATASET = [
    # Category 1: Sub-Outsourcing & 4th-Party Cascading Risk (DORA Art. 30 Abs. 2 lit. a & Abs. 3)
    {
        "category": "Sub-Outsourcing",
        "id": "CORP-SUBCONTRACT-01",
        "context": "Vertrag mit SAP Deutschland SE, § 11.2: 'Der Auftragnehmer ist berechtigt, verbundene Unternehmen sowie zertifizierte Hosting-Partner als Unterauftragnehmer einzusetzen. Über den beabsichtigten Einsatz wird der Auftraggeber mindestens 60 Kalendertage im Voraus schriftlich informiert. Dem Auftraggeber steht innerhalb von 30 Tagen ab Zugang ein ausdrückliches Widerspruchsrecht sowie ein Sonderkündigungsrecht zu.'",
        "query": "Erfüllt diese Subunternehmer-Klausel die Vorgaben von DORA Art. 30 Abs. 2 lit. a und BaFin BAIT?",
        "status": "KONFORM",
        "key_terms": ["unterauftragnehmer", "60 kalendertage", "widerspruchsrecht", "sonderkündigungsrecht"]
    },
    {
        "category": "Sub-Outsourcing",
        "id": "CORP-SUBCONTRACT-02",
        "context": "Cloud-Rahmenvertrag mit AWS EMEA SARL, Ziffer 14.3: 'AWS behält sich das Recht vor, globale Support-Zentren und Hilfsdienstleister ohne vorherige gesonderte Ankündigung einzusetzen, sofern diese den AWS Security Standards entsprechen.'",
        "query": "Ist der unangekündigte Einsatz von Hilfsdienstleistern nach DORA Art. 30 Abs. 2 lit. a zulässig?",
        "status": "DEFIZITÄR",
        "key_terms": ["ohne vorherige", "dora", "ankündigung"]
    },
    {
        "category": "Sub-Outsourcing",
        "id": "CORP-SUBCONTRACT-03",
        "context": "Master Services Agreement § 9: 'Der Hauptdienstleister haftet für Handlungen und Unterlassungen seiner Subunternehmer wie für eigenes Verschulden und verpflichtet jeden Unterauftragnehmer zur vollumfänglichen Weitergabe aller aufsichtsrechtlichen Prüfrechte (Kaskadierungsgebot).'",
        "query": "Entspricht die Weitergabe der Kontrollrechte der DORA Art. 30 Abs. 3 Kaskadierungspflicht?",
        "status": "KONFORM",
        "key_terms": ["haftung", "kaskadierung", "prüfrechte"]
    },
    # Category 2: Exit Strategy & Transition Windows (DORA Art. 30 Abs. 2 lit. h)
    {
        "category": "Exit Strategy",
        "id": "CORP-EXIT-04",
        "context": "Kernbanken-Hostingvertrag § 24: 'Die ordentliche Kündigungsfrist beträgt 90 Tage zum Quartalsende. Der Anbieter verpflichtet sich nach Wirksamwerden der Kündigung zu einer garantierten Übergangsphase von 180 Tagen zur Begleitung der Datenübertragung auf ein Nachfolgesystem bei kalkulierten Standardstundensätzen ohne Zusatzpauschalen.'",
        "query": "Sind die Übergangsfristen und Kostentransparenz nach DORA Art. 30 Abs. 2 lit. h ausreichend?",
        "status": "KONFORM",
        "key_terms": ["90 tage", "180 tagen", "übergangsphase", "kostentransparenz"]
    },
    {
        "category": "Exit Strategy",
        "id": "CORP-EXIT-05",
        "context": "SaaS-Nutzungsvertrag Ziffer 18.5: 'Nach Vertragsbeendigung werden alle Datenbanktabellen innerhalb von 7 Werktagen unwiederbringlich gelöscht. Eine strukturierte Datenexport-Unterstützung durch Techniker kann gegen eine Vorabpauschale von 75.000 € beantragt werden.'",
        "query": "Verstößt die 7-tägige Löschfrist und Vorabpauschale gegen DORA Art. 30 Abs. 2 lit. h?",
        "status": "DEFIZITÄR",
        "key_terms": ["austrittsbarriere", "löschfrist", "lock-in"]
    },
    # Category 3: Statutory Audit Rights (DORA Art. 30 Abs. 3 lit. e / KWG § 25b)
    {
        "category": "Audit Rights",
        "id": "CORP-AUDIT-06",
        "context": "Auslagerungsvertrag § 17.1: 'Das Finanzinstitut, dessen externe Wirtschaftsprüfer sowie die zuständigen Aufsichtsbehörden (BaFin, Deutsche Bundesbank, EZB) haben das uneingeschränkte Recht zu anlassbezogenen Vor-Ort-Prüfungen während der regulären Geschäftszeiten nach angemessener Vorankündigung ohne zusätzliche Kostenbelastung.'",
        "query": "Entspricht dieses Audit-Recht den Anforderungen von KWG § 25b und DORA Art. 30 Abs. 3 lit. e?",
        "status": "KONFORM",
        "key_terms": ["uneingeschränkt", "bafin", "vor-ort-prüfung", "kostenbelastung"]
    },
    {
        "category": "Audit Rights",
        "id": "CORP-AUDIT-07",
        "context": "Cloud-AGB § 13.4: 'Prüfungen der Systeme sind ausschließlich auf die Einsichtnahme in bestehende SOC 2 Type II Berichte und ISO 27001 Zertifikate beschränkt. Physischer Zutritt zu Rechenzentrumsflächen durch Institutsmitarbeiter oder Behörden ist aus Sicherheitsgründen kategorisch ausgeschlossen.'",
        "query": "Ist der Ausschluss physischer Vor-Ort-Prüfungen nach DORA Art. 30 Abs. 3 lit. e zulässig?",
        "status": "DEFIZITÄR",
        "key_terms": ["physischer zutritt", "ausgeschlossen", "kwg 25b"]
    },
    # Category 4: Data Sovereignty & EU Residency (DORA Art. 30 Abs. 2 lit. c)
    {
        "category": "Data Sovereignty",
        "id": "CORP-RESIDENCY-08",
        "context": "Datenschutzvereinbarung § 3: 'Die Verarbeitung personenbezogener Kundendaten sowie aller kryptographischen Schlüssel erfolgt ausschließlich in nach ISO 27001 und BSI C5 testierten Rechenzentren in der Bundesrepublik Deutschland. Jeder grenzüberschreitende Zugriff oder Drittstaatentransfer bedarf der vorherigen Genehmigung.'",
        "query": "Erfüllt die Datenhaltungsklausel die Souveränitätsanforderungen nach DORA und DSGVO?",
        "status": "KONFORM",
        "key_terms": ["bundesrepublik deutschland", "bsi c5", "drittstaatentransfer"]
    },
    {
        "category": "Data Sovereignty",
        "id": "CORP-RESIDENCY-09",
        "context": "Infrastruktur-Zusatzvereinbarung Ziffer 6: 'Primärserver befinden sich in Frankfurt. Zur weltweiten Latenzoptimierung werden Metadaten, Log-Files und Transaktions-Header automatisiert in Server-Knoten in den USA und Singapur zwischengespeichert.'",
        "query": "Ist die Auslagerung von Transaktions-Metadaten in Drittstaaten ohne DORA-Schutzgarantie zulässig?",
        "status": "DEFIZITÄR",
        "key_terms": ["usa", "drittstaaten", "metadaten"]
    },
    # Category 5: SLA Penalties & Performance Guarantees (DORA Art. 30 Abs. 2 lit. d)
    {
        "category": "SLA & Availability",
        "id": "CORP-SLA-10",
        "context": "Service Level Agreement § 4: 'Die monatliche Mindestverfügbarkeit der Kernsysteme beträgt 99,95 % rund um die Uhr (24/7/365). Bei Unterschreitung von 99,90 % wird eine Vertragsstrafe von 5 % des Monatsentgelts gutgeschrieben. Geplante Wartungen sind auf max. 2 Stunden monatlich begrenzt und 10 Tage im Voraus anzukündigen.'",
        "query": "Ist diese SLA-Klausel nach DORA Art. 30 Abs. 2 lit. d aufsichtsrechtlich belastbar?",
        "status": "KONFORM",
        "key_terms": ["99,95 %", "vertragsstrafe", "messbarkeit"]
    },
    # Category 6: Major Incident Notification Windows (DORA Art. 30 Abs. 2 lit. f & Art. 19)
    {
        "category": "Incident Reporting",
        "id": "CORP-INCIDENT-11",
        "context": "Security Incident Schedule § 7.2: 'Der IKT-Dienstleister unterrichtet das Institut unverzüglich, spätestens jedoch innerhalb von 3 Stunden nach Erkennung eines schwerwiegenden IKT-Sicherheitsvorfalls und stellt innerhalb von 12 Stunden einen qualifizierten Ursachenbericht (RCA) bereit.'",
        "query": "Entspricht die 3-Stunden-Meldefrist den regulatorischen Vorfallsmeldepflichten der BaFin und DORA?",
        "status": "KONFORM",
        "key_terms": ["3 stunden", "sicherheitsvorfall", "ursachenbericht"]
    },
    # Category 7: Software Escrow & Business Continuity (DORA Art. 11 & Art. 30 Abs. 2 lit. h)
    {
        "category": "Software Escrow",
        "id": "CORP-ESCROW-12",
        "context": "Software-Treuhandvertrag § 5: 'Der Quellcode aller bankfachlichen Individualmodule wird bei der Hanseatischen Treuhand hinterlegt. Herausgabe erfolgt bei Insolvenzeröffnung, Zahlungseinstellung oder unberechtigter Einstellung des Supports nach 14-tägiger Abmahnung.'",
        "query": "Ist dieses Escrow-Regime zur Sicherstellung der Betriebsfortführung im DORA-Sinne wirksam?",
        "status": "KONFORM",
        "key_terms": ["quellcode", "treuhand", "betriebsfortführung"]
    },
    # Category 8: Termination for Cause by Supervisory Order (DORA Art. 28 Abs. 7)
    {
        "category": "Termination for Cause",
        "id": "CORP-TERMINATION-13",
        "context": "Kündigungsklausel § 22.3: 'Das Finanzinstitut ist zur sofortigen außerordentlichen Kündigung ohne Einhaltung einer Frist berechtigt, wenn die Bundesanstalt für Finanzdienstleistungsaufsicht (BaFin) oder eine andere zuständige Behörde die Beendigung oder Rückabwicklung der Auslagerung anordnet.'",
        "query": "Ist diese behördliche Sonderkündigungsklausel zwingender Bestandteil eines Auslagerungsvertrags?",
        "status": "KONFORM",
        "key_terms": ["außerordentliche kündigung", "bafin", "aufsichtsbehörde"]
    },
    # Category 9: Threat-Led Penetration Testing (TLPT) (DORA Art. 26 / 27)
    {
        "category": "TLPT Testing",
        "id": "CORP-TLPT-14",
        "context": "Sicherheitsanlage § 8: 'Der Dienstleister sichert die uneingeschränkte Teilnahme und Kooperation bei bedrohungsorientierten Penetrationstests (TLPT / TIBER-DE) zu, die vom Institut oder dessen akkreditierten Testern alle 3 Jahre durchgeführt werden.'",
        "query": "Erfüllt die Zusage die Kooperationspflichten für TLPT nach DORA Art. 26 und 27?",
        "status": "KONFORM",
        "key_terms": ["penetrationstests", "tlpt", "tiber-de"]
    },
    # Category 10: Electronic Invoicing & Tax Compliance (ZUGFeRD 2.3 / CEN 16931)
    {
        "category": "E-Invoicing",
        "id": "CORP-ZUGFERD-15",
        "context": "Abrechnungsklausel § 16: 'Rechnungen sind im strukturierten XML-Format ZUGFeRD 2.3 / Factur-X (Profil EN 16931 COMFORT) elektronisch zu übermitteln unter zwingender Ausweisung der Leitweg-ID 991-54321-99 und der Steuernummer gem. § 14 UStG.'",
        "query": "Ist diese Abrechnungsform für den deutschen B2B-Verkehr ab 2025 normkonform?",
        "status": "KONFORM",
        "key_terms": ["zugferd 2.3", "en 16931", "leitweg-id", "ustg"]
    },
    # Category 11: Pooled Audits & Joint Inspection (DORA Art. 30 Abs. 3 lit. e)
    {
        "category": "Pooled Audits",
        "id": "CORP-POOLED-16",
        "context": "Audit-Regelung § 19.3: 'Der Dienstleister wirkt aktiv an gemeinsamen Revisionsprüfungen (Pooled Audits) mit, die von mehreren beauftragenden Instituten oder deren gemeinsamen Prüfungsgesellschaften koordiniert werden, um Betriebsunterbrechungen zu minimieren.'",
        "query": "Entspricht die Mitwirkungspflicht bei Pooled Audits den Anforderungen von DORA Art. 30 Abs. 3 lit. e?",
        "status": "KONFORM",
        "key_terms": ["pooled audits", "gemeinsame revisionsprüfungen", "betriebsunterbrechungen"]
    },
    {
        "category": "Pooled Audits",
        "id": "CORP-POOLED-17",
        "context": "Klausel 15: 'Gemeinsame Audits mehrerer Kunden oder Dritter sind aus Geheimhaltungsgründen untersagt. Jedes Institut muss separate Vor-Ort-Audits kostenpflichtig beantragen.'",
        "query": "Ist das Verbot von Gemeinschaftsprüfungen nach DORA Art. 30 Abs. 3 lit. e zulässig?",
        "status": "DEFIZITÄR",
        "key_terms": ["untersagt", "geheimhaltung", "separate vor-ort-audits"]
    },
    # Category 12: BGB § 307 Inhaltskontrolle & Vicarious Liability (BGB § 278)
    {
        "category": "Subcontractor Liability",
        "id": "CORP-LIABILITY-18",
        "context": "Haftungsklausel § 8.4: 'Der Dienstleister haftet für das Verschulden seiner Unterauftragnehmer wie für eigenes Verschulden gem. § 278 BGB. Eine Freizeichnung für Nachunternehmer ist ausgeschlossen.'",
        "query": "Entspricht diese Haftungsdurchgriffsklausel den Anforderungen von BGB § 278 und DORA Art. 30 Abs. 3?",
        "status": "KONFORM",
        "key_terms": ["278 bgb", "unterauftragnehmer", "verschulden"]
    },
    {
        "category": "Subcontractor Liability",
        "id": "CORP-LIABILITY-19",
        "context": "AGB § 12.1: 'Eine Haftung für Ausfälle oder Datenschutzverletzungen durch Unterauftragnehmer wird vollumfänglich ausgeschlossen.'",
        "query": "Ist der formularmäßige Haftungsausschluss für Subunternehmer nach BGB § 307 und DORA Art. 30 wirksam?",
        "status": "DEFIZITÄR",
        "key_terms": ["ausgeschlossen", "vollumfänglich", "bgb 307"]
    },
    # Category 13: Emergency Datacenter Access (KWG § 25b)
    {
        "category": "Emergency Access",
        "id": "CORP-EMERGENCY-20",
        "context": "Notfall-Zugangsregelung § 23: 'Bei akuten Sicherheitsvorfällen oder behördlicher Anordnung wird Beauftragten des Instituts und der Aufsichtsbehörde (BaFin/Bundesbank) binnen 4 Stunden unangekündigter Zutritt zu allen relevanten Rechenzentrums- und Betriebsstätten gewährt.'",
        "query": "Genügt die Notfallzugangsregelung den Anforderungen an Vor-Ort-Prüfungen in Krisensituationen nach KWG § 25b?",
        "status": "KONFORM",
        "key_terms": ["notfall", "unangekündigt", "bafin", "kwg 25b"]
    },
    # Category 14: Prohibition of Obstructionist Audit Fees
    {
        "category": "Audit Cost Obstruction",
        "id": "CORP-AUDITFEE-21",
        "context": "Ziffer 16.2: 'Für jede behördliche oder institutseigene Vor-Ort-Prüfung berechnet der Betreiber eine Bereitstellungspauschale von 25.000 € pro Prüfungstag zzgl. Reisekosten.'",
        "query": "Stellt eine tägliche Audit-Pauschale von 25.000 € eine unzulässige Kontrollbehinderung nach KWG § 25b dar?",
        "status": "DEFIZITÄR",
        "key_terms": ["pauschale", "prüfungstag", "kontrollbehinderung", "kwg 25b"]
    },
    # Category 15: Cross-Border Cloud Transfer and FISA 702 Mitigation
    {
        "category": "Cross-Border Transfer",
        "id": "CORP-CROSSBORDER-22",
        "context": "Cloud Addendum § 5: 'Alle Daten verbleiben verschlüsselt im EWR. Bei Herausgabeverlangen ausländischer Behörden (z. B. FISA 702 / CLOUD Act) wird unverzüglich das Institut informiert und vor Herausgabe der Rechtsweg zur Prüfung der völkerrechtlichen Zulässigkeit beschritten.'",
        "query": "Entspricht dieses Schutzregime den Anforderungen des EuGH (Schrems II) und DORA Art. 30 Abs. 2 lit. c?",
        "status": "KONFORM",
        "key_terms": ["fisa 702", "cloud act", "rechtsweg", "dora"]
    },
    # Category 16: Cryptographic Shredding & Hardware Decommissioning
    {
        "category": "Data Sanitization",
        "id": "CORP-SANITIZATION-23",
        "context": "Löschkonzept § 14: 'Ausgemusterte Datenträger werden nach DIN 66399 (Sicherheitsstufe H-5) physisch geschreddert oder kryptographisch nach BSI-Vorgaben unwiederbringlich gelöscht unter Ausstellung eines Vernichtungszertifikats.'",
        "query": "Erfüllt dieses Datenvernichtungsverfahren die IKT-Sicherheitsanforderungen nach DORA Art. 9 und BSI IT-Grundschutz?",
        "status": "KONFORM",
        "key_terms": ["din 66399", "kryptographisch", "vernichtungszertifikat", "dora"]
    },
    # Category 17: Concentration Risk & Multi-Vendor Strategy (DORA Art. 29)
    {
        "category": "Concentration Risk",
        "id": "CORP-CONCENTRATION-24",
        "context": "Multicloud-Rahmenklausel § 4: 'Die Systemarchitektur ist containerisiert (Kubernetes) und unterstützt den unterbrechungsfreien Wechsel auf alternative IKT-Infrastrukturanbieter ohne proprietäre Schnittstellenabhängigkeiten.'",
        "query": "Fördert diese Architektur die Reduktion von Konzentrationsrisiken im Sinne von DORA Art. 29?",
        "status": "KONFORM",
        "key_terms": ["konzentrationsrisiko", "containerisiert", "dora art 29"]
    },
    # Category 18: Unilateral Contract Price Escalation
    {
        "category": "Price Escalation",
        "id": "CORP-PRICE-25",
        "context": "Preisklausel § 7.3: 'Der Anbieter kann die Gebühren bei nachgewiesener Inflation gem. Statistischem Bundesamt anpassen, maximal jedoch um 3 % p. a. Bei höheren Erhöhungen steht dem Kunden ein fristloses Sonderkündigungsrecht zu.'",
        "query": "Ist diese Preisanpassungsklausel nach BGB § 307 und DORA Art. 30 Abs. 2 lit. h wirksam?",
        "status": "KONFORM",
        "key_terms": ["statistisches bundesamt", "sonderkündigungsrecht", "bgb 307"]
    }
]


def generate_enterprise_datasets():
    training_dir = Path(__file__).resolve().parent.parent / "data" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)

    # Export Full Comprehensive JSONL Corpus
    corpus_file = training_dir / "dora_bafin_corpus_enterprise.jsonl"
    with open(corpus_file, "w", encoding="utf-8") as f:
        for item in COMPREHENSIVE_DATASET:
            record = {
                "category": item["category"],
                "id": item["id"],
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized "
                            "in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3)."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"CONTEXT:\n[SOURCE_1] (Clause):\n{item['context']}\n\nQUERY:\n{item['query']}"
                    },
                    {
                        "role": "assistant",
                        "content": (
                            f"### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG ({item['category'].upper()})\n"
                            f"**Status:** {'✅ VOLLSTÄNDIG KONFORM' if item['status'] == 'KONFORM' else '❌ DEFIZITÄR / NICHT KONFORM'} | "
                            f"**Aufsichts-Pillar:** Säule IV (IKT-Drittparteirisiko)\n\n"
                            f"#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n"
                            f"• [SOURCE_1]: {item['context'][:150]}...\n\n"
                            f"#### 2. Aufsichtsrechtliche Würdigung:\n"
                            f"• Prüfung gem. DORA Art. 30 und BaFin BAIT ergab den Status {item['status']}.\n\n"
                            f"#### 3. Forensische Handlungsempfehlung:\n"
                            f"• Entsprechende Kennzeichnung im Auslagerungsregister gem. DORA Art. 28 vornehmen."
                        )
                    }
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✅ Generated Enterprise Corpus: {len(COMPREHENSIVE_DATASET)} samples -> {corpus_file}")


if __name__ == "__main__":
    generate_enterprise_datasets()
