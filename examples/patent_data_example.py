"""
Example usage of the uspto_api module for patent data

This example demonstrates how to use the PatentDataClient to interact with the USPTO Patent Data API.
It shows how to retrieve patent applications, search for patents by various criteria, and access
detailed patent information including inventors, applicants, assignments, and more.
"""

import os

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.config import USPTOConfig

# Method 1: Initialize the client with direct API key
# This approach is simple but less flexible
print("Method 1: Initialize with direct API key")
api_key = "tgfcazeuwmuiopipzyjnhrsbcqrymh"  # Replace with your actual API key
USPTO = PatentDataClient(api_key=api_key)

# Method 2: Initialize the client with USPTOConfig
# This approach provides more configuration options
print("\nMethod 2: Initialize with USPTOConfig")
# config = USPTOConfig(
#     api_key="YOUR_API_KEY_HERE",  # Replace with your actual API key
#     bulk_data_base_url="https://api.uspto.gov/api/v1/datasets",
#     patent_data_base_url="https://api.uspto.gov/api/v1/patent",
# )
# client = PatentDataClient(config=config)

# Method 3: Initialize the client with environment variables
# This is the most secure approach for production use
print("\nMethod 3: Initialize with environment variables")
# # Set environment variable (in a real scenario, this would be set outside the script)
# os.environ["USPTO_API_KEY"] = "YOUR_API_KEY_HERE"  # Replace with your actual API key
# config_from_env = USPTOConfig.from_env()
# client = PatentDataClient(config=config_from_env)

print("\nBeginning API requests with configured client:")

# Get patent applications
try:
    print("Attempting to get patent applications...")
    response = USPTO.get_patent_applications()
    print(f"Found {response.count} patent applications")

    # Display information about each patent application
    for patent in response.patent_file_wrapper_data_bag:
        app_meta = patent.application_meta_data
        if app_meta:
            print(f"\nApplication: {patent.application_number_text}")
            print(f"Title: {app_meta.invention_title}")
            print(f"Status: {app_meta.application_status_description_text}")
            print(f"Filing Date: {app_meta.filing_date}")

            if app_meta.patent_number:
                print(f"Patent Number: {app_meta.patent_number}")
                print(f"Grant Date: {app_meta.grant_date}")

            # Display inventors
            if app_meta.inventor_bag:
                print("\nInventors:")
                for inventor in app_meta.inventor_bag:
                    print(f"  - {inventor.first_name} {inventor.last_name}")
                    if inventor.correspondence_address_bag:
                        address = inventor.correspondence_address_bag[0]
                        if address.city_name and address.geographic_region_code:
                            print(
                                f"    ({address.city_name}, {address.geographic_region_code})"
                            )

            # Display applicants
            if app_meta.applicant_bag:
                print("\nApplicants:")
                for applicant in app_meta.applicant_bag:
                    print(f"  - {applicant.applicant_name_text}")
except Exception as e:
    print(f"Error getting patent applications: {e}")

# Search for patents by inventor name
inventor_search = USPTO.search_patents(inventor_name="Smith")
print(f"\nFound {inventor_search.count} patents with 'Smith' as inventor")

# Search for patents filed in a date range
date_search = USPTO.search_patents(
    filing_date_from="2020-01-01", filing_date_to="2020-12-31"
)
print(f"\nFound {date_search.count} patents filed in 2020")

# Get a specific patent by application number
try:
    app_no = "18045436"
    patent = USPTO.get_patent_by_application_number(application_number=app_no)
    print(f"\nRetrieved patent application: {patent.application_number_text}")

    print("\nRetrieving document information...")
    documents = USPTO.get_application_documents(application_number=app_no)

    # Display document information
    print(f"Found {len(documents)} documents")

    # Get first document as an example
    document = documents.documents[0]
    print(f"\nFirst document:")
    print(f"  Document ID: {document.document_identifier}")
    print(
        f"  Document Type: {document.document_code} - {document.document_code_description_text}"
    )
    print(f"  Date: {document.official_date}")
    print(f"  Direction: {document.direction_category}")

    # Download the document if download options are available
    if document.download_formats:
        download_format = document.download_formats[0]

        print("\nDownloading document...")
        # Create downloads directory if it doesn't exist
        if not os.path.exists(path="./downloads"):
            os.makedirs(name="./downloads")

        # Use the download_format object directly with the method
        downloaded_path = USPTO.download_document(
            destination="./downloads",
            download_format=download_format,
        )
        print(f"Downloaded document to: {downloaded_path}")

    # Check for assignments
    if patent.assignment_bag:
        print("\nAssignments:")
        for assignment in patent.assignment_bag:
            for assignee in assignment.assignee_bag:
                print(
                    f"  - {assignee.assignee_name_text} ({assignment.assignment_recorded_date})"
                )
                print(f"    Conveyance: {assignment.conveyance_text}")

except Exception as e:
    print(f"Error retrieving patent application {app_no}: {e}")

# Get a specific patent by patent number (using search)
patent_number = "10000000"  # Remove "US" prefix for the search
try:
    # Search for the patent by patent number
    print("\nSearching for patent number:", patent_number)
    patent_search = USPTO.search_patents(patent_number=patent_number, limit=1)
    if patent_search.count > 0:
        patent = patent_search.patent_file_wrapper_data_bag[0]
        if patent.application_meta_data and patent.application_meta_data.patent_number:
            print(f"\nRetrieved patent: US{patent.application_meta_data.patent_number}")
        else:
            print(
                f"\nRetrieved patent with application number: {patent.application_number_text}"
            )

        # Get term adjustment information
        if patent.patent_term_adjustment_data:
            pta = patent.patent_term_adjustment_data
            print(f"Patent Term Adjustment: {pta.adjustment_total_quantity} days")
            print(f"  A Delay: {pta.a_delay_quantity} days")
            print(f"  B Delay: {pta.b_delay_quantity} days")
            print(f"  C Delay: {pta.c_delay_quantity} days")
            print(f"  Applicant Delay: {pta.applicant_day_delay_quantity} days")

        # Get continuity information
        if patent.parent_continuity_bag:
            print("\nParent Applications:")
            for continuity in patent.parent_continuity_bag:
                print(f"  - {continuity.parent_application_number_text}")
                print(
                    f"    Type: {continuity.claim_parentage_type_code_description_text}"
                )
                print(f"    Filing Date: {continuity.parent_application_filing_date}")

        if patent.child_continuity_bag:
            print("\nChild Applications:")
            for continuity in patent.child_continuity_bag:
                print(f"  - {continuity.child_application_number_text}")
                print(
                    f"    Type: {continuity.claim_parentage_type_code_description_text}"
                )
                print(f"    Filing Date: {continuity.child_application_filing_date}")
    else:
        print(f"\nNo patents found with patent number: {patent_number}")

except Exception as e:
    print(f"Error retrieving patent {patent_number}: {e}")
