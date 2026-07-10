"""
im injecting random irregularities since the actual dataset from materials project is
pretty clean
Reads:  oxides_raw.csv
Writes: oxides_raw_unclean.csv
"""

import numpy as np
import pandas as pd
import ast

RNG_SEED = 42 # woahh hitchhiker's guide to the galaxy!?!


def inject_test_noise(input_path: str, output_path: str) -> None:
    rng = np.random.default_rng(RNG_SEED)
    df = pd.read_csv(input_path)

    # make 5% (0.05) of values just nan
    for column in ["band_gap", "density"]:
        number_missing = max(1, int(0.05 * len(df)))
        missing_index = rng.choice(df.index, size=number_missing, replace=False)
        df.loc[missing_index, column] = np.nan

    # make 3% of bandgap values negative (invalid so i should be able to clean it)
    number_negative = max(1, int(0.03 * len(df)))
    valid_index = df.index[df["band_gap"].notna()]
    negative_index = rng.choice(
        valid_index, size=min(number_negative, len(valid_index)), replace=False
    )
    df.loc[negative_index, "band_gap"] = -df.loc[negative_index, "band_gap"]
    # I must say I'm learning alot about creating noise esp seeding
    # making case changes so I can use pandas to correct them later
    case_variants = [str.upper, str.lower, str.title]
    number_recase = max(1, int(0.15 * len(df)))
    recase_index = rng.choice(df.index, size=number_recase, replace=False)
    docs = df["symmetry"].apply(ast.literal_eval)  # Series of dicts, one per row
    for index in recase_index:
        variant_function = case_variants[rng.integers(0, len(case_variants))]
        symmetry_dict = docs.loc[index]  # get this row's dict
        symmetry_dict["crystal_system"] = variant_function(
            str(symmetry_dict["crystal_system"])
        )
        df.loc[index, "symmetry"] = str(symmetry_dict)

    # duplicating a row every like 5-10 rows in the csv
    duplicate_rows = []
    i = 0
    while i < len(df):
        step = rng.integers(5, 11)
        i += step
        if i < len(df):
            duplicate_rows.append(df.iloc[[i]])
    if duplicate_rows:
        df = pd.concat([df] + duplicate_rows, ignore_index=True)
        df = df.sample(frac=1, random_state=RNG_SEED).reset_index(drop=True)
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    inject_test_noise(
        "oxide-symmetry-stability/oxides_raw.csv",
        "oxide-symmetry-stability/oxides_raw_unclean.csv",
    )
