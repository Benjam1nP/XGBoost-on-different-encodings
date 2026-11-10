"""Support vector machine (RBF kernel). Needs imputed and standardised features.

probability=True enables predict_proba (Platt scaling), so the SVM plugs into
the same AUC evaluation as the other models.
"""
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

NAME = "SVM"


def make_model():
    return make_pipeline(
        SimpleImputer(strategy="median", keep_empty_features=True),
        StandardScaler(),
        SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=0),
    )
