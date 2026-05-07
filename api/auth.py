from typing import Optional, Tuple

from api.config import API_KEY


def require_api_key(header_value: Optional[str]) -> Tuple[bool, str]:
    if not API_KEY:
        return False, "Server API key is not configured."
    if header_value != API_KEY:
        return False, "Invalid or missing API key."
    return True, ""
