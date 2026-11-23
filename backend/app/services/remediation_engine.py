import difflib
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pymupdf as fitz

from app.schemas.remediation import (
    AmendmentProposal,
    ClauseRiskItem,
    DiffToken,
    DocumentRiskHeatmap,
    LegalAmendmentAgreementResponse,
)


def compute_word_diff(original: str, replacement: str) -> list[DiffToken]:
    """
    Computes a clean, high-precision word-level redline diff between original clause and compliant replacement.
    Splits on whitespace to prevent arbitrary whitespace alignments from shredding words into interleaved fragments.
    """
    orig_words = original.strip().split()
    repl_words = replacement.strip().split()

    matcher = difflib.SequenceMatcher(None, orig_words, repl_words)
    tokens: list[DiffToken] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            text = " ".join(orig_words[i1:i2])
            if text:
                tokens.append(DiffToken(type="equal", text=text + " "))
        elif tag == "delete":
            text = " ".join(orig_words[i1:i2])
            if text:
                tokens.append(DiffToken(type="delete", text=text + " "))
        elif tag == "insert":
            text = " ".join(repl_words[j1:j2])
            if text:
                tokens.append(DiffToken(type="insert", text=text + " "))
        elif tag == "replace":
            del_text = " ".join(orig_words[i1:i2])
            ins_text = " ".join(repl_words[j1:j2])
            if del_text:
                tokens.append(DiffToken(type="delete", text=del_text + " "))
            if ins_text:
                tokens.append(DiffToken(type="insert", text=ins_text + " "))

    return tokens


class RemediationEngine:
    """
    Forensic Contract Anomaly Detection, Clause Risk Heatmap Generator,
    and BGB / DORA Legal Amendment Synthesizer.
    """

    @classmethod
    def analyze_document_risk(
        cls,
        document_id: UUID,
        filename: str,
        chunks: list[dict],
    ) -> DocumentRiskHeatmap:
        risk_items: list[ClauseRiskItem] = []
        page_risks: dict[int, list[float]] = {}

        for c in chunks:
            content = c.get("content", "")
            lower = content.lower()
            page_num = c.get("page_number", 1)
            bbox = c.get("bounding_box") or [0.0, 0.0, 0.0, 0.0]
            chunk_id = str(c.get("id", f"c_{page_num}"))

            # 1. Audit Rights Exclusion / Obstruction (CRITICAL)
            if any(k in lower for k in ["vor-ort-prüfung", "zutritt", "audit"]) and any(
                k in lower for k in ["ausgeschlossen", "nicht gestattet", "untersagt", "verwehrt"]
            ):
                item = ClauseRiskItem(
                    chunk_id=chunk_id,
                    page_number=page_num,
                    bounding_box=bbox,
                    severity="CRITICAL",
                    risk_score=95.0,
                    title="Aufsichtsrechtliches Zutrittsverbot",
                    category="Aufsichtsrechte (KWG § 25b)",
                    deficiency_summary_de="Vor-Ort-Prüfungen oder Rechenzentrumszutritt sind unzulässig ausgeschlossen (Verstoß gegen KWG § 25b & DORA Art. 30 Abs. 3 lit. e).",
                    deficiency_summary_en="Physical on-site datacenter inspections are unlawfully excluded (violation of KWG § 25b & DORA Art. 30(3)(e)).",
                    statutory_ref="KWG § 25b Abs. 3 · DORA Art. 30(3)(e)",
                    snippet=content[:250],
                )
                risk_items.append(item)
                page_risks.setdefault(page_num, []).append(95.0)

            # 2. Obstructionist Audit Fees / Deposit (CRITICAL)
            elif any(k in lower for k in ["kaution", "prüfgebühr", "aufwandspauschale", "sicherheitsleistung"]) and any(
                k in lower for k in ["25.000", "50.000", "kostenerstattung", "pauschale"]
            ):
                item = ClauseRiskItem(
                    chunk_id=chunk_id,
                    page_number=page_num,
                    bounding_box=bbox,
                    severity="CRITICAL",
                    risk_score=92.0,
                    title="Rechtswidrige Prüfgebühr / Kautionsbarriere",
                    category="Aufsichtsrechte (KWG § 25b)",
                    deficiency_summary_de="Unzulässige Gebührenforderung oder Kaution für aufsichtsrechtliche Inspektionen (§ 307 BGB unwirksame Klausel).",
                    deficiency_summary_en="Unlawful fee or deposit barrier imposed on statutory regulatory inspections (invalid under § 307 BGB).",
                    statutory_ref="BGB § 307 · BaFin BAIT 8.1",
                    snippet=content[:250],
                )
                risk_items.append(item)
                page_risks.setdefault(page_num, []).append(92.0)

            # 3. Subcontractor Liability Exclusion / Uncontrolled Sub-Outsourcing (CRITICAL)
            elif any(k in lower for k in ["subunternehmer", "nachunternehmer", "unterauftrag"]) and (
                any(k in lower for k in ["ohne vorherige zustimmung", "ohne zustimmung", "keine haftung", "haftungsausschluss"])
                or ("haftung" in lower and "ausgeschlossen" in lower)
            ):
                item = ClauseRiskItem(
                    chunk_id=chunk_id,
                    page_number=page_num,
                    bounding_box=bbox,
                    severity="CRITICAL",
                    risk_score=90.0,
                    title="Unzulässiger Haftungsausschluss für Nachunternehmer",
                    category="Sub-Outsourcing (DORA Art. 30 Abs. 3)",
                    deficiency_summary_de="Haftung für Erfüllungsgehilfen und Subdienstleister wird unzulässig abbedungen (Verstoß gegen BGB § 278).",
                    deficiency_summary_en="Liability for sub-contractors and vicarious agents is unlawfully excluded (violates BGB § 278).",
                    statutory_ref="BGB § 278 · DORA Art. 30(3)",
                    snippet=content[:250],
                )
                risk_items.append(item)
                page_risks.setdefault(page_num, []).append(90.0)

            # 4. Exit Transition Deficit (HIGH)
            elif ("kündigung" in lower or "ausstieg" in lower) and any(
                k in lower for k in ["14 tagen", "30 tagen", "ohne datenmigration", "keine unterstützung"]
            ):
                item = ClauseRiskItem(
                    chunk_id=chunk_id,
                    page_number=page_num,
                    bounding_box=bbox,
                    severity="HIGH",
                    risk_score=78.0,
                    title="Unzureichende Kündigungs- oder Migrationsfrist",
                    category="Ausstiegsstrategie (DORA Art. 30 Abs. 2)",
                    deficiency_summary_de="Ausstiegsfrist unterschreitet die aufsichtsrechtliche Mindestdauer von 60 Kalendertagen.",
                    deficiency_summary_en="Exit transition period falls below the statutory 60-day threshold.",
                    statutory_ref="DORA Art. 30(2)(e)",
                    snippet=content[:250],
                )
                risk_items.append(item)
                page_risks.setdefault(page_num, []).append(78.0)

            # 5. General Liability Exclusion for Gross Negligence (HIGH)
            elif ("grober fahrlässigkeit" in lower or "vorsatz" in lower) and ("ausgeschlossen" in lower or "beschränkt auf 10" in lower):
                item = ClauseRiskItem(
                    chunk_id=chunk_id,
                    page_number=page_num,
                    bounding_box=bbox,
                    severity="HIGH",
                    risk_score=85.0,
                    title="Klausel-Unwirksamkeit: Haftungsbeschränkung bei grober Fahrlässigkeit",
                    category="AGB-Recht (BGB § 309 Nr. 7)",
                    deficiency_summary_de="Haftungsbeschränkung erstreckt sich auf grobe Fahrlässigkeit oder Vorsatz (§ 309 Nr. 7 BGB Klauselverbot).",
                    deficiency_summary_en="Liability cap attempts to exclude gross negligence or willful intent (violates BGB § 309 No. 7).",
                    statutory_ref="BGB § 309 Nr. 7 lit. b",
                    snippet=content[:250],
                )
                risk_items.append(item)
                page_risks.setdefault(page_num, []).append(85.0)

            # Clean / Low risk clauses
            else:
                page_risks.setdefault(page_num, []).append(10.0)

        # Aggregate Page Scores
        all_pages = sorted(list({c.get("page_number", 1) for c in chunks})) or [1]
        page_scores: dict[int, float] = {}
        for p in all_pages:
            scores = page_risks.get(p, [10.0])
            page_scores[p] = round(max(scores), 1)

        critical_count = sum(1 for r in risk_items if r.severity == "CRITICAL")
        high_count = sum(1 for r in risk_items if r.severity == "HIGH")
        medium_count = sum(1 for r in risk_items if r.severity == "MEDIUM")

        if critical_count > 0:
            overall_score = min(98.0, 75.0 + critical_count * 8.0)
            rating = "CCC" if overall_score > 85 else "B"
        elif high_count > 0:
            overall_score = 65.0 + high_count * 5.0
            rating = "BB"
        elif medium_count > 0:
            overall_score = 45.0
            rating = "BBB"
        else:
            overall_score = 12.0
            rating = "AAA"

        return DocumentRiskHeatmap(
            document_id=document_id,
            filename=filename,
            overall_risk_score=round(overall_score, 1),
            risk_rating=rating,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            page_scores=page_scores,
            risk_items=risk_items,
        )

    @classmethod
    def synthesize_bespoke_amendment(
        cls,
        rule_id: str,
        original_clause: str,
        target_framework: str = "DORA",
        custom_parameters: dict | None = None,
    ) -> AmendmentProposal:
        """
        Dynamically synthesizes bespoke German BGB and European regulatory compliant
        clauses (Musterklauseln) parameterized by framework, notice windows, and penalty rates.
        """
        params = custom_parameters or {}
        lower = (original_clause or "").lower()

        # 1. Audit Rights (KWG § 25b / DORA Art. 30(3)(e))
        if any(k in lower for k in ["vor-ort", "zutritt", "prüfrechte", "audit", "inspection", "bafin", "kaution", "prüfgebühr"]):
            audit_notice = params.get("audit_notice", "angemessener Vorankündigung oder bei begründetem Verdacht anlassbezogen jederzeit unverzüglich")
            title_de = "Musterklausel für uneingeschränkte Prüf- & Kontrollrechte gem. KWG § 25b & DORA Art. 30"
            title_en = "Standard Compliant Clause for Supervisory Audit & Inspection Rights"

            replacement_de = (
                f"Der Auftragnehmer gewährt dem Auftraggeber, seinen bevollmächtigten Prüfern sowie den "
                f"zuständigen Aufsichtsbehörden (insbesondere BaFin, Deutsche Bundesbank und EZB) uneingeschränkten "
                f"physischen und logischen Zugang zu allen Geschäftsräumen, Rechenzentren und Systemen. "
                f"Prüfungen können nach {audit_notice} durchgeführt werden. "
                f"Es werden weder Prüfungsgebühren noch Sicherheitskautionen erhoben."
            )
            replacement_en = (
                "The contractor grants the client, its authorized auditors, and competent supervisory authorities "
                "(in particular BaFin, Deutsche Bundesbank, and ECB) unrestricted physical and logical access to all "
                "business premises, datacenters, and operational systems. Inspections may be conducted with reasonable notice "
                "or immediately at any time upon cause. Neither audit fees nor security deposits shall be levied."
            )
            just_de = (
                "Ersetzt die unzulässige Zutrittsverweigerung durch eine rechtssichere Klausel gemäß BaFin BAIT Ziffer 8.1 "
                "und DORA Art. 30 Abs. 3 lit. e. Beseitigt das Risiko aufsichtsrechtlicher Zwangsgelder."
            )
            just_en = (
                "Replaces the unlawful restriction of inspection rights with an authoritative clause complying with "
                "BaFin BAIT section 8.1 and DORA Art. 30(3)(e)."
            )
            bgb_basis = "BGB § 307 (Inhaltskontrolle von AGB)"
            dora_basis = "DORA Art. 30 Abs. 3 lit. e · KWG § 25b"

        # 2. Subcontractor Liability & Veto Rights (BGB § 278 / DORA Art. 30(3))
        elif any(k in lower for k in ["sub", "unterauftrag", "nachunternehmer", "subcontract"]):
            veto_days = params.get("subcontractor_veto_days", 30)
            title_de = f"Musterklausel für Unterauftragsvergaben & Durchgriffshaftung ({veto_days} Tage Veto gem. BGB § 278)"
            title_en = "Standard Clause for Sub-Contracting Governance & Vicarious Liability"

            replacement_de = (
                f"Die Hinzuziehung wesentlicher Unterauftragnehmer bedarf der vorherigen schriftlichen Zustimmung des Auftraggebers. "
                f"Der Auftraggeber verfügt über ein Widerspruchsrecht mit einer Frist von mindestens {veto_days} Kalendertagen. "
                f"Der Auftragnehmer haftet für Pflichtverletzungen sämtlicher Unterauftragnehmer und Erfüllungsgehilfen in vollem "
                f"Umfang wie für eigenes Verschulden gem. § 278 BGB. Alle vertraglichen Sicherheits- und Prüfpflichten sind "
                f"vollumfänglich auf alle Nachunternehmer zu überwälzen."
            )
            replacement_en = (
                f"The engagement of material subcontractors requires the prior written approval of the client. "
                f"The client holds an objection right with a mandatory window of at least {veto_days} calendar days. "
                f"The contractor remains strictly liable for all acts and defaults of subcontractors as for its own fault pursuant "
                f"to § 278 BGB. All cybersecurity and supervisory audit duties shall flow through to all tiers of suppliers."
            )
            just_de = (
                f"Heilt den unwirksamen Haftungsausschluss gem. § 278 BGB und statuiert das zwingende {veto_days}-Tage-Veto-Recht nach DORA Art. 30 Abs. 3."
            )
            just_en = (
                "Remedies the unlawful liability exclusion and codifies the statutory 30-day objection window under DORA Art. 30(3)."
            )
            bgb_basis = "BGB § 278 (Haftung für Erfüllungsgehilfen)"
            dora_basis = "DORA Art. 30 Abs. 3 · EBA Guidelines on Outsourcing"

        # 3. GDPR / Data Protection & Erasure (GDPR Art. 28)
        elif target_framework.upper() in ["GDPR", "DSGVO"] or any(k in lower for k in ["datenschutz", "dsgvo", "gdpr", "löschung", "erasure", "datensicherung", "speicherung"]):
            erasure_days = params.get("erasure_days", 14)
            title_de = f"Musterklausel für datenschutzkonforme Datenlöschung & Rückgabe ({erasure_days} Tage gem. Art. 28 DSGVO)"
            title_en = "Standard Clause for GDPR Compliant Data Erasure & Handover"

            replacement_de = (
                f"Der Auftragnehmer verpflichtet sich, sämtliche personenbezogenen Daten sowie Betriebsgeheimnisse des Auftraggebers "
                f"nach Vertragsbeendigung innerhalb von {erasure_days} Kalendertagen unwiederbringlich nach DIN 66399 Schutzklasse 3 "
                f"zu löschen oder vollständig an den Auftraggeber herauszugeben. Die Löschung ist durch ein qualifiziertes Vernichtungsprotokoll nachzuweisen."
            )
            replacement_en = (
                f"The contractor undertakes to irretrievably erase all personal data and confidential assets of the client "
                f"in accordance with DIN 66399 security level 3 or completely return them to the client within {erasure_days} calendar days upon termination. "
                f"Compliance must be evidenced by an official erasure certificate."
            )
            just_de = (
                "Gewährleistet die unverzügliche Datenlöschung nach DSGVO Art. 28 Abs. 3 lit. g und BDSG § 22."
            )
            just_en = (
                "Ensures mandatory data destruction compliance pursuant to GDPR Art. 28(3)(g) and German BDSG."
            )
            bgb_basis = "BGB § 280, § 307 (Verletzung vertraglicher Nebenpflichten)"
            dora_basis = "DSGVO Art. 28 Abs. 3 lit. g · DIN 66399"

        # 4. Exit Strategy & Migration (DORA Art. 30(2)(e))
        else:
            exit_notice_days = params.get("exit_notice_days", 60)
            migration_days = params.get("migration_days", 90)
            penalty_pct = params.get("penalty_daily_pct", 0.2)

            title_de = f"Musterklausel für Kündigung, Übergang ({exit_notice_days}d/{migration_days}d) gem. DORA Art. 30 Abs. 2"
            title_en = "Standard Clause for Exit Strategy & Data Migration Support"

            replacement_de = (
                f"Jede Vertragspartei kann diesen Vertrag mit einer ordentlichen Frist von mindestens {exit_notice_days} Tagen "
                f"zum Quartalsende kündigen. Im Kündigungsfall verpflichtet sich der Auftragnehmer zu einer aktiven "
                f"Migrationsunterstützung für mindestens {migration_days} Tage, um die unterbrechungsfreie Übergabe aller Datenbestände "
                f"in offenen, marktüblichen Standardformaten auf den Auftraggeber oder einen Nachfolgedienstleister sicherzustellen. "
                f"Verzögerungen werden mit einer Vertragsstrafe von {penalty_pct} % pro Werktag (max. 5 % der Jahresvergütung) sanktioniert."
            )
            replacement_en = (
                f"Either party may terminate this agreement with ordinary notice of at least {exit_notice_days} days to the end of a calendar quarter. "
                f"In case of termination, the contractor commits to comprehensive migration cooperation for at least {migration_days} days "
                f"to guarantee seamless transfer of all data assets in open, standard formats to the client or a successor vendor. "
                f"Delay penalties accrue at {penalty_pct}% per business day (capped at 5% of annual compensation)."
            )
            just_de = (
                f"Sichert die rechtskonforme Ausstiegsfrist von mindestens {exit_notice_days} Tagen und die {migration_days}-tägige Migrationsphase nach DORA Art. 30 Abs. 2 lit. e."
            )
            just_en = (
                f"Secures the mandatory {exit_notice_days}-day notice and {migration_days}-day migration assistance guarantees pursuant to DORA Art. 30(2)(e)."
            )
            bgb_basis = "BGB § 339, § 343 (Vertragsstrafenrecht)"
            dora_basis = "DORA Art. 30 Abs. 2 lit. e · BaFin VAIT/BAIT"

        is_english = any(w in lower for w in ["the ", "shall", "contractor", "audit", "liable", "services", "clause", "prohibited", "client", "inspection"]) and not any(w in lower for w in ["der ", "die ", "das ", "und ", "auftraggeber", "auftragnehmer", "gemäß", "klausel", "prüfung"])
        diff_tokens = compute_word_diff(original_clause, replacement_en if is_english else replacement_de)

        return AmendmentProposal(
            rule_id=rule_id,
            title_de=title_de,
            title_en=title_en,
            original_text=original_clause,
            compliant_replacement_de=replacement_de,
            compliant_replacement_en=replacement_en,
            legal_justification_de=just_de,
            legal_justification_en=just_en,
            bgb_statutory_basis=bgb_basis,
            dora_statutory_basis=dora_basis,
            diff_tokens=diff_tokens,
        )

    @classmethod
    def generate_amendment_proposal(
        cls,
        rule_id: str,
        original_clause: str,
    ) -> AmendmentProposal:
        """
        Generates standard German BGB and DORA compliant replacement clauses (Musterklauseln)
        along with precise word-level redline diffs.
        """
        return cls.synthesize_bespoke_amendment(
            rule_id=rule_id,
            original_clause=original_clause,
        )

    @classmethod
    def synthesize_agreement(
        cls,
        document_id: UUID,
        document_filename: str,
        chunks: list[dict],
        target_framework: str = "DORA",
        custom_parameters: dict | None = None,
    ) -> LegalAmendmentAgreementResponse:
        """
        Analyzes document risk heatmap and generates an aggregated legal amendment agreement
        (Nachtragsvereinbarung nach § 311 Abs. 1 BGB) with a cryptographic SHA-256 seal.
        """
        heatmap = cls.analyze_document_risk(document_id, document_filename, chunks)
        proposals: list[AmendmentProposal] = []

        for item in heatmap.risk_items:
            prop = cls.synthesize_bespoke_amendment(
                rule_id=item.statutory_ref,
                original_clause=item.snippet,
                target_framework=target_framework,
                custom_parameters=custom_parameters,
            )
            proposals.append(prop)

        if not proposals:
            prop = cls.synthesize_bespoke_amendment(
                rule_id="DORA-EXIT-01",
                original_clause="Allgemeine Vertragsklausel ohne explizite Ausstiegsregelung",
                target_framework=target_framework,
                custom_parameters=custom_parameters,
            )
            proposals.append(prop)

        combined_text = "".join(p.compliant_replacement_de for p in proposals)
        sha256_seal = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()

        return LegalAmendmentAgreementResponse(
            document_id=document_id,
            document_filename=document_filename,
            statutory_framework=target_framework,
            total_amendments=len(proposals),
            amendments=proposals,
            signatory_authority="DocuNorm AI Sovereign Legal Remediation Engine",
            sha256_seal=sha256_seal,
            status="SYNTHESIZED",
        )

    @classmethod
    def generate_amendment_contract_pdf(
        cls,
        document_filename: str,
        proposals: list[AmendmentProposal],
        output_dir: Path | str = "/tmp/docunorm_exports",
    ) -> Path:
        """
        Generates a binding German legal Addendum / Contract Amendment PDF
        (Nachtragsvereinbarung gem. § 311 Abs. 1 BGB) with official legal layout.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        pdf_file = output_path / f"{document_filename.replace('.pdf', '')}_NACHTRAGSVEREINBARUNG_BGB.pdf"

        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        y = 50

        # Title Header
        page.draw_rect(fitz.Rect(45, 40, 550, 95), color=(0.1, 0.2, 0.35), fill=(0.95, 0.97, 1.0))
        page.insert_text(fitz.Point(55, 60), "NACHTRAGSVEREINBARUNG ZUM IKT-DIENSTLEISTUNGSVERTRAG", fontsize=11, fontname="hebo", color=(0.08, 0.12, 0.2))
        page.insert_text(fitz.Point(55, 75), "Rechtsverbindliche Anpassung gem. § 311 Abs. 1 BGB zur Erfüllung von EU-DORA", fontsize=9, fontname="hebo", color=(0.15, 0.25, 0.4))
        page.insert_text(fitz.Point(55, 88), f"Bezugsdokument: {document_filename} • DIN EN ISO 9001 / BaFin Konform", fontsize=7.5, fontname="helv", color=(0.4, 0.45, 0.5))

        y = 120

        # Preamble
        preamble = (
            "Zwischen den Vertragsparteien wird im Hinblick auf die aufsichtsrechtlichen Anforderungen der "
            "Verordnung (EU) 2022/2554 (DORA) sowie KWG § 25b die folgende rechtliche Nachtragsvereinbarung geschlossen:"
        )
        page.insert_textbox(fitz.Rect(45, y, 550, y + 35), preamble, fontsize=8.5, fontname="helv", color=(0.1, 0.15, 0.2))
        y += 45

        for idx, prop in enumerate(proposals, 1):
            if y > 700:
                page = doc.new_page(width=595, height=842)
                y = 50

            page.draw_line(fitz.Point(45, y), fitz.Point(550, y), color=(0.8, 0.85, 0.9), width=1)
            y += 12

            # Section Title
            page.insert_text(fitz.Point(45, y), f"§ {idx} {prop.title_de}", fontsize=9.5, fontname="hebo", color=(0.85, 0.3, 0.0))
            y += 14

            page.insert_text(fitz.Point(45, y), f"Rechtsgrundlage: {prop.bgb_statutory_basis} • {prop.dora_statutory_basis}", fontsize=7.5, fontname="helv", color=(0.4, 0.45, 0.5))
            y += 12

            # Compliant text box
            box_rect = fitz.Rect(45, y, 550, y + 80)
            page.draw_rect(box_rect, color=(0.2, 0.6, 0.3), fill=(0.95, 0.99, 0.96))
            page.insert_textbox(fitz.Rect(52, y + 6, 542, y + 74), prop.compliant_replacement_de, fontsize=8.5, fontname="hebo", color=(0.05, 0.1, 0.05))
            y += 92

        # Signatures section
        if y > 680:
            page = doc.new_page(width=595, height=842)
            y = 80

        y = max(y + 20, 710)
        page.draw_line(fitz.Point(45, y), fitz.Point(550, y), color=(0.7, 0.75, 0.8), width=1)
        y += 15

        now_str = datetime.now(UTC).strftime("%d. %B %Y")
        page.insert_text(fitz.Point(45, y), f"Ort, Datum: Frankfurt am Main, den {now_str}", fontsize=8, fontname="helv", color=(0.3, 0.35, 0.4))
        y += 28

        page.draw_line(fitz.Point(45, y), fitz.Point(240, y), color=(0.4, 0.4, 0.4), width=0.8)
        page.draw_line(fitz.Point(355, y), fitz.Point(550, y), color=(0.4, 0.4, 0.4), width=0.8)
        y += 12
        page.insert_text(fitz.Point(45, y), "Unterschrift Auftraggeber (Siemens AG)", fontsize=8, fontname="hebo", color=(0.2, 0.25, 0.3))
        page.insert_text(fitz.Point(355, y), "Unterschrift Auftragnehmer (Dienstleister)", fontsize=8, fontname="hebo", color=(0.2, 0.25, 0.3))

        # Cryptographic SHA-256 Seal Footer
        combined_text = "".join(p.compliant_replacement_de for p in proposals)
        sha_seal = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()
        page.insert_text(fitz.Point(45, 820), f"Digitaler Integritäts-Hash (§ 311 BGB Nachtrag • SHA-256): {sha_seal}", fontsize=6.5, fontname="helv", color=(0.4, 0.45, 0.5))

        doc.save(str(pdf_file))
        doc.close()
        return pdf_file
