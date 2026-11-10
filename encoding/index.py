"""Index encoding: activity and resource at every position 1..k (lossless)."""
import pandas as pd

NAME = "index"
BUCKETING = "prefix"   # vector length grows with k -> one model per prefix length


def encode(p, ds):
    w = p.pivot(index="case_id", columns="pos", values=["activity", "resource"])
    w.columns = [f"{a}_{int(i) + 1}" for a, i in w.columns]
    return pd.get_dummies(w).astype(int)
