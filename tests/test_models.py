from protocol_to_study_setup_json.agent import ProtocolStudySetupAgent
from protocol_to_study_setup_json.loader import ProtocolDocumentLoader
from protocol_to_study_setup_json.models import ClinicalTrialSetup, ClinicalTrialSetupRoot


def test_clinical_trial_setup_schema_builds():
    schema = ClinicalTrialSetup.model_json_schema()
    assert "properties" in schema
    assert "clinical_trial_setup" in schema["properties"]
    trial = ClinicalTrialSetupRoot.model_json_schema()["properties"]
    assert "protocol_identification" in trial
    assert "study_design" in trial
    assert "eligibility_criteria" in trial
    assert "study_arms" in trial
    assert "laboratory_tests" in trial
    assert "investigational_kits" in trial
    assert "outcome_measures" in trial
    assert "schedule_of_events" in trial


def test_loader_reads_sample_protocol_documents():
    loader = ProtocolDocumentLoader()
    docs = loader.load_from_folder("Protocol documents")
    assert len(docs) >= 1
    assert all(doc.extracted_text.strip() for doc in docs)
    assert any("PRO-2026-NEURO-042" in doc.extracted_text for doc in docs)


def test_clinical_trial_json_matches_expected_shape():
    sample = {
        "clinical_trial_setup": {
            "protocol_identification": {
                "protocol_id": "PRO-2026-NEURO-042",
                "nct_number": "NCT09876543",
                "official_title": "Sample study",
                "brief_title": "Sample",
                "phase": "Phase 3",
                "sponsor": {"name": "Nexus Therapeutics Inc.", "type": "Industry", "lead_sponsor": True},
            },
            "study_design": {
                "allocation": "Randomized",
                "intervention_model": "Parallel Assignment",
                "masking": "Double-blind",
                "masking_roles": ["Participant", "Care Provider"],
                "primary_purpose": "Treatment",
                "target_enrollment": 450,
            },
            "eligibility_criteria": {
                "minimum_age": "50 Years",
                "maximum_age": "85 Years",
                "sex": "All",
                "inclusion_criteria": ["Has early Alzheimer's."],
                "exclusion_criteria": ["No prior investigational treatment."],
            },
            "study_arms": [],
            "laboratory_tests": [],
            "investigational_kits": [],
            "outcome_measures": {"primary_outcomes": [], "secondary_outcomes": []},
            "schedule_of_events": {"visits": []},
        }
    }
    parsed = ClinicalTrialSetup.model_validate(sample)
    assert parsed.clinical_trial_setup.protocol_identification.protocol_id == "PRO-2026-NEURO-042"
    assert parsed.clinical_trial_setup.study_design.target_enrollment == 450


def test_mock_model_response_returns_expected_json_shape():
    agent = ProtocolStudySetupAgent(azure_endpoint=None)
    result = agent.run("Protocol documents")
    assert "clinical_trial_setup" in result
    assert result["clinical_trial_setup"]["protocol_identification"]["protocol_id"] == "PRO-2026-NEURO-042"
    assert result["clinical_trial_setup"]["study_design"]["target_enrollment"] == 450
