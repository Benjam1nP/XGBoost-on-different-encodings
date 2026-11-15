# Chart instructions for Claude Code: PPM seminar talk (HSG style)

## Goal
Generate the 7 data charts that are still dashed **CHART · PLACEHOLDER** boxes in `PPM_Talk_HSG.pptx`. The conceptual graphics (pipeline, prefixes, encodings, models, evaluation) are already in the deck as shapes, so **do not** redraw those.

Write one script, `Demo/make_charts.py`, that reads the numbers and saves every chart to `Demo/charts/` as both **SVG** and **PNG at 300 dpi**. Never type numbers in by hand: every value and every annotation must come from the data, so the charts stay correct when the experiments are rerun.

## Data source
- **Main source:** `Demo/frontend/src/lib/slides.json`, written by `Demo/slides.py`. Do **not** rerun the experiments unless this file is missing.
  - `sepsis.models` / `bpic2011.models`: list of `{model, encoding, auc{k: value}, mean_auc}`
    - models: `logistic_regression`, `random_forest`, `xgboost`
    - encodings: `last_state`, `aggregation`, `index`
  - `sepsis.initial`: variants `all`, `no_symptoms`, `age_diagnostic`, `none`
  - `bpic2011.initial`: variants `all`, `age`, `none` (random forest, last state, AUC per prefix length k)
  - `sepsis.test_counts`: `{k, cases, positives}`
  - `sepsis.importance`: top 10 `{feature, importance}` (XGBoost, aggregation, share of total gain)
  - `sepsis.encoded[enc].n_columns`: vector length at k = 4
- **Only for chart G6:** compute the extra numbers with the existing functions in `Demo/data.py` and `Demo/experiment.py` (`load_dataset`, `prefix_log`, `encode_prefixes`, `ds.train_ids`). Do not write new experiment logic.

## Style (HSG template)
| Role | Hex | Use |
|---|---|---|
| HSG green (accent1) | `#00802F` | main series, highlights, “all data” line, random forest |
| Dark green (dk2) | `#0A5F2D` | titles inside charts, annotation text |
| Teal (accent4) | `#73A5AF` | second series (XGBoost, “without symptom flags”) |
| Sand, darkened | `#A8956E` | third series (“age + diagnostic”, “only age”) |
| Grey | `#555555` | fourth series / baseline (logistic regression, “no initial data”), axis labels |
| Light grey | `#EEEEEE` | noise band, gridlines `#E0E0E0` |
| Light green | `#CCE6D5` | background highlight (registration features) |
| Text | `#1A1A1A` | tick labels and data labels |

Rules:
- **Background:** white `#FFFFFF`. No chart border, no top or right spine, light horizontal gridlines only.
- **Font:** `Gill Sans Nova` if it is installed, otherwise `Arial`. Sizes are for the export size given per chart:
  - axis labels 14 pt
  - tick labels 12 pt
  - direct labels 13 pt
  - annotations 12 pt, colour `#0A5F2D`
- **No chart titles.** The slide title and subtitle already say what the chart shows.
- **Never rely on colour alone.** Label every series directly at the line end or next to the dots (no legend box). Also vary the marker (circle / square / triangle / diamond) or the line style (solid / dashed).
- Do not use the template’s red `#EB6969` or yellow `#FFF04B`.
- AUC axes are always labelled “AUC” and show 2 decimals. Prefix-length axes are labelled “Prefix length k (events observed)”.
- **Export size = the placeholder size** (inches) given below, so the image can replace the placeholder 1:1.

## The charts

### G1: Sepsis, models × encodings → slide “Results: Sepsis I” (size 7.9 × 4.4 in)
- **Chart type:** dot plot of `mean_auc`.
  - Rows: three groups by encoding (last state, aggregation, index), one row per model inside each group.
  - X-axis: AUC from 0.70 to 0.85.
- **Markers and colours:**
  - random forest: `#00802F`, circle
  - XGBoost: `#73A5AF`, square
  - logistic regression: `#555555`, triangle
- **Labels:** write each value at its dot (e.g. “0.79”).
- **Noise band:** a light grey `#EEEEEE` vertical band behind the dots. It spans ±0.025 around the median of all nine means and is labelled “within noise (~20 ICU test patients per k)”.
- **Index group:** draw it at 60% opacity, so the eye goes to the outlier only if it is one.

### G2: Sepsis, registration data removed → slide “Results: Sepsis II” (size 7.9 × 4.4 in)
- **Chart type:** line chart of AUC against prefix length k = 1…8, using `sepsis.initial`.
- **Lines:**
  - `all`: `#00802F`, solid, 3 pt, circles, label “All registration data”
  - `no_symptoms`: `#73A5AF`, solid, squares, label “Without symptom flags”
  - `age_diagnostic`: `#A8956E`, solid, diamonds, label “Only age + diagnostics”
  - `none`: `#555555`, dashed, triangles, label “No registration data”
- **Guessing line:** a horizontal dotted line at 0.5, labelled “guessing (0.5)”.
- **Y-axis:** 0.40–0.90.
- **Annotations:**
  - At k = 1, the gap between `all` and `none`, e.g. “0.79 vs 0.49 at the first event”.
  - The peak of `none`, e.g. “peak 0.74 at k = 5”.
  - Compute both values from the data.

### G3: BPIC 2011, models × encodings → slide “Results: BPIC 2011”, left (size 6.0 × 3.6 in)
- Same design as G1, using `bpic2011.models`.
- X-axis: 0.70–0.95. Band ±0.025 around the median.
- Label the logistic regression + index outlier, e.g. “0.76”.

### G4: BPIC 2011, initial data removed → slide “Results: BPIC 2011”, right (size 6.0 × 3.6 in)
- Same design as G2, using `bpic2011.initial`, k = 1…10.
- **Lines:**
  - `all`: `#00802F`, label “All initial data”
  - `age`: `#A8956E`, label “Only age”
  - `none`: `#555555`, dashed, label “No initial data”
- **Guessing line:** at 0.5.
- **Below 0.5:** shade the area below 0.5 very lightly (`#EEEEEE`) and annotate the first k where `none` < 0.5, e.g. “below guessing from k = 5”.
- **Y-axis:** 0.35–0.95.

### G5: Backup “reliability”: test cases per prefix length (size 7.9 × 4.4 in)
- **Chart type:** bars for k = 1…8 from `sepsis.test_counts`.
- **Bars:**
  - Full bar = `cases`, in `#EEEEEE` with `#555555` labels.
  - Overlaid bar = `positives` (ICU), in `#00802F`.
- **Labels:** both numbers on every bar.
- **Reference line:** a dashed horizontal line at the BPIC 2011 average positives per k, labelled “BPIC 2011 ≈ N positives per k”. Compute N with `test_counts` on the BPIC dataset. If that is slow, use 107 and add a comment in the script.

### G6: Backup “index encoding”: why index overfits (size 7.9 × 4.4 in)
- **Chart type:** two side-by-side bar panels for Sepsis with **no initial data**, k = 1…8.
  - **Left panel:** number of feature columns per encoding (last state, aggregation, index). Get it from `encode_prefixes(ds, enc, k, initial="none").shape[1]`.
  - **Right panel:** training cases available per model. For last state and aggregation this is all prefixes of all lengths (one model). For index it is the training prefixes of length k only (one model per k).
- **Colours:** last state `#00802F`, aggregation `#73A5AF`, index `#555555`.
- **Takeaway label:** “index: most columns, fewest cases per model”.

### G7: Backup “feature importance” (size 7.9 × 4.4 in)
- **Chart type:** horizontal bars of the top 10 from `sepsis.importance`, sorted from largest at the top. Values are shown as % with 1 decimal.
- **Colours:** registration features (any feature that is in `ds.initial_sets["all"]`, or simply not prefixed by `count_`, `res_`, `crp_`, `leucocytes_`, `lacticacid_`, `elapsed`, `prefix`) are `#00802F`. Event features are `#555555`.
- **Tags:** add the word tag “registration” or “event” after each label, so the split does not rely on colour.

## Optional: put the charts into the deck
If `PPM_Talk_HSG.pptx` is in the Seminar folder, use python-pptx to make a copy `PPM_Talk_HSG_charts.pptx`. On each target slide:
1. Delete the dashed placeholder rectangle and its text box. The text box text starts with “CHART · PLACEHOLDER”.
2. Insert the PNG at exactly the rectangle’s position and size.

Placeholder positions (inches, x / y / w / h):

| Chart | Position |
|---|---|
| G1, G2, G5, G6, G7 | 0.52 / 2.05 / 7.9 / 4.4 |
| G3 | 0.52 / 2.05 / 6.0 / 3.6 |
| G4 | 6.815 / 2.05 / 6.0 / 3.6 |

Keep everything else on the slides unchanged.

## Done when
- [ ] 7 charts × (SVG + PNG) are in `Demo/charts/`, named `G1_sepsis_models.png` … `G7_feature_importance.png`.
- [ ] Every number in a label or annotation matches `slides.json`. Print a short table of the values used.
- [ ] Every series has a direct label and a distinct marker or line style.
- [ ] You opened each PNG and checked it: no overlapping labels, nothing cut off, readable at slide size.
