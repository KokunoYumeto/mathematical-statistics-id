#!/usr/bin/env python3
"""Build the deterministic reader-first Zenodo package for checkpoint 16/29.

The mature v15 packager supplies the archive-safety and ZIP-verification
implementation. This wrapper gives the new boundary its own immutable release
directory and explicitly replaces the v15 cursor/evidence identities.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026.08.23.16"
TAG = "v2026.08.23.16"
MODULE_PATH = ROOT / "scripts" / "package_zenodo_checkpoint_v15.py"
SPEC = importlib.util.spec_from_file_location("o006_package_v15_impl", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load the audited packager implementation")
IMPL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IMPL)

IMPL.VERSION = VERSION
IMPL.RELEASE_DIR = ROOT / "release" / "zenodo" / VERSION
IMPL.PDF_OUT = IMPL.RELEASE_DIR / f"00_statistika-matematis-id-reader-{VERSION}.pdf"
IMPL.READER_ZIP = IMPL.RELEASE_DIR / f"10_mathematical-statistics-id-{VERSION}-reader-html.zip"
IMPL.SOURCE_ZIP = IMPL.RELEASE_DIR / f"20_mathematical-statistics-id-{VERSION}-source-provenance.zip"
IMPL.BACKEND_ZIP = IMPL.RELEASE_DIR / f"30_mathematical-statistics-id-{VERSION}-modular-backend.zip"
IMPL.LICENSE_OUT = IMPL.RELEASE_DIR / "40_LICENSE.md"
IMPL.RELEASE_MANIFEST = IMPL.RELEASE_DIR / f"50_mathematical-statistics-id-{VERSION}-release-manifest.json"
IMPL.SHA256SUMS = IMPL.RELEASE_DIR / "SHA256SUMS.txt"
IMPL.ZIP_TIMESTAMP = (2026, 8, 23, 0, 0, 0)
IMPL.EXPECTED = {
    "translated_pages": 16,
    "reader_files": 46,
    "reader_bytes": 2_564_819,
    "reader_manifest_sha256": "6cdf7d7592f9468a782801ed2dae9ed7dfdc14cde445c1026cb8018bb3ef3482",
    "pdf_pages": 197,
    "pdf_bytes": 85_357_801,
    "pdf_sha256": "f1a886ff1285315478bb7e50a773e8a5d79b47e6170a86e82e7b98126f6f6160",
    "entities": 6_567,
    "entities_sha256": "2d36d064b3e89e7cdd281f0a91f18a8386050739fe149941aec035638536836b",
    "relations": 9_035,
    "relations_sha256": "b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159",
    "translated_entities": 4_337,
}


def translated_rows_v16() -> list[dict[str, str]]:
    rows = IMPL.manifest_rows(ROOT / "00_control" / "TRANSLATION_LEDGER.csv")
    completed = [row for row in rows if row["status"] == "complete"]
    if len(completed) != 16 or completed[-1]["source_path"] != "random/point/Sufficient.html":
        raise RuntimeError("translation ledger no longer ends at Sufficient.html")
    for ordinal, row in enumerate(completed, start=1):
        if int(row["ordinal"]) != ordinal:
            raise RuntimeError("translation ledger is not contiguous")
    return completed


_reader_entries = IMPL.reader_entries


def reader_entries_v16() -> tuple[dict[str, Path], dict[str, object]]:
    entries, summary = _reader_entries()
    for stale in (
        "_evidence/CHECKPOINT_2026-08-22_FIFTEEN_PAGE.md",
        "_evidence/LIVE_BROWSER_QA_2026-08-22_FIFTEEN_PAGE.json",
        "_evidence/GITHUB_PUBLICATION_RECEIPT_2026-08-23_FIFTEEN_PAGE.json",
    ):
        entries.pop(stale, None)
    for path in (
        ROOT / "00_control" / "CHECKPOINT_2026-08-23_SIXTEEN_PAGE.md",
        ROOT / "00_control" / "LIVE_BROWSER_QA_2026-08-23_SIXTEEN_PAGE.json",
        ROOT / "00_control" / "GITHUB_PUBLICATION_RECEIPT_2026-08-23_SIXTEEN_PAGE.json",
    ):
        IMPL.add_entry(entries, f"_evidence/{path.name}", path)
    return entries, summary


_source_entries = IMPL.source_entries


def source_entries_v16(rows: list[dict[str, str]]) -> dict[str, Path]:
    entries = _source_entries(rows)
    for stale in (
        "00_control/CHECKPOINT_2026-08-22_FIFTEEN_PAGE.md",
        "00_control/LIVE_BROWSER_QA_2026-08-22_FIFTEEN_PAGE.json",
        "00_control/GITHUB_PUBLICATION_RECEIPT_2026-08-23_FIFTEEN_PAGE.json",
    ):
        entries.pop(stale, None)
    for path in (
        ROOT / "00_control" / "CHECKPOINT_2026-08-23_SIXTEEN_PAGE.md",
        ROOT / "00_control" / "LIVE_BROWSER_QA_2026-08-23_SIXTEEN_PAGE.json",
        ROOT / "00_control" / "GITHUB_PUBLICATION_RECEIPT_2026-08-23_SIXTEEN_PAGE.json",
        ROOT / "scripts" / "package_zenodo_checkpoint_v16.py",
        ROOT / "scripts" / "publish_zenodo_checkpoint_v16.py",
        ROOT / "scripts" / "verify_github_checkpoint_v16.py",
    ):
        IMPL.add_entry(entries, path.relative_to(ROOT).as_posix(), path)
    return entries


IMPL.translated_rows = translated_rows_v16
IMPL.reader_entries = reader_entries_v16
IMPL.source_entries = source_entries_v16


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_outputs() -> tuple[dict[Path, bytes], dict[str, object]]:
    outputs, release = IMPL.build_outputs()
    release["checkpoint"] = {
        "complete": False,
        "last_page": "random/point/Sufficient.html",
        "next_page": "random/interval/index.html",
        "translated_pages": 16,
        "total_pages": 29,
        "version": VERSION,
    }
    release["github"]["content_release"] = (
        "https://github.com/KokunoYumeto/mathematical-statistics-id/releases/tag/" + TAG
    )
    release["zenodo"]["previous_record_id"] = "22062664"
    release["zenodo"]["version"] = VERSION
    outputs[IMPL.RELEASE_MANIFEST] = IMPL.canonical_json(release)
    outputs[IMPL.SHA256SUMS] = (
        "\n".join(
            f"{sha256(data)}  {path.name}"
            for path, data in sorted(outputs.items(), key=lambda item: item[0].name.casefold())
        )
        + "\n"
    ).encode("utf-8")
    return outputs, release


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    outputs, release = build_outputs()
    if args.check_only:
        for path, expected in outputs.items():
            if IMPL.read_regular(path) != expected:
                raise RuntimeError(f"stale/noncanonical release artifact: {path.name}")
        mode = "verified"
    else:
        IMPL.RELEASE_DIR.mkdir(parents=True, exist_ok=True)
        expected_names = {path.name for path in outputs}
        existing_names = {path.name for path in IMPL.RELEASE_DIR.iterdir() if path.is_file()}
        unexpected = sorted(existing_names - expected_names)
        if unexpected:
            raise RuntimeError(f"unexpected pre-existing release files: {unexpected}")
        for path, data in outputs.items():
            temporary = path.with_name(path.name + ".tmp")
            temporary.write_bytes(data)
            temporary.replace(path)
        mode = "written"
    print(json.dumps({
        "mode": mode,
        "version": VERSION,
        "payload_bytes": sum(len(data) for data in outputs.values()),
        "source_commit": release["github"]["source_commit"],
        "artifacts": [
            {"filename": path.name, "bytes": len(data), "sha256": sha256(data)}
            for path, data in sorted(outputs.items(), key=lambda item: item[0].name.casefold())
        ],
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
