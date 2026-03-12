"""Example usage of pyUSPTO for Image File Wrapper (IFW) retrieval.

Demonstrates the PatentDataClient for retrieving IFW metadata via multiple identifier
types, bulk-downloading prosecution documents, and downloading publication archives.
"""

import json
import os

from pyUSPTO import PatentDataClient, USPTOConfig

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
print("Example 1: Get IFW metadata by identifier type")
print("-" * 40)

# Application number
application_number = "14412875"
app_no_ifw = client.get_IFW_metadata(application_number=application_number)
if app_no_ifw and app_no_ifw.application_meta_data:
    print(f"Title: {app_no_ifw.application_meta_data.invention_title}")
    print(f"  IFW found via application number: {application_number}")

# Patent number
patent_number = "10765880"
pat_no_ifw = client.get_IFW_metadata(patent_number=patent_number)
if pat_no_ifw and pat_no_ifw.application_meta_data:
    print(f"Title: {pat_no_ifw.application_meta_data.invention_title}")
    print(f"  IFW found via patent number: {patent_number}")

# Publication number
publication_number = "*20150157873*"
pub_no_ifw = client.get_IFW_metadata(publication_number=publication_number)
if pub_no_ifw and pub_no_ifw.application_meta_data:
    print(f"Title: {pub_no_ifw.application_meta_data.invention_title}")
    print(f"  IFW found via publication number: {publication_number}")

# PCT application number
PCT_app_number = "PCT/US2008/12705"
pct_app_no_ifw = client.get_IFW_metadata(PCT_app_number=PCT_app_number)
if pct_app_no_ifw and pct_app_no_ifw.application_meta_data:
    print(f"Title: {pct_app_no_ifw.application_meta_data.invention_title}")
    print(f"  IFW found via PCT application number: {PCT_app_number}")

# PCT publication number
PCT_pub_number = "*2009064413*"
pct_pub_no_ifw = client.get_IFW_metadata(PCT_pub_number=PCT_pub_number)
if pct_pub_no_ifw and pct_pub_no_ifw.application_meta_data:
    print(f"Title: {pct_pub_no_ifw.application_meta_data.invention_title}")
    print(f"  IFW found via PCT publication number: {PCT_pub_number}")

print("-" * 40)
print("Example 2: Download IFW as ZIP archive")
print("-" * 40)

ifw_result = client.get_IFW(
    application_number=application_number,
    destination=DEST_PATH,
    overwrite=True,
)
if ifw_result:
    print(
        f"Title: {ifw_result.wrapper.application_meta_data.invention_title if ifw_result.wrapper.application_meta_data else 'N/A'}"
    )
    print(f"Output: {ifw_result.output_path}")
    doc_bag = ifw_result.wrapper.document_bag or []
    print(
        f"Documents downloaded: {len(ifw_result.downloaded_documents)} of {len(doc_bag)}"
    )
    for doc in doc_bag:
        if doc.document_identifier:
            filename = ifw_result.downloaded_documents.get(doc.document_identifier)
            status = f"-> {filename}" if filename else "(skipped)"
            print(f"  {doc.document_code} [{doc.document_identifier}] {status}")

print("-" * 40)
print("Example 3: Download IFW as directory")
print("-" * 40)

ifw_dir_result = client.get_IFW(
    application_number=application_number,
    destination=DEST_PATH,
    overwrite=True,
    as_zip=False,
)
if ifw_dir_result:
    print(f"Output directory: {ifw_dir_result.output_path}")

print("-" * 40)
print("Example 4: Download publication XML")
print("-" * 40)

if app_no_ifw and app_no_ifw.pgpub_document_meta_data:
    pgpub_archive = app_no_ifw.pgpub_document_meta_data
    print(json.dumps(pgpub_archive.to_dict(), indent=2))
    file_path = client.download_archive(
        printed_metadata=pgpub_archive, destination=DEST_PATH, overwrite=True
    )
    print(f"Downloaded publication XML to: {file_path}")

print("-" * 40)
print("Example 5: Download grant XML")
print("-" * 40)

if app_no_ifw and app_no_ifw.grant_document_meta_data:
    grant_archive = app_no_ifw.grant_document_meta_data
    print(json.dumps(grant_archive.to_dict(), indent=2))
    file_path = client.download_archive(
        printed_metadata=grant_archive, destination=DEST_PATH, overwrite=True
    )
    print(f"Downloaded grant XML to: {file_path}")
