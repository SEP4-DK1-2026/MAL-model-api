from __future__ import annotations

import pandas as pd
from dataclasses import dataclass

from api.schemas import ModelInput, PredictionResponse, Prediction
from api.services.model_service import find_model


@dataclass
class ModelRuntime:
    def predict(
        self, model_input: ModelInput, prediction_offsets: list[int], model: str | None
    ) -> PredictionResponse:
        model, model_name = find_model(model)

        n = len(prediction_offsets)
        predictions = model.predict(
            pd.DataFrame(
                {
                    "time": [model_input.time] * n,
                    "temperature": [model_input.temperature] * n,
                    "humidity": [model_input.humidity] * n,
                    "wind_direction": [model_input.wind_direction] * n,
                    "wind_speed": [model_input.wind_speed] * n,
                    "precipitation": [model_input.precipitation] * n,
                    "light": [model_input.light] * n,
                    "prediction_offset": prediction_offsets,
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
            ],
            model=model_name,
        )


runtime = ModelRuntime()
