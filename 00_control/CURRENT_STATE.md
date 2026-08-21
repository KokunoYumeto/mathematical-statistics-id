# Current state — O006 / C140 Mathematical Statistics (id-ID)

Updated: 2026-08-21

## Status

Source admitted; exact authority and component-rights freezes complete; the
first four contiguous Indonesian pages and the full 29-page machine backend
are verified. Every entity on those four pages is now bound to its target
path, locale, byte count, and SHA-256. The repository and repaired three-page
Pages checkpoint are publicly verified; the deterministic four-page boundary
is ready for immediate deployment and public readback. The exact official
MathJax 3.1.2 `boldsymbol.js` module remains pinned. The complete 29-page course
is not yet claimed.

## Admitted source

- Core: Kyle Siegrist, *Random: Probability, Mathematical Statistics, and
  Stochastic Processes*, chapters 5–8 only (random samples, point estimation,
  set/interval estimation, and hypothesis testing).
- Exact edition identity: the unversioned official semantic-HTML site as
  retrieved 2026-08-21 and bound per URL by bytes, SHA-256, ETag, and
  Last-Modified.  There is no proved upstream repository, tag, release, or
  source archive; do not invent one.
- Core closure: 29 HTML files (4 chapter indexes + 25 instructional pages),
  1,003,900 bytes.  The bounded frozen closure is 205 files / 4,867,084 bytes.
- Replay: `python scripts/freeze_random_core.py --check-only`.
- Canonical source manifest SHA-256:
  `d36e0f8bf9fa44a38a7504f9688a08af6787d88ede99298316a3e022b6f799f5`.
- Dynamic component closure: 53 playing-card SVGs / 578,752 bytes,
  manifest SHA-256
  `842e0a5232d4432ca6a84da18f494356b27e5c36279e5788ea176a416ea3f194`;
  four component-license witnesses / 55,064 bytes, manifest SHA-256
  `8a06fecb45a9696c8308e268cbbdacb5d3685ab48a2e10f9d2b4d534395cb777`.
- Exact machine authority record: `SOURCE_AUTHORITY.json`.

## Admission decision

Random-first is admitted; STAT 415-first is rejected under the hard editable-
source and public-assessment gates.  Penn State's current 2026-08-19 course is
a more compact inference syllabus, but the bounded primary-source audit found
only generated Quarto HTML, no public QMD/configuration/source archive, and
private Canvas assignments.  Random exposes editable source-shaped HTML with
TeX, stable structural markup, public exercises, and disclosed details/answers;
its deterministic build is static serving.

This decision minimizes overlap by selecting only Random chapters 5–8.  The
probability foundations and stochastic-process chapters are not imported into
O006.  O006 owns the Indonesian translation of the complete chapter-5 sampling
module; O009 consumes its stable IDs as a prerequisite instead of translating
those bytes a second time.  The exact cross-lane boundary is recorded in
`CROSS_LANE_BOUNDARY.md`.

## Required authored bridge

Random does not close linear-model inference.  A bounded original bridge must
cover the fixed-design simple/multiple linear model, Gauss–Markov, the sampling
distribution of OLS, standard errors, t/F inference, confidence and prediction
intervals, and ANOVA decomposition.  A second large-sample bridge is added only
if the final C140 specification requires the continuous-mapping theorem,
Slutsky, the delta method, and general MLE asymptotic normality; Random already
covers LLN/CLT, consistency, asymptotic unbiasedness, relative efficiency, and
distributional approximations.

## Locale-neutral backend

The deterministic backend indexes the complete 29-page authority as 6,567
entities and 9,035 relations. It contains 29 documents, 366 sections, 760
structural units, 451 disclosures, 2,891 math-text containers, 24 figures, 236
assets, and 1,810 internal links. The source-grounded exercise rule designates
260 units and leaves 500 undesignated; its exact basis is 123 both, 95
exercise-section only, 42 native `app`/`stat` only, and 500 neither. All 664
entities on the four translated pages carry verified id-ID bindings; the other
5,903 entities have explicit untranslated/null locale fields.

- Entity JSONL: 10,180,060 bytes; SHA-256
  `6427f46c6c5f8ea5bd0e6af441759d1d00b3c5104400011a64c42092fd522427`.
- Relation CSV: 1,182,589 bytes; SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- Backend receipt SHA-256:
  `e905bfbe3cb08ad5950423edbd1a9f9b8093d62dc3c551b629df0f819c38cd10`.
- Bound translation-ledger SHA-256:
  `5c0dd978d479f84c5dc9e97878c59e1d593d896c11064eb153f3764ac6f0e8cb`.
- Replay: `python scripts/generate_random_backend.py --check-only`.

## Four-page reader checkpoint

Core ordinals 1–4 are complete: `random/sample/index.html`,
`random/sample/Introduction.html`, `random/sample/Mean.html`, and
`random/sample/LLN.html`. The build is 27 files / 1,880,544 bytes; canonical
manifest SHA-256
`d45913699c2970f75a587537e6a9b83383351f592eae880b5d36a4d6b20ab036`.
Build-receipt SHA-256 is
`cd5aab9787e9da2159d9e7484153922b35a52313c67368fd035a62e8303d0fc1`;
QA-receipt SHA-256 is
`a1ed8a964e8167162587606b92e5b780084095ed59b8071fa27a71f482042866`.

The local QA census is 4 pages, 69 units, 52 disclosures, 734 TeX spans,
ten declared protected-math repairs, nine exact TeX-text localizations, 85
local references, and 15 local fragments. Reader copies are byte-identical to
translation targets; topology,
scripts/styles, IDs, HTTPS policy, local closure, privacy, licensing assets,
the exact responsive CSS append, and the pinned MathJax runtime pass. Two
consecutive build/QA check-only replays returned identical hashes. The
checkpoint details and page hashes are in
`CHECKPOINT_2026-08-21_FOUR_PAGE.md`.

The previous accepted public deployment is commit
`e69aee58a75ff23d57a9ba481ef5773de57b4318`, workflow run `32499866722`,
and Pages deployment `6024693964`. Anonymous HTTPS readback matched all 26
manifest rows by size and SHA-256. Live QA rendered 366 MathJax expressions on
`Mean.html` and 101 on `Introduction.html`, with zero raw delimiters, incomplete
images, console errors, or page-level horizontal overflow at 1280×720 and
390×844. Exact evidence is in `PUBLICATION_RECEIPT_2026-08-21.json`; the
four-page deployment must receive its own anonymous byte and browser evidence.

## Reversal conditions

Reconsider STAT 415-first only if Penn State publishes a complete, license-
compatible QMD/configuration/assets source closure with a reproducible build
and a public exercise/answer or mastery bank.  Reconsider Random-first if the
official licensor withdraws or materially narrows the reusable grant, if exact
HTML/TeX source can no longer be frozen or served reproducibly, or if component
rights cannot be separated without removing essential instruction.  A more
focused candidate may replace Random only if it passes those same gates and
reduces total fourteen-language work after counting the missing assessment
bank and authored bridges—not merely page count.

## Rights boundary

The Random landing page identifies CC BY 2.0; `Credits.html` links CC BY 1.0.
Both permit adaptations with attribution, but the discrepancy is preserved.
Every derivative must credit Kyle Siegrist and Random, link the official work
and applicable licence, identify the translation/modifications, and avoid an
endorsement implication.  MathJax is Apache-2.0.  Dynamically referenced card
and Monty assets are independently CC0.  Third-party biography photographs and
datasets without a component grant are not redistributed merely by relying on
the site-wide notice; they must be cleared, replaced, or linked externally.

## Known upstream defects (do not silently alter authority)

`ADVERSE_LEDGER.jsonl` contains 25 source findings at this boundary: 21
determinate repairs applied only in translated targets and four open items on
later pages. LLN repairs include the missing negative-part factor, the correct
fixed-partition empirical-density limit and measurability qualifications,
sample-size subscripts, answer mapping, and three terminology/notation fixes.
Open findings are the VarianceTest link family, the interval `two2` fragment,
the unavailable ExponentialExperiment companion, and the missing
`Moments.html#poi` fragment. The ledger also records the rejected first Pages
deployment and local runtime-closure repair as one non-upstream build incident.
Authority bytes remain immutable. Do not contact upstream during production.

## Next work

1. Continue immediately with `random/sample/CLT.html` (core ordinal 5).
2. Advance contiguously through the remaining 25 source pages, growing the
   same deterministic reader and stable-ID backend.
3. Author the required linear-model bridge after the admitted core, then close
   the conditional large-sample decision from evidence.
