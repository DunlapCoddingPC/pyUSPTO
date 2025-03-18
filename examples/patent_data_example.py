"""
Example usage of the uspto_api module for patent data

This example demonstrates how to use the PatentDataClient to interact with the USPTO Patent Data API.
It shows how to retrieve patent applications, search for patents by various criteria, and access
detailed patent information including inventors, applicants, assignments, and more.
"""

import json  # For pretty printing dict
import os

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.patent_data import ApplicationContinuityData

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
client = PatentDataClient(api_key=api_key)

# Method 2: Initialize the client with USPTOConfig (alternative)
# print("\nMethod 2: Initialize with USPTOConfig")
# config_obj = USPTOConfig(
#     api_key="YOUR_API_KEY_HERE",  # Replace with your actual API key
#     # bulk_data_base_url="https://api.uspto.gov/api/v1/datasets", # Optional, uses default if not set
#     # patent_data_base_url="https://api.uspto.gov/api/v1/patent", # Optional, uses default if not set
# )
# client = PatentDataClient(config=config_obj)

# Method 3: Initialize the client with environment variables (recommended for production)
# print("\nMethod 3: Initialize with environment variables")
# # Ensure USPTO_API_KEY is set in your environment
# # os.environ["USPTO_API_KEY"] = "YOUR_API_KEY_HERE" # Example, should be set outside
# try:
#     config_from_env = USPTOConfig.from_env()
#     client = PatentDataClient(config=config_from_env)
# except ValueError as e:
#     print(f"Error initializing from environment: {e}")
#     print("Please ensure USPTO_API_KEY environment variable is set.")
#     # Fallback to method 1 for the rest of the script if env var not set for example purposes
#     if 'client' not in locals(): # If client wasn't set due to error
#         api_key_fallback = "YOUR_API_KEY_HERE_FALLBACK"
#         print(f"Falling back to placeholder API key for example: {api_key_fallback}")
#         client = PatentDataClient(api_key=api_key_fallback)


print("\nBeginning API requests with configured client:")

# Get some patent applications (default is 25)
try:
    print("\nAttempting to get some patent applications (default search)...")
    # Calling with no specific query, relying on API defaults or client defaults (e.g., limit)
    response = client.search_applications(limit=5)  # Example: get 5 results
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
        print("-" * 20)

    # Example of using the to_csv method from PatentDataResponse
    if response.count > 0:
        print("\nGenerating CSV for the current response (first few rows shown):")
        csv_data = response.to_csv()
        # Print first 3 lines of CSV (header + 2 data rows if available)
        print("\n".join(csv_data.splitlines()[:3]))
        # You could save this csv_data to a file:
        # with open("patent_search_results.csv", "w", newline="", encoding="utf-8") as f:
        # f.write(csv_data)
        # print("\nFull CSV data saved to patent_search_results.csv (example).")


except Exception as e:
    print(f"Error getting patent applications: {e}")

# Search for patents by inventor name using convenience _q parameter
try:
    print("\nSearching for patents with 'Smith' as inventor...")
    # Changed from search_patents to search_applications with inventor_name_q
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
except Exception as e:
    print(f"Error searching by inventor: {e}")


# Search for patents filed in a date range using convenience _q parameters
try:
    print("\nSearching for patents filed in 2020...")
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
except Exception as e:
    print(f"Error searching by date range: {e}")

# Get a specific patent by application number
app_no_to_fetch = "18045436"  # Known application number, ensure it's valid
try:
    print(f"\nAttempting to retrieve patent application: {app_no_to_fetch}")
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
            document_to_download = documents_bag.documents[0]  # Example: first document
            print(f"\nFirst document details:")
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
                print("\nAttempting to download first document...")
                download_path = "./download-example"
                print(document_to_download.to_dict())
                downloaded_path = client.download_document(
                    document_format=document_to_download.document_formats[0],
                    destination_path=download_path,
                    overwrite=True,
                )
                print(f"Downloaded document to: {downloaded_path}")
            else:
                print(
                    "No downloadable formats available for the first document or document identifier missing."
                )
        else:
            print("No documents listed for this application.")

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

except Exception as e:
    print(f"Error retrieving or processing patent application {app_no_to_fetch}: {e}")

# Search for a specific patent by patent number (using search_applications)
target_patent_number = "10000000"
try:
    print(f"\nSearching for patent US {target_patent_number} B2...")
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

        # Example of getting continuity data (assuming it's part of the wrapper)
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

except Exception as e:
    print(f"Error retrieving patent by number {target_patent_number}: {e}")

# Example of POST search for applications
try:
    print("\nAttempting POST search for applications with 'AI' in title...")
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
except Exception as e:
    print(f"Error with POST search: {e}")


# Example of getting status codes
try:
    print("\nGetting first 5 status codes...")
    status_code_response = client.get_status_codes(params={"limit": 5})
    print(
        f"Retrieved {len(status_code_response.status_code_bag)} status codes (out of {status_code_response.count} total)."
    )
    for code_obj in status_code_response.status_code_bag:
        print(f"  - Code: {code_obj.code}, Description: {code_obj.description}")
except Exception as e:
    print(f"Error getting status codes: {e}")
