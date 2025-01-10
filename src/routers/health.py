"""
@author: Louis Lebreton

"""
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI()

@app.get("/health")
def health_check():
    """
    Health Check Endpoint
    Purpose: Monitor API availability and system status
    Expected Response: Service health metrics and status
    """
    try:
    
        system_status = {
            "service": "Healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
        return {
            "status": "success",
            "data": system_status
        }
    except Exception as e:
        return {
            "status": "failure",
            "error": str(e)
        }