from sklearn.pipeline import Pipeline
import cloudpickle

import logging
from api.config import (
    AZURE_STORAGE_CONNECTION_STRING,
    AZURE_BLOB_CONTAINER_NAME,
    DEFAULT_MODEL,
)
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient


class ModelNotFoundError(BaseException):
    pass


logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)

blob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)
container_client: ContainerClient = blob_service_client.get_container_client(
    container=AZURE_BLOB_CONTAINER_NAME
)

_models_cache: dict[str, Pipeline] = {}


def _get_model_info(model: str | None) -> tuple[str, int | None, int | None]:
    if model is None:
        model = DEFAULT_MODEL

    model_info = model.split("-")
    if len(model_info) > 1:
        versions = model_info.pop().split("_")
        if len(versions) == 1:
            versions.append(None)
        model_info.extend(versions)
    else:
        model_info.extend([None] * 2)

    return tuple(model_info)


def get_available_models() -> list[str]:
    return [
        _get_model_info(f.removesuffix(".pkl"))
        for f in container_client.list_blob_names()
    ]


def get_model(model: str) -> Pipeline:
    if model not in _models_cache:
        blob_client: BlobClient = blob_service_client.get_blob_client(
            container=AZURE_BLOB_CONTAINER_NAME, blob=f"{model}.pkl"
        )

        data = blob_client.download_blob().readall()
        _models_cache[model] = cloudpickle.loads(data)

    return _models_cache[model]


def find_model(model: str | None) -> tuple[Pipeline, str]:
    models = get_available_models()

    model_info = _get_model_info(model)
    for i, info in enumerate(model_info):
        if i != 0 and info is None:
            (info,) = sorted(
                [model[i] for model in models],
                reverse=True,
            )[:1] or [None]
        models = [model for model in models if info == model[i]]

    if len(models) == 0 or len(models) > 1:
        raise ModelNotFoundError(f"Model '{model}' not found")

    name, major_version, minor_version = models[0]
    final_name = f"{name}-{major_version}_{minor_version}"
    return get_model(final_name), final_name
