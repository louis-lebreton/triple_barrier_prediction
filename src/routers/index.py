"""
@author: Louis Lebreton

"""
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
def index():
    """
    Index Endpoint
    Purpose: Brief explanation of the application’s purpose and capabilities.
             Provide API documentation link and available endpoints.
    """
    try:
        # Application description
        description = {
            "application_name": "Economic Data API",
            "purpose": "Provide economic and financial data metrics through easy-to-use API endpoints.",
            "capabilities": [
                "Fetch processed economic data",
                "Monitor system health",
                "Access API documentation"
            ],
            "api_documentation": "/docs",
            "available_endpoints": [
                {
                    "path": "/",
                    "description": "Index Endpoint providing overview of the API."
                },
                {
                    "path": "/health",
                    "description": "Monitor API availability and system status."
                },
                {
                    "path": "/economic-data",
                    "description": "Fetch processed economic data with start_date and end_date."
                },
                {
                    "path": "/bitcoin-data",
                    "description": "Fetch processed bitcoin data with days."
                },
                
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