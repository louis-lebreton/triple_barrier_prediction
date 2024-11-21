"""
Scraping de posts X (Twitter)
"""
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# compte X
username = ""
password = ""

target_url = "https://x.com/EmmanuelMacron"
start_date = datetime.strptime("2024-11-15", "%Y-%m-%d")
end_date = datetime.strptime("2024-11-05", "%Y-%m-%d")

# driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# page connexion X
driver.get("https://twitter.com/login")
time.sleep(5)

try:
    # login
    user_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "text"))
    )
    user_field.send_keys(username)
    user_field.send_keys(Keys.RETURN)

    time.sleep(2)

    # password
    pass_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    pass_field.send_keys(password)
    pass_field.send_keys(Keys.RETURN)

    time.sleep(5)

    driver.get(target_url)
    time.sleep(5)

    tweets_data = []
    scrolling = True
    

    while scrolling:
        # parse with bs4
        resp = driver.page_source
        soup = BeautifulSoup(resp, 'html.parser')

        # find all tweet articles
        tweet_divs = soup.find_all('article', {'role': 'article'})

        # parsing
        for tweet in tweet_divs:
            try:

                # tweet timestamp
                time_tag = tweet.find('time')
                timestamp = time_tag['datetime'] if time_tag else None

                if timestamp:
                    tweet_date = datetime.strptime(timestamp.split("T")[0], "%Y-%m-%d")
                    if tweet_date > start_date: # stop if the date is earlier than start_date
                        scrolling = True
                        print("too early / scroll")
                    elif tweet_date < end_date: # stop if the date is older than target_date
                        scrolling = False
                        print("too late / stop")
                        break
                    else: # else scrape text and author
                        # tweet text
                        tweet_text_div = tweet.find('div', {'data-testid': 'tweetText'})
                        tweet_text = tweet_text_div.get_text() if tweet_text_div else None

                        # tweet author
                        author_div = tweet.find('div', {'data-testid': 'User-Name'})
                        author = author_div.get_text() if author_div else None

                        print("scrape / stop")

                        tweets_data.append({
                            'author': author,
                            'timestamp': timestamp,
                            'tweet_text': tweet_text
                        })

            except Exception as e:
                print(f"erreur pour un tweet : {e}")
                continue

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

finally:
    driver.quit()

tweets_df = pd.DataFrame(tweets_data)

