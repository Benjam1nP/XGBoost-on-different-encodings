"""Shared data preparation for the two logs (Sepsis Cases, BPIC 2011).

Each loader returns a `Dataset` with one row per event (columns case_id, activity,
resource, timestamp, numeric attributes, `pos`, `t_since_start_h`), the case labels,
the initial (registration) data per case and a temporal 80/20 train/test split
(cases sorted by start time, first 80 % train).
"""
from dataclasses import dataclass, field

import pandas as pd

# ---------------------------------------------------------------- Sepsis
SEPSIS_LABS = ["crp", "leucocytes", "lacticacid"]
SEPSIS_SYMPTOMS = ["disfuncorg", "hypotensie", "hypoxie", "oligurie"]
SEPSIS_OTHER = ["infectionsuspected", "infusion"]

# ---------------------------------------------------------------- BPIC 2011
BPIC_CATEGORICAL = ["Diagnosis", "Treatment code", "Diagnosis code", "Specialism code"]


@dataclass
class Dataset:
    name: str
    log: pd.DataFrame            # one row per event, with `pos` and `t_since_start_h`
    labels: pd.Series            # case_id -> 0/1
    static: pd.DataFrame         # case_id -> initial data (numeric / one-hot "attr=value")
    initial_sets: dict           # variant name -> list of `static` columns
    train_ids: set               # case_ids of the earliest 80 % of cases
    max_k: int = 8
    acts: list = field(default_factory=list)
    res: list = field(default_factory=list)
    labs: list = field(default_factory=list)


def _finish(name, log, labels, static, initial_sets, labs, max_k, train_share):
    """Positions, elapsed time and the temporal split, shared by both loaders."""
    log = log.sort_values(["case_id", "timestamp"], kind="stable").reset_index(drop=True)
    log["pos"] = log.groupby("case_id").cumcount()
    log["t_since_start_h"] = (log.timestamp - log.groupby("case_id").timestamp.transform("min")).dt.total_seconds() / 3600
    starts = log.groupby("case_id")["timestamp"].min().sort_values()
    train_ids = set(starts.index[: int(train_share * len(starts))])
    return Dataset(name=name, log=log, labels=labels.loc[starts.index], static=static.loc[starts.index],
                   initial_sets=initial_sets, train_ids=train_ids, max_k=max_k,
                   acts=sorted(log.activity.unique()), res=sorted(log.resource.unique()), labs=labs)


def load_sepsis(path="sepsis_cases.csv", train_share=0.8):
    """Label = case contains Admission IC; cut before it; drop Release A-E and Return ER."""
    log = pd.read_csv(path, parse_dates=["timestamp"])
    log = log.sort_values(["case_id", "timestamp"], kind="stable").reset_index(drop=True)

    labels = log.groupby("case_id")["activity"].agg(lambda s: int((s == "Admission IC").any()))
    pos = log.groupby("case_id").cumcount()
    first_ic = log.case_id.map(pos[log.activity == "Admission IC"].groupby(log.case_id).min())
    log = log[~(first_ic.notna() & (pos >= first_ic))]
    log = log[~log.activity.str.startswith("Release") & (log.activity != "Return ER")].copy()

    diag = [c for c in log.columns if c.startswith("diagnostic")]
    sirs = [c for c in log.columns if c.startswith("sirscrit")]
    all_cols = ["age"] + diag + sirs + SEPSIS_SYMPTOMS + SEPSIS_OTHER
    static = log.groupby("case_id")[all_cols].first().astype(float)
    initial_sets = {
        "all": all_cols,
        "no_symptoms": [c for c in all_cols if c not in SEPSIS_SYMPTOMS],
        "age_diagnostic": ["age"] + diag,
        "none": [],
    }
    return _finish("sepsis", log, labels[static.index], static, initial_sets, list(SEPSIS_LABS), 8, train_share)


def _top(s, n):
    keep = s.value_counts().index[:n]
    return s.where(s.isin(keep), "other")


def load_bpic11(path="BPIC11_f1.csv", train_share=0.8):
    """Label = deviant. Rare activities / producer codes / categorical case attributes -> "other"."""
    raw = pd.read_csv(path, sep=";", low_memory=False)
    log = pd.DataFrame({
        "case_id": raw["case:concept:name"].astype(str),
        "activity": _top(raw["concept:name"].astype(str), 30),
        "resource": _top(raw["Producer code"].astype(str), 20),
        "timestamp": pd.to_datetime(raw["time:timestamp"]),
    })
    labels = (raw.groupby(log.case_id)["label"].first() == "deviant").astype(int)

    case = raw.groupby(log.case_id)[["Age"] + BPIC_CATEGORICAL].first()
    parts = [case[["Age"]].astype(float)]
    for c in BPIC_CATEGORICAL:
        parts.append(pd.get_dummies(_top(case[c].astype(str), 15), prefix=c, prefix_sep="=").astype(float))
    static = pd.concat(parts, axis=1)
    initial_sets = {"all": list(static.columns), "age": ["Age"], "none": []}
    return _finish("bpic2011", log, labels, static, initial_sets, [], 10, train_share)


LOADERS = {"sepsis": load_sepsis, "bpic2011": load_bpic11}


def load_dataset(name="sepsis", path=None):
    return LOADERS[name]() if path is None else LOADERS[name](path)


def prefix_log(ds, k):
    """First k events of every case that has at least k events."""
    p = ds.log[ds.log.pos < k]
    n = p.groupby("case_id").size()
    return p[p.case_id.isin(n[n == k].index)]


def add_common_features(X, p, ds, initial="all"):
    """Initial data (a variant name from ds.initial_sets) + elapsed time + prefix length."""
    cols = ds.initial_sets[initial]
    if cols:
        X = X.join(ds.static[cols])
    X["elapsed_h"] = p.groupby("case_id").t_since_start_h.last()
    X["prefix_len"] = p.groupby("case_id").size()
    return X.astype(float)
