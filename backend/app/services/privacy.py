import re
from dataclasses import dataclass, field


@dataclass
class PIIEntity:
    """
    Represents an isolated personal data match detected in the document.
    """

    entity_type: str
    original_value: str
    placeholder: str


@dataclass
class AnonymizationResult:
    """
    The output of the privacy firewall: clean sanitized text and audit entities.
    """

    sanitized_text: str
    entities: list[PIIEntity] = field(default_factory=list)

    @property
    def has_pii(self) -> bool:
        return len(self.entities) > 0


class PrivacyFirewallService:
    """
    Local European PII Anonymization Engine for GDPR Compliance.
    Scans and neutralizes German IBANs, Tax IDs, Emails, and Phone Numbers.
    """

    # German and European PII Regex Patterns
    PATTERNS = {
        "IBAN": re.compile(r"\bDE[0-9]{20}\b", re.IGNORECASE),
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "PHONE": re.compile(r"\+49[\s0-9()-]{7,20}\b"),
        "STEUER_ID": re.compile(r"\b[0-9]{11}\b"),
    }

    def anonymize_text(self, text: str) -> AnonymizationResult:
        sanitized = text
        detected_entities: list[PIIEntity] = []
        counters: dict[str, int] = {}

        # Scan for each pattern type
        for entity_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                original_val = match.group().strip()

                # Increment counter for this entity type (e.g., [MASKED_IBAN_1])
                counters[entity_type] = counters.get(entity_type, 0) + 1
                placeholder = f"[MASKED_{entity_type}_{counters[entity_type]}]"

                detected_entities.append(
                    PIIEntity(
                        entity_type=entity_type,
                        original_value=original_val,
                        placeholder=placeholder,
                    )
                )
                # Replace sensitive text with GDPR-safe placeholder
                sanitized = sanitized.replace(original_val, placeholder)

        return AnonymizationResult(
            sanitized_text=sanitized,
            entities=detected_entities,
        )


# Global singleton instance for easy import
privacy_firewall = PrivacyFirewallService()
