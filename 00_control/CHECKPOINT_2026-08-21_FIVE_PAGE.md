# Five-page reader checkpoint — 2026-08-21

This checkpoint binds the first five contiguous id-ID pages of the independent
29-page Random mathematical-statistics edition. It is a coherent sampling,
LLN, and CLT boundary, not a claim that the edition or configured C140 course is
complete. C140's distinct component architecture is recorded in
`C140_CONFIGURED_ARCHITECTURE_2026-08-21.md`.

## Translated source

| Ordinal | Path | Authority SHA-256 | Target SHA-256 |
|---:|---|---|---|
| 1 | `random/sample/index.html` | `9f7b9a075c430efbae92192e131152c6728f7827dc3dde987ce871ec9d6ae35c` | `bfb55848e53e4cb8cb937501e8c11d13472cad7b119d3c7f01af5fbb0023d15d` |
| 2 | `random/sample/Introduction.html` | `0af72fbf0202413525cae99e696cfa70014a803d6c5ac7a7dcafd1577742414f` | `f79a0e459b01a0598ee5f135afd7bde0c6f7020e9cbeda3756a773dde5de8539` |
| 3 | `random/sample/Mean.html` | `e21a3da7773a6f7f925b4cb0c583d5331abb1656fe01ed952c8d42b26f238cab` | `a30c72a0b9311a5d817cade1f05f2f1e315fa53aea587237c50b511351ee0e7a` |
| 4 | `random/sample/LLN.html` | `8662dfc55683fa40c79a5d453a450730e2ba151716a20eb61a2db307c33f5e85` | `2083cab957f8b07a0982280548f5c49c6e164ebd0354432036eed25276514ddf` |
| 5 | `random/sample/CLT.html` | `ee6dc9f8e9feb14f19f96a0206c3289a4aedfc014f5e3dabf79422e1dc29f9e3` | `427b4e396750be3137894296cde1a0bfc558d53a91009c1880447c250f3b0d56` |

The first four target hashes changed only because seven navigation occurrences
now resolve to local `CLT.html`. Authority bytes remain immutable.

## CLT boundary audit

- Authority/target topology: 424 elements in identical hierarchy; hierarchy
  SHA-256 `911fcd5705e0e358fb92492b30dea1d53265df24da8d86bf68b10a7f3d56c870`.
- Census: 38 units, 21 disclosures, 394 TeX spans, 56 target IDs, and three
  byte-identical raw script/style blocks.
- Target: 46,488 bytes; SHA-256
  `427b4e396750be3137894296cde1a0bfc558d53a91009c1880447c250f3b0d56`.
- Href audit: 54 exact delta entries / 75 occurrences; 11 local completed-page
  occurrences and seven same-page fragments close; all mapped external links
  use ordinary official HTTPS URLs; no JavaScript link remains.
- Thirty-three additive IDs use the `o006.random.sample.clt.*` namespace;
  native IDs are unchanged and every instructional unit has an ID.
- Fourteen exact protected-math repairs are declared: zero-origin condition;
  correlation domain, formula, and proof citation; the rigorous Peano-form CLT
  proof; indexed continuity event; restored gamma simulator parameter; dice
  result; negative-binomial support, shape domain, variable, event, and
  percentile binding. One remaining `\text{ as }` is localized to
  `\text{ ketika }`; `var`, `sd`, `cov`, and `cor` remain operators.
- Prose audit also closes the chi-square definition, negative-binomial success
  parameter, misleading generated cross-reference, omitted simulator input,
  and determinate name, conjunction, spelling, and punctuation defects.
- A direct paired visible-text audit found no unchanged English instructional
  prose; the only unchanged alphabetic direct nodes are `Random` and nine
  proper names. No formula drift or undeclared attribute delta passed QA.

## Backend

- 6,567 deterministic entities and 9,035 relations over all 29 source pages.
- 949 entities on ordinals 1–5 carry verified id-ID bindings; 5,618 later
  entities explicitly remain untranslated/null.
- Entity JSONL: 10,206,280 bytes; SHA-256
  `243b4f4294535a421fe18a811795336fae9830ead97a049e2f3f009faa435d55`.
- Relation CSV: 1,182,589 bytes; SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- Backend receipt: 18,709 bytes; SHA-256
  `1f0fad93c4bd875b7abfa6548c283704922aa6fe4c986e82eb1df1b293e29a45`.
- Translation ledger: 1,782 bytes; SHA-256
  `30553ced7cbf723efb8a20b77b4a8035a088245f0d8a6bd4e3766b9753824d42`.
- Entity identity/order and every relation byte remain stable; only verified
  locale bindings expand.

## Reader build and QA

- Reader: 28 files / 1,926,717 bytes.
- Canonical manifest: 2,701 bytes; SHA-256
  `c853d3c560b041fd3071f390b636aaf3b90b1bf076bfd47457408e6052350dbd`.
- Build receipt: 36,433 bytes; SHA-256
  `364ec734f8e50ea033d4c9ff8dc6a947baf2b062634ef7ffdbd928aa2f89635a`.
- QA receipt: 23,020 bytes; SHA-256
  `ff55bab5813e402b12c7449e98a05b8135bf2b3c17a0d661ab4ff44fa3a7cd61`.
- QA census: five translated pages, 1,867 source elements, 107 units, 73
  disclosures, 1,128 TeX spans, 118 local references, 22 fragments, 191 href
  delta entries / 274 occurrences, and one pinned MathJax runtime module.
- Reader pages are byte-identical to targets. Exact topology, protected math,
  IDs, href allowlists, HTTPS policy, local closure, privacy, licences,
  responsive reflow, and runtime dependency checks pass.

## Publication state

Published from source commit
`79d6adf164a28ba4ba6c9894397ff8cd4d6286df` (tree
`3dea7921607a44069be287db10ef35ccdd15a298`). Workflow run `32528680262`,
job `96916114133`, Pages deployment `6029599489`, and final deployment-status
record `17141386238` all succeeded.

Anonymous HTTPS readback matched all 28 manifest rows / 1,926,717 bytes by
size and SHA-256. Live CLT QA at 1280×720 and 390×844 rendered all 394 MathJax
expressions, 38 units, and 21 disclosures. Desktop body width was 1,152 px and
centered at x=56.44 within a 1,265 px document client. Mobile body width was
351.11 px at x=12 within a 375 px document client; all 130 wide elements were
contained and document scroll width stayed 375 px. Both viewports had zero raw
TeX delimiters, incomplete images, console warnings/errors, or page-level
horizontal overflow. Visual snapshots passed; the temporary viewport was reset
and the temporary tab closed. The sanitized exact evidence is in
`PUBLICATION_RECEIPT_2026-08-21.json`.

Public reader: <https://kokunoyumeto.github.io/mathematical-statistics-id/>.
Next source cursor: `random/sample/Variance.html` (ordinal 6 of 29).
