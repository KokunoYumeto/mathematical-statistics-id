#!/usr/bin/env python3
"""Freeze the bounded, redistributable component closure for O006/C140.

This script intentionally does not read from or write to ``authority/upstream``.
It freezes only:

* the 52 dynamically addressed playing-card faces plus ``Back.svg``;
* the exact Apache-2.0 license for the hosted MathJax 3.1.2 component;
* the primary CC0 authority pages for the card and Monty Hall image sources; and
* the canonical CC0 1.0 legal code shared by those image components.

No biography image, data photograph, or data set is in this component closure.
The check-only path is entirely offline and verifies the exact file set, byte
counts, SHA-256 digests, immutable URL specification, and manifest receipts.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import io
import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority"
ASSET_ROOT = AUTHORITY / "component-assets"
LICENSE_ROOT = AUTHORITY / "component-licenses"
ASSET_MANIFEST = ASSET_ROOT / "URL_MANIFEST.csv"
ASSET_RECEIPT = ASSET_ROOT / "FREEZE_RECEIPT.json"
LICENSE_MANIFEST = LICENSE_ROOT / "URL_MANIFEST.csv"
LICENSE_RECEIPT = LICENSE_ROOT / "FREEZE_RECEIPT.json"

USER_AGENT = "O006-id-ID-component-freezer/1.0 (+local scholarly edition)"
CARD_BASE = "https://www.randomservices.org/random/apps/Cards/"
MATHJAX_LICENSE_URL = (
    "https://raw.githubusercontent.com/mathjax/MathJax/3.1.2/LICENSE"
)
CARD_AUTHORITY_URL = "https://www.me.uk/cards/"
MONTY_AUTHORITY_URL = "https://svgsilh.com/"
CC0_LEGALCODE_URL = (
    "https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt"
)

DENOMINATIONS = (
    "A",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
)
SUITS = ("C", "D", "H", "S")
MANIFEST_FIELDS = (
    "relative_path",
    "component",
    "license",
    "url",
    "final_url",
    "bytes",
    "sha256",
    "content_type",
    "last_modified",
    "etag",
)


@dataclass(frozen=True)
class DownloadSpec:
    set_name: str
    relative_path: str
    component: str
    license_id: str
    url: str
    payload_kind: str


@dataclass(frozen=True)
class DownloadResult:
    spec: DownloadSpec
    data: bytes
    final_url: str
    content_type: str
    last_modified: str
    etag: str


def card_specs() -> tuple[DownloadSpec, ...]:
    faces = tuple(
        DownloadSpec(
            set_name="assets",
            relative_path=f"random/apps/Cards/{denomination}{suit}.svg",
            component="Random playing-card image",
            license_id="CC0-1.0",
            url=f"{CARD_BASE}{denomination}{suit}.svg",
            payload_kind="card-svg",
        )
        for denomination in DENOMINATIONS
        for suit in SUITS
    )
    back = DownloadSpec(
        set_name="assets",
        relative_path="random/apps/Cards/Back.svg",
        component="Random playing-card image",
        license_id="CC0-1.0",
        url=f"{CARD_BASE}Back.svg",
        payload_kind="card-svg",
    )
    result = faces + (back,)
    if len(result) != 53 or len({spec.relative_path for spec in result}) != 53:
        raise RuntimeError("internal error: card specification is not exactly 53 files")
    return result


def license_specs() -> tuple[DownloadSpec, ...]:
    return (
        DownloadSpec(
            set_name="licenses",
            relative_path="mathjax-3.1.2/LICENSE.txt",
            component="MathJax 3.1.2",
            license_id="Apache-2.0",
            url=MATHJAX_LICENSE_URL,
            payload_kind="mathjax-license",
        ),
        DownloadSpec(
            set_name="licenses",
            relative_path="cards/adrian-kennard-cards-authority.html",
            component="Random playing-card image authority",
            license_id="CC0-1.0",
            url=CARD_AUTHORITY_URL,
            payload_kind="card-authority",
        ),
        DownloadSpec(
            set_name="licenses",
            relative_path="monty/svg-silh-cc0-authority.html",
            component="Random Monty Hall car/goat image authority",
            license_id="CC0-1.0",
            url=MONTY_AUTHORITY_URL,
            payload_kind="monty-authority",
        ),
        DownloadSpec(
            set_name="licenses",
            relative_path="cc0-1.0/legalcode.txt",
            component="CC0 1.0 Universal legal code",
            license_id="CC0-1.0",
            url=CC0_LEGALCODE_URL,
            payload_kind="cc0-legalcode",
        ),
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative_path(value: str) -> Path:
    posix = PurePosixPath(value)
    if posix.is_absolute() or not posix.parts:
        raise RuntimeError(f"unsafe component path: {value}")
    if any(part in {"", ".", ".."} for part in posix.parts):
        raise RuntimeError(f"unsafe component path: {value}")
    return Path(*posix.parts)


def validate_url(spec: DownloadSpec, final_url: str) -> None:
    requested = urllib.parse.urlsplit(spec.url)
    final = urllib.parse.urlsplit(final_url)
    if requested.scheme != "https" or final.scheme != "https":
        raise RuntimeError(f"non-HTTPS component URL: {spec.url} -> {final_url}")
    # These authority URLs currently do not redirect. Refusing a future redirect
    # keeps the frozen provenance exact instead of silently changing authority.
    if final_url != spec.url:
        raise RuntimeError(f"unexpected redirect: {spec.url} -> {final_url}")


def fetch(spec: DownloadSpec) -> DownloadResult:
    request = urllib.request.Request(
        spec.url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "identity",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = getattr(response, "status", None)
            final_url = response.geturl()
            validate_url(spec, final_url)
            if status != 200:
                raise RuntimeError(f"unexpected HTTP {status}")
            data = response.read()
            result = DownloadResult(
                spec=spec,
                data=data,
                final_url=final_url,
                content_type=response.headers.get("Content-Type", ""),
                last_modified=response.headers.get("Last-Modified", ""),
                etag=response.headers.get("ETag", ""),
            )
    except Exception as exc:
        raise RuntimeError(f"fetch failed for {spec.url}: {exc}") from exc
    if not result.data:
        raise RuntimeError(f"empty response: {spec.url}")
    validate_payload(result.spec, result.data)
    return result


def validate_payload(spec: DownloadSpec, data: bytes) -> None:
    lowered = data.lower()
    if spec.payload_kind == "card-svg":
        if b"<svg" not in lowered[:2048]:
            raise RuntimeError(f"card payload is not SVG: {spec.url}")
    elif spec.payload_kind == "mathjax-license":
        if b"apache license" not in lowered or b"version 2.0" not in lowered:
            raise RuntimeError("MathJax license payload lacks Apache-2.0 markers")
    elif spec.payload_kind == "card-authority":
        if b"public domain" not in lowered or b"cc0" not in lowered:
            raise RuntimeError("card authority payload lacks public-domain/CC0 markers")
    elif spec.payload_kind == "monty-authority":
        if b"all contents" not in lowered or b"creative commons cc0" not in lowered:
            raise RuntimeError("SVG Silh authority payload lacks its CC0 statement")
    elif spec.payload_kind == "cc0-legalcode":
        if b"cc0 1.0 universal" not in lowered or b"creative commons" not in lowered:
            raise RuntimeError("CC0 legal-code payload lacks canonical markers")
    else:
        raise RuntimeError(f"unknown payload kind: {spec.payload_kind}")


def manifest_bytes(results: list[DownloadResult]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
    writer.writeheader()
    for result in sorted(results, key=lambda item: item.spec.relative_path):
        writer.writerow(
            {
                "relative_path": result.spec.relative_path,
                "component": result.spec.component,
                "license": result.spec.license_id,
                "url": result.spec.url,
                "final_url": result.final_url,
                "bytes": len(result.data),
                "sha256": sha256(result.data),
                "content_type": result.content_type,
                "last_modified": result.last_modified,
                "etag": result.etag,
            }
        )
    return stream.getvalue().encode("utf-8")


def write_set(
    root: Path,
    manifest: Path,
    receipt_path: Path,
    results: list[DownloadResult],
    schema: str,
    retrieved_at: str,
) -> dict[str, object]:
    root.mkdir(parents=True, exist_ok=False)
    for result in results:
        destination = root / safe_relative_path(result.spec.relative_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(result.data)
    manifest_data = manifest_bytes(results)
    manifest.write_bytes(manifest_data)
    receipt: dict[str, object] = {
        "schema": schema,
        "retrieved_at": retrieved_at,
        "file_count": len(results),
        "payload_bytes": sum(len(result.data) for result in results),
        "url_manifest": manifest.name,
        "url_manifest_bytes": len(manifest_data),
        "url_manifest_sha256": sha256(manifest_data),
        "user_agent": USER_AGENT,
    }
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return receipt


def freeze() -> None:
    if ASSET_ROOT.exists() or LICENSE_ROOT.exists():
        raise RuntimeError("component freeze already exists; use --check-only")
    assets = card_specs()
    licenses = license_specs()
    specifications = assets + licenses
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(fetch, specifications))
    by_set = {
        "assets": [result for result in results if result.spec.set_name == "assets"],
        "licenses": [result for result in results if result.spec.set_name == "licenses"],
    }
    if len(by_set["assets"]) != 53 or len(by_set["licenses"]) != 4:
        raise RuntimeError("download result set does not match the bounded specification")
    retrieved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    asset_receipt = write_set(
        ASSET_ROOT,
        ASSET_MANIFEST,
        ASSET_RECEIPT,
        by_set["assets"],
        "o006.random.component-assets.v1",
        retrieved_at,
    )
    asset_receipt.update(
        {
            "generation": {
                "denominations": list(DENOMINATIONS),
                "suits": list(SUITS),
                "additional_files": ["Back.svg"],
            },
            "license": "CC0-1.0",
            "license_evidence_root": "../component-licenses",
            "scope_exclusions": [
                "biography images",
                "data photographs",
                "data sets",
                "unreferenced app assets",
            ],
        }
    )
    ASSET_RECEIPT.write_text(
        json.dumps(asset_receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    license_receipt = write_set(
        LICENSE_ROOT,
        LICENSE_MANIFEST,
        LICENSE_RECEIPT,
        by_set["licenses"],
        "o006.random.component-licenses.v1",
        retrieved_at,
    )
    license_receipt.update(
        {
            "coverage": {
                "MathJax 3.1.2": "Apache-2.0",
                "Random playing-card images": "CC0-1.0",
                "Random Monty Hall car/goat source": "CC0-1.0",
            },
            "mathjax_version": "3.1.2",
            "mathjax_distribution_component": "tex-svg.js",
            "scope_note": (
                "Authority/license receipts only; no unclear biography/data "
                "photographs or data sets are included."
            ),
        }
    )
    LICENSE_RECEIPT.write_text(
        json.dumps(license_receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"component_assets": asset_receipt, "component_licenses": license_receipt},
            ensure_ascii=False,
            indent=2,
        )
    )


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or tuple(rows[0]) != MANIFEST_FIELDS:
        raise RuntimeError(f"invalid manifest schema: {path}")
    return rows


def check_set(
    root: Path,
    manifest: Path,
    receipt_path: Path,
    expected_specs: tuple[DownloadSpec, ...],
    expected_schema: str,
) -> tuple[int, int, str]:
    if not root.is_dir() or not manifest.is_file() or not receipt_path.is_file():
        raise RuntimeError(f"component freeze is incomplete: {root}")
    if root.is_symlink() or manifest.is_symlink() or receipt_path.is_symlink():
        raise RuntimeError(f"symlink is not allowed in component authority: {root}")
    rows = read_manifest(manifest)
    expected_by_path = {spec.relative_path: spec for spec in expected_specs}
    if len(expected_by_path) != len(expected_specs):
        raise RuntimeError("internal error: duplicate expected component paths")
    if [row["relative_path"] for row in rows] != sorted(expected_by_path):
        raise RuntimeError(f"manifest path order/set mismatch: {manifest}")
    payload_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path not in {manifest, receipt_path}
    }
    if payload_paths != set(expected_by_path):
        raise RuntimeError(
            f"component file-set mismatch in {root}: "
            f"missing={sorted(set(expected_by_path)-payload_paths)!r}, "
            f"extra={sorted(payload_paths-set(expected_by_path))!r}"
        )
    total_bytes = 0
    for row in rows:
        rel = row["relative_path"]
        spec = expected_by_path[rel]
        if (
            row["component"] != spec.component
            or row["license"] != spec.license_id
            or row["url"] != spec.url
            or row["final_url"] != spec.url
        ):
            raise RuntimeError(f"manifest authority mismatch: {rel}")
        path = root / safe_relative_path(rel)
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"missing/nonregular component file: {rel}")
        data = path.read_bytes()
        validate_payload(spec, data)
        if len(data) != int(row["bytes"]) or sha256(data) != row["sha256"]:
            raise RuntimeError(f"component byte mismatch: {rel}")
        total_bytes += len(data)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    manifest_data = manifest.read_bytes()
    if receipt.get("schema") != expected_schema:
        raise RuntimeError(f"receipt schema mismatch: {receipt_path}")
    if (
        receipt.get("file_count") != len(rows)
        or receipt.get("payload_bytes") != total_bytes
        or receipt.get("url_manifest_bytes") != len(manifest_data)
        or receipt.get("url_manifest_sha256") != sha256(manifest_data)
    ):
        raise RuntimeError(f"receipt totals/hash mismatch: {receipt_path}")
    return len(rows), total_bytes, sha256(manifest_data)


def check() -> None:
    asset_count, asset_bytes, asset_manifest_hash = check_set(
        ASSET_ROOT,
        ASSET_MANIFEST,
        ASSET_RECEIPT,
        card_specs(),
        "o006.random.component-assets.v1",
    )
    license_count, license_bytes, license_manifest_hash = check_set(
        LICENSE_ROOT,
        LICENSE_MANIFEST,
        LICENSE_RECEIPT,
        license_specs(),
        "o006.random.component-licenses.v1",
    )
    if asset_count != 53 or license_count != 4:
        raise RuntimeError("bounded component counts changed")
    print(
        f"PASS: {asset_count} card SVGs / {asset_bytes} bytes / manifest "
        f"{asset_manifest_hash}; {license_count} license receipts / "
        f"{license_bytes} bytes / manifest {license_manifest_hash}"
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
