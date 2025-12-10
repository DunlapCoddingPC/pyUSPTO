# Changelog

All notable changes to the pyUSPTO package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - TBD

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
