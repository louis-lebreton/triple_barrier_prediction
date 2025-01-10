"""
@author: Louis Lebreton

"""

from fastapi import FastAPI
from src.routers import index, health, get_api_data, get_tweets, predict

app = FastAPI()

# routers
app.include_router(index.router, prefix="/api", tags=["Index"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(get_api_data.router, prefix="/api", tags=["Economic data", "Bitcoin data"])
app.include_router(get_tweets.router, prefix="/api", tags=["Scrape tweets", "Convert tweets to scores"])
app.include_router(predict.router, prefix="/api", tags=["Predict"])
