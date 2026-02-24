from fastapi import FastAPI, HTTPException
from uuid import UUID, uuid4
from pydantic import EmailStr
from schema.schema import UserInput, UserUpdate, UserResponse
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os

app = FastAPI()

# --- DATABASE SETUP ---
DB_FILE = "users_db.json"


def read_db():
    """Reads the JSON file and returns the data as a dictionary."""
    if not os.path.exists(DB_FILE):
        return {}  # Return an empty dictionary if the file doesn't exist yet
    with open(DB_FILE, "r") as file:
        return json.load(file)


def write_db(data):
    """Writes the dictionary back into the JSON file."""
    with open(DB_FILE, "w") as file:
        # indent=4 makes the JSON file nicely formatted and easy to read!
        json.dump(data, file, indent=4)


# --- MODELS ---
IST = ZoneInfo("Asia/Kolkata")
TIME_FORMAT = "%Y-%m-%d %H:%M"


@app.get("/all-users")
def view_database():
    """See all users currently saved in the JSON file."""
    return read_db()


@app.post("/health-report", response_model=UserResponse)
def create_health_report(data: UserInput):
    db = read_db()
    if data.email in db:
        raise HTTPException(status_code=400, detail="Email already registered")

    current_ist_time = datetime.now(IST).strftime(TIME_FORMAT)
    user_data = data.model_dump()

    # 🏗️ Build a beautifully structured dictionary!
    structured_response = {
        "account": {
            "user_id": str(uuid4()),
            "created_at": current_ist_time,
            "updated_at": current_ist_time,
        },
        "profile": {
            "name": user_data["name"],
            "email": user_data["email"],
            "age": user_data["age"],
            "gender": user_data["gender"],
            "height": user_data["height"],
            "weight": user_data["weight"],
            "activity": user_data["activity"],
            "goal": user_data["goal"],
        },
        "metrics": {
            "bmi": user_data["bmi"],
            "bmi_category": user_data["bmi_category"],
            "recommended_calories": user_data["recommended_calories"],
            "macros": user_data["macros"],
        },
    }

    db[data.email] = structured_response
    write_db(db)
    return structured_response


@app.put("/update-report/{user_email}", response_model=UserResponse)
def update_health_report(user_email: str, user_data: UserUpdate):
    db = read_db()
    if user_email not in db:
        raise HTTPException(status_code=404, detail="User not found")

    existing_structured_data = db[user_email]

    # 1. Extract just their profile inputs
    existing_profile = existing_structured_data["profile"]
    update_data = user_data.model_dump(exclude_unset=True)

    # 2. Merge the old profile inputs with the new updates
    updated_profile = existing_profile | update_data

    # 3. Pass it back through UserInput to recalculate the math!
    recalculated_user = UserInput(**updated_profile).model_dump()

    # 4. Rebuild the beautiful nested dictionary
    new_structured_response = {
        "account": {
            "user_id": existing_structured_data["account"]["user_id"],
            "created_at": existing_structured_data["account"]["created_at"],
            "updated_at": datetime.now(IST).strftime(
                TIME_FORMAT
            ),  # ONLY update this one!
        },
        "profile": {
            "name": recalculated_user["name"],
            "email": recalculated_user["email"],
            "age": recalculated_user["age"],
            "gender": recalculated_user["gender"],
            "height": recalculated_user["height"],
            "weight": recalculated_user["weight"],
            "activity": recalculated_user["activity"],
            "goal": recalculated_user["goal"],
        },
        "metrics": {
            "bmi": recalculated_user["bmi"],
            "bmi_category": recalculated_user["bmi_category"],
            "recommended_calories": recalculated_user["recommended_calories"],
            "macros": recalculated_user["macros"],
        },
    }

    db[user_email] = new_structured_response
    write_db(db)
    return new_structured_response
