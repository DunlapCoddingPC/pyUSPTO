Bulk Data Client
================

.. automodule:: pyUSPTO.clients.bulk_data
   :members:
   :undoc-members:
   :show-inheritance:

.. _bulk-data-product-identifiers:

Bulk Data Product Identifiers
------------------------------

The table below lists all product identifiers available in the USPTO Open Data Portal Bulk Dataset Directory.
Pass these identifiers to :meth:`~pyUSPTO.BulkDataClient.get_product_by_id` or use them as a filter
when calling :meth:`~pyUSPTO.BulkDataClient.search_products`.

.. note::

   This table reflects the Bulk Dataset Directory as of 2026-Mar-30 (47 products).
   Source: `2026 Bulk Data Product Descriptions <https://data.uspto.gov/documents/documents/2026BulkDataProductDescriptions.xlsx>`_.
   USPTO adds new products over time; use :meth:`~pyUSPTO.BulkDataClient.search_products`
   without filters to retrieve the current full list.

.. list-table::
   :header-rows: 1
   :widths: 10 25 15 8 42

   * - Identifier
     - Name
     - Dates Available
     - File Types
     - Description
   * - OACT
     - Office Actions Weekly Archives
     - 2023-Dec-18 – Present
     - JSON
     - Full-text of public Office Actions bundled as JSON in downloadable weekly ZIP files. Data covers 2020-01-06 to present.
   * - PTFWPRD
     - Patent File Wrapper (Bulk Datasets) – Daily
     - 2026-Mar-23 – Present
     - JSON
     - Bibliographic and assignment static patent data as daily delta increments.
   * - PTFWPRE
     - Patent File Wrapper (Bulk Datasets) – Weekly
     - 2001-Jan-01 – Present
     - JSON
     - Bibliographic and assignment static patent data as weekly datasets in 10-year increments.
   * - TRTDXFAP
     - Trademark Full Text XML Data (No Images) – Daily Applications
     - 2025-Jan-01 – Present
     - XML
     - Pending and registered trademark text data (no images) for the current calendar year per the U.S. Trademark Applications Version 2.3 DTD.
   * - TTABTDXF
     - Trademark Full Text XML Data (No Images) – Daily TTAB
     - 2025-Jan-01 – Present
     - XML
     - TTAB text data (no images) for the current calendar year per the TTAB Version 1.0 DTD.
   * - PTGRMP2
     - Patent Grant Multi-page PDF Images
     - 1790-Jul-31 – Present
     - PDF
     - Multi-page PDF images of each patent grant issued weekly (Tuesdays) from 1790 to present. Includes Certificates-of-Correction and rescanned older grants.
   * - APPXML
     - Patent Application Full-Text Data (No Images)
     - 2001-Mar-15 – Present
     - XML
     - Concatenated full-text XML of non-provisional utility and plant patent applications published weekly (Thursdays).
   * - APPMP2
     - Patent Application Multi-Page PDF Images
     - 2001-Mar-15 – Present
     - PDF
     - Multi-page PDF images of non-provisional utility and plant patent applications published weekly (Thursdays).
   * - APPBLXML
     - Patent Application Bibliographic (Front Page) Data
     - 2001-Mar-15 – Present
     - XML
     - Concatenated bibliographic (front page) text of patent applications published weekly (Thursdays); excludes images. Subset of APPXML.
   * - APPDT
     - Patent Application Full Text Data with Embedded TIFF Images
     - 2001-Mar-15 – Present
     - XML
     - Full text, images/drawings, and complex work units (tables, math, chemical structures, genetic sequences) of patent applications published weekly (Thursdays).
   * - PTMNFEE2
     - Patent Maintenance Fee Events
     - 2026-Jan-06 – Present
     - ASCII
     - Cumulative weekly file of recorded maintenance fee events for patents granted from 1981-Sep-01 to present.
   * - PTGRDT
     - Patent Grant Full Text Data with Embedded TIFF Images (Grant Red Book / WIPO ST.36)
     - 2002-Jan-01 – Present
     - XML
     - Full text, images/drawings, and complex work units of patent grants issued weekly (Tuesdays).
   * - GZLST
     - Patent Official Gazettes
     - 2002-Jul-02 – Present
     - HTML
     - Weekly bibliographic information, representative claim, and drawing for each patent grant, plus USPTO Notices.
   * - PTGRXML
     - Patent Grant Full-Text Data (No Images)
     - 2002-Jan-01 – Present
     - ASCII, XML
     - Concatenated full-text of patent grant documents issued weekly (Tuesdays); excludes images.
   * - PTBLXML
     - Patent Grant Bibliographic (Front Page) Text Data
     - 2002-Jan-01 – Present
     - ASCII, XML
     - Concatenated bibliographic (front page) text of patent grant documents issued weekly (Tuesdays); excludes images. Subset of PTGRXML.
   * - CPCMCPT
     - CPC Master Classification Files for U.S. Patent Grants
     - 2025-Jun-17 – Present
     - TXT, XML
     - CPC classification data for all U.S. patent grants from 1790-Jul-31 to present, updated monthly.
   * - CPCMCAPP
     - CPC Master Classification Files for U.S. Patent Applications
     - 2025-Jun-17 – Present
     - TXT, XML
     - CPC classification data for all U.S. patent applications published from 2001-Mar-15 to present, updated monthly.
   * - PVPGPUBTXT
     - PatentsView Pre-Grant Publication Long Text Data
     - 2001-Mar-15 – Present
     - TSV
     - Annual files of long-text fields (Brief Summary, Claims, Detail Description, Drawing Description) for pre-grant publications from 2001 to present.
   * - PVGPATTXT
     - PatentsView Granted Patent Long Text Data
     - 1976-Jan-01 – Present
     - TSV
     - Annual files of long-text fields (Brief Summary, Claims, Detail Description, Drawing Description) for granted patents from 1976 to present.
   * - PVPGPUBDIS
     - PatentsView Pre-Grant Publication Disambiguated Data
     - 2001-Mar-15 – Present
     - TSV
     - 25 files for pre-grant publications from 2001 to present, including disambiguated applicants, assignees, inventors, locations, technology categories, and government interest statements.
   * - PVGPATDIS
     - PatentsView Granted Patent Disambiguated Data
     - 1976-Jan-01 – Present
     - TSV
     - 35 files for granted patents from 1976 to present, including disambiguated assignees, inventors, locations, cited prior art, examiner name, and government interest statements.
   * - PVSORTED
     - PatentsView Sorted Data (Beta)
     - 1976-Jan-01 – Present
     - TSV
     - Reorganized bibliographic data correcting inventor/applicant/assignee ordering inconsistencies introduced by the Leahy-Smith America Invents Act.
   * - PVANNUAL
     - PatentsView Annualized Patent Data
     - 1976-Jan-01 – Present
     - CSV
     - Small annual CSV files derived from PatentsView Granted Patent Disambiguated Data, including inventor gender attribution.
   * - TRTYRAP
     - Trademark Full Text XML Data (No Images) – Annual Applications
     - 1884-Apr-07 – Present
     - XML
     - Backfile of pending and registered trademark text data (no images) from 1884-Apr through 2025-Dec per the U.S. Trademark Applications Version 2.3 DTD.
   * - TRTDXFAG
     - Trademark Full Text XML Data (No Images) – Daily Assignments
     - 2025-Jan-01 – Present
     - XML
     - Trademark assignment text data (no images) for the current calendar year per the Trademark Assignments Version 0.4 DTD.
   * - PASDL
     - Patent Assignment XML (Ownership) Text – Daily
     - 2025-Jan-01 – Present
     - XML
     - Daily patent assignment text (no images) for the current calendar year derived from USPTO assignment recordations.
   * - PASYR
     - Patent Assignment XML (Ownership) Text – Annual
     - 1980-Jan-01 – Present
     - XML
     - Annual backfile of patent assignment text (no images) from 1980-Aug through 2025-Dec.
   * - ECOPATAI
     - Artificial Intelligence Patent Dataset (AIPD)
     - 2021-Jul-30 – 2026-Feb-03
     - DTA, TSV
     - AI patent landscape data classifying 13.2M granted patents and PGPubs from 1976–2020 across eight AI component technologies using machine learning models.
   * - TRTYRAG
     - Trademark Full Text XML Data (No Images) – Annual Assignments
     - 1951-Oct-02 – Present
     - XML
     - Backfile of trademark assignment text data from 1955-Jan-03 through 2025-Dec per the Trademark Assignments Version 0.4 DTD.
   * - TTABYR
     - Trademark Full Text XML Data (No Images) – Annual TTAB
     - 1951-Oct-02 – Present
     - XML
     - Backfile of TTAB text data from 1951-Oct-02 through 2025-Dec per the TTAB Version 1.0 DTD.
   * - PEDSJSON
     - Patent Examination Data System (Bulk Datasets) – JSON
     - 1900-Jan-01 – 2000-Dec-31
     - JSON
     - Static snapshot (created 2025-Mar-17) of patent application data from 1900–2000, migrated from the retired PEDS system, in 20-year increment downloads.
   * - PEDSXML
     - Patent Examination Data System (Bulk Datasets) – XML
     - 1900-Jan-01 – 2000-Dec-31
     - XML
     - Static snapshot (created 2025-Mar-16) of patent application data from 1900–2000, migrated from the retired PEDS system, in 20-year increment downloads.
   * - ECORSEXC
     - Patent Assignment Data for Academia and Researchers
     - 2015-Aug-05 – 2024-Apr-19
     - DTA, TSV
     - ~10M patent assignments and transactions recorded at USPTO since 1970, covering ~17.8M patents and applications.
   * - TRASECO
     - Trademark Assignment Data for Academia and Researchers
     - 2014-Apr-18 – 2024-Apr-01
     - CSV, DTA
     - 1.29M trademark assignments and transactions recorded at USPTO between 1952 and 2023, covering 2.28M unique trademark properties.
   * - TRCFECO2
     - Trademark Case File Data for Academia and Researchers
     - 2013-Jan-02 – 2024-Mar-27
     - CSV, DTA
     - 12.1M trademark applications filed with or registrations issued by USPTO between 1870 and January 2023.
   * - PTLITIG
     - Patent Litigation Docket Report Data Files for Academia and Researchers
     - 2016-Dec-29 – 2024-Mar-27
     - CSV, DTA
     - U.S. District Court patent litigation data on 81,350 unique cases filed 1963–2020, sourced from PACER and RECAP, including parties, cause of action, court location, key dates, and 5M+ docket documents.
   * - ECOPAIR
     - Patent Examination Research Dataset (PatEx)
     - 2015-Dec-02 – 2023-Sep-26
     - CSV, DTA
     - 13M+ publicly viewable patent applications and 1M+ PCT applications through June 2023, including prosecution history, continuation history, foreign priority claims, and PTA history.
   * - PTAPOATH
     - Patent and Patent Application Oath Signature Dataset
     - 2022-Sep-30 – 2022-Sep-30
     - JPEG, JSON
     - 883,811 signature images extracted from patent inventor oath documents from 1998-Sep to 2022-Sep, broken into 8 ZIP files by series code (12–17, 29, 35). 40.5 GB total.
   * - PTOFFACT
     - Patent Application Office Actions Research Dataset
     - 2017-Nov-29 – 2017-Nov-29
     - CSV, DTA
     - 4.4M Office actions mailed 2008–June 2017 for 2.2M publicly viewable applications, including grounds for rejection, claims, and pertinent prior art.
   * - PTGRAPS
     - Patent Grant Full-Text Data (No Images) – APS
     - 1976-Jan-06 – Present
     - ASCII, XML
     - Concatenated full-text of patent grants issued weekly (Tuesdays) from 1976-Jan-01 to 2001-Dec-25; excludes images.
   * - PTBLAPS
     - Patent Grant Bibliographic (Front Page) Text Data – APS
     - 1976-Jan-01 – Present
     - ASCII, XML
     - Concatenated bibliographic (front page) text of patent grants issued weekly (Tuesdays) from 1976-Jan-01 to 2000-Dec-26; excludes images. Subset of PTGRAPS.
   * - PTAPPCLM
     - Patent and Patent Application Claims Research Dataset
     - 2016-Oct-07 – 2016-Oct-11
     - CSV, DTA
     - Claims data for U.S. patents granted 1976–2014 and applications published 2001–2014, including individual claim text, dependency relationships, claim-level and document-level statistics.
   * - MOONSHOT
     - Cancer Moonshot Patent Data Files
     - 2016-Aug-19 – 2016-Aug-19
     - CSV
     - 269,353 patent documents from 1976–2016 curated to identify R&D in diagnostics, therapeutics, data analytics, and model biological systems.
   * - HISTEXC
     - Historical Patent Data Files for Academia and Researchers
     - 2015-Jun-25 – 2015-Jul-02
     - CSV, DTA
     - Four NBER research datasets with time-series and micro-level data by technology sub-category spanning two centuries of patent applications, grants, and in-force patents.
   * - PTBLSGM
     - Patent Grant Bibliographic (Front Page) Text Data – SGML
     - 2001-Jan-02 – Present
     - ASCII, XML
     - Concatenated bibliographic (front page) text of patent grants issued weekly (Tuesdays) from 2001-Jan-02 to 2001-Dec-25; excludes images. Subset of PTGRDSGM.
   * - PTGRDSGM
     - Patent Grant Full Text Data with Embedded TIFF Images (Grant Red Book / WIPO ST.36) – SGML
     - 2001-Jan-02 – Present
     - XML
     - Full text, images/drawings, and complex work units of patent grants issued weekly (Tuesdays) from 2001-Jan-02 to 2001-Dec-25.
   * - PTGRSGM
     - Patent Grant Full-Text Data (No Images) – SGML
     - 2001-Jan-02 – Present
     - ASCII, XML
     - Concatenated full-text of patent grants issued weekly (Tuesdays) from 2001-Jan-02 to 2001-Dec-25; excludes images.
