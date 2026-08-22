# Seven-page reader checkpoint — 2026-08-22

This checkpoint binds the first seven contiguous id-ID pages of the independent
29-page Random mathematical-statistics edition. It advances the sample chapter
through order statistics. It does not claim that the edition or the separately
configured C140 course is complete.

## Newly completed source

- Source: `random/sample/OrderStatistics.html`, ordinal 7 of 29.
- Authority: 63,965 bytes; SHA-256
  `19ff485c600d4294e888c1b3d05ff7eb9196449f958d3325fd72b416aca56d63`.
- Target: 69,010 bytes; SHA-256
  `351bc402538eebdffff10e5fb24161676ff36c39c80530c62b9168213211e48f`.
- Exact topology: 846 elements; hierarchy SHA-256
  `defd30f9442dfee7bcfde3f71e15567a96bce8c91132b75240cb23f2c2adc76c`.
- Census: 51 units, 34 disclosures, 569 delimited TeX spans, four
  byte-identical raw script/style blocks, and 73 IDs.
- Corrections: 48 declared mathematical repairs and no incidental TeX drift.
  They include the midrange, quantile endpoints and singleton case, tied
  empirical CDF, transformed quantiles, probability-plot notation, range-law
  domains and variance, ordered-support notation, four-dice range masses,
  physical units, and independently recomputed Iris, Michelson, M&M, and
  Cicada summaries. Authority bytes remain immutable.
- Links: 38 exact href-delta entries / 51 occurrences. Twelve earlier links
  from pages 1–6 now resolve locally to OrderStatistics. The page adds the
  frozen `BoxPlot.png` support asset.

The source's visibly incomplete Michelson stem-and-leaf display is retained
with an explicit note identifying the 28 omitted leaves and linking the
official data surface. The edition notice is 1,361 bytes, SHA-256
`3951beb5dc62b6796a5fda4afe5472c0b25a516294fb7e3dcc4a40764d0d726e`.

## Backend

- 6,567 deterministic entities and 9,035 relations over all 29 source pages.
- 1,785 entities on ordinals 1–7 carry verified id-ID bindings; 4,782 later
  entities explicitly remain untranslated/null.
- Entity JSONL: 10,289,990 bytes; SHA-256
  `7fec8864f403d12a281e4f3ff52dd1ee0dfe072e3ba252ee28f0ba7e25e5ae98`.
- Relation CSV: 1,182,589 bytes; SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- Backend receipt: 19,684 bytes; SHA-256
  `85a2e2ae66a1dbb6ad96ec25157e90abe255bdc6140da62c031316175bd837cc`.
- Translation ledger: 2,632 bytes; SHA-256
  `c3d4abc6f72148803e9ccdc83a78a118985c66a58e4c0f44f938f1c889bf6a7e`.

## Reader, deterministic QA, and local rendering

- Reader: 31 files / 2,055,914 bytes.
- Canonical manifest: 3,001 bytes; SHA-256
  `46ae01e822f9f53416cad5f5d85d64888ecc2265a85ccbeb68c4d9359c400368`.
- Build receipt: 70,055 bytes; SHA-256
  `691aec356dd3d445174a029af76451d7b07df604f458fece0d6056d14de9c931`.
- QA receipt: 56,728 bytes; SHA-256
  `290c31e8a6cf6dc6764e0d0d1e04c417932850587204bbcfa5f30f1ed0f01c62`.
- Aggregate census: seven translated pages; 3,540 source elements; 205 units;
  146 disclosures; 2,280 TeX spans; 310 IDs; 212 local references; 46
  fragments; 248 href-delta entries / 343 occurrences; 91 protected
  mathematical correction categories.
- Two consecutive backend/build/QA check-only replays returned the identical
  hashes above.

The reader-only readable-layout appendix is version
`o006-id-readable-layout-v3`: 987 bytes, SHA-256
`f25dd42eb8d52325041d6e97c5b275cdc1b11fa1b635cdd60257a4878514e450`.
It preserves the centered 72-rem desktop measure and gives mobile tables and
display equations their own horizontal scrollers. It also applies standard
visually clipped containment to assistive MathML, preserving its semantic
content without letting it widen the visual canvas.

Local live rendering of OrderStatistics passed at 1280×720 and 390×844. Both
sizes produced 569 MathJax containers, 51 units, 34 disclosures, five complete
images, zero visible raw-TeX markers, and zero console warnings/errors. Desktop
body width was 1,152 px, centered at x=56.44 in a 1,265 px document client.
Mobile body width was 351.11 px at x=12 in a 375 px document client; document
scroll width was exactly 375 px. The 662-px Michelson table and seven wider
display equations remain usable through local horizontal scrollers rather than
forcing page-level overflow. Visual snapshot review passed.

## Publication state

The translation boundary was first pushed at commit
`4c1e9ac7beab9174c5a01f5d7e45290cd18a8396`. Workflow run `32546700625`
correctly failed before deployment because the manifest-bound 790-byte
`authority/upstream/random/sample/BoxPlot.png` was covered by the repository's
authority-ignore rule and therefore absent from the clean runner. The exact
authority copy was force-added without changing its bytes or the reader at
commit `fd340e9f9a834584216a6480dd104c5bcbe4c66c`.

Workflow run `32546766027`, job `96966470663`, Pages deployment `6032396193`,
and deployment status `17150132847` then completed successfully. Anonymous
HTTPS readback matched all 31 manifest rows / 2,055,914 bytes by exact size and
SHA-256 on the first post-deployment attempt.

The live public OrderStatistics page rendered 569/569 MathJax containers at
1280×720 and 390×844, with 51 units, 34 disclosures, five complete images,
zero raw-TeX markers, zero console messages, and no page-level horizontal
overflow. Desktop remained centered at 1,152 px. The mobile document remained
exactly 375 px wide; two tables and seven displayed equations exposed local
horizontal scrollers. Visual review of the page head and the Michelson table
passed. The temporary viewport was reset and both verification tabs were
closed. Sanitized evidence is recorded in
`PUBLICATION_RECEIPT_2026-08-22_SEVEN_PAGE.json`.

Next source cursor: `random/sample/Covariance.html`, ordinal 8 of 29.
