# schemas.py
from typing import Literal, Annotated, Optional
from pydantic import BaseModel, Field, computed_field, EmailStr, field_validator
from uuid import UUID


# 1. Input Model
class UserInput(BaseModel):
    name: Annotated[str, Field(..., description="Name of the User")]
    age: Annotated[int, Field(..., gt=0, description="Age of the User")]
    gender: Literal["male", "female"]
    email: EmailStr
    height: Annotated[float, Field(..., gt=0, description="Height in cm")]
    weight: Annotated[float, Field(..., gt=0, description="Weight in kg")]
    activity: Literal["sedentary", "light", "moderate", "active", "very_active"]
    goal: Literal["fat_loss", "muscle_gain", "maintenance"]

    @field_validator("email")
    @classmethod
    def only_gmail_allowed(cls, value: EmailStr):
        if not value.lower().endswith("@gmail.com"):
            raise ValueError("Only @gmail.com emails are allowed")
        return value

    @computed_field
    @property
    def bmi(self) -> float:
        height_m = self.height / 100
        return round(self.weight / (height_m**2), 2)

    @computed_field
    @property
    def bmi_category(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    @computed_field
    @property
    def recommended_calories(self) -> float:
        if self.gender == "male":
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
        else:
            bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161

        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        tdee = bmr * multipliers[self.activity]

        calories = (
            tdee - 500
            if self.goal == "fat_loss"
            else (tdee + 300 if self.goal == "muscle_gain" else tdee)
        )
        return round(max(calories, 1200), 2)

    @computed_field
    @property
    def macros(self) -> dict:
        calories = self.recommended_calories
        if self.goal == "fat_loss":
            protein, fat = 2 * self.weight, (0.25 * calories) / 9
        elif self.goal == "muscle_gain":
            protein, fat = 1.6 * self.weight, (0.30 * calories) / 9
        else:
            protein, fat = 1.5 * self.weight, (0.25 * calories) / 9
        carbs = (calories - (protein * 4 + fat * 9)) / 4
        return {
            "protein_g": round(protein, 2),
            "fat_g": round(fat, 2),
            "carbs_g": round(carbs, 2),
        }


# 2. Update Model
class UserUpdate(BaseModel):
    name: Annotated[Optional[str], Field(None, description="Name of the User")]
    age: Annotated[Optional[int], Field(None, gt=0, description="Age of the User")]
    gender: Optional[Literal["male", "female"]] = None
    height: Annotated[Optional[float], Field(None, gt=0, description="Height in cm")]
    weight: Annotated[Optional[float], Field(None, gt=0, description="Weight in kg")]
    activity: Optional[
        Literal["sedentary", "light", "moderate", "active", "very_active"]
    ] = None
    goal: Optional[Literal["fat_loss", "muscle_gain", "maintenance"]] = None


# 3. Response Model
class UserResponse(BaseModel):
    account: dict
    profile: dict
    metrics: dict
