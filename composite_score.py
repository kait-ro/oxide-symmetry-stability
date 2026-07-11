import pandas as pd
from data_utils import flatten_symmetry, symmetry_rank


def normalize_column(df: pd.DataFrame, column: str, invert: bool = False) -> pd.Series:
    col = df[column]
    col_min = col.min()
    col_max = col.max()
    normalized = (col - col_min) / (col_max - col_min)
    if invert:
        normalized = 1 - normalized
    return normalized


def symmetry_rank_normalized(df: pd.DataFrame) -> pd.Series:
    df = df.copy()
    df["symmetry_rank_raw"] = df["crystal_system"].apply(symmetry_rank)
    normalized = (df["symmetry_rank_raw"] - 1) / (7 - 1)
    return normalized


def compose_score(
    stability_norm: pd.Series, symmetry_norm: pd.Series, method: str = "average"
) -> pd.Series:
    if method == "average":
        return (stability_norm + symmetry_norm) / 2
    elif method == "product":
        return stability_norm * symmetry_norm
    elif method == "weighted":
        return 0.5 * stability_norm + 0.5 * symmetry_norm
    else:
        raise ValueError(f"Unknown method: {method}")


def compare_rankings(df: pd.DataFrame, top_n: int = 10):
    cols_to_show = [
        "material_id",
        "formula_pretty",
        "stability_norm",
        "symmetry_norm",
        "composite_score",
    ]

    top_composite = df.nlargest(top_n, "composite_score")[cols_to_show]
    top_stability = df.nlargest(top_n, "stability_norm")[cols_to_show]
    top_symmetry = df.nlargest(top_n, "symmetry_norm")[cols_to_show]

    print(f"--- Top {top_n} by composite score ---")
    print(top_composite.to_string(index=False))
    print(f"\n--- Top {top_n} by stability alone ---")
    print(top_stability.to_string(index=False))
    print(f"\n--- Top {top_n} by symmetry alone ---")
    print(top_symmetry.to_string(index=False))

    ids_composite = set(top_composite["material_id"])
    ids_stability = set(top_stability["material_id"])
    ids_symmetry = set(top_symmetry["material_id"])

    print(
        f"\nOverlap composite vs stability: {len(ids_composite & ids_stability)} / {top_n}"
    )
    print(
        f"Overlap composite vs symmetry: {len(ids_composite & ids_symmetry)} / {top_n}"
    )
    print(
        f"Overlap stability vs symmetry: {len(ids_stability & ids_symmetry)} / {top_n}"
    )


def main(path):
    df = flatten_symmetry(pd.read_csv(path))

    print(f"Crystal systems present: {sorted(df['crystal_system'].unique())}\n")

    df["stability_norm"] = normalize_column(df, "energy_above_hull", invert=True)
    df["symmetry_norm"] = symmetry_rank_normalized(df)
    df["composite_score"] = compose_score(
        df["stability_norm"], df["symmetry_norm"], method="average"
    )
    compare_rankings(df, top_n=200)
    return df


if __name__ == "__main__":
    main(path=r"oxide-symmetry-stability\oxides_raw.csv")
