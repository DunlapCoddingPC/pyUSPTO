"""
Example usage of pyUSPTO for IFW data

This example demonstrates how to use the PatentDataClient to interact with the USPTO Patent Data API.
It shows how to retrieve IFW based on various identifying values.
"""

import os
from multiprocessing import Value

from pyUSPTO.clients.patent_data import PatentDataClient

api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "WARNING: API key is not set. Please replace 'YOUR_API_KEY_HERE' or set USPTO_API_KEY environment variable."
    )

client = PatentDataClient(api_key=api_key)


print("\nBeginning API requests with configured client:")

print("\nGet IFW Based on Application Number ->")
app_no_ifw = client.get_IFW_metadata(application_number="14412875")
if app_no_ifw and app_no_ifw.application_meta_data:
    print(app_no_ifw.application_meta_data.invention_title)
    print(" - IFW Found based on App No")


print("\nGet IFW Based on Patent Number ->")
pat_no_ifw = client.get_IFW_metadata(patent_number="10765880")
if pat_no_ifw and pat_no_ifw.application_meta_data:
    print(pat_no_ifw.application_meta_data.invention_title)
    print(" - IFW Found based on Pat No")


print("\nGet IFW Based on Publication Number ->")
pub_no_ifw = client.get_IFW_metadata(publication_number="*20150157873*")
if pub_no_ifw and pub_no_ifw.application_meta_data:
    print(pub_no_ifw.application_meta_data.invention_title)
    print(" - IFW Found based on Pub No")


print("\nGet IFW Based on PCT App Number ->")
pct_app_no_ifw = client.get_IFW_metadata(PCT_app_number="PCTUS0812705")
if pct_app_no_ifw and pct_app_no_ifw.application_meta_data:
    print(pct_app_no_ifw.application_meta_data.invention_title)
    print(" - IFW Found based on PCT App No")


print("\nGet IFW Based on PCT Pub Number ->")
pct_pub_no_ifw = client.get_IFW_metadata(PCT_pub_number="*2009064413*")
if pct_pub_no_ifw and pct_pub_no_ifw.application_meta_data:
    print(pct_pub_no_ifw.application_meta_data.invention_title)
    print(" - IFW Found based on PCT Pub No")

print("Now let's download the Patent Publication Text -->")
if app_no_ifw and app_no_ifw.pgpub_document_meta_data:
    pgpub_archive = app_no_ifw.pgpub_document_meta_data
    print(pgpub_archive)
    download_path = "./download-example"
    file_path = client.download_archive(
        printed_metadata=pgpub_archive, destination_path=download_path, overwrite=True
    )
    print(f"-Downloaded document to: {file_path}")

print("Now let's download the Patent Grant Text -->")
if app_no_ifw and app_no_ifw.grant_document_meta_data:
    grant_archive = app_no_ifw.grant_document_meta_data
    print(grant_archive)
    download_path = "./download-example"
    file_path = client.download_archive(
        printed_metadata=grant_archive, destination_path=download_path, overwrite=True
    )
    print(f"-Downloaded document to: {file_path}")
