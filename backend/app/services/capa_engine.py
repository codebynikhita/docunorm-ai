from datetime import UTC, datetime
from uuid import UUID

from app.schemas.capa import CapaMilestone, CapaSeverity, CapaStatus, SupplierCapaPlan


class CapaEngine:
    """
    Statutory Supplier Corrective Action Plan (CAPA) Engine under §§ 6, 7 LkSG.
    Synthesizes legally enforceable remediation milestones, deadlines, verification
    methods, and penalty clauses for supply chain compliance deficits.
    """

    @classmethod
    def generate_plan(
        cls,
        document_id: UUID,
        filename: str,
        chunks: list[dict],
    ) -> SupplierCapaPlan:
        full_text = " ".join(c.get("content", "") for c in chunks).lower()

        milestones: list[CapaMilestone] = []

        # 1. Child Labor / ILO 138/182 Audit
        has_child_labor_risk = "kinderarbeit" in full_text and any(k in full_text for k in ["ausnahme", "verzug", "nicht anwendbar", "vorbehalt"]) or "underage" in full_text
        if has_child_labor_risk or ("kinderarbeit" not in full_text and "ilo 138" not in full_text):
            milestones.append(
                CapaMilestone(
                    id="CAPA-01-CHILD-LABOR",
                    title_de="Sofortiges Verbot jeglicher Kinderarbeit & Altersverifikationssystem",
                    title_en="Immediate Child Labor Prohibition & Age Verification System",
                    category="MENSCHENRECHTE (HUMAN RIGHTS)",
                    severity=CapaSeverity.CRITICAL,
                    deadline_days=30,
                    statutory_basis="§ 7 Abs. 1 & § 2 Abs. 2 Nr. 1 LkSG · ILO 138/182",
                    deficiency_description="Fehlende oder lückenhafte vertragliche Verpflichtung zur Einhaltung des Mindestalters gem. ILO 138 (15 Jahre).",
                    required_action_de="Vollständige Implementierung eines behördlich geprüften Altersverifikationssystems in allen Produktionsstätten binnen 30 Tagen.",
                    required_action_en="Full implementation of verified biometric/ID age verification across all production facilities within 30 days.",
                    verification_method="Unangekündigtes Vor-Ort-Audit durch eine akkreditierte Prüforganisation (z.B. TÜV SÜD / SGS) mit Vorlage aller Geburtsurkunden.",
                    penalty_upon_default_eur=100000.0,
                    status=CapaStatus.OPEN,
                )
            )

        # 2. Environmental Conventions (Minamata Mercury / Basel Waste)
        has_env_deficit = any(k in full_text for k in ["quecksilber", "mercury", "minamata", "abfall", "hazardous waste", "basel"]) and any(k in full_text for k in ["ausschluss", "haftungsausschluss", "keine übernahme"])
        if has_env_deficit or ("minamata" not in full_text and "basler" not in full_text and "basel" not in full_text):
            milestones.append(
                CapaMilestone(
                    id="CAPA-02-ENV-TREATIES",
                    title_de="Umwelt-Compliance & Verbot grenzüberschreitender Sonderabfallexporte",
                    title_en="Environmental Treaties Compliance & Hazardous Waste Export Ban",
                    category="UMWELTSCHUTZ (ENVIRONMENTAL)",
                    severity=CapaSeverity.CRITICAL,
                    deadline_days=45,
                    statutory_basis="§ 7 Abs. 2 & § 2 Abs. 3 Nr. 1-3 LkSG · Minamata/Basler Übereinkommen",
                    deficiency_description="Unzureichende Dokumentation über die Entsorgung von Industrieabfällen und Quecksilberverbindungen.",
                    required_action_de="Vorlage lückenloser länderspezifischer Entsorgungs- und Recyclingzertifikate gem. Basler Übereinkommen für alle Prozessrückstände.",
                    required_action_en="Submission of complete disposal and recycling certificates compliant with the Basel Convention for all process residues.",
                    verification_method="Auditierung der Abfallentsorgungskette und Vorlage behördlich genehmigter Begleitscheine für Gefahrguttransporte.",
                    penalty_upon_default_eur=75000.0,
                    status=CapaStatus.OPEN,
                )
            )

        # 3. Minimum Wage / Fair Living Wage
        has_wage_risk = any(k in full_text for k in ["mindestlohn", "living wage", "milog", "vergütung"]) and any(k in full_text for k in ["unterschreitung", "abzug", "pauschal"])
        if has_wage_risk or ("milog" not in full_text and "mindestlohn" not in full_text and "angemessene vergütung" not in full_text):
            milestones.append(
                CapaMilestone(
                    id="CAPA-03-FAIR-WAGE",
                    title_de="Garantie des gesetzlichen Mindestlohns & Existenzsicherndes Einkommen",
                    title_en="Statutory Minimum Wage & Fair Living Wage Guarantee",
                    category="ARBEITSBEDINGUNGEN (WORKING CONDITIONS)",
                    severity=CapaSeverity.HIGH,
                    deadline_days=60,
                    statutory_basis="§ 7 Abs. 1 & § 2 Abs. 2 Nr. 8 LkSG · MiLoG",
                    deficiency_description="Keine ausdrückliche vertragliche Garantie zur Zahlung des gesetzlichen Mindestlohns oder existenzsichernder Entgelte.",
                    required_action_de="Anpassung der Entgelttabellen für alle Arbeiter und Vorlage von Gehaltsabrechnungsstichproben durch einen Wirtschaftsprüfer.",
                    required_action_en="Adjustment of wage tables across all manufacturing units and submission of payroll audits certified by certified accountants.",
                    verification_method="Prüfung der monatlichen Lohnabrechnungen und Nachweis der Einhaltung der nationalen gesetzlichen Mindestlohnnormen.",
                    penalty_upon_default_eur=50000.0,
                    status=CapaStatus.OPEN,
                )
            )

        # 4. Whistleblower / Grievance Mechanism (§ 8 LkSG)
        has_whistle_deficit = "beschwerde" in full_text and any(k in full_text for k in ["gebühr", "kostenpflichtig", "identitätsprüfung zwingend"])
        if has_whistle_deficit or ("whistleblower" not in full_text and "beschwerdeverfahren" not in full_text and "§ 8" not in full_text):
            milestones.append(
                CapaMilestone(
                    id="CAPA-04-WHISTLEBLOWER",
                    title_de="Einrichtung eines anonymen Hinweisgeber- und Beschwerdesystems",
                    title_en="Implementation of Anonymous Grievance & Whistleblower System",
                    category="GOVERNANCE & COMPLIANCE",
                    severity=CapaSeverity.HIGH,
                    deadline_days=60,
                    statutory_basis="§ 8 LkSG · BAFA-Handreichung Beschwerdeverfahren",
                    deficiency_description="Fehlendes oder nicht barrierefreies Beschwerdeverfahren für Beschäftigte und Betroffene in der Lieferkette.",
                    required_action_de="Einrichtung einer digitalen, mehrsprachigen und anonymen Whistleblower-Hotline mit garantierter Repressalienfreiheit gem. § 8 Abs. 4 LkSG.",
                    required_action_en="Setup of a digital, multilingual, anonymous whistleblower portal with guaranteed non-retaliation under § 8(4) LkSG.",
                    verification_method="Funktionstest des Portals, Veröffentlichung der Verfahrensordnung und Bereitstellung von Informationsmaterialien für Belegschaften.",
                    penalty_upon_default_eur=30000.0,
                    status=CapaStatus.OPEN,
                )
            )

        # 5. Cascading Sub-Supplier Due Diligence (§ 9 LkSG)
        if "mittelbare zulieferer" not in full_text and "tier-2" not in full_text and "sub-supplier" not in full_text:
            milestones.append(
                CapaMilestone(
                    id="CAPA-05-TIER-N-CASCADE",
                    title_de="Weitergabe von Sorgfaltspflichten an mittelbare Zulieferer (Tier-N)",
                    title_en="Pass-Through of Due Diligence to Indirect Tier-N Suppliers",
                    category="LIEFERKETTEN-MAPPING (SUPPLY CHAIN)",
                    severity=CapaSeverity.MEDIUM,
                    deadline_days=90,
                    statutory_basis="§ 9 LkSG & § 6 Abs. 4 LkSG (Vertragliche Zusicherungen)",
                    deficiency_description="Vertrag regelt keine Weitergabe der menschenrechtlichen und umweltbezogenen Pflichten an Unterzulieferer.",
                    required_action_de="Abschluss von Verhaltenskodex-Zusatzvereinbarungen (Supplier Code of Conduct) mit allen Hauptvorlieferanten des Lieferanten.",
                    required_action_en="Execution of Supplier Code of Conduct pass-through amendments with all primary sub-tier suppliers.",
                    verification_method="Vorlage der gegengezeichneten Lieferantenverträge der Stufe Tier-2 und Tier-3.",
                    penalty_upon_default_eur=25000.0,
                    status=CapaStatus.OPEN,
                )
            )

        crit_count = sum(1 for m in milestones if m.severity == CapaSeverity.CRITICAL)
        high_count = sum(1 for m in milestones if m.severity == CapaSeverity.HIGH)

        if crit_count > 0:
            posture = "CRITICAL_ACTION_REQUIRED"
            bafa_notif = True
            summary_de = f"Der Vertrag weist {crit_count} kritische LkSG-Defizite auf. Es wurde ein verbindlicher 30-Tage-Aktionsplan gem. § 7 LkSG erstellt. Bei Nichteinhaltung droht BAFA-Meldung und Kündigung."
            summary_en = f"Contract presents {crit_count} critical LkSG deficits. A binding 30-day corrective action plan under § 7 LkSG has been formulated. Non-compliance triggers BAFA notification and termination."
        elif high_count > 0:
            posture = "REMEDIATION_REQUIRED"
            bafa_notif = False
            summary_de = f"Es wurden {len(milestones)} Nachbesserungspunkte identifiziert. Die Umsetzung muss innerhalb von maximal 90 Tagen nachgewiesen werden."
            summary_en = f"{len(milestones)} remediation milestones identified. Implementation must be certified within a maximum of 90 days."
        else:
            posture = "ACCEPTABLE"
            bafa_notif = False
            summary_de = "Lieferantenvertrag erfüllt wesentliche LkSG-Mindeststandards. Präventive Überwachung empfohlen."
            summary_en = "Supplier contract satisfies core LkSG requirements. Preventive monitoring recommended."

        max_days = max((m.deadline_days for m in milestones), default=90)
        total_costs = sum(m.penalty_upon_default_eur for m in milestones) * 0.15  # estimated remediation cost baseline

        supplier_name = filename.replace(".pdf", "").replace("_", " ").title()

        return SupplierCapaPlan(
            plan_id=f"CAPA-{str(document_id)[:8].upper()}",
            document_id=document_id,
            filename=filename,
            supplier_name=supplier_name,
            overall_compliance_posture=posture,
            total_milestones=len(milestones),
            critical_milestones_count=crit_count,
            max_remediation_timeline_days=max_days,
            estimated_remediation_cost_eur=round(total_costs, 2),
            bafa_notification_required=bafa_notif,
            milestones=milestones,
            executive_summary_de=summary_de,
            executive_summary_en=summary_en,
            generated_at=datetime.now(UTC),
        )
