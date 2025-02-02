"""
@author: Louis Lebreton

Tweets scraping endpoint
"""
import os
from datetime import datetime
from fastapi import APIRouter, Query
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor

from src.services.df_building.get_data_scraping import scrape_tweets_one_account

router = APIRouter()

@router.get("/scrape-tweets")
def scrape_tweets(
    start_date: str = Query(..., description="Date de début au format YYYY-MM-DD"),
    end_date: str = Query(..., description="Date de fin au format YYYY-MM-DD"),
    accounts_list: list[str] = Query([
        "saylor", "LynAldenContact", "woonomic", "documentingbtc", "100trillionUSD"
    ], description="Liste des comptes X à scraper"),
    num_workers: int = Query(1, description="Nombre de workers pour la parallélisation")
):
    """
    Scrape les tweets de plusieurs comptes X sur une période choisie
    """
    # mon compte X
    LOGIN = os.getenv('LOGIN')
    PASSWORD = os.getenv('PASSWORD')

    # intervalle de temps à scraper
    since_date = datetime.strptime(start_date, "%Y-%m-%d")
    until_date = datetime.strptime(end_date, "%Y-%m-%d")

    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--disable-blink-features=AutomationControlled")

    # avec ou sans le visuel sur les pages webs
    # options.add_argument("--headless")

    # parallelisation
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for account in accounts_list:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            # scraping des tweets d'un compte X entre 2 dates
            executor.submit(scrape_tweets_one_account, LOGIN, PASSWORD, account, since_date, until_date, driver)
