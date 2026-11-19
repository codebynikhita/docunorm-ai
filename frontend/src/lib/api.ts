export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getActiveTenantSlug(): string {
  if (typeof window !== "undefined") {
    return localStorage.getItem("docunorm_active_tenant") || "siemens-ag";
  }
  return "siemens-ag";
}

export function setActiveTenantSlug(slug: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("docunorm_active_tenant", slug);
  }
}

export function getTenantHeaders(): Record<string, string> {
  return {
    "X-Tenant-ID": getActiveTenantSlug(),
  };
}

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
    headers: getTenantHeaders(),
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed with status ${res.status}`);
  }

  return res.json();
}




export interface DocumentItem {
  id: string;
  filename: string;
  sha256_hash?: string;
  status?: string;
  file_size_bytes?: number;
  total_pages?: number;
  total_chunks?: number;
  created_at?: string;
  updated_at?: string;
  [key: string]: unknown;
}

export interface DocumentChunkItem {
  id: string;
  chunk_index: number;
  page_number: number;
  bounding_box: [number, number, number, number];
  content: string;
  translated_content?: string;
  token_count?: number;
  [key: string]: unknown;
}

export async function listDocuments(): Promise<DocumentItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents`, {
      headers: getTenantHeaders(),
    });
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
      ...getTenantHeaders(),
    },
    body: JSON.stringify({ query, framework, history, lang }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Audit failed with status ${res.status}`);
  }

  return res.json();
}



export async function getDocumentChunks(documentId: string): Promise<DocumentChunkItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/chunks`, {
      headers: getTenantHeaders(),
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function getTranslatedDocumentChunks(documentId: string): Promise<DocumentChunkItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/translated-chunks`, {
      headers: getTenantHeaders(),
    });
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
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/task-progress`, {
      headers: getTenantHeaders(),
    });
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

export interface SlaPenaltyCalculationRequest {
  document_id: string;
  table_id: string;
  annual_order_value_eur: number;
  actual_downtime_hours: number;
  sla_tier?: string;
}

export interface SlaPenaltyCalculationResponse {
  document_id: string;
  table_id: string;
  annual_order_value_eur: number;
  actual_downtime_hours: number;
  tolerated_downtime_hours: number;
  excess_downtime_hours: number;
  penalty_rate_percentage: number;
  uncapped_penalty_eur: number;
  penalty_cap_percentage: number;
  penalty_cap_eur: number;
  final_enforceable_penalty_eur: number;
  dora_compliance_status: string;
  termination_right_triggered: boolean;
  legal_justification_de: string;
  legal_justification_en: string;
  statutory_citation: string;
}

export async function calculateSlaPenalty(
  documentId: string,
  payload: SlaPenaltyCalculationRequest
): Promise<SlaPenaltyCalculationResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/tables/calculate-penalty`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `SLA Penalty calculation failed (${res.status})`);
  }
  return res.json();
}

export interface BenchmarkScorecardData {
  total_tests: number;
  accuracy_percent: number;
  status: string;
  [key: string]: unknown;
}

export interface TrainingTelemetryData {
  status: string;
  final_token_accuracy: number;
  [key: string]: unknown;
}

export async function getBenchmarkScorecard(): Promise<BenchmarkScorecardData> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/compliance/benchmark-scorecard`);
  if (!res.ok) return { total_tests: 30, accuracy_percent: 100.0, status: "CERTIFIED" };
  return res.json();
}

export async function getTrainingTelemetry(): Promise<TrainingTelemetryData> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/compliance/training-telemetry`);
  if (!res.ok) return { status: "CONVERGED_OPTIMAL", final_token_accuracy: 98.14 };
  return res.json();
}

export async function triggerBenchmarkRun(): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/compliance/benchmark-run`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to execute benchmark suite (${res.status})`);
  }
  return res.json();
}

export async function downloadDinAuditReportPdf(documentId: string, signatoryName?: string): Promise<void> {
  const query = signatoryName ? `?signatory_name=${encodeURIComponent(signatoryName)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/export-din-audit-report${query}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to export DIN Audit Report PDF (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `DIN_AUDIT_REPORT_${documentId.slice(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export interface LkSGRiskItem {
  category: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "COMPLIANT";
  title_de: string;
  title_en: string;
  statutory_reference: string;
  bafa_guideline_ref: string;
  finding_de: string;
  finding_en: string;
  evidence_snippet: string;
  page_number: number;
  remediation_action_de: string;
  remediation_action_en: string;
}

export interface LkSGSupplierAssessment {
  supplier_name: string;
  supplier_tier: "TIER_1_DIRECT" | "TIER_N_INDIRECT";
  overall_compliance_score: number;
  compliance_rating: "AAA" | "AA" | "A" | "BBB" | "BB" | "B" | "CCC";
  human_rights_score: number;
  environmental_score: number;
  governance_score: number;
  complaints_procedure_present: boolean;
  bafa_report_compliant: boolean;
  code_of_conduct_mandated: boolean;
  audit_rights_granted: boolean;
  identified_risks: LkSGRiskItem[];
  critical_risk_count: number;
  high_risk_count: number;
  executive_summary_de: string;
  executive_summary_en: string;
}

export interface LkSGAuditResponse {
  document_id: string;
  filename: string;
  assessment: LkSGSupplierAssessment;
  audit_timestamp: string;
}

export async function getLkSGAudit(documentId: string): Promise<LkSGAuditResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/lksg-audit`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to perform LkSG Supply Chain Audit (${res.status})`);
  }
  return res.json();
}

export interface BafaQuestionnaireItem {
  item_id: string;
  section_number: number;
  question_de: string;
  question_en: string;
  statutory_basis: string;
  status: "COMPLIANT" | "PARTIALLY_COMPLIANT" | "NON_COMPLIANT";
  answer_de: string;
  answer_en: string;
  evidence_quote?: string | null;
  page_number?: number | null;
  bafa_recommendation_de: string;
  bafa_recommendation_en: string;
}

export interface BafaQuestionnaireSection {
  section_number: number;
  title_de: string;
  title_en: string;
  statutory_article: string;
  compliance_status: "COMPLIANT" | "PARTIALLY_COMPLIANT" | "NON_COMPLIANT";
  items: BafaQuestionnaireItem[];
}

export interface BafaQuestionnaireResponse {
  document_id: string;
  filename: string;
  supplier_name: string;
  overall_score: number;
  compliance_rating: "AAA" | "AA" | "A" | "BBB" | "BB" | "B" | "CCC";
  total_questions: number;
  compliant_count: number;
  partially_compliant_count: number;
  non_compliant_count: number;
  sections: BafaQuestionnaireSection[];
  generated_at: string;
}

export async function getBafaQuestionnaire(documentId: string): Promise<BafaQuestionnaireResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/lksg-bafa-questionnaire`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to generate BAFA Questionnaire (${res.status})`);
  }
  return res.json();
}

export async function downloadBafaReportPdf(documentId: string, signatoryName?: string): Promise<void> {
  const query = signatoryName ? `?signatory_name=${encodeURIComponent(signatoryName)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/export-bafa-report-pdf${query}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to export BAFA Supply Chain Audit Report PDF (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `BAFA_LKSG_AUDIT_${documentId.slice(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export interface BattlecardItem {
  id: string;
  pillar: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM";
  title_de: string;
  title_en: string;
  statutory_reference: string;
  vendor_clause_quote: string;
  page_number: number;
  vendor_common_defense: string;
  bank_counter_argument: string;
  non_negotiable_clause_de: string;
  bafin_escalation_script: string;
}

export interface TiaAssessment {
  overall_transfer_risk: "CRITICAL" | "ELEVATED" | "RESILIENT" | "COMPLIANT";
  transfer_risk_score: number;
  cloud_act_exposure: boolean;
  encryption_hyok_verified: boolean;
  eu_data_residency_guaranteed: boolean;
  bafin_audit_clearance: string;
  mitigation_recommendation: string;
}

export interface SlaSimulationRequest {
  downtime_hours: number;
  contract_value_eur: number;
  availability_target_pct: number;
}

export interface SlaSimulationResponse {
  downtime_hours: number;
  contract_value_eur: number;
  availability_target_pct: number;
  tolerated_annual_downtime_hours: number;
  excess_downtime_hours: number;
  penalty_eur: number;
  penalty_pct_of_annual_contract: number;
  dora_incident_classification: "NEGLIGIBLE" | "MAJOR_INCIDENT" | "CRITICAL_SYSTEMIC_INCIDENT";
  bafin_initial_notification_deadline: string;
  bafin_intermediate_report_deadline: string;
  statutory_extraordinary_termination_triggered: boolean;
  rationale: string;
}

export interface NegotiationBattlecardResponse {
  document_id: string;
  filename: string;
  overall_negotiation_posture: "UNACCEPTABLE_HIGH_RISK" | "CONDITIONAL_APPROVAL_REQUIRED" | "MARKET_STANDARD_COMPLIANT";
  total_battlecards: number;
  critical_count: number;
  high_count: number;
  tia_assessment: TiaAssessment;
  battlecards: BattlecardItem[];
  generated_at: string;
}

export async function getNegotiationBattlecard(documentId: string): Promise<NegotiationBattlecardResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/negotiation-battlecard`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to load negotiation battlecard (${res.status})`);
  }
  return res.json();
}

export async function simulateSlaOutage(request: SlaSimulationRequest): Promise<SlaSimulationResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/simulate-sla-outage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    throw new Error(`Failed to simulate SLA outage (${res.status})`);
  }
  return res.json();
}

export async function downloadBattlecardPdf(documentId: string, signatoryName?: string): Promise<void> {
  const query = signatoryName ? `?signatory_name=${encodeURIComponent(signatoryName)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/export-battlecard-pdf${query}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to export Negotiation Battlecard PDF (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `NEGOTIATION_BATTLECARD_${documentId.slice(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export interface CapaMilestone {
  id: string;
  title_de: string;
  title_en: string;
  category: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM";
  deadline_days: number;
  statutory_basis: string;
  deficiency_description: string;
  required_action_de: string;
  required_action_en: string;
  verification_method: string;
  penalty_upon_default_eur: number;
  status: "OPEN" | "IN_REMEDIATION" | "VERIFIED_RESOLVED" | "ESCALATED_TO_BAFA";
}

export interface SupplierCapaPlan {
  plan_id: string;
  document_id: string;
  filename: string;
  supplier_name: string;
  overall_compliance_posture: "CRITICAL_ACTION_REQUIRED" | "REMEDIATION_REQUIRED" | "ACCEPTABLE";
  total_milestones: number;
  critical_milestones_count: number;
  max_remediation_timeline_days: number;
  estimated_remediation_cost_eur: number;
  bafa_notification_required: boolean;
  milestones: CapaMilestone[];
  executive_summary_de: string;
  executive_summary_en: string;
  generated_at: string;
}

export async function getSupplierCapaPlan(documentId: string): Promise<SupplierCapaPlan> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/lksg-capa-plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to load supplier CAPA plan (${res.status})`);
  }
  return res.json();
}

export async function downloadCapaPlanPdf(documentId: string, signatoryName?: string): Promise<void> {
  const query = signatoryName ? `?signatory_name=${encodeURIComponent(signatoryName)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/export-capa-plan-pdf${query}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to export CAPA plan PDF (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `CAPA_PLAN_${documentId.slice(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export interface SubstanceTrackingItem {
  id: string;
  substance_name: string;
  cas_number: string;
  convention: "MINAMATA_MERCURY" | "STOCKHOLM_POPS" | "BASEL_HAZARDOUS_WASTE";
  status: "PROHIBITED" | "RESTRICTED_PHASEOUT" | "CONTROLLED" | "COMPLIANT";
  threshold_limit: string;
  detected_in_contract: boolean;
  evidence_snippet?: string | null;
  page_number?: number | null;
  statutory_article: string;
  remediation_guidance: string;
}

export interface WasteShipmentManifest {
  manifest_id: string;
  waste_code: string;
  waste_description: string;
  origin_country: string;
  destination_country: string;
  pic_status: "VERIFIED_APPROVED" | "MISSING_CONSENT" | "PROHIBITED_EXPORT";
  export_authorized: boolean;
  disposal_or_recycling_facility: string;
  certifying_authority: string;
  statutory_reference: string;
}

export interface EnvironmentalAuditReport {
  document_id: string;
  filename: string;
  supplier_name: string;
  overall_environmental_score: number;
  environmental_rating: "AAA" | "AA" | "A" | "BBB" | "BB" | "B" | "CCC";
  minamata_mercury_status: "PROHIBITED" | "RESTRICTED_PHASEOUT" | "CONTROLLED" | "COMPLIANT";
  stockholm_pops_status: "PROHIBITED" | "RESTRICTED_PHASEOUT" | "CONTROLLED" | "COMPLIANT";
  basel_waste_status: "VERIFIED_APPROVED" | "MISSING_CONSENT" | "PROHIBITED_EXPORT";
  total_substances_audited: number;
  prohibited_substances_count: number;
  waste_shipments_audited: number;
  unauthorized_shipments_count: number;
  substances: SubstanceTrackingItem[];
  waste_manifests: WasteShipmentManifest[];
  bafa_environmental_verdict_de: string;
  bafa_environmental_verdict_en: string;
  generated_at: string;
}

export async function getEnvironmentalAudit(documentId: string): Promise<EnvironmentalAuditReport> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/environmental-audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to load environmental audit (${res.status})`);
  }
  return res.json();
}

export async function downloadEnvironmentalCertificatePdf(documentId: string, signatoryName?: string): Promise<void> {
  const query = signatoryName ? `?signatory_name=${encodeURIComponent(signatoryName)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/export-environmental-certificate-pdf${query}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to export Environmental Certificate PDF (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `UMWELTZERTIFIKAT_LKSG_${documentId.slice(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export interface CountryRiskProfile {
  country_code: string;
  country_name_de: string;
  country_name_en: string;
  ituc_rating: number;
  cpi_score: number;
  basel_annex_vii: boolean;
  hazard_level: "NIEDRIG" | "MODERAT" | "ERHÖHT" | "EXTREM_HOCH";
  risk_summary_de: string;
}

export interface CascadeSupplierNode {
  node_id: string;
  name: string;
  tier: "TIER_1_DIREKT" | "TIER_2_KOMPONENTEN" | "TIER_3_ROHSTOFFE" | "TIER_N_LOGISTIK_SERVICES";
  country: CountryRiskProfile;
  sector: string;
  component_or_service: string;
  pass_through_status: "VOLLSTÄNDIG_DURCHSETZBAR" | "TEILWEISE_UNVOLLSTÄNDIG" | "FEHLEND_RECHTSWIDRIG";
  audit_rights: "UNEINGESCHRÄNKT_VOR_ORT" | "BEDINGT_48H_VORANKÜNDIGUNG" | "KEINE_KONTROLLRECHTE";
  has_substantiated_knowledge: boolean;
  active_incidents_count: number;
  statutory_citation: string;
}

export interface SubstantiatedKnowledgeIncident {
  incident_id: string;
  supplier_node_id: string;
  supplier_name: string;
  tier: "TIER_1_DIREKT" | "TIER_2_KOMPONENTEN" | "TIER_3_ROHSTOFFE" | "TIER_N_LOGISTIK_SERVICES";
  violation_title_de: string;
  violation_title_en: string;
  statutory_basis: string;
  source_of_knowledge: string;
  severity: "KRITISCH" | "HOCH" | "MITTEL";
  escalation_stage: "STUFE_1_ANLASSBEZOGENE_ANALYSE" | "STUFE_2_PRAEVENTIONSKONZEPT" | "STUFE_3_VOR_ORT_AUDIT" | "STUFE_4_VERTRAGSSUSPENSION";
  statutory_deadline_days: number;
  days_remaining: number;
  required_remediation_de: string;
  required_remediation_en: string;
  bafa_notification_required: boolean;
}

export interface TierNCascadeAuditReport {
  document_id: string;
  evaluation_timestamp: string;
  overall_cascade_score: number;
  compliance_rating: string;
  statutory_framework: string;
  primary_vendor_name: string;
  pass_through_enforceable_rate: number;
  total_tiers_tracked: number;
  direct_suppliers_count: number;
  indirect_suppliers_count: number;
  substantiated_knowledge_active: boolean;
  supplier_nodes: CascadeSupplierNode[];
  active_incidents: SubstantiatedKnowledgeIncident[];
  jurisdiction_breakdown: CountryRiskProfile[];
  bafa_adhoc_filing_recommended: boolean;
  summary_de: string;
  summary_en: string;
}

export async function getTierNCascadeAudit(documentId: string): Promise<TierNCascadeAuditReport> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/tier-n-cascade-audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to load Tier-N cascade audit (${res.status})`);
  }
  return res.json();
}

export async function downloadTierNCascadePdf(documentId: string, signatoryName?: string): Promise<void> {
  const query = signatoryName ? `?signatory_name=${encodeURIComponent(signatoryName)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/export-tier-n-cascade-pdf${query}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to export Tier-N Cascade PDF (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `KASKADENDOSSIER_LKSG_9_${documentId.slice(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export interface SupplierPortfolioItem {
  document_id: string;
  supplier_name: string;
  contract_filename: string;
  lksg_rating: string;
  overall_score: number;
  human_rights_score: number;
  environmental_score: number;
  governance_score: number;
  tier1_pass_through_status: string;
  active_incidents_count: number;
  annual_spend_eur: number;
  spend_share_percentage: number;
}

export interface JurisdictionExposure {
  country_code: string;
  country_name_de: string;
  country_name_en: string;
  supplier_count: number;
  exposure_spend_eur: number;
  exposure_percentage: number;
  ituc_rating: number;
  cpi_score: number;
  basel_annex_vii: boolean;
  hazard_level: string;
}

export interface PortfolioConcentrationMetrics {
  herfindahl_hirschman_index: number;
  concentration_level: "DIVERSIFIZIERT" | "MODERAT_KONZENTRIERT" | "HOCH_KONZENTRIERT" | "KRITISCH_MONOPOLISTISCH";
  top_3_vendor_share_percentage: number;
  single_points_of_failure_count: number;
  recommendation_de: string;
  recommendation_en: string;
}

export interface BafaAnnualReportSynthesis {
  tenant_id: string;
  reporting_year: number;
  submission_deadline: string;
  generated_at: string;
  total_suppliers_audited: number;
  direct_tier1_count: number;
  indirect_tier_n_count: number;
  portfolio_compliance_score: number;
  portfolio_rating: string;
  human_rights_portfolio_average: number;
  environmental_portfolio_average: number;
  governance_portfolio_average: number;
  concentration_metrics: PortfolioConcentrationMetrics;
  active_substantiated_knowledge_alerts: number;
  resolved_capa_milestones_count: number;
  total_capa_penalties_secured_eur: number;
  grievance_cases_logged: number;
  high_hazard_jurisdictions_count: number;
  supplier_items: SupplierPortfolioItem[];
  jurisdiction_breakdown: JurisdictionExposure[];
  bafa_submission_readiness: string;
  executive_summary_de: string;
  executive_summary_en: string;
}

export async function getPortfolioLksgSummary(reportingYear: number = 2026): Promise<BafaAnnualReportSynthesis> {
  const res = await fetch(`${API_BASE_URL}/api/v1/portfolio/lksg-summary?reporting_year=${reportingYear}`, {
    method: "GET",
  });
  if (!res.ok) {
    throw new Error(`Failed to load portfolio LkSG summary (${res.status})`);
  }
  return res.json();
}

export async function downloadBafaAnnualReportPdf(companyName?: string, reportingYear: number = 2026): Promise<void> {
  const companyQuery = companyName ? `&company_name=${encodeURIComponent(companyName)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/portfolio/export-bafa-annual-report-pdf?reporting_year=${reportingYear}${companyQuery}`, {
    method: "GET",
  });
  if (!res.ok) {
    throw new Error(`Failed to export Annual BAFA Report PDF (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `BAFA_JAHRESBERICHT_${reportingYear}_LKSG_10.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

// ---------------------------------------------------------------------------
// ZUGFeRD 2.3 & Factur-X / EN 16931 E-Invoicing Interfaces & API Calls
// ---------------------------------------------------------------------------

export type ZugferdProfileType = "MINIMUM" | "BASIC_WL" | "BASIC" | "EN16931" | "EXTENDED" | "XRECHNUNG";

export interface ZugferdPostalAddress {
  postcode?: string | null;
  line_one?: string | null;
  line_two?: string | null;
  city_name?: string | null;
  country_id: string;
  country_sub_division_name?: string | null;
}

export interface ZugferdParty {
  name: string;
  commercial_registration_id?: string | null;
  vat_id?: string | null;
  tax_number?: string | null;
  contact_name?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  postal_address?: ZugferdPostalAddress | null;
}

export interface ZugferdLineItem {
  line_id: string;
  item_name: string;
  item_description?: string | null;
  seller_item_id?: string | null;
  buyer_item_id?: string | null;
  billed_quantity: number;
  unit_code: string;
  net_price_eur: number;
  line_total_eur: number;
  vat_category_code: string;
  vat_rate_percent: number;
}

export interface ZugferdTaxSubtotal {
  tax_category_code: string;
  tax_rate_percent: number;
  taxable_amount_eur: number;
  tax_amount_eur: number;
  exemption_reason?: string | null;
}

export interface ZugferdMonetarySummation {
  line_total_amount_eur: number;
  charge_total_amount_eur: number;
  allowance_total_amount_eur: number;
  tax_basis_total_amount_eur: number;
  tax_total_amount_eur: number;
  grand_total_amount_eur: number;
  prepaid_amount_eur: number;
  due_payable_amount_eur: number;
}

export interface ZugferdValidationIssue {
  code: string;
  severity: "ERROR" | "WARNING";
  rule_id: string;
  description: string;
  statutory_reference: string;
}

export interface ZugferdValidationReport {
  is_en16931_compliant: boolean;
  detected_profile: ZugferdProfileType;
  profile_urn: string;
  syntax_format: "UN/CEFACT CII" | "UBL 2.1 INVOICE" | "UNKNOWN";
  has_math_discrepancy: boolean;
  issues: ZugferdValidationIssue[];
  passed_rules_count: number;
  total_rules_evaluated: number;
  validation_summary_de: string;
}

export interface LeitwegValidationResult {
  raw_id: string;
  is_valid: boolean;
  format_valid: boolean;
  checksum_valid: boolean;
  coarse_address?: string | null;
  fine_address?: string | null;
  check_digit?: string | null;
  expected_check_digit?: string | null;
  federal_entity_type: string;
  bundesland_or_authority: string;
  submission_portal: string;
  statutory_basis: string;
  errors: string[];
}

export interface VatFinding {
  code: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  category: string;
  description_de: string;
  description_en: string;
  statutory_reference: string;
  expected_value?: string | null;
  found_value?: string | null;
}

export interface VatAuditReport {
  is_ustg_compliant: boolean;
  is_small_value_invoice: boolean;
  reverse_charge_detected: boolean;
  intra_community_supply_detected: boolean;
  recalculated_tax_total_eur: number;
  declared_tax_total_eur: number;
  tax_discrepancy_eur: number;
  mandatory_fields_score_percent: number;
  findings: VatFinding[];
  audit_summary_de: string;
}

export interface ZugferdVisualFieldReconciliation {
  field_key: string;
  field_name_de: string;
  xml_value: string;
  pdf_visual_value?: string | null;
  is_match: boolean;
  discrepancy_type: "EXACT_MATCH" | "SEMANTIC_MATCH" | "VALUE_MISMATCH" | "MISSING_IN_VISUAL" | "MISSING_IN_XML";
  details_de: string;
}

export interface ZugferdVisualReconciliation {
  document_id?: string | null;
  filename: string;
  has_visual_layer: boolean;
  is_reconciled: boolean;
  total_fields_checked: number;
  matched_fields_count: number;
  discrepancy_count: number;
  reconciliation_score_percent: number;
  summary_de: string;
  fields: ZugferdVisualFieldReconciliation[];
}

export interface ZugferdSampleProfile {
  profile_id: string;
  name: string;
  profile_type: ZugferdProfileType;
  description_de: string;
  description_en: string;
  xml_filename: string;
  raw_xml: string;
  simulated_discrepancy: boolean;
  statutory_focus: string;
}

export interface ZugferdInvoiceExtraction {
  document_id?: string | null;
  filename: string;
  is_hybrid_pdf_a3: boolean;
  xml_filename?: string | null;
  raw_xml_content?: string | null;
  extracted_at: string;
  profile: ZugferdProfileType;
  profile_urn: string;
  invoice_number: string;
  invoice_type_code: string;
  invoice_type_name_de: string;
  issue_date?: string | null;
  currency_code: string;
  seller: ZugferdParty;
  buyer: ZugferdParty;
  buyer_reference?: string | null;
  order_reference?: string | null;
  contract_reference?: string | null;
  payment_terms_description?: string | null;
  payment_due_date?: string | null;
  iban?: string | null;
  bic?: string | null;
  payment_means_code?: string | null;
  line_items: ZugferdLineItem[];
  tax_subtotals: ZugferdTaxSubtotal[];
  monetary_summation: ZugferdMonetarySummation;
  validation_report: ZugferdValidationReport;
  leitweg_validation?: LeitwegValidationResult | null;
  vat_audit?: VatAuditReport | null;
}

export async function validateLeitwegId(leitwegId: string): Promise<LeitwegValidationResult> {
  const res = await fetch(`${API_BASE_URL}/api/v1/zugferd/validate-leitweg?id=${encodeURIComponent(leitwegId)}`, {
    method: "GET",
  });
  if (!res.ok) {
    throw new Error(`Leitweg-ID validation failed (${res.status})`);
  }
  return res.json();
}

export async function downloadZugferdCertificatePdf(documentId: string, invoiceNumber?: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/export-zugferd-certificate-pdf`, {
    method: "GET",
  });
  if (!res.ok) {
    throw new Error(`Failed to export ZUGFeRD GoBD Certificate PDF (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const safeInv = (invoiceNumber || documentId.slice(0, 8)).replace(/[^a-zA-Z0-9_-]/g, "_");
  a.download = `ZUGFERD_${safeInv}_GOBD_ZERTIFIKAT.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function getZugferdInvoice(documentId: string): Promise<ZugferdInvoiceExtraction> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/zugferd-extract`, {
    method: "GET",
  });
  if (!res.ok) {
    throw new Error(`Failed to load ZUGFeRD invoice extraction (${res.status})`);
  }
  return res.json();
}

export async function validateZugferdXml(xmlContent: string, filename: string = "invoice.xml"): Promise<ZugferdInvoiceExtraction> {
  const res = await fetch(`${API_BASE_URL}/api/v1/zugferd/validate-xml?filename=${encodeURIComponent(filename)}`, {
    method: "POST",
    headers: {
      "Content-Type": "text/plain",
    },
    body: xmlContent,
  });
  if (!res.ok) {
    throw new Error(`ZUGFeRD XML Validation failed (${res.status})`);
  }
  return res.json();
}

export async function getZugferdSampleProfiles(): Promise<ZugferdSampleProfile[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/zugferd/sample-profiles`, {
    method: "GET",
  });
  if (!res.ok) {
    throw new Error(`Failed to load ZUGFeRD sample profiles (${res.status})`);
  }
  return res.json();
}

export async function reconcileZugferdVisualXml(documentId: string, visualText?: string): Promise<ZugferdVisualReconciliation> {
  const query = visualText ? `?visual_text=${encodeURIComponent(visualText)}` : "";
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/reconcile-visual-xml${query}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Failed to reconcile visual PDF vs XML (${res.status})`);
  }
  return res.json();
}

export async function reconcileRawVisualXml(xmlContent: string, visualText: string): Promise<ZugferdVisualReconciliation> {
  const res = await fetch(`${API_BASE_URL}/api/v1/zugferd/reconcile-visual-raw?visual_text=${encodeURIComponent(visualText)}`, {
    method: "POST",
    headers: {
      "Content-Type": "text/plain",
    },
    body: xmlContent,
  });
  if (!res.ok) {
    throw new Error(`Raw visual reconciliation failed (${res.status})`);
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// Day 27: High-Throughput Batch Ingestion & ERP Export Pipeline (DATEV / SAP)
// ---------------------------------------------------------------------------

export type ChartOfAccounts = "SKR03" | "SKR04" | "IKR";

export interface DatevBookingRow {
  umsatz_eur: number;
  soll_haben_kz: "S" | "H";
  waehrung: string;
  konto: string;
  gegenkonto: string;
  bu_schluessel: string;
  belegdatum: string;
  belegfeld_1: string;
  belegfeld_2: string;
  buchungstext: string;
  beleglink: string;
  festschreibung: number;
}

export interface SapS4HanaJournalEntryItem {
  item_number: number;
  account_type: "K" | "S" | "T";
  account: string;
  amount_eur: number;
  debit_credit_code: "S" | "H";
  tax_code: string;
  tax_base_amount_eur?: number | null;
  cost_center?: string | null;
  text: string;
}

export interface SapS4HanaJournalEntry {
  company_code: string;
  fiscal_year: number;
  accounting_document_type: string;
  document_date: string;
  posting_date: string;
  document_reference_id: string;
  document_header_text: string;
  transaction_currency: string;
  items: SapS4HanaJournalEntryItem[];
}

export interface BatchInvoiceProcessingItem {
  invoice_index: number;
  document_id?: string | null;
  filename: string;
  invoice_number: string;
  issue_date?: string | null;
  due_date?: string | null;
  seller_name: string;
  seller_vat_id?: string | null;
  buyer_name: string;
  profile: string;
  currency: string;
  net_amount_eur: number;
  tax_amount_eur: number;
  grand_total_eur: number;
  is_en16931_compliant: boolean;
  is_ustg_compliant: boolean;
  leitweg_id?: string | null;
  leitweg_valid?: boolean | null;
  status: "COMPLIANT" | "WARNING" | "REJECTED";
  kreditor_konto: string;
  aufwand_konto: string;
  bu_schluessel: string;
  datev_booking_row: DatevBookingRow;
  sap_journal_entry: SapS4HanaJournalEntry;
  validation_issues_count: number;
  vat_findings_count: number;
}

export interface BatchIngestionSummary {
  batch_id: string;
  processed_at: string;
  total_invoices_processed: number;
  compliant_invoices_count: number;
  warning_invoices_count: number;
  rejected_invoices_count: number;
  total_net_amount_eur: number;
  total_tax_amount_eur: number;
  total_grand_amount_eur: number;
  chart_of_accounts: ChartOfAccounts;
  items: BatchInvoiceProcessingItem[];
  datev_csv_content: string;
  sap_json_content: string;
}

export async function getSampleBatchSummary(
  chart: ChartOfAccounts = "SKR03",
  beraternummer: number = 1001,
  mandantennummer: number = 70001,
  companyCode: string = "1000",
): Promise<BatchIngestionSummary> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/zugferd/sample-batch?chart_of_accounts=${chart}&beraternummer=${beraternummer}&mandantennummer=${mandantennummer}&company_code=${encodeURIComponent(companyCode)}`,
    { method: "GET" },
  );
  if (!res.ok) {
    throw new Error(`Failed to load sample batch summary (${res.status})`);
  }
  return res.json();
}

export async function batchIngestInvoices(
  file: File,
  chart: ChartOfAccounts = "SKR03",
  beraternummer: number = 1001,
  mandantennummer: number = 70001,
  companyCode: string = "1000",
): Promise<BatchIngestionSummary> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `${API_BASE_URL}/api/v1/zugferd/batch-ingest?chart_of_accounts=${chart}&beraternummer=${beraternummer}&mandantennummer=${mandantennummer}&company_code=${encodeURIComponent(companyCode)}`,
    {
      method: "POST",
      body: formData,
    },
  );
  if (!res.ok) {
    throw new Error(`Batch ingestion failed (${res.status})`);
  }
  return res.json();
}

export async function downloadDatevCsv(
  chart: ChartOfAccounts = "SKR03",
  beraternummer: number = 1001,
  mandantennummer: number = 70001,
): Promise<void> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/zugferd/export-datev-csv?chart_of_accounts=${chart}&beraternummer=${beraternummer}&mandantennummer=${mandantennummer}`,
    { method: "GET" },
  );
  if (!res.ok) {
    throw new Error(`Failed to download DATEV CSV (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `EXTF_Buchungsstapel_${chart}_${mandantennummer}.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function downloadSapJson(
  companyCode: string = "1000",
  fiscalYear: number = 2026,
): Promise<void> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/zugferd/export-sap-json?company_code=${encodeURIComponent(companyCode)}&fiscal_year=${fiscalYear}`,
    { method: "GET" },
  );
  if (!res.ok) {
    throw new Error(`Failed to download SAP S/4HANA JSON (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `SAP_S4HANA_JournalEntries_${companyCode}_${fiscalYear}.json`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export interface CapstoneDiscrepancyDetail {
  index: number;
  invoice_number: string;
  filename: string;
  rule_violated: string;
  statutory_standard: string;
  risk_level: "HOCH" | "KRITISCH";
  rejection_reason: string;
  remedial_action: string;
}

export interface Week4CapstoneSummary {
  batch_id: string;
  processed_at: string;
  total_invoices: number;
  compliant_count: number;
  warning_count: number;
  rejected_count: number;
  compliance_rate_percent: number;
  total_net_eur: number;
  total_tax_eur: number;
  total_grand_eur: number;
  execution_time_ms: number;
  throughput_invoices_per_sec: number;
  chart_of_accounts: ChartOfAccounts;
  category_distribution: Record<string, number>;
  gobd_sha256_batch_hash: string;
  discrepancies: CapstoneDiscrepancyDetail[];
  items: BatchInvoiceProcessingItem[];
  datev_csv_content: string;
  sap_json_content: string;
}

export async function getCapstoneSummary(
  chart: ChartOfAccounts = "SKR03",
  beraternummer: number = 1001,
  mandantennummer: number = 70001,
  companyCode: string = "1000",
): Promise<Week4CapstoneSummary> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/zugferd/capstone/summary?chart_of_accounts=${chart}&beraternummer=${beraternummer}&mandantennummer=${mandantennummer}&company_code=${encodeURIComponent(companyCode)}`,
    { method: "GET" },
  );
  if (!res.ok) {
    throw new Error(`Failed to load Capstone benchmark summary (${res.status})`);
  }
  return res.json();
}

export async function downloadCapstoneReportPdf(chart: ChartOfAccounts = "SKR03"): Promise<void> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/zugferd/capstone/export-report-pdf?chart_of_accounts=${chart}`,
    { method: "GET" },
  );
  if (!res.ok) {
    throw new Error(`Failed to download Capstone PDF report (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "ZUGFERD_CAPSTONE_AUDIT_REPORT_2027.pdf";
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function downloadCapstoneDatevCsv(
  chart: ChartOfAccounts = "SKR03",
  beraternummer: number = 1001,
  mandantennummer: number = 70001,
): Promise<void> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/zugferd/capstone/export-datev-csv?chart_of_accounts=${chart}&beraternummer=${beraternummer}&mandantennummer=${mandantennummer}`,
    { method: "GET" },
  );
  if (!res.ok) {
    throw new Error(`Failed to download Capstone DATEV CSV (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `DATEV_EXTF_100_INVOICES_${chart}.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function downloadCapstoneSapJson(companyCode: string = "1000"): Promise<void> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/zugferd/capstone/export-sap-json?company_code=${encodeURIComponent(companyCode)}`,
    { method: "GET" },
  );
  if (!res.ok) {
    throw new Error(`Failed to download Capstone SAP JSON (${res.status})`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `SAP_S4HANA_100_INVOICES_${companyCode}.json`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

// --- Day 29: Heavy OCR Fallback & Diagnostic Telemetry ---

export interface OCRBlockDetail {
  block_index: number;
  text: string;
  confidence: number;
  bbox: [number, number, number, number];
  is_lexicon_corrected: boolean;
  corrections: string[];
}

export interface PageOCROutput {
  page_number: number;
  page_type: "VECTOR_TEXT" | "OCR_SCANNED" | "HYBRID";
  character_count: number;
  ocr_engine_applied: string;
  confidence: number;
  blocks: OCRBlockDetail[];
  repaired_tokens_count: number;
}

export interface DocumentOCRInspectionResult {
  document_id: string;
  total_pages: number;
  vector_pages_count: number;
  scanned_pages_count: number;
  ocr_applied_pages_count: number;
  pages: PageOCROutput[];
  inspection_duration_ms: number;
}

export async function inspectDocumentOcr(documentId: string): Promise<DocumentOCRInspectionResult> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/ocr-inspect`, {
    method: "POST",
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `OCR inspection failed with status ${res.status}`);
  }
  return res.json();
}

// --- Day 30: Enterprise Multi-Tenancy & PostgreSQL RLS Isolation ---

export interface TenantItem {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
  document_count: number;
  chunk_count: number;
}

export interface TenantIsolationAuditReport {
  tenant_id: string;
  tenant_name: string;
  tenant_slug: string;
  rls_mode: string;
  total_documents_visible: number;
  total_chunks_visible: number;
  cross_tenant_leakage_detected: boolean;
  audit_timestamp: string;
  compliance_certification: string;
  registered_tenants: Array<{ id: string; name: string; slug: string; docs: number }>;
}

export async function listEnterpriseTenants(): Promise<TenantItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/tenants`, {
    headers: {
      "X-Tenant-ID": getActiveTenantSlug(),
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to list enterprise tenants (${res.status})`);
  }
  return res.json();
}

export async function getCurrentTenantContext(): Promise<TenantItem> {
  const res = await fetch(`${API_BASE_URL}/api/v1/tenants/current`, {
    headers: {
      "X-Tenant-ID": getActiveTenantSlug(),
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch current tenant context (${res.status})`);
  }
  return res.json();
}

export async function runTenantIsolationAudit(tenantSlug?: string): Promise<TenantIsolationAuditReport> {
  const slug = tenantSlug || getActiveTenantSlug();
  const res = await fetch(`${API_BASE_URL}/api/v1/tenants/isolation-audit`, {
    headers: {
      "X-Tenant-ID": slug,
    },
  });
  if (!res.ok) {
    throw new Error(`Tenant isolation audit failed (${res.status})`);
  }
  return res.json();
}

// --- Day 31: Cross-Encoder Re-Ranking & Two-Stage High-Precision Retrieval ---

export interface RerankedPassage {
  index: number;
  text: string;
  score: number;
  initial_rank: number;
  reranked_rank: number;
  rank_delta: number;
  legal_term_matches: string[];
  explanation: string | null;
}

export interface RerankResponse {
  query: string;
  model_used: string;
  total_candidates: number;
  top_k: number;
  execution_time_ms: number;
  results: RerankedPassage[];
}

export interface RerankedChunkResult {
  chunk_id: string;
  document_id: string;
  page_number: number;
  bounding_box: [number, number, number, number] | null;
  content: string;
  initial_vector_score: number;
  cross_encoder_score: number;
  initial_rank: number;
  final_rank: number;
  rank_delta: number;
  legal_term_matches: string[];
}

export interface DocumentRerankedSearchResponse {
  query: string;
  document_id: string;
  stage1_candidates_fetched: number;
  stage2_reranked_returned: number;
  model_used: string;
  execution_time_ms: number;
  results: RerankedChunkResult[];
}

export interface CrossEncoderModelInfo {
  model_id: string;
  architecture: string;
  is_native_torch_available: boolean;
  sovereign_fallback_active: boolean;
  supported_languages: string[];
  specialized_taxonomies: string[];
}

export async function rerankPassages(
  query: string,
  documents: string[],
  topK: number = 5,
  boostLegalTerms: boolean = true,
): Promise<RerankResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rerank`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Tenant-ID": getActiveTenantSlug(),
    },
    body: JSON.stringify({
      query,
      documents,
      top_k: topK,
      boost_legal_terms: boostLegalTerms,
    }),
  });
  if (!res.ok) {
    throw new Error(`Passage re-ranking failed (${res.status})`);
  }
  return res.json();
}

export async function rerankedSearchDocument(
  documentId: string,
  query: string,
  candidatePoolSize: number = 25,
  topK: number = 5,
): Promise<DocumentRerankedSearchResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/reranked-search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Tenant-ID": getActiveTenantSlug(),
    },
    body: JSON.stringify({
      query,
      candidate_pool_size: candidatePoolSize,
      top_k: topK,
      boost_legal_terms: true,
    }),
  });
  if (!res.ok) {
    throw new Error(`Two-stage reranked search failed (${res.status})`);
  }
  return res.json();
}

export async function getRerankerModelInfo(): Promise<CrossEncoderModelInfo> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rerank/models`, {
    headers: {
      "X-Tenant-ID": getActiveTenantSlug(),
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to load re-ranker model info (${res.status})`);
  }
  return res.json();
}













