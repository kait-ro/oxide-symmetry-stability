import pandas as pd
import ast


def flatten_symmetry(df: pd.DataFrame) -> pd.DataFrame:
    docs = df["symmetry"].apply(ast.literal_eval)
    symmetry_df = docs.apply(pd.Series)
    df = pd.concat([df, symmetry_df], axis=1)
    df = df.drop(columns=["symmetry"])
    return df.drop(columns=["fields_not_requested", "unavailable_fields"])


def symmetry_rank(crystal_system: str) -> int:
    lookup = crystal_system.capitalize()
    symmetry_ranking = {
        "Triclinic": 1,
        "Monoclinic": 2,
        "Orthorhombic": 3,
        "Tetragonal": 4,
        "Trigonal": 5,
        "Hexagonal": 6,
        "Cubic": 7,
    }
    return symmetry_ranking[lookup]