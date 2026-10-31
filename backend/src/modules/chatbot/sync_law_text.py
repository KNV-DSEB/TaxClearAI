import hashlib
import json
import re
import shutil
import ssl
import subprocess
import time
import urllib.error
import urllib.request
import urllib.robotparser
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urljoin, urlparse
from xml.etree import ElementTree

import truststore

from src.core.config import get_settings
from src.modules.chatbot.law_source import LawTextKey, read_law_text_records

DATA_DIR = Path(__file__).parent / "data"
USER_AGENT = "TaxClearAI-LawSync/1.0 (official legal text synchronization)"
_TLS_CONTEXT = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


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
    except urllib.error.HTTPError as error:
        if error.code == 404:
            parser.parse([])
        elif error.code == 403:
            raise ValueError("robots.txt denies access") from error
        else:
            raise ValueError(f"robots.txt unavailable (HTTP {error.code})") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise ValueError(f"robots.txt unavailable: {error}") from error
    if not parser.can_fetch(USER_AGENT, url):
        raise ValueError("robots.txt không cho phép truy cập")
    return _read_url(url, timeout)


def _read_url(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=timeout, context=_TLS_CONTEXT) as response:
                return cast(bytes, response.read())
        except (urllib.error.URLError, TimeoutError):
            if attempt == 1:
                raise
            time.sleep(0.25)
    raise RuntimeError("request retry limit exceeded")


def _ocr_pdf(payload: bytes) -> str | None:
    settings = get_settings()
    if not settings.law_ocr_enabled:
        return None
    configured_executable = Path(settings.law_ocr_tesseract_cmd)
    executable = (
        str(configured_executable)
        if configured_executable.is_file()
        else shutil.which(settings.law_ocr_tesseract_cmd)
    )
    if not executable:
        raise ValueError("không tìm thấy Tesseract OCR")
    import pymupdf as fitz

    tessdata_dir = settings.law_ocr_tessdata_dir
    config = str(Path(executable).parent / "tessdata" / "configs" / "tsv")
    if not Path(config).is_file():
        raise ValueError("không tìm thấy cấu hình TSV của Tesseract")

    def ocr_page(page_number: int) -> tuple[str, list[float]]:
        with fitz.open(stream=payload, filetype="pdf") as pdf:  # type: ignore[no-untyped-call]
            page = pdf.load_page(page_number)
            image = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),  # type: ignore[no-untyped-call]
                alpha=False,
            ).tobytes("png")
        command = [
            executable,
            "stdin",
            "stdout",
            "-l",
            settings.law_ocr_language,
            "--psm",
            "6",
        ]
        if tessdata_dir:
            command.extend(["--tessdata-dir", tessdata_dir])
        command.append(config)
        result = subprocess.run(
            command,
            input=image,
            capture_output=True,
            check=True,
            timeout=60,
        )
        lines: dict[tuple[str, str, str], list[str]] = {}
        scores: list[float] = []
        tsv = result.stdout.decode("utf-8", errors="replace").splitlines()
        for row in tsv[1:]:
            fields = row.split("\t", 11)
            if len(fields) != 12 or not fields[11].strip():
                continue
            key = (fields[2], fields[3], fields[4])
            lines.setdefault(key, []).append(fields[11].strip())
            try:
                confidence = float(fields[10])
            except ValueError:
                continue
            if confidence >= 0:
                scores.append(confidence)
        return "\n".join(" ".join(words) for words in lines.values()), scores

    pages: list[str] = []
    scores: list[float] = []
    with fitz.open(stream=payload, filetype="pdf") as pdf:  # type: ignore[no-untyped-call]
        page_count = len(pdf)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for text, confidence_scores in pool.map(ocr_page, range(page_count)):
            pages.append(text)
            scores.extend(confidence_scores)
    if not scores or sum(scores) / len(scores) < settings.law_ocr_min_confidence:
        raise ValueError("độ tin cậy OCR thấp hơn ngưỡng cấu hình")
    return _repair_vietnamese_ocr_errors(_repair_ocr_form_codes("\n\n".join(pages).strip())) or None


def _repair_ocr_form_codes(text: str) -> str:
    text = re.sub(r"(?i)t(?:\u00ec|i)\s+b-\u0110kt", "TB-\u0110KT", text)
    return re.sub(r"(?i)\u0110\u00d0kt", "\u0110KT", text)


def _repair_vietnamese_ocr_errors(text: str) -> str:
    corrections = {
        "h\u1ed7 s\u01a1": "h\u1ed3 s\u01a1",
        "h\u00f4 s\u01a1": "h\u1ed3 s\u01a1",
        "\u0111\u1ec1n c\u01a1 quan": "\u0111\u1ebfn c\u01a1 quan",
        "tr\u1ef1c ti\u1ec7p": "tr\u1ef1c ti\u1ebfp",
        "ng\u01b0\u1eddi n\u1ed9p thu\u00ea": "ng\u01b0\u1eddi n\u1ed9p thu\u1ebf",
        "c\u01a1 quan thu\u00ea": "c\u01a1 quan thu\u1ebf",
        "ngh\u0129a v\u1ee5 thu\u00ea": "ngh\u0129a v\u1ee5 thu\u1ebf",
        "m\u00e3 s\u1ed1 thu\u00ea": "m\u00e3 s\u1ed1 thu\u1ebf",
        "m\u00e3 s\u00f4 thu\u00ea": "m\u00e3 s\u1ed1 thu\u1ebf",
        "n\u1ed9p thu\u00ea": "n\u1ed9p thu\u1ebf",
        "v\u1ec1 thu\u00ea": "v\u1ec1 thu\u1ebf",
        "qu\u1ea3n l\u00fd thu\u00ea": "qu\u1ea3n l\u00fd thu\u1ebf",
        "\u0111\u0103ng k\u00fd thu\u00ea": "\u0111\u0103ng k\u00fd thu\u1ebf",
        "\u0111\u00ea th\u1ef1c hi\u1ec7n": "\u0111\u1ec3 th\u1ef1c hi\u1ec7n",
        "\u0111\u00ea n\u1ed9p": "\u0111\u1ec3 n\u1ed9p",
        "\u0111i\u00eam": "\u0111i\u1ec3m",
        "\u0110i\u00eam": "\u0110i\u1ec3m",
        "\u0110i\u00eau": "\u0110i\u1ec1u",
        "\u0111i\u00eau": "\u0111i\u1ec1u",
        "ch\u00e2m d\u1ee9t": "ch\u1ea5m d\u1ee9t",
        "m\u00e3 s\u00f4": "m\u00e3 s\u1ed1",
        "m\u1eabu s\u00f4": "m\u1eabu s\u1ed1",
        "cam k\u00eat": "cam k\u1ebft",
        "chuy\u00ean \u0111\u1ed5i": "chuy\u1ec3n \u0111\u1ed5i",
        "k\u00ea th\u1eeba": "k\u1ebf th\u1eeba",
        "\u0111\u00f4i v\u1edbi": "\u0111\u1ed1i v\u1edbi",
        "QHI5": "QH15",
        "~ Ho\u00e0n th\u00e0nh": "- Ho\u00e0n th\u00e0nh",
        "kho\u1ea3n I ": "kho\u1ea3n 1 ",
        "Lu\u1eadt s\u00f4": "Lu\u1eadt s\u1ed1",
        "Ngh\u1ecb \u0111\u1ecbnh s\u00f4": "Ngh\u1ecb \u0111\u1ecbnh s\u1ed1",
        "s\u1ed1 ti\u00ean thu\u1ebf": "s\u1ed1 ti\u1ec1n thu\u1ebf",
        "m\u00e3 s\u00f4 thu\u1ebf": "m\u00e3 s\u1ed1 thu\u1ebf",
        "chuy\u00ean tr\u1ea1ng th\u00e1i": "chuy\u1ec3n tr\u1ea1ng th\u00e1i",
        "H\u1ec7 th\u00f4ng": "H\u1ec7 th\u1ed1ng",
        "k\u1ebf t\u1eeb ng\u00e0y": "k\u1ec3 t\u1eeb ng\u00e0y",
        "ch\u1eadm nh\u00e2t": "ch\u1eadm nh\u1ea5t",
        "\u0111\u00e2u gi\u1edd": "\u0111\u1ea7u gi\u1edd",
        "\u0111\u1ecba \u0111i\u00eam": "\u0111\u1ecba \u0111i\u1ec3m",
        "th\u00f4ng t\u1ec9n": "th\u00f4ng tin",
    }
    for incorrect, corrected in corrections.items():
        pattern = re.escape(incorrect).replace(r"\ ", r"\s+")
        text = re.sub(pattern, corrected, text)
    text = re.sub(r"(?i)/\u00d0kt", "/\u0110KT", text)
    return text


def _extract_official_document_text(
    page: str, source_url: str, failures: list[str] | None = None
) -> str | None:
    link_parser = _LinkExtractor()
    link_parser.feed(page)
    files: dict[str, tuple[str, str]] = {}
    for link in link_parser.links:
        parsed_link = urlparse(link)
        file_name = parse_qs(parsed_link.query).get("file_name", [""])[0]
        extension = Path(file_name or parsed_link.path).suffix.lower()
        if extension not in {".docx", ".pdf"}:
            continue
        key = Path(file_name or parsed_link.path).stem.casefold()
        current = files.get(key)
        if current is None or extension == ".pdf":
            files[key] = (urljoin(source_url, link), extension)
    document_urls = [url for url, _ in files.values()]
    allowed_domains = get_settings().allowed_law_domains
    extracted_documents: list[str] = []
    for document_url in document_urls:
        if (urlparse(document_url).hostname or "").lower() not in allowed_domains:
            continue
        try:
            payload = _fetch_bytes(document_url)
            if payload.startswith(b"%PDF-") or (
                not payload.startswith(b"PK\x03\x04")
                and (
                    urlparse(document_url).path.lower().endswith(".pdf")
                    or parse_qs(urlparse(document_url).query)
                    .get("file_name", [""])[0]
                    .lower()
                    .endswith(".pdf")
                )
            ):
                from pypdf import PdfReader

                pdf = PdfReader(BytesIO(payload))
                pdf_paragraphs = [
                    text
                    for page_item in pdf.pages
                    if (text := page_item.extract_text()) and text.strip()
                ]
                if pdf_paragraphs:
                    extracted_documents.append("\n".join(pdf_paragraphs))
                else:
                    try:
                        ocr_text = _ocr_pdf(payload)
                    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
                        if failures is not None:
                            failures.append(f"{document_url} (OCR thất bại: {error})")
                    else:
                        if ocr_text:
                            extracted_documents.append(ocr_text)
                        elif failures is not None:
                            failures.append(
                                f"{document_url} (PDF không có lớp văn bản có thể trích xuất)"
                            )
                continue
            with zipfile.ZipFile(BytesIO(payload)) as archive:
                xml = ElementTree.fromstring(archive.read("word/document.xml"))
        except (
            OSError,
            ValueError,
            KeyError,
            zipfile.BadZipFile,
            urllib.error.URLError,
        ) as error:
            if failures is not None:
                failures.append(f"{document_url} ({type(error).__name__}: {error})")
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
            extracted_documents.append("\n".join(paragraphs))
    return "\n".join(extracted_documents) if extracted_documents else None


def extract_provision(text: str, article: str, clause: str, point: str | None) -> str | None:
    article_numbers = re.findall(r"\d+", article)
    clause_numbers = re.findall(r"(?i)kho\u1ea3n\s+(\d+)", clause)
    point_numbers = re.findall(r"(?i)\u0111i\u1ec3m\s+([a-z\u0111](?:\.\d+)?)", point or "")
    if len(article_numbers) != 1 or len(point_numbers) > 1:
        return None
    if not clause_numbers:
        descriptor = clause.casefold()
        if point is not None or not descriptor.startswith(
            "c\u00e1c kho\u1ea3n s\u1eeda \u0111\u1ed5i"
        ):
            return None
        article_re = re.compile(rf"(?mi)^[ \t]*\u0110i\u1ec1u\s+{article_numbers[0]}\s*[.)]")
        matches = list(article_re.finditer(text))
        if len(matches) != 1:
            return None
        next_article = re.search(
            r"(?mi)^[ \t]*\u0110i\u1ec1u\s+\d+\s*[.)]",
            text[matches[0].end() :],
        )
        end = matches[0].end() + next_article.start() if next_article else len(text)
        body_start = text.find("\n", matches[0].end())
        if body_start < 0 or body_start >= end:
            body_start = matches[0].end()
        return text[body_start:end].strip() or None
    if len(clause_numbers) != 1:
        return None
    article_re = re.compile(rf"(?mi)^[ \t]*\u0110i\u1ec1u\s+{article_numbers[0]}\s*[.)]")
    matches = list(article_re.finditer(text))
    if not matches:
        article_re = re.compile(rf"\b\u0110i\u1ec1u\s+{article_numbers[0]}\s*[.)]", re.IGNORECASE)
        matches = list(article_re.finditer(text))
    if len(matches) != 1:
        return None
    start = matches[0].start()
    next_article = re.search(
        r"(?mi)^[ \t]*\u0110i\u1ec1u\s+\d+\s*[.)]",
        text[matches[0].end() :],
    )
    if next_article is None:
        next_article = re.search(
            r"\b\u0110i\u1ec1u\s+\d+\s*[.)]",
            text[matches[0].end() :],
            re.IGNORECASE,
        )
    section = (
        text[start : matches[0].end() + next_article.start()] if next_article else text[start:]
    )
    article_end = matches[0].end() - start
    clause_text = section[article_end:]
    clause_re = re.compile(rf"(?m)^[ \t]*{clause_numbers[0]}\s*[.)]\s")
    clauses = list(clause_re.finditer(clause_text))
    if not clauses:
        clause_re = re.compile(rf"(?<![\w.]){clause_numbers[0]}\s*[.)]\s")
        clauses = list(clause_re.finditer(clause_text))
    if len(clauses) != 1:
        return None
    clause_start = clauses[0].start()
    next_clause = re.search(r"(?m)^[ \t]*\d+\s*[.)]\s", clause_text[clauses[0].end() :])
    if next_clause is None:
        next_clause = re.search(r"(?<![\w.])\d+\s*[.)]\s", clause_text[clauses[0].end() :])
    end = clauses[0].end() + next_clause.start() if next_clause else len(clause_text)
    result = clause_text[clause_start:end].strip()
    if point:
        point_label = point_numbers[0]
        point_re = re.compile(rf"(?mi)^[ \t]*{re.escape(point_label)}\s*[.)]\s", re.IGNORECASE)
        point_matches = list(point_re.finditer(result))
        if not point_matches:
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
        result = result[point_start:point_end].strip()
    return result or None


def _expand_provision(provision: dict[str, str]) -> list[dict[str, str]]:
    clause = provision.get("clause", "")
    numbers = [int(number) for number in re.findall(r"(?i)kho\u1ea3n\s+(\d+)", clause)]
    if len(numbers) == 2 and re.search(r"(?i)\u0111\u1ebfn", clause):
        clauses = list(range(numbers[0], numbers[1] + 1))
    elif numbers:
        clauses = list(dict.fromkeys(numbers))
    else:
        return [provision]

    point_text = provision.get("point", "")
    points = re.findall(r"(?i)(?:\u0111i\u1ec3m\s+)?([a-z\u0111](?:\.\d+)?)", point_text)
    if not points:
        points = [""]
    return [
        {
            **provision,
            "clause": f"Kho\u1ea3n {clause_number}",
            **({"point": f"\u0110i\u1ec3m {point}"} if point else {"point": ""}),
        }
        for clause_number in clauses
        for point in points
    ]


def synchronize() -> dict[str, object]:
    settings = get_settings()
    source_manifest = json.loads((DATA_DIR / "law_sources.json").read_text(encoding="utf-8"))
    manifest_keys: set[LawTextKey] = set()
    for document in source_manifest:
        for provision_spec in document["provisions"]:
            for provision in _expand_provision(provision_spec):
                manifest_keys.add(
                    (
                        document["document_number"],
                        provision["article"],
                        provision["clause"],
                        provision.get("point", ""),
                    )
                )
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
            attachment_failures: list[str] = []
            document_text = _extract_official_document_text(page, url, failures=attachment_failures)
            # The attachment is the canonical full text; the page is metadata only.
            full_text = document_text or page_text
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
        if re.search(r"h\u1ebft hi\u1ec7u l\u1ef1c", page_text, re.IGNORECASE):
            status = "het_hieu_luc"
        elif re.search(r"ch\u01b0a c\u00f3 hi\u1ec7u l\u1ef1c", page_text, re.IGNORECASE):
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
        for provision_spec in document["provisions"]:
            expanded_provisions = _expand_provision(provision_spec)
            if len(expanded_provisions) > 1:
                parent_key = (
                    document["document_number"],
                    provision_spec["article"],
                    provision_spec["clause"],
                    provision_spec.get("point", ""),
                )
                old_by_key.pop(parent_key, None)
            for provision in expanded_provisions:
                key = (
                    document["document_number"],
                    provision["article"],
                    provision["clause"],
                    provision.get("point", ""),
                )
                content = extract_provision(
                    full_text, provision["article"], provision["clause"], provision.get("point")
                )
                if not content or document["document_number"] not in full_text:
                    reason = (
                        "kh\u00f4ng t\u00e1ch \u0111\u01b0\u1ee3c duy nh\u1ea5t "
                        "\u0111i\u1ec1u/kho\u1ea3n/\u0111i\u1ec3m"
                    )
                    if attachment_failures and not document_text:
                        reason = (
                            "kh\u00f4ng l\u1ea5y \u0111\u01b0\u1ee3c to\u00e0n v\u0103n "
                            "\u0111\u00ednh k\u00e8m: " + attachment_failures[0]
                        )
                    skipped.append(f"{key}: {reason}")
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
    for key in list(old_by_key):
        document_number, article, clause, point = key
        expanded = _expand_provision({"article": article, "clause": clause, "point": point})
        if len(expanded) > 1:
            child_keys = {
                (
                    document_number,
                    item["article"],
                    item["clause"],
                    item.get("point", ""),
                )
                for item in expanded
            }
            if child_keys & manifest_keys:
                old_by_key.pop(key, None)
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
