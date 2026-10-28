"""
Refresh the data embedded in docs/index.html (the web rebuild of Molecule)
from the Excel database.

It reproduces the aggregation done in Molecule/main.py: mean and standard
deviation of 'moy' per Molecule x Cell_line x Mode x Serum x ConcM, after
removing the 'gap' placeholder rows (value 50).

Usage, from the repository root:
    python tools/build_web_page.py FULL_DATABASE_exemple.xlsx
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'docs' / 'index.html'
CELL_LINES = ['HG5LN', 'HG5LN-hPPARa', 'HG5LN-mPPARa', 'HG5LN-hPPARg', 'HG5LN-mPPARg', 'HG5LN-zfPPARg',
              'HELN-xPPARg', 'HG5LN-hPXR', 'HG5LN-mPXR', 'HG5LN-zfPXR', 'ZFL-zfPXR']
FAMILIES = ['Pesticides_plate', 'GOLIATH', 'PPAR_lig', 'Bisphenols', 'Other']


def build(xlsx: Path) -> dict:
    df = pd.read_excel(xlsx, sheet_name='Data')
    excluded = pd.read_excel(xlsx, sheet_name='Excluded data')
    gaps = int((df.moy == 50).sum())
    d = df[(df.moy != 50) & df.ConcM.notna() & df.moy.notna()].copy()

    p = d.pivot_table('moy', ['Molecule', 'Cell_line', 'Mode', 'Serum', 'ConcM'],
                      aggfunc=['mean', 'std', 'count']).reset_index()
    p.columns = ['Molecule', 'Cell_line', 'Mode', 'Serum', 'ConcM', 'mean', 'sd', 'n']

    mols = sorted(p.Molecule.unique(), key=str.lower)
    modes = list(p.Mode.value_counts().index)
    sers = list(p.Serum.value_counts().index)
    concs = sorted(p.ConcM.unique())
    ix = lambda lst: {v: i for i, v in enumerate(lst)}
    im, ic, imo, iser, iconc = ix(mols), ix(CELL_LINES), ix(modes), ix(sers), ix(concs)

    rows = [[im[r.Molecule], ic[r.Cell_line], imo[r.Mode], iser[r.Serum], iconc[r.ConcM],
             round(r.mean, 4), None if pd.isna(r.sd) else round(r.sd, 4), int(r.n)]
            for r in p.itertuples(index=False)]

    flags = {}
    for f in FAMILIES:
        s = df.groupby('Molecule')[f].agg(lambda x: (x == True).any())  # noqa: E712
        flags[f] = [im[m] for m in s[s].index if m in im]

    dates = d.Date.astype(str).str.extract(r'^(\d{6})')[0].dropna()
    return dict(mols=mols, cls=CELL_LINES, modes=modes, sers=sers, concs=concs, rows=rows,
                colors={c: df[df.Cell_line == c].Color.iloc[0] for c in CELL_LINES}, flags=flags,
                stats=dict(raw=len(df), gaps=gaps, measures=len(d), excluded=len(excluded), points=len(p),
                           mols=len(mols), cls=len(CELL_LINES), dmin=dates.min(), dmax=dates.max(),
                           runs=int(d.Date.nunique()),
                           combos=int(p.groupby(['Molecule', 'Cell_line', 'Mode', 'Serum']).ngroups)))


if __name__ == '__main__':
    xlsx = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'FULL_DATABASE_exemple.xlsx'
    data = json.dumps(build(xlsx), separators=(',', ':'))
    html = PAGE.read_text(encoding='utf-8')
    start = html.index('const D = ') + len('const D = ')
    end = html.index(';\nconst SERIES')
    PAGE.write_text(html[:start] + data + html[end:], encoding='utf-8')
    print(f'Updated {PAGE.relative_to(ROOT)} from {xlsx.name}')
