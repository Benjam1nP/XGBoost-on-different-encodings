"""Combine any encoding with any model and report AUC per prefix length.

Command line:
    python experiment.py                                     # Sepsis, every encoding x every model
    python experiment.py -d bpic2011 -e index -m xgboost
    python experiment.py --initial none                      # without initial (registration) data

From a notebook:
    from experiment import run
    from data import load_dataset
    ds = load_dataset("sepsis")
    auc = run(ds, "index", "random_forest")                  # pd.Series: prefix length -> AUC

Random forest and XGBoost are averaged over SEEDS (AUC per prefix length, mean over seeds).
"""
import argparse
import importlib
import time
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from data import LOADERS, add_common_features, load_dataset, prefix_log

ENCODINGS = {
    "last_state": "encoding.last_state",
    "aggregation": "encoding.aggregation",
    "index": "encoding.index",
}
MODELS = {
    "logistic_regression": "models.logistic_regression",
    "random_forest": "models.random_forest",
    "xgboost": "models.xgb",
}
SEEDS = (0, 1, 2)


def _load(registry, key):
    """Import a module lazily, so a missing package (e.g. xgboost) only matters if that model is used."""
    return importlib.import_module(registry[key]) if isinstance(registry[key], str) else registry[key]


def encode_prefixes(ds, enc, k, initial="all"):
    enc = _load(ENCODINGS, enc) if isinstance(enc, str) else enc
    p = prefix_log(ds, k)
    return add_common_features(enc.encode(p, ds), p, ds, initial)


def _split(ds, X):
    tr = X.index.isin(ds.train_ids)
    return X[tr], ds.labels[X.index[tr]], X[~tr], ds.labels[X.index[~tr]]


def _run_once(ds, enc, mdl, K, initial, seed):
    auc = {}
    if enc.BUCKETING == "single":
        # one model trained on the prefixes of all lengths stacked together
        X = pd.concat([encode_prefixes(ds, enc, k, initial) for k in K])
        Xtr, ytr, Xte, yte = _split(ds, X)
        prob = mdl.make_model(seed).fit(Xtr, ytr).predict_proba(Xte)[:, 1]
        for k in K:
            m = (Xte.prefix_len == k).values
            auc[k] = roc_auc_score(yte[m], prob[m])
    else:
        # one model per prefix length
        for k in K:
            X = encode_prefixes(ds, enc, k, initial)
            Xtr, ytr, Xte, yte = _split(ds, X)
            Xte = Xte.reindex(columns=Xtr.columns, fill_value=0)
            auc[k] = roc_auc_score(yte, mdl.make_model(seed).fit(Xtr, ytr).predict_proba(Xte)[:, 1])
    return pd.Series(auc)


def run(ds, enc, mdl, K=None, initial="all", seeds=SEEDS):
    """Train/evaluate one encoding+model combination. Returns AUC per prefix length."""
    enc = _load(ENCODINGS, enc) if isinstance(enc, str) else enc
    mdl = _load(MODELS, mdl) if isinstance(mdl, str) else mdl
    K = range(1, ds.max_k + 1) if K is None else K
    seeds = seeds if getattr(mdl, "SEEDED", False) else seeds[:1]
    s = pd.concat([_run_once(ds, enc, mdl, K, initial, sd) for sd in seeds], axis=1).mean(axis=1)
    s.name = f"{enc.NAME} + {mdl.NAME}"
    s.index.name = "prefix length"
    return s


def test_counts(ds, K=None):
    """Test cases and positives per prefix length (identical for every encoding)."""
    K = range(1, ds.max_k + 1) if K is None else K
    out = {}
    for k in K:
        ids = [i for i in prefix_log(ds, k).case_id.unique() if i not in ds.train_ids]
        out[k] = (len(ids), int(ds.labels[ids].sum()))
    return out


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
    ap.add_argument("-d", "--dataset", choices=list(LOADERS), default="sepsis")
    ap.add_argument("-e", "--encodings", nargs="+", choices=list(ENCODINGS), default=list(ENCODINGS))
    ap.add_argument("-m", "--models", nargs="+", choices=list(MODELS), default=list(MODELS))
    ap.add_argument("--initial", default="all", help="initial-data variant, e.g. all / none")
    ap.add_argument("--json", action="store_true", help="print one JSON object (used by the frontend)")
    a = ap.parse_args()

    ds = load_dataset(a.dataset)
    if a.json:
        import json
        counts = test_counts(ds)
        out = {"use_case_attributes": a.initial != "none", "runs": [],
               "test_cases": {k: n for k, (n, _) in counts.items()},
               "test_positives": {k: p for k, (_, p) in counts.items()}}
        for m in a.models:
            for e in a.encodings:
                t = time.time()
                s = run(ds, e, m, initial=a.initial)
                enc, mdl = _load(ENCODINGS, e), _load(MODELS, m)
                out["runs"].append({"encoding": e, "encoding_name": enc.NAME, "bucketing": enc.BUCKETING,
                                    "model": m, "model_name": mdl.NAME,
                                    "auc": {int(k): round(float(v), 4) for k, v in s.items()},
                                    "mean_auc": round(float(np.mean(s)), 4),
                                    "seconds": round(time.time() - t, 2)})
        print(json.dumps(out))
        raise SystemExit

    res = run_grid(ds, a.encodings, a.models, initial=a.initial)
    pd.set_option("display.width", 200)
    print("\n", res.round(3).to_string())
    print("\nmean AUC:\n", res.mean().round(3).sort_values(ascending=False).to_string())
