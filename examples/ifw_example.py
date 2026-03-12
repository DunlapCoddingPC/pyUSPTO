"""Example usage of pyUSPTO for IFW data.

This example demonstrates how to use the PatentDataClient to retrieve Image File
Wrapper (IFW) data from the USPTO Patent Data API. It covers:

- get_IFW_metadata(): retrieve a PatentFileWrapper (with populated document_bag)
  using any of the five supported identifiers:
    - application_number
    - patent_number
    - publication_number
    - PCT_app_number
    - PCT_pub_number

- get_IFW(): retrieve metadata AND bulk-download all prosecution history documents
  (PDF preferred, DOCX fallback; XML and formatless docs are skipped). Returns an
  IFWResult with:
    - wrapper: the PatentFileWrapper
    - output_path: path to the ZIP archive (as_zip=True, default) or output directory
    - downloaded_documents: dict mapping document_identifier -> filename, allowing
      each Document in document_bag to be linked to its downloaded file

- download_archive() / download_publication(): download the pgpub or grant XML
  archive from PrintedMetaData.
"""

import json
import os

from pyUSPTO.clients.patent_data import PatentDataClient
from pyUSPTO.config import USPTOConfig

api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "WARNING: API key is not set. Please replace 'YOUR_API_KEY_HERE' or set USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = PatentDataClient(config=config)

DEST_PATH = "./notes/download-example"


print("\nBeginning API requests with configured client:")

print("\nGet IFW Based on Application Number ->")
application_number = "14412875"
app_no_ifw = client.get_IFW_metadata(application_number=application_number)
if app_no_ifw and app_no_ifw.application_meta_data:
    print(f"Title: {app_no_ifw.application_meta_data.invention_title}")
    print(f" - IFW Found based on App No: {application_number}")


print("\nGet IFW Based on Patent Number ->")
patent_number = "10765880"
pat_no_ifw = client.get_IFW_metadata(patent_number=patent_number)
if pat_no_ifw and pat_no_ifw.application_meta_data:
    print(f"Title: {pat_no_ifw.application_meta_data.invention_title}")
    print(f" - IFW Found based on Pat No: {patent_number}")


print("\nGet IFW Based on Publication Number ->")
publication_number = "*20150157873*"
pub_no_ifw = client.get_IFW_metadata(publication_number=publication_number)
if pub_no_ifw and pub_no_ifw.application_meta_data:
    print(f"Title: {pub_no_ifw.application_meta_data.invention_title}")
    print(f" - IFW Found based on Pub No: {publication_number}")


print("\nGet IFW Based on PCT App Number ->")
PCT_app_number = "PCT/US2008/12705"
pct_app_no_ifw = client.get_IFW_metadata(PCT_app_number=PCT_app_number)
if pct_app_no_ifw and pct_app_no_ifw.application_meta_data:
    print(f"Title: {pct_app_no_ifw.application_meta_data.invention_title}")
    print(f" - IFW Found based on PCT App No: {PCT_app_number}")


print("\nGet IFW Based on PCT Pub Number ->")
PCT_pub_number = "*2009064413*"
pct_pub_no_ifw = client.get_IFW_metadata(PCT_pub_number=PCT_pub_number)
if pct_pub_no_ifw and pct_pub_no_ifw.application_meta_data:
    print(f"Title: {pct_pub_no_ifw.application_meta_data.invention_title}")
    print(f" - IFW Found based on PCT Pub No: {PCT_pub_number}")


print("\nGet IFW + download all prosecution docs as a ZIP archive -->")
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

print("\nGet IFW + download all prosecution docs as a directory (no ZIP) -->")
ifw_dir_result = client.get_IFW(
    application_number=application_number,
    destination=DEST_PATH,
    overwrite=True,
    as_zip=False,
)
if ifw_dir_result:
    print(f"Output directory: {ifw_dir_result.output_path}")


print("\nNow let's download the Patent Publication Text -->")
if app_no_ifw and app_no_ifw.pgpub_document_meta_data:
    pgpub_archive = app_no_ifw.pgpub_document_meta_data
    print(json.dumps(pgpub_archive.to_dict(), indent=2))
    file_path = client.download_archive(
        printed_metadata=pgpub_archive, destination=DEST_PATH, overwrite=True
    )
    print(f"-Downloaded document to: {file_path}")

print("\nNow let's download the Patent Grant Text -->")
if app_no_ifw and app_no_ifw.grant_document_meta_data:
    grant_archive = app_no_ifw.grant_document_meta_data
    print(json.dumps(grant_archive.to_dict(), indent=2))
    file_path = client.download_archive(
        printed_metadata=grant_archive, destination=DEST_PATH, overwrite=True
    )
    print(f"-Downloaded document to: {file_path}")
