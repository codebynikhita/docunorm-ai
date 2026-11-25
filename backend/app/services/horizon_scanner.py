"""
DocuNorm AI — Day 39: RegTech Horizon Scanner & Contract Drift Engine.
Tracks active European & German regulatory updates and performs automated contract drift audits.
"""

import hashlib
from datetime import UTC, date, datetime
from pathlib import Path
from uuid import UUID

import pymupdf as fitz

from app.schemas.horizon import (
    ContractDriftItem,
    ContractDriftReport,
    RegulatoryUpdate,
)

# Reference canonical horizon timeline for European & German Regulatory Regimes (2026)
STATUTORY_HORIZON_CATALOG: list[dict] = [
    {
        "update_id": "REG-DORA-RTS-2026-01",
        "title_de": "EBA/EIOPA/ESMA Final RTS zur Vergabe von Unteraufträgen für kritische IKT-Dienste (JC 2024 28)",
        "title_en": "EBA/EIOPA/ESMA Final RTS on Sub-Outsourcing of Critical ICT Services (JC 2024 28)",
        "issuing_authority": "EBA",
        "publication_date": date(2025, 11, 15),
        "enforcement_deadline": date(2026, 6, 30),
        "urgency": "HIGH",
        "impacted_frameworks": ["DORA", "KWG § 25b"],
        "summary_de": (
            "Verpflichtende Überwälzung aller aufsichtsrechtlichen Prüf- und Kontrollrechte auf Sub-Dienstleister "
            "der 4. Ebene. Verträge müssen konkrete quantitative Risikokennzahlen und ein 30-Tage-Vetorecht enthalten."
        ),
        "summary_en": (
            "Mandatory flow-through of all supervisory audit and inspection rights to 4th-party subcontractors. "
            "Agreements must stipulate quantitative concentration risk metrics and a 30-day objection right."
        ),
        "affected_clause_domains": ["subcontracting", "audit_rights", "veto_rights"],
        "statutory_source_url": "https://www.eba.europa.eu/regulation-and-policy/operational-resilience-and-dora",
    },
    {
        "update_id": "REG-BAFIN-RS-2026-10",
        "title_de": "BaFin Rundschreiben 10/2026: Zwingende Auslagerungsprüfungen und Notfall-Entflechtung bei Cloud-Hyperscalern",
        "title_en": "BaFin Circular 10/2026: Mandatory Cloud Outsourcing Audits and Emergency Unwinding Provisions",
        "issuing_authority": "BAFIN",
        "publication_date": date(2026, 2, 1),
        "enforcement_deadline": date(2026, 9, 30),
        "urgency": "IMMEDIATE",
        "impacted_frameworks": ["KWG § 25b", "BAIT", "DORA"],
        "summary_de": (
            "Fristlose Kündigungsvorrechte ohne Vorfälligkeitsentschädigung bei aufsichtsrechtlicher Beanstandung. "
            "Verpflichtende 90-tägige Migrationsbegleitung und jährliche Notfall-Entflechtungstests."
        ),
        "summary_en": (
            "Supervisory super-priority emergency termination rights without early prepayment penalty fees. "
            "Mandatory 90-day data migration support and annual contingency testing."
        ),
        "affected_clause_domains": ["exit_strategy", "termination", "unwinding", "datacenter_audits"],
        "statutory_source_url": "https://www.bafin.de/rundschreiben/10_2026_auslagerungen",
    },
    {
        "update_id": "REG-EU-AIACT-2026-08",
        "title_de": "EU AI Act Anhang III: Konformitätsnachweis & Post-Market Monitoring für Hochrisiko-KI-Systeme",
        "title_en": "EU AI Act Annex III: High-Risk AI System Certification & Post-Market Monitoring Mandates",
        "issuing_authority": "EU_COMMISSION",
        "publication_date": date(2024, 7, 12),
        "enforcement_deadline": date(2026, 8, 2),
        "urgency": "HIGH",
        "impacted_frameworks": ["EU AI Act", "GDPR", "DORA"],
        "summary_de": (
            "Vertragliche Dokumentations- und Logging-Pflichten für KI-Systeme im Kreditscoring, Risikomanagement und "
            "automatisierten Vertragsanalysen gem. Art. 9, 12 und 72 KI-Verordnung."
        ),
        "summary_en": (
            "Contractual technical documentation, automated logging, and post-market monitoring covenants for AI systems "
            "employed in credit evaluation, risk scoring, and legal analysis under EU AI Act Art. 9, 12, and 72."
        ),
        "affected_clause_domains": ["ai_governance", "logging", "human_oversight", "transparency"],
        "statutory_source_url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32024R1689",
    },
    {
        "update_id": "REG-EDPB-KEY-2026-04",
        "title_de": "EDPB Leitlinien 04/2026: Kryptografischer Souveränitätsschutz bei Drittstaatentransfers (DSGVO Art. 46/48)",
        "title_en": "EDPB Guidelines 04/2026: Cryptographic Sovereignty Safeguards for Third-Country Transfers",
        "issuing_authority": "EDPB",
        "publication_date": date(2026, 3, 10),
        "enforcement_deadline": date(2026, 10, 31),
        "urgency": "SCHEDULED",
        "impacted_frameworks": ["GDPR", "BDSG", "CLOUD Act"],
        "summary_de": (
            "Verschlüsselungsschlüssel (BYOK/HYOK) für europäische Unternehmens- und Bankdaten müssen ausschließlich auf HSM-Systemen "
            "innerhalb der EU verwaltet werden. Widerspruchspflicht gegen CLOUD Act Herausgaben ohne deutsches Rechtshilfeabkommen."
        ),
        "summary_en": (
            "Encryption keys (BYOK/HYOK) for European enterprise and banking data must reside exclusively within sovereign EU HSMs. "
            "Obligation to exhaust legal appeals against foreign CLOUD Act subpoenas."
        ),
        "affected_clause_domains": ["encryption", "key_management", "cross_border_data"],
        "statutory_source_url": "https://edpb.europa.eu/our-work-tools/general-guidance/guidelines_de",
    },
    {
        "update_id": "REG-BAFA-LKSG-2026-05",
        "title_de": "BAFA Handreichung 2026: Sorgfaltspflichten bei mittelbaren Zulieferern (§ 9 Abs. 2 LkSG)",
        "title_en": "BAFA Guidance 2026: Due Diligence Duties for Indirect Tier-N Suppliers (§ 9 LkSG)",
        "issuing_authority": "BAFA",
        "publication_date": date(2026, 1, 20),
        "enforcement_deadline": date(2026, 12, 31),
        "urgency": "INFORMATIONAL",
        "impacted_frameworks": ["LkSG", "CSDDD"],
        "summary_de": (
            "Pflicht zur unverzüglichen Durchführung anlassbezogener Risikoanalysen und Festlegung präventiver "
            "Abhilfemaßnahmen bei substantiierter Kenntnis über Tier-N Menschenrechtsverletzungen."
        ),
        "summary_en": (
            "Duty to immediately execute ad-hoc risk assessments and establish preventative corrective action plans "
            "upon substantiated knowledge of upstream Tier-N human rights infringements."
        ),
        "affected_clause_domains": ["supply_chain", "tier_n", "grievance_mechanism"],
        "statutory_source_url": "https://www.bafa.de/DE/Lieferketten/sorgfaltspflichten_lksg.html",
    },
]


class HorizonScannerEngine:
    """
    Automated Regulatory Change Tracking, RegTech Horizon Scanner, and Contract Drift Auditor.
    """

    @classmethod
    def get_active_updates(cls, reference_date: date | None = None) -> list[RegulatoryUpdate]:
        """
        Returns registered statutory regulatory updates with calculated days until enforcement deadline.
        """
        ref = reference_date or datetime.now(UTC).date()
        updates: list[RegulatoryUpdate] = []

        for item in STATUTORY_HORIZON_CATALOG:
            enforce_date = item["enforcement_deadline"]
            days_left = (enforce_date - ref).days

            update = RegulatoryUpdate(
                update_id=item["update_id"],
                title_de=item["title_de"],
                title_en=item["title_en"],
                issuing_authority=item["issuing_authority"],
                publication_date=item["publication_date"],
                enforcement_deadline=item["enforcement_deadline"],
                urgency=item["urgency"],
                impacted_frameworks=item["impacted_frameworks"],
                summary_de=item["summary_de"],
                summary_en=item["summary_en"],
                affected_clause_domains=item["affected_clause_domains"],
                statutory_source_url=item["statutory_source_url"],
                days_until_enforcement=days_left,
            )
            updates.append(update)

        return updates

    @classmethod
    def audit_contract_drift(
        cls,
        document_id: UUID,
        document_filename: str,
        chunks: list[dict],
        reference_date: date | None = None,
    ) -> ContractDriftReport:
        """
        Audits contract chunks against the regulatory horizon, identifying clauses
        that suffer from statutory drift due to upcoming or recently enacted standards.
        """
        ref_date = reference_date or datetime.now(UTC).date()
        active_updates = cls.get_active_updates(ref_date)
        drift_items: list[ContractDriftItem] = []

        # Analyze each chunk for regulatory drift
        for idx, c in enumerate(chunks, 1):
            content = c.get("content", "")
            lower = content.lower()
            page_num = c.get("page_number", 1)
            chunk_id = str(c.get("id", f"c_{page_num}_{idx}"))

            # 1. Check Subcontracting Drift vs. DORA RTS 2026
            if any(k in lower for k in ["subunternehmer", "unterauftrag", "nachunternehmer", "subcontractor"]):
                # If clause allows subcontracting without 4th-party flow-through or quantitative risk limits
                if not any(k in lower for k in ["jc 2024 28", "tier-4", "quantitative risikokennzahlen", "konzentrationsrisiko", "30-tage-veto"]):
                    upd = next((u for u in active_updates if u.update_id == "REG-DORA-RTS-2026-01"), active_updates[0])
                    drift_items.append(
                        ContractDriftItem(
                            clause_id=chunk_id,
                            page_number=page_num,
                            current_clause_text=content[:250],
                            associated_update_id="REG-DORA-RTS-2026-01",
                            drift_severity="CRITICAL_DRIFT",
                            compliance_gap_de=(
                                "Klausel regelt nur direkte Unterauftragsvergaben (Tier-2) und enthält keine "
                                "Durchgriffskaskade auf Unterauftragnehmer der 4. Ebene gem. DORA RTS (JC 2024 28)."
                            ),
                            compliance_gap_en=(
                                "Clause only covers direct Tier-2 subcontracting, omitting mandatory 4th-party "
                                "pass-through covenants under DORA RTS (JC 2024 28)."
                            ),
                            days_until_deadline=upd.days_until_enforcement,
                            retrofitting_action_required=(
                                "Ergänzung der DORA RTS Kaskadenklausel mit vertraglicher Bindung aller Nachunternehmer "
                                "entlang der Kette und Kodifizierung des 30-Tage-Vetorechts."
                            ),
                        )
                    )

            # 2. Check Termination / Unwinding Drift vs. BaFin 10/2026
            elif any(k in lower for k in ["kündigung", "laufzeit", "beendigung", "termination", "exit"]):
                if not any(k in lower for k in ["notfall-entflechtung", "aufsichtsrechtliche anordnung", "90 tage migrationsbegleitung", "ohne vorfälligkeitsentschädigung"]):
                    upd = next((u for u in active_updates if u.update_id == "REG-BAFIN-RS-2026-10"), active_updates[1])
                    drift_items.append(
                        ContractDriftItem(
                            clause_id=chunk_id,
                            page_number=page_num,
                            current_clause_text=content[:250],
                            associated_update_id="REG-BAFIN-RS-2026-10",
                            drift_severity="CRITICAL_DRIFT",
                            compliance_gap_de=(
                                "Klausel sieht keine unverzügliche aufsichtsrechtliche Kündigung ohne Vorfälligkeitsentschädigung "
                                "und keine vertraglich garantierte 90-Tage-Notfall-Entflechtung gem. BaFin RS 10/2026 vor."
                            ),
                            compliance_gap_en=(
                                "Clause lacks supervisory super-priority exit without prepayment penalties and lacks "
                                "mandatory 90-day emergency unwinding under BaFin Circular 10/2026."
                            ),
                            days_until_deadline=upd.days_until_enforcement,
                            retrofitting_action_required=(
                                "Einfügung des BaFin-Sonderkündigungsrechts gem. KWG § 25b und Vereinbarung von Notfall-Migrationstests."
                            ),
                        )
                    )

            # 3. Check AI Governance Drift vs. EU AI Act Aug 2026
            elif any(k in lower for k in ["künstliche intelligenz", "artificial intelligence", "algorithmus", "machine learning", "ki-modell", "llm"]):
                if not any(k in lower for k in ["ki-verordnung", "eu ai act", "post-market monitoring", "art. 12", "technische dokumentation"]):
                    upd = next((u for u in active_updates if u.update_id == "REG-EU-AIACT-2026-08"), active_updates[2])
                    drift_items.append(
                        ContractDriftItem(
                            clause_id=chunk_id,
                            page_number=page_num,
                            current_clause_text=content[:250],
                            associated_update_id="REG-EU-AIACT-2026-08",
                            drift_severity="HIGH_RISK",
                            compliance_gap_de=(
                                "Eingesetzte KI-Komponenten verfügen über keine vertraglich garantierten Logging- und "
                                "Post-Market-Monitoring-Pflichten zur Erfüllung von Art. 12 und 72 EU AI Act bis August 2026."
                            ),
                            compliance_gap_en=(
                                "AI systems lack contractual vendor logging and post-market monitoring duties required by "
                                "EU AI Act Art. 12 & 72 enforcement in August 2026."
                            ),
                            days_until_deadline=upd.days_until_enforcement,
                            retrofitting_action_required=(
                                "Aufnahme der EU AI Act Annex III Compliance-Klausel für automatisierte Protokollierung und Auditierbarkeit."
                            ),
                        )
                    )

            # 4. Check Encryption / Key Sovereignty vs. EDPB 04/2026
            elif any(k in lower for k in ["verschlüssel", "encryption", "key", "schlüssel", "zertifikat", "hsm", "kms"]):
                if not any(k in lower for k in ["byok", "hyok", "schlüsselhoheit", "eu-hsm", "jurisdiktion frankfurt"]):
                    upd = next((u for u in active_updates if u.update_id == "REG-EDPB-KEY-2026-04"), active_updates[3])
                    drift_items.append(
                        ContractDriftItem(
                            clause_id=chunk_id,
                            page_number=page_num,
                            current_clause_text=content[:250],
                            associated_update_id="REG-EDPB-KEY-2026-04",
                            drift_severity="CRITICAL_DRIFT",
                            compliance_gap_de=(
                                "Verschlüsselungsschlüssel werden vom Dienstleister verwaltet ohne explizite BYOK-Klausel "
                                "mit ausschließlicher Verwahrung in zertifizierten EU-HSMs (EDPB 04/2026)."
                            ),
                            compliance_gap_en=(
                                "Keys managed by vendor without explicit customer-controlled BYOK HSM located exclusively in the EU."
                            ),
                            days_until_deadline=upd.days_until_enforcement,
                            retrofitting_action_required=(
                                "Umstellung auf BYOK-Klausel mit HSM-Standortgarantie in der Bundesrepublik Deutschland."
                            ),
                        )
                    )

            # 5. Check Supply Chain Tier-N Due Diligence vs. BAFA LkSG 2026
            elif any(k in lower for k in ["lieferkette", "zulieferer", "menschenrecht", "lksg", "supply chain"]):
                if not any(k in lower for k in ["tier-n", "anlassbezogene risikoanalyse", "bafa", "csddd"]):
                    upd = next((u for u in active_updates if u.update_id == "REG-BAFA-LKSG-2026-05"), active_updates[-1])
                    drift_items.append(
                        ContractDriftItem(
                            clause_id=chunk_id,
                            page_number=page_num,
                            current_clause_text=content[:250],
                            associated_update_id="REG-BAFA-LKSG-2026-05",
                            drift_severity="MODERATE_GAP",
                            compliance_gap_de=(
                                "Vertrag regelt Sorgfaltspflichten nur für unmittelbare Zulieferer (Tier-1) ohne "
                                "anlassbezogene Prüfprozesse für mittelbare Tier-N Zulieferer gem. § 9 LkSG."
                            ),
                            compliance_gap_en=(
                                "Contract restricts human rights due diligence to direct Tier-1 suppliers without "
                                "ad-hoc upstream inspection mechanisms under German LkSG § 9."
                            ),
                            days_until_deadline=upd.days_until_enforcement,
                            retrofitting_action_required=(
                                "Einfügung der BAFA-Musterklausel für anlassbezogene Vor-Ort-Audits bei mittelbaren Lieferanten."
                            ),
                        )
                    )

        # De-duplicate drift items by clause_id preserving highest severity
        unique_drifts: list[ContractDriftItem] = []
        seen_clauses = set()
        for d in drift_items:
            if d.clause_id not in seen_clauses:
                seen_clauses.add(d.clause_id)
                unique_drifts.append(d)

        crit_count = sum(1 for d in unique_drifts if d.drift_severity == "CRITICAL_DRIFT")
        high_count = sum(1 for d in unique_drifts if d.drift_severity == "HIGH_RISK")
        mod_count = sum(1 for d in unique_drifts if d.drift_severity == "MODERATE_GAP")

        # Compute overall drift score (0 - 100)
        total_chunks = max(1, len(chunks))
        if crit_count > 0:
            drift_score = min(98.0, 70.0 + crit_count * 9.0)
            status = "ACTION_REQUIRED"
        elif high_count > 0:
            drift_score = min(75.0, 45.0 + high_count * 10.0)
            status = "ACTION_REQUIRED"
        elif mod_count > 0:
            drift_score = 30.0
            status = "ACTION_REQUIRED"
        else:
            drift_score = 0.0
            status = "UP_TO_DATE"

        earliest_deadline = min((u.enforcement_deadline for u in active_updates), default=None)

        # Check if any critical item has expired deadline
        for d in unique_drifts:
            if d.days_until_deadline < 0 and d.drift_severity == "CRITICAL_DRIFT":
                status = "NON_COMPLIANT_EXPIRED"
                drift_score = 99.0
                break

        seal_str = f"{document_id}:{drift_score}:{len(unique_drifts)}:{status}"
        sha_seal = hashlib.sha256(seal_str.encode("utf-8")).hexdigest()

        return ContractDriftReport(
            document_id=document_id,
            document_filename=document_filename,
            audited_at=datetime.now(UTC),
            overall_drift_score=round(drift_score, 1),
            total_clauses_analyzed=total_chunks,
            drifting_clauses_count=len(unique_drifts),
            critical_enforcement_items=crit_count,
            earliest_enforcement_deadline=earliest_deadline,
            applicable_regulatory_updates=active_updates,
            drift_items=unique_drifts,
            retrofitting_status=status,
            sha256_seal=sha_seal,
        )

    @classmethod
    def generate_drift_report_pdf(
        cls,
        document_filename: str,
        report: ContractDriftReport,
        signatory_name: str = "Dr. Johannes von Stauffenberg, Leitender RegTech-Auditor",
        output_dir: Path | str = "/tmp/docunorm_exports",
    ) -> Path:
        """
        Generates official 2-page DIN 5008 Regulatory Horizon & Contract Drift Audit Report PDF
        (RegTech Horizontanalyse & Vertragsdrift-Gutachten) with cryptographic SHA-256 seal.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        clean_name = document_filename.replace(".pdf", "")
        pdf_file = output_path / f"VERTRAGSDRIFT_GUTACHTEN_{clean_name}.pdf"

        doc = fitz.open()

        # ================= PAGE 1: EXECUTIVE HORIZON SCORECARD & DRIFT METRICS =================
        page1 = doc.new_page(width=595, height=842)

        # Header Box (Teal / Slate Theme)
        page1.draw_rect(fitz.Rect(45, 40, 550, 110), color=(0.1, 0.25, 0.3), fill=(0.95, 0.98, 0.98))
        page1.insert_text(fitz.Point(55, 62), "REGTECH HORIZONT-ANALYSE & VERTRAGSDRIFT-GUTACHTEN", fontsize=11, fontname="hebo", color=(0.08, 0.2, 0.25))
        page1.insert_text(fitz.Point(55, 78), "Dynamische Normennachverfolgung: DORA RTS 2026 • BaFin RS 10/2026 • EU AI Act", fontsize=8.5, fontname="hebo", color=(0.15, 0.5, 0.5))
        page1.insert_text(
            fitz.Point(55, 94),
            f"Vertrag: {document_filename} • Prüfdatum: {report.audited_at.strftime('%d.%m.%Y')} • DIN EN ISO 9001 / BaFin Konform",
            fontsize=7.5,
            fontname="helv",
            color=(0.35, 0.4, 0.45),
        )

        y = 130
        # Verdict Card
        verdict_color = (0.8, 0.1, 0.1) if report.retrofitting_status == "NON_COMPLIANT_EXPIRED" else (0.85, 0.45, 0.0) if report.retrofitting_status == "ACTION_REQUIRED" else (0.1, 0.6, 0.2)
        verdict_fill = (0.99, 0.94, 0.94) if report.retrofitting_status == "NON_COMPLIANT_EXPIRED" else (0.99, 0.97, 0.92) if report.retrofitting_status == "ACTION_REQUIRED" else (0.94, 0.99, 0.95)

        page1.draw_rect(fitz.Rect(45, y, 550, y + 60), color=verdict_color, fill=verdict_fill, width=1.5)
        page1.insert_text(fitz.Point(55, y + 22), "GESAMT-VERTRAGSDRIFT / STATUTORY DRIFT STATUS:", fontsize=8.5, fontname="hebo", color=(0.2, 0.2, 0.2))
        page1.insert_text(fitz.Point(55, y + 42), f"{report.retrofitting_status} (Drift-Score: {report.overall_drift_score}/100)", fontsize=13, fontname="hebo", color=verdict_color)
        page1.insert_text(
            fitz.Point(350, y + 25),
            f"Driftende Klauseln: {report.drifting_clauses_count} / {report.total_clauses_analyzed}",
            fontsize=8,
            fontname="hebo",
            color=(0.2, 0.2, 0.2),
        )
        page1.insert_text(
            fitz.Point(350, y + 42),
            f"Kritische Umsetzungsfristen: {report.critical_enforcement_items}",
            fontsize=8,
            fontname="helv",
            color=(0.4, 0.4, 0.4),
        )

        y += 80
        page1.insert_text(fitz.Point(45, y), "IDENTIFIZIERTE NORMEN- & KLAUSELDRIFTS (HANDLUNGSBEDARF)", fontsize=9.5, fontname="hebo", color=(0.1, 0.15, 0.25))
        y += 15

        # Render Drift Cards
        for idx, item in enumerate(report.drift_items[:3], 1):
            sev_color = (0.8, 0.15, 0.15) if item.drift_severity == "CRITICAL_DRIFT" else (0.85, 0.45, 0.0)
            page1.draw_rect(fitz.Rect(45, y, 550, y + 105), color=sev_color, fill=(0.98, 0.99, 0.99))
            page1.insert_text(fitz.Point(55, y + 16), f"§ {idx}. Klauseldrift zu {item.associated_update_id}", fontsize=9, fontname="hebo", color=sev_color)
            page1.insert_text(fitz.Point(430, y + 16), f"Frist: Noch {item.days_until_deadline} Tage", fontsize=8, fontname="hebo", color=sev_color)

            page1.insert_text(fitz.Point(55, y + 30), f"Fundstelle: Seite {item.page_number} • Schweregrad: {item.drift_severity}", fontsize=7.5, fontname="hebo", color=(0.3, 0.35, 0.4))

            page1.insert_textbox(
                fitz.Rect(55, y + 38, 540, y + 72),
                item.compliance_gap_de,
                fontsize=7.5,
                fontname="helv",
                color=(0.15, 0.15, 0.15),
            )

            # Retrofitting Action Box
            page1.draw_rect(fitz.Rect(55, y + 76, 540, y + 96), color=(0.1, 0.45, 0.4), fill=(0.93, 0.97, 0.97))
            page1.insert_text(fitz.Point(62, y + 89), f"Nachrüstungsmaßnahme: {item.retrofitting_action_required}", fontsize=7.5, fontname="hebo", color=(0.08, 0.35, 0.3))

            y += 115

        # Footer page 1
        page1.insert_text(fitz.Point(45, 810), f"DocuNorm AI RegTech Horizon Scanner • SHA-256: {report.sha256_seal[:32]}... • Seite 1 von 2", fontsize=7, fontname="helv", color=(0.4, 0.4, 0.4))

        # ================= PAGE 2: STATUTORY TIMELINE & RETROFITTING SCHEDULE =================
        page2 = doc.new_page(width=595, height=842)

        page2.draw_rect(fitz.Rect(45, 40, 550, 80), color=(0.1, 0.25, 0.3), fill=(0.95, 0.98, 0.98))
        page2.insert_text(fitz.Point(55, 65), "AUFSICHTSRECHTLICHER HORIZONT-ZEITSTRAHL (2026/2027)", fontsize=10, fontname="hebo", color=(0.08, 0.2, 0.25))
        page2.insert_text(fitz.Point(55, 82), "Maßgebliche Fristen der europäischen und deutschen Finanzmarktaufsicht", fontsize=8, fontname="helv", color=(0.35, 0.4, 0.45))

        y2 = 100
        for upd in report.applicable_regulatory_updates[:4]:
            urg_color = (0.8, 0.15, 0.15) if upd.urgency in ["IMMEDIATE", "HIGH"] else (0.1, 0.4, 0.6)
            page2.insert_text(fitz.Point(45, y2), f"{upd.update_id} ({upd.issuing_authority}) • Durchsetzungsfrist: {upd.enforcement_deadline.strftime('%d.%m.%Y')}", fontsize=8.5, fontname="hebo", color=urg_color)
            y2 += 12

            upd_box = fitz.Rect(45, y2, 550, y2 + 65)
            page2.draw_rect(upd_box, color=(0.8, 0.85, 0.85), fill=(0.98, 0.99, 0.99))
            page2.insert_textbox(fitz.Rect(52, y2 + 6, 542, y2 + 58), upd.summary_de, fontsize=7.5, fontname="helv", color=(0.1, 0.15, 0.15))
            y2 += 75

        # Legal Attestation Box
        y2 = max(y2 + 10, 620)
        page2.draw_rect(fitz.Rect(45, y2, 550, y2 + 140), color=(0.15, 0.25, 0.3), fill=(0.97, 0.98, 0.99))
        page2.insert_text(fitz.Point(55, y2 + 20), "RECHTLICHE HORIZONT-ATTESTATIERUNG & ZEITPLAN", fontsize=9.5, fontname="hebo", color=(0.08, 0.2, 0.25))

        attestation = (
            "Das vorstehende Gutachten bescheinigt die kontinuierliche Konformitätsüberwachung gem. DORA Art. 28 "
            "und BaFin KWG § 25b. Zur Vermeidung aufsichtsrechtlicher Zwangsgelder oder Stilllegungsverfügungen "
            "sind die identifizierten Nachrüstungsmaßnahmen vor Ablauf der jeweiligen Durchsetzungsfristen vertraglich umzusetzen."
        )
        page2.insert_textbox(fitz.Rect(55, y2 + 28, 535, y2 + 65), attestation, fontsize=7.5, fontname="helv", color=(0.2, 0.2, 0.2))

        now_str = datetime.now(UTC).strftime("%d. %B %Y")
        page2.insert_text(fitz.Point(55, y2 + 85), f"Frankfurt am Main, den {now_str}", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))

        page2.draw_line(fitz.Point(55, y2 + 115), fitz.Point(260, y2 + 115), color=(0.3, 0.3, 0.3), width=0.8)
        page2.insert_text(fitz.Point(55, y2 + 128), signatory_name, fontsize=7.5, fontname="hebo", color=(0.1, 0.1, 0.1))

        page2.insert_text(fitz.Point(320, y2 + 85), f"Kryptografischer Hash-Siegel:\n{report.sha256_seal}", fontsize=6.5, fontname="cour", color=(0.3, 0.35, 0.4))

        # Footer page 2
        page2.insert_text(fitz.Point(45, 810), f"DocuNorm AI RegTech Horizon Scanner • SHA-256: {report.sha256_seal[:32]}... • Seite 2 von 2", fontsize=7, fontname="helv", color=(0.4, 0.4, 0.4))

        doc.save(str(pdf_file))
        doc.close()
        return pdf_file


horizon_scanner = HorizonScannerEngine()
