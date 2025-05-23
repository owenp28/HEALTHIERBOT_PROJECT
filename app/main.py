from fastapi import FastAPI, APIRouter, Request
from dotenv import load_dotenv
import os
import csv
import json

# Load Environment Variables 
load_dotenv()

# Database config
db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("DB_USER", "root")
db_pass = os.getenv("DB_PASS", "")
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
port = int(os.getenv("PORT", 8000))

print(f"Database Host: {db_host}")
print(f"Database User: {db_user}")
print(f"Debug Mode: {debug_mode}")
print(f"API will run on port: {port}")

# FastAPI Setup
app = FastAPI(debug=debug_mode)
router = APIRouter()

# Helper Functions 
def load_symptom_data(file_path):
    data = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            if "description" not in [h.lower() for h in headers]:
                print(f"Warning: 'description' column not found in {headers}")
            for row in reader:
                disease = row.get('disease') or row.get('Disease')
                desc = row.get('description') or row.get('Description')
                if disease and desc:
                    data[disease.lower()] = desc
    except Exception as e:
        print(f"Error loading symptom data: {e}")
    return data

def get_disease_description(disease_name, symptom_data):
    return symptom_data.get(disease_name.lower(), "Description not found.")

def generate_response(user_input):
    if "fever" in user_input.lower():
        return {"disease_name": "flu"}
    elif "cough" in user_input.lower():
        return {"disease_name": "cold"}
    else:
        return {"disease_name": "unknown"}

# Load Symptom Data
symptom_data = {}
try:
    symptom_data_dir = os.path.join(os.getcwd(), "disease symptom prediction")
    symptom_data_file = os.path.join(symptom_data_dir, "symptom_Description.csv")
    if os.path.exists(symptom_data_file):
        symptom_data = load_symptom_data(symptom_data_file)
    else:
        print(f"Warning: File not found at {symptom_data_file}. Using empty symptom data.")
except Exception as e:
    print(f"Error loading symptom data: {e}")

# Load Chatbot Medical Dataset
chatbot_dataset = {}
try:
    with open('chatbot_medical_dataset.json', 'r') as file:
        chatbot_dataset = json.load(file)
except Exception as e:
    print(f"Error loading chatbot medical dataset: {e}")

# Routes 
@app.get("/")
def read_root():
    return {"message": "Welcome to HealthierBot!"}

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("input")
    if not user_input:
        return {"error": "User input is missing."}
    try:
        response = generate_response(user_input)
        disease_name = response.get("disease_name")
        description = get_disease_description(disease_name, symptom_data)
        return {"response": response, "description": description}
    except Exception as e:
        return {"error": f"An error occurred while processing the request: {e}"}

@router.get("/disease/{disease_name}")
async def get_disease_info(disease_name: str):
    description = get_disease_description(disease_name, symptom_data)
    return {"disease": disease_name, "description": description}

@app.post("/diet")
async def suggest_diet(request: Request):
    data = await request.json()
    user_input = data.get("input")
    if not user_input:
        return {"error": "User input is missing."}
    # TODO: Implement LLM or rules-based diet generation
    return {"diet": f"Balanced diet suggestion based on input: {user_input}"}

@app.post("/calories")
async def calculate_calories(request: Request):
    data = await request.json()
    food_items = data.get("food_items")
    if not food_items:
        return {"error": "Food items are missing."}
    # TODO: Implement calorie calculation logic
    return {"calories": f"Calories calculated for food items: {food_items}"}

# Include router
app.include_router(router, prefix="/api")

# Main runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=debug_mode)
