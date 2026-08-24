#!/usr/bin/env python3
"""Build the deterministic, reader-first Zenodo package for the complete 29/29 edition.

This script is deliberately local-only: it performs no network access, reads no
credentials, and invokes no Git command.  The exact published source commit is
supplied explicitly so that packaging never triggers a repository scan.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026.08.24.29"
TAG = "v2026.08.24.29"
RELEASE_DIR = ROOT / "release" / "zenodo" / VERSION
PDF_SOURCE = ROOT / "output" / "pdf" / "statistika-matematis-id-reader.pdf"
PDF_OUT = RELEASE_DIR / f"00_statistika-matematis-id-reader-{VERSION}.pdf"
READER_ZIP = RELEASE_DIR / f"10_mathematical-statistics-id-{VERSION}-reader-html.zip"
SOURCE_ZIP = RELEASE_DIR / f"20_mathematical-statistics-id-{VERSION}-source-provenance.zip"
BACKEND_ZIP = RELEASE_DIR / f"30_mathematical-statistics-id-{VERSION}-modular-backend.zip"
LICENSE_OUT = RELEASE_DIR / "40_LICENSE.md"
RELEASE_MANIFEST = RELEASE_DIR / f"50_mathematical-statistics-id-{VERSION}-release-manifest.json"
SHA256SUMS = RELEASE_DIR / "SHA256SUMS.txt"
ZIP_TIMESTAMP = (2026, 8, 24, 0, 0, 0)
PAYLOAD_CAP = 500_000_000
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"
FINAL_SOURCE_PATH = "random/hypothesis/ChiSquare.html"
DEFAULT_CHECKPOINT = "00_control/CHECKPOINT_2026-08-24_COMPLETE_29_PAGE.md"
DEFAULT_BROWSER_QA = "00_control/LIVE_BROWSER_QA_2026-08-24_COMPLETE_29_PAGE.json"

CORE_CONTROLS = (
    "00_control/SOURCE_AUTHORITY.json",
    "00_control/RIGHTS_AND_COMPONENTS.md",
    "00_control/WORKFLOW.md",
    "00_control/DECISION_LOG.md",
    "00_control/C140_CONFIGURED_ARCHITECTURE_2026-08-21.md",
    "00_control/CURRENT_STATE.md",
    "00_control/CURRENT_CURSOR.md",
    "00_control/TRANSLATION_LEDGER.csv",
    "00_control/ADVERSE_LEDGER.jsonl",
    "00_control/TERMINOLOGY_QA_2026-08-22.md",
    "00_control/TERMINOLOGY_GLOSSARY_ID_ID.csv",
    "00_control/INTERVAL_BATCH_QA_2026-08-23.json",
    "00_control/HYPOTHESIS_BATCH_QA_2026-08-23.json",
)
BUILD_EVIDENCE = (
    "build/FIRST_UNIT_MANIFEST.csv",
    "build/FIRST_UNIT_BUILD_RECEIPT.json",
    "build/FIRST_UNIT_QA_RECEIPT.json",
    "build/PDF_READER_RECEIPT.json",
    "build/PDF_VISUAL_QA_RECEIPT.json",
)
SOURCE_AUTHORITY = (
    "authority/SOURCE_URL_MANIFEST.csv",
    "authority/REFERENCE_URL_MANIFEST.csv",
    "authority/SOURCE_FREEZE_RECEIPT.json",
)
REPRODUCIBILITY_SCRIPTS = (
    "scripts/freeze_component_assets.py",
    "scripts/freeze_random_core.py",
    "scripts/generate_random_backend.py",
    "scripts/build_first_unit.py",
    "scripts/qa_first_unit.py",
    "scripts/build_pdf_reader.py",
    "scripts/qa_pdf_reader.py",
    "scripts/make_pdf_contact_sheets.py",
    "scripts/render_pdf_pages.mjs",
    "scripts/package_zenodo_complete_v29.py",
    "scripts/publish_zenodo_complete_v29.py",
    "scripts/verify_github_complete_v29.py",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def safe_relative(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise RuntimeError(f"unsafe relative path: {value}")
    return path.as_posix()


def root_path(value: str) -> Path:
    relative = safe_relative(value)
    path = ROOT / Path(relative)
    path.resolve(strict=False).relative_to(ROOT.resolve())
    return path


def read_regular(path: Path) -> bytes:
    resolved = path.resolve(strict=True)
    resolved.relative_to(ROOT.resolve())
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        raise RuntimeError(f"non-regular package input: {path.relative_to(ROOT)}")
    if getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
        raise RuntimeError(f"reparse package input: {path.relative_to(ROOT)}")
    return path.read_bytes()


def read_json(relative: str) -> dict[str, object]:
    value = json.loads(read_regular(root_path(relative)).decode("utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {relative}")
    return value


def manifest_rows(relative: str) -> list[dict[str, str]]:
    data = read_regular(root_path(relative)).decode("utf-8")
    return list(csv.DictReader(io.StringIO(data, newline="")))


def add_entry(entries: dict[str, Path], archive_path: str, source: Path) -> None:
    name = safe_relative(archive_path)
    parts = PurePosixPath(name).parts
    leaf = PurePosixPath(name).name.casefold()
    if name in entries:
        raise RuntimeError(f"duplicate archive path: {name}")
    if any(part.casefold() in {".git", "__pycache__", ".cache", "tmp"} for part in parts):
        raise RuntimeError(f"transient archive entry: {name}")
    if leaf.endswith((".pyc", ".pyo")) or any(term in leaf for term in ("token", "credential", "secret")):
        raise RuntimeError(f"credential/transient-like archive entry: {name}")
    read_regular(source)
    entries[name] = source


def add_root(entries: dict[str, Path], relative: str) -> None:
    add_entry(entries, relative, root_path(relative))


def translated_rows() -> list[dict[str, str]]:
    rows = manifest_rows("00_control/TRANSLATION_LEDGER.csv")
    if len(rows) != 29:
        raise RuntimeError(f"complete release requires exactly 29 ledger rows, found {len(rows)}")
    for ordinal, row in enumerate(rows, start=1):
        if int(row.get("ordinal", "0")) != ordinal or row.get("status") != "complete":
            raise RuntimeError(f"translation ledger is not contiguous and complete at ordinal {ordinal}")
        source_rel = safe_relative(str(row["source_path"]))
        target_rel = safe_relative(str(row["target_path"]))
        if not target_rel.startswith("source/id-ID/"):
            raise RuntimeError(f"unexpected target locale path: {target_rel}")
        source = read_regular(root_path(f"authority/upstream/{source_rel}"))
        target = read_regular(root_path(target_rel))
        if len(source) != int(row["source_bytes"]) or sha256(source) != row["source_sha256"]:
            raise RuntimeError(f"source ledger identity mismatch: {source_rel}")
        if len(target) != int(row["target_bytes"]) or sha256(target) != row["target_sha256"]:
            raise RuntimeError(f"target ledger identity mismatch: {target_rel}")
    if rows[-1]["source_path"] != FINAL_SOURCE_PATH:
        raise RuntimeError("complete release does not end at hypothesis/ChiSquare.html")
    return rows


def validate_reader(rows: list[dict[str, str]]) -> tuple[dict[str, Path], dict[str, object]]:
    manifest_path = root_path("build/FIRST_UNIT_MANIFEST.csv")
    manifest_data = read_regular(manifest_path)
    reader_rows = manifest_rows("build/FIRST_UNIT_MANIFEST.csv")
    if not reader_rows:
        raise RuntimeError("reader manifest is empty")
    entries: dict[str, Path] = {}
    total = 0
    for row in reader_rows:
        relative = safe_relative(row["relative_path"])
        payload_path = root_path(f"build/html-id/{relative}")
        payload = read_regular(payload_path)
        if len(payload) != int(row["bytes"]) or sha256(payload) != row["sha256"]:
            raise RuntimeError(f"reader manifest mismatch: {relative}")
        add_entry(entries, relative, payload_path)
        total += len(payload)
    required_html = {row["source_path"] for row in rows}
    available = {row["relative_path"] for row in reader_rows}
    missing = sorted(required_html - available)
    if missing:
        raise RuntimeError(f"reader omits translated core pages: {missing}")

    ledger_data = read_regular(root_path("00_control/TRANSLATION_LEDGER.csv"))
    build = read_json("build/FIRST_UNIT_BUILD_RECEIPT.json")
    ledger = build.get("translation_ledger")
    reader = build.get("reader")
    if not isinstance(ledger, dict) or ledger.get("required_document_count") != 29:
        raise RuntimeError("build receipt is not bound to 29 documents")
    if ledger.get("sha256") != sha256(ledger_data):
        raise RuntimeError("build receipt is bound to a different translation ledger")
    if not isinstance(reader, dict) or reader.get("file_count") != len(reader_rows):
        raise RuntimeError("build receipt reader count mismatch")
    receipt_files = reader.get("files")
    if not isinstance(receipt_files, list) or len(receipt_files) != len(reader_rows):
        raise RuntimeError("build receipt reader inventory mismatch")
    manifest_identity = [
        {"relative_path": safe_relative(row["relative_path"]), "bytes": int(row["bytes"]), "sha256": row["sha256"]}
        for row in reader_rows
    ]
    receipt_identity = [
        {"relative_path": row.get("relative_path"), "bytes": row.get("bytes"), "sha256": row.get("sha256")}
        for row in receipt_files if isinstance(row, dict)
    ]
    if receipt_identity != manifest_identity:
        raise RuntimeError("build receipt file inventory differs from the reader manifest")
    build_scripts = build.get("scripts")
    if not isinstance(build_scripts, dict):
        raise RuntimeError("build receipt has no script identities")
    for row in build_scripts.values():
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("build receipt contains a malformed script identity")
        if sha256(read_regular(root_path(str(row["path"])))) != row.get("sha256"):
            raise RuntimeError(f"build receipt is stale relative to {row['path']}")

    qa = read_json("build/FIRST_UNIT_QA_RECEIPT.json")
    counts = qa.get("pass_counts")
    results = qa.get("results")
    qa_build = qa.get("build")
    if not isinstance(counts, dict) or counts.get("translated_pages") != 29:
        raise RuntimeError("reader QA receipt is not a complete 29-page pass")
    if counts.get("reader_files") != len(reader_rows) or counts.get("reader_bytes") != total:
        raise RuntimeError("reader QA receipt inventory mismatch")
    if not isinstance(results, dict) or set(results) != required_html:
        raise RuntimeError("reader QA receipt does not cover all 29 source documents")
    if any(not isinstance(value, dict) or value.get("reader_target_byte_identical") is not True for value in results.values()):
        raise RuntimeError("reader QA receipt contains a non-identical target")
    if not isinstance(qa_build, dict) or qa_build.get("reader_manifest_sha256") != sha256(manifest_data):
        raise RuntimeError("reader QA receipt manifest identity mismatch")
    qa_scripts = qa.get("scripts")
    if not isinstance(qa_scripts, dict):
        raise RuntimeError("reader QA receipt has no script identities")
    for row in qa_scripts.values():
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("reader QA receipt contains a malformed script identity")
        if sha256(read_regular(root_path(str(row["path"])))) != row.get("sha256"):
            raise RuntimeError(f"reader QA receipt is stale relative to {row['path']}")

    evidence = ("README.md", "LICENSE.md", *BUILD_EVIDENCE)
    for relative in evidence:
        add_entry(entries, f"_evidence/{Path(relative).name}", root_path(relative))
    return entries, {
        "file_count": len(reader_rows),
        "reader_bytes": total,
        "manifest_bytes": len(manifest_data),
        "manifest_sha256": sha256(manifest_data),
    }


def validate_pdf(reader_manifest_sha256: str) -> dict[str, object]:
    receipt = read_json("build/PDF_READER_RECEIPT.json")
    pdf = read_regular(PDF_SOURCE)
    documents = receipt.get("documents")
    if receipt.get("status") != "complete-29-of-29" or receipt.get("source_documents") != 29:
        raise RuntimeError("PDF receipt is not complete-29-of-29")
    if not isinstance(documents, list) or [row.get("ordinal") for row in documents if isinstance(row, dict)] != list(range(1, 30)):
        raise RuntimeError("PDF receipt document sequence is not exactly 1 through 29")
    if receipt.get("bytes") != len(pdf) or receipt.get("sha256") != sha256(pdf):
        raise RuntimeError("PDF receipt identity mismatch")
    prerequisites = receipt.get("prerequisites")
    if not isinstance(prerequisites, list):
        raise RuntimeError("PDF receipt has no prerequisite inventory")
    prerequisite_by_path = {
        row.get("path"): row
        for row in prerequisites
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    if len(prerequisite_by_path) != len(prerequisites):
        raise RuntimeError("PDF receipt prerequisite inventory is malformed or duplicated")
    for relative in (
        "build/FIRST_UNIT_MANIFEST.csv",
        "build/FIRST_UNIT_BUILD_RECEIPT.json",
        "build/FIRST_UNIT_QA_RECEIPT.json",
    ):
        payload = read_regular(root_path(relative))
        prerequisite = prerequisite_by_path.get(relative)
        if (
            not isinstance(prerequisite, dict)
            or prerequisite.get("bytes") != len(payload)
            or prerequisite.get("sha256") != sha256(payload)
        ):
            raise RuntimeError(f"PDF receipt is stale relative to {relative}")
    if prerequisite_by_path["build/FIRST_UNIT_MANIFEST.csv"].get("sha256") != reader_manifest_sha256:
        raise RuntimeError("PDF receipt reader-manifest identity mismatch")
    if receipt.get("builder_sha256") != sha256(read_regular(root_path("scripts/build_pdf_reader.py"))):
        raise RuntimeError("PDF receipt is stale relative to build_pdf_reader.py")
    if receipt.get("renderer_sha256") != sha256(read_regular(root_path("scripts/render_pdf_pages.mjs"))):
        raise RuntimeError("PDF receipt is stale relative to render_pdf_pages.mjs")
    physical_pages = receipt.get("physical_pages")
    if not isinstance(physical_pages, int) or physical_pages <= 29:
        raise RuntimeError("PDF receipt has an implausible physical page count")
    license_payload = read_regular(root_path("LICENSE.md"))
    license_identity = receipt.get("license")
    if (
        not isinstance(license_identity, dict)
        or license_identity.get("path") != "LICENSE.md"
        or license_identity.get("bytes") != len(license_payload)
        or license_identity.get("sha256") != sha256(license_payload)
    ):
        raise RuntimeError("PDF receipt is stale relative to LICENSE.md")

    visual = read_json("build/PDF_VISUAL_QA_RECEIPT.json")
    visual_pdf = visual.get("pdf")
    render = visual.get("poppler_render")
    manual = visual.get("manual_visual_review")
    if visual.get("result") != "pass" or not isinstance(visual_pdf, dict) or not isinstance(render, dict) or not isinstance(manual, dict):
        raise RuntimeError("PDF visual QA did not pass")
    if visual_pdf.get("bytes") != len(pdf) or visual_pdf.get("sha256") != sha256(pdf) or visual_pdf.get("physical_pages") != physical_pages:
        raise RuntimeError("PDF visual QA identity mismatch")
    if render.get("png_pages") != physical_pages or render.get("edge_clipping_candidates") != 0:
        raise RuntimeError("PDF Poppler render coverage failed")
    reviewed = [value for key, value in manual.items() if key.startswith("all_") and key.endswith("_pages_reviewed_in_contact_sheets")]
    if manual.get("observed_defects") != 0 or True not in reviewed:
        raise RuntimeError("PDF manual visual review is incomplete or records defects")
    return {"bytes": len(pdf), "sha256": sha256(pdf), "physical_pages": physical_pages}


def validate_backend() -> dict[str, object]:
    receipt = read_json("backend/BACKEND_RECEIPT.json")
    counts = receipt.get("counts")
    outputs = receipt.get("outputs")
    binding = receipt.get("translation_binding")
    if not isinstance(counts, dict) or not isinstance(outputs, dict) or not isinstance(binding, dict):
        raise RuntimeError("backend receipt is incomplete")
    documents = binding.get("documents")
    entities_binding = binding.get("entities")
    if binding.get("complete_core_required") is not True or binding.get("ledger_rows") != 29:
        raise RuntimeError("backend is not bound to the complete core")
    ledger_data = read_regular(root_path("00_control/TRANSLATION_LEDGER.csv"))
    if binding.get("ledger_bytes") != len(ledger_data) or binding.get("ledger_sha256") != sha256(ledger_data):
        raise RuntimeError("backend receipt is stale relative to the translation ledger")
    if documents != {"total": 29, "translated": 29, "untranslated": 0}:
        raise RuntimeError("backend document translation binding is incomplete")
    if not isinstance(entities_binding, dict) or entities_binding.get("untranslated") != 0:
        raise RuntimeError("backend contains untranslated entities")
    result: dict[str, object] = {}
    generator = receipt.get("generator")
    if not isinstance(generator, dict) or not isinstance(generator.get("path"), str):
        raise RuntimeError("backend receipt has no generator identity")
    if sha256(read_regular(root_path(str(generator["path"])))) != generator.get("sha256"):
        raise RuntimeError("backend receipt is stale relative to its generator")
    for filename, records_key in (("entities.jsonl", "entities_total"), ("relations.csv", "relations_total")):
        payload = read_regular(root_path(f"backend/{filename}"))
        row = outputs.get(filename)
        if not isinstance(row, dict) or row.get("bytes") != len(payload) or row.get("sha256") != sha256(payload):
            raise RuntimeError(f"backend receipt identity mismatch: {filename}")
        if row.get("records") != counts.get(records_key):
            raise RuntimeError(f"backend record count mismatch: {filename}")
        result[filename] = {"bytes": len(payload), "records": row["records"], "sha256": sha256(payload)}
    return result


def final_control_paths(checkpoint: str, browser_qa: str) -> tuple[str, str]:
    checkpoint_rel = safe_relative(checkpoint)
    browser_rel = safe_relative(browser_qa)
    if not checkpoint_rel.startswith("00_control/") or not browser_rel.startswith("00_control/"):
        raise RuntimeError("final checkpoint and browser QA must be exact 00_control paths")
    checkpoint_data = read_regular(root_path(checkpoint_rel))
    browser_data = read_regular(root_path(browser_rel))
    if b"29" not in checkpoint_data or b"complete" not in checkpoint_data.lower():
        raise RuntimeError("final checkpoint does not visibly identify complete 29-page scope")
    browser = json.loads(browser_data.decode("utf-8"))
    if not isinstance(browser, dict) or browser.get("result") != "pass":
        raise RuntimeError("final live-browser QA receipt does not report pass")
    encoded = canonical_json(browser)
    if b"29" not in encoded:
        raise RuntimeError("final live-browser QA receipt does not identify 29-page scope")
    return checkpoint_rel, browser_rel


def source_entries(rows: list[dict[str, str]], checkpoint: str, browser_qa: str) -> dict[str, Path]:
    entries: dict[str, Path] = {}
    fixed = (
        ".gitattributes",
        "README.md",
        "LICENSE.md",
        "requirements.txt",
        *SOURCE_AUTHORITY,
        *CORE_CONTROLS,
        checkpoint,
        browser_qa,
        *BUILD_EVIDENCE,
        *REPRODUCIBILITY_SCRIPTS,
    )
    for relative in fixed:
        add_root(entries, relative)
    for path in sorted((ROOT / "scripts").glob("localize_*.py"), key=lambda item: item.name.casefold()):
        add_entry(entries, path.relative_to(ROOT).as_posix(), path)
    for row in rows:
        source_rel = safe_relative(row["source_path"])
        target_rel = safe_relative(row["target_path"])
        add_root(entries, target_rel)
        add_root(entries, f"authority/upstream/{source_rel}")
    target_only = "source/id-ID/random/interval/Tails-id.svg"
    if root_path(target_only).is_file():
        add_root(entries, target_only)
    licenses = ROOT / "authority" / "component-licenses"
    for path in sorted(licenses.rglob("*"), key=lambda item: item.as_posix().casefold()):
        if path.is_file():
            add_entry(entries, path.relative_to(ROOT).as_posix(), path)
    return entries


def backend_entries() -> dict[str, Path]:
    entries: dict[str, Path] = {}
    for relative in (
        "backend/entities.jsonl",
        "backend/relations.csv",
        "backend/entities.schema.json",
        "backend/BACKEND_RECEIPT.json",
        "00_control/TRANSLATION_LEDGER.csv",
        "00_control/ADVERSE_LEDGER.jsonl",
        "authority/SOURCE_URL_MANIFEST.csv",
        "authority/SOURCE_FREEZE_RECEIPT.json",
        "build/FIRST_UNIT_MANIFEST.csv",
        "LICENSE.md",
    ):
        add_root(entries, relative)
    return entries


def zip_payload(entries: dict[str, Path]) -> tuple[bytes, list[dict[str, object]]]:
    buffer = io.BytesIO()
    inventory: list[dict[str, object]] = []
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as archive:
        for name, source in sorted(entries.items(), key=lambda item: item[0].casefold()):
            data = read_regular(source)
            info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.flag_bits |= 0x800
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            inventory.append({"bytes": len(data), "path": name, "sha256": sha256(data)})
    payload = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
        if archive.testzip() is not None or archive.namelist() != [str(row["path"]) for row in inventory]:
            raise RuntimeError("generated ZIP failed exact inventory verification")
        for row in inventory:
            data = archive.read(str(row["path"]))
            if len(data) != row["bytes"] or sha256(data) != row["sha256"]:
                raise RuntimeError(f"generated ZIP entry failed verification: {row['path']}")
    return payload, inventory


def artifact(path: Path, data: bytes, kind: str, **extra: object) -> dict[str, object]:
    return {"bytes": len(data), "filename": path.name, "kind": kind, "sha256": sha256(data), **extra}


def build_outputs(source_commit: str, checkpoint: str, browser_qa: str) -> tuple[dict[Path, bytes], dict[str, object]]:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise RuntimeError("--source-commit must be an exact lowercase 40-hex Git commit")
    checkpoint_rel, browser_rel = final_control_paths(checkpoint, browser_qa)
    readme_text = read_regular(root_path("README.md")).decode("utf-8")
    license_text = read_regular(root_path("LICENSE.md")).decode("utf-8")
    if not re.search(r"29\s*(?:dari|/)\s*29", readme_text, re.IGNORECASE):
        raise RuntimeError("README does not state the complete 29/29 scope")
    if "edition in progress" in license_text.casefold():
        raise RuntimeError("LICENSE still labels the complete edition as in progress")
    if "rilis publik terakhir yang sepenuhnya diverifikasi masih berada pada" in readme_text.casefold():
        raise RuntimeError("README still presents the 16-page checkpoint as the current release boundary")
    rows = translated_rows()
    reader_entries, reader_summary = validate_reader(rows)
    pdf_summary = validate_pdf(str(reader_summary["manifest_sha256"]))
    backend_summary = validate_backend()
    for relative in (checkpoint_rel, browser_rel):
        add_entry(reader_entries, f"_evidence/{Path(relative).name}", root_path(relative))

    package_specs = (
        (READER_ZIP, "offline-html-reader", reader_entries),
        (SOURCE_ZIP, "editable-source-and-bounded-provenance", source_entries(rows, checkpoint_rel, browser_rel)),
        (BACKEND_ZIP, "locale-neutral-modular-backend", backend_entries()),
    )
    outputs: dict[Path, bytes] = {}
    package_artifacts: list[dict[str, object]] = []
    for path, kind, entries in package_specs:
        payload, inventory = zip_payload(entries)
        outputs[path] = payload
        package_artifacts.append(artifact(
            path,
            payload,
            kind,
            entries=inventory,
            entry_count=len(inventory),
            uncompressed_bytes=sum(int(row["bytes"]) for row in inventory),
        ))

    pdf = read_regular(PDF_SOURCE)
    license_data = read_regular(root_path("LICENSE.md"))
    outputs[PDF_OUT] = pdf
    outputs[LICENSE_OUT] = license_data
    release = {
        "schema": "o006.random.zenodo-release.v3",
        "version": VERSION,
        "checkpoint": {
            "complete": True,
            "first_page": rows[0]["source_path"],
            "last_page": rows[-1]["source_path"],
            "next_page": None,
            "translated_pages": 29,
            "total_pages": 29,
        },
        "artifacts": [
            artifact(PDF_OUT, pdf, "reader-first-pdf", physical_pages=pdf_summary["physical_pages"]),
            *package_artifacts,
            artifact(LICENSE_OUT, license_data, "component-rights-notice"),
        ],
        "backend": backend_summary,
        "reader": reader_summary,
        "quality_evidence": {
            "checkpoint": checkpoint_rel,
            "live_browser_qa": browser_rel,
            "pdf_receipt_sha256": sha256(read_regular(root_path("build/PDF_READER_RECEIPT.json"))),
            "pdf_visual_qa_receipt_sha256": sha256(read_regular(root_path("build/PDF_VISUAL_QA_RECEIPT.json"))),
            "reader_build_receipt_sha256": sha256(read_regular(root_path("build/FIRST_UNIT_BUILD_RECEIPT.json"))),
            "reader_qa_receipt_sha256": sha256(read_regular(root_path("build/FIRST_UNIT_QA_RECEIPT.json"))),
        },
        "translation_provenance": MODEL_PROVENANCE,
        "rights_model": "component-separated; Random landing CC BY 2.0; Random Credits links CC BY 1.0; MathJax Apache-2.0; identified reader assets CC0; no uniform aggregate relicensing claim",
        "exclusions": [
            "Git internals, caches, temporary build trees, and visual-QA raster pages",
            "credentials and local user data",
            "bulk upstream closure outside the exact 29-page authority set",
            "third-party biography media and datasets without a proved redistribution grant",
            "historical duplicate checkpoint packages and raw publication-debug dumps",
        ],
        "github": {
            "repository": "https://github.com/KokunoYumeto/mathematical-statistics-id",
            "content_release": f"https://github.com/KokunoYumeto/mathematical-statistics-id/releases/tag/{TAG}",
            "source_commit": source_commit,
        },
        "zenodo": {
            "concept_doi": "10.5281/zenodo.22059763",
            "concept_record_id": "22059763",
            "previous_record_id": "22071140",
            "version": VERSION,
        },
    }
    manifest_data = canonical_json(release)
    outputs[RELEASE_MANIFEST] = manifest_data
    # SHA256SUMS intentionally omits itself.  A checksum file cannot contain a
    # stable checksum of its own final bytes.
    outputs[SHA256SUMS] = (
        "\n".join(
            f"{sha256(data)}  {path.name}"
            for path, data in sorted(outputs.items(), key=lambda item: item[0].name.casefold())
        )
        + "\n"
    ).encode("utf-8")
    total = sum(len(data) for data in outputs.values())
    if total >= PAYLOAD_CAP:
        raise RuntimeError(f"release payload must be below {PAYLOAD_CAP:,} bytes; found {total:,}")
    return outputs, release


def tooling_self_check() -> dict[str, object]:
    expected = (
        PDF_OUT.name,
        READER_ZIP.name,
        SOURCE_ZIP.name,
        BACKEND_ZIP.name,
        LICENSE_OUT.name,
        RELEASE_MANIFEST.name,
        SHA256SUMS.name,
    )
    if len(set(expected)) != 7 or expected[0][:3] != "00_":
        raise RuntimeError("release filenames are not unique and reader-first")
    if VERSION not in PDF_OUT.name or TAG != f"v{VERSION}":
        raise RuntimeError("version/tag constants disagree")
    for relative in REPRODUCIBILITY_SCRIPTS:
        read_regular(root_path(relative))
    return {
        "mode": "tooling-self-check",
        "network_access": False,
        "credential_access": False,
        "version": VERSION,
        "release_files": list(expected),
        "payload_cap_bytes": PAYLOAD_CAP,
        "checksums_self_entry": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--tooling-self-check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check-only", action="store_true")
    parser.add_argument("--source-commit")
    parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    parser.add_argument("--browser-qa", default=DEFAULT_BROWSER_QA)
    args = parser.parse_args()
    if args.tooling_self_check:
        print(json.dumps(tooling_self_check(), ensure_ascii=False, sort_keys=True))
        return
    if not args.source_commit:
        parser.error("--source-commit is required for --write and --check-only")
    outputs, release = build_outputs(args.source_commit, args.checkpoint, args.browser_qa)
    if args.check_only:
        for path, expected in outputs.items():
            if read_regular(path) != expected:
                raise RuntimeError(f"stale/noncanonical release artifact: {path.name}")
        result_mode = "verified"
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
        result_mode = "written"
    print(json.dumps({
        "mode": result_mode,
        "version": VERSION,
        "payload_bytes": sum(len(data) for data in outputs.values()),
        "payload_cap_bytes": PAYLOAD_CAP,
        "source_commit": release["github"]["source_commit"],
        "artifacts": [
            {"filename": path.name, "bytes": len(data), "sha256": sha256(data)}
            for path, data in sorted(outputs.items(), key=lambda item: item[0].name.casefold())
        ],
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
