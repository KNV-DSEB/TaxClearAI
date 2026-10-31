import re

import pytest

from src.core.config import Settings
from src.main import app
from src.modules.chatbot.llm import MockLLM
from src.modules.chatbot.pipeline import ChatbotPipeline
from src.modules.chatbot.retriever import KeywordRetriever
from src.modules.chatbot.router import get_chatbot_pipeline

_CUSTOMER_AMOUNT_PATTERN = re.compile(
    r"(?:\d[\d.,]*\s*(?:triệu|đồng|vnd|tỷ)\b|\b\d{1,3}(?:\.\d{3})+\b)",
    re.IGNORECASE,
)


@pytest.fixture(autouse=True)
def mock_chatbot_dependency():
    app.dependency_overrides[get_chatbot_pipeline] = lambda: ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True),
        KeywordRetriever(),
        MockLLM(),
    )
    yield
    app.dependency_overrides.pop(get_chatbot_pipeline, None)


@pytest.mark.parametrize(
    ("message", "segment", "expected_money_guardrail"),
    [
        (
            "Em ơi, DN của anh thành lập được 10 năm, anh để không mấy năm nay giờ thành "
            "bỏ trốn rồi. Anh muốn giải thể thì làm thế nào?",
            "B2",
            False,
        ),
        (
            "Trước anh có thành lập DN nhưng không làm gì, giờ anh/chị muốn giải thể thì "
            "phải làm những gì, phí bao nhiêu tiền thế?",
            "B1",
            True,
        ),
        (
            "Anh có cái giấy phép cửa hàng buôn bán nhỏ lẻ, nhưng từ lúc thành lập đến giờ "
            "anh không kê khai, giờ anh muốn giải tán hộ KD để đỡ rắc rối thì làm thế nào? "
            "Phí bao nhiêu tiền, giải thể có lâu không?",
            "A2",
            True,
        ),
    ],
    ids=["b2-abandoned-company", "b1-fee-question", "a2-fee-question"],
)
def test_customer_queries_with_fail_closed_sources_and_mock_llm(
    client, message: str, segment: str, expected_money_guardrail: bool
) -> None:
    from src.modules.chatbot.dependencies import reset_rate_limit_state

    reset_rate_limit_state()

    response = client.post(
        "/chatbot/ask",
        json={"tin_nhan": message, "nhom": segment, "buoc": ""},
    )

    assert response.status_code == 200
    payload = response.json()
    answer = payload["answer"]
    assert _CUSTOMER_AMOUNT_PATTERN.search(answer) is None
    if expected_money_guardrail:
        assert payload["che_do"] == 2
        assert payload["ly_do_chan"] == "hoi_so_tien"
        assert "cổng Thuế điện tử" in answer
        assert "POST /cases/brief" not in answer
    else:
        assert payload["che_do"] != 2
        assert payload["nguon"] == []
        assert "Chưa tìm thấy căn cứ pháp lý đủ điều kiện" in answer


def test_chatbot_ask_uses_fixed_no_source_response(client) -> None:
    response = client.post(
        "/chatbot/ask",
        json={"tin_nhan": "nguyên văn điều luật", "nhom": "A2", "buoc": "Đang chuẩn bị"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["che_do"] == 3
    assert payload["citations"] == []
    assert payload["nguon"] == []
    assert "Chưa tìm thấy căn cứ pháp lý đủ điều kiện" in payload["answer"]


def test_chatbot_ask_rejects_oversized_message(client) -> None:
    response = client.post(
        "/chatbot/ask",
        json={"tin_nhan": "x" * 1001, "nhom": "A2", "buoc": "Đang chuẩn bị"},
    )

    assert response.status_code == 422


def test_chatbot_money_question_returns_mode_two(client) -> None:
    response = client.post(
        "/chatbot/ask",
        json={"tin_nhan": "Tính thuế giúp tôi", "nhom": "A2", "buoc": "Đang chuẩn bị"},
    )

    assert response.status_code == 200
    assert response.json()["che_do"] == 2
    assert response.json()["needs_expert"] is False
    answer = response.json()["answer"]
    assert "không tính hoặc ước lượng thuế, tiền phạt, phí" in answer
    assert "cổng Thuế điện tử" in answer
    assert "POST /cases/brief" not in answer
    assert "chuyên gia rà soát" in answer
    assert not any(character.isdigit() for character in answer)


@pytest.mark.parametrize("include_step", [False, True])
def test_chatbot_ask_accepts_missing_or_empty_step(client, include_step: bool) -> None:
    request_body = {"tin_nhan": "Giải thích hồ sơ", "nhom": "A2"}
    if include_step:
        request_body["buoc"] = ""

    response = client.post("/chatbot/ask", json=request_body)

    assert response.status_code == 200


def test_chatbot_ask_still_rejects_overlong_step(client) -> None:
    response = client.post(
        "/chatbot/ask",
        json={
            "tin_nhan": "Giải thích hồ sơ",
            "nhom": "A2",
            "buoc": "x" * 201,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("message", "expected_label"),
    [
        ("Anh Hùng bị thanh tra thuế", "bi_co_quan_lien_he"),
        ("chị Lan bị truy thu thuế", "bi_co_quan_lien_he"),
        ("Chị Lan muốn giấu doanh thu", "ne_thue"),
        ("ông Nam muốn né thuế", "ne_thue"),
        ("bà Hoa nợ thuế 3 kỳ", "no_ton_dong"),
        ("Tôi tên là Lan giấu doanh thu", "ne_thue"),
        ("chị Lan khai thấp doanh thu", "ne_thue"),
    ],
)
def test_chatbot_ask_detects_risk_before_redacting_names(
    client, message: str, expected_label: str
) -> None:
    response = client.post(
        "/chatbot/ask",
        json={"tin_nhan": message, "nhom": "A2", "buoc": "Đang chuẩn bị"},
    )

    assert response.status_code == 200
    assert response.json()["che_do"] == 3
    assert response.json()["ly_do_chan"] == expected_label


def test_chatbot_rate_limits_by_client_ip(client) -> None:
    from src.modules.chatbot.dependencies import reset_rate_limit_state

    reset_rate_limit_state()
    request_body = {
        "tin_nhan": "Giải thích thủ tục này",
        "nhom": "A2",
        "buoc": "Đang chuẩn bị",
    }
    for _ in range(20):
        assert client.post("/chatbot/ask", json=request_body).status_code == 200
    assert client.post("/chatbot/ask", json=request_body).status_code == 429
    reset_rate_limit_state()
