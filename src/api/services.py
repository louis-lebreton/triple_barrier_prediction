from df_building.get_data_API import get_economic_data, get_BTC_data
from df_building.get_sentiment_score import tweets_to_sentiment_scores
from df_building.get_data_scraping import scrape_tweets_one_account


def build_btc_df():

def build_economic_df():
    # clef API FRED obtenue via https://fred.stlouisfed.org/docs/api/api_key.html
    FRED_API_KEY = os.getenv('FRED_API_KEY')

    # variables d'intérêt
    series_list = [
        'DFF',       # Federal Funds Rate
        'NFINCP',    # Nonfinancial commercial paper outstanding
        'FINCP',     # Financial commercial paper outstanding
        'DPRIME',    # Bank prime loan rate
        'DPCREDIT',  # Discount window primary credit
        'DTWEXBGS',  # Nominal Broad U.S. Dollar Index
        'CPIAUCSL',  # Consumer Price Index
        'DGS3MO',    # Market Yield on U.S. Treasury Securities (3 months)
        'DGS1',      # Market Yield on U.S. Treasury Securities (1 year)
        'DGS30'      # Market Yield on U.S. Treasury Securities (30 years)
    ]

    df_economic = get_economic_data(series_id_list=series_list, api_key=FRED_API_KEY, start_date=start_date, end_date=end_date)

    df_economic.index = df_economic['date']
    df_economic.drop(columns=['date'], inplace=True)


def build_tweets_df():
    