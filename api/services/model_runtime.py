from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from api.schemas import ModelInput, PredictionResponse

from api.config import MODEL_PATH, MODEL_BLOB_URL


@dataclass
class ModelRuntime:
    loaded: bool = False
    model_path: Optional[str] = None
    model_blob_url: Optional[str] = None

    def load_if_needed(self) -> None:
        if self.loaded:
            return

        self.model_path = MODEL_PATH
        self.model_blob_url = MODEL_BLOB_URL
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
