"""股权穿透相关 Pydantic schemas."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# 穿透链
# ---------------------------------------------------------------------------

class EquityChainResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chain_type: str
    chain_depth: int
    chain_data: Optional[dict[str, Any]] = None


# ---------------------------------------------------------------------------
# 受益所有人 (UBO)
# ---------------------------------------------------------------------------

class UBOResponse(BaseModel):
    name: str
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    ownership_percentage: Optional[float] = None
    control_path: list[str] = []


# ---------------------------------------------------------------------------
# 实际控制人
# ---------------------------------------------------------------------------

class ControllerResponse(BaseModel):
    name: str
    control_type: str  # direct / indirect
    control_percentage: Optional[float] = None
    control_path: list[str] = []


# ---------------------------------------------------------------------------
# 完整股权穿透详情
# ---------------------------------------------------------------------------

class EquityChainDetailResponse(BaseModel):
    upward_chains: list[EquityChainResponse] = []
    downward_chains: list[EquityChainResponse] = []
    ubos: list[UBOResponse] = []
    controller: Optional[ControllerResponse] = None
