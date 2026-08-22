#!/usr/bin/env python3
"""Create the bounded id-ID Bayesian Estimation target.

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
SOURCE = ROOT / "authority" / "upstream" / "random" / "point" / "Bayes.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "point" / "Bayes.html"
SOURCE_URL = "https://www.randomservices.org/random/point/Bayes.html"
SOURCE_SHA256 = "96904b1fd4ab905bbffa62bd5cc0d965b3c969e543a983124e968718ed25d550"
EXPECTED_SOURCE_LINES = 577
MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)
TOKEN_RE = re.compile(r"@@M([1-9][0-9]*)@@")


# Only reader-facing rows are replaced. Formula-only rows remain exact source
# bytes unless listed in MATH_FIXES.
T: dict[int, str] = {
    2: '<html lang="id-ID">',
    6: "    <title>Penduga Bayes</title>",
    9: '    <meta name="keywords" content="probabilitas, statistika, pendugaan titik, penduga Bayes, teorema Bayes, keluarga konjugat, distribusi Bernoulli, distribusi geometrik, distribusi Poisson, distribusi normal, distribusi beta, distribusi Pareto">',
    36: '        <li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>',
    37: '        <li class="child"><a href="Estimators.html" title="Penduga">1</a></li>',
    38: '        <li class="child"><a href="Moments.html" title="Metode Momen">2</a></li>',
    39: '        <li class="child"><a href="Likelihood.html" title="Kemungkinan Maksimum">3</a></li>',
    41: '        <li class="child"><a href="Unbiased.html" title="Penduga Tak Bias Terbaik">5</a></li>',
    42: '        <li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancilar">6</a></li>',
    43: '        <li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>',
    44: '        <li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>',
    46: '    <h2 id="o006.random.point.bayes.page">4. Pendugaan Bayes</h2>',
    49: '<h3 id="o006.random.point.bayes.section.basic-theory">Teori Dasar</h3>',
    51: '<h4 id="o006.random.point.bayes.section.general-method">Metode Umum</h4>',
    53: '<p>Andaikan kembali bahwa kita mempunyai <a href="../prob/Probability.html">variabel acak</a> teramati @@M1@@ untuk suatu <a href="../prob/Experiments.html">eksperimen acak</a>, dengan nilai dalam himpunan @@M2@@. Andaikan pula bahwa distribusi @@M3@@ bergantung pada parameter @@M4@@ yang nilainya berada dalam himpunan @@M5@@. Variabel data @@M6@@ hampir selalu bernilai vektor, sehingga biasanya @@M7@@ untuk suatu @@M8@@. Menurut sifat himpunan sampel @@M9@@, distribusi @@M10@@ dapat berupa <a href="../dist/Discrete.html">diskret</a> atau <a href="../dist/Continuous.html">kontinu</a>. Parameter @@M11@@ juga dapat bernilai vektor, sehingga biasanya @@M12@@ untuk suatu @@M13@@.</p>',
    55: '<p>Dalam <dfn>analisis Bayes</dfn>, yang dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Bayes.html\')" class="ancillary">Thomas Bayes</a>, parameter deterministik tetapi tak diketahui @@M1@@ dimodelkan dengan variabel acak @@M2@@ yang mempunyai distribusi tertentu pada himpunan parameter @@M3@@. Menurut sifat himpunan itu, distribusinya dapat diskret atau kontinu. Distribusi tersebut disebut <dfn>distribusi prior</dfn> bagi @@M4@@ dan dimaksudkan untuk menyatakan pengetahuan awal tentang parameter @@M5@@ <em>sebelum</em> data dikumpulkan. Setelah mengamati @@M6@@, kita menggunakan <a href="../dist/Conditional.html#bay">teorema Bayes</a> untuk menghitung distribusi bersyarat @@M7@@ dengan syarat @@M8@@. Distribusi ini disebut <dfn>distribusi posterior</dfn> bagi @@M9@@: distribusi yang diperbarui berdasarkan informasi dalam data. Berikut uraian matematisnya dalam istilah fungsi kepadatan probabilitas.</p>',
    58: '    <p class="math">Andaikan <dfn>distribusi prior</dfn> bagi @@M1@@ pada @@M2@@ mempunyai fungsi kepadatan probabilitas @@M3@@, dan, bersyarat pada @@M4@@, fungsi kepadatan probabilitas bersyarat @@M5@@ pada @@M6@@ adalah @@M7@@. Untuk data yang mempunyai kepadatan marginal positif dan berhingga, fungsi kepadatan probabilitas <dfn>distribusi posterior</dfn> bagi @@M8@@ dengan syarat @@M9@@ adalah',
    60: '    dengan fungsi pada penyebut didefinisikan sebagai berikut, masing-masing untuk kasus diskret dan kontinu:',
    66: '        <summary>Rincian:</summary>',
    67: '        <p>Ini hanyalah teorema Bayes dengan istilah baru. Ingat bahwa <a href="../dist/Joint.html">fungsi kepadatan probabilitas gabungan</a> bagi @@M1@@ adalah pemetaan pada @@M2@@ yang diberikan oleh',
    69: '        Fungsi pada penyebut adalah fungsi kepadatan probabilitas marginal bagi @@M1@@. Jadi, menurut definisi, @@M2@@ untuk @@M3@@ merupakan fungsi kepadatan probabilitas bersyarat bagi @@M4@@ dengan syarat @@M5@@.</p>',
    73: '<p>Untuk @@M1@@ yang memenuhi syarat kepadatan marginal positif dan berhingga di atas, @@M2@@ hanyalah <em>konstanta normalisasi</em> bagi fungsi @@M3@@. Kita tidak selalu perlu menghitung @@M4@@ secara eksplisit apabila bentuk fungsional @@M5@@ dapat dikenali sebagai bentuk suatu distribusi yang diketahui. Hal itu memang terjadi pada beberapa contoh di bawah.</p>',
    75: '<p>Jika himpunan parameter @@M1@@ mempunyai ukuran @@M2@@ yang positif dan berhingga—ukuran cacah dalam kasus diskret atau ukuran Lebesgue dalam kasus kontinu—salah satu pilihan prior adalah <a href="../special/Uniform.html">distribusi seragam</a> pada @@M3@@, dengan fungsi kepadatan probabilitas @@M4@@ untuk @@M5@@. Dalam parameterisasi dan ukuran acuan yang dipilih, prior datar ini sering disebut prior <dfn>noninformatif</dfn>; penamaan tersebut tidak invarian terhadap perubahan parameter dan tidak secara harfiah berarti ketiadaan pengetahuan.</p>',
    77: '<h4 id="o006.random.point.bayes.section.random-samples">Sampel Acak</h4>',
    79: '<p>Kasus khusus yang penting terjadi ketika @@M1@@ merupakan <a href="../sample/Introduction.html">sampel acak</a> berukuran @@M2@@ dari distribusi suatu variabel dasar @@M3@@. Secara khusus, andaikan @@M4@@ bernilai dalam himpunan @@M5@@ dan mempunyai fungsi kepadatan probabilitas @@M6@@ bersyarat pada @@M7@@. Dalam hal ini, @@M8@@ dan fungsi kepadatan probabilitas @@M9@@ bagi @@M10@@ bersyarat pada @@M11@@ adalah',
    82: '<h4 id="o006.random.point.bayes.section.real-parameters">Parameter Riil</h4>',
    84: '<p>Andaikan @@M1@@ merupakan parameter bernilai riil, sehingga @@M2@@. Berikut definisi utama untuk fungsi kerugian yang dipakai pada halaman ini.</p>',
    87: '    <p class="math">Dengan syarat momen posterior kedua berhingga, <a href="../expect/Conditional.html">nilai harapan bersyarat</a> @@M1@@ merupakan <dfn>penduga Bayes</dfn> bagi @@M2@@ di bawah fungsi kerugian kuadrat.</p>',
    89: '        <li>Jika @@M1@@ mempunyai distribusi diskret pada @@M2@@, maka',
    92: '        <li>Jika @@M1@@ mempunyai distribusi kontinu pada @@M2@@, maka',
    98: '<p>Jika parameter mempunyai momen kedua berhingga di bawah distribusi gabungan prior-prediktif, @@M1@@ merupakan fungsi dari @@M2@@ dan, di antara semua fungsi @@M3@@, paling dekat dengan @@M4@@ dalam pengertian kuadrat rata-rata tak bersyarat. Setelah data dikumpulkan dan @@M5@@ teramati, <dfn>dugaan Bayes</dfn> bagi @@M6@@ adalah @@M7@@. Seperti biasa, istilah <em>penduga</em> merujuk pada variabel acak sebelum data dikumpulkan, sedangkan <em>dugaan</em> merujuk pada nilai teramati setelah data dikumpulkan. Definisi <a href="Estimators.html">bias dan galat kuadrat rata-rata</a> tetap seperti sebelumnya, tetapi kini bersyarat pada @@M8@@.</p>',
    101: '    <p class="math">Andaikan @@M1@@ merupakan penduga Bayes bagi @@M2@@.</p>',
    103: '        <li><dfn>Bias</dfn> @@M1@@ adalah @@M2@@ untuk @@M3@@.</li>',
    104: '        <li><dfn>Galat kuadrat rata-rata</dfn> @@M1@@ adalah @@M2@@ untuk @@M3@@.</li>',
    108: '<p>Seperti sebelumnya, @@M1@@ dan @@M2@@. Andaikan sekarang variabel acak @@M3@@ diamati secara berurutan, dan untuk setiap @@M4@@ kita menghitung penduga Bayes @@M5@@ bagi @@M6@@ berdasarkan @@M7@@. Kasus yang paling lazim kembali berupa pensampelan dari suatu distribusi, sehingga barisan itu saling bebas dan berdistribusi identik bersyarat pada @@M8@@. Sifat asimtotik alaminya adalah sebagai berikut.</p>',
    111: '    <p class="math">Misalkan @@M1@@ merupakan barisan penduga Bayes bagi @@M2@@ seperti di atas.</p>',
    113: '        <li>@@M1@@ <dfn>tak bias secara asimtotik</dfn> jika @@M2@@ ketika @@M3@@ untuk setiap @@M4@@.</li>',
    114: '        <li>@@M1@@ <dfn>konsisten dalam kuadrat rata-rata</dfn> jika @@M2@@ ketika @@M3@@ untuk setiap @@M4@@.</li>',
    118: '<p>Kita sering tidak dapat membentuk penduga Bayes yang tak bias, tetapi berharap penduga tersebut setidaknya tak bias secara asimtotik dan konsisten. Dengan syarat parameter terintegralkan, barisan penduga Bayes @@M1@@—yakni harapan bersyarat terhadap filtrasi yang dibangkitkan oleh data—merupakan <a href="../martingales/index.html">martingal</a> di bawah distribusi gabungan prior-prediktif. Teori martingal menyediakan perangkat yang kuat untuk mempelajari penduga ini.</p>',
    120: '<p>Dari sudut pandang Bayes, distribusi posterior @@M1@@ dengan syarat data @@M2@@ merupakan objek utama; dugaan titik bagi @@M3@@ yang diturunkan darinya bersifat sekunder. Secara khusus, fungsi @@M4@@ adalah risiko posterior di bawah kerugian kuadrat dan, seperti telah dicatat, diminimumkan pada @@M5@@. Kerugian kuadrat bukan satu-satunya <dfn>fungsi kerugian</dfn> yang dapat dipakai, meskipun hanya itulah yang dibahas di halaman ini. Untuk kerugian absolut, fungsi @@M6@@ adalah risiko posterior dan <a href="../expect/Spaces.html#cen">diketahui</a> diminimumkan pada setiap median distribusi posterior.</p>',
    122: '<h4 id="o006.random.point.bayes.section.conjugate-families">Keluarga Konjugat</h4>',
    124: '<p>Sering kali distribusi prior @@M1@@ sendiri merupakan anggota suatu keluarga parametrik, dengan parameter yang dipilih untuk menyatakan pengetahuan awal tentang @@M2@@. Dalam banyak kasus penting, keluarga itu dapat dipilih sehingga distribusi posterior @@M3@@ dengan syarat @@M4@@ tetap berada dalam keluarga yang sama untuk setiap @@M5@@. Dalam keadaan tersebut, keluarga distribusi @@M6@@ dikatakan <dfn>konjugat</dfn> terhadap keluarga distribusi @@M7@@. Keluarga konjugat menguntungkan dari segi komputasi karena distribusi posterior sering dapat dihitung melalui rumus sederhana pada parameter keluarga tanpa menerapkan teorema Bayes secara langsung. Demikian pula, jika parameternya bernilai riil, penduga Bayes sering dapat dihitung dari rumus sederhana pada parameter keluarga konjugat.</p>',
    126: '<h3 id="o006.random.point.bayes.section.special-distributions">Distribusi Khusus</h3>',
    128: '<h4 id="ber">Distribusi Bernoulli</h4>',
    130: '<p>Andaikan @@M1@@ merupakan barisan variabel saling bebas, masing-masing berdistribusi <a href="../bernoulli/Introduction.html">Bernoulli</a> dengan parameter keberhasilan tak diketahui @@M2@@. Singkatnya, @@M3@@ merupakan barisan percobaan Bernoulli bersyarat pada @@M4@@. Dalam istilah keandalan yang lazim, @@M5@@ berarti berhasil pada percobaan ke-@@M6@@ dan @@M7@@ berarti gagal pada percobaan ke-@@M8@@. Bersyarat pada @@M9@@, fungsi kepadatan probabilitas Bernoulli adalah',
    132: 'Perhatikan bahwa banyaknya keberhasilan pada @@M1@@ percobaan pertama adalah @@M2@@. Bersyarat pada @@M3@@, variabel acak @@M4@@ mempunyai <a href="../bernoulli/Binomial.html">distribusi binomial</a> dengan parameter @@M5@@ dan @@M6@@.</p>',
    134: '<p>Andaikan sekarang @@M1@@ dimodelkan dengan variabel acak @@M2@@ yang mempunyai <a href="../special/Beta.html">distribusi beta</a> prior dengan parameter kiri @@M3@@ dan parameter kanan @@M4@@. Nilai @@M5@@ dan @@M6@@ dipilih untuk menyatakan informasi awal tentang @@M7@@. Jadi, @@M8@@ mempunyai fungsi kepadatan probabilitas',
    136: 'dan mempunyai rata-rata @@M1@@. Misalnya, jika kita tidak memiliki informasi khusus tentang @@M2@@, kita dapat mengambil @@M3@@ sehingga distribusi prior seragam pada ruang parameter @@M4@@; pilihan datar dalam parameterisasi ini sering disebut prior noninformatif, dengan batas penafsiran yang telah dijelaskan di atas. Sebaliknya, jika @@M5@@ diyakini sekitar @@M6@@, kita dapat mengambil @@M7@@ dan @@M8@@ sehingga prior tersebut unimodal dengan rata-rata @@M9@@. Sebagai proses acak, barisan @@M10@@ dengan @@M11@@ yang diacak menurut @@M12@@ disebut <a href="../bernoulli/BetaBernoulli.html">proses beta–Bernoulli</a> dan menarik untuk dipelajari tersendiri di luar konteks pendugaan Bayes.</p>',
    139: '    <p class="math">Untuk @@M1@@, distribusi posterior @@M2@@ dengan syarat @@M3@@ adalah beta dengan parameter kiri @@M4@@ dan parameter kanan @@M5@@.</p>',
    141: '        <summary>Rincian:</summary>',
    142: '        <p>Tetapkan @@M1@@. Misalkan @@M2@@ dan @@M3@@. Maka',
    144: '        Karena itu,',
    146: '        Sebagai fungsi dari @@M1@@, ungkapan ini sebanding dengan fungsi kepadatan beta berparameter @@M2@@ dan @@M3@@. Faktor normalisasi @@M4@@ tidak perlu dihitung.</p>',
    150: '<p>Jadi, distribusi beta konjugat terhadap distribusi Bernoulli. Distribusi posterior hanya bergantung pada vektor data @@M1@@ melalui banyaknya keberhasilan @@M2@@ karena @@M3@@ merupakan <a href="Sufficient.html">statistik cukup</a> bagi @@M4@@. Parameter kiri beta bertambah sebesar banyaknya keberhasilan @@M5@@, sedangkan parameter kanannya bertambah sebesar banyaknya kegagalan @@M6@@.</p>',
    153: '    <p class="math">Penduga Bayes bagi @@M1@@ dengan syarat @@M2@@ adalah',
    156: '        <summary>Rincian:</summary>',
    157: '        <p>Rata-rata distribusi beta adalah parameter kiri dibagi jumlah kedua parameternya, sehingga hasil ini mengikuti hasil sebelumnya.</p>',
    162: '    <p class="app">Dalam <a href="JavaScript:openAncillary(\'../apps/BetaCoin.html\')" class="ancillary">eksperimen koin beta</a>, tetapkan @@M1@@ dan @@M2@@ serta @@M3@@ dan @@M4@@. Jalankan simulasi sebanyak 100 pengulangan; pada setiap pengulangan, amati dugaan @@M5@@ serta bentuk dan letak fungsi kepadatan posterior @@M6@@.</p>',
    165: '<p>Selanjutnya kita hitung fungsi bias dan galat kuadrat rata-rata.</p>',
    168: '    <p class="math">Untuk @@M1@@,',
    170: '    Barisan @@M1@@ tak bias secara asimtotik.</p>',
    172: '        <summary>Rincian:</summary>',
    173: '        <p>Bersyarat pada @@M1@@, @@M2@@ mempunyai distribusi binomial dengan parameter @@M3@@ dan @@M4@@, sehingga @@M5@@. Maka',
    175: '        Penyederhanaan menghasilkan rumus di atas. Jelas bahwa @@M1@@ ketika @@M2@@.</p>',
    179: '<p>Kita tidak dapat memilih @@M1@@ dan @@M2@@ agar @@M3@@ tak bias untuk semua nilai parameter; pilihan yang meniadakan bias pada satu titik akan bergantung pada nilai sebenarnya @@M4@@ yang tidak diketahui.</p>',
    182: '    <p class="app">Dalam <a href="JavaScript:openAncillary(\'../apps/BetaCoin.html\')" class="ancillary">eksperimen koin beta</a>, variasikan parameter dan amati perubahan bias. Lalu tetapkan @@M1@@, @@M2@@, @@M3@@, dan @@M4@@. Jalankan simulasi sebanyak 1.000 pengulangan. Pada setiap pembaruan, amati dugaan @@M5@@ serta bentuk dan letak fungsi kepadatan posterior @@M6@@. Bandingkan bias empiris dengan bias teoretis.</p>',
    186: '    <p class="math">Untuk @@M1@@,',
    188: '    Barisan @@M1@@ konsisten dalam kuadrat rata-rata.</p>',
    190: '        <summary>Rincian:</summary>',
    191: '        <p>Sekali lagi, bersyarat pada @@M1@@, @@M2@@ mempunyai distribusi binomial dengan parameter @@M3@@ dan @@M4@@, sehingga',
    193: '        Karena itu,',
    195: '        Penyederhanaan menghasilkan rumus di atas. Jelas bahwa @@M1@@ ketika @@M2@@.</p>',
    200: '    <p class="app">Dalam <a href="JavaScript:openAncillary(\'../apps/BetaCoin.html\')" class="ancillary">eksperimen koin beta</a>, variasikan parameter dan amati perubahan galat kuadrat rata-rata. Lalu tetapkan @@M1@@, @@M2@@, dan @@M3@@. Jalankan simulasi sebanyak 1.000 pengulangan. Pada setiap pembaruan, amati dugaan @@M4@@ serta bentuk dan letak fungsi kepadatan posterior @@M5@@. Bandingkan galat kuadrat rata-rata empiris dengan nilai teoretis.</p>',
    203: '<p>Menariknya, kita dapat memilih @@M1@@ dan @@M2@@ sehingga galat kuadrat rata-rata @@M3@@ tidak bergantung pada parameter tak diketahui @@M4@@:</p>',
    206: '    <p class="math">Misalkan @@M1@@ dan @@M2@@. Maka</p>',
    211: '    <p class="app">Dalam <a href="JavaScript:openAncillary(\'../apps/BetaCoin.html\')" class="ancillary">eksperimen koin beta</a>, tetapkan @@M1@@ dan @@M2@@. Variasikan @@M3@@ dan amati bahwa galat kuadrat rata-rata tidak berubah. Lalu tetapkan @@M4@@ dan jalankan simulasi sebanyak 1.000 pengulangan. Pada setiap pembaruan, amati dugaan @@M5@@ serta bentuk dan letak fungsi kepadatan posterior. Bandingkan bias dan galat kuadrat rata-rata empiris dengan nilai teoretis.</p>',
    214: '<p>Ingat bahwa penduga metode momen bagi @@M1@@ adalah rata-rata sampel, yaitu proporsi keberhasilan. Pada ruang parameter tertutup, rata-rata sampel juga merupakan penduga kemungkinan maksimum; pada ruang terbuka @@M2@@, maksimum hanya dicapai jika banyaknya keberhasilan berada secara ketat antara nol dan ukuran sampel, sedangkan sampel batas hanya mempunyai supremum di batas:',
    216: 'Penduga ini mempunyai galat kuadrat rata-rata @@M1@@. Untuk melihat hubungan antarpeduga, perhatikan dari <a href="#ber2" class="ref"></a> bahwa',
    218: 'Jadi, @@M1@@ merupakan rata-rata tertimbang dari @@M2@@, yaitu rata-rata distribusi prior, dan @@M3@@, yaitu penduga kemungkinan maksimum ketika maksimum tersebut dicapai.</p>',
    220: '<h4 id="o006.random.point.bayes.section.another-bernoulli-distribution">Model Bernoulli Lain</h4>',
}

T.update({
    222: '<p>Pendugaan Bayes, seperti bentuk pendugaan parametrik lainnya, sangat bergantung pada himpunan parameter. Andaikan kembali bahwa @@M1@@ merupakan barisan percobaan Bernoulli bersyarat pada parameter keberhasilan tak diketahui @@M2@@, tetapi sekarang himpunan parameternya adalah @@M3@@. Kerangka ini bersesuaian dengan pelemparan koin yang seimbang atau mempunyai gambar kepala pada kedua sisi, tetapi kita tidak mengetahui jenisnya. Kita memodelkan @@M4@@ dengan variabel acak @@M5@@ yang mempunyai fungsi kepadatan probabilitas prior @@M6@@, dengan @@M7@@ dan @@M8@@; nilai @@M9@@ dipilih untuk menyatakan pengetahuan awal tentang probabilitas bahwa koin tersebut mempunyai gambar kepala pada kedua sisi. Jika sama sekali tidak mempunyai informasi awal, kita dapat mengambil @@M10@@, prior datar yang sering disebut noninformatif dengan batas penafsiran yang telah dijelaskan di atas. Jika kita menilai koin tersebut lebih mungkin mempunyai gambar kepala pada kedua sisi, kita dapat mengambil @@M11@@. Tetapkan kembali @@M12@@ untuk @@M13@@.</p>',
    225: '    <p class="math">Distribusi posterior @@M1@@ dengan syarat @@M2@@ adalah sebagai berikut.</p>',
    227: '        <li>@@M1@@ jika @@M2@@, dan @@M3@@ jika @@M4@@.</li>',
    228: '        <li>@@M1@@ jika @@M2@@, dan @@M3@@ jika @@M4@@.</li>',
    231: '        <summary>Rincian:</summary>',
    232: '        <p>Tetapkan @@M1@@. Misalkan @@M2@@, dan misalkan @@M3@@. Seperti sebelumnya,',
    234: '        Kita menggunakan konvensi lazim—yang memberikan hasil matematis yang benar—bahwa @@M1@@ jika @@M2@@, sedangkan @@M3@@. Maka, dari teorema Bayes,',
    239: '        Jadi, jika @@M1@@ maka @@M2@@, sedangkan jika @@M3@@,',
    241: '        Tentu saja, @@M1@@. Hasil tersebut kemudian diperoleh dengan sedikit aljabar.</p>',
    245: '<p>Sekarang tetapkan',
    249: '    <p class="math">Penduga Bayes bagi @@M1@@ dengan syarat @@M2@@ adalah statistik @@M3@@ yang didefinisikan oleh</p>',
    251: '        <li>@@M1@@ jika @@M2@@.</li>',
    252: '        <li>@@M1@@ jika @@M2@@.</li>',
    255: '        <summary>Rincian:</summary>',
    256: '        <p>Menurut definisi, penduga Bayes adalah @@M1@@. Dari hasil sebelumnya, jika @@M2@@ maka',
    258: '        yang menyederhana menjadi @@M1@@. Jika @@M2@@, maka @@M3@@.</p>',
    262: '<p>Jika kita mengamati @@M1@@, maka @@M2@@ memberikan nilai yang benar, yaitu @@M3@@. Hal ini wajar karena kita mengetahui bahwa koinnya bukan koin dengan gambar kepala pada kedua sisi. Sebaliknya, jika kita mengamati @@M4@@, jenis koinnya belum pasti dan dugaan Bayes @@M5@@ bahkan tidak berada dalam ruang parameter. Namun, @@M6@@ ketika @@M7@@ dengan laju eksponensial. Selanjutnya kita hitung bias dan galat kuadrat rata-rata untuk @@M8@@ yang diberikan.</p>',
    265: '    <p class="math">Untuk @@M1@@,</p>',
    270: '    <p>Barisan penduga @@M1@@ tak bias secara asimtotik.</p>',
    272: '        <summary>Rincian:</summary>',
    273: '        <p>Menurut definisi, @@M1@@. Maka, dari hasil sebelumnya,',
    278: '        Menyubstitusikan @@M1@@ dan @@M2@@ menghasilkan pernyataan tersebut. Dalam kedua kasus, @@M3@@ ketika @@M4@@ karena @@M5@@ dan @@M6@@ ketika @@M7@@.</p>',
    282: '<p>Jika @@M1@@, penduga @@M2@@ berbias negatif, seperti telah dicatat. Jika @@M3@@, maka @@M4@@ berbias positif untuk setiap @@M5@@ dan setiap nilai @@M6@@ yang diperbolehkan.</p>',
    285: '    <p class="math">Untuk @@M1@@,</p>',
    290: '    <p>Barisan penduga @@M1@@ konsisten dalam kuadrat rata-rata.</p>',
    292: '        <summary>Rincian:</summary>',
    293: '        <p>Menurut definisi, @@M1@@. Maka',
    298: '        Menyubstitusikan @@M1@@ dan @@M2@@ menghasilkan pernyataan tersebut. Dalam kedua kasus, @@M3@@ ketika @@M4@@ karena @@M5@@ dan @@M6@@ ketika @@M7@@.</p>',
    302: '<h4 id="geo">Distribusi Geometrik</h4>',
    304: '<p>Andaikan @@M1@@ merupakan barisan variabel acak saling bebas, masing-masing berdistribusi <a href="../bernoulli/Geometric.html">geometrik</a> pada @@M2@@ dengan parameter keberhasilan tak diketahui @@M3@@. Variabel-variabel ini dapat ditafsirkan sebagai banyaknya percobaan antara keberhasilan yang berurutan dalam suatu barisan <a href="../bernoulli/index.html">percobaan Bernoulli</a>. Bersyarat pada @@M4@@, distribusi geometrik mempunyai fungsi kepadatan probabilitas',
    306: 'Sekali lagi, untuk @@M1@@, tetapkan @@M2@@. Dalam kerangka ini, @@M3@@ adalah nomor percobaan tempat keberhasilan ke-@@M4@@ terjadi dan, bersyarat pada @@M5@@, mempunyai <a href="../bernoulli/NegativeBinomial.html">distribusi binomial negatif</a> dengan parameter @@M6@@ dan @@M7@@.</p>',
    308: '<p>Andaikan sekarang @@M1@@ dimodelkan dengan variabel acak @@M2@@ yang mempunyai <a href="../special/Beta.html">distribusi beta</a> prior dengan parameter kiri @@M3@@ dan parameter kanan @@M4@@. Seperti biasa, @@M5@@ dan @@M6@@ dipilih untuk menyatakan pengetahuan awal tentang @@M7@@.</p>',
    311: '    <p class="math">Distribusi posterior @@M1@@ dengan syarat @@M2@@ adalah beta dengan parameter kiri @@M3@@ dan parameter kanan @@M4@@.</p>',
    313: '        <summary>Rincian:</summary>',
    314: '        <p>Tetapkan @@M1@@. Misalkan @@M2@@ dan @@M3@@. Maka',
    316: '        Karena itu,',
    318: '        Sebagai fungsi dari @@M1@@, ungkapan ini sebanding dengan fungsi kepadatan beta berparameter @@M2@@ dan @@M3@@. Konstanta normalisasi @@M4@@ tidak perlu dihitung.</p>',
    322: '<p>Jadi, distribusi beta konjugat terhadap distribusi geometrik. Dalam distribusi beta posterior, parameter kiri bertambah sebesar banyaknya keberhasilan @@M1@@, sedangkan parameter kanan bertambah sebesar banyaknya kegagalan @@M2@@, seperti pada model Bernoulli dalam <a href="#ber1" class="ref"></a>. Secara khusus, parameter kiri posterior bersifat deterministik dan hanya bergantung pada data melalui ukuran sampel @@M3@@.</p>',
    325: '    <p class="math">Penduga Bayes bagi @@M1@@ berdasarkan @@M2@@ adalah',
    328: '        <summary>Rincian:</summary>',
    329: '        <p>Menurut definisi, penduga Bayes adalah rata-rata distribusi posterior. Ingat kembali bahwa rata-rata distribusi beta adalah parameter kiri dibagi jumlah kedua parameternya, sehingga hasil ini mengikuti teorema sebelumnya.</p>',
    333: '<p>Ingat bahwa <a href="Moments.html#geo">penduga metode momen</a> bagi @@M1@@ dan, ketika maksimum dicapai, <a href="Likelihood.html#geo">penduga kemungkinan maksimum</a> bagi @@M2@@ pada interval @@M3@@ sama-sama adalah @@M4@@. Jika seluruh pengamatan sama dengan 1, nilai batas 1 tidak termasuk ruang parameter terbuka dan hanya merupakan supremum. Untuk melihat hubungan antarpeduga, perhatikan dari <a href="#geo1" class="ref"></a> bahwa',
    335: 'Jadi, @@M1@@, yaitu kebalikan penduga Bayes, merupakan rata-rata tertimbang dari @@M2@@, yaitu kebalikan rata-rata distribusi prior, dan @@M3@@, yaitu kebalikan penduga kemungkinan maksimum ketika maksimum tersebut dicapai.</p>',
    337: '<h4 id="poi">Distribusi Poisson</h4>',
    339: '<p>Andaikan @@M1@@ merupakan barisan variabel acak saling bebas, masing-masing mempunyai <a href="../poisson/Poisson.html">distribusi Poisson</a> dengan parameter tak diketahui @@M2@@. Ingat bahwa distribusi Poisson sering digunakan untuk memodelkan banyaknya <q>titik acak</q> dalam suatu selang waktu atau daerah ruang, khususnya dalam konteks <a href="../poisson/index.html">proses Poisson</a>. Distribusi ini dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Poisson.html\')" class="ancillary">Simeon Poisson</a> dan, bersyarat pada @@M3@@, mempunyai fungsi kepadatan probabilitas',
    341: 'Sekali lagi, untuk @@M1@@, tetapkan @@M2@@. Bersyarat pada @@M3@@, variabel acak @@M4@@ juga mempunyai distribusi Poisson, tetapi dengan parameter @@M5@@.</p>',
    343: '<p>Andaikan sekarang @@M1@@ dimodelkan dengan variabel acak @@M2@@ yang mempunyai <a href="../special/Gamma.html">distribusi gamma</a> prior dengan parameter bentuk @@M3@@ dan parameter laju @@M4@@. Seperti biasa, @@M5@@ dan @@M6@@ dipilih untuk menyatakan pengetahuan awal tentang @@M7@@. Jadi, fungsi kepadatan probabilitas prior bagi @@M8@@ adalah',
    345: 'dan mempunyai rata-rata @@M1@@. Parameter skala distribusi gamma adalah @@M2@@, tetapi rumus-rumus menjadi lebih sederhana jika kita menggunakan parameter laju.</p>',
    348: '    <p class="math">Distribusi posterior @@M1@@ dengan syarat @@M2@@ adalah gamma dengan parameter bentuk @@M3@@ dan parameter laju @@M4@@.</p>',
    350: '        <summary>Rincian:</summary>',
    351: '        <p>Tetapkan @@M1@@. Misalkan @@M2@@ dan @@M3@@. Maka',
    353: '        Karena itu,',
    358: '        Sebagai fungsi dari @@M1@@, ungkapan terakhir sebanding dengan fungsi kepadatan gamma berparameter bentuk @@M2@@ dan parameter laju @@M3@@. Konstanta normalisasi @@M4@@ kembali tidak perlu dihitung.</p>',
    362: '<p>Dengan demikian, distribusi gamma konjugat terhadap distribusi Poisson. Parameter laju posterior bersifat deterministik dan hanya bergantung pada data melalui ukuran sampel @@M1@@.</p>',
    365: '    <p class="math">Penduga Bayes bagi @@M1@@ berdasarkan @@M2@@ adalah',
    368: '        <summary>Rincian:</summary>',
    369: '        <p>Menurut definisi, penduga Bayes adalah rata-rata distribusi posterior. Ingat bahwa rata-rata distribusi gamma adalah parameter bentuk dibagi parameter laju.</p>',
    373: '<p>Karena @@M1@@ merupakan fungsi linear dari @@M2@@ dan kita mengetahui distribusi @@M3@@ bersyarat pada @@M4@@, kita dapat menghitung fungsi bias dan galat kuadrat rata-ratanya.</p>',
    376: '    <p class="math">Untuk @@M1@@,',
    378: '    Barisan penduga @@M1@@ tak bias secara asimtotik.</p>',
    380: '        <summary>Rincian:</summary>',
    381: '        <p>Perhitungannya sederhana karena distribusi @@M1@@ bersyarat pada @@M2@@ adalah Poisson dengan parameter @@M3@@.',
    383: '        Jelas bahwa @@M1@@ ketika @@M2@@.</p>',
    387: '<p>Seperti sebelumnya, kita tidak dapat memilih @@M1@@ dan @@M2@@ agar @@M3@@ tak bias untuk seluruh nilai parameter tanpa mengetahui @@M4@@.</p>',
    390: '    <p class="math">Untuk @@M1@@,',
    392: '    Barisan penduga @@M1@@ konsisten dalam kuadrat rata-rata.</p>',
    394: '        <summary>Rincian:</summary>',
    395: '        <p>Sekali lagi, perhitungannya mudah karena distribusi @@M1@@ bersyarat pada @@M2@@ adalah Poisson dengan parameter @@M3@@.',
    397: '        Jelas bahwa @@M1@@ ketika @@M2@@.</p>',
    401: '<p>Ingat bahwa <a href="Moments.html#est">penduga metode momen</a> bagi @@M1@@ dan, ketika maksimum dicapai, <a href="Likelihood.html#poi">penduga kemungkinan maksimum</a> bagi @@M2@@ pada interval @@M3@@ sama-sama adalah @@M4@@, yaitu rata-rata sampel. Jika semua pengamatan nol, nilai batas 0 tidak termasuk ruang parameter terbuka dan hanya merupakan supremum. Penduga tersebut tak bias dan mempunyai galat kuadrat rata-rata @@M5@@. Untuk melihat hubungan antarpeduga, perhatikan dari <a href="#poi1" class="ref"></a> bahwa',
    403: 'Jadi, @@M1@@ merupakan rata-rata tertimbang dari @@M2@@, yaitu rata-rata distribusi prior, dan @@M3@@, yaitu penduga kemungkinan maksimum ketika maksimum tersebut dicapai.</p>',
})

T.update({
    405: '<h4 id="nor">Distribusi Normal</h4>',
    407: '<p>Andaikan @@M1@@ merupakan barisan variabel acak saling bebas, masing-masing mempunyai <a href="../special/Normal.html">distribusi normal</a> dengan rata-rata tak diketahui @@M2@@ tetapi varians diketahui @@M3@@. Distribusi normal berperan sangat penting dalam statistika, antara lain karena <a href="../sample/CLT.html">teorema limit pusat</a>. Distribusi normal banyak digunakan untuk memodelkan besaran fisik yang dipengaruhi banyak galat acak kecil. Dalam banyak penerapan statistika, varians distribusi normal lebih stabil daripada rata-ratanya, sehingga asumsi bahwa varians diketahui tidak sepenuhnya dibuat-buat. Ingat bahwa fungsi kepadatan probabilitas normal, bersyarat pada @@M4@@, adalah',
    409: 'Sekali lagi, untuk @@M1@@, misalkan @@M2@@. Ingat bahwa @@M3@@ juga mempunyai distribusi normal bersyarat pada @@M4@@, tetapi dengan rata-rata @@M5@@ dan varians @@M6@@.</p>',
    411: '<p>Andaikan sekarang @@M1@@ dimodelkan oleh variabel acak @@M2@@ yang mempunyai distribusi normal prior dengan rata-rata @@M3@@ dan varians @@M4@@. Seperti biasa, @@M5@@ dan @@M6@@ dipilih untuk menyatakan pengetahuan awal tentang @@M7@@. Kasus khusus yang menarik terjadi ketika @@M8@@, sehingga varians distribusi prior @@M9@@ sama dengan varians distribusi pensampelan yang mendasari.</p>',
    414: '    <p class="math">Untuk @@M1@@, distribusi posterior @@M2@@ dengan syarat @@M3@@ adalah normal dengan rata-rata dan varians berikut:',
    420: '        <summary>Rincian:</summary>',
    421: '        <p>Tetapkan @@M1@@. Andaikan @@M2@@, dan misalkan @@M3@@ serta @@M4@@. Maka',
    426: '        Di sisi lain,',
    428: '        Karena itu,',
    430: '        dengan @@M1@@ bergantung pada @@M2@@, @@M3@@, @@M4@@, @@M5@@, dan @@M6@@, tetapi yang penting <em>tidak</em> pada @@M7@@. Jadi, nilai pasti @@M8@@ tidak perlu kita ketahui. Melengkapi kuadrat terhadap @@M9@@ dalam ungkapan di atas menghasilkan',
    432: '        dengan @@M1@@ sebagai faktor lain yang bergantung pada banyak besaran, tetapi tidak pada @@M2@@. Sebagai fungsi dari @@M3@@, ungkapan ini sebanding dengan distribusi normal dengan rata-rata dan varians berikut, secara berurutan:',
    437: '        Sekali lagi, konstanta normalisasi @@M1@@ tidak perlu dihitung; konstanta itu hanya akan menjadi faktor lain yang tidak kita perlukan.</p>',
    441: '<p>Jadi, keluarga normal konjugat terhadap keluarga distribusi normal dengan rata-rata tak diketahui dan varians diketahui. Perhatikan bahwa varians posterior bersifat deterministik dan bergantung pada data hanya melalui ukuran sampel @@M1@@. Dalam kasus khusus @@M2@@, distribusi posterior @@M3@@ dengan syarat @@M4@@ adalah normal dengan rata-rata @@M5@@ dan varians @@M6@@.</p>',
    444: '    <p class="math">Penduga Bayes bagi @@M1@@ adalah',
    447: '        <summary>Rincian:</summary>',
    448: '        <p>Hasil ini langsung mengikuti <a href="#nor1" class="ref"></a>.</p>',
    452: '<p>Perhatikan bahwa @@M1@@ dalam kasus khusus @@M2@@.</p>',
    455: '    <p class="math">Untuk @@M1@@,',
    457: '    Barisan penduga @@M1@@ tak bias secara asimtotik.</p>',
    459: '        <summary>Rincian:</summary>',
    460: '        <p>Ingat bahwa @@M1@@ mempunyai rata-rata @@M2@@ bersyarat pada @@M3@@. Maka',
    462: '        Jelas bahwa @@M1@@ ketika @@M2@@ untuk setiap @@M3@@.</p>',
    466: '<p>Ketika @@M1@@, berlaku @@M2@@.</p>',
    469: '    <p class="math">Untuk @@M1@@,',
    471: '    Barisan penduga @@M1@@ konsisten dalam kuadrat rata-rata.</p>',
    473: '        <summary>Rincian:</summary>',
    474: '        <p>Ingat bahwa @@M1@@ mempunyai varians @@M2@@. Maka',
    476: '        Jelas bahwa @@M1@@ ketika @@M2@@ untuk setiap @@M3@@.</p>',
    480: '<p>Ketika @@M1@@, berlaku @@M2@@.',
    481: 'Ingat bahwa <a href="Moments.html#est">penduga metode momen</a> bagi @@M1@@ dan <a href="Likelihood.html#nor">penduga kemungkinan maksimum</a> bagi @@M2@@ pada @@M3@@ sama-sama adalah @@M4@@, yaitu rata-rata sampel. Penduga ini tak bias dan mempunyai galat kuadrat rata-rata @@M5@@. Untuk melihat hubungan antarpeduga, perhatikan dari <a href="#nor2" class="ref"></a> bahwa',
    483: 'Jadi, @@M1@@ merupakan rata-rata tertimbang dari @@M2@@, yaitu rata-rata distribusi prior, dan @@M3@@, yaitu penduga kemungkinan maksimum.</p>',
    485: '<h4 id="bet">Distribusi Beta</h4>',
    487: '<p>Andaikan @@M1@@ merupakan barisan variabel acak saling bebas, masing-masing mempunyai <a href="../special/Beta.html">distribusi beta</a> dengan parameter bentuk kiri tak diketahui @@M2@@ dan parameter bentuk kanan @@M3@@. Distribusi beta banyak digunakan untuk memodelkan proporsi dan probabilitas acak serta variabel lain yang nilainya berada dalam interval terbatas, setelah diskalakan ke @@M4@@. Ingat bahwa fungsi kepadatan probabilitasnya, bersyarat pada @@M5@@, adalah',
    489: 'Andaikan sekarang @@M1@@ dimodelkan oleh variabel acak @@M2@@ yang mempunyai distribusi gamma prior dengan parameter bentuk @@M3@@ dan parameter laju @@M4@@. Seperti biasa, @@M5@@ dan @@M6@@ dipilih untuk menyatakan pengetahuan awal tentang @@M7@@. Jadi, fungsi kepadatan probabilitas prior bagi @@M8@@ adalah',
    491: 'Rata-rata distribusi prior adalah @@M1@@.</p>',
    494: '    <p class="math">Distribusi posterior @@M1@@ dengan syarat @@M2@@ adalah gamma dengan parameter bentuk @@M3@@ dan parameter laju @@M4@@.</p>',
    496: '        <summary>Rincian:</summary>',
    497: '        <p>Tetapkan @@M1@@. Misalkan @@M2@@ dan @@M3@@. Maka',
    499: '        Karena itu,',
    501: '        Sebagai fungsi dari @@M1@@, ungkapan ini sebanding dengan fungsi kepadatan gamma dengan parameter bentuk @@M2@@ dan parameter laju @@M3@@. Sekali lagi, konstanta normalisasi @@M4@@ tidak perlu dihitung.</p>',
    505: '<p>Jadi, distribusi gamma konjugat terhadap distribusi beta dengan parameter kiri tak diketahui dan parameter kanan 1. Perhatikan bahwa parameter bentuk posterior bersifat deterministik dan bergantung pada data hanya melalui ukuran sampel @@M1@@.</p>',
    508: '    <p class="math">Penduga Bayes bagi @@M1@@ berdasarkan @@M2@@ adalah',
    511: '        <summary>Rincian:</summary>',
    512: '        <p>Rata-rata distribusi gamma adalah parameter bentuk dibagi parameter laju, sehingga hasil ini mengikuti <a href="#bet1" class="ref"></a>.</p>',
    516: '<p>Mengingat strukturnya yang rumit, bias dan galat kuadrat rata-rata @@M1@@ bersyarat pada @@M2@@ akan sulit dihitung secara eksplisit. Ingat bahwa <a href="Likelihood.html#bet">penduga kemungkinan maksimum</a> bagi @@M3@@ adalah @@M4@@. Untuk melihat hubungan antarpeduga, perhatikan dari <a href="#bet2" class="ref"></a> bahwa',
    518: 'Jadi, @@M1@@, yaitu kebalikan penduga Bayes, merupakan rata-rata tertimbang dari @@M2@@, yaitu kebalikan rata-rata distribusi prior, dan @@M3@@, yaitu kebalikan penduga kemungkinan maksimum.</p>',
    520: '<h4 id="par">Distribusi Pareto</h4>',
    522: '<p>Andaikan @@M1@@ merupakan barisan variabel acak saling bebas, masing-masing mempunyai <a href="../special/Pareto.html">distribusi Pareto</a> dengan parameter bentuk tak diketahui @@M2@@ dan parameter skala @@M3@@. Distribusi Pareto digunakan untuk memodelkan variabel finansial tertentu dan variabel lain yang berdistribusi berekor berat, serta dinamai menurut <a href="JavaScript:openAncillary(\'../biographies/Pareto.html\')" class="ancillary">Vilfredo Pareto</a>. Ingat bahwa fungsi kepadatan probabilitasnya, bersyarat pada @@M4@@, adalah',
    524: 'Andaikan sekarang @@M1@@ dimodelkan oleh variabel acak @@M2@@ yang mempunyai distribusi gamma prior dengan parameter bentuk @@M3@@ dan parameter laju @@M4@@. Seperti biasa, @@M5@@ dan @@M6@@ dipilih untuk menyatakan pengetahuan awal tentang @@M7@@. Jadi, fungsi kepadatan probabilitas prior bagi @@M8@@ adalah',
    528: '    <p class="math">Untuk @@M1@@, distribusi posterior @@M2@@ dengan syarat @@M3@@ adalah gamma dengan parameter bentuk @@M4@@ dan parameter laju @@M5@@.</p>',
    530: '        <summary>Rincian:</summary>',
    531: '        <p>Tetapkan @@M1@@. Misalkan @@M2@@ dan @@M3@@. Maka',
    533: '        Karena itu,',
    535: '        Sebagai fungsi dari @@M1@@, ungkapan ini sebanding dengan fungsi kepadatan gamma dengan parameter bentuk @@M2@@ dan parameter laju @@M3@@. Sekali lagi, konstanta normalisasi @@M4@@ tidak perlu dihitung.</p>',
    539: '<p>Jadi, distribusi gamma konjugat terhadap distribusi Pareto dengan parameter bentuk tak diketahui. Perhatikan bahwa parameter bentuk posterior bersifat deterministik dan bergantung pada data hanya melalui ukuran sampel @@M1@@.</p>',
    542: '    <p class="math">Penduga Bayes bagi @@M1@@ berdasarkan @@M2@@ adalah',
    545: '        <summary>Rincian:</summary>',
    546: '        <p>Sekali lagi, rata-rata distribusi gamma adalah parameter bentuk dibagi parameter laju, sehingga hasil ini mengikuti <a href="#par1" class="ref"></a>.</p>',
    550: '<p>Mengingat strukturnya yang rumit, bias dan galat kuadrat rata-rata @@M1@@ bersyarat pada @@M2@@ akan sulit dihitung secara eksplisit. Jika hasil kali sampel lebih besar daripada 1, <a href="Likelihood.html#par">penduga kemungkinan maksimum</a> bagi @@M3@@ adalah @@M4@@. Jika hasil kali sampel sama dengan 1, fungsi kemungkinan meningkat tanpa batas ketika parameter bentuk menuju tak hingga, sehingga tidak ada penduga kemungkinan maksimum berhingga. Kasus batas tersebut berprobabilitas nol di bawah model kontinu, tetapi tetap termasuk dalam ruang sampel yang dinyatakan. Untuk melihat hubungan antarpeduga, perhatikan dari <a href="#par2" class="ref"></a> bahwa',
    552: 'Jadi, @@M1@@, yaitu kebalikan penduga Bayes, merupakan rata-rata tertimbang dari @@M2@@, yaitu kebalikan rata-rata distribusi prior, dan @@M3@@, yaitu kebalikan penduga kemungkinan maksimum ketika penduga tersebut ada.</p>',
    557: '        <li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>',
    558: '        <li class="child"><a href="Estimators.html" title="Penduga">1</a></li>',
    559: '        <li class="child"><a href="Moments.html" title="Metode Momen">2</a></li>',
    560: '        <li class="child"><a href="Likelihood.html" title="Kemungkinan Maksimum">3</a></li>',
    562: '        <li class="child"><a href="Unbiased.html" title="Penduga Tak Bias Terbaik">5</a></li>',
    563: '        <li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancilar">6</a></li>',
    564: '        <li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>',
    565: '        <li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>',
    568: '        <li class="sister"><a href="JavaScript:openAncillary(\'../apps/index.html\')" class="ancillary">Aplikasi</a></li>',
    569: '        <li class="sister"><a href="JavaScript:openAncillary(\'../data/index.html\')" class="ancillary">Himpunan Data</a></li>',
    570: '        <li class="child"><a href="JavaScript:openAncillary(\'../biographies/index.html\')" class="ancillary">Biografi</a></li>',
})


# Exact bounded target repairs; every other delimited TeX span and raw math
# block remains authority-identical and is restored from the frozen source.
MATH_FIXES: dict[int, tuple[tuple[str, str], ...]] = {
    69: ((
        r"\( h(\theta \mid x) = h(\theta) f(\bs x \mid \theta) / f(\bs x) \)",
        r"\( h(\theta \mid \bs x) = h(\theta) f(\bs x \mid \theta) / f(\bs x) \)",
    ),),
    120: ((
        r"\( u \mapsto \E[(\Theta - u)^2 \mid \bs X = \bs x) \)",
        r"\( u \mapsto \E[(\Theta - u)^2 \mid \bs X = \bs x] \)",
    ),),
    173: ((r"\( E(Y_n \mid p) = n p \)", r"\( \E(Y_n \mid p) = n p \)"),),
    203: ((r"\(U\)", r"\(U_n\)"),),
    215: ((
        r"\[ M_n = \frac{Y}{n} = \frac{1}{n} \sum_{i=1}^n X_i \]",
        r"\[ M_n = \frac{Y_n}{n} = \frac{1}{n} \sum_{i=1}^n X_i \]",
    ),),
    256: ((r"\( U_n = E(P \mid \bs{X}_n) \)", r"\( U_n = \E(P \mid \bs{X}_n) \)"),),
    258: ((
        r"\( U = 1 \cdot 0 + \frac{1}{2} \cdot 1 = \frac{1}{2} \)",
        r"\( U_n = 1 \cdot 0 + \frac{1}{2} \cdot 1 = \frac{1}{2} \)",
    ),),
    273: ((
        r"\( \bias(U_n \mid p) = E(U - p \mid p) \)",
        r"\( \bias(U_n \mid p) = \E(U_n - p \mid p) \)",
    ),),
    275: (
        (r"\bias(U \mid p)", r"\bias(U_n \mid p)"),
        (r"\P(Y = n \mid p)", r"\P(Y_n = n \mid p)"),
        (r"\P(Y \lt n \mid p)", r"\P(Y_n \lt n \mid p)"),
    ),
    322: ((r"\(Y - n\)", r"\(Y_n - n\)"),),
    396: ((r"\[ \mse(V \mid \lambda) ", r"\[ \mse(V_n \mid \lambda) "),),
    421: ((
        r"\( \bs x = (x_1, x_2, \ldots, x_n) \in \R \)",
        r"\( \bs x = (x_1, x_2, \ldots, x_n) \in \R^n \)",
    ),),
    480: ((r"\(\mse(U \mid \mu)", r"\(\mse(U_n \mid \mu)"),),
    481: ((
        r"\(\var(M) = \sigma^2 / n\)",
        r"\(\mse(M_n \mid \mu) = \var(M_n \mid \mu) = \sigma^2 / n\)",
    ),),
    550: ((r"\(U\)", r"\(U_n\)"),),
}


STABLE_IDS: dict[int, tuple[str, str]] = {
    57: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.posterior-density">'),
    86: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.posterior-mean">'),
    100: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.conditional-risk">'),
    110: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.asymptotic-properties">'),
    161: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.beta-coin-posterior-app">'),
    181: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.beta-coin-bias-app">'),
    199: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.beta-coin-mse-app">'),
    210: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.beta-coin-constant-mse-app">'),
    224: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.two-point-posterior">'),
    248: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.two-point-estimator">'),
    264: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.two-point-bias">'),
    284: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.two-point-mse">'),
    310: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.geometric-posterior">'),
    347: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.poisson-posterior">'),
    375: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.poisson-bias">'),
    389: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.poisson-mse">'),
    454: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.normal-bias">'),
    468: ('<div class="unit">', '<div class="unit" id="o006.random.point.bayes.unit.normal-mse">'),
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/point/index.html": "index.html",
    "https://www.randomservices.org/random/point/Estimators.html": "Estimators.html",
    "https://www.randomservices.org/random/point/Moments.html": "Moments.html",
    "https://www.randomservices.org/random/point/Likelihood.html": "Likelihood.html",
    "https://www.randomservices.org/random/point/Bayes.html": "Bayes.html",
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
        ">Bayesian Estimation<", ">Basic Theory<", ">The General Method<",
        ">Random Samples<", ">Real Parameters<", ">Conjugate Families<",
        ">Special Distributions<", ">The Bernoulli Distribution<",
        ">Another Bernoulli Distribution<", ">The Geometric distribution<",
        ">The Poisson Distribution<", ">The Normal Distribution<",
        ">The Beta Distribution<", ">The Pareto Distribution<",
        ">Apps<", ">Data Sets<", "> Biographies<",
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
