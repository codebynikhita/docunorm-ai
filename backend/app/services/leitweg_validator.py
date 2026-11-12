import re

from app.schemas.zugferd_invoice import LeitwegValidationResult


class LeitwegValidatorService:
    """
    Official German Federal Leitweg-ID Format & ISO 7064 MOD-97-10 Check-Digit Validator.
    Conforms to § 4 E-Rech-VO (Verordnung über die elektronische Rechnungsstellung im öffentlichen Auftragswesen des Bundes)
    and the KoSIT Specification XRechnung 3.0.
    """

    # Format: Grobadressierung (2-12 digits) [- Feinadressierung (1-30 alphanum)] - Prüfziffer (2 digits)
    LEITWEG_REGEX = re.compile(r"^([0-9]{2,12})(?:-([A-Z0-9]{1,30}))?-([0-9]{2})$")

    FEDERAL_JURISDICTION_REGISTRY: dict[str, tuple[str, str, str]] = {
        "991": (
            "Bundesbehörde (ZRE)",
            "Bund — Unmittelbare Bundesverwaltung",
            "Zentrale Rechnungseingangsplattform des Bundes (ZRE)",
        ),
        "992": (
            "Bundesland / Mittelbare Verwaltung (OZG-RE)",
            "Bund / Länder — OZG-RE Verbund",
            "Onlinezugangsgesetz-konforme Rechnungseingangsplattform (OZG-RE)",
        ),
        "993": (
            "Bundesministerium / Verfassungsorgan",
            "Bund — Verfassungsorgane & Sonderbehörden",
            "ZRE / KoSIT Bundeshub",
        ),
        "01": ("Land / Kommune", "Schleswig-Holstein", "OZG-RE / Zentrales Rechnungsportal SH"),
        "02": ("Land / Kommune", "Freie und Hansestadt Hamburg", "OZG-RE / eRechnung Hamburg"),
        "03": ("Land / Kommune", "Niedersachsen", "Niedersächsisches Rechnungsportal"),
        "04": ("Land / Kommune", "Freie Hansestadt Bremen", "Zentrale E-Rechnungsannahme Bremen (eRechnung Bremen)"),
        "05": ("Land / Kommune", "Nordrhein-Westfalen", "Vergabe.NRW / E-Rechnungsportal NRW"),
        "06": ("Land / Kommune", "Hessen", "eRechnung Hessen (ZRE-Hessen)"),
        "07": ("Land / Kommune", "Rheinland-Pfalz", "Zentraler E-Rechnungseingang RLP (ZRE-RLP)"),
        "08": ("Land / Kommune", "Baden-Württemberg", "Zentrales Servicekonto Baden-Württemberg"),
        "09": ("Land / Kommune", "Freistaat Bayern", "BayernPortal / Zentrale Rechnungsstellung BY"),
        "10": ("Land / Kommune", "Saarland", "OZG-RE Saarland"),
        "11": ("Land / Kommune", "Land Berlin", "Zentrale E-Rechnungsplattform Berlin"),
        "12": ("Land / Kommune", "Brandenburg", "OZG-RE Brandenburg"),
        "13": ("Land / Kommune", "Mecklenburg-Vorpommern", "OZG-RE Mecklenburg-Vorpommern"),
        "14": ("Land / Kommune", "Freistaat Sachsen", "E-Rechnungsportal Sachsen (OZG-RE)"),
        "15": ("Land / Kommune", "Sachsen-Anhalt", "eRechnung Sachsen-Anhalt"),
        "16": ("Land / Kommune", "Freistaat Thüringen", "OZG-RE Thüringen"),
    }

    @classmethod
    def _to_numeric_string(cls, text: str) -> str:
        """Converts alphanumeric characters (A=10 .. Z=35) per ISO 7064."""
        parts: list[str] = []
        for ch in text.upper():
            if ch.isdigit():
                parts.append(ch)
            elif "A" <= ch <= "Z":
                parts.append(str(ord(ch) - 55))
        return "".join(parts)

    @classmethod
    def compute_check_digit(cls, coarse_address: str, fine_address: str | None = None) -> str:
        """
        Calculates the official 2-digit ISO 7064 MOD-97-10 check digit for a Leitweg-ID.
        Formula: 98 - (int(numeric_base + '00') % 97), zero-padded to 2 digits.
        """
        base = coarse_address.strip() + (fine_address.strip() if fine_address else "")
        numeric_base = cls._to_numeric_string(base)
        if not numeric_base:
            return "00"
        val = int(numeric_base + "00")
        check = 98 - (val % 97)
        return f"{check:02d}"

    @classmethod
    def validate(cls, raw_id: str | None) -> LeitwegValidationResult:
        """
        Validates structure, check-digit integrity (MOD-97-10), and resolves the official
        German federal/state routing jurisdiction for a given Leitweg-ID.
        """
        if not raw_id or not raw_id.strip():
            return LeitwegValidationResult(
                raw_id="",
                is_valid=False,
                format_valid=False,
                checksum_valid=False,
                errors=["Keine Leitweg-ID (BT-10) vorhanden."],
            )

        cleaned = raw_id.strip().upper()
        errors: list[str] = []

        match = cls.LEITWEG_REGEX.match(cleaned)
        if not match:
            errors.append(
                f"Ungültiges Leitweg-ID-Format '{cleaned}'. Erwartet: Grobadressierung (2-12 Ziffern)-[Feinadressierung]-Prüfziffer (2 Ziffern)."
            )
            return LeitwegValidationResult(
                raw_id=cleaned,
                is_valid=False,
                format_valid=False,
                checksum_valid=False,
                errors=errors,
            )

        coarse = match.group(1)
        fine = match.group(2)
        provided_check = match.group(3)

        # Compute expected ISO 7064 MOD-97-10 check digit
        expected_check = cls.compute_check_digit(coarse, fine)
        checksum_valid = provided_check == expected_check

        if not checksum_valid:
            errors.append(
                f"Prüfziffernfehler nach ISO 7064 MOD-97-10: Übermittelt '{provided_check}', erwartet '{expected_check}'."
            )

        # Resolve administrative authority from Grobadressierung prefix
        entity_type = "Kommunale / Öffentliche Einrichtung"
        authority = "Nicht im Bundes-/Länderregister spezifiziert"
        portal = "Deutscher PEPPOL / ZRE / OZG-RE Zugangspunkt"

        prefix_3 = coarse[:3]
        prefix_2 = coarse[:2]

        if prefix_3 in cls.FEDERAL_JURISDICTION_REGISTRY:
            entity_type, authority, portal = cls.FEDERAL_JURISDICTION_REGISTRY[prefix_3]
        elif prefix_2 in cls.FEDERAL_JURISDICTION_REGISTRY:
            entity_type, authority, portal = cls.FEDERAL_JURISDICTION_REGISTRY[prefix_2]
        else:
            errors.append(
                f"Unbekannter Amtlicher Gemeindeschlüssel / Behördenpräfix '{prefix_2}' in Grobadressierung '{coarse}'."
            )

        is_valid = checksum_valid and len(errors) == 0

        return LeitwegValidationResult(
            raw_id=cleaned,
            is_valid=is_valid,
            format_valid=True,
            checksum_valid=checksum_valid,
            coarse_address=coarse,
            fine_address=fine,
            check_digit=provided_check,
            expected_check_digit=expected_check,
            federal_entity_type=entity_type,
            bundesland_or_authority=authority,
            submission_portal=portal,
            errors=errors,
        )


leitweg_validator = LeitwegValidatorService()
