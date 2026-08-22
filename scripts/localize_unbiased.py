#!/usr/bin/env python3
"""Create the bounded id-ID Best Unbiased Estimators target.

Translations use @@M1@@, @@M2@@, ... placeholders. Each placeholder is
restored from the corresponding delimited TeX span in the hash-locked
authority row, so translated templates never embed TeX backslashes.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "point" / "Unbiased.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "point" / "Unbiased.html"
SOURCE_URL = "https://www.randomservices.org/random/point/Unbiased.html"
SOURCE_SHA256 = "0d9765c5c7b5b8a54b29fc45c3a435d20e2a9200e027609658345087dedcd531"
EXPECTED_SOURCE_BYTES = 28635
EXPECTED_SOURCE_LINES = 411
MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)
TOKEN_RE = re.compile(r"@@M([1-9][0-9]*)@@")


# Only reader-facing rows are replaced. Formula-only rows remain exact source
# bytes unless listed in BOUNDED_FIXES.
T: dict[int, str] = {
    2: '<html lang="id-ID">',
    6: "\t<title>Penduga Tak Bias Terbaik</title>",
    9: '\t<meta name="keywords" content="probabilitas, statistika, pendugaan titik, penduga tak bias, galat kuadrat rata-rata, penduga tak bias terbaik, batas bawah Cramer-Rao, penduga linear tak bias terbaik, distribusi Bernoulli, distribusi Poisson, distribusi normal, distribusi gamma, distribusi beta, distribusi seragam">',
    36: '\t\t<li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>',
    37: '\t\t<li class="child"><a href="Estimators.html" title="Penduga">1</a></li>',
    38: '\t\t<li class="child"><a href="Moments.html" title="Metode Momen">2</a></li>',
    39: '\t\t<li class="child"><a href="Likelihood.html" title="Kemungkinan Maksimum">3</a></li>',
    40: '\t\t<li class="child"><a href="Bayes.html" title="Penduga Bayes">4</a></li>',
    42: '\t\t<li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancillary">6</a></li>',
    43: '\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>',
    44: '\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>',
    46: '\t<h2 id="o006.random.point.unbiased.page">5. Penduga Tak Bias Terbaik</h2>',
    49: '<h3 id="the">Teori Dasar</h3>',
    51: '<p>Tinjau kembali model statistika dasar: sebuah <a href="../prob/Experiments.html">eksperimen acak</a> menghasilkan <a href="../prob/Probability.html">variabel acak</a> teramati @@M1@@ yang nilainya berada dalam himpunan @@M2@@. Eksperimen tersebut biasanya mengambil sampel @@M3@@ objek dari suatu populasi lalu mencatat satu atau beberapa pengukuran untuk setiap objek. Dalam hal ini, variabel acak teramati berbentuk',
    53: 'dengan @@M1@@ sebagai vektor pengukuran untuk objek ke-@@M2@@.</p>',
    55: '<p>Andaikan @@M1@@ merupakan parameter riil distribusi @@M2@@, dengan nilai dalam himpunan parameter @@M3@@. Misalkan @@M4@@ menyatakan <a href="../dist/index.html">fungsi kepadatan probabilitas</a> bagi @@M5@@ untuk @@M6@@. Perhatikan bahwa operator <a href="../expect/Properties.html">nilai harapan</a>, <a href="../expect/Variance.html">varians</a>, dan <a href="../expect/Covariance.html">kovarians</a> juga bergantung pada @@M7@@, meskipun subskripnya kadang dihilangkan agar notasi tidak terlalu rumit.</p>',
    57: '<h4 id="dfn">Definisi</h4>',
    59: '<p>Andaikan sekarang @@M1@@ merupakan parameter sasaran yang diturunkan dari @@M2@@. (Tentu saja, @@M3@@ dapat sama dengan @@M4@@, tetapi secara umum dapat pula berupa fungsi dari @@M5@@.) Pada bagian ini kita membahas masalah umum untuk mencari <a href="Estimators.html">penduga</a> terbaik bagi @@M6@@ di antara suatu kelas penduga tak bias. Ingat bahwa jika @@M7@@ merupakan penduga tak bias bagi @@M8@@, maka @@M9@@ adalah galat kuadrat rata-ratanya. Galat kuadrat rata-rata menjadi ukuran mutu penduga tak bias, sehingga definisi berikut bersifat alami.</p>',
    62: '\t<p class="dfn">Andaikan @@M1@@ dan @@M2@@ merupakan penduga tak bias bagi @@M3@@.</p>',
    64: '\t\t<li>Jika @@M1@@ untuk setiap @@M2@@, maka @@M3@@ merupakan penduga yang <dfn>lebih baik secara seragam</dfn> daripada @@M4@@.</li>',
    65: '\t\t<li>Jika @@M1@@ lebih baik secara seragam daripada setiap penduga tak bias lain bagi @@M2@@, maka @@M3@@ merupakan <dfn>Penduga Tak Bias dengan Varians Minimum Seragam</dfn> (<dfn>UMVUE</dfn>) bagi @@M4@@.</li>',
    69: '<p>Untuk penduga tak bias @@M1@@ dan @@M2@@ bagi @@M3@@, varians @@M4@@ mungkin lebih kecil pada sebagian nilai @@M5@@, sedangkan varians @@M6@@ lebih kecil pada nilai @@M7@@ lainnya. Dalam keadaan itu tidak satu pun lebih baik secara seragam daripada yang lain. Penduga tak bias bervarians minimum adalah mutu terbaik yang dapat kita harapkan.</p>',
    71: '<h4 id="crb">Batas Bawah Cram&eacute;r-Rao</h4>',
    73: '<p>Kita akan menunjukkan bahwa, dengan syarat regularitas yang dinyatakan di bawah, varians setiap penduga tak bias bagi parameter @@M1@@ mempunyai batas bawah. Jadi, jika suatu penduga mencapai batas itu untuk setiap @@M2@@, penduga tersebut harus merupakan UMVUE bagi @@M3@@. Turunan <a href="Likelihood.html">fungsi log-kemungkinan</a>, yang kadang disebut <dfn>skor</dfn>, berperan utama dalam analisis ini. Negatif turunan keduanya berperan lebih kecil, tetapi tetap penting. Kita beri nama kedua fungsi tersebut agar pembahasan lebih ringkas.</p>',
    76: '\t<p class="dfn">Untuk @@M1@@ dan @@M2@@, definisikan',
    83: '<p>Pada sisa subbagian ini, kita meninjau statistik @@M1@@ dengan @@M2@@ (jadi, khususnya, @@M3@@ tidak bergantung pada @@M4@@). Kita memerlukan asumsi pokok berikut.</p>',
    86: '\t<p class="dfn">Kita hanya meninjau statistik @@M1@@ yang memenuhi @@M2@@ untuk @@M3@@. Kita juga mengasumsikan bahwa',
    88: '\tArtinya, operator turunan @@M1@@ boleh dipertukarkan dengan operator nilai harapan @@M2@@.</p>',
    90: '\t\t<summary>Rincian:</summary>',
    91: '\t\t<p>Perhatikan terlebih dahulu bahwa',
    93: '\t\tDi sisi lain,',
    98: '\t\tJadi, kedua ungkapan itu sama tepat ketika operator turunan dan integral boleh dipertukarkan.</p>',
    102: '<p>Secara umum, pertukaran dalam asumsi pokok di atas dapat dijamin apabila @@M1@@ terdiferensialkan terhadap @@M2@@ dan, pada suatu lingkungan setiap nilai parameter, nilai mutlak hasil kali fungsi statistik dengan turunan tersebut didominasi oleh fungsi terintegralkan. Kekontinuan bersama terhadap @@M3@@ dan @@M4@@ membantu memeriksa syarat itu. Himpunan dukungan @@M5@@ juga tidak boleh bergantung pada @@M6@@. Kekontinuan saja tidak menggantikan syarat dominasi. Untuk memakai bentuk batas yang membagi dengan informasi Fisher, informasi tersebut juga harus positif dan berhingga.</p>',
    105: '\t<p class="math">@@M1@@ untuk @@M2@@.</p>',
    107: '\t\t<summary>Rincian:</summary>',
    108: '\t\t<p>Hasil ini mengikuti asumsi <a href="#crb2" class="ref"></a> dengan mengambil @@M1@@ untuk @@M2@@.</p>',
    113: '\t<p class="math">Jika @@M1@@ merupakan statistik, maka</p>',
    116: '\t\t<summary>Rincian:</summary>',
    117: '\t\t<p>Pertama, kovarians tersebut sama dengan nilai harapan hasil kali kedua variabel karena variabel kedua mempunyai rata-rata 0 menurut <a href="#crb3" class="ref"></a>. Hasilnya kemudian mengikuti asumsi <a href="#crb2" class="ref"></a>.</p>',
    124: '\t\t<summary>Rincian:</summary>',
    125: '\t\t<p>Hasil ini berlaku karena @@M1@@ mempunyai rata-rata 0 menurut <a href="#crb3" class="ref"></a>.</p>',
    129: '<p>Teorema berikut memberikan <dfn>batas bawah Cram&eacute;r-Rao</dfn> umum untuk varians suatu statistik. Batas ini dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Cramer.html\')" class="ancillary">Harold Cram&eacute;r</a> dan <a href="JavaScript:openAncillary(\'../biographies/Rao.html\')" class="ancillary">CR Rao</a>.</p>',
    132: '\t<p class="math">Jika @@M1@@ merupakan statistik, maka',
    135: '\t\t<summary>Rincian:</summary>',
    136: '\t\t<p>Dari <a href="../expect/Covariance.html#blp6">ketaksamaan korelasi</a>,',
    138: '\t\tHasilnya sekarang mengikuti teorema <a href="#crb4" class="ref"></a> dan <a href="#crb5" class="ref"></a>.</p>',
    142: '<p>Sekarang kita dapat memberikan bentuk pertama batas bawah Cram&eacute;r-Rao bagi penduga tak bias suatu parameter.</p>',
    145: '\t<p class="math">Andaikan @@M1@@ merupakan parameter sasaran dan @@M2@@ merupakan penduga tak bias bagi @@M3@@. Maka',
    148: '\t\t<summary>Rincian:</summary>',
    149: '\t\t<p>Hasil ini langsung mengikuti <a href="#crb6" class="ref"></a> karena @@M1@@ untuk @@M2@@.</p>',
    153: '<p>Penduga bagi @@M1@@ yang mencapai batas bawah Cram&eacute;r-Rao untuk setiap nilai parameter merupakan penduga tak bias dengan varians minimum seragam (UMVUE) bagi @@M2@@.</p>',
    156: '\t<p class="math">Pada setiap nilai parameter yang tetap, kesamaan dalam <a href="#crb7" class="ref"></a> berlaku tepat ketika @@M1@@ dapat ditulis memakai suatu fungsi @@M2@@ sebagai berikut, dengan probabilitas 1. Jika hubungan berikut berlaku untuk setiap nilai parameter, batas tercapai di seluruh ruang parameter dan penduga tersebut merupakan UMVUE:',
    159: '\t\t<summary>Rincian:</summary>',
    160: '\t\t<p>Kesamaan dalam ketaksamaan korelasi berlaku tepat ketika kedua variabel acak merupakan transformasi linear satu sama lain. Ingat pula bahwa @@M1@@ mempunyai rata-rata 0.</p>',
    164: '<p>Kuantitas @@M1@@ yang muncul pada penyebut batas bawah dalam teorema <a href="#crb7" class="ref"></a> dan <a href="#crb8" class="ref"></a> disebut <dfn>bilangan informasi Fisher</dfn> bagi @@M2@@, dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Fisher.html\')" class="ancillary">Sir Ronald Fisher</a>. Teorema berikut memberikan bentuk alternatif bilangan informasi Fisher yang biasanya lebih mudah dihitung.</p>',
    167: '\t<p class="math">Jika turunan yang diperlukan ada dan pertukaran operator yang diperlukan sah, maka',
    171: '<p>Teorema berikut memberikan bentuk kedua batas bawah Cram&eacute;r-Rao bagi penduga tak bias suatu parameter.</p>',
    174: '\t<p class="math">Jika @@M1@@ merupakan parameter sasaran dan @@M2@@ merupakan penduga tak bias bagi @@M3@@, maka</p>',
    177: '\t\t<summary>Rincian:</summary>',
    178: '\t\t<p>Hasil ini mengikuti teorema <a href="#crb7" class="ref"></a> dan <a href="#crb9" class="ref"></a>.</p>',
    182: '<h4 id="sam">Sampel Acak</h4>',
    184: '<p>Andaikan sekarang @@M1@@ merupakan <a href="../sample/Introduction.html">sampel acak</a> berukuran @@M2@@ dari distribusi variabel acak @@M3@@ yang mempunyai fungsi kepadatan probabilitas @@M4@@ dan bernilai dalam himpunan @@M5@@. Jadi, @@M6@@. Kita memakai huruf kecil untuk turunan fungsi log-kemungkinan satu pengamatan @@M7@@ dan negatif turunan kedua fungsi log-kemungkinan @@M8@@.</p>',
    187: '\t<p class="dfn">Untuk @@M1@@ dan @@M2@@, definisikan',
    195: '\t<p class="math">@@M1@@ dapat ditulis dalam @@M2@@, sedangkan @@M3@@ dapat ditulis dalam @@M4@@:</p>',
    202: '<p>Teorema berikut memberikan bentuk kedua batas bawah Cram&eacute;r-Rao umum bagi varians suatu statistik, yang dikhususkan untuk sampel acak.</p>',
    205: '\t<p class="math">Jika @@M1@@ merupakan statistik, maka</p>',
    209: '<p>Teorema berikut memberikan bentuk ketiga batas bawah Cram&eacute;r-Rao bagi penduga tak bias suatu parameter, yang dikhususkan untuk sampel acak.</p>',
    212: '\t<p class="math">Andaikan @@M1@@ merupakan parameter sasaran dan @@M2@@ merupakan penduga tak bias bagi @@M3@@. Maka',
    216: '<p>Perhatikan bahwa batas bawah Cram&eacute;r-Rao berbanding terbalik dengan ukuran sampel @@M1@@. Bentuk berikut memberikan versi keempat batas bawah tersebut bagi penduga tak bias suatu parameter, sekali lagi khusus untuk sampel acak.</p>',
    219: '\t<p class="math">Jika turunan yang diperlukan ada dan pertukaran operator yang diperlukan sah, maka',
    223: '<p>Ringkasnya, terdapat empat bentuk batas bawah Cram&eacute;r-Rao bagi varians penduga tak bias untuk @@M1@@: <a href="#crb7" class="ref"></a> dan <a href="#crb10" class="ref"></a> untuk kasus umum, serta <a href="#sam4" class="ref"></a> dan <a href="#sam5" class="ref"></a> ketika @@M2@@ merupakan sampel acak dari distribusi @@M3@@. Jika penduga tak bias bagi @@M4@@ mencapai batas yang berlaku untuk setiap nilai parameter, penduga itu merupakan UMVUE.</p>',
    225: '<h3 id="exa">Contoh dan Kasus Khusus</h3>',
    227: '<p>Kita akan menerapkan hasil di atas pada beberapa keluarga distribusi parametrik. Mula-mula, ingat kembali notasi baku berikut. Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi variabel acak bernilai riil @@M3@@ dengan rata-rata @@M4@@ dan varians @@M5@@. <a href="../sample/Mean.html">Rata-rata sampel</a> adalah',
    229: 'Ingat bahwa @@M1@@ dan @@M2@@. Varians sampel khusus ketika @@M3@@ diketahui dan varians sampel baku masing-masing adalah',
    235: '<h4 id="ber">Distribusi Bernoulli</h4>',
    237: '<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../bernoulli/Introduction.html">distribusi Bernoulli</a> dengan parameter keberhasilan tak diketahui @@M3@@. Dalam bahasa keandalan yang lazim, @@M4@@ berarti berhasil pada percobaan ke-@@M5@@ dan @@M6@@ berarti gagal pada percobaan ke-@@M7@@; distribusi ini dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Bernoulli.html\')" class="ancillary">Jacob Bernoulli</a>. Ingat bahwa fungsi kepadatan probabilitas Bernoulli adalah',
    239: 'Asumsi <a href="#crb3" class="ref"></a> terpenuhi. Ingat pula bahwa rata-rata distribusi Bernoulli adalah @@M1@@, sedangkan variansnya @@M2@@.</p>',
    242: '\t<p class="math">@@M1@@ merupakan batas bawah Cram&eacute;r-Rao <a href="#sam5" class="ref"></a> bagi varians penduga tak bias untuk @@M2@@.</p>',
    246: '\t<p class="math">Rata-rata sampel @@M1@@ (yaitu proporsi keberhasilan) mencapai batas dalam <a href="#ber1" class="ref"></a>, sehingga merupakan UMVUE bagi @@M2@@.</p>',
    249: '<h4 id="poi">Distribusi Poisson</h4>',
    251: '<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../poisson/Poisson.html">distribusi Poisson</a> dengan parameter @@M3@@. Distribusi ini sering dipakai untuk memodelkan banyaknya <q>titik acak</q> dalam suatu wilayah waktu atau ruang, khususnya dalam konteks <a href="../poisson/index.html">proses Poisson</a>. Distribusi Poisson dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Poisson.html\')" class="ancillary">Simeon Poisson</a> dan mempunyai fungsi kepadatan probabilitas',
    253: 'Asumsi <a href="#crb3" class="ref"></a> terpenuhi. Ingat pula bahwa rata-rata dan varians distribusi tersebut sama-sama @@M1@@.</p>',
    256: '\t<p class="math">@@M1@@ merupakan batas bawah Cram&eacute;r-Rao <a href="#sam5" class="ref"></a> bagi varians penduga tak bias untuk @@M2@@.</p>',
    260: '\t<p class="math">Rata-rata sampel @@M1@@ mencapai batas dalam <a href="#poi1" class="ref"></a>, sehingga merupakan UMVUE bagi @@M2@@.</p>',
    263: '<h4 id="nor">Distribusi Normal</h4>',
    265: '<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../special/Normal.html">distribusi normal</a> dengan rata-rata @@M3@@ dan varians @@M4@@. Distribusi normal sangat penting dalam statistika, antara lain karena <a href="../sample/CLT.html">teorema limit pusat</a>. Distribusi ini banyak dipakai untuk memodelkan besaran fisik yang dipengaruhi banyak galat acak kecil dan mempunyai fungsi kepadatan probabilitas',
    268: '<p>Asumsi <a href="#crb3" class="ref"></a> terpenuhi untuk kedua parameter. Pendugaan rata-rata dan varians secara bersama memakai matriks informasi Fisher; pada model normal, informasi silang keduanya nol sehingga unsur diagonal invers matriks menghasilkan batas skalar yang sama seperti yang ditampilkan di bawah. Ingat pula bahwa momen pusat keempat adalah @@M1@@.</p>',
    271: '\t<p class="math">@@M1@@ merupakan batas bawah Cram&eacute;r-Rao <a href="#sam5" class="ref"></a> bagi varians penduga tak bias untuk @@M2@@.</p>',
    275: '\t<p class="math">Rata-rata sampel @@M1@@ mencapai batas dalam <a href="#nor1" class="ref"></a>, sehingga merupakan UMVUE bagi @@M2@@.</p>',
    279: '\t<p class="math">@@M1@@ merupakan batas bawah Cram&eacute;r-Rao <a href="#sam5" class="ref"></a> bagi varians penduga tak bias untuk @@M2@@.</p>',
    283: '\t<p class="math"><a href="../sample/Variance.html">Varians sampel</a> @@M1@@ mempunyai varians @@M2@@, sehingga tidak mencapai batas dalam <a href="#nor3" class="ref"></a>.</p>',
    287: '\t<p class="math">Jika @@M1@@ diketahui, varians sampel khusus @@M2@@ mencapai batas dalam <a href="#nor3" class="ref"></a>, sehingga merupakan UMVUE bagi @@M3@@.</p>',
    291: '\t<p class="math">Jika @@M1@@ tidak diketahui, tidak ada penduga tak bias bagi @@M2@@ yang mencapai batas bawah Cram&eacute;r-Rao dalam <a href="#nor3" class="ref"></a>.</p>',
    293: '\t\t<summary>Rincian:</summary>',
    294: '\t\t<p>Hasil ini mengikuti syarat kesamaan dalam ketaksamaan Cram&eacute;r-Rao pada <a href="#crb8" class="ref"></a>.</p>',
    298: '<h4 id="gam">Distribusi Gamma</h4>',
    300: '<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../special/Gamma.html">distribusi gamma</a> dengan parameter bentuk diketahui @@M3@@ dan parameter skala tak diketahui @@M4@@. Distribusi gamma sering dipakai untuk memodelkan waktu acak dan jenis variabel acak positif tertentu lainnya. Fungsi kepadatan probabilitasnya adalah',
    302: 'Asumsi dalam <a href="#crb3" class="ref"></a> terpenuhi terhadap @@M1@@. Selain itu, rata-rata dan varians distribusi gamma masing-masing adalah @@M2@@ dan @@M3@@.</p>',
    305: '\t<p class="math">@@M1@@ merupakan batas bawah Cram&eacute;r-Rao <a href="#sam5" class="ref"></a> bagi varians penduga tak bias untuk @@M2@@.</p>',
    309: '<p class="math">@@M1@@ mencapai batas dalam <a href="#gam1" class="ref"></a>, sehingga merupakan UMVUE bagi @@M2@@.</p>',
    312: '<h4 id="bet">Distribusi Beta</h4>',
    314: '<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../special/Beta.html">distribusi beta</a> dengan parameter kiri @@M3@@ dan parameter kanan @@M4@@. Distribusi beta banyak dipakai untuk memodelkan proporsi acak dan variabel acak lain yang nilainya berada dalam interval terbatas. Dalam kasus khusus ini, fungsi kepadatan probabilitas satu pengamatan dari distribusi asal sampel adalah',
    316: 'Asumsi <a href="#crb3" class="ref"></a> terpenuhi terhadap @@M1@@.</p>',
    319: '\t<p class="math">Rata-rata dan varians distribusi tersebut adalah</p>',
    327: '\t<p class="math">Batas bawah Cram&eacute;r-Rao <a href="#sam5" class="ref"></a> bagi varians penduga tak bias untuk @@M1@@ adalah @@M2@@.</p>',
    331: '\t<p class="math">Rata-rata sampel @@M1@@ tidak mencapai batas bawah Cram&eacute;r-Rao dalam <a href="#bet2" class="ref"></a>. Untuk ukuran sampel satu, penduga tersebut sama dengan pengamatan tunggal dan merupakan UMVUE bagi @@M2@@. Untuk ukuran sampel sekurang-kurangnya dua, penduga itu bukan UMVUE: negatif jumlah logaritma pengamatan merupakan statistik cukup dan lengkap, dan pengondisian rata-rata sampel pada statistik itu menurut Rao–Blackwell menurunkan varians secara ketat.</p>',
    334: '<h4 id="uni">Distribusi Seragam</h4>',
    336: '<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../special/UniformContinuous.html">distribusi seragam</a> pada @@M3@@, dengan @@M4@@ sebagai parameter tak diketahui. Jadi, fungsi kepadatan probabilitas satu pengamatan dari distribusi asal sampel adalah',
    340: '\t<p class="math">Asumsi <a href="#crb3" class="ref"></a> <em>tidak</em> terpenuhi.</p>',
    344: '\t<p class="math">Substitusi formal ke ungkapan berbasis skor dalam <a href="#sam5" class="ref"></a> bagi penduga tak bias untuk @@M1@@ menghasilkan @@M2@@. Substitusi formal ke bentuk berbasis turunan kedua menghasilkan negatif dari nilai tersebut. Namun, kedua nilai itu bukan batas bawah Cram&eacute;r-Rao yang sah karena teoremanya tidak berlaku, sebagaimana dinyatakan dalam <a href="#uni1" class="ref"></a>.</p>',
    348: '\t<p class="math">Dari bagian tentang <a href="Likelihood.html#uni">penduga kemungkinan maksimum</a>, ingat bahwa @@M1@@ tak bias dan mempunyai varians @@M2@@. Varians ini lebih kecil daripada nilai formal dalam <a href="#uni2" class="ref"></a>; hal itu menegaskan kegagalan syarat regularitas, bukan pelanggaran suatu batas bawah yang sah.</p>',
    351: '<p>Asumsi <a href="#crb3" class="ref"></a> gagal karena himpunan dukungan @@M1@@ bergantung pada parameter @@M2@@.</p>',
    353: '<h3 id="blu">Penduga Linear Tak Bias Terbaik</h3>',
    355: '<p>Sekarang kita meninjau masalah yang agak khusus, tetapi tetap sesuai dengan tema umum bagian ini. Andaikan @@M1@@ merupakan barisan variabel acak teramati bernilai riil yang saling tak berkorelasi dan mempunyai rata-rata tak diketahui yang sama, @@M2@@, tetapi simpangan bakunya dapat berbeda. Misalkan @@M3@@, dengan @@M4@@ untuk @@M5@@. Jika salah satu simpangan baku nol, variabel hasil yang bersesuaian sama dengan rata-rata itu hampir pasti dan sudah menjadi penduga tepat; bobot invers-varians di bawah tidak terdefinisi. Karena itu, rumus berikut mengasumsikan semua simpangan baku positif.</p>',
    357: '<p>Kita meninjau penduga bagi @@M1@@ yang merupakan fungsi linear dari variabel hasil. Secara khusus, penduganya berbentuk berikut, dengan vektor koefisien @@M2@@ yang harus ditentukan:',
    361: '\t<p class="math">@@M1@@ tak bias tepat ketika @@M2@@.</p>',
    365: '\t<p class="math">Varians @@M1@@ adalah',
    370: '\t<p class="math">Dengan kendala tak bias, varians diminimumkan ketika',
    373: '\t\t<summary>Rincian:</summary>',
    374: '\t\t<p>Gunakan metode pengali Lagrange (dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Lagrange.html\')" class="ancillary">Joseph-Louis Lagrange</a>).</p>',
    378: '<p>Latihan <a href="#blu3" class="ref"></a> menunjukkan cara membentuk <dfn>Penduga Linear Tak Bias Terbaik</dfn> (<dfn>BLUE</dfn>) bagi @@M1@@ jika vektor simpangan baku positif @@M2@@ diketahui.</p>',
    380: '<p>Andaikan sekarang @@M1@@ untuk @@M2@@, sehingga semua variabel hasil mempunyai simpangan baku yang sama. Hal ini khususnya berlaku jika variabel hasil membentuk sampel acak berukuran @@M3@@ dari distribusi dengan rata-rata @@M4@@ dan simpangan baku @@M5@@.</p>',
    383: '\t<p class="math">Dalam kasus ini, varians diminimumkan ketika @@M1@@ untuk setiap @@M2@@, sehingga @@M3@@, yaitu rata-rata sampel.</p>',
    386: '<p>Latihan <a href="#blu4" class="ref"></a> menunjukkan bahwa rata-rata sampel @@M1@@ merupakan penduga linear tak bias terbaik bagi @@M2@@ ketika semua simpangan baku sama; selain itu, nilai simpangan baku tersebut tidak perlu diketahui.</p>',
    391: '\t\t<li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>',
    392: '\t\t<li class="child"><a href="Estimators.html" title="Penduga">1</a></li>',
    393: '\t\t<li class="child"><a href="Moments.html" title="Metode Momen">2</a></li>',
    394: '\t\t<li class="child"><a href="Likelihood.html" title="Kemungkinan Maksimum">3</a></li>',
    395: '\t\t<li class="child"><a href="Bayes.html" title="Penduga Bayes">4</a></li>',
    397: '\t\t<li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancillary">6</a></li>',
    398: '\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>',
    399: '\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>',
    402: '\t\t<li class="sister"><a href="JavaScript:openAncillary(\'../apps/index.html\')" class="ancillary">Aplikasi</a></li>',
    403: '\t\t<li class="sister"><a href="JavaScript:openAncillary(\'../data/index.html\')" class="ancillary">Himpunan Data</a></li>',
    404: '\t\t<li class="child"><a href="JavaScript:openAncillary(\'../biographies/index.html\')" class="ancillary">Biografi</a></li>',
}


# Exact, bounded repairs to the frozen authority. These include formula defects
# and incorrect cross-references; no other source mathematics is changed.
BOUNDED_FIXES: dict[int, tuple[tuple[str, str], ...]] = {
    92: ((
        r"\E\left[h(\bs{X})\right]",
        r"\E_\theta\left[h(\bs{X})\right]",
    ),),
    96: ((
        r"\int_S \frac{d}{d \theta} h(\bs{x}) f_\theta(\bs{x}) \, d \bs{x}",
        r"\int_S \frac{d}{d \theta}\left[h(\bs{x}) f_\theta(\bs{x})\right] \, d \bs{x}",
    ),),
    164: (
        (r"\E_\theta\left[L^2(\bs{X}, \theta)\right]", r"\E_\theta\left[L_1^2(\bs{X}, \theta)\right]"),
        ('href="#crb8"', 'href="#crb6"'),
    ),
    195: ((r"\(L^2\)", r"\(L_1^2\)"),),
    197: ((
        r"\E_\theta\left[L^2(\bs{X}, \theta)\right]",
        r"\E_\theta\left[L_1^2(\bs{X}, \theta)\right]",
    ),),
    239: (('href="#crb3"', 'href="#crb2"'),),
    253: (('href="#crb3"', 'href="#crb2"'),),
    266: ((
        r"\exp\left[-\left[\frac{x - \mu}{\sigma}\right]^2 \right]",
        r"\exp\left[-\frac{1}{2}\left[\frac{x - \mu}{\sigma}\right]^2 \right]",
    ),),
    268: (('href="#crb3"', 'href="#crb2"'),),
    302: (('href="#crb3"', 'href="#crb2"'),),
    316: (('href="#crb3"', 'href="#crb2"'),),
    340: (('href="#crb3"', 'href="#crb2"'),),
    344: (('href="#sam5"', 'href="#sam4"'),),
    351: (('href="#crb3"', 'href="#crb2"'),),
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/point/index.html": "index.html",
    "https://www.randomservices.org/random/point/Estimators.html": "Estimators.html",
    "https://www.randomservices.org/random/point/Moments.html": "Moments.html",
    "https://www.randomservices.org/random/point/Likelihood.html": "Likelihood.html",
    "https://www.randomservices.org/random/point/Bayes.html": "Bayes.html",
    "https://www.randomservices.org/random/point/Unbiased.html": "Unbiased.html",
    "https://www.randomservices.org/random/sample/index.html": "../sample/index.html",
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/sample/Mean.html": "../sample/Mean.html",
    "https://www.randomservices.org/random/sample/LLN.html": "../sample/LLN.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
    "https://www.randomservices.org/random/sample/OrderStatistics.html": "../sample/OrderStatistics.html",
    "https://www.randomservices.org/random/sample/Covariance.html": "../sample/Covariance.html",
    "https://www.randomservices.org/random/sample/Normal.html": "../sample/Normal.html",
}


EDITION_NOTICE = """
    <section class="edition-notice" data-o006-edition-notice="v1">
        <p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, serta koreksi terbatas terhadap kekeliruan matematis dan data yang dicatat dalam daftar koreksi edisi.</p>
        <p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
    </section>"""


def render_template(line_number: int, source_line: str, template: str) -> str:
    spans = MATH_RE.findall(source_line)
    tokens = [int(value) for value in TOKEN_RE.findall(template)]
    if tokens != list(range(1, len(spans) + 1)):
        raise RuntimeError(
            f"line {line_number}: placeholders {tokens} do not match {len(spans)} TeX spans"
        )
    rendered = template
    for index, span in enumerate(spans, start=1):
        rendered = rendered.replace(f"@@M{index}@@", span, 1)
    return rendered


def apply_bounded_fixes(line_number: int, text: str) -> str:
    for old, new in BOUNDED_FIXES.get(line_number, ()):
        if text.count(old) != 1:
            raise RuntimeError(
                f"line {line_number}: expected one exact defect, found {text.count(old)}"
            )
        text = text.replace(old, new, 1)
    return text


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


def assert_topology(source_text: str, target_text: str) -> None:
    for pattern in (
        r'<div class="unit" id="[^"]+">',
        r"<details>",
        r"<summary>",
        r'<ol class="sub">',
        r'<h3 id="[^"]+">',
        r'<h4 id="[^"]+">',
    ):
        source_count = len(re.findall(pattern, source_text))
        target_count = len(re.findall(pattern, target_text))
        if target_count != source_count:
            raise RuntimeError(
                f"topology mismatch for {pattern!r}: source {source_count}, target {target_count}"
            )
    source_ids = set(re.findall(r'\bid="([^"]+)"', source_text))
    target_ids = set(re.findall(r'\bid="([^"]+)"', target_text))
    expected_ids = source_ids | {"o006.random.point.unbiased.page"}
    if target_ids != expected_ids:
        raise RuntimeError(
            f"native-ID mismatch: missing {sorted(expected_ids - target_ids)}, "
            f"extra {sorted(target_ids - expected_ids)}"
        )


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    if len(source_bytes) != EXPECTED_SOURCE_BYTES:
        raise RuntimeError(f"authority byte-count mismatch: {len(source_bytes)}")
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    lines = source_bytes.decode("utf-8").splitlines(keepends=True)
    if len(lines) != EXPECTED_SOURCE_LINES:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")
    for line_number, template in sorted(T.items()):
        source = lines[line_number - 1]
        ending = "\r\n" if source.endswith("\r\n") else "\n" if source.endswith("\n") else ""
        lines[line_number - 1] = render_template(
            line_number, source.removesuffix(ending), template
        ) + ending
    for line_number in sorted(BOUNDED_FIXES):
        source = lines[line_number - 1]
        ending = "\r\n" if source.endswith("\r\n") else "\n" if source.endswith("\n") else ""
        lines[line_number - 1] = apply_bounded_fixes(
            line_number, source.removesuffix(ending)
        ) + ending
    text = "".join(lines)
    text = re.sub(
        r'href="([^"]+)"',
        lambda match: f'href="{convert_href(match.group(1))}"',
        text,
    )
    marker = "\n</footer>"
    if text.count(marker) != 1:
        raise RuntimeError("footer insertion point is not unique")
    text = text.replace(marker, EDITION_NOTICE + marker, 1)

    source_text = source_bytes.decode("utf-8")
    expected_math_text = source_text
    for line_number in sorted(BOUNDED_FIXES):
        source_line = expected_math_text.splitlines(keepends=True)[line_number - 1]
        ending = "\r\n" if source_line.endswith("\r\n") else "\n" if source_line.endswith("\n") else ""
        repaired = apply_bounded_fixes(line_number, source_line.removesuffix(ending)) + ending
        expected_lines = expected_math_text.splitlines(keepends=True)
        expected_lines[line_number - 1] = repaired
        expected_math_text = "".join(expected_lines)
    if MATH_RE.findall(text) != MATH_RE.findall(expected_math_text):
        raise RuntimeError("delimited TeX inventory differs from the bounded repaired authority")
    output_lines = text.splitlines()
    for line_number, repairs in BOUNDED_FIXES.items():
        output_line = output_lines[line_number - 1]
        for old, new in repairs:
            if old in output_line or output_line.count(new) != 1:
                raise RuntimeError(
                    f"line {line_number}: bounded repair not unique: {old!r} -> {new!r}"
                )
    assert_topology(source_text, text)

    required_links = (
        'href="index.html"', 'href="Estimators.html"', 'href="Moments.html"',
        'href="Likelihood.html"', 'href="Bayes.html"',
        'href="https://www.randomservices.org/random/point/Sufficient.html"',
        'href="../sample/Introduction.html"', 'href="../sample/Mean.html"',
        'href="../sample/CLT.html"', 'href="../sample/Variance.html"',
    )
    for link in required_links:
        if link not in text:
            raise RuntimeError(f"required navigation target missing: {link}")
    if 'href="Sufficient.html"' in text:
        raise RuntimeError("future Sufficient page was incorrectly routed locally")
    for phrase in (
        '<html lang="en">', "JavaScript:openAncillary", "Expand Details",
        "Contract Details", ">Details:<", ">Point Estimation<",
        ">Best Unbiased Estimators<", ">Basic Theory<", ">Definitions<",
        ">The Cram&eacute;r-Rao Lower Bound<", ">Random Samples<",
        ">Examples and Special Cases<", ">The Bernoulli Distribution<",
        ">The Poisson Distribution<", ">The Normal Distribution<",
        ">The Gamma Distribution<", ">The Beta Distribution<",
        ">The Uniform Distribution<", ">Best Linear Unbiased Estimators<",
        ">Apps<", ">Data Sets<", "> Biographies<", "unbiased esimtator",
        "anaylsis", "ubiased estimator", "appropriate interchanges are permissible)",
        "statistik ancilar", "fungsi densitas probabilitas", ">Estimators<",
        ">The Method of Moments<", ">Maximum Likelihood<", "Bayes' Estimators",
    ):
        if phrase in text:
            raise RuntimeError(f"untranslated or unsafe phrase remains: {phrase}")
    controls = [
        char for char in text
        if ord(char) < 32 and char not in "\t\r\n"
    ]
    if controls:
        raise RuntimeError(f"forbidden control characters: {sorted(map(ord, controls))}")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(text.encode("utf-8"))
    output = TARGET.read_bytes()
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: "
        f"{len(output)} bytes / sha256 {hashlib.sha256(output).hexdigest()}"
    )


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
