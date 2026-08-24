#!/usr/bin/env python3
"""Create the bounded id-ID Set Estimation chapter-index target."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "interval" / "index.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "interval" / "index.html"
SOURCE_URL = "https://www.randomservices.org/random/interval/index.html"
SOURCE_SHA256 = "85fcad0292636fbae0935ebb775a87b9e4dbdf33692b5e2823b353163d168403"
EXPECTED_SOURCE_LINES = 117


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Pendugaan Interval</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, pendugaan himpunan, pendugaan interval, model normal satu sampel, model normal dua sampel, model Bernoulli, pendugaan Bayes">''',
    23: r'''\t\t<li class="child"><a href="../foundations/index.html" title="Dasar-Dasar">0</a></li>''',
    24: r'''\t\t<li class="child"><a href="../prob/index.html" title="Ruang Probabilitas">1</a></li>''',
    25: r'''\t\t<li class="child"><a href="../dist/index.html" title="Distribusi">2</a></li>''',
    26: r'''\t\t<li class="child"><a href="../expect/index.html" title="Nilai Harapan">3</a></li>''',
    27: r'''\t\t<li class="child"><a href="../special/index.html" title="Distribusi Khusus">4</a></li>''',
    28: r'''\t\t<li class="child"><a href="../sample/index.html" title="Sampel Acak">5</a></li>''',
    29: r'''\t\t<li class="child"><a href="../point/index.html" title="Pendugaan Titik">6</a></li>''',
    31: r'''\t\t<li class="child"><a href="../hypothesis/index.html" title="Pengujian Hipotesis">8</a></li>''',
    32: r'''\t\t<li class="child"><a href="../buffon/index.html" title="Model Geometris">9</a></li>''',
    33: r'''\t\t<li class="child"><a href="../bernoulli/index.html" title="Percobaan Bernoulli">10</a></li>''',
    34: r'''\t\t<li class="child"><a href="../urn/index.html" title="Model Pengambilan Sampel Hingga">11</a></li>''',
    35: r'''\t\t<li class="child"><a href="../games/index.html" title="Permainan Untung-untungan">12</a></li>''',
    36: r'''\t\t<li class="child"><a href="../poisson/index.html" title="Proses Poisson">13</a></li>''',
    37: r'''\t\t<li class="child"><a href="../renewal/index.html" title="Proses Pembaruan">14</a></li>''',
    38: r'''\t\t<li class="child"><a href="../markov/index.html" title="Proses Markov">15</a></li>''',
    39: r'''\t\t<li class="child"><a href="../martingales/index.html" title="Martingal">16</a></li>''',
    40: r'''\t\t<li class="child"><a href="../brown/index.html" title="Gerak Brown">17</a></li>''',
    42: r'''\t<h1 id="o006.random.interval.index.chapter">7. Pendugaan Himpunan</h1>''',
    45: r'''<h4 id="o006.random.interval.index.summary">Ringkasan</h4>''',
    47: r'''<p>Pendugaan himpunan adalah proses membangun suatu himpunan bagian dari ruang parameter berdasarkan data yang diamati dari sebuah distribusi probabilitas. Himpunan bagian tersebut akan memuat nilai parameter yang sebenarnya dengan <dfn>tingkat kepercayaan</dfn> tertentu. Dalam bab ini, kita mengkaji metode dasar pendugaan himpunan dengan menggunakan variabel pivot. Kita mempelajari pendugaan himpunan dalam beberapa model terpenting: model normal satu variabel, model normal dua variabel, dan model Bernoulli.</p>''',
    49: r'''<h4 id="o006.random.interval.index.topics">Topik</h4>''',
    52: r'''\t<li><a href="Introduction.html">Pendahuluan</a></li>''',
    53: r'''\t<li><a href="Normal.html">Pendugaan pada Model Normal</a></li>''',
    54: r'''\t<li><a href="Bernoulli.html">Pendugaan pada Model Bernoulli</a></li>''',
    55: r'''\t<li><a href="BivariateNormal.html">Pendugaan pada Model Normal Dua Sampel</a></li>''',
    56: r'''\t<li><a href="Bayes.html">Pendugaan Himpunan Bayes</a></li>''',
    59: r'''<h4 id="o006.random.interval.index.apps">Aplikasi</h4>''',
    62: r'''\t<li><a href="JavaScript:openAncillary('../apps/MeanEstimate.html')" class="ancillary">Eksperimen Pendugaan Rata-Rata</a></li>''',
    63: r'''\t<li><a href="JavaScript:openAncillary('../apps/ProportionEstimate.html')" class="ancillary">Eksperimen Pendugaan Proporsi</a></li>''',
    64: r'''\t<li><a href="JavaScript:openAncillary('../apps/VarianceEstimate.html')" class="ancillary">Eksperimen Pendugaan Varians</a></li>''',
    65: r'''\t<li><a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">Aplikasi Kuantil</a></li>''',
    68: r'''<h4 id="o006.random.interval.index.sources-resources">Sumber dan Sumber Daya</h4>''',
    71: r'''\t<li><a href="http://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt" target="external" class="external">Introduction to Probability and Mathematical Statistics</a>. Lee J Bain dan Max Engelhardt</li>''',
    72: r'''\t<li><a href="http://www.google.com/search?q=Statistical+Inference+Casella+Berger" target="external" class="external">Statistical Inference</a>. George Casella dan Roger L Berger</li>''',
    73: r'''\t<li><a href="http://www.google.com/search?q=Statistics,Freedman,Pisani,Purves" target="external" class="external">Statistics</a>. David Freedman, Robert Pisani, dan Robert Purves</li>''',
    74: r'''\t<li><a href="http://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx" target="external" class="external">An Introduction to Mathematical Statistics and Its Applications</a>. Richard J Larsen dan Morris L Marx</li>''',
    75: r'''\t<li><a href="http://www.google.com/search?q=Elementary+Statistics,Triola" target="external" class="external">Elementary Statistics</a>. Mario Triola</li>''',
    76: r'''\t<li><a href="http://www.google.com/search?q=Introductory+Statistics,Weiss" target="external" class="external">Introductory Statistics</a>. Neil A Weiss</li>''',
    77: r'''\t<li><a href="https://en.wikipedia.org/wiki/Portal:Statistics" class="external" target="external">Portal statistika Wikipedia</a></li>''',
    78: r'''\t<li><a href="http://mathworld.wolfram.com/topics/ProbabilityandStatistics.html" class="external" target="external">Artikel Wolfram MathWorld tentang probabilitas dan statistika</a></li>''',
    81: r'''<h4 id="o006.random.interval.index.quote">Kutipan</h4>''',
    83: r'''<ul class="quote" title="Kutipan">''',
    84: r'''\t<li><q>Penemuan besar memecahkan masalah besar, tetapi dalam penyelesaian setiap masalah terdapat secuil penemuan.</q>&mdash;<a href="JavaScript:openAncillary('../biographies/Polya.html')" class="ancillary" title="Buka sketsa biografis">George Pólya</a></li>''',
    90: r'''\t\t<li class="child"><a href="../foundations/index.html" title="Dasar-Dasar">0</a></li>''',
    91: r'''\t\t<li class="child"><a href="../prob/index.html" title="Ruang Probabilitas">1</a></li>''',
    92: r'''\t\t<li class="child"><a href="../dist/index.html" title="Distribusi">2</a></li>''',
    93: r'''\t\t<li class="child"><a href="../expect/index.html" title="Nilai Harapan">3</a></li>''',
    94: r'''\t\t<li class="child"><a href="../special/index.html" title="Distribusi Khusus">4</a></li>''',
    95: r'''\t\t<li class="child"><a href="../sample/index.html" title="Sampel Acak">5</a></li>''',
    96: r'''\t\t<li class="child"><a href="../point/index.html" title="Pendugaan Titik">6</a></li>''',
    98: r'''\t\t<li class="child"><a href="../hypothesis/index.html" title="Pengujian Hipotesis">8</a></li>''',
    99: r'''\t\t<li class="child"><a href="../buffon/index.html" title="Model Geometris">9</a></li>''',
    100: r'''\t\t<li class="child"><a href="../bernoulli/index.html" title="Percobaan Bernoulli">10</a></li>''',
    101: r'''\t\t<li class="child"><a href="../urn/index.html" title="Model Pengambilan Sampel Hingga">11</a></li>''',
    102: r'''\t\t<li class="child"><a href="../games/index.html" title="Permainan Untung-untungan">12</a></li>''',
    103: r'''\t\t<li class="child"><a href="../poisson/index.html" title="Proses Poisson">13</a></li>''',
    104: r'''\t\t<li class="child"><a href="../renewal/index.html" title="Proses Pembaruan">14</a></li>''',
    105: r'''\t\t<li class="child"><a href="../markov/index.html" title="Proses Markov">15</a></li>''',
    106: r'''\t\t<li class="child"><a href="../martingales/index.html" title="Martingal">16</a></li>''',
    107: r'''\t\t<li class="child"><a href="../brown/index.html" title="Gerak Brown">17</a></li>''',
    110: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    111: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    112: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/Basic.js": "../Basic.js",
    "https://www.randomservices.org/random/sample/index.html": "../sample/index.html",
    "https://www.randomservices.org/random/point/index.html": "../point/index.html",
    "https://www.randomservices.org/random/interval/index.html": "index.html",
    "https://www.randomservices.org/random/interval/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/interval/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/interval/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/interval/Bayes.html": "Bayes.html",
    "https://www.randomservices.org/random/hypothesis/index.html": "../hypothesis/index.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, serta koreksi terbatas terhadap kekeliruan bibliografis dan label yang dicatat dalam daftar koreksi edisi.</p>
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
    for phrase in (
        'lang="en"',
        "JavaScript:openAncillary",
        "http://",
        ">Set Estimation<",
        ">Summary<",
        ">Topics<",
        ">Apps<",
        ">Sources and Resources<",
        ">Data Sets<",
        "> Biographies<",
        "Rober L Berger",
        "Estimation the Normal Model",
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
