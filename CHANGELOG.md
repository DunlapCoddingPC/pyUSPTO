# Changelog

All notable changes to the pyUSPTO package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
