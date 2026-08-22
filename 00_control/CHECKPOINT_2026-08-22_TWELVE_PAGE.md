# Twelve-page checkpoint — O006 Random id-ID

Recorded: 2026-08-22T18:07:03.4327536+02:00

## Boundary

Core ordinals 1–12 of 29 are complete through
`random/point/Moments.html`. This is a coherent local edition boundary, not a
claim that the complete Random edition or configured C140 course is complete.
The next contiguous authority page is `random/point/Likelihood.html`, ordinal
13.

The Moments target passed an independent language audit, an independent
mathematics/topology audit, and an independent build/QA integration audit. The
exact frozen authority remains immutable. A corrupted intermediate localizer
draft was rejected and is not evidence; the admitted target is reproduced only
by the final hash-locked localizer.

## Ordinal 12 identities

- Authority: `authority/upstream/random/point/Moments.html`; 48,492 bytes;
  SHA-256
  `43755b5bee6179fca8d7c1c964e7c6a9bb1a9de6f3916130100c69e666a3194e`.
- Target: `source/id-ID/random/point/Moments.html`; 57,501 bytes; SHA-256
  `911915cdc9352f2624cb1bf321e4be66de947ef599b2fe63d80ae1d80d17dd27`.
- Authority census: 440 parsed elements; hierarchy SHA-256
  `8852c8962c89ef48248ba8c192af3a19d7744869de6a82c625c5280100a1bf90`;
  649 TeX spans; 37 units; 29 details; 23 native IDs; three raw script/style
  blocks.
- Target census after removing the separately validated edition notice: the
  same 440-element hierarchy and all 649 TeX spans; 37/37 units retain their
  order and 54 total IDs comprise all native IDs plus 31 additive stable IDs.
- Navigation: 37 exact href-delta categories / 48 occurrences; translated
  index, Estimators, sample, stylesheet, and icon surfaces remain local;
  untranslated Random and ancillary surfaces become credential-free official
  HTTPS anchors. There are 30 local references, 13 same-page fragment
  occurrences, and 52 external HTTPS anchors.
- Edition notice: 1,172 bytes; SHA-256
  `eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d`.

The newly local point cross-links are exact:

- `source/id-ID/random/point/index.html`: 11,267 bytes; SHA-256
  `16aaef9344b2d0f86041ba8ac5d64336f7f7a4e0880598a05e668b940a4d6bdd`;
- `source/id-ID/random/point/Estimators.html`: 44,352 bytes; SHA-256
  `4a271e29ca745eeea8a9aa386b9d21aa36f10fab123334415587155dbb5fd5a7`.

## Proved corrections

`ADVERSE_LEDGER.jsonl` records the ordinal-12 findings as O006-ADV-0130
through O006-ADV-0141. Twelve protected mathematical repairs are exact and
machine-checked across the following ten categories:

1. the undefined `\W_n^2` macro is replaced by the declared statistic;
2. the malformed sample-size set loses its empty trailing entry;
3. expectation and probability notation use the declared macros;
4. the missing negative-binomial shape factor is restored in `Var(M)`;
5. both ambiguous gamma variance denominators become `b^2/(kn)`;
6. the symmetric-beta estimator becomes
   `(1 - 2 M^(2))/(4 M^(2) - 1)`;
7. the Pareto support includes its lower endpoint;
8. the two-parameter uniform location estimator becomes `M - sqrt(3) T`;
9. the Pareto scale estimator is named `V_a`; and
10. the hypergeometric support lower bound becomes `max(0,n-N+r)`.

The target also supplies the finite-fourth-moment and nondegeneracy hypotheses
for the asymptotic variance/MSE ratios, repairs the sign in their leading-term
proof, states the exact symmetric-beta feasibility range, weakens the general
Jensen conclusion from universally strict negative bias to nonpositive bias,
and records the finite-sample domains of the negative-binomial, gamma, beta,
Pareto, uniform, and hypergeometric formulas. Four omitted paragraph closes
are restored without changing parsed topology. Determinate source prose and
three orphan `(a)` references are rendered naturally.

The adverse ledger now contains 141 sequential valid JSON records; 58,759
bytes; SHA-256
`ae320c06c0012767c4038a142b257f12dcc9f954c99e139d3c7280cafbdfcdfa`.

## Backend

The complete authority backend remains 6,567 entities / 9,035 relations. The
first 12 documents bind 3,243 translated entities; 3,324 entities on the
remaining 17 documents stay explicitly untranslated.

- `backend/entities.jsonl`: 10,431,935 bytes; SHA-256
  `be579f147cef70bade84bcb30f34973697eaa61018b4e7f277c0381f7307c233`.
- `backend/relations.csv`: 1,182,589 bytes; SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- `backend/BACKEND_RECEIPT.json`: 22,082 bytes; SHA-256
  `9c93c0a65c48790ed5759fe6fab289d56e3fa5aaeeb6b63b2728cdb03237dace`.
- `00_control/TRANSLATION_LEDGER.csv`: 5,044 bytes; SHA-256
  `fc910d4b723de0cc37b9b4955407914521a9915c9334b297373167366f72b578`.

## Reader and deterministic QA

- Reader: 42 files / 2,357,478 bytes.
- Manifest: 4,128 bytes; SHA-256
  `020f808d914fefd34e92473da916c2d3f845464ebb38e3bc4380ef173451669f`.
- Build receipt: 127,649 bytes; SHA-256
  `fdfe451256e13dd08679f4c0e9186366663e4d6566dabc6cc8a24d6560be250c`.
- QA receipt: 111,616 bytes; SHA-256
  `7369eae27c7958b964c780983b0c0929ab0beed10ad16c42f83439df9fe01a4b`.

The aggregate QA census is 12 translated pages, 5,801 source elements, 362
units, 245 details, 4,536 TeX spans, 545 IDs, 432 local references, 106
fragments, 383 href-delta categories / 522 occurrences, and 158 protected
mathematical replacements in 163 registered categories. Reader targets are
byte-identical to the source/id-ID targets. HTML topology, scripts/styles,
TeX, IDs, links, fragments, assets, HTTPS policy, rights, privacy, the pinned
MathJax runtime, and readable-layout v3 pass.

Two consecutive complete check-only replays of backend, build, and QA returned
the same identities above.

## Live readable-layout pass

The local built reader was loaded from a bounded temporary HTTP server and
visually inspected in the in-app browser.

- Desktop override 1280×720 (effective content viewport 1265×720): the body is
  1,152 px wide and centered to 0.111 px subpixel tolerance; all 652 MathJax
  containers rendered; 37 units, 29 details, and four complete images were
  present; no raw TeX, out-of-viewport element, or page-level horizontal
  overflow was found.
- Mobile override 390×844 (effective content viewport 375×844): the body is
  351.111 px wide with 12 px nominal margins and the same subpixel centering
  tolerance; all 652 MathJax containers rendered; no raw TeX, incomplete image,
  uncontained wide element, or page-level horizontal overflow was found.
- The global disclosure controls opened 29/29 details and then closed 29/29.
  The warning/error console was empty.

The temporary viewport override was reset, the temporary tab was closed, and
the task-owned temporary HTTP server was stopped.

## Commit and publication

- Boundary content commit:
  `f226ea31ea5a786bfdb95158462487eb2f8c7b47`; tree
  `4c964912663bdd985984210d09e10bc15fccf374`.
- At 2026-08-22T18:13:08.3417299+02:00, the single bounded
  `git push origin main` attempt returned exit 128 and GitHub's explicit
  account-suspended HTTP 403 response. No credential was read or retried.
  Public-byte readback is impossible because no new remote bytes were
  accepted; the exact content commit remains preserved locally.
- No upstream message was sent.

## Resume

Continue immediately with `random/point/Likelihood.html` (ordinal 13). Do not
repeat ordinal 12, restart source selection, or blend this edition with the
separate Penn State C140 component.
