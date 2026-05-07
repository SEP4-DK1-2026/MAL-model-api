from pydantic import BaseModel, Field


class ModelInput(BaseModel):
    time: int
    temperature: float
    humidity: float
    wind_direction: float
    wind_speed: float
    precipitation: float
    light: int


class PredictionRequest(BaseModel):
    modelInput: ModelInput
    predictionOffset: int = Field(gt=0, le=168)


class PredictionResponse(BaseModel):
    prediction_offset: int
    predicted_time: int
    temperature: float
    humidity: float
    wind_direction: float
    wind_speed: float
    light: int
    precipitation: float
