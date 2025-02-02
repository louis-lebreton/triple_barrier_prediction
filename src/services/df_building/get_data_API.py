"""
@author: Louis Lebreton
Récupération de données via API
- Récupération des données BTC (API Coingecko)
- Récupération des données macroéconomique (API FRED)
"""
import requests
import pandas as pd
from datetime import datetime

def get_BTC_data(days:int = 30, interval:str = 'daily') -> pd.DataFrame:
    """
    récupération des données BTC depuis API Coingecko
    Args :
    - days (int): nombre de jours à récupérer
    - interval(str): intervalle des données
    Return:
    - df (pd.DataFrame)
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd", 
        "days": str(days),
        "interval": interval
    }
    response = requests.get(url, params=params)

    # traitement du json de reponse
    data = response.json()
    prices = data["prices"]
    market_caps = data["market_caps"]
    volumes = data["total_volumes"]
    
    # construction df données BTC
    df = pd.DataFrame({
        "date": [datetime.utcfromtimestamp(x[0] / 1000) for x in prices],
        "price": [x[1] for x in prices], # recuperation du 2eme element
        "market_cap": [x[1] for x in market_caps], # recuperation du 2eme element
        "volume": [x[1] for x in volumes] # recuperation du 2eme element
    })
    return df

def get_economic_data(series_id_list, api_key, start_date="2024-01-01", end_date="2025-01-01") -> pd.DataFrame:
    """
    récupération des données macroéconomique depuis API FRED sur une unique série
    (Federal Reserve Bank of St Louis)
    Les series_id sont à retrouver ici : https://fred.stlouisfed.org/tags/series?t=id&rt=id&ob=pv&od=desc

    Args :
    - series_id_list (list): liste de series id
    - api_key(str): clef API FRED obtenue par inscription sur le site https://fred.stlouisfed.org/docs/api/api_key.html
    - start_date(str): date départ
    - end_date(str): date fin
    
    Return:
    - df (pd.DataFrame) : df economic data
    """
    url = f"https://api.stlouisfed.org/fred/series/observations"
    df = pd.DataFrame()

    for series_id in series_id_list:
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date
        }
        
        try:
            # traitement du json de reponse
            response = requests.get(url, params=params)
            data = response.json()
            observations = data["observations"]
            
            df_serie = pd.DataFrame(observations)
            df_serie["date"] = pd.to_datetime(df_serie["date"])
            df_serie[series_id] = pd.to_numeric(df_serie["value"], errors="coerce")
            
        
            # construction df données FRED pour cette variable
            if df.empty:
                df = df_serie[["date", series_id]]
            else:
                df = pd.merge(df, df_serie[["date", series_id]], on="date", how="outer")
        except:
            continue
    
    return df

    
