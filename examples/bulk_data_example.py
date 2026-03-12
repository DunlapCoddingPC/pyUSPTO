"""Example usage of pyUSPTO for bulk data products.

Demonstrates the BulkDataClient for searching products, listing files,
and downloading bulk data archives.
"""

import os

from pyUSPTO import BulkDataClient, FileData, USPTOConfig

DEST_PATH = "./notes/download-example"


def format_size(size_bytes: int | float) -> str:
    """Format a size in bytes to a human-readable string (KB, MB, GB, etc.)."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"


# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "API key is not set. Set the USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = BulkDataClient(config=config)

print("-" * 40)
print("Example 1: Search for products")
print("-" * 40)

response = client.search_products(query="patent", limit=5)
print(f"Found {response.count} products matching 'patent'")

for product in response.bulk_data_product_bag:
    print(f"\n  Product: {product.product_title_text}")
    print(f"  ID: {product.product_identifier}")
    print(f"  Description: {product.product_description_text[:100]}...")
    print(f"  Total files: {product.product_file_total_quantity}")
    print(f"  Total size: {format_size(product.product_total_file_size)}")

print("-" * 40)
print("Example 2: Paginate through products")
print("-" * 40)

max_items = 20
count = 0
for product in client.paginate_products(query="trademark", limit=10):
    count += 1
    print(f"  {count}. {product.product_title_text} ({product.product_identifier})")
    if count >= max_items:
        print(f"  ... (stopping at {max_items} products)")
        break

print("-" * 40)
print("Example 3: Get product by ID")
print("-" * 40)

product_id = "PTGRXML"  # Patent Grant Full-Text Data (No Images) - XML
product = client.get_product_by_id(product_id, include_files=True, latest=True)

print(f"Product: {product.product_title_text}")
print(f"Description: {product.product_description_text}")
print(f"Frequency: {product.product_frequency_text}")
print(f"Labels: {product.product_label_array_text}")
print(f"Categories: {product.product_dataset_category_array_text}")
print(f"Date range: {product.product_from_date} to {product.product_to_date}")

print("-" * 40)
print("Example 4: List files for a product")
print("-" * 40)

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

print("-" * 40)
print("Example 5: Download a file (with extraction)")
print("-" * 40)

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

    downloaded_path = client.download_file(
        file_data=min_file,
        destination=DEST_PATH,
        overwrite=True,
        extract=True,
    )
    print(f"Downloaded to {downloaded_path}")

print("-" * 40)
print("Example 6: Download without extraction")
print("-" * 40)

if product.product_file_bag and product.product_file_bag.file_data_bag and min_file:
    downloaded_path = client.download_file(
        file_data=min_file,
        destination=DEST_PATH,
        overwrite=True,
        extract=False,
    )
    print(f"Archive saved to {downloaded_path}")
