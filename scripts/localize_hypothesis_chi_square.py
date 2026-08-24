#!/usr/bin/env python3
"""Create the bounded id-ID chi-square hypothesis-testing target."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "hypothesis" / "ChiSquare.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "hypothesis" / "ChiSquare.html"
SOURCE_URL = "https://www.randomservices.org/random/hypothesis/ChiSquare.html"
SOURCE_BYTES = 39651
SOURCE_SHA256 = "379cf5939801c94b251884c0c82f0e6efc7ecce35cec11a645881d7ca9c7a6aa"
EXPECTED_SOURCE_LINES = 544

MATH_RE = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")
TOKEN_RE = re.compile(r"@@M(\d+)@@")
RAW_ALIGN_RE = re.compile(r"\\begin\{align\}(?:.|\n)*?\\end\{align\}")


# Every translated line is tied to its frozen authority line. Protected TeX is
# restored in authority order after the two proved formula repairs below.
T: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''	<title>Uji Khi-Kuadrat</title>''',
    9: r'''	<meta name="keywords" content="probabilitas, statistika, uji hipotesis, uji kecocokan, uji khi-kuadrat, distribusi khi-kuadrat, percobaan Bernoulli, percobaan multinomial, uji independensi">''',
    33: r'''		<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    34: r'''		<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    35: r'''		<li class="child"><a href="Normal.html" title="Pengujian pada Model Normal">2</a></li>''',
    36: r'''		<li class="child"><a href="Bernoulli.html" title="Pengujian pada Model Bernoulli">3</a></li>''',
    37: r'''		<li class="child"><a href="BivariateNormal.html" title="Pengujian pada Model Normal Dua Sampel">4</a></li>''',
    38: r'''		<li class="child"><a href="Likelihood.html" title="Uji Rasio Likelihood">5</a></li>''',
    40: r'''		<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    41: r'''		<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    43: r'''	<h2 id="o006.random.hypothesis.chi-square.page">6. Uji Khi-Kuadrat</h2>''',
    46: r'''<p>Dalam bagian ini, kita akan mempelajari sejumlah <a href="Introduction.html">uji hipotesis</a> penting yang secara umum disebut <dfn>uji khi-kuadrat</dfn>. Nama itu digunakan karena, pada setiap kasus, statistik ujinya mempunyai <a href="../special/ChiSquare.html">distribusi khi-kuadrat</a> secara asimtotik. Walaupun kategori ini memuat beberapa uji yang berbeda, semuanya mempunyai tema bersama:</p>''',
    49: r'''	<li>Setiap uji didasari oleh satu atau beberapa <a href="../bernoulli/Multinomial.html">sampel multinomial</a>. Model multinomial tentu mencakup <a href="../bernoulli/Introduction.html">model Bernoulli</a> sebagai kasus khusus.</li>''',
    50: r'''	<li>Setiap uji membandingkan <dfn>frekuensi teramati</dfn> berbagai hasil dengan <dfn>frekuensi harapan</dfn> di bawah hipotesis nol.</li>''',
    51: r'''	<li>Jika model <dfn>ditentukan secara tidak lengkap</dfn>, sebagian frekuensi harapan harus diduga; pada kondisi regular, hal ini mengurangi derajat kebebasan distribusi khi-kuadrat pembatas.</li>''',
    54: r'''<p>Kita mulai dari kasus paling sederhana, yang penurunannya paling langsung; bahkan uji ini ekuivalen dengan uji yang telah kita pelajari. Selanjutnya kita beralih ke model yang berturut-turut lebih rumit.</p>''',
    56: r'''<h4 id="o006.random.hypothesis.chi-square.topics">Topik</h4>''',
    59: r'''	<li><a href="#osb">Model Bernoulli Satu Sampel</a></li>''',
    60: r'''	<li><a href="#msb">Model Bernoulli Banyak Sampel</a></li>''',
    61: r'''	<li><a href="#osm">Model Multinomial Satu Sampel</a></li>''',
    62: r'''	<li><a href="#msm">Model Multinomial Banyak Sampel</a></li>''',
    63: r'''	<li><a href="#fit">Uji Kecocokan</a></li>''',
    64: r'''	<li><a href="#ind">Uji Independensi</a></li>''',
    65: r'''	<li><a href="#exe">Latihan Komputasi dan Simulasi</a></li>''',
    68: r'''<h3 id="osb">Model Bernoulli Satu Sampel</h3>''',
    70: r'''<p>Andaikan @@M1@@ merupakan sampel acak dari <a href="../bernoulli/Introduction.html">distribusi Bernoulli</a> dengan parameter sukses tak diketahui @@M2@@. Jadi, variabel-variabel tersebut <a href="../prob/Independence.html">saling bebas</a> dan merupakan <a href="../prob/Events.html">variabel acak</a> yang bernilai 1 dan 0 dengan probabilitas masing-masing @@M3@@ dan @@M4@@. Kita ingin menguji @@M5@@ melawan @@M6@@, dengan @@M7@@ ditentukan. Kita tentu telah mempelajari <a href="Bernoulli.html">uji pada model Bernoulli</a> semacam ini. Namun, ingatlah bahwa metode dalam bagian ini akan diperumum ke berbagai model baru yang belum kita pelajari.</p>''',
    72: r'''<p>Misalkan @@M1@@ dan @@M2@@. Statistik-statistik ini masing-masing menyatakan banyaknya (frekuensi) hasil 1 dan 0. Kita juga mengetahui bahwa keduanya mempunyai <a href="../bernoulli/Binomial.html">distribusi binomial</a>; @@M3@@ berparameter @@M4@@ dan @@M5@@, sedangkan @@M6@@ berparameter @@M7@@ dan @@M8@@. Khususnya, @@M9@@, @@M10@@, dan @@M11@@. Ingat pula bahwa @@M12@@ <a href="../point/Sufficient.html#ber">cukup</a> bagi @@M13@@. Karena itu, statistik uji yang baik seharusnya merupakan fungsi dari @@M14@@. Selanjutnya, ingat bahwa ketika @@M15@@ besar, distribusi @@M16@@ <a href="../bernoulli/Binomial.html#nor">mendekati normal</a> menurut <a href="../sample/CLT.html">teorema limit pusat</a>. Misalkan''',
    74: r'''Perhatikan bahwa @@M1@@ adalah skor baku @@M2@@ di bawah @@M3@@. Jadi, jika @@M4@@ besar, @@M5@@ kira-kira berdistribusi normal baku di bawah @@M6@@; akibatnya, @@M7@@ kira-kira berdistribusi khi-kuadrat dengan 1 derajat kebebasan di bawah @@M8@@. Pembenaran asimtotik ini mengandaikan probabilitas nol tetap di bagian dalam interval sehingga kedua frekuensi harapan bertumbuh. Seperti biasa, misalkan @@M9@@ menyatakan <a href="../dist/CDF.html#qnt">fungsi kuantil</a> distribusi khi-kuadrat dengan @@M10@@ derajat kebebasan.</p>''',
    77: r'''	<p class="math">Uji hampiran bagi @@M1@@ melawan @@M2@@ pada tingkat signifikansi @@M3@@ adalah menolak @@M4@@ jika dan hanya jika @@M5@@.</p>''',
    81: r'''	<p class="math">Uji <a href="#osb1" class="ref"></a> ekuivalen dengan uji tak bias berstatistik uji @@M1@@ (<a href="Bernoulli.html#nor">uji normal hampiran</a>) yang diturunkan dalam bagian <a href="Bernoulli.html">pengujian pada model Bernoulli</a>.</p>''',
    84: r'''<p>Untuk keperluan perumuman, hasil penting dalam latihan berikut adalah representasi khusus dari @@M1@@. Misalkan @@M2@@ dan @@M3@@. Besaran-besaran ini merupakan frekuensi harapan bagi hasil 0 dan 1 di bawah @@M4@@.</p>''',
    87: r'''	<p class="math">@@M1@@ dapat dituliskan dalam frekuensi teramati dan frekuensi harapan sebagai berikut:''',
    91: r'''<p>Representasi ini menunjukkan bahwa statistik uji @@M1@@ mengukur selisih antara frekuensi harapan di bawah @@M2@@ dan frekuensi teramati. Tentu saja, nilai @@M3@@ yang besar merupakan bukti yang mendukung @@M4@@. Terakhir, walaupun pengembangan @@M5@@ dalam Latihan 3 mempunyai dua suku, derajat kebebasannya hanya satu karena @@M6@@. Frekuensi teramati dan frekuensi harapan dapat disimpan dalam tabel @@M7@@.</p>''',
    93: r'''<h3 id="msb">Model Bernoulli Banyak Sampel</h3>''',
    95: r'''<p>Sekarang andaikan kita mempunyai sampel dari beberapa proses percobaan Bernoulli yang saling bebas dan mungkin berbeda. Secara khusus, andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../bernoulli/Introduction.html">distribusi Bernoulli</a> dengan parameter sukses tak diketahui @@M3@@ untuk setiap @@M4@@. Selain itu, sampel-sampel @@M5@@ saling bebas. Kita ingin menguji hipotesis mengenai vektor parameter tak diketahui @@M6@@. Ada dua kasus umum yang akan kita bahas, tetapi pertama-tama kita tetapkan notasi penting bagi keduanya. Untuk @@M7@@ dan @@M8@@, misalkan @@M9@@ menyatakan banyaknya hasil @@M10@@ dalam sampel @@M11@@. Frekuensi teramati @@M12@@ berdistribusi binomial; @@M13@@ berparameter @@M14@@ dan @@M15@@, sedangkan @@M16@@ berparameter @@M17@@ dan @@M18@@.</p>''',
    97: r'''<h4 id="msbc">Kasus yang Ditentukan Sepenuhnya</h4>''',
    99: r'''<p>Tinjau vektor parameter yang ditentukan, @@M1@@. Kita ingin menguji hipotesis nol @@M2@@ melawan @@M3@@. Karena hipotesis nol menentukan nilai @@M4@@ bagi setiap @@M5@@, kasus ini disebut <dfn>kasus yang ditentukan sepenuhnya</dfn>. Sekarang misalkan @@M6@@ dan @@M7@@. Besaran-besaran ini masing-masing merupakan frekuensi harapan bagi hasil 0 dan 1 dari sampel @@M8@@ di bawah @@M9@@.</p>''',
    102: r'''	<p class="math">Jika @@M1@@ besar bagi setiap @@M2@@, maka di bawah @@M3@@ statistik uji berikut kira-kira berdistribusi khi-kuadrat dengan @@M4@@ derajat kebebasan:''',
    105: r'''		<summary>Rincian:</summary>''',
    106: r'''		<p>Hasil ini mengikuti <a href="#osb3" class="ref"></a> dan sifat saling bebas.</p>''',
    110: r'''<p>Kalibrasi asimtotik di atas mengasumsikan banyak sampel tetap, probabilitas sel di bawah nol positif, dan seluruh frekuensi harapan menuju tak hingga. Istilah <q>besar</q> tidak ditentukan hanya oleh aturan praktis konvensional @@M1@@ bagi setiap @@M2@@ dan @@M3@@; aturan itu hanyalah heuristik, bukan teorema. Sel yang jarang atau sangat tak seimbang dapat memerlukan penggabungan kategori yang telah ditetapkan sebelumnya atau kalibrasi eksak/simulasi.</p>''',
    113: r'''	<p class="math">Di bawah asumsi sampel besar, uji hampiran bagi @@M1@@ melawan @@M2@@ pada tingkat signifikansi @@M3@@ adalah menolak @@M4@@ jika dan hanya jika @@M5@@.</p>''',
    116: r'''<p>Sekali lagi, statistik uji @@M1@@ mengukur selisih antara frekuensi harapan dan frekuensi teramati pada semua hasil dan semua sampel. Terdapat @@M2@@ suku dalam pengembangan @@M3@@ pada Latihan 4, tetapi hanya @@M4@@ derajat kebebasan karena @@M5@@ bagi setiap @@M6@@. Frekuensi teramati dan frekuensi harapan dapat disimpan dalam tabel @@M7@@.</p>''',
    118: r'''<h4 id="msbe">Kasus Probabilitas Sama</h4>''',
    120: r'''<p>Sekarang andaikan kita ingin menguji hipotesis nol @@M1@@, yakni semua probabilitas sukses sama, melawan hipotesis alternatif komplementer @@M2@@ bahwa probabilitas-probabilitas itu tidak semuanya sama. Berbeda dari model sebelumnya, hipotesis nol tidak menentukan nilai probabilitas sukses bersama @@M3@@. Namun, di bawah hipotesis nol, @@M4@@ sampel dapat digabungkan menjadi satu sampel besar percobaan Bernoulli dengan probabilitas sukses @@M5@@. Karena itu, pendekatan alaminya adalah menduga @@M6@@ lalu, seperti sebelumnya, mendefinisikan statistik uji yang mengukur selisih antara frekuensi harapan dan frekuensi teramati. Tantangannya adalah menentukan distribusi statistik uji tersebut.</p>''',
    122: r'''<p>Misalkan @@M1@@ menyatakan ukuran sampel total setelah semua sampel digabungkan. Rata-rata keseluruhan sampel, yang dalam konteks ini merupakan proporsi sukses keseluruhan, adalah''',
    124: r'''Proporsi sampel @@M1@@ merupakan penduga terbaik bagi @@M2@@ dalam hampir semua pengertian. Selanjutnya, misalkan @@M3@@ dan @@M4@@. Besaran-besaran ini adalah frekuensi harapan <em>dugaan</em> bagi hasil 0 dan 1 dari sampel @@M5@@ di bawah @@M6@@. Frekuensi dugaan ini sekarang tentu merupakan <em>statistik</em> (dan karena itu acak), bukan parameter. Seperti sebelumnya, kita definisikan statistik uji''',
    126: r'''Untuk jumlah sampel tetap, proporsi ukuran sampel yang tidak merosot, dan probabilitas bersama di bagian dalam ruang parameter, di bawah @@M1@@ distribusi @@M2@@ konvergen ke distribusi khi-kuadrat dengan @@M3@@ derajat kebebasan ketika @@M4@@.</p>''',
    129: r'''	<p class="math">Uji hampiran bagi @@M1@@ melawan @@M2@@ pada tingkat signifikansi @@M3@@ adalah menolak @@M4@@ jika dan hanya jika @@M5@@.</p>''',
    132: r'''<p>Secara intuitif, kita kehilangan satu derajat kebebasan dibandingkan kasus yang ditentukan sepenuhnya pada <a href="#msbc" class="ref"></a> karena harus menduga probabilitas sukses bersama tak diketahui @@M1@@. Frekuensi teramati dan harapan kembali dapat disimpan dalam tabel @@M2@@.</p>''',
    134: r'''<h3 id="osm">Model Multinomial Satu Sampel</h3>''',
    136: r'''<p>Model berikut memperumum <a href="#osb">model Bernoulli satu sampel</a> ke arah lain. Andaikan @@M1@@ merupakan barisan <a href="../bernoulli/Multinomial.html">percobaan multinomial</a>. Jadi, variabel-variabel ini saling bebas dan berdistribusi identik, masing-masing bernilai dalam himpunan @@M2@@ dengan @@M3@@ anggota. Tanpa mengurangi keumuman, kita dapat mengambil @@M4@@; model Bernoulli satu sampel lalu bersesuaian dengan @@M5@@. Misalkan @@M6@@ menyatakan fungsi kepadatan probabilitas yang sama bagi semua variabel sampel pada @@M7@@, sehingga @@M8@@ bagi @@M9@@ dan @@M10@@. Nilai-nilai @@M11@@ dianggap tidak diketahui, tetapi tentu @@M12@@, sehingga sebenarnya hanya ada @@M13@@ parameter tak diketahui. Bagi fungsi kepadatan probabilitas tertentu @@M14@@ pada @@M15@@, kita ingin menguji @@M16@@ melawan @@M17@@.</p>''',
    138: r'''<p>Pendekatan umumnya kini seharusnya jelas. Misalkan @@M1@@ menyatakan banyaknya hasil @@M2@@ dalam sampel @@M3@@:''',
    140: r'''Perhatikan bahwa @@M1@@ mempunyai distribusi binomial berparameter @@M2@@ dan @@M3@@. Jadi, @@M4@@ adalah frekuensi harapan hasil @@M5@@ di bawah @@M6@@. Statistik uji kita adalah''',
    142: r'''Di bawah @@M1@@, jika banyak kategori tetap, seluruh probabilitas nol positif, dan frekuensi harapan menuju tak hingga, distribusi @@M2@@ konvergen ke distribusi khi-kuadrat dengan @@M3@@ derajat kebebasan ketika @@M4@@. Terdapat @@M5@@ suku dalam pengembangan @@M6@@, tetapi hanya @@M7@@ derajat kebebasan karena @@M8@@.</p>''',
    145: r'''	<p class="math">Uji hampiran bagi @@M1@@ melawan @@M2@@ pada tingkat signifikansi @@M3@@ adalah menolak @@M4@@ jika dan hanya jika @@M5@@.</p>''',
    148: r'''<p>Aturan praktis konvensional meminta @@M1@@ bagi setiap @@M2@@, tetapi angka 5 bukan syarat matematis yang menjamin hampiran baik. Yang mendasari limit adalah frekuensi harapan setiap sel menuju tak hingga; untuk sampel hingga, sel jarang atau sangat tak seimbang dapat memerlukan kategori yang digabungkan menurut aturan yang telah ditetapkan atau metode eksak/simulasi.</p>''',
    150: r'''<h3 id="msm">Model Multinomial Banyak Sampel</h3>''',
    152: r'''<p>Perumuman terakhir adalah model multinomial banyak sampel. Secara khusus, andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi pada himpunan @@M3@@ dengan @@M4@@ anggota, bagi setiap @@M5@@. Kita juga mengasumsikan bahwa sampel-sampel @@M6@@ saling bebas. Tanpa mengurangi keumuman, kita dapat mengambil @@M7@@. Lalu @@M8@@ menghasilkan <a href="#msb">model Bernoulli banyak sampel</a>, sedangkan @@M9@@ bersesuaian dengan <a href="#osm">model multinomial satu sampel</a>.</p>''',
    154: r'''<p>Misalkan @@M1@@ menyatakan fungsi kepadatan probabilitas yang sama bagi semua variabel dalam sampel @@M2@@, sehingga @@M3@@ bagi @@M4@@, @@M5@@, dan @@M6@@. Fungsi-fungsi ini umumnya tidak diketahui, sehingga vektor parameter kita adalah vektor fungsi kepadatan probabilitas @@M7@@. Tentu saja, @@M8@@ bagi @@M9@@, sehingga sebenarnya terdapat @@M10@@ parameter tak diketahui. Kita tertarik menguji hipotesis mengenai @@M11@@. Seperti dalam model Bernoulli banyak sampel, ada dua kasus umum yang dibahas di bawah; pertama-tama kita tetapkan notasi penting bagi keduanya. Untuk @@M12@@ dan @@M13@@, misalkan @@M14@@ menyatakan banyaknya hasil @@M15@@ dalam sampel @@M16@@. Frekuensi teramati @@M17@@ mempunyai distribusi binomial berparameter @@M18@@ dan @@M19@@.</p>''',
    156: r'''<h4 id="msmc">Kasus yang Ditentukan Sepenuhnya</h4>''',
    158: r'''<p>Tinjau vektor fungsi kepadatan probabilitas tertentu pada @@M1@@, yang dilambangkan @@M2@@. Kita ingin menguji hipotesis nol @@M3@@ melawan @@M4@@. Karena hipotesis nol menentukan nilai @@M5@@ bagi setiap @@M6@@ dan @@M7@@, kasus ini disebut <dfn>kasus yang ditentukan sepenuhnya</dfn>. Misalkan @@M8@@. Ini adalah frekuensi harapan hasil @@M9@@ dalam sampel @@M10@@ di bawah @@M11@@.</p>''',
    161: r'''	<p class="math">Jika @@M1@@ besar bagi setiap @@M2@@, maka di bawah @@M3@@ statistik uji @@M4@@ berikut kira-kira berdistribusi khi-kuadrat dengan @@M5@@ derajat kebebasan:''',
    164: r'''		<summary>Rincian:</summary>''',
    165: r'''		<p>Hasil ini mengikuti kasus <a href="#osm">multinomial satu sampel</a> dan sifat saling bebas.</p>''',
    169: r'''<p>Secara asimtotik, banyak sampel dan banyak kategori harus tetap, semua probabilitas sel di bawah nol positif, dan setiap frekuensi harapan menuju tak hingga. Aturan praktis @@M1@@ bagi setiap @@M2@@ dan @@M3@@ hanyalah heuristik sampel hingga; semakin besar dan seimbang frekuensi harapannya, biasanya semakin baik hampiran.</p>''',
    172: r'''	<p class="math">Di bawah asumsi sampel besar, uji hampiran bagi @@M1@@ melawan @@M2@@ pada tingkat signifikansi @@M3@@ adalah menolak @@M4@@ jika dan hanya jika @@M5@@.</p>''',
    175: r'''<p>Seperti biasa, statistik uji @@M1@@ mengukur selisih antara frekuensi harapan dan frekuensi teramati pada semua hasil dan semua sampel. Terdapat @@M2@@ suku dalam pengembangan @@M3@@ pada Latihan 8, tetapi kita kehilangan @@M4@@ derajat kebebasan karena @@M5@@ bagi setiap @@M6@@.</p>''',
    177: r'''<h4 id="msme">Kasus Fungsi Kepadatan Probabilitas Sama</h4>''',
    179: r'''<p>Sekarang andaikan kita ingin menguji hipotesis nol @@M1@@, yakni semua fungsi kepadatan probabilitas sama, melawan hipotesis alternatif komplementer @@M2@@ bahwa fungsi-fungsi itu tidak semuanya sama. Berbeda dari model sebelumnya, hipotesis nol tidak menentukan fungsi kepadatan probabilitas yang sama tersebut, @@M3@@. Namun, di bawah hipotesis nol, @@M4@@ sampel dapat digabungkan menjadi satu sampel besar percobaan multinomial berfungsi kepadatan probabilitas @@M5@@. Karena itu, pendekatan alaminya adalah menduga nilai-nilai @@M6@@ lalu, seperti sebelumnya, mendefinisikan statistik uji yang mengukur selisih antara frekuensi harapan dan frekuensi teramati.</p>''',
    181: r'''<p>Misalkan @@M1@@ menyatakan ukuran sampel total setelah semua sampel digabungkan. Di bawah @@M2@@, penduga terbaik kita bagi @@M3@@ adalah''',
    183: r'''Jadi, dugaan frekuensi harapan hasil @@M1@@ dalam sampel @@M2@@ di bawah @@M3@@ adalah @@M4@@. Frekuensi dugaan ini kembali merupakan <em>statistik</em> (dan karena itu acak), bukan parameter. Seperti sebelumnya, kita definisikan statistik uji''',
    185: r'''Jika banyak sampel dan kategori tetap, proporsi ukuran sampel tidak merosot, probabilitas sel positif, dan setiap frekuensi harapan menuju tak hingga, maka di bawah @@M1@@ distribusi @@M2@@ konvergen ke distribusi khi-kuadrat ketika @@M3@@. Derajat kebebasannya dapat ditentukan secara heuristik sebagai berikut.</p>''',
    188: r'''	<p class="math">Distribusi pembatas @@M1@@ mempunyai @@M2@@ derajat kebebasan.</p>''',
    190: r'''		<summary>Rincian:</summary>''',
    191: r'''		<p>Terdapat @@M1@@ suku dalam pengembangan @@M2@@. Kita kehilangan @@M3@@ derajat kebebasan karena @@M4@@ bagi setiap @@M5@@. Kita harus menduga semua kecuali satu dari probabilitas @@M6@@ bagi @@M7@@, sehingga kehilangan @@M8@@ derajat kebebasan lagi.</p>''',
    196: r'''	<p class="math">Uji hampiran bagi @@M1@@ melawan @@M2@@ pada tingkat signifikansi @@M3@@ adalah menolak @@M4@@ jika dan hanya jika @@M5@@.</p>''',
    199: r'''<h3 id="fit">Uji Kecocokan</h3>''',
    201: r'''<p><dfn>Uji kecocokan</dfn> adalah uji hipotesis bahwa distribusi pensampelan yang tidak diketahui sama dengan distribusi tertentu yang ditentukan atau termasuk dalam suatu keluarga parametrik. Uji semacam ini jelas mendasar dan penting. <a href="#osm">Model multinomial satu sampel</a> menghasilkan uji kecocokan yang cukup umum.</p>''',
    203: r'''<p>Untuk menyiapkan masalah, andaikan kita mempunyai variabel acak teramati @@M1@@ bagi suatu eksperimen yang bernilai dalam himpunan umum @@M2@@. Variabel acak @@M3@@ dapat berdistribusi kontinu atau diskret dan dapat berupa variabel tunggal atau multivariabel. Kita ingin menguji hipotesis nol bahwa @@M4@@ mempunyai distribusi tertentu yang ditentukan sepenuhnya, atau bahwa distribusi @@M5@@ termasuk dalam keluarga parametrik tertentu.</p>''',
    205: r'''<p>Langkah pertama dalam kedua kasus adalah mengambil sampel dari distribusi @@M1@@ sehingga diperoleh barisan variabel saling bebas dan berdistribusi identik @@M2@@. Selanjutnya, kita pilih @@M3@@ dan <a href="../foundations/Sets.html#par">mempartisi</a> @@M4@@ menjadi @@M5@@ himpunan bagian yang saling lepas. Partisi ini kita lambangkan @@M6@@, dengan @@M7@@. Batas partisi harus ditetapkan sebelum memeriksa data yang sama; jika kategori dipilih atau disetel dari data, prosedur pemilihan itu harus ikut dimasukkan dalam distribusi acuan atau kalibrasi simulasi. Kemudian kita definisikan barisan variabel acak @@M8@@ dengan @@M9@@ jika dan hanya jika @@M10@@, bagi @@M11@@ dan @@M12@@.</p>''',
    208: r'''	<p class="math">@@M1@@ merupakan barisan percobaan multinomial berparameter @@M2@@ dan @@M3@@, dengan @@M4@@ bagi @@M5@@.</p>''',
    211: r'''<h4 id="fitc">Kasus yang Ditentukan Sepenuhnya</h4>''',
    213: r'''<p>Misalkan @@M1@@ menyatakan bahwa @@M2@@ mempunyai distribusi tertentu yang ditentukan sepenuhnya. Misalkan @@M3@@ menyatakan fungsi kepadatan probabilitas pada @@M4@@ yang didefinisikan oleh @@M5@@ bagi @@M6@@. Untuk menguji hipotesis @@M7@@, secara formal kita dapat menguji @@M8@@ melawan @@M9@@, tepat seperti masalah yang telah diselesaikan dalam <a href="#osm">model multinomial satu sampel</a>.</p>''',
    215: r'''<p>Secara umum, partisi ruang @@M1@@ dipilih sebelum data uji dilihat agar mempunyai rincian sebanyak mungkin tanpa menciptakan sel yang terlalu jarang. Syarat semua frekuensi harapan sekurang-kurangnya 5 hanyalah heuristik; banyak kategori harus tetap dan, untuk pembenaran asimtotik, setiap frekuensi harapan harus menuju tak hingga.</p>''',
    217: r'''<h4 id="fitp">Kasus yang Ditentukan Sebagian</h4>''',
    219: r'''<p>Sering kali kita tidak ingin menguji apakah @@M1@@ mempunyai distribusi yang ditentukan sepenuhnya—misalnya normal dengan rata-rata 5 dan varians 9—melainkan apakah distribusi @@M2@@ termasuk dalam keluarga parametrik tertentu, misalnya keluarga normal. Pendekatan alaminya adalah menduga parameter tak diketahui di bawah hipotesis nol lalu melanjutkan seperti di atas. Karena didasarkan pada parameter dugaan, frekuensi harapan @@M3@@ menjadi statistik. Dalam statistik khi-kuadrat @@M4@@, pengurangan satu derajat kebebasan bagi setiap parameter bebas yang diduga berlaku hanya ketika parameterisasi dapat diidentifikasi dan regular, penduganya konsisten di bawah nol, informasi terkait berperingkat penuh, probabilitas sel positif, dan partisi ditetapkan sebelumnya. Pada kasus batas, tidak teridentifikasi, sel kosong, atau kategori yang dipilih dari data, limit dan kalibrasinya dapat berbeda; karena itu aturan “satu derajat untuk setiap parameter” bukan hukum universal.</p>''',
    221: r'''<h3 id="ind">Uji Independensi</h3>''',
    223: r'''<p>Andaikan kita mempunyai variabel acak teramati @@M1@@ dan @@M2@@ bagi suatu eksperimen, dengan @@M3@@ bernilai dalam himpunan @@M4@@ yang mempunyai @@M5@@ anggota dan @@M6@@ bernilai dalam himpunan @@M7@@ yang mempunyai @@M8@@ anggota. Misalkan @@M9@@ menyatakan <a href="../dist/Joint.html">fungsi kepadatan probabilitas gabungan</a> dari @@M10@@, sehingga @@M11@@ bagi @@M12@@ dan @@M13@@. Ingat bahwa fungsi kepadatan probabilitas marginal @@M14@@ dan @@M15@@ masing-masing adalah @@M16@@ dan @@M17@@, dengan''',
    228: r'''Tentu saja, @@M1@@, @@M2@@, dan @@M3@@ biasanya tidak diketahui. Dalam bagian ini kita tertarik menguji apakah @@M4@@ dan @@M5@@ saling bebas, suatu uji yang mendasar dan penting. Secara formal, kita ingin menguji hipotesis nol''',
    230: r'''melawan hipotesis alternatif komplementer @@M1@@.</p>''',
    232: r'''<p>Langkah pertama adalah mengambil sampel acak @@M1@@ dari distribusi @@M2@@. Karena ruang keadaannya hingga, sampel ini membentuk barisan percobaan multinomial. Dengan notasi biasa, misalkan @@M3@@ menyatakan banyaknya kemunculan @@M4@@ dalam sampel bagi setiap @@M5@@. Statistik ini mempunyai distribusi binomial dengan parameter banyak percobaan @@M6@@ dan parameter sukses @@M7@@. Di bawah @@M8@@, parameter suksesnya adalah @@M9@@. Karena parameter sukses tidak diketahui, kita harus menduganya untuk menghitung frekuensi harapan. Penduga terbaik bagi @@M10@@ adalah proporsi sampel @@M11@@. Jadi, penduga terbaik bagi @@M12@@ dan @@M13@@ masing-masing adalah @@M14@@ dan @@M15@@, dengan @@M16@@ menyatakan banyaknya kemunculan @@M17@@ dalam sampel @@M18@@, sedangkan @@M19@@ menyatakan banyaknya kemunculan @@M20@@ dalam sampel @@M21@@:''',
    237: r'''Jadi, dugaan frekuensi harapan bagi @@M1@@ di bawah @@M2@@ adalah''',
    239: r'''Seperti biasa, kita definisikan statistik uji''',
    241: r'''Jika banyak kategori tetap, peluang marginal positif, dan semua frekuensi sel harapan menuju tak hingga, distribusi @@M1@@ konvergen ke distribusi khi-kuadrat ketika @@M2@@. Derajat kebebasannya dapat ditentukan secara heuristik sebagai berikut.</p>''',
    244: r'''	<p class="math">Distribusi pembatas @@M1@@ mempunyai @@M2@@ derajat kebebasan.</p>''',
    246: r'''		<summary>Rincian:</summary>''',
    247: r'''		<p>Terdapat @@M1@@ suku dalam pengembangan @@M2@@. Kita kehilangan satu derajat kebebasan karena @@M3@@. Kita harus menduga semua kecuali satu dari probabilitas @@M4@@ bagi @@M5@@, sehingga kehilangan @@M6@@ derajat kebebasan; kita juga harus menduga semua kecuali satu dari probabilitas @@M7@@ bagi @@M8@@, sehingga kehilangan @@M9@@ derajat kebebasan.</p>''',
    252: r'''	<p class="math">Uji hampiran bagi @@M1@@ melawan @@M2@@ pada tingkat signifikansi @@M3@@ adalah menolak @@M4@@ jika dan hanya jika @@M5@@.</p>''',
    255: r'''<p>Frekuensi teramati sering dicatat dalam tabel @@M1@@ yang disebut <dfn>tabel kontingensi</dfn>, dengan @@M2@@ sebagai bilangan pada baris @@M3@@ dan kolom @@M4@@. Dalam penyajian ini, @@M5@@ adalah jumlah frekuensi pada baris ke-@@M6@@ dan @@M7@@ adalah jumlah frekuensi pada kolom ke-@@M8@@. Karena alasan historis, variabel acak @@M9@@ dan @@M10@@ terkadang disebut <dfn>faktor</dfn>, sedangkan nilai-nilai yang mungkin disebut <dfn>kategori</dfn>.</p>''',
    257: r'''<h3 id="exe">Latihan Komputasi dan Simulasi</h3>''',
    259: r'''<h4 id="cmp">Latihan Komputasi</h4>''',
    261: r'''<p>Dalam setiap latihan berikut, tentukan derajat kebebasan statistik khi-kuadrat, hitung nilai statistik tersebut, dan hitung nilai-@@M1@@ ujinya.</p>''',
    264: r'''	<p class="math">Sebuah koin dilempar 100 kali dan menghasilkan 55 sisi kepala. Uji hipotesis nol bahwa koin itu adil.</p>''',
    266: r'''		<summary>Rincian:</summary>''',
    267: r'''		<p>1 derajat kebebasan, @@M1@@, @@M2@@.</p>''',
    272: r'''	<p class="math">Andaikan kita mempunyai 3 koin. Koin-koin itu dilempar dan menghasilkan data dalam tabel berikut:</p>''',
    277: r'''				<th>Kepala</th>''',
    278: r'''				<th>Ekor</th>''',
    281: r'''				<th>Koin 1</th>''',
    286: r'''				<th>Koin 2</th>''',
    291: r'''				<th>Koin 3</th>''',
    298: r'''		<li>Uji hipotesis nol bahwa ketiga koin adil.</li>''',
    299: r'''		<li>Uji hipotesis nol bahwa probabilitas kepala koin 1 adalah @@M1@@, koin 2 adil, dan probabilitas kepala koin 3 adalah @@M2@@.</li>''',
    300: r'''		<li>Uji hipotesis nol bahwa ketiga koin mempunyai probabilitas kepala yang sama.</li>''',
    303: r'''		<summary>Rincian:</summary>''',
    305: r'''			<li>3 derajat kebebasan, @@M1@@, @@M2@@.</li>''',
    306: r'''			<li>3 derajat kebebasan, @@M1@@, @@M2@@.</li>
			<li>2 derajat kebebasan, @@M3@@, @@M4@@.</li>''',
    312: r'''	<p class="math">Sebuah dadu dilempar 240 kali dan menghasilkan data dalam tabel berikut:</p>''',
    316: r'''				<th>Mata</th>''',
    325: r'''				<th>Frekuensi</th>''',
    336: r'''		<li>Uji hipotesis nol bahwa dadu itu adil.</li>''',
    337: r'''		<li>Uji hipotesis nol bahwa dadu tersebut adalah dadu pipih satu-enam (sisi 1 dan 6 masing-masing mempunyai probabilitas @@M1@@, sedangkan sisi 2, 3, 4, dan 5 masing-masing mempunyai probabilitas @@M2@@).</li>''',
    340: r'''		<summary>Rincian:</summary>''',
    342: r'''			<li>5 derajat kebebasan, @@M1@@, @@M2@@.</li>''',
    343: r'''			<li>5 derajat kebebasan, @@M1@@, @@M2@@.</li>''',
    349: r'''	<p class="math">Dua dadu dilempar dan menghasilkan data dalam tabel berikut:</p>''',
    353: r'''				<th>Mata</th>''',
    362: r'''				<th>Dadu 1</th>''',
    371: r'''				<th>Dadu 2</th>''',
    382: r'''		<li>Uji hipotesis nol bahwa dadu 1 adil dan dadu 2 adalah dadu pipih satu-enam.</li>''',
    383: r'''		<li>Uji hipotesis nol bahwa kedua dadu mempunyai distribusi probabilitas yang sama.</li>''',
    386: r'''		<summary>Rincian:</summary>''',
    388: r'''			<li>10 derajat kebebasan, @@M1@@, @@M2@@.</li>''',
    389: r'''			<li>5 derajat kebebasan, @@M1@@, @@M2@@.</li>''',
    395: r'''	<p class="math">Sebuah universitas mengelompokkan dosen berdasarkan jenjang menjadi <em>instruktur</em>, <em>asisten profesor</em>, <em>lektor kepala</em>, dan <em>profesor penuh</em>. Data menurut jenjang dan gender diberikan dalam tabel kontingensi berikut. Uji apakah jenjang dan gender dosen saling bebas.</p>''',
    399: r'''				<th>Dosen</th>''',
    400: r'''				<th>Instruktur</th>''',
    401: r'''				<th>Asisten Profesor</th>''',
    402: r'''				<th>Lektor Kepala</th>''',
    403: r'''				<th>Profesor Penuh</th>''',
    406: r'''				<th>Laki-laki</th>''',
    413: r'''				<th>Perempuan</th>''',
    422: r'''		<summary>Rincian:</summary>''',
    423: r'''		<p>3 derajat kebebasan, @@M1@@, @@M2@@.</p>''',
    427: r'''<h4 id="dat">Latihan Analisis Data</h4>''',
    430: r'''	<p class="stat"><a href="JavaScript:openAncillary('../data/Buffon.html')" class="ancillary">Kumpulan data percobaan Buffon</a> memuat hasil 104 pengulangan eksperimen jarum Buffon. Banyaknya lintasan yang memotong celah adalah 56. Secara teori, data ini seharusnya bersesuaian dengan 104 percobaan Bernoulli berprobabilitas sukses @@M1@@. Uji apakah anggapan itu masuk akal.</p>''',
    432: r'''		<summary>Rincian:</summary>''',
    433: r'''		<p>1 derajat kebebasan, @@M1@@, @@M2@@.</p>''',
    438: r'''	<p class="stat">Uji apakah <a href="JavaScript:openAncillary('../data/Alpha.html')" class="ancillary">data emisi alfa</a> berasal dari distribusi Poisson.</p>''',
    440: r'''		<summary>Rincian:</summary>''',
    441: r'''		<p>Kita mempartisi @@M1@@ menjadi 17 himpunan bagian: @@M2@@, @@M3@@ bagi @@M4@@, dan @@M5@@. Derajat kebebasannya 15. Parameter Poisson dugaan adalah 8,367, @@M6@@, dan @@M7@@.</p>''',
    446: r'''	<p class="stat">Uji apakah <a href="JavaScript:openAncillary('../data/Michelson.html')" class="ancillary">data kecepatan cahaya Michelson</a> berasal dari distribusi normal.</p>''',
    448: r'''		<summary>Rincian:</summary>''',
    449: r'''		<p>Gunakan partisi @@M1@@ berikut, yang ditetapkan sebelum pengujian: @@M2@@. Setelah rata-rata dan simpangan baku diduga dari data, derajat kebebasannya 8, @@M3@@, dan @@M4@@.</p>''',
    453: r'''<h4 id="sim">Latihan Simulasi</h4>''',
    455: r'''<p>Dalam latihan simulasi berikut, Anda dapat menyelidiki uji kecocokan secara empiris.</p>''',
    458: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/DiceFit.html')" class="ancillary">eksperimen kecocokan dadu</a>, atur distribusi pensampelan menjadi adil, ukuran sampel 50, dan tingkat signifikansi 0,1. Atur distribusi uji seperti di bawah, lalu jalankan simulasi 1.000 kali untuk setiap kasus. Pada (a), berikan dugaan empiris tingkat signifikansi dan bandingkan dengan 0,1. Pada kasus lainnya, berikan dugaan empiris kuasa uji. Urutkan distribusi (b)&ndash;(d) menurut kuasa yang tampak dari kecil ke besar. Apakah hasilnya masuk akal?</p>''',
    460: r'''		<li>adil</li>''',
    461: r'''		<li>pipih satu-enam</li>''',
    462: r'''		<li>distribusi simetris unimodal</li>''',
    463: r'''		<li>distribusi menceng ke kanan</li>''',
    468: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/DiceFit.html')" class="ancillary">eksperimen kecocokan dadu</a>, atur distribusi pensampelan menjadi pipih satu-enam, ukuran sampel 50, dan tingkat signifikansi 0,1. Atur distribusi uji seperti di bawah, lalu jalankan simulasi 1.000 kali untuk setiap kasus. Pada (a), berikan dugaan empiris tingkat signifikansi dan bandingkan dengan 0,1. Pada kasus lainnya, berikan dugaan empiris kuasa uji. Urutkan distribusi (b)&ndash;(d) menurut kuasa yang tampak dari kecil ke besar. Apakah hasilnya masuk akal?</p>''',
    470: r'''		<li>adil</li>''',
    471: r'''		<li>pipih satu-enam</li>''',
    472: r'''		<li>distribusi simetris unimodal</li>''',
    473: r'''		<li>distribusi menceng ke kanan</li>''',
    478: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/DiceFit.html')" class="ancillary">eksperimen kecocokan dadu</a>, atur distribusi pensampelan menjadi distribusi simetris unimodal, ukuran sampel 50, dan tingkat signifikansi 0,1. Atur distribusi uji seperti di bawah, lalu jalankan simulasi 1.000 kali untuk setiap kasus. Pada (a), berikan dugaan empiris tingkat signifikansi dan bandingkan dengan 0,1. Pada kasus lainnya, berikan dugaan empiris kuasa uji. Urutkan distribusi (b)&ndash;(d) menurut kuasa yang tampak dari kecil ke besar. Apakah hasilnya masuk akal?</p>''',
    480: r'''		<li>distribusi simetris unimodal</li>''',
    481: r'''		<li>adil</li>''',
    482: r'''		<li>pipih satu-enam</li>''',
    483: r'''		<li>distribusi menceng ke kanan</li>''',
    488: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/DiceFit.html')" class="ancillary">eksperimen kecocokan dadu</a>, atur distribusi pensampelan menjadi distribusi menceng ke kanan, ukuran sampel 50, dan tingkat signifikansi 0,1. Atur distribusi uji seperti di bawah, lalu jalankan simulasi 1.000 kali untuk setiap kasus. Pada (a), berikan dugaan empiris tingkat signifikansi dan bandingkan dengan 0,1. Pada kasus lainnya, berikan dugaan empiris kuasa uji. Urutkan distribusi (b)&ndash;(d) menurut kuasa yang tampak dari kecil ke besar. Apakah hasilnya masuk akal?</p>''',
    490: r'''		<li>distribusi menceng ke kanan</li>''',
    491: r'''		<li>adil</li>''',
    492: r'''		<li>pipih satu-enam</li>''',
    493: r'''		<li>distribusi simetris unimodal</li>''',
    498: r'''	<p class="math">Andaikan @@M1@@ dan @@M2@@ merupakan distribusi yang berbeda. Apakah kuasa uji dengan distribusi pensampelan @@M3@@ dan distribusi uji @@M4@@ sama dengan kuasa uji dengan distribusi pensampelan @@M5@@ dan distribusi uji @@M6@@? Buat konjektur berdasarkan empat latihan sebelumnya.</p>''',
    502: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/DiceFit.html')" class="ancillary">eksperimen kecocokan dadu</a>, atur distribusi pensampelan dan distribusi uji menjadi adil, serta tingkat signifikansi menjadi 0,05. Jalankan eksperimen 1.000 kali untuk setiap ukuran sampel berikut. Dalam setiap kasus, berikan dugaan empiris tingkat signifikansi dan bandingkan dengan 0,05.</p>''',
    511: r'''<div class="unit" id="o006.random.hypothesis.chi-square.unit.sim7">''',
    512: r'''	<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/DiceFit.html')" class="ancillary">eksperimen kecocokan dadu</a>, atur distribusi pensampelan menjadi adil, distribusi uji menjadi pipih satu-enam, dan tingkat signifikansi menjadi 0,05. Jalankan eksperimen 1.000 kali untuk setiap ukuran sampel berikut. Dalam setiap kasus, berikan dugaan empiris kuasa uji. Apakah kuasanya tampak konvergen?</p>''',
    524: r'''		<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    525: r'''		<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    526: r'''		<li class="child"><a href="Normal.html" title="Pengujian pada Model Normal">2</a></li>''',
    527: r'''		<li class="child"><a href="Bernoulli.html" title="Pengujian pada Model Bernoulli">3</a></li>''',
    528: r'''		<li class="child"><a href="BivariateNormal.html" title="Pengujian pada Model Normal Dua Sampel">4</a></li>''',
    529: r'''		<li class="child"><a href="Likelihood.html" title="Uji Rasio Likelihood">5</a></li>''',
    531: r'''		<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    532: r'''		<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    535: r'''		<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    536: r'''		<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Kumpulan Data</a></li>''',
    537: r'''		<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


MATH_REPAIRS: dict[int, tuple[tuple[str, str], ...]] = {
    141: ((
        r'''\[ V = \sum_{j \in S} \frac{(O_j - e_j)^2}{e^j} \]''',
        r'''\[ V = \sum_{j \in S} \frac{(O_j - e_j)^2}{e_j} \]''',
    ),),
    240: ((
        r'''\[ V = \sum_{i \in J} \sum_{j \in T} \frac{(O_{i,j} - E_{i,j})^2}{E_{i,j}} \]''',
        r'''\[ V = \sum_{i \in S} \sum_{j \in T} \frac{(O_{i,j} - E_{i,j})^2}{E_{i,j}} \]''',
    ),),
    423: ((
        r'''\(P \approx 0\)''',
        r'''\(P \approx 4.04 \times 10^{-15}\)''',
    ),),
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/hypothesis/index.html": "index.html",
    "https://www.randomservices.org/random/hypothesis/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/hypothesis/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/hypothesis/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/hypothesis/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/hypothesis/Likelihood.html": "Likelihood.html",
    "https://www.randomservices.org/random/hypothesis/ChiSquare.html": "ChiSquare.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/point/Sufficient.html": "../point/Sufficient.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probability, Mathematical Statistics, and Stochastic Processes</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan korpus yang telah diterjemahkan ke edisi lokal, pengubahan tautan pelengkap menjadi HTTPS resmi, perbaikan dua indeks rumus Pearson, pembetulan nilai-<span class="math-inline">P</span> yang dibulatkan menjadi nol, perbaikan tata bahasa dan penomoran latihan, serta penambahan syarat regularitas, kualifikasi heuristik frekuensi harapan, dan persyaratan prapenetapan partisi; semuanya dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Penerjemahan dan rekayasa edisi dilakukan dengan OpenAI Codex gpt-5.6-sol, Ultra, atas instruksi pengguna. Seluruh kredit bagi sumber, penulis, dan kontributor manusia tetap dipertahankan.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Data Buffon, alfa, dan Michelson serta aplikasi dadu tetap berupa tautan ke permukaan resmi; tautan tersebut tidak menyatakan hak edisi ini untuk mendistribusikan ulang materi eksternal.</p>
\t</section>'''


def materialize_indentation(value: str) -> str:
    return re.sub(
        r"^(?:\\t)+",
        lambda match: "\t" * (len(match.group(0)) // 2),
        value,
        flags=re.MULTILINE,
    )


def apply_math_repairs(line_number: int, value: str) -> str:
    for old, new in MATH_REPAIRS.get(line_number, ()):
        if value.count(old) != 1:
            raise RuntimeError(
                f"line {line_number}: expected one exact defect, found {value.count(old)}: {old!r}"
            )
        value = value.replace(old, new, 1)
    return value


def render_template(line_number: int, source_line: str, template: str) -> str:
    spans = MATH_RE.findall(source_line)
    tokens = [int(value) for value in TOKEN_RE.findall(template)]
    if tokens != list(range(1, len(spans) + 1)):
        raise RuntimeError(
            f"line {line_number}: placeholders {tokens} do not match {len(spans)} protected spans"
        )
    rendered = materialize_indentation(template)
    for index, span in enumerate(spans, 1):
        rendered = rendered.replace(f"@@M{index}@@", span, 1)
    return rendered


def convert_href(raw_href: str) -> str:
    if raw_href.startswith("#"):
        return raw_href
    ancillary = re.fullmatch(r"JavaScript:openAncillary\('([^']+)'\)", raw_href, re.I)
    candidate = ancillary.group(1) if ancillary else raw_href
    absolute = urljoin(SOURCE_URL, candidate)
    base, fragment = urldefrag(absolute)
    result = LOCAL_URLS.get(
        base, base.replace("http://www.randomservices.org/", "https://www.randomservices.org/")
    )
    return result + (f"#{fragment}" if fragment else "")


def strip_notice(soup: BeautifulSoup) -> None:
    notice = soup.select_one("section.edition-notice[data-o006-edition-notice='v1']")
    if notice is None:
        raise RuntimeError("edition notice missing")
    notice.decompose()


def assert_topology(source_text: str, target_text: str) -> None:
    source = BeautifulSoup(source_text, "html.parser")
    target = BeautifulSoup(target_text, "html.parser")
    strip_notice(target)
    source_tags = source.find_all(True)
    target_tags = target.find_all(True)
    source_counts = Counter(tag.name for tag in source_tags)
    target_counts = Counter(tag.name for tag in target_tags)
    if target_counts != source_counts:
        raise RuntimeError(
            f"parsed topology mismatch: source={dict(source_counts)}, target={dict(target_counts)}"
        )
    if sum(source_counts.values()) != 417:
        raise RuntimeError(f"unexpected parsed element count: {sum(source_counts.values())}")
    if [tag.name for tag in target_tags] != [tag.name for tag in source_tags]:
        raise RuntimeError("parsed start-tag order changed")
    for selector, expected in (
        ("div.unit", 29),
        ("details", 12),
        ("summary", 12),
        ("h2,h3,h4", 18),
        ("table", 4),
        ("tr", 12),
        ("th", 30),
        ("td", 32),
        ("img", 4),
        ("figure", 0),
    ):
        if len(target.select(selector)) != expected:
            raise RuntimeError(f"topology count mismatch for {selector}")

    source_ids = [tag["id"] for tag in source.find_all(id=True)]
    target_ids = [tag["id"] for tag in target.find_all(id=True)]
    if len(source_ids) != len(set(source_ids)) or len(target_ids) != len(set(target_ids)):
        raise RuntimeError("duplicate native/additive ID")
    additive_ids = {
        "o006.random.hypothesis.chi-square.page",
        "o006.random.hypothesis.chi-square.topics",
        "o006.random.hypothesis.chi-square.unit.sim7",
    }
    if set(target_ids) != set(source_ids) | additive_ids:
        raise RuntimeError(
            f"ID mismatch: missing={sorted((set(source_ids) | additive_ids) - set(target_ids))}, "
            f"extra={sorted(set(target_ids) - (set(source_ids) | additive_ids))}"
        )
    if target.select_one("div.unit:not([id])") is not None:
        raise RuntimeError("addressless instructional unit remains")

    # Apart from the explicitly permitted translated/additive attributes, the
    # structural class inventory and disclosure states are byte-independent.
    if [tuple(tag.get("class", [])) for tag in target_tags] != [
        tuple(tag.get("class", [])) for tag in source_tags
    ]:
        raise RuntimeError("class topology changed")
    if [tag.has_attr("open") for tag in target.select("details")] != [
        tag.has_attr("open") for tag in source.select("details")
    ]:
        raise RuntimeError("disclosure state changed")


def assert_links(rendered: str) -> None:
    soup = BeautifulSoup(rendered, "html.parser")
    local_chapter = {
        "index.html",
        "Introduction.html",
        "Normal.html",
        "Bernoulli.html",
        "BivariateNormal.html",
        "Likelihood.html",
        "ChiSquare.html",
    }
    for tag in soup.find_all(["a", "link", "script", "img"]):
        attribute = "href" if tag.has_attr("href") else "src" if tag.has_attr("src") else None
        if attribute is None:
            continue
        value = tag[attribute]
        parsed = urlparse(value)
        if parsed.scheme:
            if parsed.scheme != "https":
                raise RuntimeError(f"non-HTTPS external target: {value}")
            continue
        if value.startswith("#"):
            fragment = value[1:]
            if fragment and soup.find(id=fragment) is None:
                raise RuntimeError(f"broken local fragment: {value}")
            continue
        relative, _, fragment = value.partition("#")
        resolved = (TARGET.parent / relative).resolve()
        authority_resolved = (SOURCE.parent / relative).resolve()
        if relative in local_chapter:
            pass
        elif resolved.suffix.lower() in {".html", ".htm"}:
            if not resolved.is_file():
                raise RuntimeError(f"missing completed local page: {value} -> {resolved}")
        elif not resolved.is_file() and not authority_resolved.is_file():
            raise RuntimeError(f"missing local dependency: {value}")
        if fragment:
            candidate = resolved if resolved.is_file() else authority_resolved
            if candidate.is_file() and candidate.suffix.lower() in {".html", ".htm"}:
                other = BeautifulSoup(candidate.read_text("utf-8"), "html.parser")
                if other.find(id=fragment) is None:
                    raise RuntimeError(f"missing cross-page fragment: {value}")


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    if len(source_bytes) != SOURCE_BYTES:
        raise RuntimeError(f"authority byte-count mismatch: {len(source_bytes)}")
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    source_text = source_bytes.decode("utf-8")
    lines = source_text.splitlines(keepends=True)
    if len(lines) != EXPECTED_SOURCE_LINES:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")

    expected_math_lines: list[str] = []
    for line_number, original in enumerate(lines, 1):
        ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
        body = original.removesuffix(ending)
        repaired = apply_math_repairs(line_number, body)
        expected_math_lines.append(repaired + ending)
        if line_number in T:
            body = render_template(line_number, repaired, T[line_number])
        else:
            body = repaired
        lines[line_number - 1] = body + ending

    rendered = "".join(lines)
    rendered = re.sub(
        r'href="([^"]+)"',
        lambda match: f'href="{convert_href(match.group(1))}"',
        rendered,
    )
    marker = "</footer>"
    if rendered.count(marker) != 1:
        raise RuntimeError("footer insertion point is not unique")
    rendered = rendered.replace(marker, materialize_indentation(EDITION_NOTICE) + "\n" + marker, 1)

    source_math = MATH_RE.findall(source_text)
    expected_math = MATH_RE.findall("".join(expected_math_lines))
    target_math = MATH_RE.findall(rendered)
    if len(source_math) != 433 or len(expected_math) != 433 or target_math != expected_math:
        raise RuntimeError(
            f"protected-math mismatch: source={len(source_math)}, "
            f"expected={len(expected_math)}, target={len(target_math)}"
        )
    source_align = RAW_ALIGN_RE.findall(source_text)
    target_align = RAW_ALIGN_RE.findall(rendered)
    if len(source_align) != 2 or target_align != source_align:
        raise RuntimeError(
            f"raw-align mismatch: source={len(source_align)}, target={len(target_align)}"
        )

    source_p = (len(re.findall(r"<p(?:\s|>)", source_text)), source_text.count("</p>"))
    target_p = (len(re.findall(r"<p(?:\s|>)", rendered)), rendered.count("</p>"))
    if source_p != (72, 72) or target_p != (75, 75):
        raise RuntimeError(f"paragraph-tag inventory mismatch: source={source_p}, target={target_p}")
    source_a = (len(re.findall(r"<a(?:\s|>)", source_text)), source_text.count("</a>"))
    target_a = (len(re.findall(r"<a(?:\s|>)", rendered)), rendered.count("</a>"))
    if source_a != (61, 61) or target_a != (65, 65):
        raise RuntimeError(f"anchor-tag inventory mismatch: source={source_a}, target={target_a}")

    assert_topology(source_text, rendered)
    assert_links(rendered)

    for required in (
        'lang="id-ID"',
        'href="index.html"',
        'href="Introduction.html"',
        'href="Normal.html"',
        'href="Bernoulli.html"',
        'href="BivariateNormal.html"',
        'href="Likelihood.html"',
        'href="../sample/CLT.html"',
        'href="../point/Sufficient.html#ber"',
        r'''\[ V = \sum_{j \in S} \frac{(O_j - e_j)^2}{e_j} \]''',
        r'''\[ V = \sum_{i \in S} \sum_{j \in T} \frac{(O_{i,j} - E_{i,j})^2}{E_{i,j}} \]''',
        r'''\(P \approx 4.04 \times 10^{-15}\)''',
        "bukan teorema",
        "parameterisasi dapat diidentifikasi dan regular",
        "partisi harus ditetapkan sebelum memeriksa data yang sama",
        "empat latihan sebelumnya",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        'data-o006-edition-notice="v1"',
        'id="o006.random.hypothesis.chi-square.unit.sim7"',
    ):
        if required not in rendered:
            raise RuntimeError(f"required translated/corrected surface missing: {required}")

    for forbidden in (
        'lang="en"',
        "JavaScript:openAncillary",
        ">Details:<",
        "Expand Details",
        "Contract Details",
        ">Hypothesis Testing<",
        ">Chi-Square Tests<",
        ">Computational Exercises<",
        ">Data Analysis Exercises<",
        ">Simulation Exercises<",
        ">Heads<",
        ">Tails<",
        ">Score<",
        ">Frequency<",
        ">Male<",
        ">Female<",
        ">Apps<",
        ">Data Sets<",
        ">Biographies<",
        r'''\frac{(O_j - e_j)^2}{e^j}''',
        r'''\sum_{i \in J} \sum_{j \in T}''',
        r'''\(P \approx 0\)''',
        "previous three exercises",
        "https://www.randomservices.org/random/hypothesis/",
    ):
        if forbidden in rendered:
            raise RuntimeError(f"unresolved reader/source defect remains: {forbidden}")

    controls = [ch for ch in rendered if ord(ch) < 32 and ch not in "\t\r\n"]
    if controls:
        raise RuntimeError(f"forbidden control characters: {sorted(map(ord, controls))}")

    output = rendered.encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(output)
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: "
        f"{len(output)} bytes / sha256 {hashlib.sha256(output).hexdigest()} / "
        "417 core elements / 29 units / 12 disclosures / 4 tables / "
        "433 protected TeX spans / 2 raw align environments"
    )


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
