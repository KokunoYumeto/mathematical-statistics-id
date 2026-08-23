#!/usr/bin/env python3
"""Publish and anonymously verify the existing O006 Zenodo lineage at 16/29."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = Path.home() / "Documents" / "Obsidian notes" / "New zenodo token.md"
API = "https://zenodo.org/api"
DEPOSITIONS = f"{API}/deposit/depositions"
CURRENT_RECORD_ID = "22062664"
CONCEPT_RECORD_ID = "22059763"
VERSION = "2026.08.23.16"
RELEASE_DIR = ROOT / "release" / "zenodo" / VERSION
FILES = (
    f"00_statistika-matematis-id-reader-{VERSION}.pdf",
    f"10_mathematical-statistics-id-{VERSION}-reader-html.zip",
    f"20_mathematical-statistics-id-{VERSION}-source-provenance.zip",
    f"30_mathematical-statistics-id-{VERSION}-modular-backend.zip",
    "40_LICENSE.md",
    f"50_mathematical-statistics-id-{VERSION}-release-manifest.json",
    "SHA256SUMS.txt",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_inventory() -> list[dict[str, object]]:
    rows = []
    for name in FILES:
        path = RELEASE_DIR / name
        if not path.is_file():
            raise RuntimeError(f"missing release file: {name}")
        rows.append({"name": name, "bytes": path.stat().st_size, "md5": md5_file(path), "sha256": sha256_file(path)})
    if sum(int(row["bytes"]) for row in rows) > 500_000_000:
        raise RuntimeError("Zenodo payload exceeds 500,000,000 bytes")
    return rows


def read_token() -> str:
    raw = TOKEN_FILE.read_text(encoding="utf-8")
    matches = re.findall(r"[A-Za-z0-9._~-]{40,}", raw)
    if not matches:
        raise RuntimeError("Zenodo credential file contains no token-like value")
    return max(matches, key=len)


def check(response: requests.Response, expected: tuple[int, ...], action: str) -> requests.Response:
    if response.status_code not in expected:
        raise RuntimeError(f"{action} failed with HTTP {response.status_code}")
    return response


def concept_id(row: dict[str, object]) -> str:
    direct = row.get("conceptrecid")
    if direct is not None:
        return str(direct)
    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        relation = metadata.get("relations")
        if isinstance(relation, dict):
            versions = relation.get("version")
            if isinstance(versions, list) and versions and isinstance(versions[0], dict):
                parent = versions[0].get("parent")
                if isinstance(parent, dict) and parent.get("pid_value") is not None:
                    return str(parent["pid_value"])
    return ""


def lineage(session: requests.Session) -> list[dict[str, object]]:
    response = None
    for attempt in range(6):
        candidate = session.get(
            DEPOSITIONS,
            params={"q": f"conceptrecid:{CONCEPT_RECORD_ID}", "all_versions": "true", "size": 100},
            timeout=120,
        )
        if candidate.status_code == 200:
            response = candidate
            break
        if candidate.status_code not in (502, 503, 504) or attempt == 5:
            raise RuntimeError(f"search Zenodo lineage failed with HTTP {candidate.status_code}")
        time.sleep(5 * (attempt + 1))
    if response is None:
        raise RuntimeError("search Zenodo lineage did not return a response")
    value = response.json()
    rows = value if isinstance(value, list) else value.get("hits", {}).get("hits", []) if isinstance(value, dict) else []
    if not isinstance(rows, list):
        raise RuntimeError("unexpected Zenodo lineage response")
    return [row for row in rows if isinstance(row, dict) and concept_id(row) == CONCEPT_RECORD_ID]


def target(rows: list[dict[str, object]]) -> dict[str, object] | None:
    matches = [row for row in rows if bool(row.get("submitted")) and isinstance(row.get("metadata"), dict) and row["metadata"].get("version") == VERSION]
    if len(matches) > 1:
        raise RuntimeError("multiple submitted Zenodo records exist for this version")
    return matches[0] if matches else None


def metadata() -> dict[str, object]:
    return {
        "title": "Statistika Matematis — Edisi Bahasa Indonesia (id-ID): Checkpoint 16 dari 29 (Belum Lengkap)",
        "upload_type": "publication",
        "publication_type": "book",
        "publication_date": "2026-08-23",
        "description": (
            "Checkpoint edisi independen Bahasa Indonesia (id-ID) dari bab 5–8 karya Kyle Siegrist, "
            "Random: Probability, Mathematical Statistics, and Stochastic Processes. Versi ini memuat "
            "16 dari 29 halaman sumber inti secara berurutan, sampai random/point/Sufficient.html; "
            "korpus belum lengkap dan bukan satu-satunya tulang punggung naratif C140. Berkas pertama "
            "adalah pembaca PDF langsung 197 halaman A4. Pembaca HTML luring, sumber terjemahan yang "
            "dapat disunting, backend modular netral-lokal, manifes, provenance, lisensi, checksum, dan "
            "bukti QA turut disertakan. Provenans terjemahan: OpenAI Codex gpt-5.6-sol, Ultra; seluruh "
            "kredit sumber, penulis, dan kontributor manusia tetap dipertahankan. Situs asal menyatakan "
            "CC BY 2.0, sedangkan halaman Credits menautkan CC BY 1.0; perbedaan itu dipertahankan. "
            "MathJax tetap Apache 2.0 dan aset tertentu tetap CC0. Edisi ini tidak didukung maupun "
            "disahkan oleh Kyle Siegrist atau Random Services. Repositori, pembaca web, dan PDF "
            "prerelease GitHub tersedia sebagai jalur publik tambahan."
        ),
        "creators": [{"name": "Siegrist, Kyle"}],
        "contributors": [{"name": "TTP", "type": "Other"}],
        "access_right": "open",
        "license": "other-open",
        "keywords": ["Bahasa Indonesia", "id-ID", "mathematical statistics", "statistika matematis", "Bayesian estimation", "maximum likelihood", "open textbook", "offline HTML", "machine-readable curriculum", "AI translation", "in-progress edition"],
        "language": "ind",
        "version": VERSION,
        "related_identifiers": [
            {"identifier": "https://www.randomservices.org/random/", "relation": "isDerivedFrom", "resource_type": "publication-book", "scheme": "url"},
            {"identifier": "https://github.com/KokunoYumeto/mathematical-statistics-id", "relation": "isSupplementedBy", "resource_type": "software", "scheme": "url"},
        ],
    }


def refetch(session: requests.Session, deposition_id: str) -> dict[str, object]:
    value = check(session.get(f"{DEPOSITIONS}/{deposition_id}", timeout=90), (200,), "fetch Zenodo deposition").json()
    if not isinstance(value, dict):
        raise RuntimeError("unexpected Zenodo deposition response")
    return value


def ensure_draft(session: requests.Session) -> tuple[dict[str, object], bool]:
    rows = lineage(session)
    drafts = [row for row in rows if not bool(row.get("submitted"))]
    if len(drafts) > 1:
        raise RuntimeError("multiple unpublished drafts exist in the Zenodo concept")
    if drafts:
        return refetch(session, str(drafts[0]["id"])), True
    current = refetch(session, CURRENT_RECORD_ID)
    if not current.get("submitted") or str(current.get("record_id")) != CURRENT_RECORD_ID:
        raise RuntimeError("current Zenodo record is not the expected v15 record")
    response = check(session.post(f"{DEPOSITIONS}/{CURRENT_RECORD_ID}/actions/newversion", json={}, timeout=120), (201,), "create Zenodo new-version draft")
    latest = response.json().get("links", {}).get("latest_draft")
    if not latest:
        raise RuntimeError("Zenodo new-version response omitted latest_draft")
    return refetch(session, str(latest)), False


def exact_files(draft: dict[str, object], inventory: list[dict[str, object]]) -> bool:
    expected = {str(row["name"]): row for row in inventory}
    current = {str(row.get("filename")): row for row in draft.get("files") or []}
    if set(current) != set(FILES):
        return False
    for name, wanted in expected.items():
        checksum = str(current[name].get("checksum", ""))
        if checksum.startswith("md5:"):
            checksum = checksum[4:]
        if int(current[name].get("filesize", -1)) != int(wanted["bytes"]) or checksum != wanted["md5"]:
            return False
    return True


def upload(session: requests.Session, draft: dict[str, object], inventory: list[dict[str, object]]) -> dict[str, object]:
    draft_id = str(draft["id"])
    if bool(draft.get("submitted")) or concept_id(draft) != CONCEPT_RECORD_ID:
        raise RuntimeError("refusing to mutate an unexpected Zenodo draft")
    if not exact_files(draft, inventory):
        for row in list(draft.get("files") or []):
            check(session.delete(f"{DEPOSITIONS}/{draft_id}/files/{row.get('id')}", timeout=120), (204,), "delete inherited Zenodo draft file")
        draft = refetch(session, draft_id)
        bucket = str(draft.get("links", {}).get("bucket", "")).rstrip("/")
        if not bucket:
            raise RuntimeError("Zenodo draft has no upload bucket")
        for row in inventory:
            name = str(row["name"])
            with (RELEASE_DIR / name).open("rb") as stream:
                check(session.put(f"{bucket}/{quote(name)}", data=stream, timeout=900), (200, 201), f"upload Zenodo file {name}")
        draft = refetch(session, draft_id)
        if not exact_files(draft, inventory):
            raise RuntimeError("uploaded Zenodo draft does not match local inventory")
    by_name = {str(row.get("filename")): row for row in draft.get("files") or []}
    order = [{"id": by_name[name]["id"]} for name in FILES]
    ordered = session.put(f"{DEPOSITIONS}/{draft_id}/files", json=order, timeout=120)
    if ordered.status_code not in (200, 405):
        check(ordered, (200,), "sort Zenodo draft files")
    draft = refetch(session, draft_id)
    actual = [str(row.get("filename")) for row in draft.get("files") or []]
    if not actual or set(actual) != set(FILES) or sorted(actual, key=str.casefold)[0] != FILES[0]:
        raise RuntimeError("Zenodo draft is not reader-first and complete")
    return draft


def anonymous_readback(record_id: str, inventory: list[dict[str, object]]) -> dict[str, object]:
    session = requests.Session()
    session.headers.update({"User-Agent": "O006-anonymous-readback/1.0"})
    record = check(session.get(f"{API}/records/{record_id}", timeout=90), (200,), "read public Zenodo record").json()
    files = record.get("files") or []
    names = [str(row.get("key")) for row in files]
    if set(names) != set(FILES) or sorted(names, key=str.casefold)[0] != FILES[0]:
        raise RuntimeError("public Zenodo files are not exact and reader-first")
    expected = {str(row["name"]): row for row in inventory}
    verified = []
    for row in files:
        name = str(row["key"])
        url = row.get("links", {}).get("content") or row.get("links", {}).get("self")
        response = check(session.get(str(url), stream=True, timeout=900), (200,), f"download public Zenodo file {name}")
        sha = hashlib.sha256()
        total = 0
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                total += len(chunk)
                sha.update(chunk)
        if total != expected[name]["bytes"] or sha.hexdigest() != expected[name]["sha256"]:
            raise RuntimeError(f"public Zenodo file mismatch: {name}")
        verified.append({"name": name, "bytes": total, "sha256": sha.hexdigest()})
    versions = check(session.get(f"{API}/records", params={"q": f"conceptrecid:{CONCEPT_RECORD_ID}", "allversions": "true", "size": 100}, timeout=90), (200,), "read Zenodo public lineage").json()
    hits = versions.get("hits", {}).get("hits", [])
    submitted = [row for row in hits if isinstance(row, dict) and row.get("submitted")]
    if len(submitted) != 4 or any(isinstance(row, dict) and not row.get("submitted") for row in hits):
        raise RuntimeError("Zenodo lineage is not four submitted versions and zero drafts")
    return {"record_id": str(record.get("id")), "doi": str(record.get("doi")), "conceptdoi": str(record.get("conceptdoi")), "title": record.get("metadata", {}).get("title"), "version": record.get("metadata", {}).get("version"), "files": verified, "public_versions": len(submitted)}


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight", action="store_true")
    group.add_argument("--publish", action="store_true")
    group.add_argument("--verify-published", action="store_true")
    args = parser.parse_args()
    inventory = local_inventory()
    token = read_token()
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "User-Agent": "O006-Zenodo-release/1.0"})
    rows = lineage(session)
    found = target(rows)
    summary = {"concept_record_id": CONCEPT_RECORD_ID, "existing_depositions": len(rows), "existing_drafts": sum(not bool(row.get("submitted")) for row in rows), "local_files": len(inventory), "local_bytes": sum(int(row["bytes"]) for row in inventory), "version": VERSION}
    if args.preflight:
        summary["mode"] = "preflight"
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return
    if args.verify_published or found is not None:
        if found is None:
            raise RuntimeError("no submitted Zenodo record exists for this version")
        public = anonymous_readback(str(found.get("record_id") or found.get("id")), inventory)
        summary.update({"mode": "verify-published" if args.verify_published else "already-published", "public": public, "submitted_versions": 4, "unsubmitted_drafts": 0})
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return
    draft, reused = ensure_draft(session)
    draft_id = str(draft["id"])
    draft = upload(session, draft, inventory)
    check(session.put(f"{DEPOSITIONS}/{draft_id}", json={"metadata": metadata()}, timeout=120), (200,), "update Zenodo metadata")
    draft = refetch(session, draft_id)
    if draft.get("metadata", {}).get("version") != VERSION:
        raise RuntimeError("Zenodo draft metadata version mismatch")
    response = session.post(f"{DEPOSITIONS}/{draft_id}/actions/publish", json={}, timeout=180)
    check(response, (202,), "publish Zenodo version")
    published = response.json()
    record_id = str(published.get("record_id") or published.get("id"))
    public = anonymous_readback(record_id, inventory)
    final_rows = lineage(session)
    if sum(bool(row.get("submitted")) for row in final_rows) != 4 or any(not bool(row.get("submitted")) for row in final_rows):
        raise RuntimeError("authenticated Zenodo lineage is not four submitted versions and zero drafts")
    summary.update({"mode": "publish", "draft_id": draft_id, "draft_reused": reused, "public": public, "submitted_versions": 4, "unsubmitted_drafts": 0})
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
