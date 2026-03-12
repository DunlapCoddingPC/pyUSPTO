"""Example usage of pyUSPTO for PTAB interferences.

Demonstrates the PTABInterferencesClient for searching interference decisions
by outcome, party name, and application number.
"""

import os

from pyUSPTO import PTABInterferencesClient, USPTOConfig

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "API key is not set. Set the USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = PTABInterferencesClient(config=config)

print("-" * 40)
print("Example 1: Search interference decisions")
print("-" * 40)

# Search for recent interference decisions
response = client.search_decisions(
    decision_date_from_q="2023-01-01",
    limit=5,
)

print(f"\nFound {response.count} interference decisions since 2023")
print(f"Displaying first {len(response.patent_interference_data_bag)} results:")

for decision in response.patent_interference_data_bag:
    print(f"\n  Interference Number: {decision.interference_number}")

    if decision.interference_meta_data:
        meta = decision.interference_meta_data
        print(f"  Style Name: {meta.interference_style_name}")
        print(f"  Last Modified: {meta.interference_last_modified_date}")

    if decision.senior_party_data:
        senior = decision.senior_party_data
        print(f"  Senior Party: {senior.patent_owner_name}")
        if senior.patent_number:
            print(f"  Senior Patent: {senior.patent_number}")

    if decision.junior_party_data:
        junior = decision.junior_party_data
        print(f"  Junior Party: {junior.patent_owner_name}")
        if junior.publication_number:
            print(f"  Junior Publication: {junior.publication_number}")

    if decision.document_data:
        doc = decision.document_data
        print(f"  Outcome: {doc.interference_outcome_category}")
        print(f"  Decision Type: {doc.decision_type_category}")

print("-" * 40)
print("Example 2: Search by outcome")
print("-" * 40)

response = client.search_decisions(
    interference_outcome_category_q="Final Decision",
    decision_date_from_q="2012-01-01",
    limit=3,
)

print(f"\nFound {response.count} final decisions since 2012")
print(f"Displaying first {len(response.patent_interference_data_bag)} results:")

for decision in response.patent_interference_data_bag:
    print(f"\n  Interference Number: {decision.interference_number}")

    if decision.senior_party_data:
        print(f"  Senior Party: {decision.senior_party_data.patent_owner_name}")
        print(
            f"  Senior Application: {decision.senior_party_data.application_number_text}"
        )

    if decision.junior_party_data:
        print(f"  Junior Party: {decision.junior_party_data.patent_owner_name}")

    if decision.document_data:
        print(f"  Outcome: {decision.document_data.interference_outcome_category}")
        print(f"  Decision Date: {decision.document_data.decision_issue_date}")

print("-" * 40)
print("Example 3: Search by party name")
print("-" * 40)

# Search for decisions involving a specific senior party
response = client.search_decisions(
    senior_party_name_q="*Corp*",
    limit=3,
)

print(f"\nFound {response.count} decisions with 'Corp' in senior party name")
print(f"Displaying first {len(response.patent_interference_data_bag)} results:")

for decision in response.patent_interference_data_bag:
    print(f"\n  Interference Number: {decision.interference_number}")

    if decision.senior_party_data:
        senior = decision.senior_party_data
        print(f"  Senior Party: {senior.patent_owner_name}")
        if senior.counsel_name:
            print(f"  Senior Counsel: {senior.counsel_name}")

    if decision.junior_party_data:
        junior = decision.junior_party_data
        print(f"  Junior Party: {junior.patent_owner_name}")
        if junior.counsel_name:
            print(f"  Junior Counsel: {junior.counsel_name}")

print("-" * 40)
print("Example 4: Search by application number")
print("-" * 40)

response = client.search_decisions(
    senior_party_application_number_q="12*",
    limit=3,
)

print(
    f"\nFound {response.count} decisions with senior applications starting with '12'"
)
print(f"Displaying first {len(response.patent_interference_data_bag)} results:")

for decision in response.patent_interference_data_bag:
    print(f"\n  Interference Number: {decision.interference_number}")

    if decision.senior_party_data:
        print(
            f"  Senior Application: {decision.senior_party_data.application_number_text}"
        )

    if decision.junior_party_data:
        print(
            f"  Junior Publication: {decision.junior_party_data.publication_number}"
        )

    if decision.document_data:
        print(f"  Decision Type: {decision.document_data.decision_type_category}")

print("-" * 40)
print("Example 5: Paginate through decisions")
print("-" * 40)

max_items = 5
count = 0
for decision in client.paginate_decisions(
    decision_date_from_q="2023-01-01",
    limit=3,
):
    count += 1
    outcome = (
        decision.document_data.interference_outcome_category
        if decision.document_data
        else "N/A"
    )
    print(f"  {count}. {decision.interference_number} - {outcome}")

    if count >= max_items:
        print(f"  ... (stopping at {max_items} items)")
        break

print(f"Retrieved {count} decisions via pagination")

print("-" * 40)
print("Example 6: Advanced search with multiple criteria")
print("-" * 40)

response = client.search_decisions(
    decision_type_category_q="Decision",
    decision_date_from_q="2020-01-01",
    decision_date_to_q="2023-12-31",
    sort="documentData.decisionIssueDate desc",
    limit=3,
)

print(f"\nFound {response.count} Decisions between 2020-2023")
print(f"Displaying first {len(response.patent_interference_data_bag)} results:")

for decision in response.patent_interference_data_bag:
    print(f"\n  Interference Number: {decision.interference_number}")

    if decision.interference_meta_data:
        print(f"  Style: {decision.interference_meta_data.interference_style_name}")

    if decision.document_data:
        print(f"  Decision Type: {decision.document_data.decision_type_category}")
        print(f"  Decision Date: {decision.document_data.decision_issue_date}")
        print(f"  Outcome: {decision.document_data.interference_outcome_category}")

    if decision.additional_party_data_bag:
        print(f"  Additional Parties: {len(decision.additional_party_data_bag)}")
        for party in decision.additional_party_data_bag:
            print(f"    - {party.additional_party_name}")

print("-" * 40)
print("Example 7: Direct query string")
print("-" * 40)

# Use a direct query string for more complex searches
response = client.search_decisions(
    query='documentData.interferenceOutcomeCategory:"Final Decision"',
    limit=3,
)

print(f"\nFound {response.count} final decisions.")
print(f"Displaying first {len(response.patent_interference_data_bag)} results:")

for decision in response.patent_interference_data_bag:
    print(f"\n  Interference Number: {decision.interference_number}")

    if decision.document_data:
        print(f"  Outcome: {decision.document_data.interference_outcome_category}")
