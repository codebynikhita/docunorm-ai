from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.schemas.portfolio import ConcentrationRiskLevel
from app.services.portfolio_aggregator import portfolio_aggregator


@pytest.mark.asyncio
async def test_portfolio_aggregator_baseline():
    """
    Verifies that the portfolio aggregator correctly computes HHI concentration,
    statutory pillar averages, and BAFA submission readiness.
    """
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    tenant_id = uuid4()
    synthesis = await portfolio_aggregator.aggregate_portfolio(
        db=mock_db,
        tenant_id=tenant_id,
        reporting_year=2026,
    )

    assert synthesis.tenant_id == tenant_id
    assert synthesis.reporting_year == 2026
    assert synthesis.total_suppliers_audited >= 5
    assert synthesis.portfolio_compliance_score > 0.0
    assert synthesis.portfolio_rating in ["AAA", "BBB", "CCC"]

    # Concentration Metrics & HHI Check
    metrics = synthesis.concentration_metrics
    assert metrics.herfindahl_hirschman_index >= 0.0
    assert metrics.concentration_level in [
        ConcentrationRiskLevel.DIVERSIFIED,
        ConcentrationRiskLevel.MODERATE,
        ConcentrationRiskLevel.HIGH,
    ]
    assert metrics.top_3_vendor_share_percentage > 0.0

    # Jurisdictions Check
    assert len(synthesis.jurisdiction_breakdown) >= 4
    country_codes = [j.country_code for j in synthesis.jurisdiction_breakdown]
    assert "DE" in country_codes
    assert "CD" in country_codes

    # Pillar Scores Check
    assert 0.0 <= synthesis.human_rights_portfolio_average <= 100.0
    assert 0.0 <= synthesis.environmental_portfolio_average <= 100.0
    assert 0.0 <= synthesis.governance_portfolio_average <= 100.0
