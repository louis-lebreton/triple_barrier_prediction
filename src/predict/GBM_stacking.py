
"""
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
    Stacking of GBMs with optimal hyperparameters (CatBoost, LightGBM, XGBoost)
    Example usage:
        - models_to_use=('catboost', 'xgboost')
        - models_to_use=('catboost', 'lightgbm', 'xgboost')
    """
    def __init__(self, models_to_use=('catboost', 'lightgbm', 'xgboost'), random_state=999):
        if len(models_to_use) < 2 or len(models_to_use) > 3:
            raise ValueError("It's a stacking of 2 or 3 differents GBM models")
        self.models_to_use = models_to_use
        self.random_state = random_state
        self.catboost_model = None
        self.lightgbm_model = None
        self.xgboost_model = None
        self.meta_classifier = None

    def fit(self, X, y):
        X, y = check_X_y(X, y)
        
        # fit the base models with externals hyperparameters
        if 'catboost' in self.models_to_use:
            self.catboost_model = CatBoostClassifier(iterations=500, learning_rate=0.1, depth=6, verbose=0, random_state=self.random_state)
            self.catboost_model.fit(X, y)

        if 'lightgbm' in self.models_to_use:
            self.lightgbm_model = LGBMClassifier(n_estimators=500, learning_rate=0.1, max_depth=6, random_state=self.random_state)
            self.lightgbm_model.fit(X, y)

        if 'xgboost' in self.models_to_use:
            self.xgboost_model = XGBClassifier(n_estimators=500, learning_rate=0.1, max_depth=6, use_label_encoder=False, eval_metric='mlogloss', random_state=self.random_state)
            self.xgboost_model.fit(X, y)
        
        # generate meta features
        meta_features = self._generate_meta_features(X)
        
        # fit the meta-classifier (softmax layer)
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
        
        # generate meta features from the probas predicted by the GBM models
        if self.catboost_model is not None:
            meta_features.append(self.catboost_model.predict_proba(X))
        
        if self.lightgbm_model is not None:
            meta_features.append(self.lightgbm_model.predict_proba(X))
    
        if self.xgboost_model is not None:
            meta_features.append(self.xgboost_model.predict_proba(X))
        
        print(meta_features)
        print('-')
        print(np.hstack(meta_features))
        return np.hstack(meta_features)


if __name__ == '__main__':
    
    df = pd.read_csv("data/df_labeled.csv")
    
    # temporaire
    df[df['label'] == -1]  = 2

    GBM_stacking = GBMStacking(models_to_use=('catboost', 'xgboost'))
    GBM_stacking.fit(df[['lower_barrier_price', 'upper_barrier_price']], df['label'])
    predictions = GBM_stacking.predict(df[['lower_barrier_price', 'upper_barrier_price']])
    