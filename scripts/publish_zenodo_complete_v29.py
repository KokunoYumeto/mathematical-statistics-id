#!/usr/bin/env python3
"""Publish and anonymously verify the complete 29/29 edition in its Zenodo lineage.

`--tooling-self-check` and `--local-preflight` are credential-free and perform
no network access.  `--verify-published` is fully anonymous.  Only `--publish`
reads the Zenodo credential and mutates the existing concept lineage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote

import requests


ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = Path.home() / "Documents" / "Obsidian notes" / "New zenodo token.md"
API = "https://zenodo.org/api"
DEPOSITIONS = f"{API}/deposit/depositions"
CURRENT_RECORD_ID = "22071140"
CONCEPT_RECORD_ID = "22059763"
CONCEPT_DOI = "10.5281/zenodo.22059763"
VERSION = "2026.08.24.29"
RELEASE_DIR = ROOT / "release" / "zenodo" / VERSION
MANIFEST_NAME = f"50_mathematical-statistics-id-{VERSION}-release-manifest.json"
FILES = (
    f"00_statistika-matematis-id-reader-{VERSION}.pdf",
    f"10_mathematical-statistics-id-{VERSION}-reader-html.zip",
    f"20_mathematical-statistics-id-{VERSION}-source-provenance.zip",
    f"30_mathematical-statistics-id-{VERSION}-modular-backend.zip",
    "40_LICENSE.md",
    MANIFEST_NAME,
    "SHA256SUMS.txt",
)
PAYLOAD_CAP = 500_000_000
MODEL_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"


class FileLinkParser(HTMLParser):
    """Collect visible anchor targets without being confused by embedded JSON."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "a":
            return
        values = dict(attrs)
        href = values.get("href")
        if href:
            self.hrefs.append(unquote(href))


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


def release_manifest() -> dict[str, object]:
    path = RELEASE_DIR / MANIFEST_NAME
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("release manifest root is not an object")
    checkpoint = value.get("checkpoint")
    zenodo = value.get("zenodo")
    if value.get("version") != VERSION or not isinstance(checkpoint, dict) or not isinstance(zenodo, dict):
        raise RuntimeError("release manifest version/scope is incomplete")
    if checkpoint.get("complete") is not True or checkpoint.get("translated_pages") != 29 or checkpoint.get("total_pages") != 29:
        raise RuntimeError("release manifest is not complete 29/29")
    if str(zenodo.get("concept_record_id")) != CONCEPT_RECORD_ID or zenodo.get("concept_doi") != CONCEPT_DOI:
        raise RuntimeError("release manifest points to a different Zenodo concept")
    if str(zenodo.get("previous_record_id")) != CURRENT_RECORD_ID:
        raise RuntimeError("release manifest does not continue from the verified v16 record")
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts or not isinstance(artifacts[0], dict):
        raise RuntimeError("release manifest has no reader-first artifact inventory")
    if artifacts[0].get("filename") != FILES[0] or artifacts[0].get("kind") != "reader-first-pdf":
        raise RuntimeError("release manifest is not reader-first")
    return value


def checksum_rows() -> dict[str, str]:
    path = RELEASE_DIR / "SHA256SUMS.txt"
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\]+)", line)
        if not match or match.group(2) in rows:
            raise RuntimeError("SHA256SUMS contains a malformed or duplicate row")
        rows[match.group(2)] = match.group(1)
    expected = set(FILES) - {"SHA256SUMS.txt"}
    if set(rows) != expected:
        raise RuntimeError("SHA256SUMS must cover every release file except itself")
    return rows


def local_inventory() -> tuple[list[dict[str, object]], dict[str, object]]:
    manifest = release_manifest()
    checksums = checksum_rows()
    rows: list[dict[str, object]] = []
    for name in FILES:
        path = RELEASE_DIR / name
        if not path.is_file():
            raise RuntimeError(f"missing release file: {name}")
        row = {
            "name": name,
            "bytes": path.stat().st_size,
            "md5": md5_file(path),
            "sha256": sha256_file(path),
        }
        if name != "SHA256SUMS.txt" and checksums.get(name) != row["sha256"]:
            raise RuntimeError(f"SHA256SUMS mismatch: {name}")
        rows.append(row)
    artifacts = manifest.get("artifacts")
    assert isinstance(artifacts, list)
    artifact_by_name = {
        str(row.get("filename")): row for row in artifacts if isinstance(row, dict)
    }
    expected_artifacts = set(FILES) - {MANIFEST_NAME, "SHA256SUMS.txt"}
    if set(artifact_by_name) != expected_artifacts:
        raise RuntimeError("release manifest artifact names do not match the payload")
    inventory_by_name = {str(row["name"]): row for row in rows}
    for name, artifact_row in artifact_by_name.items():
        local = inventory_by_name[name]
        if artifact_row.get("bytes") != local["bytes"] or artifact_row.get("sha256") != local["sha256"]:
            raise RuntimeError(f"release manifest artifact identity mismatch: {name}")
    total = sum(int(row["bytes"]) for row in rows)
    if total >= PAYLOAD_CAP:
        raise RuntimeError(f"Zenodo payload must be below {PAYLOAD_CAP:,} bytes; found {total:,}")
    return rows, manifest


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


def authenticated_lineage(session: requests.Session) -> list[dict[str, object]]:
    response: requests.Response | None = None
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


def submitted_target(rows: list[dict[str, object]]) -> dict[str, object] | None:
    matches = [
        row for row in rows
        if bool(row.get("submitted"))
        and isinstance(row.get("metadata"), dict)
        and row["metadata"].get("version") == VERSION
    ]
    if len(matches) > 1:
        raise RuntimeError("multiple submitted Zenodo records exist for this version")
    return matches[0] if matches else None


def publication_metadata(manifest: dict[str, object]) -> dict[str, object]:
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, list) and isinstance(artifacts[0], dict)
    physical_pages = int(artifacts[0]["physical_pages"])
    return {
        "title": "Statistika Matematis — Edisi Bahasa Indonesia (id-ID): Edisi Lengkap Bab 5–8",
        "upload_type": "publication",
        "publication_type": "book",
        "publication_date": "2026-08-24",
        "description": (
            "Edisi independen Bahasa Indonesia (id-ID) yang lengkap untuk 29 dari 29 halaman inti "
            "bab 5–8 karya Kyle Siegrist, Random: Probability, Mathematical Statistics, and "
            f"Stochastic Processes. Berkas pertama adalah pembaca PDF langsung {physical_pages} halaman A4. "
            "Pembaca HTML luring, sumber terjemahan yang dapat disunting, backend modular netral-lokal, "
            "manifes, bukti QA, lisensi, dan checksum turut disertakan. Edisi lengkap Random ini tetap "
            "merupakan karya mandiri dan bukan satu-satunya tulang punggung naratif kursus C140 yang "
            "dikonfigurasi secara terpisah. Provenans terjemahan: OpenAI Codex gpt-5.6-sol, Ultra; seluruh "
            "kredit sumber, penulis, dan kontributor manusia dipertahankan. Situs asal menyatakan CC BY "
            "2.0, sedangkan halaman Credits menautkan CC BY 1.0; perbedaan itu dipertahankan. MathJax "
            "tetap Apache 2.0 dan aset tertentu tetap CC0. Edisi ini tidak didukung maupun disahkan oleh "
            "Kyle Siegrist atau Random Services. Repositori, pembaca web, dan rilis GitHub menyediakan "
            "jalur publik tambahan."
        ),
        "creators": [{"name": "Siegrist, Kyle"}],
        "access_right": "open",
        "license": "other-open",
        "keywords": [
            "Bahasa Indonesia", "id-ID", "mathematical statistics", "statistika matematis",
            "sampling distributions", "point estimation", "interval estimation", "hypothesis testing",
            "Bayesian estimation", "maximum likelihood", "open textbook", "offline HTML",
            "machine-readable curriculum", "AI translation", "complete edition",
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


def validate_draft_metadata(metadata: object, expected: dict[str, object]) -> None:
    if not isinstance(metadata, dict):
        raise RuntimeError("Zenodo draft metadata is not an object")
    for key in (
        "title",
        "upload_type",
        "publication_type",
        "publication_date",
        "description",
        "access_right",
        "license",
        "language",
        "version",
    ):
        if metadata.get(key) != expected.get(key):
            raise RuntimeError(f"Zenodo draft metadata mismatch: {key}")
    if metadata.get("creators") != expected.get("creators"):
        raise RuntimeError("Zenodo draft creator metadata mismatch")
    if set(metadata.get("keywords") or []) != set(expected.get("keywords") or []):
        raise RuntimeError("Zenodo draft keyword metadata mismatch")
    if metadata.get("related_identifiers") != expected.get("related_identifiers"):
        raise RuntimeError("Zenodo draft related-identifier metadata mismatch")


def refetch(session: requests.Session, deposition_id: str) -> dict[str, object]:
    value = check(
        session.get(f"{DEPOSITIONS}/{deposition_id}", timeout=90),
        (200,),
        "fetch Zenodo deposition",
    ).json()
    if not isinstance(value, dict):
        raise RuntimeError("unexpected Zenodo deposition response")
    return value


def ensure_draft(session: requests.Session, rows: list[dict[str, object]]) -> tuple[dict[str, object], bool]:
    drafts = [row for row in rows if not bool(row.get("submitted"))]
    if len(drafts) > 1:
        raise RuntimeError("multiple unpublished drafts exist in the Zenodo concept")
    if drafts:
        draft = refetch(session, str(drafts[0]["id"]))
        if concept_id(draft) != CONCEPT_RECORD_ID or bool(draft.get("submitted")):
            raise RuntimeError("existing draft is not the expected concept draft")
        draft_metadata = draft.get("metadata")
        draft_version = draft_metadata.get("version") if isinstance(draft_metadata, dict) else None
        if draft_version not in ("2026.08.23.16", VERSION):
            raise RuntimeError(f"existing concept draft belongs to a different version: {draft_version}")
        return draft, True
    submitted_ids = [int(str(row.get("record_id") or row.get("id"))) for row in rows if bool(row.get("submitted"))]
    if not submitted_ids or max(submitted_ids) != int(CURRENT_RECORD_ID):
        raise RuntimeError("verified v16 record is no longer the latest submitted record; refusing a stale new-version fork")
    current = refetch(session, CURRENT_RECORD_ID)
    if not current.get("submitted") or str(current.get("record_id")) != CURRENT_RECORD_ID:
        raise RuntimeError("current Zenodo record is not the expected v16 record")
    response = check(
        session.post(f"{DEPOSITIONS}/{CURRENT_RECORD_ID}/actions/newversion", json={}, timeout=120),
        (201,),
        "create Zenodo new-version draft",
    )
    latest = response.json().get("links", {}).get("latest_draft")
    if not latest:
        raise RuntimeError("Zenodo new-version response omitted latest_draft")
    latest_text = str(latest).rstrip("/")
    match = re.fullmatch(re.escape(DEPOSITIONS) + r"/(\d+)", latest_text)
    if not match:
        raise RuntimeError("Zenodo new-version response returned an unexpected latest_draft URL")
    return refetch(session, match.group(1)), False


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


def upload_exact(session: requests.Session, draft: dict[str, object], inventory: list[dict[str, object]]) -> dict[str, object]:
    draft_id = str(draft["id"])
    if bool(draft.get("submitted")) or concept_id(draft) != CONCEPT_RECORD_ID:
        raise RuntimeError("refusing to mutate an unexpected Zenodo draft")
    if not exact_files(draft, inventory):
        for row in list(draft.get("files") or []):
            check(
                session.delete(f"{DEPOSITIONS}/{draft_id}/files/{row.get('id')}", timeout=120),
                (204,),
                "delete inherited Zenodo draft file",
            )
        draft = refetch(session, draft_id)
        bucket = str(draft.get("links", {}).get("bucket", "")).rstrip("/")
        if not bucket:
            raise RuntimeError("Zenodo draft has no upload bucket")
        for row in inventory:
            name = str(row["name"])
            with (RELEASE_DIR / name).open("rb") as stream:
                check(
                    session.put(f"{bucket}/{quote(name)}", data=stream, timeout=900),
                    (200, 201),
                    f"upload Zenodo file {name}",
                )
        draft = refetch(session, draft_id)
        if not exact_files(draft, inventory):
            raise RuntimeError("uploaded Zenodo draft does not match local inventory")
    # Prefixes make the PDF the first human-visible file even on Zenodo
    # deployments whose API file-array order differs from display order.
    if min(FILES, key=str.casefold) != FILES[0]:
        raise RuntimeError("release filenames do not guarantee reader-first display")
    return draft


def anonymous_public_lineage(session: requests.Session) -> list[dict[str, object]]:
    response = check(
        session.get(
            f"{API}/records",
            params={"q": f"conceptrecid:{CONCEPT_RECORD_ID}", "all_versions": "true", "size": 25},
            timeout=90,
        ),
        (200,),
        "read Zenodo public lineage",
    )
    value = response.json()
    hits = value.get("hits", {}).get("hits", []) if isinstance(value, dict) else []
    if not isinstance(hits, list):
        raise RuntimeError("unexpected public Zenodo lineage response")
    return [row for row in hits if isinstance(row, dict) and concept_id(row) == CONCEPT_RECORD_ID]


def anonymous_find_target(session: requests.Session) -> dict[str, object]:
    rows = anonymous_public_lineage(session)
    matches = [row for row in rows if isinstance(row.get("metadata"), dict) and row["metadata"].get("version") == VERSION]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one public Zenodo record for version {VERSION}, found {len(matches)}")
    return matches[0]


def anonymous_readback(record_id: str, inventory: list[dict[str, object]]) -> dict[str, object]:
    session = requests.Session()
    session.headers.update({"User-Agent": "O006-complete-anonymous-readback/1.0"})
    record = check(session.get(f"{API}/records/{record_id}", timeout=90), (200,), "read public Zenodo record").json()
    if (
        not isinstance(record, dict)
        or concept_id(record) != CONCEPT_RECORD_ID
        or str(record.get("conceptdoi")) != CONCEPT_DOI
    ):
        raise RuntimeError("public Zenodo record is outside the expected concept")
    metadata = record.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("version") != VERSION:
        raise RuntimeError("public Zenodo record version mismatch")
    expected_metadata = publication_metadata(release_manifest())
    for key in ("title", "publication_date", "language", "version"):
        if metadata.get(key) != expected_metadata.get(key):
            raise RuntimeError(f"public Zenodo metadata mismatch: {key}")
    public_license = metadata.get("license")
    if not isinstance(public_license, dict) or public_license.get("id") != expected_metadata.get("license"):
        raise RuntimeError("public Zenodo licence metadata mismatch")
    public_creators = metadata.get("creators")
    if (
        not isinstance(public_creators, list)
        or [row.get("name") for row in public_creators if isinstance(row, dict)]
        != [row.get("name") for row in expected_metadata["creators"] if isinstance(row, dict)]
    ):
        raise RuntimeError("public Zenodo creator metadata mismatch")
    if metadata.get("related_identifiers") != expected_metadata.get("related_identifiers"):
        raise RuntimeError("public Zenodo related-identifier metadata mismatch")
    if set(metadata.get("keywords") or []) != set(expected_metadata.get("keywords") or []):
        raise RuntimeError("public Zenodo keyword metadata mismatch")
    description = str(metadata.get("description") or "")
    for marker in ("29 dari 29", MODEL_PROVENANCE, "CC BY 2.0", "CC BY 1.0"):
        if marker not in description:
            raise RuntimeError(f"public Zenodo description omits required marker: {marker}")
    files = record.get("files") or []
    by_name = {str(row.get("key")): row for row in files if isinstance(row, dict)}
    if set(by_name) != set(FILES) or min(by_name, key=str.casefold) != FILES[0]:
        raise RuntimeError("public Zenodo files are not exact and reader-first by filename")
    expected = {str(row["name"]): row for row in inventory}
    verified: list[dict[str, object]] = []
    for name in FILES:
        row = by_name[name]
        url = row.get("links", {}).get("content") or row.get("links", {}).get("self")
        response = check(session.get(str(url), stream=True, timeout=900), (200,), f"download public Zenodo file {name}")
        digest = hashlib.sha256()
        total = 0
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                total += len(chunk)
                digest.update(chunk)
        if total != expected[name]["bytes"] or digest.hexdigest() != expected[name]["sha256"]:
            raise RuntimeError(f"public Zenodo file mismatch: {name}")
        verified.append({"name": name, "bytes": total, "sha256": digest.hexdigest()})
    html_url = str(record.get("links", {}).get("html") or f"https://zenodo.org/records/{record_id}")
    html = check(session.get(html_url, timeout=90), (200,), "read public Zenodo HTML record").text
    parser = FileLinkParser()
    parser.feed(html)
    displayed = [name for href in parser.hrefs for name in FILES if f"/files/{name}" in href]
    if not displayed or displayed[0] != FILES[0]:
        raise RuntimeError("public Zenodo HTML does not present the PDF first")
    lineage = anonymous_public_lineage(session)
    target_matches = [row for row in lineage if isinstance(row.get("metadata"), dict) and row["metadata"].get("version") == VERSION]
    if len(target_matches) != 1:
        raise RuntimeError("public Zenodo lineage contains a duplicate or missing complete version")
    return {
        "record_id": str(record.get("id")),
        "doi": str(record.get("doi")),
        "conceptdoi": str(record.get("conceptdoi")),
        "url": html_url,
        "title": metadata.get("title"),
        "version": metadata.get("version"),
        "complete_scope": "29 of 29 core pages",
        "reader_first_html_verified": True,
        "files": verified,
        "public_versions": len(lineage),
    }


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


def tooling_self_check() -> dict[str, object]:
    if VERSION != "2026.08.24.29" or len(set(FILES)) != 7 or min(FILES, key=str.casefold) != FILES[0]:
        raise RuntimeError("version or reader-first file constants are invalid")
    if CONCEPT_RECORD_ID == CURRENT_RECORD_ID or not CURRENT_RECORD_ID.isdigit():
        raise RuntimeError("Zenodo concept/current-record constants are invalid")
    return {
        "mode": "tooling-self-check",
        "version": VERSION,
        "concept_record_id": CONCEPT_RECORD_ID,
        "current_record_id": CURRENT_RECORD_ID,
        "reader_first_file": FILES[0],
        "credential_access": False,
        "network_access": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--tooling-self-check", action="store_true")
    mode.add_argument("--local-preflight", action="store_true")
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--verify-published", action="store_true")
    parser.add_argument("--record-id")
    parser.add_argument("--receipt-out", help="optional safe repository-relative sanitized JSON receipt")
    args = parser.parse_args()
    if args.tooling_self_check:
        print(json.dumps(tooling_self_check(), ensure_ascii=False, sort_keys=True))
        return
    inventory, manifest = local_inventory()
    summary: dict[str, object] = {
        "schema": "o006.random.zenodo-complete-publication.v1",
        "version": VERSION,
        "concept_record_id": CONCEPT_RECORD_ID,
        "concept_doi": CONCEPT_DOI,
        "local_files": len(inventory),
        "local_bytes": sum(int(row["bytes"]) for row in inventory),
        "local_inventory": [{key: row[key] for key in ("name", "bytes", "sha256")} for row in inventory],
        "translation_provenance": MODEL_PROVENANCE,
    }
    if args.local_preflight:
        summary.update({"mode": "local-preflight", "network_access": False, "credential_access": False})
        write_receipt(args.receipt_out, summary)
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return
    if args.verify_published:
        anonymous = requests.Session()
        anonymous.headers.update({"User-Agent": "O006-complete-anonymous-readback/1.0"})
        if args.record_id:
            if not args.record_id.isdigit():
                raise RuntimeError("--record-id must be numeric")
            record_id = args.record_id
        else:
            target = anonymous_find_target(anonymous)
            record_id = str(target.get("id"))
        summary.update({"mode": "verify-published", "credential_access": False, "public": anonymous_readback(record_id, inventory)})
        write_receipt(args.receipt_out, summary)
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return

    token = read_token()
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "User-Agent": "O006-Zenodo-complete-release/1.0"})
    rows = authenticated_lineage(session)
    found = submitted_target(rows)
    drafts = [row for row in rows if not bool(row.get("submitted"))]
    if found is not None:
        if drafts:
            raise RuntimeError("complete version is submitted but an unexpected concept draft remains")
        public = anonymous_readback(str(found.get("record_id") or found.get("id")), inventory)
        summary.update({"mode": "already-published", "public": public, "submitted_versions": sum(bool(row.get("submitted")) for row in rows), "unsubmitted_drafts": 0})
        write_receipt(args.receipt_out, summary)
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return
    draft, reused = ensure_draft(session, rows)
    draft_id = str(draft["id"])
    draft = upload_exact(session, draft, inventory)
    expected_metadata = publication_metadata(manifest)
    check(
        session.put(f"{DEPOSITIONS}/{draft_id}", json={"metadata": publication_metadata(manifest)}, timeout=120),
        (200,),
        "update Zenodo metadata",
    )
    draft = refetch(session, draft_id)
    validate_draft_metadata(draft.get("metadata"), expected_metadata)
    if not exact_files(draft, inventory):
        raise RuntimeError("Zenodo draft failed final metadata/file prepublication check")
    response = check(
        session.post(f"{DEPOSITIONS}/{draft_id}/actions/publish", json={}, timeout=180),
        (202,),
        "publish Zenodo version",
    )
    published = response.json()
    record_id = str(published.get("record_id") or published.get("id"))
    public = anonymous_readback(record_id, inventory)
    final_rows = authenticated_lineage(session)
    final_target = submitted_target(final_rows)
    final_drafts = [row for row in final_rows if not bool(row.get("submitted"))]
    if final_target is None or final_drafts:
        raise RuntimeError("authenticated Zenodo lineage failed final submitted/zero-draft check")
    summary.update({
        "mode": "publish",
        "draft_id": draft_id,
        "draft_reused": reused,
        "public": public,
        "submitted_versions": sum(bool(row.get("submitted")) for row in final_rows),
        "unsubmitted_drafts": 0,
    })
    write_receipt(args.receipt_out, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
