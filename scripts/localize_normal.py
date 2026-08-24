#!/usr/bin/env python3
"""Create the bounded id-ID Special Properties of Normal Samples target."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "sample" / "Normal.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "sample" / "Normal.html"
SOURCE_URL = "https://www.randomservices.org/random/sample/Normal.html"
SOURCE_SHA256 = "d9a62017ae3a8488aedac3eceedb15d8b68243ae60894104ab88564ace25ff79"
EXPECTED_SOURCE_LINES = 490
PAGE_ID = "o006.random.sample.normal.page"
ANONYMOUS_F_SIMULATOR_UNIT_ID = "o006.random.sample.normal.unit.special-f-simulator"

MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)


# Every protected change below was independently checked against the displayed
# identity; all other inline/display TeX is restored byte-for-byte.
MATH_CORRECTIONS: dict[tuple[int, int], tuple[str, str]] = {
    (234, 1): (
        r"\(\E\left[(M(\bs{X}) - M(\bs{Y})\right] = \mu - \nu\)",
        r"\(\E\left[M(\bs{X}) - M(\bs{Y})\right] = \mu - \nu\)",
    ),
    (235, 1): (
        r"\(\var\left[(M(\bs{X}) - M(\bs{Y})\right] = \sigma^2 / m + \tau^2 / n\)",
        r"\(\var\left[M(\bs{X}) - M(\bs{Y})\right] = \sigma^2 / m + \tau^2 / n\)",
    ),
    (240, 1): (
        r"\[ Z = \frac{\left[(M(\bs{X}) - M(\bs{Y})\right] - (\mu - \nu)}{\sqrt{\sigma^2 / m + \tau^2 / n}} \]",
        r"\[ Z = \frac{\left[M(\bs{X}) - M(\bs{Y})\right] - (\mu - \nu)}{\sqrt{\sigma^2 / m + \tau^2 / n}} \]",
    ),
    (304, 2): (
        r"\((M(\bs{Y}, S(\bs{Y}))\)",
        r"\((M(\bs{Y}), S(\bs{Y}))\)",
    ),
    (313, 1): (
        r"\(Z / \sqrt{V / (m + n - 2}\)",
        r"\(Z / \sqrt{V / (m + n - 2)}\)",
    ),
    (319, 7): (r"\(\rho \in [0, 1]\)", r"\(\rho \in [-1, 1]\)"),
    (323, 1): (
        r"\(\sigma^3 = \E\left[(X - \mu)^3\right] = 0\)",
        r"\(\sigma_3 = \E\left[(X - \mu)^3\right] = 0\)",
    ),
    (326, 1): (
        r"\(((X_1, Y_1), (X_2, Y_2), \ldots (X_n, Y_n))\)",
        r"\(((X_1, Y_1), (X_2, Y_2), \ldots, (X_n, Y_n))\)",
    ),
    (422, 1): (
        r"\(\P(M \gt 49, S^2 \lt 20))\)",
        r"\(\P(M \gt 49, S^2 \lt 20)\)",
    ),
}


# No raw align/environment corrections are currently registered. Each future
# entry must lock both the exact authority row and its independently verified
# corrected row.
RAW_TEX_CORRECTIONS: dict[int, tuple[str, str]] = {}


# Verified reader-facing translation for the front half only (authority lines
# 1--260). TeX in these rows is protected and restored from authority bytes.
LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Sifat Khusus Sampel Normal</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, sampel acak, distribusi normal, rata-rata sampel, varians sampel, distribusi t Student, distribusi khi-kuadrat, model dua sampel, model bivariat">''',
    35: r'''\t\t<li class="parent"><a href="index.html">5. Sampel Acak</a></li>''',
    36: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    37: r'''\t\t<li class="child"><a href="Mean.html" title="Rata-Rata Sampel">2</a></li>''',
    38: r'''\t\t<li class="child"><a href="LLN.html" title="Hukum Bilangan Besar">3</a></li>''',
    39: r'''\t\t<li class="child"><a href="CLT.html" title="Teorema Limit Pusat">4</a></li>''',
    40: r'''\t\t<li class="child"><a href="Variance.html" title="Varians Sampel">5</a></li>''',
    41: r'''\t\t<li class="child"><a href="OrderStatistics.html" title="Statistik Terurut">6</a></li>''',
    42: r'''\t\t<li class="child"><a href="Covariance.html" title="Korelasi dan Regresi Sampel">7</a></li>''',
    44: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    45: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    47: rf'''\t<h2 id="{PAGE_ID}">8. Sifat Khusus Sampel Normal</h2>''',
    50: r'''<p>Sampel acak dari distribusi normal merupakan kasus khusus terpenting di antara topik-topik dalam bab ini. Seperti yang akan kita lihat, banyak hasil menjadi jauh lebih sederhana ketika distribusi asal sampelnya normal. Selain itu, kita akan menurunkan distribusi sejumlah variabel acak yang dibentuk dari sampel normal dan sangat penting dalam statistika inferensial.</p>''',
    52: r'''<h3 id="one">Model Satu Sampel</h3>''',
    54: r'''<p>Misalkan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan <a href="Introduction.html">sampel acak</a> dari <a href="../special/Normal.html">distribusi normal</a> dengan <a href="../expect/Properties.html">rata-rata</a> \(\mu \in \R\) dan <a href="../expect/Variance.html">simpangan baku</a> \(\sigma \in (0, \infty)\). Ingat bahwa istilah <dfn>sampel acak</dfn> berarti bahwa \(\bs{X}\) adalah barisan variabel acak yang independen dan berdistribusi identik. Ingat pula bahwa distribusi normal memiliki fungsi kepadatan probabilitas''',
    56: r'''Dalam notasi yang telah kita gunakan di bagian lain bab ini, \(\sigma_3 = \E\left[(X - \mu)^3\right] = 0\) (setara dengan kemencengan distribusi normal yang bernilai 0) dan \(\sigma_4 = \E\left[(X - \mu)^4\right] = 3 \sigma^4\) (setara dengan kurtosis distribusi normal yang bernilai 3). Karena sampel (dan khususnya ukuran sampel \(n\)) dianggap tetap dalam subbagian ini, ketergantungan pada ukuran sampel tidak ditampilkan dalam notasi.</p>''',
    58: r'''<h4 id="mea">Rata-Rata Sampel</h4>''',
    60: r'''<p>Pertama, ingat bahwa <a href="Mean.html">rata-rata sampel</a> adalah''',
    64: r'''\t<p class="math">\(M\) berdistribusi normal dengan rata-rata dan varians berikut:</p>''',
    70: r'''\t\t<summary>Rincian:</summary>''',
    71: r'''\t\t<p>Hasil ini merupakan konsekuensi dari sifat-sifat dasar distribusi normal. Ingat bahwa jumlah variabel independen yang berdistribusi normal juga berdistribusi normal, dan transformasi linear dari variabel yang berdistribusi normal juga berdistribusi normal. Rata-rata dan varians \(M\) berlaku secara umum dan telah diturunkan dalam bagian tentang <a href="LLN.html">Hukum Bilangan Besar.</a></p>''',
    75: r'''<p>Tentu saja, berdasarkan <a href="CLT.html">teorema limit pusat</a>, distribusi \(M\) mendekati distribusi normal ketika \(n\) besar, asalkan distribusi asal memiliki varians positif dan berhingga, meskipun distribusi asal tersebut tidak normal.</p>''',
    78: r'''\t<p class="math"><dfn>Skor baku</dfn> dari \(M\) adalah''',
    80: r'''\t\(Z\) berdistribusi normal baku.</p>''',
    83: r'''<p>Skor baku \(Z\) dalam <a href="#mea2" class="ref"></a> berperan penting dalam menyusun <a href="../interval/Normal.html">interval kepercayaan</a> dan <a href="../hypothesis/Normal.html">uji hipotesis</a> untuk rata-rata distribusi \(\mu\) ketika simpangan baku distribusi \(\sigma\) diketahui. Variabel acak \(Z\) juga akan muncul dalam beberapa penurunan di bagian ini.</p>''',
    85: r'''<h4 id="var">Varians Sampel</h4>''',
    87: r'''<p>Tujuan utama subbagian ini ialah menunjukkan bahwa kelipatan tertentu dari kedua versi <a href="Variance.html">varians sampel</a> yang telah kita pelajari memiliki <dfn>distribusi khi-kuadrat</dfn>. Ingat bahwa <a href="../special/ChiSquare.html">distribusi khi-kuadrat</a> dengan \(k \in \N_+\) derajat kebebasan memiliki fungsi kepadatan probabilitas''',
    89: r'''serta memiliki rata-rata \(k\) dan varians \(2k\). Fungsi pembangkit momennya adalah''',
    91: r'''Hasil terpenting yang perlu diingat ialah bahwa distribusi khi-kuadrat dengan \(k\) derajat kebebasan merupakan distribusi dari \(\sum_{i = 1}^k Z_i^2\), dengan \((Z_1, Z_2, \ldots, Z_k)\) berupa barisan variabel acak normal baku yang independen.</p>''',
    93: r'''<p>Ingat bahwa jika \(\mu\) diketahui, penduga yang wajar bagi varians \(\sigma^2\) adalah statistik''',
    95: r'''Meskipun asumsi bahwa \(\mu\) diketahui hampir selalu tidak realistis, \(W^2\) sangat mudah dianalisis dan akan digunakan dalam beberapa penurunan di bawah ini. Hasil pertama kita adalah distribusi suatu kelipatan sederhana dari \(W^2\).</p>''',
    98: r'''\t<p class="math">Variabel acak''',
    100: r'''\tberdistribusi khi-kuadrat dengan \(n\) derajat kebebasan.</p>''',
    102: r'''\t\t<summary>Rincian:</summary>''',
    103: r'''\t\t<p>Perhatikan bahwa''',
    105: r'''\t\tdan suku-suku dalam jumlah tersebut merupakan variabel normal baku yang independen.</p>''',
    109: r'''<p>Variabel \(U\) dalam <a href="#var1" class="ref"></a> berperan penting dalam menyusun <a href="../interval/Normal.html">interval kepercayaan</a> dan <a href="../hypothesis/Normal.html">uji hipotesis</a> untuk simpangan baku distribusi \(\sigma\) ketika rata-rata distribusi \(\mu\) diketahui (meskipun sekali lagi, asumsi ini biasanya tidak realistis).</p>''',
    112: r'''\t<p class="math">Rata-rata dan varians \(W^2\) adalah</p>''',
    118: r'''\t\t<summary>Rincian:</summary>''',
    119: r'''\t\t<p>Hasil-hasil ini diperoleh dari distribusi khi-kuadrat \(U\) serta sifat-sifat baku nilai harapan dan varians.</p>''',
    123: r'''<p>Sebagai penduga bagi \(\sigma^2\), bagian (a) berarti bahwa \(W^2\) <dfn>tak bias</dfn>, sedangkan bagian (b) berarti bahwa \(W^2\) <dfn>konsisten</dfn>. Tentu saja, hasil-hasil momen ini merupakan kasus khusus dari hasil umum yang diperoleh dalam bagian tentang <a href="Variance.html#spe">Varians Sampel</a>. Dalam bagian tersebut, kita juga menunjukkan bahwa \(M\) dan \(W^2\) tidak berkorelasi jika distribusi asal sampelnya memiliki <a href="../expect/Skew.html#skw">kemencengan</a> 0 (\(\sigma_3 = 0\)), seperti dalam kasus ini. </p>''',
    125: r'''<p>Untuk ukuran sampel sekurang-kurangnya dua, ingat bahwa versi baku varians sampel adalah statistik''',
    127: r'''Varians sampel \(S^2\) merupakan penduga yang lazim bagi \(\sigma^2\) ketika \(\mu\) tidak diketahui (seperti yang biasanya terjadi). Kita telah menunjukkan <a href="Variance.html">sebelumnya</a> bahwa secara umum, rata-rata sampel \(M\) dan varians sampel \(S^2\) tidak berkorelasi jika distribusi asal sampelnya memiliki kemencengan 0 (\(\sigma_3 = 0\)). Ternyata, jika distribusi sampelnya normal, kedua variabel tersebut bahkan <a href="../prob/Independence.html">independen</a>. Ini merupakan sifat yang sangat penting dan berguna, serta sekilas sangat mengejutkan karena \(S^2\) tampak bergantung secara eksplisit pada \(M\).</p>''',
    130: r'''\t<p class="math">Rata-rata sampel \(M\) dan varians sampel \(S^2\) saling independen.</p>''',
    132: r'''\t\t<summary>Rincian:</summary>''',
    133: r'''\t\t<p>Pembuktiannya didasarkan pada vektor simpangan dari rata-rata sampel. Misalkan''',
    135: r'''\t\tPerhatikan bahwa \(S^2\) dapat ditulis sebagai fungsi dari \(\bs{D}\) karena \(\sum_{i=1}^n (X_i - M) = 0\). Selanjutnya, \(M\) dan vektor \(\bs{D}\) memiliki <a href="../special/MultiNormal.html">distribusi normal multivariat</a> bersama. Kita telah menunjukkan <a href="LLN.html">sebelumnya</a> bahwa \(M\) dan \(X_i - M\) tidak berkorelasi untuk setiap \(i\), sehingga \(M\) dan \(\bs{D}\) independen. Terakhir, karena \(S^2\) merupakan fungsi dari \(\bs{D}\), dapat disimpulkan bahwa \(M\) dan \(S^2\) independen.</p>''',
    139: r'''<p>Sekarang kita dapat menentukan distribusi suatu kelipatan sederhana dari varians sampel \(S^2\).</p>''',
    142: r'''\t<p class="math">Variabel acak''',
    144: r'''\tberdistribusi khi-kuadrat dengan \(n - 1\) derajat kebebasan.</p>''',
    146: r'''\t\t<summary>Rincian:</summary>''',
    147: r'''\t\t<p>Mula-mula kita tunjukkan bahwa \(U = V + Z^2\), dengan \(U\) sebagai variabel khi-kuadrat yang berkaitan dengan \(W^2\) dan \(Z\) sebagai skor baku yang berkaitan dengan \(M\). Untuk melihatnya, perhatikan bahwa''',
    152: r'''\t\tPada ruas kanan persamaan terakhir, suku pertama adalah \(V\). Suku kedua bernilai 0 karena \(\sum_{i=1}^n (X_i - M) = 0\). Suku terakhir adalah \(\frac{n}{\sigma^2}(M - \mu)^2 = Z^2\). Berdasarkan <a href="#var1" class="ref"></a>, \(U\) berdistribusi khi-kuadrat dengan \(n\) derajat kebebasan, dan tentu saja \(Z^2\) berdistribusi khi-kuadrat dengan 1 derajat kebebasan. Berdasarkan <a href="#var3" class="ref"></a>, \(V\) dan \(Z^2\) independen. Ingat bahwa fungsi pembangkit momen dari jumlah variabel independen adalah hasil kali fungsi pembangkit momen masing-masing. Dengan demikian, mengambil fungsi pembangkit momen pada persamaan \(U = V + Z^2\) memberikan''',
    154: r'''\t\tDengan menyelesaikannya, diperoleh \(\E(e^{t V}) = 1 \big/ (1 - 2 t)^{(n-1)/2}\) untuk \(t \lt 1/2\), sehingga \(V\) berdistribusi khi-kuadrat dengan \(n - 1\) derajat kebebasan.</p>''',
    158: r'''<p>Variabel \(V\) dalam <a href="#var4" class="ref"></a> berperan penting dalam menyusun <a href="../interval/Normal.html">interval kepercayaan</a> dan <a href="../hypothesis/Normal.html">uji hipotesis</a> untuk simpangan baku distribusi \(\sigma\) ketika rata-rata distribusi \(\mu\) tidak diketahui (seperti yang hampir selalu terjadi).</p>''',
    161: r'''\t<p class="math">Rata-rata dan varians \(S^2\) adalah</p>''',
    167: r'''\t\t<summary>Rincian:</summary>''',
    168: r'''\t\t<p>Hasil-hasil ini diperoleh dari distribusi khi-kuadrat \(V\) serta sifat-sifat baku nilai harapan dan varians.</p>''',
    172: r'''<p>Seperti sebelumnya, hasil-hasil momen ini merupakan kasus khusus dari hasil umum yang diperoleh dalam bagian tentang <a href="Variance.html">Varians Sampel</a>. Sekali lagi, sebagai penduga bagi \(\sigma^2\), bagian (a) berarti bahwa \(S^2\) tak bias, sedangkan bagian (b) berarti bahwa \(S^2\) konsisten. Perhatikan pula bahwa \(\var(S^2)\) lebih besar daripada \(\var(W^2)\) (hal yang tidak mengejutkan), sebesar faktor \(\frac{n}{n - 1}\).</p>''',
    175: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/SpecialSimulator.html')" class="ancillary">simulator distribusi khusus</a>, pilih distribusi khi-kuadrat. Ubah parameter derajat kebebasan dan perhatikan bentuk serta letak fungsi kepadatan probabilitas dan bilah rata-rata–simpangan baku. Untuk nilai parameter yang dipilih, jalankan eksperimen 1.000 kali dan bandingkan fungsi kepadatan empiris serta momen empiris dengan fungsi kepadatan probabilitas dan momen yang sebenarnya.</p>''',
    179: r'''\t<p class="math">Kovarians dan korelasi antara varians sampel khusus dan varians sampel baku adalah</p>''',
    185: r'''\t\t<summary>Rincian:</summary>''',
    186: r'''\t\t<p>Hasil-hasil ini diperoleh dari hasil umum dalam bagian tentang <a href="Variance.html">varians sampel</a> dan fakta bahwa \(\sigma_4 = 3 \sigma^4\).</p>''',
    190: r'''<p>Perhatikan bahwa korelasi tersebut tidak bergantung pada parameter \(\mu\) dan \(\sigma\), serta konvergen ke 1 ketika \(n \to \infty\).</p>''',
    192: r'''<h4 id="stu">Variabel \(T\)</h4>''',
    194: r'''<p>Ingat bahwa <a href="../special/Student.html">distribusi \(t\) Student</a> dengan \(k \in \N_+\) derajat kebebasan memiliki fungsi kepadatan probabilitas''',
    196: r'''dengan \(C_k\) sebagai konstanta normalisasi yang sesuai. Distribusi ini memiliki rata-rata 0 jika \(k \gt 1\) dan varians \(k / (k - 2)\) jika \(k \gt 2\). Dalam subbagian ini, hal utama yang perlu diingat ialah bahwa distribusi \(t\) dengan \(k\) derajat kebebasan merupakan distribusi dari''',
    198: r'''dengan \(Z\) berdistribusi normal baku; \(V\) berdistribusi khi-kuadrat dengan \(k\) derajat kebebasan; serta \(Z\) dan \(V\) independen.</p>''',
    201: r'''\t<p class="dfn">Untuk ukuran sampel sekurang-kurangnya dua, definisikan''',
    205: r'''Perhatikan bahwa \(T\) serupa dengan skor baku \(Z\) yang berkaitan dengan \(M\), tetapi simpangan baku sampel \(S\) menggantikan simpangan baku distribusi \(\sigma\). Variabel \(T\) berperan penting dalam menyusun <a href="../interval/Normal.html">interval kepercayaan</a> dan <a href="../hypothesis/Normal.html">uji hipotesis</a> untuk rata-rata distribusi \(\mu\) ketika simpangan baku distribusi \(\sigma\) tidak diketahui.</p>''',
    208: r'''\t<p class="math">Misalkan \(Z\) menyatakan skor baku dalam <a href="#mea2" class="ref"></a>, dan \(V\) menyatakan variabel khi-kuadrat dalam <a href="#var4" class="ref"></a>. Maka''',
    210: r'''\tsehingga \(T\) berdistribusi \(t\) Student dengan \(n - 1\) derajat kebebasan.</p>''',
    212: r'''\t\t<summary>Rincian:</summary>''',
    213: r'''\t\t<p>Dalam definisi \(T\), bagi pembilang dan penyebut dengan \(\sigma / \sqrt{n}\). Pembilangnya kemudian menjadi \((M - \mu) \big/ (\sigma / \sqrt{n}) = Z\), sedangkan penyebutnya menjadi \(S / \sigma = \sqrt{V / (n - 1)}\). Karena \(Z\) dan \(V\) independen, \(Z\) berdistribusi normal baku, dan \(V\) berdistribusi khi-kuadrat dengan \(n - 1\) derajat kebebasan, dapat disimpulkan bahwa \(T\) berdistribusi \(t\) Student dengan \(n - 1\) derajat kebebasan.</p>''',
    218: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/SpecialSimulator.html')" class="ancillary">simulator distribusi khusus</a>, pilih distribusi \(t\). Ubah parameter derajat kebebasan dan perhatikan bentuk serta letak fungsi kepadatan probabilitas dan bilah rata-rata \( \pm \) simpangan baku. Untuk nilai parameter yang dipilih, jalankan eksperimen 1.000 kali dan bandingkan fungsi kepadatan empiris serta momen empiris dengan fungsi kepadatan dan momen distribusi.</p>''',
    221: r'''<h3 id="two">Model Dua Sampel</h3>''',
    223: r'''<p>Misalkan \(\bs{X} = (X_1, X_2, \ldots, X_m)\) merupakan sampel acak berukuran \(m\) dari distribusi normal dengan rata-rata \(\mu \in \R\) dan simpangan baku \(\sigma \in (0, \infty)\), dan \(\bs{Y} = (Y_1, Y_2, \ldots, Y_n)\) merupakan sampel acak berukuran \(n\) dari distribusi normal dengan rata-rata \(\nu \in \R\) dan simpangan baku \(\tau \in (0, \infty)\). Terakhir, misalkan \(\bs{X}\) dan \(\bs{Y}\) independen. Tentu saja, seluruh hasil di atas untuk model satu sampel dalam <a href="#one" class="ref"></a> berlaku secara terpisah bagi \(\bs{X}\) dan \(\bs{Y}\), tetapi sekarang kita tertarik pada statistik yang berguna dalam prosedur inferensial untuk membandingkan kedua distribusi normal tersebut. Kita akan menggunakan notasi dasar yang ditetapkan di atas, tetapi akan menunjukkan sampel yang menjadi acuannya.</p>''',
    225: r'''<p>Model dua sampel (atau secara lebih umum, model multisampel) muncul secara alami ketika suatu variabel dasar dalam eksperimen statistik <dfn>dipilah</dfn> menurut satu atau beberapa variabel lain (sering kali variabel nominal). Sebagai contoh, dalam <a href="JavaScript:openAncillary('../data/Cicada.html')" class="ancillary">data tonggeret</a>, bobot tonggeret jantan dan bobot tonggeret betina dapat dipandang sebagai pengamatan dari model normal dua sampel. Variabel dasar <var>bobot</var> dipilah menurut variabel <var>jenis kelamin</var>. Jika bobot dipilah menurut jenis kelamin dan spesies, kita dapat memperoleh pengamatan dari model normal enam sampel.</p>''',
    227: r'''<h4 id="dif">Selisih Rata-Rata Sampel</h4>''',
    229: r'''<p>Kita mengetahui dari <a href="#mea1" class="ref"></a> bahwa \(M(\bs{X})\) dan \(M(\bs{Y})\) berdistribusi normal. Selain itu, kedua rata-rata sampel ini independen karena sampel asalnya, \(\bs{X}\) dan \(\bs{Y}\), independen. Dengan demikian, berdasarkan sifat dasar distribusi normal, setiap kombinasi linear dari \(M(\bs{X})\) dan \(M(\bs{Y})\) juga akan berdistribusi normal. Untuk prosedur inferensial yang membandingkan rata-rata distribusi \(\mu\) dan \(\nu\), kombinasi linear terpenting adalah selisihnya.</p>''',
    232: r'''\t<p class="math">\(M(\bs{X}) - M(\bs{Y})\) berdistribusi normal dengan rata-rata dan varians berikut:</p>''',
    234: r'''\t\t<li>\(\E\left[(M(\bs{X}) - M(\bs{Y})\right] = \mu - \nu\)</li>''',
    235: r'''\t\t<li>\(\var\left[(M(\bs{X}) - M(\bs{Y})\right] = \sigma^2 / m + \tau^2 / n\)</li>''',
    239: r'''<p>Dengan demikian, skor baku''',
    240: r'''\[ Z = \frac{\left[(M(\bs{X}) - M(\bs{Y})\right] - (\mu - \nu)}{\sqrt{\sigma^2 / m + \tau^2 / n}} \]''',
    241: r'''berdistribusi normal baku. Skor baku ini berperan mendasar dalam menyusun <a href="../interval/BivariateNormal.html">interval kepercayaan</a> dan <a href="../hypothesis/BivariateNormal.html">uji hipotesis</a> untuk selisih \(\mu - \nu\) ketika simpangan baku distribusi \(\sigma\) dan \(\tau\) diketahui.</p>''',
    243: r'''<h4 id="rat">Rasio Varians Sampel</h4>''',
    245: r'''<p>Selanjutnya, kita akan menunjukkan bahwa rasio kelipatan tertentu dari varians sampel (untuk kedua versinya) dari \(\bs{X}\) dan \(\bs{Y}\) memiliki <dfn>distribusi \(F\)</dfn>. Ingat bahwa <a href="../special/Fisher.html">distribusi \(F\)</a> dengan \(j \in \N_+\) derajat kebebasan pada pembilang dan \(k \in \N_+\) derajat kebebasan pada penyebut merupakan distribusi dari''',
    247: r'''dengan \(U\) berdistribusi khi-kuadrat dengan \(j\) derajat kebebasan; \(V\) berdistribusi khi-kuadrat dengan \(k\) derajat kebebasan; serta \(U\) dan \(V\) independen. Distribusi \(F\) dinamai untuk menghormati <a href="JavaScript:openAncillary('../biographies/Fisher.html')" class="ancillary">Ronald Fisher</a> dan memiliki fungsi kepadatan probabilitas''',
    249: r'''dengan \(C_{j,k}\) sebagai konstanta normalisasi yang sesuai. Rata-ratanya adalah \(\frac{k}{k - 2}\) jika \(k \gt 2\), dan variansnya adalah \(2 \left(\frac{k}{k - 2}\right)^2 \frac{j + k  - 2}{j (k - 4)}\) jika \(k \gt 4\).</p>''',
    252: r'''\t<p class="math">Variabel acak berikut berdistribusi \(F\) dengan \(m\) derajat kebebasan pada pembilang dan \(n\) derajat kebebasan pada penyebut:''',
    255: r'''\t\t<summary>Rincian:</summary>''',
    256: r'''\t\t<p>Dengan menggunakan notasi dalam <a href="#var1" class="ref"></a>, perhatikan bahwa \(W^2(\bs{X}) / \sigma^2 = U(\bs{X}) / m\) dan \(W^2(\bs{Y}) / \tau^2 = U(\bs{Y}) / n\). Hasil tersebut langsung diperoleh karena \(U(\bs{X})\) dan \(U(\bs{Y})\) merupakan variabel khi-kuadrat independen yang masing-masing memiliki \(m\) dan \(n\) derajat kebebasan.</p>''',
}


# Verified reader-facing translation for authority lines 261--490. TeX in these
# rows is protected and restored from authority bytes except for the declared
# corrections above.
BACK_HALF_LINE_REPLACEMENTS: dict[int, str] = {
    261: r'''\t<p class="math">Jika ukuran masing-masing sampel sekurang-kurangnya dua, variabel acak berikut berdistribusi \(F\) dengan \(m - 1\) derajat kebebasan pada pembilang dan \(n - 1\) derajat kebebasan pada penyebut:''',
    264: r'''\t\t<summary>Rincian:</summary>''',
    265: r'''\t\t<p>Dengan menggunakan notasi pada <a href="#var4" class="ref"></a>, perhatikan bahwa \(S^2(\bs{X}) / \sigma^2 = V(\bs{X}) \big/ (m - 1)\) dan \(S^2(\bs{Y}) / \tau^2 = V(\bs{Y}) \big/ (n - 1)\). Hasil tersebut langsung diperoleh karena \(V(\bs{X})\) dan \(V(\bs{Y})\) merupakan variabel khi-kuadrat independen dengan derajat kebebasan masing-masing \(m - 1\) dan \(n - 1\).</p>''',
    269: r'''<p>Variabel-variabel ini berguna untuk menyusun <a href="../interval/BivariateNormal.html">interval kepercayaan</a> dan <a href="../hypothesis/BivariateNormal.html">uji hipotesis</a> bagi rasio simpangan baku \(\sigma / \tau\). Pemilihan variabel \(F\) bergantung pada diketahui atau tidaknya rata-rata \(\mu\) dan \(\nu\). Tentu saja, rata-rata biasanya tidak diketahui, sehingga statistik pada <a href="#rat2" class="ref"></a> digunakan.</p>''',
    272: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/SpecialSimulator.html')" class="ancillary">simulator distribusi khusus</a>, pilih distribusi \(F\). Variasikan parameter derajat kebebasan dan perhatikan bentuk serta letak fungsi kepadatan probabilitas dan bilah rata-rata \( \pm \) simpangan baku. Untuk nilai parameter yang dipilih, jalankan eksperimen 1.000 kali dan bandingkan fungsi kepadatan serta momen empiris dengan fungsi kepadatan dan momen distribusi sebenarnya.</p>''',
    275: r'''<h4 id="tst">Variabel \(T\)</h4>''',
    277: r'''<p>Dengan ukuran setiap sampel sekurang-kurangnya dua, konstruksi terakhir kita dalam model normal dua sampel akan menghasilkan variabel dengan distribusi \(t\) Student. Variabel ini berperan mendasar dalam menyusun <a href="../interval/BivariateNormal.html">interval kepercayaan</a> dan <a href="../hypothesis/BivariateNormal.html">uji hipotesis</a> bagi selisih \(\mu - \nu\) ketika simpangan baku distribusi \(\sigma\) dan \(\tau\) tidak diketahui. Konstruksi ini memerlukan asumsi tambahan bahwa kedua simpangan baku distribusi sama: \( \sigma = \tau \). Asumsi ini masuk akal jika terdapat variabilitas inheren pada variabel pengukuran yang tidak berubah sekalipun perlakuan berbeda diterapkan pada objek-objek dalam populasi.</p>''',
    280: r'''\t<p class="math">Skor baku yang terkait dengan selisih rata-rata sampel adalah''',
    284: r'''<p>Untuk membentuk variabel yang diinginkan, pertama-tama kita memerlukan penduga bagi \(\sigma^2\). Pendekatan yang wajar adalah menggunakan rata-rata tertimbang dari varians sampel \(S^2(\bs{X})\) dan \(S^2(\bs{Y})\), dengan derajat kebebasan sebagai faktor pembobot.</p>''',
    287: r'''\t<p class="dfn"><dfn>Penduga gabungan</dfn> bagi \(\sigma^2\) adalah''',
    292: r'''\t<p class="math">Variabel acak \( V \) berikut berdistribusi <a href="../special/ChiSquare.html">khi-kuadrat</a> dengan \(m + n - 2\) derajat kebebasan:''',
    295: r'''\t\t<summary>Rincian:</summary>''',
    296: r'''\t\t<p>Variabel tersebut dapat dinyatakan sebagai jumlah variabel-variabel khi-kuadrat yang independen.</p>''',
    301: r'''\t<p class="math">Variabel \(M(\bs{Y}) - M(\bs{X})\) dan \(S^2(\bs{X}, \bs{Y})\) saling independen.</p>''',
    303: r'''\t\t<summary>Rincian:</summary>''',
    304: r'''\t\t<p>Karena kedua sampel independen, vektor \((M(\bs{X}), S(\bs{X}))\) independen dari vektor \((M(\bs{Y}), S(\bs{Y}))\). Selain itu, dalam setiap sampel normal, \(M(\bs{X})\) independen dari \(S(\bs{X})\), dan \(M(\bs{Y})\) independen dari \(S(\bs{Y})\). Dengan demikian, vektor kedua rata-rata sampel independen dari vektor kedua simpangan baku sampel; setiap fungsi dari vektor pertama, termasuk selisih rata-rata, independen dari setiap fungsi dari vektor kedua, termasuk varians gabungan.</p>''',
    309: r'''\t<p class="math">Variabel acak \( T \) berikut berdistribusi <a href="../special/Student.html">\(t\) Student</a> dengan \(m + n - 2\) derajat kebebasan.''',
    312: r'''\t\t<summary>Rincian:</summary>''',
    313: r'''\t\t<p>Variabel acak tersebut dapat ditulis sebagai \(Z / \sqrt{V / (m + n - 2}\), dengan \(Z\) sebagai variabel normal baku yang diberikan dalam <a href="#std" class="ref"></a> dan \( V \) sebagai variabel khi-kuadrat yang diberikan dalam <a href="#tst1" class="ref"></a>. Selain itu, \( Z \) dan \( V \) independen berdasarkan <a href="#tst2" class="ref"></a>.</p>''',
    317: r'''<h3 id="biv">Model Sampel Bivariat</h3>''',
    319: r'''<p>Misalkan sekarang \(\left((X_1, Y_1), (X_2, Y_2), \ldots, (X_n, Y_n)\right)\) merupakan sampel acak berukuran \(n\) dari <a href="../special/MultiNormal.html">distribusi normal bivariat</a> dengan rata-rata \(\mu \in \R\) dan \(\nu \in \R\), simpangan baku \(\sigma \in (0, \infty)\) dan \(\tau \in (0, \infty)\), serta korelasi \(\rho \in [0, 1]\). Tentu saja, \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari distribusi normal dengan rata-rata \(\mu\) dan simpangan baku \(\sigma\), sedangkan \(\bs{Y} = (Y_1, Y_2, \ldots, Y_n)\) merupakan sampel acak berukuran \(n\) dari distribusi normal dengan rata-rata \(\nu\) dan simpangan baku \(\tau\). Karena itu, hasil-hasil di atas untuk model satu sampel dalam <a href="#one" class="ref"></a> berlaku bagi \(\bs{X}\) dan \(\bs{Y}\) secara terpisah. Perhatian kita dalam bagian ini tertuju pada hubungan antara berbagai statistik yang dihitung dari \(\bs{X}\) dan \(\bs{Y}\), serta sifat-sifat <a href="Covariance.html">kovarians sampel</a>.</p>''',
    321: r'''<p>Model bivariat (atau, secara lebih umum, multivariat) muncul secara alami ketika dua atau lebih variabel dipertimbangkan dalam eksperimen statistik. Sebagai contoh, pasangan tinggi ayah dan putranya dalam <a href="JavaScript:openAncillary('../data/Pearson.html')" class="ancillary">data tinggi Pearson</a> dapat dimodelkan sebagai pengamatan dari model normal bivariat.</p>''',
    323: r'''<p>Dalam notasi yang telah kita gunakan sebelumnya, ingat bahwa \(\sigma^3 = \E\left[(X - \mu)^3\right] = 0\), \(\sigma_4 = \E\left[(X - \mu)^4\right] = 3 \sigma^4\), \(\tau_3 = \E\left[(Y - \nu)^3\right] = 0\), \(\tau_4 = \E\left[(Y - \nu)^4\right] = 3 \tau^4\), \( \delta = \cov(X, Y) = \sigma \tau \rho\), dan \(\delta_2 = \E[(X - \mu)^2 (Y - \nu)^2] = \sigma^2 \tau^2 (1 + 2 \rho^2)\).</p>''',
    326: r'''\t<p class="math">Vektor data \(((X_1, Y_1), (X_2, Y_2), \ldots (X_n, Y_n))\) berdistribusi normal multivariat.</p>''',
    328: r'''\t\t<li>Vektor rata-ratanya berbentuk blok, dengan setiap blok berupa \((\mu, \nu)\).</li>''',
    329: r'''\t\t<li>Matriks varians-kovariansnya berbentuk blok diagonal, dengan setiap blok berupa \(\left[\begin{matrix} \sigma^2 &amp; \sigma \tau \rho \\ \sigma \tau \rho &amp; \tau^2 \end{matrix} \right]\).</li>''',
    332: r'''\t\t<summary>Rincian:</summary>''',
    333: r'''\t\t<p>Hasil ini merupakan konsekuensi dari hasil-hasil baku untuk distribusi normal multivariat. Blok pada bagian (a) dan (b) masing-masing adalah vektor rata-rata dan matriks varians-kovarians dari satu pengamatan \((X, Y)\).</p>''',
    337: r'''<h4 id="mes">Rata-Rata Sampel</h4>''',
    340: r'''\t<p class="math">\(\left(M(\bs{X}), M(\bs{Y})\right)\) berdistribusi normal bivariat. Kovarians dan korelasinya adalah</p>''',
    346: r'''\t\t<summary>Rincian:</summary>''',
    347: r'''\t\t<p>Fakta bahwa pasangan rata-rata tersebut berdistribusi normal bivariat diperoleh dari <a href="#biv1" class="ref"></a> karena \((M(\bs{X}), M(\bs{Y}))\) dapat diperoleh dari vektor data melalui transformasi linear. Bagian (a) dan (b) diperoleh dari hasil pada bagian tentang <a href="Covariance.html">korelasi sampel</a>.</p>''',
    351: r'''<p>Rata-rata dan varians \(M(\bs{X})\) maupun \(M(\bs{Y})\) telah kita ketahui dari <a href="#one">model satu sampel</a> di atas. Oleh karena itu, kita mengetahui distribusi lengkap dari \((M(\bs{X}), M(\bs{Y}))\).</p>''',
    353: r'''<h4 id="vas">Varians Sampel</h4>''',
    356: r'''\t<p class="math">Kovarians dan korelasi antara kedua varians sampel khusus adalah:</p>''',
    362: r'''\t\t<summary>Rincian:</summary>''',
    363: r'''\t\t<p>Hasil-hasil ini diperoleh dari hasil pada bagian tentang <a href="Covariance.html">korelasi sampel</a> dan bentuk khusus \(\delta_2\), \(\sigma_4\), serta \(\tau_4\).</p>''',
    368: r'''\t<p class="math">Untuk ukuran sampel sekurang-kurangnya dua, kovarians dan korelasi antara kedua varians sampel baku adalah</p>''',
    374: r'''\t\t<summary>Rincian:</summary>''',
    375: r'''\t\t<p>Hasil-hasil ini diperoleh dari hasil pada bagian tentang <a href="Covariance.html">korelasi sampel</a> dan bentuk khusus \(\delta\), \(\delta_2\), \(\sigma_4\), serta \(\tau_4\).</p>''',
    379: r'''<h4 id="cov">Kovarians Sampel</h4>''',
    381: r'''<p>Jika \(\mu\) dan \(\nu\) diketahui (sekali lagi, biasanya merupakan asumsi artifisial), penduga yang wajar bagi kovarians distribusi \(\delta\) adalah bentuk khusus kovarians sampel''',
    385: r'''\t<p class="math">Rata-rata dan varians \(W(\bs{X}, \bs{Y})\) adalah</p>''',
    391: r'''\t\t<summary>Rincian:</summary>''',
    392: r'''\t\t<p>Hasil-hasil ini diperoleh dari hasil pada bagian tentang <a href="Covariance.html">korelasi sampel</a> dan bentuk khusus \(\delta\) serta \(\delta_2\).</p>''',
    396: r'''<p>Untuk ukuran sampel sekurang-kurangnya dua, jika \(\mu\) dan \(\nu\) tidak diketahui (sekali lagi, seperti yang biasanya terjadi), penduga yang wajar bagi kovarians distribusi \(\delta\) adalah kovarians sampel baku''',
    400: r'''\t<p class="math">Rata-rata dan varians dari kovarians sampel adalah</p>''',
    406: r'''\t\t<summary>Rincian:</summary>''',
    407: r'''\t\t<p>Hasil-hasil ini merupakan konsekuensi dari <a href="Covariance.html">hasil umum</a> sebelumnya dan bentuk khusus \(\delta\) serta \(\delta_2\).</p>''',
    411: r'''<h3 id="exe">Latihan Komputasi</h3>''',
    413: r'''<p>Kita menggunakan notasi dasar yang ditetapkan di atas untuk sampel \(\bs{X}\) dan \(\bs{Y}\), serta untuk statistik \(M\), \(W^2\), \(S^2\), \(T\), dan seterusnya.</p>''',
    416: r'''\t<p class="math">Misalkan bobot bersih (dalam gram) dari 25 bungkus M&amp;M membentuk sampel acak \(\bs{X}\) dari distribusi normal dengan rata-rata 50 dan simpangan baku 4. Tentukan setiap besaran berikut:</p>''',
    418: r'''\t\t<li>Rata-rata dan simpangan baku \(M\).</li>''',
    419: r'''\t\t<li>Rata-rata dan simpangan baku \(W^2\).</li>''',
    420: r'''\t\t<li>Rata-rata dan simpangan baku \(S^2\).</li>''',
    421: r'''\t\t<li>Rata-rata dan simpangan baku \(T\).</li>''',
    422: r'''\t\t<li>\(\P(M \gt 49, S^2 \lt 20))\).</li>''',
    426: r'''\t\t<summary>Rincian:</summary>''',
    439: r'''\t<p class="math">Misalkan skor matematika SAT dari 16 siswa Alabama membentuk sampel acak \(\bs{X}\) dari distribusi normal dengan rata-rata 550 dan simpangan baku 20, sedangkan skor matematika SAT dari 25 siswa Georgia membentuk sampel acak \(\bs{Y}\) dari distribusi normal dengan rata-rata 540 dan simpangan baku 15. Kedua sampel tersebut independen. Tentukan setiap besaran berikut:</p>''',
    441: r'''\t\t<li>Rata-rata dan simpangan baku \(M(\bs{X})\).</li>''',
    442: r'''\t\t<li>Rata-rata dan simpangan baku \(M(\bs{Y})\).</li>''',
    443: r'''\t\t<li>Rata-rata dan simpangan baku \(M(\bs{X}) - M(\bs{Y})\).</li>''',
    445: r'''\t\t<li>Rata-rata dan simpangan baku \(S^2(\bs{X})\).</li>''',
    446: r'''\t\t<li>Rata-rata dan simpangan baku \(S^2(\bs{Y})\).</li>''',
    447: r'''\t\t<li>Rata-rata dan simpangan baku \(S^2(\bs{X}) / S^2(\bs{Y})\).</li>''',
    451: r'''\t\t<summary>Rincian:</summary>''',
    468: r'''\t\t<li class="parent"><a href="index.html">5. Sampel Acak</a></li>''',
    469: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    470: r'''\t\t<li class="child"><a href="Mean.html" title="Rata-Rata Sampel">2</a></li>''',
    471: r'''\t\t<li class="child"><a href="LLN.html" title="Hukum Bilangan Besar">3</a></li>''',
    472: r'''\t\t<li class="child"><a href="CLT.html" title="Teorema Limit Pusat">4</a></li>''',
    473: r'''\t\t<li class="child"><a href="Variance.html" title="Varians Sampel">5</a></li>''',
    474: r'''\t\t<li class="child"><a href="OrderStatistics.html" title="Statistik Terurut">6</a></li>''',
    475: r'''\t\t<li class="child"><a href="Covariance.html" title="Korelasi dan Regresi Sampel">7</a></li>''',
    477: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    478: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    481: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    482: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    483: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


# Additive stable identifiers are structural, not translations. The sole
# anonymous unit on this page is the F-distribution simulator at authority line
# 271. Its exact source row is guarded before replacement.
STABLE_ID_REPLACEMENTS: dict[int, tuple[str, str]] = {
    271: (
        r'''<div class="unit">''',
        rf'''<div class="unit" id="{ANONYMOUS_F_SIMULATOR_UNIT_ID}">''',
    ),
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/sample/index.html": "index.html",
    "https://www.randomservices.org/random/sample/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/sample/Mean.html": "Mean.html",
    "https://www.randomservices.org/random/sample/LLN.html": "LLN.html",
    "https://www.randomservices.org/random/sample/CLT.html": "CLT.html",
    "https://www.randomservices.org/random/sample/Variance.html": "Variance.html",
    "https://www.randomservices.org/random/point/index.html": "../point/index.html",
    "https://www.randomservices.org/random/sample/OrderStatistics.html": "OrderStatistics.html",
    "https://www.randomservices.org/random/sample/Covariance.html": "Covariance.html",
    "https://www.randomservices.org/random/sample/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/interval/Normal.html": "../interval/Normal.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "../interval/BivariateNormal.html",
    "https://www.randomservices.org/random/hypothesis/Normal.html": "../hypothesis/Normal.html",
    "https://www.randomservices.org/random/hypothesis/BivariateNormal.html": "../hypothesis/BivariateNormal.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, serta koreksi terbatas terhadap kekeliruan matematis dan data yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t</section>'''


def materialize_indentation(value: str) -> str:
    """Convert only line-leading raw tab markers into real tab bytes."""

    return re.sub(
        r"^(?:\\t)+",
        lambda match: "\t" * (len(match.group(0)) // 2),
        value,
        flags=re.MULTILINE,
    )


def restore_protected_math(line_number: int, original: str, replacement: str) -> str:
    """Restore authority TeX, applying only exact declared corrections."""

    source_spans = MATH_RE.findall(original)
    target_matches = list(MATH_RE.finditer(replacement))
    if len(source_spans) != len(target_matches):
        raise RuntimeError(
            f"line {line_number}: TeX span count changed: "
            f"{len(source_spans)} != {len(target_matches)}"
        )
    configured = {
        key: value for key, value in MATH_CORRECTIONS.items() if key[0] == line_number
    }
    output: list[str] = []
    cursor = 0
    for span_index, match in enumerate(target_matches, start=1):
        source_span = source_spans[span_index - 1]
        key = (line_number, span_index)
        expected = configured.pop(key, None)
        if expected is None:
            protected = source_span
        else:
            expected_source, corrected = expected
            if source_span != expected_source:
                raise RuntimeError(
                    f"line {line_number} span {span_index}: authority TeX changed"
                )
            protected = corrected
        output.append(replacement[cursor : match.start()])
        output.append(protected)
        cursor = match.end()
    if configured:
        raise RuntimeError(f"line {line_number}: configured TeX corrections were not consumed")
    output.append(replacement[cursor:])
    return "".join(output)


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
    return result + (f"#{fragment}" if fragment else "")


def replace_exact_line(
    lines: list[str], line_number: int, expected_raw: str, replacement_raw: str
) -> None:
    original = lines[line_number - 1]
    ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
    expected = materialize_indentation(expected_raw)
    replacement = materialize_indentation(replacement_raw)
    if original.removesuffix(ending) != expected:
        raise RuntimeError(f"line {line_number}: exact authority row changed")
    lines[line_number - 1] = replacement + ending


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    text = source_bytes.decode("utf-8")
    lines = text.splitlines(keepends=True)
    if len(lines) != EXPECTED_SOURCE_LINES:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")
    if any(line_number > 260 for line_number in LINE_REPLACEMENTS):
        raise RuntimeError("front-half replacement registry extends beyond line 260")
    overlap = set(LINE_REPLACEMENTS) & set(BACK_HALF_LINE_REPLACEMENTS)
    if overlap:
        raise RuntimeError(f"front/back replacement overlap: {sorted(overlap)}")
    replacements = {**LINE_REPLACEMENTS, **BACK_HALF_LINE_REPLACEMENTS}
    unreachable = {line_number for line_number, _ in MATH_CORRECTIONS} - set(replacements)
    if unreachable:
        raise RuntimeError(f"protected TeX corrections lack replacement lines: {sorted(unreachable)}")
    for line_number, (expected_raw, corrected_raw) in sorted(RAW_TEX_CORRECTIONS.items()):
        replace_exact_line(lines, line_number, expected_raw, corrected_raw)
    for line_number, replacement in sorted(replacements.items()):
        original = lines[line_number - 1]
        ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
        translated = materialize_indentation(replacement)
        lines[line_number - 1] = restore_protected_math(
            line_number, original.removesuffix(ending), translated
        ) + ending
    for line_number, (expected_raw, replacement_raw) in sorted(
        STABLE_ID_REPLACEMENTS.items()
    ):
        if line_number in replacements or line_number in RAW_TEX_CORRECTIONS:
            raise RuntimeError(f"line {line_number}: stable-ID replacement overlaps another mutation")
        replace_exact_line(lines, line_number, expected_raw, replacement_raw)
    text = "".join(lines)
    text = re.sub(r'href="([^"]+)"', lambda match: f'href="{convert_href(match.group(1))}"', text)
    marker = "\n</footer>"
    if text.count(marker) != 1:
        raise RuntimeError("footer insertion point is not unique")
    text = text.replace(marker, materialize_indentation(EDITION_NOTICE) + marker, 1)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(text.encode("utf-8"))
    target_bytes = TARGET.read_bytes()
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: "
        f"{len(target_bytes)} bytes / sha256 {hashlib.sha256(target_bytes).hexdigest()}"
    )


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
