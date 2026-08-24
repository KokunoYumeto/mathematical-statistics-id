#!/usr/bin/env python3
"""Create the bounded id-ID likelihood-ratio-test target (Random ordinal 28)."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "hypothesis" / "Likelihood.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "hypothesis" / "Likelihood.html"
SOURCE_URL = "https://www.randomservices.org/random/hypothesis/Likelihood.html"
SOURCE_BYTES = 21772
SOURCE_SHA256 = "60b047835a3f644cd2317c8ab984b8d41ae7669f53c1d32a79705942670b9b04"
EXPECTED_SOURCE_LINES = 307

MATH_RE = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")
TOKEN_RE = re.compile(r"@@M(\d+)@@")


# Each translated line remains tied to its frozen authority line. Protected TeX
# is reinserted in authority order after the small, explicitly proved repair set.
T: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Uji Rasio Kemungkinan</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, uji hipotesis, uji rasio kemungkinan, lemma Neyman–Pearson, distribusi eksponensial, distribusi Bernoulli, distribusi normal, uji nonparametrik">''',
    32: r'''\t\t<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    33: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    34: r'''\t\t<li class="child"><a href="Normal.html" title="Pengujian pada Model Normal">2</a></li>''',
    35: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Pengujian pada Model Bernoulli">3</a></li>''',
    36: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Pengujian pada Model Normal Dua Sampel">4</a></li>''',
    38: r'''\t\t<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    39: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    40: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    42: r'''\t<h2 id="o006.random.hypothesis.likelihood.page">5. Uji Rasio Kemungkinan</h2>''',
    45: r'''<h3 id="the">Teori Dasar</h3>''',
    47: r'''<p>Seperti biasa, titik awal kita adalah suatu <a href="../prob/Experiments.html">percobaan acak</a> dengan <a href="../prob/Probability2.html">ruang probabilitas</a> yang mendasarinya, @@M1@@. Dalam model statistika dasar, kita mempunyai <a href="../prob/Probability.html">variabel acak</a> teramati @@M2@@ yang bernilai dalam suatu himpunan @@M3@@. Secara umum, struktur @@M4@@ dapat cukup rumit. Misalnya, jika percobaannya mengambil sampel @@M5@@ objek dari suatu populasi dan mencatat berbagai pengukuran yang diminati, maka''',
    51: r'''dengan @@M1@@ sebagai vektor pengukuran untuk objek ke-@@M2@@. Kasus khusus terpenting terjadi ketika @@M3@@ saling independen dan berdistribusi identik. Dalam kasus ini, kita mempunyai <a href="../sample/Introduction.html">sampel acak</a> berukuran @@M4@@ dari distribusi yang sama tersebut.</p>''',
    53: r'''<p>Pada bagian-bagian sebelumnya, kita membangun uji parameter berdasarkan statistik uji yang alami. Namun, dalam kasus lain, ujinya mungkin tidak parametrik atau mungkin tidak ada statistik awal yang jelas. Karena itu, kita memerlukan metode yang lebih umum untuk membangun statistik uji. Selain itu, kita belum mengetahui apakah uji-uji yang telah dibangun merupakan yang terbaik dalam arti memaksimumkan kuasa pada himpunan alternatif. Pada bagian ini dan bagian berikutnya, kita menyelidiki kedua gagasan tersebut. Fungsi kemungkinan, serupa dengan yang digunakan dalam <a href="../point/Likelihood.html">pendugaan kemungkinan maksimum</a>, akan memainkan peran utama.</p>''',
    55: r'''<h4 id="smp">Uji Hipotesis Sederhana</h4>''',
    58: r'''\t<p class="dfn">Andaikan @@M1@@ mempunyai salah satu dari dua distribusi yang sama-sama didominasi oleh suatu ukuran bersama. Hipotesis sederhana kita adalah</p>''',
    60: r'''\t\t<li>@@M1@@ mempunyai fungsi kepadatan—atau fungsi massa dalam kasus diskret—@@M2@@ terhadap ukuran tersebut.</li>''',
    61: r'''\t\t<li>@@M1@@ mempunyai fungsi kepadatan—atau fungsi massa dalam kasus diskret—@@M2@@ terhadap ukuran tersebut.</li>''',
    65: r'''<p>Kita menggunakan subskrip pada ukuran probabilitas @@M1@@ untuk menunjukkan kedua hipotesis. Fungsi @@M2@@ dan @@M3@@ dipahami terhadap ukuran pendominasi yang sama; titik tempat keduanya nol dapat dikeluarkan dari @@M4@@ tanpa mengubah kedua distribusi. Uji yang akan dibangun berlandaskan gagasan sederhana berikut: jika kita mengamati @@M5@@, kondisi @@M6@@ merupakan bukti yang mendukung hipotesis alternatif, sedangkan pertidaksamaan sebaliknya merupakan bukti yang menentangnya.</p>''',
    68: r'''\t<p class="dfn"><dfn>Fungsi rasio kemungkinan</dfn> @@M1@@ didefinisikan oleh''',
    70: r'''\tJika penyebutnya nol sedangkan pembilangnya positif, rasio ditetapkan tak hingga; jika pembilangnya nol sedangkan penyebutnya positif, rasio ditetapkan nol. Statistik @@M1@@ disebut <dfn>statistik rasio kemungkinan</dfn>.</p>''',
    73: r'''<p>Dengan menyatakan kembali pengamatan sebelumnya, perhatikan bahwa nilai kecil @@M1@@ merupakan bukti yang mendukung @@M2@@. Karena itu, statistik rasio kemungkinan layak dipertimbangkan sebagai statistik uji.</p>''',
    76: r'''\t<p class="math">Pertimbangkan uji nonacak yang menolak @@M1@@ jika dan hanya jika @@M2@@, dengan @@M3@@ suatu konstanta positif yang akan ditentukan. Tingkat signifikansi uji tersebut ialah @@M4@@.</p>''',
    79: r'''<p>Seperti biasa, kita dapat mencoba membangun uji dengan memilih @@M1@@ agar @@M2@@ sama dengan nilai yang ditetapkan. Jika @@M3@@ berdistribusi diskret, kesamaan eksak ini hanya mungkin ketika @@M4@@ merupakan nilai <a href="../dist/CDF.html">fungsi distribusi</a> @@M5@@; tingkat antara dua nilai yang dapat dicapai dapat diperoleh dengan mengacak keputusan pada batas daerah rasio kemungkinan. Kasus khusus penting model ini terjadi ketika distribusi @@M6@@ bergantung pada parameter @@M7@@ yang mempunyai dua nilai yang mungkin.</p>''',
    81: r'''<div class="unit" id="o006.random.hypothesis.likelihood.unit.simple-parameter-values">''',
    82: r'''\t<p class="dfn">Andaikan himpunan parameternya @@M1@@, dan @@M2@@ menyatakan fungsi kepadatan atau massa @@M3@@ ketika @@M4@@, sedangkan @@M5@@ menyatakan fungsi kepadatan atau massa @@M6@@ ketika @@M7@@. Hipotesis pada <a href="#smp0" class="ref"></a> ekuivalen dengan</p>''',
    89: r'''<p>Seperti telah disebutkan, kasus khusus penting lainnya terjadi ketika @@M1@@ merupakan sampel acak dari suatu distribusi.</p>''',
    91: r'''<div class="unit" id="o006.random.hypothesis.likelihood.unit.random-sample-form">''',
    92: r'''\t<p class="dfn">Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi variabel acak dasar @@M3@@ yang bernilai dalam himpunan @@M4@@ dan mempunyai fungsi kepadatan atau massa @@M5@@. Dalam kasus ini, @@M6@@ dan fungsi kepadatan atau massa @@M7@@ bagi @@M8@@ berbentuk''',
    94: r'''\tHipotesis pada <a href="#smp0" class="ref"></a> menyederhana menjadi</p>''',
    96: r'''\t\t<li>@@M1@@ mempunyai fungsi kepadatan atau massa @@M2@@.</li>''',
    97: r'''\t\t<li>@@M1@@ mempunyai fungsi kepadatan atau massa @@M2@@.</li>''',
    99: r'''\t<p>Statistik rasio kemungkinannya ialah''',
    103: r'''<p>Dalam kasus khusus ini, di bawah @@M1@@, statistik rasio kemungkinan sebagai fungsi ukuran sampel @@M2@@ merupakan sebuah <a href="../martingales/index.html">martingal</a>.</p>''',
    105: r'''<h4 id="ney">Lemma Neyman–Pearson</h4>''',
    107: r'''<p>Teorema berikut adalah <dfn>Lemma Neyman–Pearson</dfn>, yang dinamai menurut <a href="JavaScript:openAncillary('../biographies/Neyman.html')" class="ancillary">Jerzy Neyman</a> dan <a href="JavaScript:openAncillary('../biographies/PearsonE.html')" class="ancillary">Egon Pearson</a>. Teorema ini menunjukkan bahwa uji rasio kemungkinan di atas paling kuat pada ukurannya; jika tingkat target berada di antara ukuran-ukuran diskret yang dapat dicapai, uji dengan tingkat eksak mengacak keputusan pada himpunan batas. Misalkan''',
    109: r'''dan ingat bahwa <dfn>ukuran</dfn> suatu daerah penolakan adalah tingkat signifikansi uji dengan daerah penolakan tersebut.</p>''',
    112: r'''\t<p class="math">Pertimbangkan uji dengan daerah penolakan @@M1@@ di atas dan sembarang @@M2@@. Jika ukuran @@M3@@ sekurang-kurangnya sebesar ukuran @@M4@@, maka uji dengan daerah penolakan @@M5@@ lebih kuat daripada uji dengan daerah penolakan @@M6@@. Dengan kata lain, jika @@M7@@, maka @@M8@@.</p>''',
    114: r'''\t\t<summary>Rincian:</summary>''',
    115: r'''\t\t<p>Pertama, dari definisi @@M1@@ dan @@M2@@, perhatikan bahwa pertidaksamaan berikut berlaku:''',
    120: r'''\t\tSekarang, untuk sembarang @@M1@@, tuliskan @@M2@@ dan @@M3@@. Dari sifat aditif probabilitas dan pertidaksamaan di atas, diperoleh''',
    122: r'''\t\tKarena itu, jika @@M1@@, maka @@M2@@.</p>''',
    126: r'''<p>Lemma Neyman–Pearson jauh lebih berguna daripada yang mungkin tampak pada awalnya. Dalam banyak kasus penting, uji paling kuat yang <em>sama</em> berlaku untuk suatu rentang alternatif dan karena itu <em>seragam paling kuat</em> pada rentang tersebut. Kesimpulan seragam ini memerlukan struktur yang membuat aturan yang sama tetap paling kuat untuk setiap alternatif; lemma untuk sepasang hipotesis sederhana saja tidak memberikannya secara otomatis. Beberapa kasus khusus dibahas di bawah.</p>''',
    128: r'''<h4 id="gen">Rasio Kemungkinan Tergeneralisasi</h4>''',
    130: r'''<p>Statistik rasio kemungkinan dapat digeneralisasi ke hipotesis majemuk. Andaikan kembali bahwa fungsi kepadatan atau massa @@M1@@ dari variabel data @@M2@@ bergantung pada parameter @@M3@@ yang bernilai dalam himpunan parameter @@M4@@. Pertimbangkan hipotesis @@M5@@ melawan @@M6@@, dengan @@M7@@.</p>''',
    133: r'''\t<p class="math">Definisikan''',
    135: r'''\tFungsi @@M1@@ disebut <dfn>fungsi rasio kemungkinan</dfn>, dan @@M2@@ disebut <dfn>statistik rasio kemungkinan</dfn>. Definisi ini digunakan pada titik data ketika supremum penyebut positif dan hingga; supremum tidak harus dicapai. Kasus nol atau tak hingga memerlukan konvensi rasio diperluas yang sama seperti di atas.</p>''',
    138: r'''<p>Dengan alasan yang sama seperti sebelumnya, nilai kecil @@M1@@ merupakan bukti yang mendukung hipotesis alternatif.</p>''',
    140: r'''<h3 id="exa">Contoh dan Kasus Khusus</h3>''',
    142: r'''<h4 id="exp">Uji pada Model Eksponensial</h4>''',
    144: r'''<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../poisson/Exponential.html">distribusi eksponensial</a> dengan parameter skala @@M3@@. Variabel sampel tersebut, misalnya, dapat menyatakan masa pakai sampel perangkat dari jenis tertentu.</p>''',
    146: r'''<div class="unit" id="o006.random.hypothesis.likelihood.unit.exponential-simple-hypotheses">''',
    147: r'''\t<p class="dfn">Pertimbangkan hipotesis sederhana @@M1@@ melawan @@M2@@, dengan @@M3@@ merupakan dua nilai tertentu yang berbeda.</p>''',
    150: r'''<p>Ingat bahwa jumlah variabel merupakan statistik cukup bagi @@M1@@:''',
    152: r'''Ingat pula bahwa @@M1@@ mempunyai <a href="../special/Gamma.html">distribusi gamma</a> dengan parameter bentuk @@M2@@ dan parameter skala @@M3@@. Untuk @@M4@@, kita menuliskan kuantil berorde @@M5@@ dari distribusi ini sebagai @@M6@@.</p>''',
    155: r'''\t<p class="math">Statistik rasio kemungkinannya ialah''',
    158: r'''\t\t<summary>Rincian:</summary>''',
    159: r'''\t\t<p>Ingat bahwa fungsi kepadatan @@M1@@ bagi distribusi eksponensial dengan parameter skala @@M2@@ diberikan oleh @@M3@@ untuk @@M4@@. Jika @@M5@@ menyatakan fungsi kepadatan ketika @@M6@@ untuk @@M7@@, maka''',
    161: r'''\t\tKarena itu, fungsi rasio kemungkinannya ialah''',
    163: r'''\t\tdengan @@M1@@.</p>''',
    168: r'''\t<p class="math">Uji-uji berikut merupakan uji paling kuat pada tingkat @@M1@@:</p>''',
    170: r'''\t\t<li>Andaikan @@M1@@. Tolak @@M2@@ melawan @@M3@@ jika dan hanya jika @@M4@@.</li>''',
    171: r'''\t\t<li>Andaikan @@M1@@. Tolak @@M2@@ melawan @@M3@@ jika dan hanya jika @@M4@@.</li>''',
    174: r'''\t\t<summary>Rincian:</summary>''',
    175: r'''\t\t<p>Di bawah @@M1@@, @@M2@@ mempunyai distribusi gamma dengan parameter @@M3@@ dan @@M4@@.</p>''',
    177: r'''\t\t\t<li>Jika @@M1@@, maka @@M2@@. Dengan aljabar sederhana, daerah penolakan berbentuk @@M3@@ berubah menjadi daerah penolakan berbentuk @@M4@@. Nilai tepat @@M5@@ dalam kaitannya dengan @@M6@@ tidak penting. Agar uji mempunyai tingkat signifikansi @@M7@@, kita harus memilih @@M8@@.</li>''',
    178: r'''\t\t\t<li>Jika @@M1@@, maka @@M2@@. Dengan aljabar sederhana, daerah penolakan berbentuk @@M3@@ berubah menjadi daerah penolakan berbentuk @@M4@@. Sekali lagi, nilai tepat @@M5@@ dalam kaitannya dengan @@M6@@ tidak penting. Agar uji mempunyai tingkat signifikansi @@M7@@, kita harus memilih @@M8@@.</li>''',
    183: r'''<p>Perhatikan bahwa uji-uji ini tidak bergantung pada nilai @@M1@@. Fakta tersebut, bersama monotonisitas fungsi kuasa, menunjukkan bahwa uji-uji itu seragam paling kuat untuk uji satu sisi yang lazim.</p>''',
    186: r'''\t<p class="math">Andaikan @@M1@@.</p>''',
    188: r'''\t\t<li>Aturan keputusan pada bagian (a) di atas seragam paling kuat untuk menguji @@M1@@ melawan @@M2@@.</li>''',
    189: r'''\t\t<li>Aturan keputusan pada bagian (b) di atas seragam paling kuat untuk menguji @@M1@@ melawan @@M2@@.</li>''',
    193: r'''<h4 id="ber">Uji pada Model Bernoulli</h4>''',
    195: r'''<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../bernoulli/Introduction.html">distribusi Bernoulli</a> dengan parameter sukses @@M3@@. Sampel tersebut dapat menyatakan hasil pelemparan koin sebanyak @@M4@@ kali, dengan @@M5@@ sebagai probabilitas munculnya sisi kepala.</p>''',
    197: r'''<div class="unit" id="o006.random.hypothesis.likelihood.unit.bernoulli-simple-hypotheses">''',
    198: r'''\t<p class="dfn">Pertimbangkan hipotesis sederhana @@M1@@ melawan @@M2@@, dengan @@M3@@ merupakan dua nilai tertentu yang berbeda.</p>''',
    201: r'''<p>Dalam model pelemparan koin, kita mengetahui bahwa probabilitas kepala adalah @@M1@@ atau @@M2@@, tetapi tidak mengetahui yang mana. Ingat bahwa banyaknya sukses merupakan statistik cukup bagi @@M3@@:''',
    203: r'''Ingat pula bahwa @@M1@@ mempunyai <a href="../bernoulli/Binomial.html">distribusi binomial</a> dengan parameter @@M2@@ dan @@M3@@. Untuk @@M4@@, kita menuliskan kuantil berorde @@M5@@ dari distribusi ini sebagai @@M6@@. Kuantil tersebut terdefinisi untuk setiap @@M7@@, tetapi karena distribusinya diskret, hanya tingkat penolakan nonacak tertentu yang dapat dicapai secara eksak; tingkat antara dua nilai dapat dicapai melalui pengacakan pada batas.</p>''',
    206: r'''\t<p class="math">Statistik rasio kemungkinannya ialah''',
    209: r'''\t\t<summary>Rincian:</summary>''',
    210: r'''\t\t<p>Ingat bahwa fungsi massa @@M1@@ bagi distribusi Bernoulli dengan parameter @@M2@@ diberikan oleh @@M3@@ untuk @@M4@@. Jika @@M5@@ menyatakan fungsi massa ketika @@M6@@ untuk @@M7@@, maka''',
    212: r'''\t\tKarena itu, fungsi rasio kemungkinannya ialah''',
    214: r'''\t\tdengan @@M1@@.</p>''',
    219: r'''\t<p class="math">Daerah penolakan berikut mempunyai arah uji paling kuat. Karena distribusi binomial diskret, untuk tingkat target @@M1@@ pilih ambang bilangan bulat yang membuat ukuran nonacak tidak melebihi tingkat tersebut; tingkat eksak diperoleh, bila diperlukan, dengan pengacakan pada titik batas. Ambang kuantil yang ditampilkan merupakan notasi nominal dan peluang ekor aktual harus diperiksa.</p>''',
    221: r'''\t\t<li>Andaikan @@M1@@. Tolak @@M2@@ melawan @@M3@@ jika dan hanya jika @@M4@@.</li>''',
    222: r'''\t\t<li>Andaikan @@M1@@. Tolak @@M2@@ melawan @@M3@@ jika dan hanya jika @@M4@@.</li>''',
    225: r'''\t\t<summary>Rincian:</summary>''',
    226: r'''\t\t<p>Di bawah @@M1@@, @@M2@@ mempunyai distribusi binomial dengan parameter @@M3@@ dan @@M4@@.</p>''',
    228: r'''\t\t\t<li>Jika @@M1@@, maka @@M2@@. Dengan aljabar sederhana, daerah penolakan berbentuk @@M3@@ berubah menjadi daerah penolakan berbentuk @@M4@@. Nilai tepat @@M5@@ dalam kaitannya dengan @@M6@@ tidak penting. Untuk mengalibrasi tingkat target @@M7@@, hitung peluang ekor binomial pada batas bilangan bulat; @@M8@@ adalah notasi kuantil nominal. Gunakan daerah nonacak terbesar yang ukurannya tidak melebihi target, lalu acak pada batas jika ukuran eksak diperlukan.</li>''',
    229: r'''\t\t\t<li>Jika @@M1@@, maka @@M2@@. Dengan aljabar sederhana, daerah penolakan berbentuk @@M3@@ berubah menjadi daerah penolakan berbentuk @@M4@@. Sekali lagi, nilai tepat @@M5@@ dalam kaitannya dengan @@M6@@ tidak penting. Untuk mengalibrasi tingkat target @@M7@@, hitung peluang ekor binomial pada batas bilangan bulat; @@M8@@ adalah notasi kuantil nominal. Gunakan daerah nonacak terbesar yang ukurannya tidak melebihi target, lalu acak pada batas jika ukuran eksak diperlukan.</li>''',
    235: r'''<p>Perhatikan bahwa arah daerah penolakan ini tidak bergantung pada nilai @@M1@@. Fakta tersebut, bersama monotonisitas fungsi kuasa, menunjukkan bahwa aturan satu sisi yang telah dikalibrasi—termasuk pengacakan batas bila tingkat eksak diminta—seragam paling kuat pada tingkat yang dipilih.</p>''',
    237: r'''<div class="unit" id="o006.random.hypothesis.likelihood.unit.bernoulli-ump">''',
    238: r'''\t<p class="math">Andaikan @@M1@@.</p>''',
    240: r'''\t\t<li>Aturan keputusan pada bagian (a) di atas, setelah kalibrasi tingkat diskret seperti dijelaskan, seragam paling kuat untuk menguji @@M1@@ melawan @@M2@@.</li>''',
    241: r'''\t\t<li>Aturan keputusan pada bagian (b) di atas, setelah kalibrasi tingkat diskret seperti dijelaskan, seragam paling kuat untuk menguji @@M1@@ melawan @@M2@@.</li>''',
    245: r'''<h4 id="nor">Uji pada Model Normal</h4>''',
    247: r'''<p>Di antara uji satu sisi yang diturunkan dalam <a href="Normal.html">model normal</a>, uji untuk @@M1@@ ketika @@M2@@ diketahui memang seragam paling kuat. Ketika terdapat parameter pengganggu—@@M3@@ dengan @@M4@@ tidak diketahui, atau @@M5@@ dengan @@M6@@ tidak diketahui—klaim seragam paling kuat tanpa pembatasan perlu dikualifikasi: uji baku mempunyai sifat optimal dalam kelas relevan seperti uji invarian, uji dengan ukuran konstan terhadap parameter pengganggu (similar), atau uji tak bias di bawah model normal, tetapi tidak otomatis seragam paling kuat di antara semua uji. Tidak satu pun uji dua sisi tersebut seragam paling kuat tanpa pembatasan tambahan.</p>''',
    249: r'''<h4 id="non">Contoh Nonparametrik</h4>''',
    251: r'''<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@, baik dari <a href="../poisson/Poisson.html">distribusi Poisson</a> berparameter 1 maupun dari <a href="../bernoulli/Geometric.html">distribusi geometrik</a> pada @@M3@@ dengan parameter @@M4@@. Perhatikan bahwa kedua distribusi mempunyai <a href="../expect/Properties.html">rata-rata</a> 1, meskipun distribusi Poisson mempunyai <a href="../expect/Variance.html">varians</a> 1 sedangkan distribusi geometrik mempunyai varians 2.</p>''',
    253: r'''<div class="unit" id="o006.random.hypothesis.likelihood.unit.nonparametric-simple-hypotheses">''',
    254: r'''\t<p class="dfn">Pertimbangkan hipotesis sederhana</p>''',
    256: r'''\t\t<li>@@M1@@ mempunyai fungsi massa @@M2@@ untuk @@M3@@.</li>''',
    257: r'''\t\t<li>@@M1@@ mempunyai fungsi massa @@M2@@ untuk @@M3@@.</li>''',
    262: r'''\t<p class="math">Statistik rasio kemungkinannya ialah''',
    265: r'''\t\t<summary>Rincian:</summary>''',
    266: r'''\t\t<p>Perhatikan bahwa''',
    268: r'''\t\tKarena itu, fungsi rasio kemungkinannya ialah''',
    270: r'''\t\tdengan @@M1@@ dan @@M2@@.</p>''',
    275: r'''\t<p class="math">Uji paling kuat berbentuk berikut, dengan @@M1@@ suatu konstanta: tolak @@M2@@ jika dan hanya jika @@M3@@.</p>''',
    277: r'''\t\t<summary>Rincian:</summary>''',
    278: r'''\t\t<p>Daerah penolakan berbentuk @@M1@@ ekuivalen dengan''',
    280: r'''\t\tDengan mengambil logaritma natural, bentuk ini ekuivalen dengan @@M1@@, dengan @@M2@@.</p>''',
    287: r'''\t\t<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    288: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    289: r'''\t\t<li class="child"><a href="Normal.html" title="Pengujian pada Model Normal">2</a></li>''',
    290: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Pengujian pada Model Bernoulli">3</a></li>''',
    291: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Pengujian pada Model Normal Dua Sampel">4</a></li>''',
    293: r'''\t\t<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    294: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    295: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    298: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    299: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Kumpulan Data</a></li>''',
    300: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


MATH_REPAIRS: dict[int, tuple[tuple[str, str], ...]] = {
    68: ((r'''\( L: S \to (0, \infty) \)''', r'''\( L: S \to [0, \infty] \)'''),),
    117: ((r'''\text{ for }''', r'''\text{ untuk }'''),),
    118: ((r'''\text{ for }''', r'''\text{ untuk }'''),),
    130: (
        (r'''\(\theta \in T_0\)''', r'''\(\theta \in \Theta_0\)'''),
        (r'''\(\theta \notin T_0\)''', r'''\(\theta \notin \Theta_0\)'''),
    ),
    152: ((r'''\(\alpha \gt 0\)''', r'''\(\alpha \in (0, 1)\)'''),),
    211: ((
        r'''p_1^x (1 - p_1^{1-x}''',
        r'''p_1^x (1 - p_1)^{1-x}''',
    ),),
    222: (
        (r'''\(p = p_0\)''', r'''\(H_0: p = p_0\)'''),
        (r'''\(p = p_1\)''', r'''\(H_1: p = p_1\)'''),
    ),
    263: (
        (r'''\text{ where }''', r'''\text{ dengan }'''),
        (r'''\text{ and }''', r'''\text{ dan }'''),
    ),
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
    "https://www.randomservices.org/random/point/Likelihood.html": "../point/Likelihood.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probability, Mathematical Statistics, and Stochastic Processes</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan korpus yang telah diterjemahkan ke edisi lokal, pengubahan tautan pelengkap menjadi HTTPS resmi, serta koreksi terbatas atas cakupan ukuran pendominasi dan kepadatan nol, pengacakan pada batas, notasi himpunan parameter, ranah kuantil, formula Bernoulli, label hipotesis, tingkat diskret, dan klaim optimalitas berparameter pengganggu; semuanya dicatat dalam daftar koreksi edisi.</p>
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
    if sum(source_counts.values()) != 212:
        raise RuntimeError(f"unexpected parsed element count: {sum(source_counts.values())}")
    if [tag.name for tag in target.find_all(True)] != [tag.name for tag in source.find_all(True)]:
        raise RuntimeError("parsed element order changed")
    for selector, expected in (
        ("div.unit", 18),
        ("details", 7),
        ("summary", 7),
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
    additive_ids = {
        "o006.random.hypothesis.likelihood.page",
        "o006.random.hypothesis.likelihood.unit.simple-parameter-values",
        "o006.random.hypothesis.likelihood.unit.random-sample-form",
        "o006.random.hypothesis.likelihood.unit.exponential-simple-hypotheses",
        "o006.random.hypothesis.likelihood.unit.bernoulli-simple-hypotheses",
        "o006.random.hypothesis.likelihood.unit.bernoulli-ump",
        "o006.random.hypothesis.likelihood.unit.nonparametric-simple-hypotheses",
    }
    if set(target_ids) != set(source_ids) | additive_ids:
        raise RuntimeError(
            f"ID mismatch: missing={sorted((set(source_ids)|additive_ids)-set(target_ids))}, "
            f"extra={sorted(set(target_ids)-(set(source_ids)|additive_ids))}"
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
            pass  # all seven pages belong to this one concurrent local chapter batch
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
    if len(source_math) != 252 or len(expected_math) != 252 or target_math != expected_math:
        raise RuntimeError(
            f"protected-math mismatch: source={len(source_math)}, "
            f"expected={len(expected_math)}, target={len(target_math)}"
        )

    source_p = (len(re.findall(r"<p(?:\s|>)", source_text)), source_text.count("</p>"))
    target_p = (len(re.findall(r"<p(?:\s|>)", rendered)), rendered.count("</p>"))
    if source_p != (45, 45) or target_p != (48, 48):
        raise RuntimeError(f"paragraph-tag inventory mismatch: source={source_p}, target={target_p}")
    source_a = (len(re.findall(r"<a(?:\s|>)", source_text)), source_text.count("</a>"))
    target_a = (len(re.findall(r"<a(?:\s|>)", rendered)), rendered.count("</a>"))
    if source_a != (37, 37) or target_a != (41, 41):
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
        'href="ChiSquare.html"',
        'href="../sample/Introduction.html"',
        'href="../point/Likelihood.html"',
        r'''\( L: S \to [0, \infty] \)''',
        r'''\(\theta \in \Theta_0\)''',
        r'''\(\alpha \in (0, 1)\)''',
        r'''p_1^x (1 - p_1)^{1-x}''',
        r'''\(H_0: p = p_0\)''',
        r'''\(H_1: p = p_1\)''',
        "ukuran pendominasi yang sama",
        "mengacak keputusan pada batas",
        "parameter pengganggu",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        'data-o006-edition-notice="v1"',
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
        ">Likelihood Ratio Tests<",
        ">Basic Theory<",
        ">Tests of Simple Hypotheses<",
        ">Generalized Likelihood Ratio<",
        ">Examples and Special Cases<",
        ">Apps<",
        ">Data Sets<",
        ">Biographies<",
        "sample form a distribution",
        "distribution an underlying random variable",
        r'''\(\theta \in T_0\)''',
        r'''\(\theta \notin T_0\)''',
        r'''\(\alpha \gt 0\)''',
        r'''p_1^x (1 - p_1^{1-x}''',
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
        "212 core elements / 18 units / 7 disclosures / 252 protected TeX spans"
    )


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
