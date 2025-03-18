"""
Example usage of the uspto_api module for bulk data

This example demonstrates how to use the BulkDataClient to interact with the USPTO Bulk Data API.
It shows how to retrieve product information, search for products, and download files.
"""

import os
import requests
from typing import Union, List, Optional
from pyUSPTO.clients import BulkDataClient  # Import from top-level package
from pyUSPTO.config import USPTOConfig


def format_size(size_bytes: Union[int, float]) -> str:
    """
    Format a size in bytes to a human-readable string (KB, MB, GB, etc.)

    Args:
        size_bytes: The size in bytes to format

    Returns:
        A human-readable string representation of the size
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1

    # Round to 2 decimal places
    return f"{size_bytes:.2f} {size_names[i]}"


# Method 1: Initialize the client with direct API key
# This approach is simple but less flexible
print("Method 1: Initialize with direct API key")
api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
client = BulkDataClient(api_key=api_key)

# Method 2: Initialize the client with USPTOConfig
# This approach provides more configuration options
print("\nMethod 2: Initialize with USPTOConfig")
config = USPTOConfig(
    api_key="YOUR_API_KEY_HERE",  # Replace with your actual API key
    bulk_data_base_url="https://api.uspto.gov/api/v1/datasets",
    patent_data_base_url="https://api.uspto.gov/api/v1/patent",
)
client = BulkDataClient(config=config)

# Method 3: Initialize the client with environment variables
# This is the most secure approach for production use
print("\nMethod 3: Initialize with environment variables")
# Set environment variable (in a real scenario, this would be set outside the script)
os.environ["USPTO_API_KEY"] = "YOUR_API_KEY_HERE"  # Replace with your actual API key
config_from_env = USPTOConfig.from_env()
client = BulkDataClient(config=config_from_env)

print("\nBeginning API requests with configured client:")

# Get all available products
response = client.get_products()
print(f"Found {response.count} products")

# Display information about each product
for product in response.bulk_data_product_bag:
    print(f"\nProduct: {product.product_title_text}")
    print(f"ID: {product.product_identifier}")
    print(f"Description: {product.product_description_text}")
    print(f"Date range: {product.product_from_date} to {product.product_to_date}")
    print(f"Total files: {product.product_file_total_quantity}")
    print(f"Total size: {format_size(size_bytes=product.product_total_file_size)}")

    # Get detailed product info with files included
    try:
        detailed_product = client.get_product_by_id(
            product.product_identifier, include_files=True
        )
        if (
            detailed_product.product_file_bag
            and detailed_product.product_file_bag.file_data_bag
        ):
            print(f"\nFiles ({detailed_product.product_file_bag.count}):")
            for file_data in detailed_product.product_file_bag.file_data_bag:
                print(f"  - {file_data.file_name} ({format_size(file_data.file_size)})")
                print(f"    Type: {file_data.file_type_text}")
                print(f"    Released: {file_data.file_release_date}")
                if file_data.file_download_uri:
                    print(f"    Download URI: {file_data.file_download_uri}")
        else:
            print(f"\nNo files available for this product")
    except Exception as e:
        print(f"\nError retrieving detailed product info: {e}")

# Search for products by date range
date_filtered = client.search_products(from_date="2025-01-01", to_date="2025-03-31")
print(f"\nFound {date_filtered.count} products in date range")

# Search for products by label
try:
    # Using labels we saw in the API response
    label_filtered = client.search_products(labels=["Patent"])
    print(f"\nFound {label_filtered.count} products with label 'Patent'")
except requests.exceptions.HTTPError as e:
    print(f"Error searching by labels: {e}")

# Get a specific product by ID
product_id = "PEDSJSON"  # Using a real product ID from the output
try:
    product = client.get_product_by_id(product_id, include_files=True)
    print(f"\nRetrieved product: {product.product_title_text}")

    # Download a file from this product
    if product.product_file_bag and product.product_file_bag.file_data_bag:
        file_to_download = product.product_file_bag.file_data_bag[0]
        print(f"File download URI: {file_to_download.file_download_uri}")
        downloaded_path = client.download_file(
            file_data=file_to_download, destination="./downloads"
        )
        print(f"Downloaded file to: {downloaded_path}")
        print(f"File size: {format_size(size_bytes=file_to_download.file_size)}")

except Exception as e:
    print(f"Error retrieving product {product_id}: {e}")
