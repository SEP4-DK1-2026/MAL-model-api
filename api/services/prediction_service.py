from __future__ import annotations

from api.schemas import ModelInput, PredictionResponse
from api.services.model_runtime import runtime


def make_predition(
    model_input: ModelInput, prediction_offsets: list[int], model: str | None
) -> PredictionResponse:
    return runtime.predict(model_input, prediction_offsets, model)
