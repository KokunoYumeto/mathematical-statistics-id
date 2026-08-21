# Statistika Matematis — Bahasa Indonesia (id-ID)

Edisi Bahasa Indonesia independen untuk peran kurikulum O006 / C140,
Statistika Matematis. Sumber inti yang diterima adalah bab statistika
matematis (bab 5–8) dari karya Kyle Siegrist, *Random: Probability,
Mathematical Statistics, and Stochastic Processes*.

Status pembaca: **4 dari 29 halaman sumber inti telah diterjemahkan**
(`sample/index.html`, `sample/Introduction.html`, `sample/Mean.html`, dan
`sample/LLN.html`).
Korpus dan jembatan model linear belum selesai; repositori ini tidak mengklaim
kelengkapan dini.

Checkpoint empat halaman lulus build dan QA deterministik: 27 berkas pembaca,
69 unit instruksional, 52 pengungkapan jawaban/rincian, dan 734 rentang TeX.
Seluruh 27 berkas publik cocok dengan manifes byte demi byte. Halaman LLN dan
halaman regresi Mean juga lulus pemeriksaan visual desktop/seluler: seluruh
rumus dirender, tanpa galat konsol, aset gagal, atau luapan horizontal halaman.
Produksi berikutnya berlanjut dari `sample/CLT.html`.

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
