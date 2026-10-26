export type Language = "DE" | "EN";

export const translations = {
  DE: {
    // Brand
    brand_sub: "Automatisierte Revisions- & Compliance-Prüfung",
    mandant: "Mandant-01",

    // Navigation in Header
    nav_workbench: "Dual-View Prüfbank",
    nav_auditor: "KI-Auditor (Studio)",
    nav_cockpit: "Vorstands-Cockpit",
    btn_sign_in: "Anmelden",
    btn_logout: "Abmelden",
    btn_certificate: "Prüfbericht",

    // Sidebar
    vault_title: "Dokumenten-Treuhand",
    dora_title: "DORA Art. 30 (BaFin)",
    zugferd_title: "ZUGFeRD / Factur-X",
    lksg_title: "LkSG Lieferkette (BAFA)",
    ledger_title: "Revisions-Protokoll",
    telemetry_title: "SYSTEMSTATUS",
    status_ready: "BETRIEBSBEREIT",
    dsgvo_verified: "GEPRÜFT",

    // Workbench & Canvas
    select_doc_placeholder: "Akte auswählen (Dokument wählen)...",
    no_docs_indexed: "Keine Akten indexiert",
    btn_select_pdf: "PDF LADEN",
    btn_submit_ingest: "REVISION STARTEN",
    empty_canvas_title: "KEIN DOKUMENT GELADEN",
    empty_canvas_desc:
      "Wählen Sie eine bestehende Akte aus der Treuhand oder importieren Sie ein neues PDF zur automatisierten BaFin/DORA Prüfung.",
    btn_load_file: "PDF Akte Laden",
    audit_engine_title: "REVISIONS-INTELLIGENZ",
    audit_ready_title: "Revisions-Assistent Bereit",
    audit_ready_desc:
      "Stellen Sie rechtliche Fragen oder wählen Sie eine BaFin/DORA Schnellprüfung.",
    suggested_checks_title: "STANDARDFRAGEN (BAFIN / DORA):",
    suggested_1: "Sind Ausstiegsfristen nach Art. 30 geregelt?",
    suggested_2: "Wie hoch ist die maximale Verzugsstrafe?",
    suggested_3: "Sind Unterauftragsvergaben genehmigungspflichtig?",
    input_placeholder: "Compliance-Frage eingeben (z.B. 'Welche Verzugsstrafen gelten?')...",
    source_tag_prefix: "Geprüfte Quelle",

    // Landing Page
    landing_badge: "BaFin & DORA Art. 30 Validiert",
    landing_hero_h1_pre: "Deutsche Regulatorik & IKT-Verträge.",
    landing_hero_h1_accent: "Revisionssicher geprüft.",
    landing_hero_sub:
      "Automatisierte Vertragsanalyse nach EU DORA (VO 2022/2554), BDSG § 26 und ZUGFeRD 2.3 / Factur-X. Mit visuellem DIN A4 Belegnachweis und beglaubigtem englischen Revisionsdossier.",
    landing_cta_demo: "Live-Demo Starten (Siemens IKT)",
    landing_cta_auth: "Anmelden / Registrieren",
    landing_cta_workbench: "Direkt zur Prüfbank",
    landing_metric_authority: "Aufsichtsbehörde",
    landing_metric_authority_sub: "DORA Pillar IV Konform",
    landing_metric_privacy: "Datensouveränität",
    landing_metric_privacy_sub: "Node Frankfurt a. M.",
    landing_metric_invoice: "E-Rechnungspflicht",
    landing_metric_invoice_sub: "EN 16931 / Factur-X",
    landing_metric_security: "Sicherheitsstufe",
    landing_metric_security_sub: "Schutzklasse 3 Validiert",
    landing_modules_tag: "Enterprise Module",
    landing_modules_title: "Vollständige Prüfung von IKT-Drittparteirisiken",
    landing_mod1_title: "DORA Art. 30 Prüfung",
    landing_mod1_desc:
      "Prüfung wesentlicher Vertragsklauseln: 60 Tage Kündigungsfrist, 90 Tage Migrationszusicherung und 30 Tage Widerspruchsrecht bei Unterauftragnehmern.",
    landing_mod2_title: "ZUGFeRD 2.3 & Factur-X",
    landing_mod2_desc:
      "Validierung hybrider PDF/XML Rechnungsdaten gem. EN 16931 und dem Wachstumschancengesetz. Automatische Leitweg-ID und Umsatzsteuer-Prüfung.",
    landing_mod3_title: "Beglaubigtes englisches Dossier",
    landing_mod3_desc:
      "Automatische klauselweise Übersetzung für internationale Vorstände und Aufsichtsgremien mit SHA-256 Prüffingerabdruck und PDF-Download.",

    // Standalone Auditor Studio
    studio_new_thread: "Neuer Prüfvorgang",
    studio_framework_label: "Aufsichtsrahmen (Framework)",
    studio_history_label: "Prüfhistorie",
    studio_presets_label: "Standard-Prüffragen",
    studio_title: "KI-Auditor Studio",
    studio_btn_workbench: "Zur Prüfbank",
    studio_btn_pdf: "Dossier PDF",
    studio_evidence_title: "Prüfbeleg & Kontext",
    studio_evidence_verified: "VERIFIZIERT",
    studio_locate_workbench: "In PDF-Prüfbank Anspringen",
    studio_empty_title: "Rechtskonforme BaFin & DORA Prüfinstanz",
    studio_empty_desc:
      "Stellen Sie konkrete Prüffragen zu Ausstiegsfristen, Haftungsobergrenzen, ZUGFeRD 2.3 E-Rechnungen oder BDSG § 26 Datenschutzstandards.",
    studio_input_placeholder:
      "Frage zu Aufsichtsrecht oder Vertragsklauseln eingeben (z. B. 'Wie hoch ist die maximale Verzugsstrafe?')...",
  },
  EN: {
    // Brand
    brand_sub: "Automated Regulatory Audit & Document Intelligence",
    mandant: "Tenant-01",

    // Navigation in Header
    nav_workbench: "Dual-View Workbench",
    nav_auditor: "AI Auditor (Studio)",
    nav_cockpit: "Executive Cockpit",
    btn_sign_in: "Sign In",
    btn_logout: "Log Out",
    btn_certificate: "Certificate",

    // Sidebar
    vault_title: "Document Vault",
    dora_title: "DORA Art. 30 (BaFin)",
    zugferd_title: "ZUGFeRD / Factur-X",
    lksg_title: "LkSG Supply Chain (BAFA)",
    ledger_title: "Audit Ledger",
    telemetry_title: "SYSTEM TELEMETRY",
    status_ready: "OPERATIONAL",
    dsgvo_verified: "ENFORCED",

    // Workbench & Canvas
    select_doc_placeholder: "Choose document from vault...",
    no_docs_indexed: "No documents indexed",
    btn_select_pdf: "SELECT PDF",
    btn_submit_ingest: "START AUDIT",
    empty_canvas_title: "NO DOCUMENT SELECTED",
    empty_canvas_desc:
      "Select an existing document from the vault above, or import a new PDF to execute automated regulatory audits.",
    btn_load_file: "Choose PDF File",
    audit_engine_title: "AUDIT INTELLIGENCE",
    audit_ready_title: "Audit Assistant Ready",
    audit_ready_desc:
      "Ask compliance queries below or pick a pre-set BaFin / DORA regulatory check.",
    suggested_checks_title: "STANDARD INQUIRIES (BAFIN / DORA):",
    suggested_1: "Are exit clauses defined under Art 30?",
    suggested_2: "What is the maximum delay penalty rate?",
    suggested_3: "Are sub-outsourcing approvals required?",
    input_placeholder: "Ask compliance query (e.g. 'What is the exit penalty?')...",
    source_tag_prefix: "Verified Source",

    // Landing Page
    landing_badge: "BaFin & DORA Art. 30 Verified",
    landing_hero_h1_pre: "German Regulatory Compliance & ICT Contracts.",
    landing_hero_h1_accent: "Audit-Ready & Verified.",
    landing_hero_sub:
      "Automated contract intelligence under EU DORA (Reg 2022/2554), BDSG § 26, and ZUGFeRD 2.3 / Factur-X. Featuring DIN A4 visual evidence tracking and certified English translation dossiers.",
    landing_cta_demo: "Launch Live Demo (Siemens ICT)",
    landing_cta_auth: "Sign In / Register",
    landing_cta_workbench: "Direct to Workbench",
    landing_metric_authority: "Supervisory Body",
    landing_metric_authority_sub: "DORA Pillar IV Compliant",
    landing_metric_privacy: "Data Sovereignty",
    landing_metric_privacy_sub: "Frankfurt Node",
    landing_metric_invoice: "E-Invoicing Mandate",
    landing_metric_invoice_sub: "EN 16931 / Factur-X",
    landing_metric_security: "Security Level",
    landing_metric_security_sub: "DIN 66399 Class 3",
    landing_modules_tag: "Enterprise Modules",
    landing_modules_title: "Comprehensive ICT Third-Party Risk Auditing",
    landing_mod1_title: "DORA Art. 30 Audit",
    landing_mod1_desc:
      "Verification of core clauses: 60-day termination notice, 90-day data migration guarantee, and 30-day sub-contractor objection window.",
    landing_mod2_title: "ZUGFeRD 2.3 & Factur-X",
    landing_mod2_desc:
      "Validation of hybrid PDF/XML e-invoices under EN 16931 and German Growth Opportunities Act. Automated Leitweg-ID and VAT checks.",
    landing_mod3_title: "Certified English Dossier",
    landing_mod3_desc:
      "Automated clause-by-clause translation for international boards and supervisory authorities with SHA-256 fingerprinting and PDF export.",

    // Standalone Auditor Studio
    studio_new_thread: "New Audit Inquiry",
    studio_framework_label: "Supervisory Framework",
    studio_history_label: "Audit History",
    studio_presets_label: "Standard Legal Inquiries",
    studio_title: "AI Auditor Studio",
    studio_btn_workbench: "Workbench ↗",
    studio_btn_pdf: "Dossier PDF",
    studio_evidence_title: "Audit Evidence & Context",
    studio_evidence_verified: "VERIFIED",
    studio_locate_workbench: "Locate in PDF Workbench",
    studio_empty_title: "Regulatory BaFin & DORA Audit Engine",
    studio_empty_desc:
      "Inquire on exit transition periods, liability caps, ZUGFeRD 2.3 hybrid invoicing, or BDSG Section 26 data sovereignty standards.",
    studio_input_placeholder:
      "Enter regulatory inquiry or clause check (e.g., 'What is the maximum delay penalty rate?')...",
  },
};
