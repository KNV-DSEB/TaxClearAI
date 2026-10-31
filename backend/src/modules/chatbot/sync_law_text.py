import hashlib
import json
import re
import time
import urllib.error
import urllib.request
import urllib.robotparser
import zipfile
from datetime import UTC, datetime
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urljoin, urlparse
from xml.etree import ElementTree

from src.core.config import get_settings
from src.modules.chatbot.law_source import LawTextKey, read_law_text_records

DATA_DIR = Path(__file__).parent / "data"
USER_AGENT = "TaxClearAI-LawSync/1.0 (official legal text synchronization)"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav", "footer", "header"}:
            self.hidden += 1
        if tag in {"p", "div", "br", "tr", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "header"} and self.hidden:
            self.hidden -= 1
        if tag in {"p", "div", "tr", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


class _LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = next((value for name, value in attrs if name == "href"), None)
            if href:
                self.links.append(href)


def _fetch(url: str, *, timeout: float = 12.0) -> str:
    return _fetch_bytes(url, timeout=timeout).decode("utf-8", errors="replace")


def _fetch_bytes(url: str, *, timeout: float = 12.0) -> bytes:
    host = urlparse(url).hostname
    if not host:
        raise ValueError("URL không hợp lệ")
    robots_url = f"https://{host}/robots.txt"
    parser = urllib.robotparser.RobotFileParser(robots_url)
    try:
        robots = _read_url(robots_url, timeout)
        parser.parse(robots.decode("utf-8", errors="replace").splitlines())
    except (urllib.error.URLError, TimeoutError) as error:
        raise ValueError("không đọc được robots.txt") from error
    if not parser.can_fetch(USER_AGENT, url):
        raise ValueError("robots.txt không cho phép truy cập")
    return _read_url(url, timeout)


def _read_url(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return cast(bytes, response.read())
        except (urllib.error.URLError, TimeoutError):
            if attempt == 1:
                raise
            time.sleep(0.25)
    raise RuntimeError("request retry limit exceeded")


def _extract_official_document_text(page: str, source_url: str) -> str | None:
    link_parser = _LinkExtractor()
    link_parser.feed(page)
    document_urls = []
    for link in link_parser.links:
        parsed_link = urlparse(link)
        file_name = parse_qs(parsed_link.query).get("file_name", [""])[0]
        extension = Path(file_name or parsed_link.path).suffix.lower()
        if extension in {".docx", ".pdf"}:
            document_urls.append(urljoin(source_url, link))
    allowed_domains = get_settings().allowed_law_domains
    for document_url in document_urls:
        if (urlparse(document_url).hostname or "").lower() not in allowed_domains:
            continue
        try:
            payload = _fetch_bytes(document_url)
            if urlparse(document_url).path.lower().endswith(".pdf") or parse_qs(
                urlparse(document_url).query
            ).get("file_name", [""])[0].lower().endswith(".pdf"):
                from pypdf import PdfReader

                pdf = PdfReader(BytesIO(payload))
                pdf_paragraphs = [
                    text
                    for page_item in pdf.pages
                    if (text := page_item.extract_text()) and text.strip()
                ]
                if pdf_paragraphs:
                    return "\n".join(pdf_paragraphs)
                continue
            with zipfile.ZipFile(BytesIO(payload)) as archive:
                xml = ElementTree.fromstring(archive.read("word/document.xml"))
        except (OSError, ValueError, KeyError, zipfile.BadZipFile, urllib.error.URLError):
            continue
        paragraphs: list[str] = []
        for paragraph in xml.iter(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
        ):
            text = "".join(
                node.text or ""
                for node in paragraph.iter(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
                )
            )
            if text.strip():
                paragraphs.append(text)
        if paragraphs:
            return "\n".join(paragraphs)
    return None


def extract_provision(text: str, article: str, clause: str, point: str | None) -> str | None:
    article_numbers = re.findall(r"\d+", article)
    clause_numbers = re.findall(r"\d+", clause)
    point_numbers = re.findall(r"[a-zđ](?:\.\d+)?", point or "", re.IGNORECASE)
    if len(article_numbers) != 1 or len(clause_numbers) != 1 or len(point_numbers) > 1:
        return None
    article_re = re.compile(rf"\bĐiều\s+{article_numbers[0]}\b", re.IGNORECASE)
    matches = list(article_re.finditer(text))
    if len(matches) != 1:
        return None
    start = matches[0].start()
    next_article = re.search(r"\bĐiều\s+\d+\b", text[matches[0].end() :], re.IGNORECASE)
    section = (
        text[start : matches[0].end() + next_article.start()] if next_article else text[start:]
    )
    article_end = matches[0].end() - start
    clause_re = re.compile(rf"(?<!\w){clause_numbers[0]}\s*[.)]\s")
    clauses = list(clause_re.finditer(section[article_end:]))
    if len(clauses) != 1:
        return None
    clause_text = section[article_end:]
    clause_start = clauses[0].start()
    next_clause = re.search(r"(?<!\w)\d+\s*[.)]\s", clause_text[clauses[0].end() :])
    end = clauses[0].end() + next_clause.start() if next_clause else len(clause_text)
    result = clause_text[clause_start:end].strip()
    if point:
        point_label = point_numbers[0]
        point_re = re.compile(rf"(?<![\w.]){re.escape(point_label)}\s*[.)]\s", re.IGNORECASE)
        point_matches = list(point_re.finditer(result))
        if len(point_matches) != 1:
            return None
        point_start = point_matches[0].start()
        point_end_match = re.search(
            r"(?<![\w.])[a-zđ](?:\.\d+)?\s*[.)]\s",
            result[point_matches[0].end() :],
            re.IGNORECASE,
        )
        point_end = (
            point_matches[0].end() + point_end_match.start() if point_end_match else len(result)
        )
        result = result[point_start:point_end]
    return result or None


def synchronize() -> dict[str, object]:
    settings = get_settings()
    source_manifest = json.loads((DATA_DIR / "law_sources.json").read_text(encoding="utf-8"))
    existing, _ = read_law_text_records()
    raw_existing = json.loads((DATA_DIR / "law_text.json").read_text(encoding="utf-8"))
    old_by_key: dict[LawTextKey, dict[str, object]] = {}
    for row in raw_existing:
        key = cast(
            LawTextKey,
            tuple(
                str(row.get(field) or "").strip()
                for field in ("document_number", "article", "clause", "point")
            ),
        )
        old_by_key[key] = row
    successes = 0
    skipped: list[str] = []
    missing_urls: list[str] = []
    expired: list[str] = []
    for document in source_manifest:
        url = document["source_url"]
        if not url:
            missing_urls.append(document["document_number"])
            continue
        domain = urlparse(url).hostname or ""
        if domain not in settings.allowed_law_domains:
            for provision in document["provisions"]:
                key = (
                    document["document_number"],
                    provision["article"],
                    provision["clause"],
                    provision.get("point", ""),
                )
                skipped.append(f"{key}: domain ngoài allowlist")
            continue
        try:
            page = _fetch(url)
            extractor = _TextExtractor()
            extractor.feed(page)
            page_text = extractor.text()
            document_text = _extract_official_document_text(page, url)
            if document_text:
                page_text = page_text + "\n" + document_text
        except Exception as error:
            for provision in document["provisions"]:
                key = (
                    document["document_number"],
                    provision["article"],
                    provision["clause"],
                    provision.get("point", ""),
                )
                skipped.append(f"{key}: tải lỗi ({error})")
            time.sleep(0.5)
            continue
        if re.search(r"hết hiệu lực", page_text, re.IGNORECASE):
            status = "het_hieu_luc"
        elif re.search(r"(?:đang|còn) hiệu lực", page_text, re.IGNORECASE):
            status = "con_hieu_luc"
        elif re.search(r"chưa có hiệu lực", page_text, re.IGNORECASE):
            status = "chua_co_hieu_luc"
        else:
            status = "khong_ro"
        effective_match = re.search(r"Hiệu lực\s*:?\s*(\d{2}/\d{2}/\d{4})", page_text, re.I)
        effective_date = None
        if effective_match:
            day, month, year = effective_match.group(1).split("/")
            effective_date = f"{year}-{month}-{day}"
        amendment_match = re.search(
            r"(?:sửa đổi|được sửa đổi)(?:, bổ sung)?\s+(?:bởi|theo)\s+"
            r"(?:Luật|Nghị định|Thông tư)\s+số\s+[^.;,]+",
            page_text,
            re.IGNORECASE,
        )
        if status == "het_hieu_luc":
            expired.append(document["document_number"])
        for provision in document["provisions"]:
            key = (
                document["document_number"],
                provision["article"],
                provision["clause"],
                provision.get("point", ""),
            )
            content = extract_provision(
                page_text, provision["article"], provision["clause"], provision.get("point")
            )
            if not content or document["document_number"] not in page_text:
                skipped.append(f"{key}: không tách được duy nhất điều/khoản/điểm")
                continue
            record = {
                **provision,
                "document_number": document["document_number"],
                "noi_dung": content,
                "source_url": url,
                "source_domain": domain,
                "fetched_at": datetime.now(UTC).isoformat(),
                "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "effectiveness_status": status,
                "effective_date": effective_date,
                "amended_by": amendment_match.group(0) if amendment_match else None,
            }
            if status == "het_hieu_luc":
                record["noi_dung"] = content
            old_by_key[key] = record
            successes += 1
        time.sleep(0.5)
    ordered = [old_by_key[record.key] for record in existing.values() if record.key in old_by_key]
    ordered_keys = {
        tuple(
            str(row.get(field) or "").strip()
            for field in ("document_number", "article", "clause", "point")
        )
        for row in ordered
    }
    ordered.extend(old_by_key[key] for key in sorted(old_by_key) if key not in ordered_keys)
    target = DATA_DIR / "law_text.json"
    target.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "successful": successes,
        "skipped": skipped,
        "missing_urls": missing_urls,
        "expired_documents": expired,
    }


def main() -> None:
    print(json.dumps(synchronize(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
