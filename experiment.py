"""Combine any encoding with any model and report AUC per prefix length.

Command line:
    python experiment.py                                   # every encoding x every model
    python experiment.py -e aggregation index -m svm xgboost
    python experiment.py --no-case-attributes

From a notebook:
    from experiment import run, ENCODINGS, MODELS
    from data import load_dataset
    ds = load_dataset()
    auc = run(ds, ENCODINGS["index"], MODELS["svm"])        # pd.Series: prefix length -> AUC
"""
import argparse
import importlib
import time
import warnings

import pandas as pd
from sklearn.metrics import roc_auc_score

from data import add_common_features, load_dataset, prefix_log

ENCODINGS = {
    "last_state": "encoding.last_state",
    "aggregation": "encoding.aggregation",
    "index": "encoding.index",
}
MODELS = {
    "xgboost": "models.xgb",
    "svm": "models.svm",
    "logistic_regression": "models.logistic_regression",
    "random_forest": "models.random_forest",
}


def _load(registry, key):
    """Import a module lazily, so a missing package (e.g. xgboost) only matters if that model is used."""
    return importlib.import_module(registry[key]) if isinstance(registry[key], str) else registry[key]


def _encode(ds, enc, k, use_case_attributes):
    p = prefix_log(ds, k)
    return add_common_features(enc.encode(p, ds), p, ds, use_case_attributes)


def _split(ds, X):
    tr = X.index.isin(ds.train_ids)
    return X[tr], ds.labels[X.index[tr]], X[~tr], ds.labels[X.index[~tr]]


def run(ds, enc, mdl, K=range(1, 9), use_case_attributes=True):
    """Train/evaluate one encoding+model combination. Returns AUC per prefix length."""
    enc = _load(ENCODINGS, enc) if isinstance(enc, str) else enc
    mdl = _load(MODELS, mdl) if isinstance(mdl, str) else mdl
    auc = {}
    if enc.BUCKETING == "single":
        # one model trained on the prefixes of all lengths stacked together
        X = pd.concat([_encode(ds, enc, k, use_case_attributes) for k in K])
        Xtr, ytr, Xte, yte = _split(ds, X)
        prob = mdl.make_model().fit(Xtr, ytr).predict_proba(Xte)[:, 1]
        for k in K:
            m = (Xte.prefix_len == k).values
            auc[k] = roc_auc_score(yte[m], prob[m])
    else:
        # one model per prefix length
        for k in K:
            X = _encode(ds, enc, k, use_case_attributes)
            Xtr, ytr, Xte, yte = _split(ds, X)
            Xte = Xte.reindex(columns=Xtr.columns, fill_value=0)
            auc[k] = roc_auc_score(yte, mdl.make_model().fit(Xtr, ytr).predict_proba(Xte)[:, 1])
    s = pd.Series(auc, name=f"{enc.NAME} + {mdl.NAME}")
    s.index.name = "prefix length"
    return s


def run_grid(ds, encodings=ENCODINGS, models=MODELS, **kw):
    """Run every combination; returns a DataFrame (rows: prefix length, columns: encoding + model)."""
    cols = []
    for e in encodings:
        for m in models:
            t = time.time()
            cols.append(run(ds, e, m, **kw))
            print(f"{cols[-1].name:40s} mean AUC {cols[-1].mean():.3f}  ({time.time() - t:.1f} s)")
    return pd.concat(cols, axis=1)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--encodings", nargs="+", choices=list(ENCODINGS), default=list(ENCODINGS))
    ap.add_argument("-m", "--models", nargs="+", choices=list(MODELS), default=list(MODELS))
    ap.add_argument("--no-case-attributes", action="store_true")
    ap.add_argument("--data", default="sepsis_cases.csv")
    ap.add_argument("--json", action="store_true", help="print one JSON object (used by the frontend)")
    a = ap.parse_args()

    ds = load_dataset(a.data)
    if a.json:
        import json
        K = range(1, 9)
        use_attr = not a.no_case_attributes
        out = {"use_case_attributes": use_attr, "runs": [],
               "test_cases": {}, "test_positives": {}}
        for k in K:  # test-set size per prefix length (same for every encoding)
            ids = prefix_log(ds, k).case_id.unique()
            y = ds.labels[[i for i in ids if i not in ds.train_ids]]
            out["test_cases"][k], out["test_positives"][k] = int(len(y)), int(y.sum())
        for m in a.models:
            for e in a.encodings:
                t = time.time()
                s = run(ds, e, m, K=K, use_case_attributes=use_attr)
                enc, mdl = _load(ENCODINGS, e), _load(MODELS, m)
                out["runs"].append({"encoding": e, "encoding_name": enc.NAME, "bucketing": enc.BUCKETING,
                                    "model": m, "model_name": mdl.NAME,
                                    "auc": {int(k): round(float(v), 4) for k, v in s.items()},
                                    "mean_auc": round(float(s.mean()), 4),
                                    "seconds": round(time.time() - t, 2)})
        print(json.dumps(out))
        raise SystemExit

    res = run_grid(ds, a.encodings, a.models, use_case_attributes=not a.no_case_attributes)
    pd.set_option("display.width", 200)
    print("\n", res.round(3).to_string())
    print("\nmean AUC:\n", res.mean().round(3).sort_values(ascending=False).to_string())
