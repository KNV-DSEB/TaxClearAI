import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, ValidationError

from src.modules.chatbot.schemas import EffectivenessStatus, LawEntry, Segment
from src.modules.legal_library.repository import LegalLibraryRepository
from src.modules.legal_library.schemas import ApplicableProvision, LegalProcedure

type LawTextKey = tuple[str, str, str, str]

PROCEDURE_TO_SEGMENTS: dict[LegalProcedure, tuple[Segment, ...]] = {
    LegalProcedure.HKD_TERMINATION: (Segment.A1, Segment.A2, Segment.A3),
    LegalProcedure.HKD_NEW_REGISTRATION: (Segment.A1, Segment.A2, Segment.A3),
    LegalProcedure.COMPANY_DISSOLUTION: (Segment.B1, Segment.B2),
    LegalProcedure.TAX_ID_TERMINATION: tuple(Segment),
}


class LawTextRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    document_number: str
    article: str
    clause: str
    point: str | None = None
    noi_dung: str
    source_url: str = ""
    source_domain: str = ""
    fetched_at: datetime | None = None
    content_sha256: str = ""
    effectiveness_status: EffectivenessStatus = EffectivenessStatus.UNKNOWN
    effective_date: date | None = None
    amended_by: str | None = None

    @property
    def key(self) -> LawTextKey:
        return tuple(
            (value or "").strip()
            for value in (self.document_number, self.article, self.clause, self.point)
        )  # type: ignore[return-value]

    @property
    def has_original_text(self) -> bool:
        normalized = self.noi_dung.casefold()
        return bool(self.noi_dung.strip()) and not any(
            marker in normalized
            for marker in ("chưa có nội dung nguyên văn", "placeholder", "[chưa", "giữ chỗ")
        )


def read_law_text_records(
    path: Path | None = None,
) -> tuple[dict[LawTextKey, LawTextRecord], list[str]]:
    file_path = path or Path(__file__).parent / "data" / "law_text.json"
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"{file_path}: cannot read law text ({error})"]
    if not isinstance(raw, list):
        return {}, [f"{file_path}: top-level JSON value must be a list"]
    records: dict[LawTextKey, LawTextRecord] = {}
    errors: list[str] = []
    for index, item in enumerate(raw, 1):
        try:
            record = LawTextRecord.model_validate(item)
        except (ValidationError, TypeError) as error:
            errors.append(f"row {index}: invalid entry ({error})")
            continue
        if record.key in records:
            errors.append(f"row {index}: duplicate entry {record.key}")
        else:
            records[record.key] = record
    return records, errors


def load_law_entries(path: Path | None = None) -> list[LawEntry]:
    records, _ = read_law_text_records(path)
    metadata: dict[LawTextKey, tuple[ApplicableProvision, set[Segment]]] = {}
    repository = LegalLibraryRepository()
    for procedure, segments in PROCEDURE_TO_SEGMENTS.items():
        for reference in repository.get_references(procedure, None):
            for provision in reference.applicable_provisions:
                key = (
                    reference.document_number,
                    provision.article,
                    provision.clause,
                    provision.point or "",
                )
                if key not in metadata:
                    metadata[key] = (provision, set())
                metadata[key][1].update(segments)
    entries: list[LawEntry] = []
    for key, record in records.items():
        meta = metadata.get(key)
        if not meta:
            continue
        _, applicable_segments = meta
        domain = urlparse(record.source_url).hostname or record.source_domain
        entries.append(
            LawEntry(
                id="L" + hashlib.sha256("|".join(key).encode()).hexdigest()[:12].upper(),
                document_number=record.document_number,
                article=record.article,
                clause=record.clause,
                point=record.point,
                noi_dung=record.noi_dung,
                source_url=record.source_url,
                source_domain=record.source_domain or domain,
                fetched_at=record.fetched_at,
                content_sha256=record.content_sha256,
                effectiveness_status=record.effectiveness_status,
                effective_date=record.effective_date,
                amended_by=record.amended_by,
                ap_dung_cho=sorted(
                    applicable_segments, key=lambda segment: list(Segment).index(segment)
                ),
                van_ban=record.document_number,
                dieu_khoan=", ".join(
                    filter(None, (record.article, record.clause, record.point or ""))
                ),
                hieu_luc=record.effectiveness_status,
            )
        )
    return entries
