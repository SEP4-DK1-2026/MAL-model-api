from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
        return self._predict_dummy(prediction_offset, model_input)

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
