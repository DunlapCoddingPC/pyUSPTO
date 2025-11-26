"""
Example usage of the pyUSPTO module for PTAB Trials API

This example demonstrates how to use the PTABTrialsClient to interact with the USPTO PTAB
(Patent Trial and Appeal Board) Trials API. It shows how to search for trial proceedings,
documents, and decisions using various search criteria.

PTAB Trials include:
- IPR (Inter Partes Review)
- PGR (Post-Grant Review)
- CBM (Covered Business Method)
- DER (Derivation) proceedings
"""

import os

from pyUSPTO import PTABTrialsClient, USPTOConfig

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
client = PTABTrialsClient(api_key=api_key)

# Method 2: Initialize the client with USPTOConfig (alternative)
# print("\nMethod 2: Initialize with USPTOConfig")
# config_obj = USPTOConfig(
#     api_key="YOUR_API_KEY_HERE",  # Replace with your actual API key
#     ptab_base_url="https://api.uspto.gov",  # Optional, uses default if not set
# )
# client = PTABTrialsClient(config=config_obj)

# Method 3: Initialize the client with environment variables (recommended for production)
# print("\nMethod 3: Initialize with environment variables")
# # Ensure USPTO_API_KEY is set in your environment
# try:
#     config_from_env = USPTOConfig.from_env()
#     client = PTABTrialsClient(config=config_from_env)
# except ValueError as e:
#     print(f"Error initializing from environment: {e}")
#     print("Please ensure USPTO_API_KEY environment variable is set.")

print("\nBeginning PTAB Trials API requests with configured client:")

# =============================================================================
# 1. Search Trial Proceedings
# =============================================================================

print("\n" + "=" * 80)
print("1. Searching for IPR trial proceedings")
print("=" * 80)

try:
    # Search for IPR proceedings filed in 2023
    response = client.search_proceedings(
        trial_type_code_q="IPR",
        petition_filing_date_from_q="2023-01-01",
        petition_filing_date_to_q="2023-12-31",
        limit=5,
    )

    print(f"\nFound {response.count} IPR proceedings filed in 2023")
    print(f"Displaying first {len(response.patent_trial_proceeding_data_bag)} results:")

    for proceeding in response.patent_trial_proceeding_data_bag:
        print(f"\n  Trial Number: {proceeding.trial_number}")

        if proceeding.trial_meta_data:
            meta = proceeding.trial_meta_data
            print(f"  Trial Type: {meta.trial_type_code}")
            print(f"  Status: {meta.trial_status_category}")
            print(f"  Filing Date: {meta.petition_filing_date}")

        if proceeding.patent_owner_data:
            print(f"  Patent Owner: {proceeding.patent_owner_data.patent_owner_name}")
            print(f"  Patent Number: {proceeding.patent_owner_data.patent_number}")

        if proceeding.regular_petitioner_data:
            print(
                f"  Petitioner: {proceeding.regular_petitioner_data.real_party_in_interest_name}"
            )

except Exception as e:
    print(f"Error searching proceedings: {e}")

# =============================================================================
# 2. Search Trial Documents
# =============================================================================

print("\n" + "=" * 80)
print("2. Searching for trial documents")
print("=" * 80)

try:
    # Search for documents in a specific trial
    # Using the new convenience parameters for petitioner and patent owner
    response = client.search_documents(
        trial_number_q="IPR2023-00001",
        document_category_q="Paper",
        petitioner_real_party_in_interest_name_q="*",  # Any petitioner
        patent_owner_name_q="*",  # Any patent owner
        limit=5,
    )

    print(f"\nFound {response.count} documents")
    print(f"Displaying first {len(response.patent_trial_document_data_bag)} results:")

    for item in response.patent_trial_document_data_bag:
        print(f"\n  Trial Number: {item.trial_number}")

        if item.document_data:
            doc = item.document_data
            print(f"  Document Type: {doc.document_type_description_text}")
            print(f"  Filing Date: {doc.document_filing_date}")
            print(f"  Document Category: {doc.document_category}")

            if doc.download_uri:
                print(f"  Download URL: {doc.download_uri}")

except Exception as e:
    print(f"Error searching documents: {e}")

# =============================================================================
# 3. Search Trial Decisions with New Convenience Parameters
# =============================================================================

print("\n" + "=" * 80)
print("3. Searching for trial decisions with new parameters")
print("=" * 80)

try:
    # Using all the new convenience parameters
    response = client.search_decisions(
        trial_type_code_q="IPR",
        decision_type_category_q="Final Written Decision",
        patent_owner_name_q="*",
        trial_status_category_q="Terminated",
        decision_date_from_q="2023-01-01",
        limit=5,
    )

    print(f"\nFound {response.count} Final Written Decisions in IPR proceedings")
    print(f"Displaying first {len(response.patent_trial_document_data_bag)} results:")

    for item in response.patent_trial_document_data_bag:
        print(f"\n  Trial Number: {item.trial_number}")

        if item.trial_meta_data:
            print(f"  Trial Type: {item.trial_meta_data.trial_type_code}")
            print(f"  Status: {item.trial_meta_data.trial_status_category}")

        if item.decision_data:
            decision = item.decision_data
            print(f"  Decision Type: {decision.decision_type_category}")
            print(f"  Decision Date: {decision.decision_issue_date}")

except Exception as e:
    print(f"Error searching decisions: {e}")

# =============================================================================
# 4. Pagination Example
# =============================================================================

print("\n" + "=" * 80)
print("4. Paginating through proceedings")
print("=" * 80)

try:
    print("\nIterating through first 10 IPR proceedings from 2024...")
    count = 0
    for proceeding in client.paginate_proceedings(
        trial_type_code_q="IPR",
        petition_filing_date_from_q="2024-01-01",
        limit=5,  # Fetch 5 per page
    ):
        count += 1
        print(f"{count}. {proceeding.trial_number}")

        if count >= 10:  # Stop after 10 results for this example
            break

    print(f"\nDisplayed {count} proceedings using pagination")

except Exception as e:
    print(f"Error paginating proceedings: {e}")

# =============================================================================
# 5. Advanced Query with Additional Parameters
# =============================================================================

print("\n" + "=" * 80)
print("5. Advanced search with additional query parameters")
print("=" * 80)

try:
    # Search using additional_query_params for custom filters
    response = client.search_proceedings(
        trial_type_code_q="PGR",
        trial_status_category_q="Instituted",
        sort="petitionFilingDate desc",
        fields="trialNumber,lastModifiedDateTime",
        limit=3,
    )

    print(f"\nFound {response.count} Instituted PGR proceedings")
    print(f"Displaying first {len(response.patent_trial_proceeding_data_bag)} results:")

    for proceeding in response.patent_trial_proceeding_data_bag:
        print(f"\n  Trial Number: {proceeding.trial_number}")
        print(f"  Last Modified: {proceeding.last_modified_date_time}")

except Exception as e:
    print(f"Error with advanced search: {e}")

# =============================================================================
# 6. Error Handling Example
# =============================================================================

print("\n" + "=" * 80)
print("6. Error handling demonstration")
print("=" * 80)

try:
    # Attempt a search that might fail (invalid date format)
    print("\nAttempting search with potentially invalid parameters...")
    response = client.search_proceedings(
        trial_number_q="INVALID-TRIAL-NUMBER",
        limit=1,
    )

    if response.count == 0:
        print("No results found for the given search criteria")
    else:
        print(f"Found {response.count} results")

except Exception as e:
    print(f"Expected error occurred: {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("PTAB Trials API example completed successfully!")
print("=" * 80)
