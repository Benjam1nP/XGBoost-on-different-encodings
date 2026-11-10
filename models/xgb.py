"""XGBoost (gradient-boosted trees). Handles missing lab values natively."""
from xgboost import XGBClassifier

NAME = "XGBoost"


def make_model():
    return XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.8,
                         colsample_bytree=0.8, random_state=0, n_jobs=-1)
