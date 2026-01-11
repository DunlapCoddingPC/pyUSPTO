"""Example usage of the BulkDataClient.

This example demonstrates how to use the BulkDataClient to interact with the USPTO Bulk Data API.
It shows how to search for products, retrieve product details, and download files.
"""

import os

from pyUSPTO.clients import BulkDataClient
from pyUSPTO.config import USPTOConfig
from pyUSPTO.models.bulk_data import FileData


def format_size(size_bytes: int | float) -> str:
    """Format a size in bytes to a human-readable string (KB, MB, GB, etc.).

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


# ============================================================================
# Client Initialization Methods
# ============================================================================

# Method 1: Initialize with API key directly
print("Method 1: Initialize with direct API key")
api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
client = BulkDataClient(api_key=api_key)

# Method 2: Initialize with USPTOConfig object
print("\nMethod 2: Initialize with USPTOConfig")
config = USPTOConfig(api_key="YOUR_API_KEY_HERE")
client = BulkDataClient(config=config)

# Method 3: Initialize from environment variables (recommended)
print("\nMethod 3: Initialize from environment variables")
os.environ["USPTO_API_KEY"] = "YOUR_API_KEY_HERE"  # Set this outside your script
config_from_env = USPTOConfig.from_env()
client = BulkDataClient(config=config_from_env)

print("\n" + "=" * 60)
print("Beginning API requests with configured client")
print("=" * 60)


# ============================================================================
# Example 1: Search for Products
# ============================================================================

print("\n--- Example 1: Search for Products ---")
# The Bulk Data API supports full-text search via the query parameter
# Field-specific queries (e.g., "productIdentifier:value") are not supported

# Search for patent-related products
response = client.search_products(query="patent", limit=5)
print(f"Found {response.count} products matching 'patent'")

for product in response.bulk_data_product_bag:
    print(f"\n  Product: {product.product_title_text}")
    print(f"  ID: {product.product_identifier}")
    print(f"  Description: {product.product_description_text[:100]}...")
    print(f"  Total files: {product.product_file_total_quantity}")
    print(f"  Total size: {format_size(product.product_total_file_size)}")


# ============================================================================
# Example 2: Paginate Through All Products
# ============================================================================

print("\n--- Example 2: Paginate Through Products ---")
# Use pagination to iterate through all matching products

count = 0
for product in client.paginate_products(query="trademark", limit=10):
    count += 1
    print(f"  {count}. {product.product_title_text} ({product.product_identifier})")
    if count >= 20:  # Limit output for example
        print("  ... (stopping after 20 products)")
        break


# ============================================================================
# Example 3: Get Product Details by ID
# ============================================================================

print("\n--- Example 3: Get Product by ID ---")
# Retrieve a specific product by its identifier
# Use include_files=True to get file listing

product_id = "PTGRXML"  # Patent Grant Full-Text Data (No Images) - XML
product = client.get_product_by_id(product_id, include_files=True, latest=True)

print(f"Product: {product.product_title_text}")
print(f"Description: {product.product_description_text}")
print(f"Frequency: {product.product_frequency_text}")
print(f"Labels: {product.product_label_array_text}")
print(f"Categories: {product.product_dataset_category_array_text}")
print(f"Date range: {product.product_from_date} to {product.product_to_date}")


# ============================================================================
# Example 4: List Files for a Product
# ============================================================================

print("\n--- Example 4: List Files for a Product ---")
# Get product with files and display file details

if product.product_file_bag and product.product_file_bag.file_data_bag:
    print(f"Found {len(product.product_file_bag.file_data_bag)} file(s):")

    for file_data in product.product_file_bag.file_data_bag:
        print(f"\n  File: {file_data.file_name}")
        print(f"  Size: {format_size(file_data.file_size)}")
        print(f"  Type: {file_data.file_type_text}")
        print(
            f"  Data range: {file_data.file_data_from_date} to {file_data.file_data_to_date}"
        )
        print(f"  Released: {file_data.file_release_date}")
        print(f"  Download URI: {file_data.file_download_uri}")
else:
    print("No files found for this product")


# ============================================================================
# Example 5: Download a File
# ============================================================================

print("\n--- Example 5: Download a File ---")
# Download a file from the product

min_file: FileData | None = None
last_bytes: float = float("inf")

if product.product_file_bag and product.product_file_bag.file_data_bag:
    for file_data in product.product_file_bag.file_data_bag:
        if file_data.file_size < last_bytes:
            last_bytes = file_data.file_size
            min_file = file_data

if min_file:
    print(f"Downloading smallest file: {min_file.file_name}")
    print(f"Size: {format_size(min_file.file_size)}")

    try:
        # Download with extraction (default behavior for archives)
        downloaded_path = client.download_file(
            file_data=min_file,
            destination="./downloads",
            overwrite=True,
            extract=True,  # Auto-extract if it's a tar.gz or zip
        )
        print(f"SUCCESS: Downloaded to {downloaded_path}")
    except Exception as e:
        print(f"ERROR: {e}")


# ============================================================================
# Example 6: Download Without Extraction
# ============================================================================

print("\n--- Example 6: Download Without Extraction ---")
# Download archive file without extracting

if product.product_file_bag and product.product_file_bag.file_data_bag and min_file:
    try:
        # Download without extraction
        downloaded_path = client.download_file(
            file_data=min_file,
            destination="./downloads",
            overwrite=True,
            extract=False,  # Keep archive compressed
        )
        print(f"SUCCESS: Archive saved to {downloaded_path}")
    except Exception as e:
        print(f"ERROR: {e}")


print("\n" + "=" * 60)
print("Examples complete!")
print("=" * 60)
