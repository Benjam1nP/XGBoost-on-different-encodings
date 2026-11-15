"""Last-state encoding: only the latest event (activity, resource, last observed numeric values)."""
import pandas as pd

NAME = "last state"
BUCKETING = "single"   # fixed columns -> one model over all prefix lengths


def encode(p, ds):
    last = p.groupby("case_id").last()
    X = pd.get_dummies(last[["activity", "resource"]]).reindex(
        columns=[f"activity_{a}" for a in ds.acts] + [f"resource_{r}" for r in ds.res], fill_value=0)
    if ds.labs:
        # last observed value of each numeric attribute (groupby.last skips missing values)
        X = X.join(p.groupby("case_id")[ds.labs].last().add_prefix("last_"))
    return X
