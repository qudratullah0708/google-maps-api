from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import http.client
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
serper_api_key = os.getenv("SERPER_API_KEY")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lead-genius-suite.vercel.app"],    # For development "http://127.0.0.1:8000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class SearchRequest(BaseModel):
    query: str
    location: str
    tbs: str  # e.g., qdr:y for past year

@app.post("/search-places/")
def search_places(request: SearchRequest):
    query_combined = request.query + " " + request.location

    payload = json.dumps({
        "q": query_combined,
        "tbs": request.tbs
    })

    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }

    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        conn.request("POST", "/maps", payload, headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return json.loads(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {e}")
