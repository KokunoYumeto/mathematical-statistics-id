#!/usr/bin/env python3
"""Build the complete 29-document Indonesian Random reader PDF."""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
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
BUILD_MANIFEST = ROOT / "build" / "FIRST_UNIT_MANIFEST.csv"
BUILD_RECEIPT = ROOT / "build" / "FIRST_UNIT_BUILD_RECEIPT.json"
QA_RECEIPT = ROOT / "build" / "FIRST_UNIT_QA_RECEIPT.json"
BACKEND_RECEIPT = ROOT / "backend" / "BACKEND_RECEIPT.json"
INTERVAL_RECEIPT = ROOT / "00_control" / "INTERVAL_BATCH_QA_2026-08-23.json"
HYPOTHESIS_RECEIPT = ROOT / "00_control" / "HYPOTHESIS_BATCH_QA_2026-08-23.json"
TRANSLATION_LEDGER = ROOT / "00_control" / "TRANSLATION_LEDGER.csv"
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
    Path.home()
    / ".cache"
    / "codex-runtimes"
    / "codex-primary-runtime"
    / "dependencies"
    / "node"
    / "bin"
    / "node.exe",
    shutil.which("node"),
)
PLAYWRIGHT = dependency_path(
    "O006_PLAYWRIGHT_DIR",
    Path.home()
    / ".cache"
    / "codex-runtimes"
    / "codex-primary-runtime"
    / "dependencies"
    / "node"
    / "node_modules"
    / "playwright",
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
PUBLICATION_DATE = "24 Agustus 2026"
FIXED_PDF_DATE = "D:20260824000000+02'00'"
TRANSLATION_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"
STATUS = "complete-29-of-29"
INVENTORY_SCHEMA = "o006.random.pdf-render-inventory.v1"
RENDER_RESULT_SCHEMA = "o006.random.pdf-render-result.v3"
PDF_RECEIPT_SCHEMA = "o006.random.pdf-reader-receipt.v3"
TOC_ROWS_PER_PAGE = 11

# This is the single canonical PDF inventory. It is cross-checked against the
# live translation ledger, then serialized and passed verbatim to the renderer.
# Chapter rows remain distinct from section rows; ordinal 17 is intentionally a
# chapter heading, not another section of point estimation.
DOCUMENTS: tuple[dict[str, Any], ...] = (
    {"ordinal": 1, "relative_path": "random/sample/index.html", "label": "5. Sampel Acak", "kind": "chapter"},
    {"ordinal": 2, "relative_path": "random/sample/Introduction.html", "label": "Pendahuluan", "kind": "section"},
    {"ordinal": 3, "relative_path": "random/sample/Mean.html", "label": "Rata-Rata Sampel", "kind": "section"},
    {"ordinal": 4, "relative_path": "random/sample/LLN.html", "label": "Hukum Bilangan Besar", "kind": "section"},
    {"ordinal": 5, "relative_path": "random/sample/CLT.html", "label": "Teorema Limit Pusat", "kind": "section"},
    {"ordinal": 6, "relative_path": "random/sample/Variance.html", "label": "Varians Sampel", "kind": "section"},
    {"ordinal": 7, "relative_path": "random/sample/OrderStatistics.html", "label": "Statistik Terurut", "kind": "section"},
    {"ordinal": 8, "relative_path": "random/sample/Covariance.html", "label": "Korelasi dan Regresi Sampel", "kind": "section"},
    {"ordinal": 9, "relative_path": "random/sample/Normal.html", "label": "Sifat Khusus Sampel Normal", "kind": "section"},
    {"ordinal": 10, "relative_path": "random/point/index.html", "label": "6. Pendugaan Titik", "kind": "chapter"},
    {"ordinal": 11, "relative_path": "random/point/Estimators.html", "label": "Penduga", "kind": "section"},
    {"ordinal": 12, "relative_path": "random/point/Moments.html", "label": "Metode Momen", "kind": "section"},
    {"ordinal": 13, "relative_path": "random/point/Likelihood.html", "label": "Kemungkinan Maksimum", "kind": "section"},
    {"ordinal": 14, "relative_path": "random/point/Bayes.html", "label": "Pendugaan Bayes", "kind": "section"},
    {"ordinal": 15, "relative_path": "random/point/Unbiased.html", "label": "Penduga Tak Bias Terbaik", "kind": "section"},
    {"ordinal": 16, "relative_path": "random/point/Sufficient.html", "label": "Statistik Cukup, Lengkap, dan Ancillary", "kind": "section"},
    {"ordinal": 17, "relative_path": "random/interval/index.html", "label": "7. Pendugaan Himpunan", "kind": "chapter"},
    {"ordinal": 18, "relative_path": "random/interval/Introduction.html", "label": "Pendahuluan", "kind": "section"},
    {"ordinal": 19, "relative_path": "random/interval/Normal.html", "label": "Pendugaan pada Model Normal", "kind": "section"},
    {"ordinal": 20, "relative_path": "random/interval/Bernoulli.html", "label": "Pendugaan pada Model Bernoulli", "kind": "section"},
    {"ordinal": 21, "relative_path": "random/interval/BivariateNormal.html", "label": "Pendugaan dalam Model Normal Dua Sampel", "kind": "section"},
    {"ordinal": 22, "relative_path": "random/interval/Bayes.html", "label": "Pendugaan Himpunan Bayes", "kind": "section"},
    {"ordinal": 23, "relative_path": "random/hypothesis/index.html", "label": "8. Pengujian Hipotesis", "kind": "chapter"},
    {"ordinal": 24, "relative_path": "random/hypothesis/Introduction.html", "label": "Pendahuluan", "kind": "section"},
    {"ordinal": 25, "relative_path": "random/hypothesis/Normal.html", "label": "Pengujian pada Model Normal", "kind": "section"},
    {"ordinal": 26, "relative_path": "random/hypothesis/Bernoulli.html", "label": "Pengujian pada Model Bernoulli", "kind": "section"},
    {"ordinal": 27, "relative_path": "random/hypothesis/BivariateNormal.html", "label": "Pengujian pada Model Normal Dua Sampel", "kind": "section"},
    {"ordinal": 28, "relative_path": "random/hypothesis/Likelihood.html", "label": "Uji Rasio Kemungkinan", "kind": "section"},
    {"ordinal": 29, "relative_path": "random/hypothesis/ChiSquare.html", "label": "Uji Khi-Kuadrat", "kind": "section"},
)

PDF_METADATA = {
    "/Title": "Statistika Matematis - Edisi Bahasa Indonesia (id-ID)",
    "/Author": "Kyle Siegrist; edisi Bahasa Indonesia oleh Kokuno Yumeto",
    "/Subject": "complete-29-of-29 - edisi lengkap korpus Random yang dibatasi",
    "/Keywords": "statistika matematis, Bahasa Indonesia, sumber pendidikan terbuka, edisi lengkap",
    "/Creator": "O006 deterministic complete-reader pipeline",
    "/Producer": "pypdf + ReportLab + Chromium",
    "/TranslationProvenance": TRANSLATION_PROVENANCE,
    "/EditionStatus": STATUS,
    "/CreationDate": FIXED_PDF_DATE,
    "/ModDate": FIXED_PDF_DATE,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid required JSON receipt {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"required JSON receipt is not an object: {path}")
    return value


def inventory_payload() -> dict[str, Any]:
    documents: list[dict[str, Any]] = []
    for row in DOCUMENTS:
        document = dict(row)
        reader_path = BUILD_HTML / str(row["relative_path"])
        if not reader_path.is_file():
            raise RuntimeError(f"canonical reader document is missing: {reader_path}")
        document["reader_bytes"] = reader_path.stat().st_size
        document["reader_sha256"] = sha256(reader_path)
        documents.append(document)
    return {
        "schema": INVENTORY_SCHEMA,
        "status": STATUS,
        "source_documents": len(DOCUMENTS),
        "documents": documents,
    }


def expected_paths() -> list[str]:
    return [str(row["relative_path"]) for row in DOCUMENTS]


def receipt_identity(path: Path, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "schema": value.get("schema"),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def assert_exact_paths(actual: list[str], *, surface: str) -> None:
    if actual != expected_paths():
        raise RuntimeError(
            f"{surface} is not the canonical 29-document path/order inventory"
        )


def validate_bound_files(
    bindings: dict[str, Any], *, surface: str, expected_names: set[str]
) -> None:
    if set(bindings) != expected_names:
        raise RuntimeError(f"{surface} has a non-canonical file-binding inventory")
    for name, binding in bindings.items():
        if not isinstance(binding, dict):
            raise RuntimeError(f"{surface} has an invalid {name} file binding")
        relative_path = binding.get("path")
        if not isinstance(relative_path, str):
            raise RuntimeError(f"{surface} has no path for {name}")
        path = (ROOT / Path(relative_path)).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"{surface} has an unsafe {name} path") from exc
        if (
            not path.is_file()
            or path.stat().st_size != binding.get("bytes")
            or sha256(path) != binding.get("sha256")
        ):
            raise RuntimeError(f"{surface} is not bound to the current {name} file")


def validate_full_pipeline_receipts() -> list[dict[str, Any]]:
    """Require a current complete reader, QA, backend, and batch boundary."""

    required = (
        BUILD_MANIFEST,
        BUILD_RECEIPT,
        QA_RECEIPT,
        BACKEND_RECEIPT,
        INTERVAL_RECEIPT,
        HYPOTHESIS_RECEIPT,
        TRANSLATION_LEDGER,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"missing full-edition prerequisite(s): {missing}")

    with TRANSLATION_LEDGER.open("r", encoding="utf-8-sig", newline="") as stream:
        ledger_rows = list(csv.DictReader(stream))
    if len(ledger_rows) != 29:
        raise RuntimeError("translation ledger must contain exactly 29 rows")
    ledger_paths: list[str] = []
    for ordinal, row in enumerate(ledger_rows, start=1):
        if int(row.get("ordinal", "0")) != ordinal or row.get("status") != "complete":
            raise RuntimeError(f"translation ledger row {ordinal} is not complete/canonical")
        source_path = row.get("source_path", "")
        if row.get("target_path") != f"source/id-ID/{source_path}":
            raise RuntimeError(f"translation ledger row {ordinal} target path mismatch")
        ledger_paths.append(source_path)
    assert_exact_paths(ledger_paths, surface="translation ledger")
    ledger_sha256 = sha256(TRANSLATION_LEDGER)

    build = load_json(BUILD_RECEIPT)
    if build.get("schema") != "o006.random.complete-core-build.v1":
        raise RuntimeError("unexpected full reader build receipt schema")
    validate_bound_files(
        build.get("scripts", {}),
        surface="reader build receipt",
        expected_names={"build", "qa"},
    )
    if build.get("translation_provenance") != TRANSLATION_PROVENANCE:
        raise RuntimeError("reader build receipt has stale translation provenance")
    build_ledger = build.get("translation_ledger", {})
    if (
        build_ledger.get("sha256") != ledger_sha256
        or build_ledger.get("required_document_count") != 29
        or build_ledger.get("required_ordinals") != list(range(1, 30))
    ):
        raise RuntimeError("reader build receipt is not bound to the complete ledger")
    assert_exact_paths(
        [
            str(row.get("source_path", ""))
            for row in build_ledger.get("verified_rows", [])
        ],
        surface="reader build ledger bindings",
    )
    build_targets = build.get("inputs", {}).get("targets", [])
    if not isinstance(build_targets, list):
        raise RuntimeError("reader build receipt target inventory is not a list")
    assert_exact_paths(
        [str(row.get("relative_path", "")) for row in build_targets],
        surface="reader build receipt targets",
    )
    build_reader = build.get("reader", {})
    if build_reader.get("manifest_sha256") != sha256(BUILD_MANIFEST):
        raise RuntimeError("reader build receipt is not bound to the current manifest")
    reader_files = build_reader.get("files", [])
    if (
        not isinstance(reader_files, list)
        or build_reader.get("file_count") != len(reader_files)
        or build_reader.get("total_bytes")
        != sum(int(row.get("bytes", -1)) for row in reader_files)
    ):
        raise RuntimeError("reader build receipt has an inconsistent output inventory")
    for row in reader_files:
        relative_path = row.get("relative_path", "")
        path = (BUILD_HTML / Path(relative_path)).resolve()
        try:
            path.relative_to(BUILD_HTML.resolve())
        except ValueError as exc:
            raise RuntimeError(f"reader build receipt has an unsafe output path: {relative_path}") from exc
        if (
            not path.is_file()
            or path.stat().st_size != row.get("bytes")
            or sha256(path) != row.get("sha256")
        ):
            raise RuntimeError(f"reader build output is absent or stale: {relative_path}")

    with BUILD_MANIFEST.open("r", encoding="utf-8-sig", newline="") as stream:
        manifest_paths = {row.get("relative_path", "") for row in csv.DictReader(stream)}
    absent_from_manifest = [path for path in expected_paths() if path not in manifest_paths]
    if absent_from_manifest:
        raise RuntimeError(f"reader manifest omits translated documents: {absent_from_manifest}")

    qa = load_json(QA_RECEIPT)
    if qa.get("schema") != "o006.random.complete-29-reader-qa.v2":
        raise RuntimeError("unexpected full reader QA receipt schema")
    validate_bound_files(
        qa.get("scripts", {}),
        surface="reader QA receipt",
        expected_names={"build", "qa"},
    )
    qa_ledger = qa.get("translation_ledger", {})
    if (
        qa_ledger.get("sha256") != ledger_sha256
        or qa_ledger.get("rows") != 29
        or qa_ledger.get("complete_sequence") != "1-29"
    ):
        raise RuntimeError("reader QA receipt is not bound to the complete ledger")
    qa_results = qa.get("results", {})
    if not isinstance(qa_results, dict) or set(qa_results) != set(expected_paths()):
        raise RuntimeError("full reader QA results do not cover exactly the canonical 29 documents")
    pass_counts = qa.get("pass_counts", {})
    if pass_counts.get("translated_pages") != 29 or pass_counts.get("html_pages") != 31:
        raise RuntimeError(
            "full reader QA receipt does not prove 29 translated pages plus the root and license pages"
        )
    qa_build = qa.get("build", {})
    if qa_build.get("receipt_sha256") != sha256(BUILD_RECEIPT):
        raise RuntimeError("full reader QA receipt is not bound to the current build receipt")
    if qa_build.get("reader_manifest_sha256") != sha256(BUILD_MANIFEST):
        raise RuntimeError("full reader QA receipt is not bound to the current manifest")

    backend = load_json(BACKEND_RECEIPT)
    if backend.get("schema") != "o006.random.backend.receipt.v2":
        raise RuntimeError("unexpected backend receipt schema")
    if backend.get("core", {}).get("files") != 29:
        raise RuntimeError("backend receipt does not cover the 29-document core")
    validate_bound_files(
        {"generator": backend.get("generator", {})},
        surface="backend receipt",
        expected_names={"generator"},
    )
    if backend.get("translation_provenance") != TRANSLATION_PROVENANCE:
        raise RuntimeError("backend receipt has stale translation provenance")
    binding = backend.get("translation_binding", {})
    documents = binding.get("documents", {})
    status_counts = binding.get("status_counts", {})
    if (
        documents.get("total") != 29
        or documents.get("translated") != 29
        or documents.get("untranslated") != 0
        or binding.get("ledger_rows") != 29
        or binding.get("ledger_sha256") != ledger_sha256
        or binding.get("translated_document_ordinals") != list(range(1, 30))
        or status_counts.get("complete") != 29
        or status_counts.get("untranslated") != 0
    ):
        raise RuntimeError("backend receipt is not current for the complete 29-document translation")
    verified_paths = [
        str(row.get("source_path", "")) for row in binding.get("verified_rows", [])
    ]
    assert_exact_paths(verified_paths, surface="backend translation bindings")
    backend_outputs = backend.get("outputs", {})
    if set(backend_outputs) != {"entities.jsonl", "relations.csv"}:
        raise RuntimeError("backend receipt has a non-canonical output inventory")
    for filename, output in backend_outputs.items():
        path = ROOT / "backend" / filename
        if (
            not path.is_file()
            or path.stat().st_size != output.get("bytes")
            or sha256(path) != output.get("sha256")
        ):
            raise RuntimeError(f"backend output is absent or stale: {filename}")

    interval = load_json(INTERVAL_RECEIPT)
    hypothesis = load_json(HYPOTHESIS_RECEIPT)
    for value, path, ordinals in (
        (interval, INTERVAL_RECEIPT, list(range(17, 23))),
        (hypothesis, HYPOTHESIS_RECEIPT, list(range(23, 30))),
    ):
        if value.get("status") != "pass":
            raise RuntimeError(f"batch QA receipt is not passing: {path}")
        if [row.get("ordinal") for row in value.get("pages", [])] != ordinals:
            raise RuntimeError(f"batch QA receipt has the wrong ordinal boundary: {path}")
        ledger = value.get("translation_ledger", {})
        if ledger.get("sha256") != ledger_sha256:
            raise RuntimeError(f"batch QA receipt is not bound to the current ledger: {path}")

    identities = [
        receipt_identity(BUILD_RECEIPT, build),
        receipt_identity(QA_RECEIPT, qa),
        receipt_identity(BACKEND_RECEIPT, backend),
        receipt_identity(INTERVAL_RECEIPT, interval),
        receipt_identity(HYPOTHESIS_RECEIPT, hypothesis),
    ]
    identities.extend(
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in (BUILD_MANIFEST, TRANSLATION_LEDGER)
    )
    return identities


class QuietHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

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


def wrap(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    font: str,
    size: float,
    leading: float,
) -> float:
    c.setFont(font, size)
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


def toc_page_count() -> int:
    return (len(DOCUMENTS) + TOC_ROWS_PER_PAGE - 1) // TOC_ROWS_PER_PAGE


def build_front_matter(path: Path, page_counts: list[int]) -> int:
    regular, bold = font_names()
    width, height = A4
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
    c.setTitle(PDF_METADATA["/Title"])
    c.setAuthor(PDF_METADATA["/Author"])
    c.setSubject(PDF_METADATA["/Subject"])
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
    c.drawString(50, height - 235, "EDISI LENGKAP: 29 DARI 29 DOKUMEN INTI")
    c.setFillColor(HexColor("#ffffff"))
    c.setFont(regular, 10.5)
    y = height - 285
    y = wrap(
        c,
        "Korpus Random yang dibatasi pada Bab 5-8: sampel acak, pendugaan titik, pendugaan interval, dan pengujian hipotesis. Semua rincian dan derivasi yang dapat diperluas dalam pembaca HTML dibuka dalam PDF ini.",
        50,
        y,
        width - 100,
        regular,
        10.5,
        15,
    )
    y -= 14
    y = wrap(
        c,
        "Berdasarkan Random: Probability, Mathematical Statistics, and Stochastic Processes karya Kyle Siegrist. Edisi ini lengkap untuk batas 29 dokumen tersebut, bukan keseluruhan situs Random.",
        50,
        y,
        width - 100,
        regular,
        10.5,
        15,
    )
    y -= 8
    y = wrap(
        c,
        "Penyusunan edisi Bahasa Indonesia: Kokuno Yumeto. Seluruh kredit sumber dan kontributor manusia dipertahankan.",
        50,
        y,
        width - 120,
        regular,
        9.2,
        14,
    )
    wrap(
        c,
        f"Provenans terjemahan dan produksi: {TRANSLATION_PROVENANCE}.",
        50,
        y,
        width - 120,
        regular,
        9.2,
        14,
    )
    c.setFont(regular, 9)
    c.setFillColor(HexColor("#d8e8f2"))
    c.drawString(50, 70, f"Diterbitkan {PUBLICATION_DATE}")
    c.drawString(50, 53, "Lisensi dan atribusi komponen dijelaskan pada halaman hak cipta dan paket sumber.")
    c.showPage()

    c.setFillColor(HexColor("#15304a"))
    c.setFont(bold, 20)
    c.drawString(45, height - 55, "Atribusi, Lisensi, dan Pemberitahuan Edisi")
    c.setStrokeColor(HexColor("#74b4d8"))
    c.setLineWidth(2)
    c.line(45, height - 68, width - 45, height - 68)
    y = height - 104
    notice_sections = (
        (
            "Sumber dan cakupan",
            "Pembaca ini mengadaptasi Random: Probability, Mathematical Statistics, and Stochastic Processes karya Kyle Siegrist. Cakupan edisi ini adalah 29 dokumen Bab 5-8 tentang sampel acak, pendugaan titik, pendugaan himpunan, dan pengujian hipotesis; edisi ini bukan reproduksi seluruh situs Random.",
        ),
        (
            "Lisensi sumber",
            "Laman utama sumber menyatakan Creative Commons Attribution 2.0 (CC BY 2.0), sedangkan laman Credits menautkan Creative Commons Attribution 1.0 (CC BY 1.0). Perbedaan saksi lisensi itu dipertahankan secara eksplisit, dan edisi ini memenuhi kewajiban atribusi serta pemberitahuan perubahan dari keduanya.",
        ),
        (
            "Perubahan edisi",
            "Perubahan meliputi penerjemahan ke Bahasa Indonesia, penambahan ID stabil dan lapisan mesin, pengalihan tautan inti ke edisi lokal, normalisasi tautan HTTPS, deskripsi gambar yang lebih informatif, pembukaan derivasi untuk PDF, dan koreksi terbatas yang terverifikasi. Daftar koreksi edisi, manifes sumber, serta hash setiap berkas disertakan dalam paket sumber.",
        ),
        (
            "Provenans dan kredit",
            f"Penyusunan edisi Bahasa Indonesia: Kokuno Yumeto. Provenans terjemahan dan produksi: {TRANSLATION_PROVENANCE}. Seluruh kredit bagi Kyle Siegrist, sumber asli, dan kontributor manusia dipertahankan.",
        ),
        (
            "Aset eksternal dan non-endorsement",
            "Tautan ke aplikasi, data, biografi, atau materi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services.",
        ),
    )
    for heading, body in notice_sections:
        c.setFillColor(HexColor("#15304a"))
        c.setFont(bold, 10.5)
        c.drawString(45, y, heading)
        y -= 17
        c.setFillColor(HexColor("#1b2f42"))
        y = wrap(c, body, 45, y, width - 90, regular, 9.3, 13.2)
        y -= 10
    c.setFillColor(HexColor("#15304a"))
    c.setFont(bold, 10.5)
    c.drawString(45, y, "Saksi publik")
    y -= 16
    public_witnesses = (
        ("Sumber", "https://www.randomservices.org/random/"),
        ("Kredit", "https://www.randomservices.org/random/Credits.html"),
        ("CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/"),
        ("CC BY 1.0", "https://creativecommons.org/licenses/by/1.0/"),
        ("DOI edisi", "https://doi.org/10.5281/zenodo.22059763"),
        ("Paket sumber", "https://github.com/kokunoyumeto/mathematical-statistics-id"),
    )
    c.setFont(regular, 7.9)
    for label, url in public_witnesses:
        visible = f"{label}: {url}"
        c.setFillColor(HexColor("#173f68"))
        c.drawString(45, y, visible)
        c.linkURL(url, (45, y - 2, 45 + c.stringWidth(visible, regular, 7.9), y + 9))
        y -= 11
    c.setFillColor(HexColor("#e8f2f8"))
    c.roundRect(45, 58, width - 90, 48, 5, fill=1, stroke=0)
    c.setFillColor(HexColor("#314b5f"))
    wrap(
        c,
        "Untuk aliran baca yang lebih baik, PDF ini menggabungkan pemberitahuan per dokumen pada halaman ini. Pembaca HTML tetap mempertahankan pemberitahuan pada setiap dokumen.",
        58,
        87,
        width - 116,
        regular,
        8.5,
        11,
    )
    c.showPage()

    groups = [
        DOCUMENTS[index : index + TOC_ROWS_PER_PAGE]
        for index in range(0, len(DOCUMENTS), TOC_ROWS_PER_PAGE)
    ]
    front_matter_pages = 2 + len(groups)
    document_start_pages: dict[int, int] = {}
    next_start = front_matter_pages + 1
    for document, count in zip(DOCUMENTS, page_counts, strict=True):
        document_start_pages[int(document["ordinal"])] = next_start
        next_start += count

    for toc_index, group in enumerate(groups, start=1):
        c.setFillColor(HexColor("#15304a"))
        c.setFont(bold, 20)
        heading = "Daftar Isi"
        if len(groups) > 1:
            heading += f" ({toc_index} dari {len(groups)})"
        c.drawString(45, height - 55, heading)
        c.setStrokeColor(HexColor("#74b4d8"))
        c.setLineWidth(2)
        c.line(45, height - 68, width - 45, height - 68)
        y = height - 104
        for document in group:
            ordinal = int(document["ordinal"])
            label = f"{ordinal:02d}. {document['label']}"
            is_chapter = document["kind"] == "chapter"
            if is_chapter:
                c.setFillColor(HexColor("#e8f2f8"))
                c.roundRect(45, y - 10, width - 90, 25, 4, fill=1, stroke=0)
            c.setFillColor(HexColor("#15304a") if is_chapter else HexColor("#1b2f42"))
            row_font = bold if is_chapter else regular
            row_size = 10 if is_chapter else 9.5
            row_x = 52 if is_chapter else 66
            c.setFont(row_font, row_size)
            c.drawString(row_x, y, label)
            page_text = str(document_start_pages[ordinal])
            c.setFont(regular, 9)
            c.drawRightString(width - 52, y, page_text)
            dots_start = row_x + c.stringWidth(label, row_font, row_size) + 6
            dots_end = width - 62 - c.stringWidth(page_text, regular, 9)
            if dots_end > dots_start:
                c.setStrokeColor(HexColor("#b9c6cf"))
                c.setDash(1, 2)
                c.line(dots_start, y - 1, dots_end, y - 1)
                c.setDash()
            y -= 42 if is_chapter else 34
        c.setFillColor(HexColor("#4d5f6c"))
        c.setFont(regular, 8.2)
        wrap(
            c,
            f"Status: lengkap untuk 29 dokumen inti yang dibatasi. Halaman daftar isi {toc_index} dari {len(groups)}.",
            45,
            70,
            width - 90,
            regular,
            8.2,
            11,
        )
        c.showPage()
    c.save()
    actual = len(PdfReader(path).pages)
    if actual != front_matter_pages:
        raise RuntimeError(
            f"front-matter page count mismatch: expected {front_matter_pages}, found {actual}"
        )
    return front_matter_pages


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


def validate_pdf_metadata(path: Path) -> None:
    reader = PdfReader(path)
    metadata = reader.metadata or {}
    mismatches = {
        key: {"expected": value, "actual": metadata.get(key)}
        for key, value in PDF_METADATA.items()
        if metadata.get(key) != value
    }
    if mismatches:
        raise RuntimeError(f"PDF canonical metadata mismatch for {path}: {mismatches}")


def outline_item_count(items: list[Any]) -> int:
    return sum(
        outline_item_count(item) if isinstance(item, list) else 1 for item in items
    )


def produce(candidate: Path) -> dict[str, Any]:
    for required in (BUILD_HTML, RENDERER, NODE, PLAYWRIGHT, CHROME, Path(sys.executable)):
        if not required.exists():
            raise RuntimeError(f"missing PDF build dependency: {required}")
    prerequisites = validate_full_pipeline_receipts()

    if TMP_ROOT.exists():
        resolved = TMP_ROOT.resolve()
        if resolved.parent != (ROOT / "tmp").resolve():
            raise RuntimeError("refusing to clear an unexpected PDF temp path")
        shutil.rmtree(TMP_ROOT)
    PAGE_ROOT.mkdir(parents=True)

    inventory = inventory_payload()
    inventory_data = canonical_json_bytes(inventory)
    inventory_path = TMP_ROOT / "render-inventory.json"
    inventory_path.write_bytes(inventory_data)
    inventory_sha256 = sha256_bytes(inventory_data)

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
                "--inventory",
                str(inventory_path),
                "--python",
                sys.executable,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=1200,
            check=False,
        )
    if completed.returncode:
        message = completed.stderr.decode("utf-8", errors="replace")[:4000]
        raise RuntimeError(f"HTML-to-PDF renderer failed: {message}")
    try:
        render = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"renderer returned invalid UTF-8 JSON: {exc}") from exc
    if (
        render.get("schema") != RENDER_RESULT_SCHEMA
        or render.get("inventory_sha256") != inventory_sha256
        or render.get("status") != STATUS
        or render.get("source_documents") != 29
    ):
        raise RuntimeError("renderer result is not bound to the canonical complete inventory")
    rows = render.get("documents", [])
    expected_projection = [
        (row["ordinal"], row["relative_path"], row["label"], row["kind"])
        for row in DOCUMENTS
    ]
    actual_projection = [
        (row.get("ordinal"), row.get("relative_path"), row.get("label"), row.get("kind"))
        for row in rows
    ]
    if actual_projection != expected_projection:
        raise RuntimeError("renderer returned a non-canonical path/order inventory")
    notice_policy = render.get("edition_notice_policy")
    if not isinstance(notice_policy, dict):
        raise RuntimeError("renderer omitted the edition-notice policy")
    if (
        notice_policy.get("schema") != "o006.random.pdf-notice-policy.v1"
        or notice_policy.get("selector")
        != 'section.edition-notice[data-o006-edition-notice="v1"]'
        or notice_policy.get("consolidated_pdf_page") != 2
        or notice_policy.get("source_notices_present") != 29
        or notice_policy.get("source_notices_hidden_in_pdf") != 29
        or notice_policy.get("source_footers_present") != 29
        or notice_policy.get("source_footer_maps") != 58
        or notice_policy.get("source_footer_extra_elements") != 0
        or notice_policy.get("source_footers_hidden_in_pdf") != 29
        or notice_policy.get("html_notices_preserved") is not True
    ):
        raise RuntimeError("renderer edition-notice policy is incomplete")
    notice_rows = notice_policy.get("per_document")
    if not isinstance(notice_rows, list) or len(notice_rows) != 29:
        raise RuntimeError("renderer notice-policy document inventory is incomplete")
    for document_row, notice_row, render_row in zip(DOCUMENTS, notice_rows, rows, strict=True):
        if (
            notice_row.get("ordinal") != document_row["ordinal"]
            or notice_row.get("relative_path") != document_row["relative_path"]
            or not isinstance(notice_row.get("bytes"), int)
            or notice_row["bytes"] < 100
            or not isinstance(notice_row.get("text_characters"), int)
            or notice_row["text_characters"] < 100
            or not isinstance(notice_row.get("sha256"), str)
            or len(notice_row["sha256"]) != 64
            or render_row.get("edition_notice_bytes") != notice_row["bytes"]
            or render_row.get("edition_notice_sha256") != notice_row["sha256"]
            or render_row.get("edition_notice_count") != 1
            or render_row.get("edition_notice_hidden") is not True
            or notice_row.get("footer_maps") != 2
            or notice_row.get("footer_extra_elements") != 0
            or render_row.get("footer_count") != 1
            or render_row.get("hidden_footer_count") != 1
        ):
            raise RuntimeError(
                f"renderer notice evidence differs for {document_row['relative_path']}"
            )

    page_counts: list[int] = []
    next_content_page = 1
    for row, document in zip(rows, inventory["documents"], strict=True):
        if (
            row.get("reader_bytes") != document["reader_bytes"]
            or row.get("reader_sha256") != document["reader_sha256"]
        ):
            raise RuntimeError(
                f"renderer reader-byte identity mismatch: {row['relative_path']}"
            )
        path = PAGE_ROOT / str(row["filename"])
        if path.parent.resolve() != PAGE_ROOT.resolve() or not path.is_file():
            raise RuntimeError(f"renderer returned an unsafe or missing PDF path: {path}")
        reader = PdfReader(path)
        page_count = len(reader.pages)
        if not page_count:
            raise RuntimeError(f"empty rendered PDF: {path.name}")
        expected_start = next_content_page
        expected_end = next_content_page + page_count - 1
        if (
            row.get("pdf_pages") != page_count
            or row.get("content_page_start") != expected_start
            or row.get("content_page_end") != expected_end
            or row.get("bytes") != path.stat().st_size
            or row.get("sha256") != sha256(path)
        ):
            raise RuntimeError(f"renderer page-range or byte identity mismatch: {path.name}")
        page_counts.append(page_count)
        next_content_page = expected_end + 1
    if render.get("content_physical_pages") != sum(page_counts):
        raise RuntimeError("renderer aggregate content-page count mismatch")

    front = TMP_ROOT / "front-matter.pdf"
    front_matter_pages = build_front_matter(front, page_counts)
    writer = PdfWriter()
    writer.append(str(front), import_outline=False)
    starts: list[int] = []
    for row in rows:
        starts.append(len(writer.pages))
        row["physical_page_start"] = len(writer.pages) + 1
        writer.append(str(PAGE_ROOT / row["filename"]), import_outline=False)
        row["physical_page_end"] = len(writer.pages)
        if row["physical_page_end"] - row["physical_page_start"] + 1 != row["pdf_pages"]:
            raise RuntimeError(f"merged page-range mismatch: {row['relative_path']}")

    canonical_box = RectangleObject((0, 0, A4[0], A4[1]))
    for number, page in enumerate(writer.pages, start=1):
        page.mediabox = RectangleObject(canonical_box)
        page.cropbox = RectangleObject(canonical_box)
        page.merge_page(
            overlay(number, float(page.mediabox.width), float(page.mediabox.height)).pages[0]
        )
    writer.add_metadata(PDF_METADATA)
    writer.add_outline_item("Sampul", 0)
    writer.add_outline_item("Atribusi, Lisensi, dan Pemberitahuan Edisi", 1)
    for toc_index in range(toc_page_count()):
        suffix = f" {toc_index + 1}" if toc_page_count() > 1 else ""
        writer.add_outline_item(f"Daftar Isi{suffix}", 2 + toc_index)
    current_chapter = None
    for document, page_index in zip(DOCUMENTS, starts, strict=True):
        if document["kind"] == "chapter":
            current_chapter = writer.add_outline_item(document["label"], page_index)
        else:
            if current_chapter is None:
                raise RuntimeError("section encountered before its chapter bookmark")
            writer.add_outline_item(document["label"], page_index, parent=current_chapter)
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
    expected_physical_pages = front_matter_pages + sum(page_counts)
    if len(final_reader.pages) != expected_physical_pages:
        raise RuntimeError(
            f"merged PDF page count mismatch: expected {expected_physical_pages}, found {len(final_reader.pages)}"
        )
    expected_outline_items = 2 + toc_page_count() + len(DOCUMENTS)
    actual_outline_items = outline_item_count(final_reader.outline)
    if actual_outline_items != expected_outline_items:
        raise RuntimeError(
            f"canonical outline count mismatch: expected {expected_outline_items}, found {actual_outline_items}"
        )
    validate_pdf_metadata(candidate)
    stable_document_receipts = []
    for row in rows:
        stable_row = dict(row)
        # Chromium's temporary per-document PDFs carry run-specific trailer
        # bytes. Their hashes are validated above within this run, but only
        # the normalized merged PDF is a canonical cross-run byte surface.
        stable_row.pop("sha256", None)
        stable_document_receipts.append(stable_row)
    return {
        "schema": PDF_RECEIPT_SCHEMA,
        "translation_provenance": TRANSLATION_PROVENANCE,
        "status": STATUS,
        "canonical_metadata": PDF_METADATA,
        "source_documents": len(DOCUMENTS),
        "physical_pages": len(final_reader.pages),
        "content_physical_pages": sum(page_counts),
        "bytes": candidate.stat().st_size,
        "sha256": sha256(candidate),
        "filename": OUTPUT.name,
        "front_matter_pages": front_matter_pages,
        "toc_pages": toc_page_count(),
        "outline_items": actual_outline_items,
        "inventory": inventory,
        "inventory_bytes": len(inventory_data),
        "inventory_sha256": inventory_sha256,
        "documents": stable_document_receipts,
        "browser_version": render.get("browser_version"),
        "browser_executable_sha256": sha256(CHROME),
        "regular_font_sha256": sha256(ARIAL) if ARIAL.is_file() else None,
        "bold_font_sha256": sha256(ARIAL_BOLD) if ARIAL_BOLD.is_file() else None,
        "renderer_sha256": sha256(RENDERER),
        "builder_sha256": sha256(Path(__file__)),
        "prerequisites": prerequisites,
        "license": {
            "path": "LICENSE.md",
            "bytes": (ROOT / "LICENSE.md").stat().st_size,
            "sha256": sha256(ROOT / "LICENSE.md"),
        },
        "pdf_notice_policy": notice_policy,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    candidate = TMP_ROOT.parent / "statistika-matematis-id-reader.candidate.pdf"
    result = produce(candidate)
    if args.check_only:
        if not OUTPUT.is_file() or not RECEIPT.is_file():
            raise RuntimeError("published PDF output or canonical receipt is missing")
        if sha256(OUTPUT) != result["sha256"] or OUTPUT.stat().st_size != result["bytes"]:
            raise RuntimeError("PDF replay differs from the current output")
        existing_receipt = load_json(RECEIPT)
        if existing_receipt != result:
            raise RuntimeError("PDF replay metadata/receipt differs from the canonical receipt")
        validate_pdf_metadata(OUTPUT)
        mode = "verified"
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        os.replace(candidate, OUTPUT)
        validate_pdf_metadata(OUTPUT)
        RECEIPT.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        mode = "written"
    if candidate.exists():
        candidate.unlink()
    shutil.rmtree(TMP_ROOT, ignore_errors=True)
    print(
        json.dumps(
            {
                "mode": mode,
                **{
                    key: result[key]
                    for key in ("filename", "bytes", "sha256", "physical_pages")
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
