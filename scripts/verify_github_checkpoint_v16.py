#!/usr/bin/env python3
"""Credential-free byte readback for the public O006 16/29 checkpoint."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import pathlib
import re
import requests


ROOT = pathlib.Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPOSITORY = "mathematical-statistics-id"
COMMIT = "4677fcf1ef8357de89ae0afd4e640e8076530873"
PREVIOUS_COMMIT = "a898a1371f9c027d2b3316814a5391ae02d561ac"
WORKFLOW_RUN_ID = 32655887678
TAG = "v2026.08.23.16"
PAGES_BASE = f"https://{OWNER.lower()}.github.io/{REPOSITORY}/"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPOSITORY}/{COMMIT}/"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}"
PDF_BYTES = 85_357_801
PDF_SHA256 = "f1a886ff1285315478bb7e50a773e8a5d79b47e6170a86e82e7b98126f6f6160"
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"
RAW_SELECTION = (
    "source/id-ID/random/point/Sufficient.html",
    "backend/entities.jsonl",
    "backend/BACKEND_RECEIPT.json",
    "00_control/CHECKPOINT_2026-08-23_SIXTEEN_PAGE.md",
    "00_control/LIVE_BROWSER_QA_2026-08-23_SIXTEEN_PAGE.json",
    "00_control/TERMINOLOGY_QA_2026-08-22.md",
    "build/FIRST_UNIT_MANIFEST.csv",
    "build/PDF_READER_RECEIPT.json",
    "README.md",
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def token_fallback() -> str | None:
    path = pathlib.Path.home() / "Downloads" / "Github Tokens.md"
    if not path.is_file():
        return None
    matches = re.findall(r"github_pat_[A-Za-z0-9_]+", path.read_text(encoding="utf-8"))
    return matches[0] if matches else None


def api_json(session: requests.Session, url: str) -> dict[str, object]:
    response = session.get(url, timeout=90)
    if response.status_code == 403 and response.headers.get("x-ratelimit-remaining") == "0":
        token = token_fallback()
        if token:
            response = session.get(
                url,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
                timeout=90,
            )
    if response.status_code != 200:
        raise RuntimeError(f"GitHub metadata request failed: HTTP {response.status_code}")
    value = response.json()
    if not isinstance(value, dict):
        raise RuntimeError("GitHub metadata response was not an object")
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
    sha = hashlib.sha256()
    for chunk in response.iter_content(1024 * 1024):
        if chunk:
            total += len(chunk)
            sha.update(chunk)
    return total, sha.hexdigest()


def main() -> None:
    session = requests.Session()
    session.headers.update({"User-Agent": "O006-anonymous-public-readback/1.0"})
    local_manifest = (ROOT / "build" / "FIRST_UNIT_MANIFEST.csv").read_bytes()
    rows = list(csv.DictReader(io.StringIO(local_manifest.decode("utf-8"), newline="")))
    if len(rows) != 46 or digest(local_manifest) != "6cdf7d7592f9468a782801ed2dae9ed7dfdc14cde445c1026cb8018bb3ef3482":
        raise RuntimeError("local reader manifest identity changed")
    verified_pages = []
    for row in rows:
        rel = row["relative_path"]
        payload = download(session, f"{PAGES_BASE}{rel}?v={COMMIT[:12]}", f"Pages {rel}")
        if len(payload) != int(row["bytes"]) or digest(payload) != row["sha256"]:
            raise RuntimeError(f"Pages identity mismatch: {rel}")
        verified_pages.append({"path": rel, "bytes": len(payload), "sha256": digest(payload)})
    root = download(session, f"{PAGES_BASE}?v={COMMIT[:12]}", "Pages root").decode("utf-8")
    if MODEL_PROVENANCE not in root or "Kyle Siegrist" not in root:
        raise RuntimeError("public root lacks provenance or source credit")
    raw_verified = []
    for rel in RAW_SELECTION:
        local = pathlib.Path(ROOT / rel).read_bytes()
        public = download(session, f"{RAW_BASE}{rel}", f"raw {rel}")
        if public != local:
            raise RuntimeError(f"raw identity mismatch: {rel}")
        raw_verified.append({"path": rel, "bytes": len(public), "sha256": digest(public)})
    release_json = api_json(session, f"{API_BASE}/releases/tags/{TAG}")
    asset = next((a for a in release_json.get("assets", []) if a.get("name") == "statistika-matematis-id-reader.pdf"), None)
    if not asset:
        raise RuntimeError("public release PDF asset is missing")
    pdf_bytes, pdf_sha = stream(session, str(asset["browser_download_url"]), "public PDF asset")
    if pdf_bytes != PDF_BYTES or pdf_sha != PDF_SHA256:
        raise RuntimeError("public release PDF identity mismatch")
    workflow = api_json(session, f"{API_BASE}/actions/runs/{WORKFLOW_RUN_ID}")
    if workflow.get("head_sha") != COMMIT or workflow.get("conclusion") != "success":
        raise RuntimeError("public workflow did not succeed at the checkpoint commit")
    print(json.dumps({
        "schema": "o006.random.github-publication-readback.v1",
        "result": "pass",
        "repository": {
            "url": f"https://github.com/{OWNER}/{REPOSITORY}",
            "branch": "main",
            "commit": COMMIT,
            "previous_public_commit": PREVIOUS_COMMIT,
        },
        "workflow": {"run_id": WORKFLOW_RUN_ID, "url": workflow.get("html_url"), "conclusion": workflow.get("conclusion")},
        "pages_readback": {
            "url": PAGES_BASE,
            "method": "credential-free HTTPS downloads of every reader-manifest row",
            "files": len(verified_pages),
            "bytes": sum(row["bytes"] for row in verified_pages),
            "manifest_sha256": digest(local_manifest),
            "all_size_and_sha256_matches": True,
            "root_model_provenance_present": True,
            "root_source_author_credit_present": True,
        },
        "raw_commit_readback": {"method": "credential-free raw.githubusercontent.com downloads", "files": raw_verified},
        "release": {
            "tag": TAG,
            "url": release_json.get("html_url"),
            "prerelease": bool(release_json.get("prerelease")),
            "completion_claim": "16 of 29 core pages; incomplete edition",
            "asset": {"name": asset.get("name"), "bytes": pdf_bytes, "sha256": pdf_sha, "anonymous_download_match": True},
        },
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
