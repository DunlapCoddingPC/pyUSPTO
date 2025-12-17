"""Example usage of pyUSPTO for IFW data.

This example demonstrates how to use the PatentDataClient to interact with the USPTO Patent Data API.
It shows how to retrieve IFW based on various identifying values.
"""

import json
import os

from pyUSPTO.clients.patent_data import PatentDataClient

api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "WARNING: API key is not set. Please replace 'YOUR_API_KEY_HERE' or set USPTO_API_KEY environment variable."
    )

client = PatentDataClient(api_key=api_key)


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


print("\nNow let's download the Patent Publication Text -->")
if app_no_ifw and app_no_ifw.pgpub_document_meta_data:
    pgpub_archive = app_no_ifw.pgpub_document_meta_data
    print(json.dumps(pgpub_archive.to_dict(), indent=2))
    download_path = "./download-example"
    file_path = client.download_archive(
        printed_metadata=pgpub_archive, destination=download_path, overwrite=True
    )
    print(f"-Downloaded document to: {file_path}")

print("\nNow let's download the Patent Grant Text -->")
if app_no_ifw and app_no_ifw.grant_document_meta_data:
    grant_archive = app_no_ifw.grant_document_meta_data
    print(json.dumps(grant_archive.to_dict(), indent=2))
    download_path = "./download-example"
    file_path = client.download_archive(
        printed_metadata=grant_archive, destination=download_path, overwrite=True
    )
    print(f"-Downloaded document to: {file_path}")
