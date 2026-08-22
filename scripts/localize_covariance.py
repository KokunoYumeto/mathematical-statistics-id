#!/usr/bin/env python3
"""Create the bounded id-ID Sample Correlation and Regression target."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "sample" / "Covariance.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "sample" / "Covariance.html"
SOURCE_URL = "https://www.randomservices.org/random/sample/Covariance.html"
SOURCE_SHA256 = "1009a5a6a129ee5592aed6c2b914973ae82bb7e7685c477c4c205dbe47fd7072"

MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)

# Every protected change below was independently derived and checked against the
# displayed identity; all other inline/display TeX is restored byte-for-byte.
MATH_CORRECTIONS: dict[tuple[int, int], tuple[str, str]] = {
    (106, 1): (
        r"\[ s(\bs{x}, \bs{y}) = \frac{1}{n - 1} \sum_{i=1}^n x_i \, y_i - \frac{n}{n - 1} m(\bs{x}) m(\bs{y}) = \frac{n}{n - 1} [m(\bs{x y}) - m(\bs{x}) m(\bs{y})] \]",
        r"\[ s(\bs{x}, \bs{y}) = \frac{1}{n - 1} \sum_{i=1}^n x_i \, y_i - \frac{n}{n - 1} m(\bs{x}) m(\bs{y}) = \frac{n}{n - 1} [m(\bs{x}\bs{y}) - m(\bs{x}) m(\bs{y})] \]",
    ),
    (135, 2): (
        r"\(\cov(\bs{x}, \bs{y})\)",
        r"\(s(\bs{x}, \bs{y})\)",
    ),
    (222, 1): (
        r"\[ \bs{u} = \frac{1}{s(\bs{x})}[\bs{x} - m(\bs{x})], \quad \bs{v} = \frac{1}{s(\bs{y})}[\bs{y} - m(\bs{y})] \]",
        r"\[ \bs{u} = \frac{1}{s(\bs{x})}[\bs{x} - m(\bs{x})\bs{1}], \quad \bs{v} = \frac{1}{s(\bs{y})}[\bs{y} - m(\bs{y})\bs{1}] \]",
    ),
    (388, 3): (
        r"\(r^2(\bs{x}, \bs{y}) \sst(\bs{y}) = s^2(\bs{x}, \bs{y}) \big/ s^2(\bs{x})\)",
        r"\(r^2(\bs{x}, \bs{y}) \sst(\bs{y}) = (n - 1)s^2(\bs{x}, \bs{y}) \big/ s^2(\bs{x})\)",
    ),
    (391, 1): (
        r"\[ \ssr(\bs{x}, \bs{y}) = \sum_{i=1}^n [\hat{y}_i - m(\bs{y})]^2 = \frac{s^2(\bs{x}, \bs{y})}{s^2(\bs{x})} \]",
        r"\[ \ssr(\bs{x}, \bs{y}) = \sum_{i=1}^n [\hat{y}_i - m(\bs{y})]^2 = (n - 1)\frac{s^2(\bs{x}, \bs{y})}{s^2(\bs{x})} \]",
    ),
    (425, 1): (
        r"\(\cor[(M(\bs{X}), M(\bs{Y})] = \rho\)",
        r"\(\cor[M(\bs{X}), M(\bs{Y})] = \rho\)",
    ),
    (455, 1): (
        r"\[ \cov[(X - \mu)^2 (Y - \nu)^2] = \E[(X - \mu)^2 (Y - \nu)^2] - \E[(X - \mu)^2] \E[(Y - \nu)^2] = \delta_2 - \sigma^2 \tau^2 \]",
        r"\[ \cov[(X - \mu)^2, (Y - \nu)^2] = \E[(X - \mu)^2 (Y - \nu)^2] - \E[(X - \mu)^2] \E[(Y - \nu)^2] = \delta_2 - \sigma^2 \tau^2 \]",
    ),
    (487, 1): (
        r"\[ \cor\left[S^2(\bs{X}), S^2(\bs{Y})\right] \to \frac{\delta_2 - \sigma^2 \tau^2}{\sqrt{(\sigma_4 - \sigma^4)(\tau_4 - \tau^4)}} \text{ as } n \to \infty \]",
        r"\[ \cor\left[S^2(\bs{X}), S^2(\bs{Y})\right] \to \frac{\delta_2 - \sigma^2 \tau^2}{\sqrt{(\sigma_4 - \sigma^4)(\tau_4 - \tau^4)}} \text{ ketika } n \to \infty \]",
    ),
    (516, 3): (
        r"\([(X_i - M(\bs{X})][Y_i - M(\bs{Y})]\)",
        r"\([X_i - M(\bs{X})][Y_i - M(\bs{Y})]\)",
    ),
    (553, 7): (
        r"\(R(\bs{X}, \bs{Y}) \to \delta / \sigma \tau = \rho\)",
        r"\(R(\bs{X}, \bs{Y}) \to \delta / (\sigma \tau) = \rho\)",
    ),
    (567, 1): (
        r"\[ \var[S(\bs{X}), \bs{Y})] = \frac{1}{4 n^2 (n - 1)^2} \sum_{i=1}^n \sum_{j=1}^n \sum_{k=1}^n \sum_{l=1}^n \cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] \]",
        r"\[ \var[S(\bs{X}, \bs{Y})] = \frac{1}{4 n^2 (n - 1)^2} \sum_{i=1}^n \sum_{j=1}^n \sum_{k=1}^n \sum_{l=1}^n \cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] \]",
    ),
    (603, 1): (
        r"\(\E\{[Y - L(Y \mid X)]\} = \var(Y)[1 - \cor^2(X, Y)] = r^2 (1 - \rho^2)\)",
        r"\(\E\{[Y - L(Y \mid X)]^2\} = \var(Y)[1 - \cor^2(X, Y)] = \tau^2 (1 - \rho^2)\)",
    ),
    (671, 1): (r"\(m = 45&deg;\)", r"\((45, 100)\)"),
    (671, 2): (r"\(s = 10&deg;\)", r"\((10, 10)\)"),
    (694, 1): (r"\(m = 25.4\)", r"\((25.4, 10.16)\)"),
    (694, 2): (r"\(s = 5.08\)", r"\((5.08, 2.54)\)"),
    (1004, 1): (r"\(14/3\)", r"\(21/5\)"),
    (1005, 1): (r"\(16/9\)", r"\(8/5\)"),
    (1006, 1): (r"\(8/3\)", r"\(12/5\)"),
    (1009, 1): (r"\(96/7\)", r"\(48/35\)"),
    (1011, 1): (r"\(2/7\)", r"\(8/35\)"),
    (1050, 1): (
        r"\(\left((X_1, Y_1), (X_2, Y_2), \ldots (X_9, Y_9)\right)\)",
        r"\(\left((X_1, Y_1), (X_2, Y_2), \ldots, (X_9, Y_9)\right)\)",
    ),
    (1070, 2): (
        r"\(5935/21\,676\,032\)",
        r"\(5939/21\,676\,032\)",
    ),
    (1136, 1): (r"\(r = 0.793\)", r"\(r \approx 0.794\)"),
    (1136, 2): (r"\(r^2 = 0.629\)", r"\(r^2 \approx 0.630\)"),
    (1137, 1): (r"\(y = 20.278 + 0.507 x\)", r"\(y \approx 20.278 + 0.507 x\)"),
    (1158, 1): (r"\(r = -0.849\)", r"\(r \approx -0.850\)"),
    (1158, 2): (r"\(r^2 = 0.721\)", r"\(r^2 \approx 0.722\)"),
    (1159, 1): (
        r"\(y = 1141.5 - 2.1 x\)",
        r"\(y \approx 1141.854 - 2.094 x\)",
    ),
    (1177, 1): (r"\(r = 0.614\)", r"\(r \approx 0.614\)"),
    (1177, 2): (r"\(r^2 = 0.377\)", r"\(r^2 \approx 0.377\)"),
    (1178, 1): (
        r"\(y = 321.5 + 0.3 \, x\)",
        r"\(y \approx 321.503 + 0.356 \, x\)",
    ),
}


# These align-environment rows are not delimited by inline/display markers, so
# they are locked separately by exact source bytes before correction.
RAW_TEX_CORRECTIONS: dict[int, tuple[str, str]] = {
    111: (
        r'''\t\t\t\sum_{i=1}^n [(x_i - m(\bs{x})][y_i - m(\bs{y})] &amp; = \sum_{i=1}^n [x_i y_i - x_i m(\bs{y}) - y_i m(\bs{x}) + m(\bs{x}) m(\bs{y})] \\''',
        r'''\t\t\t\sum_{i=1}^n [x_i - m(\bs{x})][y_i - m(\bs{y})] &amp; = \sum_{i=1}^n [x_i y_i - x_i m(\bs{y}) - y_i m(\bs{x}) + m(\bs{x}) m(\bs{y})] \\''',
    ),
    128: (
        r'''\t\t\t\sum_{i=1}^n \sum_{j=1}^n (x_i - x_j)(y_i - y_j) &amp; = \frac{1}{2 n} \sum_{i=1}^n \sum_{j=1}^n [x_i - m(\bs{x}) + m(\bs{x}) - x_j][y_i - m(\bs{y}) + m(\bs{y}) - y_j] \\''',
        r'''\t\t\t\sum_{i=1}^n \sum_{j=1}^n (x_i - x_j)(y_i - y_j) &amp; = \sum_{i=1}^n \sum_{j=1}^n [x_i - m(\bs{x}) + m(\bs{x}) - x_j][y_i - m(\bs{y}) + m(\bs{y}) - y_j] \\''',
    ),
    129: (
        r'''\t\t\t&amp; = \sum_{i=1}^n \sum_{j=1}^n \left([(x_i - m(\bs{x})][y_i - m(\bs{y})] + [x_i - m(\bs{x})][m(\bs{y}) - y_j] + [m(\bs{x}) - x_j][y_i - m(\bs{y})] + [m(\bs{x}) - x_j][m(\bs{y}) - y_j]\right)''',
        r'''\t\t\t&amp; = \sum_{i=1}^n \sum_{j=1}^n \left([x_i - m(\bs{x})][y_i - m(\bs{y})] + [x_i - m(\bs{x})][m(\bs{y}) - y_j] + [m(\bs{x}) - x_j][y_i - m(\bs{y})] + [m(\bs{x}) - x_j][m(\bs{y}) - y_j]\right)''',
    ),
    281: (
        r'''\t\t\t\frac{\partial}{\partial a}\mse(a, b) &amp; = \frac{1}{n - 1} \sum 2[y_i - (a + b x_i)] (-1) = \frac{2}{n - 1} [-\sum_{i=1}^n y_i + n a + b \sum_{i=1}^n x_i ]\\''',
        r'''\t\t\t\frac{\partial}{\partial a}\mse(a, b) &amp; = \frac{1}{n - 1} \sum_{i=1}^n 2[y_i - (a + b x_i)] (-1) = \frac{2}{n - 1} [-\sum_{i=1}^n y_i + n a + b \sum_{i=1}^n x_i ]\\''',
    ),
    282: (
        r'''\t\t\t\frac{\partial}{\partial b}\mse(a, b) &amp; = \frac{1}{n - 1} \sum 2[y_i - (a + b x_i)](-x_i) = \frac{2}{n - 1} [-\sum_{i=1}^n x_i y_i + a \sum_{i=1}^n x_i + b \sum_{i=1}^n x_i^2]''',
        r'''\t\t\t\frac{\partial}{\partial b}\mse(a, b) &amp; = \frac{1}{n - 1} \sum_{i=1}^n 2[y_i - (a + b x_i)](-x_i) = \frac{2}{n - 1} [-\sum_{i=1}^n x_i y_i + a \sum_{i=1}^n x_i + b \sum_{i=1}^n x_i^2]''',
    ),
}


LINE_REPLACEMENTS = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Korelasi dan Regresi Sampel</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, sampel acak, kovarians sampel, korelasi sampel, regresi linear, diagram pencar, penaksir takbias">''',
    39: r'''\t\t<li class="parent"><a href="index.html">5. Sampel Acak</a></li>''',
    40: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    41: r'''\t\t<li class="child"><a href="Mean.html" title="Rata-Rata Sampel">2</a></li>''',
    42: r'''\t\t<li class="child"><a href="LLN.html" title="Hukum Bilangan Besar">3</a></li>''',
    43: r'''\t\t<li class="child"><a href="CLT.html" title="Teorema Limit Pusat">4</a></li>''',
    44: r'''\t\t<li class="child"><a href="Variance.html" title="Varians Sampel">5</a></li>''',
    45: r'''\t\t<li class="child"><a href="OrderStatistics.html" title="Statistik Terurut">6</a></li>''',
    47: r'''\t\t<li class="child"><a href="Normal.html" title="Sifat Khusus Sampel Normal">8</a></li>''',
    48: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    49: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    51: r'''\t<h2 id="o006.random.sample.covariance.page">7. Korelasi dan Regresi Sampel</h2>''',
    54: r'''<h3 id="des">Teori Deskriptif</h3>''',
    56: r'''<p>Ingat kembali model dasar statistika: kita memiliki populasi objek yang menjadi perhatian dan berbagai pengukuran (variabel) yang dilakukan terhadap objek-objek tersebut. Kita memilih objek dari populasi dan mencatat variabel untuk objek-objek dalam sampel; catatan ini menjadi data kita. Pembahasan pertama menggunakan sudut pandang yang murni deskriptif. Artinya, kita tidak mengasumsikan bahwa data dihasilkan oleh suatu distribusi probabilitas yang mendasarinya. Namun, seperti biasa, ingat bahwa data itu sendiri mendefinisikan suatu distribusi probabilitas, yaitu <dfn>distribusi empiris</dfn> yang memberikan probabilitas sama kepada setiap titik data.</p>''',
    58: r'''<p>Misalkan \(x\) dan \(y\) adalah variabel bernilai riil pada suatu populasi, dan \(\left((x_1, y_1), (x_2, y_2), \ldots, (x_n, y_n)\right)\) adalah sampel teramati berukuran \(n\) dari \((x, y)\). Kita akan menggunakan \(\bs{x} = (x_1, x_2, \ldots, x_n)\) untuk menyatakan sampel dari \(x\), dan \(\bs{y} = (y_1, y_2, \ldots, y_n)\) untuk menyatakan sampel dari \(y\). Pada bagian ini, kita tertarik pada statistik yang menjadi <dfn>ukuran asosiasi</dfn> antara \(\bs{x}\) dan \(\bs{y}\), serta pada pencarian garis (atau kurva lain) yang paling sesuai dengan data.</p>''',
    60: r'''<p>Ingat bahwa <a href="Mean.html">rata-rata sampel</a> adalah''',
    62: r'''dan <a href="Variance.html">varians sampel</a> adalah''',
    65: r'''<h4 id="sct">Diagram Pencar</h4>''',
    67: r'''<p>Sering kali, langkah pertama dalam <dfn>analisis data eksploratif</dfn> ialah menggambar titik-titik data; gambar ini disebut <dfn>diagram pencar</dfn> dan dapat memberikan gambaran visual tentang hubungan statistik antara variabel-variabel tersebut.</p>''',
    70: r'''\t<figcaption>Diagram pencar</figcaption>''',
    71: r'''\t<img src="ScatterPlot.png" alt="Diagram pencar">''',
    74: r'''<p>Secara khusus, kita ingin mengetahui apakah kumpulan titik tampak menunjukkan kecenderungan linear atau apakah suatu kurva nonlinear mungkin lebih sesuai dengan kumpulan titik tersebut. Kita tertarik pada sejauh mana satu variabel \(x\) dapat digunakan untuk memprediksi variabel lainnya \(y\).</p>''',
    76: r'''<h4 id="dfn">Definisi</h4>''',
    78: r'''<p>Tujuan kita berikutnya ialah mendefinisikan statistik yang mengukur asosiasi antara data \(x\) dan \(y\).</p>''',
    80: r'''<div class="unit" id="o006.random.sample.covariance.unit.sample-covariance-correlation-definition">''',
    81: r'''\t<p class="math">Untuk ukuran sampel sedikitnya dua, <dfn>kovarians sampel</dfn> didefinisikan sebagai''',
    83: r'''\tDengan mengasumsikan bahwa vektor data tidak konstan sehingga simpangan bakunya positif, <dfn>korelasi sampel</dfn> didefinisikan sebagai''',
    87: r'''<p>Perhatikan bahwa kovarians sampel merupakan rata-rata hasil kali simpangan data \(x\) dan \(y\) dari rata-ratanya. Karena itu, satuan fisik kovarians sampel adalah hasil kali satuan \( x \) dan \( y \). Korelasi adalah bentuk kovarians yang telah dibakukan. Secara khusus, korelasi tidak berdimensi (tidak memiliki satuan fisik), sebab kovarians pada pembilang dan hasil kali simpangan baku pada penyebut memiliki satuan yang sama (yaitu hasil kali satuan \(x\) dan \(y\)). Perhatikan pula bahwa kovarians dan korelasi memiliki <dfn>tanda</dfn> yang sama: positif, negatif, atau nol. Pada kasus pertama, data \(\bs{x}\) dan \(\bs{y}\) dikatakan <dfn>berkorelasi positif</dfn>; pada kasus kedua, \(\bs{x}\) dan \(\bs{y}\) dikatakan <dfn>berkorelasi negatif</dfn>; dan pada kasus ketiga, \(\bs{x}\) dan \(\bs{y}\) dikatakan <dfn>tidak berkorelasi</dfn>.</p>''',
    89: r'''<p>Untuk melihat bahwa kovarians sampel merupakan ukuran asosiasi, ingat terlebih dahulu bahwa titik \(\left(m(\bs{x}), m(\bs{y})\right)\) merupakan ukuran pusat data bivariat. Bahkan, jika setiap titik adalah lokasi suatu massa satuan, maka \(\left(m(\bs{x}), m(\bs{y})\right)\) adalah <em>pusat massa</em> sebagaimana didefinisikan dalam fisika. Garis horizontal dan vertikal yang melalui titik pusat ini membagi bidang menjadi empat kuadran. Hasil kali simpangan \([x_i - m(\bs{x})][y_i - m(\bs{y})]\) bernilai positif di kuadran pertama dan ketiga, serta negatif di kuadran kedua dan keempat. Setelah mempelajari regresi linear di <a href="#reg" class="ref"></a>, kita akan memahami dengan jauh lebih mendalam apa yang diukur oleh kovarians.</p>''',
    92: r'''\t<figcaption>Diagram pencar dengan rata-rata</figcaption>''',
    93: r'''\t<img src="ScatterPlotMeans.png" alt="Diagram pencar dengan rata-rata">''',
    96: r'''<p>Anda mungkin bertanya-tanya mengapa kita merata-ratakan hasil kali simpangan dengan membagi oleh \(n - 1\), bukan \(n\). Penjelasan utamanya ialah bahwa dalam model probabilitas di <a href="#prb" class="ref"></a>, pilihan ini membuat kovarians sampel menjadi penaksir takbias bagi kovarians distribusi. Pemilihan pembagi ini juga dapat dipahami secara tepat melalui <dfn>derajat kebebasan</dfn>, seperti pada <a href="Variance.html">varians sampel</a>. Kedua vektor data mula-mula memiliki \(2 n\) koordinat. Pemusatan dengan rata-rata \(m(\bs{x})\) dan \(m(\bs{y})\) mengenakan satu kendala jumlah-nol pada setiap vektor, sehingga pasangan vektor berpusat memiliki \(2 n - 2\) derajat kebebasan. Setiap vektor berpusat berada dalam subruang berdimensi \(n - 1\), dan kovarians adalah hasil kali dalam kedua vektor tersebut yang dinormalisasi dengan \(n - 1\); tidak ada pengurangan derajat kebebasan tambahan ketika hasil kali komponennya dihitung. Namun, dari sudut pandang yang murni deskriptif, membagi oleh \(n\) juga masuk akal.</p>''',
    98: r'''<p>Ingat bahwa terdapat distribusi probabilitas alami yang berkaitan dengan data, yaitu distribusi empiris yang memberikan probabilitas \(\frac{1}{n}\) kepada setiap titik data \((x_i, y_i)\). (Jadi, jika titik-titik ini berbeda, distribusi tersebut adalah <a href="../dist/Discrete.html#uni">distribusi seragam diskret</a> pada data.) Rata-rata sampel tidak lain adalah <a href="../expect/Properties.html">nilai harapan</a> distribusi bivariat ini, dan kecuali suatu faktor konstan (pembagian oleh \(n - 1\), bukan \(n\)), varians sampel tidak lain adalah <a href="../expect/Variance.html">varians</a> distribusi bivariat ini. Demikian pula, kecuali suatu faktor konstan (sekali lagi pembagian oleh \(n - 1\), bukan \(n\)), kovarians sampel adalah <a href="../expect/Covariance.html">kovarians</a> distribusi bivariat dan korelasi sampel adalah korelasi distribusi bivariat. Semua hasil berikut dalam pembahasan statistika deskriptif sebenarnya merupakan kasus khusus dari hasil yang lebih umum untuk distribusi probabilitas.</p>''',
    100: r'''<h4 id="cov">Sifat-Sifat Kovarians</h4>''',
    102: r'''<p>Beberapa latihan berikut menetapkan sejumlah sifat penting kovarians sampel. Seperti biasa, simbol tebal menyatakan sampel berukuran tetap \(n\) dari variabel populasi yang bersesuaian (yaitu vektor dengan panjang \(n\)), sedangkan simbol dengan huruf biasa menyatakan bilangan riil. Hasil pertama adalah rumus kovarians sampel yang kadang-kadang lebih baik daripada definisinya untuk keperluan komputasi. Agar hasilnya dapat dinyatakan secara ringkas, misalkan \(\bs{x} \bs{y} = (x_1 \, y_1, x_2 \, y_2, \ldots, x_n \, y_n)\) menyatakan sampel dari variabel hasil kali \(x y\).</p>''',
    105: r'''\t<p class="math">Kovarians sampel dapat dihitung sebagai berikut:''',
    106: r'''\t\[ s(\bs{x}, \bs{y}) = \frac{1}{n - 1} \sum_{i=1}^n x_i \, y_i - \frac{n}{n - 1} m(\bs{x}) m(\bs{y}) = \frac{n}{n - 1} [m(\bs{x y}) - m(\bs{x}) m(\bs{y})] \]</p>''',
    108: r'''\t\t<summary>Rincian:</summary>''',
    109: r'''\t\t<p>Perhatikan bahwa''',
    119: r'''<p>Teorema berikut memberikan rumus lain untuk kovarians sampel, yang tidak memerlukan perhitungan statistik perantara.</p>''',
    122: r'''\t<p class="math">Kovarians sampel dapat dihitung sebagai berikut:''',
    125: r'''\t\t<summary>Rincian:</summary>''',
    126: r'''\t\t<p>Perhatikan bahwa''',
    131: r'''\t\tKita menghitung jumlah-jumlah tersebut suku demi suku. Jumlah pertama adalah''',
    133: r'''\t\tDua jumlah berikutnya bernilai 0. Jumlah terakhir adalah''',
    135: r'''\t\tMembagi seluruh jumlah dengan \(2 n (n - 1)\) menghasilkan \(\cov(\bs{x}, \bs{y})\).</p>''',
    139: r'''<p>Seperti tersirat dari namanya, kovarians sampel memperumum varians sampel.</p>''',
    145: r'''<p>Berdasarkan <a href="#cov3" class="ref"></a>, kini kita dapat melihat bahwa rumus komputasi pertama di <a href="#cov1" class="ref"></a> dan rumus komputasi kedua di <a href="#cov2" class="ref"></a> memperumum rumus-rumus komputasi untuk <a href="Variance.html">varians sampel</a>. Jelas bahwa kovarians sampel bersifat <dfn>simetris</dfn>.</p>''',
    151: r'''<p>Kovarians sampel bersifat linear dalam argumen pertama ketika argumen kedua ditetapkan.</p>''',
    154: r'''\t<p class="math">Jika \(\bs{x}\), \(\bs{y}\), dan \(\bs{z}\) masing-masing adalah vektor data dari variabel populasi \(x\), \(y\), dan \(z\), serta \(c\) adalah suatu konstanta, maka</p>''',
    160: r'''\t\t<summary>Rincian:</summary>''',
    162: r'''\t\t\t<li>Ingat bahwa \(m(\bs{x} + \bs{y}) = m(\bs{x}) + m(\bs{y})\). Oleh karena itu,''',
    169: r'''\t\t\t<li>Ingat bahwa \(m(c \bs{x}) = c m(\bs{x})\). Oleh karena itu,''',
    178: r'''<p>Karena sifat simetri, kovarians sampel juga linear dalam argumen kedua ketika argumen pertama ditetapkan, sehingga bersifat <dfn>bilinear</dfn>. Bentuk umum sifat bilinear diberikan dalam teorema berikut:</p>''',
    181: r'''\t<p class="math">Misalkan \(\bs{x}_i\) adalah vektor data dari variabel populasi \(x_i\) untuk \(i \in \{1, 2, \ldots, k\}\), dan \(\bs{y}_j\) adalah vektor data dari variabel populasi \(y_j\) untuk \(j \in \{1, 2, \ldots, l\}\). Misalkan pula \(a_1, \, a_2, \ldots, \, a_k\) dan \(b_1, \, b_2, \ldots, b_l\) adalah konstanta. Maka''',
    185: r'''<p>Suatu kasus khusus dari sifat bilinear memberikan cara yang baik untuk menghitung varians sampel dari suatu jumlah.</p>''',
    190: r'''\t\t<summary>Rincian:</summary>''',
    191: r'''\t\t<p>Dari hasil-hasil sebelumnya,''',
    199: r'''<p>Perumuman hasil ini untuk jumlah tiga vektor atau lebih sepenuhnya langsung: varians sampel dari suatu jumlah adalah jumlah semua kovarians sampel berpasangan. Perhatikan bahwa varians sampel suatu jumlah dapat lebih besar, lebih kecil, atau sama dengan jumlah varians sampelnya, bergantung pada tanda dan besar suku-suku silang kovarians. Secara khusus, jika vektor-vektor tersebut tidak berkorelasi secara berpasangan, varians jumlah sama dengan jumlah variansnya.</p>''',
    202: r'''\t<p class="math">Jika \(\bs{c}\) adalah himpunan data konstan, maka \(s(\bs{x}, \bs{c}) = 0\).</p>''',
    204: r'''\t\t<summary>Rincian:</summary>''',
    205: r'''\t\t<p>Hasil ini langsung mengikuti definisi. Jika \(c_i = c\) untuk setiap \(i\), maka \(m(\bs{c}) = c\), sehingga \(c_i - m(\bs{c}) = 0\) untuk setiap \(i\).</p>''',
    209: r'''<p>Dengan menggabungkan hasil latihan terakhir dan sifat bilinear di <a href="#cov6" class="ref"></a>, kita melihat bahwa kovarians tidak berubah jika konstanta ditambahkan pada himpunan data. Artinya, jika \(\bs{c}\) dan \(\bs{d}\) adalah vektor konstan, maka \(s(\bs{x}+ \bs{c}, \bs{y} + \bs{d}) = s(\bs{x}, \bs{y})\).</p>''',
    211: r'''<h4 id="cor">Sifat-Sifat Korelasi</h4>''',
    213: r'''<p>Beberapa sifat sederhana korelasi diberikan berikut ini. Sebagian besar mudah diperoleh dari sifat kovarians yang bersesuaian. Pertama, ingat bahwa <a href="Variance.html">skor baku</a> dari \(x_i\) dan \(y_i\) masing-masing adalah''',
    215: r'''Skor baku dari suatu himpunan data merupakan besaran tak berdimensi yang memiliki rata-rata 0 dan varians 1.</p>''',
    218: r'''\t<p class="math">Korelasi antara \(\bs{x}\) dan \(\bs{y}\) adalah kovarians skor bakunya \(\bs{u}\) dan \(\bs{v}\). Artinya, \(r(\bs{x}, \bs{y}) = s(\bs{u}, \bs{v})\).</p>''',
    220: r'''\t\t<summary>Rincian:</summary>''',
    221: r'''\t\t<p>Dalam notasi vektor, dengan simbol 1 tebal menyatakan vektor semua-satu, perhatikan bahwa''',
    222: r'''\t\t\[ \bs{u} = \frac{1}{s(\bs{x})}[\bs{x} - m(\bs{x})], \quad \bs{v} = \frac{1}{s(\bs{y})}[\bs{y} - m(\bs{y})] \]''',
    223: r'''\t\tKarena itu, hasilnya langsung mengikuti sifat-sifat kovarians:''',
    228: r'''<p>Korelasi bersifat simetris.</p>''',
    234: r'''<p>Berbeda dari kovarians, korelasi tidak berubah jika salah satu himpunan data dikalikan dengan konstanta positif (ingat bahwa hal ini selalu dapat dipandang sebagai perubahan skala pada variabel yang mendasarinya). Sebaliknya, mengalikan suatu himpunan data dengan konstanta negatif mengubah tanda korelasi.</p>''',
    237: r'''\t<p class="math">Jika \(c \ne 0\) adalah suatu konstanta, maka</p>''',
    239: r'''\t\t<li>\(r(c \bs{x}, \bs{y}) = r(\bs{x}, \bs{y})\) jika \(c \gt 0\)</li>''',
    240: r'''\t\t<li>\(r(c \bs{x}, \bs{y}) = -r(\bs{x}, \bs{y})\) jika \(c \lt 0\)</li>''',
    243: r'''\t\t<summary>Rincian:</summary>''',
    244: r'''\t\t<p>Berdasarkan definisi dan sifat penskalaan kovarians di <a href="#cov5" class="ref"></a>,''',
    246: r'''\t\tdan tentu saja, \( c / \left|c\right| = 1 \) jika \( c \gt 0 \), serta \( c / \left|c\right| = -1 \) jika \( c \lt 0 \).</p>''',
    250: r'''<p>Seperti kovarians, korelasi tidak berubah ketika konstanta ditambahkan pada himpunan data. Menambahkan konstanta pada suatu himpunan data sering kali bersesuaian dengan <dfn>perubahan lokasi</dfn>.</p>''',
    253: r'''\t<p class="math">Jika \(\bs{c}\) dan \(\bs{d}\) adalah vektor konstan, maka \(r(\bs{x} + \bs{c}, \bs{y} + \bs{d}) = r(\bs{x}, \bs{y})\).</p>''',
    255: r'''\t\t<summary>Rincian:</summary>''',
    256: r'''\t\t<p>Hasil ini langsung mengikuti sifat kovarians dan simpangan baku yang bersesuaian:''',
    261: r'''<p>Dua sifat terakhir menegaskan bahwa korelasi merupakan ukuran asosiasi baku yang tidak dipengaruhi oleh perubahan satuan pengukuran. Sebagai contoh, dalam <a href="JavaScript:openAncillary('../data/Challenger.html')" class="ancillary">himpunan data Challenger</a> pertama, variabel yang menjadi perhatian adalah suhu pada saat peluncuran (dalam derajat Fahrenheit) dan erosi cincin-O (dalam milimeter). Korelasi antara variabel-variabel ini sangat penting. Jika suhu diukur dalam derajat Celsius dan erosi cincin-O dalam inci, korelasi antara kedua variabel tidak akan berubah.</p>''',
    263: r'''<p>Sifat korelasi yang terpenting muncul ketika kita mempelajari garis yang paling sesuai dengan data, yaitu topik berikutnya.</p>''',
    265: r'''<h4 id="reg">Regresi Linear</h4>''',
    267: r'''<p>Dengan mengasumsikan bahwa varians sampel prediktor positif, kita ingin menemukan garis \(y = a + b x\) yang paling sesuai dengan titik-titik sampel \(\left((x_1, y_1), (x_2, y_2), \ldots, (x_n, y_n)\right)\). Ini merupakan masalah dasar dan penting dalam banyak bidang matematika, bukan hanya statistika. Kita memandang \(x\) sebagai <dfn>variabel prediktor</dfn> dan \(y\) sebagai <dfn>variabel respons</dfn>. Dengan demikian, istilah <em>paling sesuai</em> berarti bahwa kita ingin menemukan garis (yaitu mencari koefisien \(a\) dan \(b\)) yang meminimumkan rata-rata galat kuadrat antara nilai \(y\) aktual dalam data dan nilai \(y\) prediksi:''',
    269: r'''Perhatikan bahwa nilai \((a, b)\) yang meminimumkan akan sama jika fungsinya hanya berupa jumlah galat kuadrat, jika kita merata-ratakan dengan membagi oleh \(n\) alih-alih \(n - 1\), atau jika kita menggunakan akar kuadrat dari fungsi-fungsi tersebut. Tentu saja, <em>nilai minimum</em> fungsi yang sebenarnya akan berbeda jika kita mengubah fungsinya, tetapi sekali lagi, bukan titik \((a, b)\) tempat minimum itu terjadi. Pilihan khusus \(\mse\) sebagai fungsi galat paling sesuai untuk keperluan statistika. Menemukan \((a, b)\) yang meminimumkan \(\mse\) merupakan masalah standar dalam kalkulus.</p>''',
    272: r'''\t<p class="math">Grafik \(\mse\) adalah paraboloid yang membuka ke atas. Fungsi \(\mse\) mencapai minimum ketika''',
    278: r'''\t\t<summary>Rincian:</summary>''',
    279: r'''\t\t<p>Dari bentuk aljabar \( \mse \), kita dapat melihat bahwa grafiknya adalah paraboloid yang membuka ke atas. Untuk menemukan titik tunggal yang meminimumkan \( \mse \), perhatikan bahwa''',
    284: r'''\t\tMenyelesaikan \( \frac{\partial}{\partial a} \mse(a, b) = 0 \) menghasilkan \( a = m(\bs{y}) - b m(\bs{x}) \). Dengan menyubstitusikannya ke dalam \(\frac{\partial}{\partial b} \mse(a, b) = 0 \) dan menyelesaikan terhadap \( b \), diperoleh''',
    286: r'''\t\tDengan membagi pembilang dan penyebut pada ekspresi terakhir oleh \( n - 1 \) dan menggunakan rumus komputasi di atas, kita memperoleh \( b = s(\bs{x}, \bs{y}) / s^2(\bs{x}) \).</p>''',
    290: r'''<p>Tentu saja, nilai optimal \(a\) dan \(b\) adalah <em>statistik</em>, yaitu fungsi dari data. Dengan demikian, <dfn>garis regresi sampel</dfn> adalah''',
    294: r'''\t<figcaption>Diagram pencar dengan garis regresi</figcaption>''',
    295: r'''\t<img src="SampleRegression.png" alt="Diagram pencar dengan garis regresi">''',
    298: r'''<p>Perhatikan bahwa garis regresi melalui titik \(\left(m(\bs{x}), m(\bs{y})\right)\), yaitu pusat sampel titik-titik tersebut.</p>''',
    301: r'''\t<figcaption>Garis regresi melalui pusat</figcaption>''',
    302: r'''\t<img src="SampleRegressionMean.png" alt="Garis regresi melalui pusat">''',
    306: r'''\t<p class="math">Galat kuadrat rata-rata minimum adalah''',
    309: r'''\t\t<summary>Rincian:</summary>''',
    310: r'''\t\t<p>Hasil ini diperoleh dengan menyubstitusikan \( a(\bs{x}, \bs{y}) \) dan \( b(\bs{x}, \bs{y}) \) ke dalam \( \mse \), lalu menyederhanakannya.</p>''',
    315: r'''\t<p class="math">Korelasi dan kovarians sampel memenuhi sifat-sifat berikut.</p>''',
    319: r'''\t\t<li>\(r(\bs{x}, \bs{y}) = -1\) jika dan hanya jika titik-titik sampel terletak pada garis dengan kemiringan negatif.</li>''',
    320: r'''\t\t<li>\(r(\bs{x}, \bs{y}) = 1\) jika dan hanya jika titik-titik sampel terletak pada garis dengan kemiringan positif.</li>''',
    323: r'''\t\t<summary>Rincian:</summary>''',
    324: r'''\t\t<p>Perhatikan bahwa \( \mse \ge 0 \), sehingga berdasarkan teorema sebelumnya kita harus memiliki \( r^2(\bs{x}, \bs{y}) \le 1 \). Ini ekuivalen dengan bagian (a), yang selanjutnya, berdasarkan definisi korelasi sampel, ekuivalen dengan bagian (b). Untuk bagian (c) dan (d), perhatikan bahwa \( \mse(a, b) = 0 \) jika dan hanya jika \( y_i = a + b x_i \) untuk setiap \( i \), dan bahwa \( b(\bs{x}, \bs{y}) \) memiliki tanda yang sama dengan \( r(\bs{x}, \bs{y}) \).</p>''',
    328: r'''<p>Dengan demikian, kini kita melihat secara lebih mendalam bahwa kovarians dan korelasi sampel mengukur derajat kelinearan titik-titik sampel. Ingat dari pembahasan <a href="Variance.html#err">ukuran pusat dan penyebaran</a> bahwa konstanta \(a\) yang meminimumkan''',
    330: r'''adalah rata-rata sampel \(m(\bs{y})\), dan nilai minimum galat kuadrat rata-ratanya adalah varians sampel \(s^2(\bs{y})\). Jadi, selisih antara nilai galat kuadrat rata-rata ini dan nilai di <a href="#reg2" class="ref"></a>, yaitu \(s^2(\bs{y}) r^2(\bs{x}, \bs{y})\), adalah pengurangan variabilitas data \(y\) ketika suku linear dalam \(x\) ditambahkan pada prediktor. Pengurangan relatifnya ialah \(r^2(\bs{x}, \bs{y})\), sehingga statistik ini disebut <dfn>koefisien determinasi</dfn> (sampel). Perhatikan bahwa jika vektor data \(\bs{x}\) dan \(\bs{y}\) tidak berkorelasi, maka \(x\) tidak memberikan perbaikan prediksi linear bagi \(y\); garis regresi dalam kasus ini adalah garis horizontal \(y = m(\bs{y})\), dan galat kuadrat rata-ratanya adalah \(s^2(\bs{y})\).</p>''',
    332: r'''<p>Pemilihan variabel prediktor dan respons itu penting.</p>''',
    335: r'''\t<p class="math">Garis regresi sampel dengan \(x\) sebagai variabel prediktor dan \(y\) sebagai variabel respons tidak sama dengan garis regresi sampel dengan \(y\) sebagai variabel prediktor dan \(x\) sebagai variabel respons, kecuali dalam kasus ekstrem \(r(\bs{x}, \bs{y}) = \pm 1\), ketika semua titik sampel terletak pada satu garis.</p>''',
    338: r'''<h4 id="res">Residu</h4>''',
    340: r'''<p>Selisih antara nilai \(y\) aktual suatu titik data dan nilai yang diprediksi oleh garis regresi disebut <dfn>residu</dfn> titik data tersebut. Dengan demikian, residu yang bersesuaian dengan \((x_i, y_i)\) adalah \( d_i = y_i - \hat{y}_i \), dengan \( \hat{y}_i \) sebagai nilai garis regresi pada \( x_i \):''',
    342: r'''Perhatikan bahwa nilai prediksi \(\hat{y}_i\) dan residu \(d_i\) adalah <em>statistik</em>, yaitu fungsi dari data \((\bs{x}, \bs{y})\), tetapi kebergantungan ini tidak ditampilkan dalam notasi demi kesederhanaan.</p>''',
    345: r'''\t<p class="math">Jumlah residu sama dengan 0: \( \sum_{i=1}^n d_i = 0 \).</p>''',
    347: r'''\t\t<summary>Rincian:</summary>''',
    348: r'''\t\t<p>Hasil ini mengikuti langsung dari definisi dan menyatakan kembali fakta bahwa garis regresi melalui pusat himpunan data \( \left(m(\bs{x}), m(\bs{y})\right) \).</p>''',
    352: r'''<p>Berbagai plot residu dapat membantu memahami hubungan antara data \(x\) dan \(y\). Beberapa yang paling umum diberikan dalam definisi berikut:</p>''',
    355: r'''\t<p class="math">Plot residu<p>''',
    357: r'''\t\t<li>Plot \((i, d_i)\) untuk \(i \in \{1, 2, \ldots, n\}\), yaitu plot indeks terhadap residu.</li>''',
    358: r'''\t\t<li>Plot \((x_i, d_i)\) untuk \(i \in \{1, 2, \ldots, n\}\), yaitu plot nilai \(x\) terhadap residu.</li>''',
    359: r'''\t\t<li>Plot \((d_i, y_i)\) untuk \(i \in \{1, 2, \ldots, n\}\), yaitu plot residu terhadap nilai \(y\) aktual.</li>''',
    360: r'''\t\t<li>Plot \((d_i, \hat{y}_i)\) untuk \(i \in \{1, 2, \ldots, n\}\), yaitu plot residu terhadap nilai \(y\) prediksi.</li>''',
    361: r'''\t\t<li><a href="Mean.html#his">Histogram</a> residu \((d_1, d_2, \ldots, d_n)\).</li>''',
    365: r'''<h4 id="ssq">Jumlah Kuadrat</h4>''',
    367: r'''<p>Untuk pembahasan berikutnya, kita akan menafsirkan ulang rumus galat kuadrat rata-rata minimum di <a href="#reg2" class="ref"></a>. Berikut adalah definisi-definisi barunya:</p>''',
    370: r'''\t<p class="dfn">Jumlah kuadrat</p>''',
    372: r'''\t\t<li>\(\sst(\bs{y}) = \sum_{i=1}^n [y_i - m(\bs{y})]^2 \) adalah <dfn>jumlah kuadrat total</dfn>.</li>''',
    373: r'''\t\t<li>\(\ssr(\bs{x}, \bs{y}) = \sum_{i=1}^n [\hat{y}_i - m(\bs{y})]^2 \) adalah <dfn>jumlah kuadrat regresi</dfn>.</li>''',
    374: r'''\t\t<li>\(\sse(\bs{x}, \bs{y}) = \sum_{i=1}^n (y_i - \hat{y}_i)^2\) adalah <dfn>jumlah kuadrat galat</dfn>.</li>''',
    378: r'''<p>Perhatikan bahwa \(\sst(\bs{y})\) tidak lain adalah \(n - 1\) kali varians \(s^2(\bs{y})\), dan merupakan jumlah kuadrat seluruh simpangan nilai \(y\) dari rata-rata nilai \(y\). Demikian pula, \(\sse(\bs{x}, \bs{y})\) tidak lain adalah \(n - 1\) kali galat kuadrat rata-rata minimum yang diberikan di atas. Tentu saja, \(\sst(\bs{y})\) memiliki \(n - 1\) derajat kebebasan, sedangkan \(\sse(\bs{x}, \bs{y})\) memiliki \(n - 2\) derajat kebebasan dan \(\ssr(\bs{x}, \bs{y})\) memiliki satu derajat kebebasan. Jumlah kuadrat total adalah jumlah dari jumlah kuadrat regresi dan jumlah kuadrat galat:</p>''',
    381: r'''\t<p class="math">Jumlah-jumlah kuadrat berkaitan sebagai berikut:</p>''',
    387: r'''\t\t<summary>Rincian:</summary>''',
    388: r'''\t\t<p>Berdasarkan definisi \(\sst\) dan \(r\), kita melihat bahwa \(r^2(\bs{x}, \bs{y}) \sst(\bs{y}) = s^2(\bs{x}, \bs{y}) \big/ s^2(\bs{x})\). Namun, dari persamaan regresi,''',
    390: r'''\t\tMenjumlahkan terhadap \(i\) menghasilkan''',
    391: r'''\t\t\[ \ssr(\bs{x}, \bs{y}) = \sum_{i=1}^n [\hat{y}_i - m(\bs{y})]^2 = \frac{s^2(\bs{x}, \bs{y})}{s^2(\bs{x})} \]''',
    392: r'''\t\tOleh karena itu, \(\ssr(\bs{x}, \bs{y}) = r^2(\bs{x}, \bs{y}) \sst(\bs{y})\). Terakhir, dengan mengalikan hasil di atas oleh \(n - 1\), diperoleh \(\sse(\bs{x}, \bs{y}) = \sst(\bs{y}) - r^2(\bs{x}, \bs{y}) \sst(\bs{y}) = \sst(\bs{y}) - \ssr(\bs{x}, \bs{y})\).</p>''',
    396: r'''<p>Perhatikan bahwa \(r^2(\bs{x}, \bs{y}) = \ssr(\bs{x}, \bs{y}) \big/ \sst(\bs{y})\), sehingga sekali lagi \(r^2(\bs{x}, \bs{y})\) adalah koefisien determinasi&mdash;proporsi variabilitas dalam data \(y\) yang dijelaskan oleh data \(x\). Kita dapat merata-ratakan \(\sse\) dengan membaginya dengan derajat kebebasannya, lalu mengambil akar kuadrat untuk memperoleh galat baku:</p>''',
    398: r'''<div class="unit" id="o006.random.sample.covariance.unit.standard-error-of-estimate">''',
    399: r'''\t<p class="math">Untuk ukuran sampel sedikitnya tiga, <dfn>galat baku taksiran</dfn> adalah''',
    403: r'''<p>Besaran ini memang merupakan galat <em>baku</em> dalam arti yang sama dengan simpangan <em>baku</em>. Besaran ini merupakan semacam rata-rata galat, tetapi dalam pengertian akar rata-rata kuadrat.</p>''',
    405: r'''<p>Terakhir, penting diperhatikan bahwa regresi linear merupakan gagasan yang jauh lebih kuat daripada yang mungkin tampak pada awalnya, dan istilah <em>linear</em> sebenarnya dapat sedikit menyesatkan. Dengan menerapkan berbagai transformasi pada \(y\), \(x\), atau keduanya, kita dapat menyesuaikan beragam kurva berparameter dua pada data \(\left((x_1, y_1), (x_2, y_2), \ldots, (x_n, y_n)\right)\). Beberapa transformasi yang paling umum dibahas dalam latihan di <a href="#trn" class="ref"></a>.</p>''',
    407: r'''<h3 id="prb">Teori Probabilitas</h3>''',
    409: r'''<p>Kita melanjutkan pembahasan kovarians, korelasi, dan regresi sampel, tetapi sekarang dari sudut pandang yang lebih menarik, yakni dengan memperlakukan variabel-variabel tersebut sebagai variabel acak. Secara khusus, misalkan kita memiliki suatu <a href="../prob/Experiments.html">eksperimen acak</a> dasar, dan \(X\) serta \(Y\) adalah <a href="../prob/Probability.html">variabel acak</a> bernilai riil untuk eksperimen tersebut. Secara ekuivalen, \((X, Y)\) adalah vektor acak yang mengambil nilai di \(\R^2\). Misalkan \(\mu = \E(X)\) dan \(\nu = \E(Y)\) menyatakan <a href="../expect/Properties.html">rata-rata distribusi</a>, \(\sigma^2 = \var(X)\) dan \(\tau^2 = \var(Y)\) menyatakan <a href="../expect/Variance.html">varians distribusi</a>, serta \(\delta = \cov(X, Y)\) menyatakan <a href="../expect/Covariance.html">kovarians distribusi</a>, sehingga korelasi distribusinya adalah''',
    411: r'''Kita juga memerlukan beberapa momen berorde lebih tinggi. Misalkan \(\sigma_4 = \E\left[(X - \mu)^4\right]\), \(\tau_4 = \E\left[(Y - \nu)^4\right]\), dan \(\delta_2 = \E\left[(X - \mu)^2 (Y - \nu)^2\right]\). Kita mengasumsikan bahwa semua momen tersebut berhingga dan bahwa kedua simpangan baku distribusi positif.</p>''',
    413: r'''<p>Sekarang misalkan kita menjalankan eksperimen dasar sebanyak \(n\) kali. Ini menghasilkan eksperimen majemuk dengan urutan vektor acak <a href="../prob/Independence.html">independen</a> \(\left((X_1, Y_1), (X_2, Y_2), \ldots, (X_n, Y_n)\right)\), yang masing-masing memiliki distribusi yang sama dengan \((X, Y)\). Dalam istilah statistika, ini adalah <a href="Introduction.html">sampel acak</a> berukuran \(n\) dari distribusi \((X, Y)\). Statistik yang dibahas dalam <a href="#des">subbagian sebelumnya</a> terdefinisi dengan baik, tetapi kini semuanya merupakan variabel acak. Kita menggunakan notasi yang telah ditetapkan sebelumnya, kecuali bahwa sesuai konvensi biasa, variabel acak dilambangkan dengan huruf kapital. Tentu saja, sifat dan hubungan deterministik yang ditetapkan pada subbagian sebelumnya tetap berlaku. Perhatikan bahwa \(\bs{X} = (X_1, X_2, \ldots, X_n)\) adalah sampel acak berukuran \(n\) dari distribusi \(X\), dan \(\bs{Y} = (Y_1, Y_2, \ldots, Y_n)\) adalah sampel acak berukuran \(n\) dari distribusi \(Y\). Tujuan utama subbagian ini ialah mempelajari hubungan antara berbagai statistik dari \(\bs{X}\) dan \(\bs{Y}\), serta statistik yang merupakan penaksir alami bagi kovarians dan korelasi distribusi.</p>''',
    415: r'''<h4 id="men">Rata-Rata Sampel</h4>''',
    417: r'''<p>Ingat bahwa rata-rata sampel adalah''',
    419: r'''Dari bagian mengenai <a href="LLN.html">hukum bilangan besar</a> dan <a href="CLT.html">teorema limit pusat</a>, kita mengetahui banyak hal tentang distribusi \(M(\bs{X})\) dan \(M(\bs{Y})\) secara <em>individual</em>. Namun, kita perlu mengetahui lebih banyak tentang <em>distribusi bersama</em>.</p>''',
    422: r'''\t<p class="math">Kovarians dan korelasi antara \(M(\bs{X})\) dan \(M(\bs{Y})\) adalah</p>''',
    425: r'''\t\t<li>\(\cor[(M(\bs{X}), M(\bs{Y})] = \rho\)</li>''',
    428: r'''\t\t<summary>Rincian:</summary>''',
    429: r'''\t\t<p>Bagian (a) mengikuti sifat bilinear operator kovarians:''',
    431: r'''\t\tKarena independensi, suku-suku dalam jumlah terakhir bernilai 0 jika \(i \ne j\). Untuk \(i = j\), suku-sukunya adalah \(\cov(X, Y) = \delta\). Terdapat \(n\) suku demikian, sehingga \(\cov[M(\bs{X}), M(\bs{Y})] = \delta / n\). Untuk bagian (b), ingat bahwa \(\var[M(\bs{X})] = \sigma^2 / n\) dan \(\var[M(\bs{Y})] = \tau^2 / n\). Oleh karena itu,''',
    436: r'''<p>Perhatikan bahwa korelasi antara rata-rata sampel sama dengan korelasi distribusi pengambilan sampel yang mendasarinya. Secara khusus, korelasi tersebut tidak bergantung pada ukuran sampel \(n\).</p>''',
    438: r'''<h4 id="var">Varians Sampel</h4>''',
    440: r'''<p>Ingat bahwa bentuk khusus <a href="Variance.html#spe">varians sampel</a>, dalam keadaan yang jarang terjadi ketika rata-rata distribusi diketahui, adalah''',
    442: r'''Sekali lagi, kita telah mempelajari statistik ini secara individual, sehingga sekarang penekanan kita adalah pada distribusi bersamanya.</p>''',
    445: r'''\t<p class="math">Dengan mengasumsikan bahwa penyebut korelasi positif, kovarians dan korelasi antara \(W^2(\bs{X})\) dan \(W^2(\bs{Y})\) adalah</p>''',
    451: r'''\t\t<summary>Rincian:</summary>''',
    452: r'''\t\t<p>Untuk bagian (a), kita menggunakan sifat bilinear operator kovarians untuk memperoleh''',
    454: r'''\t\tKarena independensi, suku-suku dalam jumlah terakhir bernilai 0 ketika \(i \ne j\). Ketika \(i = j\), suku-sukunya adalah''',
    455: r'''\t\t\[ \cov[(X - \mu)^2 (Y - \nu)^2] = \E[(X - \mu)^2 (Y - \nu)^2] - \E[(X - \mu)^2] \E[(Y - \nu)^2] = \delta_2 - \sigma^2 \tau^2 \]''',
    456: r'''\t\tTerdapat \(n\) suku demikian, sehingga \(\cov[W^2(\bs{X}), W^2(\bs{Y})] = (\delta_2 - \sigma^2 \tau^2) \big/ n\). Bagian (b) mengikuti bagian (a) dan varians \(W^2(\bs{X})\) serta \(W^2(\bs{Y})\) dari bagian <a href="Variance.html">Varians Sampel</a>.</p>''',
    460: r'''<p>Perhatikan bahwa korelasi tidak bergantung pada ukuran sampel \(n\). Selanjutnya, ingat bahwa bentuk standar varians sampel adalah''',
    464: r'''\t<p class="math">Dengan mengasumsikan bahwa penyebut korelasi positif, kovarians dan korelasi varians sampel adalah</p>''',
    470: r'''\t\t<summary>Rincian:</summary>''',
    471: r'''\t\t<p>Ingat bahwa''',
    473: r'''\t\tDengan menggunakan sifat bilinear operator kovarians, kita memperoleh''',
    475: r'''\t\tKita menghitung kovarians dalam jumlah ini dengan mempertimbangkan kasus-kasus saling lepas:</p>''',
    477: r'''\t\t\t<li>\(\cov[(X_i - X_j)^2, (Y_k - Y_l)^2] = 0\) jika \(i = j\) atau \(k = l\), dan terdapat \(2 n^3 - n^2\) suku demikian.</li>''',
    478: r'''\t\t\t<li>\(\cov[(X_i - X_j)^2, (Y_k - Y_l)^2] = 0\) berdasarkan independensi jika \(i, j, k, l\) semuanya berbeda, dan terdapat \(n (n - 1)(n - 2)(n - 3)\) suku demikian.</li>''',
    479: r'''\t\t\t<li>\(\cov[(X_i - X_j)^2, (Y_k - Y_l)^2] = 2 \delta_2 - 2 \sigma^2 \tau^2 + 4 \delta^2\) jika \(i \ne j\) dan \(\{k, l\} = \{i, j\}\), dan terdapat \(2 n (n - 1)\) suku demikian.</li>''',
    480: r'''\t\t\t<li>\(\cov[(X_i - X_j)^2, (Y_k - Y_l)^2] = \delta_2 - \sigma^2 \tau^2\) jika \(i \ne j\), \(k \ne l\), dan \(\#(\{i, j\} \cap \{k, l\}) = 1\), dan terdapat \(4 n (n - 1)(n - 2)\) suku demikian.</li>''',
    482: r'''\t\t<p>Substitusi dan penyederhanaan memberikan hasil pada (a). Untuk (b), kita menggunakan definisi korelasi dan rumus \(\var[S^2(\bs{X})]\) serta \(\var[S^2(\bs{Y})]\) dari bagian <a href="Variance.html#std">varians sampel</a>.</p>''',
    486: r'''<p>Secara asimtotik, korelasi antara varians sampel sama dengan korelasi antara varians sampel khusus yang diberikan di <a href="#var1" class="ref"></a>:''',
    487: r'''\[ \cor\left[S^2(\bs{X}), S^2(\bs{Y})\right] \to \frac{\delta_2 - \sigma^2 \tau^2}{\sqrt{(\sigma_4 - \sigma^4)(\tau_4 - \tau^4)}} \text{ as } n \to \infty \]</p>''',
    489: r'''<h4 id="prbcov">Kovarians Sampel</h4>''',
    491: r'''<p>Pertama, misalkan rata-rata distribusi \(\mu\) dan \(\nu\) diketahui. Seperti disebutkan sebelumnya, asumsi ini hampir selalu tidak realistis, tetapi tetap merupakan titik awal yang baik karena analisisnya sangat sederhana dan hasil yang diperoleh akan berguna di bawah.</p>''',
    493: r'''<div class="unit" id="o006.random.sample.covariance.unit.special-sample-covariance-definition">''',
    494: r'''\t<p class="dfn">Penaksir alami bagi kovarians distribusi \(\delta = \cov(X, Y)\) ketika rata-rata distribusi diketahui adalah <dfn>kovarians sampel khusus</dfn>''',
    498: r'''<p>Perhatikan bahwa kovarians sampel khusus memperumum varians sampel khusus: \(W(\bs{X}, \bs{X}) = W^2(\bs{X})\).</p>''',
    501: r'''\t<p class="math">\(W(\bs{X}, \bs{Y})\) adalah rata-rata dari sampel acak berukuran \(n\) yang berasal dari distribusi \((X - \mu)(Y - \nu)\), dan memenuhi sifat-sifat berikut:</p>''',
    505: r'''\t\t<li>\(W(\bs{X}, \bs{Y}) \to \delta\) ketika \(n \to \infty\) dengan probabilitas 1</li>''',
    508: r'''\t\t<summary>Rincian:</summary>''',
    509: r'''\t\t<p>Hasil-hasil ini langsung mengikuti bagian mengenai <a href="LLN.html">hukum bilangan besar</a>. Untuk bagian (b), perhatikan bahwa''',
    514: r'''<p>Sebagai penaksir \(\delta\), bagian (a) berarti bahwa \(W(\bs{X}, \bs{Y})\) bersifat <dfn>takbias</dfn>, sedangkan bagian (c), bersama dengan varians pada bagian (b), menunjukkan bahwa \(W(\bs{X}, \bs{Y})\) bersifat <dfn>konsisten</dfn>.</p>''',
    516: r'''<p>Sekarang pertimbangkan asumsi yang lebih realistis bahwa rata-rata distribusi \(\mu\) dan \(\nu\) tidak diketahui. Pendekatan alami dalam kasus ini ialah merata-ratakan \([(X_i - M(\bs{X})][Y_i - M(\bs{Y})]\) terhadap \(i \in \{1, 2, \ldots, n\}\). Namun, alih-alih membagi rata-rata kita dengan \(n\), kita harus membaginya dengan konstanta yang menghasilkan penaksir takbias bagi \(\delta\). Seperti ditunjukkan di <a href="#prbcov2" class="ref"></a>, konstanta tersebut adalah \(n - 1\), sehingga diperoleh definisi berikut:</p>''',
    518: r'''<div class="unit" id="o006.random.sample.covariance.unit.sample-covariance-correlation-definition-probability">''',
    519: r'''\t<p class="dfn">Untuk ukuran sampel sedikitnya dua, <dfn>kovarians sampel</dfn> standar adalah''',
    521: r'''\tJika kedua simpangan baku sampel positif, <dfn>korelasi sampel</dfn> adalah''',
    529: r'''\t\t<summary>Rincian:</summary>''',
    530: r'''\t\t<p>Dengan mengembangkan seperti di atas, kita memperoleh''',
    532: r'''\t\tNamun, \(\E(X_i Y_i) = \cov(X_i, Y_i) + \E(X_i) \E(Y_i) = \delta + \mu \nu\). Demikian pula, berdasarkan kovarians rata-rata sampel dan sifat takbias, \(\E[M(\bs{X}) M(\bs{Y})] = \cov[M(\bs{X}), M(\bs{Y})] + \E[M(\bs{X})] \E[M(\bs{Y})] = \delta / n + \mu \nu\). Jadi, dengan mengambil nilai harapan pada persamaan yang ditampilkan di atas, diperoleh''',
    538: r'''\t<p class="math">\(S(\bs{X}, \bs{Y}) \to \delta\) ketika \(n \to \infty\) dengan probabilitas 1.</p>''',
    540: r'''\t<summary>Rincian:</summary>''',
    541: r'''\t\t<p>Sekali lagi, kita memiliki''',
    543: r'''\t\tdengan \(M(\bs{X} \bs{Y})\) menyatakan rata-rata sampel dari sampel hasil kali \((X_1 Y_1, X_2 Y_2, \ldots, X_n Y_n)\). Berdasarkan hukum kuat bilangan besar, \(M(\bs{X}) \to \mu\) ketika \(n \to \infty\), \(M(\bs{Y}) \to \nu\) ketika \(n \to \infty\), dan \(M(\bs{X} \bs{Y}) \to \E(X Y) = \delta + \mu \nu\) ketika \(n \to \infty\), masing-masing dengan probabilitas 1. Jadi, hasilnya diperoleh dengan mengambil limit \(n \to \infty\) pada persamaan yang ditampilkan.</p>''',
    547: r'''<p>Karena korelasi sampel \(R(\bs{X}, \bs{Y})\) merupakan fungsi nonlinear dari kovarians sampel dan simpangan baku sampel, secara umum statistik ini bukan penaksir takbias bagi korelasi distribusi \(\rho\). Dalam kebanyakan kasus, bahkan rata-rata dan varians \(R(\bs{X}, \bs{Y})\) akan sulit dihitung. Meskipun demikian, kita dapat menunjukkan konvergensi korelasi sampel menuju korelasi distribusi.</p>''',
    550: r'''\t<p class="math">\(R(\bs{X}, \bs{Y}) \to \rho\) ketika \(n \to \infty\) dengan probabilitas 1.</p>''',
    552: r'''\t\t<summary>Rincian:</summary>''',
    553: r'''\t\t<p>Hasil ini langsung mengikuti hukum kuat bilangan besar dan hasil-hasil sebelumnya. Dari <a href="#prbcov3" class="ref"></a>, \(S(\bs{X}, \bs{Y}) \to \delta\) ketika \(n \to \infty\), dan dari bagian mengenai <a href="Variance.html">varians sampel</a>, \(S(\bs{X}) \to \sigma\) ketika \(n \to \infty\) serta \(S(\bs{Y}) \to \tau\) ketika \(n \to \infty\), masing-masing dengan probabilitas 1. Karena itu, \(R(\bs{X}, \bs{Y}) \to \delta / \sigma \tau = \rho\) ketika \(n \to \infty\) dengan probabilitas 1.</p>''',
    557: r'''<p>Teorema <a href="#prbcov5" class="ref"></a> berikut memberikan rumus bagi varians kovarians sampel, yang tidak boleh disamakan dengan kovarians varians sampel di <a href="#var2" class="ref"></a>!</p>''',
    560: r'''\t<p class="math">Varians kovarians sampel adalah''',
    563: r'''\t\t<summary>Rincian:</summary>''',
    564: r'''\t\t<p>Pertama, ingat bahwa''',
    566: r'''\t\tDengan menggunakan sifat bilinear operator kovarians, kita memperoleh''',
    567: r'''\t\t\[ \var[S(\bs{X}), \bs{Y})] = \frac{1}{4 n^2 (n - 1)^2} \sum_{i=1}^n \sum_{j=1}^n \sum_{k=1}^n \sum_{l=1}^n \cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] \]''',
    568: r'''\t\tKita menghitung kovarians dalam jumlah ini dengan mempertimbangkan kasus-kasus saling lepas:</p>''',
    570: r'''\t\t\t<li>\(\cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] = 0\) jika \(i = j\) atau \(k = l\), dan terdapat \(2 n^3 - n^2\) suku demikian.</li>''',
    571: r'''\t\t\t<li>\(\cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] = 0\) jika \(i, j, k, l\) semuanya berbeda, dan terdapat \(n (n - 1)(n - 2)(n - 3)\) suku demikian.</li>''',
    572: r'''\t\t\t<li>\(\cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] = 2 \, \delta_2 + 2 \sigma^2 \tau^2\) jika \(i \ne j\) dan \(\{k, l\} = \{i, j\}\), dan terdapat \(2 n (n - 1)\) suku demikian.</li>''',
    573: r'''\t\t\t<li>\(\cov[(X_i - X_j)(Y_i - Y_j), (X_k - X_l)(Y_k - Y_l)] = \delta_2 - \delta^2\) jika \(i \ne j\), \(k \ne l\), dan \(\#(\{i, j\} \cap \{k, l\}) = 1\), dan terdapat \(4 n (n - 1)(n - 2)\) suku demikian.</li>''',
    575: r'''\t\t<p>Substitusi dan penyederhanaan memberikan hasil tersebut.</p>''',
    579: r'''<p>Tidaklah mengejutkan bahwa varians kovarians sampel standar (ketika kita tidak mengetahui rata-rata distribusi) lebih besar daripada varians kovarians sampel khusus (ketika kita mengetahui rata-rata distribusi).</p>''',
    584: r'''\t\t<summary>Rincian:</summary>''',
    585: r'''\t\t<p>Dari hasil-hasil di atas dan sedikit aljabar sederhana,''',
    587: r'''\t\tNamun, perhatikan bahwa selisih tersebut menuju 0 ketika \(n \to \infty\).</p>''',
    592: r'''\t<p class="math">\(\var[S(\bs{X}, \bs{Y})] \to 0\) ketika \(n \to \infty\), sehingga kovarians sampel merupakan penaksir <dfn>konsisten</dfn> bagi kovarians distribusi.</p>''',
    595: r'''<h4 id="prbreg">Regresi</h4>''',
    597: r'''<p>Dalam pembahasan pertama di <a href="#des" class="ref"></a>, kita mempelajari regresi dari sudut pandang deterministik dan deskriptif. Hasil yang diperoleh hanya berlaku bagi sampel. Pertanyaan yang secara statistik lebih menarik dan lebih mendalam muncul ketika data berasal dari eksperimen acak dan kita mencoba menarik inferensi tentang distribusi yang mendasarinya dari regresi sampel. Ada dua model yang lazim muncul. Salah satunya adalah model dengan variabel respons acak, tetapi variabel prediktor deterministik. Model lainnya, yang kita bahas di sini, memiliki variabel prediktor dan variabel respons yang keduanya acak, sehingga data membentuk sampel acak dari distribusi bivariat.</p>''',
    599: r'''<p>Dengan demikian, misalkan kembali kita memiliki vektor acak dasar \((X, Y)\) untuk suatu eksperimen. Ingat bahwa dalam bagian mengenai <a href="../expect/Covariance.html#blp">korelasi dan regresi</a> (distribusi), kita menunjukkan bahwa prediktor linear terbaik bagi \(Y\) jika \(X\) diketahui, dalam arti meminimumkan galat kuadrat rata-rata, adalah variabel acak''',
    601: r'''sehingga <dfn>garis regresi distribusi</dfn> diberikan oleh''',
    603: r'''Selain itu, nilai minimum galat kuadrat rata-ratanya adalah \(\E\{[Y - L(Y \mid X)]\} = \var(Y)[1 - \cor^2(X, Y)] = r^2 (1 - \rho^2)\).</p>''',
    606: r'''\t<figcaption>Garis regresi distribusi</figcaption>''',
    607: r'''\t<img src="LinearPredictor.png" alt="Grafik prediktor linear">''',
    610: r'''<p>Tentu saja, dalam penerapan nyata kita hampir tidak mungkin mengetahui parameter distribusi \(\mu\), \(\nu\), \(\sigma^2\), dan \(\delta\). Jika ingin menaksir garis regresi distribusi, pendekatan alami ialah mempertimbangkan sampel acak \(\left((X_1, Y_1), (X_2, Y_2), \ldots, (X_n, Y_n)\right)\) dari distribusi \((X, Y)\), lalu menghitung garis regresi sampel. Tentu saja, hasilnya persis sama dengan pembahasan <a href="#des">di atas</a>, kecuali bahwa semua besaran yang relevan kini merupakan variabel acak.</p>''',
    612: r'''<div class="unit" id="o006.random.sample.covariance.unit.sample-regression-line-definition">''',
    613: r'''\t<p class="dfn">Jika varians sampel prediktor positif, garis regresi sampel adalah''',
    615: r'''\tGalat kuadrat rata-ratanya adalah \(S^2(\bs{Y})[1 - R^2(\bs{X}, \bs{Y})]\), dan koefisien determinasinya adalah \(R^2(\bs{X}, \bs{Y})\).</p>''',
    619: r'''\t<figcaption>Garis regresi distribusi dan sampel</figcaption>''',
    620: r'''\t<img src="SampleLinearPredictor.png" alt="Garis regresi distribusi dan sampel">''',
    623: r'''<p>Fakta bahwa garis regresi sampel dan galat kuadrat rata-rata sepenuhnya analog dengan garis regresi distribusi dan galat kuadrat rata-rata merupakan hal yang elegan dan meyakinkan secara matematis. Sekali lagi, koefisien garis regresi sampel dapat dipandang sebagai penaksir bagi koefisien yang bersesuaian pada garis regresi distribusi.</p>''',
    626: r'''\t<p class="math">Dengan mengasumsikan bahwa varians distribusi prediktor positif, koefisien garis regresi sampel konvergen menuju koefisien garis regresi distribusi dengan probabilitas 1.</p>''',
    628: r'''\t\t<li>\(\frac{S(\bs{X}, \bs{Y})}{S^2(\bs{X})} \to \frac{\delta}{\sigma^2}\) ketika \(n \to \infty\)</li>''',
    629: r'''\t\t<li>\(M(\bs{Y}) - \frac{S(\bs{X}, \bs{Y})}{S^2(\bs{X})} M(\bs{X}) \to \nu - \frac{\delta}{\sigma^2} \mu\) ketika \(n \to \infty\)</li>''',
    632: r'''\t\t<summary>Rincian:</summary>''',
    633: r'''\t\t<p>Hasil ini mengikuti hukum kuat bilangan besar dan hasil-hasil sebelumnya. Dengan probabilitas 1, \(S(\bs{X}, \bs{Y}) \to \delta\) ketika \(n \to \infty\), \(S^2(\bs{X}) \to \sigma^2\) ketika \(n \to \infty\), \(M(\bs{X}) \to \mu\) ketika \(n \to \infty\), dan \(M(\bs{Y}) \to \nu\) ketika \(n \to \infty\).</p>''',
    637: r'''<p>Tentu saja, jika hubungan linear antara \(X\) dan \(Y\) tidak kuat sebagaimana diukur oleh korelasi sampel, transformasi pada salah satu atau kedua variabel mungkin membantu. Sekali lagi, beberapa transformasi yang lazim dibahas dalam <a href="#trn">subbagian di bawah</a>.</p>''',
    639: r'''<h3 id="exe">Latihan</h3>''',
    641: r'''<h4 id="exp">Sifat Dasar</h4>''',
    644: r'''\t<p class="math">Misalkan \( x \) dan \( y \) adalah variabel populasi, sedangkan \( \bs{x} \) dan \( \bs{y} \) masing-masing merupakan sampel berukuran \( n \) dari \( x \) dan \( y \). Misalkan pula \( m(\bs{x})  = 3 \), \( m(\bs{y}) = -1 \), \( s^2(\bs{x} ) = 4\), \( s^2(\bs{y}) = 9 \), dan \( s(\bs{x}, \bs{y}) = 5 \). Tentukan masing-masing nilai berikut:</p>''',
    654: r'''\t<p class="math">Misalkan \(x\) adalah suhu (dalam derajat Fahrenheit) dan \(y\) adalah hambatan (dalam ohm) untuk suatu jenis komponen elektronik setelah beroperasi selama 10 jam. Untuk sampel yang terdiri atas 30 komponen, \(m(\bs{x}) = 113\), \(s(\bs{x}) = 18\), \(m(\bs{y}) = 100\), \(s(\bs{y}) = 10\), \(r(\bs{x}, \bs{y}) = 0.6\).</p>''',
    656: r'''\t\t<li>Klasifikasikan \(x\) dan \(y\) berdasarkan jenis dan tingkat pengukurannya.</li>''',
    657: r'''\t\t<li>Tentukan kovarians sampelnya.</li>''',
    658: r'''\t\t<li>Tentukan persamaan garis regresinya.</li>''',
    660: r'''\t<p>Sekarang misalkan suhu dikonversi ke derajat Celsius (transformasinya adalah \(\frac{5}{9}(x - 32)\)).</p>''',
    662: r'''\t\t<li>Tentukan rata-rata sampelnya.</li>''',
    663: r'''\t\t<li>Tentukan simpangan baku sampelnya.</li>''',
    664: r'''\t\t<li>Tentukan kovarians dan korelasi sampelnya.</li>''',
    665: r'''\t\t<li>Tentukan persamaan garis regresinya.</li>''',
    668: r'''\t\t<summary>Rincian:</summary>''',
    670: r'''\t\t\t<li>suhu: kontinu, interval; hambatan: kontinu, rasio</li>''',
    671: r'''\t\t\t<li>Untuk bagian (d)–(e), pasangan rata-rata adalah \((45, 100)\), dan pasangan simpangan bakunya \((10, 10)\).</li>''',
    677: r'''\t<p class="math">Misalkan \(x\) adalah panjang dan \(y\) adalah lebar (dalam inci) daun dari suatu jenis tumbuhan. Untuk sampel yang terdiri atas 50 daun, \(m(\bs{x}) = 10\), \(s(\bs{x}) = 2\), \(m(\bs{y}) = 4\), \(s(\bs{y}) = 1\), dan \(r(\bs{x}, \bs{y}) = 0.8\). </p>''',
    679: r'''\t\t<li>Klasifikasikan \(x\) dan \(y\) berdasarkan jenis dan tingkat pengukurannya.</li>''',
    680: r'''\t\t<li>Tentukan kovarians sampelnya.</li>''',
    681: r'''\t\t<li>Tentukan persamaan garis regresi dengan \(x\) sebagai variabel prediktor dan \(y\) sebagai variabel respons.</li>''',
    683: r'''\t<p>Sekarang misalkan \(x\) dan \(y\) dikonversi ke sentimeter (2,54 sentimeter per inci).</p>''',
    685: r'''\t\t<li>Tentukan rata-rata sampelnya.</li>''',
    686: r'''\t\t<li>Tentukan simpangan baku sampelnya.</li>''',
    687: r'''\t\t<li>Tentukan kovarians dan korelasi sampelnya.</li>''',
    688: r'''\t\t<li>Tentukan persamaan garis regresinya.</li>''',
    691: r'''\t\t<summary>Rincian:</summary>''',
    693: r'''\t\t\t<li>kontinu, rasio</li>''',
    694: r'''\t\t\t<li>Untuk bagian (d)–(e), pasangan rata-rata adalah \((25.4, 10.16)\), dan pasangan simpangan bakunya \((5.08, 2.54)\).</li>''',
    699: r'''<h4 id="spe">Latihan Diagram Pencar</h4>''',
    702: r'''\t<p class="app">Klik di berbagai tempat pada <a href="JavaScript:openAncillary('../apps/Scatterplot.html')" class="ancillary">diagram pencar interaktif</a>, lalu amati perubahan rata-rata, simpangan baku, korelasi, dan garis regresinya.</p>''',
    706: r'''\t<p class="app">Klik pada <a href="JavaScript:openAncillary('../apps/Scatterplot.html')" class="ancillary">diagram pencar interaktif</a> untuk menentukan 20 titik, lalu cobalah sedekat mungkin dengan masing-masing korelasi sampel berikut:</p>''',
    719: r'''\t<p class="app">Klik pada <a href="JavaScript:openAncillary('../apps/Scatterplot.html')" class="ancillary">diagram pencar interaktif</a> untuk menentukan 20 titik. Cobalah menghasilkan diagram pencar dengan garis regresi yang memiliki</p>''',
    721: r'''\t\t<li>kemiringan 1, intersep 1</li>''',
    722: r'''\t\t<li>kemiringan 3, intersep 0</li>''',
    723: r'''\t\t<li>kemiringan \(-2\), intersep 1</li>''',
    727: r'''<h4 id="sim">Latihan Simulasi</h4>''',
    730: r'''\t<p class="app">Jalankan <a href="JavaScript:openAncillary('../apps/BivariateUniform.html')" class="ancillary">eksperimen seragam bivariat</a> sebanyak 2.000 kali untuk masing-masing kasus berikut. Bandingkan rata-rata sampel dengan rata-rata distribusi, simpangan baku sampel dengan simpangan baku distribusi, korelasi sampel dengan korelasi distribusi, dan garis regresi sampel dengan garis regresi distribusi.</p>''',
    732: r'''\t\t<li>Distribusi seragam pada persegi.</li>''',
    733: r'''\t\t<li>Distribusi seragam pada segitiga.</li>''',
    734: r'''\t\t<li>Distribusi seragam pada lingkaran.</li>''',
    739: r'''\t<p class="app">Jalankan <a href="JavaScript:openAncillary('../apps/BivariateNormal.html')" class="ancillary">eksperimen normal bivariat</a> sebanyak 2.000 kali untuk berbagai nilai simpangan baku dan korelasi distribusi. Bandingkan rata-rata sampel dengan rata-rata distribusi, simpangan baku sampel dengan simpangan baku distribusi, korelasi sampel dengan korelasi distribusi, dan garis regresi sampel dengan garis regresi distribusi.</p>''',
    742: r'''<h4 id="trn">Transformasi</h4>''',
    745: r'''\t<p class="math">Perhatikan fungsi \(y = a + b x^2\).</p>''',
    747: r'''\t\t<li>Gambarkan sketsa grafiknya untuk beberapa nilai \(a\) dan \(b\) yang representatif.</li>''',
    748: r'''\t\t<li>Perhatikan bahwa \(y\) merupakan fungsi linear dari \(x^2\), dengan intersep \(a\) dan kemiringan \(b\). </li>''',
    749: r'''\t\t<li>Oleh karena itu, untuk menyesuaikan kurva ini dengan data sampel, cukup terapkan prosedur regresi standar pada data dari variabel \(x^2\) dan \(y\).</li>''',
    754: r'''\t<p class="math">Perhatikan fungsi \(y = \frac{1}{a + b x}\) pada domain tempat penyebut tidak nol.</p>''',
    756: r'''\t\t<li>Gambarkan sketsa grafiknya untuk beberapa nilai \(a\) dan \(b\) yang representatif.</li>''',
    757: r'''\t\t<li>Perhatikan bahwa \(\frac{1}{y}\) merupakan fungsi linear dari \(x\), dengan intersep \(a\) dan kemiringan \(b\).</li>''',
    758: r'''\t\t<li>Oleh karena itu, untuk menyesuaikan kurva ini dengan data sampel kita, cukup terapkan prosedur regresi standar pada data dari variabel \(x\) dan \(\frac{1}{y}\).</li>''',
    763: r'''\t<p class="math">Perhatikan fungsi \(y = \frac{x}{a + b x}\) pada domain tempat prediktor dan penyebut tidak nol.</p>''',
    765: r'''\t\t<li>Gambarkan sketsa grafiknya untuk beberapa nilai \(a\) dan \(b\) yang representatif.</li>''',
    766: r'''\t\t<li>Perhatikan bahwa \(\frac{1}{y}\) merupakan fungsi linear dari \(\frac{1}{x}\), dengan intersep \(b\) dan kemiringan \(a\).</li> ''',
    767: r'''\t\t<li>Oleh karena itu, untuk menyesuaikan kurva ini dengan data sampel, cukup terapkan prosedur regresi standar pada data dari variabel \(\frac{1}{x}\) dan \(\frac{1}{y}\).</li>''',
    768: r'''\t\t<li>Perhatikan kembali bahwa penamaan intersep dan kemiringan terbalik dibandingkan dengan rumus standar.</li>''',
    773: r'''\t<p class="math">Perhatikan fungsi \(y = a e^{b x}\) dengan parameter skala positif.</p>''',
    775: r'''\t\t<li>Gambarkan sketsa grafiknya untuk beberapa nilai \(a\) dan \(b\) yang representatif.</li>''',
    776: r'''\t\t<li>Perhatikan bahwa \(\ln(y)\) merupakan fungsi linear dari \(x\), dengan intersep \(\ln(a)\) dan kemiringan \(b\).</li>''',
    777: r'''\t\t<li>Oleh karena itu, untuk menyesuaikan kurva ini dengan data sampel, cukup terapkan prosedur regresi standar pada data dari variabel \(x\) dan \(\ln(y)\).</li> ''',
    778: r'''\t\t<li>Setelah menyelesaikan persamaan untuk intersep \(\ln(a)\), peroleh kembali statistik \(a = e^{\ln(a)}\).</li>''',
    783: r'''\t<p class="math">Perhatikan fungsi \(y = a x^b\) dengan parameter skala dan nilai prediktor positif.</p>''',
    785: r'''\t\t<li>Gambarkan sketsa grafiknya untuk beberapa nilai \(a\) dan \(b\) yang representatif.</li>''',
    786: r'''\t\t<li>Perhatikan bahwa \(\ln(y)\) merupakan fungsi linear dari \(\ln(x)\), dengan intersep \(\ln(a)\) dan kemiringan \(b\).</li> ''',
    787: r'''\t\t<li>Oleh karena itu, untuk menyesuaikan kurva ini dengan data sampel, cukup terapkan prosedur regresi standar pada data dari variabel \(\ln(x)\) dan \(\ln(y)\).</li>''',
    788: r'''\t\t<li>Setelah menyelesaikan persamaan untuk intersep \(\ln(a)\), peroleh kembali statistik \(a = e^{\ln(a)}\).</li>''',
    792: r'''<h4 id="cmp">Latihan Komputasi</h4>''',
    794: r'''<p>Semua paket perangkat lunak statistika dapat melakukan analisis regresi. Selain garis regresi, sebagian besar paket biasanya melaporkan koefisien determinasi \(r^2(\bs{x}, \bs{y})\), jumlah kuadrat \(\sst(\bs{y})\), \(\ssr(\bs{x}, \bs{y})\), \(\sse(\bs{x}, \bs{y})\), dan galat baku taksiran \(\se(\bs{x}, \bs{y})\). Sebagian besar paket juga dapat menggambar diagram pencar dengan garis regresi yang ditumpangkan, serta berbagai grafik residu yang dibahas di atas. Banyak paket juga menyediakan cara mudah untuk mentransformasi data. Ketika variabel respons ditransformasi, prosedur tersebut meminimumkan galat kuadrat pada skala hasil transformasi, bukan pada skala respons asli. Karena itu, hampir tidak ada alasan untuk melakukan perhitungan dengan tangan, kecuali pada himpunan data kecil untuk menguasai definisi dan rumus. Dalam soal berikut, lakukan perhitungan dan gambarkan grafik dengan bantuan teknologi seminimal mungkin.</p>''',
    797: r'''\t<p class="math">Misalkan \(x\) adalah jumlah mata kuliah matematika yang telah diselesaikan dan \(y\) adalah jumlah mata kuliah sains yang telah diselesaikan oleh seorang mahasiswa di Enormous State University (ESU). Sampel yang terdiri atas 10 mahasiswa ESU memberikan data berikut: \(\left((1, 1), (3, 3), (6, 4), (2, 1), (8, 5), (2, 2), (4, 3), (6, 4), (4, 3), (4, 4)\right)\).</p>''',
    799: r'''\t\t<li>Klasifikasikan \(x\) dan \(y\) berdasarkan jenis dan tingkat pengukurannya.</li>''',
    800: r'''\t\t<li>Gambarkan sketsa diagram pencarnya.</li>''',
    802: r'''\t<p>Susun tabel dengan baris-baris yang bersesuaian dengan kasus dan kolom-kolom yang bersesuaian dengan \(i\), \(x_i\), \(y_i\),  \(x_i - m(\bs{x})\), \(y_i - m(\bs{y})\), \([x_i - m(\bs{x})]^2\), \([y_i - m(\bs{y})]^2\), \([x_i - m(\bs{x})][y_i - m(\bs{y})]\), \(\hat{y}_i\), \(\hat{y}_i - m(\bs{y})\), \([\hat{y}_i - m(\bs{y})]^2\), \(y_i - \hat{y}_i\), dan \((y_i - \hat{y}_i)^2\). Tambahkan baris di bagian bawah untuk jumlah dan rata-rata. Gunakan aritmetika eksak.</p>''',
    804: r'''\t\t<li>Lengkapi delapan kolom pertama.</li>''',
    805: r'''\t\t<li>Tentukan korelasi sampel dan koefisien determinasinya.</li>''',
    806: r'''\t\t<li>Tentukan persamaan regresi sampelnya.</li>''',
    807: r'''\t\t<li>Lengkapi tabel tersebut.</li>''',
    808: r'''\t\t<li>Verifikasi identitas-identitas untuk jumlah kuadrat.</li>''',
    811: r'''\t\t<summary>Rincian:</summary>''',
    984: r'''\t\t\t\t\t<th>Jumlah</th>''',
    999: r'''\t\t\t\t\t<th>Rata-rata</th>''',
    1004: r'''\t\t\t\t\t<td>\(21/5\)</td>''',
    1005: r'''\t\t\t\t\t<td>\(8/5\)</td>''',
    1006: r'''\t\t\t\t\t<td>\(12/5\)</td>''',
    1009: r'''\t\t\t\t\t<td>\(48/35\)</td>''',
    1011: r'''\t\t\t\t\t<td>\(8/35\)</td>''',
    1016: r'''\t\t\t<li>diskret, rasio</li>''',
    1024: r'''<p>Dua latihan berikut akan membantu Anda meninjau kembali beberapa topik probabilitas pada bagian ini.</p>''',
    1027: r'''\t<p class="math">Misalkan \((X, Y)\) memiliki distribusi kontinu dengan fungsi kerapatan probabilitas \(f(x, y) = 15 x^2 y\) untuk \(0 \le x \le y \le 1\). Tentukan masing-masing nilai berikut:</p>''',
    1029: r'''\t\t<li>\(\mu = \E(X)\) dan \(\nu = \E(Y)\)</li>''',
    1030: r'''\t\t<li>\(\sigma^2 = \var(X)\) dan \(\tau^2 = \var(Y)\)</li>''',
    1031: r'''\t\t<li>\(\sigma_3 = \E\left[(X - \mu)^3\right]\) dan \(\tau_3 = \E\left[(Y - \nu)^3\right]\)</li>''',
    1032: r'''\t\t<li>\(\sigma_4 = \E\left[(X - \mu)^4\right]\) dan \(\tau_4 = \E\left[(Y - \nu)^4\right]\)</li>''',
    1033: r'''\t\t<li>\(\delta = \cov(X, Y)\), \(\rho = \cor(X, Y)\), dan \(\delta_2 = \E\left[(X - \mu)^2 (Y - \nu)^2\right]\)</li>''',
    1034: r'''\t\t<li>\(L(Y \mid X)\) dan \(L(X \mid Y)\)</li>''',
    1037: r'''\t\t<summary>Rincian:</summary>''',
    1050: r'''\t<p class="math">Sekarang misalkan \(\left((X_1, Y_1), (X_2, Y_2), \ldots, (X_9, Y_9)\right)\) adalah sampel acak berukuran \(9\) dari distribusi pada latihan sebelumnya. Tentukan masing-masing nilai berikut:</p>''',
    1052: r'''\t\t<li>\(\E[M(\bs{X})]\) dan \(\var[M(\bs{X})]\)</li>''',
    1053: r'''\t\t<li>\(\E[M(\bs{Y})]\) dan \(\var[M(\bs{Y})]\)</li>''',
    1054: r'''\t\t<li>\(\cov[M(\bs{X}), M(\bs{Y})]\) dan \(\cor[M(\bs{X}), M(\bs{Y})]\)</li>''',
    1055: r'''\t\t<li>\(\E[W^2(\bs{X})]\) dan \(\var[W^2(\bs{X})]\)</li>''',
    1056: r'''\t\t<li>\(\E[W^2(\bs{Y})]\) dan \(\var[W^2(\bs{Y})]\)</li>''',
    1057: r'''\t\t<li>\(\E[S^2(\bs{X})]\) dan \(\var[S^2(\bs{X})]\)</li>''',
    1058: r'''\t\t<li>\(\E[S^2(\bs{Y})]\) dan \(\var[S^2(\bs{Y})]\)</li>''',
    1059: r'''\t\t<li>\(\E[W(\bs{X}, \bs{Y})]\) dan \(\var[W(\bs{X}, \bs{Y})]\)</li>''',
    1060: r'''\t\t<li>\(\E[S(\bs{X}, \bs{Y})]\) dan \(\var[S(\bs{X}, \bs{Y})]\)</li>''',
    1063: r'''\t\t<summary>Rincian:</summary>''',
    1070: r'''\t\t\t<li>\(17/448\), \(5939/21\,676\,032\)</li>''',
    1078: r'''<h4 id="Data">Latihan Analisis Data</h4>''',
    1080: r'''<p>Gunakan perangkat lunak statistika untuk soal-soal berikut.</p>''',
    1082: r'''<div class="unit" id="o006.random.sample.covariance.unit.data-pearson-heights">''',
    1083: r'''\t<p class="stat">Perhatikan variabel-variabel tinggi badan dalam <a href="JavaScript:openAncillary('../data/Pearson.html')" class="ancillary">data tinggi badan Pearson</a>.</p>''',
    1085: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut berdasarkan jenis dan tingkat pengukurannya.</li>''',
    1086: r'''\t\t<li>Hitung koefisien korelasi dan koefisien determinasi.</li>''',
    1087: r'''\t\t<li>Hitung garis regresi kuadrat terkecil dengan tinggi badan ayah sebagai variabel prediktor dan tinggi badan anak laki-laki sebagai variabel respons.</li>''',
    1088: r'''\t\t<li>Gambarkan diagram pencar dan garis regresi pada satu grafik.</li>''',
    1089: r'''\t\t<li>Prediksikan tinggi badan seorang anak laki-laki yang ayahnya bertinggi 68 inci.</li>''',
    1090: r'''\t\t<li>Hitung garis regresi jika tinggi badan dikonversi ke sentimeter (1 inci sama dengan 2,54 sentimeter).</li>''',
    1093: r'''\t\t<summary>Rincian:</summary>''',
    1095: r'''\t\t\t<li>Kontinu, rasio</li>''',
    1104: r'''<div class="unit" id="o006.random.sample.covariance.unit.data-fisher-iris">''',
    1105: r'''\t<p class="stat">Perhatikan variabel panjang daun mahkota, lebar daun mahkota, dan spesies dalam <a href="JavaScript:openAncillary('../data/Iris.html')" class="ancillary">data iris Fisher</a>.</p>''',
    1107: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut berdasarkan jenis dan tingkat pengukurannya.</li>''',
    1108: r'''\t\t<li>Hitung korelasi antara panjang dan lebar daun mahkota.</li>''',
    1109: r'''\t\t<li>Hitung korelasi antara panjang dan lebar daun mahkota untuk setiap spesies.</li>''',
    1112: r'''\t\t<summary>Rincian:</summary>''',
    1114: r'''\t\t\t<li>Spesies: diskret, nominal; panjang dan lebar daun mahkota: kontinu, rasio</li>''',
    1116: r'''\t\t\t<li>Setosa: 0.3316, Virginica: 0.3496, Versicolor: 0.6162</li>''',
    1121: r'''<div class="unit" id="o006.random.sample.covariance.unit.data-mm">''',
    1122: r'''\t<p class="stat">Perhatikan variabel jumlah permen dan berat bersih dalam <a href="JavaScript:openAncillary('../data/MM.html')" class="ancillary">data M&amp;M</a>.</p>''',
    1125: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut berdasarkan jenis dan tingkat pengukurannya.</li>''',
    1126: r'''\t\t<li>Hitung koefisien korelasi dan koefisien determinasi.</li>''',
    1127: r'''\t\t<li>Hitung garis regresi kuadrat terkecil dengan jumlah permen sebagai variabel prediktor dan berat bersih sebagai variabel respons.</li>''',
    1128: r'''\t\t<li>Gambarkan diagram pencar dan garis regresi pada bagian (c) dalam satu grafik.</li>''',
    1129: r'''\t\t<li>Prediksikan berat bersih sekantong M&amp;M yang berisi 56 permen.</li>''',
    1130: r'''\t\t<li>Secara naif, kita mungkin mengharapkan korelasi yang jauh lebih kuat antara jumlah permen dan berat bersih sekantong M&amp;M. Apa saja sumber variabilitas lain dalam berat bersih?</li>''',
    1133: r'''\t\t<summary>Rincian:</summary>''',
    1135: r'''\t\t\t<li>Jumlah permen: diskret, rasio; berat bersih: kontinu, rasio</li>''',
    1136: r'''\t\t\t<li>\(r \approx 0.794\), \(r^2 \approx 0.630\)</li>''',
    1137: r'''\t\t\t<li>\(y \approx 20.278 + 0.507 x\)</li>''',
    1139: r'''\t\t\t<li>Variabilitas berat masing-masing permen.</li>''',
    1145: r'''<div class="unit" id="o006.random.sample.covariance.unit.data-sat-by-state">''',
    1146: r'''\t<p class="stat">Perhatikan variabel tingkat partisipasi dan skor total SAT dalam <a href="JavaScript:openAncillary('../data/SAT.html')" class="ancillary">data SAT menurut negara bagian</a>.</p>''',
    1148: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut berdasarkan jenis dan tingkat pengukurannya.</li>''',
    1149: r'''\t\t<li>Hitung koefisien korelasi dan koefisien determinasi.</li>''',
    1150: r'''\t\t<li>Hitung garis regresi kuadrat terkecil dengan tingkat partisipasi sebagai variabel prediktor dan skor SAT sebagai variabel respons.</li>''',
    1151: r'''\t\t<li>Gambarkan diagram pencar dan garis regresi pada satu grafik.</li>''',
    1152: r'''\t\t<li>Berikan salah satu kemungkinan penjelasan untuk korelasi negatif tersebut.</li>''',
    1155: r'''\t\t<summary>Rincian:</summary>''',
    1157: r'''\t\t\t<li>Tingkat partisipasi: kontinu, rasio. Skor SAT barangkali dapat dianggap diskret ataupun kontinu, tetapi hanya berada pada tingkat pengukuran interval karena skor terkecil yang mungkin adalah 400 (masing-masing 200 pada bagian verbal dan matematika).</li>''',
    1158: r'''\t\t\t<li>\(r \approx -0.850\), \(r^2 \approx 0.722\)</li>''',
    1159: r'''\t\t\t<li>\(y \approx 1141.854 - 2.094 x\)</li>''',
    1160: r'''\t\t\t<li value="5">Negara bagian dengan tingkat partisipasi rendah mungkin merupakan negara bagian yang menjadikan SAT sebagai pilihan. Dalam hal itu, peserta tesnya adalah siswa berprestasi lebih tinggi yang berencana melanjutkan ke perguruan tinggi. Sebaliknya, negara bagian dengan tingkat partisipasi tinggi mungkin merupakan negara bagian yang mewajibkan SAT. Dalam hal itu, semua siswa mengikuti tes, termasuk siswa berprestasi lebih rendah yang tidak berencana melanjutkan ke perguruan tinggi.</li>''',
    1165: r'''<div class="unit" id="o006.random.sample.covariance.unit.data-sat-by-year">''',
    1166: r'''\t<p class="stat">Perhatikan skor SAT verbal dan matematika (untuk seluruh siswa) dalam <a href="JavaScript:openAncillary('../data/SAT.html')" class="ancillary">data SAT menurut tahun</a>.</p>''',
    1168: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut berdasarkan jenis dan tingkat pengukurannya.</li>''',
    1169: r'''\t\t<li>Hitung koefisien korelasi dan koefisien determinasi.</li>''',
    1170: r'''\t\t<li>Hitung garis regresi kuadrat terkecil dengan skor verbal sebagai variabel prediktor dan skor matematika sebagai variabel respons.</li>''',
    1171: r'''\t\t<li>Gambarkan diagram pencar dan garis regresi pada satu grafik.</li>''',
    1174: r'''\t\t<summary>Rincian:</summary>''',
    1176: r'''\t\t\t<li>Mungkin kontinu, tetapi hanya berada pada tingkat pengukuran interval karena skor terkecil yang mungkin pada setiap bagian adalah 200.</li>''',
    1177: r'''\t\t\t<li>\(r \approx 0.614\), \(r^2 \approx 0.377\)</li>''',
    1178: r'''\t\t\t<li>\(y \approx 321.503 + 0.356 \, x\)</li>''',
    1183: r'''<div class="unit" id="o006.random.sample.covariance.unit.data-challenger">''',
    1184: r'''\t<p class="stat">Perhatikan variabel suhu dan erosi dalam himpunan data pertama pada <a href="JavaScript:openAncillary('../data/Challenger.html')" class="ancillary">data Challenger</a>.</p>''',
    1186: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut berdasarkan jenis dan tingkat pengukurannya.</li>''',
    1187: r'''\t\t<li>Hitung koefisien korelasi dan koefisien determinasi.</li>''',
    1188: r'''\t\t<li>Hitung garis regresi kuadrat terkecil.</li>''',
    1189: r'''\t\t<li>Gambarkan diagram pencar dan garis regresi pada satu grafik.</li>''',
    1190: r'''\t\t<li>Prediksikan erosi cincin-O pada suhu 31&deg; F.</li>''',
    1191: r'''\t\t<li>Apakah prediksi pada bagian (e) bermakna? Jelaskan.</li>''',
    1192: r'''\t\t<li>Tentukan garis regresi jika suhu dikonversi ke derajat Celsius. Ingat bahwa konversinya adalah \(\frac{5}{9}(x - 32)\).</li>''',
    1195: r'''\t\t<summary>Rincian:</summary>''',
    1197: r'''\t\t\t<li>suhu: kontinu, interval; erosi: kontinu, rasio</li>''',
    1201: r'''\t\t\t<li>Taksiran ini bermasalah karena 31&deg; berada jauh di luar rentang data sampel.</li>''',
    1210: r'''\t\t<li class="parent"><a href="index.html">5. Sampel Acak</a></li>''',
    1211: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    1212: r'''\t\t<li class="child"><a href="Mean.html" title="Rata-Rata Sampel">2</a></li>''',
    1213: r'''\t\t<li class="child"><a href="LLN.html" title="Hukum Bilangan Besar">3</a></li>''',
    1214: r'''\t\t<li class="child"><a href="CLT.html" title="Teorema Limit Pusat">4</a></li>''',
    1215: r'''\t\t<li class="child"><a href="Variance.html" title="Varians Sampel">5</a></li>''',
    1216: r'''\t\t<li class="child"><a href="OrderStatistics.html" title="Statistik Terurut">6</a></li>''',
    1218: r'''\t\t<li class="child"><a href="Normal.html" title="Sifat Khusus Sampel Normal">8</a></li>''',
    1219: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    1220: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    1223: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    1224: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    1225: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary"> Biografi</a></li>''',
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
    "https://www.randomservices.org/random/sample/OrderStatistics.html": "OrderStatistics.html",
    "https://www.randomservices.org/random/sample/Covariance.html": "Covariance.html",
    "https://www.randomservices.org/random/sample/Normal.html": "Normal.html",
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


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    text = source_bytes.decode("utf-8")
    lines = text.splitlines(keepends=True)
    if len(lines) != 1232:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")
    unreachable = {line_number for line_number, _ in MATH_CORRECTIONS} - set(
        LINE_REPLACEMENTS
    )
    if unreachable:
        raise RuntimeError(f"protected TeX corrections lack replacement lines: {sorted(unreachable)}")
    for line_number, (expected_raw, corrected_raw) in sorted(RAW_TEX_CORRECTIONS.items()):
        original = lines[line_number - 1]
        ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
        expected = materialize_indentation(expected_raw)
        corrected = materialize_indentation(corrected_raw)
        if original.removesuffix(ending) != expected:
            raise RuntimeError(f"line {line_number}: raw TeX authority changed")
        lines[line_number - 1] = corrected + ending
    for line_number, replacement in sorted(LINE_REPLACEMENTS.items()):
        original = lines[line_number - 1]
        ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
        translated = materialize_indentation(replacement)
        lines[line_number - 1] = restore_protected_math(
            line_number, original.removesuffix(ending), translated
        ) + ending
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
