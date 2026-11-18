Convenience Methods
===================

:class:`~pyUSPTO.clients.patent_data.PatentDataClient` has six convenience methods. Five take a patent number, publication number, or PCT number and return the matching application. ``get_firm_portfolio`` takes customer numbers and returns the applications filed under them. You do not build a search query or look up the application number first.

.. code-block:: python

   from pyUSPTO import PatentDataClient, USPTOConfig

   config = USPTOConfig(api_key="your_api_key_here")
   client = PatentDataClient(config=config)

.. list-table::
   :header-rows: 1
   :widths: 22 40 38

   * - Method
     - Identifier
     - Returns
   * - :meth:`~pyUSPTO.clients.patent_data.PatentDataClient.get_patent`
     - Patent number
     - :class:`~pyUSPTO.models.patent_data.PatentFileWrapper`, or ``None``
   * - :meth:`~pyUSPTO.clients.patent_data.PatentDataClient.get_publication`
     - Pre-grant publication number
     - :class:`~pyUSPTO.models.patent_data.PatentFileWrapper`, or ``None``
   * - :meth:`~pyUSPTO.clients.patent_data.PatentDataClient.get_pct`
     - PCT application number or PCT publication number
     - :class:`~pyUSPTO.models.patent_data.PatentFileWrapper`, or ``None``
   * - :meth:`~pyUSPTO.clients.patent_data.PatentDataClient.get_IFW_metadata`
     - Any one of five identifiers, as keyword arguments
     - :class:`~pyUSPTO.models.patent_data.PatentFileWrapper` with ``document_bag`` filled in, or ``None``
   * - :meth:`~pyUSPTO.clients.patent_data.PatentDataClient.get_IFW`
     - Same five identifiers as ``get_IFW_metadata``
     - :class:`~pyUSPTO.models.patent_data.IFWResult`, or ``None``
   * - :meth:`~pyUSPTO.clients.patent_data.PatentDataClient.get_firm_portfolio`
     - One or more customer numbers, with an optional docket number
     - :class:`~pyUSPTO.models.patent_data.PatentDataResponse`

Look up an application
----------------------

``get_patent``, ``get_publication``, and ``get_pct`` each take one number as a positional argument and return the application's :class:`~pyUSPTO.models.patent_data.PatentFileWrapper`.

Patent number:

.. code-block:: python

   wrapper = client.get_patent("12565253")
   print(wrapper.application_number_text)  # 19378371

Publication number. A ``US`` prefix, a kind code, and separators are optional, so both calls below return the same application:

.. code-block:: python

   wrapper = client.get_publication("US20260054762A1")
   wrapper = client.get_publication("20260054762")
   print(wrapper.application_number_text)  # 19378371

PCT number. ``get_pct`` reads the format of the value. A value that starts with ``PCT`` is an application number and is requested directly. Any other value is treated as a PCT publication number and is searched. Both calls below return the same application:

.. code-block:: python

   wrapper = client.get_pct("PCT/US2025/047756")
   wrapper = client.get_pct("WO 2026/044302")
   print(wrapper.application_number_text)  # PCTUS2025047756

These three methods return metadata only. They do not fetch the application's documents.

Look up an application with its documents
------------------------------------------

``get_IFW_metadata`` returns the same :class:`~pyUSPTO.models.patent_data.PatentFileWrapper` and also calls ``get_application_documents``, so ``document_bag`` lists the application's prosecution documents. All of its arguments are keyword-only.

.. list-table::
   :header-rows: 1
   :widths: 30 25 45

   * - Keyword
     - Lookup
     - Value
   * - ``application_number``
     - Direct request
     - USPTO application number
   * - ``patent_number``
     - Search
     - Patent number
   * - ``publication_number``
     - Search
     - Pre-grant publication number
   * - ``PCT_app_number``
     - Direct request
     - PCT application number
   * - ``PCT_pub_number``
     - Search
     - PCT publication number

Pass exactly one identifier. Passing more than one raises ``ValueError``.

.. code-block:: python

   wrapper = client.get_IFW_metadata(publication_number="20260054762")
   print(wrapper.application_number_text)  # 19378371
   for doc in wrapper.document_bag or []:
       print(doc.document_code, doc.document_identifier)

Download the documents
----------------------

``get_IFW`` takes the same five identifiers as ``get_IFW_metadata``. It looks up the application, then downloads each prosecution document that has a PDF or Word format.

It also takes three download arguments:

1. ``destination``: the directory for the output. The default is the current directory.
2. ``overwrite``: whether to replace existing output. The default is ``False``.
3. ``as_zip``: whether to package the downloads in one ZIP file. The default is ``True``.

The output location depends on ``as_zip``, with ``<app>`` standing for the application number:

1. ``as_zip=True``: one ZIP file at ``<destination>/<app>_ifw.zip``.
2. ``as_zip=False``: individual files in the directory ``<destination>/<app>_ifw``.

The method behaves as follows:

1. A document with no PDF or Word format, such as a non-patent literature reference, is skipped without a warning.
2. A document that has a download URL but fails to download produces a warning. The remaining documents still download.
3. If the output path already exists and ``overwrite`` is ``False``, ``FileExistsError`` is raised.
4. If no application matches, the method returns ``None``.

The result is an :class:`~pyUSPTO.models.patent_data.IFWResult` with three attributes:

1. ``wrapper``: the :class:`~pyUSPTO.models.patent_data.PatentFileWrapper`, with ``document_bag`` filled in.
2. ``output_path``: the absolute path of the ZIP file or the output directory.
3. ``downloaded_documents``: a dictionary from each ``document_identifier`` to its file name. A skipped or failed document is not in the dictionary.

.. code-block:: python

   result = client.get_IFW(application_number="14412875", destination="./downloads")
   if result:
       print(result.output_path)
       for doc in result.wrapper.document_bag or []:
           filename = result.downloaded_documents.get(doc.document_identifier)
           print(doc.document_code, filename or "(skipped)")

For a complete script, see :doc:`examples/ifw_example`.

Look up a firm's applications
-----------------------------

``get_firm_portfolio`` takes a list of customer numbers and an optional ``docket_number``. The docket filter is combined with the customer numbers:

.. code-block:: python

   response = client.get_firm_portfolio(customer_numbers=[30589], docket_number="4704.028")
   print(response.count)  # 1
   print(response.patent_file_wrapper_data_bag[0].application_number_text)  # 18915708

A single word containing ``*`` or ``?`` is a wildcard pattern. The call below returns three applications: ``18915708``, ``PCTUS2024051265``, and ``63709062``.

.. code-block:: python

   response = client.get_firm_portfolio(customer_numbers=[30589], docket_number="4704.02*")
   print(response.count)  # 3

``docket_number`` takes one docket number or a list of docket numbers.

A value with whitespace or one of the characters ``+ - & | ! ( ) { } [ ] ^ " ~ : \ / < > =`` is quoted and matches exactly only, and so is the bare word ``AND``, ``OR``, ``NOT``, or ``TO``.

When nothing matches
--------------------

1. Every method on this page raises ``ValueError`` for a value it cannot read, such as a malformed number or an empty list, and ``get_IFW_metadata`` and ``get_IFW`` raise it when more than one identifier is passed.
2. The lookups that use a search (``get_patent``, ``get_publication``, ``get_pct`` with a publication number, and the ``patent_number``, ``publication_number``, and ``PCT_pub_number`` keywords) return ``None`` for a well-formed number that matches no application. The search endpoint answers "no matches" with HTTP 404, and these methods catch the 404.
3. ``get_firm_portfolio`` raises ``USPTOApiNotFoundError`` when no application matches, including a docket filed under a different customer number.
