import os
from dotenv import load_dotenv
from mp_api.client import MPRester
import pandas as pd  

def main() -> None:
    load_dotenv()  # reads .env and puts values into os.environ

    api_key = os.environ.get("MY_API_KEY")
    with MPRester(api_key) as mpr:
        docs = mpr.materials.summary.search(
        chemsys="*-O",              # must contain oxygen
        fields=[
            "formula_pretty",        # 1. chemical formula
            "band_gap",               # 2. electronic band gap
            "formation_energy_per_atom",  # 3. stability measure
            "energy_above_hull",      # 4. distance from most stable form
            "is_stable",              # 5. True/False stability flag
            "density",                # 6. mass per volume
            "volume",                 # 7. unit cell volume
            "nsites",                 # 8. number of atoms in unit cell
            "symmetry",               # 10. spacegroup symbol/number (nested object)
            "theoretical",            # 11. experimentally confirmed or predicted
            "nelements",              # 12. number of distinct elements
            "elements",               # 13. list of constituent elements
            "material_id",            # 15. unique MP identifier (always worth keeping) 
        ],
    )
        entry_rows = [doc.dict() for doc in docs]
        df = pd.DataFrame(entry_rows)
        df.to_csv("oxides_raw.csv", index=False)


if __name__ == "__main__":
    main()

