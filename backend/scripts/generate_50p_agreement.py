#!/usr/bin/env python3
"""
DocuNorm Sovereign AI - Institutional Banking Agreement Generator (Day 14 Capstone)
Generates an authentic 50-page Master ICT Services and Cloud Outsourcing Agreement
between Deutsche Bank AG / Commerzbank AG and Hyperscaler Cloud Provider.
Strictly drafted under German Law, BaFin RS 10/2018 (BAIT), KWG § 25b, and EU DORA.
"""
import sys
from pathlib import Path
import fitz

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "Deutsche_Bank_Master_Cloud_Agreement_50P.pdf"

SECTIONS = [
    # Part I: Preamble & Framework (Pages 1-5)
    (
        "TEIL I: PRÄAMBEL & REGULATORISCHE GRUNDLAGEN",
        "§ 1 Gegenstand der Vereinbarung und Vertragsstruktur",
        "Die Deutsche Bank AG (nachfolgend 'Institut' oder 'Auftraggeber') beauftragt die CloudScale Systems Europe SE "
        "(nachfolgend 'Dienstleister' oder 'Auftragnehmer') mit der Bereitstellung hochverfügbarer Kernbank-Cloud-Infrastrukturen "
        "für den europäischen Zahlungsverkehr, Wertpapierhandelsabwicklung und regulatorische Meldewesenprozesse. "
        "Diese Rahmenvereinbarung regelt die Erbringung von Informationstechnologie- und Cloud-Dienstleistungen unter strikter "
        "Beachtung der Verordnung (EU) 2022/2554 (DORA), des Kreditwesengesetzes (KWG § 25b), der BaFin-Rundschreiben zur "
        "bankaufsichtlichen Informationstechnologie (BAIT 8.1) sowie der Leitlinien der Europäischen Bankenaufsichtsbehörde (EBA/GL/2019/02)."
    ),
    (
        "TEIL I: PRÄAMBEL & REGULATORISCHE GRUNDLAGEN",
        "§ 2 Einstufung als kritische und wichtige Funktion (DORA Art. 30 Abs. 2)",
        "Die Vertragsparteien stellen einvernehmlich fest, dass die vereinbarten IKT-Dienste Kernfunktionen des Zahlungsverkehrs "
        "und der Liquiditätssteuerung der Deutschen Bank AG unterstützen und somit vollumfänglich als kritische oder wichtige Funktion "
        "gemäß DORA Art. 3 Nr. 22 und KWG § 25b Abs. 1 einzustufen sind. Jede Änderung dieser Einstufung bedarf der vorherigen "
        "Zustimmung des Risikoausschusses des Aufsichtsrats des Instituts und einer unverzüglichen Anzeige an die Bundesanstalt "
        "für Finanzdienstleistungsaufsicht (BaFin) sowie die Europäische Zentralbank (EZB)."
    ),
    (
        "TEIL I: PRÄAMBEL & REGULATORISCHE GRUNDLAGEN",
        "§ 3 Rangfolge der Vertragsdokumente & Vorrang zwingenden Bankaufsichtsrechts",
        "Im Falle von Widersprüchen gilt folgende strikte Rangfolge: (1) Die zwingenden Bestimmungen dieser Rahmenvereinbarung zur "
        "Einhaltung von DORA, KWG § 25b und DSGVO; (2) Die Service Level Agreements (SLA-Katalog A); (3) Die Informationssicherheitsrichtlinie "
        "(Anlage B); (4) Allgemeine Geschäftsbedingungen des Dienstleisters werden hiermit ausdrücklich abbedungen und entfalten "
        "keinerlei Rechtswirkung zwischen den Parteien (§ 305 ff. BGB)."
    ),
    (
        "TEIL I: PRÄAMBEL & REGULATORISCHE GRUNDLAGEN",
        "§ 4 Begriffsbestimmungen & Normenverweise",
        "Für diese Vereinbarung gelten die Definitionen gemäß DORA Art. 3 sowie BaFin BAIT: 'IKT-Drittdienstleister' bezeichnet jedes "
        "Unternehmen, das digitale Dienste erbringt; 'Schwerwiegender IKT-Vorfall' bezeichnet ein Ereignis mit erheblichen Auswirkungen "
        "auf die Netz- und Informationssysteme; 'Wiederherstellungszeit (RTO)' bezeichnet den maximal tolerierten Zeitraum bis zur Wiederaufnahme; "
        "'Wiederherstellungspunkt (RPO)' bezeichnet den maximal tolerierten Datenverlustzeitraum."
    ),
    (
        "TEIL I: PRÄAMBEL & REGULATORISCHE GRUNDLAGEN",
        "§ 5 Vertragslaufzeit & Ordentliche Kündigungsregelung",
        "Diese Vereinbarung tritt mit Unterzeichnung in Kraft und wird für eine feste Grundlaufzeit von drei (3) Jahren geschlossen. "
        "Jede Partei kann diesen Vertrag mit einer ordentlichen Kündigungsfrist von mindestens sechzig (60) Tagen zum Quartalsende kündigen. "
        "Das gesetzliche und aufsichtsrechtliche Recht zur außerordentlichen Kündigung aus wichtigem Grund (§ 314 BGB, DORA Art. 28 Abs. 7) "
        "bleibt hiervon unberührt."
    ),

    # Part II: Service Level Agreements & Availability (Pages 6-10)
    (
        "TEIL II: SERVICE LEVEL AGREEMENTS (SLA) & VERFÜGBARKEIT",
        "§ 6 Quantitative Dienstgüte & Mindestverfügbarkeit (SLA-Katalog A)",
        "Der Auftragnehmer garantiert für die bereitgestellten Tier-3 Cloud-Infrastrukturen eine jährliche Mindestverfügbarkeit von 99,95 % "
        "im Jahresmittel (8.760 Jahresstunden). Die maximal tolerierte ungeplante Ausfallzeit beträgt exakt 4,38 Stunden pro Kalenderjahr. "
        "Die Messung erfolgt kontinuierlich und transparent über institutseigene Überwachungsschnittstellen. Wartungsfenster dürfen maximal "
        "vier (4) Stunden pro Kalendermonat betragen und sind mindestens zehn (10) Werktage im Voraus schriftlich abzustimmen."
    ),
    (
        "TEIL II: SERVICE LEVEL AGREEMENTS (SLA) & VERFÜGBARKEIT",
        "§ 7 Wiederherstellungszeiten: RTO und RPO Schwellenwerte",
        "Gemäß BaFin BAIT 8.1 und DORA Art. 11 garantiert der Auftragnehmer für alle Kernbankkomponenten eine Wiederherstellungszeit "
        "(Recovery Time Objective - RTO) von maximal zwei (2) Stunden sowie einen maximalen Datenverlustpunkt (Recovery Point Objective - RPO) "
        "von null (0) Minuten (Synchrone Spiegelung). Bei Überschreitung dieser Schwellenwerte ist das Institut berechtigt, unverzüglich "
        "den automatisierten Notfallbetrieb über sekundäre Verfügbarkeitszonen auszulösen."
    ),
    (
        "TEIL II: SERVICE LEVEL AGREEMENTS (SLA) & VERFÜGBARKEIT",
        "§ 8 Pönalenmatrix & Gesetzliche Vertragsstrafendeckelung (BGB § 339)",
        "Für jede angefangene Stunde ungeplanter Überschreitung der tolerierten Ausfallzeit zahlt der Dienstleister eine Vertragsstrafe "
        "in Höhe von 0,2 % des jährlichen Gesamtauftragswerts, höchstens jedoch fünf Prozent (5,0 %) des jährlichen Auftragsvolumens. "
        "Erreicht der Gesamtausfall innerhalb eines Kalenderjahres mehr als 87,6 Stunden (Verfügbarkeit < 99,0 %), greift das gesetzliche "
        "Sonderkündigungsrecht gem. DORA Art. 28 Abs. 7 lit. a ohne Einhaltung einer Kündigungsfrist."
    ),
    (
        "TEIL II: SERVICE LEVEL AGREEMENTS (SLA) & VERFÜGBARKEIT",
        "§ 9 Echtzeit-Monitoring & Automatisierte SLA-Reporting-Schnittstellen",
        "Der Dienstleister stellt dem Institut eine gesicherte REST-API und ein dediziertes Dashboard zur Verfügung, über das die "
        "Verfügbarkeitsmetriken, Latenzen (P95 < 25 ms, P99 < 50 ms) und Fehlerraten in Echtzeit abrufbar sind. Monatliche Prüfberichte "
        "sind dem Informationssicherheitsbeauftragten (CISO) des Instituts unaufgefordert bis zum 3. Werktag des Folgemonats zuzustellen."
    ),
    (
        "TEIL II: SERVICE LEVEL AGREEMENTS (SLA) & VERFÜGBARKEIT",
        "§ 10 Kapazitätsmanagement & Skalierungsgarantien",
        "Der Auftragnehmer sichert ausreichende Rechen-, Netzwerk- und Speicherkapazitäten zu, um Lastspitzen im Zahlungsverkehr zum "
        "Monatsultimo (mindestens das Dreifache der durchschnittlichen Transaktionslast) ohne Latenzerhöhung oder Dienstunterbrechung zu verarbeiten. "
        "Kapazitätsengpässe berechtigen das Institut zur Kürzung der monatlichen Vergütung um 15 %."
    ),

    # Part III: Data Sovereignty, Cloud Locations & Encryption (Pages 11-15)
    (
        "TEIL III: DATENSOUVERÄNITÄT, SPEICHERORTE & KRYPTOGRAPHIE",
        "§ 11 Primäre Datenresidenz & Ausschluss von Drittstaatentransfers",
        "Sämtliche Daten des Instituts, einschließlich aller Primärdatenbanken, Replikate, Metadaten, Syslogs und Backups, werden "
        "ausschließlich in ISO/IEC 27001 zertifizierten Rechenzentren innerhalb des Europäischen Wirtschaftsraums (EWR) an den "
        "Standorten Frankfurt am Main (Deutschland) und Dublin (Irland) gespeichert und verarbeitet. Eine Übertragung in Drittstaaten "
        "(insbesondere in die USA oder nach Großbritannien) ist ohne vorherige ausdrückliche schriftliche Genehmigung der Deutschen Bank AG "
        "ausgeschlossen (DORA Art. 30 Abs. 2 lit. c; DSGVO Art. 44 ff.)."
    ),
    (
        "TEIL III: DATENSOUVERÄNITÄT, SPEICHERORTE & KRYPTOGRAPHIE",
        "§ 12 US CLOUD Act Immunität & Hold-Your-Own-Key (HYOK) Mandat",
        "Zur Abwehr extraterritorialer Zugriffsrisiken (US CLOUD Act, FISA Section 702) verbleibt die alleinige kryptographische "
        "Schlüsselgewalt beim Institut ('Hold Your Own Key' - HYOK). Der Dienstleister verfügt zu keinem Zeitpunkt über Klartext-Schlüssel. "
        "Alle Daten im Ruhezustand (Data at Rest) werden mittels AES-256 GCM verschlüsselt; Daten im Transit werden mittels TLS 1.3 "
        "mit Perfect Forward Secrecy und striktem mTLS gesichert."
    ),
    (
        "TEIL III: DATENSOUVERÄNITÄT, SPEICHERORTE & KRYPTOGRAPHIE",
        "§ 13 Kryptographische Schlüssellängen gem. BSI TR-02102",
        "Der Dienstleister verpflichtet sich zur lückenlosen Einhaltung der technischen Richtlinie BSI TR-02102. Die Verwendung veralteter "
        "Verfahren (insbesondere RSA < 3072 Bit, ECC < 256 Bit, MD5, SHA-1 oder DES/3DES) ist ausdrücklich untersagt. Mindestens einmal "
        "jährlich wird eine Krypto-Agilitätsprüfung durchgeführt, um Post-Quantum-Sicherheitsstandards schrittweise zu etablieren."
    ),
    (
        "TEIL III: DATENSOUVERÄNITÄT, SPEICHERORTE & KRYPTOGRAPHIE",
        "§ 14 Mandantentrennung & Kryptographische Isolation",
        "Die Infrastruktur des Instituts wird strikt logisch und netzwerkseitig isoliert (Dedicated Virtual Private Cloud, Bare-Metal Enclaves). "
        "Ein geteilter Speicherzugriff mit Drittkunden ist technisch ausgeschlossen. Microsegmentierung und Zero-Trust-Architekturen sind "
        "standardmäßig implementiert und werden kontinuierlich auditiert."
    ),
    (
        "TEIL III: DATENSOUVERÄNITÄT, SPEICHERORTE & KRYPTOGRAPHIE",
        "§ 15 Datenlöschung & Revisionssichere Vernichtung (DIN 66399)",
        "Nach Beendigung dieser Vereinbarung oder auf gesondertes Verlangen des Instituts werden alle Bestände innerhalb von vierzehn (14) "
        "Kalendertagen unwiderruflich nach Sicherheitsstufe 7 der DIN 66399 überschrieben und gelöscht. Der Dienstleister übergibt der "
        "Deutschen Bank AG ein notariell beglaubigtes Löschzertifikat."
    ),

    # Part IV: Supervisory Audit & Inspection Rights (Pages 16-20)
    (
        "TEIL IV: AUFSICHTLICHE PRÜF- & KONTROLLRECHTE (KWG § 25b)",
        "§ 16 Uneingeschränkte Vor-Ort-Prüfrechte (DORA Art. 30 Abs. 3 lit. e)",
        "Der Dienstleister gewährt dem Institut, dessen beauftragten Wirtschaftsprüfern sowie den zuständigen Aufsichtsbehörden "
        "(Bundesanstalt für Finanzdienstleistungsaufsicht - BaFin, Deutsche Bundesbank, Europäische Zentralbank - EZB) uneingeschränkten, "
        "vollständigen und anlassunabhängigen physischen Zugang zu allen Geschäftsräumen, Rechenzentren, Systemen, Netzwerken und "
        "relevanten Mitarbeitern während der üblichen Geschäftszeiten sowie im Krisenfall 24/7 ohne zeitliche Beschränkung."
    ),
    (
        "TEIL IV: AUFSICHTLICHE PRÜF- & KONTROLLRECHTE (KWG § 25b)",
        "§ 17 Verbot von Prüfkautionen & Kostenbarrieren (§ 307 BGB)",
        "Aufsichtsrechtliche und interne Inspektionen erfolgen kostenfrei. Die Erhebung von Vorab-Kautionsforderungen, Prüfpauschalen "
        "oder sonstigen finanziellen Erschwernissen für gesetzlich vorgeschriebene Kontrollen ist rechtswidrig und unwirksam gem. § 307 BGB. "
        "Der Dienstleister stellt sachkundiges Begleitpersonal und Prüfräume ohne gesonderte Vergütung bereit."
    ),
    (
        "TEIL IV: AUFSICHTLICHE PRÜF- & KONTROLLRECHTE (KWG § 25b)",
        "§ 18 Gemeinschaftliche Prüfungen (Pooled Audits) gem. EBA Guidelines",
        "Das Institut ist berechtigt, Vor-Ort-Prüfungen gemeinsam mit anderen beaufsichtigten Finanzinstituten (Pooled Audits) durchzuführen "
        "oder durch unabhängige Dritte wahrnehmen zu lassen, um Ressourcen zu schonen und betriebliche Störungen beim Dienstleister zu minimieren. "
        "Der Dienstleister verpflichtet sich zur vollen Kooperation mit dem gewählten Lead-Auditor."
    ),
    (
        "TEIL IV: AUFSICHTLICHE PRÜF- & KONTROLLRECHTE (KWG § 25b)",
        "§ 19 Bereitstellung von Revisionsnachweisen & CISO-Interviews",
        "Der Dienstleister stellt auf Anforderung unverzüglich (spätestens innerhalb von 48 Stunden) aktuelle SOC-1/SOC-2 Typ II Berichte, "
        "C5-Testate des BSI, ISO-27001-Zertifikate sowie ungekürzte Berichte über interne und externe Schwachstellen-Scans bereit. "
        "Der CISO des Dienstleisters steht dem Institut für formelle Revisionsgespräche quartalsweise zur Verfügung."
    ),
    (
        "TEIL IV: AUFSICHTLICHE PRÜF- & KONTROLLRECHTE (KWG § 25b)",
        "§ 20 Threat-Led Penetration Testing (TLPT) gem. DORA Art. 26 & 27",
        "Der Dienstleister verpflichtet sich zur aktiven und vollumfänglichen Teilnahme an den gesetzlich vorgeschriebenen, "
        "bedrohungsorientierten Penetrationstests (TLPT) des Instituts. Alle Systeme und Schnittstellen werden für die Durchführung "
        "von TIBER-EU/TIBER-DE Tests bereitgestellt."
    ),

    # Part V: Subcontracting & Cascading Supply Chain (Pages 21-25)
    (
        "TEIL V: UNTERAUFTRAGSVERGABEN & SUB-DIENSTLEISTER",
        "§ 21 Vorab-Zustimmungsvorbehalt & Schriftformgebot (DORA Art. 30 Abs. 2 lit. a)",
        "Die Einschaltung oder der Wechsel von Unterauftragnehmern für wesentliche oder kritische Teilleistungen ist nur mit vorheriger "
        "ausdrücklicher schriftlicher Zustimmung der Deutschen Bank AG zulässig. Der Dienstleister teilt geplante Änderungen mindestens "
        "sechzig (60) Tage im Voraus unter Vorlage einer vollumfänglichen Risikoanalyse schriftlich mit."
    ),
    (
        "TEIL V: UNTERAUFTRAGSVERGABEN & SUB-DIENSTLEISTER",
        "§ 22 Qualifiziertes Widerspruchsrecht & Sonderkündigung",
        "Das Institut hat das Recht, der beabsichtigten Hinzuziehung oder dem Wechsel eines Subunternehmers innerhalb von dreißig (30) "
        "Tagen nach Zugang der Mitteilung schriftlich zu widersprechen. Kann keine einvernehmliche Lösung gefunden werden, steht dem "
        "Institut ein fristloses Sonderkündigungsrecht zu, ohne dass hierfür Entflechtungskosten oder Ausfallentschädigungen anfallen."
    ),
    (
        "TEIL V: UNTERAUFTRAGSVERGABEN & SUB-DIENSTLEISTER",
        "§ 23 Strikte Haftungsdurchleitung & Einstandspflicht (BGB § 278)",
        "Der Dienstleister haftet für Handlungen, Unterlassungen und Pflichtverletzungen seiner Subdienstleister wie für eigenes Verschulden "
        "(BGB § 278). Ein formularmäßiger Haftungsausschluss für Erfüllungsgehilfen oder Subunternehmer ist unwirksam. Der Dienstleister "
        "überwacht die gesamte Nachunternehmerkette kontinuierlich."
    ),
    (
        "TEIL V: UNTERAUFTRAGSVERGABEN & SUB-DIENSTLEISTER",
        "§ 24 Vertragliche Weiterreichung aller DORA-Pflichten",
        "Der Dienstleister verpflichtet sich, sämtliche aufsichtsrechtlichen Pflichten aus dieser Vereinbarung (insbesondere Prüfrechte, "
        "Informationssicherheit, Vorfallsmeldungen und BCP-Konzepte) vollinhaltlich und wirksam an alle nachgelagerten Subunternehmer "
        "weiterzureichen und dem Institut entsprechende Nachweise vorzulegen."
    ),
    (
        "TEIL V: UNTERAUFTRAGSVERGABEN & SUB-DIENSTLEISTER",
        "§ 25 Verbot verdeckter Konzernauslagerungen",
        "Konzerninterne Auslagerungen an verbundene Unternehmen, Muttergesellschaften oder Tochtergesellschaften (§§ 15 ff. AktG) gelten "
        "aufsichtsrechtlich uneingeschränkt als Subunternehmerbeauftragungen und unterliegen denselben Zustimmungs-, Melde- und Kontrollpflichten."
    ),

    # Part VI: Incident Management & Regulatory Reporting (Pages 26-30)
    (
        "TEIL VI: IKT-VORFALLSMANAGEMENT & BAFIN-MELDEWESEN",
        "§ 26 4-Stunden-Meldefrist für schwerwiegende IKT-Vorfälle (DORA Art. 19)",
        "Der Dienstleister meldet schwerwiegende IKT-Sicherheitsvorfälle oder signifikante Störungen unverzüglich, spätestens jedoch "
        "innerhalb von vier (4) Stunden nach Entdeckung an das Security Operations Center (SOC) der Deutschen Bank AG. Die Meldung "
        "muss eine erste Schadensabschätzung, betroffene Systeme und eingeleitete Gegenmaßnahmen enthalten."
    ),
    (
        "TEIL VI: IKT-VORFALLSMANAGEMENT & BAFIN-MELDEWESEN",
        "§ 27 Bereitstellung von BaFin-Meldedaten (DORA RTS Meldepflichten)",
        "Zur Einhaltung der aufsichtsrechtlichen Meldefristen gegenüber der BaFin und EZB übermittelt der Dienstleister bis spätestens "
        "sechzehn (16) Stunden nach dem Vorfall den detaillierten Zwischenbericht und bis spätestens dreißig (30) Tage den finalen "
        "Untersuchungsbericht inklusive Root-Cause-Analyse (RCA) und forensischer Beweissicherung."
    ),
    (
        "TEIL VI: IKT-VORFALLSMANAGEMENT & BAFIN-MELDEWESEN",
        "§ 28 24/7 Notfallkontakt & Eskalationsmatrix",
        "Die Parteien etablieren eine permanente, redundante 24/7-Eskalationsmatrix. Wesentliche Ansprechpartner auf C-Level-Ebene "
        "müssen innerhalb von fünfzehn (15) Minuten erreichbar sein. Die Kontaktdaten werden quartalsweise verifiziert und aktualisiert."
    ),
    (
        "TEIL VI: IKT-VORFALLSMANAGEMENT & BAFIN-MELDEWESEN",
        "§ 29 Forensische Protokollierung & Aufbewahrungspflichten",
        "Sämtliche sicherheitsrelevanten Systemzugriffe, administrative Aktionen und Netzwerkverbindungen werden manipulationssicher "
        "protokolliert (WORM-Storage) und für mindestens fünf (5) Jahre aufbewahrt, um forensische Untersuchungen der Aufsichtsbehörden "
        "vollumfänglich zu ermöglichen."
    ),
    (
        "TEIL VI: IKT-VORFALLSMANAGEMENT & BAFIN-MELDEWESEN",
        "§ 30 Krisenkommunikation & Reputationsschutz",
        "Öffentliche Erklärungen, Pressemitteilungen oder Kundenbenachrichtigungen über IKT-Sicherheitsvorfälle bedürfen der vorherigen "
        "schriftlichen Freigabe durch die Kommunikations- und Rechtsabteilung der Deutschen Bank AG."
    ),

    # Part VII: Exit Strategy & Transition Assistance (Pages 31-35)
    (
        "TEIL VII: AUSSTIEGSSTRATEGIE & ENTFLECHTUNG (DORA ART. 30 ABS. 2 LIT. E)",
        "§ 31 Verpflichtender Migrationsbeistand von mindestens 90 Tagen",
        "Im Falle einer Beendigung dieser Vereinbarung (gleich aus welchem Rechtsgrund) garantiert der Dienstleister einen kontinuierlichen, "
        "unterbrechungsfreien Migrationsbeistand für einen Zeitraum von mindestens neunzig (90) Kalendertagen, um die nahtlose Übergabe "
        "aller Daten und Anwendungen auf das Institut oder einen benannten Nachfolgedienstleister sicherzustellen."
    ),
    (
        "TEIL VII: AUSSTIEGSSTRATEGIE & ENTFLECHTUNG (DORA ART. 30 ABS. 2 LIT. E)",
        "§ 32 Bereitstellung interoperabler Standardformate (Kein Vendor Lock-in)",
        "Der Dienstleister stellt alle Bestände in offenen, maschinenlesbaren, standardisierten und interoperablen Datenformaten "
        "(Parquet, JSON, CSV, ANSI-SQL Dumps) bereit. Die Verweigerung offener Standards oder die Beschränkung auf proprietäre "
        "Formate ist unzulässig und stellt eine vertragswidrige Austrittsbarriere dar (DORA Art. 30 Abs. 2 lit. h)."
    ),
    (
        "TEIL VII: AUSSTIEGSSTRATEGIE & ENTFLECHTUNG (DORA ART. 30 ABS. 2 LIT. E)",
        "§ 33 Transparente und gedeckelte Ausstiegskosten",
        "Standardmäßige Migrations- und Übergabeleistungen sind durch die vereinbarte laufende Vergütung vollständig abgegolten. "
        "Zusätzliche Unterstützungsleistungen werden nach festen, vorab vereinbarten Tagessätzen abgerechnet und sind auf maximal "
        "zwei Prozent (2,0 %) des jährlichen Auftragswerts absolut gedeckelt. Ungedeckelte Stundensätze ('Exit Tolls') sind ausgeschlossen."
    ),
    (
        "TEIL VII: AUSSTIEGSSTRATEGIE & ENTFLECHTUNG (DORA ART. 30 ABS. 2 LIT. E)",
        "§ 34 Jährliche Aktualisierung des Ausstiegsplans",
        "Der detaillierte Ausstiegs- und Entflechtungsplan (Anlage D) wird mindestens einmal jährlich gemeinsam überprüft und "
        "an veränderte Systemlandschaften angepasst. Das Institut führt regelmäßige theoretische und praktische Entflechtungssimulationen durch."
    ),
    (
        "TEIL VII: AUSSTIEGSSTRATEGIE & ENTFLECHTUNG (DORA ART. 30 ABS. 2 LIT. E)",
        "§ 35 Parallellauf & Notfall-Verlängerungsoption",
        "Das Institut ist berechtigt, den Migrationszeitraum einseitig um bis zu weitere neunzig (90) Tage zu den bisherigen Konditionen "
        "zu verlängern, falls Verzögerungen bei der Übernahme durch den Nachfolgedienstleister auftreten."
    ),

    # Part VIII: Source Code Escrow & Intellectual Property (Pages 36-40)
    (
        "TEIL VIII: QUELLCODE-ESCROW & KONTINUITÄT (DORA ART. 30 ABS. 2 LIT. H)",
        "§ 36 Fortlaufende Quellcode-Hinterlegung bei deutschem Treuhänder",
        "Der Dienstleister hinterlegt den vollständigen Quellcode aller bereitgestellten Individual- und Standardsoftware sowie "
        "alle Build-Skripte, Bibliotheken und Dokumentationen quartalsweise bei einem zertifizierten Escrow-Treuhänder in Frankfurt am Main "
        "(Three-Party Escrow Agreement gem. Anlage E)."
    ),
    (
        "TEIL VIII: QUELLCODE-ESCROW & KONTINUITÄT (DORA ART. 30 ABS. 2 LIT. H)",
        "§ 37 Automatisierte Build- und Kompilierungsverifikation",
        "Der Treuhänder führt bei jeder neuen Hinterlegung eine automatisierte Test-Kompilierung (Level 3 Verification) durch, "
        "um nachzuweisen, dass aus dem hinterlegten Quellcode eine lauffähige Softwareversion erzeugt werden kann. Die Kosten "
        "trägt der Dienstleister."
    ),
    (
        "TEIL VIII: QUELLCODE-ESCROW & KONTINUITÄT (DORA ART. 30 ABS. 2 LIT. H)",
        "§ 38 Auslösende Ereignisse (Release Triggers)",
        "Die Herausgabe des Quellcodes an das Institut erfolgt unverzüglich bei: (a) Insolvenz oder Eröffnung eines Sanierungsverfahrens; "
        "(b) Einstellung des Geschäftsbetriebs; (c) Verletzung wesentlicher Support- und Wartungspflichten nach erfolgloser Abmahnung; "
        "(d) Kontrollwechsel (Change of Control) auf einen direkten Konkurrenten des Instituts."
    ),
    (
        "TEIL VIII: QUELLCODE-ESCROW & KONTINUITÄT (DORA ART. 30 ABS. 2 LIT. H)",
        "§ 39 Kostenfreie Quellcode-Freigabe ohne Vorab-Barrieren",
        "Die Freigabe und Übergabe des Quellcodes an das Institut erfolgt kostenfrei. Klauseln, die die Herausgabe an die Begleichung "
        "von Honoraren des Insolvenzverwalters knüpfen, sind unwirksam."
    ),
    (
        "TEIL VIII: QUELLCODE-ESCROW & KONTINUITÄT (DORA ART. 30 ABS. 2 LIT. H)",
        "§ 40 Nutzungs- und Bearbeitungsrechte im Escrow-Fall",
        "Mit Eintritt eines Release Triggers erhält das Institut ein unwiderrufliches, weltweites, nicht-exklusives Recht zur Nutzung, "
        "Weiterentwicklung und Fehlerbehebung des Quellcodes für eigene bankbetriebliche Zwecke."
    ),

    # Part IX: Liability, Sanctions & BGB § 309 Protection (Pages 41-45)
    (
        "TEIL IX: HAFTUNG, VERTRAGSSTRAFEN & ZIVILRECHTSKONFORMITÄT",
        "§ 41 Unbeschränkte Haftung für Vorsatz und grobe Fahrlässigkeit (BGB § 309 Nr. 7)",
        "Die Haftung der Vertragsparteien für Vorsatz, grobe Fahrlässigkeit (BGB § 309 Nr. 7 lit. b), die Verletzung von Leben, Körper "
        "und Gesundheit sowie für Ansprüche nach dem Produkthaftungsgesetz und der Datenschutz-Grundverordnung (DSGVO Art. 82) "
        "ist unbeschränkt und kann vertraglich nicht begrenzt werden."
    ),
    (
        "TEIL IX: HAFTUNG, VERTRAGSSTRAFEN & ZIVILRECHTSKONFORMITÄT",
        "§ 42 Haftung für einfache Fahrlässigkeit & Kardinalpflichten",
        "Für einfache Fahrlässigkeit haften die Parteien nur bei Verletzung wesentlicher Vertragspflichten (Kardinalpflichten). "
        "In diesem Fall ist die Haftung auf den typischerweise vorhersehbaren Schaden begrenzt, mindestens jedoch auf den dreifachen "
        "jährlichen Auftragswert."
    ),
    (
        "TEIL IX: HAFTUNG, VERTRAGSSTRAFEN & ZIVILRECHTSKONFORMITÄT",
        "§ 43 Freistellung bei Datenschutz- und Urheberrechtsverletzungen",
        "Der Dienstleister stellt das Institut von sämtlichen Ansprüchen Dritter sowie behördlichen Bußgeldern frei, die aus schuldhaften "
        "Verletzungen des Datenschutzes oder Rechten an geistigem Eigentum durch den Dienstleister resultieren."
    ),
    (
        "TEIL IX: HAFTUNG, VERTRAGSSTRAFEN & ZIVILRECHTSKONFORMITÄT",
        "§ 44 Verjährungsfristen nach deutschem Recht",
        "Schadensersatzansprüche verjähren nach den gesetzlichen Vorschriften des Bürgerlichen Gesetzbuches (§§ 195, 199 BGB). "
        "Eine formularmäßige Verkürzung der Verjährungsfristen ist unzulässig."
    ),
    (
        "TEIL IX: HAFTUNG, VERTRAGSSTRAFEN & ZIVILRECHTSKONFORMITÄT",
        "§ 45 Versicherungspflichten des Dienstleisters",
        "Der Dienstleister weist das Bestehen einer weltweiten Cyber- und IKT-Haftpflichtversicherung mit einer Mindestdeckungssumme "
        "von 50.000.000 EUR pro Schadensfall durch jährliche Vorlage der Versicherungspolice nach."
    ),

    # Part X: ESG, LkSG, Invoicing & Final Provisions (Pages 46-50)
    (
        "TEIL X: ESG, LKSG, E-RECHNUNG & SCHLUSSBESTIMMUNGEN",
        "§ 46 Einhaltung des Lieferkettensorgfaltspflichtengesetzes (LkSG § 4 & § 5)",
        "Der Dienstleister verpflichtet sich zur Einhaltung aller menschenrechtlichen und umweltbezogenen Sorgfaltspflichten nach dem LkSG. "
        "Er führt jährliche Risikoanalysen in seiner gesamten Lieferkette durch und stellt dem Institut seinen geprüften BAFA-Bericht zur Verfügung."
    ),
    (
        "TEIL X: ESG, LKSG, E-RECHNUNG & SCHLUSSBESTIMMUNGEN",
        "§ 47 Elektronische Rechnungsstellung gem. ZUGFeRD 2.3 / Factur-X (EN 16931)",
        "Sämtliche Abrechnungen erfolgen verbindlich als strukturierte elektronische Rechnung im Profil EN 16931 COMFORT (ZUGFeRD 2.3) "
        "unter Angabe der amtlichen Leitweg-ID des Instituts. Rechnungen in Papier- oder reinem PDF-Format ohne eingebettetes XML sind unzulässig."
    ),
    (
        "TEIL X: ESG, LKSG, E-RECHNUNG & SCHLUSSBESTIMMUNGEN",
        "§ 48 Nachhaltigkeit & Green Data Center Standards (CSRD PUE < 1.25)",
        "Die betriebenen Rechenzentren erfüllen die europäischen Energieeffizienzvorgaben mit einem PUE-Wert von maximal 1,25 und "
        "werden vollständig mit zertifiziertem Grünstrom versorgt. Entsprechende Energieauditberichte werden jährlich übergeben."
    ),
    (
        "TEIL X: ESG, LKSG, E-RECHNUNG & SCHLUSSBESTIMMUNGEN",
        "§ 49 Schriftformklausel & BGB § 311 Nachtragsvereinbarungen",
        "Änderungen und Ergänzungen dieser Vereinbarung bedürfen der Schriftform (§ 126 BGB). Dies gilt auch für die Aufhebung dieses "
        "Schriftformerfordernisses. Regulatorisch veranlasste Klauselanpassungen erfolgen durch gesonderte Nachtragsvereinbarung gem. § 311 BGB."
    ),
    (
        "TEIL X: ESG, LKSG, E-RECHNUNG & SCHLUSSBESTIMMUNGEN",
        "§ 50 Anwendbares Recht, Gerichtsstand & Salvatorische Klausel",
        "Diese Vereinbarung unterliegt ausschließlich dem Recht der Bundesrepublik Deutschland unter Ausschluss des UN-Kaufrechts (CISG). "
        "Ausschließlicher Gerichtsstand für alle Streitigkeiten aus oder im Zusammenhang mit diesem Vertrag ist Frankfurt am Main. "
        "Sollte eine Bestimmung ganz oder teilweise unwirksam sein, bleibt die Wirksamkeit der übrigen Bestimmungen hiervon unberührt."
    ),
]


def generate_50_page_agreement():
    print(f"Creating 50-page Banking Agreement at: {OUTPUT_PATH}")
    doc = fitz.open()

    for idx, (part_title, clause_title, clause_body) in enumerate(SECTIONS, 1):
        page = doc.new_page(width=595, height=842)

        # Header Box
        page.draw_rect(fitz.Rect(40, 35, 555, 90), color=(0.08, 0.15, 0.3), fill=(0.96, 0.97, 1.0))
        page.draw_line(fitz.Point(40, 90), fitz.Point(555, 90), color=(0.85, 0.3, 0.0), width=2.0)

        page.insert_text(fitz.Point(52, 54), "DEUTSCHE BANK AG • MASTER CLOUD SERVICES AGREEMENT (DORA / KWG)", fontsize=10, fontname="hebo", color=(0.06, 0.12, 0.24))
        page.insert_text(fitz.Point(52, 68), f"Vertragsdossier: DB-2026-DORA-9941 • {part_title}", fontsize=8, fontname="hebo", color=(0.15, 0.25, 0.45))
        page.insert_text(fitz.Point(52, 81), "DIN EN ISO/IEC 27001 • BSI C5 Testat • EBA/GL/2019/02 Konformitätsfassung", fontsize=7.5, fontname="helv", color=(0.35, 0.42, 0.52))

        # Page Tracker
        page.insert_text(fitz.Point(430, 54), f"SEITE {idx} VON 50", fontsize=9, fontname="hebo", color=(0.85, 0.3, 0.0))

        # Section Title
        page.insert_text(fitz.Point(45, 120), clause_title, fontsize=12, fontname="hebo", color=(0.08, 0.12, 0.2))
        page.draw_line(fitz.Point(45, 128), fitz.Point(550, 128), color=(0.8, 0.85, 0.9), width=1.0)

        # Body Text Box
        body_rect = fitz.Rect(45, 145, 550, 380)
        page.insert_textbox(body_rect, clause_body, fontsize=10.5, fontname="helv", color=(0.1, 0.15, 0.22))

        # Regulatory Compliance Callout Card
        page.draw_rect(fitz.Rect(45, 410, 550, 520), color=(0.1, 0.55, 0.25), fill=(0.95, 0.99, 0.96))
        page.insert_text(fitz.Point(55, 430), "AUFSICHTSRECHTLICHER PRÜFVERMERK (DORA ART. 30 / BAFIN BAIT)", fontsize=8.5, fontname="hebo", color=(0.1, 0.55, 0.25))
        vermerk = (
            f"Diese Klausel ({clause_title.split(' ')[0]}) wurde vom zentralen Auslagerungsmanagement der Deutschen Bank AG "
            "geprüft und entspricht den aufsichtlichen Mindestanforderungen nach DORA Art. 30 sowie den Rundschreiben der BaFin. "
            "Die forensischen Belegstellen sind im revisionssicheren Informationsregister hinterlegt."
        )
        page.insert_textbox(fitz.Rect(55, 440, 540, 510), vermerk, fontsize=8.5, fontname="helv", color=(0.15, 0.2, 0.25))

        # Technical Architecture Table
        page.draw_rect(fitz.Rect(45, 540, 550, 680), color=(0.8, 0.85, 0.9), fill=(0.98, 0.98, 0.99))
        page.insert_text(fitz.Point(55, 560), "TECHNISCHE PARAMETER & COMPLIANCE-SCHWELLENWERTE", fontsize=9, fontname="hebo", color=(0.08, 0.12, 0.2))
        
        table_rows = [
            ("Verfügbarkeits-SLA (SLA-Katalog A)", "99,95 % jährliches Minimum (max. 4,38 h Ausfall/Jahr)"),
            ("Wiederherstellungsziel (RTO)", "< 2 Stunden (Synchrone Multi-Region Spiegelung)"),
            ("Datenverlustgrenze (RPO)", "0 Minuten (Zero Data Loss Commitment)"),
            ("Verschlüsselungsstandard", "AES-256 GCM (At-Rest) • TLS 1.3 mTLS (In-Transit)"),
            ("Aufsichtliches Prüfungsrecht", "Uneingeschränkt Vor-Ort (BaFin, EZB, Deutsche Bank)"),
        ]

        ty = 580
        for label, val in table_rows:
            page.insert_text(fitz.Point(55, ty), label, fontsize=8, fontname="hebo", color=(0.2, 0.25, 0.35))
            page.insert_text(fitz.Point(230, ty), val, fontsize=8, fontname="helv", color=(0.1, 0.15, 0.2))
            ty += 18

        # Footer
        page.draw_line(fitz.Point(40, 790), fitz.Point(555, 790), color=(0.8, 0.85, 0.9), width=1.0)
        footer_text = f"Deutsche Bank AG • Master Cloud Agreement 2026 • Dokumenten-ID: DB-DORA-50P-CAPSTONE • Seite {idx} von 50"
        page.insert_text(fitz.Point(45, 805), footer_text, fontsize=7.5, fontname="helv", color=(0.5, 0.55, 0.6))
        page.insert_text(fitz.Point(440, 805), "BAFIN REVISIONSFÄHIG", fontsize=7.5, fontname="hebo", color=(0.1, 0.6, 0.3))

    doc.save(str(OUTPUT_PATH))
    doc.close()
    print(f"✅ Generated 50-page Master Agreement! Size: {OUTPUT_PATH.stat().st_size} bytes")


if __name__ == "__main__":
    generate_50_page_agreement()
