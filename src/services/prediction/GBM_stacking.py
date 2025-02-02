"""
@author: Louis Lebreton
GBMs stacking
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier


class GBMStacking(BaseEstimator, ClassifierMixin):
    """
    stacking de modeles gbm avec une regression logistique comme metaclassifier

    Args :
    - models_to_use : tuple contenant les noms des gbms à utiliser
    - catboost_parameters : dictionnaire des hyperparamètres  catboost
    - lightgbm_parameters : dictionnaire des hyperparamètres lightgbm
    - xgboost_parameters : dictionnaire des hyperparamètres  xgboost
    - logistic_parameters : dictionnaire des hyperparamètres regression logistique

    Return :
    - une instance entrainée du modele gbmstacking
    """
    def __init__(self, models_to_use=('catboost', 'lightgbm', 'xgboost'),
                 catboost_parameters={}, lightgbm_parameters={}, xgboost_parameters={}, 
                 logistic_regression_parameters={}, random_state=999):
        self.models_to_use = models_to_use
        self.catboost_parameters = catboost_parameters
        self.lightgbm_parameters = lightgbm_parameters
        self.xgboost_parameters = xgboost_parameters
        self.logistic_regression_parameters = logistic_regression_parameters
        self.random_state = random_state
        self.models = {}
        self.meta_classifier = LogisticRegression(**self.logistic_regression_parameters)
        self.classes_ = None

    def fit(self, X, y):
        # X, y = check_X_y(X, y,  force_all_finite=False)
        self.classes_ = np.unique(y)
        # modeles
        model_classes = {
            'catboost': CatBoostClassifier,
            'lightgbm': LGBMClassifier,
            'xgboost': XGBClassifier
        }
        # hyperparametres des modeles
        params = {
            'catboost': self.catboost_parameters,
            'lightgbm': self.lightgbm_parameters,
            'xgboost': self.xgboost_parameters
        }

        # entrainement des GBMs
        for model_name in self.models_to_use:
            model = model_classes[model_name](**params[model_name], random_state=self.random_state)
            model.fit(X, y)
            self.models[model_name] = model

        # récupération des probas comme features du metaclassifier
        meta_features = self._generate_meta_features(X)

        # fit du metaclassifier
        self.meta_classifier.fit(meta_features, y)
        return self

    def predict(self, X):
        # X = check_array(X,  force_all_finite=False)
        meta_features = self._generate_meta_features(X)
        return self.meta_classifier.predict(meta_features)

    def predict_proba(self, X):
        # X = check_array(X,  force_all_finite=False)
        meta_features = self._generate_meta_features(X)
        return self.meta_classifier.predict_proba(meta_features)

    def _generate_meta_features(self, X):
        meta_features = [model.predict_proba(X) for model in self.models.values()]
        return np.hstack(meta_features)


if __name__ == '__main__':
    
    # test sur une série labélisée
    df = pd.read_csv("data/AAPL_df_labeled_test.csv")
    
    # renommage du label bail de -1 à 2 pour être compatible avec le modèle
    df[df['label'] == -1]  = 2

    X = df[['lower_barrier_price', 'upper_barrier_price']]
    y = df['label']
    
    gbm_stacking_model = GBMStacking(models_to_use=('catboost', 'lightgbm', 'xgboost'),
                                 catboost_parameters={'iterations': 100, 'learning_rate': 0.1, 'depth': 3},
                                 lightgbm_parameters={'n_estimators': 100, 'learning_rate': 0.1, 'max_depth': 3},
                                 xgboost_parameters={'n_estimators': 100, 'learning_rate': 0.1, 'max_depth': 3},
                                logistic_regression_parameters={'C': 1.0, 'penalty': 'l2', 'multi_class': 'multinomial', 'solver': 'lbfgs'})
    gbm_stacking_model.fit(X, y)
    predictions = gbm_stacking_model.predict(X)