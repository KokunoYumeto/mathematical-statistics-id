# Statistika Matematis — Bahasa Indonesia (id-ID)

Edisi Bahasa Indonesia independen yang dikerjakan dalam jalur kurikulum O006 /
C140, Statistika Matematis. Korpus edisi ini adalah bab statistika matematis
(bab 5–8) dari karya Kyle Siegrist, *Random: Probability, Mathematical
Statistics, and Stochastic Processes*. Edisi lengkap ini tetap diproduksi
sebagai sumber terbuka tersendiri; edisi ini bukan satu-satunya tulang punggung
naratif untuk kursus C140 yang dikonfigurasi secara terpisah.

Status pembaca: **13 dari 29 halaman sumber inti telah diterjemahkan**, secara
berurutan dari indeks Sampel Acak sampai `point/Likelihood.html`.
Korpus belum selesai; repositori ini tidak mengklaim kelengkapan dini.

Checkpoint tiga belas halaman lulus dua pemutaran ulang build dan QA
deterministik: 43 berkas pembaca, 397 unit instruksional, 267 pengungkapan
jawaban/rincian, dan 5.125 rentang TeX. Halaman Kemungkinan Maksimum lulus
pemeriksaan visual desktop/seluler dengan 592 wadah MathJax dan empat gambar
lengkap, tanpa galat konsol, TeX mentah, atau luapan horizontal halaman.
Tabel dan rumus yang lebar dapat digulir secara lokal pada layar kecil.
Produksi berikutnya berlanjut dari `point/Bayes.html`.

- Arsip Zenodo checkpoint 13/29: <https://doi.org/10.5281/zenodo.22059764>
- DOI konsep semua versi: <https://doi.org/10.5281/zenodo.22059763>
- Pembaca web dan sumber GitHub: sementara tidak tersedia selama peninjauan
  penangguhan akun; alamat kanonisnya tetap
  <https://github.com/KokunoYumeto/mathematical-statistics-id>
- Karya sumber resmi: <https://www.randomservices.org/random/>

Pembaca luring dibangun secara deterministik dari `source/id-ID/` dengan
`python scripts/build_first_unit.py`, lalu diperiksa dengan
`python scripts/qa_first_unit.py`. Lapisan mesin netral-lokal yang mencakup
seluruh 29 halaman berada di `backend/` dan dapat diputar ulang dengan
`python scripts/generate_random_backend.py --check-only`.

Edisi ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random
Services. Lihat [LICENSE.md](LICENSE.md) untuk atribusi, perbedaan pemberitahuan
CC BY 2.0 / CC BY 1.0 pada sumber resmi, lisensi komponen, dan batas hak media
pihak ketiga.

Pemulihan produksi dimulai dari `00_control/CURRENT_STATE.md` dan
`00_control/CURRENT_CURSOR.md`.
