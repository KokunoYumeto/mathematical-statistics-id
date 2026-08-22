# Nine-page reader checkpoint — 2026-08-22

This checkpoint binds the first nine contiguous id-ID pages of the independent
29-page Random mathematical-statistics edition. It completes the random-sample
chapter and does not claim that the full edition or the separately configured
C140 course is complete.

## Newly completed source

- Source: `random/sample/Normal.html`, ordinal 9 of 29.
- Authority: 35,940 bytes; SHA-256
  `d9a62017ae3a8488aedac3eceedb15d8b68243ae60894104ab88564ace25ff79`.
- Target: 38,892 bytes; SHA-256
  `58a819f8775846488f653ba26dc18ed7f15711a96652866ed84b2ea91c11a6a2`.
- Exact topology: 380 source elements; hierarchy SHA-256
  `bdeb23615d43a439d714d09c6dd514747d42e400b5f01db48cd8ad9bccef2a9f`.
- Census: 29 units, 21 disclosures, 380 delimited TeX spans, three
  byte-identical raw script/style blocks, and 44 native/additive IDs.
- Declared protected changes: nine mathematical repairs. Every other protected
  TeX span is byte-preserved.
- Links: 22 exact href-delta entries / 38 occurrences; there are no
  occurrence-specific deltas on this page.
- Edition notice: 1,172 bytes; SHA-256
  `eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d`.

Two independent read-only audits closed the target before publication. They
confirmed all 380 authority/target protected spans, all nine registered repairs,
the numerical answers, the finite-positive-variance hypothesis added to the
CLT statement, and the corrected pooled-variance independence proof. They found
no remaining untranslated reader-facing English or material mathematical
defect. The source's orphan paragraph close at line 205 remains recorded rather
than silently changing topology.

The correction ledger now runs without gaps through `O006-ADV-0112`. Page-9
repairs cover malformed delimiters, the two-sample Student construction,
correlation range, central-moment notation, a missing sample-vector comma, a
mislabelled covariance statistic, sample-size conditions, the missing finite
variance hypothesis, and the logically incomplete independence proof. Authority
bytes are unchanged. No new figure or data asset was required.

## Backend

- 6,567 deterministic entities and 9,035 relations over all 29 source pages.
- 2,640 entities on ordinals 1–9 carry verified id-ID bindings; 3,927 later
  entities explicitly remain untranslated/null.
- Entity JSONL: 10,373,499 bytes; SHA-256
  `95c56925d17e34c37e8128e1ed8e4f1f349edd5cd3077ee7816f0eb98862029b`.
- Relation CSV: 1,182,589 bytes; SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- Backend receipt: 20,644 bytes; SHA-256
  `681023726a222fafa90934d657e81576d031d2e465a8454e5776cce7772a95e4`.
- Translation ledger: 3,426 bytes; SHA-256
  `1fd6f61a0a6074282470c12ed2ec26a0395f04a9e50a9eb2632e94d159d6135b`.
- Adverse ledger: 112 valid sequential records / 44,025 bytes; SHA-256
  `87f7fde9900f6ab41f13f32ba8195d474ae45b4d48bd35dba29402199f56289f`.

## Reader and deterministic QA

- Reader: 39 files / 2,244,344 bytes.
- Canonical manifest: 3,836 bytes; SHA-256
  `e38a70e74ea24f17360b47ccffbf242f09ec26cf784fa326632a85d0f999f5a3`.
- Build receipt: 101,148 bytes; SHA-256
  `29d389ca58991ac01b676b8348690b053a6841cad2b1afd212e47cc24a6fb621`.
- QA receipt: 84,419 bytes; SHA-256
  `c450c75a0bf52c650f944a19c03faa9f5a2bd828cd7eba9bd52262f60f5f7bf2`.
- Aggregate census: nine translated pages; 4,826 source elements; 292 units;
  201 disclosures; 3,455 TeX spans; 434 IDs; 362 local references; 88
  fragments; 278 href-delta categories / 383 occurrences; 136 protected-math
  categories / 131 replacements.
- The backend, build, and QA each passed two consecutive complete check-only
  replays with the exact identities above.

## Live layout and publication state

Local in-app-browser verification passed at 1280×720 and 390×844. Desktop used
a 1,265-px document client and a centered 1,152-px body at x=56.44. Mobile used
a 375-px document client and a 351.11-px body at x=12. Both had equal client and
scroll widths, no page-level horizontal overflow, and no visible element beyond
the viewport after excluding clipped assistive MathML. All 381 MathJax
containers rendered (380 delimited spans plus one raw environment), with zero
raw-TeX markers, literal tab escapes, or console warnings/errors. All four
images loaded with nonempty alternative text. The global controls opened all 21
disclosures and collapsed all 21 again. Desktop and mobile visual inspection
showed a centered, page-filling, readable layout. The temporary viewport override
will be reset after public verification.

Commit `1806863320c1c0859e04a2d93773adbb8d4ae377` (tree
`688cd4e7d104510416a3f2e647a3a125c29c2544`) was pushed to `main`.
Workflow run `32557204624`, job `96993176639`, Pages deployment `6034057446`,
and deployment status `17154596564` all completed successfully; the clean
runner replayed the deterministic backend, build, and QA before deployment.

Immediately after deployment, anonymous HTTPS GETs matched all 39 manifest
files / 2,244,344 bytes by exact size and SHA-256 with no retry or mismatch.
Before raw-source and public-browser checks could finish, GitHub suspended the
publishing account and began returning 404 for the repository, raw commit, and
Pages site. A bounded credential check found that the first supplied credential
receives GitHub's explicit account-suspended response and the second receives
`Bad credentials`; no credential value is stored or exposed. Thus the exact
reader was successfully deployed and byte-verified, but it is not currently
publicly available and public live desktop/mobile QA remains unexecuted. This
is an external GitHub availability incident, not a reader/build failure.

Exact sanitized evidence is in
`PUBLICATION_RECEIPT_2026-08-22_NINE_PAGE.json` (5,337 bytes; SHA-256
`4d7b0e510724c6e9d7cda858441e8526d7896e8983a28c238ed4d5d72b9efa36`).
Do not claim the source mirror
or Pages reader discoverable until an anonymous current-state check again
returns the expected bytes. Continue translation locally rather than looping on
the suspended identity.

Next source after publication: `random/point/index.html`, ordinal 10 of 29.
