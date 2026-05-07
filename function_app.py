from __future__ import annotations

import json
from typing import Optional, Union

import azure.functions as func
from pydantic import ValidationError

from api.auth import require_api_key
from api.schemas import PredictionRequest
from api.services.prediction_service import (
    generate_mock_prediction,
    get_mock_historical,
    get_mock_latest,
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


@app.route(route="v1/latest", methods=["GET"])
def get_latest(req: func.HttpRequest) -> func.HttpResponse:
    auth_error = _validate_api_key(req)
    if auth_error:
        return auth_error

    latest = get_mock_latest()
    return _json_response(_model_to_dict(latest))


@app.route(route="v1/historical", methods=["GET"])
def get_historical(req: func.HttpRequest) -> func.HttpResponse:
    auth_error = _validate_api_key(req)
    if auth_error:
        return auth_error

    start_unix = req.params.get("startUnix")
    end_unix = req.params.get("endUnix")

    if start_unix is None or end_unix is None:
        return _json_response(
            {"detail": "Both startUnix and endUnix query parameters are required."},
            status_code=400,
        )

    try:
        start_unix_int = int(start_unix)
        end_unix_int = int(end_unix)
    except ValueError:
        return _json_response(
            {"detail": "startUnix and endUnix must be integers."},
            status_code=400,
        )

    historical = get_mock_historical(start_unix_int, end_unix_int)
    return _json_response([_model_to_dict(point) for point in historical])
