from fastapi import APIRouter, Request, HTTPException
from pathlib import Path
import csv

router = APIRouter()

def load_symptom_data(file_path: str):
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Error: '{file_path}' not found.")
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        try:
            symptom_data = {row["disease_name"]: row["description"] for row in reader}
        except KeyError:
            raise ValueError("CSV file must contain 'disease_name' and 'description' columns.")
    return symptom_data

try:
    symptom_data = load_symptom_data("app/data/symptom_Description.csv")  # Update the path to the correct location
except FileNotFoundError:
    symptom_data = None
except ValueError as e:
    symptom_data = None
    print(f"Error loading symptom data: {e}")

@router.post("/process")
async def process_request(request: Request):
    if symptom_data is None:
        raise HTTPException(status_code=500, detail="Symptom data not available.")
    
    data = await request.json()
    user_input = data.get("input")
    if not user_input:
        raise HTTPException(status_code=400, detail="User input is missing.")
    
    response = generate_response(user_input)
    disease_name = response.get("disease_name", "unknown_disease")
    description = symptom_data.get(disease_name, "Description not found.")
    
    return {"response": response, "description": description}

def generate_response(user_input: str):
    # Example implementation using user_input
    if "fever" in user_input.lower():
        return {"disease_name": "flu"}
    elif "cough" in user_input.lower():
        return {"disease_name": "cold"}
    else:
        return {"disease_name": "unknown_disease"}

def get_disease_description(disease_name: str, symptom_data: dict):
    return symptom_data.get(disease_name, "Description not found.")

@router.get("/disease/{disease_name}")
async def get_disease_info(disease_name: str):
    if symptom_data is None:
        raise HTTPException(status_code=500, detail="Symptom data not available.")
    description = get_disease_description(disease_name, symptom_data)
    return {"disease": disease_name, "description": description}
