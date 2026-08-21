#!/usr/bin/env python3
"""Build and verify the first deterministic O006 id-ID HTML reader unit."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import re
import shutil
import stat
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "id-ID"
AUTHORITY = ROOT / "authority" / "upstream"
SOURCE_MANIFEST = ROOT / "authority" / "SOURCE_URL_MANIFEST.csv"
SOURCE_FREEZE_RECEIPT = ROOT / "authority" / "SOURCE_FREEZE_RECEIPT.json"
LICENSE_ROOT = ROOT / "authority" / "component-licenses"
LICENSE_MANIFEST = LICENSE_ROOT / "URL_MANIFEST.csv"
LICENSE_FREEZE_RECEIPT = LICENSE_ROOT / "FREEZE_RECEIPT.json"
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

TARGETS = (
    PurePosixPath("random/sample/index.html"),
    PurePosixPath("random/sample/Introduction.html"),
    PurePosixPath("random/sample/Mean.html"),
    PurePosixPath("random/sample/LLN.html"),
    PurePosixPath("random/sample/CLT.html"),
)

# Screen.css references all of these local assets. Keeping the complete exact set
# makes offline-link closure machine-checkable for this unit.
SUPPORT = (
    PurePosixPath("random/Screen.css"),
    PurePosixPath("random/Basic.js"),
    PurePosixPath("random/icons/Icon.svg"),
    PurePosixPath("random/icons/Plus.svg"),
    PurePosixPath("random/icons/Minus.svg"),
    PurePosixPath("random/icons/DieBlue5.svg"),
    PurePosixPath("random/icons/DieGreen5.svg"),
    PurePosixPath("random/icons/DieRed5.svg"),
    PurePosixPath("random/icons/Reset.svg"),
    PurePosixPath("random/icons/Run.svg"),
    PurePosixPath("random/icons/Step.svg"),
    PurePosixPath("random/icons/Stop.svg"),
    PurePosixPath("random/sample/DotPlot.png"),
    PurePosixPath("random/sample/EmpiricalPDF.png"),
    PurePosixPath("random/sample/DiscreteDistribution.png"),
    PurePosixPath("random/sample/ContinuousDistribution.png"),
    PurePosixPath("random/sample/Histogram.png"),
    PurePosixPath("MathJax/tex-svg.js"),
)

# Build-layer-only readability repair.  The translated HTML stays byte-identical
# to its audited target while the reader's existing stylesheet receives one
# exact, deterministic appendix.  The desktop cap keeps mathematical prose
# comfortably readable without narrowing tables to a phone-like column; the
# mobile branch remains fluid and contains wide mathematical surfaces locally.
READABLE_REFLOW_CSS = b"""

/* O006 id-ID readable layout v1 (edition build only) */
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
)

PROTECTED_MATH_CORRECTIONS = (
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
        "new": r'''<p class="app">Dalam <a href="https://www.randomservices.org/random/apps/SpecialSimulator.html" class="ancillary">simulator distribusi khusus</a>, pilih distribusi gamma. Variasikan parameter \((k, b)\), lalu perhatikan bentuk fungsi densitas probabilitasnya. Dengan \(k = 10\) dan berbagai nilai \(b\), jalankan eksperimen 1.000 kali dan bandingkan fungsi densitas empiris dengan fungsi densitas probabilitas sebenarnya.</p>''',
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
)

# Reader-facing language inside TeX \text{...} remains protected mathematics:
# these exact substitutions localize words while leaving every operator,
# identifier, delimiter, and formula position unchanged.
MATH_TEXT_LOCALIZATIONS = (
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
        "<title>Statistika Matematis — Bahasa Indonesia</title></head>\n"
        '<body><main><h1>Statistika Matematis</h1>\n'
        '<p><a href="random/sample/index.html">Mulai membaca: Sampel Acak</a></p>\n'
        "<p>Edisi Bahasa Indonesia independen berdasarkan "
        '<a href="https://www.randomservices.org/random/">Random</a> karya Kyle Siegrist. '
        "Terjemahan ini tidak didukung atau disahkan oleh penulis sumber.</p>\n"
        "</main></body></html>\n"
    ).encode("utf-8")


def licences_index() -> bytes:
    return (
        "<!doctype html>\n"
        '<html lang="id-ID"><head><meta charset="utf-8">'
        "<title>Atribusi dan Lisensi</title></head><body><main>\n"
        "<h1>Atribusi dan Lisensi</h1>\n"
        "<p>Sumber utama: Kyle Siegrist, <cite>Random: Probability, Mathematical "
        "Statistics, and Stochastic Processes</cite>. Terjemahan dan perubahan "
        "struktur akses dibuat secara independen; penulis sumber tidak mendukung "
        "atau mengesahkan edisi ini.</p>\n"
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
    for change in PROTECTED_MATH_CORRECTIONS:
        source_text = authority_data[change["page"]].decode("utf-8")
        target_text = target_data[change["page"]].decode("utf-8")
        replacements = int(change["replacements"])
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
    source_rows = _manifest_rows(source_manifest_data, SOURCE_MANIFEST_HEADER, "source manifest")
    license_rows = _manifest_rows(license_manifest_data, LICENSE_MANIFEST_HEADER, "license manifest")

    payload: dict[PurePosixPath, bytes] = {
        PurePosixPath("index.html"): root_index(),
        PurePosixPath("licenses/index.html"): licences_index(),
    }
    authority_inputs: list[dict[str, Any]] = []
    target_inputs: list[dict[str, Any]] = []
    authority_data: dict[str, bytes] = {}
    target_data: dict[str, bytes] = {}

    for rel in TARGETS:
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

        translated = read_regular(SOURCE / Path(rel.as_posix()))
        translated.decode("utf-8")
        payload[rel] = translated
        target_data[rel.as_posix()] = translated
        target_inputs.append(
            {
                "relative_path": rel.as_posix(),
                "bytes": len(translated),
                "sha256": sha256_bytes(translated),
            }
        )

    _validate_target_corrections(authority_data, target_data)

    runtime_data, runtime_input = _runtime_payload()
    if RUNTIME_READER_PATH in payload:
        raise RuntimeError(f"duplicate reader runtime path: {RUNTIME_READER_PATH}")
    payload[RUNTIME_READER_PATH] = runtime_data

    reader_customizations: list[dict[str, Any]] = []
    for rel in SUPPORT:
        row = source_rows.get(rel.as_posix())
        if row is None or row["role"] != "asset":
            raise RuntimeError(f"selected reader support is not an asset manifest row: {rel}")
        if row["url"] != "https://www.randomservices.org/" + rel.as_posix():
            raise RuntimeError(f"selected support URL mismatch: {rel}")
        data, authority_record = _validated_file_record(AUTHORITY, rel, row, purpose="reader_support")
        authority_inputs.append(authority_record)
        reader_data = data
        if rel == PurePosixPath("random/Screen.css"):
            reader_data = data + READABLE_REFLOW_CSS
            reader_customizations.append(
                {
                    "kind": "readable-layout-css-append",
                    "version": "o006-id-readable-layout-v1",
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
        "authority_inputs": sorted(authority_inputs, key=lambda item: item["relative_path"].casefold()),
        "target_inputs": sorted(target_inputs, key=lambda item: item["relative_path"].casefold()),
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
        "schema": "o006.random.first-unit-build.v1",
        "frozen_manifests": evidence["frozen_manifests"],
        "inputs": {
            "authority": evidence["authority_inputs"],
            "targets": evidence["target_inputs"],
            "licenses": evidence["license_inputs"],
            "runtime": evidence["runtime_inputs"],
            "generated": evidence["generated_inputs"],
        },
        "bounded_text_corrections": list(BOUNDED_TEXT_CORRECTIONS),
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
        raise RuntimeError("first-unit build receipt is stale or noncanonical")

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
