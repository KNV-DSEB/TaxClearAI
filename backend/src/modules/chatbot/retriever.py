import re
import unicodedata
from pathlib import Path
from typing import Protocol

from src.modules.chatbot.schemas import LawEntry, Segment
from src.modules.chatbot.source_policy import is_usable_source

STOP_WORDS: frozenset[str] = frozenset(
    {
        "va",
        "la",
        "gi",
        "nao",
        "the",
        "nhu",
        "khong",
        "co",
        "duoc",
        "can",
        "hay",
        "nhung",
        "cac",
        "cua",
        "cho",
        "voi",
        "theo",
        "mot",
        "nhieu",
        "toi",
        "ban",
        "minh",
        "nay",
        "do",
        "khi",
        "tu",
        "ve",
        "trong",
        "tren",
        "duoi",
        "den",
        "ho",
        "se",
        "da",
    }
)


class Retriever(Protocol):
    def retrieve(self, query: str, segment: Segment, top_k: int) -> list[LawEntry]: ...


class KeywordRetriever:
    def __init__(
        self,
        library_path: Path | None = None,
        *,
        entries: list[LawEntry] | None = None,
        min_score: int = 1,
    ) -> None:
        self._min_score = min_score
        if entries is not None:
            self.entries = entries
        else:
            from src.modules.chatbot.law_source import load_law_entries

            self.entries = load_law_entries(library_path)
        self._entry_terms = [
            self._terms(" ".join((entry.van_ban, entry.dieu_khoan, entry.noi_dung)))
            for entry in self.entries
        ]

    def retrieve(self, query: str, segment: Segment, top_k: int) -> list[LawEntry]:
        terms = self._terms(query)
        candidates = [
            (entry, entry_terms)
            for entry, entry_terms in zip(self.entries, self._entry_terms, strict=True)
            if segment in entry.ap_dung_cho and is_usable_source(entry)
        ]
        ranked = [
            (entry, sum(term in entry_terms for term in terms), position)
            for position, (entry, entry_terms) in enumerate(candidates)
        ]
        ranked = [item for item in ranked if item[1] >= self._min_score]
        ranked.sort(key=lambda item: (-item[1], item[2]))
        return [entry for entry, _, _ in ranked[:top_k]]

    @staticmethod
    def _terms(text: str) -> set[str]:
        normalized = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
        ascii_text = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
        return {term for term in re.findall(r"[a-z0-9]{3,}", ascii_text) if term not in STOP_WORDS}
