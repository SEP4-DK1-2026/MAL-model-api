from __future__ import annotations

from api.schemas import ModelInput, PredictionResponse
from api.services.model_runtime import runtime


def load_models_if_needed() -> None:
    runtime.load_if_needed()


def make_predition(
    prediction_offset: list[int], model_input: ModelInput
) -> PredictionResponse:
    return runtime.predict(prediction_offset, model_input)
