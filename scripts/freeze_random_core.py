#!/usr/bin/env python3
"""Freeze the exact Random mathematical-statistics HTML source snapshot.

The upstream work has no public version tag or authoring repository.  Its
semantic HTML is therefore the editable source authority for this lane.  This
script deliberately freezes only the four mathematical-statistics chapters,
their author/license pages, the ancillary pages they directly invoke, and the
static files those pages directly require.  It does not crawl the wider site.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html.parser
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import deque
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority"
RAW = AUTHORITY / "upstream"
MANIFEST = AUTHORITY / "SOURCE_URL_MANIFEST.csv"
REFERENCES = AUTHORITY / "REFERENCE_URL_MANIFEST.csv"
RECEIPT = AUTHORITY / "SOURCE_FREEZE_RECEIPT.json"
ORIGIN = "https://www.randomservices.org/"
HOST = "www.randomservices.org"
USER_AGENT = "O006-id-ID-source-freezer/1.0 (+local scholarly edition)"

CORE_PATHS = (
    "random/sample/index.html",
    "random/sample/Introduction.html",
    "random/sample/Mean.html",
    "random/sample/LLN.html",
    "random/sample/CLT.html",
    "random/sample/Variance.html",
    "random/sample/OrderStatistics.html",
    "random/sample/Covariance.html",
    "random/sample/Normal.html",
    "random/point/index.html",
    "random/point/Estimators.html",
    "random/point/Moments.html",
    "random/point/Likelihood.html",
    "random/point/Bayes.html",
    "random/point/Unbiased.html",
    "random/point/Sufficient.html",
    "random/interval/index.html",
    "random/interval/Introduction.html",
    "random/interval/Normal.html",
    "random/interval/Bernoulli.html",
    "random/interval/BivariateNormal.html",
    "random/interval/Bayes.html",
    "random/hypothesis/index.html",
    "random/hypothesis/Introduction.html",
    "random/hypothesis/Normal.html",
    "random/hypothesis/Bernoulli.html",
    "random/hypothesis/BivariateNormal.html",
    "random/hypothesis/Likelihood.html",
    "random/hypothesis/ChiSquare.html",
)

AUTHORITY_PATHS = (
    "random/index.html",
    "random/Introduction.html",
    "random/Credits.html",
)

ANCILLARY_PREFIXES = (
    "/random/apps/",
    "/random/data/",
    "/random/biographies/",
)

TEXT_ASSET_SUFFIXES = {".css", ".js", ".json", ".txt", ".csv", ".tsv"}
DOWNLOADABLE_SUFFIXES = TEXT_ASSET_SUFFIXES | {
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".wav",
    ".mp3",
    ".ogg",
}


class DependencyParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.assets: list[str] = []
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value for key, value in attrs if value is not None}
        if tag in {"script", "img", "source", "audio", "video", "iframe"}:
            if "src" in data:
                self.assets.append(data["src"])
        elif tag == "object" and "data" in data:
            self.assets.append(data["data"])
        elif tag == "link" and "href" in data:
            rel = set(data.get("rel", "").lower().split())
            if rel & {"stylesheet", "icon", "preload", "modulepreload"}:
                self.assets.append(data["href"])
        elif tag == "a" and "href" in data:
            href = data["href"]
            parsed = urllib.parse.urlsplit(href)
            if PurePosixPath(parsed.path).suffix.lower() in DOWNLOADABLE_SUFFIXES:
                self.assets.append(href)
            else:
                self.references.append(href)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_url(value: str, base: str) -> str | None:
    value = value.strip()
    if not value or value.startswith(("#", "mailto:", "data:")):
        return None
    if value.lower().startswith("javascript:"):
        return None
    url = urllib.parse.urljoin(base, value)
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    clean = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))
    return clean


def local_path_for(url: str) -> Path:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != HOST or parsed.port not in (None, 443):
        raise RuntimeError(f"refusing non-authority URL: {url}")
    if parsed.query:
        raise RuntimeError(f"refusing query-bearing authority URL: {url}")
    posix = PurePosixPath(urllib.parse.unquote(parsed.path).lstrip("/"))
    if not posix.parts or any(part in {"", ".", ".."} for part in posix.parts):
        raise RuntimeError(f"unsafe authority path: {url}")
    if not (str(posix).startswith("random/") or str(posix) == "MathJax/tex-svg.js"):
        raise RuntimeError(f"authority URL is outside bounded closure: {url}")
    return Path(*posix.parts)


def fetch(url: str) -> tuple[bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            final_url = response.geturl()
            parsed = urllib.parse.urlsplit(final_url)
            if parsed.scheme != "https" or parsed.hostname != HOST or parsed.port not in (None, 443):
                raise RuntimeError(f"unsafe redirect for {url}: {final_url}")
            data = response.read()
            status = getattr(response, "status", None)
            if status != 200:
                raise RuntimeError(f"unexpected HTTP {status} for {url}")
            headers = {
                "content_type": response.headers.get("Content-Type", ""),
                "last_modified": response.headers.get("Last-Modified", ""),
                "etag": response.headers.get("ETag", ""),
            }
    except Exception as exc:
        raise RuntimeError(f"fetch failed for {url}: {exc}") from exc
    if not data:
        raise RuntimeError(f"empty response: {url}")
    return data, headers


def html_dependencies(data: bytes, url: str) -> tuple[set[str], set[str], set[str]]:
    text = data.decode("utf-8", errors="strict")
    parser = DependencyParser()
    parser.feed(text)
    assets: set[str] = set()
    references: set[str] = set()
    ancillaries: set[str] = set()
    for value in parser.assets:
        dep = canonical_url(value, url)
        if dep:
            assets.add(dep)
    for value in parser.references:
        dep = canonical_url(value, url)
        if dep:
            references.add(dep)
    for match in re.finditer(r"openAncillary\('([^']+)'\)", text):
        dep = canonical_url(match.group(1), url)
        if dep and urllib.parse.urlsplit(dep).path.startswith(ANCILLARY_PREFIXES):
            ancillaries.add(dep)
    return assets, references, ancillaries


def text_asset_dependencies(data: bytes, url: str) -> set[str]:
    text = data.decode("utf-8", errors="strict")
    found: set[str] = set()
    patterns = (
        r"url\(\s*['\"]?([^'\")]+)",
        r"(?:import|from)\s*\(?\s*['\"]([^'\"]+)",
        r"['\"]([^'\"]+\.(?:css|js|json|txt|csv|tsv|svg|png|jpe?g|gif|webp|wav|mp3|ogg))['\"]",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            dep = canonical_url(match.group(1), url)
            if dep:
                parsed = urllib.parse.urlsplit(dep)
                if parsed.hostname == HOST and (
                    parsed.path.startswith("/random/") or parsed.path == "/MathJax/tex-svg.js"
                ):
                    found.add(dep)
    return found


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> bytes:
    import io

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode("utf-8")
    path.write_bytes(data)
    return data


def freeze() -> None:
    if RAW.exists() or MANIFEST.exists() or RECEIPT.exists():
        raise RuntimeError("immutable authority already exists; use --check-only")
    RAW.mkdir(parents=True, exist_ok=False)

    rows_by_url: dict[str, dict[str, object]] = {}
    reference_rows: dict[tuple[str, str], dict[str, object]] = {}
    failed_urls: dict[str, str] = {}
    queue: deque[tuple[str, str, bool]] = deque()
    for path in CORE_PATHS:
        queue.append((urllib.parse.urljoin(ORIGIN, path), "core", True))
    for path in AUTHORITY_PATHS:
        queue.append((urllib.parse.urljoin(ORIGIN, path), "authority", True))

    seen: set[str] = set()
    while queue:
        url, role, parse_html = queue.popleft()
        if url in seen:
            existing = rows_by_url.get(url)
            if existing and existing["role"] == "asset" and role != "asset":
                existing["role"] = role
            continue
        seen.add(url)
        rel = local_path_for(url)
        try:
            data, headers = fetch(url)
        except Exception as exc:
            if role in {"core", "authority"}:
                raise
            failed_urls[url] = str(exc)
            continue
        destination = RAW / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        rows_by_url[url] = {
            "relative_path": rel.as_posix(),
            "role": role,
            "url": url,
            "bytes": len(data),
            "sha256": sha256(data),
            **headers,
        }

        suffix = rel.suffix.lower()
        content_type = headers["content_type"].lower()
        if parse_html or suffix in {".html", ".htm"} or "text/html" in content_type:
            assets, references, ancillaries = html_dependencies(data, url)
            for dep in sorted(ancillaries):
                queue.append((dep, "ancillary", True))
                reference_rows[(url, dep)] = {
                    "source_url": url,
                    "target_url": dep,
                    "kind": "ancillary",
                    "frozen": "pending",
                    "note": "",
                }
            for dep in sorted(assets):
                parsed = urllib.parse.urlsplit(dep)
                if parsed.hostname == HOST and (
                    parsed.path.startswith("/random/") or parsed.path == "/MathJax/tex-svg.js"
                ):
                    if PurePosixPath(parsed.path).suffix.lower() not in {".html", ".htm"}:
                        queue.append((dep, "asset", False))
                reference_rows[(url, dep)] = {
                    "source_url": url,
                    "target_url": dep,
                    "kind": "asset",
                    "frozen": "pending",
                    "note": "",
                }
            for dep in sorted(references):
                reference_rows[(url, dep)] = {
                    "source_url": url,
                    "target_url": dep,
                    "kind": "reference",
                    "frozen": "false",
                    "note": "outside the bounded core/ancillary freeze",
                }
        elif suffix in TEXT_ASSET_SUFFIXES:
            for dep in sorted(text_asset_dependencies(data, url)):
                queue.append((dep, "asset", False))
                reference_rows[(url, dep)] = {
                    "source_url": url,
                    "target_url": dep,
                    "kind": "asset",
                    "frozen": "pending",
                    "note": "",
                }

    rows = sorted(rows_by_url.values(), key=lambda row: str(row["relative_path"]))
    manifest_data = write_csv(
        MANIFEST,
        ["relative_path", "role", "url", "bytes", "sha256", "content_type", "last_modified", "etag"],
        rows,
    )
    for row in reference_rows.values():
        if row["kind"] in {"asset", "ancillary"}:
            target = str(row["target_url"])
            row["frozen"] = "true" if target in rows_by_url else "false"
            if target in failed_urls:
                row["note"] = failed_urls[target]
    reference_data = write_csv(
        REFERENCES,
        ["source_url", "target_url", "kind", "frozen", "note"],
        sorted(reference_rows.values(), key=lambda row: (str(row["source_url"]), str(row["target_url"]))),
    )
    core_rows = [row for row in rows if row["role"] == "core"]
    if len(core_rows) != len(CORE_PATHS):
        raise RuntimeError(f"expected {len(CORE_PATHS)} core files, found {len(core_rows)}")
    receipt = {
        "schema": "o006.random.source-freeze.v1",
        "authority": "Kyle Siegrist, Random: Probability, Mathematical Statistics, and Stochastic Processes",
        "authority_home": urllib.parse.urljoin(ORIGIN, "random/"),
        "license": "CC BY 2.0",
        "license_url": "https://creativecommons.org/licenses/by/2.0/",
        "retrieved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "edition_basis": "unversioned live semantic HTML; exact authority is this URL/byte/header manifest",
        "core_paths": list(CORE_PATHS),
        "core_files": len(core_rows),
        "core_bytes": sum(int(row["bytes"]) for row in core_rows),
        "frozen_files": len(rows),
        "frozen_bytes": sum(int(row["bytes"]) for row in rows),
        "source_manifest_bytes": len(manifest_data),
        "source_manifest_sha256": sha256(manifest_data),
        "reference_manifest_bytes": len(reference_data),
        "reference_manifest_sha256": sha256(reference_data),
        "user_agent": USER_AGENT,
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


def check() -> None:
    if not MANIFEST.is_file() or not RECEIPT.is_file() or not RAW.is_dir():
        raise RuntimeError("authority freeze is incomplete")
    with MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError("empty source manifest")
    expected_paths: set[str] = set()
    core_paths: set[str] = set()
    for row in rows:
        rel = row["relative_path"]
        if rel in expected_paths:
            raise RuntimeError(f"duplicate manifest path: {rel}")
        expected_paths.add(rel)
        path = RAW / Path(*PurePosixPath(rel).parts)
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"missing/nonregular authority file: {rel}")
        data = path.read_bytes()
        if len(data) != int(row["bytes"]) or sha256(data) != row["sha256"]:
            raise RuntimeError(f"authority byte mismatch: {rel}")
        if row["role"] == "core":
            core_paths.add(rel)
    actual_paths = {
        path.relative_to(RAW).as_posix()
        for path in RAW.rglob("*")
        if path.is_file()
    }
    if actual_paths != expected_paths:
        raise RuntimeError(
            f"authority file-set mismatch: missing={sorted(expected_paths-actual_paths)!r}, "
            f"extra={sorted(actual_paths-expected_paths)!r}"
        )
    if core_paths != set(CORE_PATHS):
        raise RuntimeError("core path set differs from the frozen 29-page specification")
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    manifest_data = MANIFEST.read_bytes()
    if len(manifest_data) != receipt["source_manifest_bytes"] or sha256(manifest_data) != receipt["source_manifest_sha256"]:
        raise RuntimeError("source manifest does not match receipt")
    reference_data = REFERENCES.read_bytes()
    if len(reference_data) != receipt["reference_manifest_bytes"] or sha256(reference_data) != receipt["reference_manifest_sha256"]:
        raise RuntimeError("reference manifest does not match receipt")
    if receipt["frozen_files"] != len(rows) or receipt["frozen_bytes"] != sum(int(row["bytes"]) for row in rows):
        raise RuntimeError("receipt closure totals do not match manifest")
    print(
        f"PASS: {len(core_paths)} core files; {len(rows)} total frozen files; "
        f"{sum(int(row['bytes']) for row in rows)} bytes; manifest {sha256(manifest_data)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true")
    group.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.freeze:
            freeze()
        else:
            check()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
