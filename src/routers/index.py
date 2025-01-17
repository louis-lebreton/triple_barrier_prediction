"""
@author: Louis Lebreton
Index endpoint
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
def index():
    """
    Index endpoint
    explication de l’objectif de l’application.
    Documentation de l’API et de ses endpoints
    """
    try:
        description = {
            "application_name": "Projet Quantitative Finance",
            "purpose": "API permettant de faciliter le lancement de certains modules du projet",
            "capabilities": [
                "Fetch processed economic data",
                "Monitor system health",
                "Fetch Bitcoin & economic data",
                "Predict financial trends",
                "Convert tweets to sentiment score",
                "Access API documentation"
            ],
            "api_documentation": "/docs",
            "available_endpoints": [
                {
                    "path": "/",
                    "description": "Index Endpoint providing overview of the API"
                },
                {
                    "path": "/health",
                    "description": "Monitor API availability and system status"
                },
                {
                    "path": "/economic-data",
                    "description": "Fetch processed economic data with start_date and end_date"
                },
                {
                    "path": "/bitcoin-data",
                    "description": "Fetch processed Bitcoin data with days"
                },
                {
                    "path": "/predict",
                    "description": "Predict financial signal using GBM stacking model based on data"
                },
                {
                    "path": "/scrape-tweets",
                    "description": "Scrape tweets X accounts"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

        return {
            "status": "success",
            "data": description
        }
    except Exception as e:
        return {
            "status": "failure",
            "error": str(e)
        }