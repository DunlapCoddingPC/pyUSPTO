# Changelog

All notable changes to the pyUSPTO package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.5.5] - 2026-07-22

### Added

- `PatentDataClient.get_firm_portfolio(customer_numbers, ...)` — helper that searches a law firm's portfolio across one or more USPTO Customer Numbers. Builds a single Lucene `OR` query, applies a named field preset by default, and returns a `PatentDataResponse`. Pairs with `get_application_metadata` / `get_application_by_number` for per-application drill-down.
- `FIELD_PRESETS` constant (exported from `pyUSPTO`) — three named field sets for `get_firm_portfolio`'s `fields` argument: `"minimal"` (8 firm-internal identifiers), `"portfolio"` (16 fields for status + deadline derivation, default), and `"full_meta"` (uses the API's `applicationMetaData` shorthand for the entire 27-key metadata object, ~7.5× payload reduction vs. the un-fielded default).
- Multi-value `customer_number_q` and `status_code_q` on `search_applications` and `get_search_results` — accept a single value or a list; lists are OR-joined as `field:(a OR b)`.
- New `status_date_from_q` / `status_date_to_q` on `search_applications` and `get_search_results` — date-range filters against `applicationMetaData.applicationStatusDate`, mirroring the existing `filing_date` and `grant_date` range params. Useful for bounding the deadline-coming-due horizon.

### Changed

- **Breaking**: `sanitize_application_number` now emits the standardized 15-character PCT format (`PCT` + 2-char country + 4-digit year + 6-digit zero-padded serial, e.g. `PCTUS2024012345`) per USPTO ODP Release 3.6 (2026-04-10). Previously emitted a non-standard 12-character form (e.g. `PCTUS2412345`). Affects every endpoint that takes a PCT application number, including `get_pct`, `get_application_by_number`, and `get_IFW_metadata(PCT_app_number=...)`. 2-digit year inputs are expanded via a sliding window (YY≥78 → 19YY, else 20YY). Legacy 12-character PCT strings are no longer accepted as input.

### Deprecated

- `Address.country_or_state_code` — USPTO ODP Release 3.6 removed `countryOrStateCode` from the Patent Assignment API response; the location data now lives in `geographicRegionCode` (already exposed as `Address.geographic_region_code`). The attribute remains for backward compatibility and will be `None` for responses from updated endpoints.

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
