from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from math import pi, sin, cos
from pathlib import Path
from typing import Any, Optional

import joblib

from api.schemas import ModelInput, PredictionResponse


@dataclass
class ModelRuntime:
    loaded: bool = False
    model: Optional[object] = None
    model_path: Optional[str] = None
    model_blob_url: Optional[str] = None

    def load_if_needed(self) -> None:
        if self.loaded:
            return

        default_model_path = Path(__file__).resolve().parents[2] / "model.pkl"
        configured_model_path = os.getenv("MODEL_PATH")

        model_path = (
            Path(configured_model_path) if configured_model_path else default_model_path
        )
        self.model_path = str(model_path)
        self.model_blob_url = os.getenv("MODEL_BLOB_URL")

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {model_path}. Set MODEL_PATH or place model.pkl in the FunctionApp folder."
            )

        self.model = joblib.load(model_path)
        self.loaded = True

    def predict(
        self, prediction_offset: int, model_input: ModelInput
    ) -> PredictionResponse:
        self.load_if_needed()
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        features = self._build_features(prediction_offset, model_input)
        raw_prediction = self.model.predict([features])
        return self._to_prediction_response(
            prediction_offset=prediction_offset,
            model_input=model_input,
            raw_prediction=raw_prediction,
        )

    def _build_features(
        self, prediction_offset: int, model_input: ModelInput
    ) -> list[float]:
        base_time = model_input.time or int(time.time())
        timestamp = datetime.fromtimestamp(base_time, tz=timezone.utc)

        month_angle = 2.0 * pi * ((timestamp.month - 1) / 12.0)
        day_of_year = timestamp.timetuple().tm_yday
        day_angle = 2.0 * pi * ((day_of_year - 1) / 365.25)
        hour_angle = 2.0 * pi * (timestamp.hour / 24.0)

        named_feature_values = {
            "temp_dry": float(model_input.temperature),
            "humidity": float(model_input.humidity),
            "wind_dir": float(model_input.wind_direction),
            "wind_speed": float(model_input.wind_speed),
            "precip_past1h": float(model_input.precipitation),
            "month_sin": float(sin(month_angle)),
            "month_cos": float(cos(month_angle)),
            "day_sin": float(sin(day_angle)),
            "day_cos": float(cos(day_angle)),
            "hour_sin": float(sin(hour_angle)),
            "hour_cos": float(cos(hour_angle)),
            "relative_hours": float(prediction_offset),
        }

        feature_names = getattr(self.model, "feature_names_in_", None)
        if feature_names is not None and len(feature_names) > 0:
            return [float(named_feature_values.get(str(name), 0.0)) for name in feature_names]

        with_time_with_offset = [
            float(model_input.time),
            float(model_input.temperature),
            float(model_input.humidity),
            float(model_input.wind_direction),
            float(model_input.wind_speed),
            float(model_input.precipitation),
            float(model_input.light),
            float(prediction_offset),
        ]

        with_offset = with_time_with_offset[1:]
        with_time = with_time_with_offset[:-1]
        weather_only = with_time_with_offset[1:-1]

        expected_features = getattr(self.model, "n_features_in_", None)
        feature_options = [
            with_time_with_offset,
            with_offset,
            with_time,
            weather_only,
        ]

        if expected_features is None:
            return with_time_with_offset

        for candidate in feature_options:
            if len(candidate) == int(expected_features):
                return candidate

        raise ValueError(
            f"Model expects {expected_features} features, but available inputs are {[len(option) for option in feature_options]}."
        )

    def _to_prediction_response(
        self,
        prediction_offset: int,
        model_input: ModelInput,
        raw_prediction: Any,
    ) -> PredictionResponse:
        base_time = model_input.time or int(time.time())
        defaults: dict[str, float | int] = {
            "predicted_time": base_time + (prediction_offset * 3600),
            "temperature": float(model_input.temperature),
            "humidity": float(model_input.humidity),
            "wind_direction": float(model_input.wind_direction),
            "wind_speed": float(model_input.wind_speed),
            "light": int(model_input.light),
            "precipitation": float(model_input.precipitation),
        }

        normalized = raw_prediction
        if hasattr(normalized, "tolist"):
            normalized = normalized.tolist()

        if (
            isinstance(normalized, list)
            and len(normalized) == 1
            and isinstance(normalized[0], (list, tuple, dict, int, float))
        ):
            normalized = normalized[0]

        if isinstance(normalized, dict):
            for key, value in normalized.items():
                target_key = {
                    "temp": "temperature",
                    "temperature": "temperature",
                    "humidity": "humidity",
                    "wind_direction": "wind_direction",
                    "windDirection": "wind_direction",
                    "wind_speed": "wind_speed",
                    "windSpeed": "wind_speed",
                    "light": "light",
                    "precipitation": "precipitation",
                    "predicted_time": "predicted_time",
                    "predictedTime": "predicted_time",
                    "time": "predicted_time",
                    "unixTime": "predicted_time",
                }.get(key)
                if target_key is not None:
                    defaults[target_key] = value
        elif isinstance(normalized, (list, tuple)):
            ordered_keys = [
                "temperature",
                "humidity",
                "wind_direction",
                "wind_speed",
                "precipitation",
                "light",
                "predicted_time",
            ]
            for idx, value in enumerate(normalized):
                if idx >= len(ordered_keys):
                    break
                defaults[ordered_keys[idx]] = value
        elif isinstance(normalized, (int, float)):
            defaults["temperature"] = normalized

        return PredictionResponse(
            prediction_offset=prediction_offset,
            predicted_time=int(defaults["predicted_time"]),
            temperature=float(defaults["temperature"]),
            humidity=float(defaults["humidity"]),
            wind_direction=float(defaults["wind_direction"]),
            wind_speed=float(defaults["wind_speed"]),
            light=int(defaults["light"]),
            precipitation=float(defaults["precipitation"]),
        )

    def _predict_dummy(
        self, prediction_offset: int, model_input: ModelInput
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
            wind_speed=max(
                0.0, model_input.wind_speed + ((prediction_offset % 5) * 0.3)
            ),
            light=max(0, model_input.light - (prediction_offset * 20)),
            precipitation=model_input.precipitation
            + (0.4 if prediction_offset % 6 == 0 else 0.0),
        )


runtime = ModelRuntime()
