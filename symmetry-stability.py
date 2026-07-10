import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_utils import flatten_symmetry, symmetry_rank


# using symmetry_rank to check if most stable = most symmetric or not
def exception_detection(df: pd.DataFrame):
    formula_grouped_data = df.groupby("formula_pretty")
    records = []
    for formula_name, group_df in formula_grouped_data:
        group_df = group_df.copy()
        group_df["symmetry_rank"] = group_df["crystal_system"].apply(symmetry_rank)

        stable_index = group_df["energy_above_hull"].idxmin()
        symmetric_index = group_df["symmetry_rank"].idxmax()
        is_exception = stable_index != symmetric_index

        for index, row in group_df.iterrows():
            records.append(
                {
                    "formula_name": formula_name,
                    "symmetry_rank": row["symmetry_rank"],
                    "energy_above_hull": row["energy_above_hull"],
                    "is_most_stable": index == stable_index,
                    "is_most_symmetric": index == symmetric_index,
                    "formula_is_exception": is_exception,
                }
            )
    """most stable = low energy_above_hull
           most symmetric = rank fom symmetry_ranking
           exception if the above two are not same row"""
    exception_df = pd.DataFrame(records)
    return exception_df


def plotting_function(exception_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    # distribution of stability at each rank
    sns.violinplot(
        x="symmetry_rank",
        y="energy_above_hull",
        data=exception_df,
        color="lightgrey",
        inner="quartile",
        cut=0,
        ax=ax,
    )

    most_stable = exception_df[exception_df["is_most_stable"]]
    most_symmetric = exception_df[exception_df["is_most_symmetric"]]

    ax.scatter(
        most_stable["symmetry_rank"] - 1,  # shift because otherwise it would be at 0
        most_stable["energy_above_hull"],
        marker="v",
        color="blue",
        label="Most stable per formula",
        s=30,
        alpha=0.6,
        edgecolors="black",
        linewidths=0.3,
        zorder=3,
    )
    ax.scatter(
        most_symmetric["symmetry_rank"] - 1,
        most_symmetric["energy_above_hull"],
        marker="^",
        color="red",
        label="Most symmetric per formula",
        s=30,
        alpha=0.6,
        edgecolors="black",
        linewidths=0.3,
        zorder=3,
    )

    ax.set_xlabel("Symmetry rank (1=Triclinic ... 7=Cubic)")
    ax.set_ylabel("Energy above hull (eV/atom), lower = more stable")
    ax.set_title("Symmetry vs. Stability — distribution per symmetry rank")
    ax.legend()
    ax.set_yscale("log")

    plt.tight_layout()
    plt.savefig(
        r"oxide-symmetry-stability\assets\symmetry_stability_violin_log.png",
        dpi=150,
    )
    plt.show()


def exception_summary(exception_df: pd.DataFrame):
    formula_level = exception_df.groupby("formula_name")["formula_is_exception"].first()

    total_formulas = formula_level.shape[0]
    exception_formulas = formula_level.sum()  # true = 1 so w
    exception_rate = exception_formulas / total_formulas

    print(f"Total formulas checked: {total_formulas}")
    print(f"Formulas flagged as exceptions: {exception_formulas}")
    print(f"Exception rate: {exception_rate:.2%}")

    poly_counts = exception_df.groupby("formula_name").size()
    formula_summary = pd.DataFrame(
        {
            "is_exception": formula_level,
            "num_polymorphs": poly_counts,
        }
    )

    print("\nException rate by number of polymorphs in the formula group:")
    print(
        formula_summary.groupby("num_polymorphs")["is_exception"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "exception_rate", "count": "num_formulas"})
    )

    return formula_summary


def main(path):
    df = flatten_symmetry(pd.read_csv(path))
    exception_df = exception_detection(df)
    formula_summary = exception_summary(exception_df)
    print(formula_summary)
    plotting_function(exception_df)


if __name__ == "__main__":
    main(path=r"oxide-symmetry-stability\oxides_raw.csv")
# end main
