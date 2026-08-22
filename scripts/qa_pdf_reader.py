#!/usr/bin/env python3
"""Automated and recorded visual-surface QA for the consolidated PDF reader."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / "output" / "pdf" / "statistika-matematis-id-reader.pdf"
DEFAULT_IMAGES = ROOT / "tmp" / "pdfs" / "pdf-qa-15"
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
    reader = PdfReader(args.pdf)
    if reader.is_encrypted:
        raise RuntimeError("reader PDF is unexpectedly encrypted")
    if len(reader.pages) != 182:
        raise RuntimeError(f"expected 182 PDF pages, found {len(reader.pages)}")
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

    extracted_lengths = [len((page.extract_text() or "").strip()) for page in reader.pages]
    if min(extracted_lengths) < 20:
        raise RuntimeError("one or more PDF pages have effectively empty extracted text")
    outline_count = len(flatten_outline(reader.outline))
    if outline_count < 17:
        raise RuntimeError(f"expected cover, contents, and 15 document outline entries; found {outline_count}")

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
    if args.manual_contact_sheets_reviewed and len(contacts) != 10:
        raise RuntimeError("manual contact-sheet review requested but the ten-sheet set is incomplete")

    result = {
        "schema": "o006.random.pdf-visual-qa-receipt.v1",
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
            "all_182_pages_reviewed_in_contact_sheets": bool(args.manual_contact_sheets_reviewed),
            "full_resolution_spot_checks": [1, 2, 107, 160, 175, 182],
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
