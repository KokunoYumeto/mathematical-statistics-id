# Statistika Matematis — Bahasa Indonesia (id-ID)

Edisi Bahasa Indonesia independen untuk bab statistika matematis (bab 5–8)
dari karya Kyle Siegrist, *Random: Probability, Mathematical Statistics, and
Stochastic Processes*. Edisi ini diproduksi dalam jalur kurikulum O006/C140,
tetapi tetap merupakan sumber terbuka tersendiri dan bukan satu-satunya tulang
punggung naratif untuk kursus C140 yang dikonfigurasi secara terpisah.

**Status: lengkap, 29 dari 29 halaman inti.** Terjemahan berjalan berurutan
dari `random/sample/index.html` sampai `random/hypothesis/ChiSquare.html` dan
mempertahankan formula, bukti, latihan, rincian/jawaban, struktur, ID sumber,
tautan, aset yang sah, serta atribusi. Provenans terjemahan dan rekayasa edisi:
`OpenAI Codex gpt-5.6-sol, Ultra`. Semua kredit karya sumber, penulis, dan
kontributor manusia tetap dipertahankan.

## Hasil edisi lengkap

- pembaca HTML luring: 67 berkas / 2.962.390 byte;
- isi: 29 halaman, 760 unit instruksional, dan 451 rincian/jawaban yang dapat
  dibuka;
- matematika hidup: 10.177 wadah MathJax pada pemeriksaan peramban lengkap;
- backend netral-lokal: 6.567 entitas / 9.035 relasi, semuanya mempunyai
  ikatan id-ID yang diverifikasi;
- PDF pembaca langsung: 255 halaman A4 / 118.920.837 byte / SHA-256
  `556a589cfdd54c9a7e7b5022976371ce31b68e11f947484bbc40cf7a6849a5bc`;
- QA desktop 1280×900 dan seluler 390×844: 29/29 rute lulus tanpa gambar
  hilang, galat MathJax, luapan halaman, permukaan lebar yang tidak tertampung,
  atau peringatan/galat konsol;
- QA visual PDF: seluruh 255 halaman dirasterkan dan diperiksa dalam 13 lembar
  kontak; tidak ada cacat visual pada kandidat yang diterima.

HTML adalah permukaan aksesibilitas utama. PDF gabungan mempertahankan teks,
outline, tautan, dan rincian yang diperluas, tetapi tidak lagi bertag setelah
penggabungan deterministik.

## Akses dan preservasi

- Pembaca web: <https://kokunoyumeto.github.io/mathematical-statistics-id/>
- Repositori dan riwayat: <https://github.com/KokunoYumeto/mathematical-statistics-id>
- Rilis edisi lengkap: <https://github.com/KokunoYumeto/mathematical-statistics-id/releases/tag/v2026.08.24.29>
- DOI konsep Zenodo, selalu menunjuk versi terbaru:
  <https://doi.org/10.5281/zenodo.22059763>
- Karya sumber resmi: <https://www.randomservices.org/random/>

Figshare tidak menjadi jalur berkas publik untuk edisi ini: layanan tidak
menyediakan lisensi campuran yang sesuai, dan akun/pointer historis juga tidak
tersedia pada pemeriksaan terakhir. Tidak ada salinan berlisensi palsu atau
item duplikat yang dibuat.

## Reproduksi

Pembaca dan backend dapat diputar ulang dari akar repositori:

```text
python scripts/freeze_random_core.py --check-only
python scripts/freeze_component_assets.py --check-only
python scripts/generate_random_backend.py --check-only
python scripts/build_first_unit.py --check-only
python scripts/qa_first_unit.py --check-only
python scripts/build_pdf_reader.py --check-only
python scripts/qa_pdf_reader.py --manual-contact-sheets-reviewed --check-only
```

Build PDF memerlukan paket Python pada `requirements.txt`, Node.js,
Playwright, dan Chrome/Chromium. Jalur nonstandar dapat diberikan melalui
`O006_NODE`, `O006_PLAYWRIGHT_DIR`, dan `O006_CHROME`.

Edisi ini tidak didukung maupun disahkan oleh Kyle Siegrist atau Random
Services. Lihat [LICENSE.md](LICENSE.md) untuk atribusi, perbedaan pemberitahuan
CC BY 2.0 / CC BY 1.0 pada sumber resmi, lisensi komponen, dan batas hak media
pihak ketiga.

Pemulihan produksi dimulai dari `00_control/WORKFLOW.md`,
`00_control/CURRENT_STATE.md`, dan `00_control/CURRENT_CURSOR.md`. Keputusan
terpisah mengenai Penn State STAT 415 dan pendamping C140 berada di
`00_control/C140_CONFIGURED_ARCHITECTURE_2026-08-21.md`.
