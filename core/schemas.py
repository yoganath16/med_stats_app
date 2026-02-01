from pydantic import BaseModel
from typing import Dict, List, Optional


class VariableProfile(BaseModel):
    type: str
    levels: Optional[List[str]] = None
    normality_p: Optional[float] = None
    normal: Optional[bool] = None
    missing_pct: float
    outliers_present: bool


class DataProfile(BaseModel):
    variables: Dict[str, VariableProfile]
    sample_size: int
    group_sizes: Optional[Dict[str, int]]
    study_design: str
    warnings: List[str]

class TestPlan(BaseModel):
    dependent_variable: str
    independent_variable: str
    selected_test: str
    assumptions: list[str]
    effect_size: str
    justification: str
    alpha: float = 0.05


class GroupStats(BaseModel):
    mean: float | None
    median: float | None
    sd: float | None
    n: int


class TestResults(BaseModel):
    test: str
    statistic: float
    p_value: float
    effect_size: float | None
    confidence_interval: list[float] | None
    group_statistics: dict[str, GroupStats] | None