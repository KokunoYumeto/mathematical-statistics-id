#!/usr/bin/env python3
"""Create the bounded id-ID Bernoulli interval-estimation target."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "interval" / "Bernoulli.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "interval" / "Bernoulli.html"
SOURCE_URL = "https://www.randomservices.org/random/interval/Bernoulli.html"
SOURCE_SHA256 = "764f961e4f0db2562a3b1e42a446d3b5b3854cd8dc3468d017ee544f3aa87750"
EXPECTED_SOURCE_LINES = 371
EXPECTED_ELEMENTS = 285
EXPECTED_MATH_SPANS = 238
EXPECTED_UNITS = 24
EXPECTED_ANONYMOUS_UNITS = 15
EXPECTED_DETAILS = 16
EXPECTED_CORE_LINKS = 50
EXPECTED_SOURCE_IDS = 11


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''  <title>Pendugaan pada Model Bernoulli</title>''',
    9: r'''  <meta name="keywords" content="probabilitas, statistika, pendugaan interval, distribusi Bernoulli, tingkat kepercayaan, interval Wilson, interval Wald, interval konservatif">''',
    32: r'''    <li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    33: r'''    <li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    34: r'''    <li class="child"><a href="Normal.html" title="Pendugaan pada Model Normal">2</a></li>''',
    36: r'''    <li class="child"><a href="BivariateNormal.html" title="Pendugaan pada Model Normal Dua Sampel">4</a></li>''',
    37: r'''    <li class="child"><a href="Bayes.html" title="Pendugaan Interval Bayes">5</a></li>''',
    38: r'''    <li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    39: r'''    <li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    41: r'''  <h2 id="o006.random.interval.bernoulli.page">3. Pendugaan pada Model Bernoulli</h2>''',
    44: r'''<h3 id="o006.random.interval.bernoulli.section-introduction">Pendahuluan</h3>''',
    46: r'''<p>Ingat bahwa <dfn>variabel indikator</dfn> adalah <a href="../prob/Events.html">variabel acak</a> yang hanya mengambil nilai 0 dan 1. Dalam penerapan, variabel indikator menunjukkan kejadian mana dari dua kejadian komplementer dalam suatu eksperimen acak yang terjadi.</p>''',
    49: r'''  <p class="math">Contoh-contoh lazim meliputi</p>''',
    51: r'''    <li>Barang hasil produksi yang dipengaruhi faktor acak yang tidak terhindarkan dapat cacat atau layak.</li>''',
    52: r'''    <li>Pemilih yang dipilih dari suatu populasi dapat mendukung calon tertentu atau tidak mendukungnya.</li>''',
    53: r'''    <li>Orang yang dipilih dari suatu populasi dapat memiliki kondisi medis tertentu atau tidak memilikinya.</li>''',
    54: r'''    <li>Siswa dalam suatu kelas dapat lulus atau gagal dalam ujian terstandar.</li>''',
    55: r'''    <li>Sampel bahan radioaktif dapat memancarkan partikel alfa atau tidak memancarkannya dalam selang sepuluh detik tertentu.</li>''',
    59: r'''<p>Ingat pula bahwa distribusi variabel indikator dikenal sebagai <dfn>distribusi Bernoulli</dfn>, yang dinamai untuk menghormati <a href="JavaScript:openAncillary('../biographies/Bernoulli.html')" class="ancillary">Jacob Bernoulli</a>, dan mempunyai fungsi kepadatan probabilitas \(\P(X = 1) = p\), \(\P(X = 0) = 1 - p\), dengan \(p \in (0, 1)\) sebagai parameter dasarnya.</p>''',
    61: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-02">''',
    62: r'''  <p class="math">Dalam konteks contoh-contoh pada <a href="#exm" class="ref"></a>,</p>''',
    64: r'''    <li>\(p\) adalah probabilitas bahwa barang hasil produksi tersebut cacat.</li>''',
    65: r'''    <li>\(p\) adalah proporsi pemilih dalam populasi yang mendukung calon tersebut.</li>''',
    66: r'''    <li>\(p\) adalah proporsi orang dalam populasi yang memiliki kondisi medis tersebut.</li>''',
    67: r'''    <li>\(p\) adalah probabilitas bahwa seorang siswa dalam kelas tersebut akan lulus ujian.</li>''',
    68: r'''    <li>\(p\) adalah probabilitas bahwa bahan tersebut akan memancarkan partikel alfa dalam selang yang ditentukan.</li>''',
    72: r'''<p>Ingat bahwa rata-rata dan varians distribusi Bernoulli adalah \(\E(X) = p\) dan \(\var(X) = p (1 - p)\). Dalam penerapan statistika, \(p\) sering tidak diketahui dan harus diduga dari data sampel. Pada bagian ini kita akan mempelajari cara membangun dugaan interval bagi parameter tersebut dari data sampel. Bagian paralel mengenai <a href="../hypothesis/Bernoulli.html">pengujian pada model Bernoulli</a> terdapat dalam bab tentang <a href="../hypothesis/index.html">pengujian hipotesis</a>.</p>''',
    74: r'''<h3 id="o006.random.interval.bernoulli.section-one-sample">Model Satu Sampel</h3>''',
    76: r'''<h4 id="o006.random.interval.bernoulli.section-one-preliminaries">Pendahuluan Dasar</h4>''',
    78: r'''<p>Andaikan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak dari distribusi Bernoulli dengan parameter tak diketahui \(p \in [0, 1]\). Artinya, \(\bs X\) adalah barisan <a href="../bernoulli/Introduction.html">percobaan Bernoulli</a>. Dari contoh-contoh dalam pendahuluan di atas, perhatikan bahwa eksperimen yang mendasari sering berupa pengambilan sampel acak dari populasi dikotomis. Jika pengambilan sampel dilakukan <em>dengan</em> pengembalian, \(\bs X\) benar-benar merupakan barisan percobaan Bernoulli. Jika pengambilan sampel dilakukan <em>tanpa</em> pengembalian, variabel-variabelnya dependen, tetapi model Bernoulli masih berlaku secara hampiran jika ukuran populasi besar dibandingkan ukuran sampel \(n\). Uraian lebih lanjut terdapat dalam <a href="../urn/Introduction.html">pendahuluan</a> pada bab tentang <a href="../urn/index.html">model pengambilan sampel hingga</a>. Pada titik batas ruang parameter, bentuk pivot di bawah terdegenerasi; derivasi aproksimasi normalnya berlaku untuk parameter di bagian dalam interval.</p>''',
    80: r'''<p>Perhatikan bahwa rata-rata sampel dari vektor data \(\bs X\), yaitu''',
    82: r'''adalah proporsi sampel objek dengan jenis yang menjadi perhatian. Menurut <a href="../sample/CLT.html">teorema limit pusat</a>, skor baku''',
    84: r'''mempunyai <a href="../special/Normal.html">distribusi normal</a> standar secara hampiran dan karena itu merupakan variabel pivot hampiran bagi \(p\). Untuk ukuran sampel tertentu \(n\), distribusi \(Z\) paling dekat dengan normal ketika \(p\) berada dekat \(\frac{1}{2}\) dan paling jauh dari normal ketika \(p\) berada dekat 0 atau 1. Karena variabel pivot tersebut berdistribusi normal secara hampiran, konstruksi interval kepercayaan bagi \(p\) dalam model ini mirip dengan konstruksi <a href="Normal.html">interval kepercayaan</a> bagi rata-rata distribusi \(\mu\) dalam model normal. Namun, semua interval kepercayaan yang dibangun dengan cara ini bersifat hampiran.</p>''',
    86: r'''<p>Seperti biasa, untuk \(r \in (0, 1)\), misalkan \(z(r)\) menyatakan <a href="../dist/CDF.html#qnt">kuantil</a> berorde \(r\) dari distribusi normal standar. Nilai \(z(r)\) dapat diperoleh dari <a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">aplikasi kuantil</a> atau dari sebagian besar paket perangkat lunak statistika.</p>''',
    88: r'''<h4 id="o006.random.interval.bernoulli.section-wilson">Interval Kepercayaan Wilson</h4>''',
    91: r'''  <p class="math">Untuk \(\alpha \in (0, 1)\), berikut adalah himpunan kepercayaan hampiran bertingkat \(1 - \alpha\) bagi \(p\):</p>''',
    93: r'''    <li>\(\left\{ p \in [0, 1]: M - z(1 - \alpha / 2) \sqrt{p (1 - p) / n} \le p \le M + z(1 - \alpha / 2) \sqrt{p (1 - p) / n} \right\}\)</li>''',
    94: r'''    <li>\(\left\{ p \in [0, 1]: p \le M + z(1 - \alpha) \sqrt{p (1 - p) / n} \right\}\)</li>''',
    95: r'''    <li>\(\left\{ p \in [0, 1]: M - z(1 - \alpha) \sqrt{p (1 - p) / n} \le p \right\}\)</li>''',
    98: r'''    <summary>Rincian:</summary>''',
    99: r'''    <p>Dari pembahasan di atas, \((M - p) / \sqrt{p (1 - p) / n}\) mempunyai distribusi normal standar secara hampiran. Karena itu, menurut definisi kuantil,</p>''',
    105: r'''    <p>Menyelesaikan pertidaksamaan pada setiap kejadian terhadap \(p\) dalam bentuk \((M - p) / \sqrt{p (1 - p) / n}\) memberikan himpunan kepercayaan yang bersesuaian.</p>''',
    109: r'''<p>Himpunan-himpunan kepercayaan ini sebenarnya berupa interval yang dikenal sebagai <dfn>interval Wilson</dfn>, untuk menghormati Edwin Wilson.</p>''',
    112: r'''  <p class="math">Himpunan kepercayaan bagi \( p \) pada <a href="#wil1" class="ref"></a> merupakan interval. Misalkan''',
    113: r'''  \[ U(z) = \frac{n}{n + z^2} \left(M + \frac{z^2}{2 n} + z \sqrt{\frac{M (1 - M)}{n} + \frac{z^2}{4 n^2}}\right)\] Maka interval dan batas berikut mempunyai tingkat kepercayaan hampiran \(1 - \alpha\) bagi \(p\).</p>''',
    115: r'''    <li>Interval dua sisi \(\left[U[-z(1 - \alpha / 2)], U[z(1 - \alpha / 2)]\right]\).</li>''',
    116: r'''    <li>Batas atas \(U[z(1 - \alpha)]\).</li>''',
    117: r'''    <li>Batas bawah \(U[-z(1 - \alpha)]\).</li>''',
    120: r'''    <summary>Rincian:</summary>''',
    121: r'''    <p>Hasil ini diperoleh dengan menyelesaikan pertidaksamaan pada <a href="#wil1" class="ref"></a> terhadap \(p\). Pada setiap pertidaksamaan, kita dapat mengisolasi suku akar lalu menguadratkan kedua ruas. Dengan demikian diperoleh pertidaksamaan kuadrat yang dapat diselesaikan memakai rumus kuadrat.</p>''',
    125: r'''<p>Seperti biasa, interval kepercayaan <dfn>berekor sama</dfn> pada (a) bukan satu-satunya interval kepercayaan dua sisi bertingkat \(1 - \alpha\) bagi \(p\). Peluang \(\alpha\) dapat dibagi antara ekor kiri dan kanan distribusi normal standar dengan cara apa pun.</p>''',
    128: r'''  <p class="math">Untuk \(\alpha, \, r \in (0, 1)\), interval kepercayaan dua sisi hampiran bertingkat \(1 - \alpha\) bagi \(p\) adalah \(\left[U[z(\alpha - r \alpha)], U[z(1 - r \alpha)]\right]\), dengan \(U\) sebagai fungsi pada <a href="#wil2" class="ref"></a>.</p>''',
    130: r'''    <summary>Rincian:</summary>''',
    131: r'''    <p>Seperti dalam bukti <a href="#wil1" class="ref"></a>,''',
    133: r'''    Menyelesaikannya terhadap \(p\) dengan bantuan rumus kuadrat memberikan hasil yang dinyatakan.</p>''',
    137: r'''<p>Dalam praktik, interval kepercayaan berekor sama bertingkat \(1 - \alpha\) pada bagian (a) dari <a href="#wil2" class="ref"></a>, yang diperoleh dengan menetapkan \(r = \frac{1}{2}\) pada <a href="#wil3" class="ref"></a>, merupakan interval yang lazim digunakan. Ketika \(r \uparrow 1\), titik ujung kanan konvergen ke batas atas kepercayaan bertingkat \(1 - \alpha\) pada bagian (b); ketika \(r \downarrow 0\), titik ujung kiri konvergen ke batas bawah kepercayaan bertingkat \(1 - \alpha\) pada bagian (c).</p>''',
    139: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-06">''',
    140: r'''  <p class="app">Buka <a href="JavaScript:openAncillary('../apps/ProportionEstimate.html')" class="ancillary">eksperimen pendugaan proporsi</a> dan pilih prosedur pendugaan Wilson. Untuk berbagai nilai \(p\), tingkat kepercayaan, ukuran sampel, dan jenis interval, jalankan eksperimen 1.000 kali dan bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis. Perhatikan ukuran sampel \(n\): prosedur tidak bekerja sesuai tingkat nominal jika, untuk nilai \(p\) tersebut, jumlah harapan sukses dan gagal tidak cukup besar.</p>''',
    143: r'''<h4 id="o006.random.interval.bernoulli.section-wald">Interval Kepercayaan Wald</h4>''',
    145: r'''<p>Interval kepercayaan hampiran bertingkat \(1 - \alpha\) yang lebih sederhana bagi \(p\) dapat diperoleh dengan mengganti rata-rata distribusi \(p\) oleh rata-rata sampel \(M\) pada suku akar dalam pertidaksamaan pada <a href="#wil1" class="ref"></a>.</p>''',
    148: r'''  <p class="math">Untuk \(\alpha \in (0, 1)\), interval dan batas berikut mempunyai tingkat kepercayaan hampiran \(1 - \alpha\) bagi \(p\):</p>''',
    150: r'''    <li>Interval dua sisi dengan titik ujung \(M \pm z(1 - \alpha / 2) \sqrt{M (1 - M) / n}\).</li>''',
    151: r'''    <li>Batas atas \(M + z(1 - \alpha) \sqrt{M (1 - M) / n}\).</li>''',
    152: r'''    <li>Batas bawah \(M - z(1 - \alpha) \sqrt{M (1 - M) / n}\).</li>''',
    155: r'''    <summary>Rincian:</summary>''',
    156: r'''    <p>Seperti telah dikemukakan, hasil-hasil ini diperoleh dari himpunan kepercayaan pada <a href="#wil1" class="ref"></a> dengan mengganti \( p \) oleh \( M \) dalam bentuk \( \sqrt{p (1 - p) / n} \).</p>''',
    160: r'''<p>Interval kepercayaan ini dikenal sebagai <dfn>interval Wald</dfn>, untuk menghormati <a href="JavaScript:openAncillary('../biographies/Wald.html')" class="ancillary">Abraham Wald</a>. Interval Wald juga dapat diperoleh dari interval Wilson pada <a href="#wil2" class="ref"></a> dengan mengasumsikan bahwa \(n\) besar dibandingkan \(z\), sehingga \(n \big/ (n + z^2) \approx 1\), \(z^2 / 2 n \approx 0\), dan \(z^2 / 4 n^2 \approx 0\). Interval pada bagian (a) simetris terhadap proporsi sampel \(M\), tetapi panjang dan pusatnya acak. Inilah interval dua sisi yang lazim digunakan. Jika semua hasil dalam sampel sama, galat baku Wald menjadi nol; karena itu interval Wald sangat tidak andal di dekat batas 0 dan 1.</p>''',
    162: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-08">''',
    163: r'''  <p class="app">Buka <a href="JavaScript:openAncillary('../apps/ProportionEstimate.html')" class="ancillary">eksperimen pendugaan proporsi</a> dan pilih prosedur pendugaan Wald. Untuk berbagai nilai \(p\), tingkat kepercayaan, ukuran sampel, dan jenis interval, jalankan eksperimen 1.000 kali dan bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis. Perhatikan ukuran sampel \(n\): prosedur tidak bekerja sesuai tingkat nominal jika, untuk nilai \(p\) tersebut, jumlah harapan sukses dan gagal tidak cukup besar.</p>''',
    166: r'''<p>Seperti biasa, interval berekor sama pada <a href="#con4" class="ref"></a> bukan satu-satunya interval kepercayaan dua sisi bertingkat \(1 - \alpha\).</p>''',
    168: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-09">''',
    169: r'''  <p class="math">Untuk \(\alpha, \, r \in (0, 1)\), interval kepercayaan dua sisi hampiran bertingkat \(1 - \alpha\) bagi \(p\) adalah''',
    171: r'''  Interval dengan panjang terkecil adalah interval berekor sama dengan \(r = \frac 1 2\).</p>''',
    174: r'''<h4 id="o006.random.interval.bernoulli.section-one-conservative">Interval Kepercayaan Konservatif</h4>''',
    176: r'''<p>Perhatikan bahwa fungsi \(p \mapsto p(1 - p)\) pada interval \( [0, 1] \) mencapai maksimum ketika \(p = \frac 1 2\), dengan nilai maksimum \(\frac{1}{4}\). Fakta ini dapat digunakan untuk memperoleh interval kepercayaan konservatif bagi \( p \) dari interval kepercayaan dasar.</p>''',
    179: r'''  <p class="math">Untuk \(\alpha \in (0, 1)\), dalam aproksimasi normal interval dan batas berikut mempunyai tingkat kepercayaan hampiran sekurang-kurangnya \(1 - \alpha\) bagi \(p\):</p>''',
    181: r'''    <li>Interval dua sisi dengan titik ujung \(M \pm z(1 - \alpha / 2) \frac{1}{2 \sqrt{n}}\).</li>''',
    182: r'''    <li>Batas atas \(M + z(1 - \alpha) \frac{1}{2 \sqrt{n}}\).</li>''',
    183: r'''    <li>Batas bawah \(M - z(1 - \alpha) \frac{1}{2 \sqrt{n}}\).</li>''',
    186: r'''    <summary>Rincian:</summary>''',
    187: r'''    <p>Seperti telah dikemukakan, hasil-hasil ini diperoleh dari himpunan kepercayaan pada <a href="#wil1" class="ref"></a> dengan mengganti \( p \) oleh \( \frac 1 2 \) dalam bentuk \( \sqrt{p (1 - p) / n} \).</p>''',
    191: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-11">''',
    192: r'''  <p class="app">Buka <a href="JavaScript:openAncillary('../apps/ProportionEstimate.html')" class="ancillary">eksperimen pendugaan proporsi</a> dan pilih prosedur pendugaan konservatif. Untuk berbagai nilai \(p\), tingkat kepercayaan, ukuran sampel, dan jenis interval, jalankan eksperimen 1.000 kali dan bandingkan proporsi interval yang berhasil dengan tingkat kepercayaan teoretis. Perhatikan ukuran sampel \(n\): prosedur tidak bekerja sesuai tingkat nominal jika, untuk nilai \(p\) tersebut, jumlah harapan sukses dan gagal tidak cukup besar. Jika ukuran sampel \(n\) cukup besar untuk nilai \(p\), tingkat kepercayaan empiris sering lebih tinggi daripada tingkat nominal.</p>''',
    195: r'''<p>Interval kepercayaan pada (a) simetris terhadap proporsi sampel \(M\) dan panjangnya deterministik. Interval konservatif tentu lebih lebar daripada interval Wald hampiran pada <a href="#con4" class="ref"></a>. Dugaan konservatif dapat digunakan untuk merancang eksperimen. Ingat bahwa <dfn>margin galat</dfn> adalah jarak antara proporsi sampel \( M \) dan suatu titik ujung interval kepercayaan.</p>''',
    197: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-12">''',
    198: r'''  <p class="math">Dugaan konservatif bagi ukuran sampel \(n\) yang diperlukan untuk menduga \(p\) dengan tingkat kepercayaan \(1 - \alpha\) dan margin galat \(d\) adalah''',
    200: r'''  dengan \(z_\alpha = z(1 - \alpha / 2)\) untuk interval dua sisi dan \(z_\alpha = z(1 - \alpha)\) untuk batas atas atau bawah kepercayaan.</p>''',
    202: r'''    <summary>Rincian:</summary>''',
    203: r'''    <p>Pada tingkat kepercayaan \( 1 - \alpha \), margin galat adalah \( z_\alpha \frac{1}{2 \sqrt{n}} \). Menyamakan bentuk ini dengan nilai \( d \) yang ditetapkan lalu menyelesaikannya terhadap ukuran sampel memberikan hasil yang dinyatakan.</p>''',
    207: r'''<p>Seperti biasa, interval berekor sama pada <a href="#wald1" class="ref"></a> bukan satu-satunya interval kepercayaan konservatif dua sisi bertingkat \(1 - \alpha\).</p>''',
    209: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-13">''',
    210: r'''  <p class="math">Untuk \(\alpha, \, r \in (0, 1)\), interval kepercayaan konservatif dua sisi hampiran bertingkat \(1 - \alpha\) bagi \(p\) adalah''',
    212: r'''  Interval dengan panjang terkecil adalah interval berekor sama dengan \(r = \frac 1 2\).</p>''',
    215: r'''<h3 id="two">Model Dua Sampel</h3>''',
    217: r'''<h4 id="o006.random.interval.bernoulli.section-two-preliminaries">Pendahuluan Dasar</h4>''',
    219: r'''<p>Sering kali terdapat dua distribusi Bernoulli asal dengan parameter \( p_1, \, p_2 \in [0, 1] \), dan kita ingin menduga selisih \( p_1 - p_2 \). Masalah ini dapat muncul dalam contoh-contoh berikut:</p>''',
    222: r'''\t<li>Dalam pengendalian mutu, andaikan \( p_1 \) adalah proporsi barang cacat yang diproduksi dalam satu kondisi produksi, sedangkan \( p_2 \) adalah proporsi barang cacat dalam kondisi yang berbeda.</li>''',
    223: r'''\t<li>Dalam suatu pemilihan, andaikan \( p_1 \) adalah proporsi pemilih yang mendukung calon tertentu pada satu tahap kampanye, sedangkan \( p_2 \) adalah proporsi yang mendukung calon tersebut pada tahap berikutnya, mungkin setelah muncul suatu skandal.</li>''',
    224: r'''\t<li>Andaikan \( p_1 \) adalah proporsi siswa yang lulus ujian terstandar dengan metode persiapan biasa, sedangkan \( p_2 \) adalah proporsi siswa yang lulus dengan metode persiapan baru.</li>''',
    225: r'''\t<li>Andaikan \( p_1 \) adalah proporsi orang yang tidak divaksinasi dalam suatu populasi yang tertular penyakit tertentu, sedangkan \( p_2 \) adalah proporsi orang yang divaksinasi yang tertular penyakit tersebut.</li>''',
    228: r'''<p>Beberapa contoh tersebut dapat dipandang sebagai masalah <dfn>perlakuan–kontrol</dfn>. Kita dapat membangun dugaan interval \(I_1\) bagi \(p_1\) dan \(I_2\) bagi \(p_2\) secara terpisah seperti pada subbagian di atas. Namun, sebagaimana dicatat dalam <a href="Introduction.html">pendahuluan</a>, jika kedua interval ini mempunyai tingkat kepercayaan \(1 - \alpha\), maka himpunan hasil kali \(I_1 \times I_2\) mempunyai tingkat kepercayaan \((1 - \alpha)^2\) bagi \((p_1, p_2)\). Karena parameter yang menjadi perhatian adalah \(p_1 - p_2\), kita akan menggunakan pendekatan lain. Rumus berikut mensyaratkan dua sampel independen; desain yang mengamati individu yang sama pada dua waktu memerlukan analisis berpasangan.</p>''',
    230: r'''<h4 id="o006.random.interval.bernoulli.section-two-simplified">Interval Kepercayaan yang Disederhanakan</h4>''',
    232: r'''<p>Andaikan \( \bs X = (X_1, X_2, \ldots, X_{n_1}) \) merupakan sampel acak berukuran \( n_1 \) dari distribusi Bernoulli berparameter \( p_1 \), dan \( \bs Y = (Y_1, Y_2, \ldots, Y_{n_2}) \) merupakan sampel acak berukuran \( n_2 \) dari distribusi Bernoulli berparameter \( p_2 \). Kita mengasumsikan bahwa sampel \( \bs X \) dan \( \bs Y \) saling bebas. Misalkan''',
    234: r'''menyatakan rata-rata sampel atau proporsi sampel bagi \( \bs X \) dan \( \bs Y \). Dugaan titik yang wajar bagi \( p_1 - p_2 \), sekaligus unsur dasar dugaan interval, adalah \( M_1 - M_2 \). Seperti pada model satu sampel, jika \( n_i \) besar, \( M_i \) mempunyai distribusi normal hampiran dengan rata-rata \( p_i \) dan varians \( p_i (1 - p_i) / n_i \) untuk \( i \in \{1, 2\} \). Karena kedua sampel saling bebas, kedua rata-rata sampelnya juga saling bebas. Karena itu, \( M_1 - M_2 \) mempunyai distribusi normal hampiran dengan rata-rata \( p_1 - p_2 \) dan varians \( p_1 (1 - p_1) / n_1 + p_2 (1 - p_2) / n_2\). Kini kita mempunyai semua unsur untuk membangun interval kepercayaan hampiran yang disederhanakan bagi \( p_1 - p_2 \).</p>''',
    237: r'''  <p class="math">Untuk \(\alpha \in (0, 1)\), interval dan batas berikut mempunyai tingkat kepercayaan hampiran \(1 - \alpha\) bagi \(p_1 - p_2\):</p>''',
    239: r'''    <li>Interval dua sisi dengan titik ujung \((M_1 - M_2) \pm z\left(1 - \alpha / 2\right) \sqrt{M_1 (1 - M_1) / n_1 + M_2 (1 - M_2) / n_2} \).</li>''',
    240: r'''    <li>Batas bawah \( (M_1 - M_2) - z(1 - \alpha) \sqrt{M_1 (1 - M_1) / n_1 + M_2 (1 - M_2) / n_2} \).</li>''',
    241: r'''    <li>Batas atas \( (M_1 - M_2) + z(1 - \alpha) \sqrt{M_1 (1 - M_1) / n_1 + M_2 (1 - M_2) / n_2} \).</li>''',
    244: r'''    <summary>Rincian:</summary>''',
    245: r'''    <p>Seperti disebutkan di atas, jika \(n_1\) dan \(n_2\) besar,''',
    247: r'''    berdistribusi normal standar secara hampiran, dan karena itu demikian pula''',
    250: r'''      <li>\(\P[-z(1 - \alpha / 2) \le Z \le z(1 - \alpha / 2)] \approx 1 - \alpha\). Menyelesaikannya terhadap \(p_1 - p_2\) memberikan interval kepercayaan dua sisi.</li>''',
    251: r'''      <li>\(\P[Z \le z(1 - \alpha)] \approx 1 - \alpha\). Menyelesaikannya terhadap \(p_1 - p_2\) memberikan batas bawah kepercayaan.</li>''',
    252: r'''      <li>\(\P[-z(1 - \alpha) \le Z] \approx 1 - \alpha\). Menyelesaikannya terhadap \(p_1 - p_2\) memberikan batas atas kepercayaan.</li>''',
    257: r'''<p>Seperti biasa, interval berekor sama pada (a) bukan satu-satunya interval kepercayaan dua sisi hampiran bertingkat \(1 - \alpha\).</p>''',
    260: r'''  <p class="math">Untuk \(\alpha, \, r \in (0, 1)\), himpunan kepercayaan hampiran bertingkat \(1 - \alpha\) bagi \(p_1 - p_2\) adalah''',
    263: r'''    <summary>Rincian:</summary>''',
    264: r'''    <p>Seperti dinyatakan dalam rincian <a href="#two1" class="ref"></a>,''',
    266: r'''    berdistribusi normal standar secara hampiran jika \(n_1\) dan \(n_2\) besar. Karena itu, \(\P[z(\alpha - r \alpha) \le Z \le z(1 - r \alpha)] \approx 1 - \alpha\). Menyelesaikannya terhadap \(p_1 - p_2\) memberikan interval kepercayaan dua sisi.</p>''',
    270: r'''<h4 id="o006.random.interval.bernoulli.section-two-conservative">Interval Kepercayaan Konservatif</h4>''',
    272: r'''<p>Sekali lagi, \(p \mapsto p (1 - p)\) mencapai maksimum ketika \(p = \frac 1 2 \), dengan nilai maksimum \(\frac 1 4\). Fakta ini dapat digunakan untuk membangun interval kepercayaan konservatif hampiran bagi \(p_1 - p_2\).</p>''',
    275: r'''  <p class="math">Untuk \(\alpha \in (0, 1)\), dalam aproksimasi normal interval dan batas berikut mempunyai tingkat kepercayaan hampiran sekurang-kurangnya \(1 - \alpha\) bagi \(p_1 - p_2\):</p>''',
    277: r'''    <li>Interval dua sisi dengan titik ujung \((M_1 - M_2) \pm \frac{1}{2} z\left(1 - \alpha / 2\right) \sqrt{1 / n_1 + 1 / n_2} \).</li>''',
    278: r'''    <li>Batas bawah \( (M_1 - M_2) - \frac{1}{2} z(1 - \alpha) \sqrt{1 / n_1 + 1 / n_2} \).</li>''',
    279: r'''    <li>Batas atas \( (M_1 - M_2) + \frac{1}{2} z(1 - \alpha) \sqrt{1 / n_1 + 1 / n_2} \).</li>''',
    282: r'''    <summary>Rincian:</summary>''',
    283: r'''    <p>Hasil-hasil ini diperoleh dari teorema <a href="#two1"></a> dengan mengganti \(M_1 (1 - M_1)\) dan \(M_2 (1 - M_2)\) masing-masing oleh \(\frac 1 4\).</p>''',
    287: r'''<h3 id="o006.random.interval.bernoulli.section-computational-exercises">Latihan Komputasi</h3>''',
    289: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-17">''',
    290: r'''  <p class="math">Dalam jajak pendapat terhadap 1.000 pemilih terdaftar di suatu distrik, 427 orang memilih calon X. Dengan prosedur Wald, bangun interval kepercayaan dua sisi 95% bagi proporsi seluruh pemilih terdaftar di distrik tersebut yang memilih X.</p>''',
    292: r'''    <summary>Rincian:</summary>''',
    297: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-18">''',
    298: r'''  <p class="math">Sebuah koin dilempar 500 kali dan menghasilkan 302 sisi kepala. Dengan prosedur Wald, bangun batas bawah kepercayaan 95% bagi probabilitas munculnya sisi kepala. Apakah data mendukung anggapan bahwa koin tersebut seimbang?</p>''',
    300: r'''    <summary>Rincian:</summary>''',
    301: r'''    <p>0.568. Tidak; batas bawah tersebut berada di atas 0.5, sehingga data memberikan bukti kuat bahwa probabilitas kepala bukan 0.5. Pernyataan ini bukan probabilitas posterior bahwa koin seimbang.</p>''',
    305: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-19">''',
    306: r'''  <p class="math">Sampel 400 cip memori dari suatu lini produksi diuji dan 30 di antaranya cacat. Bangun interval kepercayaan konservatif dua sisi 90% bagi proporsi cip yang cacat.</p>''',
    308: r'''    <summary>Rincian:</summary>''',
    313: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-20">''',
    314: r'''  <p class="math">Sebuah perusahaan farmasi ingin menduga proporsi orang yang akan mengalami reaksi merugikan terhadap obat baru tertentu. Perusahaan menghendaki interval dua sisi dengan margin galat 0.03 dan tingkat kepercayaan 95%. Berapa besar sampel yang diperlukan?</p>''',
    316: r'''    <summary>Rincian:</summary>''',
    321: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-21">''',
    322: r'''  <p class="math">Sebuah biro iklan ingin membangun batas bawah kepercayaan 99% bagi proporsi dokter gigi yang merekomendasikan merek pasta gigi tertentu. Margin galat yang dikehendaki adalah 0.02. Berapa besar sampel yang diperlukan?</p>''',
    324: r'''    <summary>Rincian:</summary>''',
    325: r'''    <p>3383</p>''',
    329: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-22">''',
    330: r'''  <p class="stat"><a href="JavaScript:openAncillary('../data/Buffon.html')" class="ancillary">Data percobaan Buffon</a> memuat hasil 104 pengulangan <a href="../buffon/Buffon.html#npr">eksperimen jarum Buffon</a>. Secara teoretis, data tersebut seharusnya bersesuaian dengan percobaan Bernoulli dengan \(p = 2 / \pi\), tetapi karena jarum dijatuhkan oleh mahasiswa sungguhan, nilai sebenarnya dari \(p\) tidak diketahui. Dengan prosedur Wald, bangun interval kepercayaan 95% bagi \(p\). Apakah data mendukung nilai teoretis \(p\)?</p>''',
    332: r'''    <summary>Rincian:</summary>''',
    333: r'''    <p>\((0.443, 0.634)\). Nilai teoretis kira-kira 0.637 dan tidak berada dalam interval kepercayaan tersebut.</p>''',
    337: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-23">''',
    338: r'''  <p class="math">Sebuah fasilitas manufaktur mempunyai dua lini produksi untuk barang tertentu. Dalam sampel 150 barang dari lini 1, terdapat 12 barang cacat. Dalam sampel 130 barang dari lini 2, terdapat 10 barang cacat. Dengan interval yang disederhanakan, bangun interval kepercayaan dua sisi 95% bagi \( p_1 - p_2 \), dengan \( p_i \) sebagai proporsi barang cacat dari lini \( i \) untuk \( i \in \{1, 2\} \).</p>''',
    340: r'''    <summary>Rincian:</summary>''',
    341: r'''    <p>\( [-0.060, 0.066] \)</p>''',
    345: r'''<div class="unit" id="o006.random.interval.bernoulli.unit-24">''',
    346: r'''  <p class="math">Vaksin influenza disesuaikan setiap tahun dengan galur influenza dominan yang diprediksi. Andaikan 45 dari 500 orang yang tidak divaksinasi tertular influenza dalam suatu selang waktu, sedangkan 20 dari 300 orang yang divaksinasi tertular influenza dalam selang waktu yang sama. Dengan interval yang disederhanakan, bangun interval kepercayaan dua sisi 99% bagi \( p_1 - p_2 \), dengan \( p_1 \) sebagai insidensi influenza dalam populasi yang tidak divaksinasi dan \( p_2 \) sebagai insidensi influenza dalam populasi yang divaksinasi.</p>''',
    352: r'''    <li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    353: r'''    <li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    354: r'''    <li class="child"><a href="Normal.html" title="Pendugaan pada Model Normal">2</a></li>''',
    356: r'''    <li class="child"><a href="BivariateNormal.html" title="Pendugaan pada Model Normal Dua Sampel">4</a></li>''',
    357: r'''    <li class="child"><a href="Bayes.html" title="Pendugaan Interval Bayes">5</a></li>''',
    358: r'''    <li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    359: r'''    <li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    362: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    363: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    364: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/interval/index.html": "index.html",
    "https://www.randomservices.org/random/interval/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/interval/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/interval/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/interval/Bayes.html": "Bayes.html",
    "https://www.randomservices.org/random/hypothesis/index.html": "../hypothesis/index.html",
    "https://www.randomservices.org/random/hypothesis/Bernoulli.html": "../hypothesis/Bernoulli.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, koreksi matematis, tautan, dan jawaban yang terbatas, serta kualifikasi rigor yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t</section>'''


MATH_REPAIRS_BY_INDEX = {
    196: r'''\(\P[Z \le z(1 - \alpha)] \approx 1 - \alpha\)''',
    198: r'''\(\P[-z(1 - \alpha) \le Z] \approx 1 - \alpha\)''',
    208: r'''\(\P[z(\alpha - r \alpha) \le Z \le z(1 - r \alpha)] \approx 1 - \alpha\)''',
    229: r'''\((0.443, 0.634)\)''',
    234: r'''\( [-0.060, 0.066] \)''',
}


ADDITIVE_IDS = {
    "o006.random.interval.bernoulli.page",
    "o006.random.interval.bernoulli.section-introduction",
    "o006.random.interval.bernoulli.section-one-sample",
    "o006.random.interval.bernoulli.section-one-preliminaries",
    "o006.random.interval.bernoulli.section-wilson",
    "o006.random.interval.bernoulli.section-wald",
    "o006.random.interval.bernoulli.section-one-conservative",
    "o006.random.interval.bernoulli.section-two-preliminaries",
    "o006.random.interval.bernoulli.section-two-simplified",
    "o006.random.interval.bernoulli.section-two-conservative",
    "o006.random.interval.bernoulli.section-computational-exercises",
    "o006.random.interval.bernoulli.unit-02",
    "o006.random.interval.bernoulli.unit-06",
    "o006.random.interval.bernoulli.unit-08",
    "o006.random.interval.bernoulli.unit-09",
    "o006.random.interval.bernoulli.unit-11",
    "o006.random.interval.bernoulli.unit-12",
    "o006.random.interval.bernoulli.unit-13",
    "o006.random.interval.bernoulli.unit-17",
    "o006.random.interval.bernoulli.unit-18",
    "o006.random.interval.bernoulli.unit-19",
    "o006.random.interval.bernoulli.unit-20",
    "o006.random.interval.bernoulli.unit-21",
    "o006.random.interval.bernoulli.unit-22",
    "o006.random.interval.bernoulli.unit-23",
    "o006.random.interval.bernoulli.unit-24",
}


class TagStream(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)


def tag_stream(value: str) -> list[str]:
    parser = TagStream()
    parser.feed(value)
    parser.close()
    return parser.tags


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

    source_tags = tag_stream(source_text)
    if len(source_tags) != EXPECTED_ELEMENTS:
        raise RuntimeError(f"unexpected authority element count: {len(source_tags)}")
    source_math = math_spans(source_text)
    if len(source_math) != EXPECTED_MATH_SPANS:
        raise RuntimeError(f"unexpected authority math count: {len(source_math)}")
    source_units = re.findall(r'<div class="unit"(?: id="([^"]+)")?>', source_text)
    if len(source_units) != EXPECTED_UNITS or source_units.count("") != EXPECTED_ANONYMOUS_UNITS:
        raise RuntimeError(f"unexpected authority unit census: {len(source_units)} / {source_units.count('')}")
    if source_text.count("<details>") != EXPECTED_DETAILS:
        raise RuntimeError("unexpected authority disclosure count")
    source_ids = re.findall(r'\bid="([^"]+)"', source_text)
    if len(source_ids) != EXPECTED_SOURCE_IDS or len(source_ids) != len(set(source_ids)):
        raise RuntimeError("unexpected authority ID census")
    if len(re.findall(r'<a\b[^>]*\bhref="[^"]+"', source_text)) != EXPECTED_CORE_LINKS:
        raise RuntimeError("unexpected authority link count")

    for line_number, replacement in sorted(LINE_REPLACEMENTS.items()):
        replace_exact_line(lines, line_number, replacement)
    core = "".join(lines)
    core = re.sub(r'href="([^"]+)"', lambda match: f'href="{convert_href(match.group(1))}"', core)

    target_tags = tag_stream(core)
    if target_tags != source_tags:
        raise RuntimeError(f"core topology changed: {len(source_tags)} -> {len(target_tags)}")
    target_math = math_spans(core)
    expected_math = [MATH_REPAIRS_BY_INDEX.get(index, span) for index, span in enumerate(source_math)]
    if len(target_math) != EXPECTED_MATH_SPANS:
        raise RuntimeError(f"protected-math count changed: {len(source_math)} -> {len(target_math)}")
    if list(map(canonical_math, target_math)) != list(map(canonical_math, expected_math)):
        for index, (actual, expected) in enumerate(zip(target_math, expected_math), start=1):
            if canonical_math(actual) != canonical_math(expected):
                raise RuntimeError(
                    f"unexpected protected-math delta at span {index}: {actual!r} != {expected!r}"
                )
        raise RuntimeError("unexpected protected-math sequence delta")
    for index, repaired in MATH_REPAIRS_BY_INDEX.items():
        if repaired not in target_math:
            raise RuntimeError(f"declared math repair not realized at source span {index + 1}")

    target_units = re.findall(r'<div class="unit"(?: id="([^"]+)")?>', core)
    if len(target_units) != EXPECTED_UNITS or any(not value for value in target_units):
        raise RuntimeError("target unit IDs are incomplete")
    if core.count("<details>") != EXPECTED_DETAILS or core.count("<summary>") != EXPECTED_DETAILS:
        raise RuntimeError("target disclosure topology changed")
    if len(re.findall(r'<a\b[^>]*\bhref="[^"]+"', core)) != EXPECTED_CORE_LINKS:
        raise RuntimeError("target core link count changed")
    ids = re.findall(r'\bid="([^"]+)"', core)
    if len(ids) != len(set(ids)):
        duplicates = sorted(value for value, count in Counter(ids).items() if count > 1)
        raise RuntimeError(f"duplicate IDs: {duplicates}")
    if set(source_ids) - set(ids):
        raise RuntimeError(f"native IDs were lost: {sorted(set(source_ids) - set(ids))}")
    if set(ids) - set(source_ids) != ADDITIVE_IDS:
        raise RuntimeError(
            f"additive ID set changed: missing={sorted(ADDITIVE_IDS - (set(ids) - set(source_ids)))}; "
            f"extra={sorted((set(ids) - set(source_ids)) - ADDITIVE_IDS)}"
        )
    if len(ids) != EXPECTED_SOURCE_IDS + len(ADDITIVE_IDS):
        raise RuntimeError("target ID count changed")

    unresolved = (
        'lang="en"',
        "JavaScript:openAncillary",
        ">Introduction<",
        ">The One-Sample Model<",
        ">The Two-Sample Model<",
        ">Preliminaries<",
        ">Wilson Confidence Intervals<",
        ">Wald Confidence Intervals<",
        ">Conservative Confidence Intervals<",
        ">Simplified Confidence Intervals<",
        ">Computational Exercises<",
        ">Details:<",
        ">Apps<",
        ">Data Sets<",
        "> Biographies<",
        "poportion",
        "squence",
        "confidecne",
        "enpoint",
        "approximatle",
        "chpater n",
        "work as advertized",
        'href="two2"',
        "hypothesis/BivariateNormal.html",
        r"\P[Z \le z(1 - \alpha / 2)] \approx 1 - \alpha",
        r"\P[-z(\alpha - r \alpha) \le Z",
        "0.579",
        "3382",
        "(0.433, 0.634)",
        "[-0.050, 0.056]",
    )
    for phrase in unresolved:
        if phrase in core:
            raise RuntimeError(f"unresolved reader-facing/source defect remains: {phrase}")
    required = (
        'href="../sample/CLT.html"',
        'href="Introduction.html"',
        'href="Normal.html"',
        'href="BivariateNormal.html"',
        'href="Bayes.html"',
        'href="../hypothesis/Bernoulli.html"',
        'href="#two1"',
        "0.568",
        "3383",
        "(0.443, 0.634)",
        "[-0.060, 0.066]",
        "jumlah harapan sukses dan gagal",
        "bukan probabilitas posterior",
    )
    for phrase in required:
        if phrase not in core:
            raise RuntimeError(f"required translated/corrected surface absent: {phrase}")
    if "http://" in core:
        raise RuntimeError("insecure HTTP link remains")

    marker = "</footer>"
    if core.count(marker) != 1:
        raise RuntimeError("footer marker count changed")
    rendered = core.replace(marker, materialize_indentation(EDITION_NOTICE) + "\n" + marker, 1)
    if len(tag_stream(rendered)) != EXPECTED_ELEMENTS + 8:
        raise RuntimeError("edition-notice element delta changed")
    if len(re.findall(r'<a\b[^>]*\bhref="[^"]+"', rendered)) != EXPECTED_CORE_LINKS + 4:
        raise RuntimeError("edition-notice link delta changed")

    output = rendered.encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(output)
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: "
        f"{len(output)} bytes / sha256 {hashlib.sha256(output).hexdigest()} / "
        f"{EXPECTED_ELEMENTS} core elements / {EXPECTED_MATH_SPANS} TeX / "
        f"{EXPECTED_UNITS} units / {EXPECTED_DETAILS} details / {len(ids)} core IDs"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
