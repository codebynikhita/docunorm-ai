import hashlib
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

# Allowed MIME types for enterprise document auditing
ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
}

# Maximum upload limit: 50 Megabytes per file
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
CHUNK_SIZE_BYTES = 64 * 1024  # 64 KB streaming buffer


class StorageService:
    """
    Manages secure local file persistence, MIME validation,
    and SHA-256 tamper-evident fingerprint computation.
    """

    def __init__(self, base_storage_dir: str = "./storage") -> None:
        self.base_dir = Path(base_storage_dir)
        self.documents_dir = self.base_dir / "documents"
        # Ensure directories exist
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    async def validate_and_hash_file(
        self,
        file: UploadFile,
    ) -> tuple[str, int, bytes]:
        """
        Validates MIME type, streams bytes to compute cryptographic SHA-256 hash,
        and enforces maximum size constraints without loading entire large files into RAM.

        Returns:
            Tuple of (sha256_hex_digest, total_file_size_bytes, file_bytes)
        """
        # 1. Validate MIME type
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=(
                    f"Unsupported media type '{content_type}'. "
                    f"DocuNorm AI currently accepts: {list(ALLOWED_MIME_TYPES.keys())}"
                ),
            )

        hasher = hashlib.sha256()
        total_size = 0
        file_chunks: list[bytes] = []

        # 2. Stream and compute hash iteratively
        while chunk := await file.read(CHUNK_SIZE_BYTES):
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.",
                )
            hasher.update(chunk)
            file_chunks.append(chunk)

        # Reset file cursor
        await file.seek(0)

        sha256_hash = hasher.hexdigest()
        full_content = b"".join(file_chunks)
        return sha256_hash, total_size, full_content

    def save_document(
        self,
        tenant_id: str,
        sha256_hash: str,
        content: bytes,
    ) -> Path:
        """
        Persists document bytes using content-addressable storage scheme:
        ./storage/documents/{tenant_id}/{sha256}.pdf
        """
        tenant_dir = self.documents_dir / str(tenant_id)
        tenant_dir.mkdir(parents=True, exist_ok=True)

        target_path = tenant_dir / f"{sha256_hash}.pdf"
        if not target_path.exists():
            target_path.write_bytes(content)

        return target_path


# Global singleton instance for dependency injection
storage_service = StorageService()
