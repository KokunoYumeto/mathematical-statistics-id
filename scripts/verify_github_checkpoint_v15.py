#!/usr/bin/env python3
"""Credential-free public-byte verification for the O006 15/29 checkpoint."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPOSITORY = "mathematical-statistics-id"
COMMIT = "df7b2322ce75419e5c682f4b882af626a320bdf5"
PREVIOUS_COMMIT = "abbd9e2374cd295b78a68d80b06ea0e3e2300cb6"
WORKFLOW_RUN_ID = 32601081875
TAG = "v2026.08.22.15"
PAGES_BASE = f"https://{OWNER.lower()}.github.io/{REPOSITORY}/"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPOSITORY}/{COMMIT}/"
RELEASE_ASSET = "statistika-matematis-id-reader.pdf"
PDF_BYTES = 76_775_084
PDF_SHA256 = "7c4898505962f6978eb064c605a77fca9ccbcd3ba7f9238f9cf0d8ae974662ef"
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"
RAW_SELECTION = (
    "source/id-ID/random/point/Unbiased.html",
    "backend/entities.jsonl",
    "backend/BACKEND_RECEIPT.json",
    "00_control/CHECKPOINT_2026-08-22_FIFTEEN_PAGE.md",
    "00_control/LIVE_BROWSER_QA_2026-08-22_FIFTEEN_PAGE.json",
    "00_control/TERMINOLOGY_QA_2026-08-22.md",
    "build/FIRST_UNIT_MANIFEST.csv",
    "build/PDF_READER_RECEIPT.json",
    "README.md",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(response: requests.Response, action: str) -> requests.Response:
    if response.status_code != 200:
        raise RuntimeError(f"{action} failed with HTTP {response.status_code}")
    return response


def get_json(session: requests.Session, url: str, action: str) -> dict[str, object]:
    value = check(session.get(url, timeout=90), action).json()
    if not isinstance(value, dict):
        raise RuntimeError(f"{action} returned a non-object")
    return value


def stream_identity(session: requests.Session, url: str, action: str) -> tuple[int, str]:
    response = check(session.get(url, stream=True, timeout=900), action)
    digest = hashlib.sha256()
    total = 0
    for chunk in response.iter_content(1024 * 1024):
        if chunk:
            total += len(chunk)
            digest.update(chunk)
    return total, digest.hexdigest()


def committed_bytes(path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{COMMIT}:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def verify_pages(session: requests.Session) -> dict[str, object]:
    manifest = committed_bytes("build/FIRST_UNIT_MANIFEST.csv")
    rows = list(csv.DictReader(io.StringIO(manifest.decode("utf-8"), newline="")))
    if len(rows) != 45 or sha256(manifest) != "d6f51461a9db39f53f832912fbe4c865059177094564ca5a6d0b30cc3c1740aa":
        raise RuntimeError("committed reader manifest identity changed")
    verified: list[dict[str, object]] = []
    for attempt in range(12):
        verified.clear()
        failure: str | None = None
        for row in rows:
            rel = row["relative_path"]
            url = f"{PAGES_BASE}{quote(rel)}?v={COMMIT[:12]}"
            response = session.get(url, timeout=90, headers={"Cache-Control": "no-cache"})
            if response.status_code != 200:
                failure = f"{rel}: HTTP {response.status_code}"
                break
            payload = response.content
            if len(payload) != int(row["bytes"]) or sha256(payload) != row["sha256"]:
                failure = f"{rel}: identity mismatch"
                break
            verified.append({"path": rel, "bytes": len(payload), "sha256": sha256(payload)})
        if failure is None:
            break
        if attempt == 11:
            raise RuntimeError(f"Pages did not converge to the checkpoint: {failure}")
        time.sleep(10)
    root = check(
        session.get(f"{PAGES_BASE}?v={COMMIT[:12]}", timeout=90, headers={"Cache-Control": "no-cache"}),
        "read public Pages root",
    ).text
    if MODEL_PROVENANCE not in root or "Kyle Siegrist" not in root:
        raise RuntimeError("public reader root lacks required provenance or source credit")
    unbiased = next(row for row in verified if row["path"] == "random/point/Unbiased.html")
    return {
        "url": PAGES_BASE,
        "method": "Credential-free HTTPS download of every committed reader-manifest row.",
        "files": len(verified),
        "bytes": sum(int(row["bytes"]) for row in verified),
        "manifest_sha256": sha256(manifest),
        "all_size_and_sha256_matches": True,
        "root_model_provenance_present": True,
        "root_source_author_credit_present": True,
        "unbiased": unbiased,
    }


def verify_raw(session: requests.Session) -> dict[str, object]:
    total = 0
    for path in RAW_SELECTION:
        wanted = committed_bytes(path)
        response = check(session.get(f"{RAW_BASE}{quote(path)}", timeout=180), f"read raw {path}")
        if response.content != wanted:
            raise RuntimeError(f"raw commit mismatch: {path}")
        total += len(wanted)
    return {
        "method": "Credential-free raw.githubusercontent.com downloads at the exact commit.",
        "selected_files": len(RAW_SELECTION),
        "bytes": total,
        "all_size_and_sha256_matches": True,
        "selection": list(RAW_SELECTION),
    }


def main() -> None:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/vnd.github+json",
            "User-Agent": "O006-anonymous-public-readback/1.0",
        }
    )
    commit = get_json(session, f"{API_BASE}/commits/main", "read public main commit")
    if commit.get("sha") != COMMIT:
        raise RuntimeError("public main does not match the release commit")
    workflow = get_json(
        session, f"{API_BASE}/actions/runs/{WORKFLOW_RUN_ID}", "read public workflow run"
    )
    if workflow.get("head_sha") != COMMIT or workflow.get("conclusion") != "success":
        raise RuntimeError("public workflow did not succeed at the exact release commit")
    jobs = get_json(
        session, f"{API_BASE}/actions/runs/{WORKFLOW_RUN_ID}/jobs", "read public workflow jobs"
    ).get("jobs")
    if not isinstance(jobs, list) or not jobs or any(row.get("conclusion") != "success" for row in jobs):
        raise RuntimeError("one or more workflow jobs did not succeed")
    release = get_json(session, f"{API_BASE}/releases/tags/{TAG}", "read public release")
    if not release.get("prerelease") or MODEL_PROVENANCE not in str(release.get("body")):
        raise RuntimeError("release status or provenance is incorrect")
    tag = get_json(session, f"{API_BASE}/git/ref/tags/{TAG}", "read public release tag")
    if tag.get("object", {}).get("sha") != COMMIT:
        raise RuntimeError("release tag does not point to the checkpoint commit")
    assets = [row for row in release.get("assets", []) if row.get("name") == RELEASE_ASSET]
    if len(assets) != 1:
        raise RuntimeError("release does not expose exactly one reader PDF asset")
    asset_url = str(assets[0].get("browser_download_url"))
    asset_bytes, asset_hash = stream_identity(session, asset_url, "download public PDF asset")
    if asset_bytes != PDF_BYTES or asset_hash != PDF_SHA256:
        raise RuntimeError("public release PDF differs from the verified local reader")
    pages = verify_pages(session)
    raw = verify_raw(session)
    print(
        json.dumps(
            {
                "schema": "o006.random.github-publication-readback.v1",
                "result": "pass",
                "repository": {
                    "url": f"https://github.com/{OWNER}/{REPOSITORY}",
                    "branch": "main",
                    "commit": COMMIT,
                    "previous_public_commit": PREVIOUS_COMMIT,
                    "anonymous_api_commit_match": True,
                },
                "workflow": {
                    "run_id": WORKFLOW_RUN_ID,
                    "url": workflow.get("html_url"),
                    "result": "success",
                    "jobs": [
                        {"id": row.get("id"), "name": row.get("name"), "conclusion": row.get("conclusion")}
                        for row in jobs
                    ],
                },
                "pages_readback": pages,
                "raw_commit_readback": raw,
                "release": {
                    "tag": TAG,
                    "url": release.get("html_url"),
                    "prerelease": True,
                    "completion_claim": "15 of 29 core pages; incomplete edition",
                    "model_provenance_present": True,
                    "asset": {
                        "name": RELEASE_ASSET,
                        "url": asset_url,
                        "bytes": asset_bytes,
                        "sha256": asset_hash,
                        "anonymous_download_match": True,
                    },
                },
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
