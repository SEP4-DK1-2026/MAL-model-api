import os
import io
import pickle
import re

from azure.storage.blob import BlobServiceClient

blob_storage_service = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])

_model_cache = {}

VERSION_PATTERN = re.compile(r"(.+)-(\d+)_(\d+)\.pkl")

def get_latest_model_blob(model_group: str):
    
    container_client = blob_storage_service.get_container_client("models")
    
    blobs = container_client.list_blobs(name_starts_with=f"{model_group}/")
    
    candidates = []
    
    for blob in blobs:
        
        filename = blob.name.split("/")[-1]
        
        match = VERSION_PATTERN.match(filename)
        
        if not match:
            continue
        
        major, minor = int(match.group(2)), int(match.group(3))
        
        candidates.append((major, minor, blob.name))
        
        if not candidates:
            raise Exception(f"No models found for {model_group}")
        
        candidates.sort(reverse=True)
        
        return candidates[0][2]


def load_latest_model(blob_group: str):
    
    blob_path = get_latest_model_blob(blob_group)
    
    if blob_path in _model_cache:
        return _model_cache[blob_path]
    
    blob_client = blob_storage_service.get_blob_client(container="models", blob=blob_path)
    
    data = blob_client.download_blob().readall()
    model = pickle.load(io.BytesIO(data))
    _model_cache[blob_path] = model

    return model