"""
Tests for PTAB models.

This module contains unit tests for the PTAB model classes with full coverage.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict
import importlib
from unittest.mock import patch

import pytest

from pyUSPTO.models.ptab import (
    # Base and shared models
    PartyData,
    # Trial Proceedings Models
    TrialMetaData,
    PatentOwnerData,
    RegularPetitionerData,
    RespondentData,
    DerivationPetitionerData,
    PTABTrialProceeding,
    PTABTrialProceedingResponse,
    # Trial Documents/Decisions Models
    TrialDocumentData,
    TrialDecisionData,
    PTABTrialDocument,
    PTABTrialDocumentResponse,
    # Appeal Decisions Models
    AppealMetaData,
    AppellantData,
    RequestorData,
    AppealDocumentData,
    DecisionData,
    PTABAppealDecision,
    PTABAppealResponse,
    # Interference Decisions Models
    InterferenceMetaData,
    SeniorPartyData,
    JuniorPartyData,
    AdditionalPartyData,
    InterferenceDocumentData,
    PTABInterferenceDecision,
    PTABInterferenceResponse,
)


# Sample API response fixtures for round-trip testing
@pytest.fixture
def trial_proceeding_api_sample() -> Dict[str, Any]:
    """Sample trial proceeding API response for testing."""
    return {
        "count": 1,
        "requestIdentifier": "4649ea27-4192-4ea4-86f9-e033ca24c17a",
        "patentTrialProceedingDataBag": [
            {
                "lastModifiedDateTime": "2025-11-20T01:27:05",
                "respondentData": {
                    "patentOwnerName": "ADAMS et al",
                    "patentNumber": "9780412",
                    "grantDate": "2017-10-03",
                    "technologyCenterNumber": "1700",
                    "groupArtUnitNumber": "1725",
                    "applicationNumberText": "15461849",
                    "inventorName": "Brian D. ADAMS et al",
                },
                "patentOwnerData": {
                    "patentOwnerName": "ADAMS et al",
                    "patentNumber": "9780412",
                    "grantDate": "2017-10-03",
                    "technologyCenterNumber": "1700",
                    "groupArtUnitNumber": "1725",
                    "applicationNumberText": "15461849",
                    "inventorName": "Brian D. ADAMS et al",
                },
                "trialMetaData": {
                    "accordedFilingDate": "2018-07-20",
                    "terminationDate": "2019-01-30",
                    "trialTypeCode": "DER",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/DER/2018/00018/DER2018-00018.zip",
                    "trialStatusCategory": "Terminated-Settled",
                    "trialLastModifiedDate": "2020-06-04",
                    "petitionFilingDate": "2018-07-20",
                    "trialLastModifiedDateTime": "2020-06-04T13:49:04",
                },
                "trialNumber": "DER2018-00018",
                "regularPetitionerData": {"counselName": "Todd Baker"},
                "derivationPetitionerData": {
                    "technologyCenterNumber": "1700",
                    "groupArtUnitNumber": "1722",
                    "applicationNumberText": "15513914",
                    "inventorName": "Brian D. ADAMS et al",
                    "counselName": "Todd Baker",
                },
            }
        ],
    }


@pytest.fixture
def trial_decision_api_sample() -> Dict[str, Any]:
    """Sample trial decision API response for testing."""
    return {
        "count": 1,
        "requestIdentifier": "e303e566-a896-4b1e-9b22-1f8b1b1cc5cf",
        "patentTrialDocumentDataBag": [
            {
                "trialNumber": "IPR2025-01319",
                "lastModifiedDateTime": "2025-11-21T03:56:35",
                "trialDocumentCategory": "Decision",
                "trialMetaData": {
                    "institutionDecisionDate": "2025-11-20",
                    "accordedFilingDate": "2025-07-17",
                    "petitionFilingDate": "2025-07-17",
                    "trialLastModifiedDateTime": "2025-11-20T15:34:55",
                    "trialLastModifiedDate": "2025-11-20",
                    "terminationDate": "2025-11-20",
                    "trialStatusCategory": "Discretionary Denial",
                    "latestDecisionDate": "2025-11-20",
                    "trialTypeCode": "IPR",
                },
                "patentOwnerData": {
                    "applicationNumberText": "17980669",
                    "counselName": "Cohen, Alexiset al",
                    "grantDate": "2023-07-18",
                    "groupArtUnitNumber": "2884",
                    "inventorName": "Yong Qin Chen",
                    "realPartyInInterestName": "Beckman Coulter, Inc. et al.",
                    "patentNumber": "11703443",
                    "technologyCenterNumber": "2800",
                },
                "regularPetitionerData": {
                    "counselName": "Knight, Dustinet al",
                    "realPartyInInterestName": "Cytek Biosciences, Inc.",
                },
                "documentData": {
                    "documentTypeDescriptionText": "RESPONSE",
                    "documentFilingDate": "2025-11-20",
                    "documentIdentifier": "171242096",
                    "documentName": "20251120 Director Notice Regarding Institution Paper 13.pdf",
                    "documentNumber": 13,
                    "documentSizeQuantity": 85780,
                    "documentTitleText": "Director Discretionary Decision: Deny",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/IPR/2025/01319/171242096.pdf",
                    "filingPartyCategory": "BOARD",
                    "documentOCRText": "Trials@uspto.gov  Paper 13",
                },
                "decisionData": {
                    "statuteAndRuleBag": ["35 USC 314", "35 USC 324"],
                    "decisionIssueDate": "2025-11-20",
                    "decisionTypeCategory": "Decision",
                    "trialOutcomeCategory": "Institution Denied",
                },
            }
        ],
    }


@pytest.fixture
def trial_document_api_sample() -> Dict[str, Any]:
    """Sample trial document API response for testing."""
    return {
        "count": 2,
        "requestIdentifier": "e02d1512-7e81-489f-9c98-4d0c6070864e",
        "patentTrialDocumentDataBag": [
            {
                "trialNumber": "DER2023-00012",
                "lastModifiedDateTime": "2025-11-20T01:22:58",
                "trialDocumentCategory": "Document",
                "trialMetaData": {
                    "accordedFilingDate": "2023-05-11",
                    "petitionFilingDate": "2023-05-11",
                    "trialLastModifiedDateTime": "2025-07-24T12:21:16",
                    "trialLastModifiedDate": "2025-07-24",
                    "trialStatusCategory": "Pending",
                    "trialTypeCode": "DER",
                },
                "patentOwnerData": {
                    "applicationNumberText": "17522731",
                    "counselName": "Ringenberg, Scotet al",
                    "groupArtUnitNumber": "3676",
                    "inventorName": "Nicholas Kleinschmit et al",
                    "realPartyInInterestName": "Holmberg, Aaron et al.",
                    "technologyCenterNumber": "3600",
                },
                "regularPetitionerData": {
                    "counselName": "Brewer, Peteret al",
                    "realPartyInInterestName": "Rasmussen, Jon et al.",
                },
                "respondentData": {
                    "applicationNumberText": "17522731",
                    "counselName": "Ringenberg, Scotet al",
                    "groupArtUnitNumber": "3676",
                    "inventorName": "Nicholas Kleinschmit et al",
                    "realPartyInInterestName": "Holmberg, Aaron et al.",
                    "technologyCenterNumber": "3600",
                },
                "derivationPetitionerData": {
                    "applicationNumberText": "17846932",
                    "counselName": "Brewer, Peteret al",
                    "groupArtUnitNumber": "3674",
                    "inventorName": "Jon Randall Rasmussen et al",
                    "realPartyInInterestName": "Rasmussen, Jon et al.",
                    "patentOwnerName": "Rasmussen, JonRandall",
                    "technologyCenterNumber": "3600",
                },
                "documentData": {
                    "documentTypeDescriptionText": "ORDER",
                    "documentFilingDate": "2025-07-24",
                    "documentIdentifier": "171138150",
                    "documentName": "Order Limited Remand Final  DER2023-00012 Circ.pdf",
                    "documentNumber": 25,
                    "documentSizeQuantity": 94697,
                    "documentTitleText": "ORDER Conduct of Proceeding Limited Remand 37 C.F.R. § 42.5(a)",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/DER/2023/00012/171138150.pdf",
                    "filingPartyCategory": "BOARD",
                },
                "decisionData": {"statuteAndRuleBag": []},
            },
            {
                "trialNumber": "DER2022-00004",
                "lastModifiedDateTime": "2025-11-20T01:22:56",
                "trialDocumentCategory": "Decision",
                "trialMetaData": {
                    "institutionDecisionDate": "2023-11-28",
                    "accordedFilingDate": "2022-03-17",
                    "petitionFilingDate": "2022-03-17",
                    "trialLastModifiedDateTime": "2023-12-29T00:00:02",
                    "trialLastModifiedDate": "2023-12-29",
                    "terminationDate": "2023-11-28",
                    "trialStatusCategory": "Institution Denied",
                    "latestDecisionDate": "2023-11-28",
                    "trialTypeCode": "DER",
                },
                "patentOwnerData": {
                    "applicationNumberText": "17018233",
                    "counselName": "Miotke, Josephet al",
                    "grantDate": "2024-05-21",
                    "groupArtUnitNumber": "2144",
                    "inventorName": "Grant Vergottini",
                    "realPartyInInterestName": "Xcential Corporation",
                    "patentNumber": "11989794",
                    "technologyCenterNumber": "2100",
                },
                "regularPetitionerData": {
                    "counselName": "Totten, Jeffreyet al",
                    "realPartyInInterestName": "Akin Gump Strauss Hauer & Feld LLP et al.",
                },
                "respondentData": {
                    "applicationNumberText": "17018233",
                    "counselName": "Miotke, Josephet al",
                    "grantDate": "2024-05-21",
                    "groupArtUnitNumber": "2144",
                    "inventorName": "Grant Vergottini",
                    "realPartyInInterestName": "Xcential Corporation",
                    "patentNumber": "11989794",
                    "technologyCenterNumber": "2100",
                },
                "derivationPetitionerData": {
                    "applicationNumberText": "17696389",
                    "counselName": "Totten, Jeffreyet al",
                    "groupArtUnitNumber": "2144",
                    "inventorName": "Louis AGNELLO",
                    "realPartyInInterestName": "Akin Gump Strauss Hauer & Feld LLP et al.",
                    "technologyCenterNumber": "2100",
                },
                "documentData": {
                    "documentTypeDescriptionText": "DECISION",
                    "documentFilingDate": "2023-11-28",
                    "documentIdentifier": "170697659",
                    "documentName": "DER2022-00004 Institution Decision.pdf",
                    "documentNumber": 15,
                    "documentSizeQuantity": 382075,
                    "documentTitleText": "Institution Decision:  Deny",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/DER/2022/00004/170697659.pdf",
                    "filingPartyCategory": "BOARD",
                    "documentOCRText": "DER2022-00004 Akin Gump Strauss Hauer & Feld LLP et al. v. Xcential Corporation\n\n\nTrials@uspto.gov  Paper 15 \n571-272-7822  Date: November 28, 2023 \n \n\n \n\nUNITED STATES PATENT AND TRADEMARK OFFICE \n \n\nBEFORE THE PATENT TRIAL AND APPEAL BOARD \n \n\n \n \n\nAKIN GUMP STRAUSS HAUER & FELD LLP, \nPetitioner Application 17/696,389, \n\nPetitioner,  \n \n\nv. \n  \n\nXCENTIAL CORP., \nRespondent Application 17/018,233, \n\nRespondent.  \n____________ \n\n \nDER2022-00004 \n______________ \n\n \nBefore JAMESON LEE, JUSTIN T. ARBES",
                },
                "decisionData": {
                    "statuteAndRuleBag": [
                        "37 CFR 42.405",
                        " 47 CFR 42.401",
                        " 40 CFR 42.401",
                        "37 CFR 42.408",
                    ],
                    "decisionIssueDate": "2023-11-28",
                    "decisionTypeCategory": "Decision",
                    "issueTypeBag": ["102", "103"],
                    "trialOutcomeCategory": "Institution Denied",
                },
            },
        ],
    }


@pytest.fixture
def appeal_decision_api_sample() -> Dict[str, Any]:
    """Sample appeal decision API response for testing."""
    return {
        "count": 1,
        "requestIdentifier": "7cf343b3-cad4-4813-9d46-993cf3c50283",
        "patentAppealDataBag": [
            {
                "appealNumber": "2015000194",
                "lastModifiedDateTime": "2015-02-18T14:23:45Z",
                "appealDocumentCategory": "Decision",
                "appealMetaData": {
                    "appealFilingDate": "2014-10-02",
                    "appealLastModifiedDate": "2015-02-18",
                    "appealLastModifiedDateTime": "2015-02-18T10:07:59",
                    "applicationTypeCategory": "Utility",
                    "docketNoticeMailedDate": "2014-11-15",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/APPEAL/2015/000194.zip",
                },
                "appellantData": {
                    "applicationNumberText": "12608694",
                    "counselName": "PAULEY ERICKSON & SWANSON",
                    "groupArtUnitNumber": "3992",
                    "inventorName": "John Smith",
                    "realPartyInInterestName": "Tech Company Inc.",
                    "patentOwnerName": "Tech Company Inc.",
                    "publicationDate": "2010-06-10",
                    "publicationNumber": "US20100145456",
                    "technologyCenterNumber": "3900",
                },
                "requestorData": {"thirdPartyName": "Third Party Requestor LLC"},
                "documentData": {
                    "documentFilingDate": "2015-02-18",
                    "documentIdentifier": "appeal-doc-12345",
                    "documentName": "Decision on Appeal.pdf",
                    "documentSizeQuantity": 345678,
                    "documentOCRText": "Decision on Appeal text content...",
                    "documentTypeDescriptionText": "Decision",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/APPEAL/2015/000194/decision.pdf",
                },
                "decisionData": {
                    "appealOutcomeCategory": "Affirmed",
                    "statuteAndRuleBag": ["35 U.S.C. § 103", "37 CFR 1.111"],
                    "decisionIssueDate": "2015-02-18",
                    "decisionTypeCategory": "Examiner Affirmed",
                    "issueTypeBag": ["Obviousness"],
                },
            }
        ],
    }


@pytest.fixture
def interference_decision_api_sample() -> Dict[str, Any]:
    """Sample interference decision API response for testing."""
    return {
        "count": 2,
        "requestIdentifier": "66576984-9c20-4e41-b4da-e28d13fe18f1",
        "patentInterferenceDataBag": [
            {
                "interferenceNumber": "104807",
                "lastModifiedDateTime": "2025-11-20T03:12:32",
                "interferenceMetaData": {
                    "interferenceLastModifiedDateTime": "2006-12-22T00:00:00",
                    "interferenceLastModifiedDate": "2006-12-22",
                    "declarationDate": "2002-12-11",
                    "interferenceStyleName": "VINOGRADOV V. FLAMM",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/INTF/104807/104807.zip",
                },
                "seniorPartyData": {
                    "applicationNumberText": "08739037",
                    "grantDate": "1999-10-12",
                    "groupArtUnitNumber": "1763",
                    "inventorName": "GEORGY  VINOGRADOV et al",
                    "patentNumber": "5965034",
                    "patentOwnerName": "GEORGY  VINOGRADOV et al",
                    "realPartyInInterestName": "GEORGY  VINOGRADOV et al",
                    "technologyCenterNumber": "1700",
                },
                "juniorPartyData": {
                    "applicationNumberText": "08748746",
                    "grantDate": "2005-02-22",
                    "groupArtUnitNumber": "1763",
                    "inventorName": "DANIEL L.  FLAMM et al",
                    "patentNumber": "6858112",
                    "patentOwnerName": "DANIEL L.  FLAMM et al",
                    "publicationDate": "2003-09-11",
                    "publicationNumber": "20030168427A1",
                    "realPartyInInterestName": "DANIEL L.  FLAMM et al",
                    "technologyCenterNumber": "1700",
                },
                "documentData": {
                    "documentIdentifier": "b8c473a3bcab88d5c33ef3231daf45a10f967103a89b8db9c791d1ee",
                    "documentName": "fd10480712-11-2002",
                    "documentSizeQuantity": 160468,
                    "documentOCRText": "The opinion in support of the decision being \nentered today is not binding precedent of the Board.  \n\nPaper 20 \nFiled by: Trial Section Motions Panel \n\nBox Interference Filed: December 11, 2002 \nWashington, D.C. 20231 \nTel: 703-308-9797 \nFax: 703-305-0942 \n\nUNITED STATES PATENT AND TRADEMARK OFFICE \n\nBEFORE THE BOARD OF PATENT APPEALS \nAND INTERFERENCES \n\nMAILED \nDANIEL L. FLAMM \n\nJunior Party DEC 2002 \n(U.S. Application 08/748,746), \n\nPAT & TM OFFICE BOARD OF PATENT \nAND INTERFER,'N\"FALS \n\nGEORGY",
                    "documentTitleText": "DECISION-104807",
                    "interferenceOutcomeCategory": "Final Decision",
                    "decisionIssueDate": "2002-12-11",
                    "decisionTypeCategory": "Decision",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/INTF/104807/Intf608_10480708739037_1039582800000.pdf",
                    "documentFilingDate": "2002-12-11",
                },
            },
            {
                "interferenceNumber": "106130",
                "lastModifiedDateTime": "2025-11-20T03:12:32",
                "additionalPartyDataBag": [
                    {
                        "applicationNumberText": "16159021",
                        "inventorName": "Lee M Kaplan et al",
                        "patentNumber": "",
                        "additionalPartyName": "LEE M. KAPLAN, ALICE P. LIOU, PETER J. TURNBAUGH, and JASON L. HARRIS",
                    },
                    {
                        "applicationNumberText": "15698965",
                        "inventorName": "Lee M Kaplan et al",
                        "patentNumber": "10149870",
                        "additionalPartyName": "LEE M. KAPLAN, ALICE P. LIOU, PETER J. TURNBAUGH, and JASON L. HARRIS",
                    },
                    {
                        "applicationNumberText": "16669143",
                        "inventorName": "Lee M Kaplan et al",
                        "patentNumber": "10729732",
                        "additionalPartyName": "LEE M. KAPLAN, ALICE P. LIOU, PETER J. TURNBAUGH, and JASON L. HARRIS",
                    },
                ],
                "interferenceMetaData": {
                    "interferenceLastModifiedDateTime": "2025-11-13T00:00:00",
                    "interferenceLastModifiedDate": "2025-11-13",
                    "declarationDate": "2021-01-26",
                    "interferenceStyleName": "LEE M. KAPLAN, ALICE P. LIOU, PETER J. TURNBAUGH, and JASON L. HARRIS v. PATRICE CANI, AMANDINE EVERARD, CLARA BELZER, and WILLEM DE VOS",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/INTF/106130/106130.zip",
                },
                "seniorPartyData": {
                    "applicationNumberText": "14443829",
                    "counselName": "ALSTON & BIRD and GEMINI LAW LLP ",
                    "groupArtUnitNumber": "1651",
                    "inventorName": "Patrice Cani et al",
                    "patentOwnerName": "CANI, PATRICE; EVERARD, Amandine; BELZER, Clara; DE VOS Willem",
                    "publicationDate": "2015-10-29",
                    "publicationNumber": "US20150306152A1",
                    "realPartyInInterestName": "UNIVERSITÉ CATHOLIQUE DE LOUVAIN; WAGENINGEN UNIVERSITEIT",
                    "technologyCenterNumber": "1600",
                },
                "juniorPartyData": {
                    "applicationNumberText": "14862663",
                    "counselName": "ROTHWELL, FIGG, ERNST & MANBECK, P.C. and LATHROP GAGE LLP",
                    "grantDate": "2018-12-11",
                    "groupArtUnitNumber": "1651",
                    "inventorName": "Lee M. Kaplan et al",
                    "patentNumber": "10149867",
                    "publicationDate": "2016-04-28",
                    "publicationNumber": "US20160113971A1",
                    "realPartyInInterestName": "Ethicon Endo-Surgery, Inc.; The General Hospital Corporation D/B/A Massachusetts General Hospital; President and Fellows of Harvard College ",
                    "technologyCenterNumber": "1600",
                },
                "documentData": {
                    "documentIdentifier": "229ba0b8d5f70d2e45cc36b79476f56f3faf51bd26c7ccc977208e7b",
                    "documentName": "106130_106130-jd-20250128.pdf",
                    "documentSizeQuantity": 97923,
                    "documentOCRText": "Microsoft Word - 106,130 Judgment (to be mailed)\n\n\n       \nTrials@uspto.gov       Filed: January 28, 2025 \nTel: 571-272-7822 \n \n\nUNITED STATES PATENT AND TRADEMARK OFFICE \n_______________ \n\n \nBEFORE THE PATENT TRIAL AND APPEAL BOARD \n\n \n________________ \n\n  \nLEE M. KAPLAN,  \n\nALICE P. LIOU, PETER J. TURNBAUGH, and JASON L. HARRIS,  \n \n\nJunior Party  \n(Patents 10,149,867; 10,149,870; and 10,729,732; \n\nand Application 16/159,021),  \n \n\nv.  \n \n\nPATRICE CANI,  \nAMANDINE EVERARD, CLARA BELZER, and WILLEM",
                    "documentTitleText": "Judgment 37 C.F.R. § 41.127(a)",
                    "interferenceOutcomeCategory": "Judgment",
                    "statuteAndRuleBag": ["37 CFR 41.127(a)"],
                    "decisionIssueDate": "2025-01-28",
                    "decisionTypeCategory": "Decision",
                    "fileDownloadURI": "https://api.uspto.gov/api/v1/patent/ptab-files/INTF/106130/Intf508_10613014862663_1738040400000.pdf",
                    "documentFilingDate": "2025-01-28",
                    "issueTypeBag": ["112"],
                },
            },
        ],
    }


class TestSelfImport:
    """Tests for Self type import compatibility across Python versions."""

    def test_self_import_works(self) -> None:
        """Test that Self type can be imported from ptab module."""
        # This test verifies the try/except import pattern works
        # by importing the module (which happens at test module import time)
        # and using a from_dict method that relies on Self type hints
        import sys

        # Verify the import succeeded (module is already imported)
        import pyUSPTO.models.ptab as ptab_module

        assert hasattr(ptab_module, "PartyData")

    def test_import_fallback_logic(self) -> None:
        """
        Tests that the module falls back to typing_extensions.Self if typing.Self fails.
        Uses builtins.__import__ patching to avoid corrupting the global typing module.
        """
        import sys
        import importlib
        import builtins
        from unittest.mock import patch
        import typing_extensions

        module_name = "pyUSPTO.models.ptab"

        # 1. Ensure the module is unloaded so we can force a fresh import
        if module_name in sys.modules:
            del sys.modules[module_name]

        # 2. Define a side_effect that simulates ImportError ONLY when importing Self from typing
        # This intercepts 'from typing import Self'
        original_import = builtins.__import__

        def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "typing" and "Self" in fromlist:
                raise ImportError("Simulated missing Self in typing")
            return original_import(name, globals, locals, fromlist, level)

        # 3. Apply the patch and import
        with patch("builtins.__import__", side_effect=mock_import):
            ptab_module = importlib.import_module(module_name)

        # 4. Verify the fallback works (it should be the typing_extensions version)
        assert ptab_module.Self is typing_extensions.Self

        # 5. Cleanup: Restore the module to its normal state for other tests
        if module_name in sys.modules:
            del sys.modules[module_name]
        importlib.import_module(module_name)

    def test_self_type_in_from_dict_methods(self) -> None:
        """Test that from_dict methods work correctly with Self return type."""
        # Create an instance using from_dict which uses Self as return type
        data = {"counselName": "Test Counsel", "patentNumber": "US1234567"}
        result = PartyData.from_dict(data)

        # Verify the return type is correct (should be PartyData instance)
        assert isinstance(result, PartyData)
        assert result.counsel_name == "Test Counsel"
        assert result.patent_number == "US1234567"

    def test_self_type_returns_correct_class_instance(self) -> None:
        """Test that from_dict returns an instance of the calling class."""
        # Test with different model classes to ensure Self works correctly
        trial_data = {"trialNumber": "IPR2023-00001"}
        trial_result = PTABTrialProceeding.from_dict(trial_data)
        assert isinstance(trial_result, PTABTrialProceeding)
        assert type(trial_result) == PTABTrialProceeding

        appeal_data = {"appealNumber": "2023-001234"}
        appeal_result = PTABAppealDecision.from_dict(appeal_data)
        assert isinstance(appeal_result, PTABAppealDecision)
        assert type(appeal_result) == PTABAppealDecision

        interference_data = {"interferenceNumber": "106123"}
        interference_result = PTABInterferenceDecision.from_dict(interference_data)
        assert isinstance(interference_result, PTABInterferenceDecision)
        assert type(interference_result) == PTABInterferenceDecision


class TestPartyData:
    """Tests for PartyData base class."""

    def test_party_data_from_dict_full(self) -> None:
        """Test PartyData.from_dict() with all fields."""
        data = {
            "applicationNumberText": "15/123456",
            "counselName": "Test Counsel",
            "grantDate": "2023-01-15",
            "groupArtUnitNumber": "3600",
            "inventorName": "John Inventor",
            "realPartyInInterestName": "Real Party Inc",
            "patentNumber": "US1234567",
            "patentOwnerName": "Patent Owner LLC",
            "technologyCenterNumber": "3600",
            "publicationDate": "2022-12-01",
            "publicationNumber": "US20220012345",
        }
        result = PartyData.from_dict(data)
        assert result.application_number_text == "15/123456"
        assert result.counsel_name == "Test Counsel"
        assert result.grant_date == date(2023, 1, 15)
        assert result.group_art_unit_number == "3600"
        assert result.inventor_name == "John Inventor"
        assert result.real_party_in_interest_name == "Real Party Inc"
        assert result.patent_number == "US1234567"
        assert result.patent_owner_name == "Patent Owner LLC"
        assert result.technology_center_number == "3600"
        assert result.publication_date == date(2022, 12, 1)
        assert result.publication_number == "US20220012345"

    def test_party_data_from_dict_empty(self) -> None:
        """Test PartyData.from_dict() with empty dict."""
        result = PartyData.from_dict({})
        assert result.application_number_text is None
        assert result.counsel_name is None
        assert result.grant_date is None
        assert result.group_art_unit_number is None
        assert result.inventor_name is None
        assert result.real_party_in_interest_name is None
        assert result.patent_number is None
        assert result.patent_owner_name is None
        assert result.technology_center_number is None
        assert result.publication_date is None
        assert result.publication_number is None

    def test_party_data_from_dict_ignores_include_raw_data(self) -> None:
        """Test PartyData.from_dict() ignores include_raw_data parameter."""
        data = {"counselName": "Test"}
        result = PartyData.from_dict(data, include_raw_data=True)
        assert result.counsel_name == "Test"


class TestPTABTrialModels:
    """Tests for PTAB trial proceeding models."""

    def test_trial_metadata_from_dict_full(self) -> None:
        """Test TrialMetaData.from_dict() with all fields."""
        data = {
            "petitionFilingDate": "2023-01-15",
            "accordedFilingDate": "2023-01-16",
            "trialLastModifiedDateTime": "2023-06-01T10:30:00Z",
            "trialLastModifiedDate": "2023-06-01",
            "trialStatusCategory": "Instituted",
            "trialTypeCode": "IPR",
            "fileDownloadURI": "https://example.com/download.zip",
            "terminationDate": "2024-01-15",
            "latestDecisionDate": "2023-12-15",
            "institutionDecisionDate": "2023-07-15",
        }
        result = TrialMetaData.from_dict(data)
        assert result.petition_filing_date == date(2023, 1, 15)
        assert result.accorded_filing_date == date(2023, 1, 16)
        assert result.trial_last_modified_date_time == datetime(
            2023, 6, 1, 10, 30, 0, tzinfo=timezone.utc
        )
        assert result.trial_last_modified_date == date(2023, 6, 1)
        assert result.trial_status_category == "Instituted"
        assert result.trial_type_code == "IPR"
        assert result.file_download_uri == "https://example.com/download.zip"
        assert result.termination_date == date(2024, 1, 15)
        assert result.latest_decision_date == date(2023, 12, 15)
        assert result.institution_decision_date == date(2023, 7, 15)

    def test_trial_metadata_from_dict_empty(self) -> None:
        """Test TrialMetaData.from_dict() with empty dict."""
        result = TrialMetaData.from_dict({})
        assert result.petition_filing_date is None
        assert result.accorded_filing_date is None
        assert result.trial_last_modified_date_time is None
        assert result.trial_last_modified_date is None
        assert result.trial_status_category is None
        assert result.trial_type_code is None
        assert result.file_download_uri is None
        assert result.termination_date is None
        assert result.latest_decision_date is None
        assert result.institution_decision_date is None

    def test_patent_owner_data_from_dict(self) -> None:
        """Test PatentOwnerData.from_dict()."""
        data = {
            "patentOwnerName": "Owner Inc",
            "patentNumber": "US1234567",
            "counselName": "Owner Counsel",
        }
        result = PatentOwnerData.from_dict(data)
        assert result.patent_owner_name == "Owner Inc"
        assert result.patent_number == "US1234567"
        assert result.counsel_name == "Owner Counsel"

    def test_regular_petitioner_data_from_dict(self) -> None:
        """Test RegularPetitionerData.from_dict()."""
        data = {
            "counselName": "Test Counsel",
            "realPartyInInterestName": "Real Party",
        }
        result = RegularPetitionerData.from_dict(data)
        assert result.counsel_name == "Test Counsel"
        assert result.real_party_in_interest_name == "Real Party"

    def test_regular_petitioner_data_from_dict_empty(self) -> None:
        """Test RegularPetitionerData.from_dict() with empty dict."""
        result = RegularPetitionerData.from_dict({})
        assert result.counsel_name is None
        assert result.real_party_in_interest_name is None

    def test_respondent_data_from_dict(self) -> None:
        """Test RespondentData.from_dict()."""
        data = {
            "counselName": "Respondent Counsel",
            "realPartyInInterestName": "Respondent Party",
            "patentNumber": "US7654321",
        }
        result = RespondentData.from_dict(data)
        assert result.counsel_name == "Respondent Counsel"
        assert result.real_party_in_interest_name == "Respondent Party"
        assert result.patent_number == "US7654321"

    def test_derivation_petitioner_data_from_dict(self) -> None:
        """Test DerivationPetitionerData.from_dict()."""
        data = {
            "counselName": "Derivation Counsel",
            "grantDate": "2023-01-15",
            "groupArtUnitNumber": "3600",
            "inventorName": "John Inventor",
            "patentNumber": "US1234567",
            "technologyCenterNumber": "3600",
            "realPartyInInterestName": "Derivation Party",
            "patentOwnerName": "Derivation Owner",
        }
        result = DerivationPetitionerData.from_dict(data)
        assert result.counsel_name == "Derivation Counsel"
        assert result.grant_date == date(2023, 1, 15)
        assert result.patent_number == "US1234567"
        assert result.patent_owner_name == "Derivation Owner"

    def test_trial_proceeding_from_dict_full(
        self, trial_proceeding_api_sample: Dict[str, Any]
    ) -> None:
        """Test PTABTrialProceeding.from_dict() with all nested objects using real API data."""
        data = trial_proceeding_api_sample["patentTrialProceedingDataBag"][0]
        result = PTABTrialProceeding.from_dict(data)

        assert result.trial_number == "DER2018-00018"
        assert result.trial_meta_data is not None
        assert result.trial_meta_data.trial_status_category == "Terminated-Settled"
        assert result.trial_meta_data.trial_type_code == "DER"
        assert result.patent_owner_data is not None
        assert result.patent_owner_data.patent_owner_name == "ADAMS et al"
        assert result.patent_owner_data.patent_number == "9780412"
        assert result.regular_petitioner_data is not None
        assert result.regular_petitioner_data.counsel_name == "Todd Baker"
        assert result.respondent_data is not None
        assert result.respondent_data.patent_owner_name == "ADAMS et al"
        assert result.derivation_petitioner_data is not None
        assert result.derivation_petitioner_data.counsel_name == "Todd Baker"
        assert result.raw_data is None

    def test_trial_proceeding_from_dict_with_raw_data(self) -> None:
        """Test PTABTrialProceeding.from_dict() with include_raw_data=True."""
        data = {
            "trialNumber": "IPR2023-00001",
            # "trialRecordIdentifier": "uuid-1",
        }
        result = PTABTrialProceeding.from_dict(data, include_raw_data=True)
        assert result.trial_number == "IPR2023-00001"
        assert result.raw_data == data

    def test_trial_proceeding_from_dict_empty(self) -> None:
        """Test PTABTrialProceeding.from_dict() with empty dict."""
        result = PTABTrialProceeding.from_dict({})
        assert result.trial_number is None
        # assert result.trial_record_identifier is None
        assert result.last_modified_date_time is None
        assert result.trial_meta_data is None
        assert result.patent_owner_data is None
        assert result.regular_petitioner_data is None
        assert result.respondent_data is None
        assert result.derivation_petitioner_data is None
        assert result.raw_data is None

    def test_trial_proceeding_response_from_dict_full(
        self, trial_proceeding_api_sample: Dict[str, Any]
    ) -> None:
        """Test PTABTrialProceedingResponse.from_dict() using real API data."""
        result = PTABTrialProceedingResponse.from_dict(trial_proceeding_api_sample)
        assert result.count == 1
        assert result.request_identifier == "4649ea27-4192-4ea4-86f9-e033ca24c17a"
        assert len(result.patent_trial_proceeding_data_bag) == 1
        assert (
            result.patent_trial_proceeding_data_bag[0].trial_number == "DER2018-00018"
        )
        assert result.raw_data is None

    def test_trial_proceeding_response_from_dict_with_raw_data(self) -> None:
        """Test PTABTrialProceedingResponse.from_dict() with include_raw_data=True."""
        data = {
            "count": 1,
            "requestIdentifier": "request-uuid-1",
            "patentTrialProceedingDataBag": [
                {"trialNumber": "IPR2023-00001"},
            ],
        }
        result = PTABTrialProceedingResponse.from_dict(data, include_raw_data=True)
        assert result.count == 1
        assert result.raw_data == data
        assert len(result.patent_trial_proceeding_data_bag) == 1
        assert result.patent_trial_proceeding_data_bag[0].raw_data == {
            "trialNumber": "IPR2023-00001"
        }

    def test_trial_proceeding_response_from_dict_empty(self) -> None:
        """Test PTABTrialProceedingResponse.from_dict() with empty list."""
        data = {
            "count": 0,
            "patentTrialProceedingDataBag": [],
        }
        result = PTABTrialProceedingResponse.from_dict(data)
        assert result.count == 0
        assert len(result.patent_trial_proceeding_data_bag) == 0


class TestPTABTrialDocumentModels:
    """Tests for PTAB trial document models."""

    def test_trial_document_data_from_dict_full(self) -> None:
        """Test TrialDocumentData.from_dict() with all fields."""
        data = {
            # "documentCategory": "Petition",
            "documentFilingDate": "2023-01-15",
            "documentIdentifier": "doc-uuid-1",
            "documentName": "Petition.pdf",
            "documentNumber": "1001",
            "documentSizeQuantity": 123456,
            "documentOCRText": "Full OCR text content here...",
            "documentTitleText": "Petition for IPR",
            "documentTypeDescriptionText": "Petition Document",
            "downloadURI": "https://example.com/doc1.pdf",
            "filingPartyCategory": "Petitioner",
            # "mimeTypeIdentifier": "application/pdf",
            # "documentStatus": "Public",
        }
        result = TrialDocumentData.from_dict(data)
        # assert result.document_category == "Petition"
        assert result.document_filing_date == date(2023, 1, 15)
        assert result.document_identifier == "doc-uuid-1"
        assert result.document_name == "Petition.pdf"
        assert result.document_number == "1001"
        assert result.document_size_quantity == 123456
        assert result.document_ocr_text == "Full OCR text content here..."
        assert result.document_title_text == "Petition for IPR"
        assert result.document_type_description_text == "Petition Document"
        assert result.file_download_uri == "https://example.com/doc1.pdf"
        assert result.filing_party_category == "Petitioner"
        # assert result.mime_type_identifier == "application/pdf"
        # assert result.document_status == "Public"

    def test_trial_document_data_from_dict_empty(self) -> None:
        """Test TrialDocumentData.from_dict() with empty dict."""
        result = TrialDocumentData.from_dict({})
        # assert result.document_category is None
        assert result.document_filing_date is None
        assert result.document_identifier is None
        assert result.document_name is None
        assert result.document_number is None
        assert result.document_size_quantity is None
        assert result.document_ocr_text is None
        assert result.document_title_text is None
        assert result.document_type_description_text is None
        assert result.file_download_uri is None
        assert result.filing_party_category is None
        # assert result.mime_type_identifier is None
        # assert result.document_status is None

    def test_trial_decision_data_from_dict_full(self) -> None:
        """Test TrialDecisionData.from_dict() with all fields."""
        data = {
            "statuteAndRuleBag": ["35 U.S.C. § 103", "37 CFR 42.100"],
            "decisionIssueDate": "2023-12-15",
            "decisionTypeCategory": "Final Written Decision",
            "issueTypeBag": ["Obviousness", "Claim Construction"],
            "trialOutcomeCategory": "Denied",
        }
        result = TrialDecisionData.from_dict(data)
        assert result.statute_and_rule_bag == ["35 U.S.C. § 103", "37 CFR 42.100"]
        assert result.decision_issue_date == date(2023, 12, 15)
        assert result.decision_type_category == "Final Written Decision"
        assert result.issue_type_bag == ["Obviousness", "Claim Construction"]
        assert result.trial_outcome_category == "Denied"

    def test_trial_decision_data_from_dict_empty(self) -> None:
        """Test TrialDecisionData.from_dict() with empty dict."""
        result = TrialDecisionData.from_dict({})
        assert result.statute_and_rule_bag == []
        assert result.decision_issue_date is None
        assert result.decision_type_category is None
        assert result.issue_type_bag == []
        assert result.trial_outcome_category is None

    def test_trial_document_from_dict_full(
        self, trial_document_api_sample: Dict[str, Any]
    ) -> None:
        """Test PTABTrialDocument.from_dict() with all nested objects using real API data."""
        data = trial_document_api_sample["patentTrialDocumentDataBag"][0]
        result = PTABTrialDocument.from_dict(data)

        assert result.trial_document_category == "Document"
        assert result.trial_number == "DER2023-00012"
        assert result.trial_meta_data is not None
        assert result.trial_meta_data.trial_status_category == "Pending"
        assert result.patent_owner_data is not None
        assert result.patent_owner_data.patent_number == None
        assert result.regular_petitioner_data is not None
        assert (
            result.regular_petitioner_data.real_party_in_interest_name
            == "Rasmussen, Jon et al."
        )
        assert result.document_data is not None
        assert result.document_data.document_number == 25
        assert result.decision_data is not None
        assert result.raw_data is None

    def test_trial_document_from_dict_with_raw_data(self) -> None:
        """Test PTABTrialDocument.from_dict() with include_raw_data=True."""
        data = {
            "trialNumber": "IPR2023-00001",
            "trialDocumentCategory": "Document",
        }
        result = PTABTrialDocument.from_dict(data, include_raw_data=True)
        assert result.trial_number == "IPR2023-00001"
        assert result.raw_data == data

    def test_trial_document_from_dict_empty(self) -> None:
        """Test PTABTrialDocument.from_dict() with empty dict."""
        result = PTABTrialDocument.from_dict({})
        assert result.trial_document_category is None
        assert result.last_modified_date_time is None
        assert result.trial_number is None
        assert result.trial_type_code is None
        assert result.trial_meta_data is None
        assert result.patent_owner_data is None
        assert result.regular_petitioner_data is None
        assert result.respondent_data is None
        assert result.derivation_petitioner_data is None
        assert result.document_data is None
        assert result.decision_data is None
        assert result.raw_data is None

    def test_trial_document_response_from_dict_full(self) -> None:
        """Test PTABTrialDocumentResponse.from_dict() with multiple documents."""
        data = {
            "count": 2,
            "patentTrialDocumentDataBag": [
                {
                    "trialNumber": "IPR2023-00001",
                    "trialDocumentCategory": "Document",
                },
                {
                    "trialNumber": "IPR2023-00002",
                    "trialDocumentCategory": "Decision",
                },
            ],
        }
        result = PTABTrialDocumentResponse.from_dict(data)
        assert result.count == 2
        assert len(result.patent_trial_document_data_bag) == 2
        assert result.patent_trial_document_data_bag[0].trial_number == "IPR2023-00001"
        assert (
            result.patent_trial_document_data_bag[0].trial_document_category
            == "Document"
        )
        assert result.patent_trial_document_data_bag[1].trial_number == "IPR2023-00002"
        assert (
            result.patent_trial_document_data_bag[1].trial_document_category
            == "Decision"
        )
        assert result.raw_data is None

    def test_trial_document_response_from_dict_with_raw_data(self) -> None:
        """Test PTABTrialDocumentResponse.from_dict() with include_raw_data=True."""
        data = {
            "count": 1,
            "patentTrialDocumentDataBag": [
                {"trialNumber": "IPR2023-00001"},
            ],
        }
        result = PTABTrialDocumentResponse.from_dict(data, include_raw_data=True)
        assert result.count == 1
        assert result.raw_data == data
        assert len(result.patent_trial_document_data_bag) == 1
        assert result.patent_trial_document_data_bag[0].raw_data == {
            "trialNumber": "IPR2023-00001"
        }

    def test_trial_document_response_from_dict_empty(self) -> None:
        """Test PTABTrialDocumentResponse.from_dict() with empty list."""
        result = PTABTrialDocumentResponse.from_dict({})
        assert result.count == 0
        assert len(result.patent_trial_document_data_bag) == 0
        assert result.raw_data is None


class TestPTABAppealModels:
    """Tests for PTAB appeal decision models."""

    def test_appeal_metadata_from_dict_full(self) -> None:
        """Test AppealMetaData.from_dict() with all fields."""
        data = {
            "appealFilingDate": "2023-01-15",
            "appealLastModifiedDate": "2023-06-01",
            "appealLastModifiedDateTime": "2023-06-01T12:00:01",
            "applicationTypeCategory": "Utility",
            "docketNoticeMailedDate": "2023-02-01",
            "fileDownloadURI": "https://example.com/appeal.zip",
        }
        result = AppealMetaData.from_dict(data)
        assert result.appeal_filing_date == date(2023, 1, 15)
        assert result.appeal_last_modified_date == date(2023, 6, 1)
        assert result.appeal_last_modified_date_time == datetime(
            2023, 6, 1, 16, 0, 1, tzinfo=timezone.utc
        )
        assert result.application_type_category == "Utility"
        assert result.docket_notice_mailed_date == date(2023, 2, 1)
        assert result.file_download_uri == "https://example.com/appeal.zip"

    def test_appeal_metadata_from_dict_empty(self) -> None:
        """Test AppealMetaData.from_dict() with empty dict."""
        result = AppealMetaData.from_dict({})
        assert result.appeal_filing_date is None
        assert result.appeal_last_modified_date is None
        assert result.application_type_category is None
        assert result.docket_notice_mailed_date is None
        assert result.file_download_uri is None

    def test_appellant_data_from_dict(self) -> None:
        """Test AppellantData.from_dict()."""
        data = {
            "applicationNumberText": "15/123456",
            "counselName": "Appellant Counsel",
            "groupArtUnitNumber": "3600",
            "inventorName": "Jane Inventor",
            "realPartyInInterestName": "Appellant Party",
            "patentOwnerName": "Appellant Owner",
            "publicationDate": "2023-01-15",
            "publicationNumber": "US20230012345",
            "technologyCenterNumber": "3600",
        }
        result = AppellantData.from_dict(data)
        assert result.application_number_text == "15/123456"
        assert result.counsel_name == "Appellant Counsel"
        assert result.inventor_name == "Jane Inventor"
        assert result.technology_center_number == "3600"
        assert result.publication_date == date(2023, 1, 15)

    def test_requestor_data_from_dict(self) -> None:
        """Test RequestorData.from_dict()."""
        data = {"thirdPartyName": "Third Party Inc"}
        result = RequestorData.from_dict(data)
        assert result.third_party_name == "Third Party Inc"

    def test_requestor_data_from_dict_empty(self) -> None:
        """Test RequestorData.from_dict() with empty dict."""
        result = RequestorData.from_dict({})
        assert result.third_party_name is None

    def test_appeal_document_data_from_dict_full(self) -> None:
        """Test AppealDocumentData.from_dict() with all fields."""
        data = {
            "documentFilingDate": "2023-01-15",
            "documentIdentifier": "doc-uuid-1",
            "documentName": "Appeal Brief",
            "documentSizeQuantity": 12345,
            "documentOCRText": "Full OCR text content",
            "documentTypeDescriptionText": "Brief",
            "fileDownloadURI": "https://example.com/download",
        }
        result = AppealDocumentData.from_dict(data)
        assert result.document_filing_date == date(2023, 1, 15)
        assert result.document_identifier == "doc-uuid-1"
        assert result.document_name == "Appeal Brief"
        assert result.document_size_quantity == 12345
        assert result.document_ocr_text == "Full OCR text content"
        assert result.document_type_description_text == "Brief"
        assert result.file_download_uri == "https://example.com/download"

    def test_appeal_document_data_from_dict_with_alias_downloaduri(self) -> None:
        """Test AppealDocumentData.from_dict() handles downloadURI alias."""
        data = {
            "documentName": "Brief.pdf",
            "downloadURI": "https://example.com/brief.pdf",
        }
        result = AppealDocumentData.from_dict(data)
        assert result.file_download_uri == "https://example.com/brief.pdf"

    def test_appeal_document_data_from_dict_with_alias_document_type(self) -> None:
        """Test AppealDocumentData.from_dict() handles documentTypeCategory alias."""
        data = {
            "documentName": "Decision.pdf",
            "documentTypeCategory": "Decision",
        }
        result = AppealDocumentData.from_dict(data)
        assert result.document_type_description_text == "Decision"

    def test_appeal_document_data_from_dict_empty(self) -> None:
        """Test AppealDocumentData.from_dict() with empty dict."""
        result = AppealDocumentData.from_dict({})
        assert result.document_filing_date is None
        assert result.document_identifier is None
        assert result.document_name is None
        assert result.document_size_quantity is None
        assert result.document_ocr_text is None
        assert result.document_type_description_text is None
        assert result.file_download_uri is None

    def test_decision_data_from_dict_full(self) -> None:
        """Test DecisionData.from_dict() with all fields."""
        data = {
            "appealOutcomeCategory": "Affirmed",
            "statuteAndRuleBag": ["35 U.S.C. § 103", "37 CFR 1.111"],
            "decisionIssueDate": "2023-12-15",
            "decisionTypeCategory": "Examiner Affirmed",
            "issueTypeBag": ["Obviousness", "Anticipation"],
        }
        result = DecisionData.from_dict(data)
        assert result.appeal_outcome_category == "Affirmed"
        assert result.statute_and_rule_bag == ["35 U.S.C. § 103", "37 CFR 1.111"]
        assert result.decision_issue_date == date(2023, 12, 15)
        assert result.decision_type_category == "Examiner Affirmed"
        assert result.issue_type_bag == ["Obviousness", "Anticipation"]

    def test_decision_data_from_dict_empty(self) -> None:
        """Test DecisionData.from_dict() with empty dict."""
        result = DecisionData.from_dict({})
        assert result.appeal_outcome_category is None
        assert result.statute_and_rule_bag == []
        assert result.decision_issue_date is None
        assert result.decision_type_category is None
        assert result.issue_type_bag == []

    def test_decision_data_to_dict_with_empty_lists(self) -> None:
        """Test DecisionData.to_dict() filters out empty lists."""
        # Create DecisionData with empty lists
        result = DecisionData.from_dict({
            "appealOutcomeCategory": "Affirmed",
            "decisionIssueDate": "2023-12-15",
            "statuteAndRuleBag": [],
            "issueTypeBag": []
        })

        # Convert to dict - empty lists should be filtered out
        result_dict = result.to_dict()

        # Verify non-empty fields are present
        assert result_dict["appealOutcomeCategory"] == "Affirmed"
        assert result_dict["decisionIssueDate"] == "2023-12-15"

        # Verify empty lists are NOT in the result
        assert "statuteAndRuleBag" not in result_dict
        assert "issueTypeBag" not in result_dict

    def test_appeal_decision_from_dict_full(self) -> None:
        """Test PTABAppealDecision.from_dict() with all nested objects."""
        data = {
            "appealNumber": "2023-001234",
            "lastModifiedDateTime": "2023-06-15T10:30:00Z",
            "appealDocumentCategory": "Decision",
            "appealMetaData": {
                "appealFilingDate": "2023-01-15",
                "applicationTypeCategory": "Utility",
            },
            "appellantData": {
                "applicationNumberText": "15/123456",
                "counselName": "Test Counsel",
                "technologyCenterNumber": "3600",
            },
            "requestorData": {"thirdPartyName": "Third Party Inc"},
            "documentData": {
                "documentName": "Final Decision",
                "documentIdentifier": "doc-123",
            },
            "decisionData": {
                "decisionTypeCategory": "Affirmed",
                "decisionIssueDate": "2023-06-01",
            },
        }
        result = PTABAppealDecision.from_dict(data)
        assert result.appeal_number == "2023-001234"
        assert result.last_modified_date_time == datetime(
            2023, 6, 15, 10, 30, 0, tzinfo=timezone.utc
        )
        assert result.appeal_document_category == "Decision"
        assert result.appeal_meta_data is not None
        assert result.appeal_meta_data.application_type_category == "Utility"
        assert result.appellant_data is not None
        assert result.appellant_data.counsel_name == "Test Counsel"
        assert result.requestor_data is not None
        assert result.requestor_data.third_party_name == "Third Party Inc"
        assert result.document_data is not None
        assert result.document_data.document_name == "Final Decision"
        assert result.decision_data is not None
        assert result.decision_data.decision_type_category == "Affirmed"
        assert result.raw_data is None

    def test_appeal_decision_from_dict_with_typo_appelant(self) -> None:
        """Test PTABAppealDecision.from_dict() handles 'appelantData' typo."""
        data = {
            "appealNumber": "2023-001234",
            "appelantData": {
                "counselName": "Test Counsel",
            },
        }
        result = PTABAppealDecision.from_dict(data)
        assert result.appellant_data is not None
        assert result.appellant_data.counsel_name == "Test Counsel"

    def test_appeal_decision_from_dict_with_raw_data(self) -> None:
        """Test PTABAppealDecision.from_dict() with include_raw_data=True."""
        data = {
            "appealNumber": "2023-001234",
            "appealDocumentCategory": "Decision",
        }
        result = PTABAppealDecision.from_dict(data, include_raw_data=True)
        assert result.appeal_number == "2023-001234"
        assert result.raw_data == data

    def test_appeal_decision_from_dict_empty(self) -> None:
        """Test PTABAppealDecision.from_dict() with empty dict."""
        result = PTABAppealDecision.from_dict({})
        assert result.appeal_number is None
        assert result.last_modified_date_time is None
        assert result.appeal_document_category is None
        assert result.appeal_meta_data is None
        assert result.appellant_data is None
        assert result.requestor_data is None
        assert result.document_data is None
        assert result.decision_data is None
        assert result.raw_data is None

    def test_appeal_response_from_dict_full(self) -> None:
        """Test PTABAppealResponse.from_dict() with multiple appeals."""
        data = {
            "count": 2,
            "requestIdentifier": "request-uuid-1",
            "patentAppealDataBag": [
                {
                    "appealNumber": "2023-001234",
                    "appealDocumentCategory": "Decision",
                },
                {
                    "appealNumber": "2023-005678",
                    "appealDocumentCategory": "Brief",
                },
            ],
        }
        result = PTABAppealResponse.from_dict(data)
        assert result.count == 2
        assert result.request_identifier == "request-uuid-1"
        assert len(result.patent_appeal_data_bag) == 2
        assert result.patent_appeal_data_bag[0].appeal_number == "2023-001234"
        assert result.patent_appeal_data_bag[0].appeal_document_category == "Decision"
        assert result.patent_appeal_data_bag[1].appeal_number == "2023-005678"
        assert result.patent_appeal_data_bag[1].appeal_document_category == "Brief"
        assert result.raw_data is None

    def test_appeal_response_from_dict_with_raw_data(self) -> None:
        """Test PTABAppealResponse.from_dict() with include_raw_data=True."""
        data = {
            "count": 1,
            "requestIdentifier": "request-uuid-1",
            "patentAppealDataBag": [
                {"appealNumber": "2023-001234"},
            ],
        }
        result = PTABAppealResponse.from_dict(data, include_raw_data=True)
        assert result.count == 1
        assert result.raw_data == data
        assert len(result.patent_appeal_data_bag) == 1
        assert result.patent_appeal_data_bag[0].raw_data == {
            "appealNumber": "2023-001234"
        }

    def test_appeal_response_from_dict_empty(self) -> None:
        """Test PTABAppealResponse.from_dict() with empty list."""
        result = PTABAppealResponse.from_dict({})
        assert result.count == 0
        assert result.request_identifier is None
        assert len(result.patent_appeal_data_bag) == 0
        assert result.raw_data is None


class TestPTABInterferenceModels:
    """Tests for PTAB interference decision models."""

    def test_interference_metadata_from_dict_full(self) -> None:
        """Test InterferenceMetaData.from_dict() with all fields."""
        data = {
            "interferenceStyleName": "Senior v. Junior",
            "interferenceLastModifiedDate": "2023-03-15",
            "fileDownloadURI": "https://example.com/interference.zip",
        }
        result = InterferenceMetaData.from_dict(data)
        assert result.interference_style_name == "Senior v. Junior"
        assert result.interference_last_modified_date == date(2023, 3, 15)
        assert result.file_download_uri == "https://example.com/interference.zip"

    def test_interference_metadata_from_dict_empty(self) -> None:
        """Test InterferenceMetaData.from_dict() with empty dict."""
        result = InterferenceMetaData.from_dict({})
        assert result.interference_style_name is None
        assert result.interference_last_modified_date is None
        assert result.file_download_uri is None

    def test_senior_party_data_from_dict(self) -> None:
        """Test SeniorPartyData.from_dict()."""
        data = {
            "applicationNumberText": "12/345678",
            "counselName": "Senior Counsel",
            "grantDate": "2023-01-15",
            "groupArtUnitNumber": "1600",
            "realPartyInInterestName": "Senior Party Inc",
            "patentNumber": "US1234567",
            "patentOwnerName": "Senior Owner",
            "technologyCenterNumber": "1600",
        }
        result = SeniorPartyData.from_dict(data)
        assert result.application_number_text == "12/345678"
        assert result.counsel_name == "Senior Counsel"
        assert result.grant_date == date(2023, 1, 15)
        assert result.patent_owner_name == "Senior Owner"
        assert result.patent_number == "US1234567"

    def test_junior_party_data_from_dict(self) -> None:
        """Test JuniorPartyData.from_dict()."""
        data = {
            "publicationNumber": "US20230012345",
            "counselName": "Junior Counsel",
            "groupArtUnitNumber": "1600",
            "inventorName": "Jane Inventor",
            "patentOwnerName": "Junior Owner",
            "publicationDate": "2023-02-20",
            "realPartyInInterestName": "Junior Party LLC",
            "technologyCenterNumber": "1600",
        }
        result = JuniorPartyData.from_dict(data)
        assert result.publication_number == "US20230012345"
        assert result.counsel_name == "Junior Counsel"
        assert result.inventor_name == "Jane Inventor"
        assert result.patent_owner_name == "Junior Owner"
        assert result.publication_date == date(2023, 2, 20)

    def test_additional_party_data_from_dict(self) -> None:
        """Test AdditionalPartyData.from_dict()."""
        data = {
            "applicationNumberText": "14/111222",
            "inventorName": "John Inventor",
            "additionalPartyName": "Additional Entity",
            "patentNumber": "US1112223",
        }
        result = AdditionalPartyData.from_dict(data)
        assert result.application_number_text == "14/111222"
        assert result.inventor_name == "John Inventor"
        assert result.additional_party_name == "Additional Entity"
        assert result.patent_number == "US1112223"

    def test_additional_party_data_from_dict_empty(self) -> None:
        """Test AdditionalPartyData.from_dict() with empty dict."""
        result = AdditionalPartyData.from_dict({})
        assert result.application_number_text is None
        assert result.inventor_name is None
        assert result.additional_party_name is None
        assert result.patent_number is None

    def test_interference_document_data_from_dict_full(self) -> None:
        """Test InterferenceDocumentData.from_dict() with all fields."""
        data = {
            "documentIdentifier": "doc-uuid-1",
            "documentName": "Final Decision.pdf",
            "documentSizeQuantity": 234567,
            "documentOCRText": "Full OCR content...",
            "documentTitleText": "Final Decision on Priority",
            "interferenceOutcomeCategory": "Priority to Senior Party",
            "decisionIssueDate": "2023-03-15",
            "decisionTypeCategory": "Final Decision",
            "fileDownloadURI": "https://example.com/decision.pdf",
            "statuteAndRuleBag": ["35 U.S.C. § 102", "37 CFR 41.125"],
            "issueTypeBag": ["Priority", "Patentability"],
        }
        result = InterferenceDocumentData.from_dict(data)
        assert result.document_identifier == "doc-uuid-1"
        assert result.document_name == "Final Decision.pdf"
        assert result.document_size_quantity == 234567
        assert result.document_ocr_text == "Full OCR content..."
        assert result.document_title_text == "Final Decision on Priority"
        assert result.interference_outcome_category == "Priority to Senior Party"
        assert result.decision_issue_date == date(2023, 3, 15)
        assert result.decision_type_category == "Final Decision"
        assert result.file_download_uri == "https://example.com/decision.pdf"
        assert result.statute_and_rule_bag == ["35 U.S.C. § 102", "37 CFR 41.125"]
        assert result.issue_type_bag == ["Priority", "Patentability"]

    def test_interference_document_data_from_dict_with_alias_downloaduri(self) -> None:
        """Test InterferenceDocumentData.from_dict() handles downloadURI alias."""
        data = {
            "documentName": "Decision.pdf",
            "downloadURI": "https://example.com/decision.pdf",
        }
        result = InterferenceDocumentData.from_dict(data)
        assert result.file_download_uri == "https://example.com/decision.pdf"

    def test_interference_document_data_from_dict_empty(self) -> None:
        """Test InterferenceDocumentData.from_dict() with empty dict."""
        result = InterferenceDocumentData.from_dict({})
        assert result.document_identifier is None
        assert result.document_name is None
        assert result.document_size_quantity is None
        assert result.document_ocr_text is None
        assert result.document_title_text is None
        assert result.interference_outcome_category is None
        assert result.decision_issue_date is None
        assert result.decision_type_category is None
        assert result.file_download_uri is None
        assert result.statute_and_rule_bag == []
        assert result.issue_type_bag == []

    def test_interference_decision_from_dict_full(self) -> None:
        """Test PTABInterferenceDecision.from_dict() with all nested objects."""
        data = {
            "interferenceNumber": "106123",
            "lastModifiedDateTime": "2023-03-15T10:30:00Z",
            "interferenceMetaData": {
                "interferenceStyleName": "Senior v. Junior",
                "interferenceLastModifiedDate": "2023-03-15",
            },
            "seniorPartyData": {
                "patentOwnerName": "Senior Inc",
                "applicationNumberText": "12/345678",
                "patentNumber": "US1234567",
            },
            "juniorPartyData": {
                "patentOwnerName": "Junior LLC",
                "publicationNumber": "US20230012345",
            },
            "additionalPartyDataBag": [
                {
                    "additionalPartyName": "Additional Party 1",
                    "applicationNumberText": "14/111222",
                },
                {
                    "additionalPartyName": "Additional Party 2",
                    "applicationNumberText": "14/333444",
                },
            ],
            "documentData": {
                "interferenceOutcomeCategory": "Priority to Senior Party",
                "decisionTypeCategory": "Final Decision",
            },
        }
        result = PTABInterferenceDecision.from_dict(data)
        assert result.interference_number == "106123"
        assert result.last_modified_date_time == datetime(
            2023, 3, 15, 10, 30, 0, tzinfo=timezone.utc
        )
        assert result.interference_meta_data is not None
        assert (
            result.interference_meta_data.interference_style_name == "Senior v. Junior"
        )
        assert result.senior_party_data is not None
        assert result.senior_party_data.patent_owner_name == "Senior Inc"
        assert result.junior_party_data is not None
        assert result.junior_party_data.patent_owner_name == "Junior LLC"
        assert len(result.additional_party_data_bag) == 2
        assert (
            result.additional_party_data_bag[0].additional_party_name
            == "Additional Party 1"
        )
        assert (
            result.additional_party_data_bag[1].additional_party_name
            == "Additional Party 2"
        )
        assert result.document_data is not None
        assert (
            result.document_data.interference_outcome_category
            == "Priority to Senior Party"
        )
        assert result.raw_data is None

    def test_interference_decision_from_dict_with_alias_decision_document_data(
        self,
    ) -> None:
        """Test PTABInterferenceDecision.from_dict() handles decisionDocumentData alias."""
        data = {
            "interferenceNumber": "106123",
            "decisionDocumentData": {
                "decisionTypeCategory": "Final Decision",
            },
        }
        result = PTABInterferenceDecision.from_dict(data)
        assert result.document_data is not None
        assert result.document_data.decision_type_category == "Final Decision"

    def test_interference_decision_from_dict_with_raw_data(self) -> None:
        """Test PTABInterferenceDecision.from_dict() with include_raw_data=True."""
        data = {
            "interferenceNumber": "106123",
        }
        result = PTABInterferenceDecision.from_dict(data, include_raw_data=True)
        assert result.interference_number == "106123"
        assert result.raw_data == data

    def test_interference_decision_from_dict_empty(self) -> None:
        """Test PTABInterferenceDecision.from_dict() with empty dict."""
        result = PTABInterferenceDecision.from_dict({})
        assert result.interference_number is None
        assert result.last_modified_date_time is None
        assert result.interference_meta_data is None
        assert result.senior_party_data is None
        assert result.junior_party_data is None
        assert len(result.additional_party_data_bag) == 0
        assert result.document_data is None
        assert result.raw_data is None

    def test_interference_response_from_dict_full(self) -> None:
        """Test PTABInterferenceResponse.from_dict() with multiple interferences."""
        data = {
            "count": 2,
            "requestIdentifier": "request-uuid-1",
            "patentInterferenceDataBag": [
                {
                    "interferenceNumber": "106123",
                },
                {
                    "interferenceNumber": "106456",
                },
            ],
        }
        result = PTABInterferenceResponse.from_dict(data)
        assert result.count == 2
        assert result.request_identifier == "request-uuid-1"
        assert len(result.patent_interference_data_bag) == 2
        assert result.patent_interference_data_bag[0].interference_number == "106123"
        assert result.patent_interference_data_bag[1].interference_number == "106456"
        assert result.raw_data is None

    def test_interference_response_from_dict_with_raw_data(self) -> None:
        """Test PTABInterferenceResponse.from_dict() with include_raw_data=True."""
        data = {
            "count": 1,
            "requestIdentifier": "request-uuid-1",
            "patentInterferenceDataBag": [
                {"interferenceNumber": "106123"},
            ],
        }
        result = PTABInterferenceResponse.from_dict(data, include_raw_data=True)
        assert result.count == 1
        assert result.raw_data == data
        assert len(result.patent_interference_data_bag) == 1
        assert result.patent_interference_data_bag[0].raw_data == {
            "interferenceNumber": "106123"
        }

    def test_interference_response_from_dict_empty(self) -> None:
        """Test PTABInterferenceResponse.from_dict() with empty list."""
        result = PTABInterferenceResponse.from_dict({})
        assert result.count == 0
        assert result.request_identifier is None
        assert len(result.patent_interference_data_bag) == 0
        assert result.raw_data is None


class TestToDictRoundTripping:
    """Tests for to_dict() methods via round-trip serialization using real API response data."""

    def test_trial_proceeding_response_round_trip(
        self, trial_proceeding_api_sample: Dict[str, Any]
    ) -> None:
        """Test PTABTrialProceedingResponse round-trip: from_dict → to_dict."""
        # Parse the API response
        response = PTABTrialProceedingResponse.from_dict(trial_proceeding_api_sample)

        # Convert back to dict
        result = response.to_dict()

        # Verify top-level fields
        assert result["count"] == trial_proceeding_api_sample["count"]
        assert (
            result["requestIdentifier"]
            == trial_proceeding_api_sample["requestIdentifier"]
        )
        assert len(result["patentTrialProceedingDataBag"]) == 1

        # Verify nested proceeding data
        proceeding = result["patentTrialProceedingDataBag"][0]
        original_proceeding = trial_proceeding_api_sample[
            "patentTrialProceedingDataBag"
        ][0]

        assert proceeding["trialNumber"] == original_proceeding["trialNumber"]
        assert (
            proceeding["trialMetaData"]["trialTypeCode"]
            == original_proceeding["trialMetaData"]["trialTypeCode"]
        )
        assert (
            proceeding["patentOwnerData"]["patentNumber"]
            == original_proceeding["patentOwnerData"]["patentNumber"]
        )

    def test_trial_decision_response_round_trip(
        self, trial_decision_api_sample: Dict[str, Any]
    ) -> None:
        """Test PTABTrialDocumentResponse round-trip with decision data."""
        # Parse the API response
        response = PTABTrialDocumentResponse.from_dict(trial_decision_api_sample)

        # Convert back to dict
        result = response.to_dict()

        # Verify top-level fields
        assert result["count"] == trial_decision_api_sample["count"]
        assert len(result["patentTrialDocumentDataBag"]) == 1

        # Verify nested document and decision data
        document = result["patentTrialDocumentDataBag"][0]
        original_document = trial_decision_api_sample["patentTrialDocumentDataBag"][0]

        assert document["trialNumber"] == original_document["trialNumber"]
        assert (
            document["trialDocumentCategory"]
            == original_document["trialDocumentCategory"]
        )
        assert (
            document["documentData"]["documentName"]
            == original_document["documentData"]["documentName"]
        )
        assert (
            document["decisionData"]["decisionTypeCategory"]
            == original_document["decisionData"]["decisionTypeCategory"]
        )

    def test_trial_document_response_round_trip(
        self, trial_document_api_sample: Dict[str, Any]
    ) -> None:
        """Test PTABTrialDocumentResponse round-trip with document data."""
        # Parse the API response
        response = PTABTrialDocumentResponse.from_dict(trial_document_api_sample)

        # Convert back to dict
        result = response.to_dict()

        # Verify top-level fields
        assert result["count"] == trial_document_api_sample["count"]
        assert len(result["patentTrialDocumentDataBag"]) == 2

        # Verify nested document data
        document = result["patentTrialDocumentDataBag"][0]
        original_document = trial_document_api_sample["patentTrialDocumentDataBag"][0]

        assert document["trialNumber"] == original_document["trialNumber"]
        assert (
            document["documentData"]["documentNumber"]
            == original_document["documentData"]["documentNumber"]
        )
        assert (
            document["regularPetitionerData"]["counselName"]
            == original_document["regularPetitionerData"]["counselName"]
        )

    def test_party_data_with_dates_round_trip(
        self, trial_proceeding_api_sample: Dict[str, Any]
    ) -> None:
        """Test that PartyData properly serializes dates in to_dict()."""
        # Get patent owner data which has dates
        party_data_dict = trial_proceeding_api_sample["patentTrialProceedingDataBag"][
            0
        ]["patentOwnerData"]
        party = PatentOwnerData.from_dict(party_data_dict)
        result = party.to_dict()

        # Verify date serialization
        assert result["grantDate"] == party_data_dict["grantDate"]
        assert isinstance(result["grantDate"], str)
        assert result["patentNumber"] == party_data_dict["patentNumber"]

    def test_to_dict_filters_none_values(self) -> None:
        """Test that to_dict() filters out None values."""
        data = {
            "applicationNumberText": "12/345678",
            "patentNumber": "US1234567",
            # Other fields omitted, will be None
        }
        party = PartyData.from_dict(data)
        result = party.to_dict()

        # Should only contain non-None values
        assert "applicationNumberText" in result
        assert "patentNumber" in result
        # None fields should be filtered out
        assert "grantDate" not in result

    def test_appeal_decision_response_round_trip(
        self, appeal_decision_api_sample: Dict[str, Any]
    ) -> None:
        """Test PTABAppealResponse round-trip: from_dict → to_dict."""
        # Parse the API response
        response = PTABAppealResponse.from_dict(appeal_decision_api_sample)

        # Convert back to dict
        result = response.to_dict()

        # Verify top-level fields
        assert result["count"] == appeal_decision_api_sample["count"]
        assert (
            result["requestIdentifier"]
            == appeal_decision_api_sample["requestIdentifier"]
        )
        assert len(result["patentAppealDataBag"]) == 1

        # Verify nested appeal data
        appeal = result["patentAppealDataBag"][0]
        original_appeal = appeal_decision_api_sample["patentAppealDataBag"][0]

        assert appeal["appealNumber"] == original_appeal["appealNumber"]
        assert (
            appeal["appealDocumentCategory"]
            == original_appeal["appealDocumentCategory"]
        )

        # Verify appealMetaData.to_dict() was called
        assert (
            appeal["appealMetaData"]["appealFilingDate"]
            == original_appeal["appealMetaData"]["appealFilingDate"]
        )
        assert (
            appeal["appealMetaData"]["applicationTypeCategory"]
            == original_appeal["appealMetaData"]["applicationTypeCategory"]
        )

        # Verify appellantData.to_dict() was called
        assert (
            appeal["appellantData"]["applicationNumberText"]
            == original_appeal["appellantData"]["applicationNumberText"]
        )
        assert (
            appeal["appellantData"]["counselName"]
            == original_appeal["appellantData"]["counselName"]
        )

        # Verify requestorData.to_dict() was called
        assert (
            appeal["requestorData"]["thirdPartyName"]
            == original_appeal["requestorData"]["thirdPartyName"]
        )

        # Verify documentData.to_dict() was called
        assert (
            appeal["documentData"]["documentName"]
            == original_appeal["documentData"]["documentName"]
        )
        assert (
            appeal["documentData"]["documentFilingDate"]
            == original_appeal["documentData"]["documentFilingDate"]
        )

        # Verify decisionData.to_dict() was called
        assert (
            appeal["decisionData"]["appealOutcomeCategory"]
            == original_appeal["decisionData"]["appealOutcomeCategory"]
        )
        assert (
            appeal["decisionData"]["decisionTypeCategory"]
            == original_appeal["decisionData"]["decisionTypeCategory"]
        )

    def test_interference_decision_response_round_trip(
        self, interference_decision_api_sample: Dict[str, Any]
    ) -> None:
        """Test PTABInterferenceResponse round-trip: from_dict → to_dict."""
        # Parse the API response
        response = PTABInterferenceResponse.from_dict(interference_decision_api_sample)

        # Convert back to dict
        result = response.to_dict()

        # Verify top-level fields
        assert result["count"] == interference_decision_api_sample["count"]
        assert (
            result["requestIdentifier"]
            == interference_decision_api_sample["requestIdentifier"]
        )
        assert len(result["patentInterferenceDataBag"]) == 2

        # Verify nested interference data
        interference = result["patentInterferenceDataBag"][0]
        original_interference = interference_decision_api_sample[
            "patentInterferenceDataBag"
        ][0]

        assert (
            interference["interferenceNumber"]
            == original_interference["interferenceNumber"]
        )

        # Verify interferenceMetaData.to_dict() was called
        assert (
            interference["interferenceMetaData"]["interferenceStyleName"]
            == original_interference["interferenceMetaData"]["interferenceStyleName"]
        )
        assert (
            interference["interferenceMetaData"]["declarationDate"]
            == original_interference["interferenceMetaData"]["declarationDate"]
        )

        # Verify seniorPartyData.to_dict() was called
        assert (
            interference["seniorPartyData"]["patentNumber"]
            == original_interference["seniorPartyData"]["patentNumber"]
        )
        assert (
            interference["seniorPartyData"]["patentOwnerName"]
            == original_interference["seniorPartyData"]["patentOwnerName"]
        )

        # Verify juniorPartyData.to_dict() was called
        assert (
            interference["juniorPartyData"]["patentNumber"]
            == original_interference["juniorPartyData"]["patentNumber"]
        )
        assert (
            interference["juniorPartyData"]["publicationNumber"]
            == original_interference["juniorPartyData"]["publicationNumber"]
        )

        # Verify documentData.to_dict() was called
        assert (
            interference["documentData"]["documentName"]
            == original_interference["documentData"]["documentName"]
        )
        assert (
            interference["documentData"]["interferenceOutcomeCategory"]
            == original_interference["documentData"]["interferenceOutcomeCategory"]
        )
