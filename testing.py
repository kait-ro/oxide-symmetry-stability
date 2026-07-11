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

    # blank canvas, 10in x 7in
    fig = plt.figure(figsize=(10, 7))
    # layout plan: 3 stacked rows, middle one (table) way bigger than header/footer, gap between rows so nothing crowds
    gs = fig.add_gridspec(3, 1, height_ratios=[1.6, 3, 1.1], hspace=0.4)

    # --- top row: title + the 3 stat callouts ---
    header_ax = fig.add_subplot(gs[0])  # claim row 0 as its own little axes
    header_ax.axis("off")  # don't want plot borders/ticks on a text-only panel
    header_ax.text(
        0.5, 0.88, "Solar-Relevance Screening",
        ha="center", fontsize=16, fontweight="bold",
        transform=header_ax.transAxes,  # coordinates are 0-1 relative to THIS panel, not the whole figure
    )
    header_ax.text(
        0.5, 0.65, f"Band gap range: {min_gap}–{max_gap} eV",
        ha="center", fontsize=11, color="dimgrey",
        transform=header_ax.transAxes,
    )

    # 3 stat cards side by side: big number on top, small grey label underneath
    stat_labels = ["Materials in range", "Mean composite score", "Flagged as exceptions"]
    stat_values = [f"{num_screened}", f"{mean_score:.3f}", f"{num_exceptions} / {num_screened}"]
    for i, (label, value) in enumerate(zip(stat_labels, stat_values)):
        x = 0.2 + i * 0.3  # spaces the 3 cards out evenly left to right (0.2, 0.5, 0.8)
        header_ax.text(x, 0.3, value, ha="center", fontsize=14, fontweight="bold", color="#2c5f8a", transform=header_ax.transAxes)
        header_ax.text(x, 0.05, label, ha="center", fontsize=9, color="dimgrey", transform=header_ax.transAxes)

    # --- middle row: the actual table ---
    table_ax = fig.add_subplot(gs[1])  # claim row 1
    table_ax.axis("off")
    table_ax.set_title("Top 10 by Composite Score", fontsize=12, fontweight="bold", pad=83)  # pad pushes title up so it doesn't touch the header row above it

    table = table_ax.table(
        cellText=top_by_composite.values,      # the actual numbers/text, row by row
        colLabels=top_by_composite.columns,     # header row text
        cellLoc="center",                       # center text inside each cell
        loc="center",                           # center the whole table inside its panel
    )
    table.auto_set_font_size(False)  # stop matplotlib from auto-shrinking font to fit, so I control size myself
    table.set_fontsize(9)
    table.scale(1, 1.8)  # stretch row height (keeps columns same width, makes rows taller/easier to read)

    # paint the header row: dark blue background, white bold text
    for col in range(len(top_by_composite.columns)):
        cell = table[0, col]  # row 0 = header row in matplotlib's table indexing
        cell.set_facecolor("#2c5f8a")
        cell.set_text_props(color="white", fontweight="bold")

    # paint the data rows: red highlight if it's an exception, otherwise alternate light grey/white stripes
    for row in range(1, len(top_by_composite) + 1):  # start at 1 since row 0 is the header
        is_exception = top_by_composite.iloc[row - 1]["Exception?"] == "Yes"  # -1 because iloc is 0-indexed but table rows start at 1
        for col in range(len(top_by_composite.columns)):
            cell = table[row, col]
            if is_exception:
                cell.set_facecolor("#fde2e2")  # pale red
            elif row % 2 == 0:
                cell.set_facecolor("#f2f2f2")  # light grey stripe on even rows only

    # --- bottom row: the honesty disclaimer, boxed so it stands out ---
    note_ax = fig.add_subplot(gs[2])  # claim row 2
    note_ax.axis("off")
    note_ax.text(
        0.5, 0.6,
        "Coarse screening proxy only, band gap here indicates \"electronically in the right range.\"\n"
        "It says nothing about photostability, degradation under illumination, device efficiency,\n"
        "or material lifetime, none of which this dataset measures.",
        ha="center", va="center", fontsize=8.5, style="italic", color="#555555",
        transform=note_ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#fff8e1", edgecolor="#e0c068"),  # yellow sticky-note box around the text
    )

    # save it as an actual image file, cropped tight to content, white background (not transparent)
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)  # close instead of show, don't want a window popping up every time this runs