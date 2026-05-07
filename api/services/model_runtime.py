from __future__ import annotations

import cloudpickle
import pandas as pd
from sklearn.pipeline import Pipeline
from dataclasses import dataclass
from pathlib import Path

from api.schemas import ModelInput, PredictionResponse


@dataclass
class ModelRuntime:
    model: Pipeline | None = None

    def load_if_needed(self) -> None:
        if self.model:
            return

        with open(Path(__file__).resolve().parent.joinpath("./model.pkl"), "rb") as f:
            self.model = cloudpickle.load(f)

    def predict(
        self, prediction_offset: int, model_input: ModelInput
    ) -> PredictionResponse:
        self.load_if_needed()

        prediction = self.model.predict(
            pd.DataFrame(
                {
                    "time": [model_input.time],
                    "prediction_offset": [prediction_offset],
                    "temperature": [model_input.temperature],
                    "humidity": [model_input.humidity],
                    "wind_direction": [model_input.wind_direction],
                    "wind_speed": [model_input.wind_speed],
                    "precipitation": [model_input.precipitation],
                    "light": [model_input.light],
                }
            )
        )[0]

        return PredictionResponse(
            prediction_offset=prediction_offset,
            predicted_time=model_input.time + prediction_offset * 60 * 60,
            temperature=prediction[0],
            humidity=prediction[1],
            wind_direction=prediction[2],
            wind_speed=prediction[3],
            precipitation=prediction[4],
            light=prediction[5],
        )


runtime = ModelRuntime()
