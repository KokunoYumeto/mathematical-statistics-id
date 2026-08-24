#!/usr/bin/env python3
"""Bounded structural, mathematics, link, and accessibility QA for ordinals 23–29."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import posixpath
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import urldefrag, urlsplit

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority" / "upstream"
TARGET_ROOT = ROOT / "source" / "id-ID"
LEDGER = ROOT / "00_control" / "TRANSLATION_LEDGER.csv"
RECEIPT = ROOT / "00_control" / "HYPOTHESIS_BATCH_QA_2026-08-23.json"

PAGES = (
    {
        "ordinal": 23,
        "path": "random/hypothesis/index.html",
        "source_elements": 155,
        "target_core_elements": 155,
        "math_spans": 0,
        "raw_align": 0,
        "units": 0,
        "details": 0,
        "page_id": "o006.random.hypothesis.index.chapter",
    },
    {
        "ordinal": 24,
        "path": "random/hypothesis/Introduction.html",
        "source_elements": 219,
        "target_core_elements": 219,
        "math_spans": 213,
        "raw_align": 0,
        "units": 12,
        "details": 1,
        "page_id": "o006.random.hypothesis.introduction.page",
    },
    {
        "ordinal": 25,
        "path": "random/hypothesis/Normal.html",
        "source_elements": 463,
        "target_core_elements": 463,
        "math_spans": 459,
        "raw_align": 0,
        "units": 45,
        "details": 20,
        "page_id": "o006.random.hypothesis.normal.page",
    },
    {
        "ordinal": 26,
        "path": "random/hypothesis/Bernoulli.html",
        "source_elements": 267,
        "target_core_elements": 267,
        "math_spans": 233,
        "raw_align": 0,
        "units": 24,
        "details": 13,
        "page_id": "o006.random.hypothesis.bernoulli.page",
    },
    {
        "ordinal": 27,
        "path": "random/hypothesis/BivariateNormal.html",
        "source_elements": 255,
        "target_core_elements": 255,
        "math_spans": 300,
        "raw_align": 0,
        "units": 17,
        "details": 13,
        "page_id": "o006.random.hypothesis.bivariate-normal.page",
    },
    {
        "ordinal": 28,
        "path": "random/hypothesis/Likelihood.html",
        "source_elements": 212,
        "target_core_elements": 212,
        "math_spans": 252,
        "raw_align": 1,
        "units": 18,
        "details": 7,
        "page_id": "o006.random.hypothesis.likelihood.page",
    },
    {
        "ordinal": 29,
        "path": "random/hypothesis/ChiSquare.html",
        "source_elements": 417,
        "target_core_elements": 417,
        "math_spans": 433,
        "raw_align": 2,
        "units": 29,
        "details": 12,
        "page_id": "o006.random.hypothesis.chi-square.page",
    },
)

INBOUND_PAGES = (
    "random/sample/index.html",
    "random/sample/OrderStatistics.html",
    "random/sample/Normal.html",
    "random/point/index.html",
    "random/interval/index.html",
    "random/interval/Normal.html",
    "random/interval/Bernoulli.html",
    "random/interval/BivariateNormal.html",
    "random/interval/Bayes.html",
)

ENGLISH_DENY = (
    'lang="en"',
    "JavaScript:openAncillary",
    "Expand Details",
    "Contract Details",
    ">Details:<",
    ">Basic Theory<",
    ">Computational Exercises<",
    ">Data Analysis Exercises<",
    ">Hypothesis Testing<",
    ">Likelihood Ratio Tests<",
    ">Applications<",
)

MATH_RE = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")
RAW_ALIGN_RE = re.compile(r"\\begin\{align\*?\}.*?\\end\{align\*?\}", re.DOTALL)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes(path: Path) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"missing or unsafe regular file: {path}")
    return path.read_bytes()


def parse(data: bytes, label: str) -> BeautifulSoup:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"non-UTF-8 HTML {label}: {exc}") from exc
    return BeautifulSoup(text, "html.parser")


def ledger_rows() -> dict[int, dict[str, str]]:
    with LEDGER.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result: dict[int, dict[str, str]] = {}
    for row in rows:
        ordinal = int(row["ordinal"])
        if ordinal in result:
            raise RuntimeError(f"duplicate translation-ledger ordinal: {ordinal}")
        result[ordinal] = row
    if sorted(result) != list(range(1, 30)):
        raise RuntimeError(f"translation ledger is not the exact complete 1-29 sequence: {sorted(result)}")
    if any(result[index]["status"] != "complete" for index in result):
        raise RuntimeError("translation ledger contains a non-complete row")
    return result


def strip_notice(document: BeautifulSoup, label: str) -> None:
    notices = document.select("section.edition-notice[data-o006-edition-notice='v1']")
    if len(notices) != 1:
        raise RuntimeError(f"expected one standard edition notice in {label}, found {len(notices)}")
    notices[0].extract()


def normalized_local_target(source_page: str, href: str) -> tuple[str, str] | None:
    if not href or href.startswith("#"):
        return None
    parts = urlsplit(href)
    if parts.scheme or parts.netloc:
        return None
    path, fragment = urldefrag(href)
    if not path.endswith(".html"):
        return None
    normalized = posixpath.normpath(posixpath.join(posixpath.dirname(source_page), path))
    if normalized.startswith("../") or not normalized.startswith("random/"):
        raise RuntimeError(f"local HTML link escapes target root: {source_page} -> {href}")
    return normalized, fragment


def check_local_links(page_path: str, soup: BeautifulSoup) -> int:
    checked = 0
    for element in soup.find_all(href=True):
        href = str(element["href"])
        if href.startswith("#"):
            fragment = href[1:]
            if fragment and soup.find(id=fragment) is None:
                raise RuntimeError(f"missing same-page fragment: {page_path} -> {href}")
            checked += 1
            continue
        local = normalized_local_target(page_path, href)
        if local is None:
            continue
        target_path, fragment = local
        target_file = TARGET_ROOT / Path(PurePosixPath(target_path).as_posix())
        target_data = read_bytes(target_file)
        if fragment:
            target_soup = parse(target_data, target_path)
            if target_soup.find(id=fragment) is None:
                raise RuntimeError(f"missing cross-page fragment: {page_path} -> {href}")
        checked += 1
    return checked


def check_page(spec: dict[str, object], ledger: dict[int, dict[str, str]]) -> dict[str, object]:
    ordinal = int(spec["ordinal"])
    rel = str(spec["path"])
    authority_path = AUTHORITY / Path(PurePosixPath(rel).as_posix())
    target_path = TARGET_ROOT / Path(PurePosixPath(rel).as_posix())
    authority_data = read_bytes(authority_path)
    target_data = read_bytes(target_path)
    row = ledger[ordinal]
    if row["source_path"] != rel or row["target_path"] != f"source/id-ID/{rel}":
        raise RuntimeError(f"translation-ledger path mismatch at ordinal {ordinal}: {rel}")
    if int(row["source_bytes"]) != len(authority_data) or row["source_sha256"] != sha256(authority_data):
        raise RuntimeError(f"authority identity differs from ledger row {ordinal}: {rel}")
    if int(row["target_bytes"]) != len(target_data) or row["target_sha256"] != sha256(target_data):
        raise RuntimeError(f"target identity differs from ledger row {ordinal}: {rel}")

    source_soup = parse(authority_data, f"authority:{rel}")
    target_soup = parse(target_data, f"target:{rel}")
    strip_notice(target_soup, rel)
    source_tags = [node.name for node in source_soup.find_all(True)]
    target_tags = [node.name for node in target_soup.find_all(True)]
    if len(source_tags) != int(spec["source_elements"]):
        raise RuntimeError(f"authority element census changed for {rel}: {len(source_tags)}")
    if len(target_tags) != int(spec["target_core_elements"]):
        raise RuntimeError(f"target core element census changed for {rel}: {len(target_tags)}")
    delta = Counter(target_tags) - Counter(source_tags)
    reverse_delta = Counter(source_tags) - Counter(target_tags)
    if delta or reverse_delta or source_tags != target_tags:
        raise RuntimeError(
            f"undeclared topology change for {rel}: added={dict(delta)}, removed={dict(reverse_delta)}"
        )

    source_text = authority_data.decode("utf-8")
    target_text = target_data.decode("utf-8")
    source_math = MATH_RE.findall(source_text)
    target_math = MATH_RE.findall(target_text)
    if len(source_math) != int(spec["math_spans"]) or len(target_math) != len(source_math):
        raise RuntimeError(
            f"protected-math census changed for {rel}: {len(source_math)} -> {len(target_math)}"
        )
    source_align = RAW_ALIGN_RE.findall(source_text)
    target_align = RAW_ALIGN_RE.findall(target_text)
    if len(source_align) != int(spec["raw_align"]) or len(target_align) != len(source_align):
        raise RuntimeError(f"raw align-environment census changed for {rel}")

    units = target_soup.select("div.unit")
    details = target_soup.find_all("details")
    if len(units) != int(spec["units"]) or len(details) != int(spec["details"]):
        raise RuntimeError(f"unit/disclosure census changed for {rel}: {len(units)}/{len(details)}")
    if any(not unit.get("id") for unit in units):
        raise RuntimeError(f"anonymous structural unit remains in {rel}")
    summaries = target_soup.find_all("summary")
    if len(summaries) != len(details) or any(item.get_text(" ", strip=True) != "Rincian:" for item in summaries):
        raise RuntimeError(f"untranslated or missing disclosure summary in {rel}")
    ids = [str(node["id"]) for node in target_soup.find_all(id=True)]
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"duplicate target IDs in {rel}")
    if str(spec["page_id"]) not in ids:
        raise RuntimeError(f"missing stable page ID in {rel}: {spec['page_id']}")
    html = target_soup.find("html")
    if html is None or html.get("lang") != "id-ID":
        raise RuntimeError(f"wrong or missing locale in {rel}")
    if any(not image.get("alt") for image in target_soup.find_all("img")):
        raise RuntimeError(f"missing image alternative text in {rel}")
    for denied in ENGLISH_DENY:
        if denied in target_text:
            raise RuntimeError(f"unresolved reader-facing surface in {rel}: {denied}")
    if "https://www.randomservices.org/random/hypothesis/" in target_text:
        raise RuntimeError(f"completed hypothesis-chapter link still points upstream in {rel}")
    local_links = check_local_links(rel, target_soup)
    return {
        "ordinal": ordinal,
        "path": rel,
        "source_bytes": len(authority_data),
        "source_sha256": sha256(authority_data),
        "target_bytes": len(target_data),
        "target_sha256": sha256(target_data),
        "source_elements": len(source_tags),
        "target_core_elements": len(target_tags),
        "math_spans": len(target_math),
        "raw_align_environments": len(target_align),
        "units": len(units),
        "details": len(details),
        "ids": len(ids),
        "local_links_checked": local_links,
    }


def check_inbound_links() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for rel in INBOUND_PAGES:
        path = TARGET_ROOT / Path(PurePosixPath(rel).as_posix())
        data = read_bytes(path)
        text = data.decode("utf-8")
        if "https://www.randomservices.org/random/hypothesis/" in text:
            raise RuntimeError(f"translated inbound page retains upstream hypothesis link: {rel}")
        document = parse(data, f"inbound:{rel}")
        checked = check_local_links(rel, document)
        links = [
            str(node["href"])
            for node in document.find_all(href=True)
            if "../hypothesis/" in str(node["href"])
        ]
        if not links:
            raise RuntimeError(f"expected a hypothesis-chapter inbound link in {rel}")
        results.append(
            {
                "path": rel,
                "bytes": len(data),
                "sha256": sha256(data),
                "hypothesis_link_occurrences": len(links),
                "local_links_checked": checked,
            }
        )
    return results


def make_receipt() -> dict[str, object]:
    ledger = ledger_rows()
    pages = [check_page(spec, ledger) for spec in PAGES]
    inbound = check_inbound_links()
    return {
        "schema": "o006.random.hypothesis-batch-qa.v1",
        "date": "2026-08-23",
        "scope": "core ordinals 23-29 plus translated inbound-link integration; bounded source/target QA only; consolidated reader/backend/PDF/release gate follows",
        "status": "pass",
        "translation_ledger": {
            "path": "00_control/TRANSLATION_LEDGER.csv",
            "bytes": LEDGER.stat().st_size,
            "sha256": sha256(read_bytes(LEDGER)),
            "rows": len(ledger),
            "complete_sequence": "1-29",
        },
        "pages": pages,
        "inbound_pages": inbound,
        "totals": {
            "pages": len(pages),
            "source_elements": sum(int(item["source_elements"]) for item in pages),
            "target_core_elements": sum(int(item["target_core_elements"]) for item in pages),
            "math_spans": sum(int(item["math_spans"]) for item in pages),
            "raw_align_environments": sum(int(item["raw_align_environments"]) for item in pages),
            "units": sum(int(item["units"]) for item in pages),
            "details": sum(int(item["details"]) for item in pages),
            "local_links_checked": sum(int(item["local_links_checked"]) for item in pages),
            "inbound_local_links_checked": sum(int(item["local_links_checked"]) for item in inbound),
        },
    }


def canonical_bytes(value: dict[str, object]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    receipt = make_receipt()
    payload = canonical_bytes(receipt)
    if args.check_only:
        existing = read_bytes(RECEIPT)
        if existing != payload:
            raise RuntimeError("hypothesis-batch QA receipt is stale or nondeterministic")
        print(f"PASS {RECEIPT.relative_to(ROOT).as_posix()}: {len(payload)} bytes / {sha256(payload)}")
        return
    RECEIPT.write_bytes(payload)
    print(f"WROTE {RECEIPT.relative_to(ROOT).as_posix()}: {len(payload)} bytes / {sha256(payload)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
