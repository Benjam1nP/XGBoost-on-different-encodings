"""Compute every number shown on the seminar slides and write frontend/src/lib/slides.json.

    python slides.py            # ~ a few minutes; then open /slides in the frontend
    python screenshots.py       # PNGs into screenshots/
"""
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from data import load_dataset, prefix_log
from experiment import ENCODINGS, MODELS, SEEDS, _load, _split, encode_prefixes, run, test_counts

OUT = Path(__file__).parent / "frontend" / "src" / "lib" / "slides.json"
CASE = "A"


def _num(v):
    return None if pd.isna(v) else round(float(v), 4)


def models_x_encodings(ds):
    out = []
    for m in MODELS:
        for e in ENCODINGS:
            t = time.time()
            s = run(ds, e, m)
            out.append({"model": m, "encoding": e, "auc": {int(k): _num(v) for k, v in s.items()},
                        "mean_auc": _num(s.mean())})
            print(f"  {ds.name:9s} {m:20s} {e:12s} {s.mean():.3f} ({time.time() - t:.0f} s)")
    return out


def initial_variants(ds, variants):
    out = []
    for v in variants:
        s = run(ds, "last_state", "random_forest", initial=v)
        out.append({"variant": v, "auc": {int(k): _num(x) for k, x in s.items()}, "mean_auc": _num(s.mean())})
        print(f"  {ds.name:9s} random forest last state, initial={v:15s} {s.mean():.3f}")
    return out


def case_table(ds):
    ev = ds.log[ds.log.case_id == CASE].head(8)
    rows = [{"pos": int(r.pos) + 1, "activity": r.activity, "resource": r.resource,
             "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M"),
             **{l: _num(r[l]) for l in ds.labs}} for _, r in ev.iterrows()]
    return {"case_id": CASE, "label": int(ds.labels[CASE]), "events": rows,
            "n_events_after_cut": int((ds.log.case_id == CASE).sum())}


def encoded_case(ds, k=4):
    """Non-zero features of case A's k-event prefix in every encoding (event part + common part)."""
    initial_cols = set(ds.initial_sets["all"])
    out = {}
    for e in ENCODINGS:
        x = encode_prefixes(ds, e, k).loc[CASE]
        x = x[(x != 0) & x.notna()]
        feats = [{"feature": f, "value": _num(v)} for f, v in x.items() if f not in initial_cols]
        init = [{"feature": f, "value": _num(v)} for f, v in x.items() if f in initial_cols]
        out[e] = {"features": feats, "initial": init, "n_columns": int(len(encode_prefixes(ds, e, k).columns))}
    return out


def feature_importance(ds, top=10):
    """XGBoost, aggregation encoding, all initial data: gain importance, mean over seeds."""
    X = pd.concat([encode_prefixes(ds, "aggregation", k) for k in range(1, ds.max_k + 1)])
    Xtr, ytr, _, _ = _split(ds, X)
    mdl = _load(MODELS, "xgboost")
    imp = np.mean([mdl.make_model(s).fit(Xtr, ytr).feature_importances_ for s in SEEDS], axis=0)
    s = pd.Series(imp / imp.sum(), index=Xtr.columns).sort_values(ascending=False).head(top)
    return [{"feature": f, "importance": _num(v)} for f, v in s.items()]


def main():
    warnings.filterwarnings("ignore")
    t0 = time.time()
    sep = load_dataset("sepsis")
    bpic = load_dataset("bpic2011")
    counts = test_counts(sep)
    res = {
        "settings": {"seeds": list(SEEDS), "train_share": 0.8},
        "sepsis": {
            "case": case_table(sep),
            "encoded": encoded_case(sep),
            "models": models_x_encodings(sep),
            "initial": initial_variants(sep, ["all", "no_symptoms", "age_diagnostic", "none"]),
            "test_counts": [{"k": k, "cases": n, "positives": p} for k, (n, p) in counts.items()],
            "importance": feature_importance(sep),
        },
        "bpic2011": {
            "models": models_x_encodings(bpic),
            "initial": initial_variants(bpic, ["all", "age", "none"]),
        },
    }
    OUT.write_text(json.dumps(res, indent=1))
    print(f"wrote {OUT} in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
