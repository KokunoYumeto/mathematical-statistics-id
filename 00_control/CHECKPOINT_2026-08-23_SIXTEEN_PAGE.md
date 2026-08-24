# O006 / C140 — sixteen-page production checkpoint

Date: 2026-08-23  
Locale: `id-ID`  
Edition: Kyle Siegrist, *Random*, chapters 5–8, independent Indonesian reader  
Boundary: core ordinals 1–16 of 29, through `random/point/Sufficient.html`

## Cursor and authority

- Last completed source: `random/point/Sufficient.html` (ordinal 16).
- Next source: `random/interval/index.html` (ordinal 17), 7,789 bytes, SHA-256
  `85fcad0292636fbae0935ebb775a87b9e4dbdf33692b5e2823b353163d168403`.
- Sufficient authority: 57,507 bytes, SHA-256
  `4d7402f2a960ea2b4232e57e4ee5992ac29801b9269f300f17f8e83074d5a0e4`.
- Sufficient target: 60,930 bytes, SHA-256
  `6dd895c08456da30a3a8a2aace5528a7ef32be5b6ad33c064af71fb5065250f6`.
- Authority manifest SHA-256:
  `d36e0f8bf9fa44a38a7504f9688a08af6787d88ede99298316a3e022b6f799f5`.

The target preserves all 436 source elements and 804 delimited TeX spans,
contains 39 units and 26 derivation disclosures, and has 51 retained/additive
IDs. Nineteen unlabelled source units received deterministic locale-neutral
IDs; native IDs were not replaced. The target contains 18 protected-math
repairs and four visible TeX-text localizations. The authority's missing
`Moments.html#poi` fragment is still an unresolved backend witness; the reader
maps that link to the stable translated Poisson-section anchor and does not
pretend the upstream fragment exists.

## Deterministic artifacts

- Reader: 46 files / 2,564,819 bytes.
- Reader manifest SHA-256:
  `6cdf7d7592f9468a782801ed2dae9ed7dfdc14cde445c1026cb8018bb3ef3482`.
- HTML build receipt SHA-256:
  `2c3b453aecfdd6cb3f6c5a8ada8c04ebbd0392a58412456f17c50e6d08bd99a7`.
- HTML QA receipt SHA-256:
  `238ece761f934f6a71058f2fca0a1780538283e359eb3d3c7808ff52b9758cdf`.
- Backend: 6,567 entities / 9,035 relations; 4,337 translated bindings.
- Backend receipt SHA-256:
  `6d929c056f14b6b40d2d29d50707f32f5fe19ce4ab7a6f905cac57008d3c6843`.
- Backend entities SHA-256:
  `2d36d064b3e89e7cdd281f0a91f18a8386050739fe149941aec035638536836b`.
- Backend relations SHA-256:
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159`.
- Translation ledger: 16 complete rows, SHA-256
  `592ea699a8d6aadf1bedb1d5545310a104b919ec350459efa6e24735460a1f45`.
- Adverse ledger through `O006-ADV-0200`, SHA-256
  `101011319837b60943e3d13d3a24db3a5b6cc3cc9c4ca9f963f2de705cd4493a`.

The exact local replay commands are:

```text
python scripts/generate_random_backend.py --check-only
python scripts/build_first_unit.py --check-only
python scripts/qa_first_unit.py --check-only
python scripts/qa_pdf_reader.py --manual-contact-sheets-reviewed --check-only
```

All four checks pass. The PDF is 197 A4 pages / 85,357,801 bytes, SHA-256
`f1a886ff1285315478bb7e50a773e8a5d79b47e6170a86e82e7b98126f6f6160`.
Its build receipt is SHA-256
`d3e9826b0bad4f120599a501521477c3b5344cf157fd7c25de5b6af81c7ab6a1`; its
visual-QA receipt is SHA-256
`91338964c52b6d2c8bb1f0bb0bf2f43cca3af22b4aae7cdb6a3f565bcbe13166`.
All 197 pages were rendered in ten contact sheets and eight full-resolution
spots; no clipping, local URI, encryption, or visual defect was found. The
merged PDF is not tagged; the offline HTML reader remains the
accessibility-first surface.

## Terminology and provenance gate

No qualifying Indonesian mathematical-statistics arXiv source with downloadable
TeX was found. The permitted fallback was inspected directly:
Universitas Lampung, Ramadhani (2022), 50 pages / 3,807,548 bytes, SHA-256
`be841f0f1429828251a9bb37d0bb58714cc59129da2905d94c68b5f39e04c884`.
The complete bounded search, evidence, and decisions are in
`TERMINOLOGY_QA_2026-08-22.md` (SHA-256
`46ce8b83bcd730e832bdc904c209eae754d5f6e97a95b1ec0f87c842c0bf4832`) and
`TERMINOLOGY_GLOSSARY_ID_ID.csv` (SHA-256
`4ac64a2fa99f90c019c865adb03a1f3852c99954474c4fefa8d28938dc19d93c`).
The additive provenance string is exactly `OpenAI Codex gpt-5.6-sol, Ultra`.
Source-author, Kyle Siegrist, Random, edition, and human-contributor credits
remain intact. Component rights remain separate: Random's BY witnesses and
MathJax Apache-2.0; no mixed-rights aggregate is relabelled.

## Fresh browser evidence

`LIVE_BROWSER_QA_2026-08-23_SIXTEEN_PAGE.json` has SHA-256
`d593b8c81b62476baf01f644c0ce5facc301fb464f39c9b71f547b319b1bf126`.
Credential-free local desktop (1280×720) and mobile (390×844) checks passed:
804 MathJax containers, 26 disclosures, zero incomplete images, zero raw TeX,
zero console errors/warnings, and no horizontal overflow. The root carries
`lang="id-ID"` and the exact provenance metadata.

## Publication gate

This is a coherent partial checkpoint, not completion of the 29-page edition.
It is public and anonymously verified in both available preservation lineages.
GitHub boundary commit `4677fcf1ef8357de89ae0afd4e640e8076530873`, workflow
`32655887678`, Pages, and prerelease `v2026.08.23.16` are verified by
`GITHUB_PUBLICATION_RECEIPT_2026-08-23_SIXTEEN_PAGE.json`. Zenodo record
`22071140`, DOI `10.5281/zenodo.22071140`, is the fourth immutable version in
concept `22059763`; all seven files / 88,066,334 bytes match anonymously and
zero drafts remain. Evidence is
`ZENODO_PUBLICATION_RECEIPT_2026-08-23_SIXTEEN_PAGE.json` (SHA-256
`144f27aef7b2d0ba87289c12893f17047fd66ef9b8d09f7a84380bbb2ff77ec9`).

The existing Figshare article could not be advanced: authenticated preflight
returned `403 InactiveAccount`, while its public API returned
`404 EntityNotFound`. No duplicate item or falsely licensed file was created;
the exact disposition is
`FIGSHARE_PUBLICATION_ATTEMPT_2026-08-23_SIXTEEN_PAGE.json` (SHA-256
`6d0e17a5ec559164ea85117ffa6d83be416bd666e4b14e2e4e2ff646a9eba642`).
No upstream message has been sent.

Next executable action: continue ordinal 17 `random/interval/index.html`; retry
the exact existing Figshare pointer only after account reactivation.
