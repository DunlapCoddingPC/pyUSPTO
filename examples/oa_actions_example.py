"""Example usage of pyUSPTO for Office Action Text Retrieval.

Demonstrates the OAActionsClient for searching full-text office action
documents, filtering by various criteria, inspecting section data,
and paginating through results.
"""

import os

from pyUSPTO import OAActionsClient, USPTOConfig

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError("API key is not set. Set the USPTO_API_KEY environment variable.")
config = USPTOConfig(api_key=api_key)
client = OAActionsClient(config=config)

print("-" * 40)
print("Example 1: Search by application number")
print("-" * 40)

response = client.search(patent_application_number_q="11363598")
print(f"Found {response.num_found} office actions for application 11363598.")
for record in response.docs[:3]:
    print(f"\n  Doc Code: {record.legacy_document_code_identifier}")
    print(f"  Submission Date: {record.submission_date}")
    print(f"  Art Unit: {record.group_art_unit_number}")
    if record.section:
        if record.section.section_102_rejection_text:
            print("  Has § 102 rejection text.")
        if record.section.section_103_rejection_text:
            print("  Has § 103 rejection text.")

print("-" * 40)
print("Example 2: Search by document code (CTNF) and tech center")
print("-" * 40)

response = client.search(
    tech_center_q="2800",
    legacy_document_code_identifier_q="CTNF",
    rows=5,
)
print(f"Found {response.num_found} CTNF office actions in tech center 2800.")
for record in response.docs:
    print(
        f"  App {record.patent_application_number}: "
        f"AU {record.group_art_unit_number}, "
        f"submitted {record.submission_date}"
    )

print("-" * 40)
print("Example 3: Search by submission date range")
print("-" * 40)

response = client.search(
    submission_date_from_q="2010-01-01",
    submission_date_to_q="2010-12-31",
    rows=5,
)
print(f"Found {response.num_found} office actions submitted in 2010.")

print("-" * 40)
print("Example 4: Search with sort")
print("-" * 40)

response = client.search(
    tech_center_q="1700",
    sort="submissionDate desc",
    rows=5,
)
print(f"Found {response.num_found} office actions in tech center 1700 (newest first).")
for record in response.docs:
    print(f"  {record.submission_date}: {record.invention_title}")

print("-" * 40)
print("Example 5: Inspect section data")
print("-" * 40)

response = client.search(
    criteria='id:"9c27199b54dc83c9a6f643b828990d0322071461557b31ead3428885"',
    rows=1,
)
if response.docs:
    record = response.docs[0]
    print(f"Record: {record.id}")
    print(f"  Patent Number: {record.patent_number}")
    print(f"  Invention Title: {record.invention_title}")
    if record.section:
        print("  Section 102 text (first 200 chars):")
        for text in record.section.section_102_rejection_text:
            if text:
                print(f"    {text[:200]}...")

print("-" * 40)
print("Example 6: Paginate through results")
print("-" * 40)

max_items = 30
count = 0
for record in client.paginate(tech_center_q="1700", rows=10):
    count += 1
    if count >= max_items:
        print(f"  ... (stopping at {max_items} items)")
        break

print(f"Retrieved {count} office action records via pagination.")

print("-" * 40)
print("Example 7: Get available fields")
print("-" * 40)

fields_response = client.get_fields()
print(f"API Status: {fields_response.api_status}")
print(f"Field Count: {fields_response.field_count}")
print(f"Last Updated: {fields_response.last_data_updated_date}")
print(f"Sample fields: {fields_response.fields[:5]}")
