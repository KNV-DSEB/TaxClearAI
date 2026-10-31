import argparse
import sys
from pathlib import Path

from src.modules.chatbot.law_source import load_law_entries, read_law_text_records
from src.modules.chatbot.source_policy import is_usable_source


def validate_library(path: Path | None = None) -> list[str]:
    records, errors = read_law_text_records(path)
    entries = {entry.id: entry for entry in load_law_entries(path)}
    issues = list(errors)
    for record in records.values():
        key = "/".join(record.key)
        matching = next(
            (
                entry
                for entry in entries.values()
                if (entry.document_number, entry.article, entry.clause, entry.point or "")
                == record.key
            ),
            None,
        )
        if matching is None:
            issues.append(f"{key}: thiếu nguyên văn hoặc không có metadata")
            continue
        if not record.has_original_text:
            issues.append(f"{key}: thiếu nguyên văn")
        if not matching.source_domain:
            issues.append(f"{key}: domain ngoài allowlist hoặc thiếu")
        if not matching.fetched_at:
            issues.append(f"{key}: thiếu fetched_at")
        if matching.effectiveness_status.value == "het_hieu_luc":
            issues.append(f"{key}: hết hiệu lực")
        elif matching.effectiveness_status.value != "con_hieu_luc":
            issues.append(f"{key}: tình trạng hiệu lực chưa xác nhận")
        if matching.content_sha256 and not is_usable_source(matching):
            issues.append(f"{key}: nguồn không dùng được (tuổi, allowlist, trạng thái hoặc hash)")
        elif not matching.content_sha256:
            issues.append(f"{key}: thiếu hash")
    usable = sum(is_usable_source(entry) for entry in entries.values())
    issues.append(f"Số mục dùng được: {usable}/{len(records)}")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = validate_library()
    print("\n".join(report))
    if args.strict and any("Số mục dùng được:" not in issue for issue in report):
        sys.exit(1)


if __name__ == "__main__":
    main()
