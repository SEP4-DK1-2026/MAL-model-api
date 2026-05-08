from __future__ import annotations

import json
from typing import Union

import azure.functions as func
from pydantic import ValidationError

from api.schemas import PredictionRequest
from api.services.prediction_service import make_predition
from api.services.model_service import ModelNotFoundError

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def _json_response(
    payload: Union[dict, list], status_code: int = 200
) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps(payload),
        status_code=status_code,
        mimetype="application/json",
    )


def _model_to_dict(model: object) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()  # Pydantic v2
    return model.dict()  # Pydantic v1


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    return _json_response({"status": "ok"})


@app.route(route="v1/predictions", methods=["POST"])
def get_prediction(req: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = req.get_json()
    except ValueError:
        return _json_response({"detail": "Invalid JSON body."}, status_code=400)

    try:
        request_model = PredictionRequest(**payload)
    except ValidationError as exc:
        return _json_response({"detail": exc.errors()}, status_code=422)

    try:
        prediction = make_predition(
            request_model.model_input,
            request_model.prediction_offsets,
            request_model.model,
        )
        return _json_response(_model_to_dict(prediction))
    except ModelNotFoundError as e:
        return _json_response({"detail": str(e)}, status_code=400)
