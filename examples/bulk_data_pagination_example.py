"""
Example usage of pagination features with the BulkDataClient.

This example demonstrates how to use the new pagination capabilities in the
BulkDataResponse objects returned by the BulkDataClient's search methods.
"""

from pyUSPTO.clients import BulkDataClient
from pyUSPTO.config import USPTOConfig


def format_size(size_bytes: int) -> str:
    """Format a size in bytes to a human-readable string."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    # Convert to float for the division
    size_value = float(size_bytes)
    while size_value >= 1024 and i < len(size_names) - 1:
        size_value /= 1024
        i += 1

    return f"{size_value:.2f} {size_names[i]}"


def demonstrate_pagination() -> None:
    """Demonstrate the use of pagination features in BulkDataResponse objects."""
    # Initialize the client using environment variables or a direct API key
    # (Replace "YOUR_API_KEY_HERE" with your actual API key if not using environment variables)
    client = BulkDataClient(api_key="YOUR_API_KEY_HERE")

    # Search for products with a small limit to demonstrate pagination
    print("Searching for products with pagination...")

    # Get the first page with a small limit
    first_page = client.search_products(
        query="patent", limit=2  # Small limit to demonstrate pagination
    )

    print(
        f"First page - found {first_page.count} products (showing {len(first_page)} per page)"
    )
    print_product_page(first_page, page_num=1)

    # Check if there are more pages
    if first_page.has_next_page():
        print("\nFetching next page...")
        # Get the next page directly from the response object
        second_page = first_page.get_next_page()
        print_product_page(second_page, page_num=2)

        # You can continue this pattern for subsequent pages
        if second_page.has_next_page():
            print("\nFetching third page...")
            third_page = second_page.get_next_page()
            print_product_page(third_page, page_num=3)

    # Demonstrate filtering capabilities of response objects
    print("\nDemonstrating filtering capabilities...")

    # Get a larger page to work with
    response = client.search_products(query="patent", limit=10)

    print(f"Total products: {response.count}")

    # Filter products by title
    filtered = response.filter(lambda p: "grant" in p.product_title_text.lower())
    print(f"Products with 'grant' in title: {len(filtered)}")
    for product in filtered:
        print(f"  - {product.product_title_text}")

    # Sort products by file size
    sorted_products = response.sort_by(
        lambda p: p.product_total_file_size, reverse=True
    )
    print("\nProducts sorted by file size (largest first):")
    for product in sorted_products[:3]:  # Show top 3
        print(
            f"  - {product.product_title_text}: {format_size(product.product_total_file_size)}"
        )

    # Find a specific product
    found = response.find(lambda p: "assignment" in p.product_title_text.lower())
    if found:
        print(f"\nFound product: {found.product_title_text}")

    # Demonstrate dataset info and fields
    print("\nDemonstrating dataset info and fields...")
    try:
        dataset_id = "patent"  # Example dataset ID
        dataset_info = client.get_dataset_info(dataset_id)
        print(f"Dataset: {dataset_info.title}")
        print(f"Description: {dataset_info.description}")

        # Get fields for the dataset
        fields = client.get_dataset_fields(dataset_id)

        # Get searchable fields
        searchable_fields = fields.get_searchable_fields()
        print(f"\nSearchable fields ({len(searchable_fields)}):")
        for field in searchable_fields[:5]:  # Show first 5
            print(f"  - {field.name}: {field.description}")

        # Get sortable fields
        sortable_fields = fields.get_sortable_fields()
        print(f"\nSortable fields ({len(sortable_fields)}):")
        for field in sortable_fields[:5]:  # Show first 5
            print(f"  - {field.name}")
    except Exception as e:
        print(f"Error getting dataset info: {e}")


def print_product_page(page, page_num: int) -> None:
    """Print information about products on the current page."""
    print(f"\nPage {page_num} products:")
    for i, product in enumerate(page, 1):
        print(f"{i}. {product.product_title_text}")
        print(f"   ID: {product.product_identifier}")
        print(
            f"   Date range: {product.product_from_date} to {product.product_to_date}"
        )
        print(f"   Size: {format_size(product.product_total_file_size)}")
        print(f"   Files: {product.product_file_total_quantity}")
        print()


if __name__ == "__main__":
    demonstrate_pagination()
