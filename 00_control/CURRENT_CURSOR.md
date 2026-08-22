# Production cursor

- Role: O006 / C140 Mathematical Statistics
- Locale: id-ID
- Authority manifest: `authority/SOURCE_URL_MANIFEST.csv`
- Authority manifest SHA-256:
  `d36e0f8bf9fa44a38a7504f9688a08af6787d88ede99298316a3e022b6f799f5`
- Ordered core: the `core_paths` array in
  `authority/SOURCE_FREEZE_RECEIPT.json`
- Last completed source page: `random/sample/Variance.html` (core ordinal 6 of 29)
- Next contiguous source page: `random/sample/OrderStatistics.html` (core ordinal 7)
- Latest reader: 6 translated pages; 29 files; 1,986,156 bytes; manifest
  SHA-256 `d3d2aa5822b4a004536b855d1e08ba72073a4e41c8fbfe5b6932db000c5de1e8`
- Latest deterministic QA receipt SHA-256:
  `b296c0f884194354d1fb4281c1f80ad973bcfc835d255a934520a1410a36c0a5`
- Public state: the five-page checkpoint is verified at
  <https://kokunoyumeto.github.io/mathematical-statistics-id/> from source
  commit `79d6adf164a28ba4ba6c9894397ff8cd4d6286df`. All 28 public files / 1,926,717
  bytes matched the manifest, and CLT passed live desktop/mobile rendering with
  394/394 MathJax outputs and no page-level overflow. Publication-receipt
  SHA-256: `35ca61902a110eea71ea1a06e0ac566a81b1f27d7dbfac4e4cb006d50220276c`.
  The six-page Variance checkpoint is locally complete and has passed two
  deterministic replays plus desktop/mobile rendering; publication and public
  byte readback are the immediate next transaction.

Resume by reading this file, `CURRENT_STATE.md`, the freeze receipt, and the
last row of `TRANSLATION_LEDGER.csv`. Publish and verify the six-page boundary,
then continue with `random/sample/OrderStatistics.html`; do not restart source
selection or repeat the completed six-page unit.
