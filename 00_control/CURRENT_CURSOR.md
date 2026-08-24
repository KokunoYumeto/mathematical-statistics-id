# Production cursor

Updated: 2026-08-24

## Lane and authority

- Role: O006 / C140 Mathematical Statistics.
- Locale: `id-ID`.
- Active component: independent complete Indonesian edition of Kyle
  Siegrist's *Random*, chapters 5–8.
- Immutable authority manifest: `authority/SOURCE_URL_MANIFEST.csv`, SHA-256
  `d36e0f8bf9fa44a38a7504f9688a08af6787d88ede99298316a3e022b6f799f5`.
- Frozen authority: 29 core documents / 1,003,900 bytes; 205 files /
  4,867,084 bytes in the bounded closure.

## Translation cursor — complete

- Last and final source page: `random/hypothesis/ChiSquare.html`, core ordinal
  29 of 29; authority 39,651 bytes / SHA-256
  `379cf5939801c94b251884c0c82f0e6efc7ecce35cec11a645881d7ca9c7a6aa`;
  target 43,445 bytes / SHA-256
  `60d8904caea827a840db04aad5f7f651ab5c6ed78672e8f0c7fcd577604ff24e`.
- Next Random page: none. Do not reopen, repeat, or extend the admitted 29-page
  boundary.
- Translation ledger: 29 contiguous `complete` rows / 18,419 bytes / SHA-256
  `ea9487f8f7cfc50318902caf878c85e527a4a8c4ec2e4d1f2796d3f4a9f85704`.
- Adverse ledger: 330 contiguous records / 149,482 bytes / SHA-256
  `e1b7d73ff16fe53552acafa32b15a885bf3c812e4ee8f4ec22830a7850efc277`.
- Bounded interval and hypothesis receipts pass at SHA-256
  `0acbf6422d8325ad104a7e6e664af7eece90e6faa790baffa34c3f01d8c6d1e5`
  and
  `42393865dbb724163c97ff3454d66aa5fdd1d01eb3f11f6e1b3d10108c8b8176`.
- Terminology/provenance QA remains closed in
  `TERMINOLOGY_QA_2026-08-22.md` and `TERMINOLOGY_GLOSSARY_ID_ID.csv`; exact
  additive provenance is `OpenAI Codex gpt-5.6-sol, Ultra`.

## Complete backend and HTML reader

- Backend: 6,567 entities / 9,035 relations; all 29 documents and all 6,567
  entities translated; zero untranslated entities. Receipt SHA-256:
  `bfa3aabef34574f31c88eb83b641af4b429bd8ad55f50a0c14ecb898ef18baf3`.
- Entities: 10,766,387 bytes / SHA-256
  `153065119b66897db7cdf94699fa36a58f7cac2294f89669683dbc863b242fdd`.
- Relations: 1,182,589 bytes / SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- Offline reader: 67 files / 2,962,390 bytes; manifest SHA-256
  `ce25e1505462bbe60cfe35a46844b40d1646baff18dff72a9f3f8bbf376c9887`.
- Reader build-receipt SHA-256:
  `9025eff944aff93122480c8e6dc30d761f6236eaa92eca6edfd953f460487521`.
- Reader QA-receipt SHA-256:
  `78b6e99ce044f9c9c9464eb197c2d9530fb1816ca9f9b7d016ff982040067737`.
- Browser QA: all 29 routes pass at 1280×900 and 390×844; 10,177 MathJax
  containers, 124 complete images, 760 units, 451 disclosures, zero console
  problems/page overflows/uncontained wide surfaces. Receipt:
  `LIVE_BROWSER_QA_2026-08-24_COMPLETE_29_PAGE.json`, SHA-256
  `e400173a33e51d04e43b5be4d2528c6ecfe22042c61af2e46dbcee9069e6a786`.

## Complete PDF

- Reader PDF: 255 A4 pages / 118,920,837 bytes / SHA-256
  `556a589cfdd54c9a7e7b5022976371ce31b68e11f947484bbc40cf7a6849a5bc`.
- PDF receipt: 97,300 bytes / SHA-256
  `7de9ed37c5a4f881f94edaa09d988f239e1e222581c419314171fcc1b095ae50`.
- Visual-QA receipt: 1,890 bytes / SHA-256
  `42366aec2a0e9f5be4a6fb4421ea0965ff831ce2f854f5f5100cacac1f8a91ff`.
- All 255 pages were rerendered and reviewed in 13 contact sheets. The rejected
  first complete candidate's Variance-table break was corrected; the accepted
  byte identity above has zero observed visual defects. The HTML reader remains
  accessibility-first because the merged PDF is not tagged.

## Current release cursor

The complete local release gate passes. Canonical checkpoint:
`CHECKPOINT_2026-08-24_COMPLETE_29_PAGE.md`. The next executable action is one
narrow final repository commit and push, then clean Pages verification, tag and
release `v2026.08.24.29` with exactly the reader PDF, anonymous byte readback,
deterministic seven-file packaging with that exact commit, and publication as
version `2026.08.24.29` in existing Zenodo concept
`10.5281/zenodo.22059763`. Do not create a duplicate Zenodo concept, retry
Figshare, ask for publication confirmation, or contact upstream.

After GitHub and Zenodo publication receipts are persisted, this independent
Random edition is complete. Overall O006/C140 then continues in a separate
component and repository with complete Penn State STAT 415, exactly the Random
completeness donor page, and the original rigor/simulation/multiple-regression/
mastery companion defined in `C140_CONFIGURED_ARCHITECTURE_2026-08-21.md`.

## Recovery order

Read `WORKFLOW.md`, this file, `CURRENT_STATE.md`, the complete checkpoint,
`SOURCE_FREEZE_RECEIPT.json`, the final translation-ledger row, the backend/
reader/PDF receipts, and the final publication receipts. Never treat historical
16-page checkpoint text as the current cursor and never run a broad workspace
or repository scan.
