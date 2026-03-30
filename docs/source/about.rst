About pyUSPTO
=============

pyUSPTO is a Python client library for interacting with the `USPTO Open Data Portal (ODP) <https://data.uspto.gov/home>`_ APIs.
The library handles authentication, HTTP session management, pagination, and response deserialization,
so you can work directly with typed Python objects instead of raw JSON.

The source code for the pyUSPTO library is available on `GitHub <https://github.com/DunlapCoddingPC/pyUSPTO>`_ and is licensed under the MIT License. Contributions are welcome! Please see the :doc:`contributing guidelines <development>`.

What is the USPTO Open Data Portal?
------------------------------------

The USPTO Open Data Portal is the United States Patent and Trademark Office's primary API platform
for publicly available patent and trademark data. It provides programmatic access to patent applications,
grants, bulk data downloads, PTAB proceedings, Office Actions, and more.

.. note::

   An API key is required to use the ODP APIs. You can register for one at the
   `USPTO Open Data Portal <https://data.uspto.gov/myodp/landing>`_.

Available Clients
-----------------

pyUSPTO provides the following clients:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Client
     - Description
   * - :class:`~pyUSPTO.PatentDataClient`
     - Search patent applications and grants, retrieve file wrappers and Image File Wrapper (IFW) documents, and download individual documents and publications.
   * - :class:`~pyUSPTO.BulkDataClient`
     - Search and download bulk data products from the ODP Bulk Dataset Directory, including patent grants, applications, assignments, and research datasets.
   * - :class:`~pyUSPTO.FinalPetitionDecisionsClient`
     - Search and retrieve Final Petition Decisions issued by the USPTO Director.
   * - :class:`~pyUSPTO.PTABTrialsClient`
     - Search PTAB trial proceedings (IPR, PGR, CBM, and derivation), documents, and decisions.
   * - :class:`~pyUSPTO.PTABAppealsClient`
     - Search PTAB ex parte appeal decisions by application number, technology center, examiner, and more.
   * - :class:`~pyUSPTO.PTABInterferencesClient`
     - Search PTAB interference decisions.
   * - :class:`~pyUSPTO.EnrichedCitationsClient`
     - Search enriched citation data linking cited references to the specific claims and rejections they support.
   * - :class:`~pyUSPTO.OAActionsClient`
     - Full-text search of Office Action documents, including body text and structured section data.
   * - :class:`~pyUSPTO.OARejectionsClient`
     - Search rejection-level data from Office Actions, including rejection type, claims, and examiner metadata.
   * - :class:`~pyUSPTO.OACitationsClient`
     - Search citation data from Office Actions derived from Form PTO-892, Form PTO-1449, and Office Action text.

Requirements
------------

- Python 3.10 or higher
- A USPTO Open Data Portal API key
