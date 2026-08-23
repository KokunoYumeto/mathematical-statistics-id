#!/usr/bin/env python3
"""Advance the existing zero-file Figshare pointer to the 16/29 checkpoint.

The edition has mixed component rights, while this Figshare account exposes no
exact custom/mixed-rights licence.  This wrapper deliberately updates the
existing article only: it publishes metadata and links, uploads no edition
bytes, and keeps CC0 limited to the metadata/link item.
"""

from __future__ import annotations

import json
import sys

import publish_figshare_metadata_checkpoint_v15 as base


VERSION = "2026.08.23.16"
base.TITLE = (
    "Statistika Matematis — Edisi Bahasa Indonesia (id-ID): "
    "Checkpoint 16 dari 29 (Tautan Metadata; Belum Lengkap)"
)
base.ZENODO_VERSION_DOI = "10.5281/zenodo.22071140"
base.ZENODO_RECORD_URL = "https://zenodo.org/records/22071140"
base.GITHUB_RELEASE_URL = (
    "https://github.com/KokunoYumeto/mathematical-statistics-id/"
    "releases/tag/v2026.08.23.16"
)
base.DESCRIPTION = f"""<p><strong>Checkpoint belum lengkap: 16 dari 29 halaman inti.</strong> Ini adalah catatan metadata CC0 dan tautan preservasi untuk edisi Bahasa Indonesia <em>Statistika Matematis</em>; item Figshare ini tidak memuat salinan berkas edisi.</p>
<p>Rilis kanonik tersedia terbuka pada Zenodo: <a href=\"{base.ZENODO_RECORD_URL}\">{base.ZENODO_VERSION_DOI}</a>. Gunakan DOI konsep <a href=\"https://doi.org/{base.ZENODO_CONCEPT_DOI}\">{base.ZENODO_CONCEPT_DOI}</a> untuk mengikuti versi-versi selanjutnya. Versi tertaut memuat tujuh berkas / 88.066.334 byte; berkas pembaca PDF adalah 197 halaman A4. Seluruh berkas telah dibaca balik secara anonim dan dicocokkan terhadap SHA-256 lokal. Provenans terjemahan: OpenAI Codex gpt-5.6-sol, Ultra; seluruh kredit sumber, penulis, dan kontributor manusia tetap dipertahankan.</p>
<p>Figshare tidak menyediakan satu label lisensi yang dapat mewakili model hak campuran checkpoint ini secara tepat. Karena itu, CC0 pada item Figshare ini berlaku <strong>hanya untuk metadata dan tautan ini</strong>, bukan untuk berkas yang ditautkan. Hak komponen dan atribusi lengkap berada di manifest rilis Zenodo; laman Random menyatakan CC BY 2.0 sementara halaman Credits menautkan CC BY 1.0, MathJax tetap Apache 2.0, dan aset tertentu tetap CC0.</p>
<p>Repositori, pembaca web, dan PDF prerelease GitHub juga tersedia pada <a href=\"{base.GITHUB_RELEASE_URL}\">rilis checkpoint 16/29</a>. Zenodo dan GitHub adalah jalur publik yang saling melengkapi; item ini hanya katalog metadata.</p>"""
base.REFERENCES = [
    f"https://doi.org/{base.ZENODO_VERSION_DOI}",
    f"https://doi.org/{base.ZENODO_CONCEPT_DOI}",
    base.GITHUB_RELEASE_URL,
    "https://www.randomservices.org/random/",
]
base.TAGS = [
    "Indonesian mathematics",
    "mathematical statistics",
    "Bayesian estimation",
    "open educational resources",
    "translation",
    "partial checkpoint",
    "Zenodo preservation",
]


_original_public_inventory = base.public_inventory


def public_inventory() -> dict[str, object]:
    result = _original_public_inventory()
    linked = result.get("linked_release")
    if isinstance(linked, dict):
        linked.update(
            {
                "scope": "16 of 29 core pages; incomplete edition",
                "public_file_count": 7,
                "public_total_bytes": 88_066_334,
                "reader_pdf_pages": 197,
            }
        )
    result["version"] = VERSION
    return result


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"--preflight", "--publish", "--check-only"}:
        raise SystemExit("usage: publish_figshare_metadata_checkpoint_v16.py --preflight|--publish|--check-only")
    mode = sys.argv[1]
    if mode == "--check-only":
        result = public_inventory()
    elif mode == "--preflight":
        result = base.private_preflight(base.token())
        result["mode"] = "preflight"
    else:
        # base.publish() resolves all module globals at call time.  Replace its
        # readback function so the resulting receipt carries the 16/29 facts.
        base.public_inventory = public_inventory
        result = base.publish()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
