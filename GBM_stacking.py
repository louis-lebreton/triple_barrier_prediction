
"""
GBM Stacking
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array

from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier


class GBMStacking(BaseEstimator, ClassifierMixin):
    """
    Stacking of GBMs already trained and optimized
    models (tuple) = (catboost_model, lightgbm_model, xgboost_model)
    exemple : (catboost_model, None, xgboost_model)
    """
    def __init__(self, models=None, random_state=999):
        if models is None or len(models) < 2 or  len(models) > 3:
            raise ValueError("you must provide a tuple of 2 or 3 GBM models")
        self.random_state = random_state
        self.catboost_model = models[0]
        self.lightgbm_model = models[1]
        self.xgboost_model = models[2]
        self.meta_classifier = None

    def fit(self, X, y):
        X, y = check_X_y(X, y)
                
        # construct meta features
        meta_features = self._generate_meta_features(X)
        
        # fit the meta-classifier
        self.meta_classifier = LogisticRegression(multi_class='multinomial', random_state=self.random_state)
        self.meta_classifier.fit(meta_features, y)
        
        return self

    def predict(self, X):
        X = check_array(X)
        meta_features = self._generate_meta_features(X)
        return self.meta_classifier.predict(meta_features)
    
    def predict_proba(self, X):
        X = check_array(X)
        meta_features = self._generate_meta_features(X)
        return self.meta_classifier.predict_proba(meta_features)
    
    def _generate_meta_features(self, X):
        meta_features = []
        
        # models chosen
        if self.catboost_model is not None:
            meta_features.append(self.catboost_model.predict_proba(X))
        
        if self.lightgbm_model is not None:
            meta_features.append(self.lightgbm_model.predict_proba(X))
    
        if self.xgboost_model is not None:
            meta_features.append(self.xgboost_model.predict_proba(X))
        
        # concatenation of the meta features
        if meta_features:
            meta_features = np.hstack(meta_features)
        else:
            raise ValueError("0 models selected for stacking")
        
        return meta_features