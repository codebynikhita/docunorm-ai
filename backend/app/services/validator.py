def validate_pdf_metadata(filename: str, file_size_bytes: int) -> bool:
    # Check 1: Filename safety & null byte protection
    if not filename or len(filename) > 255:
        raise ValueError("Filename must be between 1 and 255 characters.")
    if "\x00" in filename:
        raise ValueError("Filename cannot contain null byte characters.")

    # Check 2: Must be a PDF
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    # Check 3: Cannot be empty
    if file_size_bytes <= 0:
        raise ValueError("File cannot be empty.")

    # Check 4: Cannot exceed 50 MB
    max_size = 50 * 1024 * 1024
    if file_size_bytes > max_size:
        raise ValueError("File exceeds maximum allowed size of 50 MB.")

    return True
