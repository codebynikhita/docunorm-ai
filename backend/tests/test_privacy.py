import pytest

from app.services.privacy import PrivacyFirewallService


@pytest.fixture
def privacy_service() -> PrivacyFirewallService:
    return PrivacyFirewallService()


def test_masks_german_iban(privacy_service: PrivacyFirewallService) -> None:
    """
    Verifies that standard German IBANs (DE followed by 20 digits) are sanitized.
    """
    raw_text = "Please send invoice payment to IBAN DE89370400440532013000 immediately."
    result = privacy_service.anonymize_text(raw_text)

    assert result.has_pii is True
    assert "DE89370400440532013000" not in result.sanitized_text
    assert "[MASKED_IBAN_1]" in result.sanitized_text
    assert len(result.entities) == 1
    assert result.entities[0].entity_type == "IBAN"


def test_masks_german_tax_id(privacy_service: PrivacyFirewallService) -> None:
    """
    Verifies that 11-digit German Steuer-IDs are detected and masked.
    """
    raw_text = "Tax identification number for employee: Steuer-ID 12345678901."
    result = privacy_service.anonymize_text(raw_text)

    assert result.has_pii is True
    assert "12345678901" not in result.sanitized_text
    assert "[MASKED_STEUER_ID_1]" in result.sanitized_text
    assert any(e.entity_type == "STEUER_ID" for e in result.entities)


def test_masks_emails_and_phones(privacy_service: PrivacyFirewallService) -> None:
    """
    Verifies that business emails and German phone numbers (+49...) are scrubbed.
    """
    raw_text = "Contact Dr. Mueller at t.mueller@siemens.de or call +49 89 636 00."
    result = privacy_service.anonymize_text(raw_text)

    assert result.has_pii is True
    assert "t.mueller@siemens.de" not in result.sanitized_text
    assert "[MASKED_EMAIL_1]" in result.sanitized_text
    assert "+49 89 636 00" not in result.sanitized_text
    assert "[MASKED_PHONE_1]" in result.sanitized_text


def test_clean_text_remains_untouched(privacy_service: PrivacyFirewallService) -> None:
    """
    Verifies that text without personal data is returned unaltered.
    """
    clean_text = (
        "The supplier agrees to deliver 500 units of industrial machinery by Q3."
    )
    result = privacy_service.anonymize_text(clean_text)

    assert result.has_pii is False
    assert result.sanitized_text == clean_text
    assert len(result.entities) == 0
