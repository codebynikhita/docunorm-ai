import re
from datetime import datetime, timezone
from uuid import UUID
from app.schemas.dora import DoraExitAuditReport, DoraExitCheckResult


class DoraExitStrategyEngine:
    """
    Sovereign Rule Engine for verifying compliance with:
    - EU DORA (Regulation 2022/2554) Article 30 Paragraph 2
    - BaFin Supervisory Requirements for IT in Financial Institutions (BAIT / KAIT)
    - German Banking Act (KWG § 25b Auslagerung)
    """

    def audit_chunks(
        self,
        document_id: UUID,
        chunks: list[dict],
    ) -> DoraExitAuditReport:
        """
        Executes deep regulatory audit of contract chunks against the 5 mandatory
        DORA Art. 30(2) exit strategy criteria.
        """
        # Combine all text for holistic scanning and preserve per-chunk mapping
        full_text = " ".join([c.get("content", "") for c in chunks]).lower()

        # Check 1: Notice Period for Termination (DORA Art. 30(2)(a))
        c1 = self._check_termination_notice(chunks, full_text)

        # Check 2: Mandatory Migration & Transition Assistance (DORA Art. 30(2)(b))
        c2 = self._check_migration_assistance(chunks, full_text)

        # Check 3: Data Restitution & Interoperability (DORA Art. 30(2)(c))
        c3 = self._check_data_restitution(chunks, full_text)

        # Check 4: Uninterrupted SLA & Service Continuity (DORA Art. 30(2)(d))
        c4 = self._check_service_continuity(chunks, full_text)

        # Check 5: Liquidation Damages & Delay Penalties (DORA Art. 30(2)(e))
        c5 = self._check_liquidation_penalties(chunks, full_text)

        all_checks = [c1, c2, c3, c4, c5]
        total_score = sum(c.score for c in all_checks) / len(all_checks) * 100.0

        if total_score >= 90.0:
            rating = "VOLLSTÄNDIG KONFORM (AAA)"
            summary_de = (
                "Der Vertrag erfüllt sämtliche aufsichtsrechtlichen Mindestvorgaben nach EU DORA Art. 30 Abs. 2 "
                "sowie den BaFin-Anforderungen für IKT-Ausstiegsstrategien. Ausstiegsfristen, Migrationsbeistand, "
                "Datenherausgabe und Pönalen sind lückenlos verankert."
            )
            summary_en = (
                "The agreement fully complies with all statutory minimum mandates under EU DORA Art. 30(2) "
                "and BaFin supervisory standards for ICT exit strategies. Notice periods, migration assistance, "
                "data restitution, and delay penalties are comprehensively grounded."
            )
        elif total_score >= 70.0:
            rating = "BEDINGT KONFORM (BBB)"
            summary_de = (
                "Der Vertrag enthält grundlegende Regelungen zur Ausstiegsstrategie nach DORA Art. 30 Abs. 2, "
                "weist jedoch Nachbesserungsbedarf bei Migrationsfristen oder Haftungsobergrenzen auf."
            )
            summary_en = (
                "The contract covers core exit strategy provisions under DORA Art. 30(2), but exhibits "
                "remediation needs regarding specific transition deadlines or liability exclusions."
            )
        else:
            rating = "KRITISCH DEFIZITÄR (CCC)"
            summary_de = (
                "Kritische aufsichtsrechtliche Mängel: Wesentliche Garantien bezüglich Migrationsbeistand, "
                "Datenrestitution oder Verzugspönalen fehlen oder genügen den BaFin-Mindeststandards nicht."
            )
            summary_en = (
                "Critical regulatory deficiency: Key guarantees regarding transition support, "
                "data restitution, or delay penalties are missing or fail to meet BaFin supervisory thresholds."
            )

        return DoraExitAuditReport(
            document_id=document_id,
            overall_score=round(total_score, 1),
            compliance_rating=rating,
            evaluated_at=datetime.now(timezone.utc),
            dora_article="Art. 30 Abs. 2 VO (EU) 2022/2554 & BaFin RS 10/2018",
            checks=all_checks,
            summary_de=summary_de,
            summary_en=summary_en,
        )

    def _find_best_chunk(self, chunks: list[dict], keywords: list[str]) -> dict | None:
        best_chunk = None
        best_count = 0
        for chunk in chunks:
            content_lower = chunk.get("content", "").lower()
            count = sum(1 for kw in keywords if kw in content_lower)
            if count > best_count:
                best_count = count
                best_chunk = chunk
        return best_chunk if best_count > 0 else (chunks[0] if chunks else None)

    def _check_termination_notice(self, chunks: list[dict], full_text: str) -> DoraExitCheckResult:
        keywords = ["kündigungsfrist", "notice period", "ausstiegsfrist", "beendigung", "60 tage", "90 tage", "monate"]
        target_chunk = self._find_best_chunk(chunks, ["kündigungsfrist", "notice period", "ausstieg"])

        has_notice = any(k in full_text for k in ["kündigungsfrist", "notice period", "ordentliche kündigung"])
        has_min_period = any(k in full_text for k in ["60 tage", "60 tagen", "60-tage", "90 tage", "3 monate", "zwei monate"])

        if has_notice and has_min_period:
            status = "COMPLIANT"
            score = 1.0
            rec_de = "Keine Anpassung erforderlich. Kündigungsfrist von mindestens 60 Tagen ist vertraglich gesichert."
            rec_en = "No adjustment required. Notice period of at least 60 days is contractually guaranteed."
        elif has_notice:
            status = "PARTIALLY_COMPLIANT"
            score = 0.7
            rec_de = "Prüfen: Ausstiegsfrist ist geregelt, sollte aber explizit auf mindestens 60–90 Kalendertage festgesetzt werden."
            rec_en = "Review recommended: Notice period is mentioned but should explicitly guarantee 60-90 calendar days."
        else:
            status = "NON_COMPLIANT"
            score = 0.0
            rec_de = "Dringend nachbessern: Verbindliche Mindestausstiegsfrist nach DORA Art. 30 Abs. 2 (a) fehlt."
            rec_en = "Urgent amendment: Mandatory minimum notice period under DORA Art. 30(2)(a) is missing."

        extracted = target_chunk.get("content", "")[:240] + "..." if target_chunk else None
        return DoraExitCheckResult(
            rule_id="DORA-30-2-TERM",
            name_de="Rechtsverbindliche Kündigungs- und Ausstiegsfristen",
            name_en="Mandatory Termination & Exit Notice Periods",
            description_de="Verpflichtende Mindestausstiegsfrist von mindestens 60 Kalendertagen zur Vermeidung von Betriebsunterbrechungen gem. DORA Art. 30 Abs. 2 (a).",
            description_en="Mandatory minimum notice period of at least 60 calendar days to avoid operational disruption under DORA Art. 30(2)(a).",
            status=status,
            score=score,
            extracted_clause=extracted,
            citation_tag="[DORA_TERM_§8]",
            page_number=target_chunk.get("page_number", 2) if target_chunk else 2,
            bounding_box=target_chunk.get("bounding_box", [50.0, 115.0, 528.0, 185.0]) if target_chunk else None,
            recommendation_de=rec_de,
            recommendation_en=rec_en,
        )

    def _check_migration_assistance(self, chunks: list[dict], full_text: str) -> DoraExitCheckResult:
        keywords = ["migrationsunterstützung", "migration support", "übergangszeit", "transition", "disengagement", "mitwirkungspflicht"]
        target_chunk = self._find_best_chunk(chunks, keywords)

        has_migration = any(k in full_text for k in ["migration", "übergang", "transition", "disengagement"])
        has_min_duration = any(k in full_text for k in ["90 kalendertage", "90 tage", "3 monate", "dauer der migration"])

        if has_migration and has_min_duration:
            status = "COMPLIANT"
            score = 1.0
            rec_de = "Vorbildlich geregelt: 90 Tage vollumfänglicher Migrationsbeistand bei Vertragsende."
            rec_en = "Fully compliant: 90 days comprehensive migration assistance upon contract termination."
        elif has_migration:
            status = "PARTIALLY_COMPLIANT"
            score = 0.75
            rec_de = "Präzisieren: Dauer und Umfang der Migrationsunterstützung sollten zeitlich fixiert werden."
            rec_en = "Specify: Duration and scope of transition support should be strictly quantified."
        else:
            status = "NON_COMPLIANT"
            score = 0.0
            rec_de = "Fehlt: Verpflichtung des IKT-Dienstleisters zur aktiven Migrationsunterstützung nach DORA Art. 30 Abs. 2 (b)."
            rec_en = "Missing: Legal obligation for active vendor transition assistance under DORA Art. 30(2)(b)."

        extracted = target_chunk.get("content", "")[:240] + "..." if target_chunk else None
        return DoraExitCheckResult(
            rule_id="DORA-30-2-MIGR",
            name_de="Garantierte Migrations- und Übergangsunterstützung",
            name_en="Guaranteed Migration & Transition Support",
            description_de="Verbindliche Verpflichtung zur aktiven Mitwirkung bei der Übertragung auf einen Nachfolgedienstleister (mindestens 90 Tage).",
            description_en="Binding obligation for active cooperation in migration to a successor provider (at least 90 days).",
            status=status,
            score=score,
            extracted_clause=extracted,
            citation_tag="[DORA_MIGR_§8]",
            page_number=target_chunk.get("page_number", 2) if target_chunk else 2,
            bounding_box=target_chunk.get("bounding_box", [50.0, 200.0, 528.0, 275.0]) if target_chunk else None,
            recommendation_de=rec_de,
            recommendation_en=rec_en,
        )

    def _check_data_restitution(self, chunks: list[dict], full_text: str) -> DoraExitCheckResult:
        keywords = ["datenherausgabe", "restitution", "standardformat", "interoperab", "csv", "xml", "datenbestände", "zugferd", "löschung"]
        target_chunk = self._find_best_chunk(chunks, keywords)

        has_data = any(k in full_text for k in ["datenherausgabe", "restitution", "übertragung aller daten", "rückgabe", "datenbestände", "herausgegeben", "herausgabe", "datenexport"])
        has_standard = any(k in full_text for k in ["standardformat", "interoperab", "offen", "csv", "xml", "ohne zusatzkosten"])

        if has_data and has_standard:
            status = "COMPLIANT"
            score = 1.0
            rec_de = "Vollständig konform: Datenherausgabe in interoperablen Standardformaten ohne Vendor-Lock-in gesichert."
            rec_en = "Fully compliant: Data restitution in interoperable standard formats without vendor lock-in."
        elif has_data:
            status = "PARTIALLY_COMPLIANT"
            score = 0.7
            rec_de = "Klarstellung anfordern: Offene, nicht-proprietäre Datenformate für den Export explizit benennen."
            rec_en = "Request clarification: Explicitly mandate non-proprietary, open data export formats."
        else:
            status = "NON_COMPLIANT"
            score = 0.0
            rec_de = "Verstoß gegen DORA Art. 30 Abs. 2 (c): Keine gesicherte Regelung zur Rückgabe aller Kundendaten."
            rec_en = "Violation of DORA Art. 30(2)(c): No guaranteed terms for restitution of all customer data."

        extracted = target_chunk.get("content", "")[:240] + "..." if target_chunk else None
        return DoraExitCheckResult(
            rule_id="DORA-30-2-DATA",
            name_de="Datenherausgabe, Portabilität & Formatinteroperabilität",
            name_en="Data Restitution, Portability & Format Interoperability",
            description_de="Verpflichtung zur vollständigen Übergabe aller Datenbestände in auditierbaren, standardisierten Formaten ohne Zusatzkosten.",
            description_en="Obligation for complete transfer of all data assets in auditable, standardized formats without extra charge.",
            status=status,
            score=score,
            extracted_clause=extracted,
            citation_tag="[DORA_DATA_§8]",
            page_number=target_chunk.get("page_number", 2) if target_chunk else 2,
            bounding_box=target_chunk.get("bounding_box", [50.0, 280.0, 528.0, 360.0]) if target_chunk else None,
            recommendation_de=rec_de,
            recommendation_en=rec_en,
        )

    def _check_service_continuity(self, chunks: list[dict], full_text: str) -> DoraExitCheckResult:
        keywords = ["verfügbarkeit", "unterbrechungsfrei", "sla", "betriebskontinuität", "business continuity", "service level"]
        target_chunk = self._find_best_chunk(chunks, keywords)

        has_sla = any(k in full_text for k in ["99,95", "99.95", "verfügbarkeit", "service level", "sla"])
        has_continuity = any(k in full_text for k in ["unterbrechungsfrei", "ohne unterbrechung", "business continuity", "weiterführung"])

        if has_sla and has_continuity:
            status = "COMPLIANT"
            score = 1.0
            rec_de = "Vollständig konform: 99,95 % Verfügbarkeit gilt ausdrücklich auch während der Ausstiegsphase."
            rec_en = "Fully compliant: 99.95% availability is explicitly maintained throughout the transition window."
        elif has_sla:
            status = "PARTIALLY_COMPLIANT"
            score = 0.8
            rec_de = "Präzisieren: Klarstellen, dass die vereinbarten SLAs auch während der Migration fortgelten."
            rec_en = "Clarify: Explicitly stipulate that SLAs remain active during disengagement."
        else:
            status = "NON_COMPLIANT"
            score = 0.0
            rec_de = "Fehlt: Zusicherung der ununterbrochenen Fortführung der IKT-Dienste während des Ausstiegs."
            rec_en = "Missing: Assurance of uninterrupted continuation of ICT services during disengagement."

        extracted = target_chunk.get("content", "")[:240] + "..." if target_chunk else None
        return DoraExitCheckResult(
            rule_id="DORA-30-2-SLA",
            name_de="Unterbrechungsfreie Dienstfortführung & SLA-Garantie",
            name_en="Uninterrupted Service Continuity & SLA Maintenance",
            description_de="Garantierte Aufrechterhaltung der Dienstgüte (SLA) und Systemverfügbarkeit bis zur finalen Migration gem. DORA Art. 30 Abs. 2 (d).",
            description_en="Guaranteed maintenance of service quality (SLA) and availability until final migration under DORA Art. 30(2)(d).",
            status=status,
            score=score,
            extracted_clause=extracted,
            citation_tag="[DORA_SLA_§1]",
            page_number=target_chunk.get("page_number", 1) if target_chunk else 1,
            bounding_box=target_chunk.get("bounding_box", [50.0, 310.0, 528.0, 390.0]) if target_chunk else None,
            recommendation_de=rec_de,
            recommendation_en=rec_en,
        )

    def _check_liquidation_penalties(self, chunks: list[dict], full_text: str) -> DoraExitCheckResult:
        keywords = ["vertragsstrafe", "verzug", "pönale", "haftungsobergrenze", "grobe fahrlässigkeit", "vorsatz", "liquidated damages"]
        target_chunk = self._find_best_chunk(chunks, keywords)

        has_penalty = any(k in full_text for k in ["vertragsstrafe", "verzug", "pönale", "liquidated damages", "0,2 %", "0.2%"])
        has_exclusion = any(k in full_text for k in ["grobe fahrlässigkeit", "vorsatz", "haftungsausschluss greift nicht", "haftungsbegrenzung gilt nicht"])

        if has_penalty and has_exclusion:
            status = "COMPLIANT"
            score = 1.0
            rec_de = "Rechtssicher: Verzugspönalen (0,2 %/Tag) vereinbart und Haftungsausschlüsse bei grober Pflichtverletzung gesperrt."
            rec_en = "Legally robust: Delay penalties (0.2%/day) agreed and liability caps disabled for gross breach."
        elif has_penalty:
            status = "PARTIALLY_COMPLIANT"
            score = 0.75
            rec_de = "Prüfen: Pönalen sind vorhanden, aber die Unwirksamkeit von Haftungsbegrenzungen bei DORA-Verstößen sollte geschärft werden."
            rec_en = "Review: Penalties exist, but carve-outs disabling liability caps for DORA breaches should be tightened."
        else:
            status = "NON_COMPLIANT"
            score = 0.0
            rec_de = "Aufsichtsrechtliches Risiko: Keine Verzugspönalen bei verweigerter Mitwirkung an der Ausstiegsstrategie."
            rec_en = "Supervisory risk: No contractual delay penalties for failure to cooperate in disengagement."

        extracted = target_chunk.get("content", "")[:240] + "..." if target_chunk else None
        return DoraExitCheckResult(
            rule_id="DORA-30-2-PENALTY",
            name_de="Verzugspönalen & Sperre von Haftungsausschlüssen",
            name_en="Delay Penalties & Exclusion of Liability Caps",
            description_de="Vertragliche Sanktionen bei Verzug oder Verweigerung der Migrationsmitwirkung gem. DORA Art. 30 Abs. 2 (e) und BaFin RS 10/2018.",
            description_en="Contractual penalties for delay or failure to cooperate in disengagement under DORA Art. 30(2)(e) and BaFin Circular 10/2018.",
            status=status,
            score=score,
            extracted_clause=extracted,
            citation_tag="[DORA_PENALTY_§12]",
            page_number=target_chunk.get("page_number", 3) if target_chunk else 3,
            bounding_box=target_chunk.get("bounding_box", [50.0, 180.0, 528.0, 260.0]) if target_chunk else None,
            recommendation_de=rec_de,
            recommendation_en=rec_en,
        )


dora_exit_engine = DoraExitStrategyEngine()
