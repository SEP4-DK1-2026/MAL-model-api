from __future__ import annotations

import time
from typing import List

from api.schemas import ModelInput, PredictionResponse, WeatherData
from api.services.model_runtime import runtime


def load_models_if_needed() -> None:
    runtime.load_if_needed()


def generate_mock_prediction(
    prediction_offset: int, model_input: ModelInput
) -> PredictionResponse:
    return runtime.predict(prediction_offset, model_input)


def get_mock_latest() -> WeatherData:
    now = int(time.time())
    return WeatherData(
        unixTime=now,
        temp=13.2,
        humidity=67.5,
        windSpeed=5.1,
        windDirection=210.0,
        precipitation=0.0,
        light=420,
        forecastOffsetHours=0,
    )


def get_mock_historical(start_unix: int, end_unix: int) -> List[WeatherData]:
    if end_unix < start_unix:
        return []

    points: List[WeatherData] = []
    current = start_unix
    step = 3600

    i = 0
    while current <= end_unix:
        points.append(
            WeatherData(
                unixTime=current,
                temp=10.0 + (i * 0.05),
                humidity=70.0 - (i * 0.1),
                windSpeed=3.5 + ((i % 4) * 0.2),
                windDirection=float((160 + i * 4) % 360),
                precipitation=0.2 if i % 8 == 0 else 0.0,
                light=max(0, 500 - (i * 10)),
                forecastOffsetHours=None,
            )
        )
        current += step
        i += 1

    return points
