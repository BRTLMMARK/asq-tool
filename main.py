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

        # Normalize input for comparison
        input_name = f"{first_name} {middle_name} {last_name} {suffix}".strip().lower()

        for row in reader:
            # Extract and normalize name from the CSV
            row_name = f"{row[-4]} {row[-3]} {row[-2]} {row[-1]}".strip().lower()

            if row_name == input_name:
                selected_options_raw = row[2].strip()
                how_and_when = row[3].strip()
                please_describe = row[6].strip()
                acuity_response = row[5].strip()

                selected_options = [option.strip() for option in selected_options_raw.split(",")]

                if "None of the above" in selected_options:
                    return {
                        "client_name": input_name.title(),
                        "selected_options": selected_options,
                        "interpretation": "No Risk",
                        "message": "The client has no risk of suicidal thoughts or behaviors."
                    }

                if "Yes" in acuity_response:
                    interpretation = "Acute Positive Screen"
                    primary_impression = random.choice(phrases["Acute Positive Screen"])
                    additional_impressions = [random.choice(phrases["Acute Positive Screen"])]
                else:
                    interpretation = "Non-Acute Positive Screen"
                    primary_impression = random.choice(phrases["Non-Acute Positive Screen"])
                    additional_impressions = [random.choice(phrases["Non-Acute Positive Screen"])]

                return {
                    "client_name": input_name.title(),
                    "selected_options": selected_options,
                    "how_and_when": how_and_when if how_and_when else "No response provided.",
                    "please_describe": please_describe if please_describe else "No response provided.",
                    "acuity_response": acuity_response,
                    "interpretation": interpretation,
                    "primary_impression": primary_impression,
                    "additional_impressions": additional_impressions
                }

        raise HTTPException(status_code=404, detail=f"Client '{input_name}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing ASQ data: {e}")

handler = Mangum(app)
