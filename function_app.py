from __future__ import annotations

import json
from typing import Optional, Union

import azure.functions as func
from pydantic import ValidationError

from api.auth import require_api_key
from api.schemas import PredictionRequest
from api.services.prediction_service import (
    generate_mock_prediction,
    load_models_if_needed,
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def _validate_api_key(req: func.HttpRequest) -> Optional[func.HttpResponse]:
    is_valid, message = require_api_key(req.headers.get("x-api-key"))
    if is_valid:
        return None

    status_code = 500 if message == "Server API key is not configured." else 401
    return func.HttpResponse(
        body=json.dumps({"detail": message}),
        status_code=status_code,
        mimetype="application/json",
    )


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


@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return _json_response({"status": "ok"})


@app.route(route="v1/predictions", methods=["POST"])
def get_prediction(req: func.HttpRequest) -> func.HttpResponse:
    auth_error = _validate_api_key(req)
    if auth_error:
        return auth_error

    try:
        payload = req.get_json()
    except ValueError:
        return _json_response({"detail": "Invalid JSON body."}, status_code=400)

    try:
        request_model = PredictionRequest(**payload)
    except ValidationError as exc:
        return _json_response({"detail": exc.errors()}, status_code=422)

    load_models_if_needed()
    prediction = generate_mock_prediction(
        request_model.predictionOffset,
        request_model.modelInput,
    )
    return _json_response(_model_to_dict(prediction))
