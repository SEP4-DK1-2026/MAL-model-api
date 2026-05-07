import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH: str = os.getenv("MODEL_PATH")
MODEL_BLOB_URL: str = os.getenv("MODEL_BLOB_URL")
