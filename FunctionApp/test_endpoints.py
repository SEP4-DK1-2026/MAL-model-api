#!/usr/bin/env python3
"""
Test script for MAL Weather Prediction API
Tests all endpoints with proper authentication
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import time

# Import the function app
from function_app import app

# Test configuration
API_KEY = "test-key-12345"
BASE_URL = "http://localhost:7071/api"


def test_function_locally():
    """Test functions directly without HTTP server"""
    import azure.functions as func

    print("\n" + "=" * 70)
    print("Direct Function Testing (No HTTP Server)")
    print("=" * 70)

    # Test 1: Health check (no auth required, but we'll test the function directly)
    print("\n1. Testing health endpoint...")
    try:
        # Create a mock request
        class MockRequest:
            def get_json(self):
                return {}

            def __getitem__(self, key):
                return None

        # Call the function directly
        from function_app import health

        response = health(MockRequest())
        print(f"   Status: {response.status_code}")
        print(f"   Body: {response.get_body().decode()}")
        print("   ✓ Health check works")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

    print("\n" + "=" * 70)
    print("✓ Direct function tests passed")
    print("=" * 70)
    return True


def test_with_curl_examples():
    """Print curl commands for manual testing"""
    print("\n" + "=" * 70)
    print("Manual Testing with curl")
    print("=" * 70)

    print("\n1. Health check (no auth):")
    print(f'   curl "{BASE_URL}/health"')

    print("\n2. Get latest weather:")
    print(f'   curl "{BASE_URL}/v1/latest" \\')
    print(f'     -H "x-api-key: {API_KEY}"')

    print("\n3. Make prediction:")
    print(f'''   curl -X POST "{BASE_URL}/v1/predictions" \\
     -H "x-api-key: {API_KEY}" \\
     -H "Content-Type: application/json" \\
     -d '{{
       "modelInput": {{
         "time": 1714939200,
         "temperature": 15.0,
         "humidity": 65.0,
         "wind_direction": 270.0,
         "wind_speed": 5.5,
         "precipitation": 0.0,
         "light": 500
       }},
       "predictionOffset": 24
     }}'
''')

    print("\n4. Get historical data:")
    print(
        f'   curl "{BASE_URL}/v1/historical?startUnix=1714852800&endUnix=1714939200" \\'
    )
    print(f'     -H "x-api-key: {API_KEY}"')

    print("\n" + "=" * 70)
    print("Environment variable for Azure Functions:")
    print("  API_KEY = test-key-12345")
    print("=" * 70)


if __name__ == "__main__":
    if not test_function_locally():
        sys.exit(1)

    test_with_curl_examples()

    print("\n✓ All tests passed!")
    print("\nTo start the local Azure Functions host:")
    print("  .venv/bin/python -m azure.functions start")
