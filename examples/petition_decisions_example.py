"""Example usage of the pyUSPTO module for Final Petition Decisions.

This example demonstrates how to use the FinalPetitionDecisionsClient to interact with the
USPTO Final Petition Decisions API. It shows how to search for petition decisions, retrieve
specific decisions by ID, download decision data, and access detailed information about
petitions and their associated documents.
"""

import json
import os

from pyUSPTO.clients import FinalPetitionDecisionsClient
from pyUSPTO.models.petition_decisions import PetitionDecisionDownloadResponse

# --- Initialization ---
# Initialize the client with direct API key
print("Initialize with direct API key")
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "WARNING: API key is not set. Please replace 'YOUR_API_KEY_HERE' or set USPTO_API_KEY environment variable."
    )
client = FinalPetitionDecisionsClient(api_key=api_key)

DEST_PATH = "./download-example"

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
        print(f"  Technology Center: {decision.technology_center}")

        if decision.first_applicant_name:
            print(f"  Applicant: {decision.first_applicant_name}")

        if decision.patent_number:
            print(f"  Patent Number: {decision.patent_number}")

        if decision.inventor_bag:
            print(f"  Inventors ({len(decision.inventor_bag)}):")
            for inventor in decision.inventor_bag[:3]:  # Show first 3
                print(f"    - {inventor}")

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
    response = client.search_decisions(query="decisionTypeCode:C", limit=3)
    print(f"Found {response.count} decisions with C type.")
    print(f"Showing {len(response.petition_decision_data_bag)} results:")

    for decision in response.petition_decision_data_bag:
        print(
            f"  - {decision.petition_decision_record_identifier}: {decision.decision_type_code}"
        )

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
        decision_date_from_q="2023-01-01", decision_date_to_q="2023-12-31", limit=5
    )
    print(f"Found {response.count} decisions from 2023.")

    # Search by technology center
    print("\nSearching by technology center...")
    response = client.search_decisions(technology_center_q="2600", limit=3)
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
        decision_id = response.petition_decision_data_bag[
            0
        ].petition_decision_record_identifier
        if decision_id:
            print(f"Retrieving decision: {decision_id}")
            decision = client.get_decision_by_id(decision_id)
            if decision:
                print("\nDecision Details:")
                print(f"  ID: {decision.petition_decision_record_identifier}")
                print(f"  Application: {decision.application_number_text}")
                print(f"  Patent: {decision.patent_number}")
                print(f"  Decision Type: {decision.decision_type_code}")
                print(f"  Decision Date: {decision.decision_date}")
                print(f"  Technology Center: {decision.technology_center}")
                print(f"  Group Art Unit: {decision.group_art_unit_number}")

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
                        print(f"      Doc. Code: {doc.document_code_description_text}")
                        print(f"      Direction: {doc.direction_category}")
                        if doc.download_option_bag:
                            print(
                                f"      Download Options: {len(doc.download_option_bag)}"
                            )
                            for mime in doc.download_option_bag:
                                print(f"       >Mime Type: {mime.mime_type_identifier}")
                                print(f"       >>Pages: {mime.page_total_quantity}")

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
        format="json", decision_date_from_q="2023-01-01", limit=5, overwrite=True
    )
    if isinstance(response, PetitionDecisionDownloadResponse):
        print(
            f"Downloaded JSON with {len(response.petition_decision_data)} decision records"
        )
        print(json.dumps(response.to_dict(), indent=2))

    # Download as CSV (automatically saves to file)
    print("\nDownloading decisions as CSV...")
    csv_path = client.download_decisions(
        format="csv",
        decision_date_from_q="2023-01-01",
        limit=10,
        destination=DEST_PATH,
        overwrite=True,
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

    print(
        f"Paginating through results ({page_size} per page, max {max_pages} pages)..."
    )

    total_decisions = 0

    for decision in client.paginate_decisions(
        limit=page_size, query="decisionDate:[2023-01-01 TO 2023-12-31]"
    ):
        total_decisions += 1

        if total_decisions % page_size == 0:
            print(f"  Retrieved {total_decisions} decisions so far...")

        if total_decisions >= (page_size * max_pages):
            print(f"  (Stopping after {max_pages} pages for example)")
            break

    print(f"\nTotal decisions retrieved: {total_decisions}")

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
        d = client.get_decision_by_id(
            decision.petition_decision_record_identifier, include_documents=True
        )
        print(f"Getting docs for patent: {d.invention_title} with id: {d.petition_decision_record_identifier}")  # type: ignore
        if d and d.document_bag:
            for doc in d.document_bag:
                if doc.download_option_bag and len(doc.download_option_bag) > 0:
                    download_option = doc.download_option_bag[0]

                    print("Found downloadable document:")
                    print(f"  Document ID: {doc.document_identifier}")
                    print(f"  MIME Type: {download_option.mime_type_identifier}")
                    print(f"  Pages: {download_option.page_total_quantity}")
                    print(f"  URL: {download_option.download_url}")

                    print("\nDownloading document...")
                    file_path = client.download_petition_document(
                        download_option=download_option,
                        destination=DEST_PATH,
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
        limit=10,
    )

    print("Search criteria:")
    print("  - Application numbers starting with '16'")
    print("  - Decision date from 2020-01-01")
    print("  - Technology Center 2600")
    print(f"\nFound {response.count} matching decisions")

    if response.count > 0:
        print(f"Showing first {len(response.petition_decision_data_bag)} results:")
        for decision in response.petition_decision_data_bag:
            print(
                f"  - App: {decision.application_number_text}, "
                f"TC: {decision.technology_center}, "
                f"Date: {decision.decision_date}"
            )

except Exception as e:
    print(f"Error in advanced search: {e}")

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
