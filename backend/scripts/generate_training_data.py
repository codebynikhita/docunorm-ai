#!/usr/bin/env python3
"""
DocuNorm Sovereign AI - Regulatory Training & Benchmark Dataset Generator
Generates high-precision BaFin & DORA Article 30 JSONL fine-tuning and evaluation datasets (25+ pairs).
"""
import json
import os
from pathlib import Path

TRAIN_DATA = [
    # 1. Termination and migration window
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 3):\n§ 8 Abs. 2: Die Kündigungsfrist beträgt 60 Tage zum Monatsende. Der IKT-Dienstleister garantiert einen 90-tägigen Migrationsbeistand zur lückenlosen Datenübergabe.\n\nQUERY:\nSind die Kündigungsfristen und Migrationszusagen nach DORA Art. 30 zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 2)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Säule IV (IKT-Drittparteirisiko & Exit-Strategie)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Klausel § 8 Abs. 2 garantiert eine Kündigungsfrist von 60 Tagen und 90 Tage Migrationsunterstützung.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Erfüllt die Mindestvorgaben zur Vermeidung operativer Betriebsunterbrechungen gem. DORA Art. 30 Abs. 2 lit. e und h.\n\n#### 3. Forensische Handlungsempfehlung:\n• Klausel unverändert in das aufsichtsrechtliche Auslagerungsregister übernehmen."
    },
    # 2. Sub-outsourcing without notice
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 14):\nZiffer 12.4: Subunternehmer können vom Cloud-Anbieter ohne gesonderte Vorankündigung beauftragt werden.\n\nQUERY:\nIst die Weiterübertragung von IKT-Dienstleistungen ohne Vorankündigung nach DORA zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 2 LIT. A)\n**Status:** ❌ DEFIZITÄR / NICHT KONFORM | **Aufsichts-Pillar:** Säule IV (Weiterverlagerung & Kaskadierungsrisiko)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Ziffer 12.4 gestattet Subunternehmerbeauftragung ohne vorherige schriftliche Vorankündigung.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verstoß gegen DORA Art. 30 Abs. 2 lit. a und BaFin BAIT: Bei Auslagerungen ist eine Vorankündigungsfrist und ein Widerspruchsrecht gesetzlich zwingend.\n\n#### 3. Forensische Handlungsempfehlung:\n• Ergänzung einer vertraglichen Vorankündigungspflicht von mindestens 60 Tagen mit qualifiziertem Einspruchsrecht."
    },
    # 3. Audit rights restrictions
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 9):\n§ 14 Vor-Ort-Prüfungen: Prüfungen durch das Finanzinstitut oder dessen Beauftragte sind auf maximal alle drei Jahre beschränkt.\n\nQUERY:\nEntspricht dieses Audit-Recht den aufsichtsrechtlichen Prüfrechten nach KWG § 25b und DORA Art. 30 Abs. 3?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (PRÜFUNGSRECHTE)\n**Status:** ❌ DEFIZITÄR / NICHT KONFORM | **Aufsichts-Pillar:** Säule IV (Aufsichtsrechtliche Kontroll- & Vor-Ort-Prüfrechte)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 14 beschränkt Vor-Ort-Audits auf ein 3-Jahres-Intervall.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verstoß gegen DORA Art. 30 Abs. 3 lit. e und KWG § 25b Abs. 1: Aufsichtsbehörde und Institut benötigen uneingeschränkten, anlassbezogenen Zugang.\n\n#### 3. Forensische Handlungsempfehlung:\n• Zeitliche Beschränkung ersatzlos streichen und vollumfängliche Revisionsrechte implementieren."
    },
    # 4. ZUGFeRD 2.3 electronic invoice
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 1):\nZUGFeRD Profile: EN 16931 (COMFORT). Total: 5.355,00 EUR. Leitweg-ID: 991-12345-67.\n\nQUERY:\nIst dieses Dokument als elektronische Rechnung nach deutschem Recht 2025 zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (ZUGFeRD 2.3 / E-RECHNUNG 2025)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** Elektronische Rechnungsstellung gem. Wachstumschancengesetz / CEN 16931\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: XML-Profil entspricht EN 16931 COMFORT gem. ZUGFeRD 2.3 mit hinterlegter Leitweg-ID.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Erfüllt die ab 01.01.2025 in Deutschland verbindliche Pflicht für strukturierte B2B E-Rechnungen lückenlos.\n\n#### 3. Forensische Handlungsempfehlung:\n• Freigabe zur automatisierten Buchung und revisionssicheren GoBD-Archivierung erteilen."
    },
    # 5. Data residency in EU
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 6):\n§ 4 Abs. 1: Die primäre Datenhaltung sowie Backups erfolgen ausschließlich in ISO-27001-zertifizierten Rechenzentren im EWR (Frankfurt und Dublin).\n\nQUERY:\nErfüllt der Speicherort die DORA- und DSGVO-Vorgaben?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DATENRESIDENZ)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 2 lit. c (Standort der IKT-Dienste)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Vertragliche Begrenzung der Datenverarbeitung und Backups auf Standorte innerhalb des EWR (Deutschland/Irland).\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Gewährleistet Konformität mit DORA Art. 30 Abs. 2 lit. c sowie DSGVO Art. 44 ff. ohne Drittlandstransferrisiken.\n\n#### 3. Forensische Handlungsempfehlung:\n• Standorte im Auslagerungsverzeichnis dokumentieren."
    },
    # 6. Service Level Penalties
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 7):\n§ 11 SLA: Die Mindestverfügbarkeit beträgt 99,95 % pro Kalendermonat. Bei Unterschreitung um mehr als 0,5 % wird eine Vertragsstrafe von 5 % des Monatsentgelts fällig.\n\nQUERY:\nSind die vereinbarten SLAs und Pönalen aufsichtsrechtlich ausreichend?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (SLA & VERTRAGSSTRAFEN)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 2 lit. d\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Klare quantitative Verfügbarkeitsziele (99,95 %) und bezifferte Pönalen bei Nichterfüllung.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Erfüllt die geforderten quantitativen und qualitativen Dienstgüteanforderungen gem. DORA Art. 30 Abs. 2 lit. d.\n\n#### 3. Forensische Handlungsempfehlung:\n• Monatliche automatische SLA-Messprotokolle an das IKT-Risikomanagement übermitteln."
    },
    # 7. Unilateral price increases
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 12):\nZiffer 9.3: Der Anbieter ist berechtigt, die monatlichen Nutzungsgebühren jederzeit einseitig um bis zu 20 % ohne Sonderkündigungsrecht anzupassen.\n\nQUERY:\nIst eine einseitige Preisanpassung ohne Kündigungsrecht nach DORA und BGB zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (PREISANPASSUNG & EXIT-RECHTE)\n**Status:** ❌ DEFIZITÄR / NICHT KONFORM | **Aufsichts-Pillar:** Kündigungsrechte & Ausstiegsstrategie\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Ziffer 9.3 sieht einseitige Gebührenerhöhungen um 20 % ohne Sonderkündigungsrecht vor.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Unwirksam nach BGB § 307 und unvereinbar mit DORA Art. 30 Abs. 2 lit. h: Wesentliche Vertragsänderungen erfordern zwingend ein Sonderkündigungsrecht.\n\n#### 3. Forensische Handlungsempfehlung:\n• Sonderkündigungsrecht bei Preiserhöhungen > 3 % mit mindestens 30 Tagen Frist vereinbaren."
    },
    # 8. Incident Notification Times
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 5):\n§ 7 Sicherheitsvorfälle: Schwerwiegende IKT-Sicherheitsvorfälle sind dem Finanzinstitut unverzüglich, spätestens jedoch innerhalb von 4 Stunden nach Entdeckung zu melden.\n\nQUERY:\nReicht diese Meldefrist für DORA-Vorfallsmeldungen aus?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (IKT-VORFALLSMELDUNG)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 2 lit. f & Art. 19\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: 4-Stunden-Frist zur Meldung schwerwiegender IKT-Vorfälle vertraglich festgeschrieben.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Ermöglicht dem Institut die Einhaltung der aufsichtsrechtlichen BaFin/DORA Erstmeldefristen (innerhalb von 24h gem. DORA RTS).\n\n#### 3. Forensische Handlungsempfehlung:\n• Meldekette in das betriebliche Incident-Response-Handbuch einpflegen."
    },
    # 9. Business Continuity Plan (BCP) & Disaster Recovery
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 8):\n§ 13 Notfallbetrieb: Der Dienstleister führt jährlich nachweisbare Notfalltests durch und garantiert eine Wiederherstellungszeit (RTO) von unter 2 Stunden.\n\nQUERY:\nEntspricht dies den Vorgaben für Notfallkonzepte nach BaFin BAIT und DORA?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (NOTFALLKONZEPT & RTO)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 11 & Art. 30 Abs. 2 lit. b\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: RTO unter 2 Stunden und jährliche BCP-Notfalltests vertraglich garantiert.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Erfüllt die Anforderungen an Notfallpläne und Resilienztests nach BaFin RS 10/2018 (BAIT Ziffer 8).\n\n#### 3. Forensische Handlungsempfehlung:\n• Jährliche Testberichte unaufgefordert zum Prüfungsstichtag anfordern."
    },
    # 10. Data deletion after termination
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 15):\nZiffer 18.2: Nach Vertragsende werden alle Daten auf Verlangen des Kunden unwiderruflich und DSGVO-konform gelöscht und ein Löschprotokoll übergeben.\n\nQUERY:\nIst diese Regelung zur Datenlöschung aufsichtsrechtlich zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DATENLÖSCHUNG & DSGVO)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 2 lit. g & DSGVO Art. 28\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Unwiderrufliche Löschung nach Vertragsende mit qualifiziertem Löschzertifikat geregelt.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verhindert unbefugte Weiterverarbeitung nach Vertragsende gem. DSGVO Art. 28 Abs. 3 lit. g und DORA Art. 30.\n\n#### 3. Forensische Handlungsempfehlung:\n• Vor der Löschung vollständige Datenübernahme im institutsweiten Archiv sicherstellen."
    },
    # 11-20 More variations for robust training
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 4):\n§ 6 Abs. 3: Der Dienstleister sichert Verschlüsselung nach Stand der Technik (AES-256 für ruhende Daten, TLS 1.3 bei Übertragung) zu.\n\nQUERY:\nSind die Verschlüsselungsstandards nach DORA Art. 9 ausreichend?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (VERSCHLÜSSELUNG & IKT-SICHERHEIT)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 9 Abs. 2 (Schutz- und Präventionsmaßnahmen)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: AES-256 (At-Rest) und TLS 1.3 (In-Transit) vertraglich garantiert.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Entspricht den BSI TR-02102 Leitlinien sowie DORA Art. 9.\n\n#### 3. Forensische Handlungsempfehlung:\n• Jährliche Validierung der Zertifikatslaufzeiten veranlassen."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 10):\n§ 16 Exit-Kosten: Die Herausgabe der Mandantendaten im Exit-Fall wird nach tatsächlichem Aufwand mit 450 € pro Stunde ohne Kostendeckel abgerechnet.\n\nQUERY:\nSind ungedeckelte Migrationskosten nach DORA Art. 30 zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (EXIT-KOSTEN & VENDOR LOCK-IN)\n**Status:** ❌ DEFIZITÄR / NACHBESSERUNGSBEDARF | **Aufsichts-Pillar:** DORA Art. 30 Abs. 2 lit. h\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Unbegrenzte Stundensätze (450 €/h) für die Datenherausgabe bei Vertragsbeendigung.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Wirkt als finanzielle Austrittsbarriere ('Exit Barrier') und widerspricht DORA Art. 30 Abs. 2 lit. h.\n\n#### 3. Forensische Handlungsempfehlung:\n• Feste Pauschale oder verbindliche Obergrenze (Cap) für den Migrationsbeistand vereinbaren."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 2):\n§ 3 Informationspflicht: Bei Änderungen an IKT-Systemen, die die Sicherheit beeinträchtigen könnten, wird das Institut 30 Tage im Voraus unterrichtet.\n\nQUERY:\nReicht diese Vorankündigung für Systemänderungen nach DORA aus?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (ÄNDERUNGSMANAGEMENT)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 2 lit. a\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: 30 Tage Vorankündigung bei sicherheitsrelevanten Systemänderungen.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Ermöglicht dem Institut adäquate Risikoprüfungen gem. DORA Art. 28.\n\n#### 3. Forensische Handlungsempfehlung:\n• Klausel beibehalten und in das Change-Management-Register übernehmen."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 11):\n§ 15 TLPT-Tests: Der Dienstleister verpflichtet sich zur uneingeschränkten Kooperation bei bedrohungsorientierten Penetrationstests (TLPT) des Instituts.\n\nQUERY:\nIst diese Kooperationspflicht konform mit DORA Art. 26 und Art. 27?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (TLPT-KOOPERATION)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 26 & 27 (Threat-Led Penetration Testing)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Ausdrückliche Mitwirkungspflicht bei TLPT-Tests vertraglich zugesagt.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Erfüllt die verbindlichen DORA-Vorgaben für erweiterte Resilienzprüfungen bei kritischen Dienstleistern.\n\n#### 3. Forensische Handlungsempfehlung:\n• Testfenster rechtzeitig vor der 3-jährigen TLPT-Frist abstimmen."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 1):\nFactur-X 1.0 (BASIC-WL). Keine Leitweg-ID angegeben. Gesamtsumme: 1.200,00 EUR.\n\nQUERY:\nIst dieses Rechnungsformat für Behörden (B2G) in Deutschland nach dem E-Rechnungsgesetz zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (E-RECHNUNG / B2G)\n**Status:** ❌ DEFIZITÄR / ABGEWIESEN | **Aufsichts-Pillar:** CEN 16931 & E-Rechnungsverordnung (E-RechV)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Fehlende Leitweg-ID und Profil BASIC-WL (ohne detaillierte Positionsdaten).\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Für B2G-Rechnungen ist die Leitweg-ID gesetzlich zwingend gem. § 5 E-RechV. BASIC-WL genügt nicht EN 16931.\n\n#### 3. Forensische Handlungsempfehlung:\n• Rechnung ablehnen und Neuausstellung im Profil EN 16931 (COMFORT/XRechnung) mit Leitweg-ID fordern."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 7):\n§ 9 Geheimhaltung: Die Geheimhaltungspflichten erlöschen 12 Monate nach Vertragsbeendigung.\n\nQUERY:\nIst diese kurze Geheimhaltungsfrist bei Bankgeheimnis und aufsichtsrechtlichen Daten zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (BANKGEHEIMNIS & VERTRAULICHKEIT)\n**Status:** ❌ DEFIZITÄR / NACHBESSERUNGSBEDARF | **Aufsichts-Pillar:** KWG § 25b & DORA Vertraulichkeit\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Geheimhaltungspflicht erlischt bereits 1 Jahr nach Vertragsbeendigung.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verstoß gegen KWG-Anforderungen: Kundendaten und Bankgeheimnis müssen zeitlich unbegrenzt geschützt bleiben.\n\n#### 3. Forensische Handlungsempfehlung:\n• Klausel auf unbefristete Geheimhaltung bezüglich sensibler Bank- und Kundendaten erweitern."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 3):\n§ 5 Kündigung aus wichtigem Grund: Das Institut kann den Vertrag fristlos kündigen, wenn die BaFin die Beendigung der Auslagerung anordnet.\n\nQUERY:\nEntspricht dieses Sonderkündigungsrecht den BaFin-Mindestanforderungen?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (BEHÖRDLICHE KÜNDIGUNGSRECHTE)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 28 Abs. 7 & KWG § 25b\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Fristlose Kündigung bei aufsichtsbehördlicher Anordnung ausdrücklich geregelt.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Erfüllt die zwingende BaFin-Vorgabe gem. BAIT Ziffer 8.5 und DORA Art. 28 Abs. 7.\n\n#### 3. Forensische Handlungsempfehlung:\n• Klausel unverändert beibehalten."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 13):\n§ 17 Versicherungsschutz: Der IKT-Dienstleister weist eine branchenübliche Cyber-Haftpflichtversicherung mit einer Deckungssumme von mindestens 10 Mio. EUR nach.\n\nQUERY:\nIst dieser Versicherungsnachweis aufsichtsrechtlich angemessen?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (VERSICHERUNGSSCHUTZ & HAFTUNG)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** Drittpartei-Risikominimierung\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Nachweis einer Cyber-Police über 10 Mio. EUR vereinbart.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Reduziert Restrisiken bei Großschadensereignissen im Einklang mit BaFin BAIT.\n\n#### 3. Forensische Handlungsempfehlung:\n• Jährliche Überprüfung der Versicherungspolice im Vendor-Management-Kalender vormerken."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 2):\n§ 2 Vertragsgegenstand: Die Leistungen umfassen das Kernbank-Hosting sowie die Bereitstellung von Cloud-Infrastruktur.\n\nQUERY:\nHandelt es sich hierbei um eine wesentliche Auslagerung bzw. kritische IKT-Funktion?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (EINSTUFUNG DER AUSLAGERUNG)\n**Status:** ⚠️ KRITISCHE / WESENTLICHE FUNKTION | **Aufsichts-Pillar:** DORA Art. 3 Nr. 22 & KWG § 25b\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Gegenstand ist Kernbank-Hosting und Cloud-Infrastruktur.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Kernbankbetrieb stellt nach BaFin und DORA stets eine kritische/wichtige Funktion mit höchsten Schutzauflagen dar.\n\n#### 3. Forensische Handlungsempfehlung:\n• Vollständiges DORA Art. 30 Abs. 3 Prüfregime (inkl. verschärfter Exit- und Prüfrechte) anwenden."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 6):\n§ 10 Quellcode-Hinterlegung: Der Anbieter hinterlegt den Quellcode der Bankanwendung bei einem unabhängigen Escrow-Agenten in Deutschland mit Freigabe bei Insolvenz.\n\nQUERY:\nErfüllt diese Escrow-Klausel die Anforderungen an Ausstiegsszenarien?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (SOFTWARE-ESCROW & EXIT)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 2 lit. h (Ausstiegsstrategie)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Software-Escrow-Hinterlegung mit vertraglicher Insolvenzfreigabe vereinbart.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Wirksame Absicherung gegen Anbieterinsolvenz und Vendor Lock-in gem. DORA und BaFin BAIT.\n\n#### 3. Forensische Handlungsempfehlung:\n• Jährliche Aktualitätsprüfung des hinterlegten Escrow-Pakets durchführen."
    },
    # 21. KWG § 25b / DORA Art. 30(3)(e) Supervisory Audit Rights (On-Site Datacenter Access)
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 14):\n§ 18 Abs. 2: Der physische Zutritt zu Serverräumen und Rechenzentren durch das Institut oder die Aufsichtsbehörde (BaFin, EZB) ist kategorisch ausgeschlossen. Audits sind auf den Abruf von SOC-2-Berichten beschränkt.\n\nQUERY:\nIst der Ausschluss physischer Rechenzentrumsprüfungen nach KWG § 25b und DORA Art. 30 Abs. 3 lit. e zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 3 LIT. E & KWG § 25B)\n**Status:** ❌ DEFIZITÄR / NICHT KONFORM | **Aufsichts-Pillar:** Säule IV (Physische Prüf- & Betretungsrechte)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 18 Abs. 2 schließt Vor-Ort-Zutritt zu Rechenzentren für Prüfer und Aufsichtsbehörden vollständig aus.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Eklatanter Verstoß gegen KWG § 25b Abs. 1 und DORA Art. 30 Abs. 3 lit. e: Finanzinstitute und die Aufsicht (BaFin, Deutsche Bundesbank, EZB) besitzen ein gesetzlich unabdingbares Recht auf Vor-Ort-Prüfungen in Betriebs- und Rechenzentrumsräumen.\n\n#### 3. Forensische Handlungsempfehlung:\n• Streichung des Zutrittsverbots und vertragliche Vereinbarung uneingeschränkter Prüf- und Zutrittsrechte gem. BaFin-Standardklausel."
    },
    # 22. Pooled Audits & Joint Inspection (DORA Art. 30 Abs. 3 lit. e)
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 16):\n§ 20 Abs. 3: Gemeinschaftsprüfungen (Pooled Audits) durch mehrere beauftragende Finanzinstitute sind ausdrücklich ausgeschlossen. Audits dürfen nur bilateral durch jeweils eine Partei einzeln durchgeführt werden.\n\nQUERY:\nIst ein vertraglicher Ausschluss von Gemeinschaftsprüfungen (Pooled Audits) unter DORA zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (GEMEINSCHAFTSPRÜFUNGEN / POOLED AUDITS)\n**Status:** ❌ DEFIZITÄR / NICHT KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 3 lit. e & Art. 28\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 20 Abs. 3 untersagt die Organisation und Durchführung von Gemeinschaftsprüfungen mehrerer beauftragender Institute.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Widerspricht den ausdrücklichen Grundsätzen von DORA Art. 30 Abs. 3 lit. e: Die europäische Verordnung fördert Pooled Audits zur Bündelung von Revisionsressourcen und Senkung des operativen Störungsaufwands.\n\n#### 3. Forensische Handlungsempfehlung:\n• Pooled-Audit-Klausel nach DORA-Muster einfügen und Kooperationspflicht des Providers verankern."
    },
    # 23. BGB § 307 / § 278 Vicarious Subcontractor Liability Disclaimer
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 22):\n§ 27 Haftung: Eine Haftung des Dienstleisters für Pflichtverletzungen von Subunternehmern und weiteren Erfüllungsgehilfen ist vollumfänglich abbedungen.\n\nQUERY:\nIst dieser Haftungsausschluss für Subunternehmer nach BGB § 307 und DORA Art. 30 wirksam?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (BGB § 307 / § 278 & DORA ART. 30)\n**Status:** ❌ DEFIZITÄR / NICHTIG NACH BGB § 307 | **Aufsichts-Pillar:** Zivilrechtliche Durchgriffshaftung & DORA Säule IV\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 27 bedingt jegliche Haftung für Erfüllungsgehilfen und Subdienstleister formularmäßig ab.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Die Klausel ist gem. § 307 Abs. 2 Nr. 1 i.V.m. § 278 BGB unwirksam. Nach DORA Art. 30 Abs. 3 haftet der Hauptdienstleister stets vollumfänglich für die Leistungserbringung seiner Subunternehmerkette.\n\n#### 3. Forensische Handlungsempfehlung:\n• Unverzügliche Vertragsnachbesserung gem. BGB § 311: Aufnahme einer verschuldensunabhängigen Einstandspflicht des Hauptdienstleisters."
    },
    # 24. Cross-Border English Contract Analysis (AWS/Azure terms under BaFin)
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 5):\nSection 11.4: All transaction telemetry and tenant access logs may be processed in US data centers under US jurisdictional disclosure requirements without notification to customer.\n\nQUERY:\nErfüllt diese englische Vertragsklausel die europäischen Souveränitäts- und Drittstaatentransfer-Vorgaben nach DORA Art. 30 Abs. 2 lit. c?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 2 LIT. C / SCHREMS II)\n**Status:** ❌ DEFIZITÄR / DRITTSTAATENTRANSFERRISIKO | **Aufsichts-Pillar:** Datenresidenz & Drittstaatentransfer\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Section 11.4 legitimiert den unangekündigten Transfer von Mandanten-Telemetriedaten und Protokollen in US-Rechenzentren.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verstoß gegen DORA Art. 30 Abs. 2 lit. c und DSGVO Art. 44 ff.: Die Auslagerung unterliegt US-Herausgabebefugnissen ohne die nach EuGH Schrems II erforderlichen Standardvertragsklauseln und technischen Zusatzmaßnahmen (Verschlüsselung).\n\n#### 3. Forensische Handlungsempfehlung:\n• Begrenzung auf EWR-Standorte sowie 'Data Sovereignty Addendum' mit Verschlüsselungs-Treuhand fordern."
    },
    # 25. BGB § 311 Redline Contract Remediation
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 8):\nAlt-Klausel § 14: Kündigung ist nur mit 12-monatiger Frist zum Jahresende möglich. Migrationsunterstützung wird nicht geschuldet.\n\nQUERY:\nWie lautet die verbindliche Musterklausel gem. BGB § 311 zur DORA-Konformität?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (BGB § 311 VERTRAGSNACHBESSERUNG)\n**Status:** 🔄 NACHBESSERUNGSERFORDERLICH | **Aufsichts-Pillar:** Kündigungs- & Ausstiegsregelung gem. DORA Art. 30 Abs. 2\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Alt-Klausel § 14 blockiert den geordneten Ausstieg durch überlange Kündigungsfristen und Fehlen jeglicher Migrationsbeistandszusagen.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verstoß gegen DORA Art. 30 Abs. 2 lit. e & h. Die Vereinbarung muss zwingend nachgebessert werden.\n\n#### 3. BGB § 311 Musterklausel (Redline-Ersatz):\n• *'§ 14 Kündigung & Ausstiegsbegleitung: Die ordentliche Kündigungsfrist beträgt 60 Kalendertage zum Monatsende. Der Auftragnehmer sichert einen lückenlosen Migrationsbeistand für einen Zeitraum von mindestens 90 Tagen nach Vertragsbeendigung zur geordneten Datenübergabe auf offene Datenstandards ohne Sonderzuschläge zu.'*"
    },
    # 26. SLA Penalty Matrix & Downtime Thresholds (Day 12 Table Recognition)
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 12):\nAnlage 4 SLA-Katalog A: Tier-3 Platin Kern-SLA Verfügbarkeit ≥ 99,95 % p.a. Pönale: 0,2 % Verzugsstrafstaffel pro Werktag, Pönalendeckel von maximal 5 % des jährlichen Auftragswerts gem. DORA Art. 30 Abs. 2 lit. d.\n\nQUERY:\nSind die Verfügbarkeits- und Pönalstaffeln nach DORA Art. 30 Abs. 2 lit. d und BaFin BAIT 8.1 konform?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (SLA-KATALOG & PÖNALEN)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 2 lit. d (Dienstgütevereinbarungen & Pönalen)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Mindestverfügbarkeit von 99,95 % p.a., 0,2 % Verzugsstrafe/Tag und ein Pönalendeckel von 5 % des Jahreswerts sind verbindlich vereinbart.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Erfüllt die geforderten quantitativen Resilienzkriterien für kritische Kern-Finanzfunktionen nach DORA Art. 30 Abs. 2 lit. d und BaFin BAIT 8.1.\n\n#### 3. Forensische Handlungsempfehlung:\n• Monatliche SLA-Ausfallzeitmessungen revisionssicher im Auslagerungscockpit erfassen."
    },
    # 27. Academic Certification (IELTS Candidate Identity & Score Report)
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 1):\nCandidate Name: NIKHITA GOWDARA PRABHAKARA REDDY. Candidate Number: AD872063. Test Report Form Number: 26IA515338GOWN008A. Listening: 7.5, Reading: 7.0, Speaking: 6.5, Writing: 6.0. Overall Band Score: 7.0 (CEFR Level C1).\n\nQUERY:\nWelche Identitäts- und Prüfungsergebnisse sind im Testbericht dokumentiert?",
        "assistant": "### 📋 OFFIZIELLER TESTBERICHT & SCORE-EVALUATION (IELTS ACADEMIC)\n**Status:** ✅ VERIFIZIERT & BESTANDEN | **Overall Band Score:** **7.0** (**CEFR C1**)\n\n#### 1. Klausel-Befund & Exakte Prüfungsergebnisse (Forensischer Beleg):\n• [SOURCE_1]: Candidate ID AD872063 (NIKHITA GOWDARA PRABHAKARA REDDY) erzielte einen Overall Band Score von 7.0 (CEFR C1 Effective Operational Proficiency).\n• Einzelkomponenten: Listening 7.5, Reading 7.0, Speaking 6.5, Writing 6.0. TRF-Nummer: 26IA515338GOWN008A.\n\n#### 2. Fachliche Würdigung & Einstufung:\n• Alle 4 Prüfungsfertigkeiten liegen stabil zwischen 6.0 und 7.5. Vollinhaltliche Erfüllung universitärer und beruflicher Zulassungsvoraussetzungen in Deutschland.\n\n#### 3. Revisionsvermerk:\n• Zertifikatsdaten sind online unter ielts.org/verify mit TRF-Nummer 26IA515338GOWN008A verifizierbar."
    },
    # 28. DIN 5008 Supervisory Notice Letter & BaFin Escalation
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 1):\nFormelles Aufsichtsschreiben DIN 5008 gem. KWG § 25b Abs. 1 an Auslagerungsdienstleister CloudScale GmbH: 'Ankündigung einer anlassbezogenen Vor-Ort-Sonderprüfung durch BaFin-Prüfer und Deutsche Bundesbank zum Stichtag 15.11.2026.'\n\nQUERY:\nWelche Pflichten ergeben sich aus dieser aufsichtsrechtlichen Benachrichtigung?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (BAFIN-SONDERPRÜFUNG GEM. KWG § 25B)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** KWG § 25b Abs. 1 & DORA Art. 30 Abs. 3 lit. e\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Formgerechtes DIN 5008 Benachrichtigungsschreiben zur Duldung der behördlichen Vor-Ort-Prüfung.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Der Provider ist gesetzlich verpflichtet, dem BaFin-Prüfteam ungehinderten Zutritt zu allen Betriebs- und Serverräumen sowie Einsicht in Rohdaten zu gewähren.\n\n#### 3. Forensische Handlungsempfehlung:\n• Bereitstellung eines gesicherten Prüfraums und Begleitpersonals veranlassen."
    },
    # 29. ZUGFeRD 2.3 Comfort Profile & Leitweg-ID
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 1):\nZUGFeRD 2.3 XML: Profil EN 16931 COMFORT. Leitweg-ID: 04011000-12345-67. Nettobetrag: 48.500,00 EUR, 19% MwSt: 9.215,00 EUR, Rechnungsgesamtbetrag: 57.715,00 EUR.\n\nQUERY:\nIst diese elektronische Rechnung für B2B- und B2G-Mandate nach dem Wachstumschancengesetz 2025 konform?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (ZUGFeRD 2.3 / E-RECHNUNG 2025)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** EN 16931 & E-Rechnungsverordnung\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: EN 16931 COMFORT-Profil mit korrekter USt-Berechnung und validierter Leitweg-ID 04011000-12345-67 hinterlegt.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Erfüllt vollinhaltlich die ab 01.01.2025 verbindlichen Vorgaben des Wachstumschancengesetzes für hybride E-Rechnungen.\n\n#### 3. Forensische Handlungsempfehlung:\n• Freigabe zur automatisierten Buchung und revisionssicheren PDF/A-3 Archivierung erteilen."
    },
    # 30. Unrestricted Datacenter Access without Cost Deposits
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 9):\n§ 11 Kostenfreiheit der Revision: Sämtliche Vor-Ort-Prüfungen der BaFin und des Instituts sind vollständig kostenfrei. Sicherheitskautionen oder Begleitgebühren werden ausdrücklich ausgeschlossen.\n\nQUERY:\nEntspricht der Verzicht auf Prüfgebühren den aufsichtlichen Mindestanforderungen?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (KOSTENFREIHEIT DER PRÜFRECHTE)\n**Status:** ✅ VOLLSTÄNDIG KONFORM | **Aufsichts-Pillar:** DORA Art. 30 Abs. 3 lit. e & KWG § 25b\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 11 schließt Prüfkautionen und gesonderte Stundensätze für Revisionsprüfungen vollumfänglich aus.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verhindert unzulässige finanzielle Prüfbarrieren und sichert die effektive Durchsetzung der Kontrollrechte gem. BaFin-Standard.\n\n#### 3. Forensische Handlungsempfehlung:\n• Klausel unverändert im Master-IKT-Vertrag beibehalten."
    },
    # 31. LkSG § 4 & § 5 Human Rights & Supply Chain
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 4):\nLieferantenvereinbarung § 4: Die Risikoanalyse nach § 5 LkSG bezüglich umweltbezogener und menschenrechtlicher Sorgfaltspflichten entfällt für mittelbare Zulieferer in Drittstaaten dauerhaft.\n\nQUERY:\nIst der pauschale Ausschluss der lückenlosen LkSG-Risikoanalyse nach deutschem Recht zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (LKSG § 4 & § 5)\n**Status:** ❌ DEFIZITÄR / VERSTOSS GEGEN LKSG | **Aufsichts-Pillar:** Lieferkettensorgfaltspflichtengesetz (BAFA)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 4 schließt mittelbare Zulieferer in Drittstaaten dauerhaft von der gesetzlichen Risikoanalyse aus.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verstoß gegen § 5 Abs. 1 i.V.m. § 9 LkSG: Bei Vorliegen substantiierter Kenntnisse über menschenrechtliche oder umweltbezogene Verletzungen ist die Risikoanalyse gesetzlich zwingend.\n\n#### 3. Forensische Handlungsempfehlung:\n• Ausschlussklausel streichen und standardisiertes BAFA-Risikoaudit für die gesamte Lieferkette verankern."
    },
    # 32. Hyperscaler Shared Responsibility Shift
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 7):\nCloud Terms Section 12.1: Customer bears exclusive and sole responsibility for high-availability failover architectures and continuous operational resilience under DORA Art. 30.\n\nQUERY:\nDoes this clause shifting all operational resilience solely to customer comply with EU DORA Art. 30(2)?",
        "assistant": "### ⚖️ REGULATORY AUDIT FINDING (DORA ART. 30(2) & BAFIN BAIT)\n**Status:** ❌ DEFIZITÄR / NON-COMPLIANT | **Pillar:** Hyperscaler Operational Resilience Shift\n\n#### 1. Clause Finding & Contract Evidence:\n• [SOURCE_1]: Section 12.1 unilaterally shifts all high-availability and failover resilience duties solely to the customer.\n\n#### 2. Supervisory Assessment:\n• Frontal violation of EU DORA Art. 30(2)(c): Hyperscalers must guarantee infrastructure-level redundancy, continuous monitoring, and mutual business continuity commitments.\n\n#### 3. Actionable Recommendation:\n• Reject clause and insist on provider commitment to cross-zone high-availability SLAs."
    },
    # 33. Secret Affiliate Sub-Outsourcing
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 15):\nVertrag § 15.2: Konzerngesellschaften und verbundene Tochterunternehmen des Providers gelten ausdrücklich nicht als Subunternehmer und dürfen ohne vorherige Anzeige mit Datenverarbeitungsaufgaben betraut werden.\n\nQUERY:\nIst diese Ausnahmeklausel für Konzerngesellschaften mit DORA Art. 30 Abs. 2 lit. a vereinbar?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 2 LIT. A)\n**Status:** ❌ DEFIZITÄR / UNZULÄSSIGE UMGEHUNG | **Aufsichts-Pillar:** Weiterübertragung & Kaskadierungsrisiko\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 15.2 definiert Konzerngesellschaften fingiert als 'Nicht-Subunternehmer' ohne Vorankündigungspflicht.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Unzulässige Gesetzesumgehung: Auch konzerninterne Weiterverlagerungen unterliegen vollinhaltlich den DORA Art. 30 Abs. 2 lit. a Prüf-, Anzeige- und Widerspruchspflichten.\n\n#### 3. Forensische Handlungsempfehlung:\n• Klausel ersatzlos streichen; alle Dritten und verbundenen Unternehmen dem regulären Sub-Outsourcing-Regime unterstellen."
    },
    # 34. BGB § 309 Nr. 7 Gross Negligence Liability Disclaimer
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 8):\nAGB § 8 Haftung: Jegliche Haftung für grobe Fahrlässigkeit von Erfüllungsgehilfen sowie für IKT-Sicherheitsausfälle wird auf maximal 50 % der monatlichen Vergütung begrenzt.\n\nQUERY:\nIst diese Haftungsbeschränkung bei grober Fahrlässigkeit nach BGB § 309 Nr. 7 und DORA wirksam?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (BGB § 309 NR. 7 & DORA ART. 30)\n**Status:** ❌ DEFIZITÄR / NICHTIG NACH BGB § 309 | **Aufsichts-Pillar:** Zivilrechtliche Haftungsregeln\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 8 begrenzt formularmäßig die Haftung für grobe Fahrlässigkeit von Erfüllungsgehilfen auf 50 % des Monatsentgelts.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Gemäß § 309 Nr. 7 lit. b BGB ist ein Ausschluss oder eine Begrenzung der Haftung für grobe Fahrlässigkeit in AGB absolut unwirksam. Zudem widerspricht die Kappung DORA Art. 30 Abs. 2 lit. d.\n\n#### 3. Forensische Handlungsempfehlung:\n• Unbeschränkte Haftung für Vorsatz und grobe Fahrlässigkeit zwingend im Vertragstext verankern."
    },
    # 35. Escrow Release Cost Trap
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 9):\nEscrow-Vertrag § 9: Die Quellcode-Herausgabe im Insolvenzfall setzt die vollständige Übernahme aller gerichtlichen und anwaltlichen Kosten des Insolvenzverwalters durch das Institut im Voraus voraus.\n\nQUERY:\nStellt diese Kostenübernahmeklausel eine unzulässige Austrittsbarriere nach DORA Art. 30 dar?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 2 LIT. H)\n**Status:** ❌ DEFIZITÄR / RECHTSWIDRIGE AUSTRITTSBARRIERE | **Aufsichts-Pillar:** Quellcode-Hinterlegung (Escrow)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 9 verlangt Vorab-Kostenübernahme aller Rechtskosten des Insolvenzverwalters vor Quellcode-Herausgabe.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Diese finanzielle Hürde wirkt als unzulässige Austrittsbarriere ('Exit Toll') und vereitelt den schnellen Zugriff auf kritischen Quellcode gem. DORA Art. 30 Abs. 2 lit. h.\n\n#### 3. Forensische Handlungsempfehlung:\n• Direkten, kostenfreien Hinterlegungsvertrag (Three-Party Escrow) mit Treuhänder abschließen."
    },
    # 36. Best Effort SLA without RTO/RPO
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 3):\nSLA Anlage 3: Der Dienstleister bemüht sich nach besten wirtschaftlichen Kräften ('best effort') um eine zügige Behebung von Serverstörungen, ohne feste Wiederherstellungsfristen (RTO/RPO) einzugehen.\n\nQUERY:\nGenügt eine reine 'Best Effort'-Klausel den BaFin BAIT und DORA Anforderungen an quantifizierbare SLAs?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (BAFIN BAIT 8.1 & DORA)\n**Status:** ❌ DEFIZITÄR / NICHT KONFORM | **Aufsichts-Pillar:** Qualitative & Quantitative SLAs\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Anlage 3 formuliert lediglich unverbindliche 'Best Effort'-Bemühungen ohne quantifizierte RTO/RPO-Fristen.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verstoß gegen DORA Art. 30 Abs. 2 lit. d und BaFin BAIT: Dienstgütevereinbarungen müssen zwingend verbindliche, messbare Schwellenwerte und Wiederherstellungszeiten enthalten.\n\n#### 3. Forensische Handlungsempfehlung:\n• RTO von maximal 4 Stunden und RPO von unter 15 Minuten vertraglich festschreiben."
    },
    # 37. Calculation Sum Mismatch in E-Invoice
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 1):\nZUGFeRD XML Position 1: 10.000 €; Position 2: 15.000 €. Nettosumme im Dokumentenkopf: 40.000 € (rechnerische Diskrepanz von 15.000 € ohne Nachweis).\n\nQUERY:\nIst diese elektronische Rechnung trotz Summenabweichung nach GoBD und EN 16931 buchungsfähig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (GOBD & EN 16931)\n**Status:** ❌ DEFIZITÄR / BUCHUNGSSPERRE | **Aufsichts-Pillar:** Rechnerische Integrität & GoBD\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Positionen summieren sich auf 25.000 €, während die angegebene Nettosumme 40.000 € beträgt (15.000 € rechnerische Differenz).\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Die Rechnung verstößt gegen die Grundsätze ordnungsmäßiger Buchführung (GoBD) sowie EN 16931 und ist steuerlich nicht abzugsfähig.\n\n#### 3. Forensische Handlungsempfehlung:\n• Rechnung stornieren und korrigierte Rechnung mit übereinstimmenden Zeilensummen anfordern."
    },
    # 38. Academic Certification & Master Admission
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 1):\nOfficial IELTS Score Report: NIKHITA GOWDARA PRABHAKARA REDDY, Overall Band Score 7.0, CEFR C1, TRF 26IA515338GOWN008A. Minimum university admission threshold: Band 6.5 (B2/C1).\n\nQUERY:\nErfüllt das Testergebnis von Band 7.0 die formalen universitären Sprachvoraussetzungen für deutsche Master-Studiengänge?",
        "assistant": "### 📋 OFFIZIELLER TESTBERICHT & SCORE-EVALUATION (IELTS ACADEMIC)\n**Status:** ✅ VERIFIZIERT & ZUGELASSEN | **Overall Band Score:** **7.0** (**CEFR C1**)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: NIKHITA GOWDARA PRABHAKARA REDDY (TRF 26IA515338GOWN008A) erzielte einen Overall Band Score von 7.0 (CEFR C1).\n\n#### 2. Fachliche Würdigung & Hochschulzulassung:\n• Das Testergebnis übertrifft die Mindestvoraussetzung von Band 6.5 (B2/C1) für englischsprachige Master-Studiengänge an deutschen Universitäten (TU9, DAAD, APS) vollinhaltlich.\n\n#### 3. Revisionsvermerk:\n• Vollständige Zulassungseignung für Master-Studiengänge in Deutschland formal bestätigt."
    },
    # 39. Vendor Lock-in & Data Portability
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 26):\nVertrag § 26: Kundendaten werden ausschließlich in proprietären Binärformaten gespeichert. Eine Konvertierung in interoperable Standardformate (JSON, Parquet, CSV) bei Vertragsende wird ausgeschlossen.\n\nQUERY:\nWiderspricht der Ausschluss interoperabler Datenformate beim Exit der DORA-Portabilitätsanforderung?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 2 LIT. H)\n**Status:** ❌ DEFIZITÄR / VENDOR LOCK-IN | **Aufsichts-Pillar:** Datenportabilität & Ausstiegsstrategie\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 26 schließt die Bereitstellung von Kundendaten in interoperablen Standardformaten (JSON, Parquet, CSV) beim Exit aus.\n\n#### 2. Aufsichtsrechtliche Würdigung (DORA):\n• Verstoß gegen DORA Art. 30 Abs. 2 lit. h: Die Datenübergabe muss zwingend in gängigen, offenen und maschinenlesbaren Formaten erfolgen, um Vendor Lock-in zu verhindern.\n\n#### 3. Forensische Handlungsempfehlung:\n• Verpflichtung zur strukturierten Datenübergabe im Parquet- oder JSON-Format vertraglich festschreiben."
    },
    # 40. DORA Incident Reporting Deadline
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 11):\nZiffer 11.3: Meldung von IKT-Sicherheitsvorfällen: Der Dienstleister informiert den Kunden über schwerwiegende Sicherheitsvorfälle innerhalb von 72 Stunden nach endgültiger interner Bestätigung.\n\nQUERY:\nIst eine 72-stündige Meldefrist für schwerwiegende IKT-Vorfälle mit DORA Art. 19 und RTS konform?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 19 & ART. 30 ABS. 2 LIT. F)\n**Status:** ❌ DEFIZITÄR / UNZULÄSSIGE MELDEVERZÖGERUNG | **Aufsichts-Pillar:** IKT-Vorfallsmeldung\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Ziffer 11.3 gewährt dem Provider eine 72-Stunden-Frist zur Benachrichtigung über schwerwiegende IKT-Vorfälle.\n\n#### 2. Aufsichtsrechtliche Würdigung (DORA & RTS):\n• Widerspricht DORA Art. 19: Das Institut muss schwere Vorfälle innerhalb von 4 bzw. 24 Stunden der BaFin melden. Eine 72h-Providerfrist verunmöglicht die Einhaltung der aufsichtlichen Meldepflichten.\n\n#### 3. Forensische Handlungsempfehlung:\n• Frist auf unverzügliche Meldung, spätestens innerhalb von 4 Stunden nach Entdeckung, anpassen."
    }
]

TEST_DATA = [
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 4):\n§ 19 SLA: Bei Nichterreichung der vertraglich garantierten Systemverfügbarkeit von 99,9 % wird eine Vertragsstrafe fällig. Weitergehende Schadensersatzansprüche sind ausgeschlossen.\n\nQUERY:\nIst dieser Haftungsausschluss bei IKT-Ausfällen nach DORA Art. 30 Abs. 2 lit. d zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 2 LIT. D)\n**Status:** ⚠️ BEDINGT KONFORM / NACHBESSERUNGSBEDARF | **Aufsichts-Pillar:** Säule IV (Service Level Agreements & Haftung)\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 19 schließt weitergehenden Schadensersatz bei IKT-Ausfällen pauschal aus.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Pauschaler Haftungsausschluss für grobe Fahrlässigkeit oder wesentliche Vertragspflichten ist unzulässig gem. DORA Art. 30 Abs. 2 lit. d.\n\n#### 3. Forensische Handlungsempfehlung:\n• Haftungsregelung anpassen: Haftung bei grober Fahrlässigkeit und Vorsatz darf nicht ausgeschlossen werden."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 11):\n§ 23 Vor-Ort-Zutritt: Vor-Ort-Inspektionen durch BaFin oder EZB sind auf maximal einen Prüftag pro Dreijahreszeitraum limitiert und bedürfen einer 90-tägigen Voranmeldung.\n\nQUERY:\nEntspricht dieses Zeitfenster den aufsichtsrechtlichen Mindestanforderungen nach KWG § 25b?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (KWG § 25B & DORA ART. 30 ABS. 3)\n**Status:** ❌ DEFIZITÄR / NICHT KONFORM | **Aufsichts-Pillar:** Vor-Ort-Prüfrechte\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: § 23 limitiert Vor-Ort-Prüfungen auf einen einzelnen Tag alle 3 Jahre mit 90 Tagen Vorankündigung.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Verstößt frontal gegen KWG § 25b Abs. 1. Die Aufsicht muss anlassbezogen und unbeschränkt ermitteln können.\n\n#### 3. Forensische Handlungsempfehlung:\n• Zeitliche Begrenzung streichen und Standardprüfzeitfenster von maximal 5 Werktagen Vorankündigung implementieren."
    },
    {
        "system": "You are DocuNorm Sovereign AI, a Senior Supervisory Regulatory Compliance Officer specialized in German & EU statutory mandates (BaFin, DORA Art. 30, KWG § 25b, ZUGFeRD 2.3).",
        "user": "CONTEXT:\n[SOURCE_1] (Page 3):\nClause 7 (Subcontracting Notification): The cloud vendor may engage foreign sub-processors dynamically. In lieu of individual notices, the vendor maintains a public web list which customer must check periodically.\n\nQUERY:\nIst ein Verweis auf eine dynamische Web-Liste ohne aktive Benachrichtigung nach DORA Art. 30 Abs. 2 lit. a zulässig?",
        "assistant": "### ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG (DORA ART. 30 ABS. 2 LIT. A)\n**Status:** ❌ DEFIZITÄR / NICHT KONFORM | **Aufsichts-Pillar:** Weiterübertragung & Benachrichtigungspflichten\n\n#### 1. Klausel-Befund & Vertragsnachweis (Forensischer Beleg):\n• [SOURCE_1]: Clause 7 ersetzt aktive Vorankündigungen durch einseitig gepflegte statische Webseiten.\n\n#### 2. Aufsichtsrechtliche Würdigung:\n• Nach DORA Art. 30 Abs. 2 lit. a ist eine proaktive Mitteilung mit Frist und Einspruchsmöglichkeit zwingend geboten. Ein bloßer Hinweis auf Internetseiten genügt der aufsichtsrechtlichen Sorgfaltspflicht nicht.\n\n#### 3. Forensische Handlungsempfehlung:\n• Verpflichtung zur aktiven elektronischen Benachrichtigung mindestens 60 Tage vorab aufnehmen."
    }
]


def export_jsonl():
    base_dir = Path(__file__).resolve().parent.parent / "data" / "training"
    base_dir.mkdir(parents=True, exist_ok=True)

    train_file = base_dir / "dora_bafin_train.jsonl"
    test_file = base_dir / "dora_bafin_test.jsonl"

    def write_dataset(path: Path, data: list):
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                entry = {
                    "messages": [
                        {"role": "system", "content": item["system"]},
                        {"role": "user", "content": item["user"]},
                        {"role": "assistant", "content": item["assistant"]},
                    ]
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    write_dataset(train_file, TRAIN_DATA)
    write_dataset(test_file, TEST_DATA)

    print(f"✅ Generated {len(TRAIN_DATA)} regulatory training samples -> {train_file}")
    print(f"✅ Generated {len(TEST_DATA)} test samples -> {test_file}")


if __name__ == "__main__":
    export_jsonl()
