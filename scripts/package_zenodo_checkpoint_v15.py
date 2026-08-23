#!/usr/bin/env python3
"""Build the deterministic reader-first Zenodo package for checkpoint 15/29."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import stat
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026.08.22.15"
RELEASE_DIR = ROOT / "release" / "zenodo" / VERSION
PDF_SOURCE = ROOT / "output" / "pdf" / "statistika-matematis-id-reader.pdf"
PDF_OUT = RELEASE_DIR / f"00_statistika-matematis-id-reader-{VERSION}.pdf"
READER_ZIP = RELEASE_DIR / f"10_mathematical-statistics-id-{VERSION}-reader-html.zip"
SOURCE_ZIP = RELEASE_DIR / f"20_mathematical-statistics-id-{VERSION}-source-provenance.zip"
BACKEND_ZIP = RELEASE_DIR / f"30_mathematical-statistics-id-{VERSION}-modular-backend.zip"
LICENSE_OUT = RELEASE_DIR / "40_LICENSE.md"
RELEASE_MANIFEST = RELEASE_DIR / f"50_mathematical-statistics-id-{VERSION}-release-manifest.json"
SHA256SUMS = RELEASE_DIR / "SHA256SUMS.txt"
ZIP_TIMESTAMP = (2026, 8, 22, 0, 0, 0)

EXPECTED = {
    "translated_pages": 15,
    "reader_files": 45,
    "reader_bytes": 2_503_889,
    "reader_manifest_sha256": "d6f51461a9db39f53f832912fbe4c865059177094564ca5a6d0b30cc3c1740aa",
    "pdf_pages": 182,
    "pdf_bytes": 76_775_084,
    "pdf_sha256": "7c4898505962f6978eb064c605a77fca9ccbcd3ba7f9238f9cf0d8ae974662ef",
    "entities": 6_567,
    "entities_sha256": "7f93f59a5cbd55c647c5f5356a828843aa22754a411db579029439dd5471617b",
    "relations": 9_035,
    "relations_sha256": "b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a",
    "translated_entities": 4_012,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def read_regular(path: Path) -> bytes:
    resolved = path.resolve(strict=True)
    resolved.relative_to(ROOT.resolve())
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        raise RuntimeError(f"non-regular package input: {path.relative_to(ROOT)}")
    if getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise RuntimeError(f"reparse package input: {path.relative_to(ROOT)}")
    return path.read_bytes()


def add_entry(entries: dict[str, Path], archive_path: str, source: Path) -> None:
    name = PurePosixPath(archive_path).as_posix()
    parts = PurePosixPath(name).parts
    if name.startswith("/") or ".." in parts:
        raise RuntimeError(f"unsafe archive path: {archive_path}")
    if name in entries:
        raise RuntimeError(f"duplicate archive path: {name}")
    folded = {part.casefold() for part in parts}
    leaf = PurePosixPath(name).name.casefold()
    if folded & {".git", "__pycache__", ".cache", "tmp"}:
        raise RuntimeError(f"transient archive entry: {name}")
    if leaf.endswith((".pyc", ".pyo")) or any(
        term in leaf for term in ("token", "credential", "secret")
    ):
        raise RuntimeError(f"credential/transient-like archive entry: {name}")
    entries[name] = source


def add_root_paths(entries: dict[str, Path], paths: list[Path]) -> None:
    for path in paths:
        add_entry(entries, path.relative_to(ROOT).as_posix(), path)


def manifest_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(read_regular(path).decode("utf-8"), newline="")))


def translated_rows() -> list[dict[str, str]]:
    rows = manifest_rows(ROOT / "00_control" / "TRANSLATION_LEDGER.csv")
    completed = [row for row in rows if row["status"] == "complete"]
    if len(completed) != EXPECTED["translated_pages"]:
        raise RuntimeError(f"translated page count changed: {len(completed)}")
    if completed[-1]["source_path"] != "random/point/Unbiased.html":
        raise RuntimeError("translated boundary no longer ends at Unbiased.html")
    for ordinal, row in enumerate(completed, start=1):
        if int(row["ordinal"]) != ordinal:
            raise RuntimeError("translation ledger is not contiguous")
    return completed


def reader_entries() -> tuple[dict[str, Path], dict[str, object]]:
    manifest = ROOT / "build" / "FIRST_UNIT_MANIFEST.csv"
    data = read_regular(manifest)
    rows = manifest_rows(manifest)
    if len(rows) != EXPECTED["reader_files"] or sha256(data) != EXPECTED["reader_manifest_sha256"]:
        raise RuntimeError("reader manifest identity changed")
    entries: dict[str, Path] = {}
    total = 0
    for row in rows:
        path = ROOT / "build" / "html-id" / Path(row["relative_path"])
        payload = read_regular(path)
        if len(payload) != int(row["bytes"]) or sha256(payload) != row["sha256"]:
            raise RuntimeError(f"reader manifest mismatch: {row['relative_path']}")
        add_entry(entries, row["relative_path"], path)
        total += len(payload)
    if total != EXPECTED["reader_bytes"]:
        raise RuntimeError(f"reader byte total changed: {total}")
    evidence = [
        ROOT / "README.md",
        ROOT / "LICENSE.md",
        manifest,
        ROOT / "build" / "FIRST_UNIT_BUILD_RECEIPT.json",
        ROOT / "build" / "FIRST_UNIT_QA_RECEIPT.json",
        ROOT / "build" / "PDF_READER_RECEIPT.json",
        ROOT / "build" / "PDF_VISUAL_QA_RECEIPT.json",
        ROOT / "00_control" / "CHECKPOINT_2026-08-22_FIFTEEN_PAGE.md",
        ROOT / "00_control" / "LIVE_BROWSER_QA_2026-08-22_FIFTEEN_PAGE.json",
        ROOT / "00_control" / "GITHUB_PUBLICATION_RECEIPT_2026-08-23_FIFTEEN_PAGE.json",
    ]
    for path in evidence:
        add_entry(entries, f"_evidence/{path.name}", path)
    return entries, {
        "file_count": len(rows),
        "reader_bytes": total,
        "manifest_bytes": len(data),
        "manifest_sha256": sha256(data),
    }


def source_entries(rows: list[dict[str, str]]) -> dict[str, Path]:
    entries: dict[str, Path] = {}
    root_paths = [
        ROOT / ".gitattributes",
        ROOT / "README.md",
        ROOT / "LICENSE.md",
        ROOT / "requirements.txt",
        ROOT / "authority" / "SOURCE_URL_MANIFEST.csv",
        ROOT / "authority" / "REFERENCE_URL_MANIFEST.csv",
        ROOT / "authority" / "SOURCE_FREEZE_RECEIPT.json",
        ROOT / "00_control" / "SOURCE_AUTHORITY.json",
        ROOT / "00_control" / "RIGHTS_AND_COMPONENTS.md",
        ROOT / "00_control" / "WORKFLOW.md",
        ROOT / "00_control" / "DECISION_LOG.md",
        ROOT / "00_control" / "C140_CONFIGURED_ARCHITECTURE_2026-08-21.md",
        ROOT / "00_control" / "CURRENT_STATE.md",
        ROOT / "00_control" / "CURRENT_CURSOR.md",
        ROOT / "00_control" / "TRANSLATION_LEDGER.csv",
        ROOT / "00_control" / "ADVERSE_LEDGER.jsonl",
        ROOT / "00_control" / "TERMINOLOGY_QA_2026-08-22.md",
        ROOT / "00_control" / "TERMINOLOGY_GLOSSARY_ID_ID.csv",
        ROOT / "00_control" / "CHECKPOINT_2026-08-22_FIFTEEN_PAGE.md",
        ROOT / "00_control" / "LIVE_BROWSER_QA_2026-08-22_FIFTEEN_PAGE.json",
        ROOT / "00_control" / "GITHUB_PUBLICATION_RECEIPT_2026-08-23_FIFTEEN_PAGE.json",
        ROOT / "00_control" / "ZENODO_PUBLICATION_RECEIPT_2026-08-22_THIRTEEN_PAGE.json",
        ROOT / "build" / "FIRST_UNIT_MANIFEST.csv",
        ROOT / "build" / "FIRST_UNIT_BUILD_RECEIPT.json",
        ROOT / "build" / "FIRST_UNIT_QA_RECEIPT.json",
        ROOT / "build" / "PDF_READER_RECEIPT.json",
        ROOT / "build" / "PDF_VISUAL_QA_RECEIPT.json",
    ]
    scripts = [
        "freeze_component_assets.py",
        "freeze_random_core.py",
        "generate_random_backend.py",
        "build_first_unit.py",
        "qa_first_unit.py",
        "build_pdf_reader.py",
        "qa_pdf_reader.py",
        "make_pdf_contact_sheets.py",
        "render_pdf_pages.mjs",
        "package_zenodo_checkpoint_v15.py",
        "localize_point_index.py",
        "localize_estimators.py",
        "localize_moments.py",
        "localize_likelihood.py",
        "localize_bayes.py",
        "localize_unbiased.py",
        "localize_covariance.py",
        "localize_normal.py",
        "localize_order_statistics.py",
    ]
    root_paths.extend(ROOT / "scripts" / name for name in scripts)
    add_root_paths(entries, root_paths)
    for row in rows:
        source_rel = Path(row["source_path"])
        target_rel = Path(row["target_path"])
        add_entry(entries, target_rel.as_posix(), ROOT / target_rel)
        add_entry(
            entries,
            (Path("authority") / "upstream" / source_rel).as_posix(),
            ROOT / "authority" / "upstream" / source_rel,
        )
    for directory in (
        ROOT / "authority" / "component-licenses",
        ROOT / "authority" / "runtime" / "MathJax-3.1.2",
    ):
        for path in sorted(directory.rglob("*"), key=lambda value: value.as_posix().casefold()):
            if path.is_file():
                add_entry(entries, path.relative_to(ROOT).as_posix(), path)
    return entries


def backend_entries() -> dict[str, Path]:
    paths = [
        ROOT / "backend" / "entities.jsonl",
        ROOT / "backend" / "relations.csv",
        ROOT / "backend" / "entities.schema.json",
        ROOT / "backend" / "BACKEND_RECEIPT.json",
        ROOT / "00_control" / "TRANSLATION_LEDGER.csv",
        ROOT / "00_control" / "ADVERSE_LEDGER.jsonl",
        ROOT / "authority" / "SOURCE_URL_MANIFEST.csv",
        ROOT / "authority" / "SOURCE_FREEZE_RECEIPT.json",
        ROOT / "build" / "FIRST_UNIT_MANIFEST.csv",
        ROOT / "LICENSE.md",
    ]
    entries: dict[str, Path] = {}
    add_root_paths(entries, paths)
    return entries


def zip_payload(entries: dict[str, Path]) -> tuple[bytes, list[dict[str, object]]]:
    buffer = io.BytesIO()
    inventory: list[dict[str, object]] = []
    with zipfile.ZipFile(
        buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for name, source in sorted(entries.items(), key=lambda item: item[0].casefold()):
            data = read_regular(source)
            info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.flag_bits |= 0x800
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            inventory.append({"bytes": len(data), "path": name, "sha256": sha256(data)})
    return buffer.getvalue(), inventory


def verify_zip(data: bytes, inventory: list[dict[str, object]], name: str) -> None:
    with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"corrupt ZIP: {name}")
        expected_names = [str(row["path"]) for row in inventory]
        if archive.namelist() != expected_names or len(expected_names) != len(set(expected_names)):
            raise RuntimeError(f"ZIP inventory mismatch: {name}")
        for row in inventory:
            payload = archive.read(str(row["path"]))
            if len(payload) != row["bytes"] or sha256(payload) != row["sha256"]:
                raise RuntimeError(f"ZIP entry mismatch: {name}:{row['path']}")


def git_commit() -> str:
    value = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()
    if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
        raise RuntimeError("invalid source commit")
    return value


def build_outputs() -> tuple[dict[Path, bytes], dict[str, object]]:
    rows = translated_rows()
    reader, reader_summary = reader_entries()
    packages = [
        (READER_ZIP, reader),
        (SOURCE_ZIP, source_entries(rows)),
        (BACKEND_ZIP, backend_entries()),
    ]
    artifacts: list[dict[str, object]] = []
    outputs: dict[Path, bytes] = {}
    for path, entries in packages:
        payload, inventory = zip_payload(entries)
        verify_zip(payload, inventory, path.name)
        outputs[path] = payload
        artifacts.append(
            {
                "bytes": len(payload),
                "entries": inventory,
                "entry_count": len(inventory),
                "filename": path.name,
                "sha256": sha256(payload),
                "uncompressed_bytes": sum(int(row["bytes"]) for row in inventory),
            }
        )
    pdf = read_regular(PDF_SOURCE)
    if len(pdf) != EXPECTED["pdf_bytes"] or sha256(pdf) != EXPECTED["pdf_sha256"]:
        raise RuntimeError("reader-first PDF identity changed")
    license_data = read_regular(ROOT / "LICENSE.md")
    outputs[PDF_OUT] = pdf
    outputs[LICENSE_OUT] = license_data
    release = {
        "artifacts": [
            {
                "bytes": len(pdf),
                "filename": PDF_OUT.name,
                "kind": "reader-first-pdf",
                "physical_pages": EXPECTED["pdf_pages"],
                "sha256": sha256(pdf),
            },
            *artifacts,
            {
                "bytes": len(license_data),
                "filename": LICENSE_OUT.name,
                "kind": "component-rights-notice",
                "sha256": sha256(license_data),
            },
        ],
        "backend": {
            "entities": EXPECTED["entities"],
            "entities_sha256": EXPECTED["entities_sha256"],
            "relations": EXPECTED["relations"],
            "relations_sha256": EXPECTED["relations_sha256"],
            "translated_entities": EXPECTED["translated_entities"],
        },
        "checkpoint": {
            "complete": False,
            "last_page": "random/point/Unbiased.html",
            "next_page": "random/point/Sufficient.html",
            "translated_pages": EXPECTED["translated_pages"],
            "total_pages": 29,
            "version": VERSION,
        },
        "exclusions": [
            "Git internals, caches, visual-QA PNGs, and temporary build trees",
            "credentials and local user data",
            "untranslated bulk closure already preserved by exact manifests",
            "third-party biography media and datasets without a proved redistribution grant",
        ],
        "github": {
            "content_release": "https://github.com/KokunoYumeto/mathematical-statistics-id/releases/tag/v2026.08.22.15",
            "repository": "https://github.com/KokunoYumeto/mathematical-statistics-id",
            "source_commit": git_commit(),
        },
        "reader": reader_summary,
        "rights_model": "component-separated; Random landing CC BY 2.0; Random Credits links CC BY 1.0; MathJax Apache-2.0; identified reader assets CC0; no uniform aggregate relicensing claim",
        "schema": "o006.random.zenodo-release.v2",
        "zenodo": {
            "concept_doi": "10.5281/zenodo.22059763",
            "concept_record_id": "22059763",
            "previous_record_id": "22061677",
            "version": VERSION,
        },
    }
    manifest_data = canonical_json(release)
    outputs[RELEASE_MANIFEST] = manifest_data
    sums_rows = [
        f"{sha256(data)}  {path.name}"
        for path, data in sorted(outputs.items(), key=lambda item: item[0].name.casefold())
    ]
    outputs[SHA256SUMS] = ("\n".join(sums_rows) + "\n").encode("utf-8")
    total = sum(len(data) for data in outputs.values())
    if total > 500_000_000:
        raise RuntimeError(f"release payload exceeds 500,000,000 bytes: {total}")
    return outputs, release


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    outputs, release = build_outputs()
    if args.check_only:
        for path, expected in outputs.items():
            actual = read_regular(path)
            if actual != expected:
                raise RuntimeError(f"stale/noncanonical release artifact: {path.name}")
        mode = "verified"
    else:
        RELEASE_DIR.mkdir(parents=True, exist_ok=True)
        expected_names = {path.name for path in outputs}
        existing_names = {path.name for path in RELEASE_DIR.iterdir() if path.is_file()}
        unexpected = sorted(existing_names - expected_names)
        if unexpected:
            raise RuntimeError(f"unexpected pre-existing release files: {unexpected}")
        for path, data in outputs.items():
            temporary = path.with_name(path.name + ".tmp")
            temporary.write_bytes(data)
            os.replace(temporary, path)
        mode = "written"
    summary = {
        "artifacts": [
            {"bytes": len(data), "filename": path.name, "sha256": sha256(data)}
            for path, data in sorted(outputs.items(), key=lambda item: item[0].name.casefold())
        ],
        "mode": mode,
        "payload_bytes": sum(len(data) for data in outputs.values()),
        "source_commit": release["github"]["source_commit"],
        "version": VERSION,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
