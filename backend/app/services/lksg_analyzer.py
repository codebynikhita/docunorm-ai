import re
from typing import Literal
from uuid import UUID

from app.schemas.lksg import (
    LkSGAuditResponse,
    LkSGRiskCategory,
    LkSGRiskItem,
    LkSGSeverity,
    LkSGSupplierAssessment,
)


class LkSGAnalyzerService:
    """
    Statutory Supply Chain Due Diligence Analysis Engine for German & EU Mandates.
    Implements forensic compliance verification under:
    - Lieferkettensorgfaltspflichtengesetz (LkSG §§ 2-10)
    - BAFA Handreichungen zur Risikoanalyse & zum Beschwerdeverfahren
    - EU Corporate Sustainability Due Diligence Directive (CSDDD)
    """

    @classmethod
    def analyze_document(
        cls,
        document_id: UUID,
        filename: str,
        chunks: list[dict],
    ) -> LkSGAuditResponse:
        combined_text = " ".join(c.get("content", "") for c in chunks)
        lower_full = combined_text.lower()

        # Extract supplier name if detectable, else default from filename
        supplier_name = cls._extract_supplier_name(filename, combined_text)

        identified_risks: list[LkSGRiskItem] = []

        # -------------------------------------------------------------
        # 1. Human Rights Assessment (§ 2 Abs. 2 LkSG)
        # -------------------------------------------------------------
        # 1.1 Child Labor (§ 2 Abs. 2 Nr. 1 LkSG / ILO 138 & 182)
        hr_1 = cls._check_child_labor(chunks)
        if hr_1:
            identified_risks.append(hr_1)

        # 1.2 Forced Labor & Modern Slavery (§ 2 Abs. 2 Nr. 2 LkSG)
        hr_2 = cls._check_forced_labor(chunks)
        if hr_2:
            identified_risks.append(hr_2)

        # 1.3 Occupational Health & Safety (§ 2 Abs. 2 Nr. 5 LkSG)
        hr_3 = cls._check_occupational_safety(chunks)
        if hr_3:
            identified_risks.append(hr_3)

        # 1.4 Freedom of Association (§ 2 Abs. 2 Nr. 6 LkSG)
        hr_4 = cls._check_freedom_of_association(chunks)
        if hr_4:
            identified_risks.append(hr_4)

        # 1.5 Fair Wages & Equal Pay (§ 2 Abs. 2 Nr. 8 LkSG / MiLoG)
        hr_5 = cls._check_fair_wages(chunks)
        if hr_5:
            identified_risks.append(hr_5)

        # -------------------------------------------------------------
        # 2. Environmental Protection (§ 2 Abs. 3 LkSG)
        # -------------------------------------------------------------
        # 2.1 Minamata Convention (Mercury Prohibition)
        env_1 = cls._check_minamata(chunks)
        if env_1:
            identified_risks.append(env_1)

        # 2.2 Stockholm POPs Convention
        env_2 = cls._check_stockholm_pops(chunks)
        if env_2:
            identified_risks.append(env_2)

        # 2.3 Basel Convention (Hazardous Waste Export)
        env_3 = cls._check_basel_waste(chunks)
        if env_3:
            identified_risks.append(env_3)

        # -------------------------------------------------------------
        # 3. Governance, Complaints Procedure & BAFA Reporting (§§ 6-10 LkSG)
        # -------------------------------------------------------------
        # 3.1 Complaints Procedure (§ 8 LkSG)
        complaints_risk, has_complaints = cls._check_complaints_procedure(chunks)
        if complaints_risk:
            identified_risks.append(complaints_risk)

        # 3.2 Indirect Supplier Disclaimer Trap (§ 9 LkSG)
        indirect_risk = cls._check_indirect_suppliers(chunks)
        if indirect_risk:
            identified_risks.append(indirect_risk)

        # 3.3 BAFA Annual Reporting (§ 10 LkSG)
        bafa_risk, has_bafa_report = cls._check_bafa_reporting(chunks)
        if bafa_risk:
            identified_risks.append(bafa_risk)

        # Check Code of Conduct presence
        has_coc = any(
            k in lower_full
            for k in ["verhaltenskodex", "code of conduct", "lieferantenkodex", "menschenrechtskodex"]
        )

        # Check Audit rights presence
        has_audit_rights = any(
            k in lower_full
            for k in ["vor-ort-audit", "kontrollrecht", "inspektion", "prüfungsrecht", "audit-recht"]
        )

        # Calculate Scores
        critical_count = sum(1 for r in identified_risks if r.severity == LkSGSeverity.CRITICAL)
        high_count = sum(1 for r in identified_risks if r.severity == LkSGSeverity.HIGH)

        hr_penalty = sum(
            35 if r.severity == LkSGSeverity.CRITICAL else (20 if r.severity == LkSGSeverity.HIGH else 10)
            for r in identified_risks
            if r.category in [
                LkSGRiskCategory.CHILD_LABOR,
                LkSGRiskCategory.FORCED_LABOR,
                LkSGRiskCategory.OCCUPATIONAL_SAFETY,
                LkSGRiskCategory.FREEDOM_OF_ASSOCIATION,
                LkSGRiskCategory.DISCRIMINATION,
                LkSGRiskCategory.FAIR_WAGE,
            ]
        )
        human_rights_score = max(0.0, min(100.0, 100.0 - hr_penalty))

        env_penalty = sum(
            35 if r.severity == LkSGSeverity.CRITICAL else (20 if r.severity == LkSGSeverity.HIGH else 10)
            for r in identified_risks
            if r.category in [
                LkSGRiskCategory.ENVIRONMENT_MINAMATA,
                LkSGRiskCategory.ENVIRONMENT_POPS,
                LkSGRiskCategory.ENVIRONMENT_HAZARDOUS_WASTE,
            ]
        )
        environmental_score = max(0.0, min(100.0, 100.0 - env_penalty))

        gov_penalty = sum(
            35 if r.severity == LkSGSeverity.CRITICAL else (20 if r.severity == LkSGSeverity.HIGH else 10)
            for r in identified_risks
            if r.category in [
                LkSGRiskCategory.COMPLAINTS_PROCEDURE,
                LkSGRiskCategory.ANNUAL_REPORTING_BAFA,
                LkSGRiskCategory.INDIRECT_SUPPLIER_CONTROL,
            ]
        )
        governance_score = max(0.0, min(100.0, 100.0 - gov_penalty))

        overall_score = round(
            0.40 * human_rights_score + 0.30 * environmental_score + 0.30 * governance_score, 1
        )

        # Determine Institutional Rating
        rating = cls._determine_rating(overall_score, critical_count)

        exec_summary_de, exec_summary_en = cls._generate_executive_summary(
            supplier_name, overall_score, rating, critical_count, high_count, has_complaints, has_bafa_report
        )

        assessment = LkSGSupplierAssessment(
            supplier_name=supplier_name,
            supplier_tier="TIER_1_DIRECT",
            overall_compliance_score=overall_score,
            compliance_rating=rating,
            human_rights_score=human_rights_score,
            environmental_score=environmental_score,
            governance_score=governance_score,
            complaints_procedure_present=has_complaints,
            bafa_report_compliant=has_bafa_report,
            code_of_conduct_mandated=has_coc,
            audit_rights_granted=has_audit_rights,
            identified_risks=identified_risks,
            critical_risk_count=critical_count,
            high_risk_count=high_count,
            executive_summary_de=exec_summary_de,
            executive_summary_en=exec_summary_en,
        )

        return LkSGAuditResponse(
            document_id=document_id,
            filename=filename,
            assessment=assessment,
        )

    # -----------------------------------------------------------------
    # Forensic Statutory Rule Checks
    # -----------------------------------------------------------------

    @classmethod
    def _check_child_labor(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["kinderarbeit", "child labor", "mindestalter", "ilo 138"]):
                if any(k in lower for k in ["ausnahmsweise gestattet", "keine altersverifikation", "unter 15 jahren"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.CHILD_LABOR,
                        severity=LkSGSeverity.CRITICAL,
                        title_de="Kritisches Verbot von Kinderarbeit missachtet",
                        title_en="Critical Child Labor Prohibition Breach",
                        statutory_reference="§ 2 Abs. 2 Nr. 1 LkSG · ILO-Übereinkommen Nr. 138 & 182",
                        bafa_guideline_ref="BAFA Handreichung zur Risikoanalyse (Abschnitt 3.1)",
                        finding_de="Vertragliche Bestimmungen enthalten unzulässige Ausnahmen beim Verbot von Kinderarbeit oder verzichten auf eine wirksame Altersüberprüfung.",
                        finding_en="Contractual provisions contain inadmissible exceptions to the ban on child labor or omit effective age verification.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Strikte Null-Toleranz-Klausel bezüglich Kinderarbeit gem. ILO-Kernarbeitsnorm 138 aufnehmen und Ausweiskontrollen bei allen Zulieferern vorschreiben.",
                        remediation_action_en="Incorporate strict zero-tolerance clause regarding child labor under ILO Core Convention 138 and mandate age verification across all suppliers.",
                    )
        return None

    @classmethod
    def _check_forced_labor(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["zwangsarbeit", "forced labor", "einbehalt von ausweispapieren", "schuldknechtschaft"]):
                if any(k in lower for k in ["einbehalten", "rekrutierungsgebühren", "lohnrückbehalt"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.FORCED_LABOR,
                        severity=LkSGSeverity.CRITICAL,
                        title_de="Verdacht auf Zwangsarbeit oder Schuldknechtschaft",
                        title_en="Suspicion of Forced Labor or Debt Bondage",
                        statutory_reference="§ 2 Abs. 2 Nr. 2 & Nr. 4 LkSG · ILO-Übereinkommen Nr. 29",
                        bafa_guideline_ref="BAFA Handreichung zur Risikoanalyse (Abschnitt 3.2)",
                        finding_de="Klausel gestattet Lohnrückbehalte oder den Einbehalt von Reisedokumenten und Ausweispapieren ausländischer Wanderarbeiter.",
                        finding_en="Clause permits wage withholding or retention of identity documents belonging to migrant workers.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Klausel ersatzlos streichen; ausdrückliches Verbot der Einbehaltung von Reisedokumenten und Rekrutierungsgebühren vereinbaren.",
                        remediation_action_en="Strike clause immediately; mandate employer-pays principle for recruitment fees and ban identity document retention.",
                    )
        return None

    @classmethod
    def _check_occupational_safety(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["arbeitsschutz", "arbeitsplatzsicherheit", "occupational safety", "schutzkleidung"]):
                if any(k in lower for k in ["auf eigene kosten", "keine schutzkleidung", "entfällt die haftung"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.OCCUPATIONAL_SAFETY,
                        severity=LkSGSeverity.HIGH,
                        title_de="Mängel bei Arbeitssicherheit & Gesundheitsschutz",
                        title_en="Occupational Health & Safety Compliance Deficit",
                        statutory_reference="§ 2 Abs. 2 Nr. 5 LkSG · Arbeitsschutzgesetz (ArbSchG)",
                        bafa_guideline_ref="BAFA Handreichung zur Risikoanalyse (Abschnitt 3.5)",
                        finding_de="Kosten für persönliche Schutzausrüstung (PSA) oder Sicherheitstrainings werden unzulässig auf Arbeitnehmer überwälzt.",
                        finding_en="Costs for personal protective equipment (PPE) or mandatory safety training are impermissibly shifted to workers.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Verpflichtung des Lieferanten zur kostenfreien Bereitstellung genormter Schutzkleidung und regelmäßiger Sicherheitstrainings verankern.",
                        remediation_action_en="Mandate free provision of certified protective equipment and regular safety training sessions.",
                    )
        return None

    @classmethod
    def _check_freedom_of_association(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["gewerkschaft", "trade union", "koalitionsfreiheit", "betriebsrat"]):
                if any(k in lower for k in ["untersagt", "verboten", "ausschluss von arbeitnehmervertretungen"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.FREEDOM_OF_ASSOCIATION,
                        severity=LkSGSeverity.HIGH,
                        title_de="Verletzung der Koalitionsfreiheit & Gewerkschaftsrechte",
                        title_en="Violation of Freedom of Association & Collective Bargaining",
                        statutory_reference="§ 2 Abs. 2 Nr. 6 LkSG · ILO-Übereinkommen Nr. 87 & 98",
                        bafa_guideline_ref="BAFA Handreichung zur Risikoanalyse (Abschnitt 3.6)",
                        finding_de="Vertragliche Behinderung oder Verbot der gewerkschaftlichen Betätigung und Bildung freier Arbeitnehmervertretungen.",
                        finding_en="Contractual obstruction or ban on trade union activity and collective worker representation.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Anerkennung des Rechts auf freie gewerkschaftliche Organisation und Kollektivverhandlungen verbindlich vorschreiben.",
                        remediation_action_en="Mandate explicit recognition of worker rights to organize and negotiate collective bargaining agreements.",
                    )
        return None

    @classmethod
    def _check_fair_wages(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["mindestlohn", "angemessener lohn", "fair wage", "milog"]):
                if any(k in lower for k in ["unterschreitung zulässig", "abzüge unter den mindestlohn"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.FAIR_WAGE,
                        severity=LkSGSeverity.HIGH,
                        title_de="Unterschreitung des gesetzlichen Mindestlohns",
                        title_en="Violation of Statutory Minimum / Living Wage Mandate",
                        statutory_reference="§ 2 Abs. 2 Nr. 8 LkSG · Mindestlohngesetz (MiLoG)",
                        bafa_guideline_ref="BAFA Handreichung zur Risikoanalyse (Abschnitt 3.8)",
                        finding_de="Zulieferer behält sich Vergütungen unterhalb der gesetzlichen oder ortsüblichen Mindestlöhne vor.",
                        finding_en="Supplier reserves the right to pay remuneration below applicable statutory minimum wage standards.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Verbindliche Einhaltung des gesetzlichen Mindestlohns bzw. existenzsichernden Lohns ohne unzulässige Abzüge vertraglich vereinbaren.",
                        remediation_action_en="Contractually guarantee statutory minimum wages and living wages without unauthorized deductions.",
                    )
        return None

    @classmethod
    def _check_minamata(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["quecksilber", "mercury", "minamata"]):
                if any(k in lower for k in ["unbehandelt", "ungereinigt", "deponierung ohne filter"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.ENVIRONMENT_MINAMATA,
                        severity=LkSGSeverity.HIGH,
                        title_de="Umweltrisiko: Verstoß gegen das Minamata-Übereinkommen",
                        title_en="Environmental Risk: Minamata Mercury Convention Violation",
                        statutory_reference="§ 2 Abs. 3 Nr. 1 LkSG · Minamata-Übereinkommen über Quecksilber",
                        bafa_guideline_ref="BAFA Handreichung Umweltbezogene Sorgfaltspflichten (Abschnitt 4.1)",
                        finding_de="Unzureichende Vorkehrungen zur Behandlung oder Entsorgung von Quecksilberverbindungen.",
                        finding_en="Inadequate measures for the treatment or disposal of mercury and mercury compounds.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Zertifizierten Nachweis über quecksilberfreie Produktionsverfahren oder normgerechte Schadstoffrückhaltung fordern.",
                        remediation_action_en="Require certified proof of mercury-free manufacturing or compliant hazardous substance retention.",
                    )
        return None

    @classmethod
    def _check_stockholm_pops(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["stockholm", "persistente organische schadstoffe", "pops", "dieldrin", "aldrin"]):
                if any(k in lower for k in ["freisetzung", "einsatz zulässig", "ungefiltert"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.ENVIRONMENT_POPS,
                        severity=LkSGSeverity.HIGH,
                        title_de="Umweltrisiko: Einsatz persistenter organischer Schadstoffe (POPs)",
                        title_en="Environmental Risk: Persistent Organic Pollutants (POPs)",
                        statutory_reference="§ 2 Abs. 3 Nr. 2 LkSG · Stockholmer Übereinkommen (POPs)",
                        bafa_guideline_ref="BAFA Handreichung Umweltbezogene Sorgfaltspflichten (Abschnitt 4.2)",
                        finding_de="Einsatz oder Freisetzung völkerrechtlich verbotener persistenter organischer Schadstoffe.",
                        finding_en="Use or emission of internationally prohibited persistent organic pollutants.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Vollständige Dekontamination und Verzicht auf POP-haltige Vorprodukte vereinbaren.",
                        remediation_action_en="Mandate complete phase-out and substitution of all POP-containing preliminary substances.",
                    )
        return None

    @classmethod
    def _check_basel_waste(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["basel", "basler übereinkommen", "gefährliche abfälle", "hazardous waste export"]):
                if any(k in lower for k in ["export in nicht-oecd", "grenzüberschreitende verbringung ohne notifizierung"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.ENVIRONMENT_HAZARDOUS_WASTE,
                        severity=LkSGSeverity.HIGH,
                        title_de="Umweltrisiko: Illegale Verbringung gefährlicher Abfälle",
                        title_en="Environmental Risk: Transboundary Hazardous Waste Movement",
                        statutory_reference="§ 2 Abs. 3 Nr. 3 LkSG · Basler Übereinkommen",
                        bafa_guideline_ref="BAFA Handreichung Umweltbezogene Sorgfaltspflichten (Abschnitt 4.3)",
                        finding_de="Klausel gestattet den grenzüberschreitenden Export gefährlicher Abfälle ohne behördliche Notifizierung.",
                        finding_en="Clause permits transboundary movement of hazardous waste without statutory regulatory notification.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Striktes Verbot des Abfallexports in Nicht-OECD-Staaten und Vorlage lückenloser Entsorgungszertifikate.",
                        remediation_action_en="Enforce strict ban on waste export to non-OECD countries and require certified chain of custody.",
                    )
        return None

    @classmethod
    def _check_complaints_procedure(cls, chunks: list[dict]) -> tuple[LkSGRiskItem | None, bool]:
        combined = " ".join(c.get("content", "") for c in chunks).lower()
        has_positive = any(
            k in combined
            for k in [
                "beschwerdeverfahren ein",
                "beschwerdemechanismus ein",
                "whistleblower-system",
                "hinweisgebersystem ein",
                "zugängliches beschwerdeverfahren",
                "vertrauliches beschwerdeverfahren",
                "grievance mechanism",
                "einrichtung eines beschwerdeverfahrens",
            ]
        )
        has_negative = any(
            (neg in combined and term in combined)
            for neg in ["keine angaben", "kein beschwerdeverfahren", "entfällt das beschwerdeverfahren", "ohne hinweisgeber", "ohne beschwerde"]
            for term in ["beschwerde", "hinweisgeber", "whistleblower"]
        )

        has_channel = has_positive and not has_negative

        if not has_channel:
            first_chunk = chunks[0] if chunks else {}
            item = LkSGRiskItem(
                category=LkSGRiskCategory.COMPLAINTS_PROCEDURE,
                severity=LkSGSeverity.HIGH,
                title_de="Fehlendes oder unzureichendes Beschwerdeverfahren (§ 8 LkSG)",
                title_en="Absence of Statutory Complaints / Whistleblower Procedure (§ 8 LkSG)",
                statutory_reference="§ 8 LkSG (Beschwerdeverfahren) · Hinweisgeberschutzgesetz (HinSchG)",
                bafa_guideline_ref="BAFA Handreichung zum Beschwerdeverfahren (Abschnitt 2.1)",
                finding_de="Der Vertrag enthält keine vertragliche Verankerung des zwingend vorgeschriebenen Beschwerdeverfahrens für potentiell betroffene Personen entlang der Lieferkette.",
                finding_en="The contract omits mandatory integration of the statutory complaints procedure accessible to affected stakeholders throughout the supply chain.",
                evidence_snippet=first_chunk.get("content", "")[:250].strip(),
                page_number=first_chunk.get("page_number", 1),
                remediation_action_de="Einrichtung eines barrierefreien, vertraulichen Hinweisgeberkanals gem. § 8 LkSG vertraglich vorschreiben und Verfahrensordnung beifügen.",
                remediation_action_en="Contractually mandate confidential grievance mechanism under § 8 LkSG and attach rules of procedure.",
            )
            return item, False

        return None, True

    @classmethod
    def _check_indirect_suppliers(cls, chunks: list[dict]) -> LkSGRiskItem | None:
        for c in chunks:
            text = c.get("content", "")
            lower = text.lower()
            if any(k in lower for k in ["mittelbare zulieferer", "mittelbaren zulieferern", "indirect suppliers", "tier-n", "sub-supplier"]):
                if any(k in lower for k in ["dauerhaft", "ausgeschlossen", "entfällt", "keine sorgfaltspflicht", "verzichtet"]):
                    return LkSGRiskItem(
                        category=LkSGRiskCategory.INDIRECT_SUPPLIER_CONTROL,
                        severity=LkSGSeverity.CRITICAL,
                        title_de="Rechtswidriger Ausschluss von Sorgfaltspflichten bei mittelbaren Zulieferern",
                        title_en="Illegal Exclusion of Due Diligence for Indirect Tier-N Suppliers",
                        statutory_reference="§ 9 LkSG (Sorgfaltspflichten in Bezug auf mittelbare Zulieferer)",
                        bafa_guideline_ref="BAFA Handreichung zur Risikoanalyse (Abschnitt 5)",
                        finding_de="Klausel schließt mittelbare Zulieferer (Tier-2 bis Tier-N) dauerhaft und pauschal von der aufsichtsrechtlichen Risikoanalyse und anlassbezogenen Prüfpflicht aus.",
                        finding_en="Clause attempts to permanently waive statutory due diligence obligations and incident-based risk analyses for indirect Tier-N suppliers.",
                        evidence_snippet=text[:250].strip(),
                        page_number=c.get("page_number", 1),
                        remediation_action_de="Klausel streichen: Bei substanziierter Kenntnis von Verletzungen müssen anlassbezogene Risikoanalysen und Präventionskonzepte greifen (§ 9 Abs. 3 LkSG).",
                        remediation_action_en="Strike clause: Mandate incident-triggered risk assessment and preventative measures upon substantiated knowledge under § 9(3) LkSG.",
                    )
        return None

    @classmethod
    def _check_bafa_reporting(cls, chunks: list[dict]) -> tuple[LkSGRiskItem | None, bool]:
        combined = " ".join(c.get("content", "") for c in chunks).lower()
        has_bafa = any(
            k in combined
            for k in ["bafa-bericht", "bafa-menschenrechtsbericht", "bafa-berichterstattung", "jahresbericht gem. § 10", "31. märz"]
        )

        if not has_bafa or any(k in combined for k in ["keine berichterstattung an das bafa", "vertraulichkeitsvorbehalt gegen bafa"]):
            first_chunk = chunks[0] if chunks else {}
            item = LkSGRiskItem(
                category=LkSGRiskCategory.ANNUAL_REPORTING_BAFA,
                severity=LkSGSeverity.MEDIUM,
                title_de="Fehlende Mitwirkung an der jährlichen BAFA-Berichterstattung (§ 10 LkSG)",
                title_en="Omission of Cooperation for Annual BAFA Reporting Mandate (§ 10 LkSG)",
                statutory_reference="§ 10 LkSG (Dokumentations- und Berichtspflicht gegenüber BAFA)",
                bafa_guideline_ref="BAFA Handreichung zur Berichterstattung",
                finding_de="Der Zulieferer verpflichtet sich nicht zur Bereitstellung der für die jährliche BAFA-Berichterstattung (Frist: 31. März) erforderlichen Risiko- und Maßnahmennachweise.",
                finding_en="Supplier fails to contractually commit to providing required compliance telemetry for the annual BAFA due diligence filing (Due: March 31).",
                evidence_snippet=first_chunk.get("content", "")[:250].strip(),
                page_number=first_chunk.get("page_number", 1),
                remediation_action_de="Verpflichtung zur fristgerechten Zulieferung geprüfter Kennzahlen bis zum 31. Januar jedes Folgejahres aufnehmen.",
                remediation_action_en="Include clause mandating delivery of verified audit telemetry by January 31 of each subsequent reporting year.",
            )
            return item, False

        return None, True

    # -----------------------------------------------------------------
    # Helper & Scoring Logic
    # -----------------------------------------------------------------

    @classmethod
    def _extract_supplier_name(cls, filename: str, full_text: str) -> str:
        # Check for company names in first page
        for line in full_text.splitlines()[:15]:
            match = re.search(r"(?:Lieferant|Auftragnehmer|Dienstleister|Partner)[:\s]+([A-ZÄÖÜ][A-Za-z0-9\s.,&-]+(?:GmbH|AG|SE|KG|Inc|LLC|Ltd))", line)
            if match:
                return match.group(1).strip()

        # Clean fallback from filename
        clean = filename.replace(".pdf", "").replace("_", " ").replace("-", " ")
        return clean.strip() or "Lieferant / Auftragnehmer"

    @classmethod
    def _determine_rating(
        cls, score: float, critical_count: int
    ) -> Literal["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]:
        if critical_count > 0:
            return "CCC" if score < 60 else "B"
        if score >= 92.0:
            return "AAA"
        if score >= 82.0:
            return "AA"
        if score >= 72.0:
            return "A"
        if score >= 62.0:
            return "BBB"
        if score >= 52.0:
            return "BB"
        if score >= 42.0:
            return "B"
        return "CCC"

    @classmethod
    def _generate_executive_summary(
        cls,
        supplier_name: str,
        score: float,
        rating: str,
        critical_count: int,
        high_count: int,
        has_complaints: bool,
        has_bafa: bool,
    ) -> tuple[str, str]:
        if rating in ["AAA", "AA"]:
            de = (
                f"Der Vertrag mit '{supplier_name}' weist ein exzellentes Schutzniveau nach dem Lieferkettensorgfaltspflichtengesetz (LkSG) auf. "
                f"Mit einem Gesamtergebnis von {score}% ({rating}) sind die Kernarbeitsnormen der ILO, grundlegende Umweltschutzabkommen "
                f"sowie das gesetzliche Beschwerdeverfahren nach § 8 LkSG vorbildlich integriert. Der Vertrag ist revisionsfest gegenüber dem BAFA."
            )
            en = (
                f"The contract with '{supplier_name}' demonstrates institutional-grade compliance under the German Supply Chain Due Diligence Act (LkSG). "
                f"With an overall score of {score}% ({rating}), ILO core labor standards, multilateral environmental conventions, "
                f"and the § 8 LkSG complaints procedure are rigorously embedded. Revisionssicher for federal BAFA inspection."
            )
        elif rating in ["A", "BBB", "BB"]:
            de = (
                f"Der Vertrag mit '{supplier_name}' erreicht {score}% ({rating}) mit {high_count} verbesserungsbedürftigen Bereichen. "
                f"Es bestehen verfahrensbezogene Anpassungsbedarfe hinsichtlich der Transparenz oder Nachweisführung gegenüber der Aufsichtsbehörde (BAFA). "
                f"Eine formelle Nachbesserung wird empfohlen."
            )
            en = (
                f"The contract with '{supplier_name}' achieves {score}% ({rating}) with {high_count} areas requiring adjustment. "
                f"Procedural remediation is advised regarding documentation depth and regulatory reporting transparency for BAFA."
            )
        else:
            de = (
                f"AKUTER HANDLUNGSBEDARF: Der Vertrag mit '{supplier_name}' weist mit {score}% ({rating}) {critical_count} kritische "
                f"Verstöße gegen zwingendes deutsches Sorgfaltsrecht auf. Es drohen behördliche Zwangsgelder des BAFA sowie der Ausschluss von "
                f"öffentlichen Vergabeverfahren gem. § 22 LkSG. Unverzügliche Nachverhandlung zwingend erforderlich."
            )
            en = (
                f"CRITICAL REMEDIATION REQUIRED: The agreement with '{supplier_name}' rates at {score}% ({rating}) with {critical_count} critical "
                f"breaches of statutory German supply chain mandates. Exposure to BAFA administrative fines and exclusion from public procurement "
                f"under § 22 LkSG exists. Immediate renegotiation is required."
            )

        return de, en
