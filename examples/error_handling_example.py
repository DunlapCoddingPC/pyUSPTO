"""Example usage of pyUSPTO for error handling patterns.

Demonstrates how to handle common errors when using the USPTO API clients.
"""

import os
import time

from pyUSPTO import (
    HTTPConfig,
    PatentDataClient,
    USPTOApiAuthError,
    USPTOApiNotFoundError,
    USPTOApiRateLimitError,
    USPTOConfig,
    USPTOConnectionError,
    USPTOTimeout,
)

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
config = USPTOConfig(api_key=api_key)
client = PatentDataClient(config=config)

print("-" * 40)
print("Example 1: Authentication errors")
print("-" * 40)

try:
    bad_client = PatentDataClient(config=config)
    bad_client.search_applications(limit=1)
except USPTOApiAuthError as e:
    print(f"Authentication failed: {e}")
    print("Check your API key and try again.")

print("-" * 40)
print("Example 2: Not found errors")
print("-" * 40)

try:
    client.get_application_by_number("99999999")
except USPTOApiNotFoundError as e:
    print(f"Resource not found: {e}")
    print("The application number may be invalid or not in the system.")

print("-" * 40)
print("Example 3: Rate limiting")
print("-" * 40)

try:
    results = client.search_applications(limit=100)
    print(f"Retrieved {results.count} results")
except USPTOApiRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print("Waiting 60 seconds before retry...")
    time.sleep(60)
    results = client.search_applications(limit=100)
    print(f"Retry successful: {results.count} results")

print("-" * 40)
print("Example 4: Timeout handling")
print("-" * 40)

# Configure shorter timeout for demonstration
http_config = HTTPConfig(timeout=1)
config = USPTOConfig(api_key=api_key, http_config=http_config)
timeout_client = PatentDataClient(config=config)

try:
    timeout_client.search_applications(limit=100)
except USPTOTimeout as e:
    print(f"Request timed out: {e}")
    print("Consider increasing timeout or checking network connection.")

print("-" * 40)
print("Example 5: Connection errors")
print("-" * 40)

try:
    client.search_applications(limit=10)
except USPTOConnectionError as e:
    print(f"Connection error: {e}")
    print("Check your network connection and try again.")

print("-" * 40)
print("Example 6: General error handling")
print("-" * 40)

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
    print(f"Unexpected error: {e}")
