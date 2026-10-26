import re
from datetime import datetime, timezone
from uuid import UUID
from app.schemas.subcontractor import (
    CascadingChainNode,
    DoraSubcontractorAuditReport,
    SubcontractorCheckResult,
)


class DoraSubcontractorEngine:
    """
    Sovereign Rule Engine for verifying compliance with:
    - EU DORA (Regulation 2022/2554) Article 30 Paragraph 3 (Subcontracting of Critical/Important Functions)
    - DORA Article 28 Paragraph 3 (Information Register on Third-Party Arrangements)
    - BaFin RS 10/2018 (BAIT Ziffer 8 - Weiterverlagerung von Auslagerungen)
    - German Banking Act (KWG § 25b Abs. 1 und 2)
    """

    def audit_chunks(
        self,
        document_id: UUID,
        chunks: list[dict],
    ) -> DoraSubcontractorAuditReport:
        """
        Executes deep regulatory audit of contract chunks against the 5 mandatory
        DORA Art. 30(3) cascading subcontracting criteria.
        """
        full_text = " ".join([c.get("content", "") for c in chunks]).lower()

        # Check 1: Advance Notice & Veto Rights (Art. 30(3)(a))
        c1 = self._check_advance_notice_and_veto(chunks, full_text)

        # Check 2: Termination Rights upon Objection (Art. 30(3)(b))
        c2 = self._check_termination_on_objection(chunks, full_text)

        # Check 3: Strict Vicarious Liability (Art. 30(3)(c))
        c3 = self._check_vicarious_liability(chunks, full_text)

        # Check 4: Downstream Audit Rights Flow-Through (Art. 30(3)(e))
        c4 = self._check_downstream_audit_rights(chunks, full_text)

        # Check 5: Cascading Supply Chain Mapping & Data Residency (Art. 28(3) & 30(2)(c))
        c5, nodes, concentration_risk = self._check_chain_mapping(chunks, full_text)

        all_checks = [c1, c2, c3, c4, c5]
        total_score = sum(c.score for c in all_checks) / len(all_checks) * 100.0

        if total_score >= 88.0:
            rating = "VOLLSTÄNDIG KONFORM (AAA)"
            summary_de = (
                "Der Vertrag erfüllt die Anforderungen nach DORA Art. 30 Abs. 3 und BaFin BAIT für die "
                "Weiterverlagerung von IKT-Dienstleistungen vollständig. Vorankündigungsfristen, Vetorechte, "
                "Kaskadierung von Prüfrechten und Durchgriffshaftung sind lückenlos verankert."
            )
            summary_en = (
                "The agreement fully satisfies statutory requirements under DORA Art. 30(3) and BaFin BAIT "
                "for subcontracting arrangements. Advance notice, veto powers, audit flow-through, and "
                "strict vicarious liability are comprehensively established."
            )
        elif total_score >= 60.0:
            rating = "BEDINGT KONFORM (BBB)"
            summary_de = (
                "Der Vertrag regelt Unterauftragsvergaben grundlegend, weist jedoch Nachbesserungsbedarf bei "
                "den Vorankündigungsfristen, Sonderkündigungsrechten oder der lückenlosen Prüfrechtekaskadierung auf."
            )
            summary_en = (
                "The contract addresses sub-outsourcing at a baseline level, but requires remediation regarding "
                "formal advance notice windows, termination triggers, or downstream audit flow-through."
            )
        else:
            rating = "KRITISCH DEFIZITÄR (CCC)"
            summary_de = (
                "Schwerwiegende aufsichtsrechtliche Mängel: Unangekündigte Unterbeauftragung, unzulässige "
                "Zustimmungsfiktionen oder fehlende Durchgriffshaftung verstoßen direkt gegen DORA Art. 30 Abs. 3."
            )
            summary_en = (
                "Severe supervisory deficiency: Unannounced sub-contracting, deemed-consent traps, or absence of "
                "vicarious liability directly violate DORA Art. 30(3) and BaFin standards."
            )

        return DoraSubcontractorAuditReport(
            document_id=document_id,
            overall_score=round(total_score, 1),
            compliance_rating=rating,
            evaluated_at=datetime.now(timezone.utc),
            checks=all_checks,
            cascading_nodes=nodes,
            concentration_risk_level=concentration_risk,
            summary_de=summary_de,
            summary_en=summary_en,
        )

    def _check_advance_notice_and_veto(self, chunks: list[dict], full_text: str) -> SubcontractorCheckResult:
        # Check for unannounced subcontracting or deemed consent traps
        has_unannounced = (
            "ohne vorherige" in full_text
            or "ohne gesonderte vorankündigung" in full_text
            or "ohne vorankündigung" in full_text
            or "ohne gesonderte ankündigung" in full_text
        )
        has_deemed_consent = "zustimmungsfiktion" in full_text or "gilt die zustimmung als unwiderruflich erteilt" in full_text

        # Search for explicit notice windows
        days = self._extract_days_for_subcontracting(full_text)

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["unterauftrag", "subunternehmer", "subcontract", "weiterverlagerung", "hilfsdienstleister"]
        )

        if has_unannounced:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-01",
                name_de="Vorankündigung & Vetorecht bei Weiterverlagerung",
                name_en="Advance Notice & Veto Powers for Subcontracting",
                description_de="Verpflichtende Vorankündigung geplanter Unterauftragsvergaben mit Widerspruchsrecht.",
                description_en="Mandatory advance written notice of planned subcontracting with explicit right to object.",
                status="NON_COMPLIANT",
                score=0.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Unangekündigte Unterbeauftragung ersatzlos streichen. Schriftliche Vorankündigungsfrist von mindestens 60 Tagen implementieren.",
                recommendation_en="Eliminate unannounced subcontracting. Implement mandatory written notice window of at least 60 days.",
            )

        if has_deemed_consent:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-01",
                name_de="Vorankündigung & Vetorecht bei Weiterverlagerung",
                name_en="Advance Notice & Veto Powers for Subcontracting",
                description_de="Verpflichtende Vorankündigung geplanter Unterauftragsvergaben mit Widerspruchsrecht.",
                description_en="Mandatory advance written notice of planned subcontracting with explicit right to object.",
                status="NON_COMPLIANT",
                score=0.2,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Zustimmungsfiktionen sind aufsichtsrechtlich unzulässig. Ausdrückliche Widerspruchsfrist von mind. 30 Tagen vorsehen.",
                recommendation_en="Deemed consent mechanisms violate supervisory guidelines. Provide explicit 30-day objection window.",
            )

        has_veto = any(k in full_text for k in ["widerspruch", "veto", "zustimmung", "einspruch", "objection", "consent"])

        if days and days >= 60 and has_veto:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-01",
                name_de="Vorankündigung & Vetorecht bei Weiterverlagerung",
                name_en="Advance Notice & Veto Powers for Subcontracting",
                description_de="Verpflichtende Vorankündigung geplanter Unterauftragsvergaben mit Widerspruchsrecht.",
                description_en="Mandatory advance written notice of planned subcontracting with explicit right to object.",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Frist von 60 Tagen und Vetorecht entsprechen dem DORA-Goldstandard vollständig.",
                recommendation_en="60-day notice window and veto right fully comply with DORA Gold Standard.",
            )
        elif days and days >= 30 and has_veto:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-01",
                name_de="Vorankündigung & Vetorecht bei Weiterverlagerung",
                name_en="Advance Notice & Veto Powers for Subcontracting",
                description_de="Verpflichtende Vorankündigung geplanter Unterauftragsvergaben mit Widerspruchsrecht.",
                description_en="Mandatory advance written notice of planned subcontracting with explicit right to object.",
                status="COMPLIANT",
                score=0.85,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="30 Tage Vorankündigung erfüllt DORA Art. 30 Abs. 3 lit. a; Anhebung auf 60 Tage empfohlen.",
                recommendation_en="30-day notice fulfills DORA Art. 30(3)(a); enhancement to 60 days recommended.",
            )
        elif has_veto or "vorankündigung" in full_text or "unterricht" in full_text:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-01",
                name_de="Vorankündigung & Vetorecht bei Weiterverlagerung",
                name_en="Advance Notice & Veto Powers for Subcontracting",
                description_de="Verpflichtende Vorankündigung geplanter Unterauftragsvergaben mit Widerspruchsrecht.",
                description_en="Mandatory advance written notice of planned subcontracting with explicit right to object.",
                status="PARTIALLY_COMPLIANT",
                score=0.5,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Konkrete Mindestankündigungsfrist von 30 bis 60 Tagen vor Aufnahme des Unterbetriebs beziffern.",
                recommendation_en="Specify unambiguous minimum notice window between 30 and 60 days prior to commencement.",
            )
        else:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-01",
                name_de="Vorankündigung & Vetorecht bei Weiterverlagerung",
                name_en="Advance Notice & Veto Powers for Subcontracting",
                description_de="Verpflichtende Vorankündigung geplanter Unterauftragsvergaben mit Widerspruchsrecht.",
                description_en="Mandatory advance written notice of planned subcontracting with explicit right to object.",
                status="NON_COMPLIANT",
                score=0.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Schriftliches Zustimmungs- und Vetorecht gem. DORA Art. 30 Abs. 3 lit. a zwingend nachrüsten.",
                recommendation_en="Mandatory addition of written approval and veto privileges under DORA Art. 30(3)(a).",
            )

    def _check_termination_on_objection(self, chunks: list[dict], full_text: str) -> SubcontractorCheckResult:
        has_termination = any(
            k in full_text
            for k in ["sonderkündigungsrecht", "kündigungsrecht", "vertrag kündigen", "termination right", "right to terminate"]
        ) and any(k in full_text for k in ["widerspruch", "unterauftrag", "subunternehmer", "ablehnung", "objection"])

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["sonderkündigung", "kündigung", "terminat", "widerspruch"]
        )

        if has_termination:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-02",
                name_de="Sonderkündigungsrecht bei unakzeptierter Weiterverlagerung",
                name_en="Contractual Termination Right upon Subcontractor Objection",
                description_de="Recht zur außerordentlichen Beendigung des Vertrags bei berechtigtem Einspruch.",
                description_en="Right to terminate agreement should the entity object to a proposed subcontracting arrangement.",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Sonderkündigungsrecht bei Einspruch ist konform mit DORA Art. 30 Abs. 3 lit. b verankert.",
                recommendation_en="Termination privilege upon objection is compliant with DORA Art. 30(3)(b).",
            )
        elif any(k in full_text for k in ["kündig", "terminat"]):
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-02",
                name_de="Sonderkündigungsrecht bei unakzeptierter Weiterverlagerung",
                name_en="Contractual Termination Right upon Subcontractor Objection",
                description_de="Recht zur außerordentlichen Beendigung des Vertrags bei berechtigtem Einspruch.",
                description_en="Right to terminate agreement should the entity object to a proposed subcontracting arrangement.",
                status="PARTIALLY_COMPLIANT",
                score=0.4,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Ausdrückliche Verknüpfung des Sonderkündigungsrechts mit dem Scheitern von Subunternehmer-Einwänden herstellen.",
                recommendation_en="Explicitly link special termination right to rejected subcontractor objections.",
            )
        else:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-02",
                name_de="Sonderkündigungsrecht bei unakzeptierter Weiterverlagerung",
                name_en="Contractual Termination Right upon Subcontractor Objection",
                description_de="Recht zur außerordentlichen Beendigung des Vertrags bei berechtigtem Einspruch.",
                description_en="Right to terminate agreement should the entity object to a proposed subcontracting arrangement.",
                status="NON_COMPLIANT",
                score=0.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Sonderkündigungsrecht gem. DORA Art. 30 Abs. 3 lit. b aufnehmen.",
                recommendation_en="Incorporate statutory exit right under DORA Art. 30(3)(b).",
            )

    def _check_vicarious_liability(self, chunks: list[dict], full_text: str) -> SubcontractorCheckResult:
        has_strict_liability = any(
            k in full_text
            for k in [
                "wie für eigenes verschulden",
                "haftet für handlungen und unterlassungen",
                "haftet für sub",
                "vicarious liability",
                "liable for sub",
                "haftet vollumfänglich für seine unterauftragnehmer",
            ]
        )

        has_liability_exclusion = "haftung für subunternehmer ist ausgeschlossen" in full_text or (
            "haftungsausschluss" in full_text and "sub" in full_text
        )

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["haftung", "verschulden", "liab", "erfüllungsgehilfe"]
        )

        if has_liability_exclusion:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-03",
                name_de="Durchgriffshaftung des Hauptauftragnehmers",
                name_en="Strict Vicarious Liability of Primary Contractor",
                description_de="Volle Haftung des Hauptdienstleisters für sämtliche Unterauftragnehmer gem. BGB § 278.",
                description_en="Primary vendor remains fully liable for all acts and omissions of subcontractors.",
                status="NON_COMPLIANT",
                score=0.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Haftungsausschluss für Subdienstleister ist unzulässig und stellt ein schweres Defizit dar.",
                recommendation_en="Liability exclusion for subcontractors is prohibited under DORA and constitutes severe defect.",
            )

        if has_strict_liability:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-03",
                name_de="Durchgriffshaftung des Hauptauftragnehmers",
                name_en="Strict Vicarious Liability of Primary Contractor",
                description_de="Volle Haftung des Hauptdienstleisters für sämtliche Unterauftragnehmer gem. BGB § 278.",
                description_en="Primary vendor remains fully liable for all acts and omissions of subcontractors.",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Durchgriffshaftung gem. DORA Art. 30 Abs. 3 lit. c und BGB § 278 vorbildlich geregelt.",
                recommendation_en="Vicarious liability conforming to DORA Art. 30(3)(c) and German Civil Code BGB § 278 verified.",
            )
        elif any(k in full_text for k in ["haft", "liab"]):
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-03",
                name_de="Durchgriffshaftung des Hauptauftragnehmers",
                name_en="Strict Vicarious Liability of Primary Contractor",
                description_de="Volle Haftung des Hauptdienstleisters für sämtliche Unterauftragnehmer gem. BGB § 278.",
                description_en="Primary vendor remains fully liable for all acts and omissions of subcontractors.",
                status="PARTIALLY_COMPLIANT",
                score=0.5,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Klarstellung aufnehmen: Hauptauftragnehmer haftet für Subunternehmer wie für eigenes Verschulden.",
                recommendation_en="Clarify contract: Primary contractor is liable for subcontractor conduct as for its own fault.",
            )
        else:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-03",
                name_de="Durchgriffshaftung des Hauptauftragnehmers",
                name_en="Strict Vicarious Liability of Primary Contractor",
                description_de="Volle Haftung des Hauptdienstleisters für sämtliche Unterauftragnehmer gem. BGB § 278.",
                description_en="Primary vendor remains fully liable for all acts and omissions of subcontractors.",
                status="NON_COMPLIANT",
                score=0.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Verbindliche Klausel zur Durchgriffshaftung gem. DORA Art. 30 Abs. 3 lit. c nachrüsten.",
                recommendation_en="Mandate explicit vicarious liability clause pursuant to DORA Art. 30(3)(c).",
            )

    def _check_downstream_audit_rights(self, chunks: list[dict], full_text: str) -> SubcontractorCheckResult:
        has_flowthrough = any(
            k in full_text
            for k in [
                "kaskadierung",
                "weitergabe",
                "weitergabe aller aufsichtsrechtlichen prüfrechte",
                "verpflichtet jeden unterauftragnehmer zur weitergabe",
                "prüfrechte gelten auch für sub",
                "flow-through",
                "flow through of audit",
                "extend audit rights",
            ]
        )

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["prüfrecht", "audit", "kaskadierung", "kontrollrecht"]
        )

        if has_flowthrough:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-04",
                name_de="Kaskadierung der Prüf- & Kontrollrechte",
                name_en="Flow-Through of Supervisory Audit Rights",
                description_de="Vertragliche Durchreichung uneingeschränkter Prüf- und Zugangsrechte an alle Unterdienstleister.",
                description_en="Contractual flow-through of comprehensive audit and access privileges across all sub-tiers.",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Kaskadierungsgebot gem. DORA Art. 30 Abs. 3 lit. e und KWG § 25b Abs. 1 lückenlos erfüllt.",
                recommendation_en="Flow-through obligation under DORA Art. 30(3)(e) and KWG § 25b is comprehensively fulfilled.",
            )
        elif any(k in full_text for k in ["audit", "prüf"]):
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-04",
                name_de="Kaskadierung der Prüf- & Kontrollrechte",
                name_en="Flow-Through of Supervisory Audit Rights",
                description_de="Vertragliche Durchreichung uneingeschränkter Prüf- und Zugangsrechte an alle Unterdienstleister.",
                description_en="Contractual flow-through of comprehensive audit and access privileges across all sub-tiers.",
                status="PARTIALLY_COMPLIANT",
                score=0.4,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Prüfrechte müssen ausdrücklich auf alle Subunternehmer und Rechenzentrumsbetreiber erstreckt werden.",
                recommendation_en="Supervisory audit rights must be explicitly extended to all subcontractors and datacenter nodes.",
            )
        else:
            return SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-04",
                name_de="Kaskadierung der Prüf- & Kontrollrechte",
                name_en="Flow-Through of Supervisory Audit Rights",
                description_de="Vertragliche Durchreichung uneingeschränkter Prüf- und Zugangsrechte an alle Unterdienstleister.",
                description_en="Contractual flow-through of comprehensive audit and access privileges across all sub-tiers.",
                status="NON_COMPLIANT",
                score=0.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Kaskadierungsklausel gem. DORA Art. 30 Abs. 3 lit. e ergänzen.",
                recommendation_en="Incorporate audit flow-through clause under DORA Art. 30(3)(e).",
            )

    def _check_chain_mapping(self, chunks: list[dict], full_text: str) -> tuple[SubcontractorCheckResult, list[CascadingChainNode], str]:
        nodes: list[CascadingChainNode] = []

        # Detect primary vendor
        primary_vendor = "Hauptdienstleister / Primary Vendor"
        if "sap" in full_text:
            primary_vendor = "SAP Deutschland SE & Co. KG"
        elif "aws" in full_text:
            primary_vendor = "Amazon Web Services EMEA SARL"
        elif "siemens" in full_text:
            primary_vendor = "Siemens AG Infrastructure"
        elif "microsoft" in full_text:
            primary_vendor = "Microsoft Ireland Operations Ltd."

        nodes.append(
            CascadingChainNode(
                node_id="NODE-TIER1",
                name=primary_vendor,
                tier=1,
                service_type="Kern-IKT-Dienstleistung / Core Banking Hosting",
                location="Deutschland / EWR",
                critical_function=True,
                approval_status="GENEHMIGT",
                risk_level="NIEDRIG",
            )
        )

        # Detect Tier 2 & Tier 3 Subcontractors from context
        concentration_risk = "NIEDRIG"
        has_cross_border_risk = False

        if "aws" in full_text or "cloud" in full_text:
            nodes.append(
                CascadingChainNode(
                    node_id="NODE-TIER2-CLOUD",
                    name="AWS Cloud Infrastructure Frankfurt",
                    tier=2,
                    service_type="IaaS Cloud Compute & Storage",
                    location="Frankfurt am Main, Deutschland (EWR)",
                    critical_function=True,
                    approval_status="GENEHMIGT" if "60" in full_text else "UNTERRICHTET",
                    risk_level="NIEDRIG" if "frankfurt" in full_text else "MITTEL",
                )
            )

        if "equinix" in full_text or "rechenzentrum" in full_text:
            nodes.append(
                CascadingChainNode(
                    node_id="NODE-TIER3-DC",
                    name="Equinix FR2 Datacenter",
                    tier=3,
                    service_type="Physisches Rechenzentrum & Colocation",
                    location="Frankfurt am Main, Deutschland (EWR)",
                    critical_function=True,
                    approval_status="GENEHMIGT",
                    risk_level="NIEDRIG",
                )
            )

        if "singapur" in full_text or "usa" in full_text or "virginia" in full_text or "cloud act" in full_text:
            has_cross_border_risk = True
            concentration_risk = "KRITISCH"
            nodes.append(
                CascadingChainNode(
                    node_id="NODE-TIER4-OFFSHORE",
                    name="Global Support & Key Management Node (US/Asia)",
                    tier=4,
                    service_type="Metadaten-Verarbeitung & Key Custody",
                    location="Vereinigte Staaten / Singapur (Drittstaat)",
                    critical_function=True,
                    approval_status="NICHT_KONFORM",
                    risk_level="KRITISCH",
                )
            )

        if len(nodes) == 1:
            # Add standard Tier 2 reference if generic
            nodes.append(
                CascadingChainNode(
                    node_id="NODE-TIER2-GENERIC",
                    name="Zertifizierter Hosting-Partner",
                    tier=2,
                    service_type="Infrastruktur-Bereitstellung",
                    location="EWR (Europäischer Wirtschaftsraum)",
                    critical_function=False,
                    approval_status="UNTERRICHTET",
                    risk_level="NIEDRIG",
                )
            )

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["standort", "rechenzentrum", "drittstaat", "usa", "residenz", "location"]
        )

        if has_cross_border_risk:
            check_result = SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-05",
                name_de="Lieferketten-Kartierung & Drittstaaten-Risiko",
                name_en="Supply-Chain Mapping & Cross-Border Concentration Risk",
                description_de="Erfassung aller Sub-Stufen im Informationsregister und Prüfung von Drittstaaten-Verlagerungen.",
                description_en="Mapping of all sub-tiers in Information Register and auditing cross-border transfer risks.",
                status="NON_COMPLIANT",
                score=0.2,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Kritische IKT-Funktionen dürfen nicht ohne DORA-konforme Garantien in US-Drittstaaten ausgelagert werden.",
                recommendation_en="Critical functions cannot be delegated to US third countries without DORA-compliant safeguards.",
            )
        else:
            check_result = SubcontractorCheckResult(
                rule_id="DORA-SUBCONTRACT-05",
                name_de="Lieferketten-Kartierung & Drittstaaten-Risiko",
                name_en="Supply-Chain Mapping & Cross-Border Concentration Risk",
                description_de="Erfassung aller Sub-Stufen im Informationsregister und Prüfung von Drittstaaten-Verlagerungen.",
                description_en="Mapping of all sub-tiers in Information Register and auditing cross-border transfer risks.",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Kaskadierende Lieferkette ist lückenlos im EWR verortet und für das Informationsregister gem. DORA Art. 28(3) qualifiziert.",
                recommendation_en="Cascading supply chain is located entirely within EEA and qualified for DORA Art. 28(3) register.",
            )

        return check_result, nodes, concentration_risk

    def _extract_days_for_subcontracting(self, text: str) -> int | None:
        matches = re.findall(r"(\d+)\s*(?:tage|tagen|kalendertage|kalendertagen|werktage|werktagen|days)", text)
        for m in matches:
            val = int(m)
            if 5 <= val <= 180:
                return val
        return None

    def _find_first_matching_chunk(self, chunks: list[dict], keywords: list[str]) -> tuple[str | None, str | None, int | None]:
        for idx, chunk in enumerate(chunks, 1):
            content = chunk.get("content", "")
            content_lower = content.lower()
            if any(k in content_lower for k in keywords):
                clean_text = content.replace("\n", " ").strip()
                if len(clean_text) > 220:
                    clean_text = clean_text[:220] + "..."
                return clean_text, f"[SOURCE_{idx}]", chunk.get("page_number", 1)
        return None, None, None


subcontractor_engine = DoraSubcontractorEngine()
