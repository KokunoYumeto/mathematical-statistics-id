#!/usr/bin/env python3
"""Create the bounded id-ID two-sample/bivariate-normal testing target."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "hypothesis" / "BivariateNormal.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "hypothesis" / "BivariateNormal.html"
SOURCE_URL = "https://www.randomservices.org/random/hypothesis/BivariateNormal.html"
SOURCE_BYTES = 26540
SOURCE_SHA256 = "4a1e7607fc2ca8d18704b5cf8a9edecb5bc45556399ea6bb9ed4965c9d7669f8"
EXPECTED_SOURCE_LINES = 317

MATH_RE = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")
TOKEN_RE = re.compile(r"@@M(\d+)@@")


T: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Pengujian pada Model Normal Dua Sampel</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, uji hipotesis, model normal dua sampel, model normal bivariat, selisih rata-rata, rasio varians, distribusi t Student, distribusi khi-kuadrat, distribusi Fisher F">''',
    33: r'''\t\t<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    34: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    35: r'''\t\t<li class="child"><a href="Normal.html" title="Pengujian pada Model Normal">2</a></li>''',
    36: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Uji dalam Model Bernoulli">3</a></li>''',
    38: r'''\t\t<li class="child"><a href="Likelihood.html" title="Uji Rasio Likelihood">5</a></li>''',
    39: r'''\t\t<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    40: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    41: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    43: r'''\t<h2 id="o006.random.hypothesis.bivariate-normal.page">4. Pengujian pada Model Normal Dua Sampel</h2>''',
    46: r'''<p>Dalam bagian ini, kita mempelajari uji hipotesis pada model normal dua sampel dan model normal bivariat. Bagian ini sejajar dengan pembahasan <a href="../interval/BivariateNormal.html">pendugaan pada model normal dua sampel</a> dalam bab <a href="../interval/index.html">pendugaan himpunan</a>.</p>''',
    48: r'''<h3 id="two">Model Normal Dua Sampel</h3>''',
    50: r'''<p>Misalkan @@M1@@ adalah sampel acak berukuran @@M2@@ dari <a href="../special/Normal.html">distribusi normal</a> dengan <a href="../expect/Properties.html">rata-rata</a> @@M3@@ dan simpangan baku @@M4@@, sedangkan @@M5@@ adalah sampel acak berukuran @@M6@@ dari distribusi normal dengan rata-rata @@M7@@ dan simpangan baku @@M8@@. Selain itu, misalkan sampel @@M9@@ dan @@M10@@ <a href="../prob/Independence.html">saling bebas</a>.</p>''',
    52: r'''<p>Situasi ini sering muncul ketika variabel acak menyatakan pengukuran yang diminati pada objek-objek suatu populasi, sedangkan kedua sampel bersesuaian dengan dua perlakuan berbeda. Misalnya, kita mungkin tertarik pada tekanan darah suatu populasi pasien. Vektor @@M1@@ mencatat tekanan darah sampel kontrol, sedangkan vektor @@M2@@ mencatat tekanan darah sampel yang menerima obat baru. Demikian pula, kita mungkin tertarik pada hasil panen jagung per ekar. Vektor @@M3@@ mencatat hasil sampel yang menerima satu jenis pupuk, sedangkan vektor @@M4@@ mencatat hasil sampel yang menerima jenis pupuk lain.</p>''',
    54: r'''<p>Biasanya perhatian kita tertuju pada perbandingan parameter kedua distribusi asal sampel, baik rata-rata maupun variansnya. Dalam bagian ini, kita membangun uji bagi selisih rata-rata dan rasio varians. Seperti pada masalah pendugaan sebelumnya, prosedurnya bergantung pada parameter mana yang diketahui. Unsur utama konstruksi uji adalah <a href="../sample/Mean.html">rata-rata sampel</a>, <a href="../sample/Variance.html">varians sampel</a>, dan <a href="../sample/Normal.html">sifat khusus</a> statistik tersebut ketika distribusi asal sampelnya normal.</p>''',
    57: r'''\t<p class="dfn">Kita menggunakan notasi berikut bagi rata-rata sampel dan varians sampel dari sampel generik @@M1@@:''',
    61: r'''<h4 id="nor">Uji Selisih Rata-Rata dengan Simpangan Baku Diketahui</h4>''',
    63: r'''<p>Pertama, kita menelaah uji bagi selisih rata-rata @@M1@@ dengan asumsi simpangan baku @@M2@@ dan @@M3@@ diketahui. Asumsi ini sering, tetapi tidak selalu, kurang realistis. Dalam sebagian masalah statistika, varians stabil sehingga setidaknya diketahui secara hampiran, sedangkan rata-rata dapat berbeda akibat perlakuan yang berbeda. Kasus ini juga merupakan titik awal yang baik karena analisisnya relatif mudah.</p>''',
    66: r'''\t<p class="math">Untuk nilai hipotesis selisih rata-rata @@M1@@, definisikan statistik uji''',
    69: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai distribusi normal baku.</li>''',
    70: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai distribusi normal dengan rata-rata @@M3@@ dan varians 1.</li>''',
    73: r'''\t\t<summary>Rincian:</summary>''',
    74: r'''\t\t<p>Dari sifat sampel normal, @@M1@@ mempunyai distribusi normal dengan rata-rata @@M2@@ dan varians @@M3@@; demikian pula, @@M4@@ mempunyai distribusi normal dengan rata-rata @@M5@@ dan varians @@M6@@. Karena kedua sampel saling bebas, @@M7@@ dan @@M8@@ saling bebas. Jadi, @@M9@@ mempunyai distribusi normal dengan rata-rata @@M10@@ dan varians @@M11@@. Hasil akhir mengikuti karena @@M12@@ merupakan fungsi linear dari @@M13@@.</p>''',
    78: r'''<p>Bagian (b) sebenarnya mencakup bagian (a), tetapi keduanya dipisahkan karena memainkan peran penting yang berbeda dalam uji hipotesis. Pada bagian (b), rata-rata yang tidak nol dapat dipandang sebagai <dfn>parameter nonsentral</dfn>.</p>''',
    80: r'''<p>Seperti biasa, untuk @@M1@@, misalkan @@M2@@ menyatakan <a href="../dist/CDF.html#qnt">kuantil</a> berorde @@M3@@ dari distribusi normal baku. Untuk nilai @@M4@@ tertentu, @@M5@@ dapat diperoleh dari <a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">aplikasi kuantil</a> atau sebagian besar paket perangkat lunak statistika. Ingat pula bahwa, berdasarkan simetri, @@M6@@.</p>''',
    83: r'''\t<p class="math">Untuk setiap @@M1@@, uji berikut mempunyai tingkat signifikansi @@M2@@:</p>''',
    85: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@ atau @@M4@@; secara ekuivalen, jika dan hanya jika @@M5@@ atau @@M6@@.</li>''',
    86: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    87: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    90: r'''\t\t<summary>Rincian:</summary>''',
    91: r'''\t\t<p>Logikanya sama dengan yang telah kita gunakan. Pada bagian (a), @@M1@@ merupakan hipotesis sederhana dan, di bawah hipotesis ini, @@M2@@ mempunyai distribusi normal baku. Karena itu, jika @@M3@@ benar, peluang menolak @@M4@@ secara keliru adalah @@M5@@ menurut definisi kuantil. Pada bagian (b) dan (c), @@M6@@ menentukan suatu rentang nilai @@M7@@ dan, di bawah @@M8@@, @@M9@@ mempunyai distribusi normal tak baku menurut <a href="#nor1" class="ref"></a>. Peluang galat tipe I terbesar adalah @@M10@@ dan terjadi ketika @@M11@@. Aturan keputusan dalam @@M12@@ ekuivalen dengan aturan dalam @@M13@@ melalui aljabar sederhana.</p>''',
    96: r'''\t<p class="math">Untuk setiap uji di atas, kita <em>gagal</em> menolak @@M1@@ pada tingkat signifikansi @@M2@@ jika dan hanya jika @@M3@@ berada dalam interval kepercayaan bertingkat @@M4@@ yang bersesuaian.</p>''',
    103: r'''\t\t<summary>Rincian:</summary>''',
    104: r'''\t\t<p>Hasil ini mengikuti <a href="#nor2" class="ref"></a>. Dalam setiap kasus, kita mulai dari pertidaksamaan yang bersesuaian dengan <em>tidak</em> menolak hipotesis nol, lalu menyelesaikannya terhadap @@M1@@.</p>''',
    108: r'''<h4 id="stu">Uji Selisih Rata-Rata dengan Simpangan Baku Tidak Diketahui</h4>''',
    110: r'''<p>Selanjutnya, kita membangun uji bagi selisih rata-rata @@M1@@ dengan asumsi yang lebih realistis bahwa simpangan baku @@M2@@ dan @@M3@@ tidak diketahui. Dalam kasus ini, statistik uji yang sesuai lebih sulit ditemukan, tetapi analisis dapat dilakukan pada kasus khusus ketika kedua simpangan baku sama. Karena itu, kita mengasumsikan @@M4@@ dan nilai bersama @@M5@@ tidak diketahui. Asumsi ini masuk akal apabila terdapat variabilitas inheren pada variabel pengukuran yang tidak berubah meskipun perlakuan berbeda diterapkan pada objek-objek populasi.</p>''',
    113: r'''\t<p class="dfn">Ingat bahwa <dfn>penduga gabungan</dfn> bagi varians bersama @@M1@@ adalah rata-rata tertimbang kedua varians sampel, dengan derajat kebebasan sebagai bobotnya:''',
    115: r'''\tStatistik @@M1@@ merupakan penduga tak bias dan konsisten bagi varians bersama @@M2@@.</p>''',
    119: r'''\t<p class="math">Untuk nilai hipotesis @@M1@@, definisikan statistik uji''',
    122: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai <a href="../special/Student.html">distribusi @@M3@@ Student</a> dengan @@M4@@ derajat kebebasan.</li>''',
    123: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai <a href="../special/Student.html#non">distribusi @@M3@@ nonsentral</a> dengan @@M4@@ derajat kebebasan dan parameter nonsentral''',
    127: r'''\t\t<summary>Rincian:</summary>''',
    128: r'''\t\t<p>Bagian (b) sebenarnya mencakup bagian (a), sebab distribusi @@M1@@ biasa merupakan kasus khusus distribusi @@M2@@ nonsentral dengan parameter nonsentral 0. Melalui aljabar dasar, @@M3@@ dapat ditulis sebagai''',
    130: r'''\t\tdengan @@M1@@ sebagai skor baku @@M2@@, @@M3@@ sebagai parameter nonsentral dalam teorema, dan @@M4@@. Jadi, @@M5@@ mempunyai distribusi normal baku, @@M6@@ mempunyai distribusi khi-kuadrat dengan @@M7@@ derajat kebebasan, serta @@M8@@ dan @@M9@@ saling bebas. Menurut definisi, @@M10@@ mempunyai distribusi @@M11@@ nonsentral dengan @@M12@@ derajat kebebasan dan parameter nonsentral @@M13@@.</p>''',
    134: r'''<p>Seperti biasa, untuk @@M1@@ dan @@M2@@, misalkan @@M3@@ menyatakan <a href="../dist/CDF.html#qnt">kuantil</a> berorde @@M4@@ dari distribusi @@M5@@ dengan @@M6@@ derajat kebebasan. Untuk nilai @@M7@@ dan @@M8@@ tertentu, @@M9@@ dapat dihitung dengan <a href="JavaScript:openAncillary('../apps/QuantileApp.html')" class="ancillary">aplikasi kuantil</a> atau sebagian besar paket perangkat lunak statistika. Ingat pula bahwa, berdasarkan simetri, @@M10@@.</p>''',
    137: r'''\t<p class="math">Uji berikut mempunyai tingkat signifikansi @@M1@@:</p>''',
    139: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@ atau @@M4@@; secara ekuivalen, jika dan hanya jika @@M5@@ atau @@M6@@.</li>''',
    140: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    141: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@; secara ekuivalen, jika dan hanya jika @@M4@@.</li>''',
    144: r'''\t\t<summary>Rincian:</summary>''',
    145: r'''\t\t<p>Logikanya sama seperti sebelumnya. Pada bagian (a), @@M1@@ merupakan hipotesis sederhana dan, di bawah hipotesis ini, @@M2@@ mempunyai distribusi @@M3@@ dengan @@M4@@ derajat kebebasan. Karena itu, jika @@M5@@ benar, peluang menolak @@M6@@ secara keliru adalah @@M7@@ menurut definisi kuantil. Pada bagian (b) dan (c), @@M8@@ menentukan suatu rentang nilai @@M9@@ dan, di bawah @@M10@@, @@M11@@ mempunyai distribusi @@M12@@ nonsentral menurut <a href="#stu1" class="ref"></a>. Peluang galat tipe I terbesar adalah @@M13@@ dan terjadi ketika @@M14@@. Aturan keputusan dalam @@M15@@ ekuivalen dengan aturan dalam @@M16@@ melalui aljabar sederhana.</p>''',
    150: r'''\t<p class="math">Untuk setiap uji di atas, kita gagal menolak @@M1@@ pada tingkat signifikansi @@M2@@ jika dan hanya jika @@M3@@ berada dalam interval kepercayaan bertingkat @@M4@@ yang bersesuaian.</p>''',
    157: r'''\t\t<summary>Rincian:</summary>''',
    158: r'''\t\t<p>Hasil ini mengikuti <a href="#stu2" class="ref"></a>. Dalam setiap kasus, kita mulai dari pertidaksamaan yang bersesuaian dengan <em>tidak</em> menolak hipotesis nol, lalu menyelesaikannya terhadap @@M1@@.</p>''',
    162: r'''<h4 id="fsh">Uji Rasio Varians</h4>''',
    164: r'''<p>Selanjutnya, kita membangun uji bagi rasio varians distribusi @@M1@@. Asumsi dasarnya adalah bahwa kedua varians dan, tentu saja, kedua rata-rata @@M2@@ serta @@M3@@ tidak diketahui.</p>''',
    167: r'''\t<p class="math">Untuk nilai hipotesis @@M1@@, definisikan statistik uji''',
    170: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai <a href="../special/Fisher.html">distribusi @@M3@@</a> dengan @@M4@@ derajat kebebasan pada pembilang dan @@M5@@ derajat kebebasan pada penyebut.</li>''',
    171: r'''\t\t<li>Jika @@M1@@, maka @@M2@@ mempunyai distribusi @@M3@@ terskala dengan @@M4@@ derajat kebebasan pada pembilang, @@M5@@ derajat kebebasan pada penyebut, dan faktor skala @@M6@@.</li>''',
    174: r'''\t\t<summary>Rincian:</summary>''',
    175: r'''\t\t<p>Bagian (b) mencakup bagian (a) ketika @@M1@@, sehingga cukup membuktikan (b). Perhatikan bahwa''',
    177: r'''\t\tAkan tetapi, @@M1@@ mempunyai distribusi khi-kuadrat dengan @@M2@@ derajat kebebasan, sedangkan @@M3@@ mempunyai distribusi khi-kuadrat dengan @@M4@@ derajat kebebasan; kedua variabel itu saling bebas. Karena rasio pada tampilan di atas menggunakan masing-masing variabel setelah dibagi derajat kebebasannya, rasio tersebut mempunyai distribusi @@M5@@ dengan @@M6@@ derajat kebebasan pada pembilang dan @@M7@@ derajat kebebasan pada penyebut.</p>''',
    182: r'''\t<p class="math">Uji berikut mempunyai tingkat signifikansi @@M1@@; notasi kuantil mengikuti bagian pendugaan yang dirujuk di atas:</p>''',
    184: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@ atau @@M4@@.</li>''',
    185: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@.</li>''',
    186: r'''\t\t<li>Tolak @@M1@@ melawan @@M2@@ jika dan hanya jika @@M3@@.</li>''',
    189: r'''\t\t<summary>Rincian:</summary>''',
    190: r'''\t\t<p>Buktinya menggunakan argumen biasa. Pada bagian (a), @@M1@@ merupakan hipotesis sederhana dan, di bawah hipotesis ini, @@M2@@ mempunyai distribusi @@M3@@ dengan @@M4@@ derajat kebebasan pada pembilang dan @@M5@@ derajat kebebasan pada penyebut. Karena itu, jika @@M6@@ benar, peluang menolak @@M7@@ secara keliru adalah @@M8@@ menurut definisi kuantil. Pada bagian (b) dan (c), @@M9@@ menentukan suatu rentang nilai @@M10@@ dan, di bawah @@M11@@, @@M12@@ mempunyai distribusi @@M13@@ terskala menurut teorema <a href="#fsh1" class="ref"></a>. Peluang galat tipe I terbesar adalah @@M14@@ dan terjadi ketika @@M15@@.</p>''',
    195: r'''\t<p class="math">Untuk setiap uji di atas, kita <em>gagal</em> menolak @@M1@@ pada tingkat signifikansi @@M2@@ jika dan hanya jika @@M3@@ berada dalam interval kepercayaan bertingkat @@M4@@ yang bersesuaian.</p>''',
    202: r'''\t\t<summary>Rincian:</summary>''',
    203: r'''\t\t<p>Hasil ini mengikuti <a href="#fsh2" class="ref"></a>. Dalam setiap kasus, kita mulai dari pertidaksamaan yang bersesuaian dengan <em>tidak</em> menolak hipotesis nol, lalu menyelesaikannya terhadap @@M1@@.</p>''',
    207: r'''<h3 id="biv">Pengujian pada Model Normal Bivariat</h3>''',
    209: r'''<p>Dalam subbagian ini, kita menelaah model yang sepintas mirip dengan model normal dua sampel, tetapi sebenarnya jauh lebih sederhana. Misalkan''',
    211: r'''merupakan sampel acak berukuran @@M1@@ dari <a href="../special/MultiNormal.html">distribusi normal bivariat</a> bagi @@M2@@, dengan @@M3@@, @@M4@@, @@M5@@, @@M6@@, dan @@M7@@.</p>''',
    213: r'''<p>Jadi, alih-alih <em>sepasang sampel</em>, kita mempunyai <em>sampel pasangan</em>. Perbedaan mendasarnya adalah bahwa, dalam model ini, variabel @@M1@@ dan @@M2@@ diukur pada objek yang <em>sama</em> dari suatu sampel populasi, sedangkan pada model sebelumnya variabel @@M3@@ dan @@M4@@ diukur pada dua sampel berbeda. Model bivariat muncul, misalnya, dalam <dfn>eksperimen sebelum-sesudah</dfn>, ketika suatu pengukuran dicatat pada sampel @@M5@@ objek sebelum dan sesudah perlakuan. Sebagai contoh, kita dapat mencatat tekanan darah sampel @@M6@@ pasien sebelum dan sesudah pemberian obat tertentu.</p>''',
    215: r'''<p>Kita menggunakan notasi biasa bagi rata-rata sampel dan varians sampel dari @@M1@@ serta @@M2@@ pada definisi <a href="#dfn1" class="ref"></a>. Ingat pula bahwa <a href="../sample/Covariance.html">kovarians sampel</a> dari @@M3@@ adalah''',
    217: r'''(jangan disamakan dengan penduga gabungan simpangan baku pada definisi <a href="#stu0" class="ref"></a>).</p>''',
    220: r'''\t<p class="math">Barisan selisih @@M1@@ merupakan sampel acak berukuran @@M2@@ dari distribusi @@M3@@. Distribusi asal sampelnya normal dengan</p>''',
    228: r'''\t<p class="math">Rata-rata sampel dan varians sampel dari sampel selisih adalah</p>''',
    235: r'''<p>Sampel selisih @@M1@@ mengikuti model normal satu variabel. Bagian tentang <a href="Normal.html">pengujian pada model normal</a> dapat digunakan untuk menguji rata-rata distribusi @@M2@@ dan varians distribusi @@M3@@.</p>''',
    237: r'''<h3 id="exe">Latihan Komputasi</h3>''',
    240: r'''\t<p class="math">Sebuah obat baru sedang dikembangkan untuk menurunkan kadar zat kimia tertentu dalam darah. Sampel 36 pasien menerima plasebo, sedangkan sampel 49 pasien menerima obat tersebut. Statistiknya (dalam mg) adalah @@M1@@, @@M2@@, @@M3@@, dan @@M4@@. Ujilah pernyataan berikut pada tingkat signifikansi 10%:</p>''',
    242: r'''\t\t<li>@@M1@@ melawan @@M2@@.</li>''',
    243: r'''\t\t<li>@@M1@@ melawan @@M2@@ (dengan asumsi @@M3@@).</li>''',
    244: r'''\t\t<li>Berdasarkan (b), apakah obat tersebut efektif?</li>''',
    247: r'''\t\t<summary>Rincian:</summary>''',
    249: r'''\t\t\t<li>Statistik uji F = 16/36 ≈ 0,444, nilai kritis 0,585 dan 1,667. Tolak @@M1@@.</li>''',
    250: r'''\t\t\t<li>Statistik uji gabungan sekitar 20,82, nilai kritis sisi kanan @@M1@@. Tolak @@M2@@.</li>''',
    251: r'''\t\t\t<li>Ya: data memberikan bukti sangat kuat bahwa rata-rata pada kelompok plasebo lebih tinggi, sehingga obat mendukung penurunan kadar zat tersebut. Namun, karena (a) menolak kesamaan varians, analisis terapan sebaiknya mengonfirmasi kesimpulan dengan uji Welch, bukan hanya uji gabungan yang diminta pada (b).</li>''',
    257: r'''\t<p class="math">Sebuah perusahaan mengklaim bahwa suplemen herbal meningkatkan kecerdasan. Sampel 25 orang menjalani tes IQ baku sebelum dan sesudah mengonsumsi suplemen. Statistik sebelum dan sesudahnya adalah @@M1@@, @@M2@@, @@M3@@, @@M4@@, dan @@M5@@. Pada tingkat signifikansi 10%, apakah klaim perusahaan itu dapat dipercaya?</p>''',
    259: r'''\t\t<summary>Rincian:</summary>''',
    260: r'''\t\t<p>Statistik uji berpasangan sekitar 2,831, nilai kritis 1,3178. Tolak @@M1@@.</p>''',
    265: r'''\t<p class="stat">Dalam <a href="JavaScript:openAncillary('../data/Iris.html')" class="ancillary">data iris Fisher</a>, perhatikan variabel panjang mahkota pada sampel iris Versicolor dan Virginica. Ujilah pernyataan berikut pada tingkat signifikansi 10%:</p>''',
    267: r'''\t\t<li>@@M1@@ melawan @@M2@@.</li>''',
    268: r'''\t\t<li>@@M1@@ melawan @@M2@@ (dengan asumsi @@M3@@).</li>''',
    271: r'''\t\t<summary>Rincian:</summary>''',
    273: r'''\t\t\t<li>Statistik uji sekitar 0,944, nilai kritis 0,6222 dan 1,6073. Gagal menolak @@M1@@.</li>''',
    274: r'''\t\t\t<li>Statistik uji @@M1@@, nilai kritis sisi kiri @@M2@@. Tolak @@M3@@.</li>''',
    280: r'''\t<p class="math">Sebuah pabrik mempunyai dua mesin yang menghasilkan batang bundar dengan diameter kritis (dalam cm). Sampel 100 batang dari mesin pertama mempunyai rata-rata 10,3 dan simpangan baku 1,2. Sampel 100 batang dari mesin kedua mempunyai rata-rata 9,8 dan simpangan baku 1,6. Ujilah hipotesis berikut pada tingkat signifikansi 10%.</p>''',
    282: r'''\t\t<li>@@M1@@ melawan @@M2@@.</li>''',
    283: r'''\t\t<li>@@M1@@ melawan @@M2@@ (dengan asumsi @@M3@@).</li>''',
    286: r'''\t\t<summary>Rincian:</summary>''',
    288: r'''\t\t\t<li>Statistik uji 0,5625, nilai kritis 0,7173 dan 1,3941. Tolak @@M1@@.</li>''',
    289: r'''\t\t\t<li>Statistik uji @@M1@@, nilai kritis @@M2@@. Tolak @@M3@@. Karena (a) menolak kesamaan varians, kesimpulan terapan sebaiknya juga diperiksa dengan uji Welch.</li>''',
    297: r'''\t\t<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    298: r'''\t\t<li class="child"><a href="Introduction.html" title="Pendahuluan">1</a></li>''',
    299: r'''\t\t<li class="child"><a href="Normal.html" title="Pengujian pada Model Normal">2</a></li>''',
    300: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Uji dalam Model Bernoulli">3</a></li>''',
    302: r'''\t\t<li class="child"><a href="Likelihood.html" title="Uji Rasio Likelihood">5</a></li>''',
    303: r'''\t\t<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    304: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    305: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    308: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    309: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    310: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


MATH_REPAIRS: dict[int, tuple[tuple[str, str], ...]] = {
    50: ((
        r'''\(\bs{X} = (X_1, X_2, \ldots, X_n)\)''',
        r'''\(\bs{X} = (X_1, X_2, \ldots, X_m)\)''',
    ),),
    74: ((
        r'''\( \sigma^2 / m + \sigma^2 / n \)''',
        r'''\( \sigma^2 / m + \tau^2 / n \)''',
    ),),
    139: (
        (
            r'''\( M(\bs{Y}) - M(\bs{X}) \gt \delta + t_{m+n-2}(1 - \alpha / 2) \sqrt{\sigma^2 / m + \tau^2 / n} \)''',
            r'''\( M(\bs{Y}) - M(\bs{X}) \gt \delta + t_{m+n-2}(1 - \alpha / 2) S(\bs{X}, \bs{Y}) \sqrt{1 / m + 1 / n} \)''',
        ),
        (
            r'''\( M(\bs{Y}) - M(\bs{X}) \lt \delta - t_{m+n-2}(1 - \alpha / 2) \sqrt{\sigma^2 / m + \tau^2 / n} \)''',
            r'''\( M(\bs{Y}) - M(\bs{X}) \lt \delta - t_{m+n-2}(1 - \alpha / 2) S(\bs{X}, \bs{Y}) \sqrt{1 / m + 1 / n} \)''',
        ),
    ),
    140: (
        (r'''\(T \le -t_{m-n+2}(1 - \alpha)\)''', r'''\(T \lt -t_{m+n-2}(1 - \alpha)\)'''),
        (
            r'''\( M(\bs{Y}) - M(\bs{X}) \lt \delta - t_{m+n-2}(1 - \alpha) \sqrt{\sigma^2 / m + \tau^2 / n} \)''',
            r'''\( M(\bs{Y}) - M(\bs{X}) \lt \delta - t_{m+n-2}(1 - \alpha) S(\bs{X}, \bs{Y}) \sqrt{1 / m + 1 / n} \)''',
        ),
    ),
    141: (
        (r'''\(T \ge t_{m-n+2}(1 - \alpha)\)''', r'''\(T \gt t_{m+n-2}(1 - \alpha)\)'''),
        (
            r'''\( M(\bs{Y}) - M(\bs{X}) \gt \delta + t_{m+n-2}(1 - \alpha) \sqrt{\sigma^2 / m + \tau^2 / n} \)''',
            r'''\( M(\bs{Y}) - M(\bs{X}) \gt \delta + t_{m+n-2}(1 - \alpha) S(\bs{X}, \bs{Y}) \sqrt{1 / m + 1 / n} \)''',
        ),
    ),
    152: ((
        r'''\( [M(\bs{Y}) - M(\bs{X})] - t_{m+n-2}(1 - \alpha / 2) \sqrt{\sigma^2 / m + \tau^2 / n} \le \delta \le [M(\bs{Y}) - M(\bs{X})] + t_{m+n-2}(1 - \alpha / 2) \sqrt{\sigma^2 / m + \tau^2 / n} \)''',
        r'''\( [M(\bs{Y}) - M(\bs{X})] - t_{m+n-2}(1 - \alpha / 2) S(\bs{X}, \bs{Y}) \sqrt{1 / m + 1 / n} \le \delta \le [M(\bs{Y}) - M(\bs{X})] + t_{m+n-2}(1 - \alpha / 2) S(\bs{X}, \bs{Y}) \sqrt{1 / m + 1 / n} \)''',
    ),),
    153: ((
        r'''\( \delta \le [M(\bs{Y}) - M(\bs{X})] + t_{m+n-2}(1 - \alpha) \sqrt{\sigma^2 / m + \tau^2 / n} \)''',
        r'''\( \delta \le [M(\bs{Y}) - M(\bs{X})] + t_{m+n-2}(1 - \alpha) S(\bs{X}, \bs{Y}) \sqrt{1 / m + 1 / n} \)''',
    ),),
    154: ((
        r'''\( \delta \ge [M(\bs{Y}) - M(\bs{X})] - t_{m+n-2}(1 - \alpha) \sqrt{\sigma^2 / m + \tau^2 / n} \)''',
        r'''\( \delta \ge [M(\bs{Y}) - M(\bs{X})] - t_{m+n-2}(1 - \alpha) S(\bs{X}, \bs{Y}) \sqrt{1 / m + 1 / n} \)''',
    ),),
    175: ((r'''\( \rho = \tau^2 / \rho^2 \)''', r'''\( \rho = \tau^2 / \sigma^2 \)'''),),
    177: (
        (r'''\( S^2(\bs{X}) \big/ \sigma^2 \)''', r'''\( (m - 1) S^2(\bs{X}) \big/ \sigma^2 \)'''),
        (r'''\( S^2(\bs{Y}) \big/ \tau^2 \)''', r'''\( (n - 1) S^2(\bs{Y}) \big/ \tau^2 \)'''),
    ),
    190: ((r'''\( f \)''', r'''\( F \)'''),),
    195: ((r'''\(\rho_0\)''', r'''\(\rho\)'''),),
    197: ((
        r'''\( \frac{S^2(\bs{Y})}{S^2(\bs{X})} F_{m-1,n-1}(\alpha / 2) \le \rho \le \frac{S^2(\bs{Y})}{S^2(\bs{X})} F_{m-1,n-1}(1 - \alpha / 2) \)''',
        r'''\( \frac{S^2(\bs{Y})}{S^2(\bs{X})} f_{m-1,n-1}(\alpha / 2) \le \rho \le \frac{S^2(\bs{Y})}{S^2(\bs{X})} f_{m-1,n-1}(1 - \alpha / 2) \)''',
    ),),
    198: ((
        r'''\(\rho \le \frac{S^2(\bs{Y})}{S^2(\bs{X})} F_{m-1,n-1}(\alpha) \)''',
        r'''\(\rho \ge \frac{S^2(\bs{Y})}{S^2(\bs{X})} f_{m-1,n-1}(\alpha) \)''',
    ),),
    199: ((
        r'''\( \rho \ge \frac{S^2(\bs{Y})}{S^2(\bs{X})} F_{m-1,n-1}(1 - \alpha) \)''',
        r'''\( \rho \le \frac{S^2(\bs{Y})}{S^2(\bs{X})} f_{m-1,n-1}(1 - \alpha) \)''',
    ),),
    250: ((r'''\(\pm 1.6625\)''', r'''\(1.2918\)'''),),
    268: (
        (r'''\(H_0: \mu_1 \le \mu_2\)''', r'''\(H_0: \mu_1 \ge \mu_2\)'''),
        (r'''\(\mu_1 \gt \mu_2\)''', r'''\(H_1: \mu_1 \lt \mu_2\)'''),
    ),
    274: (
        (r'''\(-11.4\)''', r'''\(-11.303\)'''),
        (r'''\(-1.6602\)''', r'''\(-1.2902\)'''),
    ),
    289: (
        (r'''\(-4.97\)''', r'''\(-2.500\)'''),
        (r'''\(\pm 1.645\)''', r'''\(\pm 1.6526\)'''),
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
    "https://www.randomservices.org/random/interval/index.html": "../interval/index.html",
    "https://www.randomservices.org/random/interval/BivariateNormal.html": "../interval/BivariateNormal.html",
    "https://www.randomservices.org/random/sample/Mean.html": "../sample/Mean.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
    "https://www.randomservices.org/random/sample/Normal.html": "../sample/Normal.html",
    "https://www.randomservices.org/random/sample/Covariance.html": "../sample/Covariance.html",
    "https://www.randomservices.org/random/data/Fisher.html": "https://www.randomservices.org/random/data/Iris.html",
    "https://www.randomservices.org/random/data/Iris.html": "https://www.randomservices.org/random/data/Iris.html",
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
    if sum(source_counts.values()) != 255:
        raise RuntimeError(f"unexpected parsed element count: {sum(source_counts.values())}")
    if [tag.name for tag in target.find_all(True)] != [tag.name for tag in source.find_all(True)]:
        raise RuntimeError("parsed element order changed")
    for selector, expected in (
        ("div.unit", 17),
        ("details", 13),
        ("summary", 13),
        ("h2,h3,h4", 7),
        ("img", 4),
        ("figure", 0),
    ):
        if len(target.select(selector)) != expected:
            raise RuntimeError(f"topology count mismatch for {selector}")
    source_ids = [tag["id"] for tag in source.find_all(id=True)]
    target_ids = [tag["id"] for tag in target.find_all(id=True)]
    if len(source_ids) != len(set(source_ids)) or len(target_ids) != len(set(target_ids)):
        raise RuntimeError("duplicate native/additive ID")
    expected_ids = set(source_ids) | {"o006.random.hypothesis.bivariate-normal.page"}
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
        "index.html", "Introduction.html", "Normal.html", "Bernoulli.html",
        "BivariateNormal.html", "Likelihood.html", "ChiSquare.html",
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
        if relative in planned_hypothesis:
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
    if len(source_math) != 300 or len(expected_math) != 300:
        raise RuntimeError("unexpected authority/repair math count")
    if target_math != expected_math:
        raise RuntimeError(
            f"protected-math mismatch: source={len(source_math)}, target={len(target_math)}"
        )

    source_p = (len(re.findall(r"<p(?:\s|>)", source_text)), source_text.count("</p>"))
    target_p = (len(re.findall(r"<p(?:\s|>)", rendered)), rendered.count("</p>"))
    if source_p != (41, 41) or target_p != (44, 44):
        raise RuntimeError(f"paragraph-tag mismatch: source={source_p}, target={target_p}")
    source_a = (len(re.findall(r"<a(?:\s|>)", source_text)), source_text.count("</a>"))
    target_a = (len(re.findall(r"<a(?:\s|>)", rendered)), rendered.count("</a>"))
    if source_a != (44, 44) or target_a != (48, 48):
        raise RuntimeError(f"anchor-tag mismatch: source={source_a}, target={target_a}")

    assert_topology(source_text, rendered)
    assert_links(rendered)

    for required in (
        'lang="id-ID"',
        'href="index.html"', 'href="Introduction.html"', 'href="Normal.html"',
        'href="Bernoulli.html"', 'href="Likelihood.html"', 'href="ChiSquare.html"',
        'href="../interval/BivariateNormal.html"', 'href="../sample/Mean.html"',
        'href="../sample/Variance.html"', 'href="../sample/Normal.html"',
        'href="../sample/Covariance.html"',
        'href="https://www.randomservices.org/random/data/Iris.html"',
        "OpenAI Codex gpt-5.6-sol, Ultra",
        'data-o006-edition-notice="v1"',
    ):
        if required not in rendered:
            raise RuntimeError(f"required translated surface missing: {required}")
    for forbidden in (
        'lang="en"', "JavaScript:openAncillary", ">Details:<",
        "Expand Details", "Contract Details", ">Hypothesis Testing<",
        ">Tests in the Two-Sample Normal Model<", ">Computational Exercises<",
        ">Apps<", ">Data Sets<", ">Biographies<", "impotrant",
        "for the for", "test statistc", "thoerem", "mormal ,odel",
        "as mean 10.3", "data/Fisher.html", "m-n+2",
        r"\rho_0", r"F_{m-1,n-1}", "Test statistic 1.0",
        "Probably not", r"\(-4.97\)",
        r"\(-11.4\)", "sekitar 1,1",
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
        "255 core elements / 17 units / 13 disclosures / 300 protected TeX spans"
    )


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
