#!/usr/bin/env python3
"""Create the bounded id-ID Normal-model interval-estimation target."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "interval" / "Normal.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "interval" / "Normal.html"
SOURCE_URL = "https://www.randomservices.org/random/interval/Normal.html"
SOURCE_SHA256 = "21c59dd27f38c17148de5af35d53d94a01c51cd4f230c81d75e91173a9917586"
EXPECTED_SOURCE_LINES = 552


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Pendugaan pada Model Normal</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, pendugaan himpunan, pendugaan interval, distribusi normal, rata-rata, varians, pendugaan robust, tingkat kepercayaan">''',
    32: r'''\t\t<li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    33: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    35: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Pendugaan pada Model Bernoulli">3</a></li>''',
    36: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Pendugaan pada Model Normal Dua Sampel">4</a></li>''',
    37: r'''\t\t<li class="child"><a href="Bayes.html" title="Pendugaan Interval Bayes">5</a></li>''',
    38: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    39: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    41: r'''\t<h2 id="o006.random.interval.normal.page">2. Pendugaan pada Model Normal</h2>''',
    44: r'''<h3 id="the">Teori Dasar</h3>''',
    46: r'''<h4 id="mod">Model Normal</h4>''',
    48: r'''<p><a href="../special/Normal.html">Distribusi normal</a> mungkin merupakan distribusi terpenting dalam kajian statistika matematis, antara lain karena <a href="../sample/CLT.html">teorema limit pusat</a>. Sebagai akibat teorema ini, suatu besaran terukur yang dipengaruhi oleh banyak galat acak kecil akan mempunyai distribusi yang setidaknya mendekati normal. Variabel semacam itu ada di mana-mana dalam eksperimen statistika, pada bidang yang membentang dari ilmu fisika dan biologi hingga ilmu sosial.</p>''',
    50: r'''<p>Karena itu, pada bagian ini kita mengasumsikan bahwa \(\bs{X} = (X_1, X_2, \ldots, X_n)\) adalah <a href="../sample/Introduction.html">sampel acak</a> berukuran sekurang-kurangnya 2 dari <a href="../special/Normal.html">distribusi normal</a> dengan <a href="../expect/Properties.html">rata-rata</a> \(\mu\) dan <a href="../expect/Variance.html">simpangan baku</a> \(\sigma\). Tujuan kita adalah membangun <a href="Introduction.html">interval kepercayaan</a> bagi \(\mu\) dan \(\sigma\) secara terpisah, lalu secara lebih umum membangun himpunan kepercayaan bagi \((\mu, \sigma)\). Ini termasuk kasus khusus terpenting dalam pendugaan himpunan. Bagian paralel mengenai <a href="../hypothesis/Normal.html">pengujian pada model normal</a> terdapat dalam <a href="../hypothesis/index.html">Bab 8</a> tentang pengujian hipotesis. Pertama-tama kita perlu meninjau beberapa fakta dasar yang sangat penting bagi analisis kita.</p>''',
    53: r'''\t<p class="math">Ingat bahwa <a href="../sample/LLN.html">rata-rata sampel</a> \(M\) dan <a href="../sample/Variance.html">varians sampel</a> \(S^2\) adalah''',
    57: r'''<p>Dari kajian <a href="../point/index.html">pendugaan titik</a>, ingat bahwa \(M\) merupakan penduga tak bias dan konsisten bagi \(\mu\), sedangkan \(S^2\) merupakan penduga tak bias dan konsisten bagi \(\sigma^2\). Dari statistik-statistik dasar ini kita dapat membangun <a href="Introduction.html#piv">variabel pivot</a> yang akan digunakan untuk membangun dugaan interval. Ingat kembali <a href="../sample/Normal.html">sifat khusus distribusi normal</a> berikut:</p>''',
    60: r'''\t<p class="math">Definisikan''',
    63: r'''\t\t<li>\(Z\) mempunyai <a href="../special/Normal.html">distribusi normal standar</a>.</li>''',
    64: r'''\t\t<li>\(T\) mempunyai <a href="../special/Student.html">distribusi \(t\) Student</a> dengan \(n - 1\) derajat kebebasan.</li>''',
    65: r'''\t\t<li>\(V\) mempunyai <a href="../special/ChiSquare.html">distribusi khi-kuadrat</a> dengan \(n - 1\) derajat kebebasan.</li>''',
    66: r'''\t\t<li>\(Z\) dan \(V\) saling bebas.</li>''',
    70: r'''<p>Dengan demikian, masing-masing variabel acak tersebut merupakan variabel pivot bagi \((\mu, \sigma)\): distribusinya tidak bergantung pada parameter, tetapi variabelnya sendiri secara fungsional bergantung pada salah satu atau kedua parameter. Variabel pivot \(Z\) dan \(T\) akan digunakan untuk membangun dugaan interval bagi \(\mu\), sedangkan \(V\) akan digunakan untuk membangun dugaan interval bagi \(\sigma^2\). Untuk membangun dugaan tersebut, kita memerlukan <a href="../dist/CDF.html#qnt">kuantil</a> distribusi-distribusi baku ini. Kuantil dapat dihitung memakai <a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">aplikasi kuantil</a> atau sebagian besar paket perangkat lunak matematika dan statistika. Notasi yang akan kita gunakan adalah sebagai berikut:</p>''',
    73: r'''\t<p class="dfn">Misalkan \(p \in (0, 1)\) dan \(k \in \N_+\).</p>''',
    75: r'''\t\t<li>\(z(p)\) menyatakan kuantil berorde \(p\) dari distribusi normal standar.</li>''',
    76: r'''\t\t<li>\(t_k(p)\) menyatakan kuantil berorde \(p\) dari distribusi \(t\) Student dengan \(k\) derajat kebebasan.</li>''',
    77: r'''\t\t<li>\(\chi^2_k(p)\) menyatakan kuantil berorde \(p\) dari distribusi khi-kuadrat dengan \(k\) derajat kebebasan.</li>''',
    81: r'''<p>Karena distribusi normal standar dan distribusi \(t\) Student simetris terhadap 0, berlaku \(z(1 - p) = -z(p)\) dan \(t_k(1 - p) = -t_k(p)\) untuk \(p \in (0, 1)\) dan \(k \in \N_+\). Sebaliknya, distribusi khi-kuadrat tidak simetris.</p>''',
    83: r'''<h4 id="muk">Interval Kepercayaan bagi \(\mu\) dengan \(\sigma\) Diketahui</h4>''',
    85: r'''<p>Dalam pembahasan pertama, kita mengasumsikan bahwa rata-rata distribusi \(\mu\) tidak diketahui, tetapi simpangan baku \(\sigma\) diketahui. Asumsi ini tidak selalu artifisial. Sering ada keadaan ketika \(\sigma\) stabil sepanjang waktu sehingga setidaknya diketahui secara mendekati, sementara \(\mu\) berubah karena <q>perlakuan</q> yang berbeda. Contohnya diberikan dalam latihan komputasi di bawah. Variabel pivot \(Z\) menghasilkan interval kepercayaan bagi \(\mu\).</p>''',
    88: r'''\t<p class="math">Untuk \(\alpha \in (0, 1)\),</p>''',
    90: r'''\t\t<li>\(\left[M - z\left(1 - \frac{\alpha}{2}\right) \frac{\sigma}{\sqrt{n}}, M + z\left(1 - \frac{\alpha}{2}\right) \frac{\sigma}{\sqrt{n}}\right]\) adalah interval kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\).</li>''',
    91: r'''\t\t<li>\(M - z(1 - \alpha) \frac{\sigma}{\sqrt{n}}\) adalah batas bawah kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\).</li>''',
    92: r'''\t\t<li>\(M + z(1 - \alpha) \frac{\sigma}{\sqrt{n}}\) adalah batas atas kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\).</li></ol>''',
    95: r'''\t\t<summary>Rincian:</summary>''',
    96: r'''\t\t<p>Karena \(Z = \frac{M - \mu}{\sigma / \sqrt{n}}\) mempunyai distribusi normal standar, menurut definisi kuantil masing-masing kejadian berikut berpeluang \(1 - \alpha\):</p>''',
    99: r'''\t\t\t<li>\( \left\{\frac{M - \mu}{\sigma / \sqrt{n}} \le z(1 - \alpha)\right\} \)</li>''',
    100: r'''\t\t\t<li>\( \left\{\frac{M - \mu}{\sigma / \sqrt{n}} \ge -z(1 - \alpha)\right\} \)</li>''',
    102: r'''\t\t<p>Dalam setiap kasus, menyelesaikan pertidaksamaan terhadap \(\mu\) memberikan hasil yang dinyatakan.</p>''',
    106: r'''<p>Inilah dugaan interval baku bagi \(\mu\) ketika \(\sigma\) diketahui. Interval kepercayaan dua sisi pada (a) simetris terhadap rata-rata sampel \(M\) dan, seperti ditunjukkan oleh bukti, bersesuaian dengan peluang yang sama sebesar \(\frac{\alpha}{2}\) pada setiap ekor distribusi variabel pivot \(Z\). Namun, ini bukan satu-satunya interval kepercayaan dua sisi bertingkat \(1 - \alpha\); peluang \(\alpha\) dapat dibagi antara ekor kiri dan kanan distribusi \(Z\) dengan cara apa pun.</p>''',
    109: r'''\t<p class="math">Untuk setiap \(\alpha, \, p \in (0, 1)\), sebuah interval kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\) adalah''',
    112: r'''\t\t<li>\(p = \frac{1}{2}\) memberikan interval kepercayaan simetris dan berekor sama.</li>''',
    113: r'''\t\t<li>\(p \to 0\) memberikan interval dengan batas atas kepercayaan.</li>''',
    114: r'''\t\t<li>\(p \to 1\) memberikan interval dengan batas bawah kepercayaan.</li>''',
    117: r'''\t\t<summary>Rincian:</summary>''',
    118: r'''\t\t<p>Dari distribusi normal \(M\) dan definisi fungsi kuantil,''',
    120: r'''\t\tHasilnya kemudian diperoleh dengan menyelesaikan pertidaksamaan terhadap \(\mu\).</p>''',
    124: r'''<p>Ditinjau dari distribusi variabel pivot \(Z\), seperti ditunjukkan oleh bukti, interval kepercayaan dua sisi di atas bersesuaian dengan \(p \alpha\) pada ekor kanan dan \((1 - p) \alpha\) pada ekor kiri. Selanjutnya, mari kita telaah panjang interval kepercayaan ini.</p>''',
    127: r'''\t<p class="math">Untuk \(\alpha, \, p \in (0, 1)\), panjang (deterministik) interval kepercayaan dua sisi bertingkat \(1 - \alpha\) di atas adalah''',
    130: r'''\t\t<li>\(L\) menurun sebagai fungsi \(\alpha\), dengan \(L \downarrow 0\) ketika \(\alpha \uparrow 1\) dan \(L \uparrow \infty\) ketika \(\alpha \downarrow 0\).</li>''',
    131: r'''\t\t<li>\(L\) menurun sebagai fungsi \(n\), dengan \(L \downarrow 0\) ketika \(n \uparrow \infty\).</li>''',
    132: r'''\t\t<li>\(L\) meningkat sebagai fungsi \(\sigma\), dengan \(L \downarrow 0\) ketika \(\sigma \downarrow 0\) dan \(L \uparrow \infty\) ketika \(\sigma \uparrow \infty\).</li>''',
    133: r'''\t\t<li>Sebagai fungsi \(p\), \(L\) mula-mula menurun lalu meningkat, dengan nilai minimum pada titik simetri \(p = \frac{1}{2}\).</li>''',
    137: r'''<p>Hasil terakhir kembali menunjukkan adanya kompromi antara tingkat kepercayaan dan panjang interval kepercayaan. Jika \(n\) dan \(p\) tetap, kita hanya dapat memperkecil \(L\)—dan dengan demikian memperketat dugaan—dengan mengorbankan tingkat kepercayaan. Sebaliknya, kita hanya dapat menaikkan tingkat kepercayaan dengan memperpanjang interval. Ditinjau dari \(p\), yang terbaik di antara interval kepercayaan dua sisi bertingkat \(1 - \alpha\)—dan yang hampir selalu digunakan—adalah interval simetris berekor sama dengan \(p = \frac{1}{2}\):</p>''',
    140: r'''\t<p class="app">Gunakan <a href="JavaScript:openAncillary('../apps/MeanEstimate.html')" class="ancillary">eksperimen pendugaan rata-rata</a> untuk menjelajahi prosedur ini. Pilih distribusi normal dan pivot normal. Gunakan berbagai nilai parameter, tingkat kepercayaan, ukuran sampel, dan jenis interval. Untuk setiap konfigurasi, jalankan eksperimen 1.000 kali. Ketika simulasi berjalan, perhatikan bahwa interval kepercayaan berhasil memuat rata-rata jika dan hanya jika nilai variabel pivot berada di antara kedua kuantil. Perhatikan ukuran dan letak interval kepercayaan, lalu bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis.</p>''',
    144: r'''\t<p class="math">Untuk interval kepercayaan baku, misalkan \(d\) menyatakan jarak antara rata-rata sampel \(M\) dan suatu titik ujung. Artinya,''',
    146: r'''\tdengan \(z_\alpha = z(1 - \alpha /2 )\) untuk interval dua sisi dan \(z_\alpha = z(1 - \alpha)\) untuk interval kepercayaan atas atau bawah. Bilangan \(d\) adalah <dfn>margin galat</dfn> dugaan tersebut.</p>''',
    149: r'''<p>Perhatikan bahwa \(d\) deterministik dan panjang interval dua sisi baku adalah \(L = 2d\). Dalam banyak kasus, langkah pertama dalam <em>perancangan eksperimen</em> adalah menentukan ukuran sampel yang diperlukan untuk menduga \(\mu\) dengan margin galat dan tingkat kepercayaan tertentu.</p>''',
    152: r'''\t<p class="math">Ukuran sampel yang diperlukan untuk menduga \(\mu\) dengan tingkat kepercayaan \(1 - \alpha\) dan margin galat \(d\) adalah''',
    155: r'''\t\t<summary>Rincian:</summary>''',
    156: r'''\t\t<p>Hasil ini diperoleh dengan menyelesaikan definisi \(d\) di atas terhadap \(n\), lalu membulatkannya ke atas ke bilangan bulat berikutnya.</p>''',
    160: r'''<p>Perhatikan bahwa \(n\) berbanding lurus dengan \(z_\alpha^2\) dan \(\sigma^2\), serta berbanding terbalik dengan \(d^2\). Fakta terakhir ini menyiratkan <em>hukum hasil yang semakin berkurang</em> dalam mengecilkan margin galat. Misalnya, untuk mengecilkan suatu margin galat dengan faktor \(\frac{1}{2}\), kita harus memperbesar ukuran sampel dengan faktor 4.</p>''',
    162: r'''<h4 id="muu">Interval Kepercayaan bagi \(\mu\) dengan \(\sigma\) Tidak Diketahui</h4>''',
    164: r'''<p>Dalam pembahasan berikutnya, kita mengasumsikan bahwa rata-rata distribusi \(\mu\) dan simpangan baku \(\sigma\) tidak diketahui, sebagaimana lazimnya. Dalam hal ini, kita dapat menggunakan variabel pivot \(T\), bukan variabel pivot \(Z\), untuk membangun interval kepercayaan bagi \(\mu\).</p>''',
    167: r'''\t<p class="math">Untuk \(\alpha \in (0, 1)\),</p>''',
    169: r'''\t\t<li>\(\left[M - t_{n-1}\left(1 - \frac{\alpha}{2}\right) \frac{S}{\sqrt{n}}, M + t_{n-1}\left(1 - \frac{\alpha}{2}\right) \frac{S}{\sqrt{n}}\right]\) adalah interval kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\).</li>''',
    170: r'''\t\t<li>\(M - t_{n-1}(1 - \alpha) \frac{S}{\sqrt{n}}\) adalah batas bawah kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\).</li>''',
    171: r'''\t\t<li>\(M + t_{n-1}(1 - \alpha) \frac{S}{\sqrt{n}}\) adalah batas atas kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\).</li></ol>''',
    173: r'''\t\t<summary>Rincian:</summary>''',
    174: r'''\t\t<p>Karena \(T = \frac{M - \mu}{S / \sqrt{n}}\) mempunyai distribusi \(t\) Student dengan \(n - 1\) derajat kebebasan, menurut definisi kuantil masing-masing kejadian berikut berpeluang \(1 - \alpha\):</p>''',
    177: r'''\t\t\t<li>\( \left\{\frac{M - \mu}{S / \sqrt{n}} \le t_{n-1}(1 - \alpha)\right\} \)</li>''',
    178: r'''\t\t\t<li>\( \left\{\frac{M - \mu}{S / \sqrt{n}} \ge -t_{n-1}(1 - \alpha)\right\} \)</li>''',
    180: r'''\t\t<p>Dalam setiap kasus, menyelesaikan pertidaksamaan terhadap \(\mu\) memberikan hasil yang dinyatakan.</p>''',
    184: r'''<p>Inilah dugaan interval baku bagi \(\mu\) ketika \(\sigma\) tidak diketahui. Interval kepercayaan dua sisi pada (a) simetris terhadap rata-rata sampel \(M\) dan bersesuaian dengan peluang yang sama sebesar \(\frac{\alpha}{2}\) pada setiap ekor distribusi variabel pivot \(T\). Seperti sebelumnya, ini bukan satu-satunya interval kepercayaan; \(\alpha\) dapat dibagi antara ekor kiri dan kanan dengan cara apa pun.</p>''',
    187: r'''\t<p class="math">Untuk setiap \(\alpha, \, p \in (0, 1)\), sebuah interval kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\) adalah''',
    190: r'''\t\t<li>\(p = \frac{1}{2}\) memberikan interval kepercayaan simetris dan berekor sama.</li>''',
    191: r'''\t\t<li>\(p \to 0\) memberikan interval dengan batas atas kepercayaan.</li>''',
    192: r'''\t\t<li>\(p \to 1\) memberikan interval dengan batas bawah kepercayaan.</li>''',
    195: r'''\t\t<summary>Rincian:</summary>''',
    196: r'''\t\t<p>Karena \(T\) mempunyai distribusi \(t\) Student dengan \(n - 1\) derajat kebebasan, dari definisi kuantil diperoleh''',
    198: r'''\t\tHasilnya kemudian diperoleh dengan menyelesaikan pertidaksamaan terhadap \(\mu\).</p>''',
    202: r'''<p>Interval kepercayaan dua sisi di atas bersesuaian dengan \(p \alpha\) pada ekor kanan dan \((1 - p) \alpha\) pada ekor kiri distribusi variabel pivot \(T\). Selanjutnya, mari kita telaah panjang interval kepercayaan ini.</p>''',
    205: r'''\t<p class="math">Untuk \(\alpha, \, p \in (0, 1)\), panjang (acak) interval kepercayaan dua sisi bertingkat \(1 - \alpha\) di atas adalah''',
    208: r'''\t\t<li>\(L\) menurun sebagai fungsi \(\alpha\), dengan \(L \downarrow 0\) ketika \(\alpha \uparrow 1\) dan \(L \uparrow \infty\) ketika \(\alpha \downarrow 0\).</li>''',
    209: r'''\t\t<li>Sebagai fungsi \(p\), \(L\) mula-mula menurun lalu meningkat, dengan nilai minimum pada titik simetri \(p = \frac{1}{2}\).</li>''',
    214: r'''\t\t<summary>Rincian:</summary>''',
    215: r'''\t\t<p>Bagian (a) dan (b) mengikuti sifat fungsi kuantil Student \(t_{n-1}\). Bagian (c) dan (d) mengikuti fakta bahwa \(\frac{\sqrt{n - 1}}{\sigma} S\) mempunyai distribusi khi dengan \(n - 1\) derajat kebebasan.</p>''',
    219: r'''<p>Sekali lagi terdapat kompromi antara tingkat kepercayaan dan panjang interval kepercayaan. Jika \(n\) dan \(p\) tetap, kita hanya dapat memperkecil \(L\)—dan dengan demikian memperketat dugaan—dengan mengorbankan tingkat kepercayaan. Sebaliknya, kita hanya dapat menaikkan tingkat kepercayaan dengan memperpanjang interval. Ditinjau dari \(p\), yang terbaik di antara interval kepercayaan dua sisi bertingkat \(1 - \alpha\)—dan yang hampir selalu digunakan—adalah interval simetris berekor sama dengan \(p = \frac{1}{2}\). Terakhir, tidak tepat menganggap \(L\) sebagai fungsi aljabar dari \(S\), sebab \(S\) adalah statistik. Demikian pula, tidak tepat menganggap \(L\) sebagai fungsi aljabar dari \(n\), sebab mengubah \(n\) berarti mengambil data baru dan dengan demikian memperoleh nilai \(S\) yang baru.</p>''',
    222: r'''\t<p class="app">Gunakan <a href="JavaScript:openAncillary('../apps/MeanEstimate.html')" class="ancillary">eksperimen pendugaan rata-rata</a> untuk menjelajahi prosedur ini. Pilih distribusi normal dan pivot \(T\). Gunakan berbagai nilai parameter, tingkat kepercayaan, ukuran sampel, dan jenis interval. Untuk setiap konfigurasi, jalankan eksperimen 1.000 kali. Ketika simulasi berjalan, perhatikan bahwa interval kepercayaan berhasil memuat rata-rata jika dan hanya jika nilai variabel pivot berada di antara kedua kuantil. Perhatikan ukuran dan letak interval kepercayaan, lalu bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis.</p>''',
    225: r'''<h4 id="sig">Interval Kepercayaan bagi \(\sigma^2\)</h4>''',
    227: r'''<p>Selanjutnya kita akan membangun interval kepercayaan bagi \(\sigma^2\) menggunakan variabel pivot \(V\) yang diberikan dalam <a href="#mod2" class="ref"></a>.</p>''',
    230: r'''\t<p class="math">Untuk \(\alpha \in (0, 1)\),</p>''',
    232: r'''\t\t<li>\(\left[\frac{n - 1}{\chi^2_{n-1}\left(1 - \alpha / 2\right)} S^2,\frac{n - 1}{\chi^2_{n-1}\left(\alpha / 2\right)} S^2\right]\) adalah interval kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma^2\).</li>''',
    233: r'''\t\t<li>\(\frac{n - 1}{\chi^2_{n-1}\left(1 - \alpha\right)} S^2\) adalah batas bawah kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma^2\).</li>''',
    234: r'''\t\t<li>\(\frac{n - 1}{\chi^2_{n-1}(\alpha)} S^2\) adalah batas atas kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma^2\).</li>''',
    237: r'''\t\t<summary>Rincian:</summary>''',
    238: r'''\t\t<p>Karena \(V = \frac{n - 1}{\sigma^2} S^2\) mempunyai distribusi khi-kuadrat dengan \(n - 1\) derajat kebebasan, menurut definisi kuantil masing-masing kejadian berikut berpeluang \(1 - \alpha\):</p>''',
    244: r'''\t\t<p>Dalam setiap kasus, menyelesaikan pertidaksamaan terhadap \(\sigma^2\) memberikan hasil yang dinyatakan.</p>''',
    248: r'''<p>Inilah dugaan interval baku bagi \(\sigma^2\). Interval dua sisi pada (a) adalah interval <dfn>berekor sama</dfn>, yang bersesuaian dengan peluang \(\alpha / 2\) pada setiap ekor distribusi variabel pivot \(V\). Namun, interval ini tidak simetris terhadap varians sampel \(S^2\). Sekali lagi, peluang \(\alpha\) dapat dibagi antara ekor kiri dan kanan distribusi \(V\) dengan cara apa pun.</p>''',
    251: r'''\t<p class="math">Untuk setiap \(\alpha, \, p \in (0, 1)\), sebuah interval kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma^2\) adalah''',
    254: r'''\t\t<li>\(p = \frac{1}{2}\) memberikan interval kepercayaan berekor sama bertingkat \(1 - \alpha\).</li>''',
    255: r'''\t\t<li>\(p \to 0\) memberikan interval dengan batas atas bertingkat \(1 - \alpha\).</li>''',
    256: r'''\t\t<li>\(p \to 1\) memberikan interval dengan batas bawah bertingkat \(1 - \alpha\).</li>''',
    260: r'''<p>Ditinjau dari distribusi variabel pivot \(V\), interval kepercayaan di atas bersesuaian dengan \(p \alpha\) pada ekor kanan dan \((1 - p) \alpha\) pada ekor kiri. Sekali lagi, mari kita telaah panjang interval kepercayaan dua sisi yang umum. Panjangnya acak, tetapi merupakan kelipatan varians sampel \(S^2\). Karena itu, kita dapat menghitung nilai harapan dan varians panjang tersebut.</p>''',
    263: r'''\t<p class="math">Untuk \(\alpha, \, p \in (0, 1)\), panjang (acak) interval kepercayaan dua sisi pada teorema sebelumnya adalah''',
    266: r'''\t\t<li>\(\E(L) = \left[\frac{1}{\chi^2_{n-1}(\alpha - p \alpha)} - \frac{1}{\chi^2_{n-1}(1 - p \alpha)}\right] (n - 1) \sigma^2\)</li>''',
    267: r'''\t\t<li>\(\var(L) = 2 \left[\frac{1}{\chi^2_{n-1}(\alpha - p \alpha)} - \frac{1}{\chi^2_{n-1}(1 - p \alpha)}\right]^2 (n - 1) \sigma^4\)</li>''',
    271: r'''<p>Untuk membangun interval kepercayaan dua sisi yang optimal, wajar untuk mencari \(p\) yang meminimalkan panjang harapan. Masalah ini rumit, tetapi untuk \(n\) besar interval berekor sama dengan \(p = \frac{1}{2}\) ternyata mendekati optimal. Tentu saja, mengambil akar kuadrat kedua titik ujung dari interval kepercayaan mana pun bagi \(\sigma^2\) menghasilkan interval kepercayaan bertingkat \(1 - \alpha\) bagi simpangan baku distribusi \(\sigma\).</p>''',
    274: r'''\t<p class="app">Gunakan <a href="JavaScript:openAncillary('../apps/VarianceEstimate.html')" class="ancillary">eksperimen pendugaan varians</a> untuk menjelajahi prosedur ini. Pilih distribusi normal. Gunakan berbagai nilai parameter, tingkat kepercayaan, ukuran sampel, dan jenis interval. Untuk setiap konfigurasi, jalankan eksperimen 1.000 kali. Ketika simulasi berjalan, perhatikan bahwa interval kepercayaan berhasil memuat simpangan baku jika dan hanya jika nilai variabel pivot berada di antara kedua kuantil. Perhatikan ukuran dan letak interval kepercayaan, lalu bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis.</p>''',
    277: r'''<h3 id="bth">Himpunan Kepercayaan bagi \((\mu, \sigma)\)</h3>''',
    279: r'''<p>Dalam pembahasan di atas, kita membangun interval kepercayaan bagi \(\mu\) dan \(\sigma\) secara terpisah (sekali lagi, biasanya kedua parameter tidak diketahui). Selanjutnya kita akan menelaah <em>himpunan</em> kepercayaan bagi titik parameter \((\mu, \sigma)\). Himpunan-himpunan ini merupakan himpunan bagian dari ruang parameter \(\R \times (0, \infty)\).</p>''',
    281: r'''<h4 id="set">Himpunan Kepercayaan yang Dibangun dari Variabel Pivot</h4>''',
    283: r'''<p>Setiap variabel pivot \(Z\), \(T\), dan \(V\) dapat digunakan untuk membangun himpunan kepercayaan bagi \((\mu, \sigma)\). Jika digunakan sendiri-sendiri, masing-masing menghasilkan himpunan kepercayaan tak terbatas; hal ini tidak mengejutkan karena satu variabel pivot digunakan untuk menduga dua parameter. Pertama, kita tinjau variabel pivot normal \(Z\).</p>''',
    286: r'''\t<p class="math">Untuk setiap \(\alpha, \, p \in (0, 1)\), sebuah himpunan kepercayaan bertingkat \(1 - \alpha\) bagi \((\mu, \sigma)\) adalah''',
    288: r'''\tHimpunan kepercayaan ini berbentuk <q>kerucut</q> dalam ruang parameter \((\mu, \sigma)\), dengan titik puncak \((M, 0)\) dan garis batas yang mempunyai kemiringan \(-\sqrt{n} \big/ z(1 - p \alpha)\) dan \(-\sqrt{n} \big/ z(\alpha - p \alpha)\) apabila penyebutnya tidak nol; jika suatu kuantil penyebut bernilai nol, batas yang bersesuaian adalah garis vertikal.</p>''',
    290: r'''\t\t<summary>Rincian:</summary>''',
    291: r'''\t\t<p>Dari distribusi normal \(M\) dan definisi fungsi kuantil,''',
    293: r'''\t\tHasilnya kemudian diperoleh dengan menyelesaikan pertidaksamaan terhadap \(\mu\).</p>''',
    297: r'''<p>Kerucut kepercayaan tersebut ditampilkan pada grafik di bawah. (Perhatikan bahwa kedua kemiringan dapat sama-sama negatif atau sama-sama positif.)</p>''',
    300: r'''\t<figcaption>Himpunan kepercayaan berbasis variabel pivot normal</figcaption>''',
    301: r'''\t<img src="ZSet.png" alt="Kerucut himpunan kepercayaan berbasis pivot Z dalam ruang parameter mu-sigma">''',
    304: r'''<p>Variabel pivot \(T\) menghasilkan pernyataan berikut:</p>''',
    307: r'''\t<p class="math">Untuk setiap \(\alpha, \, p \in (0, 1)\), sebuah himpunan kepercayaan bertingkat \(1 - \alpha\) bagi \((\mu, \sigma)\) adalah''',
    310: r'''\t\t<summary>Rincian:</summary>''',
    311: r'''\t\t<p>Dari distribusi t Student bagi \(T\) dan definisi fungsi kuantil,''',
    313: r'''\t\tHasilnya kemudian diperoleh dengan menyelesaikan pertidaksamaan terhadap \(\mu\).</p>''',
    318: r'''\t<figcaption>Himpunan kepercayaan berbasis variabel pivot \(T\)</figcaption>''',
    319: r'''\t<img src="TSet.png" alt="Pita vertikal himpunan kepercayaan berbasis pivot T dalam ruang parameter mu-sigma">''',
    322: r'''<p>Berdasarkan konstruksinya, himpunan kepercayaan ini tidak memberikan informasi tentang \(\sigma\). Terakhir, variabel pivot \(V\) menghasilkan pernyataan berikut:</p>''',
    325: r'''\t<p class="math">Untuk setiap \(\alpha, \, p \in (0, 1)\), sebuah himpunan kepercayaan bertingkat \(1 - \alpha\) bagi \((\mu, \sigma)\) adalah''',
    328: r'''\t\t<summary>Rincian:</summary>''',
    329: r'''\t\t<p>Dari distribusi khi-kuadrat bagi \(V\) dan definisi fungsi kuantil,''',
    330: r'''\t\t\[ \P \left[\chi_{n-1}^2(\alpha - p \, \alpha) \lt V \lt \chi_{n-1}^2(1 - p \alpha) \right] = 1 - \alpha \]''',
    331: r'''\t\tHasilnya kemudian diperoleh dengan menyelesaikan pertidaksamaan terhadap \(\sigma^2\).</p>''',
    336: r'''\t<figcaption>Himpunan kepercayaan berbasis variabel pivot \(V\)</figcaption>''',
    337: r'''\t<img src="VSet.png" alt="Pita horizontal himpunan kepercayaan berbasis pivot V dalam ruang parameter mu-sigma">''',
    340: r'''<p>Berdasarkan konstruksinya, himpunan kepercayaan ini tidak memberikan informasi tentang \(\mu\).</p>''',
    342: r'''<h4 id="int">Irisan</h4>''',
    344: r'''<p>Sekarang kita dapat membentuk irisan beberapa himpunan kepercayaan di atas untuk memperoleh himpunan kepercayaan yang <em>terbatas</em> bagi \((\mu, \sigma)\). Kita akan menggunakan fakta bahwa rata-rata sampel \(M\) dan varians sampel \(S^2\) saling bebas, salah satu <a href="../sample/Normal.html">sifat khusus</a> terpenting dari sampel normal. Kita juga memerlukan hasil dalam <a href="Introduction.html#int">pendahuluan</a> tentang irisan himpunan kepercayaan. Dalam teorema-teorema berikut, misalkan \(\alpha, \, \beta, \, p, \, q \in (0, 1)\) dengan \(\alpha + \beta \lt 1\).</p>''',
    347: r'''\t<p class="math">Himpunan \(T_{\alpha, p} \cap V_{\beta, q}\) adalah himpunan kepercayaan konservatif bertingkat \(1 - (\alpha + \beta)\) bagi \((\mu, \sigma)\).</p>''',
    350: r'''<figure id="o006.random.interval.normal.figure-tv-intersection">''',
    351: r'''\t<figcaption>Himpunan kepercayaan \(T_{\alpha, p} \cap V_{\beta, q}\)</figcaption>''',
    352: r'''\t<img src="TVSet.png" alt="Irisan berbentuk persegi panjang dari pita pivot T dan V dalam ruang parameter mu-sigma">''',
    356: r'''\t<p class="math">Himpunan \(Z_{\alpha, p} \cap V_{\beta, q}\) adalah himpunan kepercayaan bertingkat \((1 - \alpha)(1 - \beta)\) bagi \((\mu, \sigma)\).</p>''',
    359: r'''<figure id="o006.random.interval.normal.figure-zv-intersection">''',
    360: r'''\t<figcaption>Himpunan kepercayaan \(Z_{\alpha, p} \cap V_{\beta, q}\)</figcaption>''',
    361: r'''\t<img src="ZVSet.png" alt="Irisan kerucut pivot Z dan pita pivot V yang membentuk daerah terbatas dalam ruang parameter mu-sigma">''',
    364: r'''<p>Menarik untuk diperhatikan bahwa himpunan kepercayaan \(T_{\alpha, p} \cap V_{\beta, q}\) merupakan himpunan hasil kali sebagai himpunan bagian ruang parameter, tetapi bukan sebagai himpunan bagian ruang sampel. Sebaliknya, himpunan kepercayaan \(Z_{\alpha, p} \cap V_{\beta, q}\) bukan himpunan hasil kali dalam ruang parameter, tetapi merupakan himpunan hasil kali dalam ruang sampel.</p>''',
    366: r'''<h3 id="exe">Latihan</h3>''',
    368: r'''<h4 id="rob">Robustitas</h4>''',
    370: r'''<p>Asumsi utama kita adalah bahwa distribusi asal sampel bersifat normal. Tentu saja, dalam masalah statistika nyata, kecil kemungkinan kita mengetahui banyak hal tentang distribusi asal sampel, apalagi mengetahui bahwa distribusi itu normal. Jika suatu prosedur statistika tetap bekerja cukup baik meskipun asumsi yang mendasarinya dilanggar, prosedur tersebut disebut <dfn>robust (tahan terhadap pelanggaran asumsi)</dfn>. Dalam subbagian ini, kita akan menjelajahi robustitas prosedur pendugaan bagi \(\mu\) dan \(\sigma\).</p>''',
    372: r'''<p>Andaikan distribusi asal sampel sebenarnya tidak normal. Ketika ukuran sampel \(n\) relatif besar, distribusi rata-rata sampel masih mendekati normal menurut <a href="../sample/CLT.html">teorema limit pusat</a>. Karena itu, dugaan interval bagi \(\mu\) mungkin masih berlaku secara mendekati.</p>''',
    375: r'''\t<p class="app">Gunakan simulasi <a href="JavaScript:openAncillary('../apps/MeanEstimate.html')" class="ancillary">eksperimen pendugaan rata-rata</a> untuk menjelajahi prosedur ini. Pilih distribusi gamma dan pivot Student. Gunakan berbagai nilai parameter, tingkat kepercayaan, ukuran sampel, dan jenis interval. Untuk setiap konfigurasi, jalankan eksperimen 1.000 kali. Perhatikan ukuran dan letak interval kepercayaan, lalu bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis.</p>''',
    379: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/MeanEstimate.html')" class="ancillary">eksperimen pendugaan rata-rata</a>, ulangi latihan sebelumnya dengan distribusi seragam.</p>''',
    382: r'''<p>Besarnya \(n\) yang diperlukan agar prosedur pendugaan interval bagi \(\mu\) bekerja dengan baik bergantung pada distribusi asal; semakin jauh distribusi tersebut menyimpang dari kenormalan, biasanya semakin besar \(n\) yang diperlukan. Konvergensi dalam teorema limit pusat dapat cepat pada banyak contoh yang lazim, sehingga ukuran sampel sekitar 30 atau lebih sering memadai dalam simulasi ini. Angka tersebut hanyalah aturan praktis, bukan jaminan universal; bentuk ekor, kemencengan, dan momen distribusi asal tetap menentukan mutu pendekatan.</p>''',
    384: r'''<p>Secara umum, prosedur interval khi-kuadrat eksak bagi \(\sigma\) tidak robust: di luar model normal, tidak ada hasil yang membuat distribusi pivot V tetap khi-kuadrat secara eksak.</p>''',
    387: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/VarianceEstimate.html')" class="ancillary">eksperimen pendugaan varians</a>, pilih distribusi gamma. Gunakan berbagai nilai parameter, tingkat kepercayaan, ukuran sampel, dan jenis interval. Untuk setiap konfigurasi, jalankan eksperimen 1.000 kali. Perhatikan ukuran dan letak interval kepercayaan, lalu bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis.</p>''',
    391: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/VarianceEstimate.html')" class="ancillary">eksperimen pendugaan varians</a>, pilih distribusi seragam. Gunakan berbagai nilai parameter, tingkat kepercayaan, ukuran sampel, dan jenis interval. Untuk setiap konfigurasi, jalankan eksperimen 1.000 kali. Perhatikan ukuran dan letak interval kepercayaan, lalu bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis.</p>''',
    394: r'''<h4 id="cmp">Latihan Komputasi</h4>''',
    396: r'''<p>Dalam latihan-latihan berikut, gunakan konstruksi berekor sama untuk interval kepercayaan dua sisi, kecuali jika dinyatakan lain.</p>''',
    399: r'''\t<p class="math">Panjang suatu komponen hasil pemesinan seharusnya 10 sentimeter, tetapi akibat ketidaksempurnaan proses produksi, panjang sebenarnya merupakan variabel acak berdistribusi normal dengan rata-rata \(\mu\) dan varians \(\sigma^2\). Varians timbul dari faktor bawaan proses yang cukup stabil sepanjang waktu. Dari data historis diketahui bahwa \(\sigma = 0.3\). Sebaliknya, \(\mu\) dapat diatur dengan menyesuaikan berbagai parameter proses sehingga cukup sering berubah menjadi nilai tak diketahui. Sampel 100 komponen mempunyai rata-rata 10.2.</p>''',
    401: r'''\t\t<li>Bangun interval kepercayaan 95% bagi \(\mu\).</li>''',
    402: r'''\t\t<li>Bangun batas atas kepercayaan 95% bagi \(\mu\).</li>''',
    403: r'''\t\t<li>Bangun batas bawah kepercayaan 95% bagi \(\mu\).</li>''',
    406: r'''\t\t<summary>Rincian:</summary>''',
    408: r'''\t\t\t<li>\((10.14, 10.26)\)</li>''',
    416: r'''\t<p class="math">Andaikan berat sekantong keripik kentang (dalam gram) merupakan variabel acak berdistribusi normal dengan rata-rata \(\mu\) dan simpangan baku \(\sigma\), keduanya tidak diketahui. Sampel 75 kantong mempunyai rata-rata 250 dan simpangan baku 10.</p>''',
    418: r'''\t\t<li>Bangun interval kepercayaan 90% bagi \(\mu\).</li>''',
    419: r'''\t\t<li>Bangun interval kepercayaan 90% bagi \(\sigma\).</li>''',
    420: r'''\t\t<li>Bangun persegi panjang kepercayaan konservatif 90% bagi \((\mu, \sigma)\).</li>''',
    423: r'''\t\t<summary>Rincian:</summary>''',
    433: r'''\t<p class="math">Pada sebuah perusahaan pemasaran jarak jauh, durasi panggilan penawaran melalui telepon (dalam detik) merupakan variabel acak berdistribusi normal dengan rata-rata \(\mu\) dan simpangan baku \(\sigma\), keduanya tidak diketahui. Sampel 50 panggilan mempunyai durasi rata-rata 300 dan simpangan baku 60.</p>''',
    435: r'''\t\t<li>Bangun batas atas kepercayaan 95% bagi \(\mu\).</li>''',
    436: r'''\t\t<li>Bangun batas bawah kepercayaan 95% bagi \(\sigma\).</li>''',
    439: r'''\t\t<summary>Rincian:</summary>''',
    448: r'''\t<p class="math">Di suatu perkebunan, berat buah persik (dalam ounce [oz]) pada saat panen merupakan variabel acak berdistribusi normal dengan simpangan baku 0.5. Berapa buah persik yang harus dijadikan sampel untuk menduga berat rata-rata dengan margin galat \(\pm 0.2\) dan tingkat kepercayaan 95%?</p>''',
    450: r'''\t\t<summary>Rincian:</summary>''',
    456: r'''\t<p class="math">Upah per jam untuk jenis pekerjaan konstruksi tertentu merupakan variabel acak berdistribusi normal dengan simpangan baku $1.25 dan rata-rata tak diketahui \(\mu\). Berapa pekerja yang harus dijadikan sampel untuk membangun batas bawah kepercayaan 95% bagi \(\mu\) dengan margin galat $0.25?</p>''',
    458: r'''\t\t<summary>Rincian:</summary>''',
    463: r'''<h4 id="dat">Latihan Analisis Data</h4>''',
    466: r'''\t<p class="stat">Dalam <a href="JavaScript:openAncillary('../data/Michelson.html')" class="ancillary">data Michelson</a>, asumsikan bahwa hasil pengukuran kecepatan cahaya mempunyai distribusi normal dengan rata-rata \(\mu\) dan simpangan baku \(\sigma\), keduanya tidak diketahui.</p>''',
    468: r'''\t\t<li>Bangun interval kepercayaan 95% bagi \(\mu\). Apakah nilai <q>sebenarnya</q> dari kecepatan cahaya berada dalam interval ini?</li>''',
    469: r'''\t\t<li>Bangun interval kepercayaan 95% bagi \(\sigma\).</li>''',
    470: r'''\t\t<li>Jelajahi secara grafis dan informal asumsi bahwa distribusi asal bersifat normal.</li>''',
    473: r'''\t\t<summary>Rincian:</summary>''',
    475: r'''\t\t\t<li>\((836.8, 868.0)\). Tidak, nilai sebenarnya tidak berada dalam interval.</li>''',
    482: r'''\t<p class="stat">Dalam <a href="JavaScript:openAncillary('../data/Cavendish.html')" class="ancillary">data Cavendish</a>, asumsikan bahwa hasil pengukuran massa jenis Bumi mempunyai distribusi normal dengan rata-rata \(\mu\) dan simpangan baku \(\sigma\), keduanya tidak diketahui.</p>''',
    484: r'''\t\t<li>Bangun interval kepercayaan 95% bagi \(\mu\). Apakah nilai <q>sebenarnya</q> dari massa jenis Bumi berada dalam interval ini?</li>''',
    485: r'''\t\t<li>Bangun interval kepercayaan 95% bagi \(\sigma\).</li>''',
    486: r'''\t\t<li>Jelajahi secara grafis dan informal asumsi bahwa distribusi asal bersifat normal.</li>''',
    489: r'''\t\t<summary>Rincian:</summary>''',
    491: r'''\t\t\t<li>\((5.364, 5.532)\). Ya, nilai sebenarnya berada dalam interval.</li>''',
    498: r'''\t<p class="stat">Dalam <a href="JavaScript:openAncillary('../data/Short.html')" class="ancillary">data Short</a>, asumsikan bahwa hasil pengukuran paralaks Matahari mempunyai distribusi normal dengan rata-rata \(\mu\) dan simpangan baku \(\sigma\), keduanya tidak diketahui.</p>''',
    500: r'''\t\t<li>Bangun interval kepercayaan 95% bagi \(\mu\). Apakah nilai <q>sebenarnya</q> dari paralaks Matahari berada dalam interval ini?</li>''',
    501: r'''\t\t<li>Bangun interval kepercayaan 95% bagi \(\sigma\).</li>''',
    502: r'''\t\t<li>Jelajahi secara grafis dan informal asumsi bahwa distribusi asal bersifat normal.</li>''',
    505: r'''\t\t<summary>Rincian:</summary>''',
    507: r'''\t\t\t<li>\((8.410, 8.822)\). Ya, nilai sebenarnya berada dalam interval.</li>''',
    514: r'''\t<p class="stat">Andaikan panjang mahkota bunga iris dari suatu spesies (Setosa, Virginica, atau Versicolor) berdistribusi normal. Gunakan <a href="JavaScript:openAncillary('../data/Fisher.html')" class="ancillary">data iris Fisher</a> untuk membangun interval kepercayaan dua sisi 90% bagi setiap parameter berikut.</p>''',
    516: r'''\t\t<li>Rata-rata panjang mahkota bunga iris Setosa.</li>''',
    517: r'''\t\t<li>Rata-rata panjang mahkota bunga iris Virginica.</li>''',
    518: r'''\t\t<li>Rata-rata panjang mahkota bunga iris Versicolor.</li>''',
    521: r'''\t\t<summary>Rincian:</summary>''',
    533: r'''\t\t<li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    534: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    536: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Pendugaan pada Model Bernoulli">3</a></li>''',
    537: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Pendugaan pada Model Normal Dua Sampel">4</a></li>''',
    538: r'''\t\t<li class="child"><a href="Bayes.html" title="Pendugaan Interval Bayes">5</a></li>''',
    539: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    540: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    543: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    544: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    545: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/sample/index.html": "../sample/index.html",
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/sample/LLN.html": "../sample/LLN.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
    "https://www.randomservices.org/random/sample/Normal.html": "../sample/Normal.html",
    "https://www.randomservices.org/random/point/index.html": "../point/index.html",
    "https://www.randomservices.org/random/interval/index.html": "index.html",
    "https://www.randomservices.org/random/interval/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/interval/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/interval/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/interval/Bayes.html": "Bayes.html",
    "https://www.randomservices.org/random/hypothesis/index.html": "../hypothesis/index.html",
    "https://www.randomservices.org/random/hypothesis/Normal.html": "../hypothesis/Normal.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, deskripsi gambar yang lebih informatif, koreksi matematis terbatas, dan kualifikasi rigor yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t</section>'''


MATH_REPAIRS_BY_INDEX = {
    73: r'''\( \left\{\frac{M - \mu}{\sigma / \sqrt{n}} \le z(1 - \alpha)\right\} \)''',
    74: r'''\( \left\{\frac{M - \mu}{\sigma / \sqrt{n}} \ge -z(1 - \alpha)\right\} \)''',
    167: r'''\( \left\{\frac{M - \mu}{S / \sqrt{n}} \le t_{n-1}(1 - \alpha)\right\} \)''',
    168: r'''\( \left\{\frac{M - \mu}{S / \sqrt{n}} \ge -t_{n-1}(1 - \alpha)\right\} \)''',
    309: r'''\[ \P \left[\chi_{n-1}^2(\alpha - p \, \alpha) \lt V \lt \chi_{n-1}^2(1 - p \alpha) \right] = 1 - \alpha \]''',
    343: r'''\((10.14, 10.26)\)''',
    356: r'''\(\pm 0.2\)''',
}


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
    return result + (f"#{fragment}" if fragment else "")


def math_spans(value: str) -> list[str]:
    return re.findall(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]", value)


def canonical_math(span: str) -> str:
    return re.sub(r"\s+", "", span)


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    source_text = source_bytes.decode("utf-8")
    lines = source_text.splitlines(keepends=True)
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

    source_math = math_spans(source_text)
    target_math = math_spans(rendered)
    if len(source_math) != 380 or len(target_math) != len(source_math):
        raise RuntimeError(f"protected-math count changed: {len(source_math)} -> {len(target_math)}")
    expected_math = [MATH_REPAIRS_BY_INDEX.get(index, span) for index, span in enumerate(source_math)]
    if Counter(map(canonical_math, target_math)) != Counter(map(canonical_math, expected_math)):
        missing = Counter(map(canonical_math, expected_math)) - Counter(map(canonical_math, target_math))
        extra = Counter(map(canonical_math, target_math)) - Counter(map(canonical_math, expected_math))
        raise RuntimeError(f"unexpected protected-math multiset delta: missing={missing}, extra={extra}")
    for index, new in MATH_REPAIRS_BY_INDEX.items():
        if index >= len(source_math) or new not in target_math:
            raise RuntimeError(f"declared math repair not realized at source span {index + 1}: {new!r}")

    unresolved = (
        'lang="en"',
        "JavaScript:openAncillary",
        ">Basic Theory<",
        ">The Normal Model<",
        ">Confidence Intervals",
        ">Confidence Sets",
        ">Intersections<",
        ">Exercises<",
        ">Robustness<",
        ">Computational Exercises<",
        ">Data Analysis Exercises<",
        ">Details:<",
        ">Apps<",
        ">Data Sets<",
        "> Biographies<",
        "among of",
        "degees",
        "confidence interal",
        "quanitle",
        "inequalilty",
        "confidence interals",
        "1000 time",
        "Verginica",
        "Sertosa",
        "Vergnica",
        r"\frac{n^2}{\sigma^2} V^2",
        r"\(\pm 2\)",
        r"\((10.1, 10.26)\)",
    )
    for phrase in unresolved:
        if phrase in rendered:
            raise RuntimeError(f"unresolved reader-facing/source defect remains: {phrase}")
    required_ids = (
        "o006.random.interval.normal.page",
        "mod1",
        "muk1",
        "muu1",
        "sig1",
        "set1",
        "int1",
        "rob1",
        "cmp1",
        "dat1",
        "o006.random.interval.normal.figure-tv-intersection",
        "o006.random.interval.normal.figure-zv-intersection",
    )
    for stable_id in required_ids:
        if f'id="{stable_id}"' not in rendered:
            raise RuntimeError(f"missing stable id: {stable_id}")
    ids = re.findall(r'\bid="([^"]+)"', rendered)
    if len(ids) != len(set(ids)):
        duplicates = sorted(value for value, count in Counter(ids).items() if count > 1)
        raise RuntimeError(f"duplicate IDs: {duplicates}")

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
