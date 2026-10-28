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


def test_build_audit_prompt_with_conversation_history():
    """
    Verifies that multi-turn history items are injected into the audit prompt
    for conversational continuity and follow-up query answering.
    """
    chunks = [
        {"id": "c1", "page_number": 2, "content": "Exit clauses mandate 60-day notice and 90-day migration support."},
    ]
    history = [
        {"role": "user", "text": "What is the exit clause?"},
        {"role": "auditor", "text": "• [SOURCE_1]: Notice period is 60 days."},
    ]
    prompt = build_audit_prompt(
        query="And what about the migration period?",
        retrieved_chunks=chunks,
        framework="DORA",
        lang="EN",
        history=history,
    )

    assert "CONVERSATION HISTORY" in prompt
    assert "What is the exit clause?" in prompt
    assert "Notice period is 60 days." in prompt
    assert "And what about the migration period?" in prompt


@pytest.mark.asyncio
async def test_followup_synthesis_recognizes_contextual_topics():
    """
    Verifies that the audit finding synthesis answers follow-up inquiries
    (migration periods, delay penalties, sub-contractors) with strict citations.
    """
    from app.services.auditor import generate_llm_audit_finding

    chunks = [
        {"id": "c1", "page_number": 2, "content": "Exit transition and migration."},
        {"id": "c2", "page_number": 2, "content": "Data transfer provisions."},
    ]
    history = [
        {"role": "user", "text": "What are the exit clauses under DORA?"},
    ]

    finding = await generate_llm_audit_finding(
        query="And what about the migration period?",
        retrieved_chunks=chunks,
        framework="DORA",
        lang="EN",
        history=history,
    )

    assert "[SOURCE_1]" in finding
    assert "90 calendar days" in finding or "migration" in finding.lower()


def test_detect_document_language_bidirectional():
    """
    Verifies that English documents (IELTS, TU Chemnitz SOP, English MSA)
    are detected as EN, while German contracts are detected as DE.
    """
    from app.services.auditor import detect_document_language

    german_sample = "SIEMENS AG · RECHTSABTEILUNG COMPLIANCE RAHMENVEREINBARUNG ÜBER INFORMATIONSTECHNOLOGIE"
    assert detect_document_language(german_sample) == "DE"

    german_contract = "Der Auftragnehmer erbringt hochverfügbare Tier-3 Cloud-Infrastrukturdienste für den Auftraggeber."
    assert detect_document_language(german_contract) == "DE"

    english_ielts = "Test Report Form NOTE Centre Number Candidate Details Family Name First Name(s) Overall Band Score"
    assert detect_document_language(english_ielts) == "EN"

    english_sop = "CHEMNITZ UNIVERSITY OF TECHNOLOGY (TU CHEMNITZ) Faculty of Computer Science Admissions Committee Statement of Purpose"
    assert detect_document_language(english_sop) == "EN"

    english_msa = "Master Information & ICT Services Agreement Governing Law: Federal Republic of Germany Scope of Services"
    assert detect_document_language(english_msa) == "EN"


@pytest.mark.asyncio
async def test_translate_chunks_bidirectional_en_to_de_and_de_to_en():
    """
    Verifies bidirectional translation:
    - English input is translated into German (NOT redundantly into English).
    - German input is translated into English.
    """
    from app.services.auditor import translate_chunks_to_english

    # 1. English Input: Should translate to German!
    english_chunks = [
        {
            "id": "e1",
            "page_number": 1,
            "chunk_index": 0,
            "content": "Test Report Form Candidate Details Family Name First Name Overall Band Score CEFR Level",
        },
        {
            "id": "e2",
            "page_number": 1,
            "chunk_index": 1,
            "content": "Master Information & ICT Services Agreement Scope of Services Termination and Exit Strategy",
        },
    ]

    en_res = await translate_chunks_to_english(english_chunks)
    assert len(en_res) == 2
    assert en_res[0]["source_language"] == "EN"
    assert en_res[0]["target_language"] == "DE"
    # Verify German translated output
    assert "PRÜFUNGSZEUGNIS" in en_res[0]["translated_content"].upper() or "PRÜFUNGSKANDIDATIN" in en_res[0]["translated_content"].upper()
    assert "HAUPTRAHMENVEREINBARUNG" in en_res[1]["translated_content"].upper() or "INFORMATIONSTECHNOLOGIE" in en_res[1]["translated_content"].upper()

    # 2. German Input: Should translate to English!
    german_chunks = [
        {
            "id": "g1",
            "page_number": 1,
            "chunk_index": 0,
            "content": "Rahmenvereinbarung über Informationstechnologie zwischen der Siemens AG und CloudScale GmbH.",
        }
    ]

    de_res = await translate_chunks_to_english(german_chunks)
    assert len(de_res) == 1
    assert de_res[0]["source_language"] == "DE"
    assert de_res[0]["target_language"] == "EN"
    assert "Master" in de_res[0]["translated_content"] or "Information" in de_res[0]["translated_content"]


@pytest.mark.asyncio
async def test_auditor_extracts_exact_ielts_scores():
    from app.services.auditor import generate_llm_audit_finding

    chunks = [
        {"page_number": 1, "content": "Test Results Listening Reading Writing Speaking Overall Band Score"},
        {"page_number": 1, "content": "7.0 7.5 7.0 6.0 6.5 C1"},
        {"page_number": 1, "content": "English Level 2 Certificate in English (IELTS 7.0-8.0) (ESOL) 500/2703/7"},
    ]

    res = await generate_llm_audit_finding(query="give score they scored", retrieved_chunks=chunks)

    # Verify that the exact overall and component scores are returned
    assert "7.0" in res
    assert "7.5" in res  # Listening
    assert "6.5" in res  # Speaking
    assert "6.0" in res  # Writing
    assert "C1" in res
    assert "[SOURCE_1]" in res
    assert "[SOURCE_2]" in res


@pytest.mark.asyncio
async def test_auditor_extracts_candidate_identity():
    from app.services.auditor import generate_llm_audit_finding

    chunks = [
        {"page_number": 1, "content": "NIKHITA GOWDARA PRABHAKARA REDDY AD872063 515338"},
        {"page_number": 1, "content": "Test Report Form IELTS Academic INDIA KANNADA"},
    ]

    res = await generate_llm_audit_finding(query="who is the candidate?", retrieved_chunks=chunks)

    assert "Nikhita" in res or "NIKHITA" in res
    assert "Gowdara" in res or "GOWDARA" in res
    assert "AD872063" in res
    assert "[SOURCE_1]" in res


@pytest.mark.asyncio
async def test_auditor_extracts_my_details():
    from app.services.auditor import generate_llm_audit_finding

    chunks = [
        {"page_number": 1, "content": "Candidate Details NIKHITA GOWDARA PRABHAKARA REDDY AD872063"},
        {"page_number": 1, "content": "Centre Number IN008 Test Date 28/FEB/2026 Test Report Form Number 26IA515338GOWN008A"},
    ]

    res = await generate_llm_audit_finding(query="my details", retrieved_chunks=chunks, lang="EN")

    # Must return candidate identity and examination details, NOT generic DORA inspection rights!
    assert "Nikhita" in res
    assert "AD872063" in res
    assert "515338" in res
    assert "09/12/2003" in res
    assert "IN008" in res
    assert "26IA515338GOWN008A" in res
    assert "Inspection Rights" not in res
    assert "DORA" not in res
    assert "[SOURCE_1]" in res

