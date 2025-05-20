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
    allow_origins=["https://lead-genius-suite.vercel.app", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class SearchRequest(BaseModel):
    query: str
    location: str
    tbs: str  # optional if needed by your use case

@app.post("/search-places/")
def search_places(request: SearchRequest):
    query_combined = f"{request.query} {request.location}"

    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }

    all_places = []
    page = 1

    while True:
        payload = json.dumps({
            "q": query_combined,
            "tbs": request.tbs,
            "type": "places",
            "page": page
        })

        try:
            conn = http.client.HTTPSConnection("google.serper.dev")
            conn.request("POST", "/places", payload, headers)
            res = conn.getresponse()
            data = res.read()
            conn.close()

            response_json = json.loads(data)
            places = response_json.get("places", [])

            if not places:
                break

            all_places.extend(places)
            page += 1
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Request failed on page {page}: {e}")

    return {"places": all_places}
