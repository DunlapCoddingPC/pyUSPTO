# Changelog

All notable changes to the pyUSPTO package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Full support for USPTO Final Petition Decisions API
- `FinalPetitionDecisionsClient` for interacting with petition decisions
- New data models for petition decisions:
  - `PetitionDecision`: Complete petition decision information
  - `PetitionDecisionDocument`: Document details and metadata
  - `DocumentDownloadOption`: Download options for petition documents
  - `PetitionDecisionResponse`: API response wrapper
  - `PetitionDecisionDownloadResponse`: Download response wrapper
- Enums for petition decision data:
  - `DecisionTypeCode`: Petition decision types
  - `DocumentDirectionCategory`: Document direction categories
- Search capabilities with convenience parameters:
  - Application number, patent number, technology center
  - Decision date ranges, applicant names, inventor names
  - Examiner names, decision types, and more
- Pagination support for petition decision searches
- Document download functionality for petition documents
- CSV and JSON export options for petition decisions
- Integration tests for petition decisions (17 tests)
- Unit tests for petition decision models and client (49 tests)
- Example usage file: `examples/petition_decisions_example.py`
- Configuration support for petition decisions base URL in `USPTOConfig`

## [0.1.2]

### Added

- Initial release of pyUSPTO
- Object Oriented Support for USPTO Patent Data API
- Basic Support for USPTO Bulk Data API
- Full type annotations and docstrings
- Comprehensive test suite
