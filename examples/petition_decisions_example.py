"""Example usage of pyUSPTO for Final Petition Decisions.

Demonstrates the FinalPetitionDecisionsClient for searching decisions,
downloading decision data, and paginating results.
"""

import json
import os

from pyUSPTO import FinalPetitionDecisionsClient, PetitionDecisionDownloadResponse, USPTOConfig

DEST_PATH = "./notes/download-example"

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "API key is not set. Set the USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = FinalPetitionDecisionsClient(config=config)

print("-" * 40)
print("Example 1: Basic search")
print("-" * 40)

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
        for inventor in decision.inventor_bag[:3]:
            print(f"    - {inventor}")

    if decision.document_bag:
        print(f"  Documents: {len(decision.document_bag)}")

print("-" * 40)
print("Example 2: Search with custom query")
print("-" * 40)

response = client.search_decisions(query="decisionTypeCode:C", limit=3)
print(f"Found {response.count} decisions with C type.")
print(f"Showing {len(response.petition_decision_data_bag)} results:")

for decision in response.petition_decision_data_bag:
    print(
        f"  - {decision.petition_decision_record_identifier}: {decision.decision_type_code}"
    )

print("-" * 40)
print("Example 3: Search with convenience parameters")
print("-" * 40)

# Search by date range
print("\nSearching by date range...")
response = client.search_decisions(
    decision_date_from_q="2023-01-01", decision_date_to_q="2023-12-31", limit=5
)
print(f"Found {response.count} decisions from 2023.")

# Search by technology center
print("\nSearching by technology center...")
response = client.search_decisions(technology_center_q="2600", limit=3)
print(f"Found {response.count} decisions from Technology Center 2600.")

print("-" * 40)
print("Example 4: Get specific decision by ID")
print("-" * 40)

# Get a decision ID from search results
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
                for rule in decision.rule_bag[:5]:
                    print(f"    - {rule}")

            if decision.statute_bag:
                print(f"\n  Statutes Cited ({len(decision.statute_bag)}):")
                for statute in decision.statute_bag[:5]:
                    print(f"    - {statute}")

            if decision.document_bag:
                print(f"\n  Associated Documents ({len(decision.document_bag)}):")
                for doc in decision.document_bag[:3]:
                    print(f"    - Doc ID: {doc.document_identifier}")
                    print(f"      Date: {doc.official_date}")
                    print(f"      Doc. Code: {doc.document_code_description_text}")
                    print(f"      Direction: {doc.direction_category}")
                    if doc.download_option_bag:
                        print(
                            f"      Download Options: {len(doc.download_option_bag)}"
                        )
                        for mime in doc.download_option_bag:
                            print(f"        Mime Type: {mime.mime_type_identifier}")
                            print(f"        Pages: {mime.page_total_quantity}")

print("-" * 40)
print("Example 5: Download petition decisions data")
print("-" * 40)

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

print("-" * 40)
print("Example 6: Paginate through results")
print("-" * 40)

max_items = 30
count = 0
for decision in client.paginate_decisions(
    limit=10, query="decisionDate:[2023-01-01 TO 2023-12-31]"
):
    count += 1
    if count >= max_items:
        print(f"  ... (stopping at {max_items} items)")
        break

print(f"Retrieved {count} decisions via pagination")

print("-" * 40)
print("Example 7: Download petition document")
print("-" * 40)

# Find a decision with downloadable documents
response = client.search_decisions(limit=20)

document_found = False
for decision in response.petition_decision_data_bag:
    d = client.get_decision_by_id(
        decision.petition_decision_record_identifier, include_documents=True
    )
    print(
        f"Getting docs for patent: {d.invention_title} with id: {d.petition_decision_record_identifier}"
    )  # type: ignore
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

print("-" * 40)
print("Example 8: Advanced search with multiple criteria")
print("-" * 40)

response = client.search_decisions(
    application_number_q="16*",
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
