def test_openapi_json_lists_core_routes(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert schema["info"]["title"] == "RecruitSaaS AI Service"
    paths = schema["paths"]
    assert "/ai/score" in paths
    assert "/ai/summarize" in paths
    assert "/ai/rank-candidates" in paths


def test_docs_endpoint_returns_html(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()
