#!/usr/bin/env python3
"""Create the bounded id-ID Introduction to Set Estimation target."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "interval" / "Introduction.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "interval" / "Introduction.html"
SOURCE_URL = "https://www.randomservices.org/random/interval/Introduction.html"
SOURCE_SHA256 = "e5e6cb402c737c1d63a58ef4509975633f9cfa483f8f0afa8860ff9b6dbb4ee3"
EXPECTED_SOURCE_LINES = 313


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Pendahuluan</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, pendugaan himpunan, pendugaan interval, tingkat kepercayaan, variabel pivot, keluarga lokasi-skala, distribusi eksponensial">''',
    32: r'''\t\t<li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    34: r'''\t\t<li class="child"><a href="Normal.html" title="Pendugaan pada Model Normal">2</a></li>''',
    35: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Pendugaan pada Model Bernoulli">3</a></li>''',
    36: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Pendugaan pada Model Normal Dua Sampel">4</a></li>''',
    37: r'''\t\t<li class="child"><a href="Bayes.html" title="Pendugaan Interval Bayes">5</a></li>''',
    38: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    39: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    41: r'''\t<h2 id="o006.random.interval.introduction.page">1. Pendahuluan</h2>''',
    44: r'''<h3 id="o006.random.interval.introduction.section.basic-theory">Teori Dasar</h3>''',
    46: r'''<h4 id="mod">Model Statistik Dasar</h4>''',
    48: r'''<p>Seperti biasa, titik awal kita adalah sebuah <a href="../prob/Experiments.html">eksperimen acak</a> dengan <a href="../prob/Events.html">ruang sampel</a> yang mendasari dan sebuah <a href="../prob/Probability.html">ukuran probabilitas</a> \(\P\). Dalam model statistik dasar, terdapat <a href="../prob/Probability.html">variabel acak</a> teramati \(\bs{X}\) yang mengambil nilai dalam suatu himpunan \(S\). Secara umum, struktur \(\bs{X}\) dapat cukup rumit. Misalnya, jika eksperimennya adalah mengambil sampel \(n\) objek dari suatu populasi dan mencatat berbagai pengukuran yang diminati, maka''',
    50: r'''dengan \(X_i\) sebagai vektor pengukuran untuk objek ke-\(i\). Kasus khusus terpenting terjadi ketika \((X_1, X_2, \ldots, X_n)\) saling bebas dan berdistribusi identik. Dalam hal ini, kita mempunyai <a href="../sample/Introduction.html">sampel acak</a> berukuran \(n\) dari distribusi bersama tersebut.</p>''',
    52: r'''<p>Misalkan pula distribusi \(\bs{X}\) bergantung pada parameter \(\theta\) yang nilainya berada dalam suatu himpunan \(\Theta\). Parameter itu juga dapat bernilai vektor; dalam hal ini \(\Theta \subseteq \R^k\) untuk suatu \(k \in \N_+\), dan vektor parameternya berbentuk \(\bs{\theta} = (\theta_1, \theta_2, \ldots, \theta_k)\).</p>''',
    54: r'''<h4 id="o006.random.interval.introduction.section.confidence-sets">Himpunan Kepercayaan</h4>''',
    56: r'''<div class="unit" id="o006.random.interval.introduction.unit-01">''',
    57: r'''\t<p class="dfn">Sebuah <dfn>himpunan kepercayaan</dfn> adalah himpunan bagian \(C(\bs{X})\) dari ruang parameter \(\Theta\) yang hanya bergantung pada variabel data \(\bs{X}\), bukan pada parameter yang tak diketahui. <dfn>Tingkat kepercayaan</dfn> adalah infimum, atas seluruh ruang parameter, dari peluang bahwa \(\theta \in C(\bs{X})\):''',
    58: r'''\t\[ \inf_{\theta \in \Theta}\P_\theta[\theta \in C(\bs{X})] \]</p>''',
    61: r'''<p>Jadi, dalam suatu pengertian, himpunan kepercayaan adalah <em>statistik bernilai himpunan</em>. Himpunan kepercayaan merupakan penduga \(\theta\) karena kita berharap \(\theta \in C(\bs{X})\) dengan peluang besar, sehingga tingkat kepercayaannya tinggi. Karena distribusi \(\bs{X}\) bergantung pada \(\theta\), ukuran probabilitas \(\P\) dalam definisi tingkat kepercayaan juga bergantung pada \(\theta\); indeks ini biasanya disembunyikan agar notasi tetap ringkas. Biasanya kita berusaha membangun himpunan kepercayaan bagi \(\theta\) dengan tingkat yang ditetapkan sebesar \(1 - \alpha\), dengan \(0 \lt \alpha \lt 1\). Tingkat kepercayaan yang lazim adalah 0,9, 0,95, dan 0,99. Kadang-kadang yang dapat dibangun hanyalah himpunan yang tingkat kepercayaannya <em>sekurang-kurangnya</em> \(1 - \alpha\); himpunan seperti ini disebut himpunan kepercayaan \(1 - \alpha\) yang <dfn>konservatif</dfn> bagi \(\theta\).</p>''',
    64: r'''\t<figcaption>Dugaan himpunan yang berhasil memuat parameter</figcaption>''',
    65: r'''\t<img src="SetEstimate.png" alt="Himpunan kepercayaan acak yang memuat nilai parameter sebenarnya">''',
    68: r'''<p>Misalkan \(C(\bs{X})\) adalah himpunan kepercayaan bertingkat sekurang-kurangnya \(1 - \alpha\) bagi parameter \(\theta\). Ketika eksperimen dijalankan dan data \(\bs{x}\) diamati, himpunan kepercayaan yang <em>dihitung</em> adalah \(C(\bs{x})\). Nilai sebenarnya dari \(\theta\) berada atau tidak berada dalam himpunan itu, dan biasanya kita tidak akan pernah mengetahuinya. Namun, menurut <a href="../sample/Mean.html">hukum bilangan besar</a>, jika eksperimen kepercayaan tersebut diulangi terus-menerus pada nilai parameter yang sama, proporsi himpunan yang memuat \(\theta\) akan konvergen ke \(\P_\theta[\theta \in C(\bs{X})] \ge 1 - \alpha\); kesamaan berlaku bila peluang cakupan pada nilai parameter tersebut tepat sama dengan tingkat nominalnya. Inilah makna tepat istilah <dfn>kepercayaan</dfn>. Dalam terminologi statistika yang lazim, himpunan acak \(C(\bs{X})\) adalah <dfn>penduga</dfn>, sedangkan himpunan deterministik \(C(\bs{x})\), berdasarkan nilai amatan \(\bs{x}\), adalah <dfn>dugaan</dfn>.</p>''',
    70: r'''<p>Kualitas himpunan kepercayaan sebagai penduga \(\theta\) ditentukan oleh dua faktor: tingkat kepercayaan dan <dfn>presisi</dfn>, yang diukur melalui <q>ukuran</q> himpunan tersebut. Penduga yang baik berukuran kecil—sehingga memberi dugaan \(\theta\) yang presisi—dan memiliki tingkat kepercayaan tinggi. Akan tetapi, untuk \(\bs{X}\) tertentu biasanya terdapat kompromi antara tingkat kepercayaan dan presisi: tingkat kepercayaan hanya dapat dinaikkan dengan memperbesar himpunan, sedangkan ukuran himpunan hanya dapat diperkecil dengan menurunkan tingkat kepercayaan. Cara mengukur <q>ukuran</q> himpunan kepercayaan bergantung pada dimensi ruang parameter dan sifat himpunannya. Selain itu, ukuran himpunan biasanya acak, walaupun dalam beberapa kasus khusus dapat bersifat deterministik.</p>''',
    72: r'''<p>Kasus-kasus ekstrem dapat memberi sedikit pemahaman. Pertama, misalkan \(C(\bs{X}) = \Theta\). Penduga himpunan ini mempunyai tingkat kepercayaan maksimum 1, tetapi tanpa presisi sehingga tidak berguna—kita sudah <em>mengetahui</em> bahwa \(\theta \in \Theta\). Pada ekstrem lain, misalkan \(C(\bs{X})\) adalah himpunan beranggota tunggal. Penduga himpunan ini mempunyai presisi terbaik yang mungkin, tetapi untuk distribusi kontinu biasanya memiliki tingkat kepercayaan 0. Di antara kedua ekstrem itu, kita berharap menemukan penduga himpunan yang sekaligus mempunyai tingkat kepercayaan dan presisi tinggi.</p>''',
    75: r'''\t<p class="math">Misalkan \(C_i(\bs{X})\) adalah himpunan kepercayaan bertingkat \(1 - \alpha_i\) bagi \(\theta\), untuk \(i \in \{1, 2, \ldots, k\}\). Jika \(\alpha = \alpha_1 + \alpha_2 + \cdots + \alpha_k \lt 1\), maka \(C_1(\bs{X}) \cap C_2(\bs{X}) \cap \cdots \cap C_k(\bs{X})\) adalah himpunan kepercayaan konservatif bertingkat \(1 - \alpha\) bagi \(\theta\).</p>''',
    77: r'''\t\t<summary>Rincian:</summary>''',
    78: r'''\t\t<p>Hasil ini mengikuti <a href="../prob/Probability.html#boo">pertidaksamaan Bonferroni</a>.</p>''',
    82: r'''<h4 id="o006.random.interval.introduction.section.real-valued-parameters">Parameter Bernilai Riil</h4>''',
    84: r'''<p>Dalam banyak kasus, kita ingin menduga parameter bernilai riil \(\lambda = \lambda(\theta)\) yang nilainya berada dalam interval \((a, b)\), dengan \(a, \, b \in \R\) dan \(a \lt b\). Tentu saja, mungkin \(a = -\infty\) atau \(b = \infty\). Dalam konteks ini, himpunan kepercayaan sering berbentuk''',
    86: r'''dengan \(L(\bs{X})\) dan \(U(\bs{X})\) sebagai statistik bernilai riil. Dalam hal ini, \((L(\bs{X}), U(\bs{X}))\) disebut <dfn>interval kepercayaan</dfn> bagi \(\lambda\). Jika \(L(\bs{X})\) dan \(U(\bs{X})\) keduanya acak, interval tersebut sering disebut <dfn>dua sisi</dfn>. Dalam kasus khusus \(U(\bs{X}) = b\), \(L(\bs{X})\) disebut <dfn>batas bawah kepercayaan</dfn> bagi \(\lambda\). Dalam kasus khusus \(L(\bs{X}) = a\), \(U(\bs{X})\) disebut <dfn>batas atas kepercayaan</dfn> bagi \(\lambda\).</p>''',
    88: r'''<div class="unit" id="o006.random.interval.introduction.unit-03">''',
    89: r'''\t<p class="math">Misalkan \(L(\bs{X})\) adalah batas bawah kepercayaan bertingkat \(1 - \alpha\) bagi \(\lambda\), dan \(U(\bs{X})\) adalah batas atas kepercayaan bertingkat \(1 - \beta\) bagi \(\lambda\). Jika \(\alpha + \beta \lt 1\), maka \((L(\bs{X}), U(\bs{X}))\) adalah interval kepercayaan konservatif bertingkat \(1 - (\alpha + \beta)\) bagi \(\lambda\).</p>''',
    91: r'''\t\t<summary>Rincian:</summary>''',
    92: r'''\t\t<p>Hasil ini langsung mengikuti <a href="#int" class="ref"></a>.</p>''',
    96: r'''<h4 id="piv">Variabel Pivot</h4>''',
    98: r'''<p>Membangun himpunan kepercayaan bagi parameter \(\theta\) mungkin tampak sangat sulit. Namun, dalam banyak kasus khusus yang penting, himpunan kepercayaan dapat dibangun dengan mudah dari variabel acak tertentu yang dikenal sebagai <em>variabel pivot</em>.</p>''',
    100: r'''<div class="unit" id="o006.random.interval.introduction.unit-04">''',
    101: r'''\t<p class="dfn">Misalkan \(V\) adalah fungsi dari \(S \times \Theta\) ke suatu himpunan \(T\). Variabel acak \(V(\bs{X}, \theta)\) adalah <dfn>variabel pivot</dfn> bagi \(\theta\) jika distribusinya tidak bergantung pada \(\theta\). Secara khusus, \(\P[V(\bs{X}, \theta) \in B]\) konstan terhadap \(\theta \in \Theta\) untuk setiap himpunan terukur \(B \subseteq T\).</p>''',
    104: r'''<p>Gagasan dasarnya adalah menggabungkan \(\bs{X}\) dan \(\theta\) secara aljabar sedemikian rupa sehingga ketergantungan distribusi variabel acak hasil \(V(\bs{X}, \theta)\) pada \(\theta\) dapat <em>dihilangkan</em>. Jika distribusi variabel pivot diketahui, maka untuk suatu \(\alpha\) kita dapat mencari \(B \subseteq T\), yang tidak bergantung pada \(\theta\), sedemikian sehingga \( \P_\theta\left[V(\bs{X}, \theta) \in B\right] = 1 - \alpha \). Dengan demikian, himpunan kepercayaan bertingkat \(1 - \alpha\) bagi parameter tersebut diberikan oleh \( C(\bs{X}) = \{ \theta \in \Theta: V(\bs{X}, \theta) \in B \} \).</p>''',
    107: r'''\t<figcaption>Himpunan kepercayaan yang dibangun dari variabel pivot</figcaption>''',
    108: r'''\t<img src="PivotVariable.png" alt="Pemetaan variabel pivot dari ruang data dan parameter ke ruang hasil">''',
    111: r'''<p>Sekarang misalkan variabel pivot \(V(\bs{X}, \theta)\) bernilai riil dan, demi kesederhanaan, mempunyai <a href="../dist/Continuous.html">distribusi kontinu</a>. Untuk \(p \in (0, 1)\), misalkan \(v(p)\) menyatakan <a href="../dist/CDF.html#qnt">kuantil</a> berorde \(p\) dari variabel pivot \(V(\bs{X}, \theta)\). Berdasarkan definisi variabel pivot, \(v(p)\) tidak bergantung pada \(\theta\).</p>''',
    114: r'''\t<p class="math">Untuk setiap \(p \in (0, 1)\), sebuah himpunan kepercayaan bertingkat \(1 - \alpha\) bagi \(\theta\) adalah''',
    117: r'''\t\t<summary>Rincian:</summary>''',
    118: r'''\t\t<p>Menurut definisi, peluang kejadian tersebut adalah \((1 - p \alpha) - (\alpha - p \alpha) = 1 - \alpha\).</p>''',
    122: r'''<p>Himpunan kepercayaan di atas menempatkan peluang \((1 - p) \alpha\) di ekor kiri dan \(p \alpha\) di ekor kanan distribusi variabel pivot \(V(\bs{X}, \theta)\). Kasus khusus \(p = \frac{1}{2}\) disebut kasus <dfn>berekor sama</dfn> dan merupakan kasus yang paling umum.</p>''',
    125: r'''\t<figcaption>Distribusi variabel pivot dengan \((1 - p) \alpha\) di ekor kiri dan \(p \alpha\) di ekor kanan.</figcaption>''',
    126: r'''\t<img src="Tails-id.svg" alt="Kurva distribusi variabel pivot V dari X dan theta dengan peluang tengah satu dikurangi alfa serta peluang pada kedua ekor">''',
    129: r'''<div class="unit" id="o006.random.interval.introduction.unit-06">''',
    130: r'''\t<p class="math">Untuk \(p\) tetap, himpunan kepercayaan <a href="#set" class="ref"></a> mengecil ketika \(\alpha\) membesar, sehingga membesar ketika \(1 - \alpha\) membesar, dalam arti relasi himpunan bagian.</p>''',
    133: r'''<p>Untuk himpunan kepercayaan <a href="#set" class="ref"></a>, secara alami kita ingin memilih \(p\) yang meminimalkan ukuran himpunan dalam suatu pengertian. Namun, masalah ini sering sulit. Interval berekor sama, yang bersesuaian dengan \(p = \frac{1}{2}\), merupakan kasus yang paling sering digunakan dan kadang-kadang—tetapi tidak selalu—merupakan pilihan optimal. Variabel pivot jauh dari unik; tantangannya adalah menemukan variabel pivot yang distribusinya diketahui dan menghasilkan batas parameter yang rapat, yaitu presisi tinggi.</p>''',
    135: r'''<div class="unit" id="o006.random.interval.introduction.unit-07">''',
    136: r'''\t<p class="math">Misalkan \(V(\bs{X}, \theta)\) adalah variabel pivot bagi \(\theta\). Jika \(g\) adalah fungsi yang didefinisikan pada daerah nilai \(V\) dan \(g\) tidak melibatkan parameter tak diketahui, maka \(U = g[V(\bs{X}, \theta)]\) juga merupakan variabel pivot bagi \(\theta\).</p>''',
    139: r'''<h3 id="o006.random.interval.introduction.section.examples-special-cases">Contoh dan Kasus Khusus</h3>''',
    141: r'''<h4 id="o006.random.interval.introduction.section.location-scale-families">Keluarga Lokasi-Skala</h4>''',
    143: r'''<p>Untuk <a href="../special/LocationScale.html">keluarga lokasi-skala</a>, variabel pivot dapat ditemukan dengan mudah. Misalkan \(Z\) adalah variabel acak bernilai riil dengan distribusi kontinu yang mempunyai fungsi kepadatan probabilitas \(g\) dan tidak mengandung parameter tak diketahui. Misalkan \(X = \mu + \sigma Z\), dengan \(\mu \in \R\) dan \(\sigma \in (0, \infty)\) sebagai parameter. Ingat bahwa fungsi kepadatan probabilitas \(X\) diberikan oleh''',
    145: r'''dan keluarga distribusi yang bersesuaian disebut <dfn>keluarga lokasi-skala</dfn> yang terkait dengan distribusi \(Z\); \(\mu\) adalah <dfn>parameter lokasi</dfn> dan \(\sigma\) adalah <dfn>parameter skala</dfn>. Secara umum, kedua parameter ini dianggap tak diketahui.</p>''',
    147: r'''<p>Sekarang misalkan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) adalah sampel acak berukuran \(n\) dari distribusi \(X\); inilah vektor hasil yang dapat diamati. Untuk setiap \(i\), misalkan''',
    150: r'''<div class="unit" id="o006.random.interval.introduction.unit-08">''',
    151: r'''\t<p class="math">Vektor acak \(\bs{Z} = (Z_1, Z_2, \ldots, Z_n)\) adalah sampel acak berukuran \(n\) dari distribusi \(Z\).</p>''',
    154: r'''<p>Khususnya, \(\bs{Z}\) adalah variabel pivot bagi \((\mu, \sigma)\), sebab \(\bs{Z}\) merupakan fungsi dari \(\bs{X}\), \(\mu\), dan \(\sigma\), sedangkan distribusi \(\bs{Z}\) tidak bergantung pada \(\mu\) maupun \(\sigma\). Karena itu, setiap fungsi dari \(\bs{Z}\) juga merupakan variabel pivot bagi \((\mu, \sigma)\), asalkan fungsi tersebut tidak melibatkan parameternya. Tentu saja, sebagian variabel pivot ini jauh lebih berguna daripada yang lain untuk menduga \(\mu\) dan \(\sigma\). Dalam latihan berikut, kita mengkaji dua variabel pivot yang umum dan penting.</p>''',
    156: r'''<div class="unit" id="o006.random.interval.introduction.unit-09">''',
    157: r'''\t<p class="math">Misalkan \(M(\bs{X})\) dan \(M(\bs{Z})\) masing-masing menyatakan <a href="../sample/Mean.html">rata-rata sampel</a> dari \(\bs{X}\) dan \(\bs{Z}\). Maka \(M(\bs{Z})\) adalah variabel pivot bagi \((\mu, \sigma)\), sebab''',
    162: r'''\t<p class="math">Misalkan \(m\) menyatakan fungsi kuantil variabel pivot \(M(\bs{Z})\). Untuk setiap \(p \in (0, 1)\), sebuah himpunan kepercayaan bertingkat \(1 - \alpha\) bagi \((\mu, \sigma)\) adalah''',
    166: r'''<div class="unit" id="o006.random.interval.introduction.unit-11">''',
    167: r'''\t<p class="math">Himpunan kepercayaan yang dibangun dalam <a href="#lcs" class="ref"></a> berbentuk <q>kerucut</q> dalam ruang parameter \((\mu, \sigma)\), dengan titik puncak \((M(\bs{X}), 0)\). Jika kuantil penyebut tidak nol, garis-garis batasnya mempunyai kemiringan \(-1 / m(1 - p \alpha)\) dan \(-1 / m(\alpha - p \alpha)\), seperti pada grafik di bawah; bila suatu kuantil bernilai nol, batas yang bersesuaian adalah garis vertikal. Perhatikan bahwa kedua kemiringan dapat sama-sama negatif atau sama-sama positif.</p>''',
    171: r'''\t<figcaption>Himpunan kepercayaan bagi \((\mu, \sigma)\) yang dibangun dari \(M\)</figcaption>''',
    172: r'''\t<img src="ZSet.png" alt="Kerucut himpunan kepercayaan dalam ruang parameter mu-sigma">''',
    175: r'''<p>Himpunan kepercayaan yang tak terbatas jelas bukan hasil yang baik, tetapi hal itu mungkin tidak mengejutkan: kita menduga dua parameter riil dengan satu variabel pivot bernilai riil. Namun, jika \(\sigma\) diketahui, himpunan tersebut menentukan sebuah <em>interval kepercayaan</em> bagi \(\mu\). Secara geometris, interval kepercayaan itu adalah penampang horizontal pada nilai \(\sigma\) yang diketahui.</p>''',
    177: r'''<div class="unit" id="o006.random.interval.introduction.unit-12">''',
    178: r'''\t<p class="math">Dua himpunan kepercayaan satu sisi bertingkat \(1 - \alpha\) bagi \((\mu, \sigma)\) adalah:</p>''',
    184: r'''\t\t<summary>Rincian:</summary>''',
    185: r'''\t\t<p>Untuk himpunan dalam <a href="#lcs" class="ref"></a>, kedua batas mengikuti langsung, masing-masing, dari \(\P[M(\bs{Z}) \lt m(1 - \alpha)] = 1 - \alpha\) dan \(\P[M(\bs{Z}) \gt m(\alpha)] = 1 - \alpha\). Argumen ini tidak memerlukan asumsi kuantil ujung yang tak dinyatakan.</p>''',
    189: r'''<p>Jika \(\sigma\) diketahui, bagian (a) memberikan batas bawah kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\), sedangkan bagian (b) memberikan batas atas kepercayaan bertingkat \(1 - \alpha\) bagi \(\mu\).</p>''',
    191: r'''<div class="unit" id="o006.random.interval.introduction.unit-13">''',
    192: r'''\t<p class="math">Untuk ukuran sampel sekurang-kurangnya 2, misalkan \(S(\bs{X})\) dan \(S(\bs{Z})\) masing-masing menyatakan <a href="../sample/Variance.html">simpangan baku sampel</a> dari \(\bs{X}\) dan \(\bs{Z}\). Maka \(S(\bs{Z})\) adalah variabel pivot bagi \((\mu, \sigma)\), sekaligus variabel pivot bagi \(\sigma\), sebab''',
    196: r'''<div class="unit" id="o006.random.interval.introduction.unit-14">''',
    197: r'''\t<p class="math">Misalkan \(s\) menyatakan fungsi kuantil \(S(\bs{Z})\). Untuk setiap \(\alpha \in (0, 1)\) dan \(p \in (0, 1)\), sebuah himpunan kepercayaan bertingkat \(1 - \alpha\) bagi \((\mu, \sigma)\) adalah''',
    201: r'''<p>Himpunan kepercayaan ini tidak memberikan informasi tentang \(\mu\), sebab variabel acak di atas merupakan variabel pivot bagi \(\sigma\) saja. Himpunan tersebut juga dapat dipandang sebagai <em>interval</em> kepercayaan terbatas bagi \(\sigma\).</p>''',
    204: r'''\t<figcaption>Himpunan kepercayaan bagi \((\mu, \sigma)\) yang dibangun dari \(S\)</figcaption>''',
    205: r'''\t<img src="VSet.png" alt="Pita horizontal himpunan kepercayaan bagi parameter skala sigma">''',
    208: r'''<div class="unit" id="o006.random.interval.introduction.unit-15">''',
    209: r'''\t<p class="math">Dua himpunan kepercayaan satu sisi bertingkat \(1 - \alpha\) bagi \((\mu, \sigma)\) adalah:</p>''',
    215: r'''\t\t<summary>Rincian:</summary>''',
    216: r'''\t\t<p>Kedua batas mengikuti langsung, masing-masing, dari \(\P[S(\bs{Z}) \lt s(1 - \alpha)] = 1 - \alpha\) dan \(\P[S(\bs{Z}) \gt s(\alpha)] = 1 - \alpha\). Argumen ini tidak memerlukan asumsi kuantil ujung yang tak dinyatakan.</p>''',
    220: r'''<p>Himpunan pada bagian (a) memberikan batas bawah kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma\), sedangkan himpunan pada bagian (b) memberikan batas atas kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma\).</p>''',
    222: r'''<p>Kita dapat mengiriskan himpunan kepercayaan yang bersesuaian dengan kedua variabel pivot untuk menghasilkan himpunan kepercayaan yang konservatif dan terbatas.</p>''',
    224: r'''<div class="unit" id="o006.random.interval.introduction.unit-16">''',
    225: r'''\t<p class="math">Jika \(\alpha, \; \beta, \; p, \; q \in (0, 1)\) dan \(\alpha + \beta \lt 1\), maka \(Z_{\alpha, p}(\bs{X}) \cap V_{\beta, q}(\bs{X})\) adalah himpunan kepercayaan konservatif bertingkat \(1 - (\alpha + \beta)\) bagi \((\mu, \sigma)\).</p>''',
    227: r'''\t\t<summary>Rincian:</summary>''',
    228: r'''\t\t<p>Hasil ini mengikuti <a href="#int" class="ref"></a>.</p>''',
    233: r'''\t<figcaption>Himpunan kepercayaan terbatas bagi \((\mu, \sigma)\) yang dibangun dari \((M, S)\)</figcaption>''',
    234: r'''\t<img src="ZVSet.png" alt="Irisan terbatas dua himpunan kepercayaan dalam ruang mu-sigma">''',
    237: r'''<p>Keluarga lokasi-skala terpenting adalah keluarga <a href="../special/Normal.html">distribusi normal</a>. Masalah <a href="Normal.html">pendugaan pada model normal</a> dibahas pada bagian berikutnya. Dalam sisa bagian ini, kita mengkaji satu keluarga skala penting lainnya.</p>''',
    239: r'''<h4 id="o006.random.interval.introduction.section.exponential-distribution">Distribusi Eksponensial</h4>''',
    241: r'''<p>Ingat bahwa <a href="../special/Gamma.html">distribusi eksponensial</a> dengan parameter skala \(\sigma \in (0, \infty)\) mempunyai fungsi kepadatan probabilitas \(f(x) = \frac{1}{\sigma} e^{-x / \sigma}, \; x \in [0, \infty)\). Distribusi ini merupakan keluarga skala yang terkait dengan distribusi eksponensial standar, yang mempunyai fungsi kepadatan probabilitas \(g(x) = e^{-x}, \; x \in [0, \infty)\). Distribusi eksponensial banyak digunakan untuk memodelkan waktu acak, seperti masa pakai dan waktu <q>kedatangan</q>, terutama dalam konteks model Poisson. Sekarang misalkan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) adalah sampel acak berukuran \(n\) dari distribusi eksponensial dengan parameter skala tak diketahui \(\sigma\). Misalkan''',
    244: r'''<div class="unit" id="o006.random.interval.introduction.unit-17">''',
    245: r'''\t<p class="math">Variabel acak \(\frac{2}{\sigma} Y\) mempunyai <a href="../special/ChiSquare.html">distribusi khi-kuadrat</a> dengan \(2 n\) derajat kebebasan, sehingga merupakan variabel pivot bagi \(\sigma\).</p>''',
    248: r'''<p>Variabel pivot ini merupakan kelipatan dari variabel \(M\) yang dibangun di atas untuk keluarga lokasi-skala umum, dengan \(\mu = 0\). Untuk \(p \in (0, 1)\) dan \(k \in (0, \infty)\), misalkan \(\chi_k^2(p)\) menyatakan <a href="../dist/CDF.html#qnt">kuantil</a> berorde \(p\) dari distribusi khi-kuadrat dengan \(k\) derajat kebebasan. Untuk nilai \(k\) dan \(p\) tertentu, \(\chi_k^2(p)\) dapat diperoleh dari <a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">aplikasi kuantil</a> atau dari sebagian besar perangkat lunak statistika.</p>''',
    250: r'''<div class="unit" id="o006.random.interval.introduction.unit-18">''',
    251: r'''\t<p class="math">Ingat bahwa</p>''',
    253: r'''\t\t<li>\(\chi_k^2(p) \to 0\) ketika \(p \downarrow 0\)</li>''',
    254: r'''\t\t<li>\(\chi_k^2(p) \to \infty\) ketika \(p \uparrow 1\)</li>''',
    258: r'''<div class="unit" id="o006.random.interval.introduction.unit-19">''',
    259: r'''\t<p class="math">Untuk setiap \(\alpha \in (0, 1)\) dan \(p \in (0, 1)\), sebuah interval kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma\) adalah''',
    263: r'''<div class="unit" id="o006.random.interval.introduction.unit-20">''',
    264: r'''\t<p class="math">Perhatikan bahwa</p>''',
    266: r'''\t\t<li>\(2 Y \big/ \chi_{2n}^2(1 - \alpha)\) adalah batas bawah kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma\).</li>''',
    267: r'''\t\t<li>\(2 Y \big/ \chi_{2n}^2(\alpha)\) adalah batas atas kepercayaan bertingkat \(1 - \alpha\) bagi \(\sigma\).</li>''',
    271: r'''<p>Di antara interval kepercayaan dua sisi yang dibangun di atas, secara alami kita memilih interval dengan panjang terkecil karena interval itu memberikan informasi terbanyak tentang parameter \(\sigma\). Namun, meminimalkan panjang sebagai fungsi \(p\) sulit secara komputasional. Interval kepercayaan dua sisi yang lazim digunakan adalah interval <dfn>berekor sama</dfn>, yang diperoleh dengan mengambil \(p = \frac{1}{2}\):''',
    274: r'''<div class="unit" id="o006.random.interval.introduction.unit-21">''',
    275: r'''\t<p class="stat">Masa pakai suatu jenis komponen, dalam jam, mengikuti distribusi eksponensial dengan parameter skala tak diketahui \(\sigma\). Sepuluh perangkat dioperasikan sampai gagal; masa pakainya adalah 592, 861, 1470, 2412, 335, 3485, 736, 758, 530, 1961.</p>''',
    277: r'''\t\t<li>Bangun interval kepercayaan dua sisi 95% bagi \(\sigma\).</li>''',
    278: r'''\t\t<li>Bangun batas bawah kepercayaan 95% bagi \(\sigma\).</li>''',
    279: r'''\t\t<li>Bangun batas atas kepercayaan 95% bagi \(\sigma\).</li>''',
    282: r'''\t\t<summary>Rincian:</summary>''',
    294: r'''\t\t<li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    296: r'''\t\t<li class="child"><a href="Normal.html" title="Pendugaan pada Model Normal">2</a></li>''',
    297: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Pendugaan pada Model Bernoulli">3</a></li>''',
    298: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Pendugaan pada Model Normal Dua Sampel">4</a></li>''',
    299: r'''\t\t<li class="child"><a href="Bayes.html" title="Pendugaan Interval Bayes">5</a></li>''',
    300: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    301: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    304: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    305: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    306: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/sample/Mean.html": "../sample/Mean.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
    "https://www.randomservices.org/random/interval/index.html": "index.html",
    "https://www.randomservices.org/random/interval/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/interval/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/interval/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/interval/Bayes.html": "Bayes.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, deskripsi gambar yang lebih informatif, dan koreksi matematis terbatas yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t</section>'''


MATH_REPAIRS_BY_INDEX = {
    28: r'''\[ \inf_{\theta \in \Theta}\P_\theta[\theta \in C(\bs{X})] \]''',
    48: r'''\(\P_\theta[\theta \in C(\bs{X})] \ge 1 - \alpha\)''',
    129: r'''\(V(\bs{X}, \theta)\)''',
    202: r'''\(\P[M(\bs{Z}) \lt m(1 - \alpha)] = 1 - \alpha\)''',
    203: r'''\(\P[M(\bs{Z}) \gt m(\alpha)] = 1 - \alpha\)''',
    233: r'''\(\P[S(\bs{Z}) \lt s(1 - \alpha)] = 1 - \alpha\)''',
    234: r'''\(\P[S(\bs{Z}) \gt s(\alpha)] = 1 - \alpha\)''',
    241: r'''\(Z_{\alpha, p}(\bs{X}) \cap V_{\beta, q}(\bs{X})\)''',
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
    if len(source_math) != 290 or len(target_math) != len(source_math):
        raise RuntimeError(f"protected-math count changed: {len(source_math)} -> {len(target_math)}")
    from collections import Counter

    def canonical_math(span: str) -> str:
        return re.sub(r"\s+", "", span)

    expected_math = [MATH_REPAIRS_BY_INDEX.get(index, span) for index, span in enumerate(source_math)]
    if Counter(map(canonical_math, target_math)) != Counter(map(canonical_math, expected_math)):
        missing = Counter(map(canonical_math, expected_math)) - Counter(map(canonical_math, target_math))
        extra = Counter(map(canonical_math, target_math)) - Counter(map(canonical_math, expected_math))
        raise RuntimeError(f"unexpected protected-math multiset delta: missing={missing}, extra={extra}")
    for index, new in MATH_REPAIRS_BY_INDEX.items():
        if index >= len(source_math) or new not in target_math:
            raise RuntimeError(f"declared math repair not realized at source span {index + 1}: {new!r}")

    for phrase in (
        'lang="en"',
        "JavaScript:openAncillary",
        ">Introduction<",
        ">Basic Theory<",
        ">Confidence Sets<",
        ">Real-Valued Parameters<",
        ">Pivot Variables<",
        ">Examples and Special Cases<",
        ">Location-Scale Families<",
        ">The Exponential Distribution<",
        ">Details:<",
        ">Apps<",
        ">Data Sets<",
        "> Biographies<",
        "confidence lower bound for \\(\\sigma\\)",
        "This results follows",
    ):
        if phrase in rendered:
            raise RuntimeError(f"unresolved reader-facing/source defect remains: {phrase}")
    required_ids = (
        "o006.random.interval.introduction.page",
        "o006.random.interval.introduction.section.basic-theory",
        "o006.random.interval.introduction.section.confidence-sets",
        "o006.random.interval.introduction.section.real-valued-parameters",
        "o006.random.interval.introduction.section.examples-special-cases",
        "o006.random.interval.introduction.section.location-scale-families",
        "o006.random.interval.introduction.section.exponential-distribution",
        "o006.random.interval.introduction.unit-01",
        "o006.random.interval.introduction.unit-21",
    )
    for stable_id in required_ids:
        if f'id="{stable_id}"' not in rendered:
            raise RuntimeError(f"missing stable id: {stable_id}")
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
