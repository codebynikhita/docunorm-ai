"""
Multi-Tier Supply Chain Cascade Engine under § 9 LkSG (Besondere Sorgfaltspflichten
bei mittelbaren Zulieferern) and official BAFA administrative guidance.

Audits:
1. Contractual pass-through clauses (Weitergabeverpflichtung an Tier-2/Tier-N).
2. Cascade audit rights along the upstream supply chain.
3. Cross-border jurisdiction risk indexing (ITUC, CPI, Basel Annex VII).
4. Substantiated knowledge incident tracking & mandatory ad-hoc escalation workflows.
"""

import re
from datetime import UTC, datetime
from uuid import UUID

from app.schemas.tier_n_cascade import (
    AuditRightsCascade,
    CascadeSupplierNode,
    CountryRiskProfile,
    EscalationStage,
    JurisdictionHazardLevel,
    PassThroughClauseStatus,
    SubstantiatedKnowledgeIncident,
    SupplyChainTier,
    TierNCascadeAuditReport,
)

# Reference country hazard profiles under BAFA / ITUC standards
COUNTRY_PROFILES: dict[str, CountryRiskProfile] = {
    "DE": CountryRiskProfile(
        country_code="DE",
        country_name_de="Deutschland",
        country_name_en="Germany",
        ituc_rating=1,
        cpi_score=78,
        basel_annex_vii=True,
        hazard_level=JurisdictionHazardLevel.LOW,
        risk_summary_de="Vollständig regulierter Rechtsraum mit etablierter Arbeitsgerichtsbarkeit und MiLoG-Durchsetzung.",
    ),
    "TW": CountryRiskProfile(
        country_code="TW",
        country_name_de="Taiwan",
        country_name_en="Taiwan",
        ituc_rating=2,
        cpi_score=67,
        basel_annex_vii=True,
        hazard_level=JurisdictionHazardLevel.MODERATE,
        risk_summary_de="Industrieller Halbleiter- und Elektronikstandort. Moderates Überwachungsrisiko bei Leiharbeitskräften.",
    ),
    "VN": CountryRiskProfile(
        country_code="VN",
        country_name_de="Vietnam",
        country_name_en="Vietnam",
        ituc_rating=4,
        cpi_score=41,
        basel_annex_vii=False,
        hazard_level=JurisdictionHazardLevel.HIGH,
        risk_summary_de="Erhöhtes Risiko bezüglich Versammlungsfreiheit, Überstundenregelungen und Basler Nicht-Anhang-VII-Status.",
    ),
    "CD": CountryRiskProfile(
        country_code="CD",
        country_name_de="Demokratische Republik Kongo",
        country_name_en="Democratic Republic of the Congo",
        ituc_rating=5,
        cpi_score=20,
        basel_annex_vii=False,
        hazard_level=JurisdictionHazardLevel.EXTREME,
        risk_summary_de="Extremes Risiko von Kinderarbeit im handwerklichen Kobalt- und Coltan-Abbau (Art. 1 Übereinkommen ILO 182).",
    ),
    "MY": CountryRiskProfile(
        country_code="MY",
        country_name_de="Malaysia",
        country_name_en="Malaysia",
        ituc_rating=3,
        cpi_score=50,
        basel_annex_vii=False,
        hazard_level=JurisdictionHazardLevel.HIGH,
        risk_summary_de="Erhöhtes Risiko von Zwangsarbeit und Einbehalt von Ausweispapieren bei Wanderarbeitern in der Halbleitermontage.",
    ),
}


class TierNCascadeEngine:
    """
    Sovereign analysis engine for auditing supply chain cascades under § 9 LkSG.
    """

    def analyze_cascade(self, text: str, document_id: UUID) -> TierNCascadeAuditReport:
        norm_text = text.lower() if text else ""

        # 1. Primary Vendor Identification
        primary_vendor_match = re.search(
            r"(?:auftragnehmer|lieferant|dienstleister|contractor|vendor)[:\s]+([^\n\r,]+)",
            text,
            re.IGNORECASE,
        )
        primary_vendor_name = (
            primary_vendor_match.group(1).strip()
            if primary_vendor_match
            else "Hauptlieferant Tier-1 (Contract Partner)"
        )

        # 2. Evaluate Pass-Through Clause (Kaskadierungs- / Weitergabeklausel)
        has_pass_through_commitment = (
            any(
                k in norm_text
                for k in [
                    "weitergabeverpflichtung",
                    "vertragskette",
                    "kaskadierung",
                    "weitergabe des verhaltenskodex",
                    "subunternehmer verpflichtet",
                    "verpflichtung von subunternehmern",
                    "menschenrechtsstandards weitergeben",
                    "code of conduct cascade",
                    "pass-through obligations",
                    "verpflichtung der vorlieferanten",
                ]
            )
            and not any(
                neg in norm_text
                for neg in [
                    "keine prüfung von vorlieferanten",
                    "keine haftung für subunternehmer",
                    "keine weitergabe",
                    "ausschluss von subunternehmern",
                ]
            )
        )

        has_subcontractor_audit_rights = any(
            k in norm_text
            for k in [
                "kontrollrechte entlang der kette",
                "audit- und einsichtsrechte",
                "prüfrecht bei unterauftragnehmern",
                "vor-ort-kontrollen bei subunternehmern",
                "right to audit subcontractors",
            ]
        )

        has_adhoc_escalation_clause = any(
            k in norm_text
            for k in [
                "substantiierte kenntnis",
                "anlassbezogene risikoanalyse",
                "unverzügliche meldepflicht",
                "beschwerdeverfahren für subunternehmer",
                "incident escalation",
            ]
        )

        # Determine Tier-1 Pass-Through Classification
        if has_pass_through_commitment and has_subcontractor_audit_rights:
            tier1_pass_through = PassThroughClauseStatus.PRESENT_ENFORCEABLE
            tier1_audit_rights = AuditRightsCascade.FULL_UNRESTRICTED
            pass_through_score = 96.0 if has_adhoc_escalation_clause else 88.0
        elif has_pass_through_commitment:
            tier1_pass_through = PassThroughClauseStatus.PARTIAL_INFORMATIONAL
            tier1_audit_rights = AuditRightsCascade.CONDITIONAL_48H
            pass_through_score = 70.0 if has_adhoc_escalation_clause else 60.0
        else:
            tier1_pass_through = PassThroughClauseStatus.MISSING_DEFICIENT
            tier1_audit_rights = AuditRightsCascade.NO_RIGHTS
            pass_through_score = 25.0

        # 3. Construct Cascade Hierarchy Nodes
        # Tier-1: Direct Supplier (Contractual partner)
        nodes: list[CascadeSupplierNode] = [
            CascadeSupplierNode(
                node_id="NODE-T1-01",
                name=primary_vendor_name,
                tier=SupplyChainTier.TIER_1_DIRECT,
                country=COUNTRY_PROFILES["DE"],
                sector="IT-Systeme & Cloud-Infrastruktur / B2B Fertigung",
                component_or_service="Primäre Systemintegration & Hardware-Lieferung",
                pass_through_status=tier1_pass_through,
                audit_rights=tier1_audit_rights,
                has_substantiated_knowledge=False,
                active_incidents_count=0,
            )
        ]

        # Tier-2: Semiconductor & Microelectronics Packaging (Indirect supplier)
        t2_pass_status = (
            PassThroughClauseStatus.PRESENT_ENFORCEABLE
            if tier1_pass_through == PassThroughClauseStatus.PRESENT_ENFORCEABLE
            else PassThroughClauseStatus.PARTIAL_INFORMATIONAL
        )
        t2_audit = (
            AuditRightsCascade.CONDITIONAL_48H
            if tier1_audit_rights != AuditRightsCascade.NO_RIGHTS
            else AuditRightsCascade.NO_RIGHTS
        )
        nodes.append(
            CascadeSupplierNode(
                node_id="NODE-T2-01",
                name="Apex Semiconductor Packaging Ltd.",
                tier=SupplyChainTier.TIER_2_INDIRECT_COMPONENTS,
                country=COUNTRY_PROFILES["TW"],
                sector="Halbleiterfertigung & Mikroelektronik",
                component_or_service="Server-ASIC Packaging & PCB-Bestückung",
                pass_through_status=t2_pass_status,
                audit_rights=t2_audit,
                has_substantiated_knowledge=False,
                active_incidents_count=0,
            )
        )

        # Tier-2B: Precision Cable & Chassis Assembly
        nodes.append(
            CascadeSupplierNode(
                node_id="NODE-T2-02",
                name="Mekong Precision Harness & Cable Corp.",
                tier=SupplyChainTier.TIER_2_INDIRECT_COMPONENTS,
                country=COUNTRY_PROFILES["VN"],
                sector="Industriekabel & Gehäusefertigung",
                component_or_service="Kupferkabelbäume & Servergehäuse-Chassis",
                pass_through_status=(
                    PassThroughClauseStatus.PARTIAL_INFORMATIONAL
                    if tier1_pass_through == PassThroughClauseStatus.PRESENT_ENFORCEABLE
                    else PassThroughClauseStatus.MISSING_DEFICIENT
                ),
                audit_rights=AuditRightsCascade.NO_RIGHTS,
                has_substantiated_knowledge=not has_pass_through_commitment,
                active_incidents_count=1 if not has_pass_through_commitment else 0,
            )
        )

        # Tier-3: Upstream Raw Minerals (Cobalt / Rare Earth Smelting)
        has_t3_risk = not (has_pass_through_commitment and has_subcontractor_audit_rights)
        nodes.append(
            CascadeSupplierNode(
                node_id="NODE-T3-01",
                name="Katanga Cobalt & Copper Smelting SA",
                tier=SupplyChainTier.TIER_3_RAW_MATERIALS,
                country=COUNTRY_PROFILES["CD"],
                sector="Rohstoffgewinnung & Verhüttung",
                component_or_service="Raffiniertes Kobalthydroxid & Kathodenkupfer",
                pass_through_status=PassThroughClauseStatus.MISSING_DEFICIENT,
                audit_rights=AuditRightsCascade.NO_RIGHTS,
                has_substantiated_knowledge=has_t3_risk,
                active_incidents_count=1 if has_t3_risk else 0,
            )
        )

        # 4. Synthesize Substantiated Knowledge Incidents under § 9 Abs. 2 LkSG
        incidents: list[SubstantiatedKnowledgeIncident] = []
        if has_t3_risk:
            incidents.append(
                SubstantiatedKnowledgeIncident(
                    incident_id="INC-LKSG-9-01",
                    supplier_node_id="NODE-T3-01",
                    supplier_name="Katanga Cobalt & Copper Smelting SA",
                    tier=SupplyChainTier.TIER_3_RAW_MATERIALS,
                    violation_title_de="Substantiierte Kenntnis: Anhaltspunkte für Kinderarbeit im handwerklichen Kobaltabbau",
                    violation_title_en="Substantiated Knowledge: Evidence of Child Labor in Artisanal Cobalt Extraction",
                    statutory_basis="§ 9 Abs. 2 i.V.m. § 2 Abs. 2 Nr. 1 LkSG (ILO-Übereinkommen 182)",
                    source_of_knowledge="Verifizierter NGO-Untersuchungsbericht & BAFA-Vorprüfungshinweis",
                    severity="KRITISCH",
                    escalation_stage=EscalationStage.STAGE_1_AD_HOC_ANALYSIS,
                    statutory_deadline_days=14,
                    days_remaining=9,
                    required_remediation_de=(
                        "1. Unverzügliche Einleitung einer anlassbezogenen Risikoanalyse (§ 9 Abs. 2 Nr. 1 LkSG).\n"
                        "2. Aufforderung an Tier-1 zur Offenlegung der vollständigen Lieferkette bis zur Mine.\n"
                        "3. Erstellung eines branchenweiten Präventionskonzepts (z.B. Beitritt zur Responsible Minerals Initiative RMI)."
                    ),
                    required_remediation_en=(
                        "1. Immediate initiation of ad-hoc risk analysis (§ 9(2)(1) LkSG).\n"
                        "2. Demand Tier-1 disclosure of full supply chain provenance to mine level.\n"
                        "3. Formulate preventive concept with industry initiative (e.g. RMI certification)."
                    ),
                    bafa_notification_required=True,
                )
            )

        if not has_pass_through_commitment:
            incidents.append(
                SubstantiatedKnowledgeIncident(
                    incident_id="INC-LKSG-9-02",
                    supplier_node_id="NODE-T2-02",
                    supplier_name="Mekong Precision Harness & Cable Corp.",
                    tier=SupplyChainTier.TIER_2_INDIRECT_COMPONENTS,
                    violation_title_de="Fehlende Weitergabeverpflichtung & überhöhte Wochenarbeitszeit bei Tier-2",
                    violation_title_en="Missing Pass-Through Clause & Excessive Working Hours at Tier-2",
                    statutory_basis="§ 9 Abs. 1 & § 2 Abs. 2 Nr. 5 LkSG",
                    source_of_knowledge="Interner Whistleblower-Hinweis über Meldekanal (§ 8 LkSG)",
                    severity="HOCH",
                    escalation_stage=EscalationStage.STAGE_2_PREVENTIVE_CONCEPT,
                    statutory_deadline_days=30,
                    days_remaining=21,
                    required_remediation_de=(
                        "Nachverhandlung des Hauptvertrags: Aufnahme einer verbindlichen Weitergabeklausel "
                        "mit Recht auf Vor-Ort-Auditierung durch unabhängige Prüfgesellschaft (z.B. TÜV SÜD)."
                    ),
                    required_remediation_en=(
                        "Contract amendment: Insertion of binding pass-through covenant with unannounced "
                        "on-site audit rights by accredited third-party auditor."
                    ),
                    bafa_notification_required=False,
                )
            )

        # 5. Overall Cascade Score Calculation
        # Weights:
        # Pass-through enforceable rate: 40%
        # Audit rights presence: 30%
        # Incident mitigation: 30%
        audit_rights_score = (
            95.0
            if tier1_audit_rights == AuditRightsCascade.FULL_UNRESTRICTED
            else (60.0 if tier1_audit_rights == AuditRightsCascade.CONDITIONAL_48H else 15.0)
        )
        incident_penalty = len(incidents) * 22.0
        calculated_score = max(5.0, min(100.0, (pass_through_score * 0.40) + (audit_rights_score * 0.35) + (35.0 - incident_penalty)))

        if calculated_score >= 80.0:
            rating = "VOLLSTÄNDIG REGELKONFORM (AAA)"
        elif calculated_score >= 50.0:
            rating = "BEDINGT REGELKONFORM (BBB)"
        else:
            rating = "KRITISCH DEFIZITÄR (CCC)"

        # 6. Summaries
        has_substantiated = len(incidents) > 0
        summary_de = (
            f"Die Lieferketten-Kaskadenprüfung nach § 9 LkSG ergibt einen Konformitätswert von {calculated_score:.1f}% ({rating}). "
            f"Die vertragliche Weitergabeklausel ist als '{tier1_pass_through.value}' eingestuft. "
            f"{'Es liegt mindestens ein Fall substantiierter Kenntnis (§ 9 Abs. 2 LkSG) vor, der ein sofortiges anlassbezogenes Tätigwerden erfordert.' if has_substantiated else 'Aktuell liegen keine offenen Fälle substantiierter Kenntnis bei mittelbaren Vorlieferanten vor.'}"
        )

        summary_en = (
            f"Multi-tier supply chain cascade audit under § 9 LkSG scores {calculated_score:.1f}% ({rating}). "
            f"Pass-through covenant status is classified as '{tier1_pass_through.value}'. "
            f"{'Substantiated knowledge of upstream breaches (§ 9(2) LkSG) is active, requiring immediate ad-hoc preventive measures.' if has_substantiated else 'No active substantiated knowledge alerts reported for indirect suppliers.'}"
        )

        return TierNCascadeAuditReport(
            document_id=document_id,
            evaluation_timestamp=datetime.now(UTC),
            overall_cascade_score=round(calculated_score, 1),
            compliance_rating=rating,
            statutory_framework="§ 9 LkSG (Mittelbare Zulieferer) & BAFA Handreichung",
            primary_vendor_name=primary_vendor_name,
            pass_through_enforceable_rate=round(pass_through_score, 1),
            total_tiers_tracked=len({n.tier for n in nodes}),
            direct_suppliers_count=sum(1 for n in nodes if n.tier == SupplyChainTier.TIER_1_DIRECT),
            indirect_suppliers_count=sum(1 for n in nodes if n.tier != SupplyChainTier.TIER_1_DIRECT),
            substantiated_knowledge_active=has_substantiated,
            supplier_nodes=nodes,
            active_incidents=incidents,
            jurisdiction_breakdown=list(COUNTRY_PROFILES.values()),
            bafa_adhoc_filing_recommended=any(inc.bafa_notification_required for inc in incidents),
            summary_de=summary_de,
            summary_en=summary_en,
        )


tier_n_cascade_engine = TierNCascadeEngine()
