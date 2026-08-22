#!/usr/bin/env python3
"""Create the bounded id-ID Point Estimation chapter-index target."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "point" / "index.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "point" / "index.html"
SOURCE_URL = "https://www.randomservices.org/random/point/index.html"
SOURCE_SHA256 = "b0e3e9e5f55bfd4ebac0047dafff725628d6a0ca6e638d7a2847095b311d637c"
EXPECTED_SOURCE_LINES = 120


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''	<title>Pendugaan Titik</title>''',
    9: r'''	<meta name="keywords" content="probabilitas, statistika, pendugaan titik, metode momen, metode kemungkinan maksimum, penduga tak bias, penduga Bayes, statistik cukup, statistik lengkap, statistik ancillary">''',
    23: r'''		<li class="child"><a href="../foundations/index.html" title="Dasar-Dasar">0</a></li>''',
    24: r'''		<li class="child"><a href="../prob/index.html" title="Ruang Probabilitas">1</a></li>''',
    25: r'''		<li class="child"><a href="../dist/index.html" title="Distribusi">2</a></li>''',
    26: r'''		<li class="child"><a href="../expect/index.html" title="Nilai Harapan">3</a></li>''',
    27: r'''		<li class="child"><a href="../special/index.html" title="Distribusi Khusus">4</a></li>''',
    28: r'''		<li class="child"><a href="../sample/index.html" title="Sampel Acak">5</a></li>''',
    30: r'''		<li class="child"><a href="../interval/index.html" title="Pendugaan Himpunan">7</a></li>''',
    31: r'''		<li class="child"><a href="../hypothesis/index.html" title="Pengujian Hipotesis">8</a></li>''',
    32: r'''		<li class="child"><a href="../buffon/index.html" title="Model Geometris">9</a></li>''',
    33: r'''		<li class="child"><a href="../bernoulli/index.html" title="Percobaan Bernoulli">10</a></li>''',
    34: r'''		<li class="child"><a href="../urn/index.html" title="Model Pengambilan Sampel Hingga">11</a></li>''',
    35: r'''		<li class="child"><a href="../games/index.html" title="Permainan Untung-untungan">12</a></li>''',
    36: r'''		<li class="child"><a href="../poisson/index.html" title="Proses Poisson">13</a></li>''',
    37: r'''		<li class="child"><a href="../renewal/index.html" title="Proses Pembaruan">14</a></li>''',
    38: r'''		<li class="child"><a href="../markov/index.html" title="Proses Markov">15</a></li>''',
    39: r'''		<li class="child"><a href="../martingales/index.html" title="Martingal">16</a></li>''',
    40: r'''		<li class="child"><a href="../brown/index.html" title="Gerak Brown">17</a></li>''',
    42: r'''	<h1 id="o006.random.point.index.chapter">6. Pendugaan Titik</h1>''',
    45: r'''<h4 id="o006.random.point.index.summary">Ringkasan</h4>''',
    47: r'''<p>Pendugaan titik adalah proses menduga parameter suatu distribusi probabilitas berdasarkan data yang diamati dari distribusi tersebut. Topik ini merupakan salah satu pokok utama statistika matematis. Dalam bab ini, kita akan mengkaji metode pendugaan titik yang paling umum: metode momen, metode kemungkinan maksimum, dan penduga Bayes. Kita juga mempelajari sifat-sifat penting penduga, termasuk kecukupan dan kelengkapan, serta pertanyaan mendasar apakah suatu penduga merupakan penduga terbaik yang dapat diperoleh.</p>''',
    49: r'''<h4 id="o006.random.point.index.topics">Topik</h4>''',
    52: r'''	<li><a href="Estimators.html">Penduga</a></li>''',
    53: r'''	<li><a href="Moments.html">Metode Momen</a></li>''',
    54: r'''	<li><a href="Likelihood.html">Kemungkinan Maksimum</a></li>''',
    55: r'''	<li><a href="Bayes.html">Pendugaan Bayes</a></li>''',
    56: r'''	<li><a href="Unbiased.html">Penduga Tak Bias Terbaik</a></li>''',
    57: r'''	<li><a href="Sufficient.html">Statistik Cukup, Lengkap, dan Ancilar</a></li>''',
    60: r'''<h4 id="o006.random.point.index.apps">Aplikasi</h4>''',
    63: r'''	<li><a href="JavaScript:openAncillary('../apps/NormalEstimate.html')" class="ancillary">Eksperimen Pendugaan pada Distribusi Normal</a></li>''',
    64: r'''	<li><a href="JavaScript:openAncillary('../apps/UniformEstimate.html')" class="ancillary">Eksperimen Pendugaan pada Distribusi Seragam</a></li>''',
    65: r'''	<li><a href="JavaScript:openAncillary('../apps/GammaEstimate.html')" class="ancillary">Eksperimen Pendugaan pada Distribusi Gamma</a></li>''',
    66: r'''	<li><a href="JavaScript:openAncillary('../apps/BetaEstimate.html')" class="ancillary">Eksperimen Pendugaan pada Distribusi Beta</a></li>''',
    67: r'''	<li><a href="JavaScript:openAncillary('../apps/ParetoEstimate.html')" class="ancillary">Eksperimen Pendugaan pada Distribusi Pareto</a></li>''',
    68: r'''	<li><a href="JavaScript:openAncillary('../apps/BetaCoin.html')" class="ancillary">Eksperimen Koin Beta</a></li>''',
    71: r'''<h4 id="o006.random.point.index.sources-resources">Sumber dan Sumber Daya</h4>''',
    74: r'''	<li><a href="http://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt" target="external" class="external">Introduction to Probability and Mathematical Statistics</a>. Lee J Bain dan Max Engelhardt</li>''',
    75: r'''	<li><a href="http://www.google.com/search?q=Statistical+Inference+Casella+Berger" target="external" class="external">Statistical Inference</a>. George Casella dan Roger L Berger</li>''',
    76: r'''	<li><a href="http://www.google.com/search?q=Statistics,Freedman,Pisani,Purves" target="external" class="external">Statistics</a>. David Freedman, Robert Pisani, dan Robert Purves</li>''',
    77: r'''	<li><a href="http://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx" target="external" class="external">An Introduction to Mathematical Statistics and Its Applications</a>. Richard J Larsen dan Morris L Marx</li>''',
    78: r'''	<li><a href="http://www.google.com/search?q=Elementary+Statistics,Triola" target="external" class="external">Elementary Statistics</a>. Mario Triola</li>''',
    79: r'''	<li><a href="http://www.google.com/search?q=Introductory+Statistics,Weiss" target="external" class="external">Introductory Statistics</a>. Neil A Weiss</li>''',
    80: r'''	<li><a href="https://en.wikipedia.org/wiki/Portal:Statistics" class="external" target="external">Portal statistika Wikipedia</a></li>''',
    81: r'''	<li><a href="http://mathworld.wolfram.com/topics/ProbabilityandStatistics.html" class="external" target="external">Artikel Wolfram MathWorld tentang probabilitas dan statistika</a></li>''',
    84: r'''<h4 id="o006.random.point.index.quote">Kutipan</h4>''',
    86: r'''<ul class="quote" title="Kutipan">''',
    87: r'''	<li><q>Jauh lebih baik memperoleh jawaban hampiran atas pertanyaan yang tepat, yang sering kali samar, daripada jawaban eksak atas pertanyaan yang keliru, yang selalu dapat dirumuskan dengan tepat.</q>&mdash;<a href="JavaScript:openAncillary('../biographies/Tukey.html')" class="ancillary">John Tukey</a>, <cite>Annals of Mathematical Statistics</cite>, <strong>33</strong> (1962).</li>''',
    93: r'''		<li class="child"><a href="../foundations/index.html" title="Dasar-Dasar">0</a></li>''',
    94: r'''		<li class="child"><a href="../prob/index.html" title="Ruang Probabilitas">1</a></li>''',
    95: r'''		<li class="child"><a href="../dist/index.html" title="Distribusi">2</a></li>''',
    96: r'''		<li class="child"><a href="../expect/index.html" title="Nilai Harapan">3</a></li>''',
    97: r'''		<li class="child"><a href="../special/index.html" title="Distribusi Khusus">4</a></li>''',
    98: r'''		<li class="child"><a href="../sample/index.html" title="Sampel Acak">5</a></li>''',
    100: r'''		<li class="child"><a href="../interval/index.html" title="Pendugaan Himpunan">7</a></li>''',
    101: r'''		<li class="child"><a href="../hypothesis/index.html" title="Pengujian Hipotesis">8</a></li>''',
    102: r'''		<li class="child"><a href="../buffon/index.html" title="Model Geometris">9</a></li>''',
    103: r'''		<li class="child"><a href="../bernoulli/index.html" title="Percobaan Bernoulli">10</a></li>''',
    104: r'''		<li class="child"><a href="../urn/index.html" title="Model Pengambilan Sampel Hingga">11</a></li>''',
    105: r'''		<li class="child"><a href="../games/index.html" title="Permainan Untung-untungan">12</a></li>''',
    106: r'''		<li class="child"><a href="../poisson/index.html" title="Proses Poisson">13</a></li>''',
    107: r'''		<li class="child"><a href="../renewal/index.html" title="Proses Pembaruan">14</a></li>''',
    108: r'''		<li class="child"><a href="../markov/index.html" title="Proses Markov">15</a></li>''',
    109: r'''		<li class="child"><a href="../martingales/index.html" title="Martingal">16</a></li>''',
    110: r'''		<li class="child"><a href="../brown/index.html" title="Gerak Brown">17</a></li>''',
    113: r'''		<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    114: r'''		<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    115: r'''		<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/sample/index.html": "../sample/index.html",
    "https://www.randomservices.org/random/point/index.html": "index.html",
    "https://www.randomservices.org/random/point/Estimators.html": "Estimators.html",
    "https://www.randomservices.org/random/point/Moments.html": "Moments.html",
    "https://www.randomservices.org/random/point/Likelihood.html": "Likelihood.html",
    "https://www.randomservices.org/random/point/Bayes.html": "Bayes.html",
    "https://www.randomservices.org/random/point/Unbiased.html": "Unbiased.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, serta koreksi terbatas terhadap kekeliruan bibliografis yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
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
    replacement = materialize_indentation(replacement_raw)
    lines[line_number - 1] = replacement + ending


def convert_href(raw_href: str) -> str:
    if raw_href.startswith("#"):
        return raw_href
    ancillary = re.fullmatch(r"JavaScript:openAncillary\('([^']+)'\)", raw_href, re.IGNORECASE)
    candidate = ancillary.group(1) if ancillary else raw_href
    absolute = urljoin(SOURCE_URL, candidate)
    base, fragment = urldefrag(absolute)
    if base in LOCAL_URLS:
        result = LOCAL_URLS[base]
    else:
        result = base.replace("http://www.randomservices.org/", "https://www.randomservices.org/")
        result = result.replace("http://www.google.com/", "https://www.google.com/")
        result = result.replace("http://mathworld.wolfram.com/", "https://mathworld.wolfram.com/")
    return result + (f"#{fragment}" if fragment else "")


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    text = source_bytes.decode("utf-8")
    lines = text.splitlines(keepends=True)
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
    rendered = rendered.replace(
        marker, materialize_indentation(EDITION_NOTICE) + "\n" + marker, 1
    )

    if 'lang="en"' in rendered:
        raise RuntimeError("English locale metadata remains")
    if "JavaScript:openAncillary" in rendered:
        raise RuntimeError("JavaScript ancillary navigation remains")
    if "http://" in rendered:
        raise RuntimeError("insecure HTTP navigation remains")
    for phrase in (
        ">Point Estimation<",
        ">Summary<",
        ">Topics<",
        ">Apps<",
        ">Sources and Resources<",
        'title="Quote"',
        ">Data Sets<",
        "> Biographies<",
    ):
        if phrase in rendered:
            raise RuntimeError(f"untranslated reader-facing phrase remains: {phrase}")

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
