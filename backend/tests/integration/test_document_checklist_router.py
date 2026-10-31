from fastapi.testclient import TestClient


def test_checklist_returns_only_metadata_based_document_statuses(client: TestClient) -> None:
    response = client.post(
        "/documents/checklist",
        json={
            "segment": "A2",
            "procedure": "terminate",
            "documents": [
                {"doc_id": "DOC_TAX_CLOSE", "declared_state": "available"},
                {"doc_id": "DOC_TAX_DECLARATIONS", "declared_state": "needs_verification"},
                {"doc_id": "DOC_HKD_TERMINATION", "declared_state": "missing"},
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_items"] == 8
    assert body["readiness_percentage"] == 12
    assert {item["status"] for item in body["checklist"]} == {
        "already_have",
        "missing",
        "needs_verification",
    }
    assert all(
        set(item) == {"doc_id", "doc_name", "status", "template_download_available", "action_guide"}
        for item in body["checklist"]
    )


def test_checklist_rejects_uploaded_document_content(client: TestClient) -> None:
    response = client.post(
        "/documents/checklist",
        json={
            "segment": "A2",
            "procedure": "terminate",
            "documents": [
                {
                    "doc_id": "DOC_TAX_CLOSE",
                    "declared_state": "available",
                    "file_base64": "sensitive-file-content",
                }
            ],
        },
    )

    assert response.status_code == 422


def test_checklist_rejects_unknown_segment(client: TestClient) -> None:
    response = client.post(
        "/documents/checklist",
        json={"segment": "C1", "procedure": "terminate"},
    )

    assert response.status_code == 422


def test_checklist_rejects_unknown_document_id_for_the_selected_procedure(
    client: TestClient,
) -> None:
    response = client.post(
        "/documents/checklist",
        json={
            "segment": "A2",
            "procedure": "terminate",
            "documents": [{"doc_id": "NOT_IN_CATALOG", "declared_state": "available"}],
        },
    )

    assert response.status_code == 422
