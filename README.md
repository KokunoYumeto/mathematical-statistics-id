# Statistika Matematis — Bahasa Indonesia (id-ID)

Edisi Bahasa Indonesia independen untuk peran kurikulum O006 / C140,
Statistika Matematis. Sumber inti yang diterima adalah bab statistika
matematis (bab 5–8) dari karya Kyle Siegrist, *Random: Probability,
Mathematical Statistics, and Stochastic Processes*.

Status pembaca: **3 dari 29 halaman sumber inti telah diterjemahkan**
(`sample/index.html`, `sample/Introduction.html`, dan `sample/Mean.html`).
Korpus dan jembatan model linear belum selesai; repositori ini tidak mengklaim
kelengkapan dini.

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
