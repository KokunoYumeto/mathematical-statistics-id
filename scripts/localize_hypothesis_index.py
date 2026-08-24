#!/usr/bin/env python3
"""Create the bounded id-ID Hypothesis Testing chapter-index target."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "hypothesis" / "index.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "hypothesis" / "index.html"
SOURCE_URL = "https://www.randomservices.org/random/hypothesis/index.html"
SOURCE_SHA256 = "4965a9bfd13b94d932cdd44268b3322078f1e9fce934173c84e170c6a6d6ed1f"
EXPECTED_SOURCE_LINES = 121


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Pengujian Hipotesis</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, uji hipotesis, model normal satu sampel, model normal dua sampel, model Bernoulli, uji rasio kemungkinan, uji khi-kuadrat">''',
    23: r'''\t\t<li class="child"><a href="../foundations/index.html" title="Dasar-Dasar">0</a></li>''',
    24: r'''\t\t<li class="child"><a href="../prob/index.html" title="Ruang Probabilitas">1</a></li>''',
    25: r'''\t\t<li class="child"><a href="../dist/index.html" title="Distribusi">2</a></li>''',
    26: r'''\t\t<li class="child"><a href="../expect/index.html" title="Nilai Harapan">3</a></li>''',
    27: r'''\t\t<li class="child"><a href="../special/index.html" title="Distribusi Khusus">4</a></li>''',
    28: r'''\t\t<li class="child"><a href="../sample/index.html" title="Sampel Acak">5</a></li>''',
    29: r'''\t\t<li class="child"><a href="../point/index.html" title="Pendugaan Titik">6</a></li>''',
    30: r'''\t\t<li class="child"><a href="../interval/index.html" title="Pendugaan Himpunan">7</a></li>''',
    32: r'''\t\t<li class="child"><a href="../buffon/index.html" title="Model Geometris">9</a></li>''',
    33: r'''\t\t<li class="child"><a href="../bernoulli/index.html" title="Percobaan Bernoulli">10</a></li>''',
    34: r'''\t\t<li class="child"><a href="../urn/index.html" title="Model Pengambilan Sampel Hingga">11</a></li>''',
    35: r'''\t\t<li class="child"><a href="../games/index.html" title="Permainan Untung-untungan">12</a></li>''',
    36: r'''\t\t<li class="child"><a href="../poisson/index.html" title="Proses Poisson">13</a></li>''',
    37: r'''\t\t<li class="child"><a href="../renewal/index.html" title="Proses Pembaruan">14</a></li>''',
    38: r'''\t\t<li class="child"><a href="../markov/index.html" title="Proses Markov">15</a></li>''',
    39: r'''\t\t<li class="child"><a href="../martingales/index.html" title="Martingal">16</a></li>''',
    40: r'''\t\t<li class="child"><a href="../brown/index.html" title="Gerak Brown">17</a></li>''',
    42: r'''\t<h1 id="o006.random.hypothesis.index.chapter">8. Pengujian Hipotesis</h1>''',
    45: r'''<h4 id="o006.random.hypothesis.index.summary">Ringkasan</h4>''',
    47: r'''<p>Pengujian hipotesis adalah proses memilih di antara hipotesis-hipotesis yang bersaing mengenai suatu distribusi probabilitas, berdasarkan data yang diamati dari distribusi tersebut. Topik ini merupakan pokok inti dalam statistika matematis dan, sesungguhnya, bagian mendasar dari bahasa statistika. Dalam bab ini, kita mempelajari dasar-dasar pengujian hipotesis dan menelaah uji hipotesis dalam beberapa model parametrik terpenting: model normal dan model Bernoulli.</p>''',
    49: r'''<h4 id="o006.random.hypothesis.index.topics">Topik</h4>''',
    52: r'''\t<li><a href="Introduction.html">Pendahuluan</a></li>''',
    53: r'''\t<li><a href="Normal.html">Pengujian pada Model Normal</a></li>''',
    54: r'''\t<li><a href="Bernoulli.html">Pengujian pada Model Bernoulli</a></li>''',
    55: r'''\t<li><a href="BivariateNormal.html">Pengujian pada Model Normal Dua Sampel</a></li>''',
    56: r'''\t<li><a href="Likelihood.html">Uji Rasio Kemungkinan</a></li>''',
    57: r'''\t<li><a href="ChiSquare.html">Uji Khi-Kuadrat</a></li>''',
    60: r'''<h4 id="o006.random.hypothesis.index.apps">Aplikasi</h4>''',
    63: r'''\t<li><a href="JavaScript:openAncillary('../apps/MeanTest.html')" class="ancillary">Eksperimen Uji Rata-Rata</a></li>''',
    64: r'''\t<li><a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">Eksperimen Uji Proporsi</a></li>''',
    65: r'''\t<li><a href="JavaScript:openAncillary('../apps/VarianceTestExperiment.html')" class="ancillary">Eksperimen Uji Varians</a></li>''',
    66: r'''\t<li><a href="JavaScript:openAncillary('../apps/DiceFit.html')" class="ancillary">Eksperimen Kecocokan Dadu</a></li>''',
    67: r'''\t<li><a href="JavaScript:openAncillary('../apps/SignTest.html')" class="ancillary">Eksperimen Uji Tanda</a></li>''',
    68: r'''\t<li><a href="JavaScript:openAncillary('../apps/ProbabilityPlot.html')" class="ancillary">Eksperimen Plot Probabilitas</a></li>''',
    69: r'''\t<li><a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">Aplikasi Kuantil</a></li>''',
    72: r'''<h4 id="o006.random.hypothesis.index.sources-resources">Sumber dan Sumber Daya</h4>''',
    75: r'''\t<li><a href="http://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt" target="external" class="external">Introduction to Probability and Mathematical Statistics</a>. Lee J Bain dan Max Engelhardt</li>''',
    76: r'''\t<li><a href="http://www.google.com/search?q=Statistical+Inference+Casella+Berger" target="external" class="external">Statistical Inference</a>. George Casella dan Roger L Berger</li>''',
    77: r'''\t<li><a href="http://www.google.com/search?q=Statistics,Freedman,Pisani,Purves" target="external" class="external">Statistics</a>. David Freedman, Robert Pisani, dan Robert Purves</li>''',
    78: r'''\t<li><a href="http://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx" target="external" class="external">An Introduction to Mathematical Statistics and Its Applications</a>. Richard J Larsen dan Morris L Marx</li>''',
    79: r'''\t<li><a href="http://www.google.com/search?q=Elementary+Statistics,Triola" target="external" class="external">Elementary Statistics</a>. Mario Triola</li>''',
    80: r'''\t<li><a href="http://www.google.com/search?q=Introductory+Statistics,Weiss" target="external" class="external">Introductory Statistics</a>. Neil A Weiss</li>''',
    81: r'''\t<li><a href="https://en.wikipedia.org/wiki/Portal:Statistics" class="external" target="external">Portal statistika Wikipedia</a></li>''',
    82: r'''\t<li><a href="http://mathworld.wolfram.com/topics/ProbabilityandStatistics.html" class="external" target="external">Artikel Wolfram MathWorld tentang probabilitas dan statistika</a></li>''',
    85: r'''<h4 id="o006.random.hypothesis.index.quote">Kutipan</h4>''',
    87: r'''<ul class="quote" title="Kutipan">''',
    88: r'''\t<li><q>Kita harus berhati-hati agar tidak mencampuradukkan data dengan abstraksi yang kita gunakan untuk menganalisisnya.</q>&mdash;<a href="JavaScript:openAncillary('../biographies/James.html')" class="ancillary" title="Buka sketsa biografis">William James</a></li>''',
    94: r'''\t\t<li class="child"><a href="../foundations/index.html" title="Dasar-Dasar">0</a></li>''',
    95: r'''\t\t<li class="child"><a href="../prob/index.html" title="Ruang Probabilitas">1</a></li>''',
    96: r'''\t\t<li class="child"><a href="../dist/index.html" title="Distribusi">2</a></li>''',
    97: r'''\t\t<li class="child"><a href="../expect/index.html" title="Nilai Harapan">3</a></li>''',
    98: r'''\t\t<li class="child"><a href="../special/index.html" title="Distribusi Khusus">4</a></li>''',
    99: r'''\t\t<li class="child"><a href="../sample/index.html" title="Sampel Acak">5</a></li>''',
    100: r'''\t\t<li class="child"><a href="../point/index.html" title="Pendugaan Titik">6</a></li>''',
    101: r'''\t\t<li class="child"><a href="../interval/index.html" title="Pendugaan Himpunan">7</a></li>''',
    103: r'''\t\t<li class="child"><a href="../buffon/index.html" title="Model Geometris">9</a></li>''',
    104: r'''\t\t<li class="child"><a href="../bernoulli/index.html" title="Percobaan Bernoulli">10</a></li>''',
    105: r'''\t\t<li class="child"><a href="../urn/index.html" title="Model Pengambilan Sampel Hingga">11</a></li>''',
    106: r'''\t\t<li class="child"><a href="../games/index.html" title="Permainan Untung-untungan">12</a></li>''',
    107: r'''\t\t<li class="child"><a href="../poisson/index.html" title="Proses Poisson">13</a></li>''',
    108: r'''\t\t<li class="child"><a href="../renewal/index.html" title="Proses Pembaruan">14</a></li>''',
    109: r'''\t\t<li class="child"><a href="../markov/index.html" title="Proses Markov">15</a></li>''',
    110: r'''\t\t<li class="child"><a href="../martingales/index.html" title="Martingal">16</a></li>''',
    111: r'''\t\t<li class="child"><a href="../brown/index.html" title="Gerak Brown">17</a></li>''',
    114: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    115: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    116: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/Basic.js": "../Basic.js",
    "https://www.randomservices.org/random/sample/index.html": "../sample/index.html",
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/sample/Mean.html": "../sample/Mean.html",
    "https://www.randomservices.org/random/sample/LLN.html": "../sample/LLN.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
    "https://www.randomservices.org/random/sample/OrderStatistics.html": "../sample/OrderStatistics.html",
    "https://www.randomservices.org/random/sample/Covariance.html": "../sample/Covariance.html",
    "https://www.randomservices.org/random/sample/Normal.html": "../sample/Normal.html",
    "https://www.randomservices.org/random/point/index.html": "../point/index.html",
    "https://www.randomservices.org/random/point/Estimators.html": "../point/Estimators.html",
    "https://www.randomservices.org/random/point/Moments.html": "../point/Moments.html",
    "https://www.randomservices.org/random/point/Likelihood.html": "../point/Likelihood.html",
    "https://www.randomservices.org/random/point/Bayes.html": "../point/Bayes.html",
    "https://www.randomservices.org/random/point/Unbiased.html": "../point/Unbiased.html",
    "https://www.randomservices.org/random/point/Sufficient.html": "../point/Sufficient.html",
    "https://www.randomservices.org/random/interval/index.html": "../interval/index.html",
    "https://www.randomservices.org/random/interval/Introduction.html": "../interval/Introduction.html",
    "https://www.randomservices.org/random/interval/Normal.html": "../interval/Normal.html",
    "https://www.randomservices.org/random/interval/Bernoulli.html": "../interval/Bernoulli.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "../interval/BivariateNormal.html",
    "https://www.randomservices.org/random/interval/Bayes.html": "../interval/Bayes.html",
    "https://www.randomservices.org/random/hypothesis/index.html": "index.html",
    "https://www.randomservices.org/random/hypothesis/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/hypothesis/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/hypothesis/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/hypothesis/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/hypothesis/Likelihood.html": "Likelihood.html",
    "https://www.randomservices.org/random/hypothesis/ChiSquare.html": "ChiSquare.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan atau sedang diselesaikan dalam bab ini ke edisi lokal, pengalihan tautan inti lain ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, serta koreksi terbatas terhadap kekeliruan bibliografis yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t\t<p>Provenans terjemahan: OpenAI Codex gpt-5.6-sol, Ultra. Seluruh kredit bagi sumber, penulis, dan kontributor manusia tetap dipertahankan.</p>
\t</section>'''


def materialize_indentation(value: str) -> str:
    return re.sub(
        r"^(?:\\t)+",
        lambda match: "\t" * (len(match.group(0)) // 2),
        value,
        flags=re.MULTILINE,
    )


def replace_exact_line(lines: list[str], line_number: int, replacement_raw: str) -> None:
    original = lines[line_number - 1]
    ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
    lines[line_number - 1] = materialize_indentation(replacement_raw) + ending


def convert_href(raw_href: str) -> str:
    if raw_href.startswith("#"):
        return raw_href
    ancillary = re.fullmatch(r"JavaScript:openAncillary\('([^']+)'\)", raw_href, re.IGNORECASE)
    candidate = ancillary.group(1) if ancillary else raw_href
    absolute = urljoin(SOURCE_URL, candidate)
    base, fragment = urldefrag(absolute)
    result = LOCAL_URLS.get(base, base)
    result = result.replace("http://www.randomservices.org/", "https://www.randomservices.org/")
    result = result.replace("http://www.google.com/", "https://www.google.com/")
    result = result.replace("http://mathworld.wolfram.com/", "https://mathworld.wolfram.com/")
    return result + (f"#{fragment}" if fragment else "")


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    lines = source_bytes.decode("utf-8").splitlines(keepends=True)
    if len(lines) != EXPECTED_SOURCE_LINES:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")

    for line_number, replacement in sorted(LINE_REPLACEMENTS.items()):
        replace_exact_line(lines, line_number, replacement)

    rendered = "".join(lines)
    rendered = re.sub(
        r'href="([^"]+)"',
        lambda match: f'href="{convert_href(match.group(1))}"',
        rendered,
    )
    marker = "</footer>"
    if rendered.count(marker) != 1:
        raise RuntimeError("footer marker count changed")
    rendered = rendered.replace(marker, materialize_indentation(EDITION_NOTICE) + "\n" + marker, 1)

    required_ids = {
        "o006.random.hypothesis.index.chapter",
        "o006.random.hypothesis.index.summary",
        "o006.random.hypothesis.index.topics",
        "o006.random.hypothesis.index.apps",
        "o006.random.hypothesis.index.sources-resources",
        "o006.random.hypothesis.index.quote",
    }
    found_ids = set(re.findall(r'\bid="([^"]+)"', rendered))
    if found_ids != required_ids:
        raise RuntimeError(f"stable-ID mismatch: {sorted(found_ids)}")
    for phrase in (
        'lang="en"',
        "JavaScript:openAncillary",
        "http://",
        ">Hypothesis Testing<",
        ">Summary<",
        ">Topics<",
        ">Apps<",
        ">Sources and Resources<",
        ">Data Sets<",
        "> Biographies<",
        "Open biographical sketch",
        "Rober L Berger",
        ">quantile app<",
        "Mean Test Experiment",
        "Proportion Test Experiment",
        "Variance Test Experiment",
        "Dice Goodness of Fit Experiment",
        "Sign Test Experiment",
        "Probability Plot Experiment",
    ):
        if phrase in rendered:
            raise RuntimeError(f"unresolved reader-facing/source defect remains: {phrase}")

    output = rendered.encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(output)
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: "
        f"{len(output)} bytes / sha256 {hashlib.sha256(output).hexdigest()}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
