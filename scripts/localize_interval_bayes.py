#!/usr/bin/env python3
"""Create the bounded id-ID Bayesian set-estimation target."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "interval" / "Bayes.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "interval" / "Bayes.html"
SOURCE_URL = "https://www.randomservices.org/random/interval/Bayes.html"
SOURCE_SHA256 = "f89dfc9ed4b9475b2cd83b467f19cfbfa6164600f14567f4237fdae9076d1cb7"
EXPECTED_SOURCE_LINES = 250
EXPECTED_CORE_ELEMENTS = 206
EXPECTED_MATH_SPANS = 281


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Pendugaan Himpunan Bayes</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, pendugaan himpunan, pendugaan interval, pendugaan Bayes, teorema Bayes, distribusi Bernoulli, distribusi Poisson, distribusi normal, distribusi beta, distribusi Pareto">''',
    34: r'''\t\t<li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    35: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    36: r'''\t\t<li class="child"><a href="Normal.html" title="Pendugaan pada Model Normal">2</a></li>''',
    37: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Pendugaan pada Model Bernoulli">3</a></li>''',
    38: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Pendugaan pada Model Normal Dua Sampel">4</a></li>''',
    40: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    41: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    43: r'''\t<h2 id="o006.random.interval.bayes.page">5. Pendugaan Himpunan Bayes</h2>''',
    46: r'''<h3 id="the">Teori Dasar</h3>''',
    48: r'''<p>Seperti biasa, titik awal kita adalah suatu <a href="../prob/Experiments.html">eksperimen acak</a> dengan <a href="../prob/Events.html">ruang sampel</a> dan <a href="../prob/Probability.html">ukuran probabilitas</a> \(\P\) yang mendasarinya. Dalam model statistika dasar, kita mempunyai <a href="../prob/Probability.html">variabel acak</a> teramati \(\bs{X}\) yang nilainya berada dalam suatu himpunan \(S\). Secara umum, struktur \(\bs{X}\) dapat cukup rumit. Misalnya, jika eksperimennya mengambil sampel \(n\) objek dari suatu populasi dan mencatat berbagai pengukuran yang diminati, maka''',
    50: r'''dengan \(X_i\) sebagai vektor pengukuran bagi objek ke-\(i\).</p>''',
    52: r'''<p>Andaikan pula bahwa distribusi \(\bs{X}\) bergantung pada parameter \(\theta\) yang nilainya berada dalam himpunan \(T\). Parameter itu juga dapat bernilai vektor; dalam hal ini \(T \subseteq \R^k\) untuk suatu \(k \in \N_+\), dan parameternya berbentuk \(\bs{\theta} = (\theta_1, \theta_2, \ldots, \theta_k)\).</p>''',
    54: r'''<h4 id="bay">Formulasi Bayes</h4>''',
    56: r'''<p>Ingat bahwa dalam <a href="../point/Bayes.html">analisis Bayes</a>, yang dinamai menurut <a href="JavaScript:openAncillary('../biographies/Bayes.html')" class="ancillary">Thomas Bayes</a>, parameter tak diketahui \(\theta\) dimodelkan dengan variabel acak \(\Theta\) yang nilainya berada dalam \(T\). Berikut tinjauan ringkasnya:</p>''',
    58: r'''<div class="unit" id="o006.random.interval.bayes.unit-01">''',
    59: r'''\t<p class="math">Formulasi Bayes</p>''',
    61: r'''\t\t<li>Fungsi kepadatan probabilitas bersyarat vektor data \(\bs{X}\), dengan syarat \(\Theta = \theta\ \in T\), dinyatakan dengan \( f(\bs{x} \mid \theta) \) untuk \( \bs{x} \in S \).</li>''',
    62: r'''\t\t<li>Parameter acak \(\Theta\) diberi <dfn>distribusi prior</dfn> dengan fungsi kepadatan probabilitas \(h\) pada \(T\).</li>''',
    63: r'''\t\t<li>Fungsi kepadatan probabilitas gabungan \((\bs X, \Theta)\) adalah \((\bs{x}, \theta) \mapsto h(\theta) f(\bs{x} \mid \theta)\) untuk \((\bs{x}, \theta) \in S \times T \).</li>''',
    64: r'''\t\t<li>Fungsi kepadatan probabilitas tak bersyarat \(\bs{X}\) adalah fungsi \(f\) yang diberikan oleh \(f(\bs{x}) = \sum_{\theta \in T} h(\theta) f(\bs{x} \mid \theta)\) untuk \(\bs{x} \in S\) jika \(\Theta\) mempunyai <a href="../dist/Discrete.html">distribusi diskret</a>, atau oleh \(f(\bs{x}) = \int_T h(\theta) f(\bs{x} \mid \theta) \, d\theta,\) untuk \(\bs{x} \in S\) jika \(\Theta\) mempunyai <a href="../dist/Continuous.html">distribusi kontinu</a>.</li>''',
    65: r'''\t\t<li>Menurut <a href="../dist/Conditional.html">teorema Bayes</a>, untuk data dengan kepadatan marginal positif dan berhingga, <dfn>fungsi kepadatan probabilitas posterior</dfn> \(\Theta\) dengan syarat \(\bs{X} = \bs{x} \in S\) adalah''',
    70: r'''<p>Distribusi prior sering bersifat subjektif dan dipilih untuk menyatakan pengetahuan yang kita miliki mengenai parameter. Dalam beberapa kasus, distribusi posterior dapat dikenali dari bentuk fungsional \(\theta \mapsto h(\theta) f(\bs{x} \mid \theta)\) tanpa perlu benar-benar menghitung konstanta normalisasi \(f(\bs{x})\), sehingga beban komputasi berkurang secara berarti. Hal ini khususnya sering terjadi ketika kita mempunyai <dfn>keluarga parametrik konjugat</dfn> bagi distribusi \(\Theta\). Artinya, jika distribusi prior \(\Theta\) termasuk dalam keluarga tersebut, distribusi posterior \(\Theta\) dengan syarat \(\bs{X} = \bs{x} \in S\) juga termasuk dalam keluarga yang sama.</p>''',
    72: r'''<p>Kasus khusus terpenting terjadi ketika kita mempunyai variabel dasar \(X\) yang nilainya berada dalam himpunan \(R\), dan, dengan syarat \(\Theta = \theta \in T\), vektor data \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari \(X\). Artinya, dengan syarat \(\Theta = \theta \in T\), \(\bs{X}\) merupakan barisan variabel yang saling bebas dan berdistribusi identik, masing-masing dengan distribusi yang sama seperti \(X\) dengan syarat \(\Theta = \theta\). Jadi, \(S = R^n\), dan jika \(X\) mempunyai fungsi kepadatan probabilitas bersyarat \(g(x \mid \theta)\), maka''',
    75: r'''<h4 id="con">Himpunan Kredibel Bayes</h4>''',
    77: r'''<p>Misalkan kini \(C(\bs{X})\) merupakan himpunan bagian ruang parameter \(T\) yang bergantung pada variabel data \(\bs{X}\), tetapi tidak pada parameter tak diketahui mana pun.</p>''',
    80: r'''\t<p class="dfn">Salah satu definisi bagi <dfn>himpunan kredibel Bayes</dfn> bertingkat sekurang-kurangnya \(1 - \alpha\) mensyaratkan bahwa''',
    84: r'''<p>Dalam definisi <a href="#dfn1" class="ref"></a>, hanya \(\Theta\) yang acak, sehingga peluang di atas dihitung menggunakan fungsi kepadatan probabilitas posterior \(\theta \mapsto h(\theta \mid \bs{x})\). Jika distribusi posterior nonatomik dan batas himpunan dipilih secara tepat, ketaksamaan tersebut dapat menjadi kesamaan.</p>''',
    87: r'''\t<p class="dfn">Definisi alternatif mensyaratkan bahwa''',
    91: r'''<p>Dalam definisi <a href="#dfn2" class="ref"></a>, \(\bs{X}\) dan \(\Theta\) keduanya acak, sehingga peluang di atas dihitung menggunakan fungsi kepadatan probabilitas gabungan \((\bs{x}, \theta) \mapsto h(\theta) f(\bs{x} \mid \theta)\). Terlepas dari perdebatan filosofisnya, definisi <a href="#dfn1" class="ref"></a> jelas lebih mudah dari sudut pandang komputasi dan karena itu paling lazim digunakan. Bentuk “sekurang-kurangnya” juga mencakup distribusi atomik, yang mungkin tidak memiliki himpunan dengan massa tepat sebesar tingkat nominal.</p>''',
    93: r'''<p>Mari kita bandingkan pendekatan klasik dan Bayes. Dalam pendekatan klasik, parameter \(\theta\) bersifat deterministik tetapi tak diketahui. <em>Sebelum</em> data dikumpulkan, himpunan kepercayaan \(C(\bs{X})\), yang acak karena \(\bs{X}\), memuat parameter dengan peluang sekurang-kurangnya \(1 - \alpha\) pada setiap nilai parameter; kesamaan berlaku bagi prosedur dengan cakupan eksak. <em>Setelah</em> data dikumpulkan, himpunan kepercayaan terhitung \(C(\bs{x})\) memuat atau tidak memuat \(\theta\), dan biasanya kita tidak akan pernah mengetahui yang mana. Sebaliknya, dalam himpunan kredibel Bayes, parameter acak \(\Theta\) berada dalam himpunan terhitung yang deterministik \(C(\bs{x})\) dengan peluang posterior sekurang-kurangnya \(1 - \alpha\).</p>''',
    95: r'''<div class="unit" id="o006.random.interval.bayes.unit-04">''',
    96: r'''\t<p class="math">Andaikan \(\Theta\) bernilai riil, sehingga \(T \subseteq \R\). Untuk \(r \in (0, 1)\), suatu <em>interval</em> kredibel Bayes bertingkat sekurang-kurangnya \(1 - \alpha\) adalah \(\left[U_{(1 - r) \alpha}(\bs{x}), U_{1 - r \alpha}(\bs{x})\right]\), dengan \(U_p(\bs{x})\) sebagai kuantil berorde \(p\) dari distribusi posterior \(\Theta\) dengan syarat \(\bs{X} = \bs{x}\). Bagi posterior kontinu, interval ini mempunyai massa posterior tepat sebesar tingkat nominal; bagi posterior atomik, peluangnya dapat lebih besar.</p>''',
    99: r'''<p>Seperti pada bagian-bagian sebelumnya, \(r\) adalah bagian dari \(\alpha\) pada ekor kanan distribusi posterior, sedangkan \(1 - r\) adalah bagian dari \(\alpha\) pada ekor kiri. Kasus \(r = \frac{1}{2}\) memberikan interval kredibel dua sisi yang berekor sama; interval itu simetris hanya jika distribusi posteriornya simetris. Membiarkan \(r \to 0\) memberikan batas bawah kredibel, sedangkan membiarkan \(r \to 1\) memberikan batas atas kredibel.</p>''',
    101: r'''<h3 id="app">Penerapan</h3>''',
    103: r'''<h4 id="ber">Distribusi Bernoulli</h4>''',
    105: r'''<p>Andaikan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari <a href="../bernoulli/Introduction.html">distribusi Bernoulli</a> dengan parameter keberhasilan tak diketahui \(p \in (0, 1)\). Dalam istilah keandalan yang lazim, \(X_i = 1\) berarti berhasil pada percobaan ke-\(i\), sedangkan \(X_i = 0\) berarti gagal pada percobaan ke-\(i\). Distribusi ini dinamai menurut <a href="JavaScript:openAncillary('../biographies/Bernoulli.html')" class="ancillary">Jacob Bernoulli</a>. Ingat bahwa distribusi Bernoulli mempunyai fungsi kepadatan probabilitas berikut, dengan syarat \(p\):''',
    107: r'''Perhatikan bahwa banyaknya keberhasilan dalam \(n\) percobaan adalah \(Y = \sum_{i=1}^n X_i\). Dengan syarat \(p\), variabel acak \(Y\) mempunyai <a href="../bernoulli/Binomial.html">distribusi binomial</a> dengan parameter \(n\) dan \(p\).</p>''',
    109: r'''<p>Dalam pembahasan sebelumnya mengenai <a href="../point/Bayes.html#ber">pendugaan Bayes</a>, kita memodelkan parameter \(p\) dengan variabel acak \(P\) yang mempunyai <a href="../special/Beta.html">distribusi beta</a>. Keluarga distribusi ini konjugat bagi \(P\). Secara khusus, jika distribusi prior \(P\) adalah beta dengan parameter bentuk kiri \(a \gt 0\) dan parameter bentuk kanan \(b \gt 0\), maka distribusi posterior \(P\) dengan syarat \(\bs{X}\) adalah beta dengan parameter bentuk kiri \(a + Y\) dan parameter bentuk kanan \(b + (n - Y)\); parameter kiri bertambah sebesar banyaknya keberhasilan, sedangkan parameter kanan bertambah sebesar banyaknya kegagalan. Jadi, interval kredibel Bayes bertingkat \(1 - \alpha\) bagi \(p\) adalah \(\left[U_{\alpha/2}(y), U_{1-\alpha/2}(y)\right]\), dengan \(U_r(y)\) sebagai kuantil berorde \(r\) dari distribusi beta posterior. Dalam kasus khusus \(a = b = 1\), distribusi prior seragam pada \((0, 1)\). Prior datar ini merupakan pilihan sederhana dalam parameterisasi tersebut, tetapi tidak secara harfiah menyatakan ketiadaan pengetahuan tentang \(p\) dan tidak invarian terhadap perubahan parameter.</p>''',
    112: r'''\t<p class="math">Andaikan kita mempunyai sebuah koin dengan probabilitas tak diketahui \(p\) untuk menghasilkan gambar kepala, dan kita memberi \(p\) prior seragam sebagai pilihan datar sederhana bagi \(p\). Koin itu kemudian dilempar 50 kali dan menghasilkan 30 gambar kepala.</p>''',
    114: r'''\t\t<li>Tentukan distribusi posterior \(p\) berdasarkan data tersebut.</li>''',
    115: r'''\t\t<li>Bangun interval kredibel Bayes 95%.</li>''',
    116: r'''\t\t<li>Bangun interval kepercayaan Wald klasik bertingkat 95%.</li>''',
    119: r'''\t\t<summary>Rincian:</summary>''',
    121: r'''\t\t\t<li>Beta dengan parameter bentuk kiri 31 dan parameter bentuk kanan 21.</li>''',
    128: r'''<h4 id="poi">Distribusi Poisson</h4>''',
    130: r'''<p>Andaikan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari <a href="../poisson/Poisson.html">distribusi Poisson</a> dengan parameter \(\lambda \in (0, \infty)\). Ingat bahwa distribusi Poisson sering digunakan untuk memodelkan banyaknya <q>titik acak</q> dalam suatu daerah waktu atau ruang, khususnya dalam konteks <a href="../poisson/index.html">proses Poisson</a>. Distribusi ini dinamai menurut <a href="JavaScript:openAncillary('../biographies/Poisson.html')" class="ancillary">Simeon Poisson</a> dan, dengan syarat \(\lambda\), mempunyai fungsi kepadatan probabilitas''',
    132: r'''Seperti biasa, jumlah nilai sampel dinyatakan dengan \(Y = \sum_{i=1}^n X_i\). Dengan syarat \(\lambda\), variabel acak \(Y\) juga mempunyai distribusi Poisson, tetapi dengan parameter \(n \lambda\).</p>''',
    134: r'''<p>Dalam pembahasan sebelumnya mengenai <a href="../point/Bayes.html#poi">pendugaan Bayes</a>, kita memodelkan \(\lambda\) dengan variabel acak \(\Lambda\) yang mempunyai <a href="../special/Gamma.html">distribusi gamma</a>. Keluarga distribusi ini konjugat bagi \(\Lambda\). Secara khusus, jika distribusi prior \(\Lambda\) adalah gamma dengan parameter bentuk \(k \gt 0\) dan parameter laju \(r \gt 0\), sehingga parameter skalanya \(1 / r\), maka distribusi posterior \(\Lambda\) dengan syarat \(\bs{X}\) adalah gamma dengan parameter bentuk \(k + Y\) dan parameter laju \(r + n\). Jadi, interval kredibel Bayes bertingkat \(1 - \alpha\) bagi \(\lambda\) adalah \(\left[U_{\alpha/2}(y), U_{1-\alpha/2}(y)\right]\), dengan \(U_p(y)\) sebagai kuantil berorde \(p\) dari distribusi gamma posterior.</p>''',
    137: r'''\t<p class="stat">Tinjau <a href="JavaScript:openAncillary('../data/Alpha.html')" class="ancillary">data emisi partikel alfa</a>, yang kita yakini berasal dari distribusi Poisson dengan parameter tak diketahui \(\lambda\). Andaikan bahwa, <em>sebelum data diamati</em>, kita memperkirakan \(\lambda\) sekitar 5 sehingga kita memberi \(\lambda\) distribusi prior gamma dengan parameter bentuk \(5\) dan parameter laju 1. Jadi, rata-ratanya 5 dan simpangan bakunya \(\sqrt{5} = 2.236\).</p>''',
    139: r'''\t\t<li>Tentukan distribusi posterior \(\lambda\) berdasarkan data tersebut.</li>''',
    140: r'''\t\t<li>Bangun interval kredibel Bayes 95%.</li>''',
    141: r'''\t\t<li>Bangun interval kepercayaan \(t\) klasik bertingkat 95%.</li>''',
    144: r'''\t\t<summary>Rincian:</summary>''',
    146: r'''\t\t\t<li>Gamma dengan parameter bentuk 10104 dan parameter laju 1208.</li>''',
    153: r'''<h4 id="nor">Distribusi Normal</h4>''',
    155: r'''<p>Andaikan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari <a href="../special/Normal.html">distribusi normal</a> dengan rata-rata tak diketahui \(\mu \in \R\) dan varians diketahui \(\sigma^2 \in (0, \infty)\). Distribusi normal memegang peran yang sangat penting dalam statistika, antara lain karena <a href="../sample/CLT.html">teorema limit pusat</a>. Distribusi ini banyak digunakan untuk memodelkan besaran fisik yang dipengaruhi banyak galat acak kecil. Ingat bahwa fungsi kepadatan probabilitas normal, dengan syarat \(\mu\), adalah''',
    157: r'''Jumlah nilai sampel dinyatakan dengan \(Y = \sum_{i=1}^n X_i\). Ingat bahwa, dengan syarat \(\mu\), \(Y\) juga mempunyai distribusi normal, tetapi dengan rata-rata \(n \mu\) dan varians \(n \sigma^2\).</p>''',
    159: r'''<p>Dalam pembahasan sebelumnya mengenai <a href="../point/Bayes.html#nor">pendugaan Bayes</a>, kita memodelkan \(\mu\) dengan variabel acak \(\Psi\) yang juga mempunyai distribusi normal. Keluarga ini konjugat bagi \(\Psi\) ketika \(\sigma\) diketahui. Secara khusus, jika distribusi prior \(\Psi\) adalah normal dengan rata-rata \(a \in \R\) dan simpangan baku \(b \in (0, \infty)\), maka distribusi posterior \(\Psi\) dengan syarat \(\bs{X}\) juga normal, dengan''',
    161: r'''Jadi, interval kredibel Bayes bertingkat \(1 - \alpha\) bagi \(\mu\) adalah \(\left[U_{\alpha/2}(y), U_{1-\alpha/2}(y)\right]\), dengan \(U_p(y)\) sebagai kuantil berorde \(p\) dari distribusi normal posterior. Kasus khusus yang menarik terjadi ketika \(b = \sigma\), sehingga simpangan baku distribusi prior \(\mu\) sama dengan simpangan baku distribusi asal sampel. Dalam kasus ini, rata-rata posterior adalah \((Y + a) \big/ (n + 1)\), sedangkan varians posterior adalah \(\sigma^2 \big/ (n + 1)\).</p>''',
    164: r'''\t<p class="math">Panjang suatu komponen hasil pemesinan seharusnya 10 sentimeter, tetapi akibat ketidaksempurnaan proses produksi, panjang sebenarnya merupakan variabel acak berdistribusi normal dengan rata-rata \(\mu\) dan varians \(\sigma^2\). Varians tersebut disebabkan faktor bawaan proses yang cukup stabil sepanjang waktu. Dari data historis diketahui bahwa \(\sigma = 0.3\). Sebaliknya, \(\mu\) dapat diatur dengan menyesuaikan berbagai parameter proses sehingga cukup sering berubah menjadi nilai tak diketahui. Karena itu, berikan \(\mu\) distribusi prior normal dengan rata-rata 10 dan simpangan baku 0.3. Sampel 100 komponen mempunyai rata-rata 10.2.</p>''',
    166: r'''\t\t<li>Tentukan distribusi posterior \(\mu\) berdasarkan data tersebut.</li>''',
    167: r'''\t\t<li>Bangun interval kredibel Bayes 95%.</li>''',
    168: r'''\t\t<li>Bangun interval kepercayaan \(z\) klasik bertingkat 95%.</li>''',
    171: r'''\t\t<summary>Rincian:</summary>''',
    173: r'''\t\t\t<li>Normal dengan rata-rata 10.198 dan simpangan baku 0.0299.</li>''',
    180: r'''<h4 id="bet">Distribusi Beta</h4>''',
    182: r'''<p>Andaikan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari <a href="../special/Beta.html">distribusi beta</a> dengan parameter bentuk kiri tak diketahui \(a \in (0, \infty)\) dan parameter bentuk kanan \(b = 1\). Distribusi beta banyak digunakan untuk memodelkan proporsi dan probabilitas acak serta variabel lain yang nilainya berada dalam interval terbatas. Ingat bahwa fungsi kepadatan probabilitasnya, dengan syarat \(a\), adalah''',
    184: r'''Hasil kali nilai sampel dinyatakan dengan \(W = X_1 X_2 \cdots X_n\).</p>''',
    186: r'''<p>Dalam pembahasan sebelumnya mengenai <a href="../point/Bayes.html#bet">pendugaan Bayes</a>, kita memodelkan \(a\) dengan variabel acak \(A\) yang mempunyai <a href="../special/Gamma.html">distribusi gamma</a>. Keluarga distribusi ini konjugat bagi \(a\). Secara khusus, jika distribusi prior \(A\) adalah gamma dengan parameter bentuk \(k \gt 0\) dan parameter laju \(r \gt 0\), maka distribusi posterior \(A\) dengan syarat \(\bs{X}\) juga gamma, dengan parameter bentuk \(k + n\) dan parameter laju \(r - \ln(W)\). Jadi, interval kredibel Bayes bertingkat \(1 - \alpha\) bagi \(A\) adalah \(\left[U_{\alpha/2}(w), U_{1-\alpha/2}(w)\right]\), dengan \(U_p(w)\) sebagai kuantil berorde \(p\) dari distribusi gamma posterior. Dalam kasus khusus \(k = 1\), distribusi prior \(a\) adalah eksponensial dengan parameter laju \(r\).</p>''',
    189: r'''\t<p class="math">Andaikan hambatan suatu komponen listrik, dalam ohm, mempunyai distribusi beta dengan parameter bentuk kiri tak diketahui \(a\) dan parameter bentuk kanan \(b = 1\). Kita memperkirakan \(a\) sekitar 10 sehingga kita memberi \(a\) distribusi prior gamma dengan parameter bentuk 10 dan parameter laju 1. Kita mengambil sampel 20 komponen dan memperoleh data berikut. Nilai dicatat hingga dua tempat desimal; karena itu, 1.00 menyatakan pengukuran yang dibulatkan, bukan pengamatan tepat pada titik ujung model kontinu.''',
    192: r'''\t\t<li>Tentukan distribusi posterior \(a\).</li>''',
    193: r'''\t\t<li>Bangun interval kredibel Bayes 95% bagi \(a\).</li>''',
    196: r'''\t\t<summary>Rincian:</summary>''',
    198: r'''\t\t\t<li>Gamma dengan parameter bentuk 30 dan parameter laju 2.424.</li>''',
    204: r'''<h4 id="par">Distribusi Pareto</h4>''',
    206: r'''<p>Andaikan \(\bs{X} = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n\) dari <a href="../special/Pareto.html">distribusi Pareto</a> dengan parameter bentuk \(a \in (0, \infty)\) dan parameter skala \(b = 1\). Distribusi Pareto digunakan untuk memodelkan variabel finansial tertentu dan variabel lain yang berdistribusi berekor berat, serta dinamai menurut <a href="JavaScript:openAncillary('../biographies/Pareto.html')" class="ancillary">Vilfredo Pareto</a>. Ingat bahwa fungsi kepadatan probabilitasnya, dengan syarat \(a\), adalah''',
    208: r'''Hasil kali nilai sampel dinyatakan dengan \(W = X_1 X_2 \cdots X_n\).</p>''',
    210: r'''<p>Dalam pembahasan sebelumnya mengenai <a href="../point/Bayes.html#par">pendugaan Bayes</a>, kita memodelkan \(a\) dengan variabel acak \(A\) yang mempunyai <a href="../special/Gamma.html">distribusi gamma</a>. Keluarga distribusi ini konjugat bagi \(A\). Secara khusus, jika distribusi prior \(A\) adalah gamma dengan parameter bentuk \(k \gt 0\) dan parameter laju \(r \gt 0\), maka distribusi posterior \(A\) dengan syarat \(\bs{X}\) juga gamma, dengan parameter bentuk \(k + n\) dan parameter laju \(r + \ln(W)\). Jadi, interval kredibel Bayes bertingkat \(1 - \alpha\) bagi \(a\) adalah \(\left[U_{\alpha/2}(w), U_{1-\alpha/2}(w)\right]\), dengan \(U_p(w)\) sebagai kuantil berorde \(p\) dari distribusi gamma posterior. Dalam kasus khusus \(k = 1\), distribusi prior \(a\) adalah eksponensial dengan parameter laju \(r\).</p>''',
    213: r'''\t<p class="math">Andaikan suatu variabel finansial mempunyai distribusi Pareto dengan parameter bentuk tak diketahui \(a\) dan parameter skala \(b = 1\). Kita memperkirakan \(a\) sekitar 4 sehingga kita memberi \(a\) distribusi prior gamma dengan parameter bentuk 4 dan parameter laju 1. Sampel acak berukuran 20 dari variabel tersebut menghasilkan data''',
    216: r'''\t\t<li>Tentukan distribusi posterior \(a\).</li>''',
    217: r'''\t\t<li>Bangun interval kredibel Bayes 95% bagi \(a\).</li>''',
    220: r'''\t\t<summary>Rincian:</summary>''',
    222: r'''\t\t\t<li>Gamma dengan parameter bentuk 24 dan parameter laju 5.223.</li>''',
    231: r'''\t\t<li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    232: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    233: r'''\t\t<li class="child"><a href="Normal.html" title="Pendugaan pada Model Normal">2</a></li>''',
    234: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Pendugaan pada Model Bernoulli">3</a></li>''',
    235: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Pendugaan pada Model Normal Dua Sampel">4</a></li>''',
    237: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    238: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    241: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    242: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    243: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/interval/index.html": "index.html",
    "https://www.randomservices.org/random/interval/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/interval/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/interval/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/point/Bayes.html": "../point/Bayes.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/hypothesis/index.html": "../hypothesis/index.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, koreksi matematis terbatas, dan kualifikasi rigor yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t</section>'''


MATH_REPAIRS_BY_INDEX: dict[int, tuple[str, str]] = {
    71: (
        r'''\[ \P\left[\Theta \in C(\bs{x}) \mid \bs{X} = \bs{x}\right] = 1 - \alpha \]''',
        r'''\[ \P\left[\Theta \in C(\bs{x}) \mid \bs{X} = \bs{x}\right] \ge 1 - \alpha \]''',
    ),
    74: (
        r'''\[ \P\left[\Theta \in C(\bs{X})\right] = 1 - \alpha \]''',
        r'''\[ \P\left[\Theta \in C(\bs{X})\right] \ge 1 - \alpha \]''',
    ),
    140: (
        r'''\([0.461, 0.724\)''',
        r'''\([0.461, 0.724]\)''',
    ),
    146: (
        r'''\[ g(x \mid \theta) = e^{-\lambda} \frac{\lambda^x}{x!}, \quad x \in \N \]''',
        r'''\[ g(x \mid \lambda) = e^{-\lambda} \frac{\lambda^x}{x!}, \quad x \in \N \]''',
    ),
    175: (
        r'''\((8.324, 8.410)\)''',
        r'''\((8.201, 8.533)\)''',
    ),
    176: (
        r'''\(\bs{x} = (X_1, X_2, \ldots, X_n)\)''',
        r'''\(\bs{X} = (X_1, X_2, \ldots, X_n)\)''',
    ),
    181: (
        r'''\[ g(x \mid \mu) = \frac{1}{\sqrt{2 \pi} \sigma} \exp\left[-\left(\frac{x - \mu}{\sigma}\right)^2 \right], \quad x \in \R \]''',
        r'''\[ g(x \mid \mu) = \frac{1}{\sqrt{2 \pi} \sigma} \exp\left[-\frac{1}{2}\left(\frac{x - \mu}{\sigma}\right)^2 \right], \quad x \in \R \]''',
    ),
    196: (
        r'''\[\E(\mu \mid \bs{X}) = \frac{Y b^2 + a \sigma^2}{\sigma^2 + n b^2}, \quad \var(\mu \mid \bs{X}) = \frac{\sigma^2 b^2}{\sigma^2 + n b^2}\]''',
        r'''\[\E(\Psi \mid \bs{X}) = \frac{Y b^2 + a \sigma^2}{\sigma^2 + n b^2}, \quad \var(\Psi \mid \bs{X}) = \frac{\sigma^2 b^2}{\sigma^2 + n b^2}\]''',
    ),
}


class TagSequenceParser(HTMLParser):
    """Collect the ordered HTML element topology without depending on bs4."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)


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


def apply_occurrence_bound_math_repairs(value: str) -> str:
    index = -1

    def repair(match: re.Match[str]) -> str:
        nonlocal index
        index += 1
        span = match.group(0)
        if index not in MATH_REPAIRS_BY_INDEX:
            return span
        old, new = MATH_REPAIRS_BY_INDEX[index]
        if span == old:
            return new
        if span == new:
            return span
        raise RuntimeError(
            f"math repair target mismatch at span {index + 1}: {span!r}"
        )

    repaired = re.sub(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]", repair, value)
    if index + 1 != EXPECTED_MATH_SPANS:
        raise RuntimeError(f"math-repair traversal count changed: {index + 1}")
    return repaired


def tag_sequence(value: str) -> list[str]:
    parser = TagSequenceParser()
    parser.feed(value)
    parser.close()
    return parser.tags


def hrefs(value: str) -> list[str]:
    return re.findall(r'\bhref="([^"]+)"', value)


def ids(value: str) -> list[str]:
    return re.findall(r'\bid="([^"]+)"', value)


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    source_text = source_bytes.decode("utf-8")
    lines = source_text.splitlines(keepends=True)
    if len(lines) != EXPECTED_SOURCE_LINES:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")

    source_tags = tag_sequence(source_text)
    if len(source_tags) != EXPECTED_CORE_ELEMENTS:
        raise RuntimeError(f"unexpected authority element count: {len(source_tags)}")
    source_math = math_spans(source_text)
    if len(source_math) != EXPECTED_MATH_SPANS:
        raise RuntimeError(f"unexpected authority math count: {len(source_math)}")
    for index, (old, _new) in MATH_REPAIRS_BY_INDEX.items():
        if source_math[index] != old:
            raise RuntimeError(
                f"math repair source mismatch at span {index + 1}: "
                f"{source_math[index]!r} != {old!r}"
            )

    for line_number, replacement in sorted(LINE_REPLACEMENTS.items()):
        replace_exact_line(lines, line_number, replacement)
    core = "".join(lines)
    core = re.sub(
        r'href="([^"]+)"',
        lambda match: f'href="{convert_href(match.group(1))}"',
        core,
    )
    core = apply_occurrence_bound_math_repairs(core)

    target_tags = tag_sequence(core)
    if target_tags != source_tags:
        raise RuntimeError(
            f"core topology changed: {len(source_tags)} -> {len(target_tags)} elements"
        )
    target_math = math_spans(core)
    if len(target_math) != EXPECTED_MATH_SPANS:
        raise RuntimeError(
            f"protected-math count changed: {len(source_math)} -> {len(target_math)}"
        )
    expected_math = [
        MATH_REPAIRS_BY_INDEX[index][1] if index in MATH_REPAIRS_BY_INDEX else span
        for index, span in enumerate(source_math)
    ]
    if Counter(map(canonical_math, target_math)) != Counter(map(canonical_math, expected_math)):
        missing = Counter(map(canonical_math, expected_math)) - Counter(
            map(canonical_math, target_math)
        )
        extra = Counter(map(canonical_math, target_math)) - Counter(
            map(canonical_math, expected_math)
        )
        raise RuntimeError(
            f"unexpected protected-math multiset delta: missing={missing}, extra={extra}"
        )
    for index, (_old, new) in MATH_REPAIRS_BY_INDEX.items():
        if new not in target_math:
            raise RuntimeError(
                f"declared math repair not realized at source span {index + 1}: {new!r}"
            )

    source_ids = ids(source_text)
    target_ids = ids(core)
    added_ids = {
        "o006.random.interval.bayes.page",
        "o006.random.interval.bayes.unit-01",
        "o006.random.interval.bayes.unit-04",
    }
    if len(source_ids) != 17 or len(target_ids) != 20:
        raise RuntimeError(f"unexpected ID census: {len(source_ids)} -> {len(target_ids)}")
    if set(target_ids) - set(source_ids) != added_ids:
        raise RuntimeError(
            f"unexpected added IDs: {sorted(set(target_ids) - set(source_ids))}"
        )
    if not set(source_ids).issubset(target_ids):
        raise RuntimeError("one or more native source IDs were not preserved")
    if len(target_ids) != len(set(target_ids)):
        duplicates = sorted(value for value, count in Counter(target_ids).items() if count > 1)
        raise RuntimeError(f"duplicate IDs: {duplicates}")

    if len(re.findall(r'<div class="unit"(?: id="[^"]+")?>', core)) != 9:
        raise RuntimeError("unit-block count changed")
    if core.count("<details>") != 5 or core.count("</details>") != 5:
        raise RuntimeError("details topology changed")
    if "<figure" in core or "<table" in core:
        raise RuntimeError("unexpected page-specific figure/table introduced")

    source_hrefs = hrefs(source_text)
    core_hrefs = hrefs(core)
    if len(source_hrefs) != 51 or len(set(source_hrefs)) != 40:
        raise RuntimeError("authority href census changed")
    if len(core_hrefs) != len(source_hrefs) or len(set(core_hrefs)) != 40:
        raise RuntimeError("target href census changed")
    changed = [(before, after) for before, after in zip(source_hrefs, core_hrefs) if before != after]
    unchanged = [before for before, after in zip(source_hrefs, core_hrefs) if before == after]
    if len(changed) != 28 or len({before for before, _after in changed}) != 23:
        raise RuntimeError(f"unexpected href rewrite census: {len(changed)} occurrences")
    if len(unchanged) != 23 or len(set(unchanged)) != 17:
        raise RuntimeError(f"unexpected unchanged href census: {len(unchanged)} occurrences")
    source_srcs = re.findall(r'\bsrc="([^"]+)"', source_text)
    target_srcs = re.findall(r'\bsrc="([^"]+)"', core)
    if Counter(source_srcs) != Counter(target_srcs):
        raise RuntimeError("shared src inventory changed")
    if "JavaScript:openAncillary" in core:
        raise RuntimeError("JavaScript ancillary link remains")
    for value in core_hrefs:
        if not (value.startswith(("https://", "#", "../")) or re.match(r"^[A-Za-z][^:]*\.html", value)):
            raise RuntimeError(f"unexpected href scheme/path: {value}")

    unresolved = (
        'lang="en"',
        ">Basic Theory<",
        ">The Bayesian Formulation<",
        ">Confidence Sets<",
        ">Applications<",
        ">The Bernoulli Distribution<",
        ">The Poisson Distribution<",
        ">The Normal Distribution<",
        ">The Beta Distribution<",
        ">The Pareto Distribution<",
        ">Details:<",
        ">Apps<",
        ">Data Sets<",
        "> Biographies<",
        "Suppose that",
        "Find the posterior",
        "Construct the",
        "prior distribution",
        "posterior distribution",
        "Bayesian confidence",
        "defintion",
        "disstributions",
        "number of failure",
        "in the contest of",
        "we showed modeled",
        "is a normally distributed",
        "standard deviation 0.03",
        r"g(x \mid \theta) = e^{-\lambda}",
        r"\E(\mu \mid \bs{X})",
        r"\([0.461, 0.724\)",
        r"\((8.324, 8.410)\)",
    )
    for phrase in unresolved:
        if phrase in core:
            raise RuntimeError(f"unresolved reader-facing/source defect remains: {phrase}")
    required = (
        "<title>Pendugaan Himpunan Bayes</title>",
        "himpunan kredibel Bayes",
        "interval kredibel Bayes",
        "berekor sama",
        "kepadatan marginal positif dan berhingga",
        "peluang sekurang-kurangnya",
        "tidak secara harfiah menyatakan ketiadaan pengetahuan",
        "pengukuran yang dibulatkan",
        "https://www.randomservices.org/random/data/Alpha.html",
        'title="Perluas Rincian"',
        'title="Ciutkan Rincian"',
        "<summary>Rincian:</summary>",
    )
    for phrase in required:
        if phrase not in core:
            raise RuntimeError(f"required reader-facing guard missing: {phrase}")

    marker = "</footer>"
    if core.count(marker) != 1:
        raise RuntimeError("footer marker count changed")
    rendered = core.replace(
        marker,
        materialize_indentation(EDITION_NOTICE) + "\n" + marker,
        1,
    )
    if rendered.count('data-o006-edition-notice="v1"') != 1:
        raise RuntimeError("edition notice insertion failed")
    if math_spans(rendered) != target_math:
        raise RuntimeError("edition notice unexpectedly changed protected math")

    output = rendered.encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(output)
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: "
        f"{len(output)} bytes / sha256 {hashlib.sha256(output).hexdigest()} / "
        f"{len(target_tags)} core elements / {len(target_math)} math spans / "
        f"{len(target_ids)} core IDs / {len(changed)} href rewrites"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
