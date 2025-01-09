from fastapi import FastAPI, HTTPException
import requests
import csv
import json
import random
from mangum import Mangum

app = FastAPI()

ASQ_URL = "https://docs.google.com/spreadsheets/d/1TiU8sv5cJg30ZL3fqPSmBwJJbB7h2xv1NNbKo4ZIydU/export?format=csv"

# Load phrases for ASQ
with open("phrases_asq.json", "r") as f:
    phrases = json.load(f)

@app.get("/analyze")
def analyze_asq(client_name: str):
    response = requests.get(ASQ_URL)
    response.raise_for_status()
    data = response.text.splitlines()

    reader = csv.reader(data)
    header = next(reader)

    for row in reader:
        name = row[-1].strip()
        if name.lower() == client_name.lower():
            selected_options_raw = row[2].strip()
            how_and_when = row[3].strip()
            please_describe = row[6].strip()
            acuity_response = row[5].strip()

            selected_options = [option.strip() for option in selected_options_raw.split(",")]

            if "None of the above" in selected_options:
                interpretation = "No Risk"
                primary_impression = random.choice(phrases["No Risk"])
                additional_impressions = []
            elif "Yes" in acuity_response:
                interpretation = "Acute Positive Screen"
                primary_impression = random.choice(phrases["Acute Positive Screen"])
                additional_impressions = [random.choice(phrases["Acute Positive Screen"])]
            else:
                interpretation = "Non-Acute Positive Screen"
                primary_impression = random.choice(phrases["Non-Acute Positive Screen"])
                additional_impressions = [random.choice(phrases["Non-Acute Positive Screen"])]

            return {
                "client_name": client_name,
                "selected_options": selected_options,
                "how_and_when": how_and_when if how_and_when else "No response provided.",
                "please_describe": please_describe if please_describe else "No response provided.",
                "acuity_response": acuity_response,
                "interpretation": interpretation,
                "primary_impression": primary_impression,
                "additional_impressions": additional_impressions
            }

    raise HTTPException(status_code=404, detail=f"Client '{client_name}' not found.")

handler = Mangum(app)
