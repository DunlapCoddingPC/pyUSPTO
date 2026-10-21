# Changelog

All notable changes to the pyUSPTO package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Python 3.15 support.
- `PetitionDecision` fields from USPTO ODP Release 5.0: `decided_petition_type_code`, `decided_petition_type_code_description_text`, `decision_mail_date`, `application_status_date`, `application_status_description_text`, `final_petition_decision_indicator`, `ocr_search_text`, `all_searchable_fields`, and `last_modified_date_time`. Also `decision_petition_type_code_description_text`, which the API returned but the model never read.
- `PetitionDecisionsClient.search_decisions(decided_petition_type_code_q=...)` filters on `decidedPetitionTypeCode`.

### Changed

- **Breaking:** `FinalPetitionDecisionsClient` is renamed `PetitionDecisionsClient`. Since USPTO ODP Release 5.0 the Petition Decisions API returns final and non-final decisions, so the old name no longer fit. `FinalPetitionDecisionsClient` is now a subclass that restricts every search, pagination, and `download_decisions` call to final decisions (`finalPetitionDecisionIndicator` true) and returns `None` from `get_decision_by_id` for a non-final decision. Code that used `FinalPetitionDecisionsClient` for all decisions must switch to `PetitionDecisionsClient`.
- `DecisionTypeCode` now covers all four decided types: `GRANTED` (`A`), `GRANTED_IN_PART` (`B`), `DENIED` (`C`), and `DISMISSED` (`D`).
- **Breaking:** `PetitionDecision.decision_petition_type_code` is now a `str`, matching the API.
- `DocumentMimeType` is now a `StrEnum`. `str()` and f-strings return the value (`"PDF"`) instead of `"DocumentMimeType.PDF"`. Equality with plain strings and `.value` are unchanged.
- `PetitionDecisionsClient.search_decisions(sort=...)` accepts a list of sort keys, sent as repeated `sort` parameters (the API rejects comma-joined keys).

### Removed

- **Breaking:** Dropped support for Python 3.10, which has reached end of life. The minimum supported version is now Python 3.11.
- `typing-extensions` is no longer a dependency; `Self` is imported from `typing` directly.
- **Breaking:** `PetitionDecision.decision_type_code`, `decision_type_code_description_text`, and `last_ingestion_datetime`, and `search_decisions(decision_type_code_q=...)`. USPTO ODP Release 5.0 replaced `decisionTypeCode` with `decidedPetitionTypeCode`, and the API sends `lastModifiedDateTime` instead of `lastIngestionDateTime`, so these were always `None` and the filter never matched. Use the new fields under Added.
- **Breaking:** `PetitionDecisionDocument.direction_category` and the `DocumentDirectionCategory` enum. Petition decision documents have no `directionCategory` (0 of 1,116,161 decisions), so the attribute was always `None`.

### Fixed

- `Document.direction_category` (patent application documents) was always `None`. The model read `documentDirectionCategory`, but the API sends `directionCategory`. `to_dict()` now emits `directionCategory`, and `DirectionCategory` gains `INTERNAL`, which the API uses for about a fifth of documents.
- `earliestPublicationNumber_q` (used by `search_applications`, `get_publication`, and `get_IFW_metadata(publication_number=...)`) is now reduced to its digits and searched with wildcards, so bare digits (`20210138233`), `US`-prefixed forms, kind codes, and separators (`US 2021/0138233 A1`) all match the stored `USyyyyNNNNNNNAn` value. Previously the value was sent verbatim and bare digits never matched. Values already containing `*` pass through unchanged.
- `get_patent`, `get_publication`, `get_pct` (publication form), and the search-based branches of `get_IFW_metadata` now return `None` on no match, as documented. The search endpoint answers no-match with HTTP 404, which previously surfaced as `USPTOApiNotFoundError`.
- Unit tests no longer depend on `USPTO_*` variables set in the developer's shell. An autouse fixture in `tests/conftest.py` clears every variable `USPTOConfig` reads (`USPTO_API_KEY`, the `USPTO_*_BASE_URL` variables, and the HTTP-setting variables such as `USPTO_REQUEST_TIMEOUT`) before each unit test.
- `petition_decisions_example.py` no longer fails when rerun (its document download now passes `overwrite=True`), and its pagination example prints each decision under a page header.
- Pagination (`paginate_*` on every client) requested one page past the end, and failed with a 404, when the total number of results was an exact multiple of the page size.
- POST pagination in `paginate_applications`, `paginate_decisions` (petitions, PTAB appeals, PTAB interferences), and `paginate_proceedings` failed with a 400 unless `post_body` already had a `pagination` dict, because the API rejects top-level `offset`/`limit`. Offset and limit now always go in `post_body["pagination"]`, and a top-level `limit` raises `ValueError`.
- `paginate_decisions` repeated and skipped decisions (about 1 in 5) because the API orders tied records differently on each request. It now appends `petitionDecisionRecordIdentifier asc` to the sort.

## [0.5.5] - 2026-07-22

### Added

- `PatentDataClient.get_firm_portfolio(customer_numbers, ...)` — helper that searches a law firm's portfolio across one or more USPTO Customer Numbers. Builds a single Lucene `OR` query, applies a named field preset by default, and returns a `PatentDataResponse`. Pairs with `get_application_metadata` / `get_application_by_number` for per-application drill-down.
- `FIELD_PRESETS` constant (exported from `pyUSPTO`) — three named field sets for `get_firm_portfolio`'s `fields` argument: `"minimal"` (8 firm-internal identifiers), `"portfolio"` (16 fields for status + deadline derivation, default), and `"full_meta"` (uses the API's `applicationMetaData` shorthand for the entire 27-key metadata object, ~7.5× payload reduction vs. the un-fielded default).
- Multi-value `customer_number_q` and `status_code_q` on `search_applications` and `get_search_results` — accept a single value or a list; lists are OR-joined as `field:(a OR b)`.
- New `status_date_from_q` / `status_date_to_q` on `search_applications` and `get_search_results` — date-range filters against `applicationMetaData.applicationStatusDate`, mirroring the existing `filing_date` and `grant_date` range params. Useful for bounding the deadline-coming-due horizon.

## [0.5.4] - 2026-05-27

### Changed

- **Breaking**: `sanitize_application_number` now emits the standardized 15-character PCT format (`PCT` + 2-char country + 4-digit year + 6-digit zero-padded serial, e.g. `PCTUS2024012345`) per USPTO ODP Release 3.6 (2026-04-10). Previously emitted a non-standard 12-character form (e.g. `PCTUS2412345`). Affects every endpoint that takes a PCT application number, including `get_pct`, `get_application_by_number`, and `get_IFW_metadata(PCT_app_number=...)`. 2-digit year inputs are expanded via a sliding window (YY≥78 → 19YY, else 20YY). Legacy 12-character PCT strings are no longer accepted as input.
- `USPTOConfig` now applies user > env > default precedence uniformly across all fields. Previously only `api_key` fell back to its environment variable; base URLs and `HTTPConfig` ignored env in the constructor. Env reading is consolidated in an internal `_env_values()` helper shared by `__init__` and `from_env`.

### Deprecated

- `Address.country_or_state_code` — USPTO ODP Release 3.6 removed `countryOrStateCode` from the Patent Assignment API response; the location data now lives in `geographicRegionCode` (already exposed as `Address.geographic_region_code`). The attribute remains for backward compatibility and will be `None` for responses from updated endpoints.

### Fixed

- `USPTO_API_KEY=""` was stored as `""` instead of `None`, breaking `is None` checks. Empty-string constructor arguments are now treated as no-value and fall back to env.

## [0.5.3] - 2026-05-13

### Changed

- Maintenance release: dependency updates only (including urllib3 v2.7.0 security update); no library code changes.

## [0.5.2] - 2026-04-16

### Added

- `PatentDataClient.stream_document(document, format)` — returns a streaming `requests.Response` the caller consumes via `iter_content()` or `iter_lines()`. Accepts the same `format` argument (`DocumentMimeType` enum or MIME string) as `download_document` and raises the same `FormatNotAvailableError` on an unavailable format. The returned response is the caller's responsibility — use as a context manager or call `.close()` when finished.
- Streaming download example in `examples/patent_data_example.py`
- Bulk Data product identifier reference table in the documentation

### Changed

- `stream_document` and `download_document` now share format resolution through an internal `_resolve_document_format` helper, so both methods raise identical errors for missing formats or missing download URLs. No changes to existing `download_document` behavior.

## [0.5.1] - 2026-03-30

### Added

- `OAActionsClient` — Office Action Text Retrieval API (v1): full-text office action documents including body text and structured section data (§101/102/103/112 rejections, citations, etc.)
- `OARejectionsClient` — Office Action Rejections API (v2): rejection-level records with rejection type indicators (`hasRej101/102/103/112/DP`), claim arrays, and examiner classification metadata
- `OACitationsClient` — Office Action Citations API: enriched citation records from office actions including cited document identifiers, legal section codes, and examiner-cited indicators
- Config and environment variable support for the three new base URLs (`USPTO_OA_ACTIONS_BASE_URL`, `USPTO_OA_REJECTIONS_BASE_URL`, `USPTO_OA_CITATIONS_BASE_URL`)

## [0.5.0] - 2026-03-27

### Added

- `EnrichedCitationsClient` for the USPTO Enriched Cited Reference Metadata API (v3) — citation data extracted from patent office actions using AI/NLP, including citation category codes (X/Y/A/etc.), passage locations in the prior art, rejected claims, and examiner vs. applicant citation indicators
- Client methods: `search_citations()` (POST-based search with convenience parameters), `paginate_citations()` (auto-paginating iterator), and `get_fields()`
- Models: `EnrichedCitation` (21 fields), `EnrichedCitationResponse`, `EnrichedCitationFieldsResponse`

## [0.4.5] - 2026-03-11

### Changed

- **Refactor**: Split `_make_request` into three typed request methods:
  - `_get_model` — returns parsed model `T`
  - `_get_json` — returns `dict[str, Any]`
  - `_stream_request` — returns `requests.Response`
- Removed all `assert isinstance` runtime checks and `# type: ignore` annotations at 28 call sites
- `DocumentBag`, `StatusCodeSearchResponse`, and `PetitionDecisionDownloadResponse` now conform to `FromDictProtocol` (`include_raw_data` parameter added to `from_dict`)

### Fixed

- PTAB appeals integration test query (`Appeal` → `REGULAR` for `applicationTypeCategory`)
- Read the Docs build: updated Python from 3.10 to 3.14 to satisfy `myst-parser>=3.11` requirement

## [0.4.4] - 2026-03-08

### Added

- `get_patent(patent_number)` — lookup `PatentFileWrapper` by granted patent number
- `get_publication(publication_number)` — lookup by publication number
- `get_pct(pct_number)` — lookup by PCT application or publication number (auto-detected)

### Fixed

- `sanitize_application_number` now strips leading zeros from PCT serial numbers

## [0.4.3] - 2026-03-05

### Added

- `get_IFW` method for bulk downloading all documents in an application's IFW
- `IFWResult` model with document map and optional ZIP output
- `get_IFW_metadata` now populates `document_bag` on the returned `PatentFileWrapper`
- Example: searching CPC codes (#102)

### Fixed

- Auto-quote `classification_q` values containing spaces or slashes (#101)
- Missing `typing_extensions` dependency
- CI refactor to exclude dev requirements from install

## [0.4.2] - 2026-02-26

### Fixed

- Quote multi-word values in query convenience parameters

## [0.4.1] - 2026-02-25

### Added

- Download path validation and zip-bomb protection
- Sanitize download filenames to prevent path traversal
- Skip symlinks during archive extraction
- Session lifecycle and extraction safety documentation

### Changed

- Enable retries for POST requests
- Remove unused `utils.http` module and `ALLOWED_METHODS`
- Enforce keyword-only arguments in `get_IFW_metadata`
- Optimize tox deps and enable parallel

## [0.4.0] - 2026-02-23

### Changed

- **Refactor**: Centralize session management in `USPTOConfig`
- `FileData.file_date` changed to `datetime` type

### Fixed

- Prevent path traversal in archive extraction
- Fix #79

## [0.3.4] - 2026-01-11

### Added

- JSON parsing error handling
- Pagination validation
- Documentation for HTTP method restrictions and `include_raw_data` flag

### Changed

- Aligned backoff factor default

## [0.3.3] - 2026-01-08

### Changed

- Bulk data client refactor (#40)

## [0.3.2] - 2025-12-31

### Changed

- Refactor downloads (#35)
- Configurable download chunk size
- Session sharing across clients

## [0.3.1] - 2025-12-15

### Added

- `paginate_decisions` POST support
- Configurable download chunk size
- Session sharing across clients
- Bulk data endpoint updates

## [0.3.0] - 2025-12-09

### Added

- **PTAB API 3.0 Support**: New clients for PTAB trials, appeals, and interferences
  - `PTABTrialsClient` - Search trial proceedings, documents, and decisions
  - `PTABAppealsClient` - Search ex parte appeal decisions
  - `PTABInterferencesClient` - Search interference decisions
- New data models in `pyUSPTO.models.ptab` for PTAB responses:
  - `PTABTrialProceeding`, `PTABAppealDecision`, `PTABInterferenceDecision`
  - Supporting models for party data, metadata, and decision information
- Configuration support for PTAB base URL in `USPTOConfig`
- Comprehensive examples for all three PTAB clients (`examples/ptab_*.py`)
- Additional convenience parameters for `PTABTrialsClient` search methods:
  - `search_documents()`: petitioner name, inventor, patent details, real party in interest
  - `search_decisions()`: trial type, patent/application numbers, status, party information, document category

### Changed

- Enhanced `PTABTrialsClient.search_documents()` with convenience parameters for petitioner, inventor, patent details
- Enhanced `PTABTrialsClient.search_decisions()` with convenience parameters for trial type, status, and party information

## [0.2.2]

### Added

- Assignment fields: `image_available_status_code`, `attorney_docket_number`, `domestic_representative`
- Address fields: `country_or_state_code`, `ict_state_code`, `ict_country_code`
- PCT application number format support in `sanitize_application_number()`

### Changed

- **BREAKING**: Assignment `correspondence_address_bag` changed to `correspondence_address` (single object, not list)
- All `PatentDataClient` methods now automatically sanitize application numbers before API requests

## [0.2.1]

### Added

- `USPTODataMismatchWarning` for API data validation
- `sanitize_application_number()` method supporting 8-digit and series code formats
- Optional `include_raw_data` parameter in `USPTOConfig` for debugging
- Content-Disposition header parsing with RFC 2231 support
- `HTTPConfig` class for configurable timeouts, retries, and headers
- `USPTOTimeout` and `USPTOConnectionError` exceptions
- Document type filtering in `get_application_documents()`
- Utility module `models/utils.py` for shared model helpers

### Changed

- Response models now support optional `include_raw_data` parameter
- Replaced print statements with Python warnings module
- Refactored base client to use `HTTPConfig`

## [0.2.0]

### Added

- Full support for USPTO Final Petition Decisions API
- `FinalPetitionDecisionsClient` with search, pagination, and document download
- Data models: `PetitionDecision`, `PetitionDecisionDocument`, `PetitionDecisionResponse`
- Enums: `DecisionTypeCode`, `DocumentDirectionCategory`
- CSV and JSON export for petition decisions

## [0.1.2]

### Added

- Initial release
- USPTO Patent Data API support
- USPTO Bulk Data API support
