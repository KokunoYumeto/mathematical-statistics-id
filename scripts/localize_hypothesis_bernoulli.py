#!/usr/bin/env python3
"""Create the bounded id-ID Bernoulli hypothesis-testing target."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "hypothesis" / "Bernoulli.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "hypothesis" / "Bernoulli.html"
SOURCE_URL = "https://www.randomservices.org/random/hypothesis/Bernoulli.html"
SOURCE_SHA256 = "a3691cdf98c1b182bf434ec94479cfea344e1e555c5928ee74555ff09ce0e603"
EXPECTED_SOURCE_LINES = 333
EXPECTED_ELEMENTS = 267
EXPECTED_MATH_SPANS = 233
EXPECTED_UNITS = 24
EXPECTED_ANONYMOUS_UNITS = 1
EXPECTED_DETAILS = 13
EXPECTED_CORE_LINKS = 50
EXPECTED_SOURCE_IDS = 34


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''	<title>Pengujian pada Model Bernoulli</title>''',
    9: r'''	<meta name="keywords" content="probabilitas, statistika, pengujian hipotesis, distribusi Bernoulli, proporsi, uji binomial, uji normal, uji tanda">''',
    32: r'''		<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    33: r'''		<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    34: r'''		<li class="child"><a href="Normal.html" title="Pengujian pada Model Normal">2</a></li>''',
    36: r'''		<li class="child"><a href="BivariateNormal.html" title="Pengujian pada Model Normal Dua Sampel">4</a></li>''',
    37: r'''		<li class="child"><a href="Likelihood.html" title="Uji Rasio Kemungkinan">5</a></li>''',
    38: r'''		<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    39: r'''		<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    40: r'''		<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    42: r'''	<h2 id="o006.random.hypothesis.bernoulli.page">3. Pengujian pada Model Bernoulli</h2>''',
    45: r'''<h3 id="bas">Uji Dasar</h3>''',
    47: r'''<h4 id="pre">Pendahuluan Dasar</h4>''',
    49: r'''<p>Andaikan s{X} = (X_1, X_2, \ldots, X_n) merupakan sampel acak dari <a href="../bernoulli/Introduction.html">distribusi Bernoulli</a> dengan parameter tak diketahui \(p \in (0, 1)\). Dengan demikian, variabel-variabel tersebut <a href="../prob/Independence.html">saling independen</a> dan masing-masing mengambil nilai 1 dan 0 dengan probabilitas \(p\) dan \(1-p\). Dalam bahasa keandalan, 1 lazim menyatakan <dfn>sukses</dfn> dan 0 menyatakan <dfn>gagal</dfn>, tetapi keduanya hanyalah istilah umum.</p>''',
    51: r'''<div class="unit" id="o006.random.hypothesis.bernoulli.unit-01">''',
    52: r'''	<p class="math">Model ini sering muncul dalam salah satu konteks berikut:</p>''',
    54: r'''		<li>Terdapat suatu <em>kejadian</em> yang menjadi perhatian dalam eksperimen dasar, dengan probabilitas tak diketahui \(p\). Kita mengulang eksperimen itu \(n\) kali dan mendefinisikan \(X_i=1\) jika dan hanya jika kejadian tersebut terjadi pada pengulangan ke-\(i\).</li>''',
    55: r'''		<li>Kita mempunyai populasi objek dengan beberapa jenis; \(p\) adalah proporsi tak diketahui dari jenis tertentu yang menjadi perhatian. Kita memilih \(n\) objek secara acak dari populasi dan menetapkan \(X_i=1\) jika dan hanya jika objek ke-\(i\) termasuk jenis tersebut.</li>''',
    59: r'''<p>Pada bagian (b), jika pengambilan sampel dilakukan <em>dengan</em> pengembalian, variabel-variabel itu benar-benar membentuk sampel acak dari distribusi Bernoulli. Jika dilakukan <em>tanpa</em> pengembalian, variabel-variabelnya dependen, tetapi model Bernoulli masih dapat berlaku secara hampiran apabila ukuran populasi sangat besar dibandingkan ukuran sampel \(n\). Uraian lebih lanjut terdapat pada pembahasan <a href="../urn/Introduction.html">metode pengambilan sampel</a> dalam bab <a href="../urn/index.html">model pengambilan sampel hingga</a>. Pada bagian ini kita membangun uji hipotesis bagi parameter \(p\). Ruang parameternya ialah interval \((0,1)\), dan semua hipotesis mendefinisikan himpunan bagian dari ruang tersebut. Bagian ini sejajar dengan <a href="../interval/Bernoulli.html">pendugaan pada model Bernoulli</a> dalam bab <a href="../interval/index.html">pendugaan himpunan</a>.</p>''',
    61: r'''<h4 id="bin">Uji Binomial</h4>''',
    63: r'''<p>Ingat bahwa banyaknya sukses \(Y = \sum_{i=1}^n X_i\) mempunyai <a href="../bernoulli/Binomial.html">distribusi binomial</a> dengan parameter \(n\) dan \(p\), serta fungsi massa probabilitas''',
    65: r'''Ingat pula bahwa nilai harapannya ialah \(\E(Y)=np\) dan variansnya \(\var(Y)=np(1-p)\). Selain itu, \(Y\) merupakan statistik <a href="../point/Sufficient.html#ber">cukup</a> bagi \(p\), sehingga menjadi calon alami untuk statistik uji mengenai \(p\). Untuk \(\alpha \in (0,1)\), misalkan \(b_{n,p}(\alpha)\) menyatakan <a href="../dist/CDF.html#qnt">kuantil</a> berorde \(\alpha\) dari distribusi binomial berparameter \(n\) dan \(p\). Karena distribusi binomial diskret, hanya tingkat ekor tertentu yang dapat dicapai tepat. Dalam pembahasan selanjutnya, \(p_0 \in (0,1)\) adalah nilai dugaan bagi \(p\).</p>''',
    68: r'''	<p class="math">Untuk setiap \(\alpha \in (0,1)\), uji berikut mempunyai tingkat signifikansi yang mendekati \(\alpha\):</p>''',
    70: r'''		<li>Tolak \(H_0: p=p_0\) melawan \(H_1: p\ne p_0\) jika dan hanya jika \(Y \le b_{n,p_0}(\alpha/2)\) atau \(Y \ge b_{n,p_0}(1-\alpha/2)\).</li>''',
    71: r'''		<li>Tolak \(H_0: p\ge p_0\) melawan \(H_1: p\lt p_0\) jika dan hanya jika \(Y \le b_{n,p_0}(\alpha)\).</li>''',
    72: r'''		<li>Tolak \(H_0: p\le p_0\) melawan \(H_1: p\gt p_0\) jika dan hanya jika \(Y \ge b_{n,p_0}(1-\alpha)\).</li>''',
    75: r'''		<summary>Rincian:</summary>''',
    76: r'''		<p>Pada bagian (a), \(H_0\) merupakan hipotesis sederhana dan, di bawah \(H_0\), statistik uji \(Y\) berdistribusi binomial dengan parameter \(n\) dan \(p_0\). Karena kisi binomial bersifat diskret, peluang menolak \(H_0\) secara keliru hanya mendekati \(\alpha\) untuk batas kuantil yang dinyatakan; ukuran sebenarnya harus dihitung dari peluang ekor binomial. Pada bagian (b) dan (c), \(H_0\) menentukan suatu rentang nilai \(p\), dan peluang galat tipe I terbesar dicapai pada batas \(p=p_0\).</p>''',
    80: r'''<p>Uji pada (a) adalah uji dua sisi simetris yang baku, dengan kira-kira \(\alpha/2\) pada masing-masing ekor distribusi binomial di bawah \(H_0\). Uji pada (b) berekor kiri dan uji pada (c) berekor kanan. Secara lebih umum, \(\alpha\) dapat dibagi antara ekor kiri dan kanan dengan cara lain.</p>''',
    83: r'''	<p class="math">Untuk \(\alpha,\,r\in(0,1)\), uji berikut mempunyai tingkat signifikansi yang mendekati \(\alpha\): tolak \(H_0:p=p_0\) melawan \(H_1:p\ne p_0\) jika dan hanya jika \(Y\le b_{n,p_0}(\alpha-r\alpha)\) atau \(Y\ge b_{n,p_0}(1-r\alpha)\).</p>''',
    85: r'''		<li>\(r=\frac{1}{2}\) menghasilkan uji dua sisi simetris yang baku.</li>''',
    86: r'''		<li>\(r\downarrow0\) menghasilkan uji berekor kiri.</li>''',
    87: r'''		<li>\(r\uparrow1\) menghasilkan uji berekor kanan.</li>''',
    90: r'''		<summary>Rincian:</summary>''',
    91: r'''		<p>Sekali lagi, \(H_0\) merupakan hipotesis sederhana dan, di bawah \(H_0\), statistik uji \(Y\) berdistribusi binomial dengan parameter \(n\) dan \(p_0\). Pembagian peluang ekor mengikuti fungsi kuantil, tetapi karena distribusinya diskret, tingkat aktual pada umumnya hanya mendekati \(\alpha\). Bagian (a)–(c) mengikuti sifat-sifat fungsi kuantil.</p>''',
    95: r'''<h4 id="nor">Uji Normal Hampiran</h4>''',
    97: r'''<p>Jika \(n\) besar dan jumlah harapan sukses maupun gagal di bawah nilai nol cukup besar, distribusi \(Y\) <a href="../bernoulli/Binomial.html#nor">mendekati distribusi normal</a> menurut <a href="../sample/CLT.html">teorema limit pusat</a>. Karena itu kita dapat membangun <a href="Normal.html">uji normal</a> hampiran.</p>''',
    100: r'''	<p class="math">Andaikan ukuran sampel \(n\) besar. Untuk nilai dugaan \(p_0\in(0,1)\), definisikan statistik uji''',
    103: r'''		<li>Jika \(p=p_0\), maka \(Z\) mempunyai distribusi normal standar secara hampiran.</li>''',
    104: r'''		<li>Jika \(p\ne p_0\), maka \(Z\) mempunyai distribusi normal secara hampiran dengan rata-rata \(\sqrt{n}\frac{p-p_0}{\sqrt{p_0(1-p_0)}}\) dan varians \(\frac{p(1-p)}{p_0(1-p_0)}\).</li>''',
    107: r'''		<summary>Rincian:</summary>''',
    109: r'''			<li>Hasil ini mengikuti teorema De Moivre–Laplace, yakni kasus khusus teorema limit pusat untuk distribusi binomial. Perhatikan bahwa \(Z\) adalah skor baku yang berkaitan dengan \(Y\).</li>''',
    110: r'''			<li>Dengan aljabar sederhana, kita dapat menulis''',
    112: r'''			Faktor kedua dalam suku kedua kembali merupakan skor baku bagi \(Y\), sehingga mempunyai distribusi normal standar secara hampiran ketika kondisi aproksimasi binomial-normal terpenuhi. Hasilnya kemudian mengikuti sifat linear dasar distribusi normal.</li>''',
    117: r'''<p>Seperti biasa, untuk \(\alpha\in(0,1)\), misalkan \(z(\alpha)\) menyatakan kuantil berorde \(\alpha\) dari distribusi normal standar. Untuk nilai \(\alpha\) tertentu, \(z(\alpha)\) dapat diperoleh dari <a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">aplikasi kuantil</a> atau sebagian besar perangkat lunak statistika. Menurut simetri, \(z(1-\alpha)=-z(\alpha)\).</p>''',
    120: r'''	<p class="math">Untuk setiap \(\alpha\in(0,1)\), uji berikut mempunyai tingkat signifikansi hampiran \(\alpha\):</p>''',
    122: r'''		<li>Tolak \(H_0:p=p_0\) melawan \(H_1:p\ne p_0\) jika dan hanya jika \(Z\lt-z(1-\alpha/2)\) atau \(Z\gt z(1-\alpha/2)\).</li>''',
    123: r'''		<li>Tolak \(H_0:p\ge p_0\) melawan \(H_1:p\lt p_0\) jika dan hanya jika \(Z\lt-z(1-\alpha)\).</li>''',
    124: r'''		<li>Tolak \(H_0:p\le p_0\) melawan \(H_1:p\gt p_0\) jika dan hanya jika \(Z\gt z(1-\alpha)\).</li>''',
    127: r'''		<summary>Rincian:</summary>''',
    128: r'''		<p>Pada bagian (a), \(H_0\) adalah hipotesis sederhana dan di bawah \(H_0\), statistik uji \(Z\) berdistribusi normal standar secara hampiran. Karena itu peluang menolak \(H_0\) secara keliru mendekati \(\alpha\). Pada bagian (b) dan (c), \(H_0\) menentukan suatu rentang nilai \(p\), dan distribusi hampiran \(Z\) dijelaskan pada <a href="#nor1" class="ref"></a>. Peluang galat tipe I terbesar mendekati \(\alpha\) pada batas \(p=p_0\).</p>''',
    132: r'''<p>Uji pada (a) adalah uji dua sisi simetris, dengan \(\alpha/2\) pada masing-masing ekor distribusi \(Z\) di bawah \(H_0\). Uji pada (b) berekor kiri dan uji pada (c) berekor kanan. Uji dua sisi yang lebih umum dapat dibangun dengan membagi \(\alpha\) secara lain antara kedua ekor distribusi normal standar.</p>''',
    135: r'''	<p class="math">Untuk setiap \(\alpha,\,r\in(0,1)\), uji berikut mempunyai tingkat signifikansi hampiran \(\alpha\): tolak \(H_0:p=p_0\) melawan \(H_1:p\ne p_0\) jika dan hanya jika \(Z\lt z(\alpha-r\alpha)\) atau \(Z\gt z(1-r\alpha)\).</p>''',
    137: r'''		<li>\(r=\frac{1}{2}\) menghasilkan uji dua sisi simetris yang baku.</li>''',
    138: r'''		<li>\(r\downarrow0\) menghasilkan uji berekor kiri.</li>''',
    139: r'''		<li>\(r\uparrow1\) menghasilkan uji berekor kanan.</li>''',
    142: r'''		<summary>Rincian:</summary>''',
    143: r'''		<p>Di bawah hipotesis sederhana \(H_0\), statistik uji \(Z\) mempunyai distribusi normal standar secara hampiran. Karena itu, menurut definisi kuantil, peluang menolak \(H_0\) secara keliru mendekati \(\alpha\).</p>''',
    147: r'''<h4 id="sim">Latihan Simulasi</h4>''',
    150: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, tetapkan \(H_0:p=p_0\), ukuran sampel 10, tingkat signifikansi 0,1, dan \(p_0=0,5\). Untuk setiap \(p\in\{0.1,0.2,\ldots,0.9\}\), jalankan eksperimen 1.000 kali, catat frekuensi relatif penolakan hipotesis nol, lalu gambarkan fungsi kuasa empiris.</p>''',
    154: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, ulangi latihan sebelumnya dengan ukuran sampel 20.</p>''',
    158: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, tetapkan \(H_0:p\le p_0\), ukuran sampel 15, tingkat signifikansi 0,05, dan \(p_0=0,3\). Untuk setiap \(p\in\{0.1,0.2,\ldots,0.9\}\), jalankan eksperimen 1.000 kali, catat frekuensi relatif penolakan hipotesis nol, lalu gambarkan fungsi kuasa empiris.</p>''',
    162: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, ulangi latihan sebelumnya dengan ukuran sampel 30.</p>''',
    166: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, tetapkan \(H_0:p\ge p_0\), ukuran sampel 20, tingkat signifikansi 0,01, dan \(p_0=0,6\). Untuk setiap \(p\in\{0.1,0.2,\ldots,0.9\}\), jalankan eksperimen 1.000 kali, catat frekuensi relatif penolakan hipotesis nol, lalu gambarkan fungsi kuasa empiris.</p>''',
    170: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, ulangi latihan sebelumnya dengan ukuran sampel 50.</p>''',
    173: r'''<h4 id="com">Latihan Komputasi</h4>''',
    176: r'''	<p class="math">Dalam jajak pendapat terhadap 1.000 pemilih terdaftar di suatu distrik, 427 orang memilih calon X. Pada tingkat 0,1, apakah bukti cukup untuk menyimpulkan bahwa lebih dari 40% pemilih terdaftar memilih X?</p>''',
    178: r'''		<summary>Rincian:</summary>''',
    179: r'''		<p>Statistik uji 1,743 dan nilai kritis 1,282. Tolak \(H_0\).</p>''',
    184: r'''	<p class="math">Sebuah koin dilempar 500 kali dan menghasilkan 302 sisi kepala. Pada tingkat 0,05, ujilah apakah koin tersebut tidak seimbang.</p>''',
    186: r'''		<summary>Rincian:</summary>''',
    187: r'''		<p>Statistik uji 4,651 dan nilai kritis \(\pm1.961\). Tolak \(H_0\); data memberikan bukti yang sangat kuat bahwa probabilitas kepala bukan 0,5.</p>''',
    192: r'''	<p class="math">Sampel 400 cip memori dari suatu lini produksi diuji dan 32 di antaranya cacat. Pada tingkat 0,05, ujilah apakah proporsi cip cacat kurang dari 0,1.</p>''',
    194: r'''		<summary>Rincian:</summary>''',
    195: r'''		<p>Statistik uji \(-1.333\) dan nilai kritis \(-1.645\). Gagal menolak \(H_0\).</p>''',
    200: r'''	<p class="math">Obat baru diberikan kepada 50 pasien dan efektif dalam 42 kasus. Pada tingkat 0,1, ujilah apakah tingkat keberhasilan obat tersebut lebih besar dari 0,8.</p>''',
    202: r'''		<summary>Rincian:</summary>''',
    203: r'''		<p>Statistik uji 0,707 dan nilai kritis 1,282. Gagal menolak \(H_0\).</p>''',
    208: r'''	<p class="stat">Dengan <a href="JavaScript:openAncillary('../data/MM.html')" class="ancillary">data M&amp;M</a>, ujilah hipotesis alternatif berikut pada tingkat signifikansi 0,1:</p>''',
    210: r'''		<li>Proporsi M&amp;M merah berbeda dari \(\frac{1}{6}\).</li>''',
    211: r'''		<li>Proporsi M&amp;M hijau kurang dari \(\frac{1}{6}\).</li>''',
    212: r'''		<li>Proporsi M&amp;M kuning lebih besar dari \(\frac{1}{6}\).</li>''',
    215: r'''		<summary>Rincian:</summary>''',
    217: r'''			<li>Statistik uji 0,162 dan nilai kritis \(\pm1.645\). Gagal menolak \(H_0\).</li>''',
    218: r'''			<li>Statistik uji \(-4.117\) dan nilai kritis \(-1.282\). Tolak \(H_0\).</li>''',
    219: r'''			<li>Statistik uji 8,266 dan nilai kritis 1,282. Tolak \(H_0\).</li>''',
    224: r'''<h3 id="sgn">Uji Tanda</h3>''',
    226: r'''<h4 id="der">Penurunan</h4>''',
    228: r'''<p>Andaikan kini kita mempunyai <a href="../prob/Experiments.html">eksperimen acak</a> dasar dengan <a href="../prob/Probability.html">variabel acak bernilai real</a> \(U\) yang menjadi perhatian. Kita mengasumsikan bahwa \(U\) mempunyai <a href="../dist/Continuous.html">distribusi kontinu</a> dengan dukungan pada suatu interval \(S\subseteq\R\), dan bahwa fungsi distribusinya meningkat ketat di sekitar kuantil yang dibandingkan sehingga kuantil tersebut unik. Misalkan \(m\) menyatakan <a href="../dist/CDF.html#qnt">kuantil</a> berorde tertentu \(p_0\in(0,1)\) bagi distribusi \(U\). Dengan demikian,''',
    230: r'''Secara umum, \(m\) tidak diketahui meskipun \(p_0\) ditentukan, sebab distribusi \(U\) tidak diketahui. Kita ingin membangun uji hipotesis bagi \(m\). Untuk nilai uji tertentu \(m_0\), misalkan''',
    232: r'''Nilai \(p\) tidak diketahui meskipun \(m_0\) ditentukan, sekali lagi karena distribusi \(U\) tidak diketahui.</p>''',
    235: r'''	<p class="math">Hubungan</p>''',
    237: r'''		<li>\(m=m_0\) jika dan hanya jika \(p=p_0\).</li>''',
    238: r'''		<li>\(m\lt m_0\) jika dan hanya jika \(p\gt p_0\).</li>''',
    239: r'''		<li>\(m\gt m_0\) jika dan hanya jika \(p\lt p_0\).</li>''',
    242: r'''		<summary>Rincian:</summary>''',
    243: r'''		<p>Hasil-hasil tersebut mengikuti dari kontinuitas dan peningkatan ketat fungsi distribusi pada rentang perbandingan. Dukungan yang berupa interval dan kontinuitas saja tidak cukup jika fungsi distribusi mempunyai bagian datar; dalam kasus itu kuantil harus didefinisikan dan hipotesis ditangani dengan lebih hati-hati.</p>''',
    247: r'''<p>Seperti biasa, kita mengulang eksperimen dasar \(n\) kali untuk menghasilkan <a href="../sample/Introduction.html">sampel acak</a> \(\bs{U}=(U_1,U_2,\ldots,U_n)\) berukuran \(n\) dari distribusi \(U\). Misalkan \(X_i=\bs{1}(U_i\le m_0)\) menjadi variabel indikator kejadian \(\{U_i\le m_0\}\), untuk \(i\in\{1,2,\ldots,n\}\).</p>''',
    250: r'''	<p class="math">Perhatikan bahwa \(\bs{X}=(X_1,X_2,\ldots,X_n)\) adalah statistik—fungsi teramati dari vektor data \(\bs{U}\)—dan merupakan sampel acak berukuran \(n\) dari distribusi Bernoulli dengan parameter \(p\).</p>''',
    253: r'''<p>Dari teorema <a href="#der1" class="ref"></a> dan <a href="#der2" class="ref"></a>, pengujian terhadap kuantil tak diketahui \(m\) dapat diubah menjadi pengujian parameter Bernoulli \(p\), sehingga uji-uji di atas berlaku. Prosedur ini disebut <dfn>uji tanda</dfn> karena pada dasarnya hanya tanda \(U_i-m_0\) yang dicatat. Prosedur ini juga merupakan <dfn>uji nonparametrik</dfn>: selain asumsi sampel acak, kontinuitas, dan keunikan kuantil yang dinyatakan, distribusi \(U\) tidak perlu termasuk keluarga parametrik tertentu.</p>''',
    255: r'''<p>Kasus terpenting adalah \(p_0=\frac{1}{2}\), yakni uji tanda untuk median. Jika distribusi \(U\) simetris terhadap pusatnya dan nilai harapan ada, median, pusat simetri, dan rata-rata berimpit; dalam kondisi ini uji tanda untuk median juga menguji rata-rata. Simetri saja tidak menjamin nilai harapan ada.</p>''',
    257: r'''<h4 id="ssm">Latihan Simulasi</h4>''',
    260: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/SignTest.html')" class="ancillary">eksperimen uji tanda</a>, tetapkan distribusi sampling normal dengan rata-rata 0 dan simpangan baku 2, ukuran sampel 10, dan tingkat signifikansi 0,1. Untuk masing-masing dari 9 nilai \(m_0\), jalankan simulasi 1.000 kali.</p>''',
    262: r'''		<li>Ketika \(m=m_0\), berikan dugaan empiris tingkat signifikansi uji dan bandingkan dengan 0,1.</li>''',
    263: r'''		<li>Untuk kasus lainnya, berikan dugaan empiris kuasa uji.</li>''',
    268: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/SignTest.html')" class="ancillary">eksperimen uji tanda</a>, tetapkan distribusi sampling seragam pada interval \([0,5]\), ukuran sampel 20, dan tingkat signifikansi 0,05. Untuk masing-masing dari 9 nilai \(m_0\), jalankan simulasi 1.000 kali.</p>''',
    270: r'''		<li>Ketika \(m=m_0\), berikan dugaan empiris tingkat signifikansi uji dan bandingkan dengan 0,05.</li>''',
    271: r'''		<li>Untuk kasus lainnya, berikan dugaan empiris kuasa uji.</li>''',
    276: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/SignTest.html')" class="ancillary">eksperimen uji tanda</a>, tetapkan distribusi sampling gamma dengan parameter bentuk 2 dan parameter skala 1, ukuran sampel 30, dan tingkat signifikansi 0,025. Untuk masing-masing dari 9 nilai \(m_0\), jalankan simulasi 1.000 kali.</p>''',
    278: r'''		<li>Ketika \(m=m_0\), berikan dugaan empiris tingkat signifikansi uji dan bandingkan dengan 0,025.</li>''',
    279: r'''		<li>Untuk kasus lainnya, berikan dugaan empiris kuasa uji.</li>''',
    283: r'''<h4 id="exe">Latihan Komputasi</h4>''',
    286: r'''	<p class="stat">Dengan <a href="JavaScript:openAncillary('../data/MM.html')" class="ancillary">data M&amp;M</a>, ujilah apakah median berat melebihi 47,9 gram pada tingkat 0,1.</p>''',
    288: r'''		<summary>Rincian:</summary>''',
    289: r'''		<p>Dengan statistik \(Y=\sum_i \mathbf{1}(U_i\le47{,}9)\), statistik uji adalah −3,286 dan nilai kritis berekor kiri −1,282. Tolak \(H_0\).</p>''',
    294: r'''	<p class="stat">Dengan <a href="JavaScript:openAncillary('../data/Iris.html')" class="ancillary">data iris Fisher</a>, lakukan pengujian berikut pada tingkat 0,1:</p>''',
    296: r'''		<li>Median panjang mahkota iris Setosa berbeda dari 15 mm.</li>''',
    297: r'''		<li>Median panjang mahkota iris Virginica kurang dari 52 mm.</li>''',
    298: r'''		<li>Median panjang mahkota iris Versicolor kurang dari 42 mm.</li>''',
    301: r'''		<summary>Rincian:</summary>''',
    303: r'''			<li>Statistik uji 3,394 dan nilai kritis \(\pm1.645\). Tolak \(H_0\).</li>''',
    304: r'''			<li>Statistik uji \(1.980\) dan nilai kritis \(1.282\). Tolak \(H_0\).</li>''',
    305: r'''			<li>Statistik uji \(0.566\) dan nilai kritis \(1.282\). Gagal menolak \(H_0\).</li>''',
    313: r'''		<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    314: r'''		<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    315: r'''		<li class="child"><a href="Normal.html" title="Pengujian pada Model Normal">2</a></li>''',
    317: r'''		<li class="child"><a href="BivariateNormal.html" title="Pengujian pada Model Normal Dua Sampel">4</a></li>''',
    318: r'''		<li class="child"><a href="Likelihood.html" title="Uji Rasio Kemungkinan">5</a></li>''',
    319: r'''		<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    320: r'''		<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    321: r'''		<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    324: r'''		<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    325: r'''		<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    326: r'''		<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


# These overrides preserve the authority's occurrence-level protected-math
# sequence even where the Indonesian prose removes English repetition.
LINE_REPLACEMENTS.update({
    49: r'''<p>Andaikan \(\bs{X}=(X_1,X_2,\ldots,X_n)\) merupakan sampel acak dari <a href="../bernoulli/Introduction.html">distribusi Bernoulli</a> dengan parameter tak diketahui \(p\in(0,1)\). Dengan demikian, variabel-variabel tersebut <a href="../prob/Independence.html">saling independen</a> dan masing-masing mengambil nilai 1 dan 0 dengan probabilitas \(p\) dan \(1-p\). Dalam bahasa keandalan, 1 lazim menyatakan <dfn>sukses</dfn> dan 0 menyatakan <dfn>gagal</dfn>, tetapi keduanya hanyalah istilah umum.</p>''',
    59: r'''<p>Pada bagian (b), jika pengambilan sampel dilakukan <em>dengan</em> pengembalian, variabel-variabel itu benar-benar membentuk sampel acak dari distribusi Bernoulli. Jika dilakukan <em>tanpa</em> pengembalian, variabel-variabelnya dependen, tetapi model Bernoulli masih dapat berlaku secara hampiran apabila ukuran populasi sangat besar dibandingkan ukuran sampel \(n\). Uraian lebih lanjut terdapat pada pembahasan <a href="../urn/Introduction.html">metode pengambilan sampel</a> dalam bab <a href="../urn/index.html">model pengambilan sampel hingga</a>. Pada bagian ini kita membangun uji hipotesis bagi parameter \(p\). Ruang parameter bagi \(p\) ialah interval \((0,1)\), dan semua hipotesis mendefinisikan himpunan bagian dari ruang tersebut. Bagian ini sejajar dengan <a href="../interval/Bernoulli.html">pendugaan pada model Bernoulli</a> dalam bab <a href="../interval/index.html">pendugaan himpunan</a>.</p>''',
    76: r'''		<p>Pada bagian (a), \(H_0\) merupakan hipotesis sederhana dan, di bawah \(H_0\), statistik uji \(Y\) berdistribusi binomial dengan parameter \(n\) dan \(p_0\). Jika \(H_0\) benar, tingkat nominal \(\alpha\) hanya mendekati peluang menolak \(H_0\) secara keliru untuk batas kuantil yang dinyatakan; karena kisi binomial diskret, ukuran sebenarnya harus dihitung dari peluang ekor. Pada bagian (b) dan (c), \(H_0\) menentukan suatu rentang nilai \(p\). Jika \(H_0\) benar, peluang galat tipe I terbesar mendekati \(\alpha\) pada batas \(p=p_0\).</p>''',
    91: r'''		<p>Sekali lagi, \(H_0\) merupakan hipotesis sederhana dan, di bawah \(H_0\), statistik uji \(Y\) berdistribusi binomial dengan parameter \(n\) dan \(p_0\). Jika \(H_0\) benar, peluang menolak \(H_0\) secara keliru mendekati \(\alpha\); tingkat aktual harus dihitung dari peluang ekor diskret. Bagian (a)–(c) mengikuti sifat-sifat fungsi kuantil.</p>''',
    128: r'''		<p>Pada bagian (a), \(H_0\) adalah hipotesis sederhana dan, di bawah \(H_0\), statistik uji \(Z\) berdistribusi normal standar secara hampiran. Jika \(H_0\) benar, peluang menolak \(H_0\) secara keliru mendekati \(\alpha\). Pada bagian (b) dan (c), \(H_0\) menentukan suatu rentang nilai \(p\); di bawah \(H_0\), distribusi hampiran \(Z\) dijelaskan pada <a href="#nor1" class="ref"></a>. Peluang galat tipe I terbesar mendekati \(\alpha\) pada batas \(p=p_0\).</p>''',
    143: r'''		<p>Hipotesis \(H_0\) sederhana dan, di bawah \(H_0\), statistik uji \(Z\) mempunyai distribusi normal standar secara hampiran. Jika \(H_0\) benar, peluang menolak \(H_0\) secara keliru mendekati \(\alpha\) menurut definisi kuantil.</p>''',
    243: r'''		<p>Hasil-hasil tersebut mengikuti jika fungsi distribusi \(U\) kontinu dan meningkat ketat pada interval perbandingan \(S\). Dukungan yang berupa interval dan kontinuitas saja tidak cukup jika fungsi distribusi mempunyai bagian datar; dalam kasus itu kuantil harus didefinisikan dan hipotesis ditangani dengan lebih hati-hati.</p>''',
    253: r'''<p>Dari teorema <a href="#der1" class="ref"></a> dan <a href="#der2" class="ref"></a>, pengujian terhadap kuantil tak diketahui \(m\) dapat diubah menjadi pengujian parameter Bernoulli \(p\), sehingga uji-uji di atas berlaku. Prosedur ini disebut <dfn>uji tanda</dfn> karena pada dasarnya hanya tanda \(U_i-m_0\) yang dicatat untuk setiap \(i\). Prosedur ini juga merupakan <dfn>uji nonparametrik</dfn>: selain sampel acak, kontinuitas, dan keunikan kuantil, kita tidak membuat asumsi parametrik tentang distribusi \(U\); khususnya, distribusi \(U\) tidak perlu termasuk keluarga parametrik tertentu.</p>''',
    289: r'''		<p>Dengan konvensi indikator yang didefinisikan di atas, statistik uji adalah −3,286 dan nilai kritis berekor kiri −1,282. Tolak \(H_0\).</p>''',
    150: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, tetapkan \(H_0:p=p_0\), ukuran sampel 10, tingkat signifikansi 0,1, dan \(p_0=0.5\). Untuk setiap \(p\in\{0.1,0.2,\ldots,0.9\}\), jalankan eksperimen 1.000 kali, catat frekuensi relatif penolakan hipotesis nol, lalu gambarkan fungsi kuasa empiris.</p>''',
    158: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, tetapkan \(H_0:p\le p_0\), ukuran sampel 15, tingkat signifikansi 0,05, dan \(p_0=0.3\). Untuk setiap \(p\in\{0.1,0.2,\ldots,0.9\}\), jalankan eksperimen 1.000 kali, catat frekuensi relatif penolakan hipotesis nol, lalu gambarkan fungsi kuasa empiris.</p>''',
    166: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/ProportionTest.html')" class="ancillary">eksperimen uji proporsi</a>, tetapkan \(H_0:p\ge p_0\), ukuran sampel 20, tingkat signifikansi 0,01, dan \(p_0=0.6\). Untuk setiap \(p\in\{0.1,0.2,\ldots,0.9\}\), jalankan eksperimen 1.000 kali, catat frekuensi relatif penolakan hipotesis nol, lalu gambarkan fungsi kuasa empiris.</p>''',
})


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/point/Sufficient.html": "../point/Sufficient.html",
    "https://www.randomservices.org/random/interval/index.html": "../interval/index.html",
    "https://www.randomservices.org/random/interval/Bernoulli.html": "../interval/Bernoulli.html",
    "https://www.randomservices.org/random/hypothesis/index.html": "index.html",
    "https://www.randomservices.org/random/hypothesis/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/hypothesis/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/hypothesis/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/hypothesis/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/hypothesis/Likelihood.html": "Likelihood.html",
    "https://www.randomservices.org/random/hypothesis/ChiSquare.html": "ChiSquare.html",
}


EDITION_NOTICE = r'''
	<section class="edition-notice" data-o006-edition-notice="v1">
		<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, ID stabil tambahan, tautan lokal untuk bagian inti yang diterjemahkan, tautan HTTPS resmi untuk bahan pelengkap, koreksi terbatas pada notasi hipotesis, markup daftar, syarat uji tanda, serta tanda statistik dan nilai kritis pada jawaban yang dicatat dalam daftar koreksi edisi.</p>
		<p>Provenans terjemahan: OpenAI Codex gpt-5.6-sol, Ultra. Kredit penulis sumber dan kontributor manusia tetap dipertahankan.</p>
		<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
	</section>'''


MATH_REPAIRS_BY_INDEX = {
    116: r'''\(H_1:p\gt p_0\)''',
    227: r'''\(1.980\)''',
    228: r'''\(1.282\)''',
    230: r'''\(0.566\)''',
    231: r'''\(1.282\)''',
}


ADDITIVE_IDS = {
    "o006.random.hypothesis.bernoulli.page",
    "o006.random.hypothesis.bernoulli.unit-01",
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
    return re.sub(r"^(?:\\t)+", lambda match: "\t" * (len(match.group(0)) // 2), value, flags=re.MULTILINE)


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
        raise RuntimeError(f"core start-tag topology changed: {len(source_tags)} -> {len(target_tags)}")
    target_math = math_spans(core)
    expected_math = [MATH_REPAIRS_BY_INDEX.get(index, span) for index, span in enumerate(source_math)]
    if len(target_math) != EXPECTED_MATH_SPANS:
        raise RuntimeError(f"protected-math count changed: {len(source_math)} -> {len(target_math)}")
    if list(map(canonical_math, target_math)) != list(map(canonical_math, expected_math)):
        for index, (actual, expected) in enumerate(zip(target_math, expected_math)):
            if canonical_math(actual) != canonical_math(expected):
                raise RuntimeError(f"unexpected protected-math delta at span {index}: {actual!r} != {expected!r}")
        raise RuntimeError("unexpected protected-math sequence delta")

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
        raise RuntimeError(f"additive ID set changed: {sorted(set(ids) - set(source_ids))}")
    if len(ids) != EXPECTED_SOURCE_IDS + len(ADDITIVE_IDS):
        raise RuntimeError("target ID count changed")

    unresolved = (
        'lang="en"', "JavaScript:openAncillary", "http://", ">Hypothesis Testing<",
        ">Basic Tests<", ">Preliminaries<", ">The Binomial Test<",
        ">An Approximate Normal Test<", ">Simulation Exercises<",
        ">Computational Exercises<", ">The Sign Test<", ">Derivation<",
        ">Details:<", ">Apps<", ">Data Sets<", "> Biographies<",
        "binommial", "left-tailed and test", "In a pole of", "more that",
        "Verginica", "data/Fisher.html", r"H_1: p \ge p_0", "Test statistic 3.286",
        r"\(-1.980\)", r"\(-0.566\)",
    )
    for phrase in unresolved:
        if phrase in core:
            raise RuntimeError(f"unresolved reader-facing/source defect remains: {phrase}")
    required = (
        'href="../sample/Introduction.html"', 'href="../sample/CLT.html"',
        'href="../point/Sufficient.html#ber"', 'href="../interval/Bernoulli.html"',
        'href="index.html"', 'href="Introduction.html"', 'href="Normal.html"',
        'href="BivariateNormal.html"', 'href="Likelihood.html"', 'href="ChiSquare.html"',
        "fungsi massa probabilitas", "ukuran sebenarnya harus dihitung",
        "fungsi distribusi mempunyai bagian datar", "Simetri saja tidak menjamin",
        'href="https://www.randomservices.org/random/data/Iris.html"',
        "−3,286", r"\(1.980\)", r"\(0.566\)",
    )
    for phrase in required:
        if phrase not in core:
            raise RuntimeError(f"required translated/corrected surface absent: {phrase}")

    marker = "</footer>"
    if core.count(marker) != 1:
        raise RuntimeError("footer marker count changed")
    rendered = core.replace(marker, materialize_indentation(EDITION_NOTICE) + "\n" + marker, 1)
    if len(tag_stream(rendered)) != EXPECTED_ELEMENTS + 9:
        raise RuntimeError(f"edition-notice element delta changed: {len(tag_stream(rendered))}")
    if len(re.findall(r'<a\b[^>]*\bhref="[^"]+"', rendered)) != EXPECTED_CORE_LINKS + 4:
        raise RuntimeError("edition-notice link delta changed")

    output = rendered.encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(output)
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: {len(output)} bytes / "
        f"sha256 {hashlib.sha256(output).hexdigest()} / {EXPECTED_ELEMENTS} core elements / "
        f"{EXPECTED_MATH_SPANS} TeX / {EXPECTED_UNITS} units / {EXPECTED_DETAILS} details / {len(ids)} core IDs"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
