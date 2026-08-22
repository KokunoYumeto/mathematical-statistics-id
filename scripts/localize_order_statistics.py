#!/usr/bin/env python3
"""Create the bounded id-ID Order Statistics target from frozen authority bytes."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "sample" / "OrderStatistics.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "sample" / "OrderStatistics.html"
SOURCE_URL = "https://www.randomservices.org/random/sample/OrderStatistics.html"
SOURCE_SHA256 = "19ff485c600d4294e888c1b3d05ff7eb9196449f958d3325fd72b416aca56d63"

MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)

# Translation must not normalize or re-space protected TeX. Every math span in
# a replaced source line is restored byte-for-byte from authority unless its
# exact (line, one-based span) key appears here; this map is the sole authority
# for corrected TeX emitted by the generator.
MATH_CORRECTIONS = {
    (77, 1): (
        r"\[ x_{(1)} = \min\{x_1, x_2 \ldots, x_n\}, \quad x_{(n)} = \max\{x_1, x_2, \ldots, x_n\} \]",
        r"\[ x_{(1)} = \min\{x_1, x_2, \ldots, x_n\}, \quad x_{(n)} = \max\{x_1, x_2, \ldots, x_n\} \]",
    ),
    (78, 2): (
        r"\(\frac{r}{2} = \frac{1}{2}\left[x_{(n)} - x_{(1)}\right]\)",
        r"\(\frac{1}{2}\left[x_{(n)} + x_{(1)}\right]\)",
    ),
    (93, 11): (
        r"\(k \in \{1, 2, \ldots, n\}\)",
        r"\(k \in \{1, 2, \ldots, n - 1\}\)",
    ),
    (96, 1): (r"\(p \in [0, 1]\)", r"\(p \in [0, 1)\)"),
    (98, 1): (
        r"\(k = \lfloor (n - 1)p + 1 \rfloor\)",
        r"\(k = \lfloor (n - 1)p + 1 \rfloor,\quad t = [(n - 1)p + 1] - k\)",
    ),
    (98, 2): (
        r"\(t = [(n - 1)p + 1] - k\)",
        r"\(x_{[1]} = x_{(n)};\quad n = 1 \Longrightarrow x_{[p]} = x_1\ (p \in [0, 1])\)",
    ),
    (140, 6): (
        r"\(F(x) = \frac{k}{n}\)",
        r"\(j_k = \max\{i : x_{(i)} = x_{(k)}\},\ k \in \{1, 2, \ldots, n - 1\},\ x_{(k)} \lt x_{(k+1)}\)",
    ),
    (140, 7): (
        r"\(x \in [x_{(k)}, x_{(k+1)})\)",
        r"\(F(x) = 0\ (x \lt x_{(1)});\quad F(x) = j_k/n\ (x_{(k)} \le x \lt x_{(k+1)});\quad F(x) = 1\ (x \ge x_{(n)})\)",
    ),
    (150, 11): (
        r"\(\bs{y} = \bs{a} + b \bs{x}\)",
        r"\(\bs{y} = (a + b x_1, a + b x_2, \ldots, a + b x_n)\)",
    ),
    (160, 3): (
        r"\(p \in [0, 1]\)",
        r"\(p = 1,\ y_{(n)} = a + b x_{(n)}\)",
    ),
    (160, 4): (
        r"\(k \in \{1, 2, \ldots,n\}\)",
        r"\(p \in [0, 1)\)",
    ),
    (160, 5): (
        r"\(t \in [0, 1)\)",
        r"\(k \in \{1, 2, \ldots, n - 1\},\ t \in [0, 1)\)",
    ),
    (190, 2): (r"\(p \in [0, 1]\)", r"\(p = 1\)"),
    (190, 3): (
        r"\(k \in \{1, 2, \ldots, n\}\)",
        r"\(p \in [0, 1)\)",
    ),
    (190, 4): (
        r"\(t \in [0, 1)\)",
        r"\(k \in \{1, 2, \ldots, n - 1\},\ t \in [0, 1)\)",
    ),
    (215, 12): (r"\( (-\infty x] \)", r"\( (-\infty, x] \)"),
    (317, 5): (
        r"\( \left(\left(x_{(1)}, y_1\right), \left(x_{(2)}, y_2\right) \ldots, \left(x_{(n)}, y_n\right)\right) \)",
        r"\( \left(\left(x_{(1)}, y_1\right), \left(x_{(2)}, y_2\right), \ldots, \left(x_{(n)}, y_n\right)\right) \)",
    ),
    (377, 1): (r"\(y_{(1)} = 40\)", r"\(w_{(1)} = 40\)"),
    (377, 2): (
        r"\(q_1 \le 72.11\)",
        r"\(q_1(w) = 10\sqrt{52} \approx 72.11\)",
    ),
    (377, 3): (r"\(q_2 \le 80\)", r"\(q_2(w) = 80\)"),
    (377, 4): (
        r"\(q_3 \le 84.85 \)",
        r"\(q_3(w) = 10\sqrt{72} \approx 84.85\)",
    ),
    (377, 5): (r"\(y_{(25)} = 90\)", r"\(w_{(25)} = 90\)"),
    (553, 2): (r"\(n\)", r"\(n \ge 2\)"),
    (566, 2): (r"\( n \)", r"\( n \ge 2 \)"),
    (569, 1): (
        r"\( \var(R) = h^2 \frac{2 (n _ 1)}{(n + 1)^2 (n + 2)} \)",
        r"\( \var(R) = h^2 \frac{2 (n - 1)}{(n + 1)^2 (n + 2)} \)",
    ),
    (573, 9): (
        r"\( X_{(n)} - X_{(1)} = h(U_{(n)} - U_{(1)} \)",
        r"\( X_{(n)} - X_{(1)} = h(U_{(n)} - U_{(1)}) \)",
    ),
    (580, 7): (
        r"\(\left\{\bs{x} \in [a, a + h]^n: a \le x_1 \le x_2 \le \cdots \le x_n \lt a + h\right\}\)",
        r"\(\left\{\bs{x} \in [a, a + h]^n: a \le x_1 \le x_2 \le \cdots \le x_n \le a + h\right\}\)",
    ),
    (608, 2): (r"\(n\)", r"\(n \ge 2\)"),
    (622, 1): (
        r"\[ g(x_1, x_2, \ldots, x_n) = n! \lambda^n e^{-\lambda(x_1 + x_2 + \cdots + x_n)}, \quad 0 \le x_1 \le x_2 \cdots \le x_n \lt \infty \]",
        r"\[ g(x_1, x_2, \ldots, x_n) = n! \lambda^n e^{-\lambda(x_1 + x_2 + \cdots + x_n)}, \quad 0 \le x_1 \le x_2 \le \cdots \le x_n \lt \infty \]",
    ),
    (714, 3): (
        r"\(h(0) = \frac{6}{1296}, \; h(1) = \frac{70}{1296}, \; h(2) = \frac{300}{1296}, \; h(3) = \frac{300}{1296}, \; h(4) = \frac{318}{1296}, \; h(5) = \frac{302}{1296}\)",
        r"\(h(0) = \frac{6}{1296}, \; h(1) = \frac{70}{1296}, \; h(2) = \frac{200}{1296}, \; h(3) = \frac{330}{1296}, \; h(4) = \frac{388}{1296}, \; h(5) = \frac{302}{1296}\)",
    ),
    (763, 1): (r"\((10, 15, 44, 51, 69)\)", r"\((10, 16, 44, 51, 69)\)"),
    (764, 1): (
        r"\((10, 14, 15, 16, 19)\)",
        r"\((10, 14, 15, 15.75, 19)\)",
    ),
    (764, 2): (
        r"\((45, 51, 55.5, 59, 69)\)",
        r"\((45, 51, 55.5, 58.75, 69)\)",
    ),
    (892, 1): (r"\(\text{km}/\text{hr}\)", r"\(\text{km}/\text{s}\)"),
    (899, 1): (
        r"\((620, 805, 850, 895, 1071)\)",
        r"\((620, 807.5, 850, 892.5, 1070)\)",
    ),
    (900, 1): (
        r"\((299\,620, 299\,805, 299\,850, 299\,895, 300\,071)\)",
        r"\((299\,620, 299\,807.5, 299\,850, 299\,892.5, 300\,070)\)",
    ),
    (954, 1): (r"\((3, 5.5, 9, 14, 20)\)", r"\((3, 6.5, 9, 12, 20)\)"),
    (954, 2): (r"\((2, 5, 7, 9, 17)\)", r"\((2, 6, 7, 9, 17)\)"),
    (954, 3): (
        r"\((1, 4, 6.5, 10, 19)\)",
        r"\((1, 4, 6.5, 9.75, 19)\)",
    ),
    (954, 4): (r"\((0, 3.5, 6, 10.5, 13)\)", r"\((0, 4, 6, 9, 13)\)"),
    (954, 5): (
        r"\((3, 8, 13.5, 18, 26)\)",
        r"\((3, 8.25, 13.5, 18, 26)\)",
    ),
    (954, 6): (
        r"\((4, 8, 12.5, 18, 20)\)",
        r"\((4, 8, 12.5, 17.75, 20)\)",
    ),
    (1007, 1): (r"\((50, 55.5, 58, 60, 61)\)", r"\((50, 56, 58, 58, 61)\)"),
    (1008, 1): (
        r"\((46.22, 48.28, 49.07, 50.23, 52.06)\)",
        r"\((46.22, 48.2925, 49.07, 50.175, 52.06)\)",
    ),
    (1025, 1): (
        r"\((0.08, 0.13, 0.17, 0.22, 0.39)\)",
        r"\((0.08, 0.1375, 0.17, 0.22, 0.39)\)",
    ),
    (1026, 2): (
        r"\((0.08, 0. 14, 0.18, 0.23, 0.31)\)",
        r"\((0.08, 0.1425, 0.18, 0.22, 0.31)\)",
    ),
    (1026, 3): (
        r"\((0.12, 0.12, 0.215, 0.29, 0.39)\)",
        r"\((0.12, 0.1325, 0.215, 0.2825, 0.39)\)",
    ),
    (1027, 1): (
        r"\((0.08, 0.17, 0.21, 0.25, 0.31)\)",
        r"\((0.08, 0.17, 0.21, 0.245, 0.31)\)",
    ),
}


LINE_REPLACEMENTS = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Statistik Terurut</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, sampel acak, statistik terurut, kuantil, kuartil, distribusi, diagram probabilitas">''',
    47: r'''\t\t<li class="parent"><a href="index.html">5. Sampel Acak</a></li>''',
    48: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    49: r'''\t\t<li class="child"><a href="Mean.html" title="Rata-Rata Sampel">2</a></li>''',
    50: r'''\t\t<li class="child"><a href="LLN.html" title="Hukum Bilangan Besar">3</a></li>''',
    51: r'''\t\t<li class="child"><a href="CLT.html" title="Teorema Limit Pusat">4</a></li>''',
    52: r'''\t\t<li class="child"><a href="Variance.html" title="Varians Sampel">5</a></li>''',
    54: r'''\t\t<li class="child"><a href="Covariance.html" title="Korelasi dan Regresi Sampel">7</a></li>''',
    55: r'''\t\t<li class="child"><a href="Normal.html" title="Sifat Khusus Sampel Normal">8</a></li>''',
    56: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    57: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    59: r'''\t<h2 id="o006.random.sample.order-statistics.page">6. Statistik Terurut</h2>''',
    62: r'''<h3 id="o006.random.sample.order-statistics.descriptive-theory">Teori Deskriptif</h3>''',
    64: r'''<p>Ingat kembali model dasar statistika: kita memiliki populasi objek yang menjadi perhatian dan berbagai pengukuran (variabel) yang dilakukan terhadap objek-objek tersebut. Kita memilih objek dari populasi dan mencatat variabel untuk objek-objek dalam sampel; catatan ini menjadi data kita. Pembahasan pertama menggunakan sudut pandang yang murni deskriptif. Artinya, kita tidak mengasumsikan bahwa data dihasilkan oleh suatu distribusi probabilitas yang mendasarinya. Namun, seperti biasa, ingat bahwa data itu sendiri membentuk suatu distribusi probabilitas, yaitu <dfn>distribusi empiris</dfn>.</p>''',
    66: r'''<h4 id="ord">Statistik Terurut</h4>''',
    68: r'''<div class="unit" id="o006.random.sample.order-statistics.unit.order-statistic-definition">''',
    69: r'''\t<p class="dfn">Misalkan \(x\) adalah variabel bernilai riil pada suatu populasi dan \(\bs{x} = (x_1, x_2, \ldots, x_n)\) adalah nilai-nilai yang diamati dalam sampel berukuran \(n\) untuk variabel tersebut. <dfn>Statistik terurut</dfn> berperingkat \(k\) adalah nilai terkecil ke-\(k\) dalam himpunan data dan biasanya dilambangkan dengan \(x_{(k)}\). Untuk menegaskan kebergantungannya pada ukuran sampel, notasi lain yang umum ialah \(x_{n:k}\). Jadi''',
    73: r'''<p>Secara alami, variabel \(x\) yang mendasarinya sedikitnya harus berada pada tingkat pengukuran ordinal. Statistik terurut memiliki satuan fisik yang sama dengan \(x\). Salah satu langkah awal dalam <dfn>analisis data eksploratif</dfn> ialah mengurutkan data, sehingga statistik terurut muncul secara alami.</p>''',
    75: r'''<div class="unit" id="o006.random.sample.order-statistics.unit.extreme-order-statistics">''',
    76: r'''\t<p class="dfn">Secara khusus, <dfn>statistik terurut ekstrem</dfn> adalah''',
    77: r'''\t\[ x_{(1)} = \min\{x_1, x_2, \ldots, x_n\}, \quad x_{(n)} = \max\{x_1, x_2, \ldots, x_n\} \]''',
    78: r'''\t<dfn>Rentang sampel</dfn> adalah \(r = x_{(n)} - x_{(1)}\), sedangkan <dfn>nilai tengah rentang sampel</dfn> adalah \(\frac{1}{2}\left[x_{(n)} + x_{(1)}\right]\).</p>''',
    81: r'''<p>Rentang sampel dan nilai tengah rentang sampel memiliki satuan fisik yang sama dengan \(x\). Rentang mengukur penyebaran himpunan data, sedangkan nilai tengah rentang mengukur pemusatannya.</p>''',
    83: r'''<h4 id="med">Median Sampel</h4>''',
    86: r'''\t<p class="dfn">Jika \(n\) ganjil, <dfn>median sampel</dfn> adalah pengamatan tengah dalam data terurut, yaitu \(x_{(k)}\) dengan \(k = \frac{n + 1}{2}\). Jika \(n\) genap, tidak ada satu pengamatan tengah, melainkan dua. Karena itu, <dfn>interval median</dfn> adalah \(\left[x_{(k)}, x_{(k + 1)}\right]\) dengan \(k = \frac{n}{2}\). Dalam hal ini, <dfn>median sampel</dfn> didefinisikan sebagai titik tengah interval median, yaitu \(\frac{1}{2}\left[x_{(k)} + x_{(k+1)}\right]\) dengan \(k = \frac{n}{2}\).</p>''',
    89: r'''<p>Dalam arti tertentu, definisi <a href="#med1" class="ref"></a> agak arbitrer karena tidak ada alasan kuat untuk memilih satu titik dalam interval median dibandingkan titik lainnya. Untuk pembahasan lebih lanjut, lihat <a href="Variance.html#err">fungsi galat</a> pada bagian <a href="Variance.html">Varians Sampel</a>. Bagaimanapun, median sampel merupakan statistik alami yang mengukur pusat himpunan data.</p>''',
    91: r'''<h4 id="qnt">Kuantil Sampel</h4>''',
    93: r'''<p>Kita dapat memperumum median sampel di atas menjadi kuantil sampel lainnya. Misalkan \(p \in [0, 1]\). Tujuan kita ialah menemukan nilai pada posisi sebesar proporsi \(p\) sepanjang data yang telah diurutkan. Kita mendefinisikan <em>peringkat</em> nilai yang dicari sebagai \((n - 1)p + 1\). Peringkat ini merupakan fungsi linear dari \(p\): nilainya 1 ketika \(p = 0\) dan \(n\) ketika \(p = 1\). Untuk ukuran sampel sedikitnya dua dan sebelum titik ujung kanan, peringkat pada umumnya bukan bilangan bulat. Kita ambil \(k = \lfloor (n - 1)p + 1 \rfloor\), yaitu bagian bulat peringkat yang diinginkan, dan \(t = [(n - 1)p + 1] - k\), yaitu bagian pecahannya. Dengan demikian, \((n - 1)p + 1 = k + t\), dengan \(k \in \{1, 2, \ldots, n-1\}\) dan \(t \in [0, 1)\). <dfn>Interpolasi linear</dfn> kemudian menghasilkan definisi berikut:</p>''',
    95: r'''<div class="unit" id="o006.random.sample.order-statistics.unit.sample-quantile-definition">''',
    96: r'''\t<p class="dfn">Untuk ukuran sampel sedikitnya dua, <dfn>kuantil sampel</dfn> berorde \(p \in [0,1)\) adalah''',
    98: r'''\tdengan \(k = \lfloor (n - 1)p + 1 \rfloor,\quad t = [(n - 1)p + 1] - k\). Untuk titik ujung kanan dan sampel tunggal, gunakan konvensi \(x_{[1]} = x_{(n)};\quad n = 1 \Longrightarrow x_{[p]} = x_1\ (p \in [0, 1])\).</p>''',
    101: r'''<p>Kuantil sampel memiliki satuan fisik yang sama dengan variabel \(x\) yang mendasarinya. Algoritme ini benar-benar memperumum hasil median sampel dalam <a href="#med" class="ref"></a>.</p>''',
    104: r'''\t<p class="math">Kuantil sampel berorde \(p = \frac{1}{2}\) adalah median sebagaimana didefinisikan sebelumnya, baik ketika \(n\) ganjil maupun ketika \(n\) genap.</p>''',
    107: r'''<div class="unit" id="o006.random.sample.order-statistics.unit.quartiles">''',
    108: r'''\t<p class="dfn">Kuartil</p>''',
    110: r'''\t\t<li>Kuantil sampel berorde \(\frac{1}{4}\) disebut <dfn>kuartil pertama</dfn> dan sering dilambangkan dengan \(q_1\).</li>''',
    111: r'''\t\t<li>Median sampel adalah kuartil berorde \(\frac{1}{2}\) dan kadang-kadang dilambangkan dengan \(q_2\).</li>''',
    112: r'''\t\t<li>Kuantil sampel berorde \(\frac{3}{4}\) disebut <dfn>kuartil ketiga</dfn> dan sering dilambangkan dengan \(q_3\).</li>''',
    113: r'''\t\t<li><dfn>Rentang antarkuartil</dfn> didefinisikan sebagai \(\iqr = q_3 - q_1\).</li>''',
    117: r'''<p>Perhatikan bahwa \(\iqr\) merupakan statistik yang mengukur penyebaran distribusi di sekitar median, tetapi tentu saja bilangan ini memberikan informasi lebih sedikit daripada <em>interval</em> \([q_1, q_3]\).</p>''',
    119: r'''<div class="unit" id="o006.random.sample.order-statistics.unit.fences">''',
    120: r'''\t<p class="dfn">Pagar</p>''',
    122: r'''\t\t<li>Statistik \(q_1 - \frac{3}{2}\iqr\) disebut <dfn>pagar bawah</dfn>.</li>''',
    123: r'''\t\t<li>Statistik \(q_3 + \frac{3}{2}\iqr\) disebut <dfn>pagar atas</dfn>.</li>''',
    127: r'''<p>Istilah <dfn>batas bawah</dfn> dan <dfn>batas atas</dfn> kadang-kadang digunakan sebagai pengganti pagar bawah dan pagar atas. Nilai data yang berada di bawah pagar bawah atau di atas pagar atas merupakan calon <dfn>pencilan</dfn>, yaitu nilai yang tampaknya tidak mengikuti pola umum data. Pencilan dapat disebabkan oleh galat pengukuran, atau dapat pula merupakan nilai sah yang cukup ekstrem. Dalam kedua keadaan itu, pencilan biasanya patut ditelaah lebih lanjut.</p>''',
    129: r'''<p>Lima statistik \(\left(x_{(1)}, q_1, q_2, q_3, x_{(n)}\right)\) sering disebut <dfn>ringkasan lima angka</dfn>. Secara bersama-sama, statistik tersebut memberikan banyak informasi tentang pusat, penyebaran, dan kemencengan himpunan data. Kelima angka itu secara kasar membagi data menjadi empat interval yang masing-masing memuat sekitar 25% data. Secara grafis, kelima angka beserta pencilan sering ditampilkan dalam <dfn>diagram kotak</dfn>, yang juga disebut <dfn>diagram kotak-dan-kumis</dfn>. Diagram kotak memiliki sumbu yang membentang sepanjang rentang data. Sebuah garis ditarik dari nilai terkecil yang bukan pencilan (yang mungkin saja minimum \(x_{(1)}\)) hingga nilai terbesar yang bukan pencilan (yang mungkin saja maksimum \(x_{(n)}\)). Tanda vertikal, atau <q>kumis</q>, diletakkan pada kedua ujung garis tersebut. Kotak persegi panjang membentang dari kuartil pertama \(q_1\) hingga kuartil ketiga \(q_3\), dengan garis tambahan pada median \(q_2\). Pencilan ditandai sebagai titik di luar kumis ekstrem. Semua paket statistika dapat menghitung kuartil dan sebagian besar dapat menggambar diagram kotak. Gambar di bawah menunjukkan diagram kotak dengan tiga pencilan.</p>''',
    132: r'''\t<figcaption>Diagram kotak</figcaption>''',
    133: r'''\t<img src="BoxPlot.png" alt="Diagram kotak dengan tiga pencilan">''',
    136: r'''<h4 id="alt">Definisi Alternatif</h4>''',
    138: r'''<p>Algoritme di atas bukan satu-satunya cara yang masuk akal untuk mendefinisikan kuantil sampel; banyak alternatif lain tersedia. Salah satu cara alami ialah terlebih dahulu menghitung <a href="Mean.html#cdf">fungsi distribusi empiris</a>''',
    140: r'''Ingat bahwa \(F\) memiliki sifat matematis sebuah <a href="../dist/CDF.html">fungsi distribusi</a> dan memang \(F\) merupakan fungsi distribusi bagi distribusi empiris data. Distribusi ini menempatkan probabilitas \(\frac{1}{n}\) pada setiap nilai data \(x_i\) (jadi, jika semua nilai data berbeda, distribusi ini adalah <a href="../dist/Discrete.html#uni">distribusi seragam diskret</a> pada \(\{x_1, x_2, \ldots, x_n\}\)). Untuk menangani nilai yang sama dengan tepat, tetapkan \(j_k=\max\{i:x_{(i)}=x_{(k)}\},\ k\in\{1,2,\ldots,n-1\},\ x_{(k)}\lt x_{(k+1)}\). Maka \(F(x)=0\ (x\lt x_{(1)});\quad F(x)=j_k/n\ (x_{(k)}\le x\lt x_{(k+1)});\quad F(x)=1\ (x\ge x_{(n)})\). Kita kemudian dapat mendefinisikan <a href="../dist/CDF.html#qnt" class="man">fungsi kuantil</a> sebagai invers fungsi distribusi, sebagaimana biasanya untuk distribusi probabilitas:''',
    142: r'''Dengan definisi ini, mudah dilihat bahwa kuantil berorde \(p \in (0, 1)\) adalah \(x_{(k)}\), dengan \(k = \lceil np \rceil\).</p>''',
    144: r'''<p>Cara lain ialah menghitung peringkat kuantil berorde \(p \in (0, 1)\) sebagai \((n + 1)p\), bukan \((n - 1)p + 1\), lalu menggunakan interpolasi linear seperti di atas. Untuk memahami alasannya, misalkan variabel \(x\) yang mendasari mengambil nilai dalam interval \((a, b)\). Sebanyak \(n\) titik dalam data \(\bs{x}\) membagi interval tersebut menjadi \(n + 1\) subinterval, sehingga masuk akal memandang \(x_{(k)}\) sebagai kuantil berorde \(\frac{k}{n + 1}\). Cara ini juga menghasilkan perhitungan median baku ketika \(p = \frac{1}{2}\). Namun, cara tersebut gagal jika \(p\) begitu kecil sehingga \((n + 1)p \lt 1\), atau begitu besar sehingga \((n + 1)p > n\).</p>''',
    146: r'''<p>Definisi utama di atas merupakan definisi yang paling umum digunakan dalam perangkat lunak statistika dan lembar kerja. Selain itu, ketika ukuran sampel \(n\) besar, pilihan di antara definisi kuantil tersebut biasanya hanya menghasilkan perbedaan kecil.</p>''',
    148: r'''<h4 id="trn">Transformasi</h4>''',
    150: r'''<p>Misalkan kembali \(\bs{x} = (x_1, x_2, \ldots, x_n)\) merupakan sampel berukuran \(n\) dari variabel populasi \(x\), dan misalkan pula \(y = a + bx\) adalah variabel baru, dengan \(a \in \R\) dan \(b \in (0, \infty)\). Transformasi semacam ini disebut <dfn>transformasi lokasi-skala</dfn> dan sering bersesuaian dengan perubahan satuan. Sebagai contoh, jika \(x\) adalah panjang benda dalam inci, \(y = 2.54x\) adalah panjang benda tersebut dalam sentimeter. Jika \(x\) adalah suhu benda dalam derajat Fahrenheit, \(y = \frac{5}{9}(x - 32)\) adalah suhunya dalam derajat Celsius. Misalkan \(\bs{y} = (a + b x_1, a + b x_2, \ldots, a + b x_n)\) menyatakan sampel dari variabel \(y\).</p>''',
    153: r'''\t<p class="math">Statistik terurut dan kuantil dipertahankan oleh transformasi lokasi-skala:</p>''',
    155: r'''\t\t<li>\(y_{(i)} = a + b x_{(i)}\) untuk \(i \in \{1, 2, \ldots, n\}\)</li>''',
    156: r'''\t\t<li>\(y_{[p]} = a + b x_{[p]}\) untuk \(p \in [0, 1]\)</li>''',
    159: r'''\t\t<summary>Rincian:</summary>''',
    160: r'''\t\t<p>Bagian (a) langsung mengikuti fakta bahwa transformasi lokasi-skala meningkat ketat sehingga mempertahankan urutan: \(x_i \lt x_j\) jika dan hanya jika \(a + b x_i \lt a + b x_j\). Untuk sampel dengan satu pengamatan, hasilnya langsung dari hubungan transformasi pada pengamatan tersebut. Selanjutnya, anggap ukuran sampel sedikitnya dua. Kasus titik ujung \(p = 1,\ y_{(n)} = a + b x_{(n)}\) berlaku langsung. Untuk \(p \in [0, 1)\), ambil \(k \in \{1, 2, \ldots, n - 1\},\ t \in [0, 1)\) seperti dalam definisi kuantil sampel berorde \(p\). Maka''',
    165: r'''<p>Seperti simpangan baku, yaitu ukuran penyebaran terpenting kita, rentang dan rentang antarkuartil tidak dipengaruhi oleh parameter lokasi, tetapi dikalikan dengan parameter skala.</p>''',
    168: r'''\t<p class="math">Rentang dan rentang antarkuartil dari \(\bs{y}\) adalah</p>''',
    174: r'''\t\t<summary>Rincian:</summary>''',
    175: r'''\t\t<p>Hasil ini langsung mengikuti <a href="#trn1" class="ref"></a>.</p>''',
    179: r'''<p>Secara lebih umum, misalkan \(y = g(x)\), dengan \(g\) fungsi bernilai riil yang meningkat ketat pada himpunan nilai yang mungkin bagi \(x\). Misalkan \(\bs{y} = \left(g(x_1), g(x_2), \ldots, g(x_n)\right)\) adalah sampel yang bersesuaian dengan variabel \(y\). Seperti dalam pembuktian Teorema 2, statistik terurut dipertahankan sehingga \(y_{(i)} = g(x_{(i)})\). Namun, jika \(g\) nonlinear, kuantil tidak dipertahankan karena kuantil menggunakan interpolasi <em>linear</em>. Artinya, \(y_{[p]}\) dan \(g(x_{[p]})\) pada umumnya berbeda. Jika \(g\) <a href="../expect/Properties2.html#jen">konveks</a> atau konkaf, setidaknya kita dapat memberikan suatu pertidaksamaan bagi kuantil sampel.</p>''',
    182: r'''\t<p class="math">Misalkan \(y = g(x)\), dengan \(g\) meningkat ketat. Maka</p>''',
    184: r'''\t\t<li>\(y_{(i)} = g\left(x_{(i)}\right)\) untuk \(i \in \{1, 2, \ldots, n\}\)</li>''',
    185: r'''\t\t<li>Jika \(g\) konveks, maka \(y_{[p]} \ge g\left(x_{[p]}\right)\) untuk \(p \in [0, 1]\)</li>''',
    186: r'''\t\t<li>Jika \(g\) konkaf, maka \(y_{[p]} \le g\left(x_{[p]}\right)\) untuk \(p \in [0, 1]\)</li>''',
    189: r'''\t\t<summary>Rincian:</summary>''',
    190: r'''\t\t<p>Seperti telah dicatat, bagian (a) mengikuti fakta bahwa \(g\) meningkat ketat sehingga mempertahankan urutan. Jika sampel hanya memuat satu pengamatan, semua kuantil sama dengan pengamatan itu sehingga kedua pertidaksamaan berlaku sebagai kesamaan. Selanjutnya, anggap ukuran sampel sedikitnya dua. Bagian (b) mengikuti definisi kekonveksan. Kasus titik ujung \(p = 1\) berlaku sebagai kesamaan. Untuk \(p \in [0, 1)\), ambil \(k \in \{1, 2, \ldots, n - 1\},\ t \in [0, 1)\) seperti dalam definisi kuantil sampel berorde \(p\); kita memperoleh''',
    192: r'''\t\tBagian (c) mengikuti argumen yang sama; kedua pertidaksamaan pada titik ujung kanan berlaku langsung karena kuantil titik ujung adalah pengamatan terbesar.</p>''',
    196: r'''<h4 id="sal">Diagram Batang-Daun</h4>''',
    198: r'''<p><dfn>Diagram batang-daun</dfn> merupakan tampilan grafis statistik terurut \(\left(x_{(1)}, x_{(2)}, \ldots, x_{(n)}\right)\). Diagram ini menyajikan data secara grafis seperti histogram, sekaligus mempertahankan data yang telah diurutkan. Pertama, kita mengasumsikan format angka yang tetap: sejumlah digit yang tetap, mungkin diikuti tanda desimal dan sejumlah digit tetap lainnya. Diagram batang-daun dibuat dengan menggunakan bagian awal untaian tersebut sebagai <dfn>batang</dfn> dan bagian sisanya sebagai daun. Karena terdapat banyak variasi, alih-alih memberikan definisi lengkap yang rumit, kita akan melihat beberapa contoh dalam latihan di bawah.</p>''',
    200: r'''<h3 id="prb">Teori Probabilitas</h3>''',
    202: r'''<p>Kita melanjutkan pembahasan statistik terurut, tetapi kini variabel-variabelnya diasumsikan sebagai variabel acak. Misalkan terdapat <a href="../prob/Experiments.html">percobaan acak</a> dasar dan \(X\) merupakan <a href="../prob/Probability.html">variabel acak</a> bernilai riil dengan <a href="../dist/CDF.html">fungsi distribusi</a> \(F\). Kita melakukan \(n\) pengulangan saling bebas dari percobaan dasar tersebut untuk menghasilkan sampel acak \(\bs{X} = (X_1, X_2, \ldots, X_n)\) berukuran \(n\) dari distribusi \(X\). Ini adalah barisan variabel acak yang <a href="../prob/Independence.html">saling bebas</a>, masing-masing dengan distribusi \(X\). Semua statistik pada bagian sebelumnya masih bermakna, tetapi sekarang merupakan variabel acak. Kita menggunakan notasi sebelumnya dengan konvensi bahwa variabel acak ditulis memakai huruf kapital. Jadi, untuk \(k \in \{1,2,\ldots,n\}\), \(X_{(k)}\) adalah <dfn>statistik terurut ke-\(k\)</dfn>, yaitu nilai terkecil ke-\(k\) di antara \((X_1,X_2,\ldots,X_n)\). Sekarang kita menelaah distribusi statistik terurut dan statistik yang diturunkan darinya.</p>''',
    204: r'''<h4 id="dst">Distribusi Statistik Terurut ke-\(k\)</h4>''',
    206: r'''<p>Menentukan fungsi distribusi statistik terurut merupakan penerapan yang baik dari <a href="../bernoulli/index.html">percobaan Bernoulli</a> dan <a href="../bernoulli/Binomial.html">distribusi binomial</a>.</p>''',
    209: r'''\t<p class="math">Fungsi distribusi \(F_k\) dari \(X_{(k)}\) diberikan oleh''',
    212: r'''\t\t<summary>Rincian:</summary>''',
    213: r'''\t\t<p>Untuk \(x \in \R\), misalkan''',
    215: r'''\t\tsehingga \(N_x\) adalah banyaknya variabel sampel yang jatuh dalam interval \((-\infty,x]\). Variabel indikator dalam jumlah tersebut saling bebas dan masing-masing bernilai 1 dengan probabilitas \(F(x)\). Jadi, \(N_x\) berdistribusi binomial dengan parameter \(n\) dan \(F(x)\). Selanjutnya, \(X_{(k)} \le x\) jika dan hanya jika \(N_x \ge k\), untuk \(x \in \R\) dan \(k \in \{1,2,\ldots,n\}\), sebab kedua kejadian itu sama-sama menyatakan bahwa sedikitnya \(k\) variabel sampel berada dalam interval \((-\infty,x]\). Karena itu''',
    220: r'''<p>Seperti biasa, statistik terurut ekstrem sangat menarik.</p>''',
    223: r'''\t<p class="math"><a href="../dist/CDF.html">Fungsi distribusi</a> \(F_1\) dari \(X_{(1)}\) dan \(F_n\) dari \(X_{(n)}\) diberikan oleh</p>''',
    225: r'''\t\t<li>\(F_1(x) = 1 - \left[1 - F(x)\right]^n\) untuk \(x \in \R\)</li>''',
    226: r'''\t\t<li>\(F_n(x) = \left[F(x)\right]^n\) untuk \(x \in \R\)</li>''',
    231: r'''\t<p class="math"><a href="../dist/CDF.html#qnt">Fungsi kuantil</a> \(F_1^{-1}\) dan \(F_n^{-1}\) dari \(X_{(1)}\) dan \(X_{(n)}\) diberikan oleh</p>''',
    233: r'''\t\t<li>\(F_1^{-1}(p) = F^{-1}\left[1 - (1 - p)^{1/n}\right]\) untuk \(p \in (0, 1)\)</li>''',
    234: r'''\t\t<li>\(F_n^{-1}(p) = F^{-1}\left(p^{1/n}\right)\) untuk \(p \in (0, 1)\)</li>''',
    237: r'''\t\t<summary>Rincian:</summary>''',
    238: r'''\t\t<p>Rumus-rumus tersebut mengikuti <a href="#dst2" class="ref"></a> dan aljabar sederhana. Ingat bahwa jika \(G\) adalah fungsi distribusi, fungsi kuantil yang bersesuaian diberikan oleh \(G^{-1}(p) = \min\{x \in \R: G(x) \ge p\}\) untuk \(p \in (0,1)\).</p>''',
    242: r'''<p>Jika distribusi yang mendasarinya kontinu, kita dapat memberikan rumus sederhana bagi fungsi kepadatan probabilitas statistik terurut.</p>''',
    245: r'''\t<p class="math">Misalkan sekarang \(X\) memiliki <a href="../dist/Continuous.html">distribusi kontinu</a> dengan fungsi kepadatan probabilitas \(f\). Maka \(X_{(k)}\) memiliki distribusi kontinu dengan fungsi kepadatan probabilitas \(f_k\) yang diberikan oleh''',
    248: r'''\t\t<summary>Rincian:</summary>''',
    249: r'''\t\t<p>Tentu saja, \(f_k(x) = F_k^\prime(x)\). Kita mengambil turunan suku demi suku dan menggunakan aturan hasil kali pada''',
    251: r'''\t\tKita menggunakan identitas binomial \(j \binom{n}{j} = n \binom{n - 1}{j - 1}\) dan \((n - j)\binom{n}{j} = n\binom{n - 1}{j}\). Hasil akhirnya ialah''',
    254: r'''\t\tKedua jumlah saling meniadakan, menyisakan hanya suku \(j=k\) pada jumlah pertama. Karena itu''',
    256: r'''\t\tNamun, \(n \binom{n-1}{k-1} = \frac{n!}{(k-1)!(n-k)!}\).</p>''',
    257: r'''\t\t<p>Terdapat pula argumen heuristik sederhana untuk hasil ini. Pertama, \(f_k(x)\,dx\) adalah probabilitas bahwa \(X_{(k)}\) berada dalam interval infinitesimal selebar \(dx\) di sekitar \(x\). Kejadian tersebut berarti bahwa satu variabel sampel berada dalam interval infinitesimal itu, \(k-1\) variabel sampel kurang dari \(x\), dan \(n-k\) variabel sampel lebih dari \(x\). Banyaknya cara memilih variabel-variabel tersebut adalah koefisien multinomial''',
    259: r'''\t\tKarena saling bebas, probabilitas bahwa variabel-variabel terpilih berada dalam interval yang ditentukan adalah''',
    264: r'''<p>Berikut adalah kasus khusus untuk statistik terurut ekstrem.</p>''',
    267: r'''\t<p class="math">Fungsi kepadatan probabilitas \(f_1\) dari \(X_{(1)}\) dan \(f_n\) dari \(X_{(n)}\) diberikan oleh</p>''',
    269: r'''\t\t<li>\(f_1(x) = n \left[1 - F(x)\right]^{n-1}f(x)\) untuk \(x \in \R\)</li>''',
    270: r'''\t\t<li>\(f_n(x) = n \left[F(x)\right]^{n-1}f(x)\) untuk \(x \in \R\)</li>''',
    274: r'''<h4 id="jnt">Distribusi Bersama</h4>''',
    276: r'''<p>Kita kembali mengasumsikan bahwa \(X\) memiliki distribusi kontinu dengan fungsi distribusi \(F\) dan fungsi kepadatan probabilitas \(f\).</p>''',
    279: r'''\t<p class="math">Misalkan \(j,k \in \{1,2,\ldots,n\}\) dengan \(j \lt k\). Fungsi kepadatan probabilitas bersama \(f_{j,k}\) dari \(\left(X_{(j)},X_{(k)}\right)\) diberikan oleh</p>''',
    282: r'''\t\t<summary>Rincian:</summary>''',
    283: r'''\t\t<p>Kita ingin menghitung probabilitas bahwa \(X_{(j)}\) berada dalam interval infinitesimal \(dx\) di sekitar \(x\), dan \(X_{(k)}\) berada dalam interval infinitesimal \(dy\) di sekitar \(y\). Harus ada \(j-1\) variabel sampel yang kurang dari \(x\), satu variabel dalam interval infinitesimal di sekitar \(x\), \(k-j-1\) variabel sampel di antara \(x\) dan \(y\), satu variabel dalam interval infinitesimal di sekitar \(y\), serta \(n-k\) variabel sampel yang lebih dari \(y\). Banyaknya cara memilih variabel-variabel itu adalah koefisien multinomial''',
    285: r'''\t\tKarena saling bebas, probabilitas bahwa variabel-variabel terpilih berada dalam interval yang ditentukan adalah''',
    290: r'''<p>Dari distribusi bersama dua statistik terurut, setidaknya secara prinsip, kita dapat menentukan distribusi berbagai statistik lain: rentang sampel \(R\); kuantil sampel \(X_{[p]}\) untuk \(p \in [0,1]\), khususnya kuartil sampel \(Q_1\), \(Q_2\), \(Q_3\); serta rentang antarkuartil IQR. Distribusi bersama statistik terurut ekstrem \((X_{(1)},X_{(n)})\) merupakan kasus yang sangat penting.</p>''',
    293: r'''\t<p class="math">Untuk ukuran sampel sedikitnya dua, fungsi kepadatan probabilitas bersama \(f_{1,n}\) dari \(\left(X_{(1)},X_{(n)}\right)\) diberikan oleh''',
    296: r'''\t\t<summary>Rincian:</summary>''',
    297: r'''\t\t<p>Ini merupakan akibat <a href="#jnt1" class="ref"></a> dengan \(j=1\) dan \(k=n\).</p>''',
    301: r'''<p>Argumen serupa dapat digunakan untuk memperoleh fungsi kepadatan probabilitas bersama untuk sembarang banyak statistik terurut. Tentu saja, kita terutama tertarik pada fungsi kepadatan probabilitas bersama dari <em>semua</em> statistik terurut. Ternyata fungsi kepadatan tersebut memiliki bentuk yang sangat sederhana.</p>''',
    304: r'''\t<p class="math">\(\left(X_{(1)}, X_{(2)}, \ldots, X_{(n)}\right)\) memiliki fungsi kepadatan probabilitas bersama \(g\) yang diberikan oleh''',
    307: r'''\t\t<summary>Rincian:</summary>''',
    308: r'''\t\t<p>Untuk setiap permutasi \(\bs{i}=(i_1,i_2,\ldots,i_n)\) dari \((1,2,\ldots,n)\), misalkan \(S_\bs{i} = \{\bs{x} \in \R^n: x_{i_1} \lt x_{i_2} \lt \cdots \lt x_{i_n}\}\). Pada \(S_\bs{i}\), pemetaan \((x_1,x_2,\ldots,x_n) \mapsto (x_{i_1},x_{i_2},\ldots,x_{i_n})\) bersifat satu-ke-satu, memiliki turunan parsial pertama yang kontinu, dan memiliki Jacobian 1. Himpunan-himpunan \(S_\bs{i}\), ketika \(\bs{i}\) merentang seluruh \(n!\) permutasi \((1,2,\ldots,n)\), saling lepas. Probabilitas bahwa \((X_1,X_2,\ldots,X_n)\) tidak berada dalam salah satu himpunan tersebut adalah 0. Hasilnya kini mengikuti rumus <a href="../dist/Transformations.html#cov">perubahan variabel</a> multivariat.</p>''',
    309: r'''\t\t<p>Sekali lagi, terdapat argumen heuristik sederhana. Untuk setiap \(\bs{x} \in \R^n\) dengan \(x_1 \lt x_2 \lt \cdots \lt x_n\), ada \(n!\) permutasi koordinat \(\bs{x}\). Kepadatan probabilitas \((X_1,X_2,\ldots,X_n)\) pada setiap titik itu ialah \(f(x_1)f(x_2)\cdots f(x_n)\). Jadi, kepadatan probabilitas \((X_{(1)},X_{(2)},\ldots,X_{(n)})\) pada \(\bs{x}\) adalah \(n!\) kali hasil kali tersebut.</p>''',
    313: r'''<h4 id="plt">Plot Probabilitas</h4>''',
    315: r'''<p><dfn>Plot probabilitas</dfn>, yang juga disebut <dfn>plot kuantil-kuantil</dfn> atau singkatnya <dfn>plot Q-Q</dfn>, merupakan uji grafis informal untuk menentukan apakah data yang diamati berasal dari distribusi tertentu. Misalkan kita mengamati data bernilai riil \((x_1,x_2,\ldots,x_n)\) dari <a href="../sample/Introduction.html">sampel acak</a> berukuran \(n\). Kita ingin mengetahui apakah data tersebut secara masuk akal dapat berasal dari <a href="../dist/Continuous.html">distribusi kontinu</a> dengan <a href="../dist/CDF.html">fungsi distribusi</a> \(F\). Pertama, kita mengurutkan data dari yang terkecil hingga terbesar, sehingga diperoleh nilai-nilai statistik terurut yang diamati: \(\left(x_{(1)},x_{(2)},\ldots,x_{(n)}\right)\).</p>''',
    317: r'''<p>Dengan konvensi posisi plot alternatif yang diperkenalkan di atas, kita memandang \(x_{(i)}\) sebagai kuantil <em>sampel</em> berorde \(\frac{i}{n+1}\); ini bukan aturan interpolasi kuantil utama pada halaman ini. Menurut definisi, kuantil <em>distribusi</em> berorde \(\frac{i}{n+1}\) adalah \(y_i = F^{-1}\left(\frac{i}{n+1}\right)\). Jika data benar-benar berasal dari distribusi tersebut, kita mengharapkan titik-titik \(\left(\left(x_{(1)},y_1\right),\left(x_{(2)},y_2\right),\ldots,\left(x_{(n)},y_n\right)\right)\) berada dekat garis diagonal \(y=x\). Sebaliknya, penyimpangan kuat dari garis ini merupakan indikasi kuat bahwa data tidak berasal dari distribusi tersebut. Plot titik-titik itu disebut <dfn>plot probabilitas</dfn>.</p>''',
    319: r'''<p>Namun, biasanya kita tidak sedang menguji apakah data berasal dari satu distribusi <em>tertentu</em>, melainkan dari suatu <em>keluarga</em> distribusi parametrik, misalnya keluarga normal, seragam, atau eksponensial. Keadaan ini lazim karena parameternya tidak diketahui; langkah berikutnya setelah plot probabilitas mungkin justru menaksir parameter tersebut. Untungnya, metode plot probabilitas memiliki perluasan sederhana untuk setiap keluarga distribusi <a href="../special/LocationScale.html">lokasi-skala</a>. Misalkan \(G\) adalah fungsi distribusi tertentu. Keluarga lokasi-skala yang terkait dengan \(G\) memiliki fungsi distribusi \(F(x)=G\left(\frac{x-a}{b}\right)\), untuk \(x \in \R\), dengan \(a \in \R\) sebagai parameter lokasi dan \(b \in (0,\infty)\) sebagai parameter skala. Untuk \(p \in (0,1)\), jika \(z_p=G^{-1}(p)\) menyatakan kuantil berorde \(p\) bagi \(G\), dan \(y_p=F^{-1}(p)\) kuantil berorde \(p\) bagi \(F\), maka \(y_p=a+bz_p\). Jadi, jika plot probabilitas berdasarkan \(F\) hampir linear, khususnya dekat garis diagonal, plot probabilitas berdasarkan \(G\) juga hampir linear. Dengan demikian, kita dapat menggunakan \(G\) tanpa mengetahui parameter lokasi dan skala.</p>''',
    321: r'''<p>Dalam latihan di bawah, Anda akan menjelajahi plot probabilitas untuk distribusi <a href="../special/Normal.html">normal</a>, <a href="../poisson/Exponential.html">eksponensial</a>, dan <a href="../dist/Continuous.html#uni">seragam</a>. Prosedur kuantitatif formal, yaitu <a href="../hypothesis/ChiSquare.html#fit">uji kecocokan khi-kuadrat</a>, akan dipelajari dalam bab <a href="../hypothesis/index.html">pengujian hipotesis</a>.</p>''',
    323: r'''<h3 id="o006.random.sample.order-statistics.exercises-applications">Latihan dan Penerapan</h3>''',
    325: r'''<h4 id="prp">Sifat Dasar</h4>''',
    328: r'''\t<p class="math">Misalkan \(x\) adalah suhu (dalam derajat Fahrenheit) untuk suatu jenis komponen elektronik setelah beroperasi selama 10 jam. Sampel 30 komponen memiliki ringkasan lima angka \((84,102,113,120,135)\).</p>''',
    330: r'''\t\t<li>Klasifikasikan \(x\) menurut jenis dan tingkat pengukurannya.</li>''',
    331: r'''\t\t<li>Tentukan rentang dan rentang antarkuartil.</li>''',
    332: r'''\t\t<li>Tentukan ringkasan lima angka, rentang, dan rentang antarkuartil jika suhu dikonversi ke derajat Celsius. Transformasinya adalah \(y = \frac{5}{9}(x - 32)\).</li>''',
    335: r'''\t\t<summary>Rincian:</summary>''',
    337: r'''\t\t\t<li>kontinu, interval</li>''',
    345: r'''\t<p class="math">Misalkan \(x\) adalah panjang (dalam inci) komponen hasil pemesinan dalam suatu proses manufaktur. Sampel 50 komponen memiliki ringkasan lima angka (9.6, 9.8, 10.0, 10.1, 10.3).</p>''',
    347: r'''\t\t<li>Klasifikasikan \(x\) menurut jenis dan tingkat pengukurannya.</li>''',
    348: r'''\t\t<li>Tentukan rentang dan rentang antarkuartil.</li>''',
    349: r'''\t\t<li>Tentukan ringkasan lima angka, rentang, dan rentang antarkuartil jika panjang diukur dalam sentimeter. Transformasinya adalah \(y = 2.54x\).</li>''',
    352: r'''\t\t<summary>Rincian:</summary>''',
    354: r'''\t\t\t<li>kontinu, rasio</li>''',
    357: r'''\t\t\t<li></li>''',
    363: r'''\t<p class="math">Profesor Moriarity mengajar satu kelas Statistika 101 yang terdiri atas 25 mahasiswa di Enormous State University (ESU). Pada ujian tengah semester pertama, ringkasan lima angkanya adalah (16, 52, 64, 72, 81) dari maksimum 100 poin. Profesor Moriarity menilai hasil tersebut agak rendah dan mempertimbangkan beberapa transformasi untuk menaikkan nilai.</p>''',
    365: r'''\t\t<li>Tentukan rentang dan rentang antarkuartil.</li>''',
    366: r'''\t\t<li>Misalkan ia menambahkan 10 poin pada setiap nilai. Tentukan ringkasan lima angka, rentang, dan rentang antarkuartil nilai hasil transformasi.</li>''',
    367: r'''\t\t<li>Misalkan ia mengalikan setiap nilai dengan 1.2. Tentukan ringkasan lima angka, rentang, dan rentang antarkuartil nilai hasil transformasi.</li>''',
    368: r'''\t\t<li>Misalkan ia menggunakan transformasi \(w=10\sqrt{x}\), yang sangat melengkungkan skala di ujung bawah, tetapi hanya sedikit di ujung atas. Berikan semua informasi yang dapat ditentukan tentang ringkasan lima angka nilai hasil transformasi.</li>''',
    369: r'''\t\t<li>Tentukan apakah nilai rendah 16 merupakan pencilan.</li>''',
    372: r'''\t<summary>Rincian:</summary>''',
    377: r'''\t\t<li>\(w_{(1)}=40\), \(q_1(w)=10\sqrt{52}\approx72.11\), \(q_2(w)=80\), \(q_3(w)=10\sqrt{72}\approx84.85\), \(w_{(25)}=90\)</li>''',
    378: r'''\t\t<li>Pagar bawahnya adalah 22, sehingga 16 memang merupakan pencilan.</li>''',
    383: r'''<h4 id="cmp">Latihan Komputasi</h4>''',
    385: r'''<p>Semua paket perangkat lunak statistika dapat menghitung statistik terurut dan kuantil, menggambar diagram batang-daun dan diagram kotak, serta pada umumnya menjalankan prosedur numerik dan grafis yang dibahas dalam bagian ini. Untuk kajian statistika nyata, khususnya yang menggunakan himpunan data besar, perangkat lunak statistika sangat penting. Namun, mengerjakan perhitungan secara manual pada himpunan data kecil buatan tetap berguna untuk menguasai konsep dan definisi. Dalam subbagian ini, lakukan perhitungan dan gambarlah grafik dengan bantuan teknologi seminimal mungkin.</p>''',
    388: r'''\t<p class="math">Misalkan \(x\) adalah banyaknya mata kuliah matematika yang telah diselesaikan seorang mahasiswa ESU. Sampel 10 mahasiswa ESU memberikan data \(\bs{x}=(3,1,2,0,2,4,3,2,1,2)\).</p>''',
    391: r'''\t\t<li>Klasifikasikan \(x\) menurut jenis dan tingkat pengukurannya.</li>''',
    392: r'''\t\t<li>Berikan statistik terurutnya.</li>''',
    393: r'''\t\t<li>Hitung ringkasan lima angka dan gambar diagram kotaknya.</li>''',
    394: r'''\t\t<li>Hitung rentang dan rentang antarkuartil.</li>''',
    397: r'''\t<summary>Rincian:</summary>''',
    399: r'''\t\t<li>diskret, rasio</li>''',
    408: r'''\t<p class="math">Misalkan sampel berukuran 12 dari variabel diskret \(x\) memiliki fungsi massa empiris \(f(-2)=1/12\), \(f(-1)=1/4\), \(f(0)=1/3\), \(f(1)=1/6\), dan \(f(2)=1/6\).</p>''',
    410: r'''\t\t<li>Berikan statistik terurutnya.</li>''',
    411: r'''\t\t<li>Hitung ringkasan lima angka dan gambar diagram kotaknya.</li>''',
    412: r'''\t\t<li>Hitung rentang dan rentang antarkuartil.</li>''',
    415: r'''\t\t<summary>Rincian:</summary>''',
    425: r'''\t<p class="math">Diagram batang-daun di bawah menyajikan nilai ujian 100 poin dalam mata kuliah probabilitas yang diikuti 38 mahasiswa. Digit pertama adalah batang dan digit kedua adalah daun. Jadi, nilai terendah adalah 47 dan tertinggi 98. Nilai pada baris dengan batang 6 adalah 60, 60, 62, 63, 65, 65, 67, dan 68.</p>''',
    484: r'''\t<p>Hitung ringkasan lima angka dan gambar diagram kotaknya.</p>''',
    486: r'''\t\t<summary>Rincian:</summary>''',
    491: r'''<h4 id="app">Latihan Aplikasi</h4>''',
    494: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/Histogram.html')" class="ancillary">aplikasi histogram</a>, buat satu distribusi terpisah yang memuat sedikitnya 30 nilai untuk setiap jenis di bawah. Catat ringkasan lima angkanya.</p>''',
    496: r'''\t\t<li>Distribusi seragam.</li>''',
    497: r'''\t\t<li>Distribusi simetris unimodal.</li>''',
    498: r'''\t\t<li>Distribusi unimodal yang menceng ke kanan.</li>''',
    499: r'''\t\t<li>Distribusi unimodal yang menceng ke kiri.</li>''',
    500: r'''\t\t<li>Distribusi simetris bimodal.</li>''',
    501: r'''\t\t<li>Distribusi berbentuk \(u\).</li>''',
    506: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ErrorFunction.html')" class="ancillary">aplikasi fungsi galat</a>, mulailah dengan suatu distribusi lalu tambahkan titik-titik berikut. Catat pengaruhnya terhadap ringkasan lima angka:</p>''',
    508: r'''\t\t<li>Tambahkan satu titik di bawah \(x_{(1)}\).</li>''',
    509: r'''\t\t<li>Tambahkan satu titik di antara \(x_{(1)}\) dan \(q_1\).</li>''',
    510: r'''\t\t<li>Tambahkan satu titik di antara \(q_1\) dan \(q_2\).</li>''',
    511: r'''\t\t<li>Tambahkan satu titik di antara \(q_2\) dan \(q_3\).</li>''',
    512: r'''\t\t<li>Tambahkan satu titik di antara \(q_3\) dan \(x_{(n)}\).</li>''',
    513: r'''\t\t<li>Tambahkan satu titik di atas \(x_{(n)}\).</li>''',
    517: r'''<p>Dalam <a href="#app2" class="ref"></a>, Anda mungkin memperhatikan bahwa ketika satu titik ditambahkan ke distribusi, satu atau beberapa dari kelima statistik tidak berubah. Secara umum, kuantil relatif tidak peka terhadap perubahan data.</p>''',
    519: r'''<h4 id="uni">Distribusi Seragam</h4>''',
    521: r'''<p>Ingat bahwa <a href="../dist/Continuous.html#uni">distribusi seragam baku</a> adalah distribusi seragam pada interval \([0,1]\).</p>''',
    524: r'''\t<p class="math">Misalkan \(\bs{X}\) adalah sampel acak berukuran \(n\) dari distribusi seragam baku. Untuk \(k \in \{1,2,\ldots,n\}\), \(X_{(k)}\) memiliki <a href="../special/Beta.html">distribusi beta</a> dengan parameter kiri \(k\) dan parameter kanan \(n-k+1\). Fungsi kepadatan probabilitas \(f_k\) diberikan oleh''',
    527: r'''\t\t<summary>Rincian:</summary>''',
    528: r'''\t\t<p>Hasil ini langsung mengikuti <a href="#dst4" class="ref"></a> karena \(f(x)=1\) dan \(F(x)=x\) untuk \(0 \le x \le 1\). Dari bentuk \(f_k\), distribusinya dapat dikenali sebagai distribusi beta dengan parameter kiri \(k\) dan parameter kanan \(n-k+1\).</p>''',
    533: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/OrderStatistic.html')" class="ancillary">eksperimen statistik terurut</a>, pilih distribusi seragam baku dan \(n=5\). Ubah \(k\) dari 1 hingga 5 dan perhatikan bentuk fungsi kepadatan probabilitas \(X_{(k)}\). Untuk setiap nilai \(k\), jalankan simulasi 1.000 kali dan bandingkan fungsi kepadatan empiris dengan fungsi kepadatan probabilitas teoretis.</p>''',
    536: r'''<p>Hasil untuk distribusi seragam baku mudah diperluas ke distribusi seragam umum pada suatu interval.</p>''',
    539: r'''\t<p class="math">Misalkan \(\bs{X}\) adalah sampel acak berukuran \(n\) dari distribusi seragam pada interval \([a,a+h]\), dengan \(a \in \R\) dan \(h \in (0,\infty)\). Untuk \(k \in \{1,2,\ldots,n\}\), \(X_{(k)}\) memiliki distribusi beta dengan parameter kiri \(k\), parameter kanan \(n-k+1\), parameter lokasi \(a\), dan parameter skala \(h\). Secara khusus,</p>''',
    545: r'''\t\t<summary>Rincian:</summary>''',
    546: r'''\t\t<p>Misalkan \(\bs{U}=(U_1,U_2,\ldots,U_n)\) adalah sampel acak berukuran \(n\) dari distribusi seragam baku, dan tetapkan \(X_i=a+hU_i\) untuk \(i \in \{1,2,\ldots,n\}\). Maka \(\bs{X}=(X_1,X_2,\ldots,X_n)\) adalah sampel acak berukuran \(n\) dari distribusi seragam pada \([a,a+h]\), dan \(X_{(k)}=a+hU_{(k)}\). Jadi, distribusi \(X_{(k)}\) mengikuti hasil sebelumnya. Bagian (a) dan (b) mengikuti hasil baku untuk distribusi beta.</p>''',
    550: r'''<p>Kita kembali ke distribusi seragam baku dan meninjau rentang sampel acak.</p>''',
    553: r'''\t<p class="math">Misalkan \(\bs{X}\) adalah sampel acak berukuran \(n \ge 2\) dari distribusi seragam baku. Rentang sampel \(R\) memiliki distribusi beta dengan parameter kiri \(n-1\) dan parameter kanan 2. Fungsi kepadatan probabilitas \(g\) diberikan oleh''',
    556: r'''\t\t<summary>Rincian:</summary>''',
    557: r'''\t\t<p>Dari <a href="#jnt2" class="ref"></a>, fungsi kepadatan probabilitas bersama \((X_{(1)},X_{(n)})\) adalah \(f_{1,n}(x,y)=n(n-1)(y-x)^{n-2}\) untuk \(0 \le x \le y \le 1\). Karena itu, untuk \(r \in [0,1]\),''',
    559: r'''\t\tDengan demikian, fungsi distribusi \(R\) adalah \(G(r)=nr^{n-1}-(n-1)r^n\) untuk \(0 \le r \le 1\). Mengambil turunan terhadap \(r\) dan menyederhanakannya memberikan fungsi kepadatan \(g(r)=n(n-1)r^{n-2}(1-r)\) untuk \(0 \le r \le 1\). Dari bentuk \(g\), distribusi ini adalah distribusi beta dengan parameter kiri \(n-1\) dan parameter kanan 2.</p>''',
    563: r'''<p>Sekali lagi, hasil ini mudah diperluas ke distribusi seragam umum.</p>''',
    566: r'''\t<p class="math">Misalkan \( \bs{X} = (X_1, X_2, \ldots, X_n) \) adalah sampel acak berukuran \( n \ge 2 \) dari distribusi seragam pada \( [a, a + h] \), dengan \( a \in \R \) dan \( h \in (0, \infty) \). Rentang sampel \( R = X_{(n)} - X_{(1)} \) memiliki distribusi beta dengan parameter kiri \( n - 1 \), parameter kanan \( 2 \), dan parameter skala \( h \). Secara khusus,</p>''',
    569: r'''\t\t<li>\(\var(R) = h^2 \frac{2(n - 1)}{(n + 1)^2 (n + 2)}\)</li>''',
    572: r'''\t\t<summary>Rincian:</summary>''',
    573: r'''\t\t<p>Misalkan kembali \(\bs{U}=(U_1,U_2,\ldots,U_n)\) adalah sampel acak berukuran \(n\) dari distribusi seragam baku, dan tetapkan \(X_i=a+hU_i\) untuk \(i \in \{1,2,\ldots,n\}\). Maka \(\bs{X}=(X_1,X_2,\ldots,X_n)\) adalah sampel acak berukuran \(n\) dari distribusi seragam pada \([a,a+h]\), dan \(X_{(k)}=a+hU_{(k)}\). Karena itu, \(X_{(n)}-X_{(1)}=h(U_{(n)}-U_{(1)})\), sehingga distribusi \(R\) mengikuti hasil sebelumnya. Bagian (a) dan (b) mengikuti hasil baku untuk distribusi beta.</p>''',
    577: r'''<p>Distribusi bersama statistik terurut untuk sampel dari distribusi seragam mudah diperoleh.</p>''',
    580: r'''\t<p class="math">Misalkan \((X_1,X_2,\ldots,X_n)\) adalah sampel acak berukuran \(n\) dari distribusi seragam pada interval \([a,a+h]\), dengan \(a \in \R\) dan \(h \in (0,\infty)\). Maka \(\left(X_{(1)},X_{(2)},\ldots,X_{(n)}\right)\) berdistribusi seragam pada \(\left\{\bs{x} \in [a,a+h]^n: a \le x_1 \le x_2 \le \cdots \le x_n \le a+h\right\}\).</p>''',
    582: r'''\t\t<summary>Rincian:</summary>''',
    583: r'''\t\t<p>Hasil ini langsung mengikuti fakta bahwa \((X_1,X_2,\ldots,X_n)\) berdistribusi seragam pada \([a,a+h]^n\). Dari <a href="#jnt3" class="ref"></a>, fungsi kepadatan probabilitas bersama statistik terurut adalah \(g(x_1,x_2,\ldots,x_n)=n!/h^n\) untuk \((x_1,x_2,\ldots,x_n) \in [a,a+h]^n\) dengan \(a \le x_1 \le x_2 \le \cdots \le x_n \le a+h\).</p>''',
    587: r'''<h4 id="exp">Distribusi Eksponensial</h4>''',
    589: r'''<p>Ingat bahwa <a href="../poisson/Exponential.html">distribusi eksponensial</a> dengan parameter laju \(\lambda \gt 0\) memiliki fungsi kepadatan probabilitas''',
    591: r'''Distribusi eksponensial banyak digunakan untuk memodelkan waktu kegagalan dan waktu acak lainnya dalam kondisi ideal tertentu. Secara khusus, waktu antarkedatangan dalam <a href="../poisson/index.html">proses Poisson</a> berdistribusi eksponensial.</p>''',
    594: r'''\t<p class="math">Misalkan \(\bs{X}\) adalah sampel acak berukuran \(n\) dari distribusi eksponensial dengan parameter laju \(\lambda\). Fungsi kepadatan probabilitas dari statistik terurut ke-\(k\), \(X_{(k)}\), adalah''',
    596: r'''\tSecara khusus, minimum \(X_{(1)}\) juga memiliki distribusi eksponensial, tetapi dengan parameter laju \(n\lambda\).</p>''',
    598: r'''\t\t<summary>Rincian:</summary>''',
    599: r'''\t\t<p>Fungsi kepadatan probabilitas dari \(X_{(k)}\) mengikuti <a href="#dst4" class="ref"></a> karena \(F(x)=1-e^{-\lambda x}\) untuk \(0 \le x \lt \infty\). Dengan menetapkan \(k=1\), diperoleh \(f_1(x)=n\lambda e^{-n\lambda x}\) untuk \(0 \le x \lt \infty\).</p>''',
    604: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/OrderStatistic.html')" class="ancillary">eksperimen statistik terurut</a>, pilih distribusi eksponensial baku dan \(n=5\). Ubah \(k\) dari 1 hingga 5 dan perhatikan bentuk fungsi kepadatan probabilitas \(X_{(k)}\). Untuk setiap nilai \(k\), jalankan simulasi 1.000 kali dan bandingkan fungsi kepadatan empiris dengan fungsi kepadatan probabilitas teoretis.</p>''',
    608: r'''\t<p class="math">Misalkan kembali \(\bs{X}\) adalah sampel acak berukuran \(n \ge 2\) dari distribusi eksponensial dengan parameter laju \(\lambda\). Rentang sampel \(R\) memiliki distribusi yang sama dengan maksimum sampel acak berukuran \(n-1\) dari distribusi eksponensial. Fungsi kepadatan probabilitasnya adalah''',
    609: r'''\t\[ h(t) = (n - 1) \lambda (1 - e^{-\lambda t})^{n - 2} e^{-\lambda t}, \quad 0 \le t \lt \infty \]''',
    611: r'''\t\t<summary>Rincian:</summary>''',
    612: r'''\t\t<p>Menurut <a href="#jnt2" class="ref"></a>, \((X_{(1)},X_{(n)})\) memiliki fungsi kepadatan probabilitas bersama \(f_{1,n}(x,y)=n(n-1)\lambda^2(e^{-\lambda x}-e^{-\lambda y})^{n-2}e^{-\lambda x}e^{-\lambda y}\) untuk \(0 \le x \le y \lt \infty\). Karena itu, untuk \(0 \le t \lt \infty\),''',
    614: r'''\t\tDengan menyubstitusikan \(u=e^{-\lambda y}\), \(du=-\lambda e^{-\lambda y}\,dy\), ke dalam integral bagian dalam lalu menghitungnya, diperoleh''',
    616: r'''\t\tMenurunkannya terhadap \(t\) memberikan fungsi kepadatan probabilitas. Dengan membandingkannya dengan <a href="#exp1" class="ref"></a>, terlihat bahwa ini adalah fungsi kepadatan probabilitas dari maksimum suatu sampel berukuran \(n-1\) dari distribusi eksponensial.</p>''',
    621: r'''\t<p class="math">Misalkan kembali \(\bs{X}\) adalah sampel acak berukuran \(n\) dari distribusi eksponensial dengan parameter laju \(\lambda\). Fungsi kepadatan probabilitas bersama statistik terurut \((X_{(1)},X_{(2)},\ldots,X_{(n)})\) adalah''',
    622: r'''\t\[ g(x_1, x_2, \ldots, x_n) = n! \lambda^n e^{-\lambda(x_1 + x_2 + \cdots + x_n)}, \quad 0 \le x_1 \le x_2 \le \cdots \le x_n \lt \infty \]</p>''',
    624: r'''\t\t<summary>Rincian:</summary>''',
    625: r'''\t\t<p>Hasil ini mengikuti <a href="#jnt3" class="ref"></a> dan aljabar sederhana.</p>''',
    629: r'''<h4 id="dce">Dadu</h4>''',
    632: r'''\t<p class="math">Empat dadu seimbang dilempar. Tentukan fungsi massa probabilitas setiap statistik terurut.</p>''',
    634: r'''\t\t<summary>Rincian:</summary>''',
    686: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/Dice.html')" class="ancillary">eksperimen dadu</a>, pilih statistik terurut dan distribusi dadu yang diberikan pada bagian (a)&ndash;(d). Naikkan banyaknya dadu dari 1 hingga 20 sambil memperhatikan bentuk fungsi massa probabilitas pada setiap tahap. Kemudian, dengan \(n=4\), jalankan simulasi 1.000 kali dan bandingkan fungsi frekuensi relatif dengan fungsi massa probabilitas.</p>''',
    688: r'''\t\t<li>Skor maksimum dengan dadu seimbang.</li>''',
    689: r'''\t\t<li>Skor minimum dengan dadu seimbang.</li>''',
    690: r'''\t\t<li>Skor maksimum dengan dadu pipih satu–enam (ace–six flat).</li>''',
    691: r'''\t\t<li>Skor minimum dengan dadu pipih satu–enam (ace–six flat).</li>''',
    696: r'''\t<p class="math">Empat dadu seimbang dilempar. Tentukan fungsi massa probabilitas bersama keempat statistik terurut.</p>''',
    698: r'''\t\t<summary>Rincian:</summary>''',
    699: r'''\t\t<p>Fungsi massa probabilitas bersama \(g\) didefinisikan pada \(\{(x_1,x_2,x_3,x_4) \in \{1,2,3,4,5,6\}^4: x_1 \le x_2 \le x_3 \le x_4\}\).</p>''',
    701: r'''\t\t\t<li>\(g(x_1,x_2,x_3,x_4)=\frac{1}{1296}\) jika semua koordinat sama (terdapat 6 vektor demikian).</li>''',
    702: r'''\t\t\t<li>\(g(x_1,x_2,x_3,x_4)=\frac{4}{1296}\) jika terdapat dua koordinat berbeda, satu nilai muncul tiga kali dan nilai lainnya sekali (terdapat 30 vektor demikian).</li>''',
    703: r'''\t\t\t<li>\(g(x_1,x_2,x_3,x_4)=\frac{6}{1296}\) jika terdapat dua koordinat berbeda dalam \((x_1,x_2,x_3,x_4)\), dan masing-masing nilai muncul dua kali (terdapat 15 vektor demikian).</li>''',
    704: r'''\t\t\t<li>\(g(x_1,x_2,x_3,x_4)=\frac{12}{1296}\) jika terdapat tiga koordinat berbeda, satu nilai muncul dua kali dan nilai lainnya masing-masing sekali (terdapat 60 vektor demikian).</li>''',
    705: r'''\t\t\t<li>\(g(x_1,x_2,x_3,x_4)=\frac{24}{1296}\) jika semua koordinat berbeda (terdapat 15 vektor demikian).</li>''',
    711: r'''\t<p class="math">Empat dadu seimbang dilempar. Tentukan fungsi massa probabilitas rentang sampel.</p>''',
    713: r'''\t\t<summary>Rincian:</summary>''',
    714: r'''\t\t<p>\(R\) memiliki fungsi massa probabilitas \(h\) yang diberikan oleh \(h(0)=\frac{6}{1296}, \; h(1)=\frac{70}{1296}, \; h(2)=\frac{200}{1296}, \; h(3)=\frac{330}{1296}, \; h(4)=\frac{388}{1296}, \; h(5)=\frac{302}{1296}\).</p>''',
    718: r'''<h4 id="pps">Simulasi Plot Probabilitas</h4>''',
    721: r'''\t<p class="app">Dalam <a href="https://www.randomservices.org/random/apps/ProbabilityPlot.html" class="ancillary">eksperimen plot probabilitas</a>, atur distribusi asal sampel menjadi distribusi normal dengan rata-rata 5 dan simpangan baku 2. Atur ukuran sampel menjadi \(n = 20\). Untuk setiap distribusi uji berikut, jalankan eksperimen 50 kali dan perhatikan bentuk geometris plot probabilitas:</p>''',
    723: r'''\t\t<li>Normal baku</li>''',
    724: r'''\t\t<li>Seragam pada interval \([0, 1]\)</li>''',
    725: r'''\t\t<li>Eksponensial dengan parameter 1</li>''',
    730: r'''\t<p class="app">Dalam <a href="https://www.randomservices.org/random/apps/ProbabilityPlot.html" class="ancillary">eksperimen plot probabilitas</a>, atur distribusi asal sampel menjadi distribusi seragam pada \([4, 10]\). Atur ukuran sampel menjadi \(n = 20\). Untuk setiap distribusi uji berikut, jalankan eksperimen 50 kali dan perhatikan bentuk geometris plot probabilitas:</p>''',
    732: r'''\t\t<li>Normal baku</li>''',
    733: r'''\t\t<li>Seragam pada interval \([0, 1]\)</li>''',
    734: r'''\t\t<li>Eksponensial dengan parameter 1</li>''',
    739: r'''\t<p class="app">Dalam <a href="https://www.randomservices.org/random/apps/ProbabilityPlot.html" class="ancillary">eksperimen plot probabilitas</a>, atur distribusi asal sampel menjadi distribusi eksponensial dengan parameter 3. Atur ukuran sampel menjadi \(n = 20\). Untuk setiap distribusi uji berikut, jalankan eksperimen 50 kali dan perhatikan bentuk geometris plot probabilitas:</p>''',
    741: r'''\t\t<li>Normal baku</li>''',
    742: r'''\t\t<li>Seragam pada interval \([0, 1]\)</li>''',
    743: r'''\t\t<li>Eksponensial dengan parameter 1</li>''',
    747: r'''<h4 id="dat">Latihan Analisis Data</h4>''',
    749: r'''<p>Gunakan perangkat lunak statistika untuk soal-soal dalam subbagian ini.</p>''',
    752: r'''\t<p class="stat">Pertimbangkan variabel panjang mahkota bunga dan spesies dalam <a href="https://www.randomservices.org/random/data/Iris.html" class="ancillary">data iris Fisher</a>.</p>''',
    754: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut menurut jenis dan tingkat pengukurannya.</li>''',
    755: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotak untuk panjang mahkota bunga.</li>''',
    756: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotak untuk panjang mahkota bunga menurut spesies.</li>''',
    757: r'''\t\t<li>Gambarkan plot probabilitas normal untuk panjang mahkota bunga.</li>''',
    760: r'''\t\t<summary>Rincian:</summary>''',
    762: r'''\t\t\t<li>panjang mahkota bunga: kontinu, rasio; spesies: diskret, nominal</li>''',
    763: r'''\t\t\t<li>\((10, 16, 44, 51, 69)\)</li>''',
    764: r'''\t\t\t<li>spesies 0: \((10, 14, 15, 15.75, 19)\); spesies 1: \((45, 51, 55.5, 58.75, 69)\); spesies 2: \((30, 40, 44, 47, 56)\)</li>''',
    770: r'''\t<p class="stat">Pertimbangkan variabel erosi dalam <a href="https://www.randomservices.org/random/data/Challenger.html" class="ancillary">himpunan data Challenger</a>.</p>''',
    772: r'''\t\t<li>Klasifikasikan variabel tersebut menurut jenis dan tingkat pengukurannya.</li>''',
    773: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotaknya.</li>''',
    774: r'''\t\t<li>Tentukan semua pencilan.</li>''',
    777: r'''\t\t<summary>Rincian:</summary>''',
    779: r'''\t\t\t<li>kontinu, rasio</li>''',
    781: r'''\t\t\t<li>Semua nilai positif, yaitu 28, 40, 48, dan 53, merupakan pencilan.</li>''',
    787: r'''\t<p class="math">Diagram batang-daun untuk <a href="https://www.randomservices.org/random/data/Michelson.html" class="ancillary">data kecepatan cahaya Michelson</a> diberikan di bawah ini. Pada contoh ini, digit terakhir, yang selalu 0, dihilangkan agar lebih ringkas. Perhatikan pula bahwa setiap batang memiliki dua baris daun: baris pertama untuk daun 0 sampai 4, yakni sebenarnya 00 sampai 40, dan baris kedua untuk daun 5 sampai 9, yakni sebenarnya 50 sampai 90. Dengan demikian, nilai minimumnya adalah 620, sedangkan bilangan pada baris kedua untuk batang 7 adalah 750, 760, 760, dan seterusnya. Catatan edisi: tabel sumber menghilangkan 28 daun pada paruh atas batang 8, yaitu 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9. Untuk memeriksa data lengkap dan melakukan perhitungan, gunakan himpunan data Michelson resmi yang ditautkan pada awal paragraf ini.</p>''',
    890: r'''\t\t<li>Klasifikasikan variabel tersebut menurut jenis dan tingkat pengukurannya.</li>''',
    891: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotaknya.</li>''',
    892: r'''\t\t<li>Hitung ringkasan lima angka untuk kecepatan dalam \(\text{km}/\text{s}\). Transformasinya adalah \(y = x + 299\,000\).</li>''',
    893: r'''\t\t<li>Gambarkan plot probabilitas normalnya.</li>''',
    896: r'''\t\t<summary>Rincian:</summary>''',
    898: r'''\t\t\t<li>kontinu, interval</li>''',
    899: r'''\t\t\t<li>\((620, 807.5, 850, 892.5, 1070)\)</li>''',
    900: r'''\t\t\t<li>\((299\,620, 299\,807.5, 299\,850, 299\,892.5, 300\,070)\)</li>''',
    906: r'''\t<p class="stat">Pertimbangkan <a href="https://www.randomservices.org/random/data/Short.html" class="ancillary">data paralaks Matahari Short</a>.</p>''',
    908: r'''\t\t<li>Klasifikasikan variabel tersebut menurut jenis dan tingkat pengukurannya.</li>''',
    909: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotaknya.</li>''',
    910: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotaknya jika variabel tersebut dikonversi ke derajat. Satu derajat sama dengan 3.600 detik busur.</li>''',
    911: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotaknya jika variabel tersebut dikonversi ke radian. Satu derajat sama dengan \(\pi/180\) radian.</li>''',
    912: r'''\t\t<li>Gambarkan plot probabilitas normalnya.</li>''',
    915: r'''\t\t<summary>Rincian:</summary>''',
    917: r'''\t\t\t<li>kontinu, rasio</li>''',
    926: r'''\t<p class="stat">Pertimbangkan <a href="https://www.randomservices.org/random/data/Cavendish.html" class="ancillary">data massa jenis Bumi Cavendish</a>.</p>''',
    928: r'''\t\t<li>Klasifikasikan variabel tersebut menurut jenis dan tingkat pengukurannya.</li>''',
    929: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotaknya.</li>''',
    930: r'''\t\t<li>Gambarkan plot probabilitas normalnya.</li>''',
    933: r'''\t<summary>Rincian:</summary>''',
    935: r'''\t\t\t<li>kontinu, rasio</li>''',
    942: r'''\t<p class="stat">Pertimbangkan <a href="https://www.randomservices.org/random/data/MM.html" class="ancillary">data M&amp;M</a>.</p>''',
    944: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut menurut jenis dan tingkat pengukurannya.</li>''',
    945: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotak untuk banyaknya permen pada setiap warna.</li>''',
    946: r'''\t\t<li>Susun diagram batang-daun untuk jumlah seluruh permen.</li>''',
    947: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotak untuk jumlah seluruh permen.</li>''',
    948: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotak untuk berat bersih.</li>''',
    951: r'''\t\t<summary>Rincian:</summary>''',
    953: r'''\t\t\t<li>banyaknya permen pada setiap warna: diskret, rasio; berat bersih: kontinu, rasio</li>''',
    954: r'''\t\t\t<li>merah: \((3, 6.5, 9, 12, 20)\); hijau: \((2, 6, 7, 9, 17)\); biru: \((1, 4, 6.5, 9.75, 19)\); jingga: \((0, 4, 6, 9, 13)\); kuning: \((3, 8.25, 13.5, 18, 26)\); cokelat: \((4, 8, 12.5, 17.75, 20)\)</li>''',
    1007: r'''\t\t\t<li>\((50, 56, 58, 58, 61)\)</li>''',
    1008: r'''\t\t\t<li>\((46.22, 48.2925, 49.07, 50.175, 52.06)\)</li>''',
    1014: r'''\t<p class="stat">Pertimbangkan variabel berat tubuh, spesies, dan jenis kelamin dalam <a href="https://www.randomservices.org/random/data/Cicada.html" class="ancillary">data Cicada</a>.</p>''',
    1016: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut menurut jenis dan tingkat pengukurannya.</li>''',
    1017: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotak untuk berat tubuh.</li>''',
    1018: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotak untuk berat tubuh menurut spesies.</li>''',
    1019: r'''\t\t<li>Hitung ringkasan lima angka dan gambarkan diagram kotak untuk berat tubuh menurut jenis kelamin.</li>''',
    1022: r'''\t\t<summary>Rincian:</summary>''',
    1024: r'''\t\t\t<li>berat tubuh: kontinu, rasio; spesies: diskret, nominal; jenis kelamin: diskret, nominal</li>''',
    1025: r'''\t\t\t<li>\((0.08, 0.1375, 0.17, 0.22, 0.39)\)</li>''',
    1026: r'''\t\t\t<li>spesies 0: \((0.08, 0.13, 0.16, 0.21, 0.27)\); spesies 1: \((0.08, 0.1425, 0.18, 0.22, 0.31)\); spesies 2: \((0.12, 0.1325, 0.215, 0.2825, 0.39)\)</li>''',
    1027: r'''\t\t\t<li>betina: \((0.08, 0.17, 0.21, 0.245, 0.31)\); jantan: \((0.08, 0.12, 0.14, 0.16, 0.39)\)</li>''',
    1033: r'''\t<p class="stat">Pertimbangkan <a href="https://www.randomservices.org/random/data/Pearson.html" class="ancillary">data tinggi badan Pearson</a>.</p>''',
    1035: r'''\t\t<li>Klasifikasikan variabel-variabel tersebut menurut jenis dan tingkat pengukurannya.</li>''',
    1036: r'''\t\t<li>Hitung ringkasan lima angka dan sketsakan diagram kotak untuk tinggi badan ayah.</li>''',
    1037: r'''\t\t<li>Hitung ringkasan lima angka dan sketsakan diagram kotak untuk tinggi badan anak laki-laki.</li>''',
    1040: r'''\t\t<summary>Rincian:</summary>''',
    1042: r'''\t\t\t<li>kontinu, rasio</li>''',
    1051: r'''\t\t<li class="parent"><a href="https://www.randomservices.org/random/index.html">Random</a></li>''',
    1052: r'''\t\t<li class="parent"><a href="index.html">5. Sampel Acak</a></li>''',
    1053: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    1054: r'''\t\t<li class="child"><a href="Mean.html" title="Rata-Rata Sampel">2</a></li>''',
    1055: r'''\t\t<li class="child"><a href="LLN.html" title="Hukum Bilangan Besar">3</a></li>''',
    1056: r'''\t\t<li class="child"><a href="CLT.html" title="Teorema Limit Pusat">4</a></li>''',
    1057: r'''\t\t<li class="child"><a href="Variance.html" title="Varians Sampel">5</a></li>''',
    1059: r'''\t\t<li class="child"><a href="https://www.randomservices.org/random/sample/Covariance.html" title="Korelasi dan Regresi Sampel">7</a></li>''',
    1060: r'''\t\t<li class="child"><a href="https://www.randomservices.org/random/sample/Normal.html" title="Sifat Khusus Sampel Normal">8</a></li>''',
    1061: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    1062: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    1065: r'''\t\t<li class="sister"><a href="https://www.randomservices.org/random/apps/index.html" class="ancillary">Aplikasi</a></li>''',
    1066: r'''\t\t<li class="sister"><a href="https://www.randomservices.org/random/data/index.html" class="ancillary">Himpunan Data</a></li>''',
    1067: r'''\t\t<li class="child"><a href="https://www.randomservices.org/random/biographies/index.html" class="ancillary">Biografi</a></li>''',
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
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, serta perbaikan terverifikasi pada nomor halaman, definisi nilai tengah rentang, syarat titik ujung kuantil, notasi dan tanda kurung, daerah dukung distribusi bersama, hasil rentang dadu, satuan, rujukan dan ringkasan data, serta kesalahan ketik. Tabel batang-daun Michelson dipertahankan dengan catatan eksplisit mengenai 28 daun yang hilang dari sumber.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t</section>'''


def materialize_indentation(value: str) -> str:
    """Convert only line-leading raw ``\\t`` markers into real tab bytes."""

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
    if raw_href == "../sample/Introduction.html":
        return raw_href
    ancillary = re.fullmatch(r"JavaScript:openAncillary\('([^']+)'\)", raw_href, re.IGNORECASE)
    candidate = ancillary.group(1) if ancillary else raw_href
    absolute = urljoin(SOURCE_URL, candidate)
    base, fragment = urldefrag(absolute)
    if base == "https://www.randomservices.org/random/data/Fisher.html":
        base = "https://www.randomservices.org/random/data/Iris.html"
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
    if len(lines) != 1074:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")
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
