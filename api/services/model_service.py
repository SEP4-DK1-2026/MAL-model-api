import os
import cloudpickle
from pathlib import Path
from sklearn.pipeline import Pipeline


class ModelNotFoundError(BaseException):
    pass


_models_cache: dict[str, Pipeline] = {}
MODELS_PATH: str = str(Path(__file__).resolve().parent.joinpath("./models"))
DEFAULT_MODEL: str = "DMI"


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


def get_model(model: str | None) -> tuple[Pipeline, str]:
    models = [
        _get_model_info(f.removesuffix(".pkl"))
        for f in os.listdir(MODELS_PATH)
        if Path(MODELS_PATH, f).is_file()
    ]

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
    if final_name not in _models_cache:
        with open(Path(MODELS_PATH, f"{final_name}.pkl"), "rb") as f:
            _models_cache[final_name] = cloudpickle.load(f)

    return _models_cache[final_name], final_name
