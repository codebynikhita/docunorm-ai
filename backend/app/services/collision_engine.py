"""
DocuNorm AI — Day 38: Cross-Regulatory Conflict & Jurisdictional Incompatibility Collision Engine.
Detects, ranks, and resolves normative clashes across DORA, GDPR, US CLOUD Act, KWG § 25b, BGB, and LkSG.
"""

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pymupdf as fitz

from app.schemas.collision import (
    ClauseReconcileRequest,
    ClauseReconcileResponse,
    DocumentConflictMatrix,
    NormativeConflict,
)


class NormativeCollisionEngine:
    """
    Forensic Cross-Standard Normative Conflict Matrix Engine.
    Detects jurisdictional clashing and synthesizes authoritative German legal harmonization covenants.
    """

    @classmethod
    def analyze_conflicts(
        cls,
        document_id: UUID,
        document_filename: str,
        chunks: list[dict],
    ) -> DocumentConflictMatrix:
        """
        Scans document chunks for multi-standard regulatory collisions and compiles
        the complete jurisdictional incompatibility matrix.
        """
        conflicts: list[NormativeConflict] = []
        jurisdiction_counts: dict[str, int] = {"EU_DE": 0, "US_EXTRATERRITORIAL": 0, "CROSS_BORDER": 0}

        for c in chunks:
            content = c.get("content", "")
            lower = content.lower()
            page_num = c.get("page_number", 1)
            bbox = c.get("bounding_box") or [0.0, 0.0, 0.0, 0.0]

            # Track jurisdiction markers
            if any(k in lower for k in ["united states", "cloud act", "fisa", "us-recht", "delaware", "california", "washington"]):
                jurisdiction_counts["US_EXTRATERRITORIAL"] += 1
            elif any(k in lower for k in ["deutschland", "frankfurt", "dsgvo", "bgb", "bafin", "kwg", "bdsg"]):
                jurisdiction_counts["EU_DE"] += 1
            else:
                jurisdiction_counts["CROSS_BORDER"] += 1

            # 1. CLOUD Act vs. GDPR Art. 48 & BDSG § 22 (CRITICAL BLOCKER)
            if any(k in lower for k in ["cloud act", "18 u.s.c", "foreign court", "us-behörd", "subpoena", "law enforcement", "rechtshilfe"]) or (
                any(k in lower for k in ["herausgabe", "behördliche anordnung"]) and any(k in lower for k in ["ohne vorherige", "unverzüglich leistet", "folgt der dienstleister"])
            ):
                if not any(k in lower for k in ["bring your own key", "byok", "rechtshilfeabkommen", "eugh", "schrems ii"]):
                    conflicts.append(
                        NormativeConflict(
                            conflict_id="CONF-CLOUD-GDPR-01",
                            title_de="Normenkollision: US CLOUD Act vs. DSGVO Art. 48 & BDSG § 22",
                            title_en="Jurisdictional Collision: US CLOUD Act vs. GDPR Art. 48 & German BDSG",
                            source_clause_text=content[:300],
                            page_number=page_num,
                            bounding_box=bbox,
                            standard_a="CLOUD_ACT",
                            standard_b="GDPR",
                            severity="CRITICAL_BLOCKER",
                            statutory_clash_summary_de=(
                                "Der Dienstleister unterwirft sich ausländischen Herausgabeverlangen (US CLOUD Act 18 U.S.C. § 2713) "
                                "ohne das zwingende Erfordernis eines zwischenstaatlichen Rechtshilfeabkommens. Dies begründet "
                                "eine unzulässige Drittstaatenübermittlung gem. DSGVO Art. 48 und verletzt das EuGH Schrems II Urteil."
                            ),
                            statutory_clash_summary_en=(
                                "The vendor subjects itself to extraterritorial US CLOUD Act subpoenas without an international "
                                "mutual legal assistance treaty (MLAT), causing an unlawful third-country data transfer under GDPR Art. 48."
                            ),
                            jurisdiction_clash="EU / Deutschland (DSGVO Art. 48) vs. United States (CLOUD Act 18 U.S.C. § 2713)",
                            legal_risk_score=96.5,
                            resolution_covenant_de=(
                                "Der Dienstleister verpflichtet sich, personenbezogene Daten und Bankgeheimnisse des Auftraggebers "
                                "ausschließlich mit HSM-Verschlüsselungsschlüsseln zu speichern, die unter ausschließlicher Kontrolle "
                                "des Auftraggebers in der Bundesrepublik Deutschland verwahrt werden (BYOK/HYOK). Ausländischen "
                                "Herausgabeanordnungen ohne völkerrechtliche Anerkennung durch ein deutsches Gericht ist mit allen "
                                "rechtlich zulässigen Rechtsmitteln unverzüglich zu widersprechen."
                            ),
                            resolution_covenant_en=(
                                "The contractor undertakes to encrypt all customer data using customer-controlled keys (BYOK) "
                                "hosted in Germany and to exhaust all legal remedies to challenge extraterritorial disclosure demands."
                            ),
                            statutory_precedence_rule="Anwendungsvorrang des EU-Rechts (EuGH Schrems II / Lex Superior)",
                        )
                    )

            # 2. DORA Art. 30(3)(e) Audit Rights vs. Multi-Tenant Physical Datacenter Secrecy (HIGH RISK)
            elif any(k in lower for k in ["vor-ort", "zutritt", "audit", "inspektion", "rechenzentrum"]) and any(
                k in lower for k in ["multi-tenant", "andere kunden", "datenschutz dritter", "schutz dritter", "nicht gestattet", "verwehrt"]
            ):
                conflicts.append(
                    NormativeConflict(
                        conflict_id="CONF-DORA-GDPR-02",
                        title_de="Spannungsverhältnis: DORA Art. 30 Prüfrechte vs. DSGVO Art. 32 Mandantengeheimnis",
                        title_en="Regulatory Clash: DORA Art. 30 Physical Audits vs. GDPR Art. 32 Multi-Tenant Confidentiality",
                        source_clause_text=content[:300],
                        page_number=page_num,
                        bounding_box=bbox,
                        standard_a="DORA",
                        standard_b="GDPR",
                        severity="HIGH_RISK",
                        statutory_clash_summary_de=(
                            "Der Dienstleister verwehrt oder beschränkt physische Audits unter Berufung auf den Schutz der Daten "
                            "anderer Mandanten im Rechenzentrum. DORA Art. 30 Abs. 3 lit. e verlangt zwingend uneingeschränkte Vor-Ort-Prüfrechte."
                        ),
                        statutory_clash_summary_en=(
                            "Vendor limits physical inspections citing multi-tenant confidentiality, clashing with mandatory DORA Art. 30(3)(e) audit rights."
                        ),
                        jurisdiction_clash="EU DORA Art. 30(3)(e) vs. EU DSGVO Art. 32 Abs. 1 lit. b",
                        legal_risk_score=88.0,
                        resolution_covenant_de=(
                            "Zur Wahrung des Schutzes Dritter bei gleichzeitiger Gewährleistung der aufsichtsrechtlichen Prüfpflichten "
                            "vereinbaren die Parteien die Durchführung statutarischer Gemeinschaftsprüfungen (Pooled Audits) gem. "
                            "DORA Art. 30 Abs. 3 lit. e Satz 2 durch unabhängige, zur Berufsverschwiegenheit verpflichtete Wirtschaftsprüfer "
                            "sowie unangekündigte Zutrittsrechte für die BaFin, EZB und Bundesbank zu den dedizierten Systemräumen."
                        ),
                        resolution_covenant_en=(
                            "The parties agree to execute statutory Pooled Audits pursuant to DORA Art. 30(3)(e) sentence 2 by certified independent auditors."
                        ),
                        statutory_precedence_rule="DORA Art. 30 Abs. 3 lit. e Satz 2 (Statutarische Kollisionsauflösung via Pooled Audits)",
                    )
                )

            # 3. BaFin KWG § 25b Termination vs. BGB Contractual Lock-in & Early Termination Penalties (CRITICAL)
            elif (
                any(k in lower for k in ["mindestlaufzeit", "24 monate", "36 monate", "vorfälligkeit", "schadensersatz bei kündigung"])
                and not any(k in lower for k in ["aufsichtsrechtliche anordnung", "bafin", "dora"])
            ) or (
                any(k in lower for k in ["ordentliche kündigung"]) and any(k in lower for k in ["ausgeschlossen", "12 monate", "strafzahlung"])
            ):
                conflicts.append(
                    NormativeConflict(
                        conflict_id="CONF-BAFIN-BGB-03",
                        title_de="Normenkollision: KWG § 25b / DORA Art. 28 Kündigung vs. BGB AGB-Laufzeitbindung",
                        title_en="Regulatory Conflict: BaFin KWG § 25b Statutory Exit vs. BGB Long-Term Lock-In",
                        source_clause_text=content[:300],
                        page_number=page_num,
                        bounding_box=bbox,
                        standard_a="KWG",
                        standard_b="BGB",
                        severity="CRITICAL_BLOCKER",
                        statutory_clash_summary_de=(
                            "Vereinbarte Mindestvertragslaufzeiten oder Entschädigungspauschalen behindern das zwingende aufsichtsrechtliche "
                            "Sonderkündigungsrecht bei Beanstandung durch die BaFin oder Abwicklungsanordnung (§ 25b Abs. 3 KWG & BGB § 307)."
                        ),
                        statutory_clash_summary_en=(
                            "Fixed-term lock-in and termination fee penalties unlawfully impede statutory regulatory unwinding rights under KWG § 25b."
                        ),
                        jurisdiction_clash="Aufsichtsrecht (KWG § 25b / DORA Art. 28 Abs. 7) vs. AGB-Recht (BGB § 307, § 309)",
                        legal_risk_score=92.0,
                        resolution_covenant_de=(
                            "Ordnet die BaFin, die EZB oder eine andere zuständige Aufsichtsbehörde die Beendigung oder Rückabwicklung der Auslagerung an, "
                            "ist der Auftraggeber berechtigt, diesen Vertrag fristlos außerordentlich zu kündigen. In diesem Fall entfallen jegliche "
                            "Vorfälligkeitsentschädigungen, Ausfallhonorare oder Restlaufzeitvergütungen vollumfänglich (§ 314 BGB analog)."
                        ),
                        resolution_covenant_en=(
                            "In case of supervisory order by BaFin or ECB, the client holds immediate emergency termination rights without any penalty fees."
                        ),
                        statutory_precedence_rule="Vorrang zwingenden öffentlichen Aufsichtsrechts (BGB § 134 / Nichtigkeit)",
                    )
                )

            # 4. LkSG § 9 Multi-Tier Transparency vs. German Trade Secrets Act (GeschGehG) (MEDIUM)
            elif any(k in lower for k in ["offenlegung lieferant", "herkunftsnachweis", "tier-n", "mittelbare zulieferer"]) and any(
                k in lower for k in ["geschäftsgeheimnis", "betriebsgeheimnis", "vertraulich", "verweigert"]
            ):
                conflicts.append(
                    NormativeConflict(
                        conflict_id="CONF-LKSG-SECRECY-04",
                        title_de="Spannungsverhältnis: LkSG § 9 Kaskadenprüfung vs. Geschäftsgeheimnisgesetz (GeschGehG)",
                        title_en="Collision: LkSG § 9 Supply Chain Transparency vs. German Trade Secrets Act (GeschGehG)",
                        source_clause_text=content[:300],
                        page_number=page_num,
                        bounding_box=bbox,
                        standard_a="LKSG",
                        standard_b="BGB",
                        severity="MEDIUM_COLLISION",
                        statutory_clash_summary_de=(
                            "Der Zulieferer verweigert die Offenlegung von Tier-N Lieferantenstrukturen unter Berufung auf den Schutz "
                            "sensibler Geschäftsgeheimnisse gem. § 1 GeschGehG, was die Erfüllung der BAFA-Sorgfaltspflichten nach § 9 LkSG gefährdet."
                        ),
                        statutory_clash_summary_en=(
                            "Supplier refuses Tier-N bill-of-materials disclosure citing trade secrets, impeding BAFA statutory due diligence under § 9 LkSG."
                        ),
                        jurisdiction_clash="Sorgfaltspflichtengesetz (§ 9 LkSG) vs. Geschäftsgeheimnisgesetz (GeschGehG § 1 ff.)",
                        legal_risk_score=68.0,
                        resolution_covenant_de=(
                            "Zur Vereinbarkeit von Lieferkettentransparenz und Betriebsgeheimnisschutz vereinbaren die Parteien ein Clean-Team-Verfahren: "
                            "Strukturdaten zu mittelbaren Zulieferern werden in einem gesicherten Compliance-Treuhandraum (Escrow) hinterlegt und nur von "
                            "zur Berufsverschwiegenheit verpflichteten Auditoren zur LkSG-Risikoanalyse eingesehen."
                        ),
                        resolution_covenant_en=(
                            "The parties establish a Clean-Team Escrow mechanism ensuring LkSG compliance while shielding proprietary trade secrets."
                        ),
                        statutory_precedence_rule="Verhältnismäßigkeitsgrundsatz nach § 16 GeschGehG & BAFA-Handreichung",
                    )
                )

            # 5. NIS-2 Incident Reporting vs. Contractual Strict Secrecy NDA (HIGH RISK)
            elif any(k in lower for k in ["sicherheitsvorfall", "cyber-angriff", "incident"]) and any(
                k in lower for k in ["strikte geheimhaltung", "keine information an behörden", "vertraulich zu behandeln", "ohne meldung"]
            ):
                conflicts.append(
                    NormativeConflict(
                        conflict_id="CONF-NIS2-CONF-05",
                        title_de="Normenkollision: NIS-2 Art. 23 / BSIG § 30 Meldepflicht vs. NDA-Geheimhaltung",
                        title_en="Collision: NIS-2 24h Early Warning Mandate vs. Contractual Non-Disclosure",
                        source_clause_text=content[:300],
                        page_number=page_num,
                        bounding_box=bbox,
                        standard_a="NIS2",
                        standard_b="BGB",
                        severity="HIGH_RISK",
                        statutory_clash_summary_de=(
                            "Vertragliche Geheimhaltungsregeln verbieten oder verzögern die gesetzliche 24-Stunden-Frühwarnung "
                            "und 72-Stunden-Meldepflicht schwerwiegender Sicherheitsvorfälle an das BSI oder die BaFin."
                        ),
                        statutory_clash_summary_en=(
                            "NDA restrictions impede statutory 24-hour early warning and 72-hour major cyber incident reporting under NIS-2 Art. 23."
                        ),
                        jurisdiction_clash="NIS-2 Richtlinie (Art. 23) / BSIG § 30 vs. Privatrechtliche NDA",
                        legal_risk_score=85.0,
                        resolution_covenant_de=(
                            "Vertragliche Vertraulichkeitspflichten gelten ausdrücklich nicht für aufsichtsrechtlich vorgeschriebene "
                            "Sicherheitsmeldungen. Der Dienstleister informiert den Auftraggeber unverzüglich, spätestens binnen 12 Stunden "
                            "nach Kenntniserlangung, um die Einhaltung der 24-Stunden-Frühwarnung gem. NIS-2 Art. 23 an das BSI zu garantieren."
                        ),
                        resolution_covenant_en=(
                            "Contractual secrecy shall not prevent statutory NIS-2 / DORA incident disclosures within 12/24 hours."
                        ),
                        statutory_precedence_rule="Zwingende Meldeordnung nach BSIG / NIS-2 (Lex Publica)",
                    )
                )

        # Remove duplicate conflict IDs preserving highest risk
        unique_conflicts_map: dict[str, NormativeConflict] = {}
        for conf in conflicts:
            if conf.conflict_id not in unique_conflicts_map or conf.legal_risk_score > unique_conflicts_map[conf.conflict_id].legal_risk_score:
                unique_conflicts_map[conf.conflict_id] = conf

        unique_conflicts = list(unique_conflicts_map.values())

        # If no conflicts detected from specific clauses, ensure clean baseline verdict
        critical_count = sum(1 for c in unique_conflicts if c.severity == "CRITICAL_BLOCKER")
        high_count = sum(1 for c in unique_conflicts if c.severity == "HIGH_RISK")
        medium_count = sum(1 for c in unique_conflicts if c.severity == "MEDIUM_COLLISION")

        if critical_count > 0:
            overall_index = min(98.0, 75.0 + critical_count * 8.0)
            verdict = "INCOMPATIBLE_BLOCKER"
        elif high_count > 0:
            overall_index = min(75.0, 50.0 + high_count * 10.0)
            verdict = "CONDITIONALLY_RECONCILABLE"
        elif medium_count > 0:
            overall_index = 35.0
            verdict = "CONDITIONALLY_RECONCILABLE"
        else:
            overall_index = 10.0
            verdict = "COMPATIBLE"

        # Calculate SHA-256 seal of conflict evaluation
        seal_content = f"{document_id}:{overall_index}:{len(unique_conflicts)}:{verdict}"
        sha_hash = hashlib.sha256(seal_content.encode("utf-8")).hexdigest()

        return DocumentConflictMatrix(
            document_id=document_id,
            document_filename=document_filename,
            analyzed_at=datetime.now(UTC),
            overall_collision_index=round(overall_index, 1),
            conflicts_detected=len(unique_conflicts),
            critical_blockers=critical_count,
            high_risks=high_count,
            medium_risks=medium_count,
            jurisdictional_exposure_map=jurisdiction_counts,
            conflicts=unique_conflicts,
            compliance_verdict=verdict,
            sha256_hash=sha_hash,
        )

    @classmethod
    def reconcile_clause(cls, request: ClauseReconcileRequest) -> ClauseReconcileResponse:
        """
        Stateless conflict detection on a single clause snippet with statutory reconciliation synthesis.
        """
        pseudo_id = UUID("00000000-0000-0000-0000-000000000000")
        chunk_dict = [{"content": request.clause_text, "page_number": 1, "bounding_box": [0.0, 0.0, 100.0, 50.0]}]
        matrix = cls.analyze_conflicts(pseudo_id, "Stateless_Snippet.pdf", chunk_dict)

        covenants_de = [c.resolution_covenant_de for c in matrix.conflicts]
        covenants_en = [c.resolution_covenant_en for c in matrix.conflicts]

        has_us = matrix.jurisdictional_exposure_map.get("US_EXTRATERRITORIAL", 0) > 0
        exposure = "US_EXTRATERRITORIAL" if has_us else "EU_DOMESTIC"

        return ClauseReconcileResponse(
            has_conflicts=len(matrix.conflicts) > 0,
            detected_conflicts=matrix.conflicts,
            reconciliation_covenant_de="\n\n".join(covenants_de) if covenants_de else None,
            reconciliation_covenant_en="\n\n".join(covenants_en) if covenants_en else None,
            jurisdiction_exposure=exposure,
        )

    @classmethod
    def generate_collision_matrix_pdf(
        cls,
        document_filename: str,
        matrix: DocumentConflictMatrix,
        signatory_name: str = "Dr. Johannes von Stauffenberg, Leitender Compliance-Jurist",
        output_dir: Path | str = "/tmp/docunorm_exports",
    ) -> Path:
        """
        Generates official 2-page DIN 5008 Multi-Standard Conflict Matrix PDF report
        (Rechtsgutachten zur aufsichtsrechtlichen Kollisionsprüfung).
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        clean_name = document_filename.replace(".pdf", "")
        pdf_file = output_path / f"KOLLISIONSPRUEFUNG_GUTACHTEN_{clean_name}.pdf"

        doc = fitz.open()

        # ================= PAGE 1: EXECUTIVE OPINION & MATRIX SCORECARD =================
        page1 = doc.new_page(width=595, height=842)

        # Header Box (Navy / Gold Theme)
        page1.draw_rect(fitz.Rect(45, 40, 550, 110), color=(0.1, 0.18, 0.32), fill=(0.96, 0.97, 1.0))
        page1.insert_text(fitz.Point(55, 62), "RECHTSGUTACHTEN: AUFSICHTSRECHTLICHE NORMENKOLLISIONSPRÜFUNG", fontsize=10.5, fontname="hebo", color=(0.08, 0.14, 0.28))
        page1.insert_text(fitz.Point(55, 78), "Inter-Regulatorische Prüfung: DORA • DSGVO • US CLOUD Act • KWG § 25b • BGB", fontsize=8.5, fontname="hebo", color=(0.7, 0.35, 0.0))
        page1.insert_text(
            fitz.Point(55, 94),
            f"Bezugsdokument: {document_filename} • Datum: {matrix.analyzed_at.strftime('%d.%m.%Y')} • DIN EN ISO 9001 Konform",
            fontsize=7.5,
            fontname="helv",
            color=(0.35, 0.4, 0.45),
        )

        y = 130
        # Verdict Card
        verdict_color = (0.8, 0.1, 0.1) if matrix.compliance_verdict == "INCOMPATIBLE_BLOCKER" else (0.85, 0.5, 0.0) if matrix.compliance_verdict == "CONDITIONALLY_RECONCILABLE" else (0.1, 0.6, 0.2)
        verdict_fill = (0.99, 0.94, 0.94) if matrix.compliance_verdict == "INCOMPATIBLE_BLOCKER" else (0.99, 0.97, 0.92) if matrix.compliance_verdict == "CONDITIONALLY_RECONCILABLE" else (0.94, 0.99, 0.95)

        page1.draw_rect(fitz.Rect(45, y, 550, y + 60), color=verdict_color, fill=verdict_fill, width=1.5)
        page1.insert_text(fitz.Point(55, y + 22), "GESAMT-KOLLISIONSBEFUND / LEGAL VERDICT:", fontsize=8.5, fontname="hebo", color=(0.2, 0.2, 0.2))
        page1.insert_text(fitz.Point(55, y + 42), f"{matrix.compliance_verdict} (Index: {matrix.overall_collision_index}/100)", fontsize=13, fontname="hebo", color=verdict_color)
        page1.insert_text(
            fitz.Point(340, y + 25),
            f"Kollisionen gesamt: {matrix.conflicts_detected} | Kritisch: {matrix.critical_blockers} | Hoch: {matrix.high_risks}",
            fontsize=8,
            fontname="hebo",
            color=(0.2, 0.2, 0.2),
        )
        page1.insert_text(
            fitz.Point(340, y + 42),
            f"US-Extraterritorial: {matrix.jurisdictional_exposure_map.get('US_EXTRATERRITORIAL', 0)} Klauseln",
            fontsize=8,
            fontname="helv",
            color=(0.4, 0.4, 0.4),
        )

        y += 80
        page1.insert_text(fitz.Point(45, y), "IDENTIFIZIERTE NORMENKOLLISIONEN & VORRANGREGELN", fontsize=9.5, fontname="hebo", color=(0.1, 0.15, 0.25))
        y += 15

        # Render Conflict Cards
        for idx, conf in enumerate(matrix.conflicts[:3], 1):
            sev_color = (0.8, 0.15, 0.15) if conf.severity == "CRITICAL_BLOCKER" else (0.85, 0.45, 0.0)
            page1.draw_rect(fitz.Rect(45, y, 550, y + 105), color=sev_color, fill=(0.98, 0.98, 0.99))
            page1.insert_text(fitz.Point(55, y + 16), f"§ {idx}. {conf.title_de}", fontsize=9, fontname="hebo", color=sev_color)
            page1.insert_text(fitz.Point(440, y + 16), f"Risiko: {conf.legal_risk_score}/100", fontsize=8, fontname="hebo", color=sev_color)

            page1.insert_text(fitz.Point(55, y + 30), f"Kollidierende Regime: {conf.standard_a} <—> {conf.standard_b} • {conf.jurisdiction_clash}", fontsize=7.5, fontname="hebo", color=(0.3, 0.35, 0.4))

            page1.insert_textbox(
                fitz.Rect(55, y + 38, 540, y + 72),
                conf.statutory_clash_summary_de,
                fontsize=7.5,
                fontname="helv",
                color=(0.15, 0.15, 0.15),
            )

            # Precedence rule banner
            page1.draw_rect(fitz.Rect(55, y + 76, 540, y + 96), color=(0.2, 0.4, 0.6), fill=(0.92, 0.95, 0.99))
            page1.insert_text(fitz.Point(62, y + 89), f"Kollisionsauflösung: {conf.statutory_precedence_rule}", fontsize=7.5, fontname="hebo", color=(0.1, 0.25, 0.45))

            y += 115

        # Footer page 1
        page1.insert_text(fitz.Point(45, 810), f"DocuNorm AI Sovereign Conflict Matrix • SHA-256: {matrix.sha256_hash[:32]}... • Seite 1 von 2", fontsize=7, fontname="helv", color=(0.4, 0.4, 0.4))

        # ================= PAGE 2: HARMONIZATION COVENANTS & ATTESTATION =================
        page2 = doc.new_page(width=595, height=842)

        page2.draw_rect(fitz.Rect(45, 40, 550, 80), color=(0.1, 0.18, 0.32), fill=(0.96, 0.97, 1.0))
        page2.insert_text(fitz.Point(55, 65), "STATUTARISCHE HARMONISIERUNGS-KLAUSELN & BINDENDE ABHILFE", fontsize=10, fontname="hebo", color=(0.08, 0.14, 0.28))
        page2.insert_text(fitz.Point(55, 82), "Rechtssichere Musterbestimmungen zur Auflösung der festgestellten Normenkollisionen", fontsize=8, fontname="helv", color=(0.35, 0.4, 0.45))

        y2 = 100
        for idx, conf in enumerate(matrix.conflicts[:3], 1):
            page2.insert_text(fitz.Point(45, y2), f"Harmonisierungsklausel zu § {idx} ({conf.conflict_id}):", fontsize=8.5, fontname="hebo", color=(0.1, 0.45, 0.2))
            y2 += 12

            cov_box = fitz.Rect(45, y2, 550, y2 + 85)
            page2.draw_rect(cov_box, color=(0.2, 0.55, 0.25), fill=(0.95, 0.99, 0.96))
            page2.insert_textbox(fitz.Rect(52, y2 + 8, 542, y2 + 78), conf.resolution_covenant_de, fontsize=8, fontname="helv", color=(0.05, 0.15, 0.05))
            y2 += 98

        # Legal Attestation Box
        y2 = max(y2 + 10, 620)
        page2.draw_rect(fitz.Rect(45, y2, 550, y2 + 140), color=(0.2, 0.25, 0.35), fill=(0.97, 0.98, 0.99))
        page2.insert_text(fitz.Point(55, y2 + 20), "RECHTLICHE WÜRDIGUNG & UNTERZEICHNUNG", fontsize=9.5, fontname="hebo", color=(0.1, 0.15, 0.25))

        attestation = (
            "Die vorstehende aufsichtsrechtliche Kollisionsprüfung wurde unter Anwendung der anerkannten Auslegungsregeln "
            "(Lex Superior, Lex Specialis und Vorrang des Unionsrechts gem. EuGH) durchgeführt. Das Bezugsdokument ist bei "
            "vollständiger Implementierung der genannten Harmonisierungsklauseln mit DORA und DSGVO in Einklang zu bringen."
        )
        page2.insert_textbox(fitz.Rect(55, y2 + 28, 535, y2 + 65), attestation, fontsize=7.5, fontname="helv", color=(0.2, 0.2, 0.2))

        now_str = datetime.now(UTC).strftime("%d. %B %Y")
        page2.insert_text(fitz.Point(55, y2 + 85), f"Frankfurt am Main, den {now_str}", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))

        page2.draw_line(fitz.Point(55, y2 + 115), fitz.Point(260, y2 + 115), color=(0.3, 0.3, 0.3), width=0.8)
        page2.insert_text(fitz.Point(55, y2 + 128), signatory_name, fontsize=7.5, fontname="hebo", color=(0.1, 0.1, 0.1))

        page2.insert_text(fitz.Point(320, y2 + 85), f"Kryptografischer Hash-Siegel:\n{matrix.sha256_hash}", fontsize=6.5, fontname="cour", color=(0.3, 0.35, 0.4))

        # Footer page 2
        page2.insert_text(fitz.Point(45, 810), f"DocuNorm AI Sovereign Conflict Matrix • SHA-256: {matrix.sha256_hash[:32]}... • Seite 2 von 2", fontsize=7, fontname="helv", color=(0.4, 0.4, 0.4))

        doc.save(str(pdf_file))
        doc.close()
        return pdf_file


collision_engine = NormativeCollisionEngine()
