#!/usr/bin/env python3
"""Create the bounded id-ID normal-model hypothesis-testing target."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "hypothesis" / "Normal.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "hypothesis" / "Normal.html"
SOURCE_URL = "https://www.randomservices.org/random/hypothesis/Normal.html"
SOURCE_BYTES = 43435
SOURCE_SHA256 = "fd7bc50171fc51310f41e9132005b66cdbbd31bf507a70a0246394b05a379ab2"
EXPECTED_SOURCE_LINES = 575

MATH_RE = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")
TOKEN_RE = re.compile(r"@@M(\d+)@@")


# Every translated line is tied to its frozen authority line. Protected TeX is
# reinserted in authority order after the small, proved repair set below.
T: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Pengujian pada Model Normal</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, uji hipotesis, distribusi normal, rata-rata, varians, distribusi t Student, distribusi khi-kuadrat, kuasa, prosedur robust">''',
    32: r'''\t\t<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    33: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    35: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Uji dalam Model Bernoulli">3</a></li>''',
    36: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Uji dalam Model Normal Dua Sampel">4</a></li>''',
    37: r'''\t\t<li class="child"><a href="Likelihood.html" title="Uji Rasio Kemungkinan">5</a></li>''',
    38: r'''\t\t<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    39: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    40: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    42: r'''\t<h2 id="o006.random.hypothesis.normal.page">2. Pengujian pada Model Normal</h2>''',
    45: r'''<h3 id="the">Teori Dasar</h3>''',
    47: r'''<h4>Model Normal</h4>''',
    49: r'''<p><a href="../special/Normal.html">Distribusi normal</a> mungkin merupakan distribusi terpenting dalam kajian statistika matematis, antara lain karena <a href="../sample/CLT.html">teorema limit pusat</a>. Sebagai konsekuensi teorema ini, suatu besaran terukur yang dipengaruhi oleh banyak galat acak kecil akan mempunyai distribusi yang setidaknya mendekati normal. Variabel semacam itu terdapat di mana-mana dalam eksperimen statistika, pada bidang yang membentang dari ilmu fisika dan biologi hingga ilmu sosial.</p>''',
    51: r'''<p>Karena itu, dalam bagian ini kita mengasumsikan bahwa @@M1@@ adalah <a href="../sample/Introduction.html">sampel acak</a> dari <a href="../special/Normal.html">distribusi normal</a> dengan <a href="../expect/Properties.html">rata-rata</a> @@M2@@ dan <a href="../expect/Variance.html">simpangan baku</a> @@M3@@. Tujuan kita adalah membangun <a href="Introduction.html">uji hipotesis</a> bagi @@M4@@ dan @@M5@@; keduanya termasuk kasus khusus terpenting dalam pengujian hipotesis. Bagian ini sejajar dengan pembahasan <a href="../interval/Normal.html">pendugaan dalam model normal</a> pada bab <a href="../interval/index.html">pendugaan himpunan</a>. Khususnya, dualitas antara pendugaan interval dan pengujian hipotesis akan berperan penting. Namun, pertama-tama kita perlu meninjau beberapa fakta dasar yang sangat penting bagi analisis kita.</p>''',
    54: r'''\t<p class="dfn">Ingat bahwa <a href="../sample/LLN.html">rata-rata sampel</a> @@M1@@ dan <a href="../sample/Variance.html">varians sampel</a> @@M2@@ adalah''',
    58: r'''<p>Dari pembahasan <a href="../point/index.html">pendugaan titik</a>, ingat bahwa @@M1@@ merupakan penduga tak bias dan konsisten bagi @@M2@@, sedangkan @@M3@@ merupakan penduga tak bias dan konsisten bagi @@M4@@. Dari statistik-statistik dasar ini kita dapat membangun <a href="Introduction.html#piv">statistik uji</a> yang akan digunakan dalam uji hipotesis. Hasil berikut adalah <a href="../sample/Normal.html">sifat khusus</a> sampel dari distribusi normal.</p>''',
    61: r'''\t<p class="math">Definisikan''',
    64: r'''\t\t<li>@@M1@@ mempunyai <a href="../special/Normal.html">distribusi normal baku</a>.</li>''',
    65: r'''\t\t<li>@@M1@@ mempunyai <a href="../special/Student.html">distribusi @@M2@@ Student</a> dengan @@M3@@ derajat kebebasan.</li>''',
    66: r'''\t\t<li>@@M1@@ mempunyai <a href="../special/ChiSquare.html">distribusi khi-kuadrat</a> dengan @@M2@@ derajat kebebasan.</li>''',
    67: r'''\t\t<li>@@M1@@ dan @@M2@@ saling bebas.</li>''',
    71: r'''<p>Jadi, setiap variabel acak ini merupakan variabel pivot bagi @@M1@@: distribusinya tidak bergantung pada parameter, tetapi variabelnya sendiri secara fungsional bergantung pada salah satu atau kedua parameter. Variabel pivot tersebut menghasilkan statistik uji alami yang dapat dipakai untuk menguji hipotesis mengenai parameter. Untuk membangun uji, kita memerlukan <a href="../dist/CDF.html#qnt">kuantil</a> distribusi-distribusi baku ini. Kuantil dapat dihitung dengan <a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">aplikasi kuantil</a> atau sebagian besar paket perangkat lunak matematika dan statistika. Notasi yang kita gunakan adalah sebagai berikut:</p>''',
    74: r'''\t<p class="dfn">Misalkan @@M1@@ dan @@M2@@.</p>''',
    76: r'''\t\t<li>@@M1@@ menyatakan kuantil berorde @@M2@@ dari distribusi normal baku.</li>''',
    77: r'''\t\t<li>@@M1@@ menyatakan kuantil berorde @@M2@@ dari distribusi @@M3@@ Student dengan @@M4@@ derajat kebebasan.</li>''',
    78: r'''\t\t<li>@@M1@@ menyatakan kuantil berorde @@M2@@ dari distribusi khi-kuadrat dengan @@M3@@ derajat kebebasan.</li>''',
    82: r'''<p>Karena distribusi normal baku dan distribusi @@M1@@ Student simetris terhadap 0, berlaku @@M2@@ dan @@M3@@ untuk @@M4@@ serta @@M5@@. Sebaliknya, distribusi khi-kuadrat tidak simetris.</p>''',
    84: r'''<h4 id="nor">Uji Rata-Rata dengan Simpangan Baku Diketahui</h4>''',
    86: r'''<p>Dalam pembahasan pertama, kita mengasumsikan bahwa rata-rata distribusi @@M1@@ tidak diketahui, tetapi simpangan baku @@M2@@ diketahui. Asumsi ini tidak selalu dibuat-buat. Sering ada keadaan ketika @@M3@@ stabil sepanjang waktu sehingga setidaknya diketahui secara mendekati, sementara @@M4@@ berubah karena <q>perlakuan</q> yang berbeda. Contohnya diberikan dalam latihan komputasi di bawah.</p>''',
    89: r'''\t<p class="math">Untuk nilai hipotesis @@M1@@, definisikan statistik uji''',
    92: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai distribusi normal baku.</li>''',
    93: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai distribusi normal dengan rata-rata @@M3@@ dan varians 1.</li>''',
    97: r'''<p>Jadi, pada kasus (b), @@M1@@ dapat dipandang sebagai <dfn>parameter nonsentral</dfn>. Grafik fungsi kepadatan peluang @@M2@@ berbentuk seperti fungsi kepadatan normal baku, tetapi bergeser ke kanan atau ke kiri sebesar parameter nonsentral, bergantung pada apakah @@M3@@ atau @@M4@@.</p>''',
    100: r'''\t<p class="math">Untuk @@M1@@, setiap uji berikut mempunyai tingkat signifikansi @@M2@@:</p>''',
    102: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@ atau @@M4@@; secara ekuivalen, jika dan hanya jika @@M5@@ atau @@M6@@.</li>''',
    103: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    104: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    107: r'''\t\t<summary>Rincian:</summary>''',
    108: r'''\t\t<p>Pada bagian (a), @@M1@@ merupakan hipotesis sederhana dan, di bawah @@M2@@, @@M3@@ mempunyai distribusi normal baku. Karena itu, menurut definisi kuantil, @@M4@@ adalah peluang menolak @@M5@@ secara keliru. Pada bagian (b) dan (c), @@M6@@ mempunyai distribusi normal nonsentral di bawah @@M7@@ seperti dibahas pada <a href="#nor1" class="ref"></a>. Jika @@M8@@ benar, peluang galat tipe I maksimum sebesar @@M9@@ terjadi ketika @@M10@@. Aturan keputusan dalam @@M11@@ ekuivalen dengan aturan yang bersesuaian dalam @@M12@@ melalui aljabar sederhana.</p>''',
    112: r'''<p>Bagian (a) adalah uji dua sisi baku, bagian (b) adalah uji sisi kanan, dan bagian (c) adalah uji sisi kiri. Dalam setiap kasus, uji hipotesis tersebut merupakan dual dari dugaan interval yang bersesuaian dalam bagian <a href="../interval/Normal.html">pendugaan pada model normal</a>.</p>''',
    115: r'''\t<p class="math">Untuk setiap uji pada <a href="#nor2" class="ref"></a>, kita <em>gagal</em> menolak @@M1@@ pada tingkat signifikansi @@M2@@ jika dan hanya jika @@M3@@ berada dalam interval kepercayaan @@M4@@ yang bersesuaian, yaitu</p>''',
    122: r'''\t\t<summary>Rincian:</summary>''',
    123: r'''\t\t<p>Hasil ini mengikuti <a href="#nor2" class="ref"></a>. Dalam setiap kasus, kita mulai dari pertidaksamaan yang bersesuaian dengan tidak menolak @@M1@@, lalu menyelesaikannya terhadap @@M2@@.</p>''',
    127: r'''<p>Uji dua sisi pada (a) menempatkan @@M1@@ pada setiap ekor distribusi statistik uji @@M2@@ di bawah @@M3@@. Uji ini disebut <dfn>tak bias</dfn>. Kita tentu dapat membangun uji bias lain dengan membagi tingkat signifikansi @@M4@@ secara tidak simetris antara ekor kiri dan kanan.</p>''',
    130: r'''\t<p class="math">Untuk setiap @@M1@@, uji berikut mempunyai tingkat signifikansi @@M2@@: tolak @@M3@@ melawan @@M4@@ jika dan hanya jika @@M5@@ atau @@M6@@.</p>''',
    132: r'''\t\t<li>@@M1@@ menghasilkan uji simetris dan tak bias.</li>''',
    133: r'''\t\t<li>@@M1@@ menghasilkan uji sisi kiri.</li>''',
    134: r'''\t\t<li>@@M1@@ menghasilkan uji sisi kanan.</li>''',
    137: r'''\t\t<summary>Rincian:</summary>''',
    138: r'''\t\t<p>Seperti sebelumnya, @@M1@@ merupakan hipotesis sederhana dan, jika @@M2@@ benar, @@M3@@ mempunyai distribusi normal baku. Karena itu, peluang menolak @@M4@@ secara keliru adalah @@M5@@ menurut definisi kuantil. Bagian (a)&ndash;(c) mengikuti sifat fungsi kuantil normal baku.</p>''',
    142: r'''<p>Nilai-@@M1@@ untuk uji-uji ini dapat dihitung dengan fungsi distribusi normal baku @@M2@@.</p>''',
    145: r'''\t<p class="math">Nilai-@@M1@@ untuk uji baku pada <a href="#nor2" class="ref"></a> berturut-turut adalah</p>''',
    153: r'''<p>Ingat bahwa <dfn>fungsi kuasa</dfn> suatu uji parameter adalah peluang menolak hipotesis nol sebagai fungsi nilai parameter yang sebenarnya. Rangkaian hasil berikut menelaah fungsi kuasa uji pada <a href="#nor4" class="ref"></a>.</p>''',
    156: r'''\t<p class="math">Fungsi kuasa uji dua sisi umum pada <a href="#nor4" class="ref"></a> adalah''',
    159: r'''\t\t<li>@@M1@@ menurun pada @@M2@@ dan meningkat pada @@M3@@, dengan @@M4@@.</li>''',
    161: r'''\t\t<li>@@M1@@ ketika @@M2@@ dan @@M3@@ ketika @@M4@@.</li>''',
    162: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ simetris terhadap @@M3@@ (dan @@M4@@).</li>''',
    163: r'''\t\t<li>Ketika @@M1@@ meningkat, @@M2@@ meningkat jika @@M3@@ dan menurun jika @@M4@@.</li>''',
    167: r'''<p>Jadi, dengan mengubah @@M1@@, kita dapat menaikkan kuasa uji pada sebagian nilai @@M2@@, tetapi hanya dengan mengorbankan kuasa pada nilai @@M3@@ lainnya.</p>''',
    170: r'''\t\t<p class="math">Fungsi kuasa uji sisi kiri pada <a href="#nor4" class="ref"></a> adalah''',
    173: r'''\t\t\t<li>@@M1@@ menurun pada @@M2@@.</li>''',
    175: r'''\t\t\t<li>@@M1@@ ketika @@M2@@ dan @@M3@@ ketika @@M4@@.</li>''',
    180: r'''\t<p class="math">Fungsi kuasa uji sisi kanan pada <a href="#nor4" class="ref"></a> adalah''',
    183: r'''\t\t<li>@@M1@@ meningkat pada @@M2@@.</li>''',
    185: r'''\t\t<li>@@M1@@ ketika @@M2@@ dan @@M3@@ ketika @@M4@@.</li>''',
    190: r'''\t<p class="math">Untuk setiap uji satu sisi, memperbesar ukuran sampel @@M1@@ atau memperkecil simpangan baku @@M2@@ menaikkan kuasa di seluruh arah alternatif yang bersesuaian. Hal yang sama berlaku bagi uji dua sisi simetris pada setiap nilai alternatif; untuk pembagian ekor asimetris umum pada <a href="#nor4" class="ref"></a>, kenaikan kuasa tidak harus seragam pada kedua sisi.</p>''',
    194: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/MeanTest.html')" class="ancillary">eksperimen uji rata-rata</a>, pilih statistik uji normal dan distribusi asal sampel normal dengan simpangan baku @@M1@@, ukuran sampel @@M2@@, serta @@M3@@. Jalankan eksperimen 1.000 kali untuk beberapa nilai rata-rata distribusi sebenarnya @@M4@@. Untuk setiap nilai @@M5@@, perhatikan distribusi nilai-@@M6@@.</p>''',
    198: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/MeanEstimate.html')" class="ancillary">eksperimen pendugaan rata-rata</a>, pilih variabel pivot normal dan distribusi normal dengan @@M1@@, simpangan baku @@M2@@, tingkat kepercayaan @@M3@@, serta ukuran sampel @@M4@@. Untuk setiap dari ketiga jenis interval kepercayaan, jalankan eksperimen 20 kali. Nyatakan hipotesis dan tingkat signifikansi yang bersesuaian; untuk setiap pengulangan, berikan himpunan @@M5@@ yang menyebabkan hipotesis nol ditolak.</p>''',
    201: r'''<p>Dalam banyak kasus, langkah pertama adalah <em>merancang</em> eksperimen agar tingkat signifikansinya @@M1@@ dan agar uji mempunyai kuasa @@M2@@ pada alternatif tertentu @@M3@@.</p>''',
    204: r'''\t<p class="math">Untuk salah satu uji satu sisi pada <a href="#nor2" class="ref"></a>, ukuran sampel @@M1@@ yang diperlukan bagi uji dengan tingkat signifikansi @@M2@@ dan kuasa @@M3@@ pada alternatif @@M4@@—yang harus berada pada arah alternatif yang diuji—adalah''',
    207: r'''\t\t<summary>Rincian:</summary>''',
    208: r'''\t\t<p>Hasil ini diperoleh dengan menyamakan fungsi kuasa dengan @@M1@@, lalu menyelesaikannya terhadap @@M2@@. Untuk ukuran sampel aktual, bulatkan ruas kanan ke atas ke bilangan bulat.</p>''',
    213: r'''\t<p class="math">Untuk uji dua sisi tak bias, ukuran sampel @@M1@@ yang diperlukan bagi uji dengan tingkat signifikansi @@M2@@ dan kuasa @@M3@@ pada alternatif @@M4@@ secara hampiran adalah''',
    216: r'''\t\t<summary>Rincian:</summary>''',
    217: r'''\t\t<p>Dalam fungsi kuasa uji dua sisi pada <a href="#nor6" class="ref"></a>, suku kedua dapat diabaikan jika @@M1@@, sedangkan suku pertama dapat diabaikan jika @@M2@@. Bulatkan hasil ke atas dan periksa kembali kuasa eksak setelah pembulatan karena rumus ini merupakan hampiran.</p>''',
    221: r'''<h4 id="stu">Uji Rata-Rata dengan Simpangan Baku Tidak Diketahui</h4>''',
    223: r'''<p>Selanjutnya, kita membangun uji bagi @@M1@@ tanpa mengasumsikan bahwa @@M2@@ diketahui. Dalam penerapan, tentu saja, @@M3@@ biasanya memang tidak diketahui.</p>''',
    226: r'''\t<p class="math">Untuk nilai hipotesis @@M1@@, definisikan statistik uji''',
    229: r'''\t\t<li>Jika @@M1@@, statistik @@M2@@ mempunyai distribusi @@M3@@ Student dengan @@M4@@ derajat kebebasan.</li>''',
    230: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai <a href="../special/Student.html#non">distribusi @@M3@@ nonsentral</a> dengan @@M4@@ derajat kebebasan dan parameter nonsentral @@M5@@.</li>''',
    234: r'''<p>Pada kasus (b), grafik fungsi kepadatan peluang @@M1@@ menyerupai distribusi @@M2@@ biasa dengan @@M3@@ derajat kebebasan, tetapi bukan sekadar translasi; arah pergeseran massanya ditentukan oleh apakah @@M4@@ atau @@M5@@.</p>''',
    237: r'''\t<p class="math">Untuk @@M1@@, setiap uji berikut mempunyai tingkat signifikansi @@M2@@:</p>''',
    239: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@ atau @@M4@@; secara ekuivalen, jika dan hanya jika @@M5@@ atau @@M6@@.</li>''',
    240: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    241: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    244: r'''\t\t<summary>Rincian:</summary>''',
    245: r'''\t\t<p>Pada bagian (a), @@M1@@ mempunyai distribusi t Student dengan @@M2@@ derajat kebebasan di bawah @@M3@@. Karena itu, jika @@M4@@ benar, peluang menolak @@M5@@ secara keliru adalah @@M6@@ menurut definisi kuantil. Pada bagian (b) dan (c), @@M7@@ mempunyai distribusi @@M8@@ nonsentral dengan @@M9@@ derajat kebebasan di bawah @@M10@@, sebagaimana pada <a href="#stu1" class="ref"></a>. Jadi, jika @@M11@@ benar, peluang galat tipe I maksimum sebesar @@M12@@ terjadi ketika @@M13@@. Aturan keputusan dalam @@M14@@ ekuivalen dengan aturan yang bersesuaian dalam @@M15@@ melalui aljabar sederhana.</p>''',
    249: r'''<p>Bagian (a) adalah uji dua sisi baku, bagian (b) adalah uji sisi kanan, dan bagian (c) adalah uji sisi kiri. Dalam setiap kasus, uji hipotesis tersebut merupakan dual dari dugaan interval yang bersesuaian dalam bagian <a href="../interval/Normal.html">pendugaan pada model normal</a>.</p>''',
    252: r'''\t<p class="math">Untuk setiap uji pada <a href="#stu2" class="ref"></a>, kita <em>gagal</em> menolak @@M1@@ pada tingkat signifikansi @@M2@@ jika dan hanya jika @@M3@@ berada dalam interval kepercayaan @@M4@@ yang bersesuaian.</p>''',
    259: r'''\t\t<summary>Rincian:</summary>''',
    260: r'''\t\t<p>Hasil ini mengikuti <a href="#stu2" class="ref"></a>. Dalam setiap kasus, kita mulai dari pertidaksamaan yang bersesuaian dengan <em>tidak</em> menolak @@M1@@, lalu menyelesaikannya terhadap @@M2@@.</p>''',
    264: r'''<p>Uji dua sisi pada (a) menempatkan @@M1@@ pada setiap ekor distribusi statistik uji @@M2@@ di bawah @@M3@@. Uji ini disebut <dfn>tak bias</dfn>. Kita tentu dapat membangun uji bias lain dengan membagi tingkat signifikansi @@M4@@ secara tidak simetris antara ekor kiri dan kanan.</p>''',
    267: r'''\t<p class="math">Untuk setiap @@M1@@, uji berikut mempunyai tingkat signifikansi @@M2@@: tolak @@M3@@ melawan @@M4@@ jika dan hanya jika @@M5@@ atau @@M6@@; secara ekuivalen, jika dan hanya jika @@M7@@ atau @@M8@@.</p>''',
    269: r'''\t\t<li>@@M1@@ menghasilkan uji simetris dan tak bias.</li>''',
    270: r'''\t\t<li>@@M1@@ menghasilkan uji sisi kiri.</li>''',
    271: r'''\t\t<li>@@M1@@ menghasilkan uji sisi kanan.</li>''',
    274: r'''\t\t<summary>Rincian:</summary>''',
    275: r'''\t\t<p>Sekali lagi, @@M1@@ merupakan hipotesis sederhana dan, di bawah @@M2@@, statistik uji @@M3@@ mempunyai distribusi @@M4@@ Student dengan @@M5@@ derajat kebebasan. Karena itu, jika @@M6@@ benar, peluang menolak @@M7@@ secara keliru adalah @@M8@@ menurut definisi kuantil. Bagian (a)&ndash;(c) mengikuti sifat fungsi kuantil.</p>''',
    279: r'''<p>Nilai-@@M1@@ untuk uji-uji ini dapat dihitung dengan fungsi distribusi @@M2@@ dari distribusi @@M3@@ dengan @@M4@@ derajat kebebasan.</p>''',
    282: r'''\t<p class="math">Nilai-@@M1@@ untuk uji baku pada <a href="#stu2" class="ref"></a> berturut-turut adalah</p>''',
    291: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/MeanTest.html')" class="ancillary">eksperimen uji rata-rata</a>, pilih statistik uji Student dan distribusi asal sampel normal dengan simpangan baku @@M1@@, ukuran sampel @@M2@@, serta @@M3@@. Jalankan eksperimen 1.000 kali untuk beberapa nilai rata-rata distribusi sebenarnya @@M4@@. Untuk setiap nilai @@M5@@, perhatikan distribusi empiris nilai-@@M6@@.</p>''',
    295: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/MeanEstimate.html')" class="ancillary">eksperimen pendugaan rata-rata</a>, pilih variabel pivot Student dan distribusi asal sampel normal dengan rata-rata 0 serta simpangan baku 2. Pilih tingkat kepercayaan 0,90 dan ukuran sampel 10. Untuk setiap dari ketiga jenis interval, jalankan eksperimen 20 kali. Nyatakan hipotesis dan tingkat signifikansi yang bersesuaian; untuk setiap pengulangan, berikan himpunan @@M1@@ yang menyebabkan hipotesis nol ditolak.</p>''',
    298: r'''<p>Fungsi kuasa uji @@M1@@ pada <a href="#stu5" class="ref"></a> dapat dihitung secara eksplisit memakai fungsi distribusi @@M2@@ nonsentral. Secara kualitatif, grafik fungsi kuasanya serupa dengan kasus ketika @@M3@@ diketahui, yaitu <a href="#nor6" class="ref"></a> (dua sisi), <a href="#nor7" class="ref"></a> (sisi kiri), dan <a href="#nor8" class="ref"></a> (sisi kanan).</p>''',
    300: r'''<p>Jika batas atas @@M1@@ bagi simpangan baku @@M2@@ diketahui, dugaan konservatif ukuran sampel yang diperlukan untuk tingkat signifikansi dan kuasa tertentu dapat diperoleh dengan metode variabel pivot normal: <a href="#nor13" class="ref"></a> untuk uji dua sisi dan <a href="#nor12" class="ref"></a> untuk uji satu sisi.</p>''',
    302: r'''<h4 id="chi">Uji Simpangan Baku</h4>''',
    304: r'''<p>Selanjutnya, kita membangun uji hipotesis bagi simpangan baku distribusi @@M1@@. Jadi, @@M2@@ diasumsikan tidak diketahui dan, hampir selalu, @@M3@@ juga tidak diketahui.</p>''',
    307: r'''\t<p class="math">Untuk nilai hipotesis @@M1@@, definisikan statistik uji''',
    310: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai distribusi khi-kuadrat dengan @@M3@@ derajat kebebasan.</li>''',
    311: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai <a href="../special/Gamma.html">distribusi gamma</a> dengan parameter bentuk @@M3@@ dan parameter skala @@M4@@.</li>''',
    315: r'''<p>Ingat bahwa distribusi khi-kuadrat biasa dengan @@M1@@ derajat kebebasan adalah distribusi gamma dengan parameter bentuk @@M2@@ dan parameter skala @@M3@@. Jadi, pada kasus (b), distribusi khi-kuadrat biasa dikalikan faktor @@M4@@. Khususnya, faktor skala itu lebih besar dari 1 jika @@M5@@ dan lebih kecil dari 1 jika @@M6@@.</p>''',
    318: r'''\t<p class="math">Untuk setiap @@M1@@, uji berikut mempunyai tingkat signifikansi @@M2@@:</p>''',
    320: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@ atau @@M4@@; secara ekuivalen, jika dan hanya jika @@M5@@ atau @@M6@@.</li>''',
    321: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    322: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    325: r'''\t\t<summary>Rincian:</summary>''',
    326: r'''\t\t<p>Logikanya hampir sama dengan uji hipotesis sebelumnya. Pada bagian (a), @@M1@@ merupakan hipotesis sederhana dan, di bawah @@M2@@, statistik uji @@M3@@ mempunyai distribusi khi-kuadrat dengan @@M4@@ derajat kebebasan. Jadi, jika @@M5@@ benar, peluang menolak @@M6@@ secara keliru adalah @@M7@@ menurut definisi kuantil. Pada bagian (b) dan (c), @@M8@@ mempunyai distribusi gamma yang lebih umum di bawah @@M9@@, seperti dibahas pada <a href="#chi1" class="ref"></a>. Jika @@M10@@ benar, peluang galat tipe I maksimum sebesar @@M11@@ terjadi ketika @@M12@@.</p>''',
    330: r'''<p>Bagian (a) adalah uji dua sisi berekor sama yang menempatkan @@M1@@ pada setiap ekor distribusi khi-kuadrat statistik uji @@M2@@ di bawah @@M3@@; pembagian ekor sama ini tidak dengan sendirinya menjamin uji tak bias. Bagian (b) adalah uji sisi kiri dan bagian (c) uji sisi kanan. Sekali lagi, terdapat dualitas antara uji hipotesis dan dugaan interval yang dibangun dalam bagian <a href="../interval/Normal.html">pendugaan pada model normal</a>.</p>''',
    333: r'''\t<p class="math">Untuk setiap uji pada <a href="#chi2" class="ref"></a>, kita <em>gagal</em> menolak @@M1@@ pada tingkat signifikansi @@M2@@ jika dan hanya jika @@M3@@ berada dalam interval kepercayaan @@M4@@ yang bersesuaian. Yaitu</p>''',
    340: r'''\t\t<summary>Rincian:</summary>''',
    341: r'''\t\t<p>Hasil ini mengikuti <a href="#chi2" class="ref"></a>. Dalam setiap kasus, kita mulai dari pertidaksamaan yang bersesuaian dengan <em>tidak</em> menolak @@M1@@, lalu menyelesaikannya terhadap @@M2@@.</p>''',
    345: r'''<p>Seperti sebelumnya, kita dapat membangun uji dua sisi yang lebih umum dengan membagi tingkat signifikansi @@M1@@ secara sembarang antara ekor kiri dan kanan distribusi khi-kuadrat.</p>''',
    348: r'''\t<p class="math">Untuk setiap @@M1@@, uji berikut mempunyai tingkat signifikansi @@M2@@: tolak @@M3@@ melawan @@M4@@ jika dan hanya jika @@M5@@ atau @@M6@@; secara ekuivalen, jika dan hanya jika @@M7@@ atau @@M8@@.</p>''',
    350: r'''\t\t<li>@@M1@@ menghasilkan uji berekor sama.</li>''',
    351: r'''\t\t<li>@@M1@@ menghasilkan uji sisi kiri.</li>''',
    352: r'''\t\t<li>@@M1@@ menghasilkan uji sisi kanan.</li>''',
    355: r'''\t\t<summary>Rincian:</summary>''',
    356: r'''\t\t<p>Seperti sebelumnya, @@M1@@ merupakan hipotesis sederhana dan, di bawah @@M2@@, statistik uji @@M3@@ mempunyai distribusi khi-kuadrat dengan @@M4@@ derajat kebebasan. Jadi, jika @@M5@@ benar, peluang menolak @@M6@@ secara keliru adalah @@M7@@ menurut definisi kuantil. Bagian (a)&ndash;(c) mengikuti sifat fungsi kuantil.</p>''',
    360: r'''<p>Ingat kembali bahwa <dfn>fungsi kuasa</dfn> suatu uji parameter adalah peluang menolak hipotesis nol sebagai fungsi nilai parameter yang sebenarnya. Fungsi kuasa uji bagi @@M1@@ dapat dinyatakan dengan fungsi distribusi @@M2@@ dari distribusi khi-kuadrat dengan @@M3@@ derajat kebebasan.</p>''',
    363: r'''\t<p class="math">Fungsi kuasa uji dua sisi umum pada <a href="#chi4" class="ref"></a> diberikan oleh rumus berikut dan mempunyai sifat-sifat yang dinyatakan:''',
    366: r'''\t\t<li>@@M1@@ mula-mula menurun lalu meningkat pada @@M2@@; titik minimumnya pada umumnya tidak tepat di @@M3@@.</li>''',
    368: r'''\t\t<li>@@M1@@ ketika @@M2@@ dan @@M3@@ ketika @@M4@@.</li>''',
    373: r'''\t<p class="math">Fungsi kuasa uji sisi kanan pada <a href="#chi2" class="ref"></a> diberikan oleh rumus berikut dan mempunyai sifat-sifat yang dinyatakan:''',
    376: r'''\t\t<li>@@M1@@ meningkat pada @@M2@@.</li>''',
    378: r'''\t\t<li>@@M1@@ ketika @@M2@@ dan @@M3@@ ketika @@M4@@.</li>''',
    383: r'''\t<p class="math">Fungsi kuasa uji sisi kiri pada <a href="#chi2" class="ref"></a> diberikan oleh rumus berikut dan mempunyai sifat-sifat yang dinyatakan:''',
    386: r'''\t\t<li>@@M1@@ menurun pada @@M2@@.</li>''',
    388: r'''\t\t<li>@@M1@@ ketika @@M2@@, sedangkan''',
    389: r'''\t\t@@M1@@ ketika @@M2@@; jadi, limit pada ujung ini berbeda dari limit pada ujung @@M3@@.</li>''',
    394: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/VarianceTestExperiment.html')" class="ancillary">eksperimen uji varians</a>, pilih distribusi normal dengan rata-rata 0, tingkat signifikansi 0,1, ukuran sampel 10, dan simpangan baku hipotesis 1,0. Untuk berbagai nilai simpangan baku sebenarnya, jalankan simulasi 1.000 kali. Catat frekuensi relatif penolakan hipotesis nol dan gambarkan kurva kuasa empiris.</p>''',
    396: r'''\t\t<li>Uji dua sisi</li>''',
    397: r'''\t\t<li>Uji sisi kiri</li>''',
    398: r'''\t\t<li>Uji sisi kanan</li>''',
    403: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/VarianceEstimate.html')" class="ancillary">eksperimen pendugaan varians</a>, pilih distribusi normal dengan rata-rata 0 dan simpangan baku 2, tingkat kepercayaan 0,90, serta ukuran sampel 10. Jalankan eksperimen 20 kali. Nyatakan hipotesis dan tingkat signifikansi yang bersesuaian; untuk setiap pengulangan, berikan himpunan simpangan baku hipotesis yang menyebabkan hipotesis nol ditolak.</p>''',
    405: r'''\t\t<li>Interval kepercayaan dua sisi</li>''',
    406: r'''\t\t<li>Batas bawah kepercayaan</li>''',
    407: r'''\t\t<li>Batas atas kepercayaan</li>''',
    411: r'''<h3 id="exe">Latihan</h3>''',
    413: r'''<h4 id="rob">Robustitas</h4>''',
    415: r'''<p>Asumsi utama kita adalah bahwa distribusi asal sampel bersifat normal. Tentu saja, dalam masalah statistika nyata, kecil kemungkinan kita mengetahui banyak hal tentang distribusi asal sampel, apalagi mengetahui bahwa distribusi itu normal. Jika distribusi asal sebenarnya tidak normal dan ukuran sampel @@M1@@ cukup besar, distribusi rata-rata sampel masih mendekati normal menurut <a href="../sample/CLT.html">teorema limit pusat</a>, sehingga uji rata-rata @@M2@@ juga dapat berlaku secara hampiran. Sebaliknya, uji varians @@M3@@ kurang robust terhadap penyimpangan dari asumsi normalitas. Latihan berikut menjelajahi gagasan-gagasan ini.</p>''',
    418: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/MeanTest.html')" class="ancillary">eksperimen uji rata-rata</a>, pilih <a href="../special/Gamma.html">distribusi gamma</a> dengan parameter bentuk 1 dan parameter skala 1. Untuk ketiga uji, berbagai ukuran sampel, dan berbagai nilai @@M1@@, jalankan eksperimen 1.000 kali. Untuk setiap konfigurasi, perhatikan distribusi empiris nilai-@@M2@@.</p>''',
    422: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/MeanTest.html')" class="ancillary">eksperimen uji rata-rata</a>, pilih <a href="../dist/Continuous.html">distribusi seragam</a> pada @@M1@@. Untuk ketiga uji serta berbagai ukuran sampel dan nilai @@M2@@, jalankan eksperimen 1.000 kali. Untuk setiap konfigurasi, perhatikan distribusi empiris nilai-@@M3@@.</p>''',
    425: r'''<p>Seberapa besar @@M1@@ harus dipilih agar prosedur pengujian bekerja baik bergantung pada distribusi asal; makin jauh distribusi itu menyimpang dari normalitas—terutama dalam kemencengan dan perilaku ekor—makin besar @@M2@@ yang mungkin diperlukan. Konvergensi dalam teorema limit pusat sering cukup cepat, tetapi aturan praktis 30 pengamatan bukan jaminan universal; validitas hampiran harus diperiksa untuk distribusi dan tujuan uji yang bersangkutan.</p>''',
    428: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/VarianceTestExperiment.html')" class="ancillary">eksperimen uji varians</a>, pilih <a href="../special/Gamma.html">distribusi gamma</a> dengan parameter bentuk 1 dan parameter skala 1. Untuk ketiga uji serta berbagai tingkat signifikansi, ukuran sampel, dan nilai @@M1@@, jalankan eksperimen 1.000 kali. Untuk setiap konfigurasi, catat frekuensi relatif penolakan @@M2@@. Ketika @@M3@@ benar, bandingkan frekuensi relatif itu dengan tingkat signifikansi.</p>''',
    432: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/VarianceTestExperiment.html')" class="ancillary">eksperimen uji varians</a>, pilih <a href="../dist/Continuous.html">distribusi seragam</a> pada @@M1@@. Untuk ketiga uji serta berbagai tingkat signifikansi, ukuran sampel, dan nilai @@M2@@, jalankan eksperimen 1.000 kali. Untuk setiap konfigurasi, catat frekuensi relatif penolakan @@M3@@. Ketika @@M4@@ benar, bandingkan frekuensi relatif itu dengan tingkat signifikansi.</p>''',
    435: r'''<h4 id="com">Latihan Komputasi</h4>''',
    438: r'''\t<p class="math">Panjang suatu komponen hasil pemesinan seharusnya 10 sentimeter. Karena proses produksi tidak sempurna, panjang sebenarnya merupakan variabel acak. Simpangan baku disebabkan oleh faktor inheren dalam proses yang relatif stabil sepanjang waktu. Dari data historis, simpangan baku diketahui dengan ketelitian tinggi sebesar 0,3. Sebaliknya, rata-rata dapat diatur dengan menyesuaikan berbagai parameter proses sehingga cukup sering berubah ke nilai yang tidak diketahui. Kita ingin menguji @@M1@@ melawan @@M2@@.</p>''',
    440: r'''\t\t<li>Andaikan sampel 100 komponen mempunyai rata-rata 10,1. Lakukan uji pada tingkat signifikansi 0,1.</li>''',
    441: r'''\t\t<li>Hitung nilai-@@M1@@ untuk data pada (a).</li>''',
    442: r'''\t\t<li>Hitung kuasa uji pada (a) ketika @@M1@@.</li>''',
    443: r'''\t\t<li>Hitung hampiran ukuran sampel yang diperlukan untuk tingkat signifikansi 0,1 dan kuasa 0,8 ketika @@M1@@.</li>''',
    446: r'''\t<summary>Rincian:</summary>''',
    448: r'''\t\t<li>Statistik uji 3,333, nilai kritis @@M1@@. Tolak @@M2@@.</li>''',
    449: r'''\t\t<li>@@M1@@</li>''',
    450: r'''\t\t<li>Kuasa uji pada 10,05 kira-kira 0,5092.</li>''',
    451: r'''\t\t<li>Ukuran sampel 223.</li>''',
    457: r'''\t<p class="math">Sekantong keripik kentang merek tertentu diiklankan mempunyai berat 250 gram. Berat sebenarnya (dalam gram) merupakan variabel acak. Andaikan sampel 75 kantong mempunyai rata-rata 248 dan simpangan baku 5. Pada tingkat signifikansi 0,05, lakukan uji berikut:</p>''',
    459: r'''\t\t<li>@@M1@@ melawan @@M2@@</li>''',
    460: r'''\t\t<li>@@M1@@ melawan @@M2@@</li>''',
    463: r'''\t\t<summary>Rincian:</summary>''',
    465: r'''\t\t\t<li>Statistik uji @@M1@@, nilai kritis @@M2@@. Tolak @@M3@@.</li>''',
    466: r'''\t\t\t<li>@@M1@@, sehingga tolak @@M2@@.</li>''',
    472: r'''\t<p class="math">Pada sebuah perusahaan pemasaran jarak jauh, durasi panggilan penawaran melalui telepon (dalam detik) merupakan variabel acak. Sampel 50 panggilan mempunyai rata-rata 310 dan simpangan baku 25. Pada tingkat signifikansi 0,1, dapatkah kita menyimpulkan bahwa</p>''',
    474: r'''\t\t<li>@@M1@@?</li>''',
    475: r'''\t\t<li>@@M1@@?</li>''',
    478: r'''\t\t<summary>Rincian:</summary>''',
    480: r'''\t\t\t<li>Statistik uji 2,828, nilai kritis 1,2991. Tolak @@M1@@.</li>''',
    481: r'''\t\t\t<li>@@M1@@, sehingga tolak @@M2@@.</li>''',
    487: r'''\t<p class="math">Di suatu perkebunan, berat buah persik (dalam ounce [oz]) pada saat panen merupakan variabel acak. Sampel 100 buah persik mempunyai rata-rata 8,2 dan simpangan baku 1,0. Pada tingkat signifikansi 0,01, dapatkah kita menyimpulkan bahwa</p>''',
    489: r'''\t\t<li>@@M1@@?</li>''',
    490: r'''\t\t<li>@@M1@@?</li>''',
    493: r'''\t\t<summary>Rincian:</summary>''',
    495: r'''\t\t\t<li>Statistik uji 2,0, nilai kritis 2,3646. Gagal menolak @@M1@@.</li>''',
    496: r'''\t\t\t<li>@@M1@@, sehingga tolak @@M2@@.</li>''',
    502: r'''\t<p class="math">Upah per jam untuk jenis pekerjaan konstruksi tertentu merupakan variabel acak dengan simpangan baku 1,25. Dalam sampel 25 pekerja, upah rata-ratanya $6,75. Pada tingkat signifikansi 0,01, dapatkah kita menyimpulkan bahwa @@M1@@?</p>''',
    504: r'''\t\t<summary>Rincian:</summary>''',
    505: r'''\t\t<p>Statistik uji @@M1@@, nilai kritis @@M2@@. Gagal menolak @@M3@@.</p>''',
    509: r'''<h4 id="dat">Latihan Analisis Data</h4>''',
    512: r'''\t<p class="stat">Dengan <a href="JavaScript:openAncillary('../data/Michelson.html')" class="ancillary">data Michelson</a>, ujilah apakah kecepatan cahaya lebih besar dari 730 (+299000) km/detik pada tingkat signifikansi 0,005.</p>''',
    514: r'''\t\t<summary>Rincian:</summary>''',
    515: r'''\t\t<p>Statistik uji 15,49, nilai kritis 2,6270. Tolak @@M1@@.</p>''',
    520: r'''\t<p class="stat">Dengan <a href="JavaScript:openAncillary('../data/Cavendish.html')" class="ancillary">data Cavendish</a>, ujilah apakah massa jenis Bumi kurang dari 5,5 kali massa jenis air pada tingkat signifikansi 0,05.</p>''',
    522: r'''\t\t<summary>Rincian:</summary>''',
    523: r'''\t\t<p>Statistik uji @@M1@@, nilai kritis @@M2@@. Gagal menolak @@M3@@.</p>''',
    528: r'''\t<p class="stat">Dengan <a href="JavaScript:openAncillary('../data/Short.html')" class="ancillary">data Short</a>, ujilah apakah paralaks Matahari berbeda dari 9 detik busur pada tingkat signifikansi 0,1.</p>''',
    530: r'''\t\t<summary>Rincian:</summary>''',
    531: r'''\t\t<p>Statistik uji @@M1@@, nilai kritis @@M2@@. Tolak @@M3@@.</p>''',
    536: r'''\t<p class="stat">Dengan <a href="JavaScript:openAncillary('../data/Fisher.html')" class="ancillary">data iris Fisher</a>, lakukan uji berikut pada tingkat signifikansi 0,1:</p>''',
    538: r'''\t\t<li>Rata-rata panjang mahkota iris Setosa berbeda dari 15 mm.</li>''',
    539: r'''\t\t<li>Rata-rata panjang mahkota iris Virginica lebih besar dari 52 mm.</li>''',
    540: r'''\t\t<li>Rata-rata panjang mahkota iris Versicolor kurang dari 44 mm.</li>''',
    543: r'''\t\t<summary>Rincian:</summary>''',
    545: r'''\t\t\t<li>Statistik uji @@M1@@, nilai kritis @@M2@@. Gagal menolak @@M3@@.</li>''',
    546: r'''\t\t\t<li>Statistik uji 4,556, nilai kritis 1,2991. Tolak @@M1@@.</li>''',
    547: r'''\t\t\t<li>Statistik uji @@M1@@, nilai kritis @@M2@@. Gagal menolak @@M3@@.</li>''',
    555: r'''\t\t<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    556: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    558: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Uji dalam Model Bernoulli">3</a></li>''',
    559: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Uji dalam Model Normal Dua Sampel">4</a></li>''',
    560: r'''\t\t<li class="child"><a href="Likelihood.html" title="Uji Rasio Kemungkinan">5</a></li>''',
    561: r'''\t\t<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    562: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    563: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    566: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    567: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    568: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


MATH_REPAIRS: dict[int, tuple[tuple[str, str], ...]] = {
    159: ((
        r'''\(m_0 = \mu_0 + \left[z(\alpha - p \alpha) + z(1 - p \alpha)\right] \frac{\sqrt{n}}{2 \sigma}\)''',
        r'''\(m_0 = \mu_0 + \left[z(\alpha - p \alpha) + z(1 - p \alpha)\right] \frac{\sigma}{2 \sqrt{n}}\)''',
    ),),
    171: ((
        r'''\[ Q(\mu) = \Phi \left( z(\alpha) + \frac{\sqrt{n}}{\sigma}(\mu - \mu_0) \right), \quad \mu \in \R \]''',
        r'''\[ Q(\mu) = \Phi \left( z(\alpha) - \frac{\sqrt{n}}{\sigma}(\mu - \mu_0) \right), \quad \mu \in \R \]''',
    ),),
    175: ((
        r'''<li>\(Q(\mu) \to 1\) as \(\mu \uparrow \infty\) and \(Q(\mu) \to 0\) as \(\mu \downarrow -\infty\).</li>''',
        r'''<li>\(Q(\mu) \to 0\) as \(\mu \uparrow \infty\) and \(Q(\mu) \to 1\) as \(\mu \downarrow -\infty\).</li>''',
    ),),
    181: ((
        r'''\[ Q(\mu) = \Phi \left( z(\alpha) - \frac{\sqrt{n}}{\sigma}(\mu - \mu_0) \right), \quad \mu \in \R \]''',
        r'''\[ Q(\mu) = \Phi \left( z(\alpha) + \frac{\sqrt{n}}{\sigma}(\mu - \mu_0) \right), \quad \mu \in \R \]''',
    ),),
    185: ((
        r'''<li>\(Q(\mu) \to 0\) as \(\mu \uparrow \infty\) and \(Q(\mu) \to 1\) as \(\mu \downarrow -\infty\).</li>''',
        r'''<li>\(Q(\mu) \to 1\) as \(\mu \uparrow \infty\) and \(Q(\mu) \to 0\) as \(\mu \downarrow -\infty\).</li>''',
    ),),
    239: ((
        r'''\( T \gt \mu_0 + t_{n-1}(1 - \alpha / 2) \frac{S}{\sqrt{n}} \)''',
        r'''\( M \gt \mu_0 + t_{n-1}(1 - \alpha / 2) \frac{S}{\sqrt{n}} \)''',
    ),),
    118: ((
        r'''\( \mu_0 \le M + z(1 - \alpha) \frac{\sigma}{\sqrt{n}}\)''',
        r'''\( \mu_0 \ge M - z(1 - \alpha) \frac{\sigma}{\sqrt{n}}\)''',
    ),),
    119: ((
        r'''\( \mu_0 \ge M - z(1 - \alpha) \frac{\sigma}{\sqrt{n}}\)''',
        r'''\( \mu_0 \le M + z(1 - \alpha) \frac{\sigma}{\sqrt{n}}\)''',
    ),),
    255: ((
        r'''\( \mu_0 \le M + t_{n-1}(1 - \alpha) \frac{S}{\sqrt{n}}\)''',
        r'''\( \mu_0 \ge M - t_{n-1}(1 - \alpha) \frac{S}{\sqrt{n}}\)''',
    ),),
    256: ((
        r'''\( \mu_0 \ge M - t_{n-1}(1 - \alpha) \frac{S}{\sqrt{n}}\)''',
        r'''\( \mu_0 \le M + t_{n-1}(1 - \alpha) \frac{S}{\sqrt{n}}\)''',
    ),),
    291: ((r'''\(\P\)''', r'''\(P\)'''),),
    315: ((r'''\( \frac{1}{2} \)''', r'''\( 2 \)'''),),
    348: (
        (r'''\(V \le \chi_{n-1}^2(\alpha - p \alpha)\)''', r'''\(V \lt \chi_{n-1}^2(\alpha - p \alpha)\)'''),
        (r'''\(V \ge \chi_{n-1}^2(1 - p \alpha)\)''', r'''\(V \gt \chi_{n-1}^2(1 - p \alpha)\)'''),
    ),
    366: (
        (r'''\((-\infty, \sigma_0)\)''', r'''\((0, \infty)\)'''),
        (r'''\((\sigma_0, \infty)\)''', r'''\(\sigma_0\)'''),
    ),
    388: ((r'''\(\sigma \uparrow \infty)\)''', r'''\(\sigma \uparrow \infty\)'''),),
    389: ((
        r'''\(Q(\sigma) \to 0\) as \(\sigma \uparrow \infty\) and as \(\sigma \downarrow 0\).</li>''',
        r'''\(Q(\sigma) \to 1\) as \(\sigma \downarrow 0\) and not as \(\sigma \uparrow \infty\).</li>''',
    ),),
    432: ((r'''\(\mu_0\)''', r'''\(\sigma_0\)'''),),
    418: ((r'''\(\P\)''', r'''\(P\)'''),),
    422: ((r'''\(\P\)''', r'''\(P\)'''),),
    449: ((r'''\(P = 0.0010\)''', r'''\(P \approx 0.0009\)'''),),
    466: ((r'''\(P \lt 0.0001\)''', r'''\(P \approx 0.00015\)'''),),
    505: ((r'''\(-2.328\)''', r'''\(-2.326\)'''),),
    545: ((r'''\(\pm 1.672\)''', r'''\(\pm 1.6766\)'''),),
    547: ((r'''\(-1.2988\)''', r'''\(-1.2991\)'''),),
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
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/sample/LLN.html": "../sample/LLN.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
    "https://www.randomservices.org/random/sample/Normal.html": "../sample/Normal.html",
    "https://www.randomservices.org/random/point/index.html": "../point/index.html",
    "https://www.randomservices.org/random/interval/index.html": "../interval/index.html",
    "https://www.randomservices.org/random/interval/Normal.html": "../interval/Normal.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probability, Mathematical Statistics, and Stochastic Processes</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID halaman stabil, pengalihan tautan korpus yang telah diterjemahkan ke edisi lokal, pengubahan tautan pelengkap menjadi HTTPS resmi, serta koreksi matematis, rujukan silang, jawaban, parameter, dan ejaan terbatas yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Penerjemahan dan rekayasa edisi dilakukan dengan OpenAI Codex gpt-5.6-sol, Ultra, atas instruksi pengguna. Seluruh kredit bagi sumber, penulis, dan kontributor manusia tetap dipertahankan.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
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
    source_counts = Counter(tag.name for tag in source.find_all(True))
    target_counts = Counter(tag.name for tag in target.find_all(True))
    if target_counts != source_counts:
        raise RuntimeError(
            f"parsed topology mismatch: source={dict(source_counts)}, target={dict(target_counts)}"
        )
    if sum(source_counts.values()) != 463:
        raise RuntimeError(f"unexpected parsed element count: {sum(source_counts.values())}")
    if [tag.name for tag in target.find_all(True)] != [tag.name for tag in source.find_all(True)]:
        raise RuntimeError("parsed element order changed")
    for selector, expected in (
        ("div.unit", 45),
        ("details", 20),
        ("summary", 20),
        ("h2,h3,h4", 10),
        ("img", 4),
        ("figure", 0),
    ):
        if len(target.select(selector)) != expected:
            raise RuntimeError(f"topology count mismatch for {selector}")
    source_ids = [tag["id"] for tag in source.find_all(id=True)]
    target_ids = [tag["id"] for tag in target.find_all(id=True)]
    if len(source_ids) != len(set(source_ids)) or len(target_ids) != len(set(target_ids)):
        raise RuntimeError("duplicate native/additive ID")
    expected_ids = set(source_ids) | {"o006.random.hypothesis.normal.page"}
    if set(target_ids) != expected_ids:
        raise RuntimeError(
            f"ID mismatch: missing={sorted(expected_ids-set(target_ids))}, "
            f"extra={sorted(set(target_ids)-expected_ids)}"
        )
    if target.select_one("div.unit:not([id])") is not None:
        raise RuntimeError("addressless instructional unit remains")


def assert_links(rendered: str) -> None:
    soup = BeautifulSoup(rendered, "html.parser")
    planned_hypothesis = {
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
            if parsed.scheme not in {"https"}:
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
        if relative in planned_hypothesis:
            pass  # all seven pages are a single concurrent local chapter batch
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
    if len(source_math) != 459 or len(expected_math) != 459 or target_math != expected_math:
        raise RuntimeError(
            f"protected-math mismatch: source={len(source_math)}, "
            f"expected={len(expected_math)}, target={len(target_math)}"
        )

    source_p = (len(re.findall(r"<p(?:\s|>)", source_text)), source_text.count("</p>"))
    target_p = (len(re.findall(r"<p(?:\s|>)", rendered)), rendered.count("</p>"))
    if source_p != (87, 87) or target_p != (90, 90):
        raise RuntimeError(f"paragraph-tag inventory mismatch: source={source_p}, target={target_p}")
    source_a = (len(re.findall(r"<a(?:\s|>)", source_text)), source_text.count("</a>"))
    target_a = (len(re.findall(r"<a(?:\s|>)", rendered)), rendered.count("</a>"))
    if source_a != (87, 88) or target_a != (91, 91):
        raise RuntimeError(f"anchor-tag repair mismatch: source={source_a}, target={target_a}")

    assert_topology(source_text, rendered)
    assert_links(rendered)

    for required in (
        'lang="id-ID"',
        'href="index.html"',
        'href="Introduction.html"',
        'href="Bernoulli.html"',
        'href="BivariateNormal.html"',
        'href="Likelihood.html"',
        'href="ChiSquare.html"',
        'href="../sample/CLT.html"',
        'href="../sample/Normal.html"',
        'href="../point/index.html"',
        'href="../interval/index.html"',
        'href="../interval/Normal.html"',
        "OpenAI Codex gpt-5.6-sol, Ultra",
        "data-o006-edition-notice=\"v1\"",
    ):
        if required not in rendered:
            raise RuntimeError(f"required translated surface missing: {required}")
    for forbidden in (
        'lang="en"',
        "JavaScript:openAncillary",
        ">Details:<",
        "Expand Details",
        "Contract Details",
        ">Hypothesis Testing<",
        ">Tests in the Normal Model<",
        ">Basic Theory<",
        ">Computational Exercises<",
        ">Data Analysis Exercises<",
        ">Apps<",
        ">Data Sets<",
        ">Biographies<",
        "has the chi-square distribution",
        "confidence level \\( \\alpha \\)",
        "0.0509",
        "Verginica",
        "values of \\(\\mu_0\\)",
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
        "463 core elements / 45 units / 20 disclosures / 459 protected TeX spans"
    )


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
