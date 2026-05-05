from typing import Optional, Tuple

import os


def require_api_key(header_value: Optional[str]) -> Tuple[bool, str]:
    expected = os.getenv("API_KEY")
    if not expected:
        return False, "Server API key is not configured."
    if header_value != expected:
        return False, "Invalid or missing API key."
    return True, ""
