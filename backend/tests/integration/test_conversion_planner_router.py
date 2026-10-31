def test_create_parallel_conversion_plan(client) -> None:
    response = client.post(
        "/conversion-plans/parallel",
        json={
            "current_model": "HKD",
            "desired_model": "HKD",
            "new_name_prepared": True,
            "new_address_prepared": True,
            "new_industry_prepared": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["conversion_kind"] == "HKD_TO_HKD"
    assert len(body["lanes"]) == 2
    assert body["hard_stops"][0]["active"] is True
    assert body["lanes"][1]["tasks"][-1]["status"] == "READY"


def test_hkd_to_company_plan_returns_its_own_active_hard_stop(client) -> None:
    response = client.post(
        "/conversion-plans/parallel",
        json={"current_model": "HKD", "desired_model": "COMPANY_LLC"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["conversion_kind"] == "HKD_TO_COMPANY"
    assert body["hard_stops"][0]["code"] == "OLD_HKD_TO_COMPANY_STATUS_REQUIRES_REVIEW"
    assert body["hard_stops"][0]["active"] is True
    assert "công ty" in body["next_action"]


def test_company_type_change_endpoint_does_not_close_old_company(client) -> None:
    response = client.post(
        "/conversion-plans/parallel",
        json={"current_model": "COMPANY_LLC", "desired_model": "COMPANY_JSC"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["conversion_kind"] == "COMPANY_TYPE_CHANGE"
    assert body["hard_stops"][0]["active"] is True
    assert body["needs_expert"] is True
    assert len(body["lanes"]) == 1
    task_ids = [task["task_id"] for task in body["lanes"][0]["tasks"]]
    assert "conversion_resolution" in task_ids
    assert "old_tax_close" not in task_ids
    assert "không phải giải thể" in body["legal_note"]
