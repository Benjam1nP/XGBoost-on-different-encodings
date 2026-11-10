# XGBoost-on-different-encodings

Predictive process monitoring on the *Sepsis Cases* log: predict ICU admission from a running case,
comparing prefix encodings and classifiers (pipeline after Teinemaa et al., 2019).

```
data.py          load log, label, cut before Admission IC, static attributes, temporal 80/20 split
encoding/        last_state.py, aggregation.py, index.py      -> encode(p, ds)
models/          xgb.py, svm.py, logistic_regression.py, random_forest.py   -> make_model()
experiment.py    combine any encoding with any model, AUC per prefix length
```

```
pip install pandas scikit-learn xgboost matplotlib
python experiment.py                                      # all 12 combinations
python experiment.py -e aggregation index -m svm xgboost  # pick some
python experiment.py --no-case-attributes
```

In a notebook:
```python
from data import load_dataset
from experiment import run
ds = load_dataset()
run(ds, "index", "random_forest")   # pd.Series: prefix length -> AUC
```

New encoding: add a module to `encoding/` with `NAME`, `BUCKETING` (`"single"` or `"prefix"`) and `encode(p, ds)`,
then register it in `ENCODINGS` in `experiment.py`. New model: add a module to `models/` with `NAME` and `make_model()`
and register it in `MODELS`.
