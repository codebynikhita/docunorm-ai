export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

export interface AuditHistoryItem {
  role: "user" | "auditor" | "assistant";
  text: string;
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
  framework: string = "DORA",
  history?: AuditHistoryItem[],
  lang: "DE" | "EN" = "DE"
): Promise<AuditApiResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/audit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, framework, history, lang }),
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

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  tenant_id: string;
  organization: string;
}

export interface AuthSessionResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export async function loginUser(email: string, password: string): Promise<AuthSessionResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Authentication failed.");
  }

  return res.json();
}

export async function signupUser(data: {
  email: string;
  password: string;
  full_name: string;
  organization?: string;
  role?: string;
}): Promise<AuthSessionResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Registration failed.");
  }

  return res.json();
}

export async function getCurrentUser(token: string): Promise<UserProfile | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export interface DoraExitCheckResult {
  rule_id: string;
  name_de: string;
  name_en: string;
  description_de: string;
  description_en: string;
  status: "COMPLIANT" | "PARTIALLY_COMPLIANT" | "NON_COMPLIANT";
  score: number;
  extracted_clause: string | null;
  citation_tag: string | null;
  page_number: number | null;
  bounding_box: [number, number, number, number] | null;
  recommendation_de: string;
  recommendation_en: string;
}

export interface DoraExitAuditReport {
  document_id: string;
  overall_score: number;
  compliance_rating: string;
  evaluated_at: string;
  dora_article: string;
  checks: DoraExitCheckResult[];
  summary_de: string;
  summary_en: string;
}

export async function getDoraExitAudit(documentId: string): Promise<DoraExitAuditReport> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/dora-exit-audit`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `DORA Exit Audit failed with status ${res.status}`);
  }
  return res.json();
}

export interface SubcontractorCheckResult {
  rule_id: string;
  name_de: string;
  name_en: string;
  description_de: string;
  description_en: string;
  status: "COMPLIANT" | "PARTIALLY_COMPLIANT" | "NON_COMPLIANT";
  score: number;
  extracted_clause: string | null;
  citation_tag: string | null;
  page_number: number | null;
  bounding_box?: [number, number, number, number] | null;
  recommendation_de: string;
  recommendation_en: string;
}

export interface CascadingChainNode {
  node_id: string;
  name: string;
  tier: number;
  service_type: string;
  location: string;
  critical_function: boolean;
  approval_status: string;
  risk_level: "NIEDRIG" | "MITTEL" | "HOCH" | "KRITISCH";
}

export interface DoraSubcontractorAuditReport {
  document_id: string;
  overall_score: number;
  compliance_rating: string;
  evaluated_at: string;
  dora_article: string;
  checks: SubcontractorCheckResult[];
  cascading_nodes: CascadingChainNode[];
  concentration_risk_level: "NIEDRIG" | "MODERAT" | "ERHÖHT" | "KRITISCH";
  summary_de: string;
  summary_en: string;
}

export async function getDoraSubcontractorAudit(documentId: string): Promise<DoraSubcontractorAuditReport> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/dora-subcontractor-audit`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `DORA Subcontractor Audit failed with status ${res.status}`);
  }
  return res.json();
}

export interface AuditRightCheckResult {
  rule_id: string;
  name_de: string;
  name_en: string;
  description_de: string;
  description_en: string;
  status: "COMPLIANT" | "PARTIALLY_COMPLIANT" | "NON_COMPLIANT";
  score: number;
  extracted_clause: string | null;
  citation_tag: string | null;
  page_number: number | null;
  bounding_box?: [number, number, number, number] | null;
  recommendation_de: string;
  recommendation_en: string;
}

export interface InspectionNoticeLetter {
  letter_id: string;
  sender_institution: string;
  recipient_vendor: string;
  reference_number: string;
  inspection_date: string;
  legal_basis: string;
  scope_of_inspection: string[];
  german_letter_content: string;
  english_letter_content: string;
}

export interface DoraAuditRightsReport {
  document_id: string;
  overall_score: number;
  compliance_rating: string;
  evaluated_at: string;
  dora_article: string;
  checks: AuditRightCheckResult[];
  notice_letter: InspectionNoticeLetter;
  summary_de: string;
  summary_en: string;
}

export async function getDoraAuditRights(documentId: string): Promise<DoraAuditRightsReport> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/dora-audit-rights`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `DORA Audit Rights Evaluation failed with status ${res.status}`);
  }
  return res.json();
}

export interface ClauseRiskItem {
  chunk_id: string;
  page_number: number;
  bounding_box: [number, number, number, number];
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "CLEAN";
  risk_score: number;
  title: string;
  category: string;
  deficiency_summary_de: string;
  deficiency_summary_en: string;
  statutory_ref: string;
  snippet: string;
}

export interface DocumentRiskHeatmap {
  document_id: string;
  filename: string;
  overall_risk_score: number;
  risk_rating: "AAA" | "AA" | "A" | "BBB" | "BB" | "B" | "CCC";
  critical_count: number;
  high_count: number;
  medium_count: number;
  page_scores: Record<number, number>;
  risk_items: ClauseRiskItem[];
}

export interface DiffToken {
  type: "equal" | "delete" | "insert";
  text: string;
}

export interface AmendmentProposal {
  rule_id: string;
  title_de: string;
  title_en: string;
  original_text: string;
  compliant_replacement_de: string;
  compliant_replacement_en: string;
  legal_justification_de: string;
  legal_justification_en: string;
  bgb_statutory_basis: string;
  dora_statutory_basis: string;
  diff_tokens: DiffToken[];
}

export async function getClauseRiskHeatmap(documentId: string): Promise<DocumentRiskHeatmap> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/clause-risk-heatmap`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Clause Risk Heatmap failed with status ${res.status}`);
  }
  return res.json();
}

export async function generateAmendmentProposal(
  documentId: string,
  ruleId: string,
  originalClause: string
): Promise<AmendmentProposal> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/generate-amendment`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      rule_id: ruleId,
      original_clause: originalClause,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to generate amendment with status ${res.status}`);
  }
  return res.json();
}

export async function downloadAmendmentPdf(documentId: string, proposals?: AmendmentProposal[]): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/export-amendment-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ proposals: proposals || [] }),
  });
  if (!res.ok) {
    throw new Error(`Failed to generate amendment contract PDF (status: ${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Nachtragsvereinbarung_BGB_${documentId.slice(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export interface TableCell {
  row_idx: number;
  col_idx: number;
  text: string;
  bounding_box: [number, number, number, number];
  is_header: boolean;
  is_numeric: boolean;
  confidence?: number;
}

export interface TableRegulatoryAnalysis {
  sla_classification: string;
  compliance_status: "COMPLIANT" | "PARTIALLY_COMPLIANT" | "CRITICAL_NON_COMPLIANT" | string;
  availability_target?: string | null;
  penalty_scale_assessed: string[];
  dora_statutory_basis: string;
  deficiencies: string[];
  recommendations: string[];
}

export interface TableStructure {
  table_id: string;
  document_id: string;
  page_number: number;
  bounding_box: [number, number, number, number];
  row_count: number;
  col_count: number;
  headers: string[];
  rows: string[][];
  cells: TableCell[];
  table_type: "SLA_PENALTY_MATRIX" | "ACADEMIC_SCORE_REPORT" | "FINANCIAL_INVOICE" | "GENERAL_CONTRACTUAL" | string;
  title: string;
  csv_data: string;
  markdown_table: string;
  regulatory_analysis?: TableRegulatoryAnalysis | null;
}

export interface DocumentTablesResponse {
  document_id: string;
  filename: string;
  total_tables: number;
  tables: TableStructure[];
}

export async function getDocumentTables(documentId: string): Promise<DocumentTablesResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/tables`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to extract tables (status: ${res.status})`);
  }
  return res.json();
}

export async function downloadTableCsv(documentId: string, tableId: string, title: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/tables/${tableId}/export.csv`);
  if (!res.ok) {
    throw new Error(`Failed to export table CSV (status: ${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const cleanTitle = title.replace(/[^a-zA-Z0-9_-]/g, "_");
  a.download = `${cleanTitle}_${tableId}.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}



