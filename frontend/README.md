# Frontend

SvelteKit app with one tab per model (XGBoost, random forest, logistic regression, SVM).
Each tab runs that model with all three encodings and shows mean AUC per encoding,
a chart of AUC per prefix length, a generated description and the full result table.
Styling follows `STYLE.md` (Firn tokens in `src/routes/layout.css`).

## Run

```
npm install
npm run dev -- --open
```

Clicking **Run** calls `POST /api/run`, which runs `python experiment.py --json -m <model>`
in the parent `Demo/` folder. Python needs `pandas scikit-learn xgboost`.

Optional environment variables:

- `PYTHON`: Python executable (default `python` on Windows, `python3` elsewhere)
- `DEMO_DIR`: folder that contains `experiment.py` (default `..`)

## Files

- `src/routes/+page.svelte`: tabs
- `src/lib/components/ModelPanel.svelte`: run button, KPI tiles, chart, description, table
- `src/lib/components/AucChart.svelte`: SVG line chart with crosshair tooltip
- `src/lib/experiment.ts`: model/encoding metadata and the description generator
- `src/routes/api/run/+server.ts`: spawns the Python experiment
