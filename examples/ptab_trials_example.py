"""Example usage of pyUSPTO for PTAB trial proceedings.

Demonstrates the PTABTrialsClient for searching proceedings, documents,
and decisions across IPR, PGR, CBM, and DER trial types.
"""

import os

from pyUSPTO import PTABTrialsClient, USPTOConfig

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "API key is not set. Set the USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = PTABTrialsClient(config=config)

print("-" * 40)
print("Example 1: Search trial proceedings")
print("-" * 40)

# Search for IPR proceedings filed in 2023
response = client.search_proceedings(
    trial_type_code_q="IPR",
    petition_filing_date_from_q="2023-01-01",
    petition_filing_date_to_q="2023-12-31",
    limit=5,
)

print(f"\nFound {response.count} IPR proceedings filed in 2023")
print(f"Displaying first {len(response.patent_trial_proceeding_data_bag)} results:")

for proceeding in response.patent_trial_proceeding_data_bag:
    print(f"\n  Trial Number: {proceeding.trial_number}")

    if proceeding.trial_meta_data:
        meta = proceeding.trial_meta_data
        print(f"  Trial Type: {meta.trial_type_code}")
        print(f"  Status: {meta.trial_status_category}")
        print(f"  Filing Date: {meta.petition_filing_date}")

    if proceeding.patent_owner_data:
        print(f"  Patent Owner: {proceeding.patent_owner_data.patent_owner_name}")
        print(f"  Patent Number: {proceeding.patent_owner_data.patent_number}")

    if proceeding.regular_petitioner_data:
        print(
            f"  Petitioner: {proceeding.regular_petitioner_data.real_party_in_interest_name}"
        )

print("-" * 40)
print("Example 2: Search trial documents")
print("-" * 40)

response = client.search_documents(
    trial_number_q="IPR2025-01319",
    limit=10,
)

print(f"\nFound {response.count} documents")
print(f"Displaying first {len(response.patent_trial_document_data_bag)} results:")

for item in response.patent_trial_document_data_bag:
    print(f"\n  Trial Number: {item.trial_number}")

    if item.document_data:
        doc = item.document_data
        print(f"  Document Type: {doc.document_type_description_text}")
        print(f"  Filing Date: {doc.document_filing_date}")

        if doc.file_download_uri:
            print(f"  Download URL: {doc.file_download_uri}")

print("-" * 40)
print("Example 3: Search trial decisions")
print("-" * 40)

response = client.search_decisions(
    trial_type_code_q="IPR",
    decision_type_category_q="Decision",
    patent_owner_name_q="*",
    trial_status_category_q="Terminated",
    decision_date_from_q="2023-01-01",
    limit=5,
)

print(f"\nFound {response.count} Decisions in IPR proceedings")
print(f"Displaying first {len(response.patent_trial_document_data_bag)} results:")

for item in response.patent_trial_document_data_bag:
    print(f"\n  Trial Number: {item.trial_number}")

    if item.trial_meta_data:
        print(f"  Trial Type: {item.trial_meta_data.trial_type_code}")
        print(f"  Status: {item.trial_meta_data.trial_status_category}")

    if item.decision_data:
        decision = item.decision_data
        print(f"  Decision Type: {decision.decision_type_category}")
        print(f"  Decision Date: {decision.decision_issue_date}")

print("-" * 40)
print("Example 4: Paginate through proceedings")
print("-" * 40)

max_items = 10
count = 0
for proceeding in client.paginate_proceedings(
    trial_type_code_q="IPR",
    petition_filing_date_from_q="2024-01-01",
    limit=5,
):
    count += 1
    print(f"  {count}. {proceeding.trial_number}")

    if count >= max_items:
        print(f"  ... (stopping at {max_items} items)")
        break

print(f"Retrieved {count} proceedings via pagination")

print("-" * 40)
print("Example 5: Advanced search with sort and fields")
print("-" * 40)

response = client.search_proceedings(
    trial_type_code_q="PGR",
    trial_status_category_q="Terminated",
    sort="trialMetaData.petitionFilingDate desc",
    fields="trialNumber,lastModifiedDateTime",
    limit=3,
)

print(f"\nFound {response.count} Terminated PGR proceedings")
print(f"Displaying first {len(response.patent_trial_proceeding_data_bag)} results:")

for proceeding in response.patent_trial_proceeding_data_bag:
    print(f"\n  Trial Number: {proceeding.trial_number}")
    print(f"  Last Modified: {proceeding.last_modified_date_time}")
