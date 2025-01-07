from fastapi import FastAPI
import requests
import csv
from mangum import Mangum

app = FastAPI()

ASQ_URL = "https://docs.google.com/spreadsheets/d/1TiU8sv5cJg30ZL3fqPSmBwJJbB7h2xv1NNbKo4ZIydU/export?format=csv"

@app.get("/analyze")
def analyze_asq(client_name: str):
    response = requests.get(ASQ_URL)
    response.raise_for_status()
    data = response.text.splitlines()

    reader = csv.reader(data)
    header = next(reader)  # Skip header row

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
                primary_impression = "The client has no risk of suicidal thoughts or behaviors."
                additional_impressions = []
                suggested_tools = []
            elif "Yes" in acuity_response:
                interpretation = "Acute Positive Screen"
                primary_impression = "The client is at imminent risk of suicide and requires immediate safety and mental health evaluation."
                additional_impressions = ["The client requires a STAT safety/full mental health evaluation."]
                suggested_tools = ["Tools for Suicide", "Immediate Mental Health Safety Plan"]
            else:
                interpretation = "Non-Acute Positive Screen"
                primary_impression = "The client is at potential risk of suicide and requires a brief suicide safety assessment."
                additional_impressions = ["The client requires a brief suicide safety assessment."]
                suggested_tools = ["Tools for Suicide", "Suicide Risk Assessment Tools"]

            return {
                "client_name": client_name,
                "selected_options": selected_options,
                "how_and_when": how_and_when if how_and_when else "No response provided.",
                "please_describe": please_describe if please_describe else "No response provided.",
                "acuity_response": acuity_response,
                "interpretation": interpretation,
                "primary_impression": primary_impression,
                "additional_impressions": additional_impressions,
                "suggested_tools": suggested_tools,
            }

    return {"error": f"Client '{client_name}' not found."}

handler = Mangum(app)
