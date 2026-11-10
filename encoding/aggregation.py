"""Aggregation encoding: counts of every activity/resource plus mean/max of the lab values (order is lost)."""
import pandas as pd

NAME = "aggregation"
BUCKETING = "single"   # fixed columns -> one model over all prefix lengths


def encode(p, ds):
    X = pd.crosstab(p.case_id, p.activity).reindex(columns=ds.acts, fill_value=0).add_prefix("count_")
    X = X.join(pd.crosstab(p.case_id, p.resource).reindex(columns=ds.res, fill_value=0).add_prefix("res_"))
    g = p.groupby("case_id")[ds.labs]
    return X.join(g.mean().add_suffix("_mean")).join(g.max().add_suffix("_max"))
