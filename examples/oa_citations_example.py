"""Example usage of pyUSPTO for Office Action Citations.

Demonstrates the OACitationsClient for searching citation data from
Office Actions, filtering by various criteria, and paginating through results.
"""

import os

from pyUSPTO import OACitationsClient, USPTOConfig

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError("API key is not set. Set the USPTO_API_KEY environment variable.")
config = USPTOConfig(api_key=api_key)
client = OACitationsClient(config=config)

print("-" * 40)
print("Example 1: Search by application number")
print("-" * 40)

response = client.search(patent_application_number_q="17519936")
print(f"Found {response.num_found} citations for application 17519936.")
for record in response.docs[:3]:
    print(f"\n  Legal Section: {record.legal_section_code}")
    print(f"  Action Type: {record.action_type_category}")
    print(f"  Reference: {record.reference_identifier}")
    print(f"  Examiner Cited: {record.examiner_cited_reference_indicator}")

print("-" * 40)
print("Example 2: Search by legal section code and tech center")
print("-" * 40)

response = client.search(
    tech_center_q="2800",
    legal_section_code_q="103",
    rows=5,
)
print(f"Found {response.num_found} section 103 citations in tech center 2800.")
for record in response.docs:
    print(
        f"  App {record.patent_application_number}: "
        f"AU {record.group_art_unit_number}, "
        f"ref {record.parsed_reference_identifier}"
    )

print("-" * 40)
print("Example 3: Search by examiner-cited indicator")
print("-" * 40)

response = client.search(
    examiner_cited_reference_indicator_q=True,
    tech_center_q="1700",
    rows=5,
)
print(f"Found {response.num_found} examiner-cited references in tech center 1700.")
for record in response.docs:
    print(f"  {record.reference_identifier}")

print("-" * 40)
print("Example 4: Search by create date range")
print("-" * 40)

response = client.search(
    create_date_time_from_q="2025-07-01",
    create_date_time_to_q="2025-07-04",
    rows=5,
)
print(f"Found {response.num_found} citations created 2025-07-01 to 2025-07-04.")

print("-" * 40)
print("Example 5: Search with sort")
print("-" * 40)

response = client.search(
    tech_center_q="2800",
    sort="createDateTime desc",
    rows=5,
)
print(f"Found {response.num_found} citations in tech center 2800 (newest first).")
for record in response.docs:
    print(f"  {record.create_date_time}: {record.patent_application_number}")

print("-" * 40)
print("Example 6: Paginate through results")
print("-" * 40)

max_items = 30
count = 0
for record in client.paginate(tech_center_q="2800", rows=10):
    count += 1
    if count >= max_items:
        print(f"  ... (stopping at {max_items} items)")
        break

print(f"Retrieved {count} citation records via pagination.")

print("-" * 40)
print("Example 7: Get available fields")
print("-" * 40)

fields_response = client.get_fields()
print(f"API Status: {fields_response.api_status}")
print(f"Field Count: {fields_response.field_count}")
print(f"Last Updated: {fields_response.last_data_updated_date}")
print(f"Sample fields: {fields_response.fields[:5]}")
