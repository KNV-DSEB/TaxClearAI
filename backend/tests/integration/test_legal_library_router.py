from fastapi.testclient import TestClient


def test_legal_library_returns_sync_metadata_and_exact_clauses(client: TestClient) -> None:
    response = client.post(
        "/legal-library/search",
        json={"procedure": "hkd_termination"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"]
    hkd_reference = next(
        item for item in payload["results"] if item["document_number"] == "168/2025/NĐ-CP"
    )
    assert hkd_reference["issuing_authority"] == "Chính phủ"
    assert hkd_reference["issued_date"] == "2025-06-30"
    assert hkd_reference["effective_date"] == "2025-07-01"
    assert hkd_reference["effectiveness_status"] == "khong_ro"
    assert any(
        item["article"] == "Điều 104" and item["clause"] == "Khoản 1"
        for item in hkd_reference["applicable_provisions"]
    )
    assert hkd_reference["source_url"].startswith("https://congbao.chinhphu.vn/")
    assert hkd_reference["last_synced"] is None
    assert hkd_reference["has_verbatim_text"] is False


def test_legal_library_includes_shared_store_sync_fields(
    client: TestClient,
) -> None:
    response = client.post("/legal-library/search", json={"query": "kinh tế tư nhân"})

    assert response.status_code == 200
    resolution = next(
        item for item in response.json()["results"] if item["document_number"] == "198/2025/QH15"
    )
    assert resolution["has_verbatim_text"] is False
    assert resolution["last_synced"] is None
    assert resolution["effectiveness_status"] == "khong_ro"
    assert "lệ phí môn bài" in resolution["change_note"]


def test_legal_library_can_search_by_query(client: TestClient) -> None:
    response = client.post("/legal-library/search", json={"query": "mã số thuế"})

    assert response.status_code == 200
    assert any(item["document_number"] == "90/2026/TT-BTC" for item in response.json()["results"])


def test_legal_library_rejects_empty_lookup(client: TestClient) -> None:
    response = client.post("/legal-library/search", json={})

    assert response.status_code == 422
