"""Example usage of pyUSPTO for PTAB ex parte appeals.

Demonstrates the PTABAppealsClient for searching appeal decisions
by technology center, decision type, and application number.
"""

import os

from pyUSPTO import PTABAppealsClient, USPTOConfig

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "API key is not set. Set the USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = PTABAppealsClient(config=config)

print("-" * 40)
print("Example 1: Search by technology center")
print("-" * 40)

# Search for decisions from Technology Center 3600 (Business Methods/Software)
response = client.search_decisions(
    technology_center_number_q="3600",
    decision_date_from_q="2023-01-01",
    decision_date_to_q="2023-12-31",
    limit=5,
)

print(f"\nFound {response.count} appeal decisions from TC 3600 in 2023")
print(f"Displaying first {len(response.patent_appeal_data_bag)} results:")

for decision in response.patent_appeal_data_bag:
    print(f"\n  Appeal Number: {decision.appeal_number}")

    if decision.appeal_meta_data:
        meta = decision.appeal_meta_data
        print(f"  Application Type: {meta.application_type_category}")
        print(f"  Filing Date: {meta.appeal_filing_date}")

    if decision.appellant_data:
        appellant = decision.appellant_data
        print(f"  Application Number: {appellant.application_number_text}")
        print(f"  Technology Center: {appellant.technology_center_number}")

        if appellant.inventor_name:
            print(f"  Inventor: {appellant.inventor_name}")

    if decision.decision_data:
        dec = decision.decision_data
        print(f"  Decision Type: {dec.decision_type_category}")
        print(f"  Decision Date: {dec.decision_issue_date}")

print("-" * 40)
print("Example 2: Search by decision type")
print("-" * 40)

response = client.search_decisions(
    decision_type_category_q="Decision",
    decision_date_from_q="2024-01-01",
    limit=5,
)

print(f"\nFound {response.count} 'Decision's since 2024")
print(f"Displaying first {len(response.patent_appeal_data_bag)} results:")

for decision in response.patent_appeal_data_bag:
    print(f"\n  Appeal Number: {decision.appeal_number}")

    if decision.appellant_data:
        print(f"  Application: {decision.appellant_data.application_number_text}")
        print(f"  Inventor: {decision.appellant_data.inventor_name or 'N/A'}")

    if decision.decision_data:
        print(f"  Decision: {decision.decision_data.decision_type_category}")
        print(f"  Outcome: {decision.decision_data.appeal_outcome_category}")
        print(f"  Date: {decision.decision_data.decision_issue_date}")

print("-" * 40)
print("Example 3: Search by application number")
print("-" * 40)

# Search for decisions related to applications starting with "15"
response = client.search_decisions(
    application_number_text_q="15*",
    decision_date_from_q="2023-01-01",
    limit=3,
)

print(f"\nFound {response.count} decisions for applications starting with '15/'")
print(f"Displaying first {len(response.patent_appeal_data_bag)} results:")

for decision in response.patent_appeal_data_bag:
    print(f"\n  Appeal Number: {decision.appeal_number}")

    if decision.appellant_data:
        print(f"  Application: {decision.appellant_data.application_number_text}")
        print(f"  TC Number: {decision.appellant_data.technology_center_number}")

    if decision.document_data:
        doc = decision.document_data
        print(f"  Document Name: {doc.document_name}")
        if doc.file_download_uri:
            print(f"  Download URL: {doc.file_download_uri}")

print("-" * 40)
print("Example 4: Paginate through decisions")
print("-" * 40)

max_items = 10
count = 0
for decision in client.paginate_decisions(
    decision_date_from_q="2024-01-01",
    limit=5,
):
    count += 1
    decision_type = (
        decision.decision_data.decision_type_category
        if decision.decision_data
        else "N/A"
    )
    print(f"  {count}. {decision.appeal_number} - {decision_type}")

    if count >= max_items:
        print(f"  ... (stopping at {max_items} items)")
        break

print(f"Retrieved {count} decisions via pagination")

print("-" * 40)
print("Example 5: Advanced search with multiple criteria")
print("-" * 40)

response = client.search_decisions(
    technology_center_number_q="2100",
    decision_type_category_q="Decision",
    decision_date_from_q="2023-01-01",
    decision_date_to_q="2023-12-31",
    sort="decisionData.decisionIssueDate desc",
    limit=3,
)

print(f"\nFound {response.count} Decisions from TC 2100 (Electronics) in 2023")
print(f"Displaying first {len(response.patent_appeal_data_bag)} results:")

for decision in response.patent_appeal_data_bag:
    print(f"\n  Appeal Number: {decision.appeal_number}")

    if decision.appellant_data:
        print(f"  Application: {decision.appellant_data.application_number_text}")

    if decision.decision_data:
        print(f"  Decision: {decision.decision_data.decision_type_category}")
        print(f"  Date: {decision.decision_data.decision_issue_date}")

print("-" * 40)
print("Example 6: Direct query string")
print("-" * 40)

# Use a direct query string for more complex searches
response = client.search_decisions(
    query="appellantData.technologyCenterNumber:3600 AND decisionData.appealOutcomeCategory:(Affirmed OR Reversed)",
    limit=10,
)

print(f"\nFound {response.count} Affirmed/Reversed decisions from TC 3600")
print(f"Displaying first {len(response.patent_appeal_data_bag)} results:")

for decision in response.patent_appeal_data_bag:
    print(f"\n  Appeal Number: {decision.appeal_number}")

    if decision.appellant_data:
        print(f"  Application: {decision.appellant_data.application_number_text}")

    if decision.decision_data:
        print(f"  Decision: {decision.decision_data.decision_type_category}")
        print(f"  Outcome: {decision.decision_data.appeal_outcome_category}")
