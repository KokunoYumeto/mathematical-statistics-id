# QA terminologi Bahasa Indonesia — 2026-08-22

## Instruksi dan batas

Sebelum produksi diperluas dari 14 halaman, dilakukan pencarian terbatas untuk
sumber berbahasa Indonesia dalam statistika matematis/inferensi yang menyediakan
sumber TeX arXiv. Sumber harus benar-benar memuat prosa Indonesia, berada dalam
bidang yang sama, dan menyediakan paket sumber yang dapat diperiksa. Tidak ada
hasil yang memenuhi ketiga syarat itu. Sesuai instruksi, audit beralih secara
jujur ke PDF institusional yang representatif. Tidak ada bukti yang direka dan
tidak ada komunikasi dengan penulis atau pengelola sumber.

## Hasil pencarian arXiv

Pencarian dibatasi pada istilah `estimasi`, `pendugaan`, `statistika`, `peluang`,
`uji hipotesis`, `fungsi kemungkinan`, `maksimum likelihood`, `statistik
matematika`, dan frasa bahasa/subject yang sepadan. Kandidat terdekat semuanya
gagal setidaknya satu syarat:

- arXiv:0807.4609v1 mempunyai TeX Indonesia (`paper_abm_knsi_2008.tex`) tetapi
  membahas komputasi klaster/dinamika molekuler, bukan statistika inferensial;
- arXiv:2202.11794v1 berada di `stat.AP` dan mempunyai TeX
  (`artikelfakultas.tex`) tetapi prosanya berbahasa Inggris;
- arXiv:2002.04384v1 berada di statistika dan berkonteks Indonesia, tetapi
  berbahasa Inggris dan e-print yang diperoleh hanya PDF;
- arXiv:1506.00091v1, 1006.1704v2, 1410.5777v1, dan 2008.12099v1 tidak memenuhi
  kombinasi bidang, bahasa, dan sumber TeX.

Paket dan ekstrak pemeriksaan tetap berada di
`tmp/arxiv_terminology_audit/`; berkas ini bukan bagian pembaca atau paket
rilis.

## Sumber fallback utama

Annisa Widya Ramadhani (2022), Universitas Lampung, *Estimasi Parameter
Distribusi Generalized Eksponensial dengan Metode Bayes Berdasarkan Fungsi
Kerugian Linear Eksponensial (LINEX) Menggunakan Aproksimasi Lindley*.

- rekaman institusional: <https://digilib.unila.ac.id/66177/>;
- PDF institusional: 50 halaman, 3.807.548 byte, SHA-256
  `be841f0f1429828251a9bb37d0bb58714cc59129da2905d94c68b5f39e04c884`;
- salinan pemeriksaan lokal:
  `tmp/arxiv_terminology_audit/fallback_unila_ramadhani_2022.pdf`;
- ekstrak teks: 75.371 byte, SHA-256
  `8de80f86bd37358d948bb1c264b6a7a47ca773927403efc9d26a7ed9610d159b`.

Bukti langsung meliputi `penduga`, `penduga Bayes`, `dugaan Bayes`, `fungsi
likelihood`, `distribusi prior`, `distribusi posterior`, `fungsi kerugian`,
`tak bias asimtotik`, `statistik cukup`, dan `distribusi sampling penduga`.
Contoh fisik terdapat pada halaman PDF 3, 22, dan 38; halaman lain juga
diperiksa secara visual, bukan hanya melalui ekstrak teks.

## Pembanding institusional

- H. Sugiyarto, Universitas Ahmad Dahlan, *Pengantar Statistika Matematika 2*
  (2021): <https://eprints.uad.ac.id/29156/1/BUKU_Stat_Mat2.pdf>; 386 halaman,
  7.983.919 byte, SHA-256
  `d2651740ccd2d395df37b421e21ba228af12ef1959992a966ee80ae7176c72d7`.
  Sumber ini sangat kuat untuk `fungsi kepadatan probabilitas`, `interval
  kepercayaan`, dan penggunaan `fungsi likelihood`, tetapi bercampur antara
  `penduga`, `penaksir`, dan `estimator`.
- Zanzawi Soejoeti, Universitas Terbuka, modul *Sampel dan Distribusi Sampling*:
  <https://pustaka.ut.ac.id/lib/wp-content/uploads/pdfmk/SATS4420-M1.pdf>; 42
  halaman, 652.935 byte, SHA-256
  `119f62eb5ff901c950d4ca3a8c34706ea5f72a2be6199341319629a337f26316`.
- RPS *Statistika Matematika*, Universitas Brawijaya: 16 halaman, 290.769 byte,
  SHA-256
  `cc7b1b33d15d05ab5ca0a6edf72b6e68c967b5a650407db12eadf2704492db85`;
  sumber ini membuktikan variasi `kemungkinan maksimum`, `pendugaan parameter`,
  `ketidakbiasan`, `kecukupan`, dan `selang kepercayaan`.
- Materi Bayes *Statistika Matematika II*, Universitas Mulawarman: 144 halaman,
  1.698.558 byte, SHA-256
  `9a339e60510143031939c3f0cf9bc6684fc050ec90d8cc425bb353cb29095e24`.
- Tesis Universitas Indonesia *Estimasi Parameter Autoregressive...* memakai
  istilah Inggris `ancillary statistic` di dalam prosa Indonesia. Karena PDF
  langsung tidak berhasil dibekukan melalui gerbang perpustakaan, bukti ini
  hanya mendukung keputusan provisional dan tidak diklaim sebagai fallback
  utama.

## Keputusan

Keputusan lengkap dan alias tersimpan di
`TERMINOLOGY_GLOSSARY_ID_ID.csv`. Perubahan yang dibenarkan adalah:

1. `penduga` / `dugaan` / `pendugaan` menjadi keluarga kanonis untuk statistik
   sebelum pengamatan, nilai setelah pengamatan, dan proses; `penaksir` serta
   `estimator` yang tampak di prosa lama dinormalisasi tanpa menyentuh ID stabil,
   URL, judul kutipan, atau nama berkas;
2. ejaan `takbias` dinormalisasi menjadi `tak bias`;
3. istilah probabilistik `densitas` dinormalisasi menjadi `kepadatan` pada
   fungsi dan grafik kepadatan; `densitas Bumi` sebagai besaran fisik tidak
   termasuk perubahan;
4. semua sembilan penggunaan lama `sampling distribution` pada 14 halaman
   ternyata menunjuk distribusi asal populasi/data, bukan distribusi suatu
   statistik. Istilahnya diperjelas menjadi `distribusi asal sampel`.
   `Distribusi sampling` dicadangkan untuk distribusi suatu statistik atau
   penduga di bawah pengambilan sampel berulang;
5. tujuh tautan topik pada halaman sampel normal sekarang memakai `interval
   kepercayaan`, bukan frasa proses `estimasi interval`;
6. kata kunci provisional `statistik ancilar` diperbaiki menjadi `statistik
   ancillary`; kelas CSS `ancillary`, URL, dan ID tidak disentuh;
7. `fungsi kemungkinan (likelihood)`, `kemungkinan maksimum`, `probabilitas`,
   `variabel acak`, istilah Bayes, dan `galat kuadrat rata-rata` dipertahankan.
   Sumber lapangan menunjukkan variasi nyata, sehingga penggantian massal tidak
   akan lebih jujur atau lebih terbaca.

Pencacahan ulang teks tampak pada keempat belas HTML menghasilkan 368
kemunculan `penduga`, 82 `tak bias`, 144 `fungsi kepadatan probabilitas`, 30
`kepadatan empiris`, 14 `distribusi asal sampel`, dan 7 `interval kepercayaan`.
Tidak ada lagi kemunculan tampak `penaksir`, `estimator`, `takbias`, `fungsi
densitas probabilitas`, `densitas empiris`, tiga varian lama untuk distribusi
asal, atau `estimasi interval`. ID stabil berbahasa netral dan istilah fisik
`densitas Bumi` sengaja tidak termasuk penggantian.

## Provenans model dan pelestarian kredit

Catatan eksplisit berikut ditambahkan secara aditif ke repositori, halaman akar
pembaca, halaman lisensi, metadata PDF berikutnya, dan receipt mesin:

`OpenAI Codex gpt-5.6-sol, Ultra`

Catatan tersebut tidak mengganti nama Kyle Siegrist, judul *Random*, kredit
edisi Bahasa Indonesia/human, pemberitahuan non-endorsement, atau lisensi dan
kredit komponen.

## Gerbang propagasi

Perubahan diterapkan hanya pada 14 target HTML yang sudah diterjemahkan dan
generator/localizer yang menghasilkannya. Setelah hash target pada ledger
diperbarui, backend dan pembaca harus dibangun ulang, lalu QA struktural,
matematika, tautan, hak, privasi, dan determinisme dijalankan sebelum produksi
halaman 15 dilanjutkan. PDF 14-halaman yang telah dipublikasikan bersifat
imutabel; PDF berikutnya akan memuat terminologi dan provenance yang diperbarui.
