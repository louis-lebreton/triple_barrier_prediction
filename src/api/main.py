"""
@author: Louis Lebreton
API avec FastAPI qui prend en entrée une date et retourne une décision d'achat ou de vente
en fonction du profil de risque choisi
"""
import joblib
from fastapi import FastAPI, HTTPException
from datetime import datetime
from pydantic import BaseModel
from scrape_tweets import scrape_tweets_for_date
from sentiment_analysis import analyze_sentiment
from api.services import build_btc_df, build_economic_df, build_tweets_df
from prediction_model import predict

app = FastAPI()

# modèle de requête
class TradeRequest(BaseModel):
    date: str  # date au format 'YYYY-MM-DD'
    risk_profile: str # HRHP or LRLP
    cash: float

# modèle de réponses
class TradeResponse(BaseModel):
    date: str
    prediction: float
    details: dict

@app.post("/predict", response_model=TradeResponse)
async def predict_price(request: TradeRequest):
    try:
        # validation date
        date = datetime.strptime(request.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="La date doit être format 'YYYY-MM-DD'.")

    # Étape 1 : Récupération des données BTC et macroéconomiques
    btc_df = get_BTC_data(date)
    economic_df = get_economic_data(date)

    if not btc_df or not economic_df:
        raise HTTPException(status_code=404, detail="BTC or macro data not found for the given date.")
    
    # Étape 2 : Scraping des tweets
    tweets = scrape_tweets_for_date(request.date)
    if not tweets:
        raise HTTPException(status_code=404, detail="No tweets found for the given date.")

    # Étape 3 : Conversion des tweets en scores quantitatifs
    sentiment_score = analyze_sentiment(tweets)


    # Étape 4 : Prédiction
    gbm_stacking_model_loaded = joblib.load(f"data/gbm_stacking_model_{request.risk_profile}.pkl")
    print("modèle chargé avec succès")
    prediction = gbm_stacking_model_loaded.predict(X_test)

    return TradeResponse(
        date=request.date,
        prediction=prediction,
        details={
            "sentiment_score": sentiment_score,
            "btc_df": btc_df,
            "economic_df": economic_df,
        }
    )
