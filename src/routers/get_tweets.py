"""
@author: Louis Lebreton

"""
import os
import datetime
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor

from src.services.df_building.get_sentiment_score import tweets_to_sentiment_scores
from src.services.df_building.get_data_scraping import scrape_tweets_one_account

app = FastAPI()

class TweetRequest(BaseModel):
    tweets: List[str]

@app.get("/scrape-tweets")
def scrape_tweets(
    start_date: str = Query(..., description="Date de début au format YYYY-MM-DD"),
    end_date: str = Query(..., description="Date de fin au format YYYY-MM-DD")):
    # mon compte X
    LOGIN = os.getenv('LOGIN')
    PASSWORD = os.getenv('PASSWORD')

    # intervalle de temps à scraper
    since_date = datetime.strptime(start_date, "%Y-%m-%d")
    until_date = datetime.strptime(end_date, "%Y-%m-%d")

    # comptes X d'intérêt
    accounts_list = ["documentingbtc", "100trillionUSD", "CoinDesk", "saylor", "scottmelker",
                    "woonomic", "LynAldenContact", "PrestonPysh", "PeterLBrandt", "rektcapital"]


    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--disable-blink-features=AutomationControlled")

    # avec ou sans le visuel sur les pages webs
    # options.add_argument("--headless")

    # parallelisation
    with ThreadPoolExecutor(max_workers=1) as executor:
        for account in accounts_list:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            # scraping des tweets d'un compte X entre 2 dates
            executor.submit(scrape_tweets_one_account, LOGIN, PASSWORD, account, since_date, until_date, driver)
    

@app.post("/tweet-to-scores")
def tweet_to_scores(request: TweetRequest) -> Dict[str, float]:
    tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
    model = AutoModelForSequenceClassification.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
    tweets = request.tweets
    # Calcul des scores pour chaque tweet
    scores = {tweet: tweets_to_sentiment_scores(tweet, tokenizer, model ) for tweet in tweets}

    return scores