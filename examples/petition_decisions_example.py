"""Example usage of the PetitionDecisionsClient."""

import json
import os

from pyUSPTO.clients.petition_decisions import PetitionDecisionsClient
from pyUSPTO.config import USPTOConfig

# Initialize client using API key from environment or placeholder
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
client = PetitionDecisionsClient(api_key=api_key)

# Search for decisions containing 'highway'
try:
    response = client.search_decisions(query="highway", limit=5)
    print(json.dumps(response.to_dict(), indent=2))
except Exception as exc:  # pragma: no cover - example usage
    print(f"Error fetching decisions: {exc}")
