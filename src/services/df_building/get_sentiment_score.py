"""
@author: Louis Lebreton
Conversion des tweets en score
via modèle BERT
"""
import torch

def tweets_to_sentiment_scores(text_list, tokenizer, model):
    """
    inference
    transformation des tweets en scores de sentiment
    """
    # tokenize le texte d'entrée
    encoded_inputs = tokenizer(text_list, padding=True, truncation=True, return_tensors="pt", max_length=128)
    # inference
    with torch.no_grad():
        outputs = model(**encoded_inputs)
    # dernière couche: softmax sur les logits pour avoir les probabilités
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return scores
