from fastapi.testclient import TestClient

from protocol_to_study_setup_json.api import app


client = TestClient(app)


def test_agent_endpoint_uses_default_protocol_folder():
    response = client.post("/agent", json={})

    assert response.status_code == 200
    assert response.json()["clinical_trial_setup"]["protocol_identification"]["protocol_id"] == "PRO-2026-NEURO-042"


def test_agent_endpoint_reports_missing_folder():
    response = client.post("/agent", json={"input_folder": "missing-protocol-folder"})

    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]