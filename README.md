# Oxide Symmetry, Stability & Solar Suitability

## What this project is

This project pulls oxide material records from the Materials Project API and asks a simple question: **does higher crystal symmetry tend to go along with higher thermodynamic stability?** It's built as a demonstration of honest, competent data handling on a real dataset — not a claim of novel materials-science discovery. Wherever a result could be over-read, this README says so explicitly.

Data is cleaned and unpacked via `data_utils.py`, which handles pulling the raw API records and flattening the nested symmetry field into usable columns (`crystal_system`, spacegroup symbol, etc.) alongside each material's stability measure (`energy_above_hull`) and other properties.

## Symmetry vs. stability, and where the pattern breaks (`symmetry_stability.py`)

For every chemical formula in the dataset, this groups all of its known polymorphs together and checks: is the *most stable* polymorph of that formula also the *most symmetric* one? When it isn't, that's flagged as an exception.

**Finding:** exceptions are effectively guaranteed *not* to occur when a formula only has one known polymorph (0% exception rate, by definition — there's nothing to disagree with). But as the number of polymorphs per formula increases, the exception rate climbs sharply, approaching 100% for formulas with many known polymorphs.

This isn't a data quality problem — it's a statistical consequence of the question being asked. With only two polymorphs, there's roughly a coin-flip chance the most-stable one and the most-symmetric one are the same row. With ten or twenty polymorphs, all of them would have to line up in the same order across two independent rankings (stability and symmetry) for no exception to occur — and that gets rarer the more competitors there are. So the honest reading here isn't "symmetry rarely predicts stability" — it's "single-polymorph or low-polymorph-count formulas show a fairly consistent match between symmetry and stability, and the apparent breakdown at higher polymorph counts is largely an artifact of how many ways there are to not perfectly align once more candidates are in play."

![Symmetry vs. stability distribution, log scale](assets/symmetry_stability_violin_log.png)

*The plot above shows the distribution of `energy_above_hull` at each symmetry rank (1 = Triclinic, 7 = Cubic), with the specific most-stable and most-symmetric material per formula marked. Y-axis is log-scaled since one outlier (~9.7 eV above hull) would otherwise flatten the rest of the distribution.*

**Honesty boundary:** this counts and describes exceptions found in the dataset. It does not explain *why* any individual exception occurs physically — that would require defect chemistry, phonon calculations, or other modeling this project doesn't attempt.

## A composite stability-symmetry score (`composite_score.py`)

To see whether combining stability and symmetry into one number reveals anything a single variable alone doesn't, this normalizes both `energy_above_hull` (inverted, so more stable = closer to 1) and symmetry rank (using the fixed 1–7 theoretical range, not just whatever range happens to appear in the pulled data) to a 0–1 scale, then averages them into a single composite score per material.

**Finding:** comparing the top-10 materials by composite score, stability alone, and symmetry alone showed almost no overlap between the symmetry-based ranking and either of the other two — 0 shared materials with stability alone, 0 shared with the composite score. Composite score and stability alone overlapped on 4 of 10.

The likely explanation: symmetry rank only has 7 possible values, so "top-10 by symmetry" is really just 10 arbitrary picks among however many hundreds or thousands of materials share the maximum rank (Cubic) — there's no way to distinguish further within that tie. `energy_above_hull`, by contrast, is continuous and close to unique per material, so its top-10 is a genuinely discriminating ranking. Comparing a near-arbitrary ranking against a highly discriminating one should be expected to produce low overlap, regardless of any real underlying relationship between symmetry and stability.

**Honesty boundary:** this composite score is an index defined for this project only — it has no established physical meaning and shouldn't be mistaken for a recognized materials science metric. Given the resolution mismatch above, the "symmetry half" of this score is also considerably coarser than the "stability half," which limits how much weight the composite score's symmetry contribution can be read as meaningful.

## Status

Done and verified: data cleaning, symmetry-vs-stability exception analysis, composite score construction and comparison.

(project not yet fully complete i still have stuff to do)