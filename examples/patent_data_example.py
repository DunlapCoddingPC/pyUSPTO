"""Example usage of pyUSPTO for patent application search and retrieval.

Demonstrates the PatentDataClient for searching applications, retrieving metadata,
downloading documents, and exporting CSV.
"""

import json
import os

from pyUSPTO import ApplicationContinuityData, PatentDataClient, USPTOConfig

DEST_PATH = "./notes/download-example"

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "API key is not set. Set the USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = PatentDataClient(config=config)

print("-" * 40)
print("Example 1: Default search")
print("-" * 40)

response = client.search_applications(limit=5)
print(
    f"Found {response.count} total patent applications matching default/broad criteria."
)
print(
    f"Displaying first {len(response.patent_file_wrapper_data_bag)} applications from response:"
)

for patent_wrapper in response.patent_file_wrapper_data_bag:
    app_meta = patent_wrapper.application_meta_data
    if app_meta:
        print(f"\n  Application: {patent_wrapper.application_number_text}")
        print(f"  Title: {app_meta.invention_title}")
        print(f"  Status: {app_meta.application_status_description_text}")
        print(f"  Filing Date: {app_meta.filing_date}")

        if app_meta.patent_number:
            print(f"  Patent Number: {app_meta.patent_number}")
            print(f"  Grant Date: {app_meta.grant_date}")

        if app_meta.inventor_bag:
            print("  Inventors:")
            for inventor in app_meta.inventor_bag:
                name_parts = [
                    part
                    for part in [inventor.first_name, inventor.last_name]
                    if part
                ]
                print(f"    - {' '.join(name_parts).strip()}")
                if inventor.correspondence_address_bag:
                    address = inventor.correspondence_address_bag[0]
                    if address.city_name and address.geographic_region_code:
                        print(
                            f"      ({address.city_name}, {address.geographic_region_code})"
                        )

        if app_meta.applicant_bag:
            print("  Applicants:")
            for applicant in app_meta.applicant_bag:
                print(f"    - {applicant.applicant_name_text}")

# Export results to CSV
if response.count > 0:
    print("\nGenerating CSV for the current response:")
    csv_data = response.to_csv()
    csv_path = os.path.join(DEST_PATH, "patent_search_results.csv")
    os.makedirs(DEST_PATH, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        f.write(csv_data)
        print(f"Full CSV data saved to {csv_path}.")

print("-" * 40)
print("Example 2: Search by inventor name")
print("-" * 40)

inventor_search_response = client.search_applications(
    inventor_name_q="Smith", limit=2
)
print(
    f"Found {inventor_search_response.count} patents with 'Smith' as inventor (showing up to 2)."
)
for patent_wrapper in inventor_search_response.patent_file_wrapper_data_bag:
    if patent_wrapper.application_meta_data:
        print(
            f"  - App No: {patent_wrapper.application_number_text}, Title: {patent_wrapper.application_meta_data.invention_title}"
        )

print("-" * 40)
print("Example 3: Search by filing date range")
print("-" * 40)

date_search_response = client.search_applications(
    filing_date_from_q="2020-01-01", filing_date_to_q="2020-12-31", limit=2
)
print(
    f"Found {date_search_response.count} patents filed in 2020 (showing up to 2)."
)
for patent_wrapper in date_search_response.patent_file_wrapper_data_bag:
    if patent_wrapper.application_meta_data:
        print(
            f"  - App No: {patent_wrapper.application_number_text}, Filing Date: {patent_wrapper.application_meta_data.filing_date}"
        )

print("-" * 40)
print("Example 4: Get application by number")
print("-" * 40)

app_no_to_fetch = "18045436"
print(f"Retrieving patent application: {app_no_to_fetch}")
patent_wrapper_detail = client.get_application_by_number(
    application_number=app_no_to_fetch
)
if patent_wrapper_detail:
    print(
        f"Successfully retrieved: {patent_wrapper_detail.application_number_text}"
    )
    if patent_wrapper_detail.application_meta_data:
        print(
            f"Title: {patent_wrapper_detail.application_meta_data.invention_title}"
        )

    print("\nRetrieving document information...")
    documents_bag = client.get_application_documents(
        application_number=app_no_to_fetch
    )
    print(f"Found {len(documents_bag)} documents for application {app_no_to_fetch}")

    if documents_bag.documents:
        document_to_download = documents_bag.documents[0]
        print("\nFirst document details:")
        print(f"  Document ID: {document_to_download.document_identifier}")
        print(
            f"  Document Type: {document_to_download.document_code} - {document_to_download.document_code_description_text}"
        )
        print(f"  Date: {document_to_download.official_date}")
        print(f"  Direction: {document_to_download.direction_category}")

        if (
            document_to_download.document_formats
            and document_to_download.document_identifier
        ):
            print("\nDownloading first PDF document...")
            print(json.dumps(document_to_download.to_dict(), indent=2))
            downloaded_path = client.download_document(
                document=document_to_download,
                format="PDF",
                destination=DEST_PATH,
                overwrite=True,
            )
            print(f"Downloaded document to: {downloaded_path}")

            print("\nStreaming same document to memory...")
            with client.stream_document(
                document=document_to_download, format="PDF"
            ) as response:
                content = response.content
                print(f"Streamed {len(content)} bytes")
        else:
            print(
                "No downloadable formats available for the first document or document identifier missing."
            )
    else:
        print("No documents listed for this application.")

    # Download publication XML (grant or pgpub)
    print("\nChecking for publication files (grant/pgpub XML)...")
    if patent_wrapper_detail.grant_document_meta_data:
        grant_metadata = patent_wrapper_detail.grant_document_meta_data
        print(f"Grant document available: {grant_metadata.xml_file_name}")
        print(f"  Product: {grant_metadata.product_identifier}")
        print(f"  Created: {grant_metadata.file_create_date_time}")

        print("\nDownloading grant XML...")
        grant_path = client.download_publication(
            printed_metadata=grant_metadata,
            destination=DEST_PATH,
            overwrite=True,
        )
        print(f"Downloaded grant XML to: {grant_path}")

    if patent_wrapper_detail.pgpub_document_meta_data:
        pgpub_metadata = patent_wrapper_detail.pgpub_document_meta_data
        print(f"\nPre-grant publication available: {pgpub_metadata.xml_file_name}")

        pgpub_path = client.download_publication(
            printed_metadata=pgpub_metadata,
            file_name="my_pgpub.xml",
            destination=DEST_PATH,
            overwrite=True,
        )
        print(f"Downloaded pgpub XML to: {pgpub_path}")

    if patent_wrapper_detail.assignment_bag:
        print("\nAssignments:")
        for assignment in patent_wrapper_detail.assignment_bag:
            for assignee in assignment.assignee_bag:
                print(
                    f"  - {assignee.assignee_name_text} (Recorded: {assignment.assignment_recorded_date})"
                )
                print(f"    Conveyance: {assignment.conveyance_text}")
else:
    print(f"Could not retrieve details for application {app_no_to_fetch}")

print("-" * 40)
print("Example 5: Search by patent number")
print("-" * 40)

target_patent_number = "10000000"
print(f"Searching for patent US {target_patent_number} B2...")
patent_search_response = client.search_applications(
    patent_number_q=target_patent_number, limit=1
)

if (
    patent_search_response.count > 0
    and patent_search_response.patent_file_wrapper_data_bag
):
    found_patent_wrapper = patent_search_response.patent_file_wrapper_data_bag[0]
    if (
        found_patent_wrapper.application_meta_data
        and found_patent_wrapper.application_meta_data.patent_number
    ):
        print(
            f"Retrieved patent: US {found_patent_wrapper.application_meta_data.patent_number}"
        )
    else:
        print(
            f"Retrieved patent application: {found_patent_wrapper.application_number_text}"
        )

    if found_patent_wrapper.patent_term_adjustment_data:
        pta = found_patent_wrapper.patent_term_adjustment_data
        print(f"Patent Term Adjustment: {pta.adjustment_total_quantity} days")
        if pta.a_delay_quantity is not None:
            print(f"  A Delay: {pta.a_delay_quantity} days")
        if pta.b_delay_quantity is not None:
            print(f"  B Delay: {pta.b_delay_quantity} days")
        if pta.c_delay_quantity is not None:
            print(f"  C Delay: {pta.c_delay_quantity} days")
        if pta.applicant_day_delay_quantity is not None:
            print(f"  Applicant Delay: {pta.applicant_day_delay_quantity} days")

    continuity_data = ApplicationContinuityData.from_wrapper(
        wrapper=found_patent_wrapper
    )
    if continuity_data.parent_continuity_bag:
        print("\nParent Applications:")
        for p_continuity in continuity_data.parent_continuity_bag:
            print(f"  - App No: {p_continuity.parent_application_number_text}")
            print(
                f"    Type: {p_continuity.claim_parentage_type_code_description_text}"
            )
            print(f"    Filing Date: {p_continuity.parent_application_filing_date}")

    if continuity_data.child_continuity_bag:
        print("\nChild Applications:")
        for c_continuity in continuity_data.child_continuity_bag:
            print(f"  - App No: {c_continuity.child_application_number_text}")
            print(
                f"    Type: {c_continuity.claim_parentage_type_code_description_text}"
            )
            print(f"    Filing Date: {c_continuity.child_application_filing_date}")
else:
    print(f"No patents found with patent number: {target_patent_number}")

print("-" * 40)
print("Example 6: POST search")
print("-" * 40)

print("POST search for applications with 'AI' in title...")
post_search_body = {
    "q": "applicationMetaData.inventionTitle:AI",
    "pagination": {"offset": 0, "limit": 2},
}
post_response = client.search_applications(post_body=post_search_body)
print(
    f"Found {post_response.count} applications via POST search (showing up to 2)."
)
for patent_wrapper in post_response.patent_file_wrapper_data_bag:
    if patent_wrapper.application_meta_data:
        print(
            f"  - App No: {patent_wrapper.application_number_text}, Title: {patent_wrapper.application_meta_data.invention_title}"
        )

print("-" * 40)
print("Example 7: Search by CPC classification")
print("-" * 40)

# CPC codes containing spaces or slashes are automatically quoted for the Lucene query.
print("Searching by CPC classification code 'H10D  64/667'...")
cpc_response = client.search_applications(classification_q="H10D  64/667", limit=3)
print(f"Found {cpc_response.count} applications with CPC code H10D 64/667.")
for patent_wrapper in cpc_response.patent_file_wrapper_data_bag:
    app_meta = patent_wrapper.application_meta_data
    if app_meta:
        print(
            f"  - App No: {patent_wrapper.application_number_text}, Title: {app_meta.invention_title}"
        )
        if app_meta.cpc_classification_bag:
            print(f"    CPC codes: {', '.join(app_meta.cpc_classification_bag)}")

print("-" * 40)
print("Example 8: Get status codes")
print("-" * 40)

status_code_response = client.get_status_codes(params={"limit": 5})
print(
    f"Retrieved {len(status_code_response.status_code_bag)} status codes (out of {status_code_response.count} total)."
)
for code_obj in status_code_response.status_code_bag:
    print(f"  - Code: {code_obj.code}, Description: {code_obj.description}")
