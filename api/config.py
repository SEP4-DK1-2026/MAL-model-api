import os
from dotenv import load_dotenv

load_dotenv()

API_KEY: str = os.getenv("API_KEY")
MODEL_PATH: str = os.getenv("MODEL_PATH")
MODEL_BLOB_URL: str = os.getenv("MODEL_BLOB_URL")
