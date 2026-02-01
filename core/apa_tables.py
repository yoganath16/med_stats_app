import pandas as pd


def format_group_table(group_stats: dict):

    if not group_stats:
        return pd.DataFrame()

    rows = []

    for group, stats in group_stats.items():
        rows.append({
            "Group": group,
            "n": stats["n"],
            "Mean": round(stats["mean"], 2) if stats["mean"] is not None else "",
            "SD": round(stats["sd"], 2) if stats["sd"] is not None else "",
            "Median": round(stats["median"], 2) if stats["median"] is not None else ""
        })

    return pd.DataFrame(rows)


def format_test_table(results):

    return pd.DataFrame([{
        "Test": results["test"],
        "Statistic": round(results["statistic"], 3),
        "p": f"{results['p_value']:.3f}".replace("0.", "."),
        "Effect size": (
            f"{results['effect_size']:.2f}"
            if results.get("effect_size") is not None else ""
        )
    }])
