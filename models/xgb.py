"""XGBoost (gradient-boosted trees). Handles missing numeric values natively."""
from xgboost import XGBClassifier

NAME = "XGBoost"
SEEDED = True


def make_model(seed=0):
    return XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.8,
                         colsample_bytree=0.8, random_state=seed, n_jobs=-1)
