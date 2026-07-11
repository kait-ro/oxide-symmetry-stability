import pandas as pd
import matplotlib.pyplot as plt
import os
from data_utils import flatten_symmetry, symmetry_rank


def select_family(df: pd.DataFrame, formula: str) -> pd.DataFrame:
    family = df[df["formula_pretty"] == formula].copy()

    if family.empty:
        raise ValueError(
            f"No records found for formula '{formula}', check spelling/capitalization."
        )

    family["symmetry_rank"] = family["crystal_system"].apply(symmetry_rank)
    family = family.sort_values("symmetry_rank").reset_index(drop=True)
    return family


def family_stability_summary(family: pd.DataFrame) -> pd.DataFrame:
    summary = family[
        ["material_id", "crystal_system", "symmetry_rank", "energy_above_hull"]
    ].copy()
    summary = summary.sort_values("symmetry_rank").reset_index(drop=True)
    return summary


def stability_spread(family: pd.DataFrame) -> dict:
    most_stable_row = family.loc[family["energy_above_hull"].idxmin()]

    stats = {
        "num_polymorphs": len(family),
        "most_stable_crystal_system": most_stable_row["crystal_system"],
        "most_stable_energy_above_hull": most_stable_row["energy_above_hull"],
        "energy_above_hull_std": family["energy_above_hull"].std(),
        "energy_above_hull_range": family["energy_above_hull"].max()
        - family["energy_above_hull"].min(),
        "energy_above_hull_mean": family["energy_above_hull"].mean(),
    }
    return stats


def plot_family(
    family: pd.DataFrame,
    summary: pd.DataFrame,
    stats: dict,
    formula: str,
    save_path: str = None,
):
    fig, (ax, text_ax) = plt.subplots(
        2, 1, figsize=(8, 8), gridspec_kw={"height_ratios": [3, 2]}
    )
    #Note for later, gridspeck_kw is letting me override the grid ratio for the plot-axis (ax, text_ax) here. so instead of being 1:1 It's 3:2
    #Other controls are "width_ratios", "hspace", "wspace"
    ax.plot(
        family["symmetry_rank"],
        family["energy_above_hull"],
        "o-",
        color="grey",
        alpha=0.6,
        label=formula,
    )

    most_stable_idx = family["energy_above_hull"].idxmin()
    ax.scatter(
        family.loc[most_stable_idx, "symmetry_rank"],
        family.loc[most_stable_idx, "energy_above_hull"],
        color="red",
        s=100,
        marker="*",
        zorder=3,
        label="Most stable polymorph",
    )

    ax.set_xlabel("Symmetry rank (1=Triclinic ... 7=Cubic)")
    ax.set_ylabel("Energy above hull (eV/atom), lower = more stable")
    ax.set_title(f"Polymorph family: {formula}")
    ax.set_xticks(range(1, 8))
    ax.legend()

    # text shit
    summary_text = summary.to_string(index=False)
    stats_text = "\n".join(f"{key}: {value}" for key, value in stats.items())
    full_text = f"{summary_text}\n\n{stats_text}"

    text_ax.axis("off")
    text_ax.text(
        0.01,
        0.99,
        full_text,
        transform=text_ax.transAxes,
        fontsize=8,
        family="monospace",
        verticalalignment="top",
    )

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.close(
        fig
    )  # close (THANK GOD this exists otherwise my pc would be opening 639 windows)


def main(path, formula="TiO2"):
    df = flatten_symmetry(pd.read_csv(path))
    output_dir = "oxide-symmetry-stability/assets"
    os.makedirs(output_dir, exist_ok=True)

    if formula == "everything":
        all_formulas = df["formula_pretty"].unique()
        print(f"Generating plots for {len(all_formulas)} formulas...")

        results = {}
        skipped = []

        for f in all_formulas:
            try:
                family = select_family(df, f)
                summary = family_stability_summary(family)
                stats = stability_spread(family)
                plot_family(
                    family, summary, stats, f, save_path=f"{output_dir}/family_{f}.png"
                )
                results[f] = (family, summary, stats)
            except Exception as e:
                skipped.append((f, str(e)))

        print(f"Done. {len(results)} plots generated, {len(skipped)} skipped.")
        if skipped:
            print("Skipped formulas (first 10):")
            for f, err in skipped[:10]:
                print(f"  {f}: {err}")

        return results

    else:
        family = select_family(df, formula)
        summary = family_stability_summary(family)
        stats = stability_spread(family)

        print(f"--- Polymorph family summary: {formula} ---")
        print(summary.to_string(index=False))
        print()
        for key, value in stats.items():
            print(f"{key}: {value}")

        plot_family(
            family,
            summary,
            stats,
            formula,
            save_path=f"{output_dir}/family_{formula}.png",
        )

        return family, summary, stats


if __name__ == "__main__":
    # main(path=r"oxide-symmetry-stability\oxides_raw.csv", formula="TiO2")
    main(path=r"oxide-symmetry-stability\oxides_raw.csv", formula="everything")
