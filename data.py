"""Shared data preparation for the Sepsis Cases log.

Loads the log, builds the ICU label, cuts every case before its first
`Admission IC`, removes discharge events, extracts static case attributes and
makes the temporal 80/20 train/test split. Encodings and models import from here.
"""
from dataclasses import dataclass, field

import pandas as pd

LABS = ["crp", "leucocytes", "lacticacid"]
STATIC_EXTRA = ["age", "disfuncorg", "hypotensie", "hypoxie", "infectionsuspected", "infusion", "oligurie"]


@dataclass
class Dataset:
    log: pd.DataFrame            # one row per event, with `pos` and `t_since_start_h`
    labels: pd.Series            # case_id -> 0/1 (reaches ICU)
    static: pd.DataFrame         # case_id -> static case attributes
    train_ids: set               # case_ids of the earliest 80% of cases
    acts: list = field(default_factory=list)
    res: list = field(default_factory=list)
    labs: list = field(default_factory=lambda: list(LABS))


def load_dataset(path="sepsis_cases.csv", train_share=0.8):
    log = pd.read_csv(path, parse_dates=["timestamp"])
    log = log.sort_values(["case_id", "timestamp"], kind="stable").reset_index(drop=True)

    # label + cut before the first Admission IC (the label must be predicted before it happens)
    log["label"] = log.groupby("case_id")["activity"].transform(lambda s: int((s == "Admission IC").any()))
    log["pos"] = log.groupby("case_id").cumcount()
    first_ic = log.case_id.map(log[log.activity == "Admission IC"].groupby("case_id")["pos"].min())
    log = log[~(first_ic.notna() & (log.pos >= first_ic))]
    # discharge events happen after the stay and would leak the outcome
    log = log[~log.activity.str.startswith("Release") & (log.activity != "Return ER")].copy()

    static_cols = [c for c in log.columns if c.startswith(("diagnostic", "sirscrit")) or c in STATIC_EXTRA]
    static = log.groupby("case_id")[static_cols].first().astype(float)
    labels = log.groupby("case_id")["label"].first()

    # temporal split: train on the patients who arrived first
    starts = log.groupby("case_id")["timestamp"].min().sort_values()
    train_ids = set(starts.index[: int(train_share * len(starts))])

    log["t_since_start_h"] = (log.timestamp - log.groupby("case_id").timestamp.transform("min")).dt.total_seconds() / 3600
    log["pos"] = log.groupby("case_id").cumcount()

    return Dataset(log=log, labels=labels, static=static, train_ids=train_ids,
                   acts=sorted(log.activity.unique()), res=sorted(log.resource.unique()))


def prefix_log(ds, k):
    """First k events of every case that has at least k events."""
    p = ds.log[ds.log.pos < k]
    n = p.groupby("case_id").size()
    return p[p.case_id.isin(n[n == k].index)]


def add_common_features(X, p, ds, use_case_attributes=True):
    """Static case attributes + elapsed time + prefix length, added to every encoding."""
    if use_case_attributes:
        X = X.join(ds.static)
    X["elapsed_h"] = p.groupby("case_id").t_since_start_h.last()
    X["prefix_len"] = p.groupby("case_id").size()
    return X.astype(float)
