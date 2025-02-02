"""
@author: Louis Lebreton

Serveur API REST qui expose plusieurs endpoints
"""
from fastapi import FastAPI
from src.routers import index, health, predict, api_data, tweets

app = FastAPI()

# routers
app.include_router(index.router, tags=["Index"])
app.include_router(health.router, tags=["Health"])
app.include_router(api_data.router, tags=["Economic & Bitcoin data"])
app.include_router(tweets.router, tags=["Scrape tweets"])
app.include_router(predict.router, tags=["Predict"])
