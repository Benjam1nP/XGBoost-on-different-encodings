"""Random forest. Missing lab values are imputed with the training median."""
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

NAME = "Random Forest"


def make_model():
    return make_pipeline(
        SimpleImputer(strategy="median", keep_empty_features=True),
        RandomForestClassifier(n_estimators=300, min_samples_leaf=3, random_state=0, n_jobs=-1),
    )
