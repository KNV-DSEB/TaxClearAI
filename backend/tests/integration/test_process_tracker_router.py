def test_track_process_endpoint(client) -> None:
    response = client.post(
        "/process-tracker/track",
        json={
            "procedure": "hkd_termination",
            "steps": [
                {
                    "step_order": 1,
                    "phase": "PREPARATION",
                    "action": "Tra cứu nghĩa vụ",
                    "agency": "Tự thực hiện",
                },
                {
                    "step_order": 2,
                    "phase": "REGISTRATION_RESULT",
                    "action": "Nhận kết quả",
                    "agency": "Cơ quan ĐKKD",
                },
            ],
            "completed_steps": [{"step_order": 1, "completed_at": "2026-10-30T09:00:00Z"}],
            "current_step_started_at": "2026-10-30T09:00:00Z",
            "as_of": "2026-10-30T09:00:00Z",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["progress_percentage"] == 50
    assert body["current_stage"] == "REGISTRATION_RESULT"
    assert body["current_step"] == "Nhận kết quả"
    assert body["critical_deadlines"][0]["deadline_date"] == "2026-11-06"


def test_track_process_rejects_unknown_completed_step(client) -> None:
    response = client.post(
        "/process-tracker/track",
        json={
            "procedure": "hkd_termination",
            "steps": [{"step_order": 1, "phase": "PREPARATION", "action": "Tra cứu nghĩa vụ"}],
            "completed_steps": [{"step_order": 2, "completed_at": "2026-10-30T09:00:00Z"}],
            "current_step_started_at": "2026-10-30T09:00:00Z",
        },
    )

    assert response.status_code == 422
