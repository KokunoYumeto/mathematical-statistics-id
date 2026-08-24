#!/usr/bin/env python3
"""Create the bounded id-ID two-sample/bivariate-normal interval target."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "interval" / "BivariateNormal.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "interval" / "BivariateNormal.html"
SOURCE_URL = "https://www.randomservices.org/random/interval/BivariateNormal.html"
SOURCE_BYTES = 30167
SOURCE_SHA256 = "fde8da8c5d1e7b7d583f9eb47dac719234f1a63072c0333bdb815c117078211a"
EXPECTED_SOURCE_LINES = 409

MATH_RE = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")
TOKEN_RE = re.compile(r"@@M(\d+)@@")


# Every translated line is tied to its frozen authority line. Mathematical
# spans are inserted in source order after the small proved repair set below.
T: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''	<title>Pendugaan dalam Model Normal Dua Sampel</title>''',
    9: r'''	<meta name="keywords" content="probabilitas, statistika, pendugaan himpunan, pendugaan interval, model normal dua sampel, selisih rata-rata, rasio varians, model normal bivariat, tingkat kepercayaan">''',
    33: r'''		<li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    34: r'''		<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    35: r'''		<li class="child"><a href="Normal.html" title="Pendugaan dalam Model Normal">2</a></li>''',
    36: r'''		<li class="child"><a href="Bernoulli.html" title="Pendugaan dalam Model Bernoulli">3</a></li>''',
    38: r'''		<li class="child"><a href="Bayes.html" title="Pendugaan Interval Bayes">5</a></li>''',
    39: r'''		<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    40: r'''		<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    42: r'''	<h2 id="o006.random.interval.bivariate-normal.page">4. Pendugaan dalam Model Normal Dua Sampel</h2>''',
    45: r'''<p>Seperti telah kita catat, <a href="../special/Normal.html">distribusi normal</a> mungkin merupakan distribusi terpenting dalam statistika matematis, antara lain karena <a href="../sample/CLT.html">teorema limit pusat</a>. Sebagai konsekuensi teorema ini, besaran terukur yang mengalami banyak galat acak kecil akan memiliki distribusi yang setidaknya mendekati normal. Variabel semacam itu terdapat di mana-mana dalam eksperimen statistik, dalam bidang yang beragam mulai dari ilmu fisika dan biologi hingga ilmu sosial.</p>''',
    47: r'''<p>Dalam bagian ini, kita mempelajari masalah pendugaan pada model normal dua sampel dan model normal bivariat. Bagian ini sejajar dengan bagian mengenai <a href="../hypothesis/BivariateNormal.html">uji dalam model normal dua sampel</a> pada bab <a href="../hypothesis/Introduction.html">pengujian hipotesis</a>.</p>''',
    49: r'''<h3 id="two">Model Normal Dua Sampel</h3>''',
    51: r'''<h4 id="pre">Pendahuluan</h4>''',
    53: r'''<p>Misalkan @@M1@@ adalah sampel acak berukuran @@M2@@ dari <a href="../special/Normal.html">distribusi normal</a> dengan <a href="../expect/Properties.html">rata-rata</a> @@M3@@ dan <a href="../expect/Variance.html">simpangan baku</a> @@M4@@, dan misalkan @@M5@@ adalah sampel acak berukuran @@M6@@ dari distribusi normal dengan rata-rata @@M7@@ dan simpangan baku @@M8@@. Selain itu, misalkan sampel @@M9@@ dan @@M10@@ <a href="../prob/Independence.html">saling bebas</a>. Biasanya parameter-parameternya tidak diketahui, sehingga ruang parameter bagi vektor parameter @@M11@@ adalah @@M12@@.</p>''',
    55: r'''<p>Situasi seperti ini sering muncul ketika variabel acak menyatakan suatu pengukuran yang diminati pada objek-objek dalam populasi, sedangkan kedua sampel bersesuaian dengan dua perlakuan berbeda. Sebagai contoh, kita mungkin tertarik pada tekanan darah suatu populasi pasien. Vektor @@M1@@ mencatat tekanan darah sampel kontrol, sedangkan vektor @@M2@@ mencatat tekanan darah sampel yang menerima obat baru. Demikian pula, kita mungkin tertarik pada hasil panen jagung per ekar. Vektor @@M3@@ mencatat hasil sampel yang menerima satu jenis pupuk, sedangkan vektor @@M4@@ mencatat hasil sampel yang menerima jenis pupuk lain.</p>''',
    57: r'''<p>Biasanya perhatian kita tertuju pada perbandingan parameter kedua distribusi asal sampel, baik rata-rata maupun simpangan bakunya. Dalam bagian ini, kita membangun interval kepercayaan bagi selisih rata-rata distribusi @@M1@@ dan bagi rasio varians distribusi @@M2@@. Seperti pada masalah pendugaan sebelumnya, konstruksinya bergantung pada penemuan <a href="Introduction.html">variabel pivot</a> yang sesuai.</p>''',
    60: r'''	<p class="dfn">Untuk sampel generik @@M1@@ berukuran sekurang-kurangnya dua dari suatu distribusi dengan rata-rata @@M2@@, kita menggunakan notasi baku untuk <a href="../sample/Mean.html">rata-rata sampel</a> dan <a href="../sample/Variance.html">varians sampel</a>.''',
    67: r'''<p>Kita juga perlu mengingat <a href="../sample/Normal.html">sifat-sifat khusus</a> statistik ini ketika distribusi asal sampelnya normal. Distribusi pivot khusus yang berperan mendasar dalam bagian ini adalah distribusi <a href="../special/Normal.html">normal baku</a>, <a href="../special/Student.html">@@M1@@ Student</a>, dan <a href="../special/Fisher.html">Fisher @@M2@@</a>. Untuk membangun dugaan interval, kita memerlukan <a href="../dist/CDF.html">kuantil</a> distribusi-distribusi tersebut. Kuantil dapat dihitung menggunakan <a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">aplikasi kuantil</a> atau sebagian besar perangkat lunak matematika dan statistika. Berikut notasi yang kita gunakan:</p>''',
    70: r'''	<p class="dfn">Misalkan @@M1@@ serta @@M2@@.</p>''',
    72: r'''		<li>@@M1@@ menyatakan kuantil berorde @@M2@@ dari distribusi normal baku.</li>''',
    73: r'''		<li>@@M1@@ menyatakan kuantil berorde @@M2@@ dari distribusi @@M3@@ Student dengan @@M4@@ derajat kebebasan.</li>''',
    74: r'''		<li>@@M1@@ menyatakan kuantil berorde @@M2@@ dari distribusi Fisher @@M3@@ dengan @@M4@@ derajat kebebasan pada pembilang dan @@M5@@ derajat kebebasan pada penyebut.</li>''',
    78: r'''<p>Ingat bahwa berdasarkan simetri, @@M1@@ dan @@M2@@ untuk @@M3@@ serta @@M4@@. Untuk distribusi Fisher, hubungan resiprokal yang tepat menukar derajat kebebasan: @@M5@@.</p>''',
    80: r'''<h4 id="knw">Interval Kepercayaan bagi Selisih Rata-Rata dengan Varians Diketahui</h4>''',
    82: r'''<p>Pertama-tama kita membangun interval kepercayaan bagi @@M1@@ dengan asumsi varians distribusi @@M2@@ dan @@M3@@ diketahui. Asumsi ini tidak selalu dibuat-buat. Seperti dalam <a href="Normal.html">model normal satu sampel</a>, varians kadang-kadang stabil sehingga setidaknya diketahui secara hampiran, sedangkan rata-rata berubah akibat perlakuan yang berbeda. Ingatlah terlebih dahulu fakta dasar berikut.</p>''',
    85: r'''	<p class="math">Selisih rata-rata sampel @@M1@@ berdistribusi normal dengan rata-rata @@M2@@ dan varians @@M3@@. Oleh karena itu, skor baku selisih rata-rata sampel''',
    87: r'''	mempunyai distribusi normal baku. Jadi, variabel ini merupakan variabel pivot bagi @@M1@@ ketika @@M2@@ diketahui.</p>''',
    90: r'''<p>Interval kepercayaan dasar serta batas bawah dan batas atas kini mudah dibangun.</p>''',
    93: r'''	<p class="math">Untuk @@M1@@,</p>''',
    95: r'''		<li>@@M1@@ adalah interval kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    96: r'''		<li>@@M1@@ adalah batas bawah kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    97: r'''		<li>@@M1@@ adalah batas atas kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    100: r'''		<summary>Rincian:</summary>''',
    101: r'''		<p>Variabel @@M1@@ yang diberikan pada <a href="#knw1" class="ref"></a> mempunyai distribusi normal baku. Karena itu, menurut definisi kuantil, setiap kejadian berikut mempunyai peluang @@M2@@:</p>''',
    107: r'''		<p>Dalam setiap kasus, menyelesaikan pertidaksamaan terhadap @@M1@@ menghasilkan pernyataan yang dimaksud.</p>''',
    111: r'''<p>Interval dua sisi pada bagian (a) adalah <dfn>interval simetris</dfn> yang menempatkan @@M1@@ pada masing-masing ekor distribusi normal baku. Seperti biasa, kita dapat membangun interval dua sisi yang lebih umum dengan membagi @@M2@@ di antara ekor kiri dan kanan dengan cara apa pun yang diinginkan.</p>''',
    115: r'''	<p class="math">Untuk setiap @@M1@@, sebuah interval kepercayaan bertingkat @@M2@@ bagi @@M3@@ adalah''',
    118: r'''		<li>@@M1@@ menghasilkan interval dua sisi simetris.</li>''',
    119: r'''		<li>@@M1@@ menghasilkan interval dengan batas bawah kepercayaan.</li>''',
    120: r'''		<li>@@M1@@ menghasilkan interval dengan batas atas kepercayaan.</li>''',
    123: r'''		<summary>Rincian:</summary>''',
    124: r'''		<p>Dari distribusi variabel pivot dan definisi fungsi kuantil,''',
    126: r'''		Dengan menyelesaikan pertidaksamaan terhadap @@M1@@, diperoleh interval kepercayaan tersebut.</p>''',
    130: r'''<p>Teorema berikut memberikan beberapa sifat dasar panjang interval ini.</p>''',
    133: r'''	<p class="math">Panjang deterministik interval kepercayaan dua sisi umum adalah''',
    136: r'''		<li>@@M1@@ menurun sebagai fungsi @@M2@@ dan juga sebagai fungsi @@M3@@.</li>''',
    137: r'''		<li>@@M1@@ meningkat sebagai fungsi @@M2@@ dan juga sebagai fungsi @@M3@@.</li>''',
    138: r'''		<li>@@M1@@ menurun sebagai fungsi @@M2@@, sehingga meningkat sebagai fungsi tingkat kepercayaan.</li>''',
    139: r'''		<li>Sebagai fungsi @@M1@@, @@M2@@ mula-mula menurun lalu meningkat, dengan nilai minimum pada @@M3@@.</li>''',
    143: r'''<p>Bagian (a) berarti bahwa dugaan dapat dibuat lebih presisi dengan memperbesar salah satu atau kedua ukuran sampel. Bagian (b) berarti bahwa dugaan menjadi kurang presisi ketika varians salah satu distribusi meningkat. Bagian (c) menyatakan kompromi yang telah kita lihat sebelumnya: jika hal-hal lain tetap, tingkat kepercayaan hanya dapat dinaikkan dengan mengurangi presisi. Bagian (d) berarti bahwa interval simetris berekor sama mempunyai panjang minimum dalam keluarga interval dua sisi yang dibangun dari pembagian peluang ekor tersebut.</p>''',
    145: r'''<h4 id="unk">Interval Kepercayaan bagi Selisih Rata-Rata dengan Varians Tidak Diketahui</h4>''',
    147: r'''<p>Metode berikutnya membangun interval kepercayaan bagi selisih rata-rata @@M1@@ tanpa perlu mengetahui simpangan baku @@M2@@ dan @@M3@@. Ada harga yang harus dibayar: kita mengasumsikan simpangan baku keduanya sama, @@M4@@, tetapi nilai bersama itu tidak diketahui. Kedua ukuran sampel harus sedikitnya dua. Asumsi kesamaan ini masuk akal jika terdapat variabilitas inheren pada variabel pengukuran yang tidak berubah walaupun perlakuan berbeda diterapkan pada objek-objek dalam populasi. Kita perlu mengingat beberapa fakta dasar dari pembahasan <a href="../sample/Normal.html">sifat-sifat khusus sampel normal</a>.</p>''',
    150: r'''	<p class="math"><dfn>Penduga gabungan</dfn> bagi varians bersama @@M1@@ adalah''',
    152: r'''	Variabel acak''',
    154: r'''	mempunyai <a href="../special/Student.html">distribusi @@M1@@ Student</a> dengan @@M2@@ derajat kebebasan.</p>''',
    157: r'''<p>Perhatikan bahwa @@M1@@ merupakan rata-rata tertimbang kedua varians sampel, dengan derajat kebebasan sebagai bobotnya. Perhatikan pula bahwa @@M2@@ adalah variabel pivot bagi @@M3@@, sehingga interval kepercayaan bagi @@M4@@ dapat dibangun dengan cara biasa.</p>''',
    160: r'''	<p class="math">Untuk @@M1@@,</p>''',
    162: r'''		<li>@@M1@@ adalah interval kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    163: r'''		<li>@@M1@@ adalah batas bawah kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    164: r'''		<li>@@M1@@ adalah batas atas kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    167: r'''		<summary>Rincian:</summary>''',
    168: r'''		<p>Variabel @@M1@@ yang diberikan pada <a href="#unk1" class="ref"></a> mempunyai distribusi t Student dengan derajat kebebasan sebanyak jumlah kedua ukuran sampel dikurangi dua. Karena itu, menurut definisi kuantil, setiap kejadian berikut mempunyai peluang @@M2@@:</p>''',
    174: r'''		<p>Dalam setiap kasus, menyelesaikan pertidaksamaan terhadap @@M1@@ menghasilkan pernyataan yang dimaksud.</p>''',
    178: r'''<p>Interval dua sisi pada bagian (a) adalah <dfn>interval simetris</dfn> yang menempatkan @@M1@@ pada masing-masing ekor distribusi @@M2@@ Student. Seperti biasa, kita dapat membangun interval dua sisi yang lebih umum dengan membagi @@M3@@ di antara ekor kiri dan kanan dengan cara apa pun yang diinginkan.</p>''',
    181: r'''	<p class="math">Untuk setiap @@M1@@, sebuah interval kepercayaan bertingkat @@M2@@ bagi @@M3@@ adalah''',
    184: r'''		<li>@@M1@@ menghasilkan interval dua sisi simetris.</li>''',
    185: r'''		<li>@@M1@@ menghasilkan interval dengan batas bawah kepercayaan.</li>''',
    186: r'''		<li>@@M1@@ menghasilkan interval dengan batas atas kepercayaan.</li>''',
    189: r'''		<summary>Rincian:</summary>''',
    190: r'''		<p>Dari distribusi variabel pivot dan definisi fungsi kuantil,''',
    192: r'''		Dengan menyelesaikan pertidaksamaan terhadap @@M1@@, diperoleh interval kepercayaan tersebut.</p>''',
    196: r'''<p>Hasil berikut membahas panjang interval dua sisi umum.</p>''',
    198: r'''<div class="unit" id="o006.random.interval.bivariate-normal.unit-10">''',
    199: r'''	<p class="math">Panjang acak interval dua sisi di atas adalah''',
    202: r'''		<li>@@M1@@ menurun sebagai fungsi @@M2@@, sehingga meningkat sebagai fungsi tingkat kepercayaan.</li>''',
    203: r'''		<li>Sebagai fungsi @@M1@@, @@M2@@ mula-mula menurun lalu meningkat, dengan nilai minimum pada @@M3@@.</li>''',
    207: r'''<p>Seperti dalam kasus varians diketahui, bagian (a) berarti bahwa jika hal-hal lain tetap, tingkat kepercayaan hanya dapat dinaikkan dengan mengurangi presisi. Bagian (b) berarti bahwa interval simetris berekor sama mempunyai panjang minimum dalam keluarga interval dua sisi ini.</p>''',
    209: r'''<h4 id="rat">Interval Kepercayaan bagi Rasio Varians</h4>''',
    211: r'''<p>Konstruksi berikut menghasilkan dugaan interval bagi rasio varians @@M1@@, atau setelah mengambil akar kuadrat, bagi rasio simpangan baku @@M2@@. Kedua ukuran sampel harus sedikitnya dua. Sekali lagi, kita perlu mengingat beberapa fakta dasar dari pembahasan <a href="../sample/Normal.html">sifat-sifat khusus</a> sampel acak dari distribusi normal.</p>''',
    214: r'''	<p class="math">Rasio''',
    216: r'''	mempunyai <a href="../special/Fisher.html">distribusi @@M1@@</a> dengan @@M2@@ derajat kebebasan pada pembilang dan @@M3@@ derajat kebebasan pada penyebut. Karena itu, variabel ini merupakan variabel pivot bagi @@M4@@.</p>''',
    219: r'''<p>Variabel pivot @@M1@@ dapat digunakan untuk membangun interval kepercayaan bagi @@M2@@ dengan cara biasa.</p>''',
    222: r'''	<p class="math">Untuk @@M1@@,</p>''',
    224: r'''		<li>@@M1@@ adalah interval kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    225: r'''		<li>@@M1@@ adalah batas bawah kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    226: r'''		<li>@@M1@@ adalah batas atas kepercayaan bertingkat @@M2@@ bagi @@M3@@.</li>''',
    229: r'''		<summary>Rincian:</summary>''',
    230: r'''		<p>Variabel @@M1@@ yang diberikan pada <a href="#rat1" class="ref"></a> mempunyai distribusi @@M2@@ dengan @@M3@@ derajat kebebasan pada pembilang dan @@M4@@ derajat kebebasan pada penyebut. Karena itu, menurut definisi kuantil, setiap kejadian berikut mempunyai peluang @@M5@@:</p>''',
    236: r'''		<p>Dalam setiap kasus, menyelesaikan pertidaksamaan terhadap @@M1@@ menghasilkan pernyataan yang dimaksud.</p>''',
    240: r'''<p>Interval kepercayaan dua sisi pada bagian (a) adalah interval kepercayaan <dfn>berekor sama</dfn> dan merupakan interval yang lazim digunakan. Namun, seperti biasa, kita dapat membagi @@M1@@ di antara ekor kiri dan kanan distribusi variabel pivot dengan cara apa pun yang diinginkan.</p>''',
    243: r'''	<p class="math">Untuk setiap @@M1@@, sebuah himpunan kepercayaan bertingkat @@M2@@ bagi @@M3@@ adalah''',
    246: r'''		<li>@@M1@@ menghasilkan interval dua sisi berekor sama.</li>''',
    247: r'''		<li>@@M1@@ menghasilkan interval dengan batas atas kepercayaan.</li>''',
    248: r'''		<li>@@M1@@ menghasilkan interval dengan batas bawah kepercayaan.</li>''',
    251: r'''		<summary>Rincian:</summary>''',
    252: r'''		<p>Dari variabel pivot @@M1@@ dan definisi fungsi kuantil,''',
    254: r'''		Dengan menyelesaikan pertidaksamaan terhadap @@M1@@, diperoleh interval kepercayaan tersebut.</p>''',
    258: r'''<p>Panjang interval kepercayaan umum dibahas berikutnya.</p>''',
    261: r'''	<p class="math">Panjang acak interval kepercayaan dua sisi umum di atas adalah''',
    263: r'''	Dengan asumsi @@M1@@ dan @@M2@@,</p>''',
    265: r'''		<li>@@M1@@ menurun sebagai fungsi @@M2@@, sehingga meningkat sebagai fungsi tingkat kepercayaan.</li>''',
    266: r'''		<li>@@M1@@</li>''',
    267: r'''		<li>@@M1@@</li>''',
    270: r'''		<summary>Rincian:</summary>''',
    271: r'''		<p>Bagian (b) dan (c) mengikuti karena @@M1@@ mempunyai distribusi @@M2@@ dengan @@M3@@ derajat kebebasan pada pembilang dan @@M4@@ derajat kebebasan pada penyebut.</p>''',
    275: r'''<p>Secara ideal, kita mungkin ingin memilih @@M1@@ yang meminimalkan @@M2@@. Namun, masalah ini sulit secara komputasional. Untungnya, interval berekor sama dengan @@M3@@ tidak terlalu jauh dari optimal ketika ukuran sampel @@M4@@ dan @@M5@@ besar; pernyataan ini bukan klaim optimalitas universal.</p>''',
    277: r'''<h3 id="biv">Pendugaan dalam Model Normal Bivariat</h3>''',
    279: r'''<p>Dalam subbagian ini, kita meninjau model yang sepintas mirip dengan model normal dua sampel, tetapi sebenarnya jauh lebih sederhana. Misalkan''',
    281: r'''adalah sampel acak berukuran @@M1@@ dari <a href="../special/MultiNormal.html">distribusi normal bivariat</a> suatu vektor acak @@M2@@, dengan @@M3@@, @@M4@@, @@M5@@, @@M6@@, dan @@M7@@.</p>''',
    283: r'''<p>Jadi, alih-alih mempunyai <em>sepasang sampel</em>, kita mempunyai <em>sampel pasangan</em>. Model seperti ini sering muncul dalam <dfn>eksperimen sebelum dan sesudah</dfn>, ketika suatu pengukuran yang diminati dicatat bagi sampel berukuran @@M1@@, baik sebelum maupun sesudah suatu perlakuan. Sebagai contoh, kita dapat mencatat tekanan darah sampel @@M2@@ pasien sebelum dan sesudah pemberian obat tertentu. Hal pentingnya ialah bahwa dalam model ini, @@M3@@ dan @@M4@@ merupakan pengukuran pada objek dasar yang sama dalam sampel. Seperti pada model normal dua sampel, perhatian biasanya tertuju pada pendugaan selisih rata-rata.</p>''',
    285: r'''<p>Untuk ukuran sampel sedikitnya dua, kita menggunakan notasi pada definisi <a href="#stats" class="ref"></a> bagi rata-rata dan varians sampel @@M1@@ serta @@M2@@. Ingat pula bahwa <a href="../sample/Covariance.html">kovarians sampel</a> dari @@M3@@ adalah''',
    287: r'''(jangan disamakan dengan penduga gabungan simpangan baku pada model dua sampel).</p>''',
    290: r'''	<p class="math">Vektor selisih @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi @@M3@@, yang berdistribusi normal dengan</p>''',
    298: r'''	<p class="math">Rata-rata sampel dan varians sampel dari sampel selisih diberikan oleh</p>''',
    305: r'''<p>Jadi, sampel selisih @@M1@@ memenuhi model normal bagi satu variabel. Bagian mengenai <a href="Normal.html">pendugaan dalam model normal</a> dapat digunakan untuk memperoleh himpunan dan interval kepercayaan bagi parameter @@M2@@.</p>''',
    308: r'''	<p class="math">Dalam konteks subbagian ini, misalkan @@M1@@ dan @@M2@@ saling bebas. Secara matematis, situasi ini memenuhi kedua model—model normal dua sampel dan model normal bivariat. Prosedur mana yang lebih baik untuk menduga selisih rata-rata @@M3@@?</p>''',
    310: r'''		<li>Jika simpangan baku @@M1@@ dan @@M2@@ diketahui.</li>''',
    311: r'''		<li>Jika simpangan baku @@M1@@ dan @@M2@@ tidak diketahui.</li>''',
    314: r'''		<summary>Rincian:</summary>''',
    316: r'''			<li>Kedua metode ekuivalen.</li>''',
    317: r'''			<li>Tidak ada urutan universal. Jika kedua simpangan baku sama sehingga prosedur gabungan dua sampel sah, prosedur dua sampel memakai dua kali ukuran sampel dikurangi dua derajat kebebasan dan lebih efisien daripada prosedur selisih berpasangan, yang memakai ukuran sampel dikurangi satu derajat kebebasan. Jika kedua simpangan baku berbeda, prosedur gabungan tersebut tidak sah, sedangkan prosedur selisih berpasangan tetap eksak bagi pasangan normal.</li>''',
    322: r'''<p>Walaupun konteks pada <a href="#biv3" class="ref"></a> memenuhi kedua model secara <em>matematis</em>, hanya satu model yang masuk akal dalam suatu masalah nyata. Sekali lagi, hal pentingnya ialah apakah @@M1@@ masuk akal sebagai pasangan variabel acak (pengukuran) yang berkaitan dengan satu objek tertentu dalam sampel.</p>''',
    324: r'''<h3 id="exe">Latihan Komputasi</h3>''',
    327: r'''	<p class="math">Sebuah obat baru sedang dikembangkan untuk menurunkan kadar suatu zat kimia dalam darah. Sebanyak 36 pasien diberi plasebo, sedangkan 49 pasien diberi obat tersebut. Misalkan @@M1@@ menyatakan pengukuran pada pasien yang menerima plasebo dan @@M2@@ pengukuran pada pasien yang menerima obat, dalam mg. Statistiknya adalah @@M3@@, @@M4@@, @@M5@@, dan @@M6@@.</p>''',
    329: r'''		<li>Hitung interval kepercayaan 90% bagi @@M1@@.</li>''',
    330: r'''		<li>Dengan asumsi @@M1@@, hitung interval kepercayaan 90% bagi @@M2@@.</li>''',
    331: r'''		<li>Berdasarkan bagian (a), apakah asumsi @@M1@@ masuk akal?</li>''',
    332: r'''		<li>Berdasarkan bagian (b), apakah obat tersebut efektif?</li>''',
    335: r'''		<summary>Rincian:</summary>''',
    339: r'''			<li>Mungkin tidak.</li>''',
    340: r'''			<li>Ya.</li>''',
    346: r'''	<p class="math">Sebuah perusahaan mengklaim bahwa suplemen herbal meningkatkan kecerdasan. Sampel sebanyak 25 orang menjalani tes IQ baku sebelum dan sesudah mengonsumsi suplemen tersebut. Misalkan @@M1@@ menyatakan IQ subjek sebelum mengonsumsi suplemen dan @@M2@@ IQ subjek sesudahnya. Statistik sebelum dan sesudah adalah @@M3@@, @@M4@@, @@M5@@, @@M6@@, dan @@M7@@. Apakah Anda mempercayai klaim perusahaan tersebut?</p>''',
    348: r'''		<summary>Rincian:</summary>''',
    349: r'''		<p>Batas bawah kepercayaan 90% bagi selisih IQ adalah 2,672. Mungkin terdapat peningkatan yang sangat kecil.</p>''',
    354: r'''	<p class="stat">Dalam <a href="JavaScript:openAncillary('../data/Iris.html')" class="ancillary">data iris Fisher</a>, misalkan @@M1@@ menyatakan panjang mahkota bunga iris Versicolor dan @@M2@@ panjang mahkota bunga iris Virginica.</p>''',
    356: r'''		<li>Hitung interval kepercayaan 90% bagi @@M1@@.</li>''',
    357: r'''		<li>Dengan asumsi @@M1@@, hitung interval kepercayaan 90% bagi @@M2@@.</li>''',
    358: r'''		<li>Berdasarkan bagian (a), apakah asumsi @@M1@@ masuk akal?</li>''',
    361: r'''		<summary>Rincian:</summary>''',
    365: r'''			<li>Ya.</li>''',
    371: r'''	<p class="math">Sebuah pabrik mempunyai dua mesin yang menghasilkan batang bundar dengan diameter kritis, dalam cm. Misalkan @@M1@@ menyatakan diameter batang dari mesin pertama dan @@M2@@ diameter batang dari mesin kedua. Sampel 100 batang dari mesin pertama mempunyai rata-rata 10,3 dan simpangan baku 1,2. Sampel 100 batang dari mesin kedua mempunyai rata-rata 9,8 dan simpangan baku 1,6.</p>''',
    373: r'''		<li>Hitung interval kepercayaan 90% bagi @@M1@@.</li>''',
    374: r'''		<li>Dengan asumsi @@M1@@, hitung interval kepercayaan 90% bagi @@M2@@.</li>''',
    375: r'''		<li>Berdasarkan bagian (a), apakah asumsi @@M1@@ masuk akal?</li>''',
    378: r'''		<summary>Rincian:</summary>''',
    382: r'''			<li>Mungkin tidak.</li>''',
    390: r'''		<li class="parent"><a href="index.html">7. Pendugaan Himpunan</a></li>''',
    391: r'''		<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    392: r'''		<li class="child"><a href="Normal.html" title="Pendugaan dalam Model Normal">2</a></li>''',
    393: r'''		<li class="child"><a href="Bernoulli.html" title="Pendugaan dalam Model Bernoulli">3</a></li>''',
    395: r'''		<li class="child"><a href="Bayes.html" title="Pendugaan Interval Bayes">5</a></li>''',
    396: r'''		<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    397: r'''		<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    400: r'''		<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    401: r'''		<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    402: r'''		<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


# Exact, occurrence-bound mathematical repairs proved in the source audit.
MATH_REPAIRS: dict[int, tuple[tuple[str, str], ...]] = {
    74: ((r'''\( f \)''', r'''\( F \)'''),),
    78: ((r'''\( F \)''', r'''\(f_{j,k}(p) = 1 / f_{k,j}(1 - p)\)'''),),
    101: ((r'''\( T \)''', r'''\( Z \)'''),),
    104: ((r'''\( \left\{Z \ge z(1 - \alpha)\right\} \)''', r'''\( \left\{Z \le z(1 - \alpha)\right\} \)'''),),
    105: ((r'''\( \left\{Z \le -z(1 - \alpha)\right\} \)''', r'''\( \left\{Z \ge -z(1 - \alpha)\right\} \)'''),),
    171: ((r'''\( \left\{T \ge t_{m+n-2}(1 - \alpha)\right\} \)''', r'''\( \left\{T \le t_{m+n-2}(1 - \alpha)\right\} \)'''),),
    172: ((r'''\( \left\{T \le -t_{m+n-2}(1 - \alpha)\right\} \)''', r'''\( \left\{T \ge -t_{m+n-2}(1 - \alpha)\right\} \)'''),),
    225: ((r'''\( f_{m-1, n-1}(1 - \alpha) \frac{S^2(\bs{Y})}{S^2(\bs{X})} \)''', r'''\( f_{m-1, n-1}(\alpha) \frac{S^2(\bs{Y})}{S^2(\bs{X})} \)'''),),
    226: (
        (r'''\(f_{m-1, n-1}(\alpha) \frac{S^2(\bs{Y})}{S^2(\bs{X})} \)''', r'''\(f_{m-1, n-1}(1 - \alpha) \frac{S^2(\bs{Y})}{S^2(\bs{X})} \)'''),
        (r'''\( \nu - \mu \)''', r'''\( \tau^2 / \sigma^2 \)'''),
    ),
    233: ((r'''\( \left\{U \ge f_{m-1,n-1}(1 - \alpha)\right\} \)''', r'''\( \left\{U \ge f_{m-1,n-1}(\alpha)\right\} \)'''),),
    234: ((r'''\( \left\{U \le f{m-1,n-1}(\alpha)\right\} \)''', r'''\( \left\{U \le f_{m-1,n-1}(1 - \alpha)\right\} \)'''),),
    253: ((r'''\[ \P \left[ f_{m-1,n-1}(\alpha - p \, \alpha) \lt \frac{S^2(\bs{X}, \mu) \tau^2}{S^2(\bs{Y}, \nu) \sigma^2} \lt f_{m-1,n-1}(1 - p \,\alpha) \right] = 1 - \alpha \]''', r'''\[ \P \left[ f_{m-1,n-1}(\alpha - p \, \alpha) \lt \frac{S^2(\bs{X}) \tau^2}{S^2(\bs{Y}) \sigma^2} \lt f_{m-1,n-1}(1 - p \,\alpha) \right] = 1 - \alpha \]'''),),
    266: ((r'''\( \E(L) = \frac{\tau^2}{\sigma^2} \frac{m - 1}{m - 3} \)''', r'''\( \E(L) = \left[f_{m-1,n-1}(1 - p \alpha) - f_{m-1,n-1}(\alpha - p \alpha)\right] \frac{\tau^2}{\sigma^2} \frac{m - 1}{m - 3} \)'''),),
    267: ((r'''\( \var(L) = 2 \frac{\tau^4}{\sigma^4} \left(\frac{m - 1}{m - 3}\right)^2 \frac{m + n - 4}{(n - 1) (m - 5)} \)''', r'''\( \var(L) = \left[f_{m-1,n-1}(1 - p \alpha) - f_{m-1,n-1}(\alpha - p \alpha)\right]^2 2 \frac{\tau^4}{\sigma^4} \left(\frac{m - 1}{m - 3}\right)^2 \frac{m + n - 4}{(n - 1) (m - 5)} \)'''),),
    271: ((r'''\( \frac{\sigma^2}{\tau^2} \frac{S^2(\bs{Y})}{S^2(\bs{X})^2} \)''', r'''\( \frac{\sigma^2}{\tau^2} \frac{S^2(\bs{Y})}{S^2(\bs{X})} \)'''),),
    337: ((r'''\((1.149, 1.936)\)''', r'''\((1.148, 1.937)\)'''),),
    338: ((r'''\((-24.834, -23.166)\)''', r'''\((-25.917, -22.083)\)'''),),
    380: ((r'''\((1.127, 1.578)\)''', r'''\((1.129, 1.574)\)'''),),
    381: ((r'''\((0.832, 0.168)\)''', r'''\((-0.831, -0.169)\)'''),),
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/interval/index.html": "index.html",
    "https://www.randomservices.org/random/interval/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/interval/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/interval/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/interval/Bayes.html": "Bayes.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/sample/Mean.html": "../sample/Mean.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
    "https://www.randomservices.org/random/sample/Normal.html": "../sample/Normal.html",
    "https://www.randomservices.org/random/sample/Covariance.html": "../sample/Covariance.html",
    "https://www.randomservices.org/random/hypothesis/Introduction.html": "../hypothesis/Introduction.html",
    "https://www.randomservices.org/random/hypothesis/BivariateNormal.html": "../hypothesis/BivariateNormal.html",
}


EDITION_NOTICE = r'''
	<section class="edition-notice" data-o006-edition-notice="v1">
		<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, perbaikan satu paragraf sumber yang kehilangan tag pembuka, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, dan koreksi matematis, jawaban, tautan, serta ejaan terbatas yang dicatat dalam daftar koreksi edisi.</p>
		<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
	</section>'''


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
                f"line {line_number}: expected one exact math defect, found {value.count(old)}: {old!r}"
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
        raise RuntimeError("edition notice missing from target")
    notice.decompose()


def assert_topology(source_text: str, target_text: str) -> None:
    source = BeautifulSoup(source_text, "html.parser")
    target = BeautifulSoup(target_text, "html.parser")
    strip_notice(target)
    source_counts = Counter(tag.name for tag in source.find_all(True))
    target_counts = Counter(tag.name for tag in target.find_all(True))
    expected = source_counts.copy()
    expected["p"] += 1  # line 67 has a proved orphan closing paragraph tag
    if target_counts != expected:
        raise RuntimeError(
            f"parsed topology mismatch: source={dict(source_counts)}, target={dict(target_counts)}"
        )
    if sum(source_counts.values()) != 303 or sum(target_counts.values()) != 304:
        raise RuntimeError("unexpected parsed element count")
    source_sequence = [tag.name for tag in source.find_all(True)]
    target_sequence = [tag.name for tag in target.find_all(True)]
    if target_sequence != source_sequence[:55] + ["p"] + source_sequence[55:]:
        raise RuntimeError("parsed topology order changed beyond the line-67 paragraph repair")
    for selector, expected_count in (
        ("div.unit", 21),
        ("details", 12),
        ("summary", 12),
        ("h2,h3,h4", 8),
        ("img", 4),
    ):
        if len(target.select(selector)) != expected_count:
            raise RuntimeError(f"topology count mismatch for {selector}")
    source_ids = [tag["id"] for tag in source.find_all(id=True)]
    target_ids = [tag["id"] for tag in target.find_all(id=True)]
    if len(source_ids) != len(set(source_ids)) or len(target_ids) != len(set(target_ids)):
        raise RuntimeError("duplicate native/additive id")
    expected_ids = set(source_ids) | {
        "o006.random.interval.bivariate-normal.page",
        "o006.random.interval.bivariate-normal.unit-10",
    }
    if set(target_ids) != expected_ids:
        raise RuntimeError(
            f"ID inventory mismatch: missing={sorted(expected_ids-set(target_ids))}, "
            f"extra={sorted(set(target_ids)-expected_ids)}"
        )
    if target.select_one("div.unit:not([id])") is not None:
        raise RuntimeError("target retains an addressless instructional unit")


def assert_local_closure(rendered: str) -> None:
    soup = BeautifulSoup(rendered, "html.parser")
    for tag in soup.find_all(["a", "link", "script", "img"]):
        attribute = "href" if tag.has_attr("href") else "src" if tag.has_attr("src") else None
        if attribute is None:
            continue
        value = tag[attribute]
        parsed = urlparse(value)
        if parsed.scheme or value.startswith("#"):
            continue
        relative = value.split("#", 1)[0]
        resolved = (TARGET.parent / relative).resolve()
        authority_resolved = (SOURCE.parent / relative).resolve()
        if resolved.suffix.lower() in {".html", ".htm"}:
            if not resolved.is_file():
                raise RuntimeError(f"missing translated local page: {value} -> {resolved}")
        elif not resolved.is_file() and not authority_resolved.is_file():
            raise RuntimeError(
                f"missing local dependency in target and frozen authority: "
                f"{value} -> {resolved} / {authority_resolved}"
            )


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

    expected_math_text_lines: list[str] = []
    for line_number, original in enumerate(lines, 1):
        ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
        body = original.removesuffix(ending)
        repaired = apply_math_repairs(line_number, body)
        expected_math_text_lines.append(repaired + ending)
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

    expected_math_text = "".join(expected_math_text_lines)
    source_math = MATH_RE.findall(source_text)
    expected_math = MATH_RE.findall(expected_math_text)
    target_math = MATH_RE.findall(rendered)
    if len(source_math) != 267 or len(expected_math) != 267 or target_math != expected_math:
        raise RuntimeError(
            f"protected-math inventory mismatch: source={len(source_math)}, "
            f"expected={len(expected_math)}, target={len(target_math)}"
        )
    source_align = re.findall(r"\\begin\{align\}(?:.|\n)*?\\end\{align\}", source_text)
    target_align = re.findall(r"\\begin\{align\}(?:.|\n)*?\\end\{align\}", rendered)
    if len(source_align) != 1 or target_align != source_align:
        raise RuntimeError("raw align environment changed")
    source_p = (len(re.findall(r"<p(?:\s|>)", source_text)), source_text.count("</p>"))
    target_p = (len(re.findall(r"<p(?:\s|>)", rendered)), rendered.count("</p>"))
    if source_p != (58, 59) or target_p != (61, 61):
        raise RuntimeError(f"paragraph-tag repair mismatch: source={source_p}, target={target_p}")

    assert_topology(source_text, rendered)
    assert_local_closure(rendered)

    for required in (
        'href="index.html"',
        'href="Introduction.html"',
        'href="../sample/CLT.html"',
        'href="../sample/Normal.html"',
        'href="Normal.html"',
        'href="Bernoulli.html"',
        'href="Bayes.html"',
        'href="https://www.randomservices.org/random/data/Iris.html"',
    ):
        if required not in rendered:
            raise RuntimeError(f"required navigation target missing: {required}")
    for forbidden in (
        'lang="en"',
        "JavaScript:openAncillary",
        "../data/Fisher.html",
        ">Details:<",
        "Expand Details",
        "Contract Details",
        ">Apps<",
        ">Data Sets<",
        "> Biographies<",
        ">The Two-Sample Normal Model<",
        ">Preliminaries<",
        "Confidence Intervals for the Difference",
        "Confidence Intervals for the Ratio",
        ">Estimation in the Bivariate Normal Model<",
        ">Computational Exercises<",
        "student \\( f \\)",
        "has the standard normal distribution",
        "sometime stable",
        "in anyway",
        "inteval",
        "an decreasing",
        "vary small",
        "denote consider",
        " as mean 10.3",
        "(-24.834, -23.166)",
        "(0.832, 0.168)",
    ):
        if forbidden in rendered:
            raise RuntimeError(f"unresolved reader-facing/source defect remains: {forbidden}")
    controls = [ch for ch in rendered if ord(ch) < 32 and ch not in "\t\r\n"]
    if controls:
        raise RuntimeError(f"forbidden control characters: {sorted(map(ord, controls))}")

    output = rendered.encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(output)
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: "
        f"{len(output)} bytes / sha256 {hashlib.sha256(output).hexdigest()} / "
        "304 core elements / 21 units / 12 disclosures / 267 protected TeX spans"
    )


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
