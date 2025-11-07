"""
Example usage of the pyUSPTO module for Final Petition Decisions

This example demonstrates how to use the FinalPetitionDecisionsClient to interact with the
USPTO Final Petition Decisions API. It shows how to search for petition decisions, retrieve
specific decisions by ID, download decision data, and access detailed information about
petitions and their associated documents.
"""

import os

from pyUSPTO.clients import FinalPetitionDecisionsClient
from pyUSPTO.config import USPTOConfig

# --- Initialization ---
# Choose one method to initialize the client.
# For this example, Method 1 is active. Replace "YOUR_API_KEY_HERE" with your actual key.

# Method 1: Initialize the client with direct API key
print("Method 1: Initialize with direct API key")
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "WARNING: API key is not set. Please replace 'YOUR_API_KEY_HERE' or set USPTO_API_KEY environment variable."
    )
client = FinalPetitionDecisionsClient(api_key=api_key)

# Method 2: Initialize the client with USPTOConfig (alternative)
# print("\nMethod 2: Initialize with USPTOConfig")
# config_obj = USPTOConfig(
#     api_key="YOUR_API_KEY_HERE",  # Replace with your actual API key
#     petition_decisions_base_url="https://api.uspto.gov",  # Optional, uses default if not set
# )
# client = FinalPetitionDecisionsClient(config=config_obj)

# Method 3: Initialize the client with environment variables (recommended for production)
# print("\nMethod 3: Initialize with environment variables")
# # Ensure USPTO_API_KEY is set in your environment
# config_from_env = USPTOConfig.from_env()
# client = FinalPetitionDecisionsClient(config=config_from_env)

print("\nBeginning API requests with configured client:")

# Basic search for petition decisions
try:
    print("\n" + "=" * 60)
    print("Example 1: Basic Search for Petition Decisions")
    print("=" * 60)

    response = client.search_decisions(limit=5)
    print(f"Found {response.count} total petition decisions.")
    print(f"Displaying first {len(response.petition_decision_data_bag)} decisions:")

    for decision in response.petition_decision_data_bag:
        print(f"\n  Decision ID: {decision.petition_decision_record_identifier}")
        print(f"  Application Number: {decision.application_number_text}")
        print(f"  Decision Type: {decision.decision_type_code}")
        print(f"  Decision Date: {decision.decision_date}")
        print(f"  Technology Center: {decision.technology_center_number}")

        if decision.applicant_name:
            print(f"  Applicant: {decision.applicant_name}")

        if decision.patent_number:
            print(f"  Patent Number: {decision.patent_number}")

        if decision.inventor_bag:
            print(f"  Inventors ({len(decision.inventor_bag)}):")
            for inventor in decision.inventor_bag[:3]:  # Show first 3
                name_parts = [
                    part for part in [inventor.first_name, inventor.last_name] if part
                ]
                print(f"    - {' '.join(name_parts).strip()}")

        if decision.document_bag:
            print(f"  Documents: {len(decision.document_bag)}")

        print("-" * 40)

except Exception as e:
    print(f"Error in basic search: {e}")

# Search with query parameter
try:
    print("\n" + "=" * 60)
    print("Example 2: Search with Custom Query")
    print("=" * 60)

    # Search for decisions mentioning specific terms
    response = client.search_decisions(
        query="decisionTypeCode:GRANT",
        limit=3
    )
    print(f"Found {response.count} decisions with GRANT type.")
    print(f"Showing {len(response.petition_decision_data_bag)} results:")

    for decision in response.petition_decision_data_bag:
        print(f"  - {decision.petition_decision_record_identifier}: {decision.decision_type_code}")

except Exception as e:
    print(f"Error searching with query: {e}")

# Search using convenience parameters
try:
    print("\n" + "=" * 60)
    print("Example 3: Search Using Convenience Parameters")
    print("=" * 60)

    # Search by application number (if you have a specific one)
    print("\nSearching by date range...")
    response = client.search_decisions(
        decision_date_from_q="2023-01-01",
        decision_date_to_q="2023-12-31",
        limit=5
    )
    print(f"Found {response.count} decisions from 2023.")

    # Search by technology center
    print("\nSearching by technology center...")
    response = client.search_decisions(
        technology_center_q="2600",
        limit=3
    )
    print(f"Found {response.count} decisions from Technology Center 2600.")

except Exception as e:
    print(f"Error with convenience parameters: {e}")

# Get a specific decision by ID
try:
    print("\n" + "=" * 60)
    print("Example 4: Get Specific Decision by ID")
    print("=" * 60)

    # First, get a decision ID from search results
    response = client.search_decisions(limit=1)
    if response.count > 0:
        decision_id = response.petition_decision_data_bag[0].petition_decision_record_identifier

        print(f"Retrieving decision: {decision_id}")
        decision = client.get_decision_by_id(decision_id)

        print(f"\nDecision Details:")
        print(f"  ID: {decision.petition_decision_record_identifier}")
        print(f"  Application: {decision.application_number_text}")
        print(f"  Patent: {decision.patent_number}")
        print(f"  Decision Type: {decision.decision_type_code}")
        print(f"  Decision Date: {decision.decision_date}")
        print(f"  Technology Center: {decision.technology_center_number}")
        print(f"  Group Art Unit: {decision.group_art_unit_number}")
        print(f"  Examiner: {decision.examiner_name_text}")

        if decision.rule_bag:
            print(f"\n  Rules Cited ({len(decision.rule_bag)}):")
            for rule in decision.rule_bag[:5]:  # Show first 5
                print(f"    - {rule}")

        if decision.statute_bag:
            print(f"\n  Statutes Cited ({len(decision.statute_bag)}):")
            for statute in decision.statute_bag[:5]:  # Show first 5
                print(f"    - {statute}")

        if decision.document_bag:
            print(f"\n  Associated Documents ({len(decision.document_bag)}):")
            for doc in decision.document_bag[:3]:  # Show first 3
                print(f"    - Doc ID: {doc.document_identifier}")
                print(f"      Date: {doc.official_date}")
                print(f"      Direction: {doc.document_direction_category}")
                if doc.page_total_quantity:
                    print(f"      Pages: {doc.page_total_quantity}")
                if doc.download_option_bag:
                    print(f"      Download Options: {len(doc.download_option_bag)}")

except Exception as e:
    print(f"Error retrieving decision by ID: {e}")

# Download petition decisions data
try:
    print("\n" + "=" * 60)
    print("Example 5: Download Petition Decisions Data")
    print("=" * 60)

    # Download as JSON (returns response object)
    print("\nDownloading decisions as JSON...")
    response = client.download_decisions(
        format="json",
        decision_date_from_q="2023-01-01",
        limit=5
    )
    print(f"Downloaded JSON with {len(response.petition_decision_data)} decision records")

    # Download as CSV (automatically saves to file)
    print("\nDownloading decisions as CSV...")
    csv_path = client.download_decisions(
        format="csv",
        decision_date_from_q="2023-01-01",
        limit=10,
        destination_path="./downloads"
    )
    print(f"Downloaded CSV to: {csv_path}")

except Exception as e:
    print(f"Error downloading decisions: {e}")

# Pagination example
try:
    print("\n" + "=" * 60)
    print("Example 6: Paginating Through Results")
    print("=" * 60)

    page_size = 10
    max_pages = 3  # Limit to 3 pages for example

    print(f"Paginating through results ({page_size} per page, max {max_pages} pages)...")

    page_count = 0
    total_decisions = 0

    for page_response in client.paginate_decisions(
        limit=page_size,
        query="decisionDate:[2023-01-01 TO 2023-12-31]"
    ):
        page_count += 1
        decisions_in_page = len(page_response.petition_decision_data_bag)
        total_decisions += decisions_in_page

        print(f"  Page {page_count}: {decisions_in_page} decisions")

        if page_count >= max_pages:
            print(f"  (Stopping after {max_pages} pages for example)")
            break

    print(f"\nTotal decisions retrieved: {total_decisions} across {page_count} pages")

except Exception as e:
    print(f"Error during pagination: {e}")

# Download a petition document
try:
    print("\n" + "=" * 60)
    print("Example 7: Download Petition Decision Document")
    print("=" * 60)

    # Find a decision with downloadable documents
    response = client.search_decisions(limit=20)

    document_found = False
    for decision in response.petition_decision_data_bag:
        if decision.document_bag:
            for doc in decision.document_bag:
                if doc.download_option_bag and len(doc.download_option_bag) > 0:
                    download_option = doc.download_option_bag[0]

                    print(f"Found downloadable document:")
                    print(f"  Document ID: {doc.document_identifier}")
                    print(f"  MIME Type: {download_option.mime_type_identifier}")
                    print(f"  Pages: {download_option.page_total_quantity}")
                    print(f"  URL: {download_option.download_url}")

                    print(f"\nDownloading document...")
                    file_path = client.download_petition_document(
                        download_option,
                        file_path="./downloads"
                    )
                    print(f"Downloaded to: {file_path}")

                    document_found = True
                    break

        if document_found:
            break

    if not document_found:
        print("No downloadable documents found in the first 20 results")

except Exception as e:
    print(f"Error downloading document: {e}")

# Advanced search example
try:
    print("\n" + "=" * 60)
    print("Example 8: Advanced Search with Multiple Criteria")
    print("=" * 60)

    # Search with multiple parameters
    response = client.search_decisions(
        application_number_q="16*",  # Applications starting with 16
        decision_date_from_q="2020-01-01",
        technology_center_q="2600",
        limit=10
    )

    print(f"Search criteria:")
    print(f"  - Application numbers starting with '16'")
    print(f"  - Decision date from 2020-01-01")
    print(f"  - Technology Center 2600")
    print(f"\nFound {response.count} matching decisions")

    if response.count > 0:
        print(f"Showing first {len(response.petition_decision_data_bag)} results:")
        for decision in response.petition_decision_data_bag:
            print(f"  - App: {decision.application_number_text}, "
                  f"TC: {decision.technology_center_number}, "
                  f"Date: {decision.decision_date}")

except Exception as e:
    print(f"Error in advanced search: {e}")

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
