"""
@author: Louis Lebreton
Scraping de posts X (Twitter)
Export dans data/tweets/
"""
import os
import random
import time

from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def scrape_tweets_one_account(username, password, account, start_date, end_date, driver)-> None:
    """
    fonction pour scraper les tweets d'un compte X
    export du df des tweets format csv dans data/tweets/

    Args :
    - username : str : nom d'utilisateur pour la connexion Twitter
    - password : str : mot de passe pour la connexion Twitter
    - proxy : str : proxy à utiliser pour la connexion (format : 'ip:port')
    - account : str : comptes à scraper
    - start_date : datetime : date de début pour la collecte des tweets
    - end_date : datetime : date de fin pour la collecte des tweets
    - driver : webdriver : instance de Selenium WebDriver 

    Return : None
    """
    tweets_data = []

    driver.get("https://twitter.com/login")
    time.sleep(random.uniform(3, 6))  # variabilité pour éviter la détection

    try:
        # login
        user_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        user_field.send_keys(username)
        user_field.send_keys(Keys.RETURN)
        time.sleep(random.uniform(2, 4))

        # password
        pass_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        pass_field.send_keys(password)
        pass_field.send_keys(Keys.RETURN)
        time.sleep(random.uniform(4, 7))

        # target url (account)
        
        driver.get(f"https://x.com/{account}")
        
        time.sleep(random.uniform(4, 7))
        print('-'*100)
        print(f'{account}: début du scraping/scrolling')
        scrolling = True

        while scrolling:
            # html
            resp = driver.page_source
            soup = BeautifulSoup(resp, 'html.parser')

            # find tweet
            tweet_divs = soup.find_all('article', {'role': 'article'})

            # tweet parsing
            for tweet in tweet_divs:
                try:
                    # non prise en compte du tweet epingle
                    social_context = tweet.find('div', {'data-testid': 'socialContext'})
                    if social_context and "Épinglé" in social_context.text:
                        print(f"{account}: tweet épinglé ignoré")
                        continue

                    # timestamp
                    time_tag = tweet.find('time')
                    timestamp = time_tag['datetime'] if time_tag else None

                    if timestamp:
                        tweet_date = datetime.strptime(timestamp.split("T")[0], "%Y-%m-%d")
                        if tweet_date > start_date:  # beginning
                            scrolling = True
                            print('too early')
                        elif tweet_date < end_date:  # end
                            scrolling = False
                            print(f'{account}: fin du scraping')
                            break
                        else: 
                            # tweet
                            tweet_text_div = tweet.find('div', {'data-testid': 'tweetText'})
                            tweet_text = tweet_text_div.get_text() if tweet_text_div else None
                            
                            #author
                            author_div = tweet.find('div', {'data-testid': 'User-Name'})
                            author = author_div.get_text() if author_div else None

                            tweets_data.append({
                                'author': author,
                                'timestamp': timestamp,
                                'tweet_text': tweet_text
                            })
                            print(f'{account}: tweet at {timestamp} scraped')

                except Exception as e:
                    print(f"erreur: {e}")
                    continue

            # smooth scrolling : pour passer à la 'page' suivante par itération random
            for _ in range(5):
                driver.execute_script("window.scrollBy(0, window.innerHeight / 5);")
                time.sleep(random.uniform(1, 2))

    finally:
        driver.quit()

    # export df sans duplicates car risque de tweets plusieurs fois scrapés
    tweets_df = pd.DataFrame(tweets_data).drop_duplicates('tweet_text', keep='last')
    print(f'{account}: export du df dans data/tweets/tweets_data_{account}.csv')
    tweets_df.to_csv(f'data/tweets/tweets_data_{account}.csv', index=False)


if __name__ == "__main__":
    # mon compte X
    LOGIN = os.getenv('LOGIN')
    PASSWORD = os.getenv('PASSWORD')

    # intervalle à scraper
    start_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-01-01", "%Y-%m-%d")

    # 10 comptes X à scraper
    accounts_list = ["documentingbtc", "100trillionUSD", "CoinDesk", "saylor", "scottmelker",
                     "woonomic", "LynAldenContact", "PrestonPysh", "PeterLBrandt", "rektcapital"]
    
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    # parallelisation
    with ThreadPoolExecutor(max_workers=5) as executor:
        for account in accounts_list:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            executor.submit(scrape_tweets_one_account, LOGIN, PASSWORD, account, start_date, end_date, driver)