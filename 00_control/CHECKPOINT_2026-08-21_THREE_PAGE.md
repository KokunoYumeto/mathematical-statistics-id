# Three-page reader checkpoint — 2026-08-21

This checkpoint binds the first three contiguous id-ID pages of the admitted
29-page Random mathematical-statistics core. It is an honest intermediate
reader, not a claim that O006/C140 is complete.

## Translated source

| Core ordinal | Path | Authority SHA-256 | Target SHA-256 |
|---:|---|---|---|
| 1 | `random/sample/index.html` | `9f7b9a075c430efbae92192e131152c6728f7827dc3dde987ce871ec9d6ae35c` | `5673cb96ddccad719ed00e84ed5817cd4d378419ee0b1aaf7e226f6bfb3c02ed` |
| 2 | `random/sample/Introduction.html` | `0af72fbf0202413525cae99e696cfa70014a803d6c5ac7a7dcafd1577742414f` | `ab861c521bf9d078bf35db60b45bde1f6e6f7749dd3b77c712397bb6bc3f1c4e` |
| 3 | `random/sample/Mean.html` | `e21a3da7773a6f7f925b4cb0c583d5331abb1656fe01ed952c8d42b26f238cab` | `2df29d408c4e8194ac81d68a4abf623b908660adc098deccbb1d15c09c7e0fa9` |

Authority bytes are immutable. The target records the exact determinate source
corrections in `ADVERSE_LEDGER.jsonl`; every protected mathematical delta is
explicitly allowlisted and counted by the build and QA scripts.

## Backend

- 6,567 deterministic entities and 9,035 relations over all 29 core pages.
- 760 structural units; 260 exercise-designated and 500 not designated.
- Entity JSONL: 8,810,386 bytes; SHA-256
  `b7f807b9ac6701c54b719c44053cc015bbabcec7cfd0b30fd2c39b588bc19d3c`.
- Relation CSV: 1,182,589 bytes; SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- Backend receipt SHA-256:
  `06ccf5bed11f5ff5dcbd9624156a42692845f5d042e66908a876767d557f4cfa`.

## Reader build and QA

- Reader: 26 files / 1,845,409 bytes.
- Canonical manifest: 2,513 bytes; SHA-256
  `52edafb9d815fb07c1c51a46ab036e71989436088b418270b33ab0465d366a8f`.
- Build receipt SHA-256:
  `82675f175706287a52292bb48e01cfa0cc93b06253c8641925381e6ab9eb8a94`.
- QA receipt SHA-256:
  `b2520463e7b68319555e4dfa0cdc8160d4df65e70cd6cee33b5494256861b546`.
- QA census: 3 pages, 48 units, 39 disclosures, 466 TeX spans, five
  allowlisted protected-math replacements, 56 local references, 8 local
  fragments, and one pinned MathJax runtime module. Reader copies are
  byte-identical to translated targets.
- The exact desktop/mobile CSS appendix is statically verified. Live visual
  and anonymous byte readback are required immediately after Pages deployment
  before this checkpoint may be called publicly verified.

The first Pages deployment passed anonymous byte readback but failed browser
QA: MathJax 3.1.2 attempted to load the omitted local path
`MathJax/input/tex/extensions/boldsymbol.js`, leaving equations unrendered.
The repair pins the official MathJax 3.1.2 tag, commit
`c8292351190ce249f7143f224dbe7a190c8228fe`, and blob
`4570456930955792300c57537ad580ef14311335`; the decoded reader file is 4,709
bytes with SHA-256
`716cf8735d00abfb1627f8adbbf4aeb915ac9b5c55d47aeaf276e73dac6a2aa1`.
The failed deployment is rejected evidence, not an accepted checkpoint.

Two consecutive replay pairs passed with identical hashes:

```text
python scripts/build_first_unit.py --check-only
python scripts/qa_first_unit.py --check-only
```

Next source cursor: `random/sample/LLN.html`.
