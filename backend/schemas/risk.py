"""风险扫描相关 Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# 单条风险
# ---------------------------------------------------------------------------

class RiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    risk_type: str
    risk_level: str
    risk_detail: Optional[dict[str, Any]] = None
    detected_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# 风险汇总
# ---------------------------------------------------------------------------

class RiskSummaryResponse(BaseModel):
    total_risks: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    lawsuits: list[RiskResponse] = []
    dishonest: list[RiskResponse] = []
    restrictions: list[RiskResponse] = []
    penalties: list[RiskResponse] = []


# ---------------------------------------------------------------------------
# 分页风险列表
# ---------------------------------------------------------------------------

class RiskListResponse(BaseModel):
    items: list[RiskResponse] = []
    total: int = 0
