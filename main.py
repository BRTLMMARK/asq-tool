from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import csv
import json
import random
from mangum import Mangum

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

ASQ_URL = "https://docs.google.com/spreadsheets/d/1TiU8sv5cJg30ZL3fqPSmBwJJbB7h2xv1NNbKo4ZIydU/export?format=csv"

# Load phrases for ASQ
with open("phrases_asq.json", "r") as f:
    phrases = json.load(f)

@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok", "message": "ASQ Tool API is running and accessible."}

@app.get("/analyze")
def analyze_asq(first_name: str, last_name: str, middle_name: str = "", suffix: str = ""):
    try:
        response = requests.get(ASQ_URL)
        response.raise_for_status()
        data = response.text.splitlines()

        reader = csv.reader(data)
        header = next(reader)

        input_name = f"{first_name} {middle_name} {last_name} {suffix}".strip()

        for row in reader:
            row_name = f"{row[-4]} {row[-3]} {row[-2]} {row[-1]}".strip()

            if row_name.lower() == input_name.lower():
                selected_options_raw = row[2].strip()
                how_and_when = row[3].strip()
                please_describe = row[6].strip()
                acuity_response = row[5].strip()

                selected_options = [option.strip() for option in selected_options_raw.split(",")]

                interpretation = "Acute Positive Screen" if "Yes" in acuity_response else "Non-Acute Positive Screen"
                primary_impression = (
                    "The responses indicate a critical need for immediate intervention."
                    if interpretation == "Acute Positive Screen"
                    else "Responses suggest no immediate risk but monitoring is required."
                )

                additional_impressions = [
                    "An acute positive screen was detected, requiring urgent intervention."
                ] if interpretation == "Acute Positive Screen" else []

                return {
                    "client_name": input_name.title(),
                    "selected_options": selected_options,
                    "how_and_when": how_and_when or "N/A",
                    "please_describe": please_describe or "N/A",
                    "acuity_response": acuity_response or "N/A",
                    "interpretation": interpretation,
                    "primary_impression": primary_impression,
                    "additional_impressions": additional_impressions
                }

        raise HTTPException(status_code=404, detail=f"Client '{input_name}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing ASQ data: {e}")

handler = Mangum(app)
