# Statistika Matematis — Bahasa Indonesia (id-ID)

Edisi Bahasa Indonesia independen yang dikerjakan dalam jalur kurikulum O006 /
C140, Statistika Matematis. Korpus edisi ini adalah bab statistika matematis
(bab 5–8) dari karya Kyle Siegrist, *Random: Probability, Mathematical
Statistics, and Stochastic Processes*. Edisi lengkap ini tetap diproduksi
sebagai sumber terbuka tersendiri; edisi ini bukan satu-satunya tulang punggung
naratif untuk kursus C140 yang dikonfigurasi secara terpisah.

Provenans terjemahan: OpenAI Codex gpt-5.6-sol, Ultra. Semua kredit karya
sumber, penulis, dan kontributor manusia tetap dipertahankan secara terpisah.

Status pembaca: **16 dari 29 halaman sumber inti telah diterjemahkan**, secara
berurutan dari indeks Sampel Acak sampai `point/Sufficient.html`.
Korpus belum selesai; repositori ini tidak mengklaim kelengkapan dini.

Checkpoint enam belas halaman lulus dua pemutaran ulang build dan QA
deterministik: 46 berkas pembaca, 505 unit instruksional, 326 pengungkapan
jawaban/rincian, dan 804 wadah MathJax pada halaman Statistik Cukup, Lengkap,
dan Ancillary.
Pemeriksaan
desktop/seluler menemukan tata letak yang terpusat dan memenuhi halaman, tanpa
galat konsol, TeX mentah, gambar hilang, atau luapan horizontal halaman. PDF
pembaca langsung berisi 197 halaman A4 dan seluruh rincian yang diperluas.
Produksi berikutnya berlanjut dari `interval/index.html`.

- Arsip Zenodo checkpoint terbaru: lihat receipt publik di `00_control/` setelah
  rilis; DOI konsep semua versi tetap <https://doi.org/10.5281/zenodo.22059763>
- DOI konsep semua versi: <https://doi.org/10.5281/zenodo.22059763>
- Pembaca web: <https://kokunoyumeto.github.io/mathematical-statistics-id/>
- Sumber, riwayat, dan rilis PDF GitHub:
  <https://github.com/KokunoYumeto/mathematical-statistics-id>
- Rilis PDF checkpoint 16/29: public link is recorded in the sixteen-page
  publication receipt under `00_control/`.
- Pointer metadata Figshare checkpoint 16/29: public DOI is recorded in the
  sixteen-page publication receipt under `00_control/`.
- Karya sumber resmi: <https://www.randomservices.org/random/>

Pembaca luring dibangun secara deterministik dari `source/id-ID/` dengan
`python scripts/build_first_unit.py`, lalu diperiksa dengan
`python scripts/qa_first_unit.py`. Lapisan mesin netral-lokal yang mencakup
seluruh 29 halaman berada di `backend/` dan dapat diputar ulang dengan
`python scripts/generate_random_backend.py --check-only`.
PDF dibangun dengan `python scripts/build_pdf_reader.py` setelah dependensi
Python pada `requirements.txt`, Node.js, Playwright, dan Chrome/Chromium
tersedia. Jalur nonstandar dapat diberikan melalui `O006_NODE`,
`O006_PLAYWRIGHT_DIR`, dan `O006_CHROME`.

Edisi ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random
Services. Lihat [LICENSE.md](LICENSE.md) untuk atribusi, perbedaan pemberitahuan
CC BY 2.0 / CC BY 1.0 pada sumber resmi, lisensi komponen, dan batas hak media
pihak ketiga.

Pemulihan produksi dimulai dari `00_control/CURRENT_STATE.md` dan
`00_control/CURRENT_CURSOR.md`.
