#!/usr/bin/env python3
"""Build the deterministic, redistribution-bounded Zenodo checkpoint package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026.08.22.13"
RELEASE_DIR = ROOT / "release" / "zenodo" / VERSION
READER_ZIP = RELEASE_DIR / f"mathematical-statistics-id-{VERSION}-reader.zip"
SOURCE_ZIP = RELEASE_DIR / f"mathematical-statistics-id-{VERSION}-source-provenance.zip"
BACKEND_ZIP = RELEASE_DIR / f"mathematical-statistics-id-{VERSION}-modular-backend.zip"
RELEASE_MANIFEST = RELEASE_DIR / f"mathematical-statistics-id-{VERSION}-release-manifest.json"
SHA256SUMS = RELEASE_DIR / "SHA256SUMS.txt"
ZIP_TIMESTAMP = (2026, 8, 22, 0, 0, 0)

PUBLISHED_ARTIFACTS = {
    "mathematical-statistics-id-2026.08.22.13-reader.zip": {
        "bytes": 875_600,
        "sha256": "c692d68526bce894a16158821746346f46267639c07ca1742917b659a79a2ddb",
    },
    "mathematical-statistics-id-2026.08.22.13-source-provenance.zip": {
        "bytes": 747_513,
        "sha256": "fbf68552bb0515ce29ca2b2eb43791d5b270d70164b21dd96a64c8d0f739994c",
    },
    "mathematical-statistics-id-2026.08.22.13-modular-backend.zip": {
        "bytes": 990_673,
        "sha256": "78cc226d4eb1bbfcf371e016bcc394b558847465bdee2ca7cd6965a648701a89",
    },
    "mathematical-statistics-id-2026.08.22.13-release-manifest.json": {
        "bytes": 33_081,
        "sha256": "de768b416689120ce5f1b2d7ad75401323bb5c525ce3d253c071426ba4e1bfa8",
    },
    "SHA256SUMS.txt": {
        "bytes": 503,
        "sha256": "ce873ab4249fa3612cceb3c72991f5d12c16963c06ccb3a25baf6e2cb7b1663b",
    },
}

ZENODO = {
    "concept_record_id": "22059763",
    "record_id": "22059764",
    "reserved_version_doi": "10.5281/zenodo.22059764",
    "title": "Statistika Matematis — Edisi Bahasa Indonesia (id-ID): Checkpoint 13 dari 29 (Belum Lengkap)",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_regular(path: Path) -> bytes:
    resolved = path.resolve(strict=True)
    resolved.relative_to(ROOT.resolve())
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        raise RuntimeError(f"non-regular package input: {path.relative_to(ROOT)}")
    if getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise RuntimeError(f"reparse package input: {path.relative_to(ROOT)}")
    return path.read_bytes()


def files_below(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise RuntimeError(f"missing package directory: {directory.relative_to(ROOT)}")
    return sorted(
        (path for path in directory.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(directory).as_posix().casefold(),
    )


def add_entry(entries: dict[str, Path], archive_path: str, source: Path) -> None:
    canonical = PurePosixPath(archive_path).as_posix()
    if canonical.startswith("/") or ".." in PurePosixPath(canonical).parts:
        raise RuntimeError(f"unsafe archive path: {archive_path}")
    if canonical in entries:
        raise RuntimeError(f"duplicate archive path: {canonical}")
    entries[canonical] = source


def root_relative_entries(paths: Iterable[Path]) -> dict[str, Path]:
    entries: dict[str, Path] = {}
    for path in paths:
        add_entry(entries, path.relative_to(ROOT).as_posix(), path)
    return entries


def core_authority_paths() -> list[Path]:
    receipt_path = ROOT / "authority" / "SOURCE_FREEZE_RECEIPT.json"
    receipt = json.loads(read_regular(receipt_path))
    core_paths = receipt.get("core_paths")
    if not isinstance(core_paths, list) or len(core_paths) != 29:
        raise RuntimeError("source freeze no longer declares exactly 29 core paths")
    result: list[Path] = []
    for value in core_paths:
        rel = PurePosixPath(str(value))
        if rel.is_absolute() or ".." in rel.parts:
            raise RuntimeError(f"unsafe core authority path: {value}")
        result.append(ROOT / "authority" / "upstream" / Path(rel.as_posix()))
    return result


def reader_entries() -> dict[str, Path]:
    reader = ROOT / "build" / "html-id"
    entries: dict[str, Path] = {}
    for path in files_below(reader):
        add_entry(entries, path.relative_to(reader).as_posix(), path)
    for path in (
        ROOT / "README.md",
        ROOT / "LICENSE.md",
        ROOT / "build" / "FIRST_UNIT_MANIFEST.csv",
        ROOT / "build" / "FIRST_UNIT_BUILD_RECEIPT.json",
        ROOT / "build" / "FIRST_UNIT_QA_RECEIPT.json",
        ROOT / "00_control" / "LIVE_BROWSER_QA_2026-08-22_THIRTEEN_PAGE.json",
        ROOT / "00_control" / "CHECKPOINT_2026-08-22_THIRTEEN_PAGE.md",
    ):
        add_entry(entries, f"_evidence/{path.name}", path)
    return entries


def source_entries() -> dict[str, Path]:
    paths: list[Path] = [
        ROOT / "README.md",
        ROOT / "LICENSE.md",
        ROOT / "requirements.txt",
        ROOT / ".gitattributes",
        ROOT / "authority" / "SOURCE_URL_MANIFEST.csv",
        ROOT / "authority" / "REFERENCE_URL_MANIFEST.csv",
        ROOT / "authority" / "SOURCE_FREEZE_RECEIPT.json",
        ROOT / "build" / "FIRST_UNIT_MANIFEST.csv",
        ROOT / "build" / "FIRST_UNIT_BUILD_RECEIPT.json",
        ROOT / "build" / "FIRST_UNIT_QA_RECEIPT.json",
    ]
    paths.extend(files_below(ROOT / "00_control"))
    paths.extend(files_below(ROOT / "source" / "id-ID"))
    paths.extend(
        sorted(
            (ROOT / "scripts").glob("*.py"),
            key=lambda path: path.name.casefold(),
        )
    )
    paths.extend(files_below(ROOT / "authority" / "component-licenses"))
    paths.extend(files_below(ROOT / "authority" / "runtime"))
    paths.extend(core_authority_paths())
    return root_relative_entries(paths)


def backend_entries() -> dict[str, Path]:
    paths = files_below(ROOT / "backend")
    paths.extend(
        [
            ROOT / "README.md",
            ROOT / "LICENSE.md",
            ROOT / "00_control" / "TRANSLATION_LEDGER.csv",
            ROOT / "authority" / "SOURCE_URL_MANIFEST.csv",
            ROOT / "authority" / "SOURCE_FREEZE_RECEIPT.json",
            ROOT / "build" / "FIRST_UNIT_MANIFEST.csv",
        ]
    )
    return root_relative_entries(paths)


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
        for archive_path, source in sorted(entries.items(), key=lambda item: item[0].casefold()):
            data = read_regular(source)
            info = zipfile.ZipInfo(archive_path, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.flag_bits |= 0x800
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            inventory.append(
                {"bytes": len(data), "path": archive_path, "sha256": sha256(data)}
            )
    return buffer.getvalue(), inventory


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def validate_reader_manifest() -> dict[str, object]:
    manifest_path = ROOT / "build" / "FIRST_UNIT_MANIFEST.csv"
    manifest_data = read_regular(manifest_path)
    rows = list(csv.DictReader(io.StringIO(manifest_data.decode("utf-8"), newline="")))
    if len(rows) != 43:
        raise RuntimeError(f"reader manifest count changed: {len(rows)}")
    total = 0
    for row in rows:
        path = ROOT / "build" / "html-id" / Path(row["relative_path"])
        data = read_regular(path)
        if len(data) != int(row["bytes"]) or sha256(data) != row["sha256"]:
            raise RuntimeError(f"reader manifest mismatch: {row['relative_path']}")
        total += len(data)
    if total != 2_415_553:
        raise RuntimeError(f"reader byte total changed: {total}")
    return {
        "bytes": len(manifest_data),
        "file_count": len(rows),
        "reader_bytes": total,
        "sha256": sha256(manifest_data),
    }


def verify_zip(path: Path, expected: list[dict[str, object]]) -> None:
    with zipfile.ZipFile(path, "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"corrupt ZIP entry in {path.name}")
        names = archive.namelist()
        expected_names = [str(item["path"]) for item in expected]
        if names != expected_names or len(names) != len(set(names)):
            raise RuntimeError(f"ZIP inventory mismatch: {path.name}")
        for item in expected:
            data = archive.read(str(item["path"]))
            if len(data) != item["bytes"] or sha256(data) != item["sha256"]:
                raise RuntimeError(f"ZIP entry mismatch: {path.name}:{item['path']}")


def verify_published_release() -> dict[str, object]:
    """Verify the immutable bytes already published as Zenodo version 13/29.

    Live controls necessarily change after publication.  They must never make
    an earlier DOI artifact look rebuildable or invite overwriting it.  The
    release manifest freezes every ZIP entry; the constants above freeze the
    five public outer files.
    """

    if not RELEASE_DIR.is_dir():
        raise RuntimeError(f"missing published release directory: {RELEASE_DIR}")
    actual_names = sorted(
        path.name for path in RELEASE_DIR.iterdir() if path.is_file()
    )
    expected_names = sorted(PUBLISHED_ARTIFACTS)
    if actual_names != expected_names:
        raise RuntimeError(
            f"published release inventory mismatch: {actual_names!r}"
        )

    outer: list[dict[str, object]] = []
    for name in expected_names:
        path = RELEASE_DIR / name
        data = read_regular(path)
        expected = PUBLISHED_ARTIFACTS[name]
        if len(data) != expected["bytes"] or sha256(data) != expected["sha256"]:
            raise RuntimeError(f"published artifact identity mismatch: {name}")
        outer.append(
            {"bytes": len(data), "filename": name, "sha256": sha256(data)}
        )

    manifest_data = read_regular(RELEASE_MANIFEST)
    release = json.loads(manifest_data)
    if canonical_json(release) != manifest_data:
        raise RuntimeError("release manifest is not canonical JSON")
    if release.get("schema") != "o006.random.zenodo-release.v1":
        raise RuntimeError("unexpected release-manifest schema")
    if release.get("checkpoint", {}).get("version") != VERSION:
        raise RuntimeError("release-manifest version mismatch")

    artifacts = release.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 3:
        raise RuntimeError("release manifest must describe exactly three ZIPs")
    artifact_by_name = {str(item.get("filename")): item for item in artifacts}
    expected_zip_names = {READER_ZIP.name, SOURCE_ZIP.name, BACKEND_ZIP.name}
    if set(artifact_by_name) != expected_zip_names:
        raise RuntimeError("release-manifest ZIP inventory mismatch")

    forbidden_parts = {".git", "__pycache__", ".cache", ".tmp"}
    for name in sorted(expected_zip_names):
        item = artifact_by_name[name]
        inventory = item.get("entries")
        if not isinstance(inventory, list):
            raise RuntimeError(f"missing ZIP entry inventory: {name}")
        if item.get("entry_count") != len(inventory):
            raise RuntimeError(f"ZIP entry count mismatch: {name}")
        if item.get("bytes") != PUBLISHED_ARTIFACTS[name]["bytes"]:
            raise RuntimeError(f"manifest outer byte mismatch: {name}")
        if item.get("sha256") != PUBLISHED_ARTIFACTS[name]["sha256"]:
            raise RuntimeError(f"manifest outer SHA-256 mismatch: {name}")
        for entry in inventory:
            entry_name = str(entry.get("path", ""))
            parts = {part.casefold() for part in PurePosixPath(entry_name).parts}
            leaf = PurePosixPath(entry_name).name.casefold()
            if parts & forbidden_parts or leaf.endswith((".pyc", ".pyo")):
                raise RuntimeError(f"forbidden transient ZIP entry: {name}:{entry_name}")
            if any(term in leaf for term in ("token", "credential", "secret")):
                raise RuntimeError(f"credential-like ZIP entry name: {name}:{entry_name}")
        verify_zip(RELEASE_DIR / name, inventory)

    sums_rows = [
        f"{artifact_by_name[name]['sha256']}  {name}"
        for name in sorted(expected_zip_names, key=str.casefold)
    ]
    sums_rows.append(f"{sha256(manifest_data)}  {RELEASE_MANIFEST.name}")
    expected_sums = ("\n".join(sums_rows) + "\n").encode("utf-8")
    if read_regular(SHA256SUMS) != expected_sums:
        raise RuntimeError("published SHA256SUMS content mismatch")

    return {
        "artifacts": outer,
        "immutable": True,
        "mode": "published-release-verified",
        "record_id": ZENODO["record_id"],
        "version": VERSION,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    if args.check_only:
        print(
            json.dumps(
                verify_published_release(), ensure_ascii=False, sort_keys=True
            )
        )
        return
    raise RuntimeError(
        f"Zenodo version {VERSION} is published and immutable; package the next "
        "checkpoint under a new version and release directory"
    )

    reader_manifest = validate_reader_manifest()
    package_specs = [
        (READER_ZIP, reader_entries()),
        (SOURCE_ZIP, source_entries()),
        (BACKEND_ZIP, backend_entries()),
    ]
    payloads: dict[Path, bytes] = {}
    inventories: dict[Path, list[dict[str, object]]] = {}
    for path, entries in package_specs:
        payload, inventory = zip_payload(entries)
        payloads[path] = payload
        inventories[path] = inventory

    artifacts = []
    for path, _ in package_specs:
        inventory = inventories[path]
        artifacts.append(
            {
                "bytes": len(payloads[path]),
                "entries": inventory,
                "entry_count": len(inventory),
                "filename": path.name,
                "sha256": sha256(payloads[path]),
                "uncompressed_bytes": sum(int(item["bytes"]) for item in inventory),
            }
        )

    release = {
        "artifacts": artifacts,
        "authority": {
            "core_files": 29,
            "source_manifest_bytes": 50913,
            "source_manifest_sha256": "d36e0f8bf9fa44a38a7504f9688a08af6787d88ede99298316a3e022b6f799f5",
        },
        "backend": {
            "entities": 6567,
            "entities_sha256": "b3aa63bb840cbde1e78dcef627c0e0e762a558e390d515de22c1a70dd8ca3843",
            "relations": 9035,
            "relations_sha256": "b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a",
            "translated_entities": 3521,
        },
        "checkpoint": {
            "complete": False,
            "last_page": "random/point/Likelihood.html",
            "next_page": "random/point/Bayes.html",
            "translated_pages": 13,
            "total_pages": 29,
            "version": VERSION,
        },
        "exclusions": [
            ".git and caches",
            "credentials and local user data",
            "untranslated closure assets not required by the reader",
            "third-party biography photographs and datasets without a proved redistribution grant",
        ],
        "reader": reader_manifest,
        "rights_model": "component-separated; Random landing CC BY 2.0; Random Credits links CC BY 1.0; MathJax Apache-2.0; identified reader assets CC0; no uniform aggregate relicensing claim",
        "schema": "o006.random.zenodo-release.v1",
        "zenodo": ZENODO,
    }
    manifest_data = canonical_json(release)
    sums_rows = [
        f"{artifact['sha256']}  {artifact['filename']}"
        for artifact in sorted(artifacts, key=lambda item: str(item["filename"]).casefold())
    ]
    sums_rows.append(f"{sha256(manifest_data)}  {RELEASE_MANIFEST.name}")
    sums_data = ("\n".join(sums_rows) + "\n").encode("utf-8")

    expected_outputs = {
        **payloads,
        RELEASE_MANIFEST: manifest_data,
        SHA256SUMS: sums_data,
    }
    if args.check_only:
        for path, expected in expected_outputs.items():
            actual = read_regular(path)
            if actual != expected:
                raise RuntimeError(f"stale/noncanonical release artifact: {path.name}")
    else:
        RELEASE_DIR.mkdir(parents=True, exist_ok=True)
        for path, data in expected_outputs.items():
            temporary = path.with_name(path.name + ".tmp")
            temporary.write_bytes(data)
            os.replace(temporary, path)

    for path, _ in package_specs:
        verify_zip(path, inventories[path])
    summary = {
        "artifacts": [
            {"bytes": len(data), "filename": path.name, "sha256": sha256(data)}
            for path, data in expected_outputs.items()
        ],
        "mode": "verified" if args.check_only else "written",
        "record_id": ZENODO["record_id"],
        "version": VERSION,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
