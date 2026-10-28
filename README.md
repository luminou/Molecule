# Molecule

An interactive dashboard for exploring a toxicology screening database: 179 chemicals tested on 11 luciferase reporter cell lines (PPARα, PPARγ and PXR from human, mouse, zebrafish and Xenopus), in agonist and antagonist mode, with and without serum.

I wrote it in Python with **pandas** and **Bokeh** in 2019–2020, while working as a research scientist, so that colleagues could filter a ~30,000-row Excel sheet and read dose–response curves in a few clicks instead of building pivot charts by hand.

**Live case study and web rebuild:** https://luminou.github.io/Molecule/
**All data projects:** https://luminou.github.io/Data_Projects/

---

## What the app does

1. **Loads** the lab database (`FULL_DATABASE.xlsx`, sheet `Data`) into a pandas DataFrame.
2. **Aggregates** replicate runs with one `pivot_table`: mean and standard deviation of the normalised luciferase activity (`moy`) per molecule × cell line × mode × serum × concentration.
3. **Cleans** the table for plotting: placeholder "gap" rows (value 50) become `NaN`, concentrations become ordered labels, and error bounds (mean ± SD) are precomputed.
4. **Filters** with four checkbox groups (cell line, mode, serum, molecule). Each group keeps a boolean mask, and a row is displayed only when all four masks are `True`.
5. **Displays** a bar chart, a line chart, hover tooltips, SD whiskers and a data table that share one `ColumnDataSource`, plus a button that downloads the current selection as CSV (written in JavaScript with `CustomJS`).

## How to read the data

| Column | Meaning |
|---|---|
| `Molecule` | The chemical tested (pesticides, bisphenols, PFAS, drugs, reference ligands). |
| `Cell_line` | Reporter cell line. **HG5LN** is the control line: it emits light whatever the receptor, so it should stay at 100 %. A drop on HG5LN means fewer living cells, i.e. toxicity at that dose. |
| `Mode` | `Ago`: does the chemical activate the receptor? `Antago`: does it block a reference activator? An antagonist drop is only meaningful if HG5LN stays at 100 % at the same doses. |
| `Serum` | Whether the exposure medium contained serum. |
| `ConcM` | Concentration in mol/L. |
| `moy` | Normalised luciferase activity for one run (mean of the wells). |

## Repository structure

```
Molecule/
├── Molecule/
│   ├── main.py               # the Bokeh server app
│   └── templates/index.html  # page template used by bokeh serve
├── FULL_DATABASE_exemple.xlsx  # example database (sheets: Data, Excluded data, Pivot chart)
├── start.bat                 # opens an Anaconda prompt on Windows
├── README.txt                # original setup notes (French)
├── docs/                     # GitHub Pages site: case study + interactive rebuild
│   └── index.html
└── tools/
    ├── build_web_page.py     # refreshes the data embedded in docs/index.html
    └── page_template.html    # source of the web page (data placeholder: __DATA__)
```

## Running the original app

Requirements: Python 3 with pandas, NumPy and Bokeh (the code targets the Bokeh 1.x API, e.g. `WidgetBox` and `plot_width`).

```bash
conda install bokeh pandas numpy openpyxl
bokeh serve Molecule --show
```

The app opens at `http://localhost:5006/Molecule`. Edit the path in `Molecule/main.py` so that `pd.read_excel` points to your copy of the database. Stop the server with `Ctrl+C`.

## Updating the web page

The web page embeds the aggregated data (about 12,600 dose points), so it runs without a server.

```bash
python tools/build_web_page.py FULL_DATABASE_exemple.xlsx
```

## Original app vs. web rebuild

The page in `docs/` rebuilds the dashboard in plain JavaScript and SVG so it can be used in a browser without Python.

**Kept from the Python app**
- Four checkbox filters combined with AND logic, exactly as in `main.py`.
- Mean ± SD across runs from the same `pivot_table` grouping.
- Bar view, line view, hover tooltips and a data table that stay in sync.
- Exporting the current selection as CSV (copied to the clipboard on the web page).

**From the "possible improvements" list at the end of `main.py`**
- **One line per series.** The original drew a single line through every selected point; the rebuild gives each molecule × cell line × mode × serum combination its own line.
- **Select all / none** for cell lines, and a search box for the molecule list.
- **Hill model fit** (4-parameter logistic, least squares) with an EC50 per curve, on by default.
- **True log-scale** concentration axis instead of text labels.

**Added for the web page**
- An overview heatmap (molecule × cell line, strongest agonist response), where hatched cells mark conditions that were never tested and pale blue marks tested-but-inactive. Clicking a cell loads it in the dashboard.

## Author

Clémentine Garoche
