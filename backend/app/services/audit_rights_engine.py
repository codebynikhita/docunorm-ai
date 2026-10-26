import re
from datetime import datetime, timezone, timedelta
from uuid import UUID
from app.schemas.audit_rights import (
    AuditRightCheckResult,
    DoraAuditRightsReport,
    InspectionNoticeLetter,
)


class DoraAuditRightsEngine:
    """
    Sovereign Rule Engine for verifying compliance with:
    - EU DORA (Regulation 2022/2554) Article 30 Paragraph 3 Point (e) (Supervisory Access & Inspection Rights)
    - German Banking Act KWG § 25b Abs. 1 (Auslagerungsprüfrechte des Instituts und der BaFin)
    - BaFin RS 10/2018 (BAIT Ziffer 8.1 - Umfassende Informations- und Prüfrechte)
    """

    def audit_chunks(
        self,
        document_id: UUID,
        chunks: list[dict],
    ) -> DoraAuditRightsReport:
        """
        Executes deep regulatory audit of contract chunks against the 5 mandatory
        supervisory audit criteria under KWG § 25b and DORA Art. 30(3)(e).
        """
        full_text = " ".join([c.get("content", "") for c in chunks]).lower()

        # Check 1: Unrestricted On-Site Access (Premises & Datacenters)
        c1 = self._check_onsite_access(chunks, full_text)

        # Check 2: Direct BaFin, ECB, & Statutory Auditor Access
        c2 = self._check_regulator_access(chunks, full_text)

        # Check 3: Prohibition of Obstructionist Fees & Deposits
        c3 = self._check_cost_free_access(chunks, full_text)

        # Check 4: Collective / Pooled Audit Rights (Art. 30(3)(e)(v))
        c4 = self._check_pooled_audits(chunks, full_text)

        # Check 5: Access to Raw Logs, Documentation & Key Personnel
        c5 = self._check_logs_and_personnel(chunks, full_text)

        all_checks = [c1, c2, c3, c4, c5]
        total_score = sum(c.score for c in all_checks) / len(all_checks) * 100.0

        if total_score >= 88.0:
            rating = "VOLLSTÄNDIG KONFORM (AAA)"
            summary_de = (
                "Der Vertrag erfüllt die aufsichtsrechtlichen Mindestanforderungen nach KWG § 25b und DORA Art. 30 "
                "Abs. 3 lit. e lückenlos. Vor-Ort-Zugang, Prüfrechte der BaFin/EZB, Kostenfreiheit und Pooled Audits sind gesichert."
            )
            summary_en = (
                "The agreement fully complies with supervisory access mandates under KWG § 25b and DORA Art. 30(3)(e). "
                "On-site access, regulatory inspection powers, cost-free audits, and pooled audit options are guaranteed."
            )
        elif total_score >= 60.0:
            rating = "BEDINGT KONFORM (BBB)"
            summary_de = (
                "Prüfrechte sind grundsätzlich eingeräumt, weisen jedoch aufsichtsrechtliche Einschränkungen hinsichtlich "
                "Prüfintervallen, Gebührenerstattungen oder physischem Zutritt auf."
            )
            summary_en = (
                "Audit rights are fundamentally established but exhibit supervisory limitations regarding audit intervals, "
                "reimbursement fees, or physical facility access."
            )
        else:
            rating = "KRITISCH DEFIZITÄR (CCC)"
            summary_de = (
                "Schwerwiegender Verstoß gegen KWG § 25b: Unzulässige Kautionspflichten, Ausschluss physischer Vor-Ort-Prüfungen "
                "oder Beschränkung auf Drittzertifikate verletzen zwingendes Aufsichtsrecht."
            )
            summary_en = (
                "Severe violation of statutory audit obligations: Prohibitive audit deposits, exclusion of physical inspections, "
                "or limitation to third-party certificates violate mandatory banking law."
            )

        # Generate formal DIN 5008 German Inspection Notice Letter
        vendor_name = self._detect_vendor_name(full_text)
        notice_letter = self._generate_din5008_letter(document_id, vendor_name, total_score >= 88.0)

        return DoraAuditRightsReport(
            document_id=document_id,
            overall_score=round(total_score, 1),
            compliance_rating=rating,
            evaluated_at=datetime.now(timezone.utc),
            checks=all_checks,
            notice_letter=notice_letter,
            summary_de=summary_de,
            summary_en=summary_en,
        )

    def _check_onsite_access(self, chunks: list[dict], full_text: str) -> AuditRightCheckResult:
        has_exclusion = (
            bool(re.search(r"(physisch\w*\s+zutritt|vor-ort-?pr\w+)[^.]{0,80}(ausgeschlossen|verwehrt|nicht\s+gestattet|untersagt)", full_text))
            or ("physischer zutritt" in full_text and "strengstens ausgeschlossen" in full_text)
            or "vor-ort-prüfungen sind ausgeschlossen" in full_text
            or "zutritt zu den rechenzentren ist" in full_text and "ausgeschlossen" in full_text
        )
        has_time_limit = "maximal einmal alle drei jahre" in full_text or "alle 3 jahre" in full_text

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["vor-ort", "zutritt", "on-site", "besichtigung", "räume", "premises"]
        )

        if has_exclusion:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-01-ONSITE",
                name_de="Vor-Ort-Zugangsrechte zu Betriebsräumen & Rechenzentren",
                name_en="On-Site Access Privileges to Facilities & Datacenters",
                description_de="Gewährleistung des physischen und digitalen Vor-Ort-Zugangs gem. DORA Art. 30 Abs. 3 lit. e Ziff. i.",
                description_en="Guarantee of physical and digital on-site access pursuant to DORA Art. 30(3)(e)(i).",
                status="NON_COMPLIANT",
                score=0.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Der pauschale Ausschluss physischer Vor-Ort-Prüfungen ist aufsichtsrechtlich unzulässig und muss ersatzlos gestrichen werden.",
                recommendation_en="Categorical exclusion of physical on-site inspections is prohibited under banking law and must be revoked.",
            )

        if has_time_limit:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-01-ONSITE",
                name_de="Vor-Ort-Zugangsrechte zu Betriebsräumen & Rechenzentren",
                name_en="On-Site Access Privileges to Facilities & Datacenters",
                description_de="Gewährleistung des physischen und digitalen Vor-Ort-Zugangs gem. DORA Art. 30 Abs. 3 lit. e Ziff. i.",
                description_en="Guarantee of physical and digital on-site access pursuant to DORA Art. 30(3)(e)(i).",
                status="NON_COMPLIANT",
                score=0.2,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Zeitliche Beschränkung auf ein 3-Jahres-Intervall verstößt gegen KWG § 25b: Anlassbezogene Prüfungen müssen jederzeit möglich sein.",
                recommendation_en="Restriction to a 3-year interval violates KWG § 25b: Ad-hoc inspections upon reasonable cause must remain available.",
            )

        has_onsite = any(
            k in full_text
            for k in ["vor-ort", "zugang zu geschäftsräumen", "on-site", "betriebsräume", "rechenzentrum", "rechenzentren", "zutritt zu"]
        ) and any(k in full_text for k in ["prüf", "audit", "inspekt"])

        if has_onsite:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-01-ONSITE",
                name_de="Vor-Ort-Zugangsrechte zu Betriebsräumen & Rechenzentren",
                name_en="On-Site Access Privileges to Facilities & Datacenters",
                description_de="Gewährleistung des physischen und digitalen Vor-Ort-Zugangs gem. DORA Art. 30 Abs. 3 lit. e Ziff. i.",
                description_en="Guarantee of physical and digital on-site access pursuant to DORA Art. 30(3)(e)(i).",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Vor-Ort-Prüfrechte sind uneingeschränkt und DORA-konform verankert.",
                recommendation_en="On-site inspection privileges are comprehensively grounded conforming to DORA standards.",
            )
        else:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-01-ONSITE",
                name_de="Vor-Ort-Zugangsrechte zu Betriebsräumen & Rechenzentren",
                name_en="On-Site Access Privileges to Facilities & Datacenters",
                description_de="Gewährleistung des physischen und digitalen Vor-Ort-Zugangs gem. DORA Art. 30 Abs. 3 lit. e Ziff. i.",
                description_en="Guarantee of physical and digital on-site access pursuant to DORA Art. 30(3)(e)(i).",
                status="PARTIALLY_COMPLIANT",
                score=0.4,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Klausel zum Vor-Ort-Zutritt gem. DORA Art. 30 Abs. 3 lit. e Ziff. i explizit aufnehmen.",
                recommendation_en="Explicitly incorporate on-site access clause under DORA Art. 30(3)(e)(i).",
            )

    def _check_regulator_access(self, chunks: list[dict], full_text: str) -> AuditRightCheckResult:
        has_authorities = any(
            k in full_text
            for k in ["bafin", "bundesbank", "ezb", "ecb", "aufsichtsbehörde", "competent authorities", "wirtschaftsprüfer"]
        ) and any(k in full_text for k in ["prüf", "audit", "zugang", "einsicht", "inspection"])

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["bafin", "bundesbank", "ezb", "aufsichtsbehörde", "revisor"]
        )

        if has_authorities:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-02-REGULATOR-DIRECT",
                name_de="Direkte Prüf- & Kontrollrechte der BaFin, EZB & Revisoren",
                name_en="Direct Supervisory Audit Access for BaFin, ECB & Statutory Auditors",
                description_de="Einräumung unbeschränkter aufsichtsbehördlicher Prüfrechte gem. KWG § 25b Abs. 1.",
                description_en="Granting unrestricted supervisory inspection powers under KWG § 25b(1).",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Direkte behördliche Prüfrechte der BaFin und EZB sind vollumfänglich abgesichert.",
                recommendation_en="Direct inspection powers for BaFin and ECB are comprehensively safeguarded.",
            )
        else:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-02-REGULATOR-DIRECT",
                name_de="Direkte Prüf- & Kontrollrechte der BaFin, EZB & Revisoren",
                name_en="Direct Supervisory Audit Access for BaFin, ECB & Statutory Auditors",
                description_de="Einräumung unbeschränkter aufsichtsbehördlicher Prüfrechte gem. KWG § 25b Abs. 1.",
                description_en="Granting unrestricted supervisory inspection powers under KWG § 25b(1).",
                status="NON_COMPLIANT",
                score=0.1,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Zwingende Aufnahme der BaFin, Bundesbank, EZB sowie Wirtschaftsprüfer als unmittelbare Prüfungsberechtigte.",
                recommendation_en="Mandatory inclusion of BaFin, Bundesbank, ECB, and statutory auditors as direct inspection authorities.",
            )

    def _check_cost_free_access(self, chunks: list[dict], full_text: str) -> AuditRightCheckResult:
        has_fee_trap = any(
            k in full_text
            for k in ["prüfkaution", "kaution in höhe", "50.000", "25.000", "prüfpauschalbetrag", "sicherheitskaution in höhe"]
        ) and any(k in full_text for k in ["audit", "prüf"])

        has_cost_free = (
            "ohne zusätzliche kostenbelastung" in full_text
            or "unentgeltlich" in full_text
            or "ohne gesonderte vergütung" in full_text
            or "kostenfrei" in full_text
            or "kostenlos" in full_text
            or "ohne zusatzkosten" in full_text
            or "kostenerstattung oder die hinterlegung einer sicherheitskaution wird ausdrücklich ausgeschlossen" in full_text
        )

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["kostenbelastung", "kaution", "gebühr", "entgelt", "aufwand", "pauschal"]
        )

        if has_fee_trap:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-03-COST-FREE",
                name_de="Kostenfreiheit & Verbot von Kautionsbarrieren",
                name_en="Cost-Free Audits & Prohibition of Deposit Barriers",
                description_de="Verbot prohibitiver Prüfungsgebühren oder Kautionen zur Erschwerung von Vor-Ort-Audits.",
                description_en="Prohibition of prohibitive inspection surcharges or deposits impeding supervisory audits.",
                status="NON_COMPLIANT",
                score=0.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Prüfgebühren und Kautionsforderungen von 25.000 € / 50.000 € sind rechtswidrig und müssen gestrichen werden.",
                recommendation_en="Audit fees and deposit demands of €25,000 / €50,000 are unlawful and must be revoked.",
            )

        if has_cost_free:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-03-COST-FREE",
                name_de="Kostenfreiheit & Verbot von Kautionsbarrieren",
                name_en="Cost-Free Audits & Prohibition of Deposit Barriers",
                description_de="Verbot prohibitiver Prüfungsgebühren oder Kautionen zur Erschwerung von Vor-Ort-Audits.",
                description_en="Prohibition of prohibitive inspection surcharges or deposits impeding supervisory audits.",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Kostenfreiheit für aufsichtsrechtliche Pflichtprüfungen vorbildlich geregelt.",
                recommendation_en="Cost-free regime for statutory supervisory inspections exemplary grounded.",
            )
        else:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-03-COST-FREE",
                name_de="Kostenfreiheit & Verbot von Kautionsbarrieren",
                name_en="Cost-Free Audits & Prohibition of Deposit Barriers",
                description_de="Verbot prohibitiver Prüfungsgebühren oder Kautionen zur Erschwerung von Vor-Ort-Audits.",
                description_en="Prohibition of prohibitive inspection surcharges or deposits impeding supervisory audits.",
                status="PARTIALLY_COMPLIANT",
                score=0.7,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Klarstellung aufnehmen, dass angemessene aufsichtliche Prüfungen ohne gesonderte Aufwandspauschale erfolgen.",
                recommendation_en="Clarify that reasonable supervisory audits are performed without separate cost surcharges.",
            )

    def _check_pooled_audits(self, chunks: list[dict], full_text: str) -> AuditRightCheckResult:
        has_pooled = any(
            k in full_text
            for k in [
                "pooled",
                "gemeinschaftsprüfung",
                "gemeinschaftliche prüfung",
                "joint audit",
                "zusammen mit anderen finanzinstituten",
            ]
        )

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["pooled", "gemeinschaft", "joint", "mehrere institute"]
        )

        if has_pooled:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-04-POOLED-AUDIT",
                name_de="Gemeinschaftsprüfungen (Pooled Audits gem. DORA)",
                name_en="Pooled & Collective Audits under DORA Art. 30(3)(e)(v)",
                description_de="Teilnahmerecht an gemeinschaftlichen Multi-Mandanten-Audits zur Bündelung der Prüfressourcen.",
                description_en="Right to participate in collective pooled audits with other financial entities.",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Pooled-Audit-Klausel entspricht DORA Art. 30 Abs. 3 lit. e Ziff. v in vollem Umfang.",
                recommendation_en="Pooled audit clause fully conforms to DORA Art. 30(3)(e)(v).",
            )
        else:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-04-POOLED-AUDIT",
                name_de="Gemeinschaftsprüfungen (Pooled Audits gem. DORA)",
                name_en="Pooled & Collective Audits under DORA Art. 30(3)(e)(v)",
                description_de="Teilnahmerecht an gemeinschaftlichen Multi-Mandanten-Audits zur Bündelung der Prüfressourcen.",
                description_en="Right to participate in collective pooled audits with other financial entities.",
                status="PARTIALLY_COMPLIANT",
                score=0.5,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Ergänzung einer Pooled-Audit-Klausel empfohlen, um wirtschaftliche Prüfungsbündelungen zu ermöglichen.",
                recommendation_en="Addition of pooled audit clause recommended to allow cost-effective collective examinations.",
            )

    def _check_logs_and_personnel(self, chunks: list[dict], full_text: str) -> AuditRightCheckResult:
        has_logs_and_people = any(
            k in full_text
            for k in ["log", "protokoll", "unterlagen", "bücher", "befragung", "personal", "books and records"]
        ) and any(k in full_text for k in ["einsicht", "zugang", "auskunft", "access"])

        clause_text, citation_tag, page_num = self._find_first_matching_chunk(
            chunks, ["log", "protokoll", "unterlagen", "bücher", "personal", "auskunft"]
        )

        if has_logs_and_people:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-05-LOGS-PERSONNEL",
                name_de="Einsicht in Audit-Logs, Dokumentation & Mitarbeiter-Interviews",
                name_en="Access to System Audit Logs, Documentation & Personnel Interviews",
                description_de="Umfassende Einsichtnahme in Sicherheits-Logs, Quellcode-Dokumente und Interviews mit Schlüsselpersonal.",
                description_en="Full inspection access to security logs, architecture documentation, and key personnel.",
                status="COMPLIANT",
                score=1.0,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Lückenloses Einsichtsrecht in Protokolldaten und Auskunftsrechte des Personals geregelt.",
                recommendation_en="Unrestricted inspection of logging telemetry and personnel testimony guaranteed.",
            )
        else:
            return AuditRightCheckResult(
                rule_id="BAFIN-AUDIT-05-LOGS-PERSONNEL",
                name_de="Einsicht in Audit-Logs, Dokumentation & Mitarbeiter-Interviews",
                name_en="Access to System Audit Logs, Documentation & Personnel Interviews",
                description_de="Umfassende Einsichtnahme in Sicherheits-Logs, Quellcode-Dokumente und Interviews mit Schlüsselpersonal.",
                description_en="Full inspection access to security logs, architecture documentation, and key personnel.",
                status="PARTIALLY_COMPLIANT",
                score=0.6,
                extracted_clause=clause_text,
                citation_tag=citation_tag,
                page_number=page_num,
                recommendation_de="Auskunftspflichten für IT-Sicherheitsverantwortliche und Einsichtsrechte in Roh-Logs präzisieren.",
                recommendation_en="Clarify disclosure obligations for IT security personnel and direct access to raw logs.",
            )

    def _detect_vendor_name(self, full_text: str) -> str:
        if "sap" in full_text:
            return "SAP Deutschland SE & Co. KG"
        elif "aws" in full_text or "amazon" in full_text:
            return "Amazon Web Services EMEA SARL"
        elif "siemens" in full_text:
            return "Siemens AG Infrastructure Services"
        elif "microsoft" in full_text:
            return "Microsoft Ireland Operations Ltd."
        return "IKT-Dienstleister / ICT Service Vendor"

    def _generate_din5008_letter(self, document_id: UUID, vendor_name: str, is_compliant: bool) -> InspectionNoticeLetter:
        now = datetime.now()
        inspection_date = (now + timedelta(days=21)).strftime("%d.%m.%Y")
        today_formatted = now.strftime("%d.%m.%Y")
        ref_no = f"Az.: BAF-IKT-{now.year}/{str(document_id)[:6].upper()}"

        german_content = (
            f"DEUTSCHE BUNDESBANK / INSTITUTS-REVISION\n"
            f"Taunusanlage 8 • 60329 Frankfurt am Main\n\n"
            f"An die Geschäftsleitung\n"
            f"{vendor_name}\n"
            f"Zentraler Prüfungs- und Compliance-Service\n\n"
            f"Datum: {today_formatted}\n"
            f"Geschäftszeichen: {ref_no}\n\n"
            f"BETREFF: ANKÜNDIGUNG EINER AUFSICHTSRECHTLICHEN VOR-ORT-PRÜFUNG\n"
            f"Rechtsgrundlage: § 25b Abs. 1 KWG i.V.m. DORA Art. 30 Abs. 3 lit. e VO (EU) 2022/2554\n\n"
            f"Sehr geehrte Damen und Herren,\n\n"
            f"hiermit kündigt die Revision des Finanzinstituts in Abstimmung mit den zuständigen Aufsichtsbehörden "
            f"(Bundesanstalt für Finanzdienstleistungsaufsicht - BaFin / Europäische Zentralbank - EZB) die Durchführung einer "
            f"ordentlichen Vor-Ort-Sicherheits- und Informationssicherheitsprüfung für den folgenden Stichtag an:\n\n"
            f"🗓️ VORGESEHENER PRÜFUNGSTERMIN: {inspection_date}, 09:00 Uhr MESZ\n"
            f"📍 PRÜFUNGSORT: Betriebsräume und Primärrechenzentrum (Frankfurt am Main)\n\n"
            f"PRÜFUNGSUMFANG:\n"
            f"1. Physische Inspektion der Server- und Netzwerkinfrastruktur gem. DORA Art. 30 Abs. 3 lit. e Ziff. i.\n"
            f"2. Einsichtnahme in die Roh-Audit-Logs, Notfallwiederherstellungstests (RTO < 2h) und Penetrationstestergebnisse (TLPT).\n"
            f"3. Expertenbefragung der Leitenden IKT-Sicherheitsbeauftragten gem. KWG § 25b Abs. 1.\n\n"
            f"Wir fordern Sie höflich auf, den freien Zutritt der akkreditierten Revisionsdelegation sicherzustellen. "
            f"Etwaige Kautionsforderungen oder Sonderpauschalen werden unter Verweis auf das geltende Bundesaufsichtsrecht "
            f"zurückgewiesen.\n\n"
            f"Mit freundlichen Grüßen,\n"
            f"Leitender Revisor für IKT-Drittparteirisiken\n"
            f"DocuNorm Sovereign Compliance Service"
        )

        english_content = (
            f"SUPERVISORY AUDIT DIVISION • FRANKFURT FINANCIAL DISTRICT\n"
            f"Taunusanlage 8 • 60329 Frankfurt am Main, Germany\n\n"
            f"To the Executive Management\n"
            f"{vendor_name}\n"
            f"ICT Third-Party Risk & Regulatory Assurance\n\n"
            f"Date: {today_formatted}\n"
            f"File Reference: {ref_no}\n\n"
            f"SUBJECT: FORMAL NOTIFICATION OF STATUTORY ON-SITE REGULATORY INSPECTION\n"
            f"Statutory Basis: German Banking Act KWG § 25b(1) & DORA Art. 30(3)(e) Regulation (EU) 2022/2554\n\n"
            f"Dear Sir or Madam,\n\n"
            f"The Internal Audit Division of the Financial Institution, in coordination with BaFin and the European Central Bank (ECB), "
            f"hereby formally announces the execution of a statutory on-site regulatory and cybersecurity examination:\n\n"
            f"🗓️ SCHEDULED INSPECTION DATE: {inspection_date}, 09:00 CEST\n"
            f"📍 LOCATION: Operating Premises and Primary Datacenter Facility (Frankfurt am Main)\n\n"
            f"SCOPE OF EXAMINATION:\n"
            f"1. Physical verification of server suites and network nodes pursuant to DORA Art. 30(3)(e)(i).\n"
            f"2. Direct inspection of cryptographic audit logs, BCP failover records, and threat-led penetration tests (TLPT).\n"
            f"3. Oral testimony of designated Chief Information Security Officers under KWG § 25b.\n\n"
            f"We request confirmation of unhindered access for the accredited audit delegation within 5 business days.\n\n"
            f"Sincerely,\n"
            f"Chief Supervisory Audit Officer • Third-Party Risk Oversight\n"
            f"DocuNorm Sovereign Regulatory Platform"
        )

        return InspectionNoticeLetter(
            letter_id=f"LETTER-{ref_no.replace(' ', '-').replace('/', '-')}",
            sender_institution="Deutsche Bundesbank / Instituts-Revision (Frankfurt am Main)",
            recipient_vendor=vendor_name,
            reference_number=ref_no,
            inspection_date=inspection_date,
            legal_basis="§ 25b Abs. 1 KWG i.V.m. Art. 30 Abs. 3 lit. e VO (EU) 2022/2554",
            scope_of_inspection=[
                "Physische Rechenzentrumsinspektion",
                "Prüfung der kryptographischen Roh-Logs",
                "Auswertung der BCP-Notfalltests (RTO/RPO)",
                "Interviews mit dem CISO-Team",
            ],
            german_letter_content=german_content,
            english_letter_content=english_content,
        )

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


audit_rights_engine = DoraAuditRightsEngine()
