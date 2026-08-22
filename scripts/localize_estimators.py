#!/usr/bin/env python3
"""Create the bounded id-ID Estimators target."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "point" / "Estimators.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "point" / "Estimators.html"
SOURCE_URL = "https://www.randomservices.org/random/point/Estimators.html"
SOURCE_SHA256 = "10914ffca9034209da0111918cfb534d60982bde0bba142a11d61d43114c6e2a"
EXPECTED_SOURCE_LINES = 492

MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)


# All mathematical changes are exact, independently checked target repairs.
# Every other protected TeX span is restored byte-for-byte from the authority.
MATH_CORRECTIONS: dict[tuple[int, int], tuple[str, str]] = {
    (78, 4): (r"\( \theta \in \Theta \)", r"\( \theta \in T \)"),
    (81, 1): (
        r"\(\bias(U) = E(U - \theta) = \E(U) - \theta \)",
        r"\(\bias(U) = \E(U - \theta) = \E(U) - \theta \)",
    ),
    (123, 3): (
        r"\(\bs{X} = (X_1, X_2, \ldots,)\)",
        r"\(\bs{X} = (X_1, X_2, \ldots)\)",
    ),
    (163, 1): (
        r"\[ |\E(U_n - \theta)| \le \E(|U_n - \theta|) \le \sqrt{\E[(U_n - \theta)]^2} \to 0 \text{ as } n \to \infty \]",
        r"\[ |\E(U_n - \theta)| \le \E(|U_n - \theta|) \le \sqrt{\E[(U_n - \theta)^2]} \to 0 \text{ ketika } n \to \infty \]",
    ),
    (192, 11): (
        r"\( (\P_n(A): n \in \N_+) \)",
        r"\( (P_n(A): n \in \N_+) \)",
    ),
    (239, 4): (r"\( T \)", r"\( [0, \infty) \)"),
    (244, 3): (r"\( \var(U) \gt 0 \)", r"\( \var(U) \ge 0 \)"),
    (244, 4): (
        r"\( [\E(U)]^2 \lt \theta^2 \)",
        r"\( [\E(U)]^2 \le \theta^2 \)",
    ),
    (244, 5): (r"\( \E(U) \lt \theta \)", r"\( \E(U) \le \theta \)"),
    (254, 17): (r"\( \rho \in [0, 1] \)", r"\( \rho \in [-1, 1] \)"),
    (294, 1): (r"\(U_n\)", r"\(W_n\)"),
    (294, 2): (r"\(V_n\)", r"\(S_n\)"),
    (294, 8): (r"\(V_n\)", r"\(S_n\)"),
    (294, 9): (r"\(U_n\)", r"\(W_n\)"),
    (331, 6): (r"\( n \in \N \)", r"\( n \in \N_+ \)"),
}


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Penduga</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, pendugaan titik, penduga tak bias, galat kuadrat rata-rata, penduga konsisten, rata-rata sampel, varians sampel, kovarians sampel, regresi linear, distribusi Poisson">''',
    38: r'''\t\t<li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>''',
    40: r'''\t\t<li class="child"><a href="Moments.html" title="Metode Momen">2</a></li>''',
    41: r'''\t\t<li class="child"><a href="Likelihood.html" title="Kemungkinan Maksimum">3</a></li>''',
    42: r'''\t\t<li class="child"><a href="Bayes.html" title="Penduga Bayes">4</a></li>''',
    43: r'''\t\t<li class="child"><a href="Unbiased.html" title="Penduga Tak Bias Terbaik">5</a></li>''',
    44: r'''\t\t<li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancilar">6</a></li>''',
    45: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    46: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    48: r'''\t<h2 id="o006.random.point.estimators.page">1. Penduga</h2>''',
    51: r'''<h3 id="o006.random.point.estimators.section.basic-statistical-model">Model Statistik Dasar</h3>''',
    53: r'''<p>Seperti biasa, titik awal kita adalah sebuah <a href="../prob/Experiments.html">eksperimen acak</a> yang dimodelkan oleh <a href="../prob/Probability2.html">ruang probabilitas</a> \((\Omega, \ms F, \P)\). Dalam model statistik dasar, kita memiliki <a href="../prob/Probability.html">variabel acak</a> teramati \(\bs{X}\) dengan nilai dalam suatu himpunan \(S\). Ingat bahwa, secara umum, variabel ini dapat memiliki struktur yang cukup rumit. Sebagai contoh, jika eksperimennya adalah mengambil sampel \(n\) objek dari suatu populasi dan mencatat berbagai pengukuran yang menjadi perhatian, maka vektor data berbentuk''',
    55: r'''dengan \(X_i\) merupakan vektor pengukuran untuk objek ke-\(i\). Kasus khusus yang paling penting adalah ketika \((X_1, X_2, \ldots, X_n)\) saling bebas dan berdistribusi identik (IID). Dalam hal ini, \(\bs{X}\) adalah <a href="../sample/Introduction.html">sampel acak</a> berukuran \(n\) dari distribusi suatu variabel pengukuran dasar \(X\).</p>''',
    57: r'''<h4 id="o006.random.point.estimators.section.statistics">Statistik</h4>''',
    59: r'''<p>Ingat pula bahwa <dfn>statistik</dfn> adalah variabel acak yang merupakan fungsi teramati dari variabel hasil eksperimen acak: \(\bs{U} = \bs{u}(\bs{X})\), dengan \( \bs{u} \) fungsi yang diketahui dari \( S \) ke suatu himpunan lain. Jadi, statistik hanyalah variabel acak yang diturunkan dari variabel pengamatan \(\bs{X}\), dengan asumsi bahwa \(\bs{U}\) juga teramati. Seperti ditunjukkan oleh notasinya, \(\bs{U}\) biasanya juga bernilai vektor. Perhatikan bahwa vektor data awal \(\bs{X}\) sendiri merupakan statistik, tetapi biasanya kita tertarik pada statistik yang diturunkan dari \(\bs{X}\). Statistik \(\bs{U}\) dapat dihitung untuk menjawab suatu pertanyaan inferensial. Dalam konteks ini, jika dimensi \(\bs{U}\) (sebagai vektor) lebih kecil daripada dimensi \(\bs{X}\) (seperti yang biasanya terjadi), maka kita telah mencapai <dfn>reduksi data</dfn>. Idealnya, kita ingin mencapai reduksi data yang berarti tanpa kehilangan informasi tentang pertanyaan inferensial yang sedang dikaji.</p>''',
    61: r'''<h4 id="o006.random.point.estimators.section.parameters">Parameter</h4>''',
    64: r'''\t<p class="dfn">Dalam pengertian teknis, <dfn>parameter</dfn> \(\bs{\theta}\) adalah fungsi dari <em>distribusi</em> \(\bs{X}\), dengan nilai dalam suatu himpunan \(T\).</p>''',
    66: r'''\t\t<p>Seperti biasa, \(T\) dilengkapi dengan suatu <a href="../foundations/Measurable.html">\(\sigma\)-aljabar</a> \(\ms T\) yang terdiri atas himpunan-himpunan bagian yang diperbolehkan, sehingga \((T, \ms T)\) merupakan <dfn>ruang parameter</dfn>.</p>''',
    70: r'''<p>Biasanya, distribusi \(\bs{X}\) memiliki \(k \in \N_+\) parameter riil yang menjadi perhatian, sehingga \(\bs{\theta}\) berbentuk \(\bs{\theta} = (\theta_1, \theta_2, \ldots, \theta_k)\) dan dengan demikian \(T \subseteq \R^k\). Dalam banyak kasus, satu atau lebih parameter tersebut tidak diketahui dan harus diduga dari variabel data \(\bs{X}\). Ini merupakan salah satu masalah terpenting dan paling mendasar dalam statistika, sekaligus pokok bahasan bab ini. Jika \( \bs{U} \) adalah suatu statistik, distribusi \( \bs{U} \) akan bergantung pada parameter \(\bs{X}\); demikian pula besaran distribusional seperti rata-rata, varians, kovarians, fungsi kepadatan probabilitas, dan sebagainya. Biasanya kita tidak menampakkan kebergantungan ini dalam notasi agar ekspresi matematis tidak menjadi terlalu rumit, tetapi penting untuk menyadari bahwa kebergantungan yang mendasarinya tetap ada. Gagasan utamanya adalah bahwa dengan mengamati suatu nilai \( \bs{u} \) dari statistik \( \bs{U} \), kita diharapkan memperoleh informasi tentang parameter yang tidak diketahui.</p>''',
    72: r'''<h4 id="est">Penduga</h4>''',
    74: r'''<p>Sekarang andaikan kita memiliki parameter riil yang tidak diketahui, \(\theta\), dengan nilai dalam ruang parameter \(T \subseteq \R\). Statistik bernilai riil \(U = u(\bs{X})\) yang digunakan untuk menduga \(\theta\) disebut <dfn>penduga</dfn> bagi \(\theta\). Jadi, penduga merupakan variabel acak dan karenanya memiliki distribusi, rata-rata, varians, dan seterusnya (semuanya, seperti telah disebutkan, pada umumnya bergantung pada \( \theta \)). Ketika kita benar-benar menjalankan eksperimen dan mengamati data \(\bs{x}\), nilai teramati \(u = ''',
    75: r'''u(\bs{x})\) (sebuah bilangan tunggal) adalah <dfn>dugaan</dfn> bagi parameter \(\theta\). Definisi-definisi berikut bersifat mendasar.</p>''',
    78: r'''\t<p class="dfn">Andaikan \( U \) adalah statistik yang digunakan sebagai penduga parameter \( \theta \) dengan nilai dalam \( T \subseteq \R \). Untuk \( \theta \in T \),</p>''',
    80: r'''\t\t<li>\( U - \theta \) adalah <dfn>galat</dfn>.</li>''',
    81: r'''\t\t<li>\(\bias(U) = \E(U - \theta) = \E(U) - \theta \) adalah <dfn>bias</dfn> \( U \).</li>''',
    82: r'''\t\t<li>\(\mse(U) = \E\left[(U - \theta)^2\right] \) adalah <dfn>galat kuadrat rata-rata</dfn> \( U \).</li>''',
    86: r'''<p>Jadi, galat adalah selisih antara penduga dan parameter yang diduga; tentu saja galat merupakan variabel acak. Bias \( U \) hanyalah nilai harapan galat, sedangkan galat kuadrat rata-rata adalah nilai harapan kuadrat galat. Perhatikan bahwa bias dan galat kuadrat rata-rata merupakan fungsi dari \( \theta \in T \). Definisi-definisi berikut melengkapi definisi bias secara alami.</p>''',
    89: r'''\t<p class="dfn">Andaikan kembali bahwa \( U \) adalah statistik yang digunakan sebagai penduga parameter \( \theta \) dengan nilai dalam \( T \subseteq \R \).</p>''',
    91: r'''\t\t<li>\(U\) <dfn>tak bias</dfn> jika \(\bias(U) = 0\), atau secara ekuivalen \(\E(U) = \theta\), untuk setiap \(\theta \in T\).</li>''',
    92: r'''\t\t<li>\(U\) <dfn>berbias negatif</dfn> jika \(\bias(U) \le 0\), atau secara ekuivalen \(\E(U) \le \theta\), untuk setiap \(\theta \in T\).</li>''',
    93: r'''\t\t<li>\(U\) <dfn>berbias positif</dfn> jika \(\bias(U) \ge 0\), atau secara ekuivalen \(\E(U) \ge \theta\), untuk setiap \(\theta \in T\).</li>''',
    97: r'''<p>Jadi, bagi penduga tak bias, nilai harapan penduga sama dengan parameter yang diduga; jelas ini merupakan sifat yang diinginkan. Di sisi lain, penduga berbias positif secara rata-rata menghasilkan dugaan yang terlalu tinggi, sedangkan penduga berbias negatif secara rata-rata menghasilkan dugaan yang terlalu rendah. Definisi bias negatif dan positif kita bersifat <em>lemah</em> karena menggunakan pertidaksamaan lemah \(\le\) dan \(\ge\). Tentu ada definisi ketat yang bersesuaian, dengan pertidaksamaan ketat \(\lt\) dan \(\gt\). Namun, perhatikan bahwa tidak satu pun dari definisi tersebut harus berlaku. Sebagai contoh, dapat terjadi bahwa \(\bias(U) \lt 0\) untuk sebagian \(\theta \in T\), \(\bias(U) = 0\) untuk sebagian \(\theta \in T\) lainnya, dan \(\bias(U) \gt 0\) untuk nilai \(\theta \in T\) yang lain lagi.</p>''',
    102: r'''\t\t<summary>Rincian:</summary>''',
    103: r'''\t\t<p>Hasil ini mengikuti sifat-sifat dasar nilai harapan dan varians:''',
    108: r'''<p>Khususnya, jika penduga tak bias, maka galat kuadrat rata-rata \(U\) sama dengan <a href="../expect/Variance.html">varians</a> \(U\).</p>''',
    110: r'''<p>Idealnya, kita ingin memiliki penduga tak bias dengan galat kuadrat rata-rata yang kecil. Namun, hal ini tidak selalu mungkin, dan <a href="#est3" class="ref"></a> menunjukkan hubungan yang rumit antara bias dan galat kuadrat rata-rata. Pada bagian berikutnya kita akan melihat contoh dua penduga suatu parameter yang merupakan kelipatan satu sama lain; yang satu tak bias, tetapi yang lain memiliki galat kuadrat rata-rata lebih kecil. Namun, jika kita memiliki dua penduga tak bias bagi \(\theta\), secara alami kita memilih penduga dengan varians (galat kuadrat rata-rata) yang lebih kecil.</p>''',
    113: r'''\t<p class="dfn">Andaikan \( U \) dan \( V \) adalah penduga tak bias bagi parameter \( \theta \) dengan nilai dalam \( T \subseteq \R \).</p>''',
    115: r'''\t\t<li>\( U \) <dfn>lebih efisien daripada</dfn> \( V \) jika \( \var(U) \le \var(V) \).</li>''',
    116: r'''\t\t<li><dfn>Efisiensi relatif</dfn> \(U\) terhadap \(V\) adalah''',
    121: r'''<h4 id="o006.random.point.estimators.section.asymptotic-properties">Sifat Asimtotik</h4>''',
    123: r'''<p>Andaikan kembali bahwa kita memiliki parameter riil \( \theta \) dengan nilai yang mungkin dalam ruang parameter \( T \). Dalam eksperimen statistik, kita sering mengamati barisan tak hingga variabel acak seiring waktu, \(\bs{X} = (X_1, X_2, \ldots)\), sehingga pada waktu \( n \) kita telah mengamati \( \bs{X}_n = (X_1, X_2, \ldots, X_n) \). Dalam keadaan ini, kita sering memiliki suatu rumus umum yang mendefinisikan penduga \(\theta\) untuk setiap ukuran sampel \(n\). Secara teknis, ini menghasilkan suatu <em>barisan</em> penduga bernilai riil bagi \(\theta\): \( \bs{U} = (U_1, U_2, \ldots) \), dengan \( U_n \) fungsi bernilai riil dari \( \bs{X}_n \) untuk setiap \( n \in \N_+ \). Dalam hal ini, kita dapat membahas sifat asimtotik penduga ketika \(n \to \infty\). Sebagian besar definisi berikut merupakan perumuman alami dari definisi sebelumnya.</p>''',
    126: r'''\t<p class="dfn">Barisan penduga \(\bs{U} = (U_1, U_2, \ldots)\) <dfn>tak bias secara asimtotik</dfn> jika \( \bias(U_n) \to 0\) ketika \(n \to \infty\) untuk setiap \(\theta \in T \), atau secara ekuivalen, \(\E(U_n) \to \theta\) ketika \(n \to \infty\) untuk setiap \(\theta \in T\).</p>''',
    130: r'''\t<p class="dfn">Andaikan \(\bs{U} = (U_1, U_2, \ldots)\) dan \(\bs{V} = (V_1, V_2, \ldots)\) adalah dua barisan penduga yang tak bias secara asimtotik. <dfn>Efisiensi relatif asimtotik</dfn> \(\bs{U}\) terhadap \(\bs{V}\) adalah''',
    132: r'''\tdengan asumsi bahwa limit tersebut ada.</p>''',
    135: r'''<p>Secara alami, kita mengharapkan penduga membaik ketika ukuran sampel \(n\) bertambah dan, dalam suatu pengertian, konvergen menuju parameter ketika \( n \to \infty \). Gagasan umum ini dikenal sebagai <em>konsistensi</em>. Sekali lagi, untuk pembahasan selanjutnya kita mengasumsikan bahwa \(\bs{U} = (U_1, U_2, \ldots)\) adalah barisan penduga bagi parameter bernilai riil \( \theta \), dengan nilai dalam ruang parameter \( T \).</p>''',
    138: r'''\t<p class="dfn">Konsistensi</p>''',
    140: r'''\t\t<li>\( \bs{U} \) <dfn>konsisten</dfn> jika \(U_n \to \theta\) ketika \(n \to \infty\) <a href="../prob/Convergence.html">dalam probabilitas</a> untuk setiap \(\theta \in T\). Artinya, \( \P\left(\left|U_n - \theta\right| \gt \epsilon\right) \to 0\) ketika \(n \to \infty\) untuk setiap \(\epsilon \gt 0\) dan \(\theta \in T\).</li>''',
    141: r'''\t\t<li>\( \bs{U} \) <dfn>konsisten dalam kuadrat rata-rata</dfn> jika \( \mse(U_n) = \E[(U_n - \theta)^2] \to 0 \) ketika \( n \to \infty \) untuk setiap \( \theta \in T \).</li>''',
    145: r'''<p>Berikut adalah hubungan antara kedua definisi tersebut:</p>''',
    148: r'''\t<p class="math">Jika \( \bs{U} \) konsisten dalam kuadrat rata-rata, maka \(\bs{U}\) konsisten.</p>''',
    150: r'''\t\t<summary>Rincian:</summary>''',
    151: r'''\t\t<p>Dari <a href="../expect/Properties2.html#mar">ketaksamaan Markov</a>,''',
    156: r'''<p>Fakta bahwa konsistensi dalam kuadrat rata-rata mengakibatkan konsistensi biasa hanyalah versi statistik dari teorema yang menyatakan bahwa <a href="../expect/Variance.html">konvergensi dalam kuadrat rata-rata</a> mengakibatkan konvergensi dalam probabilitas. Berikut satu lagi akibat penting dari konsistensi dalam kuadrat rata-rata.</p>''',
    159: r'''\t<p class="math">Jika \( \bs{U} \) konsisten dalam kuadrat rata-rata, maka \( \bs{U} \) tak bias secara asimtotik.</p>''',
    161: r'''\t\t<summary>Rincian:</summary>''',
    162: r'''\t\t<p>Hasil ini mengikuti fakta bahwa galat absolut rata-rata lebih kecil daripada akar galat kuadrat rata-rata, yang merupakan kasus khusus suatu hasil umum tentang norma. Lihat bagian mengenai <a href="../expect/Spaces.html">ruang vektor</a> untuk perincian lebih lanjut. Dengan menggunakan hasil ini dan ketaksamaan segitiga biasa untuk nilai harapan, kita peroleh''',
    163: r'''\t\t\[ |\E(U_n - \theta)| \le \E(|U_n - \theta|) \le \sqrt{\E[(U_n - \theta)^2]} \to 0 \text{ ketika } n \to \infty \]''',
    164: r'''\t\tDengan demikian \( \E(U_n) \to \theta \) ketika \( n \to \infty \) untuk \( \theta \in T \).</p>''',
    168: r'''<p>Dalam beberapa subbagian berikutnya, kita akan meninjau kembali beberapa masalah dasar pendugaan yang dipelajari dalam bab mengenai <a href="../sample/index.html">sampel acak</a>.</p>''',
    170: r'''<h3 id="o006.random.point.estimators.section.single-variable-model">Pendugaan dalam Model Variabel Tunggal</h3>''',
    172: r'''<p>Andaikan \( X \) adalah variabel acak dasar bernilai riil untuk suatu eksperimen, dengan rata-rata \( \mu \in \R\) dan varians \( \sigma^2 \in (0, \infty) \). Kita mengambil sampel dari distribusi \( X \) untuk menghasilkan barisan \(\bs{X} = (X_1, X_2, \ldots)\) variabel-variabel yang saling bebas, masing-masing dengan distribusi \( X \). Untuk setiap \( n \in \N_+ \), \( \bs{X}_n = (X_1, X_2, \ldots, X_n) \) merupakan sampel acak berukuran \(n\) dari distribusi \(X\).</p>''',
    174: r'''<h4 id="mea">Menduga Rata-Rata</h4>''',
    176: r'''<p>Subbagian ini meninjau kembali beberapa hasil yang diperoleh dalam bagian mengenai <a href="../sample/LLN.html">hukum bilangan besar</a>. Ingat bahwa penduga alami bagi rata-rata distribusi \(\mu\) adalah <a href="../sample/LLN.html">rata-rata sampel</a>, yang didefinisikan oleh''',
    180: r'''\t<p class="math">Sifat-sifat \( \bs M = (M_1, M_2, \ldots) \) sebagai barisan penduga bagi \( \mu \).</p>''',
    182: r'''\t\t<li>\(\E(M_n) = \mu\), sehingga \(M_n\) tak bias untuk \( n \in \N_+ \).</li>''',
    183: r'''\t\t<li>\(\var(M_n) = \sigma^2 / n\) untuk \( n \in \N_+ \), sehingga \( \bs M \) konsisten.</li>''',
    187: r'''<p>Konsistensi \(\bs M\) tidak lain adalah <a href="../sample/LLN.html">hukum lemah bilangan besar</a>. Selain itu, terdapat sejumlah kasus khusus penting dari <a href="#mea1" class="ref"></a>. Lihat bagian mengenai <a href="../sample/Mean.html">rata-rata sampel</a> untuk perinciannya.</p>''',
    190: r'''\t<p class="math">Kasus-kasus khusus rata-rata sampel</p>''',
    192: r'''\t\t<li>Andaikan \(X = \bs{1}_A\), variabel indikator bagi suatu kejadian \(A\) yang memiliki probabilitas \(\P(A)\). Maka rata-rata sampel dari sampel acak berukuran \( n \in \N_+ \) yang berasal dari distribusi \( X \) adalah <dfn>frekuensi relatif</dfn> atau <dfn>probabilitas empiris</dfn> bagi \(A\), yang dilambangkan \(P_n(A)\). Dengan demikian, \(P_n(A)\) merupakan penduga tak bias bagi \( \P(A) \) untuk \( n \in \N_+ \), dan \( (P_n(A): n \in \N_+) \) konsisten.</li>''',
    193: r'''\t\t<li>Andaikan \(F\) menyatakan fungsi distribusi suatu variabel acak bernilai riil \(Y\). Untuk \(y \in \R\) yang tetap, <dfn>fungsi distribusi empiris</dfn> \(F_n(y)\) hanyalah rata-rata sampel dari sampel acak berukuran \(n \in \N_+\) yang berasal dari distribusi variabel indikator \(X = \bs{1}(Y \le y)\). Dengan demikian, \(F_n(y)\) merupakan penduga tak bias bagi \( F(y) \) untuk \( n \in \N_+ \), dan \( (F_n(y): n \in \N_+) \) konsisten.</li>''',
    194: r'''\t\t<li>Andaikan \(U\) adalah variabel acak dengan distribusi diskret pada suatu himpunan terhitung \(S\), dan \(f\) menyatakan fungsi kepadatan probabilitas \(U\). Untuk \(u \in S\) yang tetap, <dfn>fungsi kepadatan probabilitas empiris</dfn> \(f_n(u)\) hanyalah rata-rata sampel dari sampel acak berukuran \(n \in \N_+\) yang berasal dari distribusi variabel indikator \(X = \bs{1}(U = u)\). Dengan demikian, \(f_n(u)\) merupakan penduga tak bias bagi \( f(u) \) untuk \( n \in \N_+ \), dan \( (f_n(u): n \in \N_+) \) konsisten.</li>''',
    198: r'''<h4 id="o006.random.point.estimators.section.estimating-variance">Menduga Varians</h4>''',
    200: r'''<p>Subbagian ini meninjau kembali beberapa hasil yang diperoleh dalam bagian mengenai <a href="../sample/Variance.html">varians sampel</a>. Kita juga mengasumsikan bahwa momen pusat keempat \(\sigma_4 = \E\left[(X - \mu)^4\right]\) berhingga. Ingat bahwa \(\sigma_4 / \sigma^4\) adalah <a href="../expect/Skew.html#kur">kurtosis</a> \(X\). Ingat pula bahwa jika \(\mu\) diketahui (hampir selalu merupakan asumsi artifisial), penduga alami bagi \(\sigma^2\) adalah suatu versi khusus <a href="../sample/Variance.html">varians sampel</a>, yang didefinisikan oleh''',
    204: r'''\t<p class="math">Sifat-sifat \( \bs W^2 = (W_1^2, W_2^2, \ldots) \) sebagai barisan penduga bagi \( \sigma^2 \).</p>''',
    206: r'''\t\t<li>\(\E\left(W_n^2\right) = \sigma^2\), sehingga \(W_n^2\) tak bias untuk \( n \in \N_+ \).</li>''',
    207: r'''\t\t<li>\(\var\left(W_n^2\right) = \frac{1}{n}(\sigma_4 - \sigma^4)\) untuk \( n \in \N_+ \), sehingga \(\bs W^2\) konsisten.</li>''',
    210: r'''\t\t<summary>Rincian:</summary>''',
    211: r'''\t\t<p>\( \bs W^2 \) bersesuaian dengan pengambilan sampel dari distribusi \( (X - \mu)^2 \). Distribusi ini memiliki rata-rata \( \sigma^2 \) dan varians \( \sigma_4 - \sigma^4 \), sehingga hasil tersebut langsung mengikuti <a href="#mea1" class="ref"></a>.</p>''',
    215: r'''<p>Jika \(\mu\) tidak diketahui (asumsi yang lebih masuk akal), penduga alami bagi varians distribusi adalah versi standar <a href="../sample/Variance.html">varians sampel</a>, yang didefinisikan oleh''',
    219: r'''\t<p class="math">Sifat-sifat \( \bs S^2 = (S_2^2, S_3^2, \ldots) \) sebagai barisan penduga bagi \( \sigma^2 \).</p>''',
    221: r'''\t\t<li>\(\E\left(S_n^2\right) = \sigma^2\), sehingga \(S_n^2\) tak bias untuk \( n \in \{2, 3, \ldots\} \).</li>''',
    222: r'''\t\t<li>\(\var\left(S_n^2\right) = \frac{1}{n} \left(\sigma_4 - \frac{n - 3}{n - 1} \sigma^4 \right)\) untuk \( n \in \{2, 3, \ldots\} \), sehingga \(\bs S^2\) merupakan barisan yang konsisten.</li>''',
    226: r'''<p>Secara alami, kita ingin membandingkan barisan \( \bs W^2 \) dan \( \bs S^2 \) sebagai penduga bagi \( \sigma^2 \). Namun, ingat kembali bahwa \( \bs W^2 \) hanya masuk akal jika \( \mu \) diketahui.</p>''',
    229: r'''\t<p class="math">Perbandingan \( \bs W^2 \) dan \( \bs S^2 \)</p>''',
    231: r'''\t\t<li>\(\var\left(W_n^2\right) \lt \var(S_n^2)\) untuk \( n \in \{2, 3, \ldots\} \).</li>''',
    232: r'''\t\t<li>Efisiensi relatif asimtotik \(\bs W^2\) terhadap \(\bs S^2\) adalah 1.</li>''',
    236: r'''<p>Jadi, menurut bagian (a) dari <a href="#comp" class="ref"></a>, \(W_n^2\) lebih baik daripada \(S_n^2\) untuk \( n \in \{2, 3, \ldots\} \), dengan asumsi bahwa \(\mu\) diketahui sehingga kita benar-benar dapat <em>menggunakan</em> \(W_n^2\). Hal ini mungkin tidak mengejutkan, tetapi menurut bagian (b), \(S_n^2\) bekerja hampir sebaik \(W_n^2\) untuk ukuran sampel \( n \) yang besar. Tentu saja, simpangan baku sampel \(S_n\) merupakan penduga alami bagi simpangan baku distribusi \(\sigma\). Sayangnya, penduga ini berbias. Berikut hasil yang lebih umum:</p>''',
    239: r'''\t<p class="math">Andaikan \( \theta \) adalah parameter dengan nilai yang mungkin dalam \(T \subseteq (0, \infty) \), dan \( U \) adalah statistik dengan nilai dalam \( [0, \infty) \). Jika \( U^2 \) merupakan penduga tak bias bagi \( \theta^2 \), maka \( U \) merupakan penduga berbias negatif bagi \( \theta \).</p>''',
    241: r'''\t\t<summary>Rincian:</summary>''',
    242: r'''\t\t<p>Perhatikan bahwa''',
    244: r'''\t\tKarena \( T \) hanya memuat nilai parameter positif dan \( U \) bernilai nonnegatif, nilai harapannya juga nonnegatif. Selain itu, \( \var(U) \ge 0 \), sehingga \( [\E(U)]^2 \le \theta^2 \). Oleh karena itu, \( \E(U) \le \theta \) untuk setiap \( \theta \in T \).</p>''',
    248: r'''<p>Jadi, kita tidak seharusnya terlalu terpaku pada sifat tak bias. Bagi kebanyakan distribusi penarikan sampel, tidak akan ada statistik \(U\) dengan sifat bahwa \(U\) merupakan penduga tak bias bagi \(\sigma\) dan \(U^2\) merupakan penduga tak bias bagi \(\sigma^2\).</p>''',
    250: r'''<h3 id="o006.random.point.estimators.section.bivariate-model">Pendugaan dalam Model Bivariat</h3>''',
    252: r'''<p>Dalam subbagian ini, kita meninjau kembali beberapa hasil yang diperoleh dalam bagian mengenai <a href="../sample/Covariance.html">korelasi dan regresi</a>.</p>''',
    254: r'''<p>Andaikan \( X \) dan \( Y \) adalah variabel acak bernilai riil untuk suatu eksperimen, sehingga \( (X, Y) \) memiliki distribusi bivariat pada \( \R^2 \). Misalkan \( \mu = \E(X)\) dan \( \sigma^2 = \var(X) \) masing-masing menyatakan rata-rata dan varians \( X \), serta \( \nu = \E(Y) \) dan \( \tau^2 = \var(Y) \) masing-masing menyatakan rata-rata dan varians \( Y \). Untuk parameter bivariat, misalkan \( \delta = \cov(X, Y) \) menyatakan kovarians distribusi dan \( \rho = \cor(X, Y) \) menyatakan korelasi distribusi. Kita juga memerlukan satu momen berorde lebih tinggi: misalkan \( \delta_2 = \E\left[(X - \mu)^2 (Y - \nu)^2\right] \), dan seperti biasa kita mengasumsikan bahwa semua parameter tersebut ada. Jadi, ruang parameter umumnya adalah \( \mu, \, \nu \in \R \), \( \sigma^2, \, \tau^2 \in (0, \infty) \), \( \delta \in \R \), dan \( \rho \in [-1, 1] \). Sekarang andaikan kita mengambil sampel dari distribusi \( (X, Y) \) untuk menghasilkan barisan variabel-variabel bebas \(\left((X_1, Y_1), (X_2, Y_2), \ldots\right)\), yang masing-masing memiliki distribusi \( (X, Y) \). Seperti biasa, kita tuliskan \(\bs{X}_n = (X_1, X_2, \ldots, X_n)\) dan \(\bs{Y}_n = (Y_1, Y_2, \ldots, Y_n)\); keduanya masing-masing merupakan sampel acak berukuran \(n\) dari distribusi \(X\) dan \(Y\). Karena sekarang kita memiliki dua variabel dasar, notasi kita perlu sedikit diperluas.</p>''',
    256: r'''<h4 id="o006.random.point.estimators.section.estimating-covariance">Menduga Kovarians</h4>''',
    258: r'''<p>Jika \(\mu\) dan \(\nu\) diketahui (hampir selalu merupakan asumsi artifisial), penduga alami bagi kovarians distribusi \(\delta\) adalah suatu versi khusus kovarians sampel, yang didefinisikan oleh''',
    262: r'''\t<p class="math">Sifat-sifat \( \bs W = (W_1, W_2, \ldots) \) sebagai barisan penduga bagi \( \delta \).</p>''',
    264: r'''\t\t<li>\(\E\left(W_n\right) = \delta\), sehingga \(W_n\) tak bias untuk \( n \in \N_+ \).</li>''',
    265: r'''\t\t<li>\( \var\left(W_n\right) = \frac{1}{n}(\delta_2 - \delta^2) \) untuk \( n \in \N_+ \), sehingga \(\bs W\) konsisten.</li>''',
    268: r'''\t\t<summary>Rincian:</summary>''',
    269: r'''\t\t<p>Bukti ini sudah pernah kita kerjakan, tetapi begitu mendasar sehingga layak diulang. Perhatikan bahwa \( \bs W \) bersesuaian dengan pengambilan sampel dari distribusi \( (X - \mu) (Y - \nu) \). Distribusi ini memiliki rata-rata \( \delta \) dan varians \( \delta_2 - \delta^2 \), sehingga hasil-hasil tersebut segera mengikuti dari <a href="#mea1" class="ref"></a>.</p>''',
    273: r'''<p>Jika \(\mu\) dan \(\nu\) tidak diketahui (yang biasanya merupakan asumsi lebih masuk akal), penduga alami bagi kovarians distribusi \(\delta\) adalah bentuk baku kovarians sampel, yang didefinisikan oleh''',
    277: r'''\t<p class="math">Sifat-sifat \( \bs S = (S_2, S_3, \ldots) \) sebagai barisan penduga bagi \( \delta \).</p>''',
    279: r'''\t\t<li>\(\E\left(S_n\right) = \delta\), sehingga \( S_n \) tak bias untuk \( n \in \{2, 3, \ldots\} \).</li>''',
    280: r'''\t\t<li>\( \var\left(S_n\right) = \frac{1}{n}\left(\delta_2 + \frac{1}{n - 1} \sigma^2 \tau^2 - \frac{n - 2}{n - 1} \delta^2\right) \) untuk \( n \in \{2, 3, \ldots\} \), sehingga \(\bs S\) konsisten.</li>''',
    284: r'''<p>Sekali lagi, karena kita memiliki dua barisan penduga yang bersaing bagi \( \delta \), kita ingin membandingkan keduanya.</p>''',
    287: r'''\t<p class="math">Perbandingan \(\bs W\) dan \(\bs S\) sebagai penduga bagi \(\delta\):</p>''',
    289: r'''\t\t<li>\(\var\left(W_n\right) \lt \var\left(S_n\right)\) untuk \( n \in \{2, 3, \ldots\} \).</li>''',
    290: r'''\t\t<li>Efisiensi relatif asimtotik \(\bs W\) terhadap \(\bs S\) adalah 1.</li>''',
    294: r'''<p>Jadi, \(W_n\) lebih baik daripada \(S_n\) untuk \( n \in \{2, 3, \ldots\} \), dengan asumsi bahwa \(\mu\) dan \( \nu \) diketahui sehingga kita benar-benar dapat <em>menggunakan</em> \(W_n\). Namun, untuk \( n \) besar, \(S_n\) bekerja hampir sama baiknya dengan \(W_n\).</p>''',
    296: r'''<h4 id="o006.random.point.estimators.section.estimating-correlation">Menduga Korelasi</h4>''',
    298: r'''<p>Penduga alami bagi korelasi distribusi \(\rho\) adalah korelasi sampel''',
    300: r'''Perhatikan bahwa statistik ini merupakan fungsi nonlinear dari kovarians sampel dan kedua simpangan baku sampel. Rasio di atas digunakan ketika hasil kali kedua simpangan baku sampel positif; ketika hasil kali itu nol, tetapkan statistiknya bernilai 0. Karena kedua varians sampel konvergen hampir pasti menuju varians distribusi yang positif, definisi pada kejadian berpenyebut nol ini tidak memengaruhi limit. Untuk sebagian besar distribusi \((X, Y)\), hampir mustahil menghitung bias atau galat kuadrat rata-rata penduga ini. Jika kita <em>dapat</em> menghitung nilai harapannya, kemungkinan besar kita akan mendapati bahwa penduga ini berbias. Di sisi lain, meskipun kita tidak dapat menghitung galat kuadrat rata-ratanya, penerapan sederhana hukum bilangan besar menunjukkan bahwa \(R_n \to \rho\) ketika \(n \to \infty\) dengan probabilitas 1. Jadi, \( \bs R = (R_2, R_3, \ldots) \) setidaknya konsisten.</p>''',
    302: r'''<h4 id="o006.random.point.estimators.section.estimating-regression-coefficients">Menduga Koefisien Regresi</h4>''',
    304: r'''<p>Ingat bahwa <a href="../expect/Covariance.html#blp">garis regresi distribusi</a>, dengan \(X\) sebagai variabel prediktor dan \(Y\) sebagai variabel respons, adalah \(y = a + b \, x\), dengan''',
    306: r'''Di sisi lain, garis regresi sampel berdasarkan sampel berukuran \( n \in \{2, 3, \ldots\} \) adalah \(y = A_n + B_n x\), dengan''',
    308: r'''Tentu saja, statistik \(A_n\) dan \(B_n\) masing-masing merupakan penduga alami bagi parameter \(a\) dan \(b\), dan dalam arti tertentu diturunkan dari penduga-penduga kita sebelumnya bagi rata-rata, varians, dan kovarians distribusi. Rumus di atas digunakan ketika varians sampel prediktor positif; ketika varians itu nol, tetapkan kedua statistik pada nilai tetap yang sembarang. Karena varians sampel prediktor konvergen hampir pasti menuju varians distribusi yang positif, definisi pada kejadian berpenyebut nol ini tidak memengaruhi limit. Sekali lagi, untuk sebagian besar distribusi \((X, Y)\), bias dan galat kuadrat rata-rata penduga-penduga ini sulit dihitung. Namun, penerapan hukum bilangan besar menunjukkan bahwa, dengan probabilitas 1, \( A_n \to a \) dan \( B_n \to b \) ketika \( n \to \infty \). Jadi, setidaknya \( \bs A = (A_2, A_3, \ldots) \) dan \( \bs B = (B_2, B_3, \ldots) \) konsisten.</p>''',
    310: r'''<h3 id="o006.random.point.estimators.section.exercises-and-special-cases">Latihan dan Kasus Khusus</h3>''',
    312: r'''<h4 id="poi">Distribusi Poisson</h4>''',
    314: r'''<p>Mari kita bahas sebuah contoh sederhana yang menggambarkan beberapa gagasan di atas. Ingat bahwa <a href="../poisson/Poisson.html">distribusi Poisson</a> dengan parameter \(\lambda \in (0, \infty)\) memiliki fungsi kepadatan probabilitas \(g\) yang diberikan oleh''',
    316: r'''Distribusi Poisson sering digunakan untuk memodelkan banyaknya <q>titik</q> acak dalam suatu wilayah waktu atau ruang, khususnya dalam konteks <a href="../poisson/index.html">proses Poisson</a>. Parameter \(\lambda\) sebanding dengan ukuran wilayah waktu atau ruang tersebut; konstanta kesebandingannya adalah <dfn>laju</dfn> rata-rata titik-titik acak. Distribusi ini dinamai menurut <a href="JavaScript:openAncillary('../biographies/Poisson.html')" class="ancillary">Simeon Poisson</a>.</p>''',
    319: r'''\t<p class="math">Misalkan \(X\) berdistribusi Poisson dengan parameter \(\lambda\). Maka</p>''',
    326: r'''\t\t<summary>Rincian:</summary>''',
    327: r'''\t\t<p>Ingat notasi permutasi \( x^{(n)} = x (x - 1) \cdots (x - n + 1) \) untuk \( x \in \R \) dan \( n \in \N \). Nilai harapan \( \E[X^{(n)}] \) adalah <dfn>momen faktorial</dfn> \( X \) berorde \( n \). Mudah dilihat bahwa momen-momen faktorialnya adalah \( \E\left[X^{(n)}\right] = \lambda^n \) untuk \( n \in \N \). Hasil-hasil di atas mengikuti fakta ini.</p>''',
    331: r'''<p>Sekarang, misalkan kita mengambil sampel dari distribusi \( X \) untuk menghasilkan barisan variabel acak independen \( \bs{X} = (X_1, X_2, \ldots) \), yang masing-masing berdistribusi Poisson dengan parameter tak diketahui \( \lambda \in (0, \infty) \). Sekali lagi, \(\bs{X}_n = (X_1, X_2, \ldots, X_n)\) merupakan sampel acak berukuran \(n \in \N_+\) dari distribusi tersebut untuk setiap \( n \in \N_+ \). Dari latihan sebelumnya, \(\lambda\) merupakan rata-rata sekaligus varians distribusi, sehingga kita dapat menggunakan rata-rata sampel \(M_n\) atau varians sampel \(S_n^2\) sebagai penduga bagi \(\lambda\). Keduanya tak bias, jadi manakah yang lebih baik? Secara alami, kita menggunakan galat kuadrat rata-rata sebagai kriteria.</p>''',
    334: r'''\t<p class="math">Perbandingan \(\bs M\) dengan \(\bs S^2\) sebagai penduga bagi \(\lambda\).</p>''',
    336: r'''\t\t<li>\(\var\left(M_n\right) = \frac{\lambda}{n}\) untuk \( n \in \N_+ \).</li>''',
    337: r'''\t\t<li>\(\var\left(S_n^2\right) = \frac{\lambda}{n} \left(1 + 2 \lambda \frac{n}{n - 1} \right)\) untuk \( n \in \{2, 3, \ldots\} \).</li>''',
    338: r'''\t\t<li>\(\var\left(M_n\right) \lt \var\left(S_n^2\right)\), sehingga \( M_n \) lebih efisien daripada penduga varians sampel untuk \( n \in \{2, 3, \ldots\} \).</li>''',
    339: r'''\t\t<li>Efisiensi relatif asimtotik \(\bs M\) terhadap \(\bs S^2\) adalah \(1 + 2 \lambda\).</li>''',
    343: r'''<p>Jadi, kesimpulan kita adalah bahwa rata-rata sampel \(M_n\) merupakan penduga yang lebih baik bagi parameter \(\lambda\) daripada varians sampel \(S_n^2\) untuk \( n \in \{2, 3, \ldots\} \), dan perbedaan kualitasnya meningkat bersama \(\lambda\).</p>''',
    346: r'''\t<p class="app">Jalankan <a href="JavaScript:openAncillary('../apps/Poisson.html')" class="ancillary">eksperimen Poisson</a> sebanyak 100 kali untuk beberapa nilai parameter. Dalam setiap kasus, hitung penduga \(M\) dan \(S^2\). Penduga mana yang tampaknya bekerja lebih baik?</p>''',
    350: r'''\t<p class="stat">Emisi partikel elementer dari suatu sampel bahan radioaktif dalam selang waktu tertentu sering diasumsikan mengikuti distribusi Poisson. Oleh karena itu, misalkan <a href="JavaScript:openAncillary('../data/Alpha.html')" class="ancillary">himpunan data emisi alfa</a> merupakan sampel dari distribusi Poisson. Duga parameter laju \(\lambda\).</p>''',
    352: r'''\t\t<li>dengan menggunakan rata-rata sampel</li>''',
    353: r'''\t\t<li>dengan menggunakan varians sampel</li>''',
    356: r'''\t\t<summary>Rincian:</summary>''',
    364: r'''<h4 id="o006.random.point.estimators.section.simulation-exercises">Latihan Simulasi</h4>''',
    367: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/MeanEstimate.html')" class="ancillary">eksperimen rata-rata sampel</a>, tetapkan distribusi penarikan sampel menjadi gamma. Tingkatkan ukuran sampel dengan bilah geser dan amati secara grafis maupun numerik sifat tak bias dan konsistennya. Jalankan eksperimen sebanyak 1.000 kali dan bandingkan rata-rata sampel dengan rata-rata distribusi.</p>''',
    371: r'''\t<p class="app">Jalankan <a href="JavaScript:openAncillary('../apps/NormalEstimate.html')" class="ancillary">eksperimen pendugaan pada distribusi normal</a> sebanyak 1.000 kali untuk beberapa nilai parameter.</p>''',
    373: r'''\t\t<li>Bandingkan bias empiris dan galat kuadrat rata-rata \(M\) dengan nilai-nilai teoretisnya.</li>''',
    374: r'''\t\t<li>Bandingkan bias empiris dan galat kuadrat rata-rata \(S^2\) serta \(W^2\) dengan nilai-nilai teoretisnya. Penduga mana yang tampaknya bekerja lebih baik?</li>''',
    379: r'''\t<p class="app">Dalam <a href="JavaScript:openAncillary('../apps/Match.html')" class="ancillary">eksperimen pencocokan</a>, variabel acaknya adalah banyaknya kecocokan. Jalankan simulasi sebanyak 1.000 kali dan bandingkan</p>''',
    381: r'''\t\t<li>rata-rata sampel dengan rata-rata distribusi.</li>''',
    382: r'''\t\t<li>fungsi kepadatan empiris dengan fungsi kepadatan probabilitas.</li>''',
    387: r'''\t<p class="app">Jalankan <a href="JavaScript:openAncillary('../apps/ExponentialExperiment.html')" class="ancillary">eksperimen eksponensial</a> sebanyak 1.000 kali dan bandingkan simpangan baku sampel dengan simpangan baku distribusi.</p>''',
    390: r'''<h4 id="o006.random.point.estimators.section.data-analysis-exercises">Latihan Analisis Data</h4>''',
    393: r'''\t<p class="stat">Untuk <a href="JavaScript:openAncillary('../data/Michelson.html')" class="ancillary">data kelajuan cahaya Michelson</a>, hitung rata-rata sampel dan varians sampel.</p>''',
    395: r'''\t\t<summary>Rincian:</summary>''',
    401: r'''\t<p class="stat">Untuk <a href="JavaScript:openAncillary('../data/Cavendish.html')" class="ancillary">data densitas Bumi Cavendish</a>, hitung rata-rata sampel dan varians sampel.</p>''',
    403: r'''\t\t<summary>Rincian:</summary>''',
    409: r'''\t<p class="stat">Untuk <a href="JavaScript:openAncillary('../data/Short.html')" class="ancillary">data paralaks matahari Short</a>, hitung rata-rata sampel dan varians sampel.</p>''',
    411: r'''\t\t<summary>Rincian:</summary>''',
    417: r'''\t<p class="stat">Pertimbangkan <a href="JavaScript:openAncillary('../data/Cicada.html')" class="ancillary">data Cicada</a>.</p>''',
    419: r'''\t\t<li>Hitung rata-rata sampel dan varians sampel variabel panjang tubuh.</li>''',
    420: r'''\t\t<li>Hitung rata-rata sampel dan varians sampel variabel berat tubuh.</li>''',
    421: r'''\t\t<li>Hitung kovarians sampel dan korelasi sampel antara variabel panjang tubuh dan berat tubuh.</li>''',
    424: r'''\t\t<summary>Rincian:</summary>''',
    434: r'''\t<p class="stat">Pertimbangkan <a href="JavaScript:openAncillary('../data/MM.html')" class="ancillary">data M&amp;M</a>.</p>''',
    436: r'''\t\t<li>Hitung rata-rata sampel dan varians sampel variabel berat bersih.</li>''',
    437: r'''\t\t<li>Hitung rata-rata sampel dan varians sampel jumlah total permen.</li>''',
    438: r'''\t\t<li>Hitung kovarians sampel dan korelasi sampel antara jumlah permen dan berat bersih.</li>''',
    441: r'''\t\t<summary>Rincian:</summary>''',
    443: r'''\t\t\t<li>49.215, 2.3163</li>''',
    444: r'''\t\t\t<li>57.1, 5.68</li>''',
    451: r'''\t<p class="stat">Pertimbangkan <a href="JavaScript:openAncillary('../data/Pearson.html')" class="ancillary">data tinggi badan Pearson</a>.</p>''',
    453: r'''\t\t<li>Hitung rata-rata sampel dan varians sampel tinggi badan ayah.</li>''',
    454: r'''\t\t<li>Hitung rata-rata sampel dan varians sampel tinggi badan anak laki-laki.</li>''',
    455: r'''\t\t<li>Hitung kovarians sampel dan korelasi sampel antara tinggi badan ayah dan tinggi badan anak laki-laki.</li>''',
    458: r'''\t\t<summary>Rincian:</summary>''',
    467: r'''<p>Penduga rata-rata, varians, dan kovarians yang telah kita bahas dalam bagian ini dapat dianggap alami dalam arti tertentu. Namun, untuk parameter lain, belum tentu jelas cara menemukan penduga yang masuk akal. Dalam beberapa bagian berikutnya, kita akan membahas masalah konstruksi penduga. Setelah itu, kita kembali mempelajari sifat-sifat matematis penduga dan menelaah kapan kita dapat mengetahui bahwa suatu penduga adalah yang terbaik untuk data yang diberikan.</p>''',
    472: r'''\t\t<li class="parent"><a href="index.html">6. Pendugaan Titik</a></li>''',
    474: r'''\t\t<li class="child"><a href="Moments.html" title="Metode Momen">2</a></li>''',
    475: r'''\t\t<li class="child"><a href="Likelihood.html" title="Kemungkinan Maksimum">3</a></li>''',
    476: r'''\t\t<li class="child"><a href="Bayes.html" title="Penduga Bayes">4</a></li>''',
    477: r'''\t\t<li class="child"><a href="Unbiased.html" title="Penduga Tak Bias Terbaik">5</a></li>''',
    478: r'''\t\t<li class="child"><a href="Sufficient.html" title="Statistik Cukup, Lengkap, dan Ancilar">6</a></li>''',
    479: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    480: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    483: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    484: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    485: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


STABLE_ID_REPLACEMENTS: dict[int, tuple[str, str]] = {
    63: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.parameter-definition">'''),
    77: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.error-bias-mse">'''),
    88: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.bias-signs">'''),
    112: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.efficiency">'''),
    125: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.asymptotic-unbiasedness">'''),
    129: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.asymptotic-relative-efficiency">'''),
    137: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.consistency">'''),
    147: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.mean-square-implies-consistency">'''),
    158: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.mean-square-implies-asymptotic-unbiasedness">'''),
    189: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.sample-mean-special-cases">'''),
    203: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.known-mean-variance-estimator">'''),
    218: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.sample-variance-estimator">'''),
    238: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.square-root-bias">'''),
    261: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.known-means-covariance-estimator">'''),
    276: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.sample-covariance-estimator">'''),
    286: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.covariance-efficiency-comparison">'''),
    318: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.poisson-moments">'''),
    333: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.poisson-estimator-comparison">'''),
    345: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.poisson-simulation">'''),
    349: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.alpha-emissions-data">'''),
    366: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.sample-mean-simulation">'''),
    370: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.normal-estimation-simulation">'''),
    378: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.matching-simulation">'''),
    386: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.exponential-simulation">'''),
    392: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.michelson-data">'''),
    400: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.cavendish-data">'''),
    408: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.short-data">'''),
    416: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.cicada-data">'''),
    433: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.mm-data">'''),
    450: (r'''<div class="unit">''', r'''<div class="unit" id="o006.random.point.estimators.unit.pearson-data">'''),
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/point/index.html": "index.html",
    "https://www.randomservices.org/random/point/Estimators.html": "Estimators.html",
    "https://www.randomservices.org/random/point/Moments.html": "Moments.html",
    "https://www.randomservices.org/random/sample/index.html": "../sample/index.html",
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/sample/Mean.html": "../sample/Mean.html",
    "https://www.randomservices.org/random/sample/LLN.html": "../sample/LLN.html",
    "https://www.randomservices.org/random/sample/Variance.html": "../sample/Variance.html",
    "https://www.randomservices.org/random/sample/Covariance.html": "../sample/Covariance.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probabilitas, Statistika Matematis, dan Proses Stokastik</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID stabil, pengalihan tautan inti yang telah diterjemahkan ke edisi lokal, pengalihan tautan inti yang belum diterjemahkan ke sumber resmi, pengubahan tautan pelengkap menjadi tautan HTTPS resmi, serta koreksi terbatas terhadap kekeliruan matematis dan data yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t</section>'''


def materialize_indentation(value: str) -> str:
    return re.sub(
        r"^(?:\\t)+",
        lambda match: "\t" * (len(match.group(0)) // 2),
        value,
        flags=re.MULTILINE,
    )


def restore_protected_math(line_number: int, original: str, replacement: str) -> str:
    source_spans = MATH_RE.findall(original)
    target_matches = list(MATH_RE.finditer(replacement))
    if len(source_spans) != len(target_matches):
        raise RuntimeError(
            f"line {line_number}: TeX span count changed: "
            f"{len(source_spans)} != {len(target_matches)}"
        )
    configured = {
        key: value for key, value in MATH_CORRECTIONS.items() if key[0] == line_number
    }
    output: list[str] = []
    cursor = 0
    for span_index, match in enumerate(target_matches, start=1):
        source_span = source_spans[span_index - 1]
        expected = configured.pop((line_number, span_index), None)
        if expected is None:
            protected = source_span
        else:
            expected_source, corrected = expected
            if source_span != expected_source:
                raise RuntimeError(
                    f"line {line_number} span {span_index}: authority TeX changed"
                )
            protected = corrected
        output.append(replacement[cursor : match.start()])
        output.append(protected)
        cursor = match.end()
    if configured:
        raise RuntimeError(f"line {line_number}: configured TeX corrections were not consumed")
    output.append(replacement[cursor:])
    return "".join(output)


def convert_href(raw_href: str) -> str:
    if raw_href.startswith("#"):
        return raw_href
    ancillary = re.fullmatch(r"JavaScript:openAncillary\('([^']+)'\)", raw_href, re.IGNORECASE)
    candidate = ancillary.group(1) if ancillary else raw_href
    absolute = urljoin(SOURCE_URL, candidate)
    base, fragment = urldefrag(absolute)
    if base in LOCAL_URLS:
        result = LOCAL_URLS[base]
    else:
        result = base.replace(
            "http://www.randomservices.org/", "https://www.randomservices.org/"
        )
    return result + (f"#{fragment}" if fragment else "")


def replace_exact_line(
    lines: list[str], line_number: int, expected_raw: str, replacement_raw: str
) -> None:
    original = lines[line_number - 1]
    ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
    expected = materialize_indentation(expected_raw)
    replacement = materialize_indentation(replacement_raw)
    if original.removesuffix(ending) != expected:
        raise RuntimeError(f"line {line_number}: exact authority row changed")
    lines[line_number - 1] = replacement + ending


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    lines = source_bytes.decode("utf-8").splitlines(keepends=True)
    if len(lines) != EXPECTED_SOURCE_LINES:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")
    unreachable = {line_number for line_number, _ in MATH_CORRECTIONS} - set(
        LINE_REPLACEMENTS
    )
    if unreachable:
        raise RuntimeError(
            f"protected TeX corrections lack replacement lines: {sorted(unreachable)}"
        )
    for line_number, replacement in sorted(LINE_REPLACEMENTS.items()):
        original = lines[line_number - 1]
        ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
        translated = materialize_indentation(replacement)
        lines[line_number - 1] = restore_protected_math(
            line_number, original.removesuffix(ending), translated
        ) + ending
    for line_number, (expected, replacement) in sorted(STABLE_ID_REPLACEMENTS.items()):
        if line_number in LINE_REPLACEMENTS:
            raise RuntimeError(f"line {line_number}: stable-ID replacement overlaps translation")
        replace_exact_line(lines, line_number, expected, replacement)
    text = "".join(lines)
    text = re.sub(
        r'href="([^"]+)"',
        lambda match: f'href="{convert_href(match.group(1))}"',
        text,
    )
    marker = "\n</footer>"
    if text.count(marker) != 1:
        raise RuntimeError("footer insertion point is not unique")
    text = text.replace(marker, materialize_indentation(EDITION_NOTICE) + marker, 1)
    for phrase in (
        'lang="en"',
        "JavaScript:openAncillary",
        "Expand Details",
        "Contract Details",
        ">Details:<",
        ">Point Estimation<",
        ">Estimators<",
        ">Simulation Exercises<",
        ">Data Analysis Exercises<",
        ">Apps<",
        ">Data Sets<",
        "> Biographies<",
    ):
        if phrase in text:
            raise RuntimeError(f"untranslated or unsafe reader-facing phrase remains: {phrase}")
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
