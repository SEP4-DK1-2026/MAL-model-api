from pydantic import BaseModel
from typing import Optional


class ModelInput(BaseModel):
    time: int
    temperature: float
    humidity: float
    wind_direction: float
    wind_speed: float
    precipitation: float
    light: int


class PredictionRequest(BaseModel):
    model_input: ModelInput
    prediction_offsets: list[int]
    model: Optional[str] = None


class Prediction(BaseModel):
    prediction_offset: int
    predicted_time: int
    temperature: float
    humidity: float
    wind_direction: float
    wind_speed: float
    precipitation: float
    light: int


class PredictionResponse(BaseModel):
    predictions: list[Prediction]
    model: str
