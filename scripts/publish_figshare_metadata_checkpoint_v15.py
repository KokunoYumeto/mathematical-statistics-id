#!/usr/bin/env python3
"""Update the existing CC0 Figshare pointer to the O006 checkpoint 15/29.

Figshare exposes no Other/custom/mixed-rights licence for this account. The
script therefore uploads no edition files and never applies CC0 to the linked
mixed-rights release. It updates exactly article 33314784 and creates no item.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


API = "https://api.figshare.com/v2"
ARTICLE_ID = 33314784
PROJECT_ID = 280296
COLLECTION_ID = 8668413
AUTHOR_ID = 21544022
CATEGORY_ID = 26095
TOKEN_PATH = Path.home() / "Documents" / "TOKENS" / "Figshare Token.md"
TITLE = (
    "Statistika Matematis — Edisi Bahasa Indonesia (id-ID): "
    "Checkpoint 15 dari 29 (Tautan Metadata; Belum Lengkap)"
)
ZENODO_VERSION_DOI = "10.5281/zenodo.22062664"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.22059763"
ZENODO_RECORD_URL = "https://zenodo.org/records/22062664"
GITHUB_RELEASE_URL = (
    "https://github.com/KokunoYumeto/mathematical-statistics-id/"
    "releases/tag/v2026.08.22.15"
)
DESCRIPTION = f"""<p><strong>Checkpoint belum lengkap: 15 dari 29 halaman inti.</strong> Ini adalah catatan metadata CC0 dan tautan preservasi untuk edisi Bahasa Indonesia <em>Statistika Matematis</em>; item Figshare ini tidak memuat salinan berkas edisi.</p>
<p>Rilis kanonik tersedia terbuka pada Zenodo: <a href="{ZENODO_RECORD_URL}">{ZENODO_VERSION_DOI}</a>. Gunakan DOI konsep <a href="https://doi.org/{ZENODO_CONCEPT_DOI}">{ZENODO_CONCEPT_DOI}</a> untuk mengikuti versi-versi selanjutnya. Versi tertaut memuat tujuh berkas / 79.416.980 byte; berkas pertama adalah pembaca PDF 182 halaman A4. Seluruh berkas telah dibaca balik secara anonim dan dicocokkan terhadap SHA-256 lokal. Provenans terjemahan: OpenAI Codex gpt-5.6-sol, Ultra; seluruh kredit sumber, penulis, dan kontributor manusia tetap dipertahankan.</p>
<p>Figshare tidak menyediakan satu label lisensi yang dapat mewakili model hak campuran checkpoint ini secara tepat. Karena itu, CC0 pada item Figshare ini berlaku <strong>hanya untuk metadata dan tautan ini</strong>, bukan untuk berkas yang ditautkan. Hak komponen dan atribusi lengkap berada di manifest rilis Zenodo; laman Random menyatakan CC BY 2.0 sementara halaman Credits menautkan CC BY 1.0, MathJax tetap Apache 2.0, dan aset tertentu tetap CC0.</p>
<p>Repositori, pembaca web, dan PDF prerelease GitHub juga tersedia pada <a href="{GITHUB_RELEASE_URL}">rilis checkpoint 15/29</a>. Zenodo dan GitHub adalah jalur publik yang saling melengkapi; item ini hanya katalog metadata.</p>"""
REFERENCES = [
    f"https://doi.org/{ZENODO_VERSION_DOI}",
    f"https://doi.org/{ZENODO_CONCEPT_DOI}",
    GITHUB_RELEASE_URL,
    "https://www.randomservices.org/random/",
]
TAGS = [
    "Indonesian mathematics",
    "mathematical statistics",
    "Bayesian estimation",
    "open educational resources",
    "translation",
    "partial checkpoint",
    "Zenodo preservation",
]


def controlled_description(value: str) -> bool:
    return (
        ZENODO_VERSION_DOI in value
        and ZENODO_CONCEPT_DOI in value
        and "hanya untuk metadata dan tautan ini" in value
        and GITHUB_RELEASE_URL in value
    )


def token() -> str:
    value = TOKEN_PATH.read_text(encoding="utf-8").strip()
    if len(value) < 40 or any(character.isspace() for character in value):
        raise RuntimeError("Figshare credential file does not contain one plausible token")
    return value


def request(
    method: str,
    endpoint: str,
    *,
    payload: Any | None = None,
    credential: str | None = None,
    expected: tuple[int, ...] = (200,),
) -> Any:
    argv = [
        "curl.exe",
        "--silent",
        "--show-error",
        "--location",
        "--request",
        method,
        "--header",
        "Accept: application/json",
    ]
    if payload is not None:
        argv.extend(
            [
                "--header",
                "Content-Type: application/json",
                "--data-binary",
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            ]
        )
    config = None
    if credential is not None:
        if not re.fullmatch(r"[A-Za-z0-9._~-]{40,}", credential):
            raise RuntimeError("Figshare token contains unexpected characters")
        argv.extend(["--config", "-"])
        config = f'header = "Authorization: token {credential}"\n'.encode("ascii")
    sentinel = b"\n__O006_FIGSHARE_STATUS__:"
    argv.extend(["--write-out", sentinel.decode("ascii") + "%{http_code}", API + endpoint])
    completed = subprocess.run(
        argv,
        input=config,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
        check=False,
    )
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"curl failed for Figshare {method} {endpoint}: {detail}")
    if sentinel not in completed.stdout:
        raise RuntimeError(f"Figshare {method} {endpoint} response lacks status sentinel")
    raw, status_raw = completed.stdout.rsplit(sentinel, 1)
    status = int(status_raw.decode("ascii"))
    if status not in expected:
        detail = raw.decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"Figshare {method} {endpoint} returned HTTP {status}: {detail}")
    return json.loads(raw.decode("utf-8")) if raw else None


def validate_license_inventory(credential: str) -> dict[str, object]:
    public = request("GET", "/licenses")
    account = request("GET", "/account/licenses", credential=credential)
    public_names = [str(row.get("name")) for row in public]
    account_names = [str(row.get("name")) for row in account]
    if public_names != account_names or len(account_names) != 7:
        raise RuntimeError("Figshare public/account license inventories changed unexpectedly")
    if any(name.casefold() in {"other", "custom", "mixed rights"} for name in account_names):
        raise RuntimeError("an exact custom license now exists; use a file-bearing review route")
    cc0 = [row for row in account if row.get("name") == "CC0"]
    if len(cc0) != 1 or int(cc0[0]["value"]) != 2:
        raise RuntimeError("Figshare CC0 identity changed")
    return {"count": len(account_names), "names": account_names, "exact_mixed_rights": False}


def public_inventory() -> dict[str, object]:
    article = request("GET", f"/articles/{ARTICLE_ID}")
    project_articles = request("GET", f"/projects/{PROJECT_ID}/articles?page_size=100")
    collection = request("GET", f"/collections/{COLLECTION_ID}")
    collection_articles = request("GET", f"/collections/{COLLECTION_ID}/articles?page_size=100")
    if article.get("title") != TITLE or not controlled_description(article.get("description", "")):
        raise RuntimeError("public Figshare article is not the controlled checkpoint-15 pointer")
    if article.get("defined_type_name") != "online resource":
        raise RuntimeError("Figshare pointer type changed")
    if article.get("license", {}).get("name") != "CC0" or article.get("files"):
        raise RuntimeError("Figshare pointer is no longer a zero-file CC0 metadata item")
    if not set(REFERENCES).issubset(set(article.get("references", []))):
        raise RuntimeError("Figshare pointer lost a required reference")
    project_ids = {int(row["id"]) for row in project_articles}
    collection_ids = {int(row["id"]) for row in collection_articles}
    if ARTICLE_ID not in project_ids:
        raise RuntimeError("Figshare project lost the O006 pointer")
    return {
        "result": "published-metadata-pointer-and-publicly-verified",
        "article": {
            "id": ARTICLE_ID,
            "doi": article.get("doi"),
            "url": article.get("url_public_html"),
            "version": article.get("version"),
            "title": article.get("title"),
            "license": article.get("license", {}).get("name"),
            "file_count": 0,
        },
        "project": {"id": PROJECT_ID, "contains_article": True},
        "collection": {
            "id": COLLECTION_ID,
            "doi": collection.get("doi"),
            "version": collection.get("version"),
            "contains_article": ARTICLE_ID in collection_ids,
            "disposition": (
                "The current collection is reader-PDF-bearing and excludes link-only catalog "
                "records; do not re-add this pointer until an honestly licensed file-bearing "
                "Figshare version exists."
            ),
        },
        "linked_release": {
            "zenodo_version_doi": ZENODO_VERSION_DOI,
            "zenodo_concept_doi": ZENODO_CONCEPT_DOI,
            "scope": "15 of 29 core pages; incomplete edition",
            "public_file_count": 7,
            "public_total_bytes": 79_416_980,
            "reader_pdf_pages": 182,
        },
        "rights_boundary": (
            "CC0 applies only to the Figshare metadata/link item. No edition bytes were copied "
            "because Figshare exposes no exact mixed-rights license for this account."
        ),
    }


def private_preflight(credential: str) -> dict[str, object]:
    license_inventory = validate_license_inventory(credential)
    article = request("GET", f"/account/articles/{ARTICLE_ID}", credential=credential)
    if int(article.get("id")) != ARTICLE_ID or article.get("files"):
        raise RuntimeError("unexpected Figshare article identity or file inventory")
    if article.get("license", {}).get("name") != "CC0":
        raise RuntimeError("existing Figshare pointer is not CC0")
    project_articles = request(
        "GET", f"/account/projects/{PROJECT_ID}/articles?page_size=100", credential=credential
    )
    occurrences = sum(int(row["id"]) == ARTICLE_ID for row in project_articles)
    if occurrences != 1:
        raise RuntimeError(f"expected one O006 project item, found {occurrences}")
    return {
        "article_id": ARTICLE_ID,
        "current_title": article.get("title"),
        "current_version": article.get("version"),
        "file_count": len(article.get("files", [])),
        "license_inventory": license_inventory,
        "project_occurrences": occurrences,
    }


def publish() -> dict[str, object]:
    credential = token()
    preflight = private_preflight(credential)
    try:
        current_public = request("GET", f"/articles/{ARTICLE_ID}")
        already_current = (
            current_public.get("title") == TITLE
            and controlled_description(current_public.get("description", ""))
            and not current_public.get("files")
        )
    except Exception:
        already_current = False
    if not already_current:
        payload = {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": TAGS,
            "references": REFERENCES,
            "categories": [CATEGORY_ID],
            "authors": [{"id": AUTHOR_ID}],
            "defined_type": "online resource",
            "license": 2,
        }
        request(
            "PUT",
            f"/account/articles/{ARTICLE_ID}",
            payload=payload,
            credential=credential,
            expected=(200, 205),
        )
        request(
            "POST",
            f"/account/articles/{ARTICLE_ID}/publish",
            credential=credential,
            expected=(201,),
        )
    last_error: Exception | None = None
    for _ in range(15):
        try:
            result = public_inventory()
            result["authenticated_preflight"] = preflight
            return result
        except Exception as error:
            last_error = error
            time.sleep(2)
    raise RuntimeError(f"Figshare public readback did not converge: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight", action="store_true")
    group.add_argument("--publish", action="store_true")
    group.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only:
        result = public_inventory()
    elif args.preflight:
        result = private_preflight(token())
        result["mode"] = "preflight"
    else:
        result = publish()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
