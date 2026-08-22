#!/usr/bin/env python3
"""Create the bounded id-ID Method of Moments target.

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
SOURCE = ROOT / "authority" / "upstream" / "random" / "point" / "Moments.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "point" / "Moments.html"
SOURCE_URL = "https://www.randomservices.org/random/point/Moments.html"
SOURCE_SHA256 = "43755b5bee6179fca8d7c1c964e7c6a9bb1a9de6f3916130100c69e666a3194e"
EXPECTED_SOURCE_LINES = 628
MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)
TOKEN_RE = re.compile(r"@@M([1-9][0-9]*)@@")

# Only reader-facing rows are replaced. Formula-only rows remain exact source
# bytes unless listed in MATH_FIXES.
T: dict[int, str] = {
    2: '<html lang="id-ID">',
    6: '    <title>Metode Momen</title>',
    9: '    <meta name="keywords" content="probabilitas, statistika, pendugaan titik, metode momen, rata-rata, varians, distribusi normal, distribusi Bernoulli, distribusi geometrik, distribusi binomial negatif, distribusi Poisson, distribusi gamma, distribusi beta, distribusi Pareto, distribusi seragam, distribusi hipergeometrik">',
    36: '        <li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>',
    37: '        <li class="child"><a href="Estimators.html" title="Penduga">1</a></li>',
    39: '        <li class="child"><a href="Likelihood.html" title="Kemungkinan Maksimum">3</a></li>',
    40: '        <li class="child"><a href="Bayes.html" title="Penduga Bayes">4</a></li>',
    41: '        <li class="child"><a href="Unbiased.html" title="Penduga Tak Bias Terbaik">5</a></li>',
    42: '        <li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancilar">6</a></li>',
    43: '        <li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>',
    44: '        <li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>',
    46: '    <h2 id="o006.random.point.moments.page">2. Metode Momen</h2>',
    49: '<h3 id="o006.random.point.moments.section.basic-theory">Teori Dasar</h3>',
    51: '<h4 id="o006.random.point.moments.section.method">Metode</h4>',
    53: '<p>Andaikan kita memiliki suatu <a href="../prob/Experiments.html">eksperimen acak</a> dasar dengan <a href="../prob/Probability.html">variabel acak</a> teramati bernilai riil @@M1@@. Distribusi @@M2@@ memiliki @@M3@@ parameter bernilai riil yang tidak diketahui, atau secara ekuivalen vektor parameter @@M4@@ dengan nilai dalam suatu himpunan bagian dari @@M5@@. Seperti biasa, kita mengulangi eksperimen sebanyak @@M6@@ kali untuk menghasilkan <a href="../sample/Introduction.html">sampel acak</a> berukuran @@M7@@ dari distribusi @@M8@@.',
    55: 'Jadi, @@M1@@ merupakan barisan variabel acak yang <a href="../prob/Independence.html">saling bebas</a>, masing-masing dengan distribusi @@M2@@. <dfn>Metode momen</dfn> adalah teknik untuk membangun <a href="Estimators.html">penduga</a> parameter dengan mencocokkan <em>momen sampel</em> dengan <em>momen distribusi</em> yang bersesuaian.</p>',
    58: '    <p class="dfn">Misalkan @@M1@@ menyatakan <a href="../expect/Properties.html#mom">momen</a> ke-@@M2@@ dari @@M3@@ terhadap titik asal (nol):',
    62: '<p>Notasi ini menekankan kebergantungan momen-momen tersebut pada vektor parameter @@M1@@. Perhatikan pula bahwa @@M2@@ hanyalah rata-rata @@M3@@, yang biasanya kita nyatakan cukup dengan @@M4@@.</p>',
    65: '    <p class="dfn">Misalkan @@M1@@ menyatakan momen sampel ke-@@M2@@ terhadap titik asal (nol):',
    69: '<p>Secara ekuivalen, @@M1@@ adalah rata-rata sampel untuk sampel acak @@M2@@ dari distribusi @@M3@@. Notasi ini menekankan kebergantungan momen sampel pada sampel @@M4@@. Perhatikan pula bahwa @@M5@@ hanyalah rata-rata sampel biasa, yang umumnya kita nyatakan dengan @@M6@@ (atau @@M7@@ jika hendak menegaskan kebergantungannya pada ukuran sampel). Dari hasil sebelumnya, kita mengetahui bahwa @@M8@@ merupakan penduga tak bias dan konsisten bagi @@M9@@ untuk setiap @@M10@@. Metodenya bekerja sebagai berikut.</p>',
    72: '    <p class="dfn">Untuk membangun penduga <dfn>metode momen</dfn> @@M1@@ masing-masing bagi parameter @@M2@@, kita tinjau persamaan',
    74: '    secara berurutan untuk @@M1@@ sampai kita dapat menyatakan @@M2@@ sebagai fungsi dari @@M3@@.</p>',
    77: '<p>Persamaan untuk @@M1@@ memberikan @@M2@@ persamaan dengan @@M3@@ peubah tak diketahui, sehingga ada harapan—tetapi tidak ada jaminan—bahwa persamaan tersebut dapat diselesaikan untuk menyatakan @@M4@@ sebagai fungsi dari @@M5@@. Bahkan, terkadang kita memerlukan persamaan dengan @@M6@@. Latihan <a href="#bet2" class="ref"></a> memberikan contoh sederhana. Metode momen dapat diperluas ke parameter yang berkaitan dengan distribusi bivariat atau distribusi multivariat yang lebih umum dengan mencocokkan momen hasil kali sampel dengan momen hasil kali distribusi yang bersesuaian. Metode momen juga terkadang tetap masuk akal ketika variabel sampel @@M7@@ tidak saling bebas, asalkan setidaknya berdistribusi identik. <a href="#hyp">Model hipergeometrik</a> pada subbagian berikut merupakan salah satu contohnya.</p>',
    79: '<p>Tentu saja, penduga metode momen bergantung pada ukuran sampel @@M1@@. Sejauh ini kita menyembunyikan indeks tersebut agar notasi tetap sederhana. Namun, dalam penerapan berikut, indeks itu kita tampilkan kembali karena kita hendak membahas perilaku asimtotik. Pada sampel berhingga, persamaan momen dapat pula tidak mempunyai solusi dalam ruang parameter atau menghasilkan penyebut nol; dalam kasus seperti itu, rumus yang ditampilkan hanya berlaku ketika solusinya terdefinisi dan memenuhi batas parameter yang dinyatakan.</p>',
    81: '<h4 id="est">Menduga Rata-Rata dan Varians</h4>',
    83: '<p>Menduga <a href="../expect/Properties.html">rata-rata</a> dan <a href="../expect/Variance.html">varians</a> suatu distribusi merupakan penerapan metode momen yang paling sederhana. Di seluruh subbagian ini, kita mengasumsikan suatu variabel acak dasar bernilai riil @@M1@@ dengan @@M2@@ dan @@M3@@. Sesekali kita juga memerlukan @@M4@@, yaitu momen pusat keempat. Kita mengambil sampel dari distribusi @@M5@@ untuk menghasilkan barisan @@M6@@ yang terdiri atas variabel-variabel saling bebas, masing-masing dengan distribusi @@M7@@. Untuk setiap @@M8@@, @@M9@@ merupakan sampel acak berukuran @@M10@@ dari distribusi @@M11@@. Kita mulai dengan menduga rata-rata, yang pada dasarnya langsung diperoleh dengan metode ini.</p>',
    86: '    <p class="math">Andaikan rata-rata @@M1@@ tidak diketahui. Penduga metode momen bagi @@M2@@ berdasarkan @@M3@@ adalah rata-rata sampel',
    89: '        <li>@@M1@@, sehingga @@M2@@ tak bias untuk @@M3@@.</li>',
    90: '        <li>@@M1@@ untuk @@M2@@, sehingga @@M3@@ konsisten.</li>',
    93: '        <summary>Rincian:</summary>',
    94: '        <p>Inilah bentuk paling dasar dari metode tersebut. Metode momen bekerja dengan mencocokkan rata-rata distribusi dengan rata-rata sampel. Fakta bahwa @@M1@@ dan @@M2@@ untuk @@M3@@ merupakan sifat yang telah kita jumpai beberapa kali.</p>',
    98: '<p>Sebaliknya, pendugaan varians distribusi bergantung pada apakah rata-rata distribusi @@M1@@ diketahui atau tidak. Mula-mula kita tinjau kasus yang lebih realistis ketika rata-rata juga tidak diketahui. Ingat bahwa untuk @@M2@@, <a href="../sample/Variance.html">varians sampel</a> berdasarkan @@M3@@ adalah',
    100: 'Ingat pula bahwa @@M1@@, sehingga @@M2@@ tak bias untuk @@M3@@, dan bahwa @@M4@@, sehingga @@M5@@ konsisten.</p>',
    103: '    <p class="math">Andaikan rata-rata @@M1@@ dan varians @@M2@@ keduanya tidak diketahui. Untuk @@M3@@, penduga metode momen bagi @@M4@@ berdasarkan @@M5@@ adalah',
    106: '        <li>@@M1@@ untuk @@M2@@, sehingga @@M3@@ tak bias secara asimtotik.</li>',
    107: '        <li>@@M1@@ untuk @@M2@@, sehingga @@M3@@ konsisten.</li>',
    110: '        <summary>Rincian:</summary>',
    112: '        <p>Seperti sebelumnya, penduga metode momen bagi rata-rata distribusi @@M1@@ adalah rata-rata sampel @@M2@@. Di sisi lain, @@M3@@, sehingga penduga metode momen bagi @@M4@@ adalah @@M5@@, yang dapat disederhanakan menjadi hasil di atas. Perhatikan bahwa @@M6@@ untuk @@M7@@.</p>',
    114: '            <li>Perhatikan bahwa @@M1@@, sehingga @@M2@@.</li>',
    115: '            <li>Ingat bahwa @@M1@@. Namun, @@M2@@. Hasilnya diperoleh dengan menyubstitusikan @@M3@@ yang diberikan di atas dan @@M4@@ pada bagian (a).</li>',
    120: '<p>Jadi, @@M1@@ berbias negatif dan secara rata-rata menduga @@M2@@ terlalu rendah. Karena hasil ini, @@M3@@ disebut <dfn>varians sampel berbias</dfn> untuk membedakannya dari varians sampel biasa (tak bias) @@M4@@.</p>',
    122: '<p>Selanjutnya, mari kita tinjau kasus yang jarang terjadi dan biasanya tidak realistis, tetapi menarik secara matematis: rata-rata diketahui, sedangkan varians tidak diketahui.</p>',
    125: '    <p class="math">Andaikan rata-rata @@M1@@ diketahui dan varians @@M2@@ tidak diketahui. Untuk @@M3@@, penduga metode momen bagi @@M4@@ berdasarkan @@M5@@ adalah',
    128: '        <li>@@M1@@, sehingga @@M2@@ tak bias untuk @@M3@@.</li>',
    129: '        <li>@@M1@@ untuk @@M2@@, sehingga @@M3@@ konsisten.</li>',
    132: '        <summary>Rincian:</summary>',
    133: '        <p>Hasil-hasil ini berlaku karena @@M1@@ merupakan rata-rata sampel yang bersesuaian dengan sampel acak berukuran @@M2@@ dari distribusi @@M3@@.</p>',
    137: '<p>Kita membandingkan barisan penduga @@M1@@ dengan barisan penduga @@M2@@ dalam bagian pengantar mengenai <a href="Estimators.html">penduga</a>. Dengan syarat momen pusat keempat berhingga dan lebih besar daripada kuadrat varians, ingat bahwa @@M3@@ untuk @@M4@@ dan @@M5@@ ketika @@M6@@. Tidak ada hubungan umum yang sederhana antara @@M7@@ dan @@M8@@, ataupun antara @@M9@@ dan @@M10@@, tetapi hubungan asimtotiknya sederhana.</p>',
    140: '    <p class="math">Jika momen pusat keempat berhingga dan lebih besar daripada kuadrat varians, maka @@M1@@ dan @@M2@@ ketika @@M3@@.</p>',
    142: '        <summary>Rincian:</summary>',
    143: '        <p>Berdasarkan uraian sebelumnya, kita cukup membuktikan salah satu limit tersebut. Koefisien @@M1@@ dan @@M2@@ dalam @@M3@@ masing-masing asimtotik terhadap @@M4@@ dan negatifnya ketika @@M5@@. Dengan hipotesis di atas, selisih kedua momen itu menghasilkan suku utama bersama yang positif pada pembilang dan penyebut, sehingga rasionya menuju 1.</p>',
    147: '<p>Dari sini juga diperoleh bahwa jika @@M1@@ dan @@M2@@ keduanya tidak diketahui, penduga metode momen bagi simpangan baku @@M3@@ adalah @@M4@@. Dalam kasus yang jarang terjadi, yaitu ketika @@M5@@ diketahui tetapi @@M6@@ tidak diketahui, penduga metode momen bagi @@M7@@ adalah @@M8@@.</p>',
    149: '<h4 id="o006.random.point.moments.section.two-parameter-estimation">Menduga Dua Parameter</h4>',
    151: '<p>Ada beberapa distribusi khusus penting dengan dua parameter; sebagian di antaranya disertakan dalam latihan komputasi pada <a href="#spe" class="ref"></a> berikut. Dengan dua parameter, kita dapat menurunkan penduga metode momen dengan mencocokkan rata-rata dan varians distribusi dengan rata-rata dan varians sampel, alih-alih mencocokkan rata-rata dan momen kedua distribusi dengan rata-rata dan momen kedua sampel. Pendekatan alternatif ini terkadang menghasilkan persamaan yang lebih mudah. Untuk menetapkan notasi, andaikan suatu distribusi pada @@M1@@ memiliki parameter @@M2@@ dan @@M3@@. Kita mengambil sampel dari distribusi tersebut untuk menghasilkan barisan variabel saling bebas @@M4@@, semuanya dengan distribusi yang sama. Untuk @@M5@@, @@M6@@ merupakan sampel acak berukuran @@M7@@ dari distribusi itu. Misalkan @@M8@@, @@M9@@, dan @@M10@@ masing-masing menyatakan rata-rata sampel, momen sampel kedua, dan varians sampel berbias yang bersesuaian dengan @@M11@@, sedangkan @@M12@@, @@M13@@, dan @@M14@@ masing-masing menyatakan rata-rata, momen kedua, dan varians distribusi.</p>',
    154: '    <p class="math">Jika penduga metode momen @@M1@@ dan @@M2@@, masing-masing bagi @@M3@@ dan @@M4@@, dapat diperoleh dengan menyelesaikan dua persamaan pertama',
    156: '    maka @@M1@@ dan @@M2@@ juga dapat diperoleh dengan menyelesaikan persamaan',
    159: '        <summary>Rincian:</summary>',
    160: '        <p>Ingat bahwa @@M1@@. Selain itu, @@M2@@. Jadi, persamaan @@M3@@, @@M4@@ ekuivalen dengan persamaan @@M5@@, @@M6@@.</p>',
    164: '<p>Karena hasil ini, varians sampel berbias @@M1@@ akan muncul dalam banyak masalah pendugaan untuk distribusi khusus yang kita tinjau di bawah.</p>',
    166: '<h3 id="spe">Distribusi Khusus</h3>',
    168: '<h4 id="norm">Distribusi Normal</h4>',
    170: '<p><a href="../special/Normal.html">Distribusi normal</a> dengan rata-rata @@M1@@ dan varians @@M2@@ adalah distribusi kontinu pada @@M3@@ dengan fungsi kepadatan probabilitas @@M4@@ yang diberikan oleh',
    172: 'Distribusi ini merupakan salah satu distribusi terpenting dalam probabilitas dan statistika, terutama karena <a href="../sample/CLT.html">teorema limit pusat</a>.</p>',
    174: '<p>Andaikan sekarang @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi normal dengan rata-rata @@M3@@ dan varians @@M4@@. Dari hasil umum di atas, kita mengetahui bahwa jika @@M5@@ tidak diketahui maka rata-rata sampel @@M6@@ adalah penduga metode momen bagi @@M7@@, dan jika @@M8@@ juga tidak diketahui maka penduga metode momen bagi @@M9@@ adalah @@M10@@. Sebaliknya, dalam kasus yang jarang terjadi, yaitu ketika @@M11@@ diketahui, @@M12@@ adalah penduga metode momen bagi @@M13@@. Tujuan kita adalah melihat bagaimana perbandingan di atas menyederhana untuk distribusi normal.</p>',
    177: '    <p class="math">Galat kuadrat rata-rata bagi @@M1@@ dan @@M2@@.</p>',
    181: '        <li>@@M1@@ untuk @@M2@@.</li>',
    184: '    <summary>Rincian:</summary>',
    185: '    <p>Ingat bahwa untuk distribusi normal, @@M1@@. Dengan menyubstitusikan nilai ini ke dalam hasil umum, kita memperoleh bagian (a) dan (b). Bagian (c) mengikuti dari (a) dan (b). Tentu saja, dari <a href="#asymp" class="ref"></a>, efisiensi relatif asimtotiknya tetap 1.</p>',
    189: '<p>Jadi, @@M1@@ dan @@M2@@ merupakan kelipatan satu sama lain; @@M3@@ tak bias, tetapi ketika sampel berasal dari distribusi normal, @@M4@@ memiliki galat kuadrat rata-rata yang lebih kecil. Yang mengejutkan, galat kuadrat rata-rata @@M5@@ bahkan lebih kecil daripada @@M6@@.</p>',
    192: '    <p class="math">Galat kuadrat rata-rata bagi @@M1@@ dan @@M2@@.</p>',
    195: '        <li>@@M1@@ untuk @@M2@@.</li>',
    198: '        <summary>Rincian:</summary>',
    199: '        <p>Sekali lagi, karena sampel berasal dari distribusi normal, @@M1@@. Dengan menyubstitusikan nilai ini ke dalam rumus umum bagi @@M2@@, kita memperoleh bagian (a).</p>',
    204: '    <p class="app">Jalankan <a href="JavaScript:openAncillary(\'../apps/NormalEstimate.html\')" class="ancillary">eksperimen pendugaan pada distribusi normal</a> sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M1@@ serta parameter @@M2@@ dan @@M3@@. Bandingkan bias empiris dan galat kuadrat rata-rata @@M4@@ serta @@M5@@ dengan nilai teoretisnya. Penduga mana yang lebih baik dari segi bias? Penduga mana yang lebih baik dari segi galat kuadrat rata-rata?</p>',
    207: '<p>Selanjutnya kita tinjau penduga bagi simpangan baku @@M1@@. Seperti dicatat dalam pembahasan umum di atas, @@M2@@ adalah penduga metode momen ketika @@M3@@ tidak diketahui, sedangkan @@M4@@ adalah penduga metode momen dalam kasus yang jarang terjadi, yaitu ketika @@M5@@ diketahui. Penduga alami lainnya tentu saja adalah @@M6@@, yaitu simpangan baku sampel biasa. Barisan berikut, yang didefinisikan melalui <a href="../special/Gamma.html">fungsi gamma</a>, ternyata penting dalam analisis ketiga penduga tersebut.</p>',
    210: '    <p class="math">Tinjau barisan',
    212: '    Maka @@M1@@ untuk @@M2@@ dan @@M3@@ ketika @@M4@@.</p>',
    215: '<p>Pertama, andaikan @@M1@@ diketahui sehingga @@M2@@ merupakan penduga metode momen bagi @@M3@@.</p>',
    218: '    <p class="math">Untuk @@M1@@,</p>',
    226: '        <summary>Rincian:</summary>',
    227: '        <p>Ingat bahwa @@M1@@ memiliki <a href="../special/ChiSquare.html">distribusi khi-kuadrat</a> dengan @@M2@@ derajat kebebasan, sehingga @@M3@@ memiliki <a href="../special/ChiSquare.html#chi">distribusi khi</a> dengan @@M4@@ derajat kebebasan. Dengan menyelesaikan hubungan tersebut terhadap penduga simpangan baku, kita peroleh',
    229: '        Dari rumus rata-rata dan varians distribusi khi, kita peroleh',
    237: '<p>Jadi, bias @@M1@@ sebagai penduga bagi @@M2@@ tidak positif dan menjadi negatif kecuali kuadrat penduga tersebut konstan hampir pasti; penduga ini tak bias secara asimtotik dan konsisten. Secara umum—apa pun distribusi yang mendasarinya—kita mengetahui bahwa @@M3@@ merupakan penduga tak bias bagi @@M4@@, sehingga bias @@M5@@ sebagai penduga bagi @@M6@@ juga tidak positif, dan menjadi negatif kecuali kuadratnya konstan hampir pasti. Dalam kasus normal, karena @@M7@@ tidak melibatkan parameter yang tidak diketahui, statistik @@M8@@ merupakan penduga tak bias bagi @@M9@@. Selanjutnya kita tinjau simpangan baku sampel biasa @@M10@@.</p>',
    240: '    <p class="math">Untuk @@M1@@,</p>',
    248: '        <summary>Rincian:</summary>',
    249: '        <p>Ingat bahwa @@M1@@ memiliki <a href="../special/ChiSquare.html">distribusi khi-kuadrat</a> dengan @@M2@@ derajat kebebasan, sehingga @@M3@@ memiliki <a href="../special/ChiSquare.html#chi">distribusi khi</a> dengan @@M4@@ derajat kebebasan. Buktinya sama seperti pada <a href="#norm4" class="ref"></a>, tetapi dengan @@M5@@ menggantikan @@M6@@.</p>',
    253: '<p>Seperti @@M1@@, statistik @@M2@@ berbias negatif sebagai penduga bagi @@M3@@, tetapi tak bias secara asimtotik dan juga konsisten. Karena @@M4@@ tidak melibatkan parameter yang tidak diketahui, statistik @@M5@@ merupakan penduga tak bias bagi @@M6@@. Perhatikan pula bahwa, dari segi bias dan galat kuadrat rata-rata, @@M7@@ dengan ukuran sampel @@M8@@ berperilaku seperti @@M9@@ dengan ukuran sampel @@M10@@. Terakhir, kita tinjau @@M11@@, yaitu penduga metode momen bagi @@M12@@ ketika @@M13@@ tidak diketahui.</p>',
    256: '    <p class="math">Untuk @@M1@@,</p>',
    264: '        <summary>Rincian:</summary>',
    265: '        <p>Hasil-hasil tersebut segera mengikuti dari <a href="#norm5" class="ref"></a> karena @@M1@@.</p>',
    269: '<h4 id="ber">Distribusi Bernoulli</h4>',
    271: '<p>Ingat bahwa <dfn>variabel indikator</dfn> adalah variabel acak @@M1@@ yang hanya bernilai 0 dan 1. Distribusi @@M2@@ dikenal sebagai <dfn>distribusi Bernoulli</dfn>, dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Bernoulli.html\')" class="ancillary">Jacob Bernoulli</a>, dan memiliki fungsi kepadatan probabilitas @@M3@@ yang diberikan oleh',
    273: 'dengan @@M1@@ sebagai <dfn>parameter keberhasilan</dfn>. Rata-rata distribusi adalah @@M2@@ dan variansnya @@M3@@.</p>',
    275: '<p>Andaikan sekarang @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi Bernoulli dengan parameter keberhasilan @@M3@@ yang tidak diketahui. Karena rata-rata distribusi adalah @@M4@@, dari hasil umum pada <a href="#est" class="ref"></a> penduga metode momen bagi @@M5@@ adalah @@M6@@, yaitu rata-rata sampel. Dalam kasus ini, sampel @@M7@@ merupakan barisan <a href="../bernoulli/index.html">percobaan Bernoulli</a>, dan @@M8@@ memiliki versi terskala dari <a href="../bernoulli/Binomial.html">distribusi binomial</a> dengan parameter @@M9@@ dan @@M10@@:',
    277: 'Karena @@M1@@ untuk setiap @@M2@@, diperoleh @@M3@@ dan @@M4@@ untuk setiap @@M5@@. Jadi, setiap persamaan metode momen akan menghasilkan rata-rata sampel @@M6@@ sebagai penduga bagi @@M7@@. Walaupun sangat sederhana, ini merupakan penerapan penting karena percobaan Bernoulli muncul sebagai komponen dalam berbagai masalah pendugaan, seperti fungsi kepadatan probabilitas empiris dan fungsi distribusi empiris.</p>',
    279: '<h4 id="geo">Distribusi Geometrik</h4>',
    281: '<p><dfn>Distribusi geometrik</dfn> pada @@M1@@ dengan parameter keberhasilan @@M2@@ memiliki fungsi kepadatan probabilitas @@M3@@ yang diberikan oleh',
    283: '<a href="../bernoulli/Geometric.html">Distribusi geometrik</a> pada @@M1@@ memodelkan banyaknya percobaan yang diperlukan untuk memperoleh keberhasilan pertama dalam barisan <a href="../bernoulli/index.html">percobaan Bernoulli</a> dengan parameter keberhasilan @@M2@@. Rata-rata distribusinya adalah @@M3@@.</p>',
    286: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi geometrik pada @@M3@@ dengan parameter keberhasilan @@M4@@ yang tidak diketahui. Penduga metode momen bagi @@M5@@ adalah',
    289: '        <summary>Rincian:</summary>',
    290: '        <p>Persamaan metode momen bagi @@M1@@ adalah @@M2@@.</p>',
    294: '<p>Distribusi geometrik pada @@M1@@ dengan parameter keberhasilan @@M2@@ memiliki fungsi kepadatan probabilitas',
    296: 'Versi distribusi geometrik ini memodelkan banyaknya kegagalan sebelum keberhasilan pertama dalam barisan percobaan Bernoulli. Rata-rata distribusinya adalah @@M1@@.</p>',
    299: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi geometrik pada @@M3@@ dengan parameter @@M4@@ yang tidak diketahui. Penduga metode momen bagi @@M5@@ adalah',
    302: '        <summary>Rincian:</summary>',
    303: '        <p>Persamaan metode momen bagi @@M1@@ adalah @@M2@@.</p>',
    307: '<h4 id="o006.random.point.moments.section.negative-binomial">Distribusi Binomial Negatif</h4>',
    309: '<p>Secara lebih umum, <a href="../bernoulli/NegativeBinomial.html">distribusi binomial negatif</a> pada @@M1@@ dengan parameter bentuk @@M2@@ dan parameter keberhasilan @@M3@@ memiliki fungsi kepadatan probabilitas',
    311: 'Jika @@M1@@ bilangan bulat positif, distribusi ini memodelkan banyaknya kegagalan sebelum keberhasilan ke-@@M2@@ dalam barisan <a href="../bernoulli/index.html">percobaan Bernoulli</a> dengan parameter keberhasilan @@M3@@. Namun, definisi distribusi tersebut berlaku untuk setiap @@M4@@. Rata-ratanya @@M5@@ dan variansnya @@M6@@. Andaikan sekarang @@M7@@ merupakan sampel acak berukuran @@M8@@ dari distribusi binomial negatif pada @@M9@@ dengan parameter bentuk @@M10@@ dan parameter keberhasilan @@M11@@.</p>',
    314: '    <p class="math">Jika @@M1@@ dan @@M2@@ tidak diketahui, penduga metode momen yang bersesuaian, @@M3@@ dan @@M4@@, adalah',
    317: '        <summary>Rincian:</summary>',
    318: '        <p>Rumus di atas menghasilkan nilai dalam ruang parameter hanya ketika rata-rata sampel positif dan varians sampel berbias lebih besar daripada rata-rata sampel. Mencocokkan rata-rata dan varians distribusi dengan rata-rata dan varians sampel memberikan persamaan',
    323: '<p>Seperti biasa, hasilnya lebih sederhana ketika salah satu parameter diketahui.</p>',
    326: '    <p class="math">Andaikan @@M1@@ diketahui tetapi @@M2@@ tidak diketahui. Penduga metode momen @@M3@@ bagi @@M4@@ adalah',
    329: '        <summary>Rincian:</summary>',
    330: '        <p>Mencocokkan rata-rata distribusi dengan rata-rata sampel memberikan persamaan',
    336: '    <p class="math">Andaikan @@M1@@ tidak diketahui tetapi @@M2@@ diketahui. Penduga metode momen bagi @@M3@@ adalah',
    339: '        <li>@@M1@@, sehingga @@M2@@ tak bias.</li>',
    340: '        <li>@@M1@@, sehingga @@M2@@ konsisten.</li>',
    343: '        <summary>Rincian:</summary>',
    344: '        <p>Mencocokkan rata-rata distribusi dengan rata-rata sampel memberikan persamaan @@M1@@.</p>',
    346: '            <li>@@M1@@ dan @@M2@@.</li>',
    347: '            <li>@@M1@@ dan @@M2@@.</li>',
    352: '<h4 id="o006.random.point.moments.section.poisson">Distribusi Poisson</h4>',
    354: '<p><a href="../poisson/Poisson.html">Distribusi Poisson</a> dengan parameter @@M1@@ adalah distribusi diskret pada @@M2@@ dengan fungsi kepadatan probabilitas @@M3@@ yang diberikan oleh',
    356: 'Rata-rata dan variansnya sama-sama @@M1@@. Distribusi ini dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Poisson.html\')" class="ancillary">Simeon Poisson</a> dan banyak digunakan untuk memodelkan banyaknya <q>titik acak</q> dalam suatu wilayah waktu atau ruang, terutama dalam konteks <a href="../poisson/index.html">proses Poisson</a>. Parameter @@M2@@ sebanding dengan ukuran wilayah tersebut, dengan konstanta kesebandingannya berperan sebagai <dfn>laju</dfn> rata-rata titik-titik tersebut dalam waktu atau ruang.</p>',
    358: '<p>Andaikan sekarang @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi Poisson dengan parameter @@M3@@. Karena @@M4@@ adalah rata-ratanya, dari hasil umum pada <a href="#est" class="ref"></a> penduga metode momen bagi @@M5@@ adalah rata-rata sampel @@M6@@.</p>',
    360: '<h4 id="gam">Distribusi Gamma</h4>',
    362: '<p><a href="../special/Gamma.html">Distribusi gamma</a> dengan parameter bentuk @@M1@@ dan parameter skala @@M2@@ adalah distribusi kontinu pada @@M3@@ dengan fungsi kepadatan probabilitas @@M4@@ yang diberikan oleh',
    364: 'Fungsi kepadatan gamma mempunyai beragam bentuk, sehingga distribusi ini digunakan untuk memodelkan berbagai jenis variabel acak positif. Ketika @@M1@@, distribusi gamma juga dikenal sebagai <a href="../poisson/Gamma.html">distribusi Erlang</a>, dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Erlang.html\')" class="ancillary">Agner Erlang</a>. Dalam kasus ini, distribusi tersebut memodelkan waktu kedatangan ke-@@M2@@ dalam <a href="../poisson/index.html">proses Poisson</a>. Rata-ratanya @@M3@@ dan variansnya @@M4@@.</p>',
    366: '<p>Andaikan sekarang @@M1@@ merupakan sampel acak dari distribusi gamma dengan parameter bentuk @@M2@@ dan parameter skala @@M3@@. Untuk rumus dua parameter di bawah, diperlukan ukuran sampel sekurang-kurangnya dua dan varians sampel berbias yang positif; untuk sampel kontinu, syarat kedua berlaku hampir pasti.</p>',
    370: '    Andaikan @@M1@@ dan @@M2@@ keduanya tidak diketahui, serta @@M3@@ dan @@M4@@ adalah penduga metode momen yang bersesuaian. Maka',
    373: '        <summary>Rincian:</summary>',
    374: '        <p>Mencocokkan rata-rata dan varians distribusi dengan rata-rata dan varians sampel menghasilkan persamaan @@M1@@, @@M2@@. Dengan menyelesaikan sistem tersebut, diperoleh hasil di atas.</p>',
    378: '<p>Penduga metode momen bagi @@M1@@ dan @@M2@@ pada <a href="#gam1" class="ref"></a> merupakan fungsi nonlinear yang rumit dari rata-rata sampel @@M3@@ dan varians sampel @@M4@@. Karena itu, menghitung bias dan galat kuadrat rata-rata penduga-penduga ini merupakan masalah sulit yang tidak akan kita coba. Namun, kita dapat menilai mutu penduga secara empiris melalui simulasi.</p>',
    380: '<p>Ketika salah satu parameter diketahui, penduga metode momen bagi parameter lainnya jauh lebih sederhana.</p>',
    383: '    <p class="math">Andaikan @@M1@@ tidak diketahui, tetapi @@M2@@ diketahui. Penduga metode momen bagi @@M3@@ adalah',
    386: '        <li>@@M1@@, sehingga @@M2@@ tak bias.</li>',
    387: '        <li>@@M1@@, sehingga @@M2@@ konsisten.</li>',
    390: '        <summary>Rincian:</summary>',
    391: '        <p>Jika @@M1@@ diketahui, persamaan metode momen bagi @@M2@@ adalah @@M3@@. Dengan menyelesaikan persamaan tersebut, diperoleh rumus di atas. Selanjutnya, @@M4@@, sehingga @@M5@@ tak bias. Terakhir, @@M6@@.</p>',
    396: '    <p class="math">Andaikan @@M1@@ tidak diketahui, tetapi @@M2@@ diketahui. Penduga metode momen bagi @@M3@@ adalah',
    399: '        <li>@@M1@@, sehingga @@M2@@ tak bias.</li>',
    400: '        <li>@@M1@@, sehingga @@M2@@ konsisten.</li>',
    403: '        <summary>Rincian:</summary>',
    404: '        <p>Jika @@M1@@ diketahui, persamaan metode momen bagi @@M2@@ adalah @@M3@@. Dengan menyelesaikan persamaan tersebut, diperoleh rumus di atas. Selanjutnya, @@M4@@, sehingga @@M5@@ tak bias. Terakhir, @@M6@@.</p>',
    409: '    <p class="app">Jalankan <a href="JavaScript:openAncillary(\'../apps/GammaEstimate.html\')" class="ancillary">eksperimen pendugaan gamma</a> sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M1@@ serta parameter @@M2@@ dan @@M3@@. Amati bias empiris dan galat kuadrat rata-rata penduga @@M4@@, @@M5@@, @@M6@@, dan @@M7@@. Secara intuitif, penduga ketika salah satu parameter diketahui mungkin diharapkan bekerja lebih baik daripada penduga yang bersesuaian ketika kedua parameter tidak diketahui; selidiki dugaan ini secara empiris.</p>',
    412: '<h4 id="bet">Distribusi Beta</h4>',
    414: '<p><a href="../special/Beta.html">Distribusi beta</a> dengan parameter kiri @@M1@@ dan parameter kanan @@M2@@ adalah distribusi kontinu pada @@M3@@ dengan fungsi kepadatan probabilitas @@M4@@ yang diberikan oleh',
    416: 'Fungsi kepadatan beta mempunyai beragam bentuk, sehingga distribusi ini banyak digunakan untuk memodelkan probabilitas dan proporsi acak serta—setelah diskalakan dengan tepat—berbagai jenis variabel acak yang bernilai dalam interval terbatas. Dua momen pertamanya adalah',
    418: 'Andaikan sekarang @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi beta dengan parameter kiri @@M3@@ dan parameter kanan @@M4@@. Untuk rumus dua parameter di bawah, diperlukan ukuran sampel sekurang-kurangnya dua dan varians sampel berbias yang positif; untuk sampel kontinu, syarat kedua berlaku hampir pasti.</p>',
    421: '    <p class="math">Andaikan @@M1@@ dan @@M2@@ keduanya tidak diketahui, serta @@M3@@ dan @@M4@@ adalah penduga metode momen yang bersesuaian. Maka',
    424: '        <summary>Rincian:</summary>',
    425: '        <p>Persamaan metode momen bagi @@M1@@ dan @@M2@@ adalah',
    427: '        Dengan menyelesaikan sistem tersebut, diperoleh hasil di atas.</p>',
    431: '<p>Penduga metode momen bagi @@M1@@ dan @@M2@@ pada <a href="#bet1" class="ref"></a> merupakan fungsi nonlinear yang rumit dari momen sampel @@M3@@ dan @@M4@@. Karena itu, kita tidak akan mencoba menentukan bias dan galat kuadrat rata-ratanya secara analitis, tetapi kita dapat menyelidikinya secara empiris melalui simulasi.</p>',
    434: '    <p class="math">Andaikan @@M1@@ tidak diketahui, tetapi @@M2@@ diketahui. Misalkan @@M3@@ adalah penduga metode momen bagi @@M4@@. Maka',
    437: '        <summary>Rincian:</summary>',
    438: '        <p>Jika @@M1@@ diketahui, persamaan metode momen bagi @@M2@@ sebagai penduga @@M3@@ adalah @@M4@@. Dengan menyelesaikan persamaan tersebut terhadap @@M5@@, diperoleh rumus di atas.</p>',
    443: '    <p class="math">Andaikan @@M1@@ tidak diketahui, tetapi @@M2@@ diketahui. Misalkan @@M3@@ adalah penduga metode momen bagi @@M4@@. Maka',
    446: '        <summary>Rincian:</summary>',
    447: '        <p>Jika @@M1@@ diketahui, persamaan metode momen bagi @@M2@@ sebagai penduga @@M3@@ adalah @@M4@@. Dengan menyelesaikan persamaan tersebut terhadap @@M5@@, diperoleh rumus di atas.</p>',
    452: '    <p class="app">Jalankan <a href="JavaScript:openAncillary(\'../apps/BetaEstimate.html\')" class="ancillary">eksperimen pendugaan beta</a> sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M1@@ serta parameter @@M2@@ dan @@M3@@. Amati bias empiris dan galat kuadrat rata-rata penduga @@M4@@, @@M5@@, @@M6@@, dan @@M7@@. Secara intuitif, penduga ketika salah satu parameter diketahui mungkin diharapkan bekerja lebih baik daripada penduga yang bersesuaian ketika kedua parameter tidak diketahui; selidiki dugaan ini secara empiris.</p>',
    455: '<p>Latihan <a href="#bet2" class="ref"></a> berikut membahas distribusi yang hanya memiliki satu parameter, tetapi persamaan momen kedua dari metode momen diperlukan untuk menurunkan penduganya.</p>',
    458: '    <p class="math">Andaikan @@M1@@ merupakan sampel acak dari distribusi beta <dfn>simetris</dfn>, dengan parameter kiri dan kanan sama dengan nilai tak diketahui @@M2@@. Penduga metode momen bagi @@M3@@ adalah',
    461: '        <summary>Rincian:</summary>',
    462: '        <p>Perhatikan bahwa rata-rata @@M1@@ dari distribusi simetris adalah @@M2@@, tidak bergantung pada @@M3@@, sehingga persamaan pertama metode momen tidak berguna. Namun, mencocokkan momen kedua distribusi dengan momen kedua sampel menghasilkan persamaan',
    464: '        Dengan menyelesaikan persamaan tersebut, diperoleh hasil di atas. Solusi positif hanya ada ketika momen sampel kedua lebih besar daripada seperempat dan lebih kecil daripada setengah; di luar rentang itu, persamaan momen tidak mempunyai solusi positif.</p>',
    468: '<h4 id="par">Distribusi Pareto</h4>',
    470: '<p><a href="../special/Pareto.html">Distribusi Pareto</a> dengan parameter bentuk @@M1@@ dan parameter skala @@M2@@ adalah distribusi kontinu pada @@M3@@ dengan fungsi kepadatan probabilitas @@M4@@ yang diberikan oleh',
    472: 'Distribusi Pareto dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Pareto.html\')" class="ancillary">Vilfredo Pareto</a> dan merupakan distribusi yang sangat miring serta <dfn>berekor berat</dfn>. Distribusi ini sering digunakan untuk memodelkan pendapatan dan jenis variabel acak positif tertentu lainnya. Jika @@M1@@, dua momen pertama distribusi Pareto adalah',
    474: 'Andaikan sekarang @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi Pareto dengan parameter bentuk @@M3@@ dan parameter skala @@M4@@. Untuk rumus dua parameter di bawah, diperlukan ukuran sampel sekurang-kurangnya dua dan varians sampel berbias yang positif; untuk sampel kontinu, syarat kedua berlaku hampir pasti.</p>',
    477: '    <p class="math">Andaikan @@M1@@ dan @@M2@@ keduanya tidak diketahui, serta @@M3@@ dan @@M4@@ adalah penduga metode momen yang bersesuaian. Maka',
    483: '        <summary>Rincian:</summary>',
    484: '        <p>Persamaan metode momen bagi @@M1@@ dan @@M2@@ adalah',
    489: '        Dengan menyelesaikan sistem tersebut terhadap @@M1@@ dan @@M2@@, diperoleh hasil di atas.</p>',
    493: '<p>Penduga metode momen pada contoh <a href="#par1" class="ref"></a> merupakan fungsi nonlinear yang rumit dari @@M1@@ dan @@M2@@, sehingga menghitung bias dan galat kuadrat rata-ratanya sulit. Sebagai gantinya, kita dapat menyelidiki bias dan galat kuadrat rata-rata secara empiris melalui simulasi.</p>',
    496: '    <p class="app">Jalankan <a href="JavaScript:openAncillary(\'../apps/ParetoEstimate.html\')" class="ancillary">eksperimen pendugaan Pareto</a> sebanyak 1.000 kali untuk beberapa nilai ukuran sampel @@M1@@ serta parameter @@M2@@ dan @@M3@@. Amati bias empiris dan galat kuadrat rata-rata penduga @@M4@@ dan @@M5@@.</p>',
    499: '<p>Ketika salah satu parameter diketahui, penduga metode momen bagi parameter lainnya lebih sederhana.</p>',
    502: '    <p class="math">Andaikan @@M1@@ tidak diketahui, tetapi @@M2@@ diketahui. Misalkan @@M3@@ adalah penduga metode momen bagi @@M4@@. Maka',
    505: '        <summary>Rincian:</summary>',
    506: '        <p>Jika @@M1@@ diketahui, persamaan metode momen bagi @@M2@@ sebagai penduga @@M3@@ adalah @@M4@@. Dengan menyelesaikan persamaan tersebut terhadap @@M5@@, diperoleh rumus di atas. Karena model pada bagian ini mensyaratkan parameter bentuk lebih besar daripada dua, hasil mentah ini juga harus diperiksa terhadap syarat tersebut.</p>',
    511: '    <p class="math">Andaikan @@M1@@ tidak diketahui, tetapi @@M2@@ diketahui. Misalkan @@M3@@ adalah penduga metode momen bagi @@M4@@. Maka',
    514: '        <li>@@M1@@, sehingga @@M2@@ tak bias.</li>',
    515: '        <li>@@M1@@, sehingga @@M2@@ konsisten.</li>',
    518: '        <summary>Rincian:</summary>',
    519: '        <p>Jika @@M1@@ diketahui, persamaan metode momen bagi @@M2@@ sebagai penduga @@M3@@ adalah @@M4@@. Dengan menyelesaikan persamaan tersebut terhadap @@M5@@, diperoleh rumus di atas. Selanjutnya, @@M6@@, sehingga @@M7@@ tak bias. Terakhir, @@M8@@.</p>',
    523: '<h4 id="uni">Distribusi Seragam</h4>',
    525: '<p><a href="../special/UniformContinuous.html">Distribusi seragam kontinu</a> pada interval tertutup yang ujung kirinya adalah parameter lokasi dan panjangnya adalah parameter skala, dengan parameter lokasi @@M1@@ dan parameter skala @@M2@@, memiliki fungsi kepadatan probabilitas @@M3@@ yang diberikan oleh',
    527: 'Distribusi tersebut memodelkan suatu titik yang dipilih <q>secara acak</q> dari interval @@M1@@. Rata-rata distribusinya @@M2@@ dan variansnya @@M3@@. Andaikan sekarang @@M4@@ merupakan sampel acak berukuran @@M5@@ dari distribusi seragam. Untuk rumus dua parameter di bawah, diperlukan ukuran sampel sekurang-kurangnya dua dan varians sampel berbias yang positif; untuk sampel kontinu, syarat kedua berlaku hampir pasti.</p>',
    530: '    <p class="math">Andaikan @@M1@@ dan @@M2@@ keduanya tidak diketahui, serta @@M3@@ dan @@M4@@ menyatakan penduga metode momen yang bersesuaian. Maka',
    533: '        <summary>Rincian:</summary>',
    534: '        <p>Mencocokkan rata-rata dan varians distribusi dengan rata-rata dan varians sampel menghasilkan persamaan @@M1@@ dan @@M2@@. Dengan menyelesaikan sistem tersebut, diperoleh hasil di atas.</p>',
    538: '<p>Seperti biasa, kita memperoleh hasil yang lebih sederhana ketika salah satu parameter diketahui.</p>',
    541: '    <p class="math">Andaikan @@M1@@ diketahui dan @@M2@@ tidak diketahui, serta @@M3@@ menyatakan penduga metode momen bagi @@M4@@. Maka',
    544: '        <li>@@M1@@, sehingga @@M2@@ tak bias.</li>',
    545: '        <li>@@M1@@, sehingga @@M2@@ konsisten.</li>',
    548: '        <summary>Rincian:</summary>',
    549: '        <p>Mencocokkan rata-rata distribusi dengan rata-rata sampel menghasilkan persamaan @@M1@@. Dengan menyelesaikan persamaan tersebut, diperoleh rumus di atas.</p>',
    551: '            <li>@@M1@@.</li>',
    552: '            <li>@@M1@@.</li>',
    558: '    <p class="math">Andaikan @@M1@@ diketahui dan @@M2@@ tidak diketahui, serta @@M3@@ menyatakan penduga metode momen bagi @@M4@@. Maka',
    561: '        <li>@@M1@@, sehingga @@M2@@ tak bias.</li>',
    562: '        <li>@@M1@@, sehingga @@M2@@ konsisten.</li>',
    565: '        <summary>Rincian:</summary>',
    566: '        <p>Mencocokkan rata-rata distribusi dengan rata-rata sampel menghasilkan persamaan @@M1@@. Dengan menyelesaikan persamaan tersebut, diperoleh rumus di atas.</p>',
    568: '            <li>@@M1@@.</li>',
    569: '            <li>@@M1@@.</li>',
    574: '<h4 id="hyp">Model Hipergeometrik</h4>',
    576: '<p>Asumsi dasar metode momen adalah bahwa barisan variabel acak teramati @@M1@@ merupakan sampel acak dari suatu distribusi. Namun, setidaknya dalam beberapa kasus, metode ini tetap masuk akal ketika variabel-variabel berdistribusi identik tetapi saling bergantung. Dalam <dfn>model hipergeometrik</dfn>, kita memiliki populasi berisi @@M2@@ objek, dengan @@M3@@ objek <dfn>tipe 1</dfn> dan @@M4@@ objek sisanya <dfn>tipe 0</dfn>. Parameter @@M5@@, yaitu <dfn>ukuran populasi</dfn>, adalah bilangan bulat positif. Parameter @@M6@@, yaitu <dfn>jumlah objek tipe 1</dfn>, adalah bilangan bulat taknegatif dengan @@M7@@. Keduanya merupakan parameter dasar, dan biasanya salah satu atau keduanya tidak diketahui. Berikut beberapa contoh umum.</p>',
    579: '    <li>Objeknya adalah perangkat, yang diklasifikasikan sebagai <dfn>baik</dfn> atau <dfn>cacat</dfn>.</li>',
    580: '    <li>Objeknya adalah orang, yang diklasifikasikan sebagai <dfn>perempuan</dfn> atau <dfn>laki-laki</dfn>.</li>',
    581: '    <li>Objeknya adalah pemilih, yang diklasifikasikan sebagai <dfn>pendukung</dfn> atau <dfn>penentang</dfn> kandidat tertentu.</li>',
    582: '    <li>Objeknya adalah satwa liar dari jenis tertentu, yang <dfn>ditandai</dfn> atau <dfn>tidak ditandai</dfn>.</li>',
    585: '<p>Kita mengambil sampel @@M1@@ objek secara acak dari populasi, tanpa pengembalian; ukuran sampel diasumsikan sekurang-kurangnya satu dan tidak melebihi ukuran populasi. Misalkan @@M2@@ adalah tipe objek ke-@@M3@@ yang terpilih, sehingga barisan variabel teramati adalah @@M4@@. Variabel-variabel ini merupakan indikator yang berdistribusi identik, dengan @@M5@@ untuk setiap @@M6@@, tetapi saling bergantung karena pensampelan dilakukan tanpa pengembalian. Banyaknya objek tipe 1 dalam sampel adalah @@M7@@. Statistik ini memiliki <a href="../urn/Hypergeometric.html">distribusi hipergeometrik</a> dengan parameter @@M8@@, @@M9@@, dan @@M10@@, serta fungsi kepadatan probabilitas yang diberikan oleh',
    589: '    <p class="math">Seperti di atas, misalkan @@M1@@ adalah variabel teramati dalam model hipergeometrik dengan parameter @@M2@@ dan @@M3@@. Maka</p>',
    591: '        <li>Penduga metode momen bagi @@M1@@ adalah @@M2@@, yaitu rata-rata sampel.</li>',
    592: '        <li>Penduga metode momen bagi @@M1@@ ketika @@M2@@ diketahui adalah @@M3@@.</li>',
    593: '        <li>Penduga metode momen bagi @@M1@@ ketika @@M2@@ diketahui adalah @@M3@@ jika @@M4@@.</li>',
    596: '        <summary>Rincian:</summary>',
    597: '        <p>Semua hasil ini langsung mengikuti fakta bahwa @@M1@@. Penduga bagi parameter bilangan bulat di atas adalah nilai mentah real dari metode momen; jika hasilnya harus berada dalam ruang parameter bilangan bulat, diperlukan aturan proyeksi atau pembulatan terkendala yang dinyatakan secara terpisah.</p>',
    601: '<p>Dalam contoh pemilih (3) di atas, biasanya @@M1@@ dan @@M2@@ keduanya tidak diketahui, tetapi kita hanya tertarik menduga rasio @@M3@@. Dalam contoh keandalan (1), biasanya kita mengetahui @@M4@@ dan tertarik menduga @@M5@@. Dalam contoh satwa liar (4), biasanya kita mengetahui @@M6@@ dan tertarik menduga @@M7@@. Contoh ini dikenal sebagai model <dfn>tangkap–tangkap kembali</dfn>.</p>',
    603: '<p>Jelas terdapat hubungan erat antara model hipergeometrik dan <a href="#ber">model percobaan Bernoulli</a> pada subbagian di atas. Jika pensampelan dilakukan <em>dengan</em> pengembalian, model percobaan Bernoulli berlaku, bukan model hipergeometrik. Selain itu, jika ukuran populasi @@M1@@ besar dibandingkan ukuran sampel @@M2@@, model percobaan Bernoulli memberikan hampiran yang baik bagi model hipergeometrik.</p>',
    608: '        <li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>',
    609: '        <li class="child"><a href="Estimators.html" title="Penduga">1</a></li>',
    611: '        <li class="child"><a href="Likelihood.html" title="Kemungkinan Maksimum">3</a></li>',
    612: '        <li class="child"><a href="Bayes.html" title="Penduga Bayes">4</a></li>',
    613: '        <li class="child"><a href="Unbiased.html" title="Penduga Tak Bias Terbaik">5</a></li>',
    614: '        <li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancilar">6</a></li>',
    615: '        <li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>',
    616: '        <li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>',
    619: '        <li class="sister"><a href="JavaScript:openAncillary(\'../apps/index.html\')" class="ancillary">Aplikasi</a></li>',
    620: '        <li class="sister"><a href="JavaScript:openAncillary(\'../data/index.html\')" class="ancillary">Himpunan Data</a></li>',
    621: '        <li class="child"><a href="JavaScript:openAncillary(\'../biographies/index.html\')" class="ancillary">Biografi</a></li>',
}

# Exact bounded repairs; every other delimited TeX span is authority-identical.
MATH_FIXES: dict[int, tuple[tuple[str, str], ...]] = {
    133: ((r"\( \W_n^2 \)", r"\( W_n^2 \)"),),
    181: ((r"\(n \in \{2, 3, \ldots, \}\)", r"\(n \in \{2, 3, \ldots\}\)"),),
    346: ((r"\( E(U_p) = \frac{p}{1 - p} \E(M)\)", r"\( \E(U_p) = \frac{p}{1 - p} \E(M)\)"),),
    347: ((r"\( \var(M) = \frac{1}{n} \var(X) = \frac{1 - p}{n p^2} \)", r"\( \var(M) = \frac{1}{n} \var(X) = \frac{k(1 - p)}{n p^2} \)"),),
    400: ((r"\( \var(V_k) = b^2 / k n \)", r"\( \var(V_k) = \frac{b^2}{k n} \)"),),
    404: ((r"\(\var(V_k) = \var(M) / k^2 = k b ^2 / (n k^2) = b^2 / k n\)", r"\(\var(V_k) = \var(M) / k^2 = k b ^2 / (n k^2) = \frac{b^2}{k n}\)"),),
    459: ((r"\[ U = \frac{2 M^{(2)}}{1 - 4 M^{(2)}} \]", r"\[ U = \frac{1 - 2 M^{(2)}}{4 M^{(2)} - 1} \]"),),
    470: ((r"\( (b, \infty) \)", r"\( [b, \infty) \)"),),
    531: ((r"\[ U = 2 M - \sqrt{3} T, \quad V = 2 \sqrt{3} T \]", r"\[ U = M - \sqrt{3} T, \quad V = 2 \sqrt{3} T \]"),),
    544: ((r"\( V \)", r"\( V_a \)"),),
    585: ((r"\( P(X_i = 1) = r / N \)", r"\( \P(X_i = 1) = r / N \)"),),
    586: ((r"\[ P(Y = y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, N - n + r\}, \ldots, \min\{n, r\}\} \]", r"\[ \P(Y = y) = \frac{\binom{r}{y} \binom{N - r}{n - y}}{\binom{N}{n}} = \binom{n}{y} \frac{r^{(y)} (N - r)^{(n - y)}}{N^{(n)}}, \quad y \in \{\max\{0, n - N + r\}, \ldots, \min\{n, r\}\} \]"),),
}

STABLE_IDS: dict[int, tuple[str, str]] = {
    57: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.distribution-moments">'),
    64: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.sample-moments">'),
    85: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.mean-estimator">'),
    102: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.biased-sample-variance">'),
    124: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.known-mean-variance">'),
    153: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.two-parameter-equivalence">'),
    203: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.normal-variance-simulation">'),
    285: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.geometric-positive-support">'),
    298: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.geometric-zero-support">'),
    313: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.negative-binomial-both-unknown">'),
    325: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.negative-binomial-known-shape">'),
    335: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.negative-binomial-known-success">'),
    382: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.gamma-known-scale">'),
    395: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.gamma-known-shape">'),
    408: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.gamma-simulation">'),
    433: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.beta-known-right">'),
    442: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.beta-known-left">'),
    451: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.beta-simulation">'),
    495: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.pareto-simulation">'),
    501: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.pareto-known-scale">'),
    510: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.pareto-known-shape">'),
    529: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.uniform-both-unknown">'),
    540: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.uniform-known-location">'),
    557: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.uniform-known-scale">'),
    588: ('<div class="unit">', '<div class="unit" id="o006.random.point.moments.unit.hypergeometric-estimators">'),
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
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/sample/LLN.html": "../sample/LLN.html",
    "https://www.randomservices.org/random/sample/CLT.html": "../sample/CLT.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
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
    for line_number in (218, 240, 493):
        if not lines[line_number - 1].rstrip("\r\n").endswith("</p>"):
            raise RuntimeError(f"line {line_number}: paragraph repair missing")
    ending = "\r\n" if lines[585].endswith("\r\n") else "\n"
    if lines[585].removesuffix(ending).endswith("</p>"):
        raise RuntimeError("line 586 unexpectedly already closes paragraph")
    lines[585] = lines[585].removesuffix(ending) + "</p>" + ending
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
        'lang="en"', "JavaScript:openAncillary", "Expand Details",
        "Contract Details", ">Details:<", ">Point Estimation<",
        ">The Method of Moments<", ">Basic Theory<",
        ">Special Distributions<", ">Apps<", ">Data Sets<", "> Biographies<",
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
