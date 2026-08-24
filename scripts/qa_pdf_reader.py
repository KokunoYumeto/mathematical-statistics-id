#!/usr/bin/env python3
"""Automated and recorded visual-surface QA for the consolidated PDF reader."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / "output" / "pdf" / "statistika-matematis-id-reader.pdf"
DEFAULT_IMAGES = ROOT / "tmp" / "pdfs" / "pdf-qa-29"
PDF_RECEIPT = ROOT / "build" / "PDF_READER_RECEIPT.json"
RECEIPT = ROOT / "build" / "PDF_VISUAL_QA_RECEIPT.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def flatten_outline(rows: list[Any]) -> list[Any]:
    result: list[Any] = []
    for row in rows:
        if isinstance(row, list):
            result.extend(flatten_outline(row))
        else:
            result.append(row)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--images", type=Path, default=DEFAULT_IMAGES)
    parser.add_argument("--manual-contact-sheets-reviewed", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    pdf_receipt = json.loads(PDF_RECEIPT.read_text(encoding="utf-8"))
    if pdf_receipt.get("status") != "complete-29-of-29":
        raise RuntimeError("PDF reader receipt is not the complete 29-page-source edition")
    if int(pdf_receipt.get("source_documents", -1)) != 29:
        raise RuntimeError("PDF reader receipt does not bind exactly 29 source documents")
    documents = pdf_receipt.get("documents")
    if not isinstance(documents, list) or len(documents) != 29:
        raise RuntimeError("PDF reader receipt document inventory is incomplete")
    if [int(row.get("ordinal", -1)) for row in documents] != list(range(1, 30)):
        raise RuntimeError("PDF reader receipt document order is not exact ordinals 1-29")
    for row in documents:
        reflow = row.get("terminal_reflow")
        if not isinstance(reflow, dict) or reflow.get("schema") != "o006.random.pdf-terminal-reflow.v2":
            raise RuntimeError(f"renderer reflow evidence missing for ordinal {row.get('ordinal')}")
        if (
            row.get("raw_tex")
            or row.get("page_overflow")
            or int(row.get("incomplete_images", -1)) != 0
            or int(row.get("print_content_width", -1)) not in (695, 696)
            or int(row.get("print_content_scroll_width", -1)) > int(row.get("print_content_width", -2)) + 1
            or int(row.get("maximum_print_overflow_px", -1)) != 0
            or row.get("wide_elements") not in ([], None)
        ):
            raise RuntimeError(f"renderer defect recorded for ordinal {row.get('ordinal')}")
        if reflow.get("terminal_exercise_grid") is True:
            geometry = reflow.get("grid_geometry")
            question_items = int(reflow.get("terminal_question_items", -1))
            answer_items = int(reflow.get("terminal_answer_items", -1))
            alignment = reflow.get("grid_alignment")
            if (
                not isinstance(geometry, dict)
                or geometry.get("evaluated") is not True
                or geometry.get("pass") is not True
                or not 1 <= question_items <= 8
                or not 1 <= answer_items <= 8
                or alignment not in ("paired-items", "parallel-lists")
                or (alignment == "paired-items" and question_items != answer_items)
                or (alignment == "parallel-lists" and question_items == answer_items)
            ):
                raise RuntimeError(f"terminal exercise grid is not geometry-safe for ordinal {row.get('ordinal')}")
        if int(row.get("open_details", -1)) != int(row.get("details", -2)):
            raise RuntimeError(f"not all disclosures were rendered open for ordinal {row.get('ordinal')}")
    expected_pages = int(pdf_receipt.get("physical_pages", -1))
    front_matter_pages = int(pdf_receipt.get("front_matter_pages", -1))
    if front_matter_pages != 5:
        raise RuntimeError(f"expected exactly five front-matter pages, found {front_matter_pages}")
    if any(int(row.get("pdf_pages", -1)) < 1 for row in documents):
        raise RuntimeError("one or more source documents have no positive PDF page range")
    if expected_pages != front_matter_pages + sum(int(row.get("pdf_pages", -1)) for row in documents):
        raise RuntimeError("PDF page total is inconsistent with front matter and document inventory")
    if args.pdf.stat().st_size != int(pdf_receipt.get("bytes", -1)) or sha256(args.pdf) != pdf_receipt.get("sha256"):
        raise RuntimeError("PDF bytes do not match the canonical reader receipt")
    reader = PdfReader(args.pdf)
    if reader.is_encrypted:
        raise RuntimeError("reader PDF is unexpectedly encrypted")
    if len(reader.pages) != expected_pages:
        raise RuntimeError(f"expected {expected_pages} PDF pages, found {len(reader.pages)}")
    page_sizes = {
        (round(float(page.mediabox.width), 3), round(float(page.mediabox.height), 3))
        for page in reader.pages
    }
    if page_sizes != {(595.276, 841.89)}:
        raise RuntimeError(f"non-A4 or inconsistent page sizes: {page_sizes}")

    localhost_uris: list[str] = []
    file_uris: list[str] = []
    external_uris = 0
    for page in reader.pages:
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            action = annotation.get("/A")
            uri = str(action.get("/URI")) if action and action.get("/URI") else ""
            if not uri:
                continue
            external_uris += 1
            lowered = uri.lower()
            if "127.0.0.1" in lowered or "localhost" in lowered:
                localhost_uris.append(uri)
            if lowered.startswith(("file:", "c:\\", "/")):
                file_uris.append(uri)
    if localhost_uris or file_uris:
        raise RuntimeError(f"private/local PDF link annotations remain: {localhost_uris + file_uris}")

    extracted_texts = [page.extract_text() or "" for page in reader.pages]
    extracted_lengths = [len(text.strip()) for text in extracted_texts]
    if min(extracted_lengths) < 20:
        raise RuntimeError("one or more PDF pages have effectively empty extracted text")
    rights_text = extracted_texts[1]
    rights_text_normalized = " ".join(rights_text.split())
    for required in (
        "Atribusi, Lisensi, dan Pemberitahuan Edisi",
        "CC BY 2.0",
        "CC BY 1.0",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "tidak didukung maupun disahkan",
        "https://www.randomservices.org/random/",
        "https://www.randomservices.org/random/Credits.html",
        "https://creativecommons.org/licenses/by/2.0/",
        "https://creativecommons.org/licenses/by/1.0/",
        "https://doi.org/10.5281/zenodo.22059763",
        "https://github.com/kokunoyumeto/mathematical-statistics-id",
    ):
        if " ".join(required.split()) not in rights_text_normalized:
            raise RuntimeError(f"consolidated rights page is missing required text: {required}")
    content_text = "\n".join(extracted_texts[front_matter_pages:])
    if "Pemberitahuan edisi." in content_text:
        raise RuntimeError("document-level edition notices remain visible in the consolidated PDF")
    notice_policy = pdf_receipt.get("pdf_notice_policy")
    if (
        not isinstance(notice_policy, dict)
        or notice_policy.get("schema") != "o006.random.pdf-notice-policy.v1"
        or notice_policy.get("consolidated_pdf_page") != 2
        or notice_policy.get("source_notices_present") != 29
        or notice_policy.get("source_notices_hidden_in_pdf") != 29
        or notice_policy.get("source_footers_present") != 29
        or notice_policy.get("source_footer_maps") != 58
        or notice_policy.get("source_footer_extra_elements") != 0
        or notice_policy.get("source_footers_hidden_in_pdf") != 29
        or notice_policy.get("html_notices_preserved") is not True
        or not isinstance(notice_policy.get("per_document"), list)
        or len(notice_policy["per_document"]) != 29
    ):
        raise RuntimeError("PDF receipt does not bind the complete notice-consolidation policy")
    license_identity = pdf_receipt.get("license")
    license_path = ROOT / "LICENSE.md"
    if (
        not isinstance(license_identity, dict)
        or license_identity.get("path") != "LICENSE.md"
        or license_identity.get("bytes") != license_path.stat().st_size
        or license_identity.get("sha256") != sha256(license_path)
    ):
        raise RuntimeError("PDF receipt is stale relative to LICENSE.md")
    outline_count = len(flatten_outline(reader.outline))
    if outline_count != 34:
        raise RuntimeError(
            "expected exactly cover, rights page, three contents pages, and 29 document outline "
            f"entries; found {outline_count}"
        )

    images = sorted(args.images.glob("page-*.png"))
    if len(images) != len(reader.pages):
        raise RuntimeError(f"Poppler render count mismatch: {len(images)}")
    ink_ratios: list[float] = []
    edge_ink_pages: list[int] = []
    dimensions: set[tuple[int, int]] = set()
    for page_number, path in enumerate(images, start=1):
        with Image.open(path) as source:
            image = source.convert("L")
            dimensions.add(image.size)
            histogram = image.histogram()
            ink = sum(histogram[:245])
            ink_ratios.append(ink / (image.width * image.height))
            if page_number != 1:
                border = list(image.crop((0, 0, image.width, 2)).get_flattened_data())
                border += list(image.crop((0, image.height - 2, image.width, image.height)).get_flattened_data())
                border += list(image.crop((0, 0, 2, image.height)).get_flattened_data())
                border += list(image.crop((image.width - 2, 0, image.width, image.height)).get_flattened_data())
                if any(pixel < 235 for pixel in border):
                    edge_ink_pages.append(page_number)
    if dimensions != {(596, 842)}:
        raise RuntimeError(f"unexpected Poppler raster dimensions: {dimensions}")
    if min(ink_ratios) < 0.001:
        raise RuntimeError("one or more pages appear blank")
    if edge_ink_pages:
        raise RuntimeError(f"possible clipping at page edge: {edge_ink_pages}")
    contacts = sorted((args.images / "contact-sheets").glob("contact-*.png"))
    expected_contact_sheets = math.ceil(expected_pages / 20)
    if args.manual_contact_sheets_reviewed and len(contacts) != expected_contact_sheets:
        raise RuntimeError(
            "manual contact-sheet review requested but the complete sheet set is absent: "
            f"{len(contacts)} != {expected_contact_sheets}"
        )

    spot_checks = {1, expected_pages}
    cumulative = front_matter_pages
    spot_checks.update(range(2, front_matter_pages + 1))
    for row in documents:
        start = cumulative + 1
        cumulative += int(row["pdf_pages"])
        spot_checks.add(start)
        spot_checks.add(cumulative)

    result = {
        "schema": "o006.random.pdf-visual-qa-receipt.v2",
        "result": "pass",
        "pdf": {
            "path": "output/pdf/statistika-matematis-id-reader.pdf",
            "bytes": args.pdf.stat().st_size,
            "sha256": sha256(args.pdf),
            "physical_pages": len(reader.pages),
            "page_size_points": [595.276, 841.89],
            "encrypted": False,
            "outline_entries": outline_count,
            "external_uri_annotations": external_uris,
            "local_or_loopback_uri_annotations": 0,
            "minimum_extracted_text_characters": min(extracted_lengths),
        },
        "poppler_render": {
            "png_pages": len(images),
            "raster_dimensions": [596, 842],
            "edge_clipping_candidates": 0,
            "minimum_ink_ratio": min(ink_ratios),
            "median_ink_ratio": statistics.median(ink_ratios),
            "maximum_ink_ratio": max(ink_ratios),
        },
        "manual_visual_review": {
            "contact_sheets": len(contacts),
            "all_pages_reviewed_in_contact_sheets": bool(args.manual_contact_sheets_reviewed),
            "reviewed_physical_pages": expected_pages if args.manual_contact_sheets_reviewed else 0,
            "full_resolution_spot_checks": sorted(spot_checks),
            "observed_defects": 0,
            "known_limit": "The consolidated PDF is not tagged after deterministic merge; the offline HTML reader remains the accessibility-first surface.",
        },
    }
    if args.check_only:
        if not RECEIPT.is_file():
            raise RuntimeError("PDF visual QA receipt is missing")
        previous = json.loads(RECEIPT.read_text(encoding="utf-8"))
        if previous != result:
            raise RuntimeError("PDF visual QA receipt differs from the current evidence")
        mode = "verified"
    else:
        RECEIPT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        mode = "written"
    print(json.dumps({"mode": mode, "result": "pass", "pages": len(reader.pages), "sha256": result["pdf"]["sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
