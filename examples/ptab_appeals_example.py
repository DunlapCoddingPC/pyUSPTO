"""Example usage of the pyUSPTO module for PTAB Appeals API.

This example demonstrates how to use the PTABAppealsClient to interact with the USPTO PTAB
(Patent Trial and Appeal Board) Appeals API. It shows how to search for ex parte appeal
decisions using various search criteria.

PTAB Appeals include ex parte appeals from patent application examinations to the Board.
"""

import os

from pyUSPTO import PTABAppealsClient

# --- Initialization ---
# Initialize the client with direct API key
print("Method 1: Initialize with direct API key")
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "WARNING: API key is not set. Please replace 'YOUR_API_KEY_HERE' or set USPTO_API_KEY environment variable."
    )
client = PTABAppealsClient(api_key=api_key)


print("\nBeginning PTAB Appeals API requests with configured client:")
# =============================================================================
# 1. Search Appeal Decisions by Technology Center
# =============================================================================

print("\n" + "=" * 80)
print("1. Searching for appeal decisions by technology center")
print("=" * 80)

try:
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

except Exception as e:
    print(f"Error searching appeal decisions: {e}")

# =============================================================================
# 2. Search by Decision Type
# =============================================================================

print("\n" + "=" * 80)
print("2. Searching for 'Affirmed' decisions")
print("=" * 80)

try:
    # Search for decisions where the examiner was affirmed
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

except Exception as e:
    print(f"Error searching by decision type: {e}")

# =============================================================================
# 3. Search by Application Number
# =============================================================================

print("\n" + "=" * 80)
print("3. Searching for decisions by application number pattern")
print("=" * 80)

try:
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

except Exception as e:
    print(f"Error searching by application number: {e}")

# =============================================================================
# 4. Pagination Example
# =============================================================================

print("\n" + "=" * 80)
print("4. Paginating through appeal decisions")
print("=" * 80)

try:
    print("\nIterating through first 10 appeal decisions from 2024...")
    count = 0
    for decision in client.paginate_decisions(
        decision_date_from_q="2024-01-01",
        limit=5,  # Fetch 5 per page
    ):
        count += 1
        decision_type = (
            decision.decision_data.decision_type_category
            if decision.decision_data
            else "N/A"
        )
        print(f"{count}. {decision.appeal_number} - {decision_type}")

        if count >= 10:  # Stop after 10 results for this example
            break

    print(f"\nDisplayed {count} decisions using pagination")

except Exception as e:
    print(f"Error paginating decisions: {e}")

# =============================================================================
# 5. Advanced Search with Multiple Criteria
# =============================================================================

print("\n" + "=" * 80)
print("5. Advanced search with multiple criteria")
print("=" * 80)

try:
    # Search with multiple convenience parameters
    response = client.search_decisions(
        technology_center_number_q="2100",  # Electronics
        decision_type_category_q="Decision",
        decision_date_from_q="2023-01-01",
        decision_date_to_q="2023-12-31",
        sort="decisionDate desc",
        limit=3,
    )

    print(f"\nFound {response.count} 'Decision's from TC 2100 (Electronics) in 2023")
    print(f"Displaying first {len(response.patent_appeal_data_bag)} results:")

    for decision in response.patent_appeal_data_bag:
        print(f"\n  Appeal Number: {decision.appeal_number}")

        if decision.appellant_data:
            print(f"  Application: {decision.appellant_data.application_number_text}")

        if decision.decision_data:
            print(f"  Decision: {decision.decision_data.decision_type_category}")
            print(f"  Date: {decision.decision_data.decision_issue_date}")

except Exception as e:
    print(f"Error with advanced search: {e}")

# =============================================================================
# 6. Direct Query String Example
# =============================================================================

print("\n" + "=" * 80)
print("6. Using direct query string for complex searches")
print("=" * 80)

try:
    # Use a direct query string for more complex searches
    response = client.search_decisions(
        query="appellantData.technologyCenterNumber:3600 AND decisionData.appealOutcomeCategory:(Affirmed OR Reversed)",
        limit=10,
    )

    print(f"\nFound {response.count} Affirmed/Reversed decisions from TC 3600")
    print(f"Displaying first {len(response.patent_appeal_data_bag)} results:")

    for decision in response.patent_appeal_data_bag:
        print(f"\n  Appeal Number: {decision.appeal_number}")
        print(f"  >App. Number: {decision.appellant_data.application_number_text}")  # type: ignore
        if decision.decision_data:
            print(f"  >Decision: {decision.decision_data.decision_type_category}")
            print(f"  >Outcome: {decision.decision_data.appeal_outcome_category}")

except Exception as e:
    print(f"Error with direct query: {e}")

# =============================================================================
# 7. Error Handling Example
# =============================================================================

print("\n" + "=" * 80)
print("7. Error handling demonstration")
print("=" * 80)

try:
    # Attempt a search that might return no results
    print("\nAttempting search with unlikely parameters...")
    response = client.search_decisions(
        appeal_number_q="INVALID-APPEAL-NUMBER",
        limit=1,
    )

    if response.count == 0:
        print("No results found for the given search criteria")
    else:
        print(f"Found {response.count} results")

except Exception as e:
    print(f"Expected error occurred: {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("PTAB Appeals API example completed successfully!")
print("=" * 80)
