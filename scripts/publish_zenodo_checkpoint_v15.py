#!/usr/bin/env python3
"""Advance the existing O006 Zenodo concept to the verified 15/29 checkpoint."""

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
CURRENT_RECORD_ID = "22061677"
CONCEPT_RECORD_ID = "22059763"
VERSION = "2026.08.22.15"
RELEASE_DIR = ROOT / "release" / "zenodo" / VERSION
FILES = (
    "00_statistika-matematis-id-reader-2026.08.22.15.pdf",
    "10_mathematical-statistics-id-2026.08.22.15-reader-html.zip",
    "20_mathematical-statistics-id-2026.08.22.15-source-provenance.zip",
    "30_mathematical-statistics-id-2026.08.22.15-modular-backend.zip",
    "40_LICENSE.md",
    "50_mathematical-statistics-id-2026.08.22.15-release-manifest.json",
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
    rows: list[dict[str, object]] = []
    for name in FILES:
        path = RELEASE_DIR / name
        if not path.is_file():
            raise RuntimeError(f"missing release file: {path}")
        rows.append(
            {
                "name": name,
                "bytes": path.stat().st_size,
                "md5": md5_file(path),
                "sha256": sha256_file(path),
            }
        )
    if sum(int(row["bytes"]) for row in rows) > 500_000_000:
        raise RuntimeError("release payload exceeds 500,000,000 bytes")
    return rows


def read_token() -> str:
    raw = TOKEN_FILE.read_text(encoding="utf-8").strip()
    candidates = re.findall(r"[A-Za-z0-9._~-]{40,}", raw)
    if not candidates:
        raise RuntimeError("Zenodo credential file contains no token-like value")
    return max(candidates, key=len)


def check(response: requests.Response, expected: tuple[int, ...], action: str) -> requests.Response:
    if response.status_code not in expected:
        detail = response.text[:1000].replace(read_token(), "[REDACTED]")
        raise RuntimeError(f"{action} failed with HTTP {response.status_code}: {detail}")
    return response


def deposition_rows(value: object) -> list[dict[str, object]]:
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        hits = value.get("hits")
        if isinstance(hits, dict) and isinstance(hits.get("hits"), list):
            return [row for row in hits["hits"] if isinstance(row, dict)]
    raise RuntimeError("unexpected deposition-search response")


def concept_id(row: dict[str, object]) -> str:
    direct = row.get("conceptrecid")
    if direct is not None:
        return str(direct)
    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        relation = metadata.get("relations")
        if isinstance(relation, dict):
            version = relation.get("version")
            if isinstance(version, list) and version:
                parent = version[0].get("parent") if isinstance(version[0], dict) else None
                if isinstance(parent, dict) and parent.get("pid_value") is not None:
                    return str(parent["pid_value"])
    return ""


def search_lineage(session: requests.Session) -> list[dict[str, object]]:
    response = check(
        session.get(
            DEPOSITIONS,
            params={"q": f"conceptrecid:{CONCEPT_RECORD_ID}", "all_versions": "true", "size": 100},
            timeout=60,
        ),
        (200,),
        "search Zenodo lineage",
    )
    rows = deposition_rows(response.json())
    return [row for row in rows if concept_id(row) == CONCEPT_RECORD_ID]


def published_target(rows: list[dict[str, object]]) -> dict[str, object] | None:
    matches = [
        row
        for row in rows
        if bool(row.get("submitted"))
        and isinstance(row.get("metadata"), dict)
        and row["metadata"].get("version") == VERSION
    ]
    if len(matches) > 1:
        raise RuntimeError(f"multiple submitted Zenodo records for version {VERSION}")
    return matches[0] if matches else None


def metadata() -> dict[str, object]:
    return {
        "title": "Statistika Matematis — Edisi Bahasa Indonesia (id-ID): Checkpoint 15 dari 29 (Belum Lengkap)",
        "upload_type": "publication",
        "publication_type": "book",
        "publication_date": "2026-08-22",
        "description": (
            "Checkpoint edisi independen Bahasa Indonesia (id-ID) dari bab 5–8 karya "
            "Kyle Siegrist, Random: Probability, Mathematical Statistics, and Stochastic "
            "Processes. Versi ini memuat 15 dari 29 halaman sumber inti secara berurutan, "
            "sampai random/point/Unbiased.html; korpus belum lengkap dan tidak diklaim sebagai "
            "satu-satunya tulang punggung naratif C140. Berkas pertama adalah pembaca PDF "
            "langsung 182 halaman A4. Pembaca HTML luring, sumber terjemahan yang dapat "
            "disunting, backend modular netral-lokal, manifes, provenance ringkas, lisensi, "
            "checksum, dan bukti QA turut disertakan. Provenans terjemahan: "
            "OpenAI Codex gpt-5.6-sol, Ultra; seluruh kredit sumber, penulis, dan "
            "kontributor manusia tetap dipertahankan. Situs asal menyatakan CC BY 2.0, "
            "sedangkan halaman Credits menautkan CC BY 1.0; perbedaan itu dipertahankan. "
            "MathJax tetap Apache 2.0 dan aset tertentu tetap CC0. Edisi ini tidak didukung "
            "maupun disahkan oleh Kyle Siegrist atau Random Services. Repositori, pembaca web, "
            "dan PDF prerelease GitHub tersedia sebagai jalur publik tambahan."
        ),
        "creators": [{"name": "Siegrist, Kyle"}],
        "contributors": [{"name": "TTP", "type": "Other"}],
        "access_right": "open",
        "license": "other-open",
        "keywords": [
            "Bahasa Indonesia",
            "id-ID",
            "mathematical statistics",
            "statistika matematis",
            "Bayesian estimation",
            "maximum likelihood",
            "open textbook",
            "offline HTML",
            "machine-readable curriculum",
            "AI translation",
            "in-progress edition",
        ],
        "language": "ind",
        "version": VERSION,
        "related_identifiers": [
            {
                "identifier": "https://www.randomservices.org/random/",
                "relation": "isDerivedFrom",
                "resource_type": "publication-book",
                "scheme": "url",
            },
            {
                "identifier": "https://github.com/KokunoYumeto/mathematical-statistics-id",
                "relation": "isSupplementedBy",
                "resource_type": "software",
                "scheme": "url",
            },
        ],
    }


def refetch_draft(session: requests.Session, draft_id: str) -> dict[str, object]:
    response = check(session.get(f"{DEPOSITIONS}/{draft_id}", timeout=60), (200,), "fetch draft")
    value = response.json()
    if not isinstance(value, dict):
        raise RuntimeError("unexpected Zenodo draft response")
    return value


def ensure_draft(session: requests.Session) -> tuple[dict[str, object], bool]:
    rows = search_lineage(session)
    drafts = [row for row in rows if not bool(row.get("submitted"))]
    if len(drafts) > 1:
        raise RuntimeError(f"multiple unpublished drafts in concept lineage: {len(drafts)}")
    if drafts:
        draft = refetch_draft(session, str(drafts[0]["id"]))
        return draft, True
    current = check(
        session.get(f"{DEPOSITIONS}/{CURRENT_RECORD_ID}", timeout=60),
        (200,),
        "fetch current record",
    ).json()
    if not current.get("submitted") or str(current.get("record_id")) != CURRENT_RECORD_ID:
        raise RuntimeError("current Zenodo record is not the expected submitted v14")
    response = check(
        session.post(f"{DEPOSITIONS}/{CURRENT_RECORD_ID}/actions/newversion", json={}, timeout=120),
        (201,),
        "create Zenodo new-version draft",
    )
    value = response.json()
    latest = value.get("links", {}).get("latest_draft") if isinstance(value, dict) else None
    if not latest:
        raise RuntimeError("new-version response omitted latest_draft")
    draft_response = check(session.get(str(latest), timeout=60), (200,), "fetch new-version draft")
    draft = draft_response.json()
    return draft, False


def clear_and_upload(
    session: requests.Session, draft: dict[str, object], inventory: list[dict[str, object]]
) -> dict[str, object]:
    draft_id = str(draft["id"])
    if bool(draft.get("submitted")) or concept_id(draft) != CONCEPT_RECORD_ID:
        raise RuntimeError("refusing to mutate an unexpected or submitted draft")
    expected_by_name = {str(row["name"]): row for row in inventory}

    def exact_files(value: dict[str, object]) -> bool:
        current = {str(row.get("filename")): row for row in value.get("files") or []}
        if set(current) != set(FILES):
            return False
        for name, wanted in expected_by_name.items():
            row = current[name]
            checksum = str(row.get("checksum", ""))
            if checksum.startswith("md5:"):
                checksum = checksum[4:]
            if int(row.get("filesize", -1)) != int(wanted["bytes"]) or checksum != wanted["md5"]:
                return False
        return True

    if not exact_files(draft):
        for row in list(draft.get("files") or []):
            file_id = row.get("id")
            if file_id is None:
                raise RuntimeError("draft file has no id")
            check(
                session.delete(f"{DEPOSITIONS}/{draft_id}/files/{file_id}", timeout=120),
                (204,),
                f"delete inherited draft file {row.get('filename')}",
            )
        draft = refetch_draft(session, draft_id)
        bucket = str(draft.get("links", {}).get("bucket", "")).rstrip("/")
        if not bucket:
            raise RuntimeError("draft has no upload bucket")
        for row in inventory:
            name = str(row["name"])
            with (RELEASE_DIR / name).open("rb") as stream:
                check(
                    session.put(f"{bucket}/{quote(name)}", data=stream, timeout=900),
                    (200, 201),
                    f"upload {name}",
                )
        draft = refetch_draft(session, draft_id)
        if not exact_files(draft):
            raise RuntimeError("uploaded Zenodo draft files do not match local MD5/size inventory")
    by_name = {str(row.get("filename")): row for row in draft.get("files") or []}
    if set(by_name) != set(FILES):
        raise RuntimeError(f"draft file inventory mismatch: {sorted(by_name)}")
    order = [{"id": by_name[name]["id"]} for name in FILES]
    order_response = session.put(f"{DEPOSITIONS}/{draft_id}/files", json=order, timeout=120)
    if order_response.status_code not in (200, 405):
        check(order_response, (200,), "sort Zenodo draft files")
    draft = refetch_draft(session, draft_id)
    actual_names = [str(row.get("filename")) for row in draft.get("files") or []]
    if (
        not actual_names
        or set(actual_names) != set(FILES)
        or sorted(actual_names, key=str.casefold)[0] != FILES[0]
    ):
        raise RuntimeError(f"Zenodo draft is not reader-first or complete: {actual_names}")
    for row in draft.get("files") or []:
        expected = expected_by_name[str(row["filename"])]
        if int(row.get("filesize", -1)) != int(expected["bytes"]):
            raise RuntimeError(f"draft file size mismatch: {row['filename']}")
    return draft


def anonymous_readback(record_id: str, inventory: list[dict[str, object]]) -> dict[str, object]:
    session = requests.Session()
    session.headers.update({"User-Agent": "O006-anonymous-readback/1.0"})
    record = check(session.get(f"{API}/records/{record_id}", timeout=90), (200,), "read public record").json()
    files = record.get("files") or []
    actual_names = [str(row.get("key")) for row in files]
    if (
        not actual_names
        or set(actual_names) != set(FILES)
        or sorted(actual_names, key=str.casefold)[0] != FILES[0]
    ):
        raise RuntimeError(f"public files are not reader-first or complete: {actual_names}")
    expected = {str(row["name"]): row for row in inventory}
    verified: list[dict[str, object]] = []
    for row in files:
        name = str(row["key"])
        digest = hashlib.sha256()
        total = 0
        file_url = row.get("links", {}).get("content") or row.get("links", {}).get("self")
        if not file_url:
            raise RuntimeError(f"public file has no content link: {name}")
        response = check(
            session.get(str(file_url), stream=True, timeout=900),
            (200,),
            f"download public file {name}",
        )
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                digest.update(chunk)
                total += len(chunk)
        wanted = expected[name]
        if total != wanted["bytes"] or digest.hexdigest() != wanted["sha256"]:
            raise RuntimeError(f"public file mismatch: {name}")
        verified.append({"name": name, "bytes": total, "sha256": digest.hexdigest()})
    versions_response = check(
        session.get(
            f"{API}/records",
            params={"q": f"conceptrecid:{CONCEPT_RECORD_ID}", "allversions": "true", "size": 10},
            timeout=90,
        ),
        (200,),
        "read public version lineage",
    ).json()
    hits = versions_response.get("hits", {}).get("hits", [])
    if len(hits) != 3:
        raise RuntimeError(f"expected three public versions, found {len(hits)}")
    return {
        "record_id": str(record.get("id")),
        "doi": str(record.get("doi")),
        "conceptdoi": str(record.get("conceptdoi")),
        "title": str(record.get("metadata", {}).get("title")),
        "version": str(record.get("metadata", {}).get("version")),
        "files": verified,
        "public_versions": len(hits),
    }


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
    session.headers.update(
        {"Authorization": f"Bearer {token}", "User-Agent": "O006-Zenodo-release/1.0"}
    )
    lineage = search_lineage(session)
    target = published_target(lineage)
    summary: dict[str, object] = {
        "concept_record_id": CONCEPT_RECORD_ID,
        "existing_depositions": len(lineage),
        "existing_drafts": sum(not bool(row.get("submitted")) for row in lineage),
        "local_files": len(inventory),
        "local_bytes": sum(int(row["bytes"]) for row in inventory),
        "mode": (
            "preflight"
            if args.preflight
            else "verify-published"
            if args.verify_published
            else "publish"
        ),
    }
    if args.preflight:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return
    if args.verify_published:
        if target is None:
            raise RuntimeError(f"no submitted Zenodo record for version {VERSION}")
        public = anonymous_readback(str(target.get("record_id") or target.get("id")), inventory)
        final_lineage = search_lineage(session)
        if sum(bool(row.get("submitted")) for row in final_lineage) != 3 or any(
            not bool(row.get("submitted")) for row in final_lineage
        ):
            raise RuntimeError(
                "authenticated Zenodo lineage is not three submitted versions and zero drafts"
            )
        summary.update(
            {
                "final_depositions": len(final_lineage),
                "public": public,
                "submitted_versions": 3,
                "unsubmitted_drafts": 0,
            }
        )
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return
    if target is not None:
        public = anonymous_readback(str(target.get("record_id") or target.get("id")), inventory)
        final_lineage = search_lineage(session)
        if sum(bool(row.get("submitted")) for row in final_lineage) != 3 or any(
            not bool(row.get("submitted")) for row in final_lineage
        ):
            raise RuntimeError(
                "authenticated Zenodo lineage is not three submitted versions and zero drafts"
            )
        summary.update(
            {
                "already_published": True,
                "final_depositions": len(final_lineage),
                "public": public,
                "submitted_versions": 3,
                "unsubmitted_drafts": 0,
            }
        )
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return
    draft, reused = ensure_draft(session)
    draft_id = str(draft["id"])
    draft = clear_and_upload(session, draft, inventory)
    check(
        session.put(f"{DEPOSITIONS}/{draft_id}", json={"metadata": metadata()}, timeout=120),
        (200,),
        "update Zenodo metadata",
    )
    draft = refetch_draft(session, draft_id)
    if draft.get("metadata", {}).get("version") != VERSION:
        raise RuntimeError("draft metadata version mismatch")
    try:
        published_response = session.post(
            f"{DEPOSITIONS}/{draft_id}/actions/publish", json={}, timeout=180
        )
        check(published_response, (202,), "publish Zenodo version")
        published = published_response.json()
    except requests.Timeout:
        time.sleep(5)
        published = refetch_draft(session, draft_id)
        if not bool(published.get("submitted")):
            raise RuntimeError("Zenodo publish timed out and draft remains unpublished")
    record_id = str(published.get("record_id") or published.get("id"))
    public = anonymous_readback(record_id, inventory)
    final_lineage = search_lineage(session)
    if sum(bool(row.get("submitted")) for row in final_lineage) != 3 or any(
        not bool(row.get("submitted")) for row in final_lineage
    ):
        raise RuntimeError("authenticated Zenodo lineage is not three submitted versions and zero drafts")
    summary.update(
        {
            "draft_id": draft_id,
            "draft_reused": reused,
            "final_depositions": len(final_lineage),
            "public": public,
            "submitted_versions": 3,
            "unsubmitted_drafts": 0,
        }
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
