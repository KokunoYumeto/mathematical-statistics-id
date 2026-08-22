#!/usr/bin/env python3
"""Build the reader-first PDF for the current 14/29 Indonesian checkpoint."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pikepdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
BUILD_HTML = ROOT / "build" / "html-id"
TMP_ROOT = ROOT / "tmp" / "pdfs"
PAGE_ROOT = TMP_ROOT / "pages"
OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT = OUTPUT_DIR / "statistika-matematis-id-reader.pdf"
RECEIPT = ROOT / "build" / "PDF_READER_RECEIPT.json"
RENDERER = ROOT / "scripts" / "render_pdf_pages.mjs"


def dependency_path(env_name: str, *candidates: str | Path | None) -> Path:
    override = os.environ.get(env_name)
    if override:
        return Path(override).expanduser()
    normalized = [Path(value) for value in candidates if value]
    for candidate in normalized:
        if candidate.exists():
            return candidate
    return normalized[0]


NODE = dependency_path(
    "O006_NODE",
    r"C:\Users\Floris\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe",
    shutil.which("node"),
)
PLAYWRIGHT = dependency_path(
    "O006_PLAYWRIGHT_DIR",
    r"C:\Users\Floris\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright",
    ROOT / "node_modules" / "playwright",
)
CHROME = dependency_path(
    "O006_CHROME",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    shutil.which("google-chrome"),
    shutil.which("chromium"),
    shutil.which("chromium-browser"),
)
ARIAL = Path(r"C:\Windows\Fonts\arial.ttf")
ARIAL_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")
PUBLICATION_DATE = "22 Agustus 2026"
FIXED_PDF_DATE = "D:20260822200000+02'00'"

DOCUMENTS = (
    (1, "5. Sampel Acak"),
    (2, "Pengantar Sampel Acak"),
    (3, "Rata-rata Sampel"),
    (4, "Hukum Bilangan Besar"),
    (5, "Teorema Limit Pusat"),
    (6, "Varians Sampel"),
    (7, "Statistik Urutan"),
    (8, "Kovarians dan Korelasi Sampel"),
    (9, "Sampel Normal"),
    (10, "6. Pendugaan Titik"),
    (11, "Penduga"),
    (12, "Metode Momen"),
    (13, "Kemungkinan Maksimum"),
    (14, "Pendugaan Bayes"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return


@contextlib.contextmanager
def local_server():
    handler = partial(QuietHandler, directory=str(BUILD_HTML))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def font_names() -> tuple[str, str]:
    if ARIAL.is_file() and ARIAL_BOLD.is_file():
        pdfmetrics.registerFont(TTFont("O006Arial", str(ARIAL)))
        pdfmetrics.registerFont(TTFont("O006ArialBold", str(ARIAL_BOLD)))
        return "O006Arial", "O006ArialBold"
    return "Helvetica", "Helvetica-Bold"


def wrap(c: canvas.Canvas, text: str, x: float, y: float, width: float, font: str, size: float, leading: float) -> float:
    words = text.split()
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if line and c.stringWidth(candidate, font, size) > width:
            c.drawString(x, y, line)
            y -= leading
            line = word
        else:
            line = candidate
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def build_front_matter(path: Path, page_counts: list[int]) -> None:
    regular, bold = font_names()
    width, height = A4
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
    c.setTitle("Statistika Matematis - Edisi Bahasa Indonesia (id-ID)")
    c.setAuthor("Kyle Siegrist; edisi Bahasa Indonesia oleh Kokuno Yumeto")
    c.setFillColor(HexColor("#15304a"))
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(HexColor("#74b4d8"))
    c.rect(0, height - 34, width, 34, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont(bold, 25)
    c.drawString(50, height - 150, "Statistika Matematis")
    c.setFont(regular, 16)
    c.drawString(50, height - 180, "Edisi Bahasa Indonesia (id-ID)")
    c.setFont(bold, 13)
    c.setFillColor(HexColor("#74b4d8"))
    c.drawString(50, height - 235, "CHECKPOINT PARSIAL: 14 DARI 29 HALAMAN INTI")
    c.setFillColor(HexColor("#ffffff"))
    c.setFont(regular, 10.5)
    y = height - 285
    y = wrap(c, "Bab sampel acak lengkap, diikuti pendugaan titik sampai Pendugaan Bayes. Edisi lengkap belum diklaim; halaman berikutnya adalah Penduga Tak Bias Terbaik.", 50, y, width - 100, regular, 10.5, 15)
    y -= 14
    y = wrap(c, "Berdasarkan Random: Probability, Mathematical Statistics, and Stochastic Processes karya Kyle Siegrist.", 50, y, width - 100, regular, 10.5, 15)
    c.setFont(regular, 9)
    c.setFillColor(HexColor("#d8e8f2"))
    c.drawString(50, 70, f"Diterbitkan {PUBLICATION_DATE}")
    c.drawString(50, 53, "Lisensi dan atribusi komponen dijelaskan pada halaman hak cipta dan paket sumber.")
    c.showPage()

    c.setFillColor(HexColor("#15304a"))
    c.setFont(bold, 20)
    c.drawString(45, height - 55, "Daftar Isi")
    c.setStrokeColor(HexColor("#74b4d8"))
    c.setLineWidth(2)
    c.line(45, height - 68, width - 45, height - 68)
    y = height - 96
    start_page = 3
    for (ordinal, title), count in zip(DOCUMENTS, page_counts, strict=True):
        c.setFont(bold if ordinal in (1, 10) else regular, 9.5)
        c.setFillColor(HexColor("#1b2f42"))
        label = f"{ordinal:02d}. {title}"
        c.drawString(52, y, label)
        c.setFont(regular, 9)
        page_text = str(start_page)
        c.drawRightString(width - 52, y, page_text)
        dots_start = 58 + c.stringWidth(label, bold if ordinal in (1, 10) else regular, 9.5)
        dots_end = width - 62 - c.stringWidth(page_text, regular, 9)
        c.setStrokeColor(HexColor("#b9c6cf"))
        c.setDash(1, 2)
        c.line(dots_start, y - 1, dots_end, y - 1)
        c.setDash()
        y -= 26
        start_page += count
    c.setFillColor(HexColor("#4d5f6c"))
    c.setFont(regular, 8.2)
    wrap(c, "Status: belum lengkap. Semua rincian dan derivasi yang dapat diperluas dalam pembaca HTML dibuka di PDF ini. Laman sumber 1-14 disusun berurutan.", 45, 92, width - 90, regular, 8.2, 11)
    c.showPage()
    c.save()


def overlay(page_number: int, width: float, height: float) -> PdfReader:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height), pageCompression=1, invariant=1)
    regular, _ = font_names()
    c.setFillColor(HexColor("#60717d"))
    c.setFont(regular, 8)
    c.drawCentredString(width / 2, 18, str(page_number))
    c.save()
    buffer.seek(0)
    return PdfReader(buffer)


def produce(candidate: Path) -> dict[str, Any]:
    for required in (BUILD_HTML, RENDERER, NODE, PLAYWRIGHT, CHROME):
        if not required.exists():
            raise RuntimeError(f"missing PDF build dependency: {required}")
    if TMP_ROOT.exists():
        resolved = TMP_ROOT.resolve()
        if resolved.parent != (ROOT / "tmp").resolve():
            raise RuntimeError("refusing to clear an unexpected PDF temp path")
        shutil.rmtree(TMP_ROOT)
    PAGE_ROOT.mkdir(parents=True)
    with local_server() as base_url:
        completed = subprocess.run(
            [
                str(NODE),
                str(RENDERER),
                "--base-url",
                base_url,
                "--output-dir",
                str(PAGE_ROOT),
                "--playwright-dir",
                str(PLAYWRIGHT),
                "--chrome",
                str(CHROME),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600,
            check=False,
        )
    if completed.returncode:
        message = completed.stderr.decode("utf-8", errors="replace")[:4000]
        raise RuntimeError(f"HTML-to-PDF renderer failed: {message}")
    render = json.loads(completed.stdout.decode("utf-8"))
    rows = render.get("documents", [])
    if len(rows) != 14:
        raise RuntimeError(f"expected 14 rendered source documents, found {len(rows)}")
    page_counts: list[int] = []
    for row in rows:
        path = PAGE_ROOT / row["filename"]
        reader = PdfReader(path)
        if not reader.pages:
            raise RuntimeError(f"empty rendered PDF: {path.name}")
        page_counts.append(len(reader.pages))
        row["pdf_pages"] = len(reader.pages)
        row["sha256"] = sha256(path)

    front = TMP_ROOT / "front-matter.pdf"
    build_front_matter(front, page_counts)
    writer = PdfWriter()
    writer.append(str(front))
    starts: list[int] = []
    for row in rows:
        starts.append(len(writer.pages))
        writer.append(str(PAGE_ROOT / row["filename"]))
    canonical_box = RectangleObject((0, 0, A4[0], A4[1]))
    for number, page in enumerate(writer.pages, start=1):
        page.mediabox = RectangleObject(canonical_box)
        page.cropbox = RectangleObject(canonical_box)
        page.merge_page(overlay(number, float(page.mediabox.width), float(page.mediabox.height)).pages[0])
    writer.add_metadata(
        {
            "/Title": "Statistika Matematis - Edisi Bahasa Indonesia (id-ID)",
            "/Author": "Kyle Siegrist; edisi Bahasa Indonesia oleh Kokuno Yumeto",
            "/Subject": "Checkpoint parsial: 14 dari 29 halaman inti",
            "/Keywords": "statistika matematis, Bahasa Indonesia, sumber pendidikan terbuka",
            "/Creator": "O006 deterministic reader pipeline",
            "/Producer": "pypdf + ReportLab + Chromium",
            "/CreationDate": FIXED_PDF_DATE,
            "/ModDate": FIXED_PDF_DATE,
        }
    )
    writer.add_outline_item("Sampul", 0)
    writer.add_outline_item("Daftar Isi", 1)
    for (_, title), page_index in zip(DOCUMENTS, starts, strict=True):
        writer.add_outline_item(title, page_index)
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    candidate.parent.mkdir(parents=True, exist_ok=True)
    raw_pdf = TMP_ROOT / "merged-unoptimized.pdf"
    with raw_pdf.open("wb") as stream:
        writer.write(stream)
    with pikepdf.Pdf.open(raw_pdf) as pdf:
        pdf.remove_unreferenced_resources()
        pdf.save(
            candidate,
            compress_streams=True,
            recompress_flate=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            normalize_content=True,
            deterministic_id=True,
        )
    raw_pdf.unlink()
    final_reader = PdfReader(candidate)
    if len(final_reader.pages) != 2 + sum(page_counts):
        raise RuntimeError("merged PDF page count mismatch")
    return {
        "schema": "o006.random.pdf-reader-receipt.v1",
        "status": "partial-14-of-29",
        "source_documents": 14,
        "physical_pages": len(final_reader.pages),
        "bytes": candidate.stat().st_size,
        "sha256": sha256(candidate),
        "filename": OUTPUT.name,
        "front_matter_pages": 2,
        "documents": rows,
        "browser_version": render.get("browserVersion"),
        "browser_executable_sha256": sha256(CHROME),
        "regular_font_sha256": sha256(ARIAL) if ARIAL.is_file() else None,
        "bold_font_sha256": sha256(ARIAL_BOLD) if ARIAL_BOLD.is_file() else None,
        "renderer_sha256": sha256(RENDERER),
        "builder_sha256": sha256(Path(__file__)),
        "reader_manifest_sha256": sha256(ROOT / "build" / "FIRST_UNIT_MANIFEST.csv"),
        "reader_build_receipt_sha256": sha256(ROOT / "build" / "FIRST_UNIT_BUILD_RECEIPT.json"),
        "reader_qa_receipt_sha256": sha256(ROOT / "build" / "FIRST_UNIT_QA_RECEIPT.json"),
        "license_path": "LICENSE.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    candidate = TMP_ROOT.parent / "statistika-matematis-id-reader.candidate.pdf"
    result = produce(candidate)
    if args.check_only:
        if not OUTPUT.is_file():
            raise RuntimeError("published PDF output is missing")
        if sha256(OUTPUT) != result["sha256"] or OUTPUT.stat().st_size != result["bytes"]:
            raise RuntimeError("PDF replay differs from the current output")
        mode = "verified"
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        os.replace(candidate, OUTPUT)
        RECEIPT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        mode = "written"
    if candidate.exists():
        candidate.unlink()
    shutil.rmtree(TMP_ROOT, ignore_errors=True)
    print(json.dumps({"mode": mode, **{k: result[k] for k in ("filename", "bytes", "sha256", "physical_pages")}}, sort_keys=True))


if __name__ == "__main__":
    main()
