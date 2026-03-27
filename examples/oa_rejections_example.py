"""Examples for the OARejectionsClient.

This module demonstrates how to use the OARejectionsClient to search for
rejection-level data from USPTO Office Actions.
"""

from pyUSPTO import OARejectionsClient, USPTOConfig

config = USPTOConfig.from_env()
client = OARejectionsClient(config=config)

# --- Example 1: Search by application number ---
response = client.search(patent_application_number_q="12190351")
print(f"Found {response.count} records for application 12190351")
for record in response.docs:
    print(f"  {record.id}: {record.legacy_document_code_identifier}")

# --- Example 2: Search by document code and date range ---
response = client.search(
    legacy_document_code_identifier_q="CTNF",
    submission_date_from_q="2020-01-01",
    submission_date_to_q="2020-12-31",
    rows=5,
)
print(f"\nFound {response.count} CTNF rejections in 2020")

# --- Example 3: Search with a direct criteria string ---
response = client.search(
    criteria="hasRej103:1 AND groupArtUnitNumber:1713",
    rows=5,
)
print(f"\nFound {response.count} 103-rejection records in art unit 1713")

# --- Example 4: Inspect rejection flags ---
response = client.search(patent_application_number_q="12190351", rows=1)
if response.docs:
    record = response.docs[0]
    print(f"\nRecord: {record.id}")
    print(f"  101 rejection: {record.has_rej_101}")
    print(f"  102 rejection: {record.has_rej_102}")
    print(f"  103 rejection: {record.has_rej_103}")
    print(f"  112 rejection: {record.has_rej_112}")
    print(f"  Alice indicator: {record.alice_indicator}")
    print(f"  Claims: {record.claim_number_array_document}")

# --- Example 5: Search with POST body ---
response = client.search(
    post_body={"criteria": "patentApplicationNumber:12190351", "rows": 10}
)
print(f"\nFound {response.count} records via POST body")

# --- Example 6: Paginate through results ---
count = 0
for record in client.paginate(
    legal_section_code_q="103",
    submission_date_from_q="2020-01-01",
    submission_date_to_q="2020-01-31",
    rows=25,
):
    count += 1
    if count >= 50:
        break
print(f"\nIterated through {count} records")

# --- Example 7: Get available fields ---
fields = client.get_fields()
print(f"\nAPI: {fields.api_key} ({fields.api_version_number})")
print(f"Status: {fields.api_status}")
print(f"Fields ({fields.field_count}): {fields.fields[:5]}...")
