# Statistika Matematis — Bahasa Indonesia (id-ID)

Edisi Bahasa Indonesia independen yang dikerjakan dalam jalur kurikulum O006 /
C140, Statistika Matematis. Korpus edisi ini adalah bab statistika matematis
(bab 5–8) dari karya Kyle Siegrist, *Random: Probability, Mathematical
Statistics, and Stochastic Processes*. Edisi lengkap ini tetap diproduksi
sebagai sumber terbuka tersendiri; edisi ini bukan satu-satunya tulang punggung
naratif untuk kursus C140 yang dikonfigurasi secara terpisah.

Status pembaca: **7 dari 29 halaman sumber inti telah diterjemahkan**, secara
berurutan dari indeks Sampel Acak sampai `sample/OrderStatistics.html`.
Korpus belum selesai; repositori ini tidak mengklaim kelengkapan dini.

Checkpoint tujuh halaman lulus dua pemutaran ulang build dan QA deterministik:
31 berkas pembaca, 205 unit instruksional, 146 pengungkapan jawaban/rincian,
dan 2.280 rentang TeX. Halaman Statistik Terurut lulus pemeriksaan visual
desktop/seluler dengan 569 rumus dan lima gambar lengkap, tanpa galat konsol,
TeX mentah, atau luapan horizontal halaman. Tabel dan rumus yang lebar dapat
digulir secara lokal pada layar kecil. Seluruh 31 berkas publik cocok dengan
manifes byte demi byte. Produksi berikutnya berlanjut dari
`sample/Covariance.html`.

- Pembaca web: <https://kokunoyumeto.github.io/mathematical-statistics-id/>
- Sumber dan bukti: <https://github.com/KokunoYumeto/mathematical-statistics-id>
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
