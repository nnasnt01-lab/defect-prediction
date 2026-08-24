# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A Korean-language, day-by-day curriculum of Jupyter notebooks teaching data analysis and basic ML using pandas / matplotlib / scikit-learn, built around a semiconductor manufacturing dataset (SECOM). There is no application code, package, or test suite — the deliverable in each lab is a `.ipynb` notebook with real, executed outputs (not just source code).

## Environment

- Windows, PowerShell. Python 3.14.7 is the active interpreter (`python`), installed at `C:\Users\LG\AppData\Local\Programs\Python\Python314`. A legacy Python 3.8.7 also exists on the machine but is not on the priority PATH — don't target it.
- Installed packages: `pandas`, `matplotlib`, `scikit-learn` (numpy/scipy come along), plus `nbconvert`, `nbformat`, `nbclient`, `jupyter_client`, `ipykernel` — the latter group was added specifically so notebooks can be executed headlessly from the command line rather than only from the VS Code UI.

## Running a notebook (the core workflow)

Every lab's ask is "actually run it and show the real output" — never fabricate output text. Execute a notebook in place with:

```powershell
python -m jupyter nbconvert --to notebook --execute --inplace "day0X\labNN_xxx\labNN_xxx.ipynb"
```

- `nbconvert` sets the kernel's working directory to the notebook's own folder. This is why data loads inside notebooks use paths like `../../data/04_secom.csv` (from a `dayXX/labNN_xxx/` notebook up to the shared top-level `data/` folder) or `../../day02/lab06_clean-dataset/results/secom_clean.csv` (one lab reading another lab's saved output). Preserve this relative-path convention when adding load/save code.
- After executing, read back the actual output (via the `Read` tool on the `.ipynb`, or a short `python -c "import json; ..."` snippet reading `cells[i]['outputs']`) before reporting results — don't infer output from the code alone.
- Korean text in matplotlib charts renders as empty boxes unless a Hangul-capable font is set. Always include this before plotting in a new figure:
  ```python
  plt.rcParams["font.family"] = "Malgun Gothic"
  plt.rcParams["axes.unicode_minus"] = False
  ```

### Known nbformat bug when editing cells

If a cell is converted from an empty markdown cell into a code cell (e.g. `NotebookEdit` with `cell_type: "code"` on `edit_mode: "replace"`), the resulting JSON is missing the required `outputs`/`execution_count` fields and `nbconvert` fails validation with `'outputs' is a required property`. Fix before executing:

```powershell
python -c "
import json
path = 'PATH_TO_NOTEBOOK.ipynb'
nb = json.load(open(path, encoding='utf-8'))
for c in nb['cells']:
    if c['cell_type'] == 'code':
        c.setdefault('outputs', [])
        c.setdefault('execution_count', None)
json.dump(nb, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
"
```
Alternatively, avoid the bug entirely by using `edit_mode: "insert"` (creates a well-formed new cell) instead of converting an existing markdown cell's type.

## Repository structure

```
data/                          shared raw inputs, read-only, referenced by relative path — never edited in place
  04_secom.csv                 SECOM dataset: 1567 rows × 592 cols (measured_at, sensor_001..sensor_590, result [양품/불량])
  day01_bottling.csv           bottling line QC data: 4800 rows × 13 cols
day01/, day02/, day03/, ...    one folder per curriculum day
  labNN_kebab-case-name/       one folder per lab within a day
    labNN_snake_case_name.ipynb
    results/                  optional — a lab's own saved outputs (PNG charts, cleaned CSVs). Only exists where a lab produces artifacts; create it if a new lab needs one.
```

## Notebook template conventions

Each lab notebook follows a fixed teaching template — preserve its shape when adding cells rather than restructuring it:

- Markdown headers `## Step N. ...` divide the notebook into stages; a "용어 풀이" (terminology) table near the top defines vocabulary used in that lab.
- Bracketed blanks like `[센서]`, `[50]` inside markdown cells are fill-in-the-blank answers the learner (or an AI assistant on their behalf) completes — fill them in place rather than adding new prose cells.
- When the user asks to add a cell without specifying where, always append it as the new last cell of the notebook — do not search for or fill an earlier pre-placed blank cell under some `Step N` heading.
- Most notebooks end with a `---` + `## 직접 해보기 (도전)` (self-directed challenge) section; new exploratory work belongs there.
- Code comments, variable/column names, and all prose are written in Korean, matching the learner's own style — keep new code consistent with this (e.g. `센서`, `평균`, `표준편차`, `빈칸_비율` rather than English names).

## Cross-lab data pipeline

The labs are not independent — later notebooks reload files produced by earlier ones, so changing an earlier lab's output shape can break later ones:

1. **day02/lab04** — loads `data/04_secom.csv`, builds a control chart (mean ± 3·std) for one sensor, saves chart PNGs to its own `results/`.
2. **day02/lab05** — builds a full per-sensor diagnostic table (`sensor_diagnosis`: missing %, distinct value count, std, min/max) across all `sensor_*` columns.
3. **day02/lab06** — reloads raw data, re-derives the lab05 filtering (drop ≥50% missing, constant, or near-zero-std sensors → `df1`), drops sensors pairwise-correlated ≥0.9 keeping the one with fewer missing values (`df2`), ranks remaining sensors by correlation with the failure label, and saves reduced tables to `day02/lab06_clean-dataset/results/` (e.g. `secom_clean.csv`, `secom_clean_b.csv`) — these are the files day03 consumes.
4. **day03/lab07** — loads `day02/lab06_clean-dataset/results/secom_clean.csv`, median-imputes remaining sensor NaNs, encodes `result` → binary `불량여부`, and does a `stratify=y` `train_test_split` (test_size=0.2, random_state=42) into `X_train`/`X_test`/`y_train`/`y_test`.
5. **day03/lab08** — reproduces that same split as a baseline, compares a dummy "always predict 양품" classifier against trained models (logistic regression needs `StandardScaler` fit on `X_train` only, then applied to both splits; tree-based models don't need scaling).

When asked to extend this pipeline, match the established random_state (42), test_size (0.2), and stratify choices unless told otherwise, and never let a later lab silently mutate an earlier lab's already-saved CSV.
