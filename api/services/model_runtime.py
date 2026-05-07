from __future__ import annotations

import cloudpickle
import pandas as pd
from sklearn.pipeline import Pipeline
from dataclasses import dataclass
from pathlib import Path

from api.schemas import ModelInput, PredictionResponse, Prediction


@dataclass
class ModelRuntime:
    model: Pipeline | None = None

    def load_if_needed(self) -> None:
        if self.model:
            return

        with open(Path(__file__).resolve().parent.joinpath("./model.pkl"), "rb") as f:
            self.model = cloudpickle.load(f)

    def predict(
        self, prediction_offsets: list[int], model_input: ModelInput
    ) -> PredictionResponse:
        self.load_if_needed()

        n = range(len(prediction_offsets))
        predictions = self.model.predict(
            pd.DataFrame(
                {
                    "time": [model_input.time for _ in n],
                    "prediction_offset": prediction_offsets,
                    "temperature": [model_input.temperature for _ in n],
                    "humidity": [model_input.humidity for _ in n],
                    "wind_direction": [model_input.wind_direction for _ in n],
                    "wind_speed": [model_input.wind_speed for _ in n],
                    "precipitation": [model_input.precipitation for _ in n],
                    "light": [model_input.light for _ in n],
                }
            )
        )

        return PredictionResponse(
            predictions=[
                Prediction(
                    prediction_offset=prediction_offsets[i],
                    predicted_time=model_input.time + prediction_offsets[i] * 60 * 60,
                    temperature=prediction[0],
                    humidity=prediction[1],
                    wind_direction=prediction[2],
                    wind_speed=prediction[3],
                    precipitation=prediction[4],
                    light=prediction[5],
                )
                for i, prediction in enumerate(predictions)
            ]
        )


runtime = ModelRuntime()
