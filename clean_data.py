import pandas as pd
from data_utils import flatten_symmetry


def load_raw_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)


def clean_oxide_data(df: pd.DataFrame) -> pd.DataFrame:
    new_df = flatten_symmetry(df)

    numeric_cols = [
        "density",
        "energy_above_hull",
        "formation_energy_per_atom",
        "nsites",
        "band_gap",
        "volume",
    ]
    for col in numeric_cols:
        new_df[col] = pd.to_numeric(new_df[col], errors="coerce")

    def capitalize(row: str) -> str:
        return row.capitalize()

    new_df["crystal_system"] = new_df["crystal_system"].apply(capitalize)
    new_df["band_gap"] = new_df["band_gap"].mask(new_df["band_gap"] < 0)
    new_df["formation_energy_per_atom"] = new_df["formation_energy_per_atom"].mask(
        new_df["formation_energy_per_atom"] > 2
    )
    new_df = new_df.dropna()
    return new_df


def main():
    df = load_raw_data("oxide-symmetry-stability/oxides_raw_unclean.csv")
    print(df.describe())
    print(clean_oxide_data(df).describe())


if __name__ == "__main__":
    main()
# end main
