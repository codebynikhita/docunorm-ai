const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface DocumentUploadResponse {
  message: string;
  is_duplicate: boolean;
  document: {
    id: string;
    filename: string;
    total_pages: number | null;
    sha256_hash: string;
    file_size_bytes: number;
    created_at: string;
  };
}

export async function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed with status ${res.status}`);
  }

  return res.json();
}




export async function listDocuments(): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export interface AuditCitationResponse {
  source_tag: string;
  chunk_id?: string;
  page_number: number;
  bounding_box?: [number, number, number, number];
  content?: string;
}

export interface AuditApiResponse {
  document_id: string;
  query: string;
  framework: string;
  status: string;
  finding_summary: string;
  citations: AuditCitationResponse[];
}

export async function auditDocument(
  documentId: string,
  query: string,
  framework: string = "DORA"
): Promise<AuditApiResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/audit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, framework }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Audit failed with status ${res.status}`);
  }

  return res.json();
}



export async function getDocumentChunks(documentId: string): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/chunks`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function getTranslatedDocumentChunks(documentId: string): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/translated-chunks`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export interface TaskProgressResponse {
  document_id: string;
  status: "pending" | "processing" | "ready" | "failed" | "unknown";
  progress: number;
  stage: string;
  error?: string | null;
}

export async function getDocumentTaskProgress(documentId: string): Promise<TaskProgressResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/task-progress`);
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}
