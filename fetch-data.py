import os
from dotenv import load_dotenv
from mp_api.client import MPRester
import pandas as pd


def main() -> None:
    load_dotenv()

    api_key = os.environ.get("MY_API_KEY")
    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(
            chemsys="*-O",
            fields=[
                "formula_pretty",
                "band_gap",
                "formation_energy_per_atom",
                "energy_above_hull",
                "is_stable",
                "density",
                "volume",
                "nsites",
                "symmetry",
                "theoretical",
                "nelements",
                "elements",
                "material_id",
            ],
        )
        entry_rows = [doc.dict() for doc in docs]
        df = pd.DataFrame(entry_rows)
        df.to_csv("oxides_raw.csv", index=False)


if __name__ == "__main__":
    main()
