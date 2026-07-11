# solar_filter.py
import pandas as pd
from data_utils import flatten_symmetry
from symmetry_stability import exception_detection
from composite_score import normalize_column, symmetry_rank_normalized, compose_score
import matplotlib.pyplot as plt



def filter_by_band_gap(df: pd.DataFrame, min_gap: float, max_gap: float) -> pd.DataFrame:
    return df[(df["band_gap"] >= min_gap) & (df["band_gap"] <= max_gap)].copy()


def cross_reference_solar_candidates(solar_subset: pd.DataFrame, exception_df: pd.DataFrame) -> pd.DataFrame:
    exception_by_formula = (
        exception_df.groupby("formula_name")["formula_is_exception"].first().reset_index().rename(columns={"formula_name": "formula_pretty"})
    )
    merged = solar_subset.merge(exception_by_formula, on="formula_pretty", how="left")
    return merged


def solar_screening_summary(merged: pd.DataFrame, min_gap: float, max_gap: float):
    print(f"--- Solar-relevance screening: band_gap in [{min_gap}, {max_gap}] eV ---")
    print(f"Materials in range: {len(merged)}")
    
    if len(merged) == 0:
        print("No materials found in this band gap range.")
        return

    print(f"Mean composite_score of screened materials: {merged['composite_score'].mean():.3f}")
    print(f"Materials also flagged as formula exceptions: {merged['formula_is_exception'].sum()} / {len(merged)}")

    top_by_composite = merged.nlargest(10, "composite_score")[
        ["material_id", "formula_pretty", "band_gap", "composite_score", "formula_is_exception"]
    ]
    print("\nTop 10 screened materials by composite score:")
    print(top_by_composite.to_string(index=False))

    print(
        "\nNote: this is a coarse screening proxy only. Band gap here indicates "
        "'electronically in the right range' it says nothing about photostability, "
        "degradation under illumination, device efficiency, or material lifetime, "
        "none of which this dataset measures."
    )

def save_screening_report(merged: pd.DataFrame, min_gap: float, max_gap: float, save_path: str):
    top_by_composite = merged.nlargest(10, "composite_score")[
        ["material_id", "formula_pretty", "band_gap", "composite_score", "formula_is_exception"]
    ].copy()

    #fancy text stuff and true = yes, false = no
    top_by_composite["band_gap"] = top_by_composite["band_gap"].round(3) #round cuts off decimal places
    top_by_composite["composite_score"] = top_by_composite["composite_score"].round(3)
    top_by_composite["formula_is_exception"] = top_by_composite["formula_is_exception"].map({True: "Yes", False: "No"})
    top_by_composite.columns = ["Material ID", "Formula", "Band Gap (eV)", "Composite Score", "Exception?"] #changing column names

    num_screened = len(merged)
    mean_score = merged["composite_score"].mean() if num_screened > 0 else float("nan")
    num_exceptions = merged["formula_is_exception"].sum() if num_screened > 0 else 0 #thanks python for being able to sum bool under the hood!

    fig = plt.figure(figsize=(10, 7))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.6, 3, 1.1], hspace=0.4)
    #top row with title and the 3 stats
    header_ax = fig.add_subplot(gs[0]) 
    header_ax.axis("off")
    header_ax.text(
        0.5, 0.88, "Solar-Relevance Screening",
        ha="center", fontsize=16, fontweight="bold",
        transform=header_ax.transAxes, #coordinates are 0-1 relative to THIS panel, not the whole figure
    )
    header_ax.text(
        0.5, 0.65, f"Band gap range: {min_gap}–{max_gap} eV",
        ha="center", fontsize=11, color="dimgrey",
        transform=header_ax.transAxes,
    )
    # 3 stat cards side by side, big number on top, small grey label underneath
    stat_labels = ["Materials in range", "Mean composite score", "Flagged as exceptions"]
    stat_values = [f"{num_screened}", f"{mean_score:.3f}", f"{num_exceptions} / {num_screened}"]
    for i, (label, value) in enumerate(zip(stat_labels, stat_values)):
        x = 0.2 + i * 0.3 # spaces the 3 cards out evenly left to right (0.2, 0.5, 0.8)
        header_ax.text(x, 0.3, value, ha="center", fontsize=14, fontweight="bold", color="#2c5f8a", transform=header_ax.transAxes)
        header_ax.text(x, 0.05, label, ha="center", fontsize=9, color="dimgrey", transform=header_ax.transAxes)

    # --- Table panel ---
    table_ax = fig.add_subplot(gs[1])
    table_ax.axis("off")
    table_ax.set_title("Top 10 by Composite Score", fontsize=12, fontweight="bold", pad=83)
    # pad pushes title up so it doesn't touch the header row above it, if someone reads this and has a better way, PLEASE let me know.
    table = table_ax.table(
        cellText=top_by_composite.values,
        colLabels=top_by_composite.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False) #auto font size, bad. me set font size, good
    table.set_fontsize(9) 
    table.scale(1, 1.8)

    # fancy coloring
    for col in range(len(top_by_composite.columns)):
        cell = table[0, col]
        cell.set_facecolor("#2c5f8a")
        cell.set_text_props(color="white", fontweight="bold")

    # even fancier coloring
    for row in range(1, len(top_by_composite) + 1):
        is_exception = top_by_composite.iloc[row - 1]["Exception?"] == "Yes"
        for col in range(len(top_by_composite.columns)):
            cell = table[row, col]
            if is_exception:
                cell.set_facecolor("#fde2e2")
            elif row % 2 == 0:
                cell.set_facecolor("#f2f2f2")

    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig) #once again, thank god this exists.

def main(path, min_gap=1.1, max_gap=3.0):
    df = flatten_symmetry(pd.read_csv(path))

    df["stability_norm"] = normalize_column(df, "energy_above_hull", invert=True)
    df["symmetry_norm"] = symmetry_rank_normalized(df)
    df["composite_score"] = compose_score(df["stability_norm"], df["symmetry_norm"], method="average")

    exception_df = exception_detection(df)

    solar_subset = filter_by_band_gap(df, min_gap, max_gap) 
    merged = cross_reference_solar_candidates(solar_subset, exception_df)

    solar_screening_summary(merged, min_gap, max_gap)
    save_screening_report(merged, min_gap, max_gap, save_path="oxide-symmetry-stability/assets/solar_screening_report.png")

    return merged


if __name__ == "__main__":
    main(path=r"oxide-symmetry-stability\oxides_raw.csv", min_gap=1.1, max_gap=3.0)