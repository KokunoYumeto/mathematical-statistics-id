#!/usr/bin/env python3
"""Anonymous exact-byte readback for the complete 29/29 GitHub boundary.

The verifier never reads credentials.  It checks every Pages-manifest file,
every bounded source/backend entry named by the Zenodo release manifest, the
successful Pages workflow, the exact release tag, and the complete PDF asset.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path, PurePosixPath

import requests


ROOT = Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPOSITORY = "mathematical-statistics-id"
BRANCH = "main"
VERSION = "2026.08.24.29"
TAG = "v2026.08.24.29"
PREVIOUS_PUBLIC_COMMIT = "4677fcf1ef8357de89ae0afd4e640e8076530873"
PAGES_BASE = f"https://{OWNER.lower()}.github.io/{REPOSITORY}/"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}"
RELEASE_DIR = ROOT / "release" / "zenodo" / VERSION
RELEASE_MANIFEST = RELEASE_DIR / f"50_mathematical-statistics-id-{VERSION}-release-manifest.json"
PDF_SOURCE = ROOT / "output" / "pdf" / "statistika-matematis-id-reader.pdf"
DEFAULT_ASSET_NAME = "statistika-matematis-id-reader.pdf"
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def safe_relative(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise RuntimeError(f"unsafe manifest path: {value}")
    return path.as_posix()


def local_bytes(relative: str) -> bytes:
    normalized = safe_relative(relative)
    path = (ROOT / Path(normalized)).resolve(strict=True)
    path.relative_to(ROOT.resolve())
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"raw readback input is not a regular local file: {normalized}")
    return path.read_bytes()


def read_release_manifest() -> dict[str, object]:
    value = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("release manifest root is not an object")
    checkpoint = value.get("checkpoint")
    if value.get("version") != VERSION or not isinstance(checkpoint, dict):
        raise RuntimeError("release manifest version/scope is invalid")
    if checkpoint.get("complete") is not True or checkpoint.get("translated_pages") != 29 or checkpoint.get("total_pages") != 29:
        raise RuntimeError("release manifest is not complete 29/29")
    return value


def reader_manifest() -> tuple[bytes, list[dict[str, str]]]:
    payload = local_bytes("build/FIRST_UNIT_MANIFEST.csv")
    rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8"), newline="")))
    if not rows:
        raise RuntimeError("reader manifest is empty")
    names: set[str] = set()
    total = 0
    for row in rows:
        relative = safe_relative(row["relative_path"])
        if relative in names:
            raise RuntimeError(f"duplicate reader-manifest path: {relative}")
        names.add(relative)
        data = local_bytes(f"build/html-id/{relative}")
        if len(data) != int(row["bytes"]) or digest(data) != row["sha256"]:
            raise RuntimeError(f"local reader-manifest mismatch: {relative}")
        total += len(data)
    ledger = list(csv.DictReader(io.StringIO(local_bytes("00_control/TRANSLATION_LEDGER.csv").decode("utf-8"), newline="")))
    if len(ledger) != 29 or any(int(row.get("ordinal", "0")) != index or row.get("status") != "complete" for index, row in enumerate(ledger, 1)):
        raise RuntimeError("translation ledger is not exactly complete ordinals 1 through 29")
    missing = sorted({row["source_path"] for row in ledger} - names)
    if missing:
        raise RuntimeError(f"reader manifest omits core pages: {missing}")
    return payload, rows


def package_raw_inventory(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise RuntimeError("release manifest has no artifacts")
    selected_kinds = {"editable-source-and-bounded-provenance", "locale-neutral-modular-backend"}
    selected = [row for row in artifacts if isinstance(row, dict) and row.get("kind") in selected_kinds]
    if {str(row.get("kind")) for row in selected} != selected_kinds:
        raise RuntimeError("release manifest omits bounded source or backend inventory")
    inventory: dict[str, dict[str, object]] = {}
    for artifact in selected:
        entries = artifact.get("entries")
        if not isinstance(entries, list) or not entries:
            raise RuntimeError(f"release artifact has no entry inventory: {artifact.get('filename')}")
        for row in entries:
            if not isinstance(row, dict):
                raise RuntimeError("release entry inventory contains a non-object")
            relative = safe_relative(str(row.get("path", "")))
            local = local_bytes(relative)
            expected = {"bytes": int(row.get("bytes", -1)), "sha256": str(row.get("sha256", ""))}
            if len(local) != expected["bytes"] or digest(local) != expected["sha256"]:
                raise RuntimeError(f"release/raw local identity mismatch: {relative}")
            previous = inventory.get(relative)
            if previous is not None and previous != expected:
                raise RuntimeError(f"conflicting duplicate release inventory: {relative}")
            inventory[relative] = expected
    if len(inventory) < 29:
        raise RuntimeError("bounded GitHub raw inventory is implausibly small")
    return inventory


def validate_release_files(manifest: dict[str, object]) -> dict[str, object]:
    sums_path = RELEASE_DIR / "SHA256SUMS.txt"
    sums: dict[str, str] = {}
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\]+)", line)
        if not match or match.group(2) in sums:
            raise RuntimeError("malformed or duplicate SHA256SUMS row")
        sums[match.group(2)] = match.group(1)
    if "SHA256SUMS.txt" in sums:
        raise RuntimeError("SHA256SUMS must not claim an unstable checksum of itself")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise RuntimeError("release artifact inventory missing")
    artifact_names = {str(row.get("filename")) for row in artifacts if isinstance(row, dict)}
    manifest_name = RELEASE_MANIFEST.name
    expected_sums = artifact_names | {manifest_name}
    if set(sums) != expected_sums:
        raise RuntimeError("SHA256SUMS does not exactly cover release artifacts plus the manifest")
    for name, expected in sums.items():
        path = RELEASE_DIR / name
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"local release checksum mismatch: {name}")
    for row in artifacts:
        if not isinstance(row, dict):
            raise RuntimeError("release artifact inventory contains a non-object")
        name = str(row.get("filename", ""))
        path = RELEASE_DIR / name
        if name not in sums or row.get("bytes") != path.stat().st_size or row.get("sha256") != sums[name]:
            raise RuntimeError(f"release manifest artifact identity mismatch: {name}")
    pdf_artifacts = [row for row in artifacts if isinstance(row, dict) and row.get("kind") == "reader-first-pdf"]
    if len(pdf_artifacts) != 1:
        raise RuntimeError("release manifest must contain one reader-first PDF")
    pdf = PDF_SOURCE.read_bytes()
    pdf_row = pdf_artifacts[0]
    if len(pdf) != pdf_row.get("bytes") or digest(pdf) != pdf_row.get("sha256"):
        raise RuntimeError("local PDF does not match release manifest")
    return {
        "bytes": len(pdf),
        "sha256": digest(pdf),
        "physical_pages": pdf_row.get("physical_pages"),
        "checksum_rows": len(sums),
    }


def api_json(session: requests.Session, url: str, label: str) -> dict[str, object]:
    response = session.get(url, headers={"Accept": "application/vnd.github+json"}, timeout=90)
    if response.status_code != 200:
        raise RuntimeError(f"{label} failed: HTTP {response.status_code}")
    value = response.json()
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} response was not an object")
    return value


def download(session: requests.Session, url: str, label: str) -> bytes:
    response = session.get(url, headers={"Cache-Control": "no-cache"}, timeout=180)
    if response.status_code != 200:
        raise RuntimeError(f"{label} failed: HTTP {response.status_code}")
    return response.content


def stream(session: requests.Session, url: str, label: str) -> tuple[int, str]:
    response = session.get(url, stream=True, timeout=900)
    if response.status_code != 200:
        raise RuntimeError(f"{label} failed: HTTP {response.status_code}")
    total = 0
    value = hashlib.sha256()
    for chunk in response.iter_content(1024 * 1024):
        if chunk:
            total += len(chunk)
            value.update(chunk)
    return total, value.hexdigest()


def resolve_tag_commit(session: requests.Session) -> str:
    reference = api_json(session, f"{API_BASE}/git/ref/tags/{TAG}", "GitHub tag reference")
    target = reference.get("object")
    if not isinstance(target, dict):
        raise RuntimeError("GitHub tag reference has no target")
    object_type = target.get("type")
    sha = str(target.get("sha", ""))
    if object_type == "commit":
        return sha
    if object_type == "tag":
        annotated = api_json(session, f"{API_BASE}/git/tags/{sha}", "GitHub annotated tag")
        nested = annotated.get("object")
        if not isinstance(nested, dict) or nested.get("type") != "commit":
            raise RuntimeError("GitHub annotated tag does not resolve directly to a commit")
        return str(nested.get("sha", ""))
    raise RuntimeError(f"unsupported GitHub tag target type: {object_type}")


def write_receipt(relative: str | None, value: dict[str, object]) -> None:
    if relative is None:
        return
    normalized = Path(relative.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise RuntimeError("receipt path must be a safe repository-relative path")
    path = (ROOT / normalized).resolve()
    path.relative_to(ROOT.resolve())
    if any(term in path.name.casefold() for term in ("token", "credential", "secret")):
        raise RuntimeError("refusing a credential-like receipt filename")
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary.write_bytes(payload)
    temporary.replace(path)


def local_preflight(commit: str) -> tuple[dict[str, object], bytes, list[dict[str, str]], dict[str, dict[str, object]], dict[str, object]]:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError("--commit must be an exact lowercase 40-hex commit")
    manifest = read_release_manifest()
    github = manifest.get("github")
    if not isinstance(github, dict) or github.get("source_commit") != commit:
        raise RuntimeError("--commit does not match the release manifest source commit")
    reader_data, reader_rows = reader_manifest()
    raw_inventory = package_raw_inventory(manifest)
    pdf = validate_release_files(manifest)
    return manifest, reader_data, reader_rows, raw_inventory, pdf


def tooling_self_check() -> dict[str, object]:
    if VERSION != "2026.08.24.29" or TAG != f"v{VERSION}" or len(PREVIOUS_PUBLIC_COMMIT) != 40:
        raise RuntimeError("GitHub publication constants are invalid")
    return {
        "mode": "tooling-self-check",
        "version": VERSION,
        "tag": TAG,
        "repository": f"{OWNER}/{REPOSITORY}",
        "network_access": False,
        "credential_access": False,
        "verification_scope": ["every Pages manifest row", "bounded source/backend package inventory", "workflow", "tag", "release PDF"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--tooling-self-check", action="store_true")
    mode.add_argument("--local-preflight", action="store_true")
    mode.add_argument("--verify-public", action="store_true")
    parser.add_argument("--commit")
    parser.add_argument("--workflow-run-id", type=int)
    parser.add_argument("--asset-name", default=DEFAULT_ASSET_NAME)
    parser.add_argument("--receipt-out", help="optional safe repository-relative sanitized JSON receipt")
    args = parser.parse_args()
    if args.tooling_self_check:
        print(json.dumps(tooling_self_check(), ensure_ascii=False, sort_keys=True))
        return
    if not args.commit:
        parser.error("--commit is required for --local-preflight and --verify-public")
    manifest, reader_data, reader_rows, raw_inventory, pdf = local_preflight(args.commit)
    summary: dict[str, object] = {
        "schema": "o006.random.github-complete-publication-readback.v1",
        "result": "pass",
        "mode": "local-preflight" if args.local_preflight else "verify-public",
        "credential_access": False,
        "version": VERSION,
        "repository": {
            "url": f"https://github.com/{OWNER}/{REPOSITORY}",
            "branch": BRANCH,
            "commit": args.commit,
            "previous_public_commit": PREVIOUS_PUBLIC_COMMIT,
        },
        "local_scope": {
            "reader_files": len(reader_rows),
            "reader_bytes": sum(int(row["bytes"]) for row in reader_rows),
            "reader_manifest_sha256": digest(reader_data),
            "bounded_raw_files": len(raw_inventory),
            "release_pdf": pdf,
            "complete_scope": "29 of 29 core pages",
        },
    }
    if args.local_preflight:
        summary["network_access"] = False
        write_receipt(args.receipt_out, summary)
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return
    if not args.workflow_run_id or args.workflow_run_id <= 0:
        parser.error("--workflow-run-id is required and must be positive for --verify-public")

    session = requests.Session()
    session.headers.update({"User-Agent": "O006-complete-anonymous-public-readback/1.0"})
    commit_meta = api_json(session, f"{API_BASE}/commits/{args.commit}", "GitHub commit")
    if commit_meta.get("sha") != args.commit:
        raise RuntimeError("public GitHub commit identity mismatch")
    workflow = api_json(session, f"{API_BASE}/actions/runs/{args.workflow_run_id}", "GitHub workflow")
    if workflow.get("head_sha") != args.commit or workflow.get("conclusion") != "success":
        raise RuntimeError("public Pages workflow did not succeed at the release commit")
    tag_commit = resolve_tag_commit(session)
    if tag_commit != args.commit:
        raise RuntimeError("public release tag does not resolve to the release commit")

    verified_pages: list[dict[str, object]] = []
    for row in reader_rows:
        relative = safe_relative(row["relative_path"])
        payload = download(session, f"{PAGES_BASE}{relative}?v={args.commit[:12]}", f"Pages {relative}")
        if len(payload) != int(row["bytes"]) or digest(payload) != row["sha256"]:
            raise RuntimeError(f"Pages identity mismatch: {relative}")
        verified_pages.append({"path": relative, "bytes": len(payload), "sha256": digest(payload)})
    root = download(session, f"{PAGES_BASE}?v={args.commit[:12]}", "Pages root").decode("utf-8")
    if MODEL_PROVENANCE not in root or "Kyle Siegrist" not in root:
        raise RuntimeError("public Pages root lacks model provenance or source credit")
    if not re.search(r"29\s*(?:dari|/)\s*29", root, re.IGNORECASE):
        raise RuntimeError("public Pages root lacks the complete 29/29 claim")

    raw_base = f"https://raw.githubusercontent.com/{OWNER}/{REPOSITORY}/{args.commit}/"
    raw_verified: list[dict[str, object]] = []
    for relative, expected in sorted(raw_inventory.items(), key=lambda item: item[0].casefold()):
        payload = download(session, f"{raw_base}{relative}", f"raw {relative}")
        if len(payload) != expected["bytes"] or digest(payload) != expected["sha256"]:
            raise RuntimeError(f"raw commit identity mismatch: {relative}")
        raw_verified.append({"path": relative, "bytes": len(payload), "sha256": digest(payload)})

    release = api_json(session, f"{API_BASE}/releases/tags/{TAG}", "GitHub release")
    if bool(release.get("draft")) or bool(release.get("prerelease")):
        raise RuntimeError("complete edition GitHub release is draft or prerelease")
    release_text = f"{release.get('name', '')}\n{release.get('body', '')}"
    if "29" not in release_text or not re.search(r"complete|lengkap", release_text, re.IGNORECASE):
        raise RuntimeError("GitHub release metadata does not identify the complete 29-page boundary")
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise RuntimeError("GitHub release assets response is invalid")
    asset_names = [str(row.get("name")) for row in assets if isinstance(row, dict)]
    if len(asset_names) != len(assets) or len(asset_names) != 1 or set(asset_names) != {args.asset_name}:
        raise RuntimeError(
            f"GitHub release asset inventory must be exactly one file named {args.asset_name}; "
            f"found {sorted(asset_names, key=str.casefold)}"
        )
    asset = assets[0]
    pdf_bytes, pdf_sha = stream(session, str(asset["browser_download_url"]), "public GitHub PDF asset")
    if pdf_bytes != pdf["bytes"] or pdf_sha != pdf["sha256"]:
        raise RuntimeError("public GitHub release PDF identity mismatch")

    summary.update({
        "workflow": {
            "run_id": args.workflow_run_id,
            "url": workflow.get("html_url"),
            "conclusion": workflow.get("conclusion"),
            "head_sha": workflow.get("head_sha"),
        },
        "pages_readback": {
            "url": PAGES_BASE,
            "method": "anonymous HTTPS download of every reader-manifest row",
            "files": len(verified_pages),
            "bytes": sum(int(row["bytes"]) for row in verified_pages),
            "manifest_sha256": digest(reader_data),
            "all_size_and_sha256_matches": True,
            "root_model_provenance_present": True,
            "root_source_author_credit_present": True,
            "root_complete_29_of_29_present": True,
        },
        "raw_commit_readback": {
            "method": "anonymous raw.githubusercontent.com exact bounded package inventory",
            "files": raw_verified,
        },
        "release": {
            "tag": TAG,
            "tag_commit": tag_commit,
            "url": release.get("html_url"),
            "draft": False,
            "prerelease": False,
            "completion_claim": "complete 29 of 29 core pages",
            "asset": {
                "name": asset.get("name"),
                "bytes": pdf_bytes,
                "sha256": pdf_sha,
                "anonymous_download_match": True,
            },
        },
    })
    write_receipt(args.receipt_out, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
