#!/usr/bin/env python3
"""Create the bounded id-ID Introduction to Hypothesis Testing target."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urldefrag, urljoin

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authority" / "upstream" / "random" / "hypothesis" / "Introduction.html"
TARGET = ROOT / "source" / "id-ID" / "random" / "hypothesis" / "Introduction.html"
SOURCE_URL = "https://www.randomservices.org/random/hypothesis/Introduction.html"
SOURCE_SHA256 = "fb05a9d71b55ba113e2f71afa052bc059b35f2c5b6946012c19ecbc693faab1a"
EXPECTED_SOURCE_LINES = 239
EXPECTED_SOURCE_ELEMENTS = 219
EXPECTED_SOURCE_MATH = 213
EXPECTED_SOURCE_HREFS = 26
EXPECTED_NATIVE_IDS = (
    "MathJax-script",
    "the",
    "pre",
    "hyp",
    "hyp1",
    "err",
    "err1",
    "err2",
    "pow",
    "pow1",
    "pow2",
    "pow3",
    "pva",
    "pva1",
    "jus",
    "par",
    "par1",
    "par2",
    "par3",
    "equ",
    "equ1",
    "equ2",
    "piv",
)
EXPECTED_UNIT_IDS = (
    "hyp1",
    "err1",
    "err2",
    "pow1",
    "pow2",
    "pow3",
    "pva1",
    "par1",
    "par2",
    "par3",
    "equ1",
    "equ2",
)
PAGE_ID = "o006.random.hypothesis.introduction.page"
MATH_RE = re.compile(r"\\\((?:.|\n)*?\\\)|\\\[(?:.|\n)*?\\\]")


LINE_REPLACEMENTS: dict[int, str] = {
    2: r'''<html lang="id-ID">''',
    6: r'''\t<title>Pendahuluan</title>''',
    9: r'''\t<meta name="keywords" content="probabilitas, statistika, sampel acak, uji hipotesis, galat tipe I, galat tipe II, hipotesis nol, hipotesis alternatif, tingkat signifikansi, parameter, statistik uji, daerah kritis">''',
    32: r'''\t\t<li class="parent"><a href="../index.html">Random</a></li>''',
    33: r'''\t\t<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    35: r'''\t\t<li class="child"><a href="Normal.html" title="Uji pada Model Normal">2</a></li>''',
    36: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Uji pada Model Bernoulli">3</a></li>''',
    37: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Uji pada Model Normal Dua Sampel">4</a></li>''',
    38: r'''\t\t<li class="child"><a href="Likelihood.html" title="Uji Rasio Kemungkinan">5</a></li>''',
    39: r'''\t\t<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    40: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    41: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    43: r'''\t<h2 id="o006.random.hypothesis.introduction.page">1. Pendahuluan</h2>''',
    46: r'''<h3 id="the">Teori Dasar</h3>''',
    48: r'''<h4 id="pre">Pendahuluan</h4>''',
    50: r'''<p>Seperti biasa, titik awal kita adalah sebuah <a href="../prob/Experiments.html">eksperimen acak</a> yang dimodelkan oleh <a href="../prob/Probability2.html">ruang probabilitas</a> \((\Omega, \ms F, \P)\). Dalam model statistik dasar, kita mempunyai <a href="../prob/Events.html">variabel acak</a> teramati \(\bs{X}\) yang nilainya berada dalam suatu himpunan \(S\). Secara umum, struktur \(\bs{X}\) dapat cukup rumit. Misalnya, jika eksperimennya adalah mengambil sampel \(n\) objek dari suatu populasi dan mencatat berbagai pengukuran yang diminati, maka''',
    52: r'''dengan \(X_i\) sebagai vektor pengukuran untuk objek ke-\(i\). Kasus khusus terpenting terjadi ketika \((X_1, X_2, \ldots, X_n)\) saling bebas dan berdistribusi identik. Dalam hal ini, kita mempunyai <a href="../sample/Introduction.html">sampel acak</a> berukuran \(n\) dari distribusi yang sama tersebut.</p>''',
    54: r'''<p>Bagian ini bertujuan mendefinisikan dan membahas konsep-konsep dasar <dfn>pengujian hipotesis</dfn> statistik. Secara kolektif, konsep-konsep ini kadang-kadang disebut kerangka <dfn>Neyman–Pearson</dfn>, untuk menghormati <a href="JavaScript:openAncillary('../biographies/Neyman.html')" class="ancillary" title="Buka sketsa biografi">Jerzy Neyman</a> dan <a href="JavaScript:openAncillary('../biographies/PearsonE.html')" class="ancillary" title="Buka sketsa biografi">Egon Pearson</a>, yang pertama kali memformalkannya.</p>''',
    56: r'''<h4 id="hyp">Hipotesis</h4>''',
    59: r'''\t<p class="dfn">Sebuah <dfn>hipotesis statistik</dfn> adalah pernyataan tentang distribusi \(\bs{X}\). Secara ekuivalen, hipotesis statistik menentukan suatu <em>himpunan</em> distribusi yang mungkin bagi \(\bs{X}\), yakni himpunan distribusi yang membuat pernyataan tersebut benar. Hipotesis yang menentukan tepat satu distribusi bagi \(\bs{X}\) disebut <dfn>sederhana</dfn>; hipotesis yang menentukan lebih dari satu distribusi bagi \(\bs{X}\) disebut <dfn>majemuk</dfn>.</p>''',
    62: r'''<p>Dalam <dfn>pengujian hipotesis</dfn>, tujuannya adalah menilai apakah terdapat bukti statistik yang cukup untuk menolak <dfn>hipotesis nol</dfn> yang diasumsikan, demi <dfn>hipotesis alternatif</dfn> yang diajukan. Hipotesis nol biasanya dilambangkan dengan \(H_0\), sedangkan hipotesis alternatif biasanya dilambangkan dengan \(H_1\).</p>''',
    64: r'''<p>Uji hipotesis merupakan suatu <em>keputusan statistik</em>; kesimpulannya adalah <dfn>menolak</dfn> hipotesis nol demi hipotesis alternatif atau <dfn>gagal menolak</dfn> hipotesis nol. Keputusan tersebut tentu harus didasarkan pada nilai amatan \(\bs{x}\) dari vektor data \(\bs{X}\). Karena itu, kita mencari himpunan bagian \(R\) yang sesuai dari ruang sampel \(S\), lalu menolak \(H_0\) jika dan hanya jika \(\bs{x} \in R\). Himpunan \(R\) dikenal sebagai <dfn>daerah penolakan</dfn> atau <dfn>daerah kritis</dfn>. Perhatikan asimetri antara hipotesis nol dan hipotesis alternatif. Asimetri ini timbul karena, dalam suatu pengertian, kita <em>mengasumsikan</em> hipotesis nol, kemudian memeriksa apakah bukti dalam \(\bs{x}\) cukup kuat untuk menggugurkan asumsi tersebut demi hipotesis alternatif.</p>''',
    66: r'''<p>Dalam suatu pengertian, uji hipotesis merupakan analogi statistik bagi pembuktian dengan kontradiksi. Misalkan sejenak bahwa \(H_1\) adalah sebuah pernyataan dalam teori matematika dan \(H_0\) adalah negasinya. Salah satu cara membuktikan \(H_1\) ialah mengasumsikan \(H_0\), lalu menurunkan suatu kontradiksi secara logis. Tentu saja kita tidak <q>membuktikan</q> apa pun dalam uji hipotesis, tetapi terdapat kemiripan: kita mengasumsikan \(H_0\), lalu menilai apakah data \(\bs{x}\) cukup bertentangan dengan asumsi itu sehingga kita beralasan untuk menolak \(H_0\) demi \(H_1\).</p>''',
    68: r'''<p>Daerah kritis sering didefinisikan melalui suatu statistik \(w(\bs{X})\), yang disebut <dfn>statistik uji</dfn>, dengan \(w\) sebagai fungsi dari \(S\) ke himpunan lain \(T\). Kita mencari daerah penolakan \(R_T \subseteq T\) yang sesuai, lalu menolak \(H_0\) ketika nilai amatan \(w(\bs{x}) \in R_T\). Dengan demikian, daerah penolakan dalam \(S\) adalah \(R = w^{-1}(R_T) = \left\{\bs{x} \in S: w(\bs{x}) \in R_T\right\}\). Seperti biasa, penggunaan statistik sering memungkinkan <dfn>reduksi data</dfn> yang berarti ketika dimensi statistik uji jauh lebih kecil daripada dimensi vektor data.</p>''',
    70: r'''<h4 id="err">Galat</h4>''',
    72: r'''<p>Keputusan akhir dapat benar atau keliru. Terdapat dua jenis galat, bergantung pada hipotesis mana yang sebenarnya benar.</p>''',
    75: r'''\t<p class="dfn">Jenis galat:</p>''',
    77: r'''\t\t<li><dfn>Galat tipe I</dfn> adalah menolak hipotesis nol \(H_0\) ketika \(H_0\) benar.</li>''',
    78: r'''\t\t<li><dfn>Galat tipe II</dfn> adalah gagal menolak hipotesis nol \(H_0\) ketika hipotesis alternatif \(H_1\) benar.</li>''',
    82: r'''<p>Demikian pula, terdapat dua cara untuk membuat keputusan yang <em>benar</em>: kita dapat menolak \(H_0\) ketika \(H_1\) benar, atau gagal menolak \(H_0\) ketika \(H_0\) benar. Kemungkinan-kemungkinan itu dirangkum dalam tabel berikut.</p>''',
    85: r'''\t<caption class="displayed">Uji Hipotesis</caption>''',
    87: r'''\t\t<th>Keadaan | Keputusan</th>''',
    88: r'''\t\t<th>Gagal menolak \(H_0\)</th>''',
    89: r'''\t\t<th>Menolak \(H_0\)</th>''',
    92: r'''\t<th>\(H_0\) Benar</th>''',
    93: r'''\t\t<td>Benar</td>''',
    94: r'''\t\t<td>Galat tipe I</td>''',
    97: r'''\t\t<th>\(H_1\) Benar</th>''',
    98: r'''\t\t<td>Galat tipe II</td>''',
    99: r'''\t\t<td>Benar</td>''',
    103: r'''<p>Tentu saja, setelah mengamati \(\bs{X} = \bs{x}\) dan mengambil keputusan, kita telah membuat keputusan yang benar atau melakukan galat, dan biasanya kita tidak akan pernah mengetahui mana yang terjadi. Namun, <em>sebelum</em> data dikumpulkan, kita dapat meninjau probabilitas berbagai galat tersebut.</p>''',
    105: r'''<p>Jika \(H_0\) benar—artinya distribusi \(\bs{X}\) ditentukan oleh \(H_0\)—maka \(\P(\bs{X} \in R)\) adalah probabilitas galat tipe I bagi distribusi tersebut. Jika \(H_0\) majemuk, maka \(H_0\) menentukan beragam distribusi bagi \(\bs{X}\), sehingga terdapat suatu <em>himpunan</em> probabilitas galat tipe I.</p>''',
    108: r'''\t<p class="dfn">Supremum probabilitas galat tipe I atas himpunan distribusi yang ditentukan oleh \(H_0\) adalah <dfn>tingkat signifikansi</dfn> uji tersebut atau <dfn>ukuran</dfn> daerah kritisnya.</p>''',
    111: r'''<p>Tingkat signifikansi sering dilambangkan dengan \(\alpha\). Biasanya, daerah penolakan dibangun agar tingkat signifikansinya sama dengan suatu nilai kecil yang ditetapkan (umumnya 0,1; 0,05; atau 0,01).</p>''',
    113: r'''<p>Jika \(H_1\) benar—artinya distribusi \(\bs{X}\) ditentukan oleh \(H_1\)—maka \(\P(\bs{X} \notin R)\) adalah probabilitas galat tipe II bagi distribusi tersebut. Sekali lagi, jika \(H_1\) majemuk, maka \(H_1\) menentukan beragam distribusi bagi \(\bs{X}\), sehingga terdapat suatu himpunan probabilitas galat tipe II. Secara umum, terdapat kompromi antara probabilitas galat tipe I dan tipe II. Jika probabilitas galat tipe I dikurangi dengan memperkecil daerah penolakan \(R\), probabilitas galat tipe II pasti meningkat karena daerah komplemennya \(S \setminus R\) menjadi lebih besar.</p>''',
    115: r'''<p>Kasus-kasus ekstrem memberi sedikit pemahaman. Pertama, tinjau aturan keputusan yang <em>tidak pernah</em> menolak \(H_0\), apa pun bukti \(\bs{x}\). Aturan ini bersesuaian dengan daerah penolakan \(R = \emptyset\). Galat tipe I mustahil terjadi, sehingga tingkat signifikansinya 0. Sebaliknya, probabilitas galat tipe II adalah 1 untuk setiap distribusi yang ditentukan oleh \(H_1\). Pada ekstrem lain, tinjau aturan keputusan yang selalu menolak \(H_0\), apa pun bukti \(\bs{x}\). Aturan ini bersesuaian dengan daerah penolakan \(R = S\). Galat tipe II mustahil terjadi, tetapi kini probabilitas galat tipe I adalah 1 untuk setiap distribusi yang ditentukan oleh \(H_0\). Di antara kedua uji yang tidak berguna ini terdapat uji-uji bermakna yang mempertimbangkan bukti \(\bs{x}\).</p>''',
    117: r'''<h4 id="pow">Kuasa</h4>''',
    120: r'''\t<p class="dfn">Jika \(H_1\) benar, sehingga distribusi \(\bs{X}\) ditentukan oleh \(H_1\), maka \(\P(\bs{X} \in R)\), yakni probabilitas menolak \(H_0\), adalah <dfn>kuasa</dfn> uji bagi distribusi tersebut.</p>''',
    123: r'''<p>Dengan demikian, kuasa uji bagi suatu distribusi yang ditentukan oleh \(H_1\) adalah probabilitas membuat keputusan yang benar.</p>''',
    126: r'''\t<p class="dfn">Misalkan terdapat dua uji yang masing-masing bersesuaian dengan daerah penolakan \(R_1\) dan \(R_2\), serta masing-masing mempunyai tingkat signifikansi \(\alpha\). Uji dengan daerah \(R_1\) disebut <dfn>lebih berkuasa secara seragam</dfn> daripada uji dengan daerah \(R_2\) jika''',
    127: r'''\t\[ \P(\bs{X} \in R_1) \ge \P(\bs{X} \in R_2) \text{ untuk setiap distribusi } \bs{X} \text{ yang ditentukan oleh } H_1 \]</p>''',
    130: r'''<p>Dalam hal ini, tentu kita lebih memilih uji pertama. Namun, dua uji sering kali tidak terurut secara seragam: satu uji lebih berkuasa bagi sebagian distribusi yang ditentukan oleh \(H_1\), sedangkan uji lain lebih berkuasa bagi distribusi lain yang ditentukan oleh \(H_1\).</p>''',
    133: r'''\t<p class="dfn">Jika suatu uji mempunyai tingkat signifikansi \(\alpha\) dan lebih berkuasa secara seragam daripada setiap uji lain yang juga mempunyai tingkat signifikansi \(\alpha\), uji tersebut disebut <dfn>uji paling berkuasa secara seragam</dfn> pada tingkat \(\alpha\).</p>''',
    136: r'''<p>Jelas bahwa uji paling berkuasa secara seragam adalah yang terbaik yang dapat kita capai.</p>''',
    138: r'''<h4 id="pva">Nilai-\(P\)</h4>''',
    140: r'''<p>Dalam kebanyakan kasus, terdapat prosedur umum untuk membangun sebuah uji—yakni daerah penolakan \(R_\alpha\)—bagi setiap tingkat signifikansi \(\alpha \in (0, 1)\) yang diberikan. Biasanya, \(R_\alpha\) mengecil dalam arti relasi himpunan bagian ketika \(\alpha\) mengecil.</p>''',
    143: r'''\t<p class="dfn"><dfn>Nilai-\(P\)</dfn> dari nilai amatan \(\bs{x}\) bagi \(\bs{X}\), yang dilambangkan dengan \(P(\bs{x})\), didefinisikan sebagai nilai \(\alpha\) terkecil yang memenuhi \(\bs{x} \in R_\alpha\); dengan kata lain, tingkat signifikansi terkecil yang membuat \(H_0\) ditolak ketika \(\bs{X} = \bs{x}\).</p>''',
    146: r'''<p>Mengetahui \(P(\bs{x})\) memungkinkan kita menguji \(H_0\) pada tingkat signifikansi mana pun untuk data \(\bs{x}\) yang diberikan: jika \(P(\bs{x}) \le \alpha\), kita menolak \(H_0\) pada tingkat signifikansi \(\alpha\); jika \(P(\bs{x}) \gt \alpha\), kita gagal menolak \(H_0\) pada tingkat signifikansi \(\alpha\). Perhatikan bahwa \(P(\bs{X})\) adalah sebuah <em>statistik</em>. Secara informal, \(P(\bs{x})\) sering dapat dipandang sebagai probabilitas hasil yang <q>sama ekstrem atau lebih ekstrem</q> daripada nilai amatan \(\bs{x}\), dengan makna <em>ekstrem</em> ditafsirkan relatif terhadap hipotesis nol \(H_0\).</p>''',
    148: r'''<h4 id="jus">Analogi dengan Sistem Peradilan</h4>''',
    150: r'''<p>Terdapat analogi yang membantu antara pengujian hipotesis statistik dan sistem peradilan pidana di Amerika Serikat serta berbagai negara lain. Tinjau seseorang yang didakwa melakukan tindak pidana. <em>Hipotesis nol</em> yang diasumsikan adalah bahwa orang tersebut tidak bersalah; <em>hipotesis alternatif</em> yang diajukan adalah bahwa orang tersebut bersalah. Pengujian kedua hipotesis itu berupa persidangan, dengan bukti yang diajukan oleh kedua pihak berperan sebagai data. Setelah menimbang bukti, juri memberikan putusan <em>tidak bersalah</em> atau <em>bersalah</em>. Perhatikan bahwa <em>tidak melakukan tindak pidana</em> bukanlah putusan tersendiri dari juri, sebab tujuan persidangan bukanlah <em>membuktikan</em> orang tersebut tidak melakukan tindak pidana. Tujuannya adalah menilai apakah bukti cukup kuat untuk menggugurkan hipotesis nol bahwa orang tersebut tidak bersalah demi hipotesis alternatif bahwa ia bersalah. <em>Galat tipe I</em> adalah menyatakan bersalah seseorang yang sebenarnya tidak bersalah; <em>galat tipe II</em> adalah membebaskan seseorang yang sebenarnya bersalah. Secara umum, galat tipe I dianggap lebih serius, sehingga untuk menahan peluangnya pada tingkat yang sangat rendah, standar pemidanaan dalam perkara pidana serius adalah <em>melampaui keraguan yang beralasan</em>.</p>''',
    152: r'''<h3 id="par">Uji untuk Parameter Tak Diketahui</h3>''',
    154: r'''<p>Pengujian hipotesis merupakan konsep yang sangat umum, tetapi sebuah kelas khusus yang penting muncul ketika distribusi variabel data \(\bs{X}\) bergantung pada parameter \(\theta\) yang nilainya berada dalam ruang parameter \(\Theta\). Parameter dapat bernilai vektor, sehingga \(\bs{\theta} = (\theta_1, \theta_2, \ldots, \theta_k)\) dan \(\Theta \subseteq \R^k\) untuk suatu \(k \in \N_+\). Hipotesis umumnya berbentuk''',
    155: r'''\[ H_0: \theta \in \Theta_0 \text{ melawan } H_1: \theta \notin \Theta_0 \]''',
    156: r'''dengan \(\Theta_0\) sebagai himpunan bagian yang ditetapkan dari ruang parameter \(\Theta\). Dalam kerangka ini, probabilitas membuat galat atau keputusan benar bergantung pada nilai sebenarnya dari \(\theta\). Jika \(R\) adalah daerah penolakan, maka <dfn>fungsi kuasa</dfn> \(Q\) diberikan oleh''',
    158: r'''Fungsi kuasa memberikan banyak informasi tentang uji tersebut.</p>''',
    161: r'''\t<p class="math">Fungsi kuasa memenuhi sifat-sifat berikut:</p>''',
    163: r'''\t\t<li>\(Q(\theta)\) adalah probabilitas galat tipe I ketika \(\theta \in \Theta_0\).</li>''',
    164: r'''\t\t<li>\(\sup\left\{Q(\theta): \theta \in \Theta_0\right\}\) adalah tingkat signifikansi uji.</li>''',
    165: r'''\t\t<li>\(1 - Q(\theta)\) adalah probabilitas galat tipe II ketika \(\theta \notin \Theta_0\).</li>''',
    166: r'''\t\t<li>\(Q(\theta)\) adalah kuasa uji ketika \(\theta \notin \Theta_0\).</li>''',
    170: r'''<p>Jika terdapat dua uji, kita dapat membandingkannya melalui fungsi kuasanya.</p>''',
    173: r'''\t<p class="math">Misalkan terdapat dua uji yang masing-masing bersesuaian dengan daerah penolakan \(R_1\) dan \(R_2\), serta masing-masing mempunyai tingkat signifikansi \(\alpha\). Uji dengan daerah penolakan \(R_1\) lebih berkuasa secara seragam daripada uji dengan daerah penolakan \(R_2\) jika \(Q_1(\theta) \ge Q_2(\theta)\) untuk semua \(\theta \notin \Theta_0\).</p>''',
    176: r'''<p>Kebanyakan uji hipotesis untuk parameter riil tak diketahui \(\theta\) termasuk dalam tiga kasus khusus berikut.</p>''',
    179: r'''\t<p class="dfn">Misalkan \(\theta\) adalah parameter riil dan \(\theta_0 \in \Theta\) adalah nilai yang ditetapkan. Ketiga uji berikut berturut-turut disebut <dfn>uji dua sisi</dfn>, <dfn>uji berekor kiri</dfn>, dan <dfn>uji berekor kanan</dfn>.</p>''',
    181: r'''\t\t<li>\(H_0: \theta = \theta_0\) melawan \(H_1: \theta \ne \theta_0\)</li>''',
    182: r'''\t\t<li>\(H_0: \theta \ge \theta_0\) melawan \(H_1: \theta \lt \theta_0\)</li>''',
    183: r'''\t\t<li>\(H_0: \theta \le \theta_0\) melawan \(H_1: \theta \gt \theta_0\)</li>''',
    187: r'''<p>Dengan demikian, uji-uji tersebut dinamai menurut hipotesis alternatif yang diajukan. Tentu saja, selain \(\theta\) mungkin terdapat parameter tak diketahui lain yang disebut <dfn>parameter pengganggu</dfn>.</p>''',
    189: r'''<h4 id="equ">Ekuivalensi antara Uji Hipotesis dan Himpunan Kepercayaan</h4>''',
    191: r'''<p>Terdapat ekuivalensi antara uji hipotesis dan <a href="../interval/Introduction.html">himpunan kepercayaan</a> bagi parameter \(\theta\).</p>''',
    194: r'''\t<p class="math">Misalkan \(C(\bs{X})\) adalah himpunan kepercayaan dengan peluang cakupan sekurang-kurangnya \(1 - \alpha\) bagi \(\theta\). Uji berikut mempunyai tingkat signifikansi paling tinggi \(\alpha\) untuk hipotesis \(H_0: \theta = \theta_0\) melawan \(H_1: \theta \ne \theta_0\): tolak \(H_0\) jika dan hanya jika \(\theta_0 \notin C(\bs{x})\).</p>''',
    196: r'''\t\t<summary>Rincian:</summary>''',
    197: r'''\t\t<p>Menurut asumsi, \(\P_{\theta_0}[\theta_0 \in C(\bs{X})] \ge 1 - \alpha\). Karena itu, jika \(H_0\) benar sehingga \(\theta = \theta_0\), probabilitas galat tipe I adalah \(\P_{\theta_0}[\theta_0 \notin C(\bs{X})] \le \alpha\).</p>''',
    201: r'''<p>Secara ekuivalen, kita <em>gagal</em> menolak \(H_0\) dalam uji dengan tingkat signifikansi paling tinggi \(\alpha\) jika dan hanya jika \(\theta_0\) berada dalam himpunan kepercayaan dengan tingkat kepercayaan sekurang-kurangnya \(1 - \alpha\) yang bersesuaian. Secara khusus, ekuivalensi ini berlaku bagi pendugaan interval parameter riil \(\theta\) dan uji-uji umum untuk \(\theta\) pada <a href="#par3" class="ref"></a>.</p>''',
    204: r'''\t<p class="math">Dalam setiap kasus berikut, interval kepercayaan mempunyai tingkat kepercayaan sekurang-kurangnya \(1 - \alpha\), dan uji mempunyai tingkat signifikansi paling tinggi \(\alpha\).</p>''',
    206: r'''\t\t<li>Misalkan \(\left[L(\bs{X}), U(\bs{X})\right]\) adalah interval kepercayaan dua sisi bagi \(\theta\). Tolak \(H_0: \theta = \theta_0\) melawan \(H_1: \theta \ne \theta_0\) jika dan hanya jika \(\theta_0 \lt L(\bs{X})\) atau \(\theta_0 \gt U(\bs{X})\).</li>''',
    207: r'''\t\t<li>Misalkan \(L(\bs{X})\) adalah batas bawah kepercayaan bagi \(\theta\). Tolak \(H_0: \theta \le \theta_0\) melawan \(H_1: \theta \gt \theta_0\) jika dan hanya jika \(\theta_0 \lt L(\bs{X})\).</li>''',
    208: r'''\t\t<li>Misalkan \(U(\bs{X})\) adalah batas atas kepercayaan bagi \(\theta\). Tolak \(H_0: \theta \ge \theta_0\) melawan \(H_1: \theta \lt \theta_0\) jika dan hanya jika \(\theta_0 \gt U(\bs{X})\).</li>''',
    212: r'''<h4 id="piv">Variabel Pivot dan Statistik Uji</h4>''',
    214: r'''<p>Ingat bahwa himpunan kepercayaan bagi parameter tak diketahui \(\theta\) sering dibangun melalui <dfn>variabel pivot</dfn>, yakni variabel acak \(W(\bs{X}, \theta)\) yang bergantung pada vektor data \(\bs{X}\) dan parameter \(\theta\), tetapi distribusinya diketahui dan tidak bergantung pada \(\theta\). Dalam hal ini, statistik uji yang wajar bagi uji-uji dasar pada definisi <a href="#par3" class="ref"></a> adalah \(W(\bs{X}, \theta_0)\).</p>''',
    218: r'''\t\t<li class="parent"><a href="../index.html">Random</a></li>''',
    219: r'''\t\t<li class="parent"><a href="index.html">8. Pengujian Hipotesis</a></li>''',
    221: r'''\t\t<li class="child"><a href="Normal.html" title="Uji pada Model Normal">2</a></li>''',
    222: r'''\t\t<li class="child"><a href="Bernoulli.html" title="Uji pada Model Bernoulli">3</a></li>''',
    223: r'''\t\t<li class="child"><a href="BivariateNormal.html" title="Uji pada Model Normal Dua Sampel">4</a></li>''',
    224: r'''\t\t<li class="child"><a href="Likelihood.html" title="Uji Rasio Kemungkinan">5</a></li>''',
    225: r'''\t\t<li class="child"><a href="ChiSquare.html" title="Uji Khi-Kuadrat">6</a></li>''',
    226: r'''\t\t<li class="details"><button type="button" title="Perluas Rincian" onclick="expandDetails(true);"><img src="../icons/Plus.svg" alt="Perluas"></button></li>''',
    227: r'''\t\t<li class="details"><button type="button" title="Ciutkan Rincian" onclick="expandDetails(false);"><img src="../icons/Minus.svg" alt="Ciutkan"></button></li>''',
    230: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../apps/index.html')" class="ancillary">Aplikasi</a></li>''',
    231: r'''\t\t<li class="sister"><a href="JavaScript:openAncillary('../data/index.html')" class="ancillary">Himpunan Data</a></li>''',
    232: r'''\t\t<li class="child"><a href="JavaScript:openAncillary('../biographies/index.html')" class="ancillary">Biografi</a></li>''',
}


LOCAL_URLS = {
    "https://www.randomservices.org/random/Screen.css": "../Screen.css",
    "https://www.randomservices.org/random/icons/Icon.svg": "../icons/Icon.svg",
    "https://www.randomservices.org/random/sample/Introduction.html": "../sample/Introduction.html",
    "https://www.randomservices.org/random/interval/Introduction.html": "../interval/Introduction.html",
    "https://www.randomservices.org/random/hypothesis/index.html": "index.html",
    "https://www.randomservices.org/random/hypothesis/Introduction.html": "Introduction.html",
    "https://www.randomservices.org/random/hypothesis/Normal.html": "Normal.html",
    "https://www.randomservices.org/random/hypothesis/Bernoulli.html": "Bernoulli.html",
    "https://www.randomservices.org/random/hypothesis/BivariateNormal.html": "BivariateNormal.html",
    "https://www.randomservices.org/random/hypothesis/Likelihood.html": "Likelihood.html",
    "https://www.randomservices.org/random/hypothesis/ChiSquare.html": "ChiSquare.html",
}


EDITION_NOTICE = r'''
\t<section class="edition-notice" data-o006-edition-notice="v1">
\t\t<p><strong>Pemberitahuan edisi.</strong> Terjemahan Bahasa Indonesia ini mengadaptasi <a href="https://www.randomservices.org/random/">Random: Probability, Mathematical Statistics, and Stochastic Processes</a> karya Kyle Siegrist. Perubahan pada halaman ini mencakup penerjemahan, penambahan ID halaman stabil, pengalihan tautan korpus yang telah diterjemahkan ke edisi lokal, pengalihan tautan korpus di luar lingkup ke sumber HTTPS resmi, pengubahan tautan pelengkap menjadi HTTPS resmi, serta koreksi HTML dan matematis terbatas yang dicatat dalam daftar koreksi edisi.</p>
\t\t<p>Penerjemahan dan rekayasa edisi dilakukan dengan OpenAI Codex gpt-5.6-sol, Ultra, atas instruksi pengguna. Seluruh kredit bagi sumber, penulis, dan kontributor manusia tetap dipertahankan.</p>
\t\t<p>Situs asal menyatakan <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, sedangkan halaman <a href="https://www.randomservices.org/random/Credits.html">Kredit</a> menautkan <a href="https://creativecommons.org/licenses/by/1.0/">CC BY 1.0</a>; perbedaan ini dipertahankan. Edisi independen ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random Services. Tautan ke aplikasi, data, dan biografi pihak ketiga tidak menyatakan hak untuk mendistribusikan ulang materi tersebut.</p>
\t</section>'''


# Indices refer to the ordered protected TeX spans in the frozen authority.
# Entries 101 and 139 translate prose inside \text{} without changing mathematics.
# The remaining entries are target-only corrections proved from the surrounding result.
MATH_CHANGES_BY_INDEX = {
    101: r'''\[ \P(\bs{X} \in R_1) \ge \P(\bs{X} \in R_2) \text{ untuk setiap distribusi } \bs{X} \text{ yang ditentukan oleh } H_1 \]''',
    136: r'''\(\bs{\theta} = (\theta_1, \theta_2, \ldots, \theta_k)\)''',
    139: r'''\[ H_0: \theta \in \Theta_0 \text{ melawan } H_1: \theta \notin \Theta_0 \]''',
    148: r'''\(\sup\left\{Q(\theta): \theta \in \Theta_0\right\}\)''',
    171: r'''\(C(\bs{X})\)''',
    179: r'''\(\P_{\theta_0}[\theta_0 \in C(\bs{X})] \ge 1 - \alpha\)''',
    182: r'''\(\P_{\theta_0}[\theta_0 \notin C(\bs{X})] \le \alpha\)''',
    191: r'''\(\left[L(\bs{X}), U(\bs{X})\right]\)''',
}


def materialize_indentation(value: str) -> str:
    return re.sub(
        r"^(?:\\t)+",
        lambda match: "\t" * (len(match.group(0)) // 2),
        value,
        flags=re.MULTILINE,
    )


def replace_exact_line(lines: list[str], line_number: int, replacement_raw: str) -> None:
    original = lines[line_number - 1]
    ending = "\r\n" if original.endswith("\r\n") else "\n" if original.endswith("\n") else ""
    lines[line_number - 1] = materialize_indentation(replacement_raw) + ending


def convert_href(raw_href: str) -> str:
    if raw_href.startswith("#"):
        return raw_href
    ancillary = re.fullmatch(r"JavaScript:openAncillary\('([^']+)'\)", raw_href, re.IGNORECASE)
    candidate = ancillary.group(1) if ancillary else raw_href
    absolute = urljoin(SOURCE_URL, candidate)
    base, fragment = urldefrag(absolute)
    result = LOCAL_URLS.get(base, base)
    result = result.replace("http://www.randomservices.org/", "https://www.randomservices.org/")
    return result + (f"#{fragment}" if fragment else "")


def core_soup(value: str) -> BeautifulSoup:
    soup = BeautifulSoup(value, "html.parser")
    notice = soup.select_one("section.edition-notice[data-o006-edition-notice='v1']")
    if notice is not None:
        notice.decompose()
    return soup


def assert_core_topology(source_text: str, target_text: str) -> None:
    source = core_soup(source_text)
    target = core_soup(target_text)
    source_tags = [tag.name for tag in source.find_all(True)]
    target_tags = [tag.name for tag in target.find_all(True)]
    if len(source_tags) != EXPECTED_SOURCE_ELEMENTS or target_tags != source_tags:
        raise RuntimeError(
            f"semantic element topology changed: {len(source_tags)} -> {len(target_tags)}"
        )
    source_units = tuple(tag.get("id") for tag in source.select("div.unit"))
    target_units = tuple(tag.get("id") for tag in target.select("div.unit"))
    if source_units != EXPECTED_UNIT_IDS or target_units != source_units:
        raise RuntimeError(f"native unit IDs changed: {source_units!r} -> {target_units!r}")
    if len(source.find_all("details")) != 1 or len(target.find_all("details")) != 1:
        raise RuntimeError("disclosure topology changed")
    source_ids = tuple(tag.get("id") for tag in source.find_all(id=True))
    target_ids = tuple(tag.get("id") for tag in target.find_all(id=True))
    if source_ids != EXPECTED_NATIVE_IDS:
        raise RuntimeError(f"authority native-ID census changed: {source_ids!r}")
    if target_ids != EXPECTED_NATIVE_IDS[:1] + (PAGE_ID,) + EXPECTED_NATIVE_IDS[1:]:
        raise RuntimeError(f"target ID census changed: {target_ids!r}")
    if len(target_ids) != len(set(target_ids)):
        raise RuntimeError("duplicate target IDs")


def assert_links(rendered: str) -> None:
    soup = BeautifulSoup(rendered, "html.parser")
    core = core_soup(rendered)
    if len(core.find_all("a", href=True)) != EXPECTED_SOURCE_HREFS:
        raise RuntimeError("core link count changed")
    if len(soup.find_all("a", href=True)) != EXPECTED_SOURCE_HREFS + 4:
        raise RuntimeError("edition-notice link delta changed")
    required_local = {
        "index.html",
        "Normal.html",
        "Bernoulli.html",
        "BivariateNormal.html",
        "Likelihood.html",
        "ChiSquare.html",
        "../sample/Introduction.html",
        "../interval/Introduction.html",
    }
    hrefs = {tag["href"] for tag in core.find_all("a", href=True)}
    missing = required_local - hrefs
    if missing:
        raise RuntimeError(f"required local corpus links missing: {sorted(missing)!r}")
    allowed_local = required_local | {"../icons/Icon.svg", "../Screen.css"}
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.startswith("#") or href in allowed_local or href.startswith("https://"):
            continue
        raise RuntimeError(f"unexpected unresolved or non-HTTPS href: {href}")


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise RuntimeError(f"authority hash mismatch: {digest}")
    source_text = source_bytes.decode("utf-8")
    lines = source_text.splitlines(keepends=True)
    if len(lines) != EXPECTED_SOURCE_LINES:
        raise RuntimeError(f"unexpected authority line count: {len(lines)}")
    for line_number, replacement in sorted(LINE_REPLACEMENTS.items()):
        replace_exact_line(lines, line_number, replacement)
    rendered = "".join(lines)
    rendered = re.sub(
        r'href="([^"]+)"',
        lambda match: f'href="{convert_href(match.group(1))}"',
        rendered,
    )
    marker = "</footer>"
    if rendered.count(marker) != 1:
        raise RuntimeError("footer marker count changed")
    rendered = rendered.replace(marker, materialize_indentation(EDITION_NOTICE) + "\n" + marker, 1)

    source_math = MATH_RE.findall(source_text)
    raw_target_math = MATH_RE.findall(rendered)
    expected_math = [MATH_CHANGES_BY_INDEX.get(i, span) for i, span in enumerate(source_math)]
    if len(source_math) != EXPECTED_SOURCE_MATH or len(raw_target_math) != len(source_math):
        raise RuntimeError(
            f"protected TeX count changed: source={len(source_math)}, "
            f"target={len(raw_target_math)}"
        )
    expected_iter = iter(expected_math)
    rendered = MATH_RE.sub(lambda _match: next(expected_iter), rendered)
    target_math = MATH_RE.findall(rendered)
    if len(source_math) != EXPECTED_SOURCE_MATH or target_math != expected_math:
        mismatch = next(
            (
                i
                for i, (expected, actual) in enumerate(zip(expected_math, target_math))
                if expected != actual
            ),
            min(len(expected_math), len(target_math)),
        )
        raise RuntimeError(
            f"protected TeX sequence changed unexpectedly at span {mismatch + 1}: "
            f"source={len(source_math)}, target={len(target_math)}"
        )
    assert_core_topology(source_text, rendered)
    assert_links(rendered)

    required = (
        'lang="id-ID"',
        f'id="{PAGE_ID}"',
        "Pengujian Hipotesis",
        "hipotesis nol",
        "galat tipe I",
        "fungsi kuasa",
        "Nilai-\\(P\\)",
        "OpenAI Codex gpt-5.6-sol, Ultra",
        'data-o006-edition-notice="v1"',
    )
    for phrase in required:
        if phrase not in rendered:
            raise RuntimeError(f"required translated surface missing: {phrase}")
    forbidden = (
        'lang="en"',
        "JavaScript:openAncillary",
        ">Introduction<",
        ">Basic Theory<",
        ">Hypotheses<",
        ">Errors<",
        ">Power<",
        ">Details:<",
        "Expand Details",
        "Contract Details",
        ">Apps<",
        ">Data Sets<",
        "> Biographies<",
        r"\theta_n)",
        r"\max\left\{Q(\theta)",
        r"P[\theta \notin C",
        r"\left[L(\bs{X}, U(\bs{X})\right]",
    )
    for phrase in forbidden:
        if phrase in rendered:
            raise RuntimeError(f"unresolved reader-facing/source defect remains: {phrase}")

    output = rendered.encode("utf-8")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(output)
    print(
        f"WROTE {TARGET.relative_to(ROOT).as_posix()}: "
        f"{len(output)} bytes / sha256 {hashlib.sha256(output).hexdigest()}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
