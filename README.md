# Statistika Matematis — Bahasa Indonesia (id-ID)

Edisi Bahasa Indonesia independen yang dikerjakan dalam jalur kurikulum O006 /
C140, Statistika Matematis. Korpus edisi ini adalah bab statistika matematis
(bab 5–8) dari karya Kyle Siegrist, *Random: Probability, Mathematical
Statistics, and Stochastic Processes*. Edisi lengkap ini tetap diproduksi
sebagai sumber terbuka tersendiri; edisi ini bukan satu-satunya tulang punggung
naratif untuk kursus C140 yang dikonfigurasi secara terpisah.

Provenans terjemahan: OpenAI Codex gpt-5.6-sol, Ultra. Semua kredit karya
sumber, penulis, dan kontributor manusia tetap dipertahankan secara terpisah.

Status pembaca: **15 dari 29 halaman sumber inti telah diterjemahkan**, secara
berurutan dari indeks Sampel Acak sampai `point/Unbiased.html`.
Korpus belum selesai; repositori ini tidak mengklaim kelengkapan dini.

Checkpoint lima belas halaman lulus dua pemutaran ulang build dan QA
deterministik: 45 berkas pembaca, 466 unit instruksional, 300 pengungkapan
jawaban/rincian, dan 247 wadah MathJax pada halaman Penduga Tak Bias Terbaik.
Pemeriksaan
desktop/seluler menemukan tata letak yang terpusat dan memenuhi halaman, tanpa
galat konsol, TeX mentah, gambar hilang, atau luapan horizontal halaman. PDF
pembaca langsung berisi 182 halaman A4 dan seluruh rincian yang diperluas.
Produksi berikutnya berlanjut dari `point/Sufficient.html`.

- Arsip Zenodo checkpoint 15/29: <https://doi.org/10.5281/zenodo.22062664>
- DOI konsep semua versi: <https://doi.org/10.5281/zenodo.22059763>
- Pembaca web: <https://kokunoyumeto.github.io/mathematical-statistics-id/>
- Sumber, riwayat, dan rilis PDF GitHub:
  <https://github.com/KokunoYumeto/mathematical-statistics-id>
- Rilis PDF checkpoint 15/29:
  <https://github.com/KokunoYumeto/mathematical-statistics-id/releases/tag/v2026.08.22.15>
- Pointer metadata Figshare checkpoint 15/29:
  <https://doi.org/10.6084/m9.figshare.33314784.v3>
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
