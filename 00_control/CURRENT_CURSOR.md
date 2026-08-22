# Production cursor

- Role: O006 / C140 Mathematical Statistics
- Locale: id-ID
- Authority manifest: `authority/SOURCE_URL_MANIFEST.csv`
- Authority manifest SHA-256:
  `d36e0f8bf9fa44a38a7504f9688a08af6787d88ede99298316a3e022b6f799f5`
- Ordered core: the `core_paths` array in
  `authority/SOURCE_FREEZE_RECEIPT.json`
- Last completed source page: `random/point/Estimators.html` (core ordinal 11 of 29)
- Next contiguous source page: `random/point/Moments.html` (core ordinal 12)
- Latest reader: 11 translated pages; 41 files; 2,300,109 bytes; manifest
  SHA-256 `5ec24c67e16ca04ed74925f9814a8aa29a8874a10d312287a9b1d5141658e6ed`
- Latest deterministic QA receipt SHA-256:
  `2115e0416ebe3f4005d3de049983d54bd3685249b2d74b403d35a1d7f69b6180`
- Publication transaction: commit
  `1806863320c1c0859e04a2d93773adbb8d4ae377`, workflow `32557204624`, job
  `96993176639`, deployment `6034057446`, and deployment status `17154596564`
  succeeded. All 39 Pages files / 2,244,344 bytes matched anonymously
  immediately after deployment. GitHub then suspended the publishing account;
  repository, raw commit, and Pages currently return 404. Public live-browser
  QA could not be completed after withdrawal. Sanitized evidence:
  `PUBLICATION_RECEIPT_2026-08-22_NINE_PAGE.json`; SHA-256
  `4d7b0e510724c6e9d7cda858441e8526d7896e8983a28c238ed4d5d72b9efa36`.
- Ten-page local checkpoint: `CHECKPOINT_2026-08-22_TEN_PAGE.md` (5,323 bytes;
  SHA-256 `96a63189ca27fa8f50cdfe9a146fdc434913dea6813983fa088d34df453bbadb`),
  preserved in local commit `16384bdf1e9c3b00c82815f32c7bc5e11f923034`.
  Its backend, build, and QA each passed two byte-identical check-only replays. A fresh live
  browser pass is deferred because the in-app browser was unavailable. The
  one-shot 2026-08-22T09:14:35+02:00 GitHub check again returned the explicit
  suspended-account response; no credential was retried.
- Eleven-page local checkpoint:
  `CHECKPOINT_2026-08-22_ELEVEN_PAGE.md`; ordinal 11 preserves the exact
  380-element hierarchy and 432 TeX spans, binds 2,931 translated backend
  entities, passes two deterministic backend/build/QA replays, and passes new
  live desktop/mobile centered reflow checks with all 432 MathJax containers,
  no page-level overflow, and functional 15/15 disclosure controls. Exact
  commit and the single bounded GitHub boundary attempt remain to be recorded.

Resume by reading this file, `CURRENT_STATE.md`, the freeze receipt, and the
last row of `TRANSLATION_LEDGER.csv`. Continue with
`random/point/Moments.html`; perform only one bounded GitHub current-state
recheck for the eleven-page boundary, then do not loop on that external
surface. Do not restart source selection or repeat the completed pages.
