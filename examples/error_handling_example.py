"""Error handling example for pyUSPTO.

This example demonstrates how to handle common errors when using the USPTO API clients.
"""

import os
import time

from pyUSPTO.clients import PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.exceptions import (
    USPTOApiAuthError,
    USPTOApiNotFoundError,
    USPTOApiRateLimitError,
    USPTOConnectionError,
    USPTOTimeout,
)
from pyUSPTO.http_config import HTTPConfig

# Initialize client
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
client = PatentDataClient(api_key=api_key)

# Example 1: Handle authentication errors
print("Example 1: Authentication errors")
try:
    # This will fail with invalid API key
    bad_client = PatentDataClient(api_key="invalid_key")
    bad_client.search_applications(limit=1)
except USPTOApiAuthError as e:
    print(f"Authentication failed: {e}")
    print("Check your API key and try again.")

# Example 2: Handle not found errors
print("\nExample 2: Not found errors")
try:
    # Try to get a non-existent application
    client.get_application_by_number("99999999")
except USPTOApiNotFoundError as e:
    print(f"Resource not found: {e}")
    print("The application number may be invalid or not in the system.")

# Example 3: Handle rate limiting with retry
print("\nExample 3: Rate limiting")
try:
    # If you hit rate limits, the API returns 429
    results = client.search_applications(limit=100)
    print(f"Retrieved {results.count} results")
except USPTOApiRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print("Waiting 60 seconds before retry...")
    time.sleep(60)
    # Retry the request
    results = client.search_applications(limit=100)
    print(f"Retry successful: {results.count} results")

# Example 4: Handle timeouts with custom configuration
print("\nExample 4: Timeout handling")
# Configure shorter timeout for demonstration
http_config = HTTPConfig(timeout=1)  # Very short timeout
config = USPTOConfig(api_key=api_key, http_config=http_config)
timeout_client = PatentDataClient(config=config)

try:
    timeout_client.search_applications(limit=100)
except USPTOTimeout as e:
    print(f"Request timed out: {e}")
    print("Consider increasing timeout or checking network connection.")

# Example 5: Handle connection errors
print("\nExample 5: Connection errors")
try:
    # This might fail due to network issues
    client.search_applications(limit=10)
except USPTOConnectionError as e:
    print(f"Connection error: {e}")
    print("Check your network connection and try again.")

# Example 6: Catch-all for unexpected errors
print("\nExample 6: General error handling")
try:
    results = client.search_applications(patent_number_q="10000000", limit=5)
    if results.count > 0:
        print(f"Found {results.count} matching patents")
    else:
        print("No results found")
except USPTOApiRateLimitError:
    print("Rate limited - wait and retry")
except USPTOApiAuthError:
    print("Authentication failed - check API key")
except USPTOTimeout:
    print("Request timed out - try again")
except USPTOConnectionError:
    print("Connection failed - check network")
except Exception as e:
    # Catch any other unexpected errors
    print(f"Unexpected error: {e}")
