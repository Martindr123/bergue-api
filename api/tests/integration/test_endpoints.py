# app/tests/integration/test_endpoints.py

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_healthcheck():
    response = client.get("/api/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_doc_initiate():
    # On peut envoyer un faux fichier en mémoire
    with open("tests/sample_data/fake_compte_rendu.pdf", "rb") as f:
        files = {"compte_rendu_file": f}
        data = {
            "description_missions": "exemple",
            "montant_provision": "1000",
        }
        response = client.post("/api/generate-doc/initiate", files=files, data=data)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert "job_id" in json_resp
    assert json_resp["status"] == "started"
