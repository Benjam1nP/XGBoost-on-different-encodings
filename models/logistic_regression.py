"""Logistic regression. Needs imputed and standardised features."""
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

NAME = "Logistic Regression"
SEEDED = False   # deterministic, one run is enough


def make_model(seed=0):
    return make_pipeline(
        SimpleImputer(strategy="median", keep_empty_features=True),
        StandardScaler(),
        LogisticRegression(C=0.1, max_iter=2000),
    )
