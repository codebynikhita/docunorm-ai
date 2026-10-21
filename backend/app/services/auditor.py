import re


def build_audit_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """
    Constructs a strictly grounded regulatory audit prompt for an LLM.
    Each chunk is assigned a source tag like [SOURCE_1], [SOURCE_2], etc.
    """
    formatted_chunks = []
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        page = chunk.get("page_number", 1)
        content = chunk.get("content", "")
        formatted_chunks.append(f"[SOURCE_{idx}] (Page {page}):\n{content}")

    context_str = "\n\n".join(formatted_chunks)

    prompt = f"""You are DocuNorm AI, an automated regulatory compliance auditor.
Your job is to strictly ground your answer ONLY on the provided document sources.
If the answer cannot be found in the sources, state that you cannot find the information.
Do NOT extrapolate or assume. When stating facts, cite the source using [SOURCE_X].

### Document Sources:
{context_str}

### Audit Query:
{query}

### Audit Finding & Answer:"""
    return prompt


def parse_citations_from_response(
    response_text: str, 
    chunk_map: dict[str, dict]
) -> list[dict]:
    """
    Extracts all [SOURCE_X] tags from the AI response and matches them
    against chunk_map to retrieve page_number, bounding_box, and snippet.
    """
    # Regex to find tags like [SOURCE_1], [SOURCE_2]
    # pattern: r"\[SOURCE_(\d+)\]"
    found_tags = set(re.findall(r"\[SOURCE_\d+\]", response_text))

    citations: list[dict] = []
    for tag in found_tags:
        # tag is e.g. "[SOURCE_1]" -> key in chunk_map is "SOURCE_1"
        clean_key = tag.strip("[]")
        if clean_key in chunk_map:
            chunk_data = chunk_map[clean_key]
            citations.append({
                "source_tag": tag,
                "chunk_id": chunk_data.get("chunk_id"),
                "page_number": chunk_data.get("page_number"),
                "bounding_box": chunk_data.get("bounding_box"),
                "content": chunk_data.get("content"),
            })

    return citations