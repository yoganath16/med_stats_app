import matplotlib.pyplot as plt
import seaborn as sns


def boxplot_by_group(df, dv, iv):
    fig, ax = plt.subplots(figsize=(6,4))
    sns.boxplot(data=df, x=iv, y=dv, ax=ax)
    ax.set_title(f"{dv} by {iv}")
    return fig


def distribution_plot(df, dv):
    fig, ax = plt.subplots(figsize=(6,4))
    sns.histplot(df[dv].dropna(), kde=True, ax=ax)
    ax.set_title(f"Distribution of {dv}")
    return fig