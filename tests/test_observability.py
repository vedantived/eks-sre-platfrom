def test_response_includes_generated_request_id_header(client):
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_supplied_request_id_header_is_echoed_back(client):
    response = client.get("/health", headers={"X-Request-ID": "fixed-test-id-123"})
    assert response.headers["X-Request-ID"] == "fixed-test-id-123"


def test_each_request_gets_a_distinct_request_id(client):
    first = client.get("/health").headers["X-Request-ID"]
    second = client.get("/health").headers["X-Request-ID"]
    assert first != second
