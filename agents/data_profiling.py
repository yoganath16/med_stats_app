import pandas as pd
import numpy as np
from scipy import stats
from core.schemas import DataProfile, VariableProfile


def detect_variable_type(series):
    # Try numeric conversion first
    s_num = pd.to_numeric(series, errors="coerce")
    numeric_ratio = s_num.notna().mean()

    # If not mostly numeric → categorical
    if numeric_ratio < 0.9:
        return "categorical"

    clean = s_num.dropna()

    unique_count = clean.nunique()
    n = len(clean)
    unique_ratio = unique_count / n

    # Very few unique numeric values → encoded category or ordinal
    if unique_count <= 10:
        return "categorical"

    # Discrete but many repeats (Likert-like)
    if unique_ratio < 0.05:
        return "categorical"

    return "continuous"



def profile_dataset(df: pd.DataFrame) -> DataProfile:
    variables = {}
    warnings = []

    for col in df.columns:
        s = df[col]
        missing_pct = s.isna().mean() * 100
        var_type = detect_variable_type(s)

        outliers_present = False
        normality_p = None
        normal = None
        levels = None

        if var_type == "continuous":
            clean = s.dropna()
            if len(clean) >= 3:
                normality_p = stats.shapiro(clean)[1]
                normal = bool(normality_p > 0.05)

            z = np.abs(stats.zscore(clean))
            outliers_present = bool((z > 3).any())


        if var_type == "categorical":
            levels = [str(x) for x in s.dropna().unique().tolist()]

        variables[col] = VariableProfile(
            type=var_type,
            levels=levels,
            normality_p=normality_p,
            normal=normal,
            missing_pct=missing_pct,
            outliers_present=outliers_present
        )

    return DataProfile(
        variables=variables,
        sample_size=len(df),
        group_sizes=None,
        study_design="observational",
        warnings=warnings
    )
