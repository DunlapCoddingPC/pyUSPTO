"""Example usage of the pyUSPTO module for PTAB Interferences API.

This example demonstrates how to use the PTABInterferencesClient to interact with the USPTO PTAB
(Patent Trial and Appeal Board) Interferences API. It shows how to search for interference
decisions using various search criteria.

PTAB Interferences are proceedings to determine priority of invention when two or more parties
claim the same patentable invention.
"""

import os

from pyUSPTO import PTABInterferencesClient
from pyUSPTO.config import USPTOConfig

# --- Initialization ---
# Initialize the client with direct API key
print("Initialize with direct API key")
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "WARNING: API key is not set. Please replace 'YOUR_API_KEY_HERE' or set USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = PTABInterferencesClient(config=config)

print("\nBeginning PTAB Interferences API requests with configured client:")

# =============================================================================
# 1. Search Interference Decisions
# =============================================================================

print("\n" + "=" * 80)
print("1. Searching for interference decisions")
print("=" * 80)

try:
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

except Exception as e:
    print(f"Error searching interference decisions: {e}")

# =============================================================================
# 2. Search by Interference Outcome
# =============================================================================

print("\n" + "=" * 80)
print("2. Searching for decisions by outcome")
print("=" * 80)

try:
    # Search for decisions with specific outcomes
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

except Exception as e:
    print(f"Error searching by outcome: {e}")

# =============================================================================
# 3. Search by Party Name
# =============================================================================

print("\n" + "=" * 80)
print("3. Searching for decisions by party name")
print("=" * 80)

try:
    # Search for decisions involving a specific senior party
    response = client.search_decisions(
        senior_party_name_q="*Corp*",  # Any company with "Corp" in the name
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

except Exception as e:
    print(f"Error searching by party name: {e}")

# =============================================================================
# 4. Search by Application Numbers
# =============================================================================

print("\n" + "=" * 80)
print("4. Searching for decisions by application numbers")
print("=" * 80)

try:
    # Search for decisions involving specific application numbers
    response = client.search_decisions(
        senior_party_application_number_q="12*",  # Applications starting with 12/
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

except Exception as e:
    print(f"Error searching by application numbers: {e}")

# =============================================================================
# 5. Pagination Example
# =============================================================================

print("\n" + "=" * 80)
print("5. Paginating through interference decisions")
print("=" * 80)

try:
    print("\nIterating through first 5 interference decisions from 2023...")
    count = 0
    for decision in client.paginate_decisions(
        decision_date_from_q="2023-01-01",
        limit=3,  # Fetch 3 per page
    ):
        count += 1
        outcome = (
            decision.document_data.interference_outcome_category
            if decision.document_data
            else "N/A"
        )
        print(f"{count}. {decision.interference_number} - {outcome}")

        if count >= 5:  # Stop after 5 results for this example
            break

    print(f"\nDisplayed {count} decisions using pagination")

except Exception as e:
    print(f"Error paginating decisions: {e}")

# =============================================================================
# 6. Advanced Search with Multiple Criteria
# =============================================================================

print("\n" + "=" * 80)
print("6. Advanced search with multiple criteria")
print("=" * 80)

try:
    # Search with multiple convenience parameters
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

        # Show additional parties if present
        if decision.additional_party_data_bag:
            print(f"  Additional Parties: {len(decision.additional_party_data_bag)}")
            for party in decision.additional_party_data_bag:
                print(f"    - {party.additional_party_name}")

except Exception as e:
    print(f"Error with advanced search: {e}")

# =============================================================================
# 7. Direct Query String Example
# =============================================================================

print("\n" + "=" * 80)
print("7. Using direct query string for complex searches")
print("=" * 80)

try:
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

except Exception as e:
    print(f"Error with direct query: {e}")

print("\n" + "=" * 80)
print("PTAB Interferences API example completed successfully!")
print("=" * 80)
