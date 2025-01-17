"""
@author: Louis Lebreton

Endpoints pour récupérer :
Données économiques traitées
Données Bitcoin traitées
"""
import os

import pandas as pd
from fastapi import APIRouter, Query

from src.services.df_building.get_data_API import get_economic_data, get_BTC_data

router = APIRouter()

@router.get("/economic-data")
def fetch_economic_data(
    start_date: str = Query(..., description="Date de début au format YYYY-MM-DD"),
    end_date: str = Query(..., description="Date de fin au format YYYY-MM-DD")):
    """
    Endpoint pour obtenir les données économiques traitées
    """
    series_list= [
            'DFF', 'NFINCP', 'FINCP', 'DPRIME', 'DPCREDIT',
            'DTWEXBGS', 'CPIAUCSL', 'DGS3MO', 'DGS1', 'DGS30'
        ]
    # clef API FRED obtenue via https://fred.stlouisfed.org/docs/api/api_key.html
    FRED_API_KEY = os.getenv('FRED_API_KEY')
    if not FRED_API_KEY:
        return {"error": "La clé API FRED n'est pas configurée dans les variables d'environnement."}

    try:
        df_economic = get_economic_data(series_id_list=series_list, api_key=FRED_API_KEY, start_date=start_date, end_date=end_date)
        
        # prétraitement des données
        df_economic.index = pd.to_datetime(df_economic['date'])
        df_economic.drop(columns=['date'], inplace=True)
        df_economic['CPIAUCSL'] = df_economic['CPIAUCSL'].ffill()
        df_economic['FINCP'] = df_economic['FINCP'].bfill()
        df_economic['NFINCP'] = df_economic['NFINCP'].bfill()

        for col in df_economic.columns:
            df_economic[col] = df_economic[col].interpolate()
            df_economic[col] = df_economic[col].bfill()
            df_economic[col] = df_economic[col].ffill()

        # conversion en dict JSON
        result = df_economic.reset_index().to_dict(orient='records')
        return result

    except Exception as e:
        return {"error": str(e)}


@router.get("/bitcoin-data")
def fetch_btc_data(days: int = Query(..., description="days")):
    """
    Endpoint pour obtenir les données Bitcoin traitées
    """
    try:
        df_btc = get_BTC_data(days = days, interval = 'daily')
        
        # pct_change
        df_btc["increase_volume"] = (df_btc["volume"] - df_btc["volume"].shift(1)) / df_btc["volume"].shift(1)
        df_btc["increase_market_cap"] = (df_btc["market_cap"] - df_btc["market_cap"].shift(1)) / df_btc["market_cap"].shift(1)
        df_btc["increase_price"] = (df_btc["price"] - df_btc["price"].shift(1)) / df_btc["price"].shift(1)

        # moving average 7 semaines
        df_btc["MA7_volume"] = df_btc["volume"].rolling(window=7).mean()
        df_btc["MA7_market_cap"] = df_btc["market_cap"].rolling(window=7).mean()
        df_btc["MA7_price"] = df_btc["price"].rolling(window=7).mean()

        # moving average 1 mois
        df_btc["MA30_volume"] = df_btc["volume"].rolling(window=30).mean()
        df_btc["MA30_market_cap"] = df_btc["market_cap"].rolling(window=30).mean()
        df_btc["MA30_price"] = df_btc["price"].rolling(window=30).mean()

        # lags 1 semaine
        df_btc["volume_lag_7"] = df_btc["volume"].shift(7)
        df_btc["market_cap_lag_7"] = df_btc["market_cap"].shift(7)
        df_btc["price_lag_7"] = df_btc["price"].shift(7)

        # lags 1 mois
        df_btc["volume_lag_30"] = df_btc["volume"].shift(30)
        df_btc["market_cap_lag_30"] = df_btc["market_cap"].shift(30)
        df_btc["price_lag_30"] = df_btc["price"].shift(30)

        # date en index
        df_btc.index = df_btc['date']
        df_btc.drop(columns=['date'], inplace=True)
        df_btc = df_btc.fillna(0)
        
        # conversion en dict JSON
        result = df_btc.reset_index().to_dict(orient='records')
        return result

    except Exception as e:
        return {"error": str(e)}
    
