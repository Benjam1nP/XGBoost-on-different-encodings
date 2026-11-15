"""Random forest. Missing numeric values are imputed with the training median."""
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

NAME = "Random Forest"
SEEDED = True


def make_model(seed=0):
    return make_pipeline(
        SimpleImputer(strategy="median", keep_empty_features=True),
        RandomForestClassifier(n_estimators=300, min_samples_leaf=5, random_state=seed, n_jobs=-1),
    )
