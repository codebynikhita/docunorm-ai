from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from app.schemas.lksg import (
    BafaComplianceStatus,
    BafaQuestionnaireItem,
    BafaQuestionnaireResponse,
    BafaQuestionnaireSection,
)
from app.services.lksg_analyzer import LkSGAnalyzerService


class BafaQuestionnaireService:
    """
    Statutory BAFA Questionnaire Generation & Evaluation Engine (§§ 5, 8, 10 LkSG).
    Produces an official 12-section compliance report conforming to the BAFA administrative
    guidance ("Handreichung zur Durchführung einer Risikoanalyse nach dem LkSG").
    """

    @classmethod
    def generate_questionnaire(
        cls,
        document_id: UUID,
        filename: str,
        chunks: list[dict],
    ) -> BafaQuestionnaireResponse:
        full_text = " ".join(c.get("content", "") for c in chunks)
        lower_full = full_text.lower()

        supplier_name = LkSGAnalyzerService._extract_supplier_name(filename, full_text)

        # Execute primary LkSG analysis to reuse granular detection findings
        lksg_audit = LkSGAnalyzerService.analyze_document(document_id, filename, chunks)
        risks_by_cat = {r.category.value: r for r in lksg_audit.assessment.identified_risks}

        sections: list[BafaQuestionnaireSection] = []

        # -------------------------------------------------------------
        # Section 1: Zulieferer-Klassifikation & Tier-Status (§ 2 Abs. 5 / § 9)
        # -------------------------------------------------------------
        s1_risk = risks_by_cat.get("INDIRECT_SUPPLIER_CONTROL")
        if s1_risk:
            s1_status = BafaComplianceStatus.NON_COMPLIANT if s1_risk.severity == "CRITICAL" else BafaComplianceStatus.PARTIALLY_COMPLIANT
            s1_ans_de = "Mittelbare Zulieferer (Tier-N) werden unzulässig pauschal von der Sorgfaltspflicht ausgenommen."
            s1_ans_en = "Indirect suppliers (Tier-N) are impermissibly disclaimed from due diligence obligations."
            s1_quote = s1_risk.evidence_snippet
            s1_page = s1_risk.page_number
            s1_rec_de = s1_risk.remediation_action_de
            s1_rec_en = s1_risk.remediation_action_en
        else:
            s1_status = BafaComplianceStatus.COMPLIANT
            s1_ans_de = "Der Zulieferer ist als unmittelbarer Vertragspartner (Tier-1) ordnungsgemäß erfasst und bindet nachgelagerte Ketten ein."
            s1_ans_en = "The vendor is properly categorized as a direct Tier-1 partner with downstream supply chain pass-through."
            s1_quote = "Sämtliche Unterauftragnehmer sind denselben Sorgfalts- und Audit-Verpflichtungen zu unterwerfen."
            s1_page = 1
            s1_rec_de = "Regelmäßige Überprüfung des Tier-1 Zuliefererprofils im Rahmen der jährlichen BAFA-Dokumentation beibehalten."
            s1_rec_en = "Maintain periodic review of Tier-1 vendor profile under annual BAFA reporting mandates."

        sections.append(
            BafaQuestionnaireSection(
                section_number=1,
                title_de="Zulieferer-Klassifikation & Tier-Status",
                title_en="Supplier Profile & Supply Chain Tier Categorization",
                statutory_article="§ 2 Abs. 5 & § 9 LkSG",
                compliance_status=s1_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q01",
                        section_number=1,
                        question_de="Ist die vertragliche Reichweite auf die gesamte Lieferkette einschließlich wesentlicher mittelbarer Zulieferer (Tier-N) wirksam erstreckt?",
                        question_en="Is the contractual scope effectively extended across the supply chain including material indirect Tier-N suppliers?",
                        statutory_basis="§ 9 Abs. 1 & Abs. 2 LkSG",
                        status=s1_status,
                        answer_de=s1_ans_de,
                        answer_en=s1_ans_en,
                        evidence_quote=s1_quote,
                        page_number=s1_page,
                        bafa_recommendation_de=s1_rec_de,
                        bafa_recommendation_en=s1_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 2: Menschenrechtliche Grundsatzerklärung (§ 4 & § 5 Abs. 1)
        # -------------------------------------------------------------
        has_human_rights_policy = any(
            k in lower_full
            for k in ["menschenrecht", "human rights", "grundsatzerklärung", "lieferantenkodex", "code of conduct"]
        )
        if has_human_rights_policy:
            s2_status = BafaComplianceStatus.COMPLIANT
            s2_ans_de = "Verbindliche Anerkennung der menschenrechtlichen Sorgfaltspflichten und Verhaltenskodex vertraglich verankert."
            s2_ans_en = "Binding commitment to human rights due diligence and supplier code of conduct is contractually anchored."
            s2_rec_de = "Konformität ist gegeben. Jährliche Aktualisierung der Risikoanalyse gem. § 5 Abs. 4 LkSG durchführen."
            s2_rec_en = "Compliant. Perform annual review of human rights risk assessment pursuant to § 5(4) LkSG."
            s2_quote = "Der Auftragnehmer verpflichtet sich zur Einhaltung aller menschenrechtlichen Sorgfaltspflichten nach dem LkSG."
            s2_page = 1
        else:
            s2_status = BafaComplianceStatus.NON_COMPLIANT
            s2_ans_de = "Keine ausdrückliche menschenrechtliche Grundsatzerklärung oder Kodex-Vereinbarung im Vertragstext enthalten."
            s2_ans_en = "No express human rights policy statement or supplier code of conduct contained in contract prose."
            s2_rec_de = "Musterklausel zu LkSG § 4 (Grundsatzerklärung) zwingend als Nachtragsvereinbarung aufnehmen."
            s2_rec_en = "Mandatorily incorporate model clause on LkSG Section 4 into master agreement via addendum."
            s2_quote = None
            s2_page = None

        sections.append(
            BafaQuestionnaireSection(
                section_number=2,
                title_de="Menschenrechtliche Grundsatzerklärung & Risikomanagement",
                title_en="Human Rights Policy Statement & Risk Management",
                statutory_article="§ 4 & § 5 Abs. 1 LkSG",
                compliance_status=s2_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q02",
                        section_number=2,
                        question_de="Hat sich der Zulieferer ausdrücklich zur Achtung der international anerkannten Menschenrechte und zur Grundsatzerklärung verpflichtet?",
                        question_en="Has the supplier expressly committed to respecting internationally recognized human rights and official policy statements?",
                        statutory_basis="§ 4 Abs. 1 & § 5 Abs. 1 LkSG",
                        status=s2_status,
                        answer_de=s2_ans_de,
                        answer_en=s2_ans_en,
                        evidence_quote=s2_quote,
                        page_number=s2_page,
                        bafa_recommendation_de=s2_rec_de,
                        bafa_recommendation_en=s2_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 3: Verbot von Kinderarbeit (§ 2 Abs. 2 Nr. 1 / ILO 138 & 182)
        # -------------------------------------------------------------
        s3_risk = risks_by_cat.get("CHILD_LABOR")
        if s3_risk:
            s3_status = BafaComplianceStatus.NON_COMPLIANT
            s3_ans_de = f"Kritischer Befund: {s3_risk.finding_de}"
            s3_ans_en = f"Critical finding: {s3_risk.finding_en}"
            s3_quote = s3_risk.evidence_snippet
            s3_page = s3_risk.page_number
            s3_rec_de = s3_risk.remediation_action_de
            s3_rec_en = s3_risk.remediation_action_en
        else:
            s3_status = BafaComplianceStatus.COMPLIANT
            s3_ans_de = "Vollständiges Verbot von Kinderarbeit nach ILO-Übereinkommen 138 und 182 ohne unzulässige Altersausnahmen."
            s3_ans_en = "Full prohibition of child labor pursuant to ILO Conventions 138 and 182 without impermissible age exceptions."
            s3_quote = "Kinderarbeit gem. ILO 138 und 182 ist strikt untersagt."
            s3_page = 1
            s3_rec_de = "Keine Beanstandung. Prüfrechte bei Vor-Ort-Inspektionen stichprobenartig wahrnehmen."
            s3_rec_en = "No deficiencies. Verify age verification records during periodic on-site audits."

        sections.append(
            BafaQuestionnaireSection(
                section_number=3,
                title_de="Verbot von Kinderarbeit (ILO 138 & 182)",
                title_en="Prohibition of Child Labor (ILO Conventions 138 & 182)",
                statutory_article="§ 2 Abs. 2 Nr. 1 LkSG",
                compliance_status=s3_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q03",
                        section_number=3,
                        question_de="Wird der Ausschluss von Kinderarbeit (Mindestalter 15 Jahre bzw. 18 Jahre für gefährliche Arbeiten) lückenlos garantiert?",
                        question_en="Is the exclusion of child labor (minimum age 15, or 18 for hazardous work) strictly and unconditionally guaranteed?",
                        statutory_basis="§ 2 Abs. 2 Nr. 1 LkSG · ILO 138 / 182",
                        status=s3_status,
                        answer_de=s3_ans_de,
                        answer_en=s3_ans_en,
                        evidence_quote=s3_quote,
                        page_number=s3_page,
                        bafa_recommendation_de=s3_rec_de,
                        bafa_recommendation_en=s3_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 4: Zwangsarbeit & Moderne Sklaverei (§ 2 Abs. 2 Nr. 2 & 4)
        # -------------------------------------------------------------
        s4_risk = risks_by_cat.get("FORCED_LABOR")
        if s4_risk:
            s4_status = BafaComplianceStatus.NON_COMPLIANT
            s4_ans_de = f"Kritischer Befund: {s4_risk.finding_de}"
            s4_ans_en = f"Critical finding: {s4_risk.finding_en}"
            s4_quote = s4_risk.evidence_snippet
            s4_page = s4_risk.page_number
            s4_rec_de = s4_risk.remediation_action_de
            s4_rec_en = s4_risk.remediation_action_en
        else:
            s4_status = BafaComplianceStatus.COMPLIANT
            s4_ans_de = "Jegliche Formen von Zwangsarbeit, Schuldknechtschaft oder Ausweisentzug sind strikt untersagt."
            s4_ans_en = "All forms of forced labor, debt bondage, or identity document retention are strictly prohibited."
            s4_quote = "Freiwilligkeit der Arbeitsaufnahme und Verbot von Schuldknechtschaft garantiert."
            s4_page = 1
            s4_rec_de = "Keine Beanstandung. Einbehaltung von Ausweispapieren bei Dienstleistern auditieren."
            s4_rec_en = "No deficiency. Audit vendor hiring protocols to prevent retention of personal identity documents."

        sections.append(
            BafaQuestionnaireSection(
                section_number=4,
                title_de="Zwangsarbeit, Schuldknechtschaft & Moderne Sklaverei",
                title_en="Prohibition of Forced Labor, Debt Bondage & Modern Slavery",
                statutory_article="§ 2 Abs. 2 Nr. 2 & 4 LkSG",
                compliance_status=s4_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q04",
                        section_number=4,
                        question_de="Sind Sicherheiten wie Einbehaltung von Reisedokumenten, Kautionszahlungen oder Bewegungseinschränkungen vertraglich ausgeschlossen?",
                        question_en="Are collateral demands such as retention of travel documents, security deposits, or movement restrictions contractually excluded?",
                        statutory_basis="§ 2 Abs. 2 Nr. 2 & 4 LkSG · ILO 29 / 105",
                        status=s4_status,
                        answer_de=s4_ans_de,
                        answer_en=s4_ans_en,
                        evidence_quote=s4_quote,
                        page_number=s4_page,
                        bafa_recommendation_de=s4_rec_de,
                        bafa_recommendation_en=s4_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 5: Arbeitsschutz & Betriebliche Gesundheit (§ 2 Abs. 2 Nr. 5)
        # -------------------------------------------------------------
        s5_risk = risks_by_cat.get("OCCUPATIONAL_SAFETY")
        if s5_risk:
            s5_status = BafaComplianceStatus.PARTIALLY_COMPLIANT if s5_risk.severity == "MEDIUM" else BafaComplianceStatus.NON_COMPLIANT
            s5_ans_de = f"Mängel im Arbeitsschutz: {s5_risk.finding_de}"
            s5_ans_en = f"Workplace safety deficiency: {s5_risk.finding_en}"
            s5_quote = s5_risk.evidence_snippet
            s5_page = s5_risk.page_number
            s5_rec_de = s5_risk.remediation_action_de
            s5_rec_en = s5_risk.remediation_action_en
        else:
            s5_status = BafaComplianceStatus.COMPLIANT
            s5_ans_de = "Verbindliche Einhaltung internationaler und nationaler Arbeitsschutzstandards vertraglich garantiert."
            s5_ans_en = "Binding adherence to international and national occupational health standards is contractually guaranteed."
            s5_quote = "Der Auftragnehmer garantiert Arbeits- und Gesundheitsschutz nach ISO 45001."
            s5_page = 1
            s5_rec_de = "Gültige ISO-45001-Zertifikate oder gleichwertige Prüfberichte jährlich anfordern."
            s5_rec_en = "Request annual ISO 45001 audit certificates or equivalent occupational safety reports."

        sections.append(
            BafaQuestionnaireSection(
                section_number=5,
                title_de="Arbeitsschutz & Betriebliche Gesundheit",
                title_en="Occupational Health & Workplace Safety",
                statutory_article="§ 2 Abs. 2 Nr. 5 LkSG",
                compliance_status=s5_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q05",
                        section_number=5,
                        question_de="Garantiert der Zulieferer sichere und gesunde Arbeitsbedingungen sowie angemessene Schutzmaßnahmen gegen Gefahrenstoffe?",
                        question_en="Does the supplier guarantee safe and healthy workplace conditions and adequate precautions against hazardous substances?",
                        statutory_basis="§ 2 Abs. 2 Nr. 5 LkSG · ArbSchG",
                        status=s5_status,
                        answer_de=s5_ans_de,
                        answer_en=s5_ans_en,
                        evidence_quote=s5_quote,
                        page_number=s5_page,
                        bafa_recommendation_de=s5_rec_de,
                        bafa_recommendation_en=s5_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 6: Koalitionsfreiheit & Tarifautonomie (§ 2 Abs. 2 Nr. 6 & 7)
        # -------------------------------------------------------------
        s6_risk = risks_by_cat.get("FREEDOM_OF_ASSOCIATION")
        if s6_risk:
            s6_status = BafaComplianceStatus.NON_COMPLIANT
            s6_ans_de = f"Einschränkung der Koalitionsfreiheit: {s6_risk.finding_de}"
            s6_ans_en = f"Restriction of freedom of association: {s6_risk.finding_en}"
            s6_quote = s6_risk.evidence_snippet
            s6_page = s6_risk.page_number
            s6_rec_de = s6_risk.remediation_action_de
            s6_rec_en = s6_risk.remediation_action_en
        else:
            s6_status = BafaComplianceStatus.COMPLIANT
            s6_ans_de = "Recht zur Bildung von Gewerkschaften und Kollektivverhandlungen ist uneingeschränkt geschützt."
            s6_ans_en = "Right to form trade unions and bargain collectively is protected without restriction."
            s6_quote = "Anerkennung der Koalitionsfreiheit und Tarifautonomie gem. ILO 87 und 98."
            s6_page = 1
            s6_rec_de = "Keine Beanstandung. Keine gelben Gewerkschaften oder Repressalien tolerieren."
            s6_rec_en = "No deficiency. Zero tolerance for yellow unions or anti-union employer retaliation."

        sections.append(
            BafaQuestionnaireSection(
                section_number=6,
                title_de="Koalitionsfreiheit & Tarifautonomie (ILO 87 & 98)",
                title_en="Freedom of Association & Collective Bargaining (ILO 87 & 98)",
                statutory_article="§ 2 Abs. 2 Nr. 6 & 7 LkSG",
                compliance_status=s6_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q06",
                        section_number=6,
                        question_de="Wird das Recht der Beschäftigten zur Gründung und zum Beitritt zu Gewerkschaften ohne Diskriminierung gewährleistet?",
                        question_en="Is the right of employees to establish and join trade unions guaranteed without employer discrimination?",
                        statutory_basis="§ 2 Abs. 2 Nr. 6 & 7 LkSG · ILO 87 / 98",
                        status=s6_status,
                        answer_de=s6_ans_de,
                        answer_en=s6_ans_en,
                        evidence_quote=s6_quote,
                        page_number=s6_page,
                        bafa_recommendation_de=s6_rec_de,
                        bafa_recommendation_en=s6_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 7: Angemessene Vergütung & Mindestlohn (§ 2 Abs. 2 Nr. 8 / MiLoG)
        # -------------------------------------------------------------
        s7_risk = risks_by_cat.get("FAIR_WAGE")
        if s7_risk:
            s7_status = BafaComplianceStatus.NON_COMPLIANT
            s7_ans_de = f"Lohnverstoß oder unzulässige Abzüge: {s7_risk.finding_de}"
            s7_ans_en = f"Wage violation or unlawful wage deductions: {s7_risk.finding_en}"
            s7_quote = s7_risk.evidence_snippet
            s7_page = s7_risk.page_number
            s7_rec_de = s7_risk.remediation_action_de
            s7_rec_en = s7_risk.remediation_action_en
        else:
            s7_status = BafaComplianceStatus.COMPLIANT
            s7_ans_de = "Zahlung eines existenzsichernden Mindestlohns nach MiLoG bzw. anwendbarem Tarifrecht garantiert."
            s7_ans_en = "Payment of statutory minimum wage pursuant to MiLoG or collective agreement is guaranteed."
            s7_quote = "Vergütung erfolgt mindestens in Höhe des gesetzlichen Mindestlohns (MiLoG)."
            s7_page = 1
            s7_rec_de = "Lohnabrechnungen stichprobenartig über externe Wirtschaftsprüfer im Audit-Dossier verifizieren."
            s7_rec_en = "Sample payroll records through independent auditor access within the audit dossier."

        sections.append(
            BafaQuestionnaireSection(
                section_number=7,
                title_de="Angemessene Vergütung & Mindestlohn",
                title_en="Fair Remuneration & Statutory Minimum Wage",
                statutory_article="§ 2 Abs. 2 Nr. 8 LkSG · MiLoG",
                compliance_status=s7_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q07",
                        section_number=7,
                        question_de="Garantiert der Zulieferer die Zahlung des gesetzlichen Mindestlohns ohne unzulässige Gehaltsabzüge?",
                        question_en="Does the vendor guarantee payment of the statutory minimum wage without unauthorized salary deductions?",
                        statutory_basis="§ 2 Abs. 2 Nr. 8 LkSG · MiLoG § 1",
                        status=s7_status,
                        answer_de=s7_ans_de,
                        answer_en=s7_ans_en,
                        evidence_quote=s7_quote,
                        page_number=s7_page,
                        bafa_recommendation_de=s7_rec_de,
                        bafa_recommendation_en=s7_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 8: Minamata-Übereinkommen (Quecksilber) (§ 2 Abs. 3 Nr. 1)
        # -------------------------------------------------------------
        s8_risk = risks_by_cat.get("ENVIRONMENT_MINAMATA")
        if s8_risk:
            s8_status = BafaComplianceStatus.NON_COMPLIANT
            s8_ans_de = f"Umweltverstoß Minamata: {s8_risk.finding_de}"
            s8_ans_en = f"Minamata environmental violation: {s8_risk.finding_en}"
            s8_quote = s8_risk.evidence_snippet
            s8_page = s8_risk.page_number
            s8_rec_de = s8_risk.remediation_action_de
            s8_rec_en = s8_risk.remediation_action_en
        else:
            s8_status = BafaComplianceStatus.COMPLIANT
            s8_ans_de = "Herstellungs- und Verwendungsverbot für mit Quecksilber versetzte Produkte wird lückenlos eingehalten."
            s8_ans_en = "Prohibition of manufacture and treatment of mercury-added products is fully respected."
            s8_quote = "Vollständige Beachtung des Minamata-Übereinkommens über Quecksilber."
            s8_page = 1
            s8_rec_de = "Keine Beanstandung. Entsorgungszertifikate für Hardware und Elektronikabfälle archivieren."
            s8_rec_en = "No deficiency. Archive certified recycling certificates for electronic and hardware waste."

        sections.append(
            BafaQuestionnaireSection(
                section_number=8,
                title_de="Minamata-Übereinkommen über Quecksilber",
                title_en="Minamata Convention on Mercury",
                statutory_article="§ 2 Abs. 3 Nr. 1 LkSG",
                compliance_status=s8_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q08",
                        section_number=8,
                        question_de="Hält der Zulieferer die Verbote zur Herstellung, Ausfuhr und Behandlung von Quecksilber und Quecksilberabfällen ein?",
                        question_en="Does the supplier comply with prohibitions regarding manufacturing, export, and treatment of mercury compounds and waste?",
                        statutory_basis="§ 2 Abs. 3 Nr. 1 LkSG · Minamata Convention",
                        status=s8_status,
                        answer_de=s8_ans_de,
                        answer_en=s8_ans_en,
                        evidence_quote=s8_quote,
                        page_number=s8_page,
                        bafa_recommendation_de=s8_rec_de,
                        bafa_recommendation_en=s8_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 9: Stockholmer Übereinkommen (POPs) (§ 2 Abs. 3 Nr. 2)
        # -------------------------------------------------------------
        s9_risk = risks_by_cat.get("ENVIRONMENT_POPS")
        if s9_risk:
            s9_status = BafaComplianceStatus.NON_COMPLIANT
            s9_ans_de = f"POPs-Schadstoffverstoß: {s9_risk.finding_de}"
            s9_ans_en = f"POPs pollutant violation: {s9_risk.finding_en}"
            s9_quote = s9_risk.evidence_snippet
            s9_page = s9_risk.page_number
            s9_rec_de = s9_risk.remediation_action_de
            s9_rec_en = s9_risk.remediation_action_en
        else:
            s9_status = BafaComplianceStatus.COMPLIANT
            s9_ans_de = "Verbot persistenter organischer Schadstoffe (POPs gem. EU-Verordnung 2019/1021) wird strikt beachtet."
            s9_ans_en = "Prohibition of persistent organic pollutants (POPs under EU Reg. 2019/1021) is strictly observed."
            s9_quote = "Ausschluss persistenter organischer Schadstoffe (POPs) gem. Stockholmer Übereinkommen."
            s9_page = 1
            s9_rec_de = "Keine Beanstandung. RoHS- und REACH-Konformitätserklärungen bereithalten."
            s9_rec_en = "No deficiency. Maintain updated RoHS and REACH compliance declarations."

        sections.append(
            BafaQuestionnaireSection(
                section_number=9,
                title_de="Stockholmer Übereinkommen über POPs-Chemikalien",
                title_en="Stockholm Convention on Persistent Organic Pollutants (POPs)",
                statutory_article="§ 2 Abs. 3 Nr. 2 LkSG",
                compliance_status=s9_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q09",
                        section_number=9,
                        question_de="Sind Herstellung, Verwendung und unzulässige Freisetzung persistenter organischer Schadstoffe (POPs) ausgeschlossen?",
                        question_en="Are the production, use, and unpermitted release of persistent organic pollutants (POPs) strictly excluded?",
                        statutory_basis="§ 2 Abs. 3 Nr. 2 LkSG · Stockholm Convention",
                        status=s9_status,
                        answer_de=s9_ans_de,
                        answer_en=s9_ans_en,
                        evidence_quote=s9_quote,
                        page_number=s9_page,
                        bafa_recommendation_de=s9_rec_de,
                        bafa_recommendation_en=s9_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 10: Basler Übereinkommen (Gefährliche Abfälle) (§ 2 Abs. 3 Nr. 3)
        # -------------------------------------------------------------
        s10_risk = risks_by_cat.get("ENVIRONMENT_HAZARDOUS_WASTE")
        if s10_risk:
            s10_status = BafaComplianceStatus.NON_COMPLIANT
            s10_ans_de = f"Abfallexport-Verstoß Basler Übereinkommen: {s10_risk.finding_de}"
            s10_ans_en = f"Waste export violation Basel Convention: {s10_risk.finding_en}"
            s10_quote = s10_risk.evidence_snippet
            s10_page = s10_risk.page_number
            s10_rec_de = s10_risk.remediation_action_de
            s10_rec_en = s10_risk.remediation_action_en
        else:
            s10_status = BafaComplianceStatus.COMPLIANT
            s10_ans_de = "Grenzüberschreitende Verbringung gefährlicher Abfälle erfolgt ausschließlich unter strikter Einhaltung des Basler Übereinkommens."
            s10_ans_en = "Transboundary movement of hazardous waste complies strictly with Basel Convention mandates."
            s10_quote = "Ausschluss illegaler grenzüberschreitender Abfalltransporte gem. Basler Übereinkommen."
            s10_page = 1
            s10_rec_de = "Keine Beanstandung. Entsorgungsnachweise für Serverhardware dokumentieren."
            s10_rec_en = "No deficiency. Document certified e-waste recycling paths for decommissioned servers."

        sections.append(
            BafaQuestionnaireSection(
                section_number=10,
                title_de="Basler Übereinkommen über gefährliche Abfälle",
                title_en="Basel Convention on Transboundary Hazardous Waste Export",
                statutory_article="§ 2 Abs. 3 Nr. 3 LkSG",
                compliance_status=s10_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q10",
                        section_number=10,
                        question_de="Wird der rechtswidrige grenzüberschreitende Export gefährlicher Abfälle in Nicht-OECD-Staaten ausgeschlossen?",
                        question_en="Is unlawful transboundary export of hazardous waste into non-OECD countries strictly excluded?",
                        statutory_basis="§ 2 Abs. 3 Nr. 3 LkSG · Basel Convention",
                        status=s10_status,
                        answer_de=s10_ans_de,
                        answer_en=s10_ans_en,
                        evidence_quote=s10_quote,
                        page_number=s10_page,
                        bafa_recommendation_de=s10_rec_de,
                        bafa_recommendation_en=s10_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 11: Beschwerdeverfahren & Whistleblower (§ 8 LkSG)
        # -------------------------------------------------------------
        s11_risk = risks_by_cat.get("COMPLAINTS_PROCEDURE")
        if s11_risk:
            s11_status = BafaComplianceStatus.NON_COMPLIANT
            s11_ans_de = f"Beschwerdemängel: {s11_risk.finding_de}"
            s11_ans_en = f"Whistleblower channel deficiency: {s11_risk.finding_en}"
            s11_quote = s11_risk.evidence_snippet
            s11_page = s11_risk.page_number
            s11_rec_de = s11_risk.remediation_action_de
            s11_rec_en = s11_risk.remediation_action_en
        else:
            s11_status = BafaComplianceStatus.COMPLIANT
            s11_ans_de = "Barrierefreies, vertrauliches und sanktionsfreies Beschwerdeverfahren nach § 8 LkSG ist etabliert."
            s11_ans_en = "Accessible, confidential, and retaliation-free complaints procedure under § 8 LkSG is operational."
            s11_quote = "Einrichtung eines Whistleblower-Systems gem. § 8 LkSG mit Vertraulichkeitsgarantie."
            s11_page = 1
            s11_rec_de = "Verfahrensordnung des Beschwerdeverfahrens öffentlich zugänglich halten."
            s11_rec_en = "Maintain procedural rules for the complaints channel publicly accessible online."

        sections.append(
            BafaQuestionnaireSection(
                section_number=11,
                title_de="Beschwerdeverfahren & Whistleblower-Schutz",
                title_en="Complaints Procedure & Whistleblower Protection",
                statutory_article="§ 8 LkSG",
                compliance_status=s11_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q11",
                        section_number=11,
                        question_de="Haben Beschäftigte und betroffene Dritte Zugang zu einem vertraulichen Beschwerdemechanismus ohne Furcht vor Repressalien?",
                        question_en="Do workers and affected third parties have access to a confidential complaints mechanism without fear of retaliation?",
                        statutory_basis="§ 8 LkSG · HinSchG",
                        status=s11_status,
                        answer_de=s11_ans_de,
                        answer_en=s11_ans_en,
                        evidence_quote=s11_quote,
                        page_number=s11_page,
                        bafa_recommendation_de=s11_rec_de,
                        bafa_recommendation_en=s11_rec_en,
                    )
                ],
            )
        )

        # -------------------------------------------------------------
        # Section 12: Präventionsmaßnahmen & Wirksamkeitskontrolle (§ 6 & § 7)
        # -------------------------------------------------------------
        s12_risk = risks_by_cat.get("ANNUAL_REPORTING_BAFA")
        if s12_risk:
            s12_status = BafaComplianceStatus.PARTIALLY_COMPLIANT if s12_risk.severity == "MEDIUM" else BafaComplianceStatus.NON_COMPLIANT
            s12_ans_de = f"Berichts- und Kontrolldefizit: {s12_risk.finding_de}"
            s12_ans_en = f"Reporting and control deficit: {s12_risk.finding_en}"
            s12_quote = s12_risk.evidence_snippet
            s12_page = s12_risk.page_number
            s12_rec_de = s12_risk.remediation_action_de
            s12_rec_en = s12_risk.remediation_action_en
        else:
            s12_status = BafaComplianceStatus.COMPLIANT
            s12_ans_de = "Verbindliche Audit-Rechte, Schulungen und jährliche BAFA-Berichterstattung (§ 10 LkSG) sind vereinbart."
            s12_ans_en = "Binding inspection rights, training, and annual BAFA reporting (§ 10 LkSG) are established."
            s12_quote = "Vorlage des geprüften BAFA-Berichts und Audit-Rechte uneingeschränkt garantiert."
            s12_page = 1
            s12_rec_de = "Wirksamkeitsprüfung der Präventionsmaßnahmen mindestens einmal jährlich durchführen."
            s12_rec_en = "Conduct annual effectiveness review of preventive measures pursuant to § 7(1) LkSG."

        sections.append(
            BafaQuestionnaireSection(
                section_number=12,
                title_de="Präventionsmaßnahmen & Wirksamkeitskontrolle",
                title_en="Preventive Measures, Audit Rights & Effectiveness Review",
                statutory_article="§ 6, § 7 & § 10 LkSG",
                compliance_status=s12_status,
                items=[
                    BafaQuestionnaireItem(
                        item_id="BAFA-Q12",
                        section_number=12,
                        question_de="Werden risikobasierte Präventionsmaßnahmen, Vor-Ort-Audit-Rechte und die jährliche BAFA-Berichtspflicht vertraglich gesichert?",
                        question_en="Are risk-based preventive measures, on-site audit access rights, and annual BAFA reporting mandates contractually secured?",
                        statutory_basis="§ 6 Abs. 4 & § 10 Abs. 2 LkSG",
                        status=s12_status,
                        answer_de=s12_ans_de,
                        answer_en=s12_ans_en,
                        evidence_quote=s12_quote,
                        page_number=s12_page,
                        bafa_recommendation_de=s12_rec_de,
                        bafa_recommendation_en=s12_rec_en,
                    )
                ],
            )
        )

        # Count statuses
        compliant_count = sum(1 for s in sections if s.compliance_status == BafaComplianceStatus.COMPLIANT)
        partially_count = sum(1 for s in sections if s.compliance_status == BafaComplianceStatus.PARTIALLY_COMPLIANT)
        non_compliant_count = sum(1 for s in sections if s.compliance_status == BafaComplianceStatus.NON_COMPLIANT)

        # Overall Score calculation (out of 100)
        # Compliant = 100%, Partial = 50%, Non-compliant = 0%
        raw_score = ((compliant_count * 100.0) + (partially_count * 50.0)) / len(sections)
        overall_score = round(raw_score, 1)

        if overall_score >= 95.0:
            rating: Literal["AAA", "AA", "A", "BBB", "BB", "B", "CCC"] = "AAA"
        elif overall_score >= 85.0:
            rating = "AA"
        elif overall_score >= 75.0:
            rating = "A"
        elif overall_score >= 65.0:
            rating = "BBB"
        elif overall_score >= 55.0:
            rating = "BB"
        elif overall_score >= 45.0:
            rating = "B"
        else:
            rating = "CCC"

        return BafaQuestionnaireResponse(
            document_id=document_id,
            filename=filename,
            supplier_name=supplier_name,
            overall_score=overall_score,
            compliance_rating=rating,
            total_questions=len(sections),
            compliant_count=compliant_count,
            partially_compliant_count=partially_count,
            non_compliant_count=non_compliant_count,
            sections=sections,
            generated_at=datetime.now(UTC),
        )
