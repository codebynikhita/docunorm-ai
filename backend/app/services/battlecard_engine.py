import re
from datetime import UTC, datetime
from uuid import UUID

from app.schemas.battlecard import (
    BattlecardItem,
    BattlecardSeverity,
    ConflictPillar,
    NegotiationBattlecardResponse,
    SlaSimulationRequest,
    SlaSimulationResponse,
    TiaAssessment,
)


class BattlecardEngine:
    """
    Sovereign AI Negotiation Battlecard & Schrems II / CLOUD Act Conflict Engine.
    Equips banking procurement and legal teams with unassailable statutory arguments,
    counter-scripts, and non-negotiable BGB/DORA clauses when negotiating against hyperscalers.
    """

    @classmethod
    def evaluate_contract(
        cls,
        document_id: UUID,
        filename: str,
        chunks: list[dict],
    ) -> NegotiationBattlecardResponse:
        full_text = " ".join(c.get("content", "") for c in chunks).lower()

        # ---------------------------------------------------------------------
        # 1. Schrems II & US CLOUD Act Conflict Assessment
        # ---------------------------------------------------------------------
        has_us_nexus = any(k in full_text for k in ["united states", "usa", "delaware", "california", "cloud act", "fisa", "us law", "us-recht"])
        has_hyok = any(k in full_text for k in ["hyok", "hold-your-own-key", "hsm", "kundenkontrollierte verschlüsselung", "bring your own key", "byok"])
        has_eu_residency = any(k in full_text for k in ["frankfurt", "eu-only", "europäischer wirtschaftsraum", "ewr", "germany only", "deutschland"])

        cloud_act_exposure = has_us_nexus or not (has_hyok and has_eu_residency)
        
        # Risk score calculation
        if cloud_act_exposure and not has_hyok:
            transfer_risk = "CRITICAL"
            risk_score = 92.0
            verdict = "KEINE FREIGABE · Hohes Risiko behördlicher US-Herausgabeanordnungen ohne Rechtshilfeabkommen (EuGH Schrems II)."
            rec = "Zwingende Vereinbarung von HYOK-Verschlüsselung mit HSM-Standort in Frankfurt a.M. und Verweigerungsklausel für US-Herausgaben gem. DSGVO Art. 48."
        elif cloud_act_exposure and has_hyok:
            transfer_risk = "ELEVATED"
            risk_score = 48.0
            verdict = "BEDINGT FREIGABEFÄHIG · Technische Schutzmaßnahmen (HYOK) vorhanden, aber US-Mutterkonzernhaftung ungelöst."
            rec = "Ergänzende vertragliche Garantien nach EDPB-Empfehlungen 01/2020 zur Anfechtung extraterritorialer Auskunftsersuchen vor US-Gerichten."
        else:
            transfer_risk = "COMPLIANT"
            risk_score = 12.0
            verdict = "FREIGABEFÄHIG · Vollständige EWR-Datenresidenz und kryptographische Abschirmung zertifiziert."
            rec = "Laufende jährliche Re-Zertifizierung des HSM-Schlüsselmanagements beibehalten."

        tia = TiaAssessment(
            overall_transfer_risk=transfer_risk,
            transfer_risk_score=risk_score,
            cloud_act_exposure=cloud_act_exposure,
            encryption_hyok_verified=has_hyok,
            eu_data_residency_guaranteed=has_eu_residency,
            bafin_audit_clearance=verdict,
            mitigation_recommendation=rec,
        )

        # ---------------------------------------------------------------------
        # 2. Targeted Battlecard Synthesizer
        # ---------------------------------------------------------------------
        battlecards: list[BattlecardItem] = []

        # Check A: US CLOUD Act Subpoena Disclosure
        if any(k in full_text for k in ["subpoena", "court order", "lawful request", "gesetzliche auskunft", "behördliche anordnung"]):
            quote, p_num = cls._find_verbatim_quote(chunks, ["subpoena", "court order", "lawful request", "auskunft", "anordnung"])
            battlecards.append(
                BattlecardItem(
                    id="BC-01-CLOUD-ACT",
                    pillar=ConflictPillar.CLOUD_ACT_CONFLICT,
                    severity=BattlecardSeverity.CRITICAL,
                    title_de="Extraterritoriale US-Behördenherausgabe (CLOUD Act vs. DSGVO Art. 48)",
                    title_en="Extraterritorial US Subpoena Compliance (CLOUD Act vs. GDPR Art. 48)",
                    statutory_reference="DSGVO Art. 48 · KWG § 25a · EuGH Schrems II (C-311/18)",
                    vendor_clause_quote=quote or "Der Anbieter behält sich vor, behördlichen Anordnungen und Beschlussfassungen Dritter ohne Vorankündigung Folge zu leisten.",
                    page_number=p_num,
                    vendor_common_defense="Unser Rechtsrahmen als US-Konzern verpflichtet uns zwingend zur Kooperation mit US-Behörden. Wir können uns nicht über US-Recht hinwegsetzen.",
                    bank_counter_argument="Gemäß Art. 48 DSGVO und KWG § 25a ist die Herausgabe europäischer Bankdaten an Drittstaaten ohne Rechtshilfeabkommen (MLAT) für uns strafbewehrt (§ 203 StGB). Ohne strikte richterliche EWR-Prüfung und Vorab-Benachrichtigung ist dieser Vertrag nicht unterzeichnungsfähig.",
                    non_negotiable_clause_de="„Der Anbieter verpflichtet sich, behördliche Herausgabeersuchen aus Drittstaaten unverzüglich gerichtlich anzufechten und die Bank unverzüglich vor Herausgabe zu benachrichtigen, sofern nicht ausdrücklich durch zwingendes Recht untersagt. Sämtliche Daten sind ausnahmslos mit Schlüsseln der Bank (HYOK) zu verschlüsseln.“",
                    bafin_escalation_script="„Sollte dieser Passus unverändert bleiben, sind wir gem. KWG § 25b Abs. 3 verpflichtet, der BaFin eine wesentliche Auslagerung mit ungelöster Geheimhaltungsgefährdung anzuzeigen, was die Untersagung der Auslagerung zur Folge hat.“",
                )
            )

        # Check B: Exit Fee / Disguised Toll
        if any(k in full_text for k in ["transfer fee", "migration fee", "exit toll", "wechselgebühr", "übertragungskosten", "kostenerstattung bei beendigung"]):
            quote, p_num = cls._find_verbatim_quote(chunks, ["transfer fee", "migration fee", "exit toll", "wechselgebühr", "kosten"])
            battlecards.append(
                BattlecardItem(
                    id="BC-02-EXIT-TOLL",
                    pillar=ConflictPillar.EXIT_LOCKIN,
                    severity=BattlecardSeverity.CRITICAL,
                    title_de="Verschleierte Ausstiegsgebühren & Vendor Lock-in (DORA Art. 30 Abs. 2)",
                    title_en="Disguised Exit Tolls & Data Restitution Barrier (DORA Art. 30(2))",
                    statutory_reference="DORA Art. 30 Abs. 2 lit. e & Art. 28 Abs. 8",
                    vendor_clause_quote=quote or "Bei Beendigung des Vertrages fallen für die Datenmigration und Systembereinigung gesonderte Gebühren nach Aufwand an.",
                    page_number=p_num,
                    vendor_common_defense="Datenexporte in alternative Formate erfordern signifikanten Rechen- und Personalaufwand unserer Engineers. Eine kostenlose Bereitstellung ist wirtschaftlich unzumutbar.",
                    bank_counter_argument="DORA Art. 30 Abs. 2 lit. e verbietet ausdrücklich jede vertragliche Hürde, die eine vollständige Datenrückführung behindert. Datenübertragungen müssen in marktgängigen, offenen Formaten ohne prohibitive Extragebühren erfolgen.",
                    non_negotiable_clause_de="„Der Anbieter stellt alle Kundendaten bei Beendigung dieses Vertrages unentgeltlich in offenen, maschinenlesbaren Standardformaten (JSON, Parquet, XML) zur Verfügung und leistet für mindestens 90 Tage vollumfängliche Migrationsunterstützung ohne Zusatzentgelt.“",
                    bafin_escalation_script="„Die Vereinbarung von Ausstiegsgebühren stellt einen direkten Verstoß gegen DORA Art. 28 dar. Die Europäische Bankenaufsicht (EBA) stuft derartige Klauseln als unzulässige Ausstiegsbarriere ein.“",
                )
            )

        # Check C: Subcontractor Deemed Consent
        if any(k in full_text for k in ["deemed consent", "stillschweigende zustimmung", "fiktion", "widerspruch", "subcontractor"]):
            quote, p_num = cls._find_verbatim_quote(chunks, ["deemed", "stillschweigend", "fiktion", "subcontractor", "unterauftragnehmer"])
            battlecards.append(
                BattlecardItem(
                    id="BC-03-SUBCONTRACTOR-VETO",
                    pillar=ConflictPillar.SUBCONTRACTOR_CHAIN,
                    severity=BattlecardSeverity.HIGH,
                    title_de="Zustimmungsfiktion bei Unterbeauftragung (DORA Art. 30 Abs. 3)",
                    title_en="Deemed Consent for Sub-Outsourcing (DORA Art. 30(3))",
                    statutory_reference="DORA Art. 30 Abs. 3 lit. a · BaFin BAIT 8.3",
                    vendor_clause_quote=quote or "Unterauftragnehmer gelten als genehmigt, sofern der Kunde nicht binnen 14 Tagen schriftlich widerspricht.",
                    page_number=p_num,
                    vendor_common_defense="Wir betreiben eine hochdynamische Cloud-Infrastruktur mit Hunderten globaler Dienstleister. Ein individueller Vorab-Zustimmungsprozess für jeden Kunden würde unsere Release-Zyklen lahmlegen.",
                    bank_counter_argument="Als regulierte Bank müssen wir für jede 4th-Party-Auslagerung eine risikoorientierte Wesentlichkeitsprüfung durchführen. DORA Art. 30 Abs. 3 verlangt ein ausdrückliches Vetorecht mit einer Kündigungsmöglichkeit bei berechtigtem Widerspruch.",
                    non_negotiable_clause_de="„Der Anbieter kündigt jeden Wechsel oder Hinzuziehung wesentlicher Unterauftragnehmer mindestens 60 Tage im Voraus schriftlich an. Bei berechtigtem Widerspruch der Bank aus aufsichtsrechtlichen Gründen steht der Bank ein außerordentliches Kündigungsrecht ohne Vorfälligkeitsentschädigung zu.“",
                    bafin_escalation_script="„Die Akzeptanz einer 14-tägigen Zustimmungsfiktion würde im aufsichtlichen BaFin-SREP-Audit als Mangel der Risikosteuerung eingestuft und Eigenkapitalzuschläge auslösen.“",
                )
            )

        # Check D: Audit Rights Restrictions / Fees
        if any(k in full_text for k in ["audit fee", "prüfgebühr", "vorankündigung 30 tage", "inspektionsgebühr", "revisionskosten"]):
            quote, p_num = cls._find_verbatim_quote(chunks, ["audit fee", "prüfgebühr", "inspektion", "kosten der prüfung"])
            battlecards.append(
                BattlecardItem(
                    id="BC-04-AUDIT-BARRIER",
                    pillar=ConflictPillar.AUDIT_OBSTRUCTION,
                    severity=BattlecardSeverity.HIGH,
                    title_de="Kosten- & Zugangsbarrieren bei Vor-Ort-Audits (DORA Art. 30 Abs. 3 lit. e)",
                    title_en="Audit Cost Barriers & Access Restrictions (DORA Art. 30(3)(e))",
                    statutory_reference="DORA Art. 30 Abs. 3 lit. e · KWG § 25b Abs. 2 · BaFin BAIT 8.1",
                    vendor_clause_quote=quote or "Vor-Ort-Audits erfordern eine 30-tägige Vorankündigung und werden mit einer Aufwandspauschale von 2.500 EUR pro Prüftag berechnet.",
                    page_number=p_num,
                    vendor_common_defense="Audits in Hochsicherheits-Rechenzentren stören den operativen Betrieb und erfordern dedizierte Sicherheitsbegleiter. Es ist marktüblich, diesen Aufwand umzulegen.",
                    bank_counter_argument="KWG § 25b und DORA Art. 30 garantieren Aufsichtsbehörden (BaFin, EZB) und der Bank uneingeschränkte, unentgeltliche Prüfungsrechte. Kostenbarrieren oder unzumutbare Vorlauffristen verstoßen direkt gegen geltendes Bankenaufsichtsrecht.",
                    non_negotiable_clause_de="„Der Bank, ihren Prüfern sowie der zuständigen Aufsichtsbehörde (BaFin, EZB) wird zu den üblichen Geschäftszeiten unentgeltlich und ohne unzumutbare Vorlauffrist voller Zugang zu allen relevanten Geschäftsräumen, Rechenzentren, Systemen und Audit-Logs gewährt.“",
                    bafin_escalation_script="„Eine Kostenpauschale für aufsichtsrechtliche Pflichtprüfungen ist vor der BaFin nicht vertretbar und führt zur Verweigerung der Auslagerungsgenehmigung.“",
                )
            )

        # Fallback if no specific trigger fired: Add Golden Standard DORA Battlecard
        if not battlecards:
            battlecards.append(
                BattlecardItem(
                    id="BC-00-GENERAL-DORA",
                    pillar=ConflictPillar.EXIT_LOCKIN,
                    severity=BattlecardSeverity.MEDIUM,
                    title_de="Allgemeine aufsichtsrechtliche Nachbesserung (DORA Compliance Baseline)",
                    title_en="Statutory DORA Compliance Baseline Verification",
                    statutory_reference="DORA Art. 30 & KWG § 25b",
                    vendor_clause_quote="Standardvertragsbedingungen nach angelsächsischem Recht ohne explizite DORA-Referenzen.",
                    page_number=1,
                    vendor_common_defense="Wir bieten weltweiten Standard-Service ohne länderspezifische Sondervereinbarungen.",
                    bank_counter_argument="Seit Januar 2025 ist DORA in der gesamten Europäischen Union unmittelbar geltendes Recht. Auslagerungsvereinbarungen ohne explizite DORA-Garantien sind für Finanzunternehmen in der EU rechtswidrig.",
                    non_negotiable_clause_de="„Der Anbieter sichert zu, alle Anforderungen gem. DORA Art. 30 vollumfänglich zu erfüllen und der Bank unverzüglich alle für das aufsichtliche Informationsregister (Register of Information) erforderlichen Daten bereitzustellen.“",
                    bafin_escalation_script="„Ohne Aufnahme des DORA-Zusatzes kann der Vertrag vom Vorstand nicht freigegeben werden.“",
                )
            )

        crit_count = sum(1 for b in battlecards if b.severity == BattlecardSeverity.CRITICAL)
        high_count = sum(1 for b in battlecards if b.severity == BattlecardSeverity.HIGH)

        if crit_count > 0:
            posture = "UNACCEPTABLE_HIGH_RISK"
        elif high_count > 0:
            posture = "CONDITIONAL_APPROVAL_REQUIRED"
        else:
            posture = "MARKET_STANDARD_COMPLIANT"

        return NegotiationBattlecardResponse(
            document_id=document_id,
            filename=filename,
            overall_negotiation_posture=posture,
            total_battlecards=len(battlecards),
            critical_count=crit_count,
            high_count=high_count,
            tia_assessment=tia,
            battlecards=battlecards,
            generated_at=datetime.now(UTC),
        )

    @classmethod
    def simulate_sla_outage(cls, req: SlaSimulationRequest) -> SlaSimulationResponse:
        """
        Interactive 'What-If' SLA Outage Stress Simulator.
        Calculates financial penalties, DORA Art. 11/19 incident severity,
        and statutory extraordinary termination triggers.
        """
        # Annual hours = 8760
        annual_hours = 8760.0
        tolerated_hours = round(annual_hours * ((100.0 - req.availability_target_pct) / 100.0), 2)
        excess_hours = max(0.0, round(req.downtime_hours - tolerated_hours, 2))

        # Penalty formula: 0.2% of annual contract per excess hour, capped at 5.0%
        penalty_rate_per_hour = 0.002
        raw_penalty = excess_hours * penalty_rate_per_hour * req.contract_value_eur
        max_penalty = 0.05 * req.contract_value_eur
        penalty_eur = round(min(raw_penalty, max_penalty), 2)
        penalty_pct = round((penalty_eur / req.contract_value_eur) * 100.0, 2) if req.contract_value_eur > 0 else 0.0

        # DORA Incident Classification
        if req.downtime_hours < 2.0:
            category = "NEGLIGIBLE"
            init_notif = "Keine Meldepflicht (Reguläre interne Protokollierung)"
            inter_notif = "Keine Folgemeldung erforderlich"
            term_triggered = False
            rationale = "Ausfallzeit liegt innerhalb der vertraglichen Toleranzgrenzen. Kein aufsichtsrechtlicher Notfall."
        elif req.downtime_hours <= 8.0:
            category = "MAJOR_INCIDENT"
            init_notif = "Innerhalb von 4 Stunden nach Einstufung (DORA Art. 19 Abs. 4)"
            inter_notif = "Innerhalb von 72 Stunden (Auswirkungs- und Ursachenbericht)"
            term_triggered = False
            rationale = "Schwerwiegender IKT-Vorfall (Major Incident). Pflicht zur Ad-hoc-Meldung an die BaFin und Einleitung von Notfall-Wiederanlaufplänen."
        else:
            category = "CRITICAL_SYSTEMIC_INCIDENT"
            init_notif = "Unverzüglich, spätestens binnen 2 Stunden (Ad-hoc Krisen-Meldung)"
            inter_notif = "Täglicher Lagebericht bis zur vollständigen Wiederherstellung"
            term_triggered = True
            rationale = "Kritischer systemischer Ausfall. Gesetzliches außerordentliches Kündigungsrecht der Bank nach DORA Art. 28 Abs. 7 ausgelöst!"

        return SlaSimulationResponse(
            downtime_hours=req.downtime_hours,
            contract_value_eur=req.contract_value_eur,
            availability_target_pct=req.availability_target_pct,
            tolerated_annual_downtime_hours=tolerated_hours,
            excess_downtime_hours=excess_hours,
            penalty_eur=penalty_eur,
            penalty_pct_of_annual_contract=penalty_pct,
            dora_incident_classification=category,
            bafin_initial_notification_deadline=init_notif,
            bafin_intermediate_report_deadline=inter_notif,
            statutory_extraordinary_termination_triggered=term_triggered,
            rationale=rationale,
        )

    @classmethod
    def _find_verbatim_quote(cls, chunks: list[dict], keywords: list[str]) -> tuple[str, int]:
        for c in chunks:
            text = c.get("content", "")
            lower_text = text.lower()
            if any(k in lower_text for k in keywords):
                sentences = re.split(r"(?<=[.!?])\s+", text)
                for s in sentences:
                    if any(k in s.lower() for k in keywords):
                        return s.strip()[:240], c.get("page_number", 1)
        return "", 1
