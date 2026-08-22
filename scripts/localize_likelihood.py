#!/usr/bin/env python3
"""Create the bounded id-ID Maximum Likelihood target.

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
SOURCE = ROOT / "authority" / "upstream" / "random" / "point" / "Likelihood.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "point" / "Likelihood.html"
SOURCE_URL = "https://www.randomservices.org/random/point/Likelihood.html"
SOURCE_SHA256 = "f8c94e3de84f7a025fd32395169938f37e7fd7958d5a8be9d56b54ed307d6ffd"
EXPECTED_SOURCE_LINES = 600
MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)
TOKEN_RE = re.compile(r"@@M([1-9][0-9]*)@@")

# Only reader-facing rows are replaced. Formula-only rows remain exact source
# bytes unless listed in MATH_FIXES.
T: dict[int, str] = {
    2: '<html lang="id-ID">',
    6: "    <title>Kemungkinan Maksimum</title>",
    9: '    <meta name="keywords" content="probabilitas, statistika, pendugaan titik, kemungkinan maksimum, fungsi kemungkinan, fungsi log-kemungkinan, distribusi Bernoulli, distribusi geometrik, distribusi binomial negatif, distribusi Poisson, distribusi normal, distribusi gamma, distribusi beta, distribusi Pareto, distribusi seragam, distribusi hipergeometrik">',
    36: '        <li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>',
    37: '        <li class="child"><a href="Estimators.html" title="Penduga">1</a></li>',
    38: '        <li class="child"><a href="Moments.html" title="Metode Momen">2</a></li>',
    40: '        <li class="child"><a href="Bayes.html" title="Penduga Bayes">4</a></li>',
    41: '        <li class="child"><a href="Unbiased.html" title="Penduga Tak Bias Terbaik">5</a></li>',
    42: '        <li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancilar">6</a></li>',
    43: '        <li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>',
    44: '        <li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>',
    46: '    <h2 id="o006.random.point.likelihood.page">3. Kemungkinan Maksimum</h2>',
    49: '<h3 id="the">Teori Dasar</h3>',
    51: '<h4 id="mle">Metode</h4>',
    53: '<p>Andaikan kembali bahwa kita mempunyai <a href="../prob/Probability.html">variabel acak</a> teramati @@M1@@ untuk suatu <a href="../prob/Experiments.html">eksperimen acak</a>, dengan nilai dalam himpunan @@M2@@. Andaikan pula bahwa distribusi @@M3@@ bergantung pada parameter tak diketahui @@M4@@, yang nilainya berada dalam himpunan parameter @@M5@@. Tentu saja, variabel data @@M6@@ hampir selalu bernilai vektor. Parameter @@M7@@ juga dapat bernilai vektor. Fungsi kepadatan probabilitas @@M8@@ pada @@M9@@ akan kita nyatakan dengan @@M10@@ untuk @@M11@@. Distribusi @@M12@@ dapat berupa <a href="../dist/Discrete.html">diskret</a> ataupun <a href="../dist/Continuous.html">kontinu</a>.</p>',
    55: '<p>Fungsi kemungkinan diperoleh dengan mempertukarkan peran @@M1@@ dan @@M2@@ dalam fungsi kepadatan probabilitas: kita memandang @@M3@@ sebagai peubah dan @@M4@@ sebagai informasi yang diberikan, tepat seperti sudut pandang dalam pendugaan.</p>',
    58: '    <p class="dfn"><dfn>Fungsi kemungkinan (likelihood)</dfn> pada @@M1@@ adalah fungsi @@M2@@ yang diberikan oleh',
    62: '<p>Dalam metode <dfn>kemungkinan maksimum</dfn>, untuk setiap nilai vektor data kita mencari nilai parameter yang memaksimumkan fungsi kemungkinan.</p>',
    65: '    <p class="dfn">Andaikan nilai maksimum @@M1@@ dicapai di @@M2@@ untuk setiap @@M3@@. Maka statistik @@M4@@ merupakan <dfn>penduga kemungkinan maksimum</dfn> bagi @@M5@@.</p>',
    68: '<p>Metode kemungkinan maksimum menarik secara intuitif: kita memilih nilai parameter yang memberikan nilai fungsi kemungkinan terbesar pada data yang benar-benar teramati.</p>',
    70: '<p>Karena fungsi logaritma natural naik secara ketat pada @@M1@@, nilai maksimum fungsi kemungkinan, jika ada, dicapai pada titik yang sama dengan nilai maksimum logaritma fungsi kemungkinan. Untuk nilai fungsi kemungkinan yang nol, kita menggunakan konvensi nilai diperluas bahwa logaritmanya adalah minus tak hingga.</p>',
    73: '    <p class="dfn"><dfn>Fungsi log-kemungkinan</dfn> pada @@M1@@ adalah fungsi @@M2@@:',
    75: '    Jika nilai maksimum @@M1@@ dicapai di @@M2@@ untuk setiap @@M3@@, maka statistik @@M4@@ merupakan penduga kemungkinan maksimum bagi @@M5@@.</p>',
    78: '<p>Fungsi log-kemungkinan sering lebih mudah digunakan daripada fungsi kemungkinan, biasanya karena fungsi kepadatan probabilitas @@M1@@ mempunyai struktur hasil kali.</p>',
    80: '<h4 id="vec">Vektor Parameter</h4>',
    82: '<p>Kasus khusus yang penting terjadi ketika @@M1@@ merupakan vektor berisi @@M2@@ parameter riil, sehingga @@M3@@. Dalam hal ini, masalah kemungkinan maksimum adalah memaksimumkan fungsi beberapa peubah. Jika ruang parameter @@M4@@ mempunyai interior tak kosong, metode kalkulus dapat digunakan. Jika nilai maksimum @@M5@@ dicapai di titik @@M6@@ pada bagian dalam @@M7@@, maka @@M8@@ mempunyai maksimum lokal di @@M9@@. Jadi, apabila fungsi kemungkinan terdiferensialkan, persamaan berikut menghasilkan calon titik interior:',
    84: 'atau, secara ekuivalen,',
    86: 'Namun, setiap titik stasioner masih harus dibandingkan dan diperiksa sebagai maksimum; nilai maksimum juga dapat dicapai pada batas @@M1@@ atau bahkan tidak ada.</p>',
    88: '<h4 id="sam">Sampel Acak</h4>',
    90: '<p>Kasus khusus terpenting terjadi ketika variabel data membentuk <a href="../sample/index.html">sampel acak</a> dari suatu distribusi.</p>',
    93: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi variabel acak @@M3@@ yang bernilai dalam suatu himpunan @@M4@@, dengan fungsi kepadatan probabilitas @@M5@@ untuk @@M6@@. Maka @@M7@@ bernilai dalam @@M8@@, dan fungsi kemungkinan serta log-kemungkinan untuk @@M9@@ adalah',
    100: '<h4 id="inv">Perluasan Metode dan Sifat Invariansi</h4>',
    102: '<p>Kembali ke kerangka umum, andaikan sekarang @@M1@@ merupakan fungsi satu-satu dari himpunan parameter @@M2@@ ke seluruh himpunan @@M3@@. Kita dapat memandang @@M4@@ sebagai parameter baru bernilai dalam @@M5@@ dan dengan mudah memparameterkan ulang fungsi kepadatan probabilitas. Jadi, tetapkan @@M6@@ untuk @@M7@@ dan @@M8@@. Fungsi kemungkinan yang bersesuaian untuk @@M9@@ adalah',
    104: 'Jelas bahwa jika @@M1@@ memaksimumkan @@M2@@ untuk @@M3@@, maka @@M4@@ memaksimumkan @@M5@@ untuk @@M6@@. Jadi, jika @@M7@@ adalah penduga kemungkinan maksimum bagi @@M8@@, maka @@M9@@ adalah penduga kemungkinan maksimum bagi @@M10@@.</p>',
    106: '<p>Jika fungsi @@M1@@ tidak satu-satu, fungsi kemungkinan biasa untuk parameter baru @@M2@@ tidak terdefinisi melalui parameterisasi ulang tunggal, karena kepadatan umumnya tidak ditentukan sepenuhnya oleh @@M3@@. Namun, metode tersebut mempunyai perluasan alami melalui kemungkinan profil.</p>',
    109: '    <p class="dfn">Andaikan @@M1@@, dengan himpunan target sama dengan citra fungsi tersebut, dan nyatakan parameter baru dengan @@M2@@. Definisikan <dfn>fungsi kemungkinan profil</dfn> bagi @@M3@@ pada @@M4@@ dengan',
    111: '    Jika @@M1@@ memaksimumkan @@M2@@ untuk setiap @@M3@@, maka @@M4@@ merupakan <dfn>penduga kemungkinan maksimum</dfn> bagi @@M5@@.</p>',
    114: '<p>Definisi ini memperluas metode kemungkinan maksimum ke kasus ketika parameter kepentingan tidak sepenuhnya memparameterkan fungsi kepadatan probabilitas. Teorema berikut dikenal sebagai <dfn>sifat invariansi</dfn>: jika masalah kemungkinan maksimum bagi @@M1@@ dapat diselesaikan, masalah bagi @@M2@@ juga dapat diselesaikan.</p>',
    117: '    <p class="math">Dalam kerangka definisi <a href="#inv1" class="ref"></a>, jika @@M1@@ merupakan penduga kemungkinan maksimum bagi @@M2@@, maka @@M3@@ merupakan penduga kemungkinan maksimum bagi @@M4@@.</p>',
    119: '        <summary>Rincian:</summary>',
    120: '        <p>Seperti sebelumnya, jika @@M1@@ memaksimumkan @@M2@@ untuk @@M3@@, maka @@M4@@ memaksimumkan @@M5@@ untuk @@M6@@.</p>',
    124: '<h3 id="exe">Contoh dan Kasus Khusus</h3>',
    126: '<p>Dalam subbagian berikut kita mempelajari pendugaan kemungkinan maksimum untuk sejumlah keluarga distribusi parametrik khusus. Ingat bahwa jika @@M1@@ merupakan sampel acak dari distribusi dengan rata-rata @@M2@@ dan varians @@M3@@, maka penduga <a href="Moments.html">metode momen</a> bagi @@M4@@ dan @@M5@@ masing-masing adalah',
    131: 'Tentu saja, @@M1@@ adalah <a href="../sample/Mean.html">rata-rata sampel</a>, sedangkan @@M2@@ adalah versi berbias dari <a href="../sample/Variance.html">varians sampel</a>. Statistik-statistik tersebut terkadang juga muncul sebagai penduga kemungkinan maksimum. Statistik lain yang akan muncul dalam beberapa contoh di bawah adalah',
    133: 'momen sampel kedua terhadap titik asal. Seperti biasa, usahakan menurunkan sendiri hasilnya sebelum membuka rincian.</p>',
    135: '<h4 id="ber">Distribusi Bernoulli</h4>',
    137: '<p>Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari <a href="../bernoulli/Introduction.html">distribusi Bernoulli</a> dengan parameter keberhasilan @@M3@@. Ingat bahwa fungsi kepadatan probabilitas Bernoulli adalah',
    139: 'Jadi, @@M1@@ merupakan barisan variabel indikator saling bebas dengan @@M2@@ untuk setiap @@M3@@. Dalam istilah keandalan yang lazim, @@M4@@ adalah hasil percobaan ke-@@M5@@, dengan 1 berarti berhasil dan 0 berarti gagal. Misalkan @@M6@@ menyatakan banyaknya keberhasilan, sehingga proporsi keberhasilan—rata-rata sampel—adalah @@M7@@. Ingat bahwa @@M8@@ mempunyai <a href="../bernoulli/Binomial.html">distribusi binomial</a> dengan parameter @@M9@@ dan @@M10@@.</p>',
    142: '    <p class="math">Rata-rata sampel @@M1@@ merupakan penduga kemungkinan maksimum bagi @@M2@@ pada himpunan parameter @@M3@@.</p>',
    144: '        <summary>Rincian:</summary>',
    145: '        <p>Perhatikan bahwa @@M1@@ untuk @@M2@@. Jadi, untuk titik interior, fungsi log-kemungkinan pada @@M3@@ adalah',
    147: '        Mendiferensialkan terhadap @@M1@@ dan menyederhanakannya menghasilkan',
    149: '        dengan @@M1@@. Jika jumlah keberhasilan berada secara ketat antara nol dan ukuran sampel, terdapat satu titik kritis interior pada @@M2@@. Turunan keduanya adalah',
    151: '        Jadi fungsi log-kemungkinan cekung ketat pada bagian interior. Jika tidak ada keberhasilan, kemungkinan dimaksimumkan di batas p = 0; jika semua percobaan berhasil, kemungkinan dimaksimumkan di batas p = 1. Dengan demikian, dalam semua kasus maksimum pada himpunan parameter tertutup dicapai di @@M1@@.</p>',
    155: '<p>Ingat bahwa @@M1@@ juga merupakan penduga <a href="Moments.html">metode momen</a> bagi @@M2@@. Selalu menyenangkan ketika dua prosedur pendugaan yang berbeda memberikan hasil yang sama. Selanjutnya kita tinjau masalah yang sama dengan himpunan parameter yang jauh lebih terbatas.</p>',
    158: '    <p class="math">Andaikan sekarang @@M1@@ bernilai dalam @@M2@@. Penduga kemungkinan maksimum bagi @@M3@@ adalah statistik',
    162: '        <li>@@M1@@ berbias positif dalam arti lemah—biasnya taknegatif—tetapi tak bias secara asimtotik.</li>',
    164: '        <li>@@M1@@ konsisten.</li>',
    167: '        <summary>Rincian:</summary>',
    168: '        <p>Perhatikan bahwa fungsi kemungkinan pada @@M1@@ adalah @@M2@@ untuk @@M3@@, dengan @@M4@@ seperti biasa. Jadi @@M5@@. Di sisi lain, @@M6@@ jika @@M7@@, sedangkan @@M8@@ jika @@M9@@. Dengan demikian, jika @@M10@@ maksimum dicapai pada @@M11@@, sedangkan jika @@M12@@ maksimum dicapai pada @@M13@@.</p>',
    170: '            <li>Jika @@M1@@, maka @@M2@@ sehingga @@M3@@. Jika @@M4@@,',
    173: '            <li>Perhatikan bahwa @@M1@@ dan @@M2@@ ketika @@M3@@, baik untuk @@M4@@ maupun @@M5@@.</li>',
    174: '            <li>Jika @@M1@@, maka @@M2@@ dengan probabilitas 1 sehingga @@M3@@. Jika @@M4@@,',
    177: '            <li>Dari bagian (c), @@M1@@ ketika @@M2@@.</li>',
    182: '<p>Distribusi Bernoulli pada <a href="#ber2" class="ref"></a> memodelkan koin yang adil atau mempunyai gambar pada kedua sisi. Hasil <a href="#ber1" class="ref"></a> dan <a href="#ber2" class="ref"></a> menunjukkan bahwa penduga kemungkinan maksimum suatu parameter, seperti penyelesaian setiap masalah pemaksimuman, sangat bergantung pada domain.</p>',
    185: '    <p class="math">@@M1@@ secara seragam lebih baik daripada @@M2@@ pada himpunan parameter @@M3@@.</p>',
    187: '        <summary>Rincian:</summary>',
    188: '        <p>Ingat bahwa @@M1@@. Jika @@M2@@, maka @@M3@@ sehingga kedua penduga memberikan jawaban yang benar. Jika @@M4@@, maka @@M5@@.</p>',
    193: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi Bernoulli dengan parameter keberhasilan tak diketahui @@M3@@. Tentukan penduga kemungkinan maksimum bagi @@M4@@, yaitu varians distribusi Bernoulli yang mendasarinya.</p>',
    195: '        <summary>Rincian:</summary>',
    196: '        <p>Berdasarkan sifat invariansi, penduganya adalah @@M1@@, dengan @@M2@@ sebagai rata-rata sampel.</p>',
    200: '<h4 id="geo">Distribusi Geometrik</h4>',
    202: '<p>Ingat bahwa <a href="../bernoulli/Geometric.html">distribusi geometrik</a> pada @@M1@@ dengan parameter keberhasilan @@M2@@ mempunyai fungsi kepadatan probabilitas',
    204: 'Distribusi geometrik mengatur nomor percobaan tempat keberhasilan pertama terjadi dalam barisan <a href="../bernoulli/index.html">percobaan Bernoulli</a>.</p>',
    207: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi geometrik dengan parameter tak diketahui @@M2@@. Jika rata-rata sampel lebih besar daripada 1, penduga kemungkinan maksimum bagi @@M3@@ adalah @@M4@@. Jika seluruh pengamatan sama dengan 1 sehingga rata-rata sampelnya 1, tidak ada penduga kemungkinan maksimum pada ruang parameter terbuka; supremum kemungkinan didekati ketika parameter menuju 1 dari kiri.</p>',
    209: '        <summary>Rincian:</summary>',
    210: '        <p>Perhatikan bahwa @@M1@@ untuk @@M2@@. Jadi fungsi log-kemungkinan yang bersesuaian dengan data @@M3@@ adalah',
    212: '        dengan @@M1@@. Maka',
    214: '        Jika rata-rata sampel lebih besar daripada 1, turunannya nol ketika @@M1@@. Selanjutnya, @@M2@@, sehingga maksimum dicapai pada titik kritis. Kasus batas ketika rata-rata sampel sama dengan 1 dijelaskan dalam pernyataan di atas.</p>',
    218: '<p>Ingat bahwa @@M1@@ juga merupakan <a href="Moments.html#geo">penduga metode momen</a> bagi @@M2@@ ketika nilainya berada dalam ruang parameter. Selalu meyakinkan ketika dua prosedur pendugaan yang berbeda menghasilkan penduga yang sama.</p>',
    220: '<h4 id="ngb">Distribusi Binomial Negatif</h4>',
}

T.update({
    222: '<p>Secara lebih umum, <a href="../bernoulli/NegativeBinomial.html">distribusi binomial negatif</a> pada @@M1@@ dengan parameter bentuk @@M2@@ dan parameter keberhasilan @@M3@@ mempunyai fungsi kepadatan probabilitas',
    224: 'Jika @@M1@@ bilangan bulat positif, distribusi ini mengatur banyaknya kegagalan sebelum keberhasilan ke-@@M2@@ dalam barisan <a href="../bernoulli/index.html">percobaan Bernoulli</a> dengan parameter keberhasilan @@M3@@. Namun, distribusi tersebut juga terdefinisi untuk setiap @@M4@@, tidak hanya untuk bilangan bulat.</p>',
    227: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi binomial negatif pada @@M3@@, dengan parameter bentuk @@M4@@ diketahui dan parameter keberhasilan @@M5@@ tidak diketahui. Jika rata-rata sampel positif, penduga kemungkinan maksimum bagi @@M6@@ adalah',
    230: '        <summary>Rincian:</summary>',
    231: '        <p>Perhatikan bahwa @@M1@@ untuk @@M2@@. Jadi fungsi log-kemungkinan yang bersesuaian dengan @@M3@@ adalah',
    233: '        dengan @@M1@@ dan @@M2@@. Maka',
    235: '        Turunannya nol ketika @@M1@@, dengan @@M2@@ seperti biasa. Selanjutnya, @@M3@@, sehingga maksimum dicapai pada titik kritis. Jika rata-rata sampel tersebut nol, rumus tersebut menghasilkan nilai batas 1 yang tidak termasuk ruang parameter terbuka; dalam kasus itu supremum kemungkinan tidak dicapai.</p>',
    239: '<p>Ketika terdefinisi dalam ruang parameter, hasil ini kembali sama dengan penduga metode momen bagi @@M1@@ ketika @@M2@@ diketahui.</p>',
    241: '<h4 id="poi">Distribusi Poisson</h4>',
    243: '<p>Ingat bahwa <a href="../poisson/Poisson.html">distribusi Poisson</a> dengan parameter @@M1@@ mempunyai fungsi kepadatan probabilitas',
    245: 'Distribusi Poisson dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Poisson.html\')" class="ancillary">Simeon Poisson</a> dan banyak digunakan untuk memodelkan banyaknya <q>titik</q> acak dalam suatu wilayah waktu atau ruang, terutama dalam konteks <a href="../poisson/index.html">proses Poisson</a>. Parameter @@M1@@ sebanding dengan ukuran wilayah tersebut.</p>',
    248: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi Poisson dengan parameter tak diketahui @@M2@@. Jika rata-rata sampel positif, penduga kemungkinan maksimum bagi @@M3@@ adalah rata-rata sampel @@M4@@. Jika semua pengamatan nol, tidak ada pemaksimum pada ruang parameter terbuka; supremum didekati ketika parameter menuju 0 dari kanan.</p>',
    250: '        <summary>Rincian:</summary>',
    251: '        <p>Perhatikan bahwa @@M1@@ untuk @@M2@@. Jadi fungsi log-kemungkinan yang bersesuaian dengan @@M3@@ adalah',
    253: '        dengan @@M1@@ dan @@M2@@. Jadi, @@M3@@. Jika jumlah nilai pengamatan positif, turunan tersebut nol ketika @@M4@@ dan turunan keduanya @@M5@@, sehingga maksimum dicapai pada titik kritis. Jika jumlah nilai pengamatan nol, fungsi kemungkinan menurun pada ruang parameter dan tidak mempunyai pemaksimum.</p>',
    257: '<p>Ingat bahwa pada distribusi Poisson, parameter @@M1@@ sekaligus merupakan rata-rata dan varians. Jadi @@M2@@ juga merupakan <a href="Moments.html">penduga metode momen</a> bagi @@M3@@. Pada <a href="Estimators.html#poi">bagian pengantar</a> kita menunjukkan bahwa @@M4@@ mempunyai galat kuadrat rata-rata yang lebih kecil daripada @@M5@@, meskipun keduanya tak bias.</p>',
    260: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi Poisson dengan parameter @@M2@@, dan misalkan @@M3@@. Jika rata-rata sampel positif, tentukan penduga kemungkinan maksimum bagi @@M4@@ dengan dua cara. Jika rata-rata sampel nol, jelaskan mengapa pada ruang parameter semula tidak ada pemaksimum dan nilai 1 hanya merupakan supremum bagi parameter turunan tersebut.</p>',
    262: '        <li>Secara langsung, dengan menentukan fungsi kemungkinan untuk parameter @@M1@@.</li>',
    263: '        <li>Dengan menggunakan hasil <a href="#poi1" class="ref"></a> dan sifat invariansi.</li>',
    266: '        <summary>Rincian:</summary>',
    267: '        <p>Untuk rata-rata sampel positif, hasilnya adalah @@M1@@, dengan @@M2@@ sebagai rata-rata sampel.</p>',
    271: '<h4 id="nor">Distribusi Normal</h4>',
    273: '<p>Ingat bahwa <a href="../special/Normal.html">distribusi normal</a> dengan rata-rata @@M1@@ dan varians @@M2@@ mempunyai fungsi kepadatan probabilitas',
    275: 'Distribusi normal sering digunakan untuk memodelkan besaran fisik yang dipengaruhi galat acak kecil.</p>',
    278: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi normal dengan rata-rata tak diketahui @@M2@@ dan varians @@M3@@. Jika varians sampel positif, penduga kemungkinan maksimum bagi @@M4@@ dan @@M5@@ masing-masing adalah @@M6@@ dan @@M7@@. Jika varians sampel nol, kemungkinan tidak terbatas ketika varians distribusi mendekati nol dan tidak ada penduga kemungkinan maksimum pada ruang parameter tersebut.</p>',
    280: '        <summary>Rincian:</summary>',
    281: '        <p>Perhatikan bahwa',
    283: '        Jadi fungsi log-kemungkinan yang bersesuaian dengan data @@M1@@ adalah',
    285: '        Pengambilan turunan parsial menghasilkan',
    290: '        Turunan parsial bernilai nol ketika @@M1@@ dan @@M2@@. Jadi, apabila varians sampel positif, satu-satunya titik kritis adalah @@M3@@. Dengan sedikit kalkulus tambahan, turunan parsial kedua pada titik kritis adalah',
    292: '        Matriks Hessian pada titik kritis tersebut definit negatif, dan bentuk log-kemungkinan menunjukkan bahwa titik itu merupakan maksimum global.</p>',
    296: '<p>Tentu saja, @@M1@@ dan @@M2@@ juga merupakan penduga metode momen masing-masing bagi @@M3@@ dan @@M4@@.</p>',
    299: '    <p class="app">Jalankan <a href="JavaScript:openAncillary(\'../apps/NormalEstimate.html\')" class="ancillary">eksperimen pendugaan normal</a> sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M1@@, rata-rata @@M2@@, dan varians @@M3@@. Untuk parameter @@M4@@, bandingkan penduga kemungkinan maksimum @@M5@@ dengan varians sampel biasa @@M6@@. Penduga mana yang tampaknya lebih baik dari segi galat kuadrat rata-rata?</p>',
    303: '    <p class="math">Andaikan kembali bahwa @@M1@@ merupakan sampel acak dari distribusi normal dengan rata-rata tak diketahui @@M2@@ dan varians tak diketahui @@M3@@. Apabila varians sampel positif, tentukan penduga kemungkinan maksimum bagi @@M4@@, yaitu momen kedua terhadap titik asal bagi distribusi yang mendasarinya.</p>',
    305: '        <summary>Rincian:</summary>',
    306: '        <p>Berdasarkan sifat invariansi, penduganya adalah @@M1@@, dengan @@M2@@ sebagai rata-rata sampel dan @@M3@@ sebagai versi berbias dari varians sampel.</p>',
    310: '<h4 id="gam">Distribusi Gamma</h4>',
    312: '<p>Ingat bahwa <a href="../special/Gamma.html">distribusi gamma</a> dengan parameter bentuk @@M1@@ dan parameter skala @@M2@@ mempunyai fungsi kepadatan probabilitas',
    314: 'Distribusi gamma sering digunakan untuk memodelkan waktu acak, terutama dalam konteks <a href="../poisson/index.html">proses Poisson</a>, serta jenis variabel acak positif tertentu lainnya.</p>',
    317: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi gamma dengan parameter bentuk @@M2@@ diketahui dan parameter skala tak diketahui @@M3@@. Penduga kemungkinan maksimum bagi @@M4@@ adalah @@M5@@.</p>',
    319: '        <summary>Rincian:</summary>',
    320: '        <p>Perhatikan bahwa untuk @@M1@@,',
    322: '        sehingga fungsi log-kemungkinan yang bersesuaian dengan data @@M1@@ adalah',
    324: '        dengan @@M1@@ dan @@M2@@. Jadi,',
    326: '        Turunannya nol ketika @@M1@@. Selanjutnya, @@M2@@. Pada titik kritis @@M3@@, turunan keduanya adalah @@M4@@ sehingga maksimum dicapai di titik kritis.</p>',
    330: '<p>Ingat bahwa @@M1@@ juga merupakan penduga metode momen bagi @@M2@@ ketika @@M3@@ diketahui. Namun, ketika @@M4@@ tidak diketahui, penduga metode momen bagi @@M5@@ adalah @@M6@@.</p>',
    333: '    <p class="app">Jalankan <a href="JavaScript:openAncillary(\'../apps/GammaEstimate.html\')" class="ancillary">eksperimen pendugaan gamma</a> sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M1@@, parameter bentuk @@M2@@, dan parameter skala @@M3@@. Dalam setiap kasus, bandingkan <a href="Moments.html">penduga metode momen</a> @@M4@@ bagi @@M5@@ ketika @@M6@@ tidak diketahui dengan penduga metode momen sekaligus kemungkinan maksimum @@M7@@ bagi @@M8@@ ketika @@M9@@ diketahui. Penduga mana yang tampaknya lebih baik dari segi galat kuadrat rata-rata?</p>',
    336: '<h4 id="bet">Distribusi Beta</h4>',
    338: '<p>Ingat bahwa <a href="../special/Beta.html">distribusi beta</a> dengan parameter kiri @@M1@@ dan parameter kanan @@M2@@ mempunyai fungsi kepadatan probabilitas',
    340: 'Distribusi beta sering digunakan untuk memodelkan proporsi acak dan variabel acak lain yang nilainya berada dalam interval terbatas.</p>',
    343: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi beta dengan parameter kiri tak diketahui @@M2@@ dan parameter kanan @@M3@@. Penduga kemungkinan maksimum bagi @@M4@@ adalah',
    346: '        <summary>Rincian:</summary>',
    347: '        <p>Perhatikan bahwa @@M1@@ untuk @@M2@@. Jadi fungsi log-kemungkinan yang bersesuaian dengan data @@M3@@ adalah',
    349: '        Karena itu, @@M1@@. Turunannya nol ketika @@M2@@. Selanjutnya, @@M3@@, sehingga maksimum dicapai pada titik kritis.</p>',
    353: '<p>Ingat bahwa ketika @@M1@@, <a href="Moments.html#bet">penduga metode momen</a> bagi @@M2@@ adalah @@M3@@. Namun, ketika @@M4@@ juga tidak diketahui, penduga metode momen bagi @@M5@@ adalah @@M6@@. Ketika @@M7@@, mana yang lebih baik: penduga metode momen atau penduga kemungkinan maksimum?</p>',
    356: '    <p class="app">Dalam <a href="JavaScript:openAncillary(\'../apps/BetaEstimate.html\')" class="ancillary">eksperimen pendugaan beta</a>, tetapkan @@M1@@. Jalankan eksperimen sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M2@@ dan parameter @@M3@@. Dalam setiap kasus, bandingkan penduga @@M4@@, @@M5@@, dan @@M6@@. Penduga mana yang tampaknya lebih baik dari segi galat kuadrat rata-rata?</p>',
    359: '<p>Terakhir, perhatikan bahwa @@M1@@ adalah rata-rata sampel untuk sampel acak berukuran @@M2@@ dari distribusi @@M3@@. Distribusi tersebut adalah distribusi eksponensial dengan laju @@M4@@.</p>',
    361: '<h4 id="par">Distribusi Pareto</h4>',
    363: '<p>Ingat bahwa <a href="../special/Pareto.html">distribusi Pareto</a> dengan parameter bentuk @@M1@@ dan parameter skala @@M2@@ mempunyai fungsi kepadatan probabilitas',
    365: 'Distribusi ini dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Pareto.html\')" class="ancillary">Vilfredo Pareto</a> dan merupakan distribusi berekor berat yang sering digunakan untuk memodelkan pendapatan serta jenis variabel acak tertentu lainnya.</p>',
    368: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi Pareto dengan parameter bentuk tak diketahui @@M2@@ dan parameter skala tak diketahui @@M3@@. Jika sampel tidak konstan—yang berlaku hampir pasti untuk sampel kontinu berukuran sekurang-kurangnya dua—penduga kemungkinan maksimum bagi @@M4@@ adalah @@M5@@, yaitu <a href="../sample/OrderStatistics.html">statistik terurut</a> pertama. Penduga kemungkinan maksimum bagi @@M6@@ adalah',
    371: '        <summary>Rincian:</summary>',
    372: '        <p>Perhatikan bahwa @@M1@@ untuk @@M2@@. Jadi fungsi log-kemungkinan yang bersesuaian dengan data @@M3@@ adalah',
    374: '        Secara ekuivalen, domainnya adalah @@M1@@ dan @@M2@@. Perhatikan bahwa @@M3@@ naik terhadap @@M4@@ untuk setiap @@M5@@ sehingga dimaksimumkan ketika @@M6@@ untuk setiap @@M7@@. Selanjutnya,',
    376: '        Jika penyebutnya positif, turunannya nol ketika @@M1@@. Selanjutnya, @@M2@@, sehingga maksimum dicapai pada titik kritis. Jika semua pengamatan sama, penyebut tersebut nol dan kemungkinan tidak terbatas ketika parameter bentuk bertambah; tidak ada penduga kemungkinan maksimum berhingga.</p>',
    380: '<p>Ingat bahwa jika @@M1@@, <a href="Moments.html#par">penduga metode momen</a> bagi @@M2@@ dan @@M3@@ adalah',
    384: '    <p class="app">Buka <a href="JavaScript:openAncillary(\'../apps/ParetoEstimate.html\')" class="ancillary">eksperimen pendugaan Pareto</a>. Jalankan eksperimen sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M1@@ dan parameter @@M2@@ serta @@M3@@. Bandingkan penduga metode momen dengan penduga kemungkinan maksimum. Penduga mana yang tampaknya lebih baik dari segi bias dan galat kuadrat rata-rata?</p>',
    387: '<p>Parameter skala pada distribusi Pareto sering kali diketahui.</p>',
    390: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi Pareto dengan parameter bentuk tak diketahui @@M2@@ dan parameter skala diketahui @@M3@@. Jika jumlah log-rasio sampel terhadap skala positif, penduga kemungkinan maksimum bagi @@M4@@ adalah',
    393: '        <summary>Rincian:</summary>',
    394: '        <p>Dengan menyesuaikan bukti sebelumnya, fungsi log-kemungkinan yang bersesuaian dengan data @@M1@@ adalah',
    396: '        Turunannya adalah',
    398: '        Jika penyebutnya positif, turunan nol ketika @@M1@@. Selanjutnya, @@M2@@, sehingga maksimum dicapai pada titik kritis. Jika semua pengamatan sama dengan batas skala, penyebutnya nol dan tidak ada pemaksimum berhingga.</p>',
    402: '<h4 id="uni">Distribusi Seragam</h4>',
})

T.update({
    404: '<p>Dalam subbagian ini kita mempelajari masalah pendugaan terkait distribusi seragam yang menjadi sumber wawasan dan contoh tandingan. Dalam suatu arti, masalah pertama merupakan padanan kontinu dari masalah pendugaan yang dipelajari pada bagian <a href="../urn/OrderStatistics.html">statistik terurut</a> dalam bab <a href="../urn/index.html">model pensampelan berhingga</a>. Andaikan @@M1@@ merupakan sampel acak dari <a href="../dist/Continuous.html#uni">distribusi seragam</a> pada interval @@M2@@, dengan @@M3@@ sebagai parameter tak diketahui. Jadi, distribusi asal sampel mempunyai fungsi kepadatan probabilitas',
    406: 'Mula-mula mari kita tinjau kembali hasil dari bagian sebelumnya.</p>',
    409: '    <p class="math">Penduga metode momen bagi @@M1@@ adalah @@M2@@. Penduga @@M3@@ mempunyai sifat-sifat berikut.</p>',
    411: '        <li>@@M1@@ tak bias.</li>',
    412: '        <li>@@M1@@ sehingga @@M2@@ konsisten.</li>',
    416: '<p>Sekarang mari kita tentukan penduga kemungkinan maksimumnya.</p>',
    419: '    <p class="math">Jika maksimum sampel positif, penduga kemungkinan maksimum bagi @@M1@@ adalah @@M2@@, yaitu <a href="../sample/OrderStatistics.html">statistik terurut</a> ke-@@M3@@. Penduga ini merupakan penduga kemungkinan maksimum hampir pasti; pada kejadian berprobabilitas nol ketika semua pengamatan sama dengan 0, supremum pada ruang parameter terbuka tidak dicapai. Statistik @@M4@@ mempunyai sifat-sifat berikut.</p>',
    422: '        <li>@@M1@@ sehingga @@M2@@ berbias negatif tetapi tak bias secara asimtotik.</li>',
    424: '        <li>@@M1@@ sehingga @@M2@@ konsisten.</li>',
    427: '        <summary>Rincian:</summary>',
    428: '        <p>Fungsi kemungkinan yang bersesuaian dengan data @@M1@@ adalah @@M2@@ untuk @@M3@@ bagi setiap @@M4@@, dengan parameter skala positif. Jika maksimum sampel positif, domainnya ekuivalen dengan @@M5@@. Fungsi @@M6@@ menurun, sehingga maksimum dicapai pada nilai terkecil, yaitu @@M7@@. Bagian (a) dan (c) menyatakan kembali hasil dari bagian statistik terurut; bagian (b) dan (d) mengikuti dari keduanya.</p>',
    432: '<p>Karena nilai harapan @@M1@@ merupakan kelipatan yang diketahui dari parameter @@M2@@, kita dapat dengan mudah membangun penduga tak bias.</p>',
    435: '    <p class="math">Misalkan @@M1@@. Penduga @@M2@@ mempunyai sifat-sifat berikut.</p>',
    437: '        <li>@@M1@@ tak bias.</li>',
    438: '        <li>@@M1@@ sehingga @@M2@@ konsisten.</li>',
    439: '        <li>Efisiensi relatif asimtotik @@M1@@ terhadap @@M2@@ tidak berhingga.</li>',
    442: '        <summary>Rincian:</summary>',
    443: '        <p>Bagian (a) dan (b) mengikuti dari <a href="#uni2" class="ref"></a> dan sifat dasar nilai harapan serta varians. Untuk bagian (c),',
    448: '<p>Bagian terakhir menunjukkan bahwa versi tak bias @@M1@@ dari penduga kemungkinan maksimum jauh lebih baik daripada penduga metode momen @@M2@@. Dalam pengertian laju galat kuadrat rata-rata yang digunakan pada halaman ini, sumber menyebut penduga seperti @@M3@@, yang galat kuadrat rata-ratanya turun pada orde @@M4@@, <dfn>super efisien</dfn>; istilah superefisien dalam teori asimtotik umum mempunyai arti yang lebih khusus. Setelah memperoleh penduga yang sangat baik, mari kita cari penduga yang sangat buruk. Calon alami ialah penduga berdasarkan @@M5@@, yaitu statistik terurut <em>pertama</em>. Hasil berikut memudahkan perhitungannya.</p>',
    451: '    <p class="math">Sampel @@M1@@ mempunyai sifat-sifat berikut.</p>',
    453: '        <li>@@M1@@ berdistribusi seragam pada @@M2@@ untuk setiap @@M3@@.</li>',
    454: '        <li>@@M1@@ juga merupakan sampel acak dari distribusi seragam pada @@M2@@.</li>',
    455: '        <li>@@M1@@ mempunyai distribusi yang sama dengan @@M2@@.</li>',
    458: '        <summary>Rincian:</summary>',
    460: '            <li>Ini merupakan akibat langsung dari fakta bahwa pencerminan afin terhadap titik tengah interval memetakan distribusi seragam pada interval tersebut kembali ke distribusi yang sama.</li>',
    461: '            <li>Hasil ini mengikuti bagian (a) dan fakta bahwa jika @@M1@@ merupakan barisan variabel saling bebas, maka @@M2@@ juga demikian.</li>',
    462: '            <li>Dari bagian (b), @@M1@@ mempunyai distribusi yang sama dengan @@M2@@.</li>',
    467: '<p>Sekarang kita dapat membangun penduga yang sangat buruk.</p>',
    470: '    <p class="math">Misalkan @@M1@@. Maka</p>',
    472: '        <li>@@M1@@ merupakan penduga tak bias bagi @@M2@@.</li>',
    473: '        <li>@@M1@@ sehingga @@M2@@ bahkan tidak konsisten.</li>',
    476: '        <summary>Rincian:</summary>',
    477: '        <p>Hasil-hasil ini mengikuti dari <a href="#uni4" class="ref"></a>:</p>',
    479: '            <li>@@M1@@ sehingga @@M2@@.</li>',
    486: '    <p class="app">Jalankan <a href="JavaScript:openAncillary(\'../apps/UniformEstimate.html\')" class="ancillary">eksperimen pendugaan seragam</a> sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M1@@ dan parameter @@M2@@. Dalam setiap kasus, bandingkan bias empiris serta galat kuadrat rata-rata penduga dengan nilai teoretisnya. Urutkan penduga berdasarkan galat kuadrat rata-rata empiris.</p>',
    489: '<p>Rangkaian latihan berikut menunjukkan bahwa penduga kemungkinan maksimum tidak selalu unik. Andaikan @@M1@@ merupakan sampel acak dari <a href="../dist/Continuous.html#uni">distribusi seragam</a> pada interval @@M2@@, dengan @@M3@@ sebagai parameter tak diketahui. Jadi, distribusi asal sampel mempunyai fungsi kepadatan probabilitas',
    491: 'Seperti biasa, mula-mula kita tinjau penduga metode momen.</p>',
    494: '    <p class="math">Penduga metode momen bagi @@M1@@ adalah @@M2@@. Penduga @@M3@@ mempunyai sifat-sifat berikut.</p>',
    496: '        <li>@@M1@@ tak bias.</li>',
    497: '        <li>@@M1@@ sehingga @@M2@@ konsisten.</li>',
    501: '<p>Namun, seperti telah dijanjikan, penduga kemungkinan maksimumnya tidak unik.</p>',
    504: '    <p class="math">Setiap statistik @@M1@@ merupakan penduga kemungkinan maksimum bagi @@M2@@.</p>',
    506: '        <summary>Rincian:</summary>',
    507: '        <p>Fungsi kemungkinan yang bersesuaian dengan data @@M1@@ adalah @@M2@@ untuk @@M3@@ dan @@M4@@. Domainnya ekuivalen dengan @@M5@@ dan @@M6@@. Karena fungsi kemungkinan konstan pada domain ini, hasilnya mengikuti.</p>',
    511: '<p>Untuk melengkapi pembahasan, mari kita tinjau masalah pendugaan penuh. Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi seragam pada @@M3@@, dengan @@M4@@ dan @@M5@@ keduanya tidak diketahui. Berikut hasil dari bagian sebelumnya.</p>',
    514: '    <p class="math">Misalkan @@M1@@ dan @@M2@@ masing-masing menyatakan penduga metode momen bagi @@M3@@ dan @@M4@@. Maka',
    516: '    dengan @@M1@@ sebagai rata-rata sampel dan @@M2@@ sebagai versi berbias dari varians sampel; simbol T menyatakan akar kuadrat nonnegatifnya.</p>',
    519: '<p>Pada tahap ini tidak mengherankan bahwa penduga kemungkinan maksimum merupakan fungsi dari statistik terurut terbesar dan terkecil.</p>',
    522: '    <p class="math">Jika rentang sampel positif, penduga kemungkinan maksimum bagi @@M1@@ dan @@M2@@ masing-masing adalah @@M3@@ dan @@M4@@. Jika rentang sampel nol, nilai skala 0 berada di luar ruang parameter dan supremum kemungkinan tidak dicapai.</p>',
    524: '        <li>@@M1@@ sehingga @@M2@@ berbias positif dan tak bias secara asimtotik.</li>',
    525: '        <li>@@M1@@ sehingga @@M2@@ berbias negatif dan tak bias secara asimtotik.</li>',
    526: '        <li>@@M1@@ sehingga @@M2@@ konsisten.</li>',
    527: '        <li>@@M1@@ sehingga @@M2@@ konsisten.</li>',
    530: '        <summary>Rincian:</summary>',
    531: '        <p>Fungsi kemungkinan yang bersesuaian dengan data @@M1@@ adalah @@M2@@ untuk @@M3@@ dan @@M4@@. Domainnya ekuivalen dengan @@M5@@ dan @@M6@@. Pada rentang sampel positif, fungsi kemungkinan hanya bergantung pada @@M7@@ dalam domain ini dan menurun terhadapnya, sehingga maksimum dicapai ketika @@M8@@ dan @@M9@@. Bagian (a)&ndash;(d) mengikuti hasil baku bagi statistik terurut dari distribusi seragam.</p>',
    535: '<h4 id="hyp">Model Hipergeometrik</h4>',
    537: '<p>Dalam semua contoh sebelumnya, barisan variabel acak teramati @@M1@@ merupakan sampel acak dari suatu distribusi. Namun, kemungkinan maksimum adalah metode yang sangat umum dan tidak mensyaratkan variabel teramati saling bebas ataupun berdistribusi identik. Dalam <dfn>model hipergeometrik</dfn>, terdapat populasi berisi @@M2@@ objek, dengan @@M3@@ objek <dfn>tipe 1</dfn> dan @@M4@@ objek lainnya <dfn>tipe 0</dfn>. <dfn>Ukuran populasi</dfn> @@M5@@ adalah bilangan bulat positif. <dfn>Jumlah objek tipe 1</dfn> @@M6@@ adalah bilangan bulat taknegatif dengan @@M7@@. Keduanya merupakan parameter dasar, dan biasanya salah satu atau keduanya tidak diketahui. Berikut beberapa contoh umum.</p>',
    540: '    <li>Objeknya adalah perangkat, yang diklasifikasikan sebagai <dfn>baik</dfn> atau <dfn>cacat</dfn>.</li>',
    541: '    <li>Objeknya adalah orang, yang diklasifikasikan sebagai <dfn>perempuan</dfn> atau <dfn>laki-laki</dfn>.</li>',
    542: '    <li>Objeknya adalah pemilih, yang diklasifikasikan sebagai <dfn>pendukung</dfn> atau <dfn>penentang</dfn> kandidat tertentu.</li>',
    543: '    <li>Objeknya adalah satwa liar dari jenis tertentu, yang <dfn>ditandai</dfn> atau <dfn>tidak ditandai</dfn>.</li>',
    546: '<p>Kita mengambil sampel @@M1@@ objek secara acak dari populasi, tanpa pengembalian, dengan ukuran sampel sekurang-kurangnya satu dan tidak melebihi ukuran populasi. Misalkan @@M2@@ adalah tipe objek terpilih ke-@@M3@@ sehingga barisan variabel teramati adalah @@M4@@. Variabel-variabel ini merupakan indikator yang berdistribusi identik, dengan @@M5@@ untuk setiap @@M6@@, tetapi saling bergantung karena pensampelan tanpa pengembalian. Banyaknya objek tipe 1 dalam sampel adalah @@M7@@. Statistik ini mempunyai <a href="../urn/Hypergeometric.html">distribusi hipergeometrik</a> dengan parameter @@M8@@, @@M9@@, dan @@M10@@, serta fungsi kepadatan probabilitas',
    548: 'Ingat notasi <dfn>pangkat jatuh</dfn>: @@M1@@ untuk @@M2@@ dan @@M3@@.</p>',
    551: '    <p class="math">Seperti di atas, misalkan @@M1@@ adalah variabel teramati dalam model hipergeometrik dengan parameter @@M2@@ dan @@M3@@. Maka</p>',
    553: '        <li>Salah satu penduga kemungkinan maksimum bagi @@M1@@ ketika @@M2@@ diketahui adalah @@M3@@. Jika rasio yang tak dibulatkan merupakan bilangan bulat dan nilai tersebut maupun bilangan bulat tepat di bawahnya sama-sama layak, keduanya memaksimumkan kemungkinan.</li>',
    554: '        <li>Salah satu penduga kemungkinan maksimum bagi @@M1@@ ketika @@M2@@ diketahui adalah @@M3@@ jika @@M4@@. Jika rasio tersebut bilangan bulat dan kedua nilai bersebelahan layak, keduanya terikat sebagai pemaksimum. Jika tidak ada objek tipe 1 yang teramati dan parameter tipe 1 positif, tidak ada pemaksimum berhingga; jika parameter tipe 1 nol, ukuran populasi tidak teridentifikasi.</li>',
    557: '        <summary>Rincian:</summary>',
    558: '        <p>Dari penerapan sederhana aturan perkalian, fungsi kepadatan probabilitas @@M1@@ bagi @@M2@@ adalah',
    560: '        dengan @@M1@@.</p>',
    562: '            <li>Dengan @@M1@@ diketahui, fungsi kemungkinan yang bersesuaian dengan data @@M2@@ adalah',
    564: '            Dengan syarat nilai parameter satu unit lebih kecil masih berada dalam domain, aljabar memberikan @@M1@@ jika dan hanya jika @@M2@@, yang ekuivalen dengan @@M3@@. Jadi salah satu maksimum @@M4@@ dicapai pada @@M5@@; jika rasio tersebut merupakan bilangan bulat dan nilai itu maupun bilangan bulat tepat di bawahnya sama-sama layak, keduanya terikat.',
    566: '            <li>Demikian pula, dengan @@M1@@ diketahui, fungsi kemungkinan yang bersesuaian dengan data @@M2@@ adalah',
    568: '            Dengan syarat ukuran populasi satu unit lebih kecil masih layak bagi data teramati sehingga kemungkinan pada nilai itu positif, aljabar memberikan @@M1@@ jika dan hanya jika @@M2@@, yang ekuivalen dengan @@M3@@ dengan asumsi @@M4@@. Jadi salah satu maksimum @@M5@@ dicapai ketika @@M6@@; jika rasio tersebut merupakan bilangan bulat dan kedua nilai yang bersebelahan layak bagi data teramati, keduanya terikat.</li>',
    573: '<p>Dalam contoh keandalan, biasanya @@M1@@ diketahui dan kita ingin menduga @@M2@@. Dalam contoh satwa liar, biasanya @@M3@@ diketahui dan kita ingin menduga @@M4@@. Contoh ini dikenal sebagai model <dfn>tangkap–tangkap kembali</dfn>.</p>',
    575: '<p>Jelas terdapat hubungan erat antara model hipergeometrik dan <a href="#ber">model percobaan Bernoulli</a> pada subbagian di atas. Jika pensampelan dilakukan <em>dengan</em> pengembalian, model percobaan Bernoulli dengan @@M1@@ berlaku, bukan model hipergeometrik. Selain itu, jika ukuran populasi @@M2@@ besar dibandingkan ukuran sampel @@M3@@, model hipergeometrik dihampiri dengan baik oleh model percobaan Bernoulli, kembali dengan @@M4@@.</p>',
    580: '        <li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>',
    581: '        <li class="child"><a href="Estimators.html" title="Penduga">1</a></li>',
    582: '        <li class="child"><a href="Moments.html" title="Metode Momen">2</a></li>',
    584: '        <li class="child"><a href="Bayes.html" title="Penduga Bayes">4</a></li>',
    585: '        <li class="child"><a href="Unbiased.html" title="Penduga Tak Bias Terbaik">5</a></li>',
    586: '        <li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancilar">6</a></li>',
    587: '        <li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>',
    588: '        <li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>',
    591: '        <li class="sister"><a href="JavaScript:openAncillary(\'../apps/index.html\')" class="ancillary">Aplikasi</a></li>',
    592: '        <li class="sister"><a href="JavaScript:openAncillary(\'../data/index.html\')" class="ancillary">Himpunan Data</a></li>',
    593: '        <li class="child"><a href="JavaScript:openAncillary(\'../biographies/index.html\')" class="ancillary">Biografi</a></li>',
})

# Exact bounded target repairs; every other delimited TeX span remains
# authority-identical and is restored from the frozen source.
MATH_FIXES: dict[int, tuple[tuple[str, str], ...]] = {
    110: ((
        r"\[ \hat{L}_\bs{x}(\lambda) = \max\left\{L_\bs{x}(\theta): \theta \in h^{-1}\{\lambda\} \right\}; \quad \lambda \in \Lambda \]",
        r"\[ \hat{L}_\bs{x}(\lambda) = \sup\left\{L_\bs{x}(\theta): \theta \in h^{-1}\{\lambda\} \right\}, \quad \lambda \in \Lambda \]",
    ),),
    132: ((
        r"\[ M_2 = \frac{1}{n} \sum_{i=1}^n X_i^2 \]",
        r"\[ M^{(2)} = \frac{1}{n} \sum_{i=1}^n X_i^2 \]",
    ),),
    142: ((r"\( (0, 1) \)", r"\( [0, 1] \)"),),
    150: ((
        r"\[ \frac{d^2}{d p^2} \ln L_{\bs{x}}(p) = -\frac{y}{p^2} - \frac{n - 1}{(1 - p)^2} \lt 0 \]",
        r"\[ \frac{d^2}{d p^2} \ln L_{\bs{x}}(p) = -\frac{y}{p^2} - \frac{n - y}{(1 - p)^2} \lt 0 \]",
    ),),
    168: ((
        r"\(L_{\bs{x}}\left(\frac{1}{2}\right) = \left(\frac{1}{2}\right)^y\)",
        r"\(L_{\bs{x}}\left(\frac{1}{2}\right) = \left(\frac{1}{2}\right)^n\)",
    ),),
    193: ((r"\(p \in (0, 1)\)", r"\(p \in [0, 1]\)"),),
    202: ((r"\(\N_+\)", r"\(\mathbb{N}_+\)"),),
    203: ((
        r"\[ g(x) = p (1 - p)^{x-1}, \quad x \in \N_+ \]",
        r"\[ g(x) = p (1 - p)^{x-1}, \quad x \in \mathbb{N}_+ \]",
    ),),
    210: (
        (r"\( x \in \N_+ \)", r"\( x \in \mathbb{N}_+ \)"),
        (
            r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \in \N_+^n \)",
            r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \in \mathbb{N}_+^n \)",
        ),
    ),
    213: ((
        r"\[ \frac{d}{dp} \ln L(p) = \frac{n}{p} - \frac{y - n}{1 - p} \]",
        r"\[ \frac{d}{dp} \ln L_{\bs{x}}(p) = \frac{n}{p} - \frac{y - n}{1 - p} \]",
    ),),
    223: ((
        r"\[ g(x) = \binom{x + k - 1}{k - 1} p^k (1 - p)^x, \quad x \in \N \]",
        r"\[ g(x) = \frac{\Gamma(x + k)}{\Gamma(k)\,x!} p^k (1 - p)^x, \quad x \in \N \]",
    ),),
    231: ((
        r"\( \ln g(x) = \ln \binom{x + k - 1}{k - 1} + k \ln p + x \ln(1 - p) \)",
        r"\( \ln g(x) = \ln \Gamma(x + k) - \ln \Gamma(k) - \ln(x!) + k \ln p + x \ln(1 - p) \)",
    ),),
    233: ((
        r"\( C = \sum_{i=1}^n \ln \binom{x_i + k - 1}{k - 1} \)",
        r"\( C = \sum_{i=1}^n [\ln \Gamma(x_i + k) - \ln \Gamma(k) - \ln(x_i!)] \)",
    ),),
    291: ((
        r"\[ \frac{\partial^2}{\partial \mu^2} \ln L_\bs{x}(m, t^2) = -n / t^2, \; \frac{\partial^2}{\partial \mu \partial \sigma^2} \ln L_\bs{x}(m, t^2) = 0, \; \frac{\partial^2}{\partial (\sigma^2)^2} \ln L_\bs{x}(m, t^2) = -n / t^4\]",
        r"\[ \frac{\partial^2}{\partial \mu^2} \ln L_\bs{x}(m, t^2) = -n / t^2, \; \frac{\partial^2}{\partial \mu \partial \sigma^2} \ln L_\bs{x}(m, t^2) = 0, \; \frac{\partial^2}{\partial (\sigma^2)^2} \ln L_\bs{x}(m, t^2) = -n / (2 t^4)\]",
    ),),
    326: (
        (r"\( b = y / n k = 1 / k m \)", r"\( b = \frac{y}{n k} = \frac{m}{k} \)"),
        (r"\( b = y / n k \)", r"\( b = \frac{y}{n k} \)"),
    ),
    347: (
        (r"\( x \in (0, \infty) \)", r"\( x \in (0, 1) \)"),
        (
            r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \in (0, \infty)^n \)",
            r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \in (0, 1)^n \)",
        ),
    ),
    353: ((
        r"\(U = M (M - M_2) \big/ (M_2 - M^2)\)",
        r"\(U = M (M - M^{(2)}) \big/ (M^{(2)} - M^2)\)",
    ),),
    373: ((
        r"\[ \ln L_\bs{x}(a, b) = n \ln a + n a \ln b - (a + 1) \sum_{i=1}^n \ln x_i; \quad 0 \lt a \lt \infty, \, 0 \lt b \le x_i \text{ for each } i \in \{1, 2, \ldots, n\} \]",
        r"\[ \ln L_\bs{x}(a, b) = n \ln a + n a \ln b - (a + 1) \sum_{i=1}^n \ln x_i; \quad 0 \lt a \lt \infty, \, 0 \lt b \le x_i \text{ untuk setiap } i \in \{1, 2, \ldots, n\} \]",
    ),),
    381: ((
        r"\[ 1 + \sqrt{\frac{M_2}{M_2 - M^2}}, \; \frac{M_2}{M} \left(1 - \sqrt{\frac{M_2 - M^2}{M_2}}\right)\]",
        r"\[ 1 + \sqrt{\frac{M^{(2)}}{M^{(2)} - M^2}}, \; \frac{M^{(2)}}{M} \left(1 - \sqrt{\frac{M^{(2)} - M^2}{M^{(2)}}}\right)\]",
    ),),
    428: ((
        r"\( i \in \{1, 2, \ldots n\} \)",
        r"\( i \in \{1, 2, \ldots, n\} \)",
    ),),
    444: ((
        r"\[ \frac{\var(U)}{\var(V)} = \frac{h^2 / 3 n}{h^2 / n (n + 2)} = \frac{n + 2}{3} \to \infty \text{ as } n \to \infty \]",
        r"\[ \frac{\var(U)}{\var(V)} = \frac{h^2/(3n)}{h^2/[n(n + 2)]} = \frac{n + 2}{3} \to \infty \text{ ketika } n \to \infty \]",
    ),),
    486: ((r"\(a\)", r"\(h\)"),),
    507: ((
        r"\( \bs{x} = (x_1, x_2, \ldots, x_n\} \)",
        r"\( \bs{x} = (x_1, x_2, \ldots, x_n) \)",
    ),),
    515: ((
        r"\[ U = 2 M - \sqrt{3} T, \quad V = 2 \sqrt{3} T \]",
        r"\[ U = M - \sqrt{3} T, \quad V = 2 \sqrt{3} T \]",
    ),),
    516: ((
        r"\( T = \frac{1}{n} \sum_{i=1}^n (X_i - M)^2 \)",
        r"\( T^2 = \frac{1}{n} \sum_{i=1}^n (X_i - M)^2 \)",
    ),),
    524: ((
        r"\( E(U) = a + \frac{h}{n + 1} \)",
        r"\( \E(U) = a + \frac{h}{n + 1} \)",
    ),),
    525: ((
        r"\( E(V) = h \frac{n - 1}{n + 1} \)",
        r"\( \E(V) = h \frac{n - 1}{n + 1} \)",
    ),),
    546: ((
        r"\( P(X_i = 1) = r / N \)",
        r"\( \P(X_i = 1) = r / N \)",
    ),),
    547: ((
        r"\[ P(Y = y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, N - n + r\}, \ldots, \min\{n, r\}\} \]",
        r"\[ \P(Y = y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, n - N + r\}, \ldots, \min\{n, r\}\} \]",
    ),),
    553: ((
        r"\( U = \lfloor N M \rfloor = \lfloor N Y / n \rfloor \)",
        r"\( U = \min\{N, \lfloor (N + 1)Y / n \rfloor\} \)",
    ),),
    563: ((
        r"\[ L_{\bs{x}}(r) = \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad r \in \{y, \ldots, \min\{n, y + N - n\}\}  \]",
        r"\[ L_{\bs{x}}(r) = \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad r \in \{y, \ldots, N - n + y\} \]",
    ),),
    564: (
        (r"\( r \lt N y / n \)", r"\( r \lt (N + 1)y / n \)"),
        (
            r"\( r = \lfloor N y / n \rfloor \)",
            r"\( r = \min\{N, \lfloor (N + 1)y / n \rfloor\} \)",
        ),
    ),
    568: ((r"\( L_{\bs{x}}(r) \)", r"\( L_{\bs{x}}(N) \)"),),
}

STABLE_IDS: dict[int, tuple[str, str]] = {
    57: ('<div class="unit">', '<div class="unit" id="o006.random.point.likelihood.unit.likelihood-function">'),
    64: ('<div class="unit">', '<div class="unit" id="o006.random.point.likelihood.unit.maximum-likelihood-estimator">'),
    72: ('<div class="unit">', '<div class="unit" id="o006.random.point.likelihood.unit.log-likelihood-function">'),
    92: ('<div class="unit">', '<div class="unit" id="o006.random.point.likelihood.unit.random-sample-likelihood">'),
    116: ('<div class="unit">', '<div class="unit" id="o006.random.point.likelihood.unit.invariance-property">'),
    192: ('<div class="unit">', '<div class="unit" id="o006.random.point.likelihood.unit.bernoulli-variance">'),
    521: ('<div class="unit">', '<div class="unit" id="o006.random.point.likelihood.unit.uniform-location-scale-mle">'),
}

LOCAL_URLS = {
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/point/index.html": "index.html",
    "https://www.randomservices.org/random/point/Estimators.html": "Estimators.html",
    "https://www.randomservices.org/random/point/Moments.html": "Moments.html",
    "https://www.randomservices.org/random/point/Likelihood.html": "Likelihood.html",
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


def apply_math_fixes(line_number: int, text: str) -> str:
    for old, new in MATH_FIXES.get(line_number, ()):
        if text.count(old) != 1:
            raise RuntimeError(
                f"line {line_number}: expected one exact math defect, found {text.count(old)}"
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


def replace_exact(lines: list[str], line_number: int, old: str, new: str) -> None:
    source = lines[line_number - 1]
    ending = "\r\n" if source.endswith("\r\n") else "\n" if source.endswith("\n") else ""
    body = source.removesuffix(ending)
    if body.strip() != old:
        raise RuntimeError(f"line {line_number}: stable-ID authority row changed")
    indent = body[: len(body) - len(body.lstrip())]
    lines[line_number - 1] = indent + new + ending


def main() -> None:
    source_bytes = SOURCE.read_bytes()
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
    for line_number in sorted(MATH_FIXES):
        source = lines[line_number - 1]
        ending = "\r\n" if source.endswith("\r\n") else "\n" if source.endswith("\n") else ""
        lines[line_number - 1] = apply_math_fixes(
            line_number, source.removesuffix(ending)
        ) + ending
    if not lines[469].rstrip("\r\n").endswith("</p>"):
        raise RuntimeError("line 470 paragraph repair missing")
    for line_number, (old, new) in sorted(STABLE_IDS.items()):
        replace_exact(lines, line_number, old, new)
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
    for phrase in (
        '<html lang="en">', "JavaScript:openAncillary", "Expand Details",
        "Contract Details", ">Details:<", ">Point Estimation<",
        ">Maximum Likelihood<", ">Basic Theory<", ">The Method<",
        ">Vector of Parameters<", ">Random Samples<",
        ">Examples and Special Cases<", ">The Bernoulli Distribution<",
        ">The Geometric Distribution<", ">The Negative Binomial Distribution<",
        ">The Poisson Distribution<", ">The Normal Distribution<",
        ">The Gamma Distribution<", ">The Beta Distribution<",
        ">The Pareto Distribution<", ">Uniform Distributions<",
        ">The Hypergeometric Model<", ">Apps<", ">Data Sets<", "> Biographies<",
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
