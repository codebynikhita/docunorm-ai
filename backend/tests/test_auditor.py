import pytest
from app.services.auditor import build_audit_prompt, parse_citations_from_response


def test_build_audit_prompt_formats_chunks_correctly():
    """
    Verifies that the audit prompt strictly formats each source chunk with its page number
    and enforces European regulatory grounding instructions.
    """
    chunks = [
        {"id": "c1", "page_number": 1, "content": "Master supply agreement between Siemens and Supplier."},
        {"id": "c2", "page_number": 2, "content": "Penalty fee is 0.5% per week of delay."},
    ]
    prompt = build_audit_prompt(query="What is the late penalty?", retrieved_chunks=chunks)

    assert "What is the late penalty?" in prompt
    assert "[SOURCE_1] (Page 1):" in prompt
    assert "[SOURCE_2] (Page 2):" in prompt
    assert "Penalty fee is 0.5% per week of delay." in prompt
    assert "strictly ground" in prompt.lower() or "audit" in prompt.lower()


def test_parse_citations_from_response_extracts_correct_metadata():
    """
    Verifies that source tags [SOURCE_X] in the AI answer are extracted
    and linked to their exact page numbers and bounding boxes.
    """
    ai_response = (
        "According to [SOURCE_2], the late delivery penalty is 0.5% per week, "
        "as defined in the agreement signed under [SOURCE_1]."
    )
    chunk_map = {
        "SOURCE_1": {
            "chunk_id": "c1",
            "page_number": 1,
            "bounding_box": [50.0, 72.0, 450.0, 110.0],
            "content": "Master supply agreement text...",
        },
        "SOURCE_2": {
            "chunk_id": "c2",
            "page_number": 2,
            "bounding_box": [50.0, 120.0, 400.0, 150.0],
            "content": "Penalty fee text...",
        },
    }

    citations = parse_citations_from_response(ai_response, chunk_map)

    assert len(citations) == 2
    # Verify SOURCE_2 was cited
    c2 = next(c for c in citations if c["source_tag"] == "[SOURCE_2]")
    assert c2["page_number"] == 2
    assert c2["bounding_box"] == [50.0, 120.0, 400.0, 150.0]

    # Verify SOURCE_1 was cited
    c1 = next(c for c in citations if c["source_tag"] == "[SOURCE_1]")
    assert c1["page_number"] == 1
    assert c1["bounding_box"] == [50.0, 72.0, 450.0, 110.0]


def test_parse_citations_handles_no_citations():
    """If AI response contains no [SOURCE_X] tags, returns empty list."""
    ai_response = "I could not find relevant information in the provided document."
    citations = parse_citations_from_response(ai_response, {})
    assert citations == []
