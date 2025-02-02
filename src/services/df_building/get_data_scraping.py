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


def tweets_parser(tweet_divs: list, tweets_scrap_dict:dict, tweets_data: list, account:str) -> tuple:
    """
    parsing de tweets à partir des balises html

    Args :
    tweet_divs : list
        balises HTML contenant les tweets
    tweets_data : list
        liste des tweets scrapés ajoutés

    Return (tuple) : 
        tweets_data (list) : Liste des données de tweets parsées
        tweets_scrap_dict (dict) : Dernier dictionnaire de données de tweet extrait
    """
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
                
                # tweet
                tweet_text_div = tweet.find('div', {'data-testid': 'tweetText'})
                tweet_text = tweet_text_div.get_text() if tweet_text_div else None
                
                # author
                author_div = tweet.find('div', {'data-testid': 'User-Name'})
                author = author_div.get_text() if author_div else None

                tweets_scrap_dict = {
                    'author': author,
                    'timestamp': timestamp,
                    'tweet_text': tweet_text
                }
                tweets_data.append(tweets_scrap_dict)
                print(f'{account}: tweet scraped {timestamp}')

        except Exception as e:
            print(f'{account}: tweet at {timestamp}: erreur {e}')
            continue

    return tweets_data, tweets_scrap_dict

def scrape_tweets_one_account(username, password, account, since_date, until_date, driver)-> None:
    """
    fonction pour scraper les tweets d'un compte X
    dans une intervalle entre 2 dates (since_date to until_date)
    export du df des tweets format csv dans data/tweets/{nom_du_compte}/

    Args :
    - username : str : nom d'utilisateur pour la connexion Twitter
    - password : str : mot de passe pour la connexion Twitter
    - proxy : str : proxy à utiliser pour la connexion (format : 'ip:port')
    - account : str : comptes à scraper
    - since_date : datetime : date de fin pour la collecte des tweets (la plus ancienne)
    - until_date : datetime : date de début pour la collecte des tweets (la plus récente)
    - driver : webdriver : instance de Selenium WebDriver 

    Return : None
    """

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

        
        print(f'{account}: début du scraping')

        since_date_str = str(since_date).split(' ')[0]
        until_date_str = str(until_date).split(' ')[0]
        last_tweet_date_str = until_date_str

        while since_date_str != until_date_str:
            # target url (account + intervalle de date)
            print(f'{account}: scraping de {since_date_str} à {until_date_str}')

            target_url = f"https://x.com/search?q=from:{account}%20since:{since_date_str}%20until:{until_date_str}&src=typed_query&f=live"
            driver.get(target_url)
        
            time.sleep(random.uniform(4, 7))
            print('-'*100)

            tweets_data = []
            tweets_scrap_dict = None
            previous_tweets_scrap_dict = None

            scrolling = True

            while scrolling:
                
                # html
                resp = driver.page_source
                soup = BeautifulSoup(resp, 'html.parser')

                # find tweet
                tweet_divs = soup.find_all('article', {'role': 'article'})
                # tweet parsing
                tweets_data, tweets_scrap_dict = tweets_parser(tweet_divs, tweets_scrap_dict, tweets_data, account)
                    
                # smooth scrolling : pour passer à la 'page' suivante par itération random
                for _ in range(5):
                    driver.execute_script("window.scrollBy(0, window.innerHeight / 5);")
                    time.sleep(random.uniform(1, 2))

                
                # si on scrape le même tweet, c'est qu'on est arrivé à la fin du scrolling possible
                # il faut donc relancer une recherche depuis la date du dernier tweet
                if tweets_scrap_dict == previous_tweets_scrap_dict:
                    print(f"{account}: fin du scrolling car arrivé en bas")
                    scrolling = False

                    # df sans duplicates car risque de tweets plusieurs fois scrapés
                    tweets_df = pd.DataFrame(tweets_data).drop_duplicates('tweet_text', keep='last')
                    if not tweets_df.empty:
                        last_tweet_date_str = tweets_df['timestamp'].iloc[-1][:10]
                        until_date_str = last_tweet_date_str
                    
                    # export dans un folder
                    output_dir = f"data/tweets/{account}"
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    print(f'{account}: export du df dans {output_dir}/tweets_data_{account}_{last_tweet_date_str}.csv')
                    tweets_df.to_csv(f'{output_dir}/tweets_data_{account}_{last_tweet_date_str}.csv', index=False)

                previous_tweets_scrap_dict = tweets_scrap_dict

        driver.quit()

    except Exception as e:
        print(f"erreur critique : {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    # mon compte X
    LOGIN = os.getenv('LOGIN')
    PASSWORD = os.getenv('PASSWORD')

    # intervalle à scraper
    since_date = datetime.strptime("2018-01-01", "%Y-%m-%d")
    until_date = datetime.strptime("2019-08-10", "%Y-%m-%d")

    # comptes X à scraper
    accounts_list = ["woonomic", "100trillionUSD", "saylor", "documentingbtc", "LynAldenContact"]

    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--disable-blink-features=AutomationControlled")
    # avec ou sans visuel sur les pages webs
    # options.add_argument("--headless")

    # parallelisation
    with ThreadPoolExecutor(max_workers=2) as executor:
        for account in accounts_list:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            executor.submit(scrape_tweets_one_account, LOGIN, PASSWORD, account, since_date, until_date, driver)

