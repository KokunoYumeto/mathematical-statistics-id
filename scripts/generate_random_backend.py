#!/usr/bin/env python3
"""Generate the deterministic O006 Random-core stable-ID backend.

The generator intentionally uses only the Python standard library.  Its source
universe is the 29 paths frozen by authority/SOURCE_FREEZE_RECEIPT.json and the
metadata in authority/SOURCE_URL_MANIFEST.csv.  It never edits authority HTML.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import io
import json
import posixpath
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


ENTITY_SCHEMA_VERSION = "o006.random.backend.entity.v2"
RELATION_SCHEMA_VERSION = "o006.random.backend.relation.v1"
RECEIPT_SCHEMA_VERSION = "o006.random.backend.receipt.v2"

RECEIPT_REL = PurePosixPath("authority/SOURCE_FREEZE_RECEIPT.json")
MANIFEST_REL = PurePosixPath("authority/SOURCE_URL_MANIFEST.csv")
UPSTREAM_REL = PurePosixPath("authority/upstream")
ENTITY_SCHEMA_REL = PurePosixPath("backend/entities.schema.json")
ENTITIES_REL = PurePosixPath("backend/entities.jsonl")
RELATIONS_REL = PurePosixPath("backend/relations.csv")
BACKEND_RECEIPT_REL = PurePosixPath("backend/BACKEND_RECEIPT.json")
TRANSLATION_LEDGER_REL = PurePosixPath("00_control/TRANSLATION_LEDGER.csv")

TRANSLATION_LEDGER_COLUMNS = [
    "ordinal",
    "source_path",
    "target_path",
    "status",
    "source_bytes",
    "source_sha256",
    "target_bytes",
    "target_sha256",
    "notes",
]
TARGET_LOCALE = "id-ID"

TYPE_CODE = {
    "document": 0,
    "section": 1,
    "unit": 2,
    "disclosure": 3,
    "math_text": 4,
    "figure": 5,
    "asset": 6,
    "internal_link": 7,
}
TYPE_PRIORITY = {name: code for name, code in TYPE_CODE.items()}

VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
TEXT_CONTAINER_TAGS = {
    "p",
    "li",
    "td",
    "th",
    "dt",
    "dd",
    "caption",
    "figcaption",
    "summary",
    "pre",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "math",
}
ASSET_TAGS = {
    "img",
    "script",
    "input",
    "audio",
    "video",
    "source",
    "object",
    "embed",
    "iframe",
    "canvas",
    "picture",
}
NAV_LINK_RELS = {"contents", "previous", "prev", "next", "up", "index", "chapter"}
ASSET_LINK_RELS = {"icon", "stylesheet", "preload", "modulepreload", "manifest"}
INTERNAL_HOSTS = {"randomservices.org", "www.randomservices.org"}
MATH_MARKER_RE = re.compile(r"\\[\[(]|\$\$")
EXERCISE_HEADING_RE = re.compile(r"\bexercises?\b", re.IGNORECASE)
OPEN_ANCILLARY_RE = re.compile(
    r"^\s*javascript\s*:\s*openAncillary\(\s*(['\"])(.*?)\1\s*\)\s*;?\s*$",
    re.IGNORECASE,
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

RIGHTS_RANDOM = "random-site-cc-by-notice-discrepancy"
RIGHTS_MATHJAX = "apache-2.0"
RIGHTS_CARDS = "cc0-1.0-cards"
RIGHTS_MONTY = "cc0-1.0-monty"
RIGHTS_UNCLEARED = "unresolved-third-party-or-data"
RIGHTS_UNDETERMINED = "undetermined"

# These six targets are the defects preserved in the current O006 control
# ledger.  Classification is additive metadata only; authority bytes remain
# untouched.  Several targets occur from more than one page.
KNOWN_UPSTREAM_DEFECT_PATHS = {
    "random/apps/ExponentialExperiment.html",
    "random/apps/VarianceTestExperiment.html",
    "random/data/1948Election.html",
    "random/data/Fisher.html",
    "random/dist/discrete.html",
    "random/interval/two2",
}


class BackendError(RuntimeError):
    """A deterministic input, coverage, or verification failure."""


def exercise_designation_basis(
    unit_record: dict[str, Any], records_by_id: dict[str, dict[str, Any]]
) -> str:
    """Classify a unit from its native type and semantic section ancestry."""
    native_designated = unit_record["unit_type"] in {"app", "stat"}
    section_designated = False
    section_id = unit_record["section_entity_id"]
    seen_sections: set[str] = set()
    while section_id is not None:
        if section_id in seen_sections:
            raise BackendError(
                f"section hierarchy cycle for unit: {unit_record['entity_id']}"
            )
        seen_sections.add(section_id)
        section_record = records_by_id.get(section_id)
        if section_record is None or section_record["entity_type"] != "section":
            raise BackendError(
                f"invalid section ancestry for unit: {unit_record['entity_id']}"
            )
        if EXERCISE_HEADING_RE.search(section_record["source_text"]):
            section_designated = True
        parent_id = section_record["parent_entity_id"]
        parent_record = records_by_id.get(parent_id) if parent_id is not None else None
        section_id = (
            parent_id
            if parent_record is not None and parent_record["entity_type"] == "section"
            else None
        )

    if native_designated and section_designated:
        return "both"
    if native_designated:
        return "native-unit-type"
    if section_designated:
        return "exercise-section"
    return "not-designated"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    return (text + "\n").encode("utf-8")


def path_from_posix(root: Path, relative: PurePosixPath | str) -> Path:
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise BackendError(f"unsafe relative path: {rel}")
    return root.joinpath(*rel.parts)


def normalized_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


@dataclass(eq=False)
class TextPiece:
    data: str
    parent: "Element"
    event_order: int
    line: int
    column: int


@dataclass(eq=False)
class Element:
    tag: str
    attrs: dict[str, str]
    parent: "Element | None"
    event_order: int
    line: int
    column: int
    sibling_index: int
    dom_path: str
    children: list["Element | TextPiece"] = field(default_factory=list)

    def classes(self) -> list[str]:
        return [part for part in self.attrs.get("class", "").split() if part]


class CorpusHTMLParser(HTMLParser):
    """A small deterministic tree builder sufficient for the frozen corpus."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Element("#document", {}, None, 0, 1, 0, 1, "")
        self.stack: list[Element] = [self.root]
        self.elements: list[Element] = []
        self.text_pieces: list[TextPiece] = []
        self.event_order = 0

    def _next_event(self) -> int:
        self.event_order += 1
        return self.event_order

    def _pop_through(self, index: int) -> None:
        del self.stack[index:]

    def _implicit_close_before(self, tag: str) -> None:
        # Random is mostly explicit HTML.  These HTML implied-end cases keep a
        # malformed list item or paragraph from swallowing later structures.
        groups = {
            "li": {"li"},
            "dt": {"dt", "dd"},
            "dd": {"dt", "dd"},
            "tr": {"tr"},
            "td": {"td", "th"},
            "th": {"td", "th"},
            "option": {"option"},
        }
        closable = groups.get(tag)
        if closable:
            for index in range(len(self.stack) - 1, 0, -1):
                open_tag = self.stack[index].tag
                if open_tag in closable:
                    self._pop_through(index)
                    break
                if open_tag in {"ol", "ul", "dl", "table", "select"}:
                    break

        block_starts = {
            "address", "article", "aside", "blockquote", "details", "div",
            "dl", "fieldset", "figcaption", "figure", "footer", "form",
            "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "main",
            "nav", "ol", "p", "pre", "section", "table", "ul",
        }
        if tag in block_starts:
            for index in range(len(self.stack) - 1, 0, -1):
                if self.stack[index].tag == "p":
                    self._pop_through(index)
                    break
                if self.stack[index].tag in {"div", "section", "body", "html"}:
                    break

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], push: bool) -> None:
        tag = tag.lower()
        self._implicit_close_before(tag)
        parent = self.stack[-1]
        sibling_index = 1 + sum(
            isinstance(child, Element) and child.tag == tag for child in parent.children
        )
        line, column = self.getpos()
        attr_map: dict[str, str] = {}
        for key, value in attrs:
            key = key.lower()
            if key not in attr_map:
                attr_map[key] = "" if value is None else value
        dom_path = f"{parent.dom_path}/{tag}[{sibling_index}]"
        node = Element(
            tag=tag,
            attrs=attr_map,
            parent=parent,
            event_order=self._next_event(),
            line=line,
            column=column,
            sibling_index=sibling_index,
            dom_path=dom_path,
        )
        parent.children.append(node)
        self.elements.append(node)
        if push and tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, True)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, False)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                self._pop_through(index)
                return

    def handle_data(self, data: str) -> None:
        if not data:
            return
        line, column = self.getpos()
        piece = TextPiece(data, self.stack[-1], self._next_event(), line, column)
        self.stack[-1].children.append(piece)
        self.text_pieces.append(piece)


def iter_text(node: Element) -> Iterable[str]:
    for child in node.children:
        if isinstance(child, TextPiece):
            yield child.data
        elif child.tag not in {"script", "style"}:
            yield from iter_text(child)


def element_text(node: Element) -> str:
    return normalized_text("".join(iter_text(node)))


def nearest_ancestor(node: Element, predicate: Any) -> Element | None:
    current = node.parent
    while current is not None and current.tag != "#document":
        if predicate(current):
            return current
        current = current.parent
    return None


def text_owner(node: Element) -> bool:
    if node.tag in TEXT_CONTAINER_TAGS:
        return True
    # A few frozen pages place a display-math text node directly in details or
    # another block container instead of wrapping it in a paragraph.
    return node.tag in {"article", "body", "details", "div", "main", "section"}


def resource_attribute(node: Element) -> tuple[str | None, str | None]:
    if node.tag == "object":
        return "data", node.attrs.get("data")
    if node.tag == "link":
        return "href", node.attrs.get("href")
    return "src", node.attrs.get("src")


def link_rel_tokens(node: Element) -> set[str]:
    return {token.lower() for token in node.attrs.get("rel", "").split() if token}


def is_asset_node(node: Element) -> bool:
    if node.tag in ASSET_TAGS:
        if node.tag in {"canvas", "picture"}:
            return True
        return resource_attribute(node)[1] is not None
    return node.tag == "link" and bool(link_rel_tokens(node) & ASSET_LINK_RELS)


def is_link_node(node: Element) -> bool:
    if node.tag in {"a", "area"}:
        return "href" in node.attrs
    return node.tag == "link" and bool(link_rel_tokens(node) & NAV_LINK_RELS)


def extracted_href(href: str) -> tuple[str | None, str]:
    match = OPEN_ANCILLARY_RE.match(href)
    if match:
        return match.group(2), "javascript-open-ancillary"
    return href, "hyperlink"


@dataclass(frozen=True)
class ResolvedTarget:
    is_internal: bool
    raw_navigation_target: str | None
    resolved: str | None
    path: str | None
    fragment: str | None
    query: str | None


def resolve_target(source_path: str, raw_target: str | None) -> ResolvedTarget:
    if raw_target is None:
        return ResolvedTarget(False, None, None, None, None, None)
    navigation_target, _ = extracted_href(raw_target)
    if navigation_target is None:
        return ResolvedTarget(False, None, None, None, None, None)
    value = navigation_target.strip()
    if not value:
        value = ""
    split = urlsplit(value)
    scheme = split.scheme.lower()
    host = (split.hostname or "").lower()
    if scheme and scheme not in {"http", "https"}:
        return ResolvedTarget(False, navigation_target, None, None, None, None)
    if split.netloc and host not in INTERNAL_HOSTS:
        return ResolvedTarget(False, navigation_target, None, None, None, None)
    if scheme in {"http", "https"} and host not in INTERNAL_HOSTS:
        return ResolvedTarget(False, navigation_target, None, None, None, None)

    target_path = unquote(split.path).replace("\\", "/")
    if split.netloc or target_path.startswith("/"):
        target_path = target_path.lstrip("/")
    elif target_path:
        target_path = posixpath.join(posixpath.dirname(source_path), target_path)
    else:
        target_path = source_path
    target_path = posixpath.normpath(target_path)
    if target_path == "." or target_path.startswith("../") or target_path == "..":
        return ResolvedTarget(True, navigation_target, None, None, split.fragment or None, split.query or None)
    suffix = ""
    if split.query:
        suffix += f"?{split.query}"
    if split.fragment:
        suffix += f"#{split.fragment}"
    return ResolvedTarget(
        True,
        navigation_target,
        target_path + suffix,
        target_path,
        unquote(split.fragment) if split.fragment else None,
        split.query or None,
    )


def asset_kind(node: Element) -> str:
    if node.tag == "link":
        rels = link_rel_tokens(node)
        if "stylesheet" in rels:
            return "stylesheet"
        if "icon" in rels:
            return "icon"
        return "linked-resource"
    if node.tag == "script":
        return "script"
    if node.tag == "img":
        return "image"
    if node.tag in {"audio", "video", "source"}:
        return "media"
    if node.tag in {"iframe", "object", "embed"}:
        return "embedded-resource"
    return "inline-visual"


def asset_rights(target_path: str | None, manifest_row: dict[str, str] | None) -> str:
    if target_path is None:
        return RIGHTS_UNDETERMINED
    lowered = target_path.lower()
    if lowered.startswith("mathjax/"):
        return RIGHTS_MATHJAX
    if lowered.startswith("random/apps/cards/"):
        return RIGHTS_CARDS
    if "monty" in lowered and lowered.endswith((".svg", ".png", ".jpg", ".jpeg", ".webp")):
        return RIGHTS_MONTY
    if lowered.startswith("random/biographies/") or lowered.startswith("random/data/"):
        return RIGHTS_UNCLEARED
    if manifest_row is not None and lowered.startswith("random/"):
        return RIGHTS_RANDOM
    return RIGHTS_UNDETERMINED


def source_label(node: Element, entity_type: str) -> str:
    if entity_type == "asset":
        return normalized_text(
            node.attrs.get("alt", "")
            or node.attrs.get("title", "")
            or resource_attribute(node)[1]
            or ""
        )
    return element_text(node)


def load_inputs(root: Path) -> tuple[dict[str, Any], bytes, dict[str, dict[str, str]], list[dict[str, Any]]]:
    receipt_path = path_from_posix(root, RECEIPT_REL)
    manifest_path = path_from_posix(root, MANIFEST_REL)
    receipt_bytes = receipt_path.read_bytes()
    manifest_bytes = manifest_path.read_bytes()
    try:
        receipt = json.loads(receipt_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BackendError(f"invalid UTF-8 JSON freeze receipt: {exc}") from exc

    if receipt.get("schema") != "o006.random.source-freeze.v1":
        raise BackendError("unexpected source-freeze schema")
    if len(manifest_bytes) != receipt.get("source_manifest_bytes"):
        raise BackendError("source manifest byte count differs from freeze receipt")
    if sha256_bytes(manifest_bytes) != receipt.get("source_manifest_sha256"):
        raise BackendError("source manifest SHA-256 differs from freeze receipt")

    manifest_text = manifest_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(manifest_text, newline=""))
    expected_columns = [
        "relative_path", "role", "url", "bytes", "sha256", "content_type",
        "last_modified", "etag",
    ]
    if reader.fieldnames != expected_columns:
        raise BackendError(f"unexpected source manifest columns: {reader.fieldnames}")
    rows = list(reader)
    if any(None in row for row in rows):
        raise BackendError("malformed source manifest row")
    manifest: dict[str, dict[str, str]] = {}
    for row in rows:
        relative_path = row["relative_path"]
        if relative_path in manifest:
            raise BackendError(f"duplicate source manifest path: {relative_path}")
        if not SHA256_RE.fullmatch(row["sha256"]):
            raise BackendError(f"invalid manifest SHA-256 for {relative_path}")
        manifest[relative_path] = row

    core_paths = receipt.get("core_paths")
    if not isinstance(core_paths, list) or len(core_paths) != receipt.get("core_files"):
        raise BackendError("core_paths/core_files mismatch")
    if len(core_paths) != 29 or len(set(core_paths)) != 29:
        raise BackendError("the O006 core must contain exactly 29 unique paths")

    sources: list[dict[str, Any]] = []
    total_bytes = 0
    for document_order, source_path in enumerate(core_paths, 1):
        if not isinstance(source_path, str):
            raise BackendError("non-string core path")
        row = manifest.get(source_path)
        if row is None or row["role"] != "core":
            raise BackendError(f"core path missing a core manifest row: {source_path}")
        source_file = path_from_posix(path_from_posix(root, UPSTREAM_REL), source_path)
        data = source_file.read_bytes()
        expected_bytes = int(row["bytes"])
        if len(data) != expected_bytes:
            raise BackendError(f"source byte mismatch: {source_path}")
        actual_sha256 = sha256_bytes(data)
        if actual_sha256 != row["sha256"]:
            raise BackendError(f"source SHA-256 mismatch: {source_path}")
        try:
            html = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise BackendError(f"source is not UTF-8: {source_path}") from exc
        total_bytes += len(data)
        sources.append(
            {
                "document_order": document_order,
                "source_path": source_path,
                "source_url": row["url"],
                "source_bytes": len(data),
                "source_sha256": actual_sha256,
                "html": html,
            }
        )
    if total_bytes != receipt.get("core_bytes"):
        raise BackendError("core byte total differs from freeze receipt")
    return receipt, receipt_bytes, manifest, sources


def canonical_positive_integer(value: str, *, field_name: str, row_number: int) -> int:
    """Parse an unsigned canonical decimal integer from a ledger cell."""
    if not value or not value.isascii() or not value.isdecimal():
        raise BackendError(
            f"translation ledger row {row_number} has invalid {field_name}: {value!r}"
        )
    parsed = int(value)
    if parsed < 1 or str(parsed) != value:
        raise BackendError(
            f"translation ledger row {row_number} has non-canonical {field_name}: {value!r}"
        )
    return parsed


def load_translation_bindings(
    root: Path, sources: list[dict[str, Any]]
) -> tuple[bytes, dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Verify and bind the exact id-ID translation ledger to core pages.

    The ledger is a canonical, contiguous prefix of the frozen core order. A
    row is admitted only when both its authority-side and live target-side byte
    claims verify. The resolved target must stay below source/id-ID even if a
    path component is a symlink.
    """
    ledger_path = path_from_posix(root, TRANSLATION_LEDGER_REL)
    ledger_bytes = ledger_path.read_bytes()
    if ledger_bytes.startswith(b"\xef\xbb\xbf"):
        raise BackendError("translation ledger must be UTF-8 without BOM")
    try:
        ledger_text = ledger_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BackendError(f"translation ledger is not UTF-8: {exc}") from exc

    reader = csv.DictReader(io.StringIO(ledger_text, newline=""))
    if reader.fieldnames != TRANSLATION_LEDGER_COLUMNS:
        raise BackendError(
            f"unexpected translation ledger columns: {reader.fieldnames}"
        )
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise BackendError("malformed translation ledger row")
    if len(rows) > len(sources):
        raise BackendError("translation ledger contains more rows than the frozen core")

    target_root = path_from_posix(root, PurePosixPath("source/id-ID")).resolve()
    source_paths_seen: set[str] = set()
    target_paths_seen: set[str] = set()
    bindings: dict[str, dict[str, Any]] = {}
    verified_rows: list[dict[str, Any]] = []

    for row_number, row in enumerate(rows, 2):
        expected_ordinal = row_number - 1
        ordinal = canonical_positive_integer(
            row["ordinal"], field_name="ordinal", row_number=row_number
        )
        if ordinal != expected_ordinal:
            raise BackendError(
                f"translation ledger row {row_number} is not in contiguous ordinal order"
            )
        source = sources[ordinal - 1]
        source_path = row["source_path"]
        if source_path != source["source_path"]:
            raise BackendError(
                f"translation ledger ordinal {ordinal} is not the canonical core path: "
                f"expected {source['source_path']}, found {source_path}"
            )
        if source_path in source_paths_seen:
            raise BackendError(f"duplicate translation source path: {source_path}")
        source_paths_seen.add(source_path)
        if row["status"] != "complete":
            raise BackendError(
                f"translation ledger ordinal {ordinal} has unsupported status: "
                f"{row['status']!r}"
            )

        source_bytes = canonical_positive_integer(
            row["source_bytes"], field_name="source_bytes", row_number=row_number
        )
        if source_bytes != source["source_bytes"]:
            raise BackendError(
                f"translation ledger source byte mismatch at ordinal {ordinal}"
            )
        if not SHA256_RE.fullmatch(row["source_sha256"]):
            raise BackendError(
                f"translation ledger has invalid source SHA-256 at ordinal {ordinal}"
            )
        if row["source_sha256"] != source["source_sha256"]:
            raise BackendError(
                f"translation ledger source SHA-256 mismatch at ordinal {ordinal}"
            )

        target_path = row["target_path"]
        if "\\" in target_path:
            raise BackendError(
                f"translation ledger target path must use POSIX separators: {target_path}"
            )
        target_rel = PurePosixPath(target_path)
        if (
            target_rel.is_absolute()
            or not target_path
            or str(target_rel) != target_path
            or "." in target_rel.parts
            or ".." in target_rel.parts
            or target_rel.parts[:2] != ("source", "id-ID")
        ):
            raise BackendError(f"unsafe or non-canonical translation target path: {target_path}")
        expected_target_path = str(PurePosixPath("source/id-ID") / source_path)
        if target_path != expected_target_path:
            raise BackendError(
                f"translation target path does not mirror its source at ordinal {ordinal}: "
                f"expected {expected_target_path}, found {target_path}"
            )
        if target_path in target_paths_seen:
            raise BackendError(f"duplicate translation target path: {target_path}")
        target_paths_seen.add(target_path)

        target_file = path_from_posix(root, target_rel)
        resolved_target = target_file.resolve(strict=True)
        try:
            resolved_target.relative_to(target_root)
        except ValueError as exc:
            raise BackendError(
                f"translation target resolves outside source/id-ID: {target_path}"
            ) from exc
        if not resolved_target.is_file():
            raise BackendError(f"translation target is not a file: {target_path}")
        target_data = resolved_target.read_bytes()
        target_bytes = canonical_positive_integer(
            row["target_bytes"], field_name="target_bytes", row_number=row_number
        )
        if len(target_data) != target_bytes:
            raise BackendError(
                f"translation target byte mismatch at ordinal {ordinal}: {target_path}"
            )
        if not SHA256_RE.fullmatch(row["target_sha256"]):
            raise BackendError(
                f"translation ledger has invalid target SHA-256 at ordinal {ordinal}"
            )
        target_sha256 = sha256_bytes(target_data)
        if target_sha256 != row["target_sha256"]:
            raise BackendError(
                f"translation target SHA-256 mismatch at ordinal {ordinal}: {target_path}"
            )

        binding = {
            "translation_ledger_ordinal": ordinal,
            "translation_status": "complete",
            "translation_target_bytes": target_bytes,
            "translation_target_locale": TARGET_LOCALE,
            "translation_target_path": target_path,
            "translation_target_sha256": target_sha256,
        }
        bindings[source_path] = binding
        verified_rows.append(
            {
                "ordinal": ordinal,
                "source_bytes": source_bytes,
                "source_path": source_path,
                "source_sha256": source["source_sha256"],
                "status": row["status"],
                "target_bytes": target_bytes,
                "target_locale": TARGET_LOCALE,
                "target_path": target_path,
                "target_sha256": target_sha256,
            }
        )

    return ledger_bytes, bindings, verified_rows


def entity_id(document_order: int, entity_type: str, kind_order: int) -> str:
    return f"O006-{document_order:03d}-{TYPE_CODE[entity_type]:02d}-{kind_order:04d}"


def injected_id(document_order: int, entity_type: str, kind_order: int) -> str:
    return f"o006-{document_order:03d}-{TYPE_CODE[entity_type]:02d}-{kind_order:04d}"


def parse_document(
    source: dict[str, Any], translation_binding: dict[str, Any] | None
) -> dict[str, Any]:
    parser = CorpusHTMLParser()
    parser.feed(source["html"])
    parser.close()
    html_nodes = [node for node in parser.elements if node.tag == "html"]
    if len(html_nodes) != 1:
        raise BackendError(f"expected one html element: {source['source_path']}")
    title_nodes = [node for node in parser.elements if node.tag == "title"]
    title = element_text(title_nodes[0]) if title_nodes else ""

    native_nodes: dict[str, list[Element]] = defaultdict(list)
    for node in parser.elements:
        native_id = node.attrs.get("id")
        if native_id:
            native_nodes[native_id].append(node)

    math_owners: dict[Element, None] = {}
    uncovered_math: list[dict[str, Any]] = []
    for piece in parser.text_pieces:
        if not MATH_MARKER_RE.search(piece.data):
            continue
        owner: Element | None = piece.parent
        while owner is not None and owner.tag != "#document" and not text_owner(owner):
            owner = owner.parent
        if owner is None or owner.tag == "#document":
            uncovered_math.append({"line": piece.line, "column": piece.column})
        else:
            math_owners[owner] = None
    if uncovered_math:
        raise BackendError(
            f"math markers without structural text owner in {source['source_path']}: "
            f"{uncovered_math}"
        )

    descriptors: list[tuple[int, int, Element, str]] = []
    html_node = html_nodes[0]
    descriptors.append((html_node.event_order, TYPE_PRIORITY["document"], html_node, "document"))
    for node in parser.elements:
        if node.tag in {"h1", "h2", "h3", "h4"}:
            descriptors.append((node.event_order, TYPE_PRIORITY["section"], node, "section"))
        if node.tag == "div" and "unit" in node.classes():
            descriptors.append((node.event_order, TYPE_PRIORITY["unit"], node, "unit"))
        if node.tag == "details":
            descriptors.append((node.event_order, TYPE_PRIORITY["disclosure"], node, "disclosure"))
        if node in math_owners:
            descriptors.append((node.event_order, TYPE_PRIORITY["math_text"], node, "math_text"))
        if node.tag == "figure":
            descriptors.append((node.event_order, TYPE_PRIORITY["figure"], node, "figure"))
        if is_asset_node(node):
            descriptors.append((node.event_order, TYPE_PRIORITY["asset"], node, "asset"))
        if is_link_node(node):
            href = node.attrs.get("href", "")
            if resolve_target(source["source_path"], href).is_internal:
                descriptors.append((node.event_order, TYPE_PRIORITY["internal_link"], node, "internal_link"))
    descriptors.sort(key=lambda item: (item[0], item[1]))

    kind_counts: Counter[str] = Counter()
    node_entities: dict[Element, dict[str, str]] = defaultdict(dict)
    records: list[dict[str, Any]] = []
    for source_order, (_, _, node, entity_type) in enumerate(descriptors, 1):
        kind_counts[entity_type] += 1
        kind_order = kind_counts[entity_type]
        stable_id = entity_id(source["document_order"], entity_type, kind_order)
        native_id = node.attrs.get("id") or None
        duplicate_count = len(native_nodes[native_id]) if native_id else 0
        occurrence: int | None = None
        if native_id:
            occurrence = native_nodes[native_id].index(node) + 1
        target_id = native_id or injected_id(source["document_order"], entity_type, kind_order)
        label = title if entity_type == "document" else source_label(node, entity_type)
        page_binding = translation_binding or {
            "translation_ledger_ordinal": None,
            "translation_status": "untranslated",
            "translation_target_bytes": None,
            "translation_target_locale": None,
            "translation_target_path": None,
            "translation_target_sha256": None,
        }
        record: dict[str, Any] = {
            "component_rights_class": RIGHTS_RANDOM,
            "document_order": source["document_order"],
            "dom_path": node.dom_path,
            "entity_id": stable_id,
            "entity_type": entity_type,
            "hierarchy": [],
            "html_tag": node.tag,
            "injected_target_id": None if native_id else target_id,
            "kind_order": kind_order,
            "native_id": native_id,
            "native_id_duplicate": duplicate_count > 1,
            "native_id_duplicate_count": duplicate_count,
            "native_id_occurrence": occurrence,
            "parent_entity_id": None,
            "schema_version": ENTITY_SCHEMA_VERSION,
            "section_entity_id": None,
            "sibling_order": 1,
            "source_column": node.column,
            "source_line": node.line,
            "source_order": source_order,
            "source_path": source["source_path"],
            "source_sha256": source["source_sha256"],
            "source_text": label,
            "source_text_sha256": sha256_bytes(label.encode("utf-8")),
            "source_url": source["source_url"],
            "target_id": target_id,
            **page_binding,
        }
        if entity_type == "section":
            record["section_level"] = int(node.tag[1])
        elif entity_type == "unit":
            direct_paragraphs = [
                child for child in node.children
                if isinstance(child, Element) and child.tag == "p"
            ]
            semantic_classes: list[str] = []
            for paragraph in direct_paragraphs:
                for class_name in paragraph.classes():
                    if class_name in {"app", "dfn", "math", "stat"} and class_name not in semantic_classes:
                        semantic_classes.append(class_name)
            unit_type = semantic_classes[0] if len(semantic_classes) == 1 else "unclassified"
            record.update(
                {
                    # Final exercise classification is assigned after section
                    # ancestry is available.  Native app/stat is one of two
                    # independent positive source cues.
                    "exercise_like": unit_type in {"app", "stat"},
                    "exercise_like_basis": (
                        "native-unit-type"
                        if unit_type in {"app", "stat"}
                        else "not-designated"
                    ),
                    "unit_classes": node.classes(),
                    "unit_type": unit_type,
                }
            )
        elif entity_type == "disclosure":
            record["details_parent_entity_id"] = None
        elif entity_type == "math_text":
            text = label
            record.update(
                {
                    "math_display_count": text.count("\\["),
                    "math_dollar_count": text.count("$$") // 2,
                    "math_inline_count": text.count("\\("),
                }
            )
        elif entity_type == "figure":
            record["figure_asset_entity_ids"] = []
        elif entity_type == "asset":
            attribute, raw_target = resource_attribute(node)
            resolved = resolve_target(source["source_path"], raw_target)
            record.update(
                {
                    "asset_attribute": attribute,
                    "asset_kind": asset_kind(node),
                    "asset_manifest_role": None,
                    "asset_target": raw_target,
                    "asset_target_bytes": None,
                    "asset_target_fragment": resolved.fragment,
                    "asset_target_path": resolved.path,
                    "asset_target_resolved": resolved.resolved,
                    "asset_target_sha256": None,
                    "asset_target_status": "inline" if raw_target is None else "unclassified",
                    "asset_target_url": None,
                }
            )
        elif entity_type == "internal_link":
            raw_target = node.attrs.get("href", "")
            resolved = resolve_target(source["source_path"], raw_target)
            _, href_kind = extracted_href(raw_target)
            if node.tag == "link":
                href_kind = "document-relation"
            record.update(
                {
                    "link_kind": href_kind,
                    "link_target": raw_target,
                    "link_target_entity_ids": [],
                    "link_target_fragment": resolved.fragment,
                    "link_target_path": resolved.path,
                    "link_target_resolved": resolved.resolved,
                    "link_target_status": "unclassified",
                }
            )
        records.append(record)
        node_entities[node][entity_type] = stable_id

    # A DOM element can satisfy more than one catalog category (for example, a
    # details element containing bare display math).  It still receives one
    # injectable HTML anchor, shared by all stable entities for that element.
    records_by_id = {record["entity_id"]: record for record in records}
    for node, entity_types in node_entities.items():
        if node.attrs.get("id"):
            continue
        primary_type = min(entity_types, key=lambda value: TYPE_PRIORITY[value])
        shared_target = records_by_id[entity_types[primary_type]]["injected_target_id"]
        for stable_id in entity_types.values():
            records_by_id[stable_id]["injected_target_id"] = shared_target
            records_by_id[stable_id]["target_id"] = shared_target

    injected_nodes: dict[str, Element] = {}
    native_id_set = set(native_nodes)
    for node, entity_types in node_entities.items():
        sample = records_by_id[next(iter(entity_types.values()))]
        injected = sample["injected_target_id"]
        if injected is None:
            continue
        if injected in native_id_set:
            raise BackendError(
                f"injected/native target collision in {source['source_path']}: {injected}"
            )
        previous = injected_nodes.get(injected)
        if previous is not None and previous is not node:
            raise BackendError(
                f"duplicate injected target in {source['source_path']}: {injected}"
            )
        injected_nodes[injected] = node

    section_parent: dict[str, str] = {}
    section_for_node: dict[Element, str | None] = {}
    section_stack: list[tuple[int, str]] = []
    section_nodes = {
        node: node_entities[node]["section"]
        for node in parser.elements if "section" in node_entities.get(node, {})
    }
    for node in parser.elements:
        if node in section_nodes:
            level = int(node.tag[1])
            while section_stack and section_stack[-1][0] >= level:
                section_stack.pop()
            parent = section_stack[-1][1] if section_stack else node_entities[html_node]["document"]
            section_id = section_nodes[node]
            section_parent[section_id] = parent
            section_stack.append((level, section_id))
            section_for_node[node] = section_id
        else:
            section_for_node[node] = section_stack[-1][1] if section_stack else None

    primary_priority = [
        "section", "unit", "disclosure", "figure", "math_text", "internal_link", "asset"
    ]
    primary_by_node: dict[Element, str] = {}
    for node, entity_types in node_entities.items():
        for entity_type in primary_priority:
            if entity_type in entity_types:
                primary_by_node[node] = entity_types[entity_type]
                break

    document_id = node_entities[html_node]["document"]
    entity_node: dict[str, Element] = {
        stable_id: node
        for node, entity_types in node_entities.items()
        for stable_id in entity_types.values()
    }
    for record in records:
        stable_id = record["entity_id"]
        node = entity_node[stable_id]
        if record["entity_type"] == "document":
            record["section_entity_id"] = None
            continue
        if record["entity_type"] == "section":
            record["parent_entity_id"] = section_parent[stable_id]
            record["section_entity_id"] = stable_id
            continue
        ancestor = node.parent
        parent_id: str | None = None
        while ancestor is not None and ancestor.tag != "#document":
            candidate = primary_by_node.get(ancestor)
            if candidate is not None:
                parent_id = candidate
                break
            ancestor = ancestor.parent
        section_id = section_for_node.get(node)
        record["section_entity_id"] = section_id
        record["parent_entity_id"] = parent_id or section_id or document_id

    sibling_counts: Counter[str] = Counter()
    for record in records:
        parent_key = record["parent_entity_id"] or ""
        sibling_counts[parent_key] += 1
        record["sibling_order"] = sibling_counts[parent_key]

    def hierarchy_for(stable_id: str, trail: set[str] | None = None) -> list[str]:
        trail = set() if trail is None else trail
        if stable_id in trail:
            raise BackendError(f"entity hierarchy cycle in {source['source_path']}: {stable_id}")
        trail.add(stable_id)
        record = records_by_id[stable_id]
        parent_id = record["parent_entity_id"]
        if parent_id is None:
            result = [stable_id]
        else:
            result = hierarchy_for(parent_id, trail) + [stable_id]
        trail.remove(stable_id)
        return result

    for record in records:
        record["hierarchy"] = hierarchy_for(record["entity_id"])

    # Native red-die app/stat units are exercise-like even outside an exercise
    # section.  Conversely, computational exercises commonly use the blue-die
    # math type, so semantic h1-h4 section ancestry is an independent cue.  Do
    # not use the generic entity hierarchy here: structural math containers can
    # intervene between a unit and its active heading stack.
    for record in records:
        if record["entity_type"] != "unit":
            continue
        basis = exercise_designation_basis(record, records_by_id)
        record["exercise_like"] = basis != "not-designated"
        record["exercise_like_basis"] = basis

    for record in records:
        if record["entity_type"] == "disclosure":
            node = entity_node[record["entity_id"]]
            unit = nearest_ancestor(node, lambda candidate: "unit" in node_entities.get(candidate, {}))
            record["details_parent_entity_id"] = (
                node_entities[unit]["unit"] if unit is not None else record["parent_entity_id"]
            )
        elif record["entity_type"] == "figure":
            figure_node = entity_node[record["entity_id"]]
            asset_ids: list[str] = []
            for node, entity_types in node_entities.items():
                if "asset" not in entity_types:
                    continue
                ancestor = node.parent
                while ancestor is not None and ancestor.tag != "#document":
                    if ancestor is figure_node:
                        asset_ids.append(entity_types["asset"])
                        break
                    ancestor = ancestor.parent
            record["figure_asset_entity_ids"] = sorted(
                asset_ids, key=lambda stable_id: records_by_id[stable_id]["source_order"]
            )

    duplicate_native_ids = []
    for native_id, nodes in sorted(native_nodes.items()):
        if len(nodes) <= 1:
            continue
        duplicate_native_ids.append(
            {
                "entity_ids": [
                    stable_id
                    for node in nodes
                    for stable_id in node_entities.get(node, {}).values()
                ],
                "native_id": native_id,
                "occurrences": len(nodes),
                "source_columns": [node.column for node in nodes],
                "source_lines": [node.line for node in nodes],
                "source_path": source["source_path"],
            }
        )

    all_native = {native_id: nodes[:] for native_id, nodes in native_nodes.items()}
    return {
        "all_native": all_native,
        "duplicate_native_ids": duplicate_native_ids,
        "entity_node": entity_node,
        "node_entities": node_entities,
        "parser": parser,
        "records": records,
    }


def classify_targets(
    parsed_documents: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    manifest: dict[str, dict[str, str]],
) -> None:
    document_entity: dict[str, str] = {}
    native_entities: dict[tuple[str, str], list[str]] = defaultdict(list)
    native_outside_catalog: set[tuple[str, str]] = set()
    for source, parsed in zip(sources, parsed_documents):
        for record in parsed["records"]:
            if record["entity_type"] == "document":
                document_entity[source["source_path"]] = record["entity_id"]
        for native_id, nodes in parsed["all_native"].items():
            for node in nodes:
                entity_types = parsed["node_entities"].get(node, {})
                target_id = next(
                    (
                        entity_types[entity_type]
                        for entity_type in (
                            "section", "unit", "disclosure", "figure",
                            "math_text", "internal_link", "asset",
                        )
                        if entity_type in entity_types
                    ),
                    None,
                )
                if target_id is None:
                    native_outside_catalog.add((source["source_path"], native_id))
                else:
                    native_entities[(source["source_path"], native_id)].append(target_id)

    for parsed in parsed_documents:
        for record in parsed["records"]:
            if record["entity_type"] == "asset":
                path = record["asset_target_path"]
                row = manifest.get(path) if path else None
                record["component_rights_class"] = asset_rights(path, row)
                if record["asset_target"] is None:
                    status = "inline"
                elif path is None:
                    status = "external-or-invalid"
                elif row is None:
                    status = "unmanifested-internal"
                else:
                    status = "manifest-resource"
                    record["asset_manifest_role"] = row["role"]
                    record["asset_target_bytes"] = int(row["bytes"])
                    record["asset_target_sha256"] = row["sha256"]
                    record["asset_target_url"] = row["url"]
                record["asset_target_status"] = status
            elif record["entity_type"] == "internal_link":
                path = record["link_target_path"]
                fragment = record["link_target_fragment"]
                targets: list[str] = []
                if path is None:
                    status = "unresolved-internal"
                elif path in document_entity:
                    if fragment:
                        targets = native_entities.get((path, fragment), [])[:]
                        if len(targets) == 1:
                            status = "resolved-entity"
                        elif len(targets) > 1:
                            status = "ambiguous-native-id"
                        elif (path, fragment) in native_outside_catalog:
                            status = "native-target-outside-catalog"
                        else:
                            status = "missing-fragment"
                    else:
                        targets = [document_entity[path]]
                        status = "resolved-document"
                elif path in manifest:
                    status = "manifest-resource-fragment-unchecked" if fragment else "manifest-resource"
                elif path in KNOWN_UPSTREAM_DEFECT_PATHS:
                    status = "known-upstream-defect"
                else:
                    # The freeze is intentionally bounded to this core and its
                    # closure, so absence from it does not prove an upstream
                    # link is broken.
                    status = "out-of-freeze-internal"
                record["link_target_entity_ids"] = sorted(targets)
                record["link_target_status"] = status


def validate_records(records: list[dict[str, Any]]) -> None:
    required_common = {
        "component_rights_class", "document_order", "dom_path", "entity_id",
        "entity_type", "hierarchy", "html_tag", "injected_target_id",
        "kind_order", "native_id", "native_id_duplicate",
        "native_id_duplicate_count", "native_id_occurrence", "parent_entity_id",
        "schema_version", "section_entity_id", "sibling_order", "source_column",
        "source_line", "source_order", "source_path", "source_sha256",
        "source_text", "source_text_sha256", "source_url", "target_id",
        "translation_ledger_ordinal", "translation_status",
        "translation_target_bytes", "translation_target_locale",
        "translation_target_path", "translation_target_sha256",
    }
    records_by_id = {record["entity_id"]: record for record in records}
    seen: set[str] = set()
    expected_source_order: Counter[int] = Counter()
    for record in records:
        missing = required_common - set(record)
        if missing:
            raise BackendError(f"entity missing required fields {sorted(missing)}")
        stable_id = record["entity_id"]
        if stable_id in seen:
            raise BackendError(f"duplicate stable entity ID: {stable_id}")
        seen.add(stable_id)
        if record["schema_version"] != ENTITY_SCHEMA_VERSION:
            raise BackendError(f"wrong entity schema version: {stable_id}")
        if not SHA256_RE.fullmatch(record["source_sha256"]):
            raise BackendError(f"invalid source SHA-256: {stable_id}")
        if not SHA256_RE.fullmatch(record["source_text_sha256"]):
            raise BackendError(f"invalid text SHA-256: {stable_id}")
        if sha256_bytes(record["source_text"].encode("utf-8")) != record["source_text_sha256"]:
            raise BackendError(f"text SHA-256 mismatch: {stable_id}")
        if record["translation_status"] == "complete":
            if not isinstance(record["translation_ledger_ordinal"], int):
                raise BackendError(f"complete entity lacks ledger ordinal: {stable_id}")
            if record["translation_target_locale"] != TARGET_LOCALE:
                raise BackendError(f"complete entity has wrong target locale: {stable_id}")
            if not isinstance(record["translation_target_bytes"], int):
                raise BackendError(f"complete entity lacks target bytes: {stable_id}")
            if not isinstance(record["translation_target_path"], str):
                raise BackendError(f"complete entity lacks target path: {stable_id}")
            if not isinstance(record["translation_target_sha256"], str) or not SHA256_RE.fullmatch(
                record["translation_target_sha256"]
            ):
                raise BackendError(f"complete entity has invalid target SHA-256: {stable_id}")
        elif record["translation_status"] == "untranslated":
            nullable_fields = (
                "translation_ledger_ordinal",
                "translation_target_bytes",
                "translation_target_locale",
                "translation_target_path",
                "translation_target_sha256",
            )
            if any(record[field_name] is not None for field_name in nullable_fields):
                raise BackendError(f"untranslated entity has target binding: {stable_id}")
        else:
            raise BackendError(f"invalid translation status: {stable_id}")
        if record["hierarchy"][-1] != stable_id:
            raise BackendError(f"hierarchy does not terminate at entity: {stable_id}")
        expected_source_order[record["document_order"]] += 1
        if record["source_order"] != expected_source_order[record["document_order"]]:
            raise BackendError(f"non-contiguous source order: {stable_id}")
        if record["native_id"] is None:
            if record["injected_target_id"] != record["target_id"]:
                raise BackendError(f"missing injected target ID: {stable_id}")
        elif record["injected_target_id"] is not None:
            raise BackendError(f"unexpected injected target ID: {stable_id}")
        if record["entity_type"] == "unit":
            expected_basis = exercise_designation_basis(record, records_by_id)
            if record["exercise_like_basis"] != expected_basis:
                raise BackendError(f"incorrect exercise basis: {stable_id}")
            expected_exercise = expected_basis != "not-designated"
            if record["exercise_like"] is not expected_exercise:
                raise BackendError(f"inconsistent exercise classification: {stable_id}")
    parent_ids = {record["parent_entity_id"] for record in records if record["parent_entity_id"]}
    if not parent_ids.issubset(seen):
        raise BackendError(f"missing parent entity IDs: {sorted(parent_ids - seen)}")
    page_bindings: dict[str, tuple[Any, ...]] = {}
    binding_fields = (
        "translation_ledger_ordinal",
        "translation_status",
        "translation_target_bytes",
        "translation_target_locale",
        "translation_target_path",
        "translation_target_sha256",
    )
    for record in records:
        binding = tuple(record[field_name] for field_name in binding_fields)
        prior = page_bindings.setdefault(record["source_path"], binding)
        if binding != prior:
            raise BackendError(
                f"inconsistent translation binding within page: {record['source_path']}"
            )


def make_relations(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    relations: list[dict[str, str]] = []
    document_order_by_entity = {
        record["entity_id"]: record["document_order"] for record in records
    }

    def add(
        relation_type: str,
        source_entity_id: str,
        target_entity_id: str | None,
        target_ref: str | None,
        source_path: str,
        source_order: int,
    ) -> None:
        relations.append(
            {
                "relation_id": "",
                "relation_type": relation_type,
                "schema_version": RELATION_SCHEMA_VERSION,
                "source_entity_id": source_entity_id,
                "source_order": str(source_order),
                "source_path": source_path,
                "target_entity_id": target_entity_id or "",
                "target_ref": target_ref or "",
            }
        )

    for record in records:
        if record["parent_entity_id"]:
            add(
                "contains",
                record["parent_entity_id"],
                record["entity_id"],
                None,
                record["source_path"],
                record["source_order"],
            )
        if record["entity_type"] == "disclosure" and record["details_parent_entity_id"]:
            add(
                "details-parent",
                record["entity_id"],
                record["details_parent_entity_id"],
                None,
                record["source_path"],
                record["source_order"],
            )
        elif record["entity_type"] == "asset":
            add(
                "asset-target",
                record["entity_id"],
                None,
                record["asset_target_resolved"] or record["asset_target"],
                record["source_path"],
                record["source_order"],
            )
        elif record["entity_type"] == "internal_link":
            targets = record["link_target_entity_ids"]
            if targets:
                relation_type = (
                    "internal-link-target-ambiguous"
                    if record["link_target_status"] == "ambiguous-native-id"
                    else "internal-link-target"
                )
                for target in targets:
                    add(
                        relation_type,
                        record["entity_id"],
                        target,
                        record["link_target_resolved"],
                        record["source_path"],
                        record["source_order"],
                    )
            else:
                add(
                    "internal-link-reference",
                    record["entity_id"],
                    None,
                    record["link_target_resolved"] or record["link_target"],
                    record["source_path"],
                    record["source_order"],
                )
    relations.sort(
        key=lambda row: (
            document_order_by_entity[row["source_entity_id"]],
            int(row["source_order"]),
            row["relation_type"],
            row["target_entity_id"],
            row["target_ref"],
        )
    )
    for index, row in enumerate(relations, 1):
        row["relation_id"] = f"O006-90-{index:06d}"
    return relations


def csv_bytes(rows: list[dict[str, str]]) -> bytes:
    fieldnames = [
        "schema_version", "relation_id", "relation_type", "source_entity_id",
        "target_entity_id", "target_ref", "source_path", "source_order",
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def build(root: Path) -> tuple[dict[PurePosixPath, bytes], dict[str, Any]]:
    freeze_receipt, freeze_receipt_bytes, manifest, sources = load_inputs(root)
    ledger_bytes, translation_bindings, verified_translation_rows = (
        load_translation_bindings(root, sources)
    )
    parsed_documents = [
        parse_document(source, translation_bindings.get(source["source_path"]))
        for source in sources
    ]
    classify_targets(parsed_documents, sources, manifest)
    records = [
        record
        for parsed in parsed_documents
        for record in parsed["records"]
    ]
    validate_records(records)
    relations = make_relations(records)

    entities_data = b"".join(canonical_json_bytes(record) for record in records)
    relations_data = csv_bytes(relations)
    schema_path = path_from_posix(root, ENTITY_SCHEMA_REL)
    script_path = Path(__file__).resolve()
    schema_data = schema_path.read_bytes()
    script_data = script_path.read_bytes()

    duplicate_native_ids = [
        duplicate
        for parsed in parsed_documents
        for duplicate in parsed["duplicate_native_ids"]
    ]
    counts = dict(sorted(Counter(record["entity_type"] for record in records).items()))
    unit_unresolved = [
        record["entity_id"]
        for record in records
        if record["entity_type"] == "unit" and record["unit_type"] == "unclassified"
    ]
    details_without_unit = [
        record["entity_id"]
        for record in records
        if record["entity_type"] == "disclosure"
        and record["details_parent_entity_id"]
        and next(
            parent["entity_type"]
            for parent in records
            if parent["entity_id"] == record["details_parent_entity_id"]
        ) != "unit"
    ]
    assets_undetermined = [
        record["entity_id"]
        for record in records
        if record["entity_type"] == "asset"
        and record["component_rights_class"] in {RIGHTS_UNCLEARED, RIGHTS_UNDETERMINED}
    ]
    unresolved_links = [
        {
            "entity_id": record["entity_id"],
            "source_path": record["source_path"],
            "status": record["link_target_status"],
            "target": record["link_target"],
            "target_resolved": record["link_target_resolved"],
        }
        for record in records
        if record["entity_type"] == "internal_link"
        and record["link_target_status"] in {
            "ambiguous-native-id", "missing-fragment", "unresolved-internal"
        }
    ]
    known_defect_links = [
        {
            "entity_id": record["entity_id"],
            "source_path": record["source_path"],
            "target": record["link_target"],
            "target_resolved": record["link_target_resolved"],
        }
        for record in records
        if record["entity_type"] == "internal_link"
        and record["link_target_status"] == "known-upstream-defect"
    ]
    out_of_freeze_links = sum(
        record["entity_type"] == "internal_link"
        and record["link_target_status"] == "out-of-freeze-internal"
        for record in records
    )
    translated_entity_count = sum(
        record["translation_status"] == "complete" for record in records
    )
    translated_ordinals = [row["ordinal"] for row in verified_translation_rows]
    final_ledger_bytes, final_bindings, final_verified_rows = (
        load_translation_bindings(root, sources)
    )
    if (
        final_ledger_bytes != ledger_bytes
        or final_bindings != translation_bindings
        or final_verified_rows != verified_translation_rows
    ):
        raise BackendError(
            "translation ledger or a bound target changed during backend generation"
        )
    receipt = {
        "core": {
            "bytes": sum(source["source_bytes"] for source in sources),
            "files": len(sources),
            "source_hashes_verified": True,
            "sources": [
                {
                    "bytes": source["source_bytes"],
                    "document_order": source["document_order"],
                    "path": source["source_path"],
                    "sha256": source["source_sha256"],
                    "url": source["source_url"],
                }
                for source in sources
            ],
        },
        "counts": {
            "entities_by_type": counts,
            "entities_total": len(records),
            "relations_total": len(relations),
        },
        "determinism": {
            "csv": "UTF-8 without BOM; RFC 4180 quoting; LF; fixed column and row order",
            "json": "UTF-8 without BOM; sorted keys; LF; JSONL compact / receipt indented",
            "volatile_fields_omitted": True,
        },
        "duplicate_native_ids": duplicate_native_ids,
        "generator": {
            "path": "scripts/generate_random_backend.py",
            "sha256": sha256_bytes(script_data),
        },
        "outputs": {
            "entities.jsonl": {
                "bytes": len(entities_data),
                "records": len(records),
                "sha256": sha256_bytes(entities_data),
            },
            "relations.csv": {
                "bytes": len(relations_data),
                "records": len(relations),
                "sha256": sha256_bytes(relations_data),
            },
        },
        "link_target_audit": {
            "known_upstream_defects": known_defect_links,
            "out_of_freeze_internal_count": out_of_freeze_links,
        },
        "schema": RECEIPT_SCHEMA_VERSION,
        "schemas": {
            "entity": ENTITY_SCHEMA_VERSION,
            "entity_schema_path": "backend/entities.schema.json",
            "entity_schema_sha256": sha256_bytes(schema_data),
            "relation": RELATION_SCHEMA_VERSION,
        },
        "source_freeze": {
            "receipt_path": str(RECEIPT_REL),
            "receipt_sha256": sha256_bytes(freeze_receipt_bytes),
            "schema": freeze_receipt["schema"],
            "source_manifest_path": str(MANIFEST_REL),
            "source_manifest_sha256": freeze_receipt["source_manifest_sha256"],
        },
        "translation_provenance": "OpenAI Codex gpt-5.6-sol, Ultra",
        "translation_binding": {
            "documents": {
                "total": len(sources),
                "translated": len(verified_translation_rows),
                "untranslated": len(sources) - len(verified_translation_rows),
            },
            "entities": {
                "total": len(records),
                "translated": translated_entity_count,
                "untranslated": len(records) - translated_entity_count,
            },
            "ledger_bytes": len(ledger_bytes),
            "ledger_columns": TRANSLATION_LEDGER_COLUMNS,
            "ledger_path": str(TRANSLATION_LEDGER_REL),
            "ledger_rows": len(verified_translation_rows),
            "ledger_sha256": sha256_bytes(ledger_bytes),
            "status_counts": {
                "complete": len(verified_translation_rows),
                "untranslated": len(sources) - len(verified_translation_rows),
            },
            "target_locale": TARGET_LOCALE,
            "translated_document_ordinals": translated_ordinals,
            "verified_rows": verified_translation_rows,
        },
        "unresolved_classification": {
            "asset_rights_entity_ids": assets_undetermined,
            "details_without_unit_parent_entity_ids": details_without_unit,
            "internal_link_targets": unresolved_links,
            "unit_exercise_entity_ids": unit_unresolved,
        },
    }
    receipt_data = canonical_json_bytes(receipt, pretty=True)
    outputs = {
        ENTITIES_REL: entities_data,
        RELATIONS_REL: relations_data,
        BACKEND_RECEIPT_REL: receipt_data,
    }
    summary = {
        "counts": receipt["counts"],
        "duplicate_native_ids": duplicate_native_ids,
        "known_upstream_defect_links": len(known_defect_links),
        "outputs": receipt["outputs"],
        "unresolved_classification_counts": {
            key: len(value)
            for key, value in receipt["unresolved_classification"].items()
        },
    }
    return outputs, summary


def check_or_write(root: Path, outputs: dict[PurePosixPath, bytes], check_only: bool) -> None:
    mismatches: list[str] = []
    for relative_path, expected in outputs.items():
        destination = path_from_posix(root, relative_path)
        if check_only:
            if not destination.is_file():
                mismatches.append(f"missing {relative_path}")
                continue
            actual = destination.read_bytes()
            if actual != expected:
                mismatches.append(
                    f"byte mismatch {relative_path}: expected {sha256_bytes(expected)}, "
                    f"found {sha256_bytes(actual)}"
                )
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(expected)
            if destination.read_bytes() != expected:
                raise BackendError(f"post-write byte verification failed: {relative_path}")
    if mismatches:
        raise BackendError("check-only failed:\n" + "\n".join(mismatches))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="regenerate in memory and verify exact output bytes without writing",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (defaults to the generator's parent repository)",
    )
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        outputs, summary = build(root)
        check_or_write(root, outputs, args.check_only)
    except (BackendError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    mode = "verified" if args.check_only else "written"
    print(json.dumps({"mode": mode, **summary}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
