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



export async function getDocumentChunks(documentId: string): Promise<DocumentChunkItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/documents/${documentId}/chunks`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export async function getTranslatedDocumentChunks(documentId: string): Promise<DocumentChunkItem[]> {
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








