from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

from api.schemas import ModelInput, PredictionResponse, WeatherData


@dataclass
class _ModelRegistry:
    loaded: bool = False


_registry = _ModelRegistry()


def load_models_if_needed() -> None:
    if not _registry.loaded:
        _registry.loaded = True


def generate_mock_prediction(
    prediction_offset: int, model_input: ModelInput
) -> PredictionResponse:
    base_time = model_input.time or int(time.time())
    predicted_time = base_time + (prediction_offset * 3600)

    return PredictionResponse(
        prediction_offset=prediction_offset,
        predicted_time=predicted_time,
        temperature=model_input.temperature + (prediction_offset * 0.15),
        humidity=max(0.0, model_input.humidity - (prediction_offset * 0.2)),
        wind_direction=float(
            (model_input.wind_direction + prediction_offset * 7) % 360
        ),
        wind_speed=max(0.0, model_input.wind_speed + ((prediction_offset % 5) * 0.3)),
        light=max(0, model_input.light - (prediction_offset * 20)),
        precipitation=model_input.precipitation
        + (0.4 if prediction_offset % 6 == 0 else 0.0),
    )


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
