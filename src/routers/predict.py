
"""
@author: Louis Lebreton

"""
from fastapi import FastAPI, Query, HTTPException
from typing import List
import pandas as pd
import joblib
import logging
from datetime import datetime

# configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/predict")
def predict(
    start_date: str = Query(..., description="Date de début au format YYYY-MM-DD"),
    end_date: str = Query(..., description="Date de fin au format YYYY-MM-DD"),
    risk_profile: str = Query(..., description="risk_profile")
) -> List[float]:
    """
    Prédit les résultats entre deux dates pour un profil de risque donné
    """
    try:
        # validation des dates
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if start_date >= end_date:
            raise ValueError("La date de début doit être antérieure à la date de fin.")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erreur de format de date : {e}")


    model_path = f"../models/gbm_stacking_model_{risk_profile}.pkl"
    try:
        #  chargement du modèle
        gbm_stacking_model = joblib.load(model_path)
        logger.info(f"Modèle '{model_path}' chargé avec succès.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement du modèle : {e}")

    data_path = f"../data/data_{risk_profile}.csv"
    try:
        # chargement des données
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
        logger.info(f"Données '{data_path}' chargées avec succès")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des données : {e}")

    # data preprocessing
    try:
        data['label'] = data['label'].replace(-1, 2)
        data_filtered = data[(data.index >= start_date) & (data.index <= end_date)]
        if data_filtered.empty:
            raise ValueError("Aucune donnée disponible pour l'intervalle de dates spécifié.")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la préparation des données : {e}")

    # prédiction
    try:
        predictions = gbm_stacking_model.predict(data_filtered)
        return predictions.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {e}")
