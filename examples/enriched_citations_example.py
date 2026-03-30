"""Example usage of pyUSPTO for Enriched Cited Reference Metadata.

Demonstrates the EnrichedCitationsClient for searching citation data
extracted from patent office actions, filtering by various criteria,
and paginating through results.
"""

import os

from pyUSPTO import EnrichedCitationsClient, USPTOConfig

# --- Client Initialization ---
api_key = os.environ.get("USPTO_API_KEY", "YOUR_API_KEY_HERE")
if api_key == "YOUR_API_KEY_HERE":
    raise ValueError(
        "API key is not set. Set the USPTO_API_KEY environment variable."
    )
config = USPTOConfig(api_key=api_key)
client = EnrichedCitationsClient(config=config)

print("-" * 40)
print("Example 1: Search by application number")
print("-" * 40)

response = client.search_citations(patent_application_number_q="15061308")
print(f"Found {response.num_found} citations for application 15061308.")
for citation in response.docs[:5]:
    print(f"\n  Cited Document: {citation.cited_document_identifier}")
    print(f"  Category Code: {citation.citation_category_code}")
    print(f"  Office Action Date: {citation.office_action_date}")
    print(f"  Office Action Type: {citation.office_action_category}")
    if citation.examiner_cited_reference_indicator:
        print("  Cited by: Examiner")
    if citation.passage_location_text:
        print(f"  Passages: {citation.passage_location_text}")

print("-" * 40)
print("Example 2: Search by tech center and citation category")
print("-" * 40)

response = client.search_citations(
    tech_center_q="2800",
    citation_category_code_q="X",
    rows=5,
)
print(f"Found {response.num_found} 'X' citations in tech center 2800.")
for citation in response.docs:
    print(
        f"  App {citation.patent_application_number}: "
        f"{citation.cited_document_identifier} "
        f"(claims: {citation.related_claim_number_text})"
    )

print("-" * 40)
print("Example 3: Search by date range")
print("-" * 40)

response = client.search_citations(
    office_action_date_from_q="2019-01-01",
    office_action_date_to_q="2019-12-31",
    rows=5,
)
print(f"Found {response.num_found} citations from 2019.")

print("-" * 40)
print("Example 4: Combined filters")
print("-" * 40)

response = client.search_citations(
    tech_center_q="2800",
    citation_category_code_q="Y",
    examiner_cited_q=True,
    rows=5,
)
print(
    f"Found {response.num_found} examiner-cited 'Y' citations in tech center 2800."
)
for citation in response.docs:
    print(
        f"  App {citation.patent_application_number}: "
        f"{citation.cited_document_identifier} "
        f"(art unit: {citation.group_art_unit_number})"
    )

print("-" * 40)
print("Example 5: Search with sort")
print("-" * 40)

response = client.search_citations(
    tech_center_q="2800",
    sort="officeActionDate desc",
    rows=5,
)
print(f"Found {response.num_found} citations, sorted by date descending.")
for citation in response.docs:
    print(f"  {citation.office_action_date}: {citation.cited_document_identifier}")

print("-" * 40)
print("Example 6: Search by cited document identifier")
print("-" * 40)

response = client.search_citations(
    cited_document_identifier_q="US 20190165601 A1",
    rows=5,
)
print(f"Found {response.num_found} citations of US 20190165601 A1.")

print("-" * 40)
print("Example 7: Paginate through results")
print("-" * 40)

max_items = 30
count = 0
for _ in client.paginate_citations(
    tech_center_q="2800", rows=10
):
    count += 1
    if count >= max_items:
        print(f"  ... (stopping at {max_items} items)")
        break

print(f"Retrieved {count} citations via pagination")

print("-" * 40)
print("Example 8: Get available fields")
print("-" * 40)

fields_response = client.get_fields()
print(f"API Status: {fields_response.api_status}")
print(f"Field Count: {fields_response.field_count}")
print(f"Fields: {fields_response.fields}")
print(f"Last Updated: {fields_response.last_data_updated_date}")
