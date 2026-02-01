import numpy as np
import pandas as pd
from scipy import stats
import pingouin as pg


def group_summary(df, dv, iv):
    summary = {}
    for g, sub in df.groupby(iv):
        s = sub[dv].dropna()
        summary[str(g)] = {
            "mean": float(s.mean()),
            "median": float(s.median()),
            "sd": float(s.std()),
            "n": int(len(s))
        }
    return summary


def run_mann_whitney(df, dv, iv):
    groups = [g[dv].dropna() for _, g in df.groupby(iv)]
    stat, p = stats.mannwhitneyu(groups[0], groups[1], alternative="two-sided")

    r = abs(stat) / np.sqrt(len(groups[0]) + len(groups[1]))

    return stat, p, r


def run_ttest(df, dv, iv):
    g1, g2 = [g[dv].dropna() for _, g in df.groupby(iv)]
    stat, p = stats.ttest_ind(g1, g2, equal_var=False)

    d = pg.compute_effsize(g1, g2, eftype="cohen")

    return stat, p, d


def run_anova(df, dv, iv):
    groups = [g[dv].dropna() for _, g in df.groupby(iv)]
    stat, p = stats.f_oneway(*groups)

    eta = pg.anova(data=df, dv=dv, between=iv)["np2"].values[0]

    return stat, p, eta


def run_kruskal(df, dv, iv):
    groups = [g[dv].dropna() for _, g in df.groupby(iv)]
    stat, p = stats.kruskal(*groups)

    return stat, p, None


def run_chi_square(df, dv, iv):
    table = pd.crosstab(df[dv], df[iv])
    stat, p, _, _ = stats.chi2_contingency(table)

    return stat, p, None


def run_correlation(df, dv, iv, method):
    x = df[dv]
    y = df[iv]

    if method == "pearson":
        r, p = stats.pearsonr(x, y)
    else:
        r, p = stats.spearmanr(x, y)

    return r, p, r

def execute_test(df, test_plan):
    dv = test_plan["dependent_variable"]
    iv = test_plan["independent_variable"]
    test = test_plan["selected_test"]

    group_stats = None
    effect = None
    ci = None

    if "Mann-Whitney" in test:
        stat, p, effect = run_mann_whitney(df, dv, iv)
        group_stats = group_summary(df, dv, iv)

    elif "t-test" in test:
        stat, p, effect = run_ttest(df, dv, iv)
        group_stats = group_summary(df, dv, iv)

    elif "ANOVA" in test:
        stat, p, effect = run_anova(df, dv, iv)
        group_stats = group_summary(df, dv, iv)

    elif "Kruskal" in test:
        stat, p, effect = run_kruskal(df, dv, iv)
        group_stats = group_summary(df, dv, iv)

    elif "Chi-square" in test:
        stat, p, effect = run_chi_square(df, dv, iv)

    elif "Pearson" in test:
        stat, p, effect = run_correlation(df, dv, iv, "pearson")

    elif "Spearman" in test:
        stat, p, effect = run_correlation(df, dv, iv, "spearman")

    else:
        raise ValueError(f"Unsupported test: {test}")

    return {
        "test": test,
        "statistic": float(stat),
        "p_value": float(p),
        "effect_size": None if effect is None else float(effect),
        "confidence_interval": ci,
        "group_statistics": group_stats
    }