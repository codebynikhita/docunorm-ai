from uuid import UUID
from pydantic import BaseModel, Field


class TableCell(BaseModel):
    row_idx: int
    col_idx: int
    text: str
    bounding_box: tuple[float, float, float, float] = Field(
        ..., description="Visual [x0, y0, x1, y1] coordinates on PDF page"
    )
    is_header: bool = False
    is_numeric: bool = False
    confidence: float = 1.0


class TableRegulatoryAnalysis(BaseModel):
    sla_classification: str = Field(
        ..., description="e.g. Tier-3 Mission-Critical Cloud Service Level"
    )
    compliance_status: str = Field(
        ..., description="COMPLIANT, PARTIALLY_COMPLIANT, or CRITICAL_NON_COMPLIANT"
    )
    availability_target: str | None = Field(
        default=None, description="e.g. 99.95% annual availability"
    )
    penalty_scale_assessed: list[str] = Field(
        default_factory=list, description="Evaluated penalty tiers (0.2%/day, 5%, 25%)"
    )
    dora_statutory_basis: str = Field(
        default="DORA Art. 30 Abs. 2 lit. c, e · BaFin BAIT 8.1"
    )
    deficiencies: list[str] = Field(
        default_factory=list, description="Identified legal or SLA loopholes"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Remediation steps for supervisory compliance"
    )


class TableStructure(BaseModel):
    table_id: str
    document_id: UUID
    page_number: int
    bounding_box: tuple[float, float, float, float]
    row_count: int
    col_count: int
    headers: list[str]
    rows: list[list[str]]
    cells: list[TableCell] = Field(default_factory=list)
    table_type: str = Field(
        ..., description="SLA_PENALTY_MATRIX, ACADEMIC_SCORE_REPORT, FINANCIAL_INVOICE, or GENERAL_CONTRACTUAL"
    )
    title: str
    csv_data: str
    markdown_table: str
    regulatory_analysis: TableRegulatoryAnalysis | None = None


class DocumentTablesResponse(BaseModel):
    document_id: UUID
    filename: str
    total_tables: int
    tables: list[TableStructure]
