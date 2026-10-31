import json
import re

from fastapi.testclient import TestClient

_JOINED_WORDS = (
    "thuếtheo",
    "cấpxã",
    "quảkhi",
    "cònnghĩa",
    "đanghoạt",
    "thuậnvới",
    "ángiải",
    "doanhtrước",
    "cổphần",
    "liệuquốc",
    "vụđó",
    "giảithể",
    "chuyểnđổi",
    "yêucầu",
    "cáckhoản",
)
_JOINED_WORD_PATTERN = re.compile(
    "|".join(re.escape(word) for word in _JOINED_WORDS), re.IGNORECASE
)
_SEGMENTS = ("A1", "A2", "A3", "B1", "B2")
_TARGETS = ("terminate", "convert_to_new_entity")


def assert_no_joined_words(payload: object) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    match = _JOINED_WORD_PATTERN.search(text)
    assert match is None, f"Joined words found in response: {match.group(0) if match else ''}"


def test_roadmap_and_checklist_text_has_no_joined_words(client: TestClient) -> None:
    for segment in _SEGMENTS:
        for target in _TARGETS:
            roadmap = client.post(
                "/procedures/roadmap",
                json={"segment": segment, "target_action": target},
            )
            assert roadmap.status_code == 200
            assert_no_joined_words(roadmap.json())

            checklist = client.post(
                "/documents/checklist",
                json={"segment": segment, "procedure": target, "documents": []},
            )
            assert checklist.status_code == 200
            assert_no_joined_words(checklist.json())
