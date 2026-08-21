#!/usr/bin/env python3
"""Exact structural, mathematical, link, locale, and privacy QA for unit 1."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True
import build_first_unit as build_pipeline  # noqa: E402
from bs4 import BeautifulSoup, Comment  # noqa: E402
from bs4.element import Tag  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority" / "upstream"
TARGET = ROOT / "source" / "id-ID"
READER = ROOT / "build" / "html-id"
QA_RECEIPT = ROOT / "build" / "FIRST_UNIT_QA_RECEIPT.json"

PAIRS = (
    PurePosixPath("random/sample/index.html"),
    PurePosixPath("random/sample/Introduction.html"),
    PurePosixPath("random/sample/Mean.html"),
)

# This is an exact page/original-href allowlist. There is deliberately no URL
# rewriting rule, suffix heuristic, or substring replacement in the verifier.
HREF_DELTA_ALLOWLIST: dict[PurePosixPath, dict[str, str]] = {
    PurePosixPath("random/sample/index.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../special/index.html": "https://www.randomservices.org/random/special/index.html",
        "../point/index.html": "https://www.randomservices.org/random/point/index.html",
        "../foundations/index.html": "https://www.randomservices.org/random/foundations/index.html",
        "../prob/index.html": "https://www.randomservices.org/random/prob/index.html",
        "../dist/index.html": "https://www.randomservices.org/random/dist/index.html",
        "../expect/index.html": "https://www.randomservices.org/random/expect/index.html",
        "../interval/index.html": "https://www.randomservices.org/random/interval/index.html",
        "../hypothesis/index.html": "https://www.randomservices.org/random/hypothesis/index.html",
        "../buffon/index.html": "https://www.randomservices.org/random/buffon/index.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "../urn/index.html": "https://www.randomservices.org/random/urn/index.html",
        "../games/index.html": "https://www.randomservices.org/random/games/index.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "../renewal/index.html": "https://www.randomservices.org/random/renewal/index.html",
        "../markov/index.html": "https://www.randomservices.org/random/markov/index.html",
        "../martingales/index.html": "https://www.randomservices.org/random/martingales/index.html",
        "../brown/index.html": "https://www.randomservices.org/random/brown/index.html",
        "LLN.html": "https://www.randomservices.org/random/sample/LLN.html",
        "CLT.html": "https://www.randomservices.org/random/sample/CLT.html",
        "Variance.html": "https://www.randomservices.org/random/sample/Variance.html",
        "OrderStatistics.html": "https://www.randomservices.org/random/sample/OrderStatistics.html",
        "Covariance.html": "https://www.randomservices.org/random/sample/Covariance.html",
        "Normal.html": "https://www.randomservices.org/random/sample/Normal.html",
        "JavaScript:openAncillary('../apps/Histogram.html')": "https://www.randomservices.org/random/apps/Histogram.html",
        "JavaScript:openAncillary('../apps/ErrorFunction.html')": "https://www.randomservices.org/random/apps/ErrorFunction.html",
        "JavaScript:openAncillary('../apps/Dice.html')": "https://www.randomservices.org/random/apps/Dice.html",
        "JavaScript:openAncillary('../apps/SampleMean.html')": "https://www.randomservices.org/random/apps/SampleMean.html",
        "JavaScript:openAncillary('../apps/OrderStatistic.html')": "https://www.randomservices.org/random/apps/OrderStatistic.html",
        "JavaScript:openAncillary('../apps/ProbabilityPlot.html')": "https://www.randomservices.org/random/apps/ProbabilityPlot.html",
        "JavaScript:openAncillary('../apps/Scatterplot.html')": "https://www.randomservices.org/random/apps/Scatterplot.html",
        "JavaScript:openAncillary('../biographies/Clemens.html')": "https://www.randomservices.org/random/biographies/Clemens.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
        "http://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt": "https://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt",
        "http://www.google.com/search?q=Statistical+Inference+Casella+Berger": "https://www.google.com/search?q=Statistical+Inference+Casella+Berger",
        "http://www.google.com/search?q=Statistics,Freedman,Pisani,Purves": "https://www.google.com/search?q=Statistics,Freedman,Pisani,Purves",
        "http://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx": "https://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx",
        "http://www.google.com/search?q=Elementary+Statistics,Triola": "https://www.google.com/search?q=Elementary+Statistics,Triola",
        "http://www.google.com/search?q=Introductory+Statistics,Weiss": "https://www.google.com/search?q=Introductory+Statistics,Weiss",
        "http://mathworld.wolfram.com/topics/ProbabilityandStatistics.html": "https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
    },
    PurePosixPath("random/sample/Introduction.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "LLN.html": "https://www.randomservices.org/random/sample/LLN.html",
        "CLT.html": "https://www.randomservices.org/random/sample/CLT.html",
        "Variance.html": "https://www.randomservices.org/random/sample/Variance.html",
        "OrderStatistics.html": "https://www.randomservices.org/random/sample/OrderStatistics.html",
        "Covariance.html": "https://www.randomservices.org/random/sample/Covariance.html",
        "Normal.html": "https://www.randomservices.org/random/sample/Normal.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../data/MM.html')": "https://www.randomservices.org/random/data/MM.html",
        "JavaScript:openAncillary('../data/Cicada.html')": "https://www.randomservices.org/random/data/Cicada.html",
        "JavaScript:openAncillary('../data/Fisher.html')": "https://www.randomservices.org/random/data/Iris.html",
        "JavaScript:openAncillary('../data/Polio.html')": "https://www.randomservices.org/random/data/Polio.html",
        "JavaScript:openAncillary('../data/Challenger.html')": "https://www.randomservices.org/random/data/Challenger.html",
        "JavaScript:openAncillary('../data/Michelson.html')": "https://www.randomservices.org/random/data/Michelson.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
        "JavaScript:openAncillary('../data/Snow.html')": "https://www.randomservices.org/random/data/Snow.html",
        "JavaScript:openAncillary('../data/SAT.html')": "https://www.randomservices.org/random/data/SAT.html",
        "../dist/discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "../foundations/Equivalence.html": "https://www.randomservices.org/random/foundations/Equivalence.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../prob/Events.html": "https://www.randomservices.org/random/prob/Events.html",
        "JavaScript:openAncillary('../data/Berkeley.html')": "https://www.randomservices.org/random/data/Berkeley.html",
        "JavaScript:openAncillary('../data/LiteraryDigest.html')": "https://www.randomservices.org/random/data/LiteraryDigest.html",
        "JavaScript:openAncillary('../data/1948Election.html')": "https://www.randomservices.org/random/data/Election1948.html",
        "JavaScript:openAncillary('../data/Cavendish.html')": "https://www.randomservices.org/random/data/Cavendish.html",
        "JavaScript:openAncillary('../data/Short.html')": "https://www.randomservices.org/random/data/Short.html",
        "JavaScript:openAncillary('../data/Draft.html')": "https://www.randomservices.org/random/data/Draft.html",
        "../buffon/Buffon.html": "https://www.randomservices.org/random/buffon/Buffon.html",
        "../bernoulli/Introduction.html": "https://www.randomservices.org/random/bernoulli/Introduction.html",
        "../poisson/Introduction.html": "https://www.randomservices.org/random/poisson/Introduction.html",
        "../special/index.html": "https://www.randomservices.org/random/special/index.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "../special/Gamma.html": "https://www.randomservices.org/random/special/Gamma.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "../special/Pareto.html": "https://www.randomservices.org/random/special/Pareto.html",
        "../special/Weibull.html": "https://www.randomservices.org/random/special/Weibull.html",
        "../urn/OrderStatistics.html": "https://www.randomservices.org/random/urn/OrderStatistics.html",
        "../urn/index.html": "https://www.randomservices.org/random/urn/index.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/sample/Mean.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "LLN.html": "https://www.randomservices.org/random/sample/LLN.html",
        "CLT.html": "https://www.randomservices.org/random/sample/CLT.html",
        "Variance.html": "https://www.randomservices.org/random/sample/Variance.html",
        "OrderStatistics.html": "https://www.randomservices.org/random/sample/OrderStatistics.html",
        "Covariance.html": "https://www.randomservices.org/random/sample/Covariance.html",
        "Normal.html": "https://www.randomservices.org/random/sample/Normal.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../dist/Discrete.html#uni": "https://www.randomservices.org/random/dist/Discrete.html#uni",
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../dist/CDF.html": "https://www.randomservices.org/random/dist/CDF.html",
        "../dist/Discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "../dist/Continuous.html": "https://www.randomservices.org/random/dist/Continuous.html",
        "JavaScript:openAncillary('../apps/Histogram.html')": "https://www.randomservices.org/random/apps/Histogram.html",
        "JavaScript:openAncillary('../data/Fisher.html')": "https://www.randomservices.org/random/data/Iris.html",
        "JavaScript:openAncillary('../data/Challenger.html')": "https://www.randomservices.org/random/data/Challenger.html",
        "JavaScript:openAncillary('../data/Michelson.html')": "https://www.randomservices.org/random/data/Michelson.html",
        "JavaScript:openAncillary('../data/Short.html')": "https://www.randomservices.org/random/data/Short.html",
        "JavaScript:openAncillary('../data/Cavendish.html')": "https://www.randomservices.org/random/data/Cavendish.html",
        "JavaScript:openAncillary('../data/MM.html')": "https://www.randomservices.org/random/data/MM.html",
        "JavaScript:openAncillary('../data/Cicada.html')": "https://www.randomservices.org/random/data/Cicada.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
}

CORRECTION_DELTAS = {
    (
        PurePosixPath("random/sample/Introduction.html"),
        "JavaScript:openAncillary('../data/Fisher.html')",
        "https://www.randomservices.org/random/data/Iris.html",
    ),
    (
        PurePosixPath("random/sample/Introduction.html"),
        "JavaScript:openAncillary('../data/1948Election.html')",
        "https://www.randomservices.org/random/data/Election1948.html",
    ),
    (
        PurePosixPath("random/sample/Introduction.html"),
        "../dist/discrete.html",
        "https://www.randomservices.org/random/dist/Discrete.html",
    ),
    (
        PurePosixPath("random/sample/Mean.html"),
        "JavaScript:openAncillary('../data/Fisher.html')",
        "https://www.randomservices.org/random/data/Iris.html",
    ),
}

NOTICE_MARKUP_SHA256 = {
    PurePosixPath("random/sample/index.html"): "d56c45b9741ffdb1adbc27999f42e6a6ea2865a5271b413222d4a8c1a40044c6",
    PurePosixPath("random/sample/Introduction.html"): "64ad3ed4c57ffe8c0c91fae7047ba7d57399538bef9f7beae730e1fa4f4fa931",
    PurePosixPath("random/sample/Mean.html"): "b5dbee259ec1dd62c84f5d776320e15142359cc401afa413f9a2524f906fb275",
}
NOTICE_LINKS = (
    "https://www.randomservices.org/random/",
    "https://creativecommons.org/licenses/by/2.0/",
    "https://www.randomservices.org/random/Credits.html",
    "https://creativecommons.org/licenses/by/1.0/",
)
NOTICE_TOKEN_COUNTS = {
    "Kyle Siegrist": 2,
    "Random": 2,
    "CC BY 2.0": 1,
    "CC BY 1.0": 1,
    "tidak didukung maupun disahkan": 1,
}
NOTICE_ALLOWED_TAGS = {"section", "p", "strong", "a"}
NOTICE_FORBIDDEN_TAGS = {"script", "style", "iframe", "object", "embed", "base", "form"}
FETCH_ATTRIBUTES = {"src", "srcset", "poster", "data", "action", "formaction"}
REFERENCE_ATTRIBUTES = FETCH_ATTRIBUTES | {
    "href",
    "xlink:href",
    "background",
    "cite",
    "longdesc",
    "manifest",
    "usemap",
}

MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)
RAW_TEXT_RE = re.compile(r"<(script|style)\b[^>]*>(.*?)</\1\s*>", re.IGNORECASE | re.DOTALL)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_URL_RE = re.compile(
    r"url\(\s*(?:(['\"])(.*?)\1|([^)]*?))\s*\)", re.IGNORECASE | re.DOTALL
)
CSS_IMPORT_RE = re.compile(r"@import\s+(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL)
REMOTE_TEXT_RE = re.compile(r"(?i)(?:https?:)?//")
LOCAL_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/]+Users[\\/]+|file:(?:/|\\/){2,4}|/(?:home|Users|root)/)",
    re.IGNORECASE,
)
SECRET_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*[^\s<]{12,}"
)
ENGLISH_DENY = (
    "Random Samples",
    "Expand Details",
    "Contract Details",
    ">Summary<",
    ">Topics<",
    ">Sources and Resources<",
    ">Examples<",
    ">Details:<",
    ">Designed experiment<",
    ">Observational study<",
)

# These three exact non-fetching metadata links are already part of the approved
# href delta set. All fetching link relations remain forbidden remotely.
EXACT_EXTERNAL_METADATA_LINKS = {
    ("random/sample/index.html", "https://www.randomservices.org/random/index.html", "contents"),
    ("random/sample/index.html", "https://www.randomservices.org/random/special/index.html", "previous"),
    ("random/sample/index.html", "https://www.randomservices.org/random/point/index.html", "next"),
}


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read(path: Path) -> bytes:
    return build_pipeline.read_regular(path)


def soup(data: bytes, label: str, *, parser: str = "lxml") -> BeautifulSoup:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"non-UTF-8 document {label}: {exc}")
    parsed = BeautifulSoup(text, parser)
    if parser == "lxml":
        if len(parsed.find_all("html")) != 1 or len(parsed.find_all("head")) != 1 or len(parsed.find_all("body")) != 1:
            fail(f"incomplete or multiply rooted HTML document: {label}")
    return parsed


def hierarchy_signature(node: Tag | BeautifulSoup) -> tuple[Any, ...]:
    children = tuple(hierarchy_signature(child) for child in node.children if isinstance(child, Tag))
    if isinstance(node, Tag):
        return (node.name, children)
    return children


def math_spans(text: str) -> list[str]:
    """Extract TeX without swallowing HTML after a malformed display opener.

    The frozen Mean authority contains one proved ``\\[`` display that reaches
    ``</p>`` without ``\\]``.  A cross-document regex would absorb translated
    prose until a later close and cannot prove protected-byte equality.  At
    that exact kind of malformed surface the paragraph boundary is used as the
    terminus, preserving the defect while keeping subsequent TeX comparable.
    """
    spans: list[str] = []
    cursor = 0
    while True:
        inline = text.find(r"\(", cursor)
        display = text.find(r"\[", cursor)
        starts = [
            (value, marker)
            for value, marker in ((inline, r"\("), (display, r"\["))
            if value >= 0
        ]
        if not starts:
            break
        start, opener = min(starts)
        closer = r"\)" if opener == r"\(" else r"\]"
        close = text.find(closer, start + 2)
        paragraph_end = text.find("</p>", start + 2)
        if paragraph_end >= 0 and (close < 0 or paragraph_end < close):
            spans.append(text[start:paragraph_end])
            cursor = paragraph_end
        elif close >= 0:
            spans.append(text[start : close + 2])
            cursor = close + 2
        else:
            spans.append(text[start:])
            break
    return spans


def normalize_authority_math(rel: PurePosixPath, spans: list[str]) -> tuple[list[str], int]:
    """Apply only the declared, exact source corrections inside TeX spans."""
    normalized = list(spans)
    applied = 0
    for change in build_pipeline.PROTECTED_MATH_CORRECTIONS:
        if change["page"] != rel.as_posix() or change["surface"] != "math_span":
            continue
        old = change.get("span_old", change["old"])
        new = change.get("span_new", change["new"])
        expected = int(change["replacements"])
        observed = sum(span.count(old) for span in normalized)
        if observed != expected:
            fail(
                f"{rel}: protected TeX correction authority count changed for {old!r}: "
                f"{observed} != {expected}"
            )
        normalized = [span.replace(old, new) for span in normalized]
        applied += observed
    return normalized, applied


def element_stream(parsed: BeautifulSoup) -> list[Tag]:
    return list(parsed.find_all(True))


def validate_allowlist() -> None:
    if set(HREF_DELTA_ALLOWLIST) != set(PAIRS):
        fail("href-delta allowlist page set differs from the first-unit page set")
    for rel, mapping in HREF_DELTA_ALLOWLIST.items():
        if len(mapping) != len(set(mapping)):
            fail(f"duplicate href-delta key for {rel}")
        for original, target in mapping.items():
            if not original or urlparse(target).scheme != "https":
                fail(f"non-HTTPS or empty exact href delta for {rel}: {original!r}->{target!r}")
    actual_corrections = {
        (rel, original, target)
        for rel, mapping in HREF_DELTA_ALLOWLIST.items()
        for original, target in mapping.items()
        if (rel, original, target) in CORRECTION_DELTAS
    }
    if actual_corrections != CORRECTION_DELTAS:
        fail("the four controlled filename/case corrections are not exactly allowlisted")
    for change in build_pipeline.TRANSPORT_HARDENING:
        rel = PurePosixPath(change["page"])
        if HREF_DELTA_ALLOWLIST.get(rel, {}).get(change["original_href"]) != change["target_href"]:
            fail("transport-only hardening and href-delta allowlist disagree")


def validate_notice(notice: Tag, rel: PurePosixPath) -> dict[str, Any]:
    if notice.name != "section":
        fail(f"{rel}: edition notice is not a section")
    if notice.attrs != {"class": ["edition-notice"], "data-o006-edition-notice": "v1"}:
        fail(f"{rel}: edition notice root attributes differ")
    expected_hierarchy = (
        "section",
        (
            ("p", (("strong", ()), ("a", ()))),
            ("p", (("a", ()), ("a", ()), ("a", ()))),
        ),
    )
    if hierarchy_signature(notice) != expected_hierarchy:
        fail(f"{rel}: edition notice hierarchy differs")
    if notice.find_all(string=lambda value: isinstance(value, Comment)):
        fail(f"{rel}: comments are forbidden in the edition notice")
    for tag in notice.find_all(True):
        if tag.name in NOTICE_FORBIDDEN_TAGS or tag.name not in NOTICE_ALLOWED_TAGS:
            fail(f"{rel}: forbidden edition-notice element: {tag.name}")
        for attr in tag.attrs:
            lower = attr.lower()
            if lower.startswith("on") or lower in FETCH_ATTRIBUTES or lower in {"style", "srcdoc"}:
                fail(f"{rel}: active/fetching edition-notice attribute: {tag.name}[{attr}]")
        if tag.name == "section":
            allowed = {"class", "data-o006-edition-notice"}
        elif tag.name == "a":
            allowed = {"href"}
        else:
            allowed = set()
        if set(tag.attrs) != allowed:
            fail(f"{rel}: edition-notice attribute set differs on {tag.name}")
    links = tuple(str(link.get("href")) for link in notice.find_all("a"))
    if links != NOTICE_LINKS:
        fail(f"{rel}: edition-notice links differ")
    text = notice.get_text(" ", strip=True)
    for token, expected_count in NOTICE_TOKEN_COUNTS.items():
        if text.count(token) != expected_count:
            fail(f"{rel}: edition-notice token count differs for {token!r}")
    markup = notice.decode(formatter="minimal").encode("utf-8")
    if sha256_bytes(markup) != NOTICE_MARKUP_SHA256[rel]:
        fail(f"{rel}: edition-notice bounded markup differs")
    return {"bytes": len(markup), "sha256": sha256_bytes(markup), "links": len(links)}


def compare_pair(rel: PurePosixPath) -> dict[str, Any]:
    source_data = read(AUTHORITY / Path(rel.as_posix()))
    target_data = read(TARGET / Path(rel.as_posix()))
    reader_data = read(READER / Path(rel.as_posix()))
    if reader_data != target_data:
        fail(f"{rel}: built reader is not byte-identical to the translation target")

    source = soup(source_data, f"source:{rel}")
    target = soup(target_data, f"target:{rel}")
    notices = target.select('[data-o006-edition-notice="v1"]')
    if len(notices) != 1:
        fail(f"{rel}: expected exactly one edition notice, found {len(notices)}")
    notice_result = validate_notice(notices[0], rel)
    notices[0].decompose()

    source_hierarchy = hierarchy_signature(source)
    target_hierarchy = hierarchy_signature(target)
    if source_hierarchy != target_hierarchy:
        fail(f"{rel}: hierarchical DOM signature differs after validated notice removal")

    source_text = source_data.decode("utf-8")
    target_text = target_data.decode("utf-8")
    source_raw = [(name.lower(), body) for name, body in RAW_TEXT_RE.findall(source_text)]
    target_raw = [(name.lower(), body) for name, body in RAW_TEXT_RE.findall(target_text)]
    if source_raw != target_raw:
        fail(f"{rel}: script/style raw text differs")
    source_math = math_spans(source_text)
    target_math = math_spans(target_text)
    expected_math, protected_math_replacements = normalize_authority_math(rel, source_math)
    if expected_math != target_math:
        fail(f"{rel}: exact TeX/math sequence changed ({len(source_math)} vs {len(target_math)})")

    source_tags = element_stream(source)
    target_tags = element_stream(target)
    if len(source_tags) != len(target_tags):
        fail(f"{rel}: element count differs after validated notice removal")
    allowed_attr_deltas = {"lang", "title", "alt", "content", "id", "href"}
    page_allowlist = HREF_DELTA_ALLOWLIST[rel]
    seen_deltas: set[tuple[str, str]] = set()
    href_delta_occurrences = 0
    for index, (source_tag, target_tag) in enumerate(zip(source_tags, target_tags), start=1):
        if source_tag.name != target_tag.name:
            fail(f"{rel}: paired element name differs at element {index}")
        all_keys = set(source_tag.attrs) | set(target_tag.attrs)
        for key in all_keys:
            source_value = source_tag.attrs.get(key)
            target_value = target_tag.attrs.get(key)
            if source_value == target_value:
                if key == "href" and str(source_value) in page_allowlist:
                    fail(f"{rel}: allowlisted href delta was not applied at element {index}")
                continue
            if key not in allowed_attr_deltas:
                fail(f"{rel}: unexplained attr delta at element {index}: {key}")
            if key == "lang" and not (source_value == "en" and target_value == "id-ID"):
                fail(f"{rel}: invalid lang delta {source_value!r}->{target_value!r}")
            elif key == "id":
                if source_value is not None:
                    fail(f"{rel}: existing id changed at element {index}")
                if not isinstance(target_value, str) or not target_value.startswith("o006.random."):
                    fail(f"{rel}: invalid additive stable id at element {index}: {target_value!r}")
            elif key == "href":
                original = str(source_value)
                expected = page_allowlist.get(original)
                if expected is None or target_value != expected:
                    fail(
                        f"{rel}: href delta not exactly allowlisted at element {index}: "
                        f"{source_value!r}->{target_value!r}"
                    )
                seen_deltas.add((original, expected))
                href_delta_occurrences += 1
    expected_deltas = set(page_allowlist.items())
    if seen_deltas != expected_deltas:
        missing = sorted(expected_deltas - seen_deltas)
        extra = sorted(seen_deltas - expected_deltas)
        fail(f"{rel}: href-delta use mismatch; missing={missing}; extra={extra}")

    full = soup(target_data, f"target:{rel}:full")
    ids = [str(tag["id"]) for tag in full.find_all(attrs={"id": True})]
    if len(ids) != len(set(ids)):
        duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
        fail(f"{rel}: duplicate target IDs: {duplicates}")
    if full.html is None or full.html.get("lang") != "id-ID":
        fail(f"{rel}: html lang is not id-ID")
    if full.find("meta", attrs={"charset": re.compile("utf-8", re.I)}) is None:
        fail(f"{rel}: UTF-8 meta declaration absent")
    units = full.select("div.unit")
    for unit in units:
        if not unit.get("id"):
            fail(f"{rel}: unit without stable id")
    if LOCAL_PATH_RE.search(target_text) or SECRET_RE.search(target_text):
        fail(f"{rel}: local path or secret-shaped text detected")
    for phrase in ENGLISH_DENY:
        if phrase in target_text:
            fail(f"{rel}: active English UI/prose residue: {phrase}")

    hierarchy_bytes = json.dumps(source_hierarchy, separators=(",", ":")).encode("utf-8")
    return {
        "source_bytes": len(source_data),
        "source_sha256": sha256_bytes(source_data),
        "target_bytes": len(target_data),
        "target_sha256": sha256_bytes(target_data),
        "reader_bytes": len(reader_data),
        "reader_sha256": sha256_bytes(reader_data),
        "reader_target_byte_identical": True,
        "elements": len(source_tags),
        "hierarchy_sha256": sha256_bytes(hierarchy_bytes),
        "raw_script_style_blocks": len(source_raw),
        "math_spans": len(source_math),
        "protected_math_replacements": protected_math_replacements,
        "href_delta_entries": len(seen_deltas),
        "href_delta_occurrences": href_delta_occurrences,
        "units": len(units),
        "details": len(full.find_all("details")),
        "ids": len(ids),
        "edition_notice": notice_result,
    }


def _attribute_text(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return " ".join(str(item) for item in value)
    return str(value)


def _external_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme or parsed.netloc)


def _validate_https(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
        fail(f"external navigation must be credential-free HTTPS: {label}: {value}")


def _local_target(page: Path, value: str) -> tuple[Path, str]:
    if not value or "\x00" in value or "\\" in value:
        fail(f"noncanonical local reference in {page}: {value!r}")
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        fail(f"not a local reference in {page}: {value}")
    decoded_path = unquote(parsed.path)
    if decoded_path != parsed.path or "\\" in decoded_path or "\x00" in decoded_path:
        fail(f"encoded/noncanonical local path in {page}: {value}")
    if decoded_path.startswith("/"):
        target = READER / decoded_path.lstrip("/")
    elif decoded_path:
        target = page.parent / decoded_path
    else:
        target = page
    resolved = target.resolve(strict=False)
    try:
        resolved.relative_to(READER.resolve())
    except ValueError:
        fail(f"local reference escapes reader: {page.relative_to(READER)} -> {value}")
    build_pipeline.ensure_regular(resolved, reject_hardlinks=True)
    return resolved, unquote(parsed.fragment)


def _check_local_reference(
    page: Path,
    value: str,
    parsed_cache: dict[Path, BeautifulSoup],
    counts: Counter[str],
) -> None:
    target, fragment = _local_target(page, value)
    counts["local_refs"] += 1
    if fragment:
        if target.suffix.lower() not in {".html", ".htm", ".svg"}:
            fail(f"fragment targets a non-document: {page.relative_to(READER)} -> {value}")
        target_doc = parsed_cache.get(target)
        if target_doc is None:
            parser = "xml" if target.suffix.lower() == ".svg" else "lxml"
            target_doc = soup(read(target), f"reader-fragment:{target}", parser=parser)
            parsed_cache[target] = target_doc
        if target_doc.find(id=fragment) is None:
            fail(f"broken fragment: {page.relative_to(READER)} -> {value}")
        counts["fragments"] += 1


def _css_references(css: str) -> list[str]:
    without_comments = CSS_COMMENT_RE.sub("", css)
    refs = []
    for match in CSS_URL_RE.finditer(without_comments):
        refs.append((match.group(2) if match.group(1) else match.group(3)).strip())
    refs.extend(match.group(2).strip() for match in CSS_IMPORT_RE.finditer(without_comments))
    return refs


def _check_css(
    owner: Path,
    css: str,
    parsed_cache: dict[Path, BeautifulSoup],
    counts: Counter[str],
) -> None:
    for value in _css_references(css):
        if not value:
            fail(f"empty CSS URL in {owner.relative_to(READER)}")
        if _external_url(value):
            fail(f"remote CSS url/@import is forbidden: {owner.relative_to(READER)} -> {value}")
        _check_local_reference(owner, value, parsed_cache, counts)
        counts["css_refs"] += 1


def _check_html_reference(
    page: Path,
    tag: Tag,
    attr: str,
    value: str,
    parsed_cache: dict[Path, BeautifulSoup],
    counts: Counter[str],
) -> None:
    if _external_url(value):
        if tag.name == "a" and attr == "href":
            _validate_https(value, f"{page.relative_to(READER)} a[href]")
            counts["external_https_anchors"] += 1
            return
        if tag.name == "link" and attr == "href":
            rels = tuple(str(item).lower() for item in (tag.get("rel") or []))
            if len(rels) == 1 and (page.relative_to(READER).as_posix(), value, rels[0]) in EXACT_EXTERNAL_METADATA_LINKS:
                _validate_https(value, f"{page.relative_to(READER)} link[{rels[0]}]")
                counts["external_https_metadata_links"] += 1
                return
        fail(f"remote reference is forbidden outside an anchor href: {page.relative_to(READER)} {tag.name}[{attr}]={value}")
    _check_local_reference(page, value, parsed_cache, counts)


def check_reader_references() -> dict[str, int]:
    rows = build_pipeline.canonical_rows(READER)
    pages = [READER / rel for rel, _, _ in rows if PurePosixPath(rel).suffix.lower() == ".html"]
    stylesheets = [READER / rel for rel, _, _ in rows if PurePosixPath(rel).suffix.lower() == ".css"]
    svgs = [READER / rel for rel, _, _ in rows if PurePosixPath(rel).suffix.lower() == ".svg"]
    if not pages:
        fail("reader contains no HTML pages")
    parsed_cache: dict[Path, BeautifulSoup] = {}
    counts: Counter[str] = Counter()
    for page in pages:
        parsed_cache[page.resolve()] = soup(read(page), f"reader:{page.relative_to(READER)}")

    for page in pages:
        parsed = parsed_cache[page.resolve()]
        if parsed.find("base") is not None:
            fail(f"base element is forbidden: {page.relative_to(READER)}")
        for meta in parsed.find_all("meta"):
            if str(meta.get("http-equiv", "")).casefold() == "refresh":
                fail(f"meta refresh is forbidden: {page.relative_to(READER)}")
        for tag in parsed.find_all(True):
            for attr, raw_value in tag.attrs.items():
                attr_lower = attr.lower()
                value = _attribute_text(raw_value).strip()
                if attr_lower.startswith("on"):
                    # Event handlers are allowed only when byte-preserved by the
                    # authority comparison; neither generated page has one.
                    rel = PurePosixPath(page.relative_to(READER).as_posix())
                    if rel not in PAIRS:
                        fail(f"event handler in generated reader page: {page.relative_to(READER)} {attr}")
                if attr_lower == "style":
                    _check_css(page, value, parsed_cache, counts)
                if attr_lower == "srcset":
                    for candidate in value.split(","):
                        url = candidate.strip().split()[0] if candidate.strip() else ""
                        if not url:
                            fail(f"malformed srcset in {page.relative_to(READER)}")
                        _check_html_reference(page, tag, attr_lower, url, parsed_cache, counts)
                    continue
                if attr_lower in REFERENCE_ATTRIBUTES and value:
                    _check_html_reference(page, tag, attr_lower, value, parsed_cache, counts)
                elif REMOTE_TEXT_RE.search(value):
                    fail(f"remote URL outside a reference attribute: {page.relative_to(READER)} {tag.name}[{attr}]")
            if tag.name == "style":
                _check_css(page, tag.decode_contents(formatter=None), parsed_cache, counts)

    for stylesheet in stylesheets:
        _check_css(stylesheet, read(stylesheet).decode("utf-8"), parsed_cache, counts)

    for svg in svgs:
        parsed = soup(read(svg), f"reader-svg:{svg.relative_to(READER)}", parser="xml")
        for tag in parsed.find_all(True):
            for attr in ("href", "xlink:href"):
                value = tag.get(attr)
                if value:
                    if _external_url(str(value)):
                        fail(f"remote SVG reference is forbidden: {svg.relative_to(READER)} {attr}={value}")
                    _check_local_reference(svg, str(value), parsed_cache, counts)
            if tag.get("style"):
                _check_css(svg, str(tag["style"]), parsed_cache, counts)
        for style in parsed.find_all("style"):
            _check_css(svg, style.decode_contents(formatter=None), parsed_cache, counts)

    counts["html_pages"] = len(pages)
    counts["css_files"] = len(stylesheets)
    counts["svg_files"] = len(svgs)
    return dict(sorted(counts.items()))


def check_mathjax_runtime() -> dict[str, Any]:
    expected_runtime, authority_record = build_pipeline._runtime_payload()
    runtime_path = READER / Path(build_pipeline.RUNTIME_READER_PATH.as_posix())
    runtime_data = read(runtime_path)
    if runtime_data != expected_runtime:
        fail("reader MathJax boldsymbol runtime differs from the pinned official bytes")
    bundle_path = READER / "MathJax" / "tex-svg.js"
    bundle_data = read(bundle_path)
    if b'"[tex]/boldsymbol"' not in bundle_data:
        fail("MathJax bundle no longer declares the local boldsymbol autoload component")
    script_pages: list[str] = []
    for rel in PAIRS:
        page = READER / Path(rel.as_posix())
        parsed = soup(read(page), f"mathjax-runtime:{rel}")
        for script in parsed.find_all("script", src=True):
            target, fragment = _local_target(page, str(script["src"]))
            if target == bundle_path.resolve():
                if fragment:
                    fail(f"MathJax script reference unexpectedly has a fragment: {rel}")
                script_pages.append(rel.as_posix())
    expected_script_pages = [
        "random/sample/Introduction.html",
        "random/sample/Mean.html",
    ]
    if script_pages != expected_script_pages:
        fail(f"MathJax bundle reference pages changed: {script_pages}")
    return {
        "reader_relative_path": build_pipeline.RUNTIME_READER_PATH.as_posix(),
        "bytes": len(runtime_data),
        "sha256": sha256_bytes(runtime_data),
        "official_tag": authority_record["tag"],
        "official_commit": authority_record["commit"],
        "git_blob_sha1": authority_record["git_blob_sha1"],
        "script_page_references": len(script_pages),
        "script_pages": script_pages,
        "runtime_file_count": 1,
    }


def check_readable_reflow() -> dict[str, Any]:
    rel = PurePosixPath("random/Screen.css")
    authority_data = read(AUTHORITY / Path(rel.as_posix()))
    reader_data = read(READER / Path(rel.as_posix()))
    expected = authority_data + build_pipeline.READABLE_REFLOW_CSS
    if reader_data != expected:
        fail("reader Screen.css is not the exact authority bytes plus readable-layout appendix")
    css = build_pipeline.READABLE_REFLOW_CSS.decode("utf-8")
    required = (
        "O006 id-ID readable layout v1",
        "min-width: 801px",
        "max-width: 72rem",
        "margin: 1rem auto",
        "max-width: 800px",
        "margin: 0.75rem",
        "overflow-x: auto",
    )
    missing = [token for token in required if token not in css]
    if missing:
        fail(f"readable-layout invariant missing from CSS appendix: {missing}")
    return {
        "version": "o006-id-readable-layout-v1",
        "reader_relative_path": rel.as_posix(),
        "authority_bytes": len(authority_data),
        "authority_sha256": sha256_bytes(authority_data),
        "append_bytes": len(build_pipeline.READABLE_REFLOW_CSS),
        "append_sha256": sha256_bytes(build_pipeline.READABLE_REFLOW_CSS),
        "reader_bytes": len(reader_data),
        "reader_sha256": sha256_bytes(reader_data),
        "desktop_min_width_px": 801,
        "desktop_max_width_rem": 72,
        "mobile_max_width_px": 800,
        "mobile_fluid": True,
    }


def expected_qa_receipt(
    build_summary: dict[str, Any],
    results: dict[str, dict[str, Any]],
    reference_counts: dict[str, int],
    mathjax_runtime: dict[str, Any],
    readable_reflow: dict[str, Any],
) -> dict[str, Any]:
    build_receipt_data = read(build_pipeline.BUILD_RECEIPT)
    qa_script_data = read(Path(__file__).resolve())
    build_script_data = read(Path(build_pipeline.__file__).resolve())
    counts = {
        "translated_pages": len(results),
        "source_elements": sum(int(result["elements"]) for result in results.values()),
        "math_spans": sum(int(result["math_spans"]) for result in results.values()),
        "raw_script_style_blocks": sum(
            int(result["raw_script_style_blocks"]) for result in results.values()
        ),
        "href_delta_entries": sum(int(result["href_delta_entries"]) for result in results.values()),
        "href_delta_occurrences": sum(
            int(result["href_delta_occurrences"]) for result in results.values()
        ),
        "transport_hardening_deltas": len(build_pipeline.TRANSPORT_HARDENING),
        "controlled_filename_case_corrections": len(CORRECTION_DELTAS),
        "bounded_text_correction_categories": len(build_pipeline.BOUNDED_TEXT_CORRECTIONS),
        "protected_math_correction_categories": len(build_pipeline.PROTECTED_MATH_CORRECTIONS),
        "protected_math_replacements": sum(
            int(result["protected_math_replacements"]) for result in results.values()
        ),
        "readable_layout_css_appends": 1,
        "mathjax_runtime_files": int(mathjax_runtime["runtime_file_count"]),
        "units": sum(int(result["units"]) for result in results.values()),
        "details": sum(int(result["details"]) for result in results.values()),
        "ids": sum(int(result["ids"]) for result in results.values()),
        "reader_files": int(build_summary["file_count"]),
        "reader_bytes": int(build_summary["total_bytes"]),
        **reference_counts,
    }
    return {
        "schema": "o006.random.first-unit-qa.v1",
        "build": {
            "receipt_path": build_pipeline.BUILD_RECEIPT.relative_to(ROOT).as_posix(),
            "receipt_bytes": len(build_receipt_data),
            "receipt_sha256": sha256_bytes(build_receipt_data),
            "reader_manifest_sha256": build_summary["manifest_sha256"],
            "reader_file_count": build_summary["file_count"],
            "reader_total_bytes": build_summary["total_bytes"],
        },
        "scripts": {
            "build": {
                "path": Path(build_pipeline.__file__).resolve().relative_to(ROOT).as_posix(),
                "bytes": len(build_script_data),
                "sha256": sha256_bytes(build_script_data),
            },
            "qa": {
                "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
                "bytes": len(qa_script_data),
                "sha256": sha256_bytes(qa_script_data),
            },
        },
        "transport_hardening": list(build_pipeline.TRANSPORT_HARDENING),
        "bounded_text_corrections": list(build_pipeline.BOUNDED_TEXT_CORRECTIONS),
        "protected_math_corrections": list(build_pipeline.PROTECTED_MATH_CORRECTIONS),
        "mathjax_runtime": mathjax_runtime,
        "readable_reflow": readable_reflow,
        "results": results,
        "pass_counts": counts,
    }


def run(*, check_only: bool = False) -> dict[str, Any]:
    validate_allowlist()
    build_summary = build_pipeline.check(verbose=False)
    results = {rel.as_posix(): compare_pair(rel) for rel in PAIRS}
    intro = results["random/sample/Introduction.html"]
    if intro["units"] != 22 or intro["details"] != 16:
        fail(f"Introduction census changed: {intro}")
    mean = results["random/sample/Mean.html"]
    if mean["units"] != 26 or mean["details"] != 23 or mean["math_spans"] != 365:
        fail(f"Mean census changed: {mean}")
    reference_counts = check_reader_references()
    mathjax_runtime = check_mathjax_runtime()
    readable_reflow = check_readable_reflow()
    receipt = expected_qa_receipt(
        build_summary, results, reference_counts, mathjax_runtime, readable_reflow
    )
    receipt_data = build_pipeline.canonical_json_bytes(receipt)
    if check_only:
        actual = build_pipeline.read_regular(QA_RECEIPT, reject_hardlinks=True)
        if actual != receipt_data:
            fail("first-unit QA receipt is stale or noncanonical")
    else:
        build_pipeline.make_directory(QA_RECEIPT.parent)
        build_pipeline.write_regular(QA_RECEIPT, receipt_data)
    actual = build_pipeline.read_regular(QA_RECEIPT, reject_hardlinks=True)
    if actual != receipt_data:
        fail("first-unit QA receipt replay mismatch")
    counts = receipt["pass_counts"]
    print(
        f"PASS QA: {counts['translated_pages']} translated pages / "
        f"{counts['reader_bytes']} reader bytes / {counts['units']} units / "
        f"{counts['details']} details / {counts.get('local_refs', 0)} local refs / "
        f"{counts.get('fragments', 0)} fragments / receipt {sha256_bytes(actual)}"
    )
    return {
        "qa_receipt_bytes": len(actual),
        "qa_receipt_sha256": sha256_bytes(actual),
        "pass_counts": counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    run(check_only=args.check_only)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
