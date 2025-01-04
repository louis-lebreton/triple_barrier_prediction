"""
@author: Louis Lebreton
Conversion des tweets en score
via modèle BERT
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd


tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
model = AutoModelForSequenceClassification.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")

tweets_df = pd.read_csv('data/tweets/tweets_data_CoinDesk.csv')
tweets_text = tweets_df['tweet_text'].tolist()


def tweets_to_sentiment_scores(text_list):
    encoded_inputs = tokenizer(text_list, padding=True, truncation=True, return_tensors="pt", max_length=128)
    with torch.no_grad():
        outputs = model(**encoded_inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return scores
