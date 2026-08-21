# Four-page reader checkpoint — 2026-08-21

This checkpoint binds the first four contiguous id-ID pages of the admitted
29-page Random mathematical-statistics core. It is an honest intermediate
reader, not a claim that O006/C140 or the required linear-model bridge is
complete.

## Translated source

| Core ordinal | Path | Authority SHA-256 | Target SHA-256 |
|---:|---|---|---|
| 1 | `random/sample/index.html` | `9f7b9a075c430efbae92192e131152c6728f7827dc3dde987ce871ec9d6ae35c` | `257b7ba98e4eca06ed0b4afc340844a27477a3488def13964c64310d022103cb` |
| 2 | `random/sample/Introduction.html` | `0af72fbf0202413525cae99e696cfa70014a803d6c5ac7a7dcafd1577742414f` | `c38dfaa8dcc2e74f073d1f8975c3d66a14dd9995be5c75c8a753bdcf3e71aad6` |
| 3 | `random/sample/Mean.html` | `e21a3da7773a6f7f925b4cb0c583d5331abb1656fe01ed952c8d42b26f238cab` | `8dc9b5e1f5d21c49df5ce4075f8e9b1dbb6628aff4ae57533f34a64d21dd2e00` |
| 4 | `random/sample/LLN.html` | `8662dfc55683fa40c79a5d453a450730e2ba151716a20eb61a2db307c33f5e85` | `c302b38e338f2e582320e86d4f916440b152d7a70b7a97c761ad01fd12473416` |

The first three target hashes changed only because their navigation now points
to the local LLN page. Authority bytes remain immutable. Every protected
mathematical delta and source defect is explicitly enumerated in the build/QA
receipts and `ADVERSE_LEDGER.jsonl`.

## LLN boundary

- Authority/target topology: 305 elements in identical hierarchy; hierarchy
  SHA-256 `5c0d5dbd8f5ce20bd12602452d97e7e74779ee36a0186126919674afc4789a07`.
- Census: 21 units, 13 answer/detail disclosures, 268 TeX spans, 33 unique
  target IDs, and three byte-identical script/style blocks.
- Link deltas: 36 exact entries across 49 occurrences; 24 assembled-reader
  local references and seven fragments resolve.
- Five source-math repairs: the missing `1/n` on the negative-part sum, the
  fixed-partition density limit, `P_9`, `P_{16}`, and denominator grouping.
- Nine exact reader-language substitutions inside protected TeX text preserve
  all operators, identifiers, delimiters, and formula positions.
- The anonymous empirical-density unit receives the additive stable ID
  `o006.random.sample.lln.unit.discrete-empirical-density`.

## Backend

- 6,567 deterministic entities and 9,035 relations over all 29 core pages.
- 664 entity records on ordinals 1–4 carry verified id-ID path/hash/locale
  bindings; 5,903 records on later pages explicitly remain untranslated/null.
- Entity JSONL: 10,180,060 bytes; SHA-256
  `6427f46c6c5f8ea5bd0e6af441759d1d00b3c5104400011a64c42092fd522427`.
- Relation CSV: 1,182,589 bytes; SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- Backend receipt: 18,239 bytes; SHA-256
  `e905bfbe3cb08ad5950423edbd1a9f9b8093d62dc3c551b629df0f819c38cd10`.
- Translation ledger: 1,461 bytes; SHA-256
  `5c0dd978d479f84c5dc9e97878c59e1d593d896c11064eb153f3764ac6f0e8cb`.
- Entity IDs/order and all relation bytes remain unchanged. Draft 2020-12
  schema validation and two deterministic backend replays pass.

## Reader build and QA

- Reader: 27 files / 1,880,544 bytes.
- Canonical manifest: 2,607 bytes; SHA-256
  `d45913699c2970f75a587537e6a9b83383351f592eae880b5d36a4d6b20ab036`.
- Build receipt: 29,016 bytes; SHA-256
  `cd5aab9787e9da2159d9e7484153922b35a52313c67368fd035a62e8303d0fc1`.
- QA receipt: 15,224 bytes; SHA-256
  `a1ed8a964e8167162587606b92e5b780084095ed59b8071fa27a71f482042866`.
- QA census: 4 translated pages, 1,443 source elements, 69 units, 52
  disclosures, 734 TeX spans, 85 local references, 15 fragments, and one
  pinned MathJax runtime module. Reader pages are byte-identical to their
  translated targets.
- Exact topology, protected math, IDs, href allowlists, HTTPS policy, local
  closure, privacy, licences, responsive reflow, and runtime dependency checks
  pass. Two consecutive check-only replay pairs must match these hashes before
  publication.

## Publication state

The accepted source commit is
`612ff79040b53f2305d367119a26c0b229d0e3b4` (tree
`dbcd410818d37260e99b17b4450fe5f3612183f9`). Workflow run `32505273448`, job
`96843911029`, Pages deployment `6025637584`, and deployment-status record
`17131093081` all succeeded. Anonymous HTTPS readback matched all 27 manifest
rows / 1,880,544 bytes by size and SHA-256.

Live browser QA rendered 268/268 MathJax outputs on LLN at 1280×720 and
390×844, with 21 units and 13 disclosures. At mobile width, 225 wide
mathematical elements were contained by local scroll surfaces and none escaped
to page-level overflow. The Mean regression page rendered 366/366 expressions
at 390×844. All checks found zero raw TeX delimiters, incomplete images,
console errors, uncontained wide elements, or page-level horizontal overflow.
The desktop and mobile snapshots were visually reviewed and the temporary
viewport override was reset. Exact evidence is in
`PUBLICATION_RECEIPT_2026-08-21.json`, 4,747 bytes, SHA-256
`b96bd77870ba23c3f7635e11b85246fb1dfbfdc6557e64a5607c2d27badb2ffe`.

Next source cursor: `random/sample/CLT.html` (core ordinal 5).
