#!/usr/bin/env python3
"""Build and verify the complete deterministic O006 Random id-ID HTML reader."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import posixpath
import re
import shutil
import stat
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "id-ID"
AUTHORITY = ROOT / "authority" / "upstream"
SOURCE_MANIFEST = ROOT / "authority" / "SOURCE_URL_MANIFEST.csv"
SOURCE_FREEZE_RECEIPT = ROOT / "authority" / "SOURCE_FREEZE_RECEIPT.json"
LICENSE_ROOT = ROOT / "authority" / "component-licenses"
LICENSE_MANIFEST = LICENSE_ROOT / "URL_MANIFEST.csv"
LICENSE_FREEZE_RECEIPT = LICENSE_ROOT / "FREEZE_RECEIPT.json"
TRANSLATION_LEDGER = ROOT / "00_control" / "TRANSLATION_LEDGER.csv"
BUILD_DIR = ROOT / "build"
OUTPUT = BUILD_DIR / "html-id"
MANIFEST = BUILD_DIR / "FIRST_UNIT_MANIFEST.csv"
BUILD_RECEIPT = BUILD_DIR / "FIRST_UNIT_BUILD_RECEIPT.json"
QA_SCRIPT = ROOT / "scripts" / "qa_first_unit.py"
RUNTIME_ROOT = ROOT / "authority" / "runtime" / "MathJax-3.1.2"
RUNTIME_BASE64 = RUNTIME_ROOT / "boldsymbol.js.base64"
RUNTIME_RECEIPT = RUNTIME_ROOT / "RUNTIME_RECEIPT.json"
RUNTIME_READER_PATH = PurePosixPath("MathJax/input/tex/extensions/boldsymbol.js")
RUNTIME_BYTES = 4709
RUNTIME_SHA256 = "716cf8735d00abfb1627f8adbbf4aeb915ac9b5c55d47aeaf276e73dac6a2aa1"
TRANSLATION_PROVENANCE = "OpenAI Codex gpt-5.6-sol, Ultra"
CORE_DOCUMENT_COUNT = 29

SOURCE_MANIFEST_HEADER = (
    "relative_path",
    "role",
    "url",
    "bytes",
    "sha256",
    "content_type",
    "last_modified",
    "etag",
)
LICENSE_MANIFEST_HEADER = (
    "relative_path",
    "component",
    "license",
    "url",
    "final_url",
    "bytes",
    "sha256",
    "content_type",
    "last_modified",
    "etag",
)
TRANSLATION_LEDGER_HEADER = (
    "ordinal",
    "source_path",
    "target_path",
    "status",
    "source_bytes",
    "source_sha256",
    "target_bytes",
    "target_sha256",
    "notes",
)

TARGETS = (
    PurePosixPath("random/sample/index.html"),
    PurePosixPath("random/sample/Introduction.html"),
    PurePosixPath("random/sample/Mean.html"),
    PurePosixPath("random/sample/LLN.html"),
    PurePosixPath("random/sample/CLT.html"),
    PurePosixPath("random/sample/Variance.html"),
    PurePosixPath("random/sample/OrderStatistics.html"),
    PurePosixPath("random/sample/Covariance.html"),
    PurePosixPath("random/sample/Normal.html"),
    PurePosixPath("random/point/index.html"),
    PurePosixPath("random/point/Estimators.html"),
    PurePosixPath("random/point/Moments.html"),
    PurePosixPath("random/point/Likelihood.html"),
    PurePosixPath("random/point/Bayes.html"),
    PurePosixPath("random/point/Unbiased.html"),
    PurePosixPath("random/point/Sufficient.html"),
    PurePosixPath("random/interval/index.html"),
    PurePosixPath("random/interval/Introduction.html"),
    PurePosixPath("random/interval/Normal.html"),
    PurePosixPath("random/interval/Bernoulli.html"),
    PurePosixPath("random/interval/BivariateNormal.html"),
    PurePosixPath("random/interval/Bayes.html"),
    PurePosixPath("random/hypothesis/index.html"),
    PurePosixPath("random/hypothesis/Introduction.html"),
    PurePosixPath("random/hypothesis/Normal.html"),
    PurePosixPath("random/hypothesis/Bernoulli.html"),
    PurePosixPath("random/hypothesis/BivariateNormal.html"),
    PurePosixPath("random/hypothesis/Likelihood.html"),
    PurePosixPath("random/hypothesis/ChiSquare.html"),
)

TARGET_ONLY_SUPPORT = {
    PurePosixPath("random/interval/Tails-id.svg"): {
        "bytes": 2150,
        "sha256": "b218a05a39687f1e5c7bf0a14c1702b49e6ce24129e378ede2bcfa7a9fe2c151",
        "purpose": "reader_support_target_only_corrected_figure",
    },
}

HTML_REFERENCE_ATTRIBUTES = {
    "href",
    "src",
    "srcset",
    "poster",
    "data",
    "action",
    "formaction",
    "xlink:href",
    "background",
    "cite",
    "longdesc",
    "manifest",
    "usemap",
}
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_URL_RE = re.compile(
    r"url\(\s*(?:(['\"])(.*?)\1|([^)]*?))\s*\)", re.IGNORECASE | re.DOTALL
)
CSS_IMPORT_RE = re.compile(r"@import\s+(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL)


class DependencyHTMLParser(HTMLParser):
    """Collect dependency-bearing HTML/SVG attributes and inline CSS."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []
        self.inline_css: list[str] = []
        self._style_depth = 0

    def _attributes(self, attrs: list[tuple[str, str | None]]) -> None:
        for raw_name, raw_value in attrs:
            if raw_value is None:
                continue
            name = raw_name.casefold()
            value = raw_value.strip()
            if not value:
                continue
            if name == "style":
                self.inline_css.append(value)
            elif name == "srcset":
                for candidate in value.split(","):
                    fields = candidate.strip().split()
                    if not fields:
                        raise RuntimeError("malformed empty srcset candidate")
                    self.references.append(("html:srcset", fields[0]))
            elif name in HTML_REFERENCE_ATTRIBUTES:
                self.references.append((f"html:{name}", value))

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._attributes(attrs)
        if tag.casefold() == "style":
            self._style_depth += 1

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._attributes(attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "style" and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._style_depth and data:
            self.inline_css.append(data)

# Build-layer-only readability repair.  The translated HTML stays byte-identical
# to its audited target while the reader's existing stylesheet receives one
# exact, deterministic appendix.  The desktop cap keeps mathematical prose
# comfortably readable without narrowing tables to a phone-like column; the
# mobile branch remains fluid and contains wide mathematical surfaces locally.
READABLE_REFLOW_CSS = b"""

/* O006 id-ID readable layout v3 (edition build only) */
@media screen and (min-width: 801px) {
	body:not(.ancillary) {
		box-sizing: border-box;
		max-width: 72rem;
		margin: 1rem auto;
		padding: 0 1.5rem;
	}
}

@media screen and (max-width: 800px) {
	body:not(.ancillary) {
		box-sizing: border-box;
		margin: 0.75rem;
	}
	img, svg, canvas {
		max-width: 100%;
		height: auto;
	}
	div.unit, div.scroll, div.data {
		box-sizing: border-box;
		max-width: 100%;
		overflow-x: auto;
	}
	table {
		display: block;
		max-width: 100%;
		overflow-x: auto;
	}
	mjx-container[display="true"] {
		box-sizing: border-box;
		max-width: 100%;
		overflow-x: auto;
		overflow-y: hidden;
	}
	mjx-assistive-mml,
	mjx-assistive-mml[display="block"] {
		width: 1px !important;
		height: 1px !important;
		max-width: 1px !important;
		max-height: 1px !important;
		overflow: hidden !important;
		clip: rect(0 0 0 0) !important;
		clip-path: inset(50%) !important;
		white-space: nowrap !important;
	}
}
"""

LICENSE_FILES = (
    (
        PurePosixPath("mathjax-3.1.2/LICENSE.txt"),
        PurePosixPath("licenses/MathJax-3.1.2-LICENSE.txt"),
        "Apache-2.0",
    ),
    (
        PurePosixPath("cc0-1.0/legalcode.txt"),
        PurePosixPath("licenses/CC0-1.0-legalcode.txt"),
        "CC0-1.0",
    ),
)

TRANSPORT_HARDENING = (
    {
        "page": "random/sample/index.html",
        "original_href": "http://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt",
        "target_href": "https://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt",
        "reason": "transport-only HTTP-to-HTTPS hardening",
    },
    {
        "page": "random/sample/index.html",
        "original_href": "http://www.google.com/search?q=Statistical+Inference+Casella+Berger",
        "target_href": "https://www.google.com/search?q=Statistical+Inference+Casella+Berger",
        "reason": "transport-only HTTP-to-HTTPS hardening",
    },
    {
        "page": "random/sample/index.html",
        "original_href": "http://www.google.com/search?q=Statistics,Freedman,Pisani,Purves",
        "target_href": "https://www.google.com/search?q=Statistics,Freedman,Pisani,Purves",
        "reason": "transport-only HTTP-to-HTTPS hardening",
    },
    {
        "page": "random/sample/index.html",
        "original_href": "http://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx",
        "target_href": "https://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx",
        "reason": "transport-only HTTP-to-HTTPS hardening",
    },
    {
        "page": "random/sample/index.html",
        "original_href": "http://www.google.com/search?q=Elementary+Statistics,Triola",
        "target_href": "https://www.google.com/search?q=Elementary+Statistics,Triola",
        "reason": "transport-only HTTP-to-HTTPS hardening",
    },
    {
        "page": "random/sample/index.html",
        "original_href": "http://www.google.com/search?q=Introductory+Statistics,Weiss",
        "target_href": "https://www.google.com/search?q=Introductory+Statistics,Weiss",
        "reason": "transport-only HTTP-to-HTTPS hardening",
    },
    {
        "page": "random/sample/index.html",
        "original_href": "http://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
        "target_href": "https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
        "reason": "transport-only HTTP-to-HTTPS hardening",
    },
)

TRANSPORT_HARDENING += tuple(
    {**change, "page": "random/point/index.html"}
    for change in TRANSPORT_HARDENING
    if change["page"] == "random/sample/index.html"
)

BOUNDED_TEXT_CORRECTIONS = (
    {
        "page": "random/sample/Introduction.html",
        "old": r"Secara teknis, suatu <dfn>statistik</dfn> \(w = w(\bs x)\) adalah fungsi yang dapat diamati dari hasil \(\bs x\) eksperimen tersebut.",
        "new": r"Secara teknis, suatu <dfn>statistik</dfn> \(w = w(\bs x)\) adalah fungsi teramati dari hasil eksperimen \(\bs x\).",
        "replacements": 1,
    },
    {
        "page": "random/sample/Introduction.html",
        "old": "Bagaimana kita mengetahui bahwa seseorang akan memilih kandidat yang dikatakannya, atau bahwa ia akan memberikan suara sama sekali (galat pengukuran)?",
        "new": "Bagaimana kita mengetahui bahwa seseorang benar-benar akan memilih kandidat yang menurut pengakuannya akan ia pilih, atau bahkan akan memberikan suara (galat pengukuran)?",
        "replacements": 1,
    },
    {
        "page": "random/sample/Introduction.html",
        "old": "dinyatakan dalam mil ($0.001)",
        "new": "dinyatakan dalam satuan seperseribu dolar ($0.001)",
        "replacements": 1,
    },
    {
        "page": "random/sample/Introduction.html",
        "old": "data wajib militer Vietnam",
        "new": "data undian wajib militer era Perang Vietnam",
        "replacements": 1,
    },
    {
        "page": "random/sample/Introduction.html",
        "old": "Skor SAT Matematika dan Verbal: kemungkinan kontinu, rasio",
        "new": "Skor SAT Matematika dan Verbal: mungkin kontinu, rasio",
        "replacements": 1,
    },
    {
        "page": "random/sample/Introduction.html",
        "old": "pengambilan sampel hingga",
        "new": "pengambilan sampel berhingga",
        "replacements": 1,
    },
    {
        "page": "random/sample/Mean.html",
        "old": "linearitas nilai harapan",
        "new": "linearitas rata-rata sampel",
        "replacements": 2,
        "reason": "the proof invokes linearity of the sample-mean functional, not expectation",
    },
    {
        "page": "random/sample/Mean.html",
        "old": "konstanta tersebut. .",
        "new": "konstanta tersebut.",
        "replacements": 1,
        "reason": "remove duplicated terminal punctuation inherited from the authority",
    },
    {
        "page": "random/sample/CLT.html",
        "old": "0.6741",
        "new": "0.6797",
        "replacements": 1,
        "reason": "the continuity-corrected dice probability is approximately 0.6797",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "nilai harapan</a>) dari distribusi empiris",
        "new": "nilai harapan</a> dari distribusi empiris",
        "replacements": 1,
        "reason": "remove the orphan closing parenthesis after the expected-value link",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "nilai-nilai yang meminimumkan mae",
        "new": "nilai-nilai yang meminimumkannya",
        "replacements": 1,
        "reason": "repair an untranslated bare operator token in prose",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "Hasil-hasil ini mengikuti Teorema 7 dan 8.",
        "new": "Hasil-hasil ini mengikuti sifat penskalaan dan translasi di atas.",
        "replacements": 1,
        "reason": "replace a brittle generated theorem number and spelling defect with the determinate results used",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "Sekarang, untuk \\(i \\in \\{1, 2, \\ldots, n\\}\\), misalkan",
        "new": "Sekarang, anggap himpunan data tidak konstan sehingga simpangan bakunya positif. Untuk \\(i \\in \\{1, 2, \\ldots, n\\}\\), misalkan",
        "replacements": 1,
        "reason": "standard scores require a positive sample standard deviation",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "Distribusi \\(\\sqrt{n}\\left(W^2 - \\sigma^2\\right)",
        "new": "Jika kuadrat deviasi tidak hampir pasti konstan, distribusi \\(\\sqrt{n}\\left(W^2 - \\sigma^2\\right)",
        "replacements": 1,
        "reason": "the standardized CLT denominator must be positive",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "Selanjutnya, kita menghitung kovarians dan korelasi antara rata-rata sampel dan varians sampel khusus.</p>",
        "new": "Selanjutnya, kita menghitung kovarians dan korelasi antara rata-rata sampel dan varians sampel khusus. Rumus korelasi berikut berlaku ketika simpangan baku distribusi dasar positif dan kuadrat deviasinya tidak hampir pasti konstan.</p>",
        "replacements": 1,
        "reason": "state the nondegeneracy conditions under which the displayed correlation exists",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "ketika \\(\\mu\\) tidak diketahui. Dalam hal ini",
        "new": "ketika \\(\\mu\\) tidak diketahui dan sampel memuat sedikitnya dua pengamatan. Dalam hal ini",
        "replacements": 1,
        "reason": "the standard sample variance divides by n-1",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "Pembuktiannya persis sama dengan pembuktian bagi varians baku khusus dalam",
        "new": "Pembuktiannya persis sama dengan pembuktian bagi simpangan baku sampel khusus dalam",
        "replacements": 1,
        "reason": "the Jensen argument parallels the sample-standard-deviation result, not the variance result",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "Tentukan rata-rata sampel jika panjang diukur dalam sentimeter.",
        "new": "Tentukan rata-rata dan simpangan baku sampel jika panjang diukur dalam sentimeter.",
        "replacements": 1,
        "reason": "align the exercise prompt with its two-statistic answer",
    },
    {
        "page": "random/sample/Variance.html",
        "old": "<th>Rata-rata</th>",
        "new": "<th>Rata-rata; kolom terakhir: varians sampel</th>",
        "replacements": 1,
        "reason": "14/9 is the sample variance, not the arithmetic mean of the squared-deviation column",
    },
    {
        "page": "random/sample/Normal.html",
        "old": "distribusi \\(M\\) mendekati distribusi normal jika \\(n\\) besar, bahkan ketika distribusi asal sampelnya tidak normal",
        "new": "distribusi \\(M\\) mendekati distribusi normal ketika \\(n\\) besar, asalkan distribusi asal memiliki varians positif dan berhingga, meskipun distribusi asal tersebut tidak normal",
        "replacements": 1,
        "reason": "the central limit theorem requires a finite positive parent variance; IID alone is insufficient",
    },
    {
        "page": "random/sample/Normal.html",
        "old": "Sekarang, ingat bahwa versi baku varians sampel adalah statistik",
        "new": "Untuk ukuran sampel sekurang-kurangnya dua, ingat bahwa versi baku varians sampel adalah statistik",
        "replacements": 1,
        "reason": "the standard sample variance divides by n-minus-one",
    },
    {
        "page": "random/sample/Normal.html",
        "old": '<p class="dfn">Definisikan',
        "new": '<p class="dfn">Untuk ukuran sampel sekurang-kurangnya dua, definisikan',
        "replacements": 1,
        "reason": "the one-sample Student statistic requires a nondegenerate sample variance",
    },
    {
        "page": "random/sample/Normal.html",
        "old": "Variabel acak berikut berdistribusi \\(F\\) dengan \\(m - 1\\) derajat kebebasan",
        "new": "Jika ukuran masing-masing sampel sekurang-kurangnya dua, variabel acak berikut berdistribusi \\(F\\) dengan \\(m - 1\\) derajat kebebasan",
        "replacements": 1,
        "reason": "the standard sample-variance ratio requires m and n at least two",
    },
    {
        "page": "random/sample/Normal.html",
        "old": "Konstruksi terakhir kita dalam model normal dua sampel",
        "new": "Dengan ukuran setiap sampel sekurang-kurangnya dua, konstruksi terakhir kita dalam model normal dua sampel",
        "replacements": 1,
        "reason": "the pooled two-sample Student construction requires m and n at least two",
    },
    {
        "page": "random/sample/Normal.html",
        "old": "Pasangan-pasangan variabel berikut saling independen:",
        "new": "Karena kedua sampel independen, vektor \\((M(\\bs{X}), S(\\bs{X}))\\) independen dari vektor \\((M(\\bs{Y}), S(\\bs{Y}))\\)",
        "replacements": 1,
        "reason": "replace the malformed and logically incomplete independence proof with its correct vector argument",
    },
    {
        "page": "random/sample/Normal.html",
        "old": "Kovarians dan korelasi antara kedua varians sampel baku adalah",
        "new": "Untuk ukuran sampel sekurang-kurangnya dua, kovarians dan korelasi antara kedua varians sampel baku adalah",
        "replacements": 1,
        "reason": "standard sample variances require n at least two",
    },
    {
        "page": "random/sample/Normal.html",
        "old": "Jika \\(\\mu\\) dan \\(\\nu\\) tidak diketahui (sekali lagi, ini biasanya merupakan keadaan yang terjadi), penduga yang wajar",
        "new": "Untuk ukuran sampel sekurang-kurangnya dua, jika \\(\\mu\\) dan \\(\\nu\\) tidak diketahui (sekali lagi, seperti yang biasanya terjadi), penduga yang wajar",
        "replacements": 1,
        "reason": "the standard sample covariance divides by n-minus-one",
    },
    {
        "page": "random/sample/Normal.html",
        "old": "Rata-rata dan varians dari varians sampel adalah",
        "new": "Rata-rata dan varians dari kovarians sampel adalah",
        "replacements": 1,
        "reason": "the displayed statistic is sample covariance, not sample variance",
    },
    {
        "page": "random/sample/index.html",
        "old": "Rober L Berger",
        "new": "Roger L Berger",
        "replacements": 1,
        "reason": "correct the misspelled name of Statistical Inference coauthor Roger L. Berger",
    },
    {
        "page": "random/point/index.html",
        "old": "Rober L Berger",
        "new": "Roger L Berger",
        "replacements": 1,
        "reason": "correct the misspelled name of Statistical Inference coauthor Roger L. Berger",
    },
)

BOUNDED_TEXT_CORRECTIONS += (
    {
        "page": "random/point/Moments.html",
        "old": "Namun, dalam penerapan berikut, indeks itu kita tampilkan kembali karena kita hendak membahas perilaku asimtotik.</p>",
        "new": "Namun, dalam penerapan berikut, indeks itu kita tampilkan kembali karena kita hendak membahas perilaku asimtotik. Pada sampel berhingga, persamaan momen dapat pula tidak mempunyai solusi dalam ruang parameter atau menghasilkan penyebut nol; dalam kasus seperti itu, rumus yang ditampilkan hanya berlaku ketika solusinya terdefinisi dan memenuhi batas parameter yang dinyatakan.</p>",
        "replacements": 1,
        "reason": "state the finite-sample parameter-space and zero-denominator limits of raw moment equations",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"Ingat bahwa \( \var(W_n^2) \lt \var(S_n^2) \) untuk \( n \in \{2, 3, \ldots\} \), tetapi \( \var(S_n^2) / \var(W_n^2) \to 1 \) ketika \( n \to \infty \).",
        "new": r"Dengan syarat momen pusat keempat berhingga dan lebih besar daripada kuadrat varians, ingat bahwa \( \var(W_n^2) \lt \var(S_n^2) \) untuk \( n \in \{2, 3, \ldots\} \) dan \( \var(S_n^2) / \var(W_n^2) \to 1 \) ketika \( n \to \infty \).",
        "replacements": 1,
        "reason": "the variance comparison and ratio require finite nondegenerate fourth central moment",
    },
    {
        "page": "random/point/Moments.html",
        "old": r'    <p class="math">\( \mse(T_n^2) / \mse(W_n^2) \to 1 \) dan \( \mse(T_n^2) / \mse(S_n^2) \to 1 \) ketika \( n \to \infty \).</p>',
        "new": r'    <p class="math">Jika momen pusat keempat berhingga dan lebih besar daripada kuadrat varians, maka \( \mse(T_n^2) / \mse(W_n^2) \to 1 \) dan \( \mse(T_n^2) / \mse(S_n^2) \to 1 \) ketika \( n \to \infty \).</p>',
        "replacements": 1,
        "reason": "exclude infinite and zero leading terms from the asymptotic MSE-ratio theorem",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"Koefisien \( \sigma_4 \) dan \( \sigma^4 \) dalam \( \mse(T_n^2) \) masing-masing asimtotik terhadap \( 1 / n \) ketika \( n \to \infty \).",
        "new": r"Koefisien \( \sigma_4 \) dan \( \sigma^4 \) dalam \( \mse(T_n^2) \) masing-masing asimtotik terhadap \( 1 / n \) dan negatifnya ketika \( n \to \infty \). Dengan hipotesis di atas, selisih kedua momen itu menghasilkan suku utama bersama yang positif pada pembilang dan penyebut, sehingga rasionya menuju 1.",
        "replacements": 1,
        "reason": "restore the negative sign of the sigma-fourth coefficient and complete the ratio proof",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"Jadi, \( W \) berbias negatif sebagai penduga bagi \( \sigma \), tetapi tak bias secara asimtotik dan konsisten.",
        "new": r"Jadi, bias \( W \) sebagai penduga bagi \( \sigma \) tidak positif dan menjadi negatif kecuali kuadrat penduga tersebut konstan hampir pasti; penduga ini tak bias secara asimtotik dan konsisten.",
        "replacements": 1,
        "reason": "Jensen gives weak rather than universally strict negative bias",
    },
    {
        "page": "random/point/Moments.html",
        "old": "        <p>Mencocokkan rata-rata dan varians distribusi dengan rata-rata dan varians sampel memberikan persamaan",
        "new": "        <p>Rumus di atas menghasilkan nilai dalam ruang parameter hanya ketika rata-rata sampel positif dan varians sampel berbias lebih besar daripada rata-rata sampel. Mencocokkan rata-rata dan varians distribusi dengan rata-rata dan varians sampel memberikan persamaan",
        "replacements": 1,
        "reason": "state the exact admissibility conditions for the two-parameter negative-binomial estimates",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"<p>Andaikan sekarang \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak dari distribusi gamma dengan parameter bentuk \(k\) dan parameter skala \(b\).</p>",
        "new": r"<p>Andaikan sekarang \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak dari distribusi gamma dengan parameter bentuk \(k\) dan parameter skala \(b\). Untuk rumus dua parameter di bawah, diperlukan ukuran sampel sekurang-kurangnya dua dan varians sampel berbias yang positif; untuk sampel kontinu, syarat kedua berlaku hampir pasti.</p>",
        "replacements": 1,
        "reason": "close the gamma two-parameter denominator and parameter-space domain",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"Andaikan sekarang \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari distribusi beta dengan parameter kiri \(a\) dan parameter kanan \(b\).</p>",
        "new": r"Andaikan sekarang \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari distribusi beta dengan parameter kiri \(a\) dan parameter kanan \(b\). Untuk rumus dua parameter di bawah, diperlukan ukuran sampel sekurang-kurangnya dua dan varians sampel berbias yang positif; untuk sampel kontinu, syarat kedua berlaku hampir pasti.</p>",
        "replacements": 1,
        "reason": "close the beta two-parameter denominator and parameter-space domain",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"Andaikan sekarang \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari distribusi Pareto dengan parameter bentuk \(a \gt 2\) dan parameter skala \(b \gt 0\).</p>",
        "new": r"Andaikan sekarang \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari distribusi Pareto dengan parameter bentuk \(a \gt 2\) dan parameter skala \(b \gt 0\). Untuk rumus dua parameter di bawah, diperlukan ukuran sampel sekurang-kurangnya dua dan varians sampel berbias yang positif; untuk sampel kontinu, syarat kedua berlaku hampir pasti.</p>",
        "replacements": 1,
        "reason": "close the Pareto two-parameter denominator and parameter-space domain",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"Andaikan sekarang \( \bs{X} = (X_1, X_2, \ldots, X_n) \) merupakan sampel acak berukuran \( n \) dari distribusi seragam.</p>",
        "new": r"Andaikan sekarang \( \bs{X} = (X_1, X_2, \ldots, X_n) \) merupakan sampel acak berukuran \( n \) dari distribusi seragam. Untuk rumus dua parameter di bawah, diperlukan ukuran sampel sekurang-kurangnya dua dan varians sampel berbias yang positif; untuk sampel kontinu, syarat kedua berlaku hampir pasti.</p>",
        "replacements": 1,
        "reason": "close the uniform two-parameter denominator and parameter-space domain",
    },
    {
        "page": "random/point/Moments.html",
        "old": "        Dengan menyelesaikan persamaan tersebut, diperoleh hasil di atas.</p>",
        "new": "        Dengan menyelesaikan persamaan tersebut, diperoleh hasil di atas. Solusi positif hanya ada ketika momen sampel kedua lebih besar daripada seperempat dan lebih kecil daripada setengah; di luar rentang itu, persamaan momen tidak mempunyai solusi positif.</p>",
        "replacements": 1,
        "reason": "state the exact positive-solution range of the repaired symmetric-beta estimator",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"<p>Jika \(b\) diketahui, persamaan metode momen bagi \(U_b\) sebagai penduga \(a\) adalah \(b U_b \big/ (U_b - 1) = M\). Dengan menyelesaikan persamaan tersebut terhadap \(U_b\), diperoleh rumus di atas.</p>",
        "new": r"<p>Jika \(b\) diketahui, persamaan metode momen bagi \(U_b\) sebagai penduga \(a\) adalah \(b U_b \big/ (U_b - 1) = M\). Dengan menyelesaikan persamaan tersebut terhadap \(U_b\), diperoleh rumus di atas. Karena model pada bagian ini mensyaratkan parameter bentuk lebih besar daripada dua, hasil mentah ini juga harus diperiksa terhadap syarat tersebut.</p>",
        "replacements": 1,
        "reason": "the known-scale Pareto moment solution may fall outside the section's shape-parameter model",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"<p>Kita mengambil sampel \( n \) objek secara acak dari populasi, tanpa pengembalian. Misalkan",
        "new": r"<p>Kita mengambil sampel \( n \) objek secara acak dari populasi, tanpa pengembalian; ukuran sampel diasumsikan sekurang-kurangnya satu dan tidak melebihi ukuran populasi. Misalkan",
        "replacements": 1,
        "reason": "state the hypergeometric sampling constraint one through population size",
    },
    {
        "page": "random/point/Moments.html",
        "old": r"        <p>Semua hasil ini langsung mengikuti fakta bahwa \( \E(X) = \P(X = 1) = r / N \).</p>",
        "new": r"        <p>Semua hasil ini langsung mengikuti fakta bahwa \( \E(X) = \P(X = 1) = r / N \). Penduga bagi parameter bilangan bulat di atas adalah nilai mentah real dari metode momen; jika hasilnya harus berada dalam ruang parameter bilangan bulat, diperlukan aturan proyeksi atau pembulatan terkendala yang dinyatakan secara terpisah.</p>",
        "replacements": 1,
        "reason": "distinguish raw real moment estimates from constrained integer-valued parameter estimates",
    },
)

BOUNDED_TEXT_CORRECTIONS += (
    {
        "page": "random/point/Unbiased.html",
        "old": "turunannya didominasi oleh fungsi terintegralkan pada suatu lingkungan setiap nilai parameter",
        "new": "nilai mutlak hasil kali fungsi statistik dengan turunan tersebut didominasi oleh fungsi terintegralkan",
        "replacements": 1,
        "reason": "differentiate under the integral only under a local integrable-domination condition",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "Kekontinuan saja cukup untuk menggantikan syarat dominasi.",
        "new": "Kekontinuan saja tidak menggantikan syarat dominasi. Untuk memakai bentuk batas yang membagi dengan informasi Fisher, informasi tersebut juga harus positif dan berhingga.",
        "replacements": 1,
        "reason": "state both the domination requirement and the finite positive information denominator",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "untuk suatu nilai parameter merupakan penduga tak bias dengan varians minimum seragam",
        "new": "untuk setiap nilai parameter merupakan penduga tak bias dengan varians minimum seragam",
        "replacements": 1,
        "reason": "attaining a pointwise bound implies UMVUE only when attainment holds across the parameter set",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "Kesamaan tersebut langsung membuat penduga menjadi UMVUE.",
        "new": "Pada setiap nilai parameter yang tetap, kesamaan",
        "replacements": 1,
        "reason": "state the equality characterization pointwise before drawing a uniform conclusion",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "Jika hubungan berikut berlaku pada satu nilai parameter, penduga tersebut merupakan UMVUE:",
        "new": "Jika hubungan berikut berlaku untuk setiap nilai parameter, batas tercapai di seluruh ruang parameter dan penduga tersebut merupakan UMVUE:",
        "replacements": 1,
        "reason": "require equality across the full parameter set before concluding UMVUE",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "Untuk pendugaan rata-rata dan varians secara bersama, rumus skalar yang sama berlaku langsung.",
        "new": "Pendugaan rata-rata dan varians secara bersama memakai matriks informasi Fisher; pada model normal, informasi silang keduanya nol sehingga unsur diagonal invers matriks menghasilkan batas skalar yang sama seperti yang ditampilkan di bawah.",
        "replacements": 1,
        "reason": "qualify the scalar normal bounds with the diagonal joint Fisher-information calculation",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "fungsi kepadatan probabilitas untuk satu pengamatan X dari distribusi yang disampel adalah",
        "new": "fungsi kepadatan probabilitas satu pengamatan dari distribusi asal sampel adalah",
        "replacements": 2,
        "reason": "identify g_a as the one-observation density in both beta and uniform models",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "Rata-rata sampel bukan UMVUE untuk setiap ukuran sampel.",
        "new": "Untuk ukuran sampel satu, penduga tersebut sama dengan pengamatan tunggal dan merupakan UMVUE",
        "replacements": 1,
        "reason": "record the n-equals-one beta exception to the source's invalid nonattainment inference",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "Tidak tercapainya batas itu sendiri membuktikan bahwa penduga bukan UMVUE.",
        "new": "Untuk ukuran sampel sekurang-kurangnya dua, penduga itu bukan UMVUE",
        "replacements": 1,
        "reason": "state the separately justified strict Rao-Blackwell conclusion for beta samples of size at least two",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "Namun, nilai itu bukan batas bawah",
        "new": "Substitusi formal ke bentuk berbasis turunan kedua menghasilkan negatif dari nilai tersebut. Namun, kedua nilai itu bukan batas bawah",
        "replacements": 1,
        "reason": "label the support-dependent uniform substitution as formal rather than a valid Cramer-Rao bound",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "hal itu melanggar batas bawah Cram&eacute;r–Rao.",
        "new": "hal itu menegaskan kegagalan syarat regularitas, bukan pelanggaran suatu batas bawah yang sah.",
        "replacements": 1,
        "reason": "interpret the smaller uniform-estimator variance as failed regularity, not a contradicted bound",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": "tetapi simpangan bakunya dapat berbeda.</p>",
        "new": "Jika salah satu simpangan baku nol, variabel hasil yang bersesuaian sama dengan rata-rata itu hampir pasti dan sudah menjadi penduga tepat; bobot invers-varians di bawah tidak terdefinisi. Karena itu, rumus berikut mengasumsikan semua simpangan baku positif.</p>",
        "replacements": 1,
        "reason": "separate the exact zero-variance case before imposing positivity for inverse-variance BLUE weights",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": r"jika vektor simpangan baku \(\bs{\sigma}\) diketahui.",
        "new": r"jika vektor simpangan baku positif \(\bs{\sigma}\) diketahui.",
        "replacements": 1,
        "reason": "carry the positive-standard-deviation domain into the BLUE summary",
    },
)

BOUNDED_REFERENCE_CORRECTIONS = (
    {
        "page": "random/point/Unbiased.html",
        "old": 'href="#crb3"',
        "new": 'href="#crb2"',
        "replacements": 7,
        "surface": "internal_reference",
        "reason": "the seven distribution checks invoke assumption crb2 rather than consequence crb3",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": 'href="#crb8"',
        "new": 'href="#crb6"',
        "replacements": 1,
        "surface": "internal_reference",
        "reason": "the Fisher-information denominator occurs in the general bound crb6, not the equality theorem crb8",
    },
    {
        "page": "random/point/Unbiased.html",
        "old": 'href="#sam5"',
        "new": 'href="#sam4"',
        "replacements": 1,
        "surface": "internal_reference",
        "reason": "the formal uniform substitution is made in the score-based random-sample bound sam4",
    },
)

PROTECTED_MATH_CORRECTIONS = (
    {
        "page": "random/sample/Introduction.html",
        "old": r"\newcommand{\bs}{\boldsymbol}",
        "new": r"\newcommand{\bs}[1]{\boldsymbol{#1}}",
        "replacements": 1,
        "surface": "math_span",
        "reason": "give the vector macro an explicit argument so MathJax does not concatenate its first use into the undefined control sequence \\boldsymbolx",
    },
    {
        "page": "random/sample/Mean.html",
        "old": r"p\left(\bigcup_{i \in I} A_i\right)",
        "new": r"p\left(\bigcup_{j \in J} A_j\right)",
        "replacements": 1,
        "surface": "raw_tex",
        "reason": "the partition is indexed by j in J; i in I is undefined here",
    },
    {
        "page": "random/sample/Mean.html",
        "old": r"\quad x \in A_j \</p>",
        "new": r"\quad x \in A_j \]</p>",
        "span_old": "\\quad x \\in A_j \\",
        "span_new": r"\quad x \in A_j \]",
        "replacements": 1,
        "surface": "math_span",
        "reason": "close the displayed expression with \\] before the paragraph ends",
    },
    {
        "page": "random/sample/Mean.html",
        "old": r"\lambda_k(A_j)",
        "new": r"\lambda_d(A_j)",
        "replacements": 2,
        "surface": "math_span",
        "reason": "the ambient dimension is d and k is undefined",
    },
    {
        "page": "random/sample/Mean.html",
        "old": r"\([50.315, 50.324)\)",
        "new": r"\([50.315, 50.325)\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "rounding to 0.01 gives the upper half-step endpoint 50.325",
    },
    {
        "page": "random/sample/Mean.html",
        "old": r"\((10, 20])\)",
        "new": r"\((10, 20]\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "remove the unmatched literal parenthesis after the interval",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"= \frac{1}{n} \sum_{i=1}^n X_i^+ - \sum_{i=1}^n X_i^- \to",
        "new": r"= \frac{1}{n} \sum_{i=1}^n X_i^+ - \frac{1}{n} \sum_{i=1}^n X_i^- \to",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the negative-part term in the sample-mean decomposition also requires the factor 1/n",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"\[ f_n(x) \approx f(x), \quad x \in S \]",
        "new": r"\[ f_n(x) \to \frac{\P(X \in A_j)}{\lambda_d(A_j)} = \frac{1}{\lambda_d(A_j)} \int_{A_j} f(u) \, du \text{ ketika } n \to \infty, \quad j \in J, \; x \in A_j \]",
        "replacements": 1,
        "surface": "math_span",
        "reason": "for a fixed partition the empirical density converges to the cell-average density, not generally to f(x)",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"\(P\left(\left[0, \frac{1}{2}\right]\right)\)",
        "new": r"\(P_9\left(\left[0, \frac{1}{2}\right]\right)\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the empirical probability is based on the stated sample size 9",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"\(P\left([2, 3]\right)\)",
        "new": r"\(P_{16}\left([2, 3]\right)\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the empirical probability is based on the stated sample size 16",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"\(\frac{19}{216}, \frac{3743}{746 \; 496}\)",
        "new": r"\(\frac{19}{216}, \frac{3743}{746 \, 496}\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the denominator is the integer 746496; use narrow grouping rather than a binary-relation-sized gap",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\(\bs{V} = (V_0, V_1, V_2, \ldots)\)",
        "new": r"\(\bs{V} = (V_0, V_1, V_2, \ldots), V_0 = 0\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the converse partial-sum characterization requires the process to start at zero",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\(m \in \N\)",
        "new": r"\(m \in \N_+\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "cor(Y_0,Y_n) is undefined because Y_0 has zero variance",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\[ \cor(Y_m, Y_m) = \frac{\cov(Y_m, Y_n)}{\sd(Y_m) \sd(Y_n)} = \frac{m \sigma^2}{\sqrt{m \sigma^2} \sqrt{n \sigma^2}} = \sqrt{\frac{m}{n}} \]",
        "new": r"\[ \cor(Y_m, Y_n) = \frac{\cov(Y_m, Y_n)}{\sd(Y_m) \sd(Y_n)} = \frac{m \sigma^2}{\sqrt{m \sigma^2} \sqrt{n \sigma^2}} = \sqrt{\frac{m}{n}} \]",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the displayed correlation is between Y_m and Y_n, not Y_m and itself",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\[ \chi\left(\frac{t}{\sqrt{n}}\right) = 1 + \frac{1}{2} \chi^{\prime\prime}(s_n) \frac{t^2}{n} \text{ where } \left|s_n\right| \le \frac{\left|t\right|}{n} \]",
        "new": r"\[ \chi\left(\frac{t}{\sqrt{n}}\right) = 1 - \frac{t^2}{2n} + o\left(\frac{1}{n}\right) \]",
        "replacements": 1,
        "surface": "math_span",
        "reason": "use the valid second-order Peano expansion for a complex characteristic function",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\(s_n \to 0\)",
        "new": r"\(o(1/n)\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "replace the invalid real-valued Lagrange-remainder intermediate with its Peano remainder",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\(\chi^{\prime\prime}(s_n) \to -1\)",
        "new": r"\(t\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "state the fixed characteristic-function argument after replacing the invalid remainder proof",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\[ \chi_n(t) = \left[1 + \frac{1}{2} \chi^{\prime\prime}(s_n) \frac{t^2}{n} \right]^n \to e^{-\frac{1}{2} t^2} \text{ as } n \to \infty \]",
        "new": r"\[ \chi_n(t) = \left[1 - \frac{t^2}{2n} + o\left(\frac{1}{n}\right)\right]^n \to e^{-\frac{1}{2} t^2} \text{ ketika } n \to \infty \]",
        "replacements": 1,
        "surface": "math_span",
        "reason": "complete the characteristic-function proof with the valid Peano expansion and complex exponential limit",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\(\{Y = k\}\)",
        "new": r"\(\{Y_n = k\}\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the continuity-correction event concerns the indexed sum Y_n",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r'''<p class="app">In the <a href="JavaScript:openAncillary('../apps/SpecialSimulator.html')" class="ancillary">special distribution simulator</a>, select the gamma distribution. Vary and \(b\) and note the shape of the probability density function. With \(k = 10\) and various values of \(b\), run the experiment 1000 times and compare the empirical density function to the true probability density function.</p>''',
        "new": r'''<p class="app">Dalam <a href="https://www.randomservices.org/random/apps/SpecialSimulator.html" class="ancillary">simulator distribusi khusus</a>, pilih distribusi gamma. Variasikan parameter \((k, b)\), lalu perhatikan bentuk fungsi kepadatan probabilitasnya. Dengan \(k = 10\) dan berbagai nilai \(b\), jalankan eksperimen 1.000 kali dan bandingkan fungsi kepadatan empiris dengan fungsi kepadatan probabilitas sebenarnya.</p>''',
        "span_old": r"\(b\)",
        "span_new": r"\((k, b)\)",
        "span_index": 202,
        "replacements": 1,
        "surface": "math_span",
        "reason": "restore the omitted gamma shape parameter in the simulator instruction",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\[ f(n) = \binom{n + k - 1}{n} p^k (1 - p)^n, \quad n \in \N_+ \]",
        "new": r"\[ f(n) = \binom{n + k - 1}{n} p^k (1 - p)^n, \quad n \in \N \]",
        "replacements": 1,
        "surface": "math_span",
        "reason": "a negative-binomial failure count can be zero",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\( k \in (0, 1) \)",
        "new": r"\( k \in (0, \infty) \)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the negative-binomial shape parameter is positive, not restricted below one",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r'''<p class="math">Suppose that \(Y\) has the negative binomial distribution with trial parameter \(k = 10\) and success parameter \(p = 0.4\). Find normal approximations to each of the following: </p>''',
        "new": r'''<p class="math">Misalkan \(V\) menyatakan nomor percobaan tempat keberhasilan ke-\(k = 10\) terjadi dalam barisan percobaan Bernoulli dengan parameter keberhasilan \(p = 0.4\). Tentukan aproksimasi normal untuk masing-masing hal berikut:</p>''',
        "span_old": r"\(Y\)",
        "span_new": r"\(V\)",
        "span_index": 340,
        "replacements": 1,
        "surface": "math_span",
        "reason": "the retained answers use the trial number of the kth success, not the failure count",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\(\P(20 \lt Y \lt 30)\)",
        "new": r"\(\P(20 \le V \le 30)\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the retained probability answer uses the inclusive trial-number event",
    },
    {
        "page": "random/sample/CLT.html",
        "old": (
            r"<li>\(\P(20 \lt Y \lt 30)\)</li>"
            "\n\t\t"
            r"<li>The 80th percentile of \(Y\)</li>"
        ),
        "new": (
            r"<li>\(\P(20 \le V \le 30)\)</li>"
            "\n\t\t"
            r"<li>Persentil ke-80 dari \(V\)</li>"
        ),
        "span_old": r"\(Y\)",
        "span_new": r"\(V\)",
        "span_index": 344,
        "replacements": 1,
        "surface": "math_span",
        "reason": "bind the percentile request to the corrected trial-number variable",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\sum_{i=1}^n x_i^2 - 2 m \sum_{i=1}^n x_i - \sum_{i=1}^n m^2\\",
        "new": r"\sum_{i=1}^n x_i^2 - 2 m \sum_{i=1}^n x_i + \sum_{i=1}^n m^2\\",
        "replacements": 1,
        "surface": "raw_tex",
        "reason": "the expansion of each squared deviation has a positive m-squared term",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(\cor\left(M, W^2\right) = \sigma^3 \big/ \sqrt{\sigma^2 (\sigma_4 - \sigma^4)}\)",
        "new": r"\(\cor\left(M, W^2\right) = \frac{\sigma_3}{\sigma \sqrt{\sigma_4 - \sigma^4}}\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the covariance numerator is the third central moment sigma_3, not sigma cubed",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\sum_{k=1}^n \cov[(X_i - X_j)^2, (X_k - X_l)^2]",
        "new": r"\sum_{l=1}^n \cov[(X_i - X_j)^2, (X_k - X_l)^2]",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the fourth independent summation index is l",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(\var\left(S^2\right) \gt \var\left(W^2\right)\)",
        "new": r"\(\var\left(S^2\right) \ge \var\left(W^2\right)\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "equality holds for a degenerate population; strictness requires positive variance",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\( V^2 \)",
        "new": r"\( S^2 \)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the standard sample variance is denoted S-squared; V-squared is undefined",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(s^2 = 203/121\)",
        "new": r"\(s^2 = 203/132\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the twelve-value sample variance is 203/132",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\((10, 20])\)",
        "new": r"\((10, 20]\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "remove the unmatched literal parenthesis after the interval",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"<li>\(-2/875\)\)</li>",
        "new": r"<li>\(-2/875\)</li>",
        "replacements": 1,
        "surface": "raw_tex",
        "reason": "remove the orphan closing TeX delimiter after the answer",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(1/5 \lambda^2\)",
        "new": r"\(1/(5 \lambda^2)\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "place lambda-squared in the denominator of var(M)",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(8/5 \lambda^4\)",
        "new": r"\(8/(5 \lambda^4)\)",
        "replacements": 2,
        "surface": "math_span",
        "reason": "place lambda-fourth in the denominator of both exponential-sample answers",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(17/10 \lambda^4\)",
        "new": r"\(17/(10 \lambda^4)\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "place lambda-fourth in the denominator of var(S-squared)",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(2/5 \lambda^3\)",
        "new": r"\(2/(5 \lambda^3)\)",
        "replacements": 2,
        "surface": "math_span",
        "reason": "place lambda-cubed in the denominator of both covariance answers",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(207/512\)",
        "new": r"\(603/448\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "correct var(S-squared) for eight ace-six-flat die rolls",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(s(1) = 30.5\)",
        "new": r"\(s(1) = 5.5\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "correct the frozen Iris subgroup sample standard deviation for type 1",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(s(2) = 28.7\)",
        "new": r"\(s(2) = 5.4\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "correct the frozen Iris subgroup sample standard deviation for type 2",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(\text{km}/\text{hr}\)",
        "new": r"\(\text{km}/\text{s}\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "the retained transformation x+299000 converts km/s, not km/hr",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(s(g) = 0.57\)",
        "new": r"\(s(g) = 3.12\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "correct the frozen green M-and-M count sample standard deviation",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(s(0) = 3.69\)",
        "new": r"\(s(o) = 3.69\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "use the letter o for the orange subgroup rather than zero",
    },
    {
        "page": "random/sample/Variance.html",
        "old": r"\(s(1) = 0.185\)",
        "new": r"\(s(1) = 0.055\)",
        "replacements": 1,
        "surface": "math_span",
        "reason": "correct the frozen species-1 Cicada subgroup sample standard deviation",
    },
)

ORDER_STATISTICS_MATH_CORRECTIONS = (
    (20, r"\[ x_{(1)} = \min\{x_1, x_2 \ldots, x_n\}, \quad x_{(n)} = \max\{x_1, x_2, \ldots, x_n\} \]", r"\[ x_{(1)} = \min\{x_1, x_2, \ldots, x_n\}, \quad x_{(n)} = \max\{x_1, x_2, \ldots, x_n\} \]", "restore the missing separator in the minimum list"),
    (22, r"\(\frac{r}{2} = \frac{1}{2}\left[x_{(n)} - x_{(1)}\right]\)", r"\(\frac{1}{2}\left[x_{(n)} + x_{(1)}\right]\)", "define the sample midrange as the half-sum of the extremes"),
    (42, r"\(k \in \{1, 2, \ldots, n\}\)", r"\(k \in \{1, 2, \ldots, n - 1\}\)", "keep the interpolation index valid on the p-less-than-one branch"),
    (44, r"\(p \in [0, 1]\)", r"\(p \in [0, 1)\)", "separate the right endpoint from the interpolation formula"),
    (46, r"\(k = \lfloor (n - 1)p + 1 \rfloor\)", r"\(k = \lfloor (n - 1)p + 1 \rfloor,\quad t = [(n - 1)p + 1] - k\)", "state the interpolation index and fraction together"),
    (47, r"\(t = [(n - 1)p + 1] - k\)", r"\(x_{[1]} = x_{(n)};\quad n = 1 \Longrightarrow x_{[p]} = x_1\ (p \in [0, 1])\)", "close the p-equals-one and singleton quantile cases"),
    (75, r"\(F(x) = \frac{k}{n}\)", r"\(j_k = \max\{i : x_{(i)} = x_{(k)}\},\ k \in \{1, 2, \ldots, n - 1\},\ x_{(k)} \lt x_{(k+1)}\)", "index empirical-CDF jumps by the last tied observation"),
    (76, r"\(x \in [x_{(k)}, x_{(k+1)})\)", r"\(F(x) = 0\ (x \lt x_{(1)});\quad F(x) = j_k/n\ (x_{(k)} \le x \lt x_{(k+1)});\quad F(x) = 1\ (x \ge x_{(n)})\)", "state a tie-aware empirical CDF on all intervals"),
    (106, r"\(\bs{y} = \bs{a} + b \bs{x}\)", r"\(\bs{y} = (a + b x_1, a + b x_2, \ldots, a + b x_n)\)", "replace the undefined bold-a vector with the explicit transformed sample"),
    (114, r"\(p \in [0, 1]\)", r"\(p = 1,\ y_{(n)} = a + b x_{(n)}\)", "prove the transformed right-endpoint quantile directly"),
    (115, r"\(k \in \{1, 2, \ldots,n\}\)", r"\(p \in [0, 1)\)", "restrict the interpolation proof to the non-endpoint branch"),
    (116, r"\(t \in [0, 1)\)", r"\(k \in \{1, 2, \ldots, n - 1\},\ t \in [0, 1)\)", "keep both interpolation indices valid in the transformation proof"),
    (143, r"\(p \in [0, 1]\)", r"\(p = 1\)", "separate the convexity proof's right endpoint"),
    (144, r"\(k \in \{1, 2, \ldots, n\}\)", r"\(p \in [0, 1)\)", "restrict the convexity interpolation branch below one"),
    (145, r"\(t \in [0, 1)\)", r"\(k \in \{1, 2, \ldots, n - 1\},\ t \in [0, 1)\)", "keep convexity interpolation indices within the sample"),
    (178, r"\( (-\infty x] \)", r"\( (-\infty, x] \)", "restore the missing interval comma"),
    (297, r"\( \left(\left(x_{(1)}, y_1\right), \left(x_{(2)}, y_2\right) \ldots, \left(x_{(n)}, y_n\right)\right) \)", r"\( \left(\left(x_{(1)}, y_1\right), \left(x_{(2)}, y_2\right), \ldots, \left(x_{(n)}, y_n\right)\right) \)", "restore the missing separator in the probability-plot point sequence"),
    (328, r"\(y_{(1)} = 40\)", r"\(w_{(1)} = 40\)", "use the stated transformed-grade variable"),
    (329, r"\(q_1 \le 72.11\)", r"\(q_1(w) = 10\sqrt{52} \approx 72.11\)", "give the exact transformed first quartile"),
    (330, r"\(q_2 \le 80\)", r"\(q_2(w) = 80\)", "give the exact transformed median"),
    (331, r"\(q_3 \le 84.85 \)", r"\(q_3(w) = 10\sqrt{72} \approx 84.85\)", "give the exact transformed third quartile"),
    (332, r"\(y_{(25)} = 90\)", r"\(w_{(25)} = 90\)", "use the stated transformed-grade variable"),
    (400, r"\(n\)", r"\(n \ge 2\)", "exclude the degenerate one-point uniform range from the beta density"),
    (419, r"\( n \)", r"\( n \ge 2 \)", "state the sample-size domain for the general-uniform range result"),
    (428, r"\( \var(R) = h^2 \frac{2 (n _ 1)}{(n + 1)^2 (n + 2)} \)", r"\( \var(R) = h^2 \frac{2 (n - 1)}{(n + 1)^2 (n + 2)} \)", "replace the stray underscore with subtraction in the range variance"),
    (437, r"\( X_{(n)} - X_{(1)} = h(U_{(n)} - U_{(1)} \)", r"\( X_{(n)} - X_{(1)} = h(U_{(n)} - U_{(1)}) \)", "close the transformed-range parenthesis"),
    (445, r"\(\left\{\bs{x} \in [a, a + h]^n: a \le x_1 \le x_2 \le \cdots \le x_n \lt a + h\right\}\)", r"\(\left\{\bs{x} \in [a, a + h]^n: a \le x_1 \le x_2 \le \cdots \le x_n \le a + h\right\}\)", "include the stated closed uniform endpoint in the support"),
    (472, r"\(n\)", r"\(n \ge 2\)", "exclude the degenerate one-point exponential range from the density"),
    (491, r"\[ g(x_1, x_2, \ldots, x_n) = n! \lambda^n e^{-\lambda(x_1 + x_2 + \cdots + x_n)}, \quad 0 \le x_1 \le x_2 \cdots \le x_n \lt \infty \]", r"\[ g(x_1, x_2, \ldots, x_n) = n! \lambda^n e^{-\lambda(x_1 + x_2 + \cdots + x_n)}, \quad 0 \le x_1 \le x_2 \le \cdots \le x_n \lt \infty \]", "restore the missing inequality in the ordered exponential support"),
    (532, r"\(h(0) = \frac{6}{1296}, \; h(1) = \frac{70}{1296}, \; h(2) = \frac{300}{1296}, \; h(3) = \frac{300}{1296}, \; h(4) = \frac{318}{1296}, \; h(5) = \frac{302}{1296}\)", r"\(h(0) = \frac{6}{1296}, \; h(1) = \frac{70}{1296}, \; h(2) = \frac{200}{1296}, \; h(3) = \frac{330}{1296}, \; h(4) = \frac{388}{1296}, \; h(5) = \frac{302}{1296}\)", "correct the four-fair-dice range mass counts"),
    (540, r"\((10, 15, 44, 51, 69)\)", r"\((10, 16, 44, 51, 69)\)", "correct the frozen Iris five-number summary"),
    (541, r"\((10, 14, 15, 16, 19)\)", r"\((10, 14, 15, 15.75, 19)\)", "correct the frozen Iris species-zero upper quartile"),
    (542, r"\((45, 51, 55.5, 59, 69)\)", r"\((45, 51, 55.5, 58.75, 69)\)", "correct the frozen Iris species-one upper quartile"),
    (545, r"\(\text{km}/\text{hr}\)", r"\(\text{km}/\text{s}\)", "correct the Michelson velocity unit"),
    (547, r"\((620, 805, 850, 895, 1071)\)", r"\((620, 807.5, 850, 892.5, 1070)\)", "correct the complete Michelson five-number summary"),
    (548, r"\((299\,620, 299\,805, 299\,850, 299\,895, 300\,071)\)", r"\((299\,620, 299\,807.5, 299\,850, 299\,892.5, 300\,070)\)", "correct the transformed Michelson summary"),
    (554, r"\((3, 5.5, 9, 14, 20)\)", r"\((3, 6.5, 9, 12, 20)\)", "correct the frozen red M-and-M summary"),
    (555, r"\((2, 5, 7, 9, 17)\)", r"\((2, 6, 7, 9, 17)\)", "correct the frozen green M-and-M summary"),
    (556, r"\((1, 4, 6.5, 10, 19)\)", r"\((1, 4, 6.5, 9.75, 19)\)", "correct the frozen blue M-and-M summary"),
    (557, r"\((0, 3.5, 6, 10.5, 13)\)", r"\((0, 4, 6, 9, 13)\)", "correct the frozen orange M-and-M summary"),
    (558, r"\((3, 8, 13.5, 18, 26)\)", r"\((3, 8.25, 13.5, 18, 26)\)", "correct the frozen yellow M-and-M summary"),
    (559, r"\((4, 8, 12.5, 18, 20)\)", r"\((4, 8, 12.5, 17.75, 20)\)", "correct the frozen brown M-and-M summary"),
    (560, r"\((50, 55.5, 58, 60, 61)\)", r"\((50, 56, 58, 58, 61)\)", "correct the M-and-M total-count summary"),
    (561, r"\((46.22, 48.28, 49.07, 50.23, 52.06)\)", r"\((46.22, 48.2925, 49.07, 50.175, 52.06)\)", "correct the M-and-M net-weight summary"),
    (562, r"\((0.08, 0.13, 0.17, 0.22, 0.39)\)", r"\((0.08, 0.1375, 0.17, 0.22, 0.39)\)", "correct the frozen Cicada overall summary"),
    (564, r"\((0.08, 0. 14, 0.18, 0.23, 0.31)\)", r"\((0.08, 0.1425, 0.18, 0.22, 0.31)\)", "correct the frozen Cicada species-one summary"),
    (565, r"\((0.12, 0.12, 0.215, 0.29, 0.39)\)", r"\((0.12, 0.1325, 0.215, 0.2825, 0.39)\)", "correct the frozen Cicada species-two summary"),
    (566, r"\((0.08, 0.17, 0.21, 0.25, 0.31)\)", r"\((0.08, 0.17, 0.21, 0.245, 0.31)\)", "correct the frozen female Cicada upper quartile"),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/sample/OrderStatistics.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in ORDER_STATISTICS_MATH_CORRECTIONS
)

COVARIANCE_RAW_TEX_CORRECTIONS = (
    (
        r"\sum_{i=1}^n [(x_i - m(\bs{x})][y_i - m(\bs{y})]",
        r"\sum_{i=1}^n [x_i - m(\bs{x})][y_i - m(\bs{y})]",
        "remove the unmatched opening parenthesis in the centered x factor",
    ),
    (
        r"= \frac{1}{2 n} \sum_{i=1}^n \sum_{j=1}^n [x_i - m(\bs{x}) + m(\bs{x}) - x_j][y_i - m(\bs{y}) + m(\bs{y}) - y_j]",
        r"= \sum_{i=1}^n \sum_{j=1}^n [x_i - m(\bs{x}) + m(\bs{x}) - x_j][y_i - m(\bs{y}) + m(\bs{y}) - y_j]",
        "remove the spurious one-over-2n factor from the pairwise-covariance expansion",
    ),
    (
        r"\left([(x_i - m(\bs{x})][y_i - m(\bs{y})]",
        r"\left([x_i - m(\bs{x})][y_i - m(\bs{y})]",
        "remove the unmatched opening parenthesis in the expanded pairwise sum",
    ),
    (
        r"\sum 2[y_i - (a + b x_i)] (-1)",
        r"\sum_{i=1}^n 2[y_i - (a + b x_i)] (-1)",
        "restore the missing limits on the derivative sum with respect to the intercept",
    ),
    (
        r"\sum 2[y_i - (a + b x_i)](-x_i)",
        r"\sum_{i=1}^n 2[y_i - (a + b x_i)](-x_i)",
        "restore the missing limits on the derivative sum with respect to the slope",
    ),
)

COVARIANCE_MATH_CORRECTIONS = (
    (
        69,
        r"\[ s(\bs{x}, \bs{y}) = \frac{1}{n - 1} \sum_{i=1}^n x_i \, y_i - \frac{n}{n - 1} m(\bs{x}) m(\bs{y}) = \frac{n}{n - 1} [m(\bs{x y}) - m(\bs{x}) m(\bs{y})] \]",
        r"\[ s(\bs{x}, \bs{y}) = \frac{1}{n - 1} \sum_{i=1}^n x_i \, y_i - \frac{n}{n - 1} m(\bs{x}) m(\bs{y}) = \frac{n}{n - 1} [m(\bs{x}\bs{y}) - m(\bs{x}) m(\bs{y})] \]",
        "use the product-vector notation defined immediately before the theorem",
    ),
    (74, r"\(\cov(\bs{x}, \bs{y})\)", r"\(s(\bs{x}, \bs{y})\)", "conclude with sample-covariance notation rather than the population operator"),
    (
        116,
        r"\[ \bs{u} = \frac{1}{s(\bs{x})}[\bs{x} - m(\bs{x})], \quad \bs{v} = \frac{1}{s(\bs{y})}[\bs{y} - m(\bs{y})] \]",
        r"\[ \bs{u} = \frac{1}{s(\bs{x})}[\bs{x} - m(\bs{x})\bs{1}], \quad \bs{v} = \frac{1}{s(\bs{y})}[\bs{y} - m(\bs{y})\bs{1}] \]",
        "subtract the mean times the all-ones vector rather than a scalar from a vector",
    ),
    (
        242,
        r"\(r^2(\bs{x}, \bs{y}) \sst(\bs{y}) = s^2(\bs{x}, \bs{y}) \big/ s^2(\bs{x})\)",
        r"\(r^2(\bs{x}, \bs{y}) \sst(\bs{y}) = (n - 1)s^2(\bs{x}, \bs{y}) \big/ s^2(\bs{x})\)",
        "restore the factor n-minus-one because SST equals (n-minus-one) times the sample variance",
    ),
    (
        245,
        r"\[ \ssr(\bs{x}, \bs{y}) = \sum_{i=1}^n [\hat{y}_i - m(\bs{y})]^2 = \frac{s^2(\bs{x}, \bs{y})}{s^2(\bs{x})} \]",
        r"\[ \ssr(\bs{x}, \bs{y}) = \sum_{i=1}^n [\hat{y}_i - m(\bs{y})]^2 = (n - 1)\frac{s^2(\bs{x}, \bs{y})}{s^2(\bs{x})} \]",
        "restore the factor n-minus-one in the regression sum of squares",
    ),
    (290, r"\(\cor[(M(\bs{X}), M(\bs{Y})] = \rho\)", r"\(\cor[M(\bs{X}), M(\bs{Y})] = \rho\)", "remove the unmatched parenthesis in the sample-means correlation"),
    (
        309,
        r"\[ \cov[(X - \mu)^2 (Y - \nu)^2] = \E[(X - \mu)^2 (Y - \nu)^2] - \E[(X - \mu)^2] \E[(Y - \nu)^2] = \delta_2 - \sigma^2 \tau^2 \]",
        r"\[ \cov[(X - \mu)^2, (Y - \nu)^2] = \E[(X - \mu)^2 (Y - \nu)^2] - \E[(X - \mu)^2] \E[(Y - \nu)^2] = \delta_2 - \sigma^2 \tau^2 \]",
        "separate the two covariance arguments with a comma",
    ),
    (357, r"\([(X_i - M(\bs{X})][Y_i - M(\bs{Y})]\)", r"\([X_i - M(\bs{X})][Y_i - M(\bs{Y})]\)", "remove the unmatched opening parenthesis in the centered product"),
    (392, r"\(R(\bs{X}, \bs{Y}) \to \delta / \sigma \tau = \rho\)", r"\(R(\bs{X}, \bs{Y}) \to \delta / (\sigma \tau) = \rho\)", "make the product in the correlation denominator explicit"),
    (
        396,
        r"\[ \var[S(\bs{X}), \bs{Y})] = \frac{1}{4 n^2 (n - 1)^2} \sum_{i=1}^n \sum_{j=1}^n \sum_{k=1}^n \sum_{l=1}^n \cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] \]",
        r"\[ \var[S(\bs{X}, \bs{Y})] = \frac{1}{4 n^2 (n - 1)^2} \sum_{i=1}^n \sum_{j=1}^n \sum_{k=1}^n \sum_{l=1}^n \cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] \]",
        "place both sample vectors inside the sample-covariance statistic",
    ),
    (
        423,
        r"\(\E\{[Y - L(Y \mid X)]\} = \var(Y)[1 - \cor^2(X, Y)] = r^2 (1 - \rho^2)\)",
        r"\(\E\{[Y - L(Y \mid X)]^2\} = \var(Y)[1 - \cor^2(X, Y)] = \tau^2 (1 - \rho^2)\)",
        "square the prediction error and use the declared population standard deviation",
    ),
    (473, r"\(m = 45&deg;\)", r"\((45, 100)\)", "give both sample means after the Celsius conversion"),
    (474, r"\(s = 10&deg;\)", r"\((10, 10)\)", "give both sample standard deviations after the Celsius conversion"),
    (488, r"\(m = 25.4\)", r"\((25.4, 10.16)\)", "give both sample means after the centimetre conversion"),
    (489, r"\(s = 5.08\)", r"\((5.08, 2.54)\)", "give both sample standard deviations after the centimetre conversion"),
    (699, r"\(14/3\)", r"\(21/5\)", "divide the squared-x-deviation total by all ten observations in the row labelled mean"),
    (700, r"\(16/9\)", r"\(8/5\)", "divide the squared-y-deviation total by all ten observations in the row labelled mean"),
    (701, r"\(8/3\)", r"\(12/5\)", "divide the cross-deviation total by all ten observations in the row labelled mean"),
    (704, r"\(96/7\)", r"\(48/35\)", "divide the fitted-deviation-square total by all ten observations in the row labelled mean"),
    (706, r"\(2/7\)", r"\(8/35\)", "divide the residual-square total by all ten observations in the row labelled mean"),
    (
        740,
        r"\(\left((X_1, Y_1), (X_2, Y_2), \ldots (X_9, Y_9)\right)\)",
        r"\(\left((X_1, Y_1), (X_2, Y_2), \ldots, (X_9, Y_9)\right)\)",
        "restore the missing separator in the random-sample sequence",
    ),
    (771, r"\(5935/21\,676\,032\)", r"\(5939/21\,676\,032\)", "use the exact symbolic variance of the sample variance for the frozen density"),
    (782, r"\(r = 0.793\)", r"\(r \approx 0.794\)", "round the frozen M-and-M correlation correctly"),
    (783, r"\(r^2 = 0.629\)", r"\(r^2 \approx 0.630\)", "round the frozen M-and-M coefficient of determination correctly"),
    (784, r"\(y = 20.278 + 0.507 x\)", r"\(y \approx 20.278 + 0.507 x\)", "mark the rounded M-and-M regression coefficients as approximate"),
    (785, r"\(r = -0.849\)", r"\(r \approx -0.850\)", "exclude the aggregate footer from the state-level SAT correlation and round correctly"),
    (786, r"\(r^2 = 0.721\)", r"\(r^2 \approx 0.722\)", "exclude the aggregate footer from the state-level SAT coefficient of determination"),
    (787, r"\(y = 1141.5 - 2.1 x\)", r"\(y \approx 1141.854 - 2.094 x\)", "fit the state-level SAT regression without the aggregate footer"),
    (788, r"\(r = 0.614\)", r"\(r \approx 0.614\)", "mark the rounded all-student SAT correlation as approximate"),
    (789, r"\(r^2 = 0.377\)", r"\(r^2 \approx 0.377\)", "mark the rounded all-student SAT coefficient of determination as approximate"),
    (790, r"\(y = 321.5 + 0.3 \, x\)", r"\(y \approx 321.503 + 0.356 \, x\)", "use the exact all-student math-on-verbal SAT regression"),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/sample/Covariance.html",
        "old": old,
        "new": new,
        "replacements": 1,
        "surface": "raw_tex",
        "reason": reason,
    }
    for old, new, reason in COVARIANCE_RAW_TEX_CORRECTIONS
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/sample/Covariance.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in COVARIANCE_MATH_CORRECTIONS
)

NORMAL_MATH_CORRECTIONS = (
    (
        196,
        r"\(\E\left[(M(\bs{X}) - M(\bs{Y})\right] = \mu - \nu\)",
        r"\(\E\left[M(\bs{X}) - M(\bs{Y})\right] = \mu - \nu\)",
        "remove the unmatched parenthesis from the mean of the sample-mean difference",
    ),
    (
        197,
        r"\(\var\left[(M(\bs{X}) - M(\bs{Y})\right] = \sigma^2 / m + \tau^2 / n\)",
        r"\(\var\left[M(\bs{X}) - M(\bs{Y})\right] = \sigma^2 / m + \tau^2 / n\)",
        "remove the unmatched parenthesis from the variance of the sample-mean difference",
    ),
    (
        198,
        r"\[ Z = \frac{\left[(M(\bs{X}) - M(\bs{Y})\right] - (\mu - \nu)}{\sqrt{\sigma^2 / m + \tau^2 / n}} \]",
        r"\[ Z = \frac{\left[M(\bs{X}) - M(\bs{Y})\right] - (\mu - \nu)}{\sqrt{\sigma^2 / m + \tau^2 / n}} \]",
        "remove the unmatched parenthesis from the standardized sample-mean difference",
    ),
    (
        266,
        r"\((M(\bs{Y}, S(\bs{Y}))\)",
        r"\((M(\bs{Y}), S(\bs{Y}))\)",
        "separate the Y-sample mean and standard deviation as a pair",
    ),
    (
        275,
        r"\(Z / \sqrt{V / (m + n - 2}\)",
        r"\(Z / \sqrt{V / (m + n - 2)}\)",
        "close the denominator in the pooled two-sample Student construction",
    ),
    (
        286,
        r"\(\rho \in [0, 1]\)",
        r"\(\rho \in [-1, 1]\)",
        "include negative correlations in the bivariate-normal parameter range",
    ),
    (
        299,
        r"\(\sigma^3 = \E\left[(X - \mu)^3\right] = 0\)",
        r"\(\sigma_3 = \E\left[(X - \mu)^3\right] = 0\)",
        "use the declared third-central-moment subscript notation",
    ),
    (
        305,
        r"\(((X_1, Y_1), (X_2, Y_2), \ldots (X_n, Y_n))\)",
        r"\(((X_1, Y_1), (X_2, Y_2), \ldots, (X_n, Y_n))\)",
        "restore the missing separator in the bivariate sample vector",
    ),
    (
        355,
        r"\(\P(M \gt 49, S^2 \lt 20))\)",
        r"\(\P(M \gt 49, S^2 \lt 20)\)",
        "remove the extra closing parenthesis from the joint probability",
    ),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/sample/Normal.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in NORMAL_MATH_CORRECTIONS
)

ESTIMATORS_MATH_CORRECTIONS = (
    (
        67,
        r"\( \theta \in \Theta \)",
        r"\( \theta \in T \)",
        "quantify over the declared parameter space T rather than undefined Theta",
    ),
    (
        69,
        r"\(\bias(U) = E(U - \theta) = \E(U) - \theta \)",
        r"\(\bias(U) = \E(U - \theta) = \E(U) - \theta \)",
        "use the page's declared expectation macro consistently",
    ),
    (
        117,
        r"\(\bs{X} = (X_1, X_2, \ldots,)\)",
        r"\(\bs{X} = (X_1, X_2, \ldots)\)",
        "remove the stray comma after the sequence ellipsis",
    ),
    (
        162,
        r"\[ |\E(U_n - \theta)| \le \E(|U_n - \theta|) \le \sqrt{\E[(U_n - \theta)]^2} \to 0 \text{ as } n \to \infty \]",
        r"\[ |\E(U_n - \theta)| \le \E(|U_n - \theta|) \le \sqrt{\E[(U_n - \theta)^2]} \to 0 \text{ ketika } n \to \infty \]",
        "put the squared error inside the expectation and localize the connective",
    ),
    (
        197,
        r"\( (\P_n(A): n \in \N_+) \)",
        r"\( (P_n(A): n \in \N_+) \)",
        "use the empirical-probability notation defined earlier in the sentence",
    ),
    (
        272,
        r"\( T \)",
        r"\( [0, \infty) \)",
        "allow the nonnegative values required for sample standard deviation",
    ),
    (
        280,
        r"\( \var(U) \gt 0 \)",
        r"\( \var(U) \ge 0 \)",
        "do not infer strict variance from a multipoint parameter space",
    ),
    (
        281,
        r"\( [\E(U)]^2 \lt \theta^2 \)",
        r"\( [\E(U)]^2 \le \theta^2 \)",
        "derive the weak inequality needed for negative bias",
    ),
    (
        282,
        r"\( \E(U) \lt \theta \)",
        r"\( \E(U) \le \theta \)",
        "state weak negative bias without an unproved strictness condition",
    ),
    (
        305,
        r"\( \rho \in [0, 1] \)",
        r"\( \rho \in [-1, 1] \)",
        "include valid negative correlations",
    ),
    (350, r"\(U_n\)", r"\(W_n\)", "name the covariance estimator proved above"),
    (351, r"\(V_n\)", r"\(S_n\)", "name the sample covariance estimator proved above"),
    (357, r"\(V_n\)", r"\(S_n\)", "name the sample covariance estimator in the asymptotic comparison"),
    (358, r"\(U_n\)", r"\(W_n\)", "name the known-means covariance estimator in the asymptotic comparison"),
    (
        404,
        r"\( n \in \N \)",
        r"\( n \in \N_+ \)",
        "exclude the zero-sized sample from the positive sample-size sequence",
    ),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/point/Estimators.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in ESTIMATORS_MATH_CORRECTIONS
)

MOMENTS_MATH_CORRECTIONS = (
    (
        133,
        r"\( \W_n^2 \)",
        r"\( W_n^2 \)",
        "remove the undefined W macro from the known-mean variance proof",
    ),
    (
        214,
        r"\(n \in \{2, 3, \ldots, \}\)",
        r"\(n \in \{2, 3, \ldots\}\)",
        "remove the empty trailing entry from the sample-size set",
    ),
    (
        386,
        r"\( E(U_p) = \frac{p}{1 - p} \E(M)\)",
        r"\( \E(U_p) = \frac{p}{1 - p} \E(M)\)",
        "use the declared expectation macro consistently",
    ),
    (
        389,
        r"\( \var(M) = \frac{1}{n} \var(X) = \frac{1 - p}{n p^2} \)",
        r"\( \var(M) = \frac{1}{n} \var(X) = \frac{k(1 - p)}{n p^2} \)",
        "restore the missing negative-binomial shape factor",
    ),
    (
        445,
        r"\( \var(V_k) = b^2 / k n \)",
        r"\( \var(V_k) = \frac{b^2}{k n} \)",
        "group the gamma-estimator variance denominator unambiguously",
    ),
    (
        452,
        r"\(\var(V_k) = \var(M) / k^2 = k b ^2 / (n k^2) = b^2 / k n\)",
        r"\(\var(V_k) = \var(M) / k^2 = k b ^2 / (n k^2) = \frac{b^2}{k n}\)",
        "apply the same gamma-estimator denominator repair in the proof",
    ),
    (
        512,
        r"\[ U = \frac{2 M^{(2)}}{1 - 4 M^{(2)}} \]",
        r"\[ U = \frac{1 - 2 M^{(2)}}{4 M^{(2)} - 1} \]",
        "solve the symmetric-beta second-moment equation correctly",
    ),
    (
        519,
        r"\( (b, \infty) \)",
        r"\( [b, \infty) \)",
        "make the Pareto support agree with the displayed density",
    ),
    (
        583,
        r"\[ U = 2 M - \sqrt{3} T, \quad V = 2 \sqrt{3} T \]",
        r"\[ U = M - \sqrt{3} T, \quad V = 2 \sqrt{3} T \]",
        "correct the two-parameter uniform location estimator",
    ),
    (
        592,
        r"\( V \)",
        r"\( V_a \)",
        "name the Pareto scale estimator actually under discussion",
    ),
    (
        621,
        r"\( P(X_i = 1) = r / N \)",
        r"\( \P(X_i = 1) = r / N \)",
        "use the page's declared probability macro",
    ),
    (
        627,
        r"\[ P(Y = y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, N - n + r\}, \ldots, \min\{n, r\}\} \]",
        r"\[ \P(Y = y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, n - N + r\}, \ldots, \min\{n, r\}\} \]",
        "use the declared probability macro and correct the hypergeometric support lower bound",
    ),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/point/Moments.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in MOMENTS_MATH_CORRECTIONS
)

LIKELIHOOD_MATH_CORRECTIONS = (
    (
        95,
        r"\[ \hat{L}_\bs{x}(\lambda) = \max\left\{L_\bs{x}(\theta): \theta \in h^{-1}\{\lambda\} \right\}; \quad \lambda \in \Lambda \]",
        r"\[ \hat{L}_\bs{x}(\lambda) = \sup\left\{L_\bs{x}(\theta): \theta \in h^{-1}\{\lambda\} \right\}, \quad \lambda \in \Lambda \]",
        "make the noninjective profile likelihood well-defined without assuming fiberwise attainment",
    ),
    (
        120,
        r"\[ M_2 = \frac{1}{n} \sum_{i=1}^n X_i^2 \]",
        r"\[ M^{(2)} = \frac{1}{n} \sum_{i=1}^n X_i^2 \]",
        "use the edition's established notation for the second sample moment",
    ),
    (
        137,
        r"\( (0, 1) \)",
        r"\( [0, 1] \)",
        "include the Bernoulli boundary values required for an MLE on every sample",
    ),
    (
        146,
        r"\[ \frac{d^2}{d p^2} \ln L_{\bs{x}}(p) = -\frac{y}{p^2} - \frac{n - 1}{(1 - p)^2} \lt 0 \]",
        r"\[ \frac{d^2}{d p^2} \ln L_{\bs{x}}(p) = -\frac{y}{p^2} - \frac{n - y}{(1 - p)^2} \lt 0 \]",
        "restore the failure-count factor in the Bernoulli second derivative",
    ),
    (
        162,
        r"\(L_{\bs{x}}\left(\frac{1}{2}\right) = \left(\frac{1}{2}\right)^y\)",
        r"\(L_{\bs{x}}\left(\frac{1}{2}\right) = \left(\frac{1}{2}\right)^n\)",
        "correct the restricted Bernoulli likelihood at one half",
    ),
    (
        198,
        r"\(p \in (0, 1)\)",
        r"\(p \in [0, 1]\)",
        "align the Bernoulli variance exercise with the closed parameter space",
    ),
    (
        202,
        r"\(\N_+\)",
        r"\(\mathbb{N}_+\)",
        "replace the undefined positive-integer macro in the geometric support",
    ),
    (
        204,
        r"\[ g(x) = p (1 - p)^{x-1}, \quad x \in \N_+ \]",
        r"\[ g(x) = p (1 - p)^{x-1}, \quad x \in \mathbb{N}_+ \]",
        "replace the undefined positive-integer macro in the geometric density",
    ),
    (
        210,
        r"\( x \in \N_+ \)",
        r"\( x \in \mathbb{N}_+ \)",
        "replace the undefined positive-integer macro in the geometric proof",
    ),
    (
        211,
        r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \in \N_+^n \)",
        r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \in \mathbb{N}_+^n \)",
        "replace the undefined positive-integer macro in the geometric sample space",
    ),
    (
        214,
        r"\[ \frac{d}{dp} \ln L(p) = \frac{n}{p} - \frac{y - n}{1 - p} \]",
        r"\[ \frac{d}{dp} \ln L_{\bs{x}}(p) = \frac{n}{p} - \frac{y - n}{1 - p} \]",
        "restore the data subscript on the geometric log-likelihood",
    ),
    (
        222,
        r"\[ g(x) = \binom{x + k - 1}{k - 1} p^k (1 - p)^x, \quad x \in \N \]",
        r"\[ g(x) = \frac{\Gamma(x + k)}{\Gamma(k)\,x!} p^k (1 - p)^x, \quad x \in \N \]",
        "make the negative-binomial coefficient unambiguous for noninteger positive shape",
    ),
    (
        234,
        r"\( \ln g(x) = \ln \binom{x + k - 1}{k - 1} + k \ln p + x \ln(1 - p) \)",
        r"\( \ln g(x) = \ln \Gamma(x + k) - \ln \Gamma(k) - \ln(x!) + k \ln p + x \ln(1 - p) \)",
        "use the same gamma-function coefficient in the negative-binomial log-density",
    ),
    (
        239,
        r"\( C = \sum_{i=1}^n \ln \binom{x_i + k - 1}{k - 1} \)",
        r"\( C = \sum_{i=1}^n [\ln \Gamma(x_i + k) - \ln \Gamma(k) - \ln(x_i!)] \)",
        "use the same gamma-function coefficient in the negative-binomial constant",
    ),
    (
        290,
        r"\[ \frac{\partial^2}{\partial \mu^2} \ln L_\bs{x}(m, t^2) = -n / t^2, \; \frac{\partial^2}{\partial \mu \partial \sigma^2} \ln L_\bs{x}(m, t^2) = 0, \; \frac{\partial^2}{\partial (\sigma^2)^2} \ln L_\bs{x}(m, t^2) = -n / t^4\]",
        r"\[ \frac{\partial^2}{\partial \mu^2} \ln L_\bs{x}(m, t^2) = -n / t^2, \; \frac{\partial^2}{\partial \mu \partial \sigma^2} \ln L_\bs{x}(m, t^2) = 0, \; \frac{\partial^2}{\partial (\sigma^2)^2} \ln L_\bs{x}(m, t^2) = -n / (2 t^4)\]",
        "restore the missing one-half factor in the normal Hessian",
    ),
    (
        323,
        r"\( b = y / n k = 1 / k m \)",
        r"\( b = \frac{y}{n k} = \frac{m}{k} \)",
        "group the gamma scale critical value unambiguously",
    ),
    (
        325,
        r"\( b = y / n k \)",
        r"\( b = \frac{y}{n k} \)",
        "group the repeated gamma scale critical value unambiguously",
    ),
    (
        351,
        r"\( x \in (0, \infty) \)",
        r"\( x \in (0, 1) \)",
        "correct the beta distribution support",
    ),
    (
        352,
        r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \in (0, \infty)^n \)",
        r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \in (0, 1)^n \)",
        "correct the beta sample-data domain",
    ),
    (
        362,
        r"\(U = M (M - M_2) \big/ (M_2 - M^2)\)",
        r"\(U = M (M - M^{(2)}) \big/ (M^{(2)} - M^2)\)",
        "keep the beta method-of-moments comparison notation consistent",
    ),
    (
        401,
        r"\[ 1 + \sqrt{\frac{M_2}{M_2 - M^2}}, \; \frac{M_2}{M} \left(1 - \sqrt{\frac{M_2 - M^2}{M_2}}\right)\]",
        r"\[ 1 + \sqrt{\frac{M^{(2)}}{M^{(2)} - M^2}}, \; \frac{M^{(2)}}{M} \left(1 - \sqrt{\frac{M^{(2)} - M^2}{M^{(2)}}}\right)\]",
        "keep the Pareto method-of-moments comparison notation consistent",
    ),
    (
        438,
        r"\( i \in \{1, 2, \ldots n\} \)",
        r"\( i \in \{1, 2, \ldots, n\} \)",
        "restore the missing separator in the uniform index set",
    ),
    (
        451,
        r"\[ \frac{\var(U)}{\var(V)} = \frac{h^2 / 3 n}{h^2 / n (n + 2)} = \frac{n + 2}{3} \to \infty \text{ as } n \to \infty \]",
        r"\[ \frac{\var(U)}{\var(V)} = \frac{h^2/(3n)}{h^2/[n(n + 2)]} = \frac{n + 2}{3} \to \infty \text{ ketika } n \to \infty \]",
        "group the variance ratio unambiguously and localize its limit phrase",
    ),
    (
        478,
        r"\(a\)",
        r"\(h\)",
        "name the actual scale parameter in the uniform simulation exercise",
    ),
    (
        491,
        r"\( \bs{x} = (x_1, x_2, \ldots, x_n\} \)",
        r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \)",
        "close the uniform data vector with the correct delimiter",
    ),
    (
        506,
        r"\[ U = 2 M - \sqrt{3} T, \quad V = 2 \sqrt{3} T \]",
        r"\[ U = M - \sqrt{3} T, \quad V = 2 \sqrt{3} T \]",
        "correct the two-parameter uniform location moment estimator",
    ),
    (
        508,
        r"\( T = \frac{1}{n} \sum_{i=1}^n (X_i - M)^2 \)",
        r"\( T^2 = \frac{1}{n} \sum_{i=1}^n (X_i - M)^2 \)",
        "identify the biased sample variance as T squared rather than T",
    ),
    (
        513,
        r"\( E(U) = a + \frac{h}{n + 1} \)",
        r"\( \E(U) = a + \frac{h}{n + 1} \)",
        "use the declared expectation macro for the uniform location estimator",
    ),
    (
        515,
        r"\( E(V) = h \frac{n - 1}{n + 1} \)",
        r"\( \E(V) = h \frac{n - 1}{n + 1} \)",
        "use the declared expectation macro for the uniform scale estimator",
    ),
    (
        541,
        r"\( P(X_i = 1) = r / N \)",
        r"\( \P(X_i = 1) = r / N \)",
        "use the declared probability macro in the hypergeometric setup",
    ),
    (
        547,
        r"\[ P(Y = y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, N - n + r\}, \ldots, \min\{n, r\}\} \]",
        r"\[ \P(Y = y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, n - N + r\}, \ldots, \min\{n, r\}\} \]",
        "use the probability macro and correct the hypergeometric support lower bound",
    ),
    (
        556,
        r"\( U = \lfloor N M \rfloor = \lfloor N Y / n \rfloor \)",
        r"\( U = \min\{N, \lfloor (N + 1)Y / n \rfloor\} \)",
        "correct the known-population hypergeometric maximum-likelihood selector",
    ),
    (
        567,
        r"\[ L_{\bs{x}}(r) = \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad r \in \{y, \ldots, \min\{n, y + N - n\}\}  \]",
        r"\[ L_{\bs{x}}(r) = \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad r \in \{y, \ldots, N - n + y\} \]",
        "correct the feasible type-one population-size domain",
    ),
    (
        570,
        r"\( r \lt N y / n \)",
        r"\( r \lt (N + 1)y / n \)",
        "correct the adjacent-likelihood comparison for the type-one size",
    ),
    (
        572,
        r"\( r = \lfloor N y / n \rfloor \)",
        r"\( r = \min\{N, \lfloor (N + 1)y / n \rfloor\} \)",
        "apply the corrected hypergeometric mode selector in the proof",
    ),
    (
        580,
        r"\( L_{\bs{x}}(r) \)",
        r"\( L_{\bs{x}}(N) \)",
        "name the population-size likelihood being maximized",
    ),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/point/Likelihood.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in LIKELIHOOD_MATH_CORRECTIONS
)

BAYES_MATH_CORRECTIONS = (
    (
        49,
        r"\( h(\theta \mid x) = h(\theta) f(\bs x \mid \theta) / f(\bs x) \)",
        r"\( h(\theta \mid \bs x) = h(\theta) f(\bs x \mid \theta) / f(\bs x) \)",
        "use the sample vector consistently in the posterior-density identity",
    ),
    (
        123,
        r"\( u \mapsto \E[(\Theta - u)^2 \mid \bs X = \bs x) \)",
        r"\( u \mapsto \E[(\Theta - u)^2 \mid \bs X = \bs x] \)",
        "close the conditional posterior-risk expression with the matching bracket",
    ),
    (
        206,
        r"\( E(Y_n \mid p) = n p \)",
        r"\( \E(Y_n \mid p) = n p \)",
        "use the page's declared expectation macro",
    ),
    (
        238,
        r"\(U\)",
        r"\(U_n\)",
        "restore the estimator index in the constant-MSE discussion",
    ),
    (
        250,
        r"\[ M_n = \frac{Y}{n} = \frac{1}{n} \sum_{i=1}^n X_i \]",
        r"\[ M_n = \frac{Y_n}{n} = \frac{1}{n} \sum_{i=1}^n X_i \]",
        "restore the indexed Bernoulli success count",
    ),
    (
        299,
        r"\( U_n = E(P \mid \bs{X}_n) \)",
        r"\( U_n = \E(P \mid \bs{X}_n) \)",
        "use the page's declared expectation macro",
    ),
    (
        304,
        r"\( U = 1 \cdot 0 + \frac{1}{2} \cdot 1 = \frac{1}{2} \)",
        r"\( U_n = 1 \cdot 0 + \frac{1}{2} \cdot 1 = \frac{1}{2} \)",
        "restore the estimator index in the two-point Bernoulli rule",
    ),
    (
        317,
        r"\( \bias(U_n \mid p) = E(U - p \mid p) \)",
        r"\( \bias(U_n \mid p) = \E(U_n - p \mid p) \)",
        "use the expectation macro and the indexed estimator in the bias definition",
    ),
    (
        376,
        r"\(Y - n\)",
        r"\(Y_n - n\)",
        "restore the indexed geometric failure count",
    ),
    (
        448,
        r"\[ \mse(V \mid \lambda) ",
        r"\[ \mse(V_n \mid \lambda) ",
        "restore the estimator index in the Poisson MSE decomposition",
    ),
    (
        484,
        r"\( \bs x = (x_1, x_2, \ldots, x_n) \in \R \)",
        r"\( \bs x = (x_1, x_2, \ldots, x_n) \in \R^n \)",
        "put the normal data vector in its n-dimensional sample space",
    ),
    (
        535,
        r"\(\mse(U \mid \mu)",
        r"\(\mse(U_n \mid \mu)",
        "restore the estimator index in the special-case normal MSE",
    ),
    (
        540,
        r"\(\var(M) = \sigma^2 / n\)",
        r"\(\mse(M_n \mid \mu) = \var(M_n \mid \mu) = \sigma^2 / n\)",
        "identify the indexed sample mean and its equal MSE and variance",
    ),
    (
        618,
        r"\(U\)",
        r"\(U_n\)",
        "restore the estimator index in the Pareto comparison",
    ),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/point/Bayes.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in BAYES_MATH_CORRECTIONS
)

PROTECTED_MATH_CORRECTIONS += (
    {
        "page": "random/point/Bayes.html",
        "old": r"\bias(U \mid p)",
        "new": r"\bias(U_n \mid p)",
        "replacements": 1,
        "surface": "raw_math_environment",
        "reason": "restore the indexed estimator in the raw bias derivation",
    },
    {
        "page": "random/point/Bayes.html",
        "old": r"\P(Y = n \mid p)",
        "new": r"\P(Y_n = n \mid p)",
        "replacements": 1,
        "surface": "raw_math_environment",
        "reason": "restore the indexed success count in the raw bias derivation",
    },
    {
        "page": "random/point/Bayes.html",
        "old": r"\P(Y \lt n \mid p)",
        "new": r"\P(Y_n \lt n \mid p)",
        "replacements": 1,
        "surface": "raw_math_environment",
        "reason": "restore the indexed success count in the complementary raw event",
    },
)

UNBIASED_MATH_CORRECTIONS = (
    (
        68,
        r"\E\left[h(\bs{X})\right]",
        r"\E_\theta\left[h(\bs{X})\right]",
        "retain the theta subscript on the expectation differentiated under the model",
    ),
    (
        98,
        r"\E_\theta\left[L^2(\bs{X}, \theta)\right]",
        r"\E_\theta\left[L_1^2(\bs{X}, \theta)\right]",
        "identify the squared score rather than an undefined unsubscripted L",
    ),
    (
        115,
        r"\(L^2\)",
        r"\(L_1^2\)",
        "identify the squared full-sample score in the random-sample decomposition",
    ),
    (
        119,
        r"\E_\theta\left[L^2(\bs{X}, \theta)\right]",
        r"\E_\theta\left[L_1^2(\bs{X}, \theta)\right]",
        "identify the squared full-sample score in the Fisher-information identity",
    ),
    (
        169,
        r"\exp\left[-\left[\frac{x - \mu}{\sigma}\right]^2 \right]",
        r"\exp\left[-\frac{1}{2}\left[\frac{x - \mu}{\sigma}\right]^2 \right]",
        "restore the missing one-half factor in the normal density exponent",
    ),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/point/Unbiased.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in UNBIASED_MATH_CORRECTIONS
)

PROTECTED_MATH_CORRECTIONS += (
    {
        "page": "random/point/Unbiased.html",
        "old": r"\int_S \frac{d}{d \theta} h(\bs{x}) f_\theta(\bs{x}) \, d \bs{x}",
        "new": r"\int_S \frac{d}{d \theta}\left[h(\bs{x}) f_\theta(\bs{x})\right] \, d \bs{x}",
        "replacements": 1,
        "surface": "raw_math_environment",
        "environment_index": 2,
        "reason": "differentiate the bracketed product under the integral rather than h alone",
    },
)

# The admitted Sufficient page contains a bounded set of proved formula and
# notation defects.  These are indexed against the frozen authority's
# protected-TeX stream so the reader and verifier agree on every correction.
SUFFICIENT_MATH_CORRECTIONS = (
    (88, r"\( C \)", r"\( c(y) \)", "replace the factorization constant with the required data-only positive function"),
    (89, r"\( h_\theta(y) = C G(y, \theta) \)", r"\( h_\theta(y) = c(y) G(y, \theta) \)", "use the data-only positive factor consistently"),
    (92, r"\( f_\theta(\bs x) \big/ h_\theta[u(x)] = r(\bs x) / C\)", r"\( f_\theta(\bs x) \big/ h_\theta[u(\bs{x})] = r(\bs x) / c[u(\bs{x})]\)", "correct the vector argument and data-only denominator in the factorization proof"),
    (150, r"\( \theta \in \Theta \)", r"\( \theta \in T \)", "use the page's declared parameter-space symbol"),
    (229, r"\(\theta \in \Theta\)", r"\(\theta \in T\)", "use the page's declared parameter-space symbol"),
    (331, r"\[\E[r(Y)] = \sum_{y=0}^n r(y) \binom{n}{k} p^y (1 - p)^{n-y} = (1 - p)^n \sum_{y=0}^n r(y) \binom{n}{y} \left(\frac{p}{1 - p}\right)^y\]", r"\[\E[r(Y)] = \sum_{y=0}^n r(y) \binom{n}{y} p^y (1 - p)^{n-y} = (1 - p)^n \sum_{y=0}^n r(y) \binom{n}{y} \left(\frac{p}{1 - p}\right)^y\]", "the summation variable is y, not the undefined k"),
    (404, r"\[ f(\bs x) = g(x_1) g(x_2) \cdot g(x_n) = \frac{e^{-n \theta} \theta^y}{x_1! x_2! \cdots x_n!}, \quad \bs x = (x_1, x_2, \ldots, x_n) \in \N^n \]", r"\[ f(\bs x) = g(x_1) g(x_2) \cdots g(x_n) = \frac{e^{-n \theta} \theta^y}{x_1! x_2! \cdots x_n!}, \quad \bs x = (x_1, x_2, \ldots, x_n) \in \N^n \]", "restore the omitted product factors"),
    (460, r"\[ f(\bs x) = g(x_1) g(x_2) \cdots g(x_n) = \frac{1}{(2 \pi)^{n/2} \sigma^n} \exp\left[-\frac{1}{2 \sigma^2} \sum_{i=1}^n (x_i - \mu)^2\right], \quad \bs x = (x_1, x_2 \ldots, x_n) \in \R^n \]", r"\[ f(\bs x) = g(x_1) g(x_2) \cdots g(x_n) = \frac{1}{(2 \pi)^{n/2} \sigma^n} \exp\left[-\frac{1}{2 \sigma^2} \sum_{i=1}^n (x_i - \mu)^2\right], \quad \bs x = (x_1, x_2, \ldots, x_n) \in \R^n \]", "repair the tuple punctuation"),
    (461, r"\[ f(\bs x) = \frac{1}{(2 \pi)^{n/2} \sigma^n} e^{-n \mu^2 / \sigma^2} \exp\left(-\frac{1}{2 \sigma^2}  \sum_{i=1}^n x_i^2 + \frac{2 \mu}{\sigma^2} \sum_{i=1}^n x_i \right), \quad \bs x = (x_1, x_2 \ldots, x_n) \in \R^n\]", r"\[ f(\bs x) = \frac{1}{(2 \pi)^{n/2} \sigma^n} e^{-n \mu^2 / (2 \sigma^2)} \exp\left(-\frac{1}{2 \sigma^2}  \sum_{i=1}^n x_i^2 + \frac{\mu}{\sigma^2} \sum_{i=1}^n x_i \right), \quad \bs x = (x_1, x_2, \ldots, x_n) \in \R^n\]", "restore the missing normal expansion factors and tuple punctuation"),
    (586, r"\( \bs{Z} = (Z_1, X_2, \ldots, Z_n) \)", r"\( \bs{Z} = (Z_1, Z_2, \ldots, Z_n) \)", "use the defined transformed variable Z_2"),
    (617, r"\( (U, V) \)", r"\( (P, Q) \)", "match the beta sufficient-statistic names defined in the theorem"),
    (658, r"\[ f(\bs x) = g(x_1) g(x_2) \cdots g(x_n) = \frac{a^n b^{n a}}{(x_1 x_2 \cdots x_n)^{a + 1}} \bs{1}\left(x_{(n)} \ge b\right), \quad (x_1, x_2, \ldots, x_n) \in (0, \infty)^n  \]", r"\[ f(\bs x) = g(x_1) g(x_2) \cdots g(x_n) = \frac{a^n b^{n a}}{(x_1 x_2 \cdots x_n)^{a + 1}} \bs{1}\left(x_{(1)} \ge b\right), \quad (x_1, x_2, \ldots, x_n) \in (0, \infty)^n  \]", "the Pareto support is determined by the sample minimum"),
    (669, r"\( M^{(2)} = \sum_{i=1}^n X_i^2 \)", r"\( M^{(2)} = \frac{1}{n} \sum_{i=1}^n X_i^2 \)", "use the stated second sample moment rather than the unnormalised sum"),
    (690, r"\[ f(\bs x) = g(x_1) g(x_2) \cdots g(x_n) = \frac{1}{h^n}, \quad \bs x = (x_1, x_2, \ldots x_n) \in [a, a + h]^n \]", r"\[ f(\bs x) = g(x_1) g(x_2) \cdots g(x_n) = \frac{1}{h^n}, \quad \bs x = (x_1, x_2, \ldots, x_n) \in [a, a + h]^n \]", "repair the tuple punctuation"),
    (726, r"\( h \)", r"\( a \)", "the sentence concerns the location parameter a"),
    (747, r"\[ h(y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, N - n + r\}, \ldots, \min\{n, r\}\} \]", r"\[ h(y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, n - N + r\}, \ldots, \min\{n, r\}\} \]", "correct the lower support bound for sampling without replacement"),
    (751, r"\( y \in \{\max\{0, N - n + r\}, \ldots, \min\{n, r\}\} \)", r"\( y \in \{\max\{0, n - N + r\}, \ldots, \min\{n, r\}\} \)", "correct the lower support bound in the conditional-distribution statement"),
    (759, r"\( y \in \{\max\{0, N - n + r\}, \ldots, \min\{n, r\}\} \)", r"\( y \in \{\max\{0, n - N + r\}, \ldots, \min\{n, r\}\} \)", "correct the repeated lower support bound"),
)

PROTECTED_MATH_CORRECTIONS += tuple(
    {
        "page": "random/point/Sufficient.html",
        "old": old,
        "new": new,
        "span_old": old,
        "span_new": new,
        "span_index": span_index,
        "replacements": 1,
        "surface": "math_span",
        "reason": reason,
    }
    for span_index, old, new, reason in SUFFICIENT_MATH_CORRECTIONS
)

# Reader-facing language inside TeX \text{...} remains protected mathematics:
# these exact substitutions localize words while leaving every operator,
# identifier, delimiter, and formula position unchanged.
MATH_TEXT_LOCALIZATIONS = (
    {
        "page": "random/point/Likelihood.html",
        "old": r"\text{ for each }",
        "new": r"\text{ untuk setiap }",
        "replacements": 1,
        "surface": "math_span",
    },
    {
        "page": "random/sample/Covariance.html",
        "old": r"\text{ as }",
        "new": r"\text{ ketika }",
        "replacements": 1,
        "surface": "math_span",
    },
    {
        "page": "random/sample/CLT.html",
        "old": r"\text{ as }",
        "new": r"\text{ ketika }",
        "replacements": 1,
        "surface": "math_span",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"\text{ as }",
        "new": r"\text{ ketika }",
        "replacements": 5,
        "surface": "math_span",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"\text{ for infinitely many }",
        "new": r"\text{ untuk tak hingga banyak }",
        "replacements": 2,
        "surface": "math_span",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"\text{For some rational }",
        "new": r"\text{Untuk suatu bilangan rasional }",
        "replacements": 1,
        "surface": "math_span",
    },
    {
        "page": "random/sample/LLN.html",
        "old": r"\text{ for every }",
        "new": r"\text{ untuk setiap }",
        "replacements": 1,
        "surface": "math_span",
    },
    {
        "page": "random/point/Sufficient.html",
        "old": r"\text{ is independent of }",
        "new": r"\text{ tidak bergantung pada }",
        "replacements": 1,
        "surface": "math_span",
    },
    {
        "page": "random/point/Sufficient.html",
        "old": r"\text{ if and only if }",
        "new": r"\text{ jika dan hanya jika }",
        "replacements": 1,
        "surface": "math_span",
    },
    {
        "page": "random/point/Sufficient.html",
        "old": r"\text{ for all }",
        "new": r"\text{ untuk semua }",
        "replacements": 2,
        "surface": "math_span",
    },
)

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _under_root(path: Path) -> tuple[Path, Path]:
    absolute = _absolute(path)
    try:
        relative = absolute.relative_to(ROOT)
    except ValueError as exc:
        raise RuntimeError(f"path is outside the edition root: {absolute}") from exc
    return absolute, relative


def _lexists(path: Path) -> bool:
    return os.path.lexists(os.fspath(path))


def _is_reparse(info: os.stat_result) -> bool:
    marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(marker and (getattr(info, "st_file_attributes", 0) & marker))


def _is_link_or_reparse(path: Path, info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or _is_reparse(info) or path.is_symlink()


def assert_no_reparse_components(path: Path) -> None:
    absolute, relative = _under_root(path)
    current = ROOT
    if _lexists(current):
        root_info = os.lstat(current)
        if _is_link_or_reparse(current, root_info):
            raise RuntimeError(f"edition root is linked or reparse-backed: {current}")
    for part in relative.parts:
        current = current / part
        if not _lexists(current):
            break
        info = os.lstat(current)
        if _is_link_or_reparse(current, info):
            raise RuntimeError(f"linked/reparse path is forbidden: {current}")
    if absolute != _absolute(path):  # defensive; _absolute is deterministic
        raise RuntimeError(f"unstable path normalization: {path}")


def ensure_regular(path: Path, *, reject_hardlinks: bool = False) -> None:
    assert_no_reparse_components(path)
    if not _lexists(path):
        raise RuntimeError(f"required regular file is absent: {path}")
    info = os.lstat(path)
    if not stat.S_ISREG(info.st_mode):
        raise RuntimeError(f"required path is not a regular file: {path}")
    if reject_hardlinks and getattr(info, "st_nlink", 1) != 1:
        raise RuntimeError(f"hard-linked file is forbidden here: {path}")


def ensure_directory(path: Path) -> None:
    assert_no_reparse_components(path)
    if not _lexists(path):
        raise RuntimeError(f"required directory is absent: {path}")
    if not stat.S_ISDIR(os.lstat(path).st_mode):
        raise RuntimeError(f"required path is not a directory: {path}")


def read_regular(path: Path, *, reject_hardlinks: bool = False) -> bytes:
    ensure_regular(path, reject_hardlinks=reject_hardlinks)
    return path.read_bytes()


def make_directory(path: Path) -> None:
    _, relative = _under_root(path)
    current = ROOT
    ensure_directory(current)
    for part in relative.parts:
        current = current / part
        if _lexists(current):
            info = os.lstat(current)
            if _is_link_or_reparse(current, info) or not stat.S_ISDIR(info.st_mode):
                raise RuntimeError(f"refusing unsafe directory component: {current}")
        else:
            os.mkdir(current)


def ensure_write_target(path: Path) -> None:
    _under_root(path)
    assert_no_reparse_components(path.parent)
    ensure_directory(path.parent)
    if _lexists(path):
        assert_no_reparse_components(path)
        info = os.lstat(path)
        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError(f"refusing non-regular output file: {path}")
        if getattr(info, "st_nlink", 1) != 1:
            raise RuntimeError(f"refusing hard-linked output file: {path}")


def write_regular(path: Path, data: bytes) -> None:
    ensure_write_target(path)
    path.write_bytes(data)
    ensure_regular(path, reject_hardlinks=True)


def secure_tree_files(base: Path) -> list[Path]:
    ensure_directory(base)
    files: list[Path] = []

    def visit(directory: Path) -> None:
        with os.scandir(directory) as entries:
            for entry in entries:
                entry_path = Path(entry.path)
                # DirEntry.stat() can report a synthetic zero link count on
                # Windows network/provider-backed volumes; lstat() returns the
                # real file identity and reparse attributes.
                info = os.lstat(entry_path)
                if entry.is_symlink() or _is_reparse(info):
                    raise RuntimeError(f"linked/reparse reader entry is forbidden: {entry_path}")
                if stat.S_ISDIR(info.st_mode):
                    visit(entry_path)
                elif stat.S_ISREG(info.st_mode):
                    if getattr(info, "st_nlink", 1) != 1:
                        raise RuntimeError(f"hard-linked reader file is forbidden: {entry_path}")
                    files.append(entry_path)
                else:
                    raise RuntimeError(f"non-regular reader entry is forbidden: {entry_path}")

    visit(base)
    return files


def root_index() -> bytes:
    return (
        "<!doctype html>\n"
        '<html lang="id-ID"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<meta name="translation-provenance" content="{TRANSLATION_PROVENANCE}">\n'
        "<title>Statistika Matematis — Bahasa Indonesia</title>\n"
        "<style>body{margin:0;background:#e8edf2;color:#102536;font-family:system-ui,sans-serif}"
        "main{box-sizing:border-box;width:min(100%,72rem);min-height:100vh;margin:0 auto;"
        "padding:clamp(1.25rem,4vw,4rem);background:#fff;line-height:1.6}"
        "a{color:#174f7a}li{margin:.45rem 0}</style></head>\n"
        '<body><main><h1>Statistika Matematis</h1>\n'
        "<p>Edisi lengkap Bahasa Indonesia: 29 dari 29 halaman inti dalam bab "
        "statistika matematis telah diterjemahkan.</p>\n"
        "<nav aria-label=\"Bab\"><ol>\n"
        '<li><a href="random/sample/index.html">5. Sampel Acak</a></li>\n'
        '<li><a href="random/point/index.html">6. Pendugaan Titik</a></li>\n'
        '<li><a href="random/interval/index.html">7. Pendugaan Himpunan</a></li>\n'
        '<li><a href="random/hypothesis/index.html">8. Pengujian Hipotesis</a></li>\n'
        "</ol></nav>\n"
        "<p>Edisi Bahasa Indonesia independen berdasarkan "
        '<a href="https://www.randomservices.org/random/">Random</a> karya Kyle Siegrist. '
        "Terjemahan ini tidak didukung atau disahkan oleh penulis sumber.</p>\n"
        f"<p>Provenans terjemahan: {TRANSLATION_PROVENANCE}. Kredit karya sumber "
        "dan kontributor manusia tetap dipertahankan.</p>\n"
        '<p><a href="licenses/index.html">Atribusi dan lisensi komponen</a></p>\n'
        "</main></body></html>\n"
    ).encode("utf-8")


def licences_index() -> bytes:
    return (
        "<!doctype html>\n"
        '<html lang="id-ID"><head><meta charset="utf-8">'
        f'<meta name="translation-provenance" content="{TRANSLATION_PROVENANCE}">'
        "<title>Atribusi dan Lisensi</title>"
        "<style>body{margin:0;background:#e8edf2;color:#102536;font-family:system-ui,sans-serif}"
        "main{box-sizing:border-box;width:min(100%,72rem);min-height:100vh;margin:0 auto;"
        "padding:clamp(1.25rem,4vw,4rem);background:#fff;line-height:1.6}"
        "a{color:#174f7a}</style></head><body><main>\n"
        "<h1>Atribusi dan Lisensi</h1>\n"
        "<p>Sumber utama: Kyle Siegrist, <cite>Random: Probability, Mathematical "
        "Statistics, and Stochastic Processes</cite>. Terjemahan dan perubahan "
        "struktur akses dibuat secara independen; penulis sumber tidak mendukung "
        "atau mengesahkan edisi ini.</p>\n"
        f"<p>Provenans terjemahan: {TRANSLATION_PROVENANCE}. Catatan ini tidak "
        "menggantikan kredit sumber atau kontributor manusia.</p>\n"
        '<p><a href="https://www.randomservices.org/random/">Karya sumber</a>. '
        'Laman utama menautkan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>; '
        '<a href="https://www.randomservices.org/random/Credits.html">laman kredit</a> '
        'menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>. '
        "Perbedaan tersebut dipertahankan di sini.</p>\n"
        "<p>MathJax 3.1.2 tersedia di bawah Apache License 2.0; teks lisensinya "
        'disertakan sebagai <a href="MathJax-3.1.2-LICENSE.txt">berkas lokal</a>.</p>\n'
        "</main></body></html>\n"
    ).encode("utf-8")


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _manifest_rows(data: bytes, header: tuple[str, ...], label: str) -> dict[str, dict[str, str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"{label} is not UTF-8: {exc}") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != header:
        raise RuntimeError(f"{label} header mismatch: {reader.fieldnames}")
    rows: dict[str, dict[str, str]] = {}
    folded: set[str] = set()
    for line_number, row in enumerate(reader, start=2):
        if None in row or any(row.get(key) is None for key in header):
            raise RuntimeError(f"{label} malformed row {line_number}")
        rel = row["relative_path"]
        pure = PurePosixPath(rel)
        if (
            not rel
            or pure.is_absolute()
            or pure.as_posix() != rel
            or any(part in {"", ".", ".."} for part in pure.parts)
            or "\\" in rel
            or ":" in rel
            or "\x00" in rel
        ):
            raise RuntimeError(f"{label} noncanonical path at row {line_number}: {rel!r}")
        folded_rel = rel.casefold()
        if rel in rows or folded_rel in folded:
            raise RuntimeError(f"{label} duplicate/colliding path: {rel}")
        folded.add(folded_rel)
        size = row["bytes"]
        if not size.isdigit() or str(int(size)) != size:
            raise RuntimeError(f"{label} invalid byte count for {rel}: {size!r}")
        if not SHA256_RE.fullmatch(row["sha256"]):
            raise RuntimeError(f"{label} invalid SHA-256 for {rel}")
        rows[rel] = {key: row[key] for key in header}
    return rows


def _canonical_positive_integer(value: str, *, label: str) -> int:
    if not value or not value.isascii() or not value.isdecimal():
        raise RuntimeError(f"{label} is not a positive canonical integer: {value!r}")
    parsed = int(value)
    if parsed < 1 or str(parsed) != value:
        raise RuntimeError(f"{label} is not a positive canonical integer: {value!r}")
    return parsed


def _load_translation_ledger(
    source_rows: dict[str, dict[str, str]],
) -> tuple[bytes, list[dict[str, Any]], dict[str, bytes]]:
    """Bind the build to the live, exact, complete 29-document ledger."""

    if len(TARGETS) != CORE_DOCUMENT_COUNT or len(set(TARGETS)) != CORE_DOCUMENT_COUNT:
        raise RuntimeError("TARGETS must contain exactly 29 unique Random core paths")
    ledger_data = read_regular(TRANSLATION_LEDGER)
    if ledger_data.startswith(b"\xef\xbb\xbf"):
        raise RuntimeError("translation ledger must be UTF-8 without BOM")
    try:
        ledger_text = ledger_data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"translation ledger is not UTF-8: {exc}") from exc
    reader = csv.DictReader(io.StringIO(ledger_text, newline=""))
    if tuple(reader.fieldnames or ()) != TRANSLATION_LEDGER_HEADER:
        raise RuntimeError(f"translation ledger header mismatch: {reader.fieldnames}")
    raw_rows = list(reader)
    if len(raw_rows) != CORE_DOCUMENT_COUNT:
        raise RuntimeError(
            f"translation ledger must contain exactly {CORE_DOCUMENT_COUNT} rows, found {len(raw_rows)}"
        )
    if any(
        None in row or any(row.get(column) is None for column in TRANSLATION_LEDGER_HEADER)
        for row in raw_rows
    ):
        raise RuntimeError("translation ledger contains a malformed row")

    verified_rows: list[dict[str, Any]] = []
    target_data: dict[str, bytes] = {}
    target_paths_seen: set[str] = set()
    for ordinal, (expected_rel, row) in enumerate(zip(TARGETS, raw_rows, strict=True), 1):
        row_number = ordinal + 1
        found_ordinal = _canonical_positive_integer(
            row["ordinal"], label=f"translation ledger row {row_number} ordinal"
        )
        if found_ordinal != ordinal:
            raise RuntimeError(
                f"translation ledger is not contiguous at row {row_number}: "
                f"expected ordinal {ordinal}, found {found_ordinal}"
            )
        source_path = row["source_path"]
        if source_path != expected_rel.as_posix():
            raise RuntimeError(
                f"translation ledger ordinal {ordinal} path mismatch: "
                f"expected {expected_rel}, found {source_path}"
            )
        if row["status"] != "complete":
            raise RuntimeError(
                f"translation ledger ordinal {ordinal} is not complete: {row['status']!r}"
            )
        manifest_row = source_rows.get(source_path)
        if manifest_row is None or manifest_row["role"] != "core":
            raise RuntimeError(f"ledger authority is not a frozen core row: {source_path}")
        source_bytes = _canonical_positive_integer(
            row["source_bytes"], label=f"translation ledger ordinal {ordinal} source_bytes"
        )
        if source_bytes != int(manifest_row["bytes"]):
            raise RuntimeError(f"translation ledger source byte mismatch at ordinal {ordinal}")
        if row["source_sha256"] != manifest_row["sha256"]:
            raise RuntimeError(f"translation ledger source SHA-256 mismatch at ordinal {ordinal}")

        expected_target_path = (PurePosixPath("source/id-ID") / expected_rel).as_posix()
        target_path = row["target_path"]
        if target_path != expected_target_path or target_path in target_paths_seen:
            raise RuntimeError(
                f"translation ledger target path mismatch/collision at ordinal {ordinal}: {target_path}"
            )
        target_paths_seen.add(target_path)
        translated = read_regular(ROOT / Path(target_path))
        try:
            translated.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"translation target is not UTF-8 at ordinal {ordinal}: {exc}") from exc
        target_bytes = _canonical_positive_integer(
            row["target_bytes"], label=f"translation ledger ordinal {ordinal} target_bytes"
        )
        if len(translated) != target_bytes:
            raise RuntimeError(f"translation ledger target byte mismatch at ordinal {ordinal}")
        if not SHA256_RE.fullmatch(row["target_sha256"]):
            raise RuntimeError(f"translation ledger target SHA-256 is invalid at ordinal {ordinal}")
        target_sha256 = sha256_bytes(translated)
        if target_sha256 != row["target_sha256"]:
            raise RuntimeError(f"translation ledger target SHA-256 mismatch at ordinal {ordinal}")
        target_data[source_path] = translated
        verified_rows.append(
            {
                "ordinal": ordinal,
                "source_path": source_path,
                "source_bytes": source_bytes,
                "source_sha256": row["source_sha256"],
                "target_path": target_path,
                "target_bytes": target_bytes,
                "target_sha256": target_sha256,
                "status": "complete",
            }
        )
    return ledger_data, verified_rows, target_data


def _css_references(css: str) -> list[tuple[str, str]]:
    without_comments = CSS_COMMENT_RE.sub("", css)
    references: list[tuple[str, str]] = []
    for match in CSS_URL_RE.finditer(without_comments):
        value = (match.group(2) if match.group(1) else match.group(3)).strip()
        references.append(("css:url", value))
    references.extend(
        ("css:import", match.group(2).strip())
        for match in CSS_IMPORT_RE.finditer(without_comments)
    )
    return references


def _resolve_local_dependency(owner: PurePosixPath, value: str) -> PurePosixPath | None:
    if not value:
        raise RuntimeError(f"empty dependency reference in {owner}")
    if "\x00" in value or "\\" in value:
        raise RuntimeError(f"noncanonical dependency reference in {owner}: {value!r}")
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    decoded = unquote(parsed.path)
    if decoded != parsed.path or "\x00" in decoded or "\\" in decoded:
        raise RuntimeError(f"encoded/noncanonical dependency path in {owner}: {value!r}")
    if not decoded:
        return None
    joined = decoded.lstrip("/") if decoded.startswith("/") else posixpath.join(
        owner.parent.as_posix(), decoded
    )
    normalized = posixpath.normpath(joined)
    dependency = PurePosixPath(normalized)
    if (
        dependency.is_absolute()
        or normalized in {"", ".", ".."}
        or any(part in {"", ".", ".."} for part in dependency.parts)
        or ":" in normalized
    ):
        raise RuntimeError(f"dependency escapes or is noncanonical in {owner}: {value!r}")
    return dependency


def _dependency_references(
    owner: PurePosixPath, data: bytes
) -> list[tuple[str, str]]:
    suffix = owner.suffix.casefold()
    if suffix == ".css":
        try:
            return _css_references(data.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"dependency stylesheet is not UTF-8: {owner}") from exc
    if suffix not in {".html", ".htm", ".svg"}:
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"dependency document is not UTF-8: {owner}") from exc
    parser = DependencyHTMLParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        raise RuntimeError(f"cannot parse dependency-bearing document {owner}: {exc}") from exc
    references = list(parser.references)
    for css in parser.inline_css:
        references.extend(_css_references(css))
    return references


def _discover_support_closure(
    target_data: dict[str, bytes],
    source_rows: dict[str, dict[str, str]],
    provided_paths: set[PurePosixPath],
) -> tuple[
    dict[PurePosixPath, bytes],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, str]],
]:
    """Resolve every transitive local reader dependency from the 29 targets."""

    target_paths = set(TARGETS)
    pending: set[PurePosixPath] = set()
    support_data: dict[PurePosixPath, bytes] = {}
    authority_records: list[dict[str, Any]] = []
    target_only_records: list[dict[str, Any]] = []
    edges: set[tuple[str, str, str, str]] = set()

    def enqueue(owner: PurePosixPath, data: bytes) -> None:
        for kind, raw_reference in _dependency_references(owner, data):
            dependency = _resolve_local_dependency(owner, raw_reference)
            if dependency is None:
                continue
            edges.add((owner.as_posix(), kind, raw_reference, dependency.as_posix()))
            if dependency not in target_paths and dependency not in provided_paths:
                pending.add(dependency)

    for rel in TARGETS:
        enqueue(rel, target_data[rel.as_posix()])

    while pending:
        rel = min(pending, key=lambda item: (item.as_posix().casefold(), item.as_posix()))
        pending.remove(rel)
        if rel in support_data:
            continue
        target_only = TARGET_ONLY_SUPPORT.get(rel)
        if target_only is not None:
            data = read_regular(SOURCE / Path(rel.as_posix()))
            if len(data) != target_only["bytes"] or sha256_bytes(data) != target_only["sha256"]:
                raise RuntimeError(f"target-only support differs from its exact pin: {rel}")
            record = {
                "relative_path": rel.as_posix(),
                "purpose": target_only["purpose"],
                "authority_backed": False,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
            target_only_records.append(record)
        else:
            row = source_rows.get(rel.as_posix())
            if row is None:
                raise RuntimeError(f"local dependency is absent from the frozen manifest: {rel}")
            if row["role"] != "asset":
                raise RuntimeError(
                    f"local dependency is neither a translated target nor a frozen asset: {rel} ({row['role']})"
                )
            if row["url"] != "https://www.randomservices.org/" + rel.as_posix():
                raise RuntimeError(f"local dependency authority URL mismatch: {rel}")
            data, record = _validated_file_record(
                AUTHORITY, rel, row, purpose="reader_support_transitive"
            )
            authority_records.append(record)
        support_data[rel] = data
        enqueue(rel, data)

    missing_target_only = set(TARGET_ONLY_SUPPORT) - set(support_data)
    if missing_target_only:
        raise RuntimeError(
            "pinned target-only support is not referenced by the complete reader: "
            + ", ".join(path.as_posix() for path in sorted(missing_target_only))
        )
    edge_records = [
        {"owner": owner, "kind": kind, "reference": reference, "resolved_path": target}
        for owner, kind, reference, target in sorted(
            edges, key=lambda item: tuple(part.casefold() for part in item)
        )
    ]
    return support_data, authority_records, target_only_records, edge_records


def _freeze_evidence(
    manifest_path: Path,
    receipt_path: Path,
    *,
    schema: str,
    bytes_field: str,
    hash_field: str,
    filename_field: str | None = None,
) -> tuple[bytes, dict[str, Any]]:
    manifest_data = read_regular(manifest_path)
    receipt_data = read_regular(receipt_path)
    try:
        receipt = json.loads(receipt_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid freeze receipt {receipt_path}: {exc}") from exc
    if receipt.get("schema") != schema:
        raise RuntimeError(f"unexpected freeze receipt schema: {receipt_path}")
    if receipt.get(bytes_field) != len(manifest_data):
        raise RuntimeError(f"freeze receipt byte count does not bind {manifest_path}")
    if receipt.get(hash_field) != sha256_bytes(manifest_data):
        raise RuntimeError(f"freeze receipt hash does not bind {manifest_path}")
    if filename_field is not None and receipt.get(filename_field) != manifest_path.name:
        raise RuntimeError(f"freeze receipt filename does not bind {manifest_path}")
    evidence = {
        "manifest_path": manifest_path.relative_to(ROOT).as_posix(),
        "manifest_bytes": len(manifest_data),
        "manifest_sha256": sha256_bytes(manifest_data),
        "freeze_receipt_path": receipt_path.relative_to(ROOT).as_posix(),
        "freeze_receipt_bytes": len(receipt_data),
        "freeze_receipt_sha256": sha256_bytes(receipt_data),
        "freeze_receipt_schema": schema,
    }
    return manifest_data, evidence


def _validated_file_record(
    base: Path,
    rel: PurePosixPath,
    row: dict[str, str],
    *,
    purpose: str,
) -> tuple[bytes, dict[str, Any]]:
    path = base / Path(rel.as_posix())
    data = read_regular(path)
    expected_size = int(row["bytes"])
    expected_hash = row["sha256"]
    if len(data) != expected_size or sha256_bytes(data) != expected_hash:
        raise RuntimeError(f"selected frozen input does not match its manifest: {rel}")
    record: dict[str, Any] = {
        "relative_path": rel.as_posix(),
        "purpose": purpose,
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }
    for key, value in row.items():
        if key not in {"relative_path", "bytes", "sha256"}:
            record[key] = value
    return data, record


def _runtime_payload() -> tuple[bytes, dict[str, Any]]:
    encoded = read_regular(RUNTIME_BASE64)
    receipt_data = read_regular(RUNTIME_RECEIPT)
    try:
        receipt = json.loads(receipt_data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid MathJax runtime receipt: {exc}") from exc
    expected = {
        "schema": "o006.mathjax-runtime.v1",
        "component": "MathJax",
        "version": "3.1.2",
        "license": "Apache-2.0",
        "official_repository": "https://github.com/mathjax/MathJax",
        "tag": "3.1.2",
        "commit": "c8292351190ce249f7143f224dbe7a190c8228fe",
        "git_path": "es5/input/tex/extensions/boldsymbol.js",
        "git_blob_sha1": "4570456930955792300c57537ad580ef14311335",
        "raw_url": (
            "https://raw.githubusercontent.com/mathjax/MathJax/3.1.2/"
            "es5/input/tex/extensions/boldsymbol.js"
        ),
        "encoded_authority": {
            "path": RUNTIME_BASE64.relative_to(ROOT).as_posix(),
            "encoding": "base64",
            "bytes": 6281,
            "sha256": "c613a859a03f6aff52641565de9d05d616add490072d3860598de5803deeaf33",
        },
        "decoded_runtime": {
            "reader_path": RUNTIME_READER_PATH.as_posix(),
            "bytes": RUNTIME_BYTES,
            "sha256": RUNTIME_SHA256,
        },
    }
    if receipt != expected:
        raise RuntimeError("MathJax runtime receipt differs from the admitted exact profile")
    if (
        len(encoded) != receipt["encoded_authority"]["bytes"]
        or sha256_bytes(encoded) != receipt["encoded_authority"]["sha256"]
    ):
        raise RuntimeError("MathJax encoded authority bytes do not match the runtime receipt")
    try:
        compact = b"".join(encoded.split())
        decoded = base64.b64decode(compact, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise RuntimeError(f"invalid MathJax runtime base64: {exc}") from exc
    if len(decoded) != RUNTIME_BYTES or sha256_bytes(decoded) != RUNTIME_SHA256:
        raise RuntimeError("decoded MathJax runtime bytes do not match the pinned release asset")
    return decoded, {
        "authority_receipt_path": RUNTIME_RECEIPT.relative_to(ROOT).as_posix(),
        "authority_receipt_bytes": len(receipt_data),
        "authority_receipt_sha256": sha256_bytes(receipt_data),
        **receipt,
    }


def _math_spans(text: str) -> list[str]:
    """Extract inline/display TeX with the same paragraph-boundary rule as QA."""

    spans: list[str] = []
    cursor = 0
    while True:
        starts = [
            (value, marker)
            for value, marker in ((text.find(r"\(", cursor), r"\("), (text.find(r"\[", cursor), r"\["))
            if value >= 0
        ]
        if not starts:
            break
        start, opener = min(starts)
        closer = r"\)" if opener == r"\(" else r"\]"
        close = text.find(closer, start + 2)
        paragraph_end = text.find("</p>", start + 2)
        if paragraph_end >= 0 and (close < 0 or paragraph_end < close):
            spans.append(text[start:paragraph_end])
            cursor = paragraph_end
        elif close >= 0:
            spans.append(text[start : close + 2])
            cursor = close + 2
        else:
            spans.append(text[start:])
            break
    return spans


def _raw_align_environments(text: str) -> list[str]:
    """Extract undelimited align/align* environments in source order."""

    pattern = re.compile(r"\\begin\{(align\*?)\}.*?\\end\{\1\}", re.DOTALL)
    return [match.group(0) for match in pattern.finditer(text)]


def _validate_target_corrections(
    authority_data: dict[str, bytes], target_data: dict[str, bytes]
) -> None:
    for change in TRANSPORT_HARDENING:
        text = target_data[change["page"]].decode("utf-8")
        if text.count(change["original_href"]) != 0:
            raise RuntimeError(f"stale HTTP href remains: {change['original_href']}")
        if text.count(change["target_href"]) != 1:
            raise RuntimeError(f"transport-hardening href count changed: {change['target_href']}")
    for change in BOUNDED_TEXT_CORRECTIONS:
        text = target_data[change["page"]].decode("utf-8")
        if text.count(change["old"]) != 0:
            raise RuntimeError(f"stale bounded prose remains in {change['page']}: {change['old']}")
        if text.count(change["new"]) != change["replacements"]:
            raise RuntimeError(f"bounded prose correction count changed in {change['page']}: {change['new']}")
    for change in BOUNDED_REFERENCE_CORRECTIONS:
        source_text = authority_data[change["page"]].decode("utf-8")
        target_text = target_data[change["page"]].decode("utf-8")
        replacements = int(change["replacements"])
        target_additions = int(change.get("target_additions", 0))
        if target_text.count(change["old"]) != source_text.count(change["old"]) - replacements:
            raise RuntimeError(
                f"bounded source-reference repair count changed in {change['page']}: {change['old']}"
            )
        if target_text.count(change["new"]) != (
            source_text.count(change["new"]) + replacements + target_additions
        ):
            raise RuntimeError(
                f"bounded target-reference repair count changed in {change['page']}: {change['new']}"
            )
    for change in PROTECTED_MATH_CORRECTIONS:
        source_text = authority_data[change["page"]].decode("utf-8")
        target_text = target_data[change["page"]].decode("utf-8")
        replacements = int(change["replacements"])
        span_index = change.get("span_index")
        if change["surface"] == "math_span" and span_index is not None:
            source_spans = _math_spans(source_text)
            target_spans = _math_spans(target_text)
            index = int(span_index) - 1
            if index < 0 or index >= len(source_spans) or index >= len(target_spans):
                raise RuntimeError(
                    f"protected source-correction span index changed in {change['page']}: {span_index}"
                )
            old = change.get("span_old", change["old"])
            new = change.get("span_new", change["new"])
            if source_spans[index].count(old) != replacements:
                raise RuntimeError(
                    f"protected source-correction authority span changed in {change['page']}: {old}"
                )
            if target_spans[index].count(old) != 0:
                raise RuntimeError(
                    f"stale protected source defect remains in {change['page']} span {span_index}: {old}"
                )
            expected_new = source_spans[index].count(new) + replacements
            if target_spans[index].count(new) != expected_new:
                raise RuntimeError(
                    f"protected source-correction span count changed in {change['page']}: {new}"
                )
            continue
        environment_index = change.get("environment_index")
        if change["surface"] == "raw_math_environment" and environment_index is not None:
            source_environments = _raw_align_environments(source_text)
            target_environments = _raw_align_environments(target_text)
            index = int(environment_index) - 1
            if (
                index < 0
                or index >= len(source_environments)
                or index >= len(target_environments)
            ):
                raise RuntimeError(
                    "protected raw-math environment index changed in "
                    f"{change['page']}: {environment_index}"
                )
            old = change["old"]
            new = change["new"]
            if source_environments[index].count(old) != replacements:
                raise RuntimeError(
                    "protected raw-math authority environment changed in "
                    f"{change['page']}: {old}"
                )
            if target_environments[index].count(old) != 0:
                raise RuntimeError(
                    "stale protected raw-math defect remains in "
                    f"{change['page']} environment {environment_index}: {old}"
                )
            expected_new = source_environments[index].count(new) + replacements
            if target_environments[index].count(new) != expected_new:
                raise RuntimeError(
                    "protected raw-math correction count changed in "
                    f"{change['page']}: {new}"
                )
            continue
        if source_text.count(change["old"]) != replacements:
            raise RuntimeError(
                f"protected source-correction authority count changed in {change['page']}: {change['old']}"
            )
        if target_text.count(change["old"]) != 0:
            raise RuntimeError(
                f"stale protected source defect remains in {change['page']}: {change['old']}"
            )
        expected_new = source_text.count(change["new"]) + replacements
        if target_text.count(change["new"]) != expected_new:
            raise RuntimeError(
                f"protected source-correction count changed in {change['page']}: {change['new']}"
            )


def collect_inputs() -> tuple[dict[PurePosixPath, bytes], dict[str, Any]]:
    source_manifest_data, source_freeze = _freeze_evidence(
        SOURCE_MANIFEST,
        SOURCE_FREEZE_RECEIPT,
        schema="o006.random.source-freeze.v1",
        bytes_field="source_manifest_bytes",
        hash_field="source_manifest_sha256",
    )
    license_manifest_data, license_freeze = _freeze_evidence(
        LICENSE_MANIFEST,
        LICENSE_FREEZE_RECEIPT,
        schema="o006.random.component-licenses.v1",
        bytes_field="url_manifest_bytes",
        hash_field="url_manifest_sha256",
        filename_field="url_manifest",
    )
    try:
        source_freeze_document = json.loads(read_regular(SOURCE_FREEZE_RECEIPT).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid source freeze receipt: {exc}") from exc
    frozen_core_paths = source_freeze_document.get("core_paths")
    expected_core_paths = [rel.as_posix() for rel in TARGETS]
    if (
        frozen_core_paths != expected_core_paths
        or source_freeze_document.get("core_files") != CORE_DOCUMENT_COUNT
    ):
        raise RuntimeError("TARGETS/translation ledger order differs from the frozen 29-document core")
    source_freeze["core_document_count"] = CORE_DOCUMENT_COUNT
    source_freeze["core_order_verified"] = True
    source_freeze["core_paths"] = expected_core_paths
    source_rows = _manifest_rows(source_manifest_data, SOURCE_MANIFEST_HEADER, "source manifest")
    license_rows = _manifest_rows(license_manifest_data, LICENSE_MANIFEST_HEADER, "license manifest")
    ledger_data, ledger_rows, target_data = _load_translation_ledger(source_rows)

    payload: dict[PurePosixPath, bytes] = {
        PurePosixPath("index.html"): root_index(),
        PurePosixPath("licenses/index.html"): licences_index(),
    }
    authority_inputs: list[dict[str, Any]] = []
    target_inputs: list[dict[str, Any]] = []
    authority_data: dict[str, bytes] = {}

    for rel, ledger_row in zip(TARGETS, ledger_rows, strict=True):
        row = source_rows.get(rel.as_posix())
        if row is None or row["role"] != "core":
            raise RuntimeError(f"selected translation authority is not a core manifest row: {rel}")
        if row["url"] != "https://www.randomservices.org/" + rel.as_posix():
            raise RuntimeError(f"selected authority URL mismatch: {rel}")
        authority, authority_record = _validated_file_record(
            AUTHORITY, rel, row, purpose="translation_authority"
        )
        authority_data[rel.as_posix()] = authority
        authority_inputs.append(authority_record)

        translated = target_data[rel.as_posix()]
        payload[rel] = translated
        target_inputs.append(
            {
                "ordinal": ledger_row["ordinal"],
                "relative_path": rel.as_posix(),
                "ledger_target_path": ledger_row["target_path"],
                "status": ledger_row["status"],
                "bytes": len(translated),
                "sha256": sha256_bytes(translated),
            }
        )

    if sum(record["bytes"] for record in authority_inputs) != source_freeze_document.get(
        "core_bytes"
    ):
        raise RuntimeError("verified translation-authority byte total differs from the core freeze")

    _validate_target_corrections(authority_data, target_data)

    runtime_data, runtime_input = _runtime_payload()
    if RUNTIME_READER_PATH in payload:
        raise RuntimeError(f"duplicate reader runtime path: {RUNTIME_READER_PATH}")
    payload[RUNTIME_READER_PATH] = runtime_data

    support_data, support_authority_inputs, target_only_inputs, dependency_edges = (
        _discover_support_closure(target_data, source_rows, {RUNTIME_READER_PATH})
    )
    authority_inputs.extend(support_authority_inputs)
    reader_customizations: list[dict[str, Any]] = []
    for rel in sorted(support_data, key=lambda item: (item.as_posix().casefold(), item.as_posix())):
        data = support_data[rel]
        reader_data = data
        if rel == PurePosixPath("random/Screen.css"):
            reader_data = data + READABLE_REFLOW_CSS
            reader_customizations.append(
                {
                    "kind": "readable-layout-css-append",
                    "version": "o006-id-readable-layout-v3",
                    "reader_relative_path": rel.as_posix(),
                    "authority_bytes": len(data),
                    "authority_sha256": sha256_bytes(data),
                    "append_bytes": len(READABLE_REFLOW_CSS),
                    "append_sha256": sha256_bytes(READABLE_REFLOW_CSS),
                    "reader_bytes": len(reader_data),
                    "reader_sha256": sha256_bytes(reader_data),
                    "desktop_min_width_px": 801,
                    "desktop_max_width_rem": 72,
                    "mobile_max_width_px": 800,
                }
            )
        payload[rel] = reader_data

    if read_regular(TRANSLATION_LEDGER) != ledger_data:
        raise RuntimeError("translation ledger changed during reader input collection")
    for rel in TARGETS:
        if read_regular(SOURCE / Path(rel.as_posix())) != target_data[rel.as_posix()]:
            raise RuntimeError(f"translation target changed during reader input collection: {rel}")

    license_inputs: list[dict[str, Any]] = []
    for source_rel, reader_rel, expected_license in LICENSE_FILES:
        row = license_rows.get(source_rel.as_posix())
        if row is None or row["license"] != expected_license:
            raise RuntimeError(f"selected license is absent or mislabeled: {source_rel}")
        data, license_record = _validated_file_record(
            LICENSE_ROOT, source_rel, row, purpose="reader_license"
        )
        license_record["reader_relative_path"] = reader_rel.as_posix()
        license_inputs.append(license_record)
        payload[reader_rel] = data

    generated_inputs = []
    for rel in (PurePosixPath("index.html"), PurePosixPath("licenses/index.html")):
        data = payload[rel]
        generated_inputs.append(
            {"reader_relative_path": rel.as_posix(), "bytes": len(data), "sha256": sha256_bytes(data)}
        )

    evidence = {
        "frozen_manifests": {
            "source": source_freeze,
            "component_licenses": license_freeze,
        },
        "translation_ledger": {
            "path": TRANSLATION_LEDGER.relative_to(ROOT).as_posix(),
            "bytes": len(ledger_data),
            "sha256": sha256_bytes(ledger_data),
            "required_document_count": CORE_DOCUMENT_COUNT,
            "required_ordinals": list(range(1, CORE_DOCUMENT_COUNT + 1)),
            "verified_rows": ledger_rows,
        },
        "authority_inputs": sorted(authority_inputs, key=lambda item: item["relative_path"].casefold()),
        "target_inputs": target_inputs,
        "target_only_inputs": sorted(
            target_only_inputs, key=lambda item: item["relative_path"].casefold()
        ),
        "dependency_closure": {
            "algorithm": "transitive local HTML/SVG href/src/reference attributes plus inline/external CSS url/import",
            "authority_backed_support_paths": sorted(
                (record["relative_path"] for record in support_authority_inputs),
                key=str.casefold,
            ),
            "target_only_support_paths": sorted(
                (record["relative_path"] for record in target_only_inputs),
                key=str.casefold,
            ),
            "support_file_count": len(support_data),
            "edges": dependency_edges,
        },
        "license_inputs": sorted(license_inputs, key=lambda item: item["relative_path"].casefold()),
        "runtime_inputs": [runtime_input],
        "generated_inputs": sorted(
            generated_inputs, key=lambda item: item["reader_relative_path"].casefold()
        ),
        "reader_customizations": reader_customizations,
    }
    return payload, evidence


def canonical_rows(base: Path) -> list[tuple[str, int, str]]:
    files = secure_tree_files(base)
    rels = [(path.relative_to(base).as_posix(), path) for path in files]
    folded = [rel.casefold() for rel, _ in rels]
    if len(folded) != len(set(folded)):
        raise RuntimeError("case-folding path collision in reader")
    rels.sort(key=lambda item: item[0].casefold())
    return [(rel, path.stat().st_size, digest(path)) for rel, path in rels]


def manifest_bytes(rows: list[tuple[str, int, str]]) -> bytes:
    lines = ["relative_path,bytes,sha256\n"]
    for rel, size, sha in rows:
        if any(ch in rel for ch in '\",\r\n'):
            raise RuntimeError(f"manifest path needs quoting: {rel}")
        lines.append(f"{rel},{size},{sha}\n")
    return "".join(lines).encode("utf-8")


def _script_record(path: Path) -> dict[str, Any]:
    data = read_regular(path)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def expected_receipt(
    evidence: dict[str, Any],
    rows: list[tuple[str, int, str]],
    reader_manifest: bytes,
) -> dict[str, Any]:
    return {
        "schema": "o006.random.complete-core-build.v1",
        "translation_provenance": TRANSLATION_PROVENANCE,
        "frozen_manifests": evidence["frozen_manifests"],
        "translation_ledger": evidence["translation_ledger"],
        "inputs": {
            "authority": evidence["authority_inputs"],
            "targets": evidence["target_inputs"],
            "target_only_support": evidence["target_only_inputs"],
            "licenses": evidence["license_inputs"],
            "runtime": evidence["runtime_inputs"],
            "generated": evidence["generated_inputs"],
        },
        "dependency_closure": evidence["dependency_closure"],
        "bounded_text_corrections": list(BOUNDED_TEXT_CORRECTIONS),
        "bounded_reference_corrections": list(BOUNDED_REFERENCE_CORRECTIONS),
        "protected_math_corrections": list(PROTECTED_MATH_CORRECTIONS),
        "transport_hardening": list(TRANSPORT_HARDENING),
        "reader_customizations": evidence["reader_customizations"],
        "reader": {
            "directory": OUTPUT.relative_to(ROOT).as_posix(),
            "manifest_path": MANIFEST.relative_to(ROOT).as_posix(),
            "manifest_bytes": len(reader_manifest),
            "manifest_sha256": sha256_bytes(reader_manifest),
            "file_count": len(rows),
            "total_bytes": sum(size for _, size, _ in rows),
            "files": [
                {"relative_path": rel, "bytes": size, "sha256": sha}
                for rel, size, sha in rows
            ],
        },
        "scripts": {
            "build": _script_record(Path(__file__).resolve()),
            "qa": _script_record(QA_SCRIPT),
        },
    }


def clean_output() -> None:
    output_absolute, output_relative = _under_root(OUTPUT)
    if output_relative.as_posix() != "build/html-id":
        raise RuntimeError(f"refusing unsafe output target: {output_absolute}")
    make_directory(BUILD_DIR)
    ensure_write_target(MANIFEST)
    ensure_write_target(BUILD_RECEIPT)
    if _lexists(OUTPUT):
        assert_no_reparse_components(OUTPUT)
        info = os.lstat(OUTPUT)
        if not stat.S_ISDIR(info.st_mode):
            raise RuntimeError(f"reader output is not a directory: {OUTPUT}")
        secure_tree_files(OUTPUT)
        shutil.rmtree(OUTPUT)
    make_directory(OUTPUT)


def build() -> dict[str, Any]:
    payload, evidence = collect_inputs()
    clean_output()
    for rel, data in payload.items():
        target = OUTPUT / Path(rel.as_posix())
        make_directory(target.parent)
        if _lexists(target):
            raise RuntimeError(f"reader destination unexpectedly exists: {target}")
        write_regular(target, data)
    rows = canonical_rows(OUTPUT)
    reader_manifest = manifest_bytes(rows)
    write_regular(MANIFEST, reader_manifest)
    receipt = expected_receipt(evidence, rows, reader_manifest)
    write_regular(BUILD_RECEIPT, canonical_json_bytes(receipt))
    return check()


def check(*, verbose: bool = True) -> dict[str, Any]:
    payload, evidence = collect_inputs()
    if not _lexists(OUTPUT):
        raise RuntimeError("reader output is absent")
    rows = canonical_rows(OUTPUT)
    actual = {PurePosixPath(rel): (size, sha) for rel, size, sha in rows}
    if set(actual) != set(payload):
        missing = sorted(str(path) for path in set(payload) - set(actual))
        extra = sorted(str(path) for path in set(actual) - set(payload))
        raise RuntimeError(f"reader file-set mismatch; missing={missing}; extra={extra}")
    for rel, expected in payload.items():
        target = OUTPUT / Path(rel.as_posix())
        data = read_regular(target, reject_hardlinks=True)
        if data != expected:
            raise RuntimeError(f"reader byte mismatch: {rel}")

    expected_manifest = manifest_bytes(rows)
    actual_manifest = read_regular(MANIFEST, reject_hardlinks=True)
    if actual_manifest != expected_manifest:
        raise RuntimeError("reader manifest is stale or noncanonical")

    expected_build_receipt = canonical_json_bytes(expected_receipt(evidence, rows, expected_manifest))
    actual_build_receipt = read_regular(BUILD_RECEIPT, reject_hardlinks=True)
    if actual_build_receipt != expected_build_receipt:
        raise RuntimeError("complete-core build receipt is stale or noncanonical")

    summary = {
        "file_count": len(rows),
        "total_bytes": sum(size for _, size, _ in rows),
        "manifest_bytes": len(expected_manifest),
        "manifest_sha256": sha256_bytes(expected_manifest),
        "build_receipt_bytes": len(actual_build_receipt),
        "build_receipt_sha256": sha256_bytes(actual_build_receipt),
    }
    if verbose:
        print(
            f"PASS build: {summary['file_count']} reader files / "
            f"{summary['total_bytes']} bytes / manifest {summary['manifest_sha256']} / "
            f"receipt {summary['build_receipt_sha256']}"
        )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only:
        check()
    else:
        build()


if __name__ == "__main__":
    main()
