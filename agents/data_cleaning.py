import pandas as pd


def clean_numeric_series(series: pd.Series):
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace("O", "0", regex=False)
        .str.replace("o", "0", regex=False)
    )

    numeric = pd.to_numeric(cleaned, errors="coerce")
    success_ratio = numeric.notna().mean()

    return numeric, success_ratio


def clean_dataset(df: pd.DataFrame):

    df_clean = df.copy()

    numeric_fixes = 0
    whitespace_fixed = 0
    missing_filled = 0

    # -------------------------
    # Normalize column names
    # -------------------------

    original_cols = df_clean.columns.tolist()
    df_clean.columns = (
        df_clean.columns.astype(str)
        .str.strip()
        .str.replace("\u00a0", " ")
    )

    if original_cols != df_clean.columns.tolist():
        whitespace_fixed += 1

    # -------------------------
    # Clean each column
    # -------------------------

    for col in df_clean.columns:

        series = df_clean[col]

        # Try numeric correction
        numeric_series, success_ratio = clean_numeric_series(series)

        # If most values convert → treat as numeric cleanup
        if success_ratio > 0.8:
            before_na = series.isna().sum()
            df_clean[col] = numeric_series
            after_na = df_clean[col].isna().sum()

            if not series.equals(numeric_series):
                numeric_fixes += 1

            if after_na > before_na:
                missing_filled += (after_na - before_na)

    # -------------------------
    # Build clean summary
    # -------------------------

    issues = []

    if numeric_fixes:
        issues.append(f"Corrected inconsistent numeric formatting in {numeric_fixes} column(s).")

    if whitespace_fixed:
        issues.append("Removed hidden whitespace and formatting artifacts.")

    if missing_filled:
        issues.append("Standardized missing values introduced during numeric conversion.")

    if not issues:
        issues.append("No major data quality issues detected.")

    return df_clean, issues