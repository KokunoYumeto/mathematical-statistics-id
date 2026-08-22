# Eight-page reader checkpoint — 2026-08-22

This checkpoint binds the first eight contiguous id-ID pages of the independent
29-page Random mathematical-statistics edition. It advances the sample chapter
through covariance, correlation, and simple least-squares regression. It does
not claim that the edition or the separately configured C140 course is complete.

## Newly completed source

- Source: `random/sample/Covariance.html`, ordinal 8 of 29.
- Authority: 75,623 bytes; SHA-256
  `1009a5a6a129ee5592aed6c2b914973ae82bb7e7685c477c4c205dbe47fd7072`.
- Target: 80,932 bytes; SHA-256
  `f07eeac25a26897fffbcd3b10435d393849822b3cbf725c3fca581361a8fdb78`.
- Exact topology: 906 source elements; hierarchy SHA-256
  `7ebbc4e8dbc4a99c4baf6358cffce07bedc43b1c01a6b42b8312c9899deaaaea`.
- Census: 58 units, 34 disclosures, 795 delimited TeX spans, three
  byte-identical raw script/style blocks, and 80 native/additive IDs.
- Declared protected changes: 31 math-span repairs, one TeX-text localization,
  and five raw-TeX repairs. All other protected mathematics is byte-preserved.
- Links: 23 exact href-delta entries / 32 occurrences, including two
  occurrence-specific source-fragment repairs.
- Edition notice: 1,172 bytes; SHA-256
  `eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d`.
  It truthfully discloses the bounded mathematical and data corrections.

The correction ledger now runs through `O006-ADV-0103`. Page-8 repairs cover
malformed covariance/regression notation and derivations, two missing `n-1`
factors, the population prediction-error identity, omitted domain conditions,
conversion answers, a five-cell comparison-table error, one exact rational
answer, frozen M&M/SAT calculations, and two broken cross-references. The raw
`<p class="math">Plot residu<p>` artifact is retained and recorded because HTML
parsing closes it deterministically without hiding content. Authority bytes are
unchanged.

## Frozen assets and data checks

Six direct page figures were added byte-for-byte from the frozen authority:

- `ScatterPlot.png`: 11,182 bytes; SHA-256
  `d546fefb4e505f5df089bd15fef57fcd032997c8b1f76b2b47d6fbb7c0fde9ca`.
- `ScatterPlotMeans.png`: 18,766 bytes; SHA-256
  `d798b203ee1826ab3a1068c22c8d15a61feab442f369de8456dea0b7a134b468`.
- `SampleRegression.png`: 12,152 bytes; SHA-256
  `15782d5d41f81e3be7b4539c6a565dc721086720a3e46fc707e124bd539b8671`.
- `SampleRegressionMean.png`: 13,129 bytes; SHA-256
  `6e0a8943af7ddef57c4b87b8a9b3f80205f6be8dbf951854af2cd5a3b37c2a24`.
- `LinearPredictor.png`: 8,403 bytes; SHA-256
  `eb0cb55795d2a48852107a6f6c331ec2f87fabdfb226d8d5b16888761d6b8afe`.
- `SampleLinearPredictor.png`: 6,324 bytes; SHA-256
  `e6548fd85a97649ad87a8efff010ef2c07d7e16b70c3c81f717581097fd4052c`.

The six figures total 69,956 bytes. Frozen-data recomputation used `MM.tsv`
(683 bytes; SHA-256
`015acb5f251f2a747395d33f5d8575f7ef673561c3d0cc261875323c51e2ac45`),
`SAT1.tsv` (738 bytes; SHA-256
`aeb6d648c3fdf780e704d98fb43bf256f3994c7f11bf75871538713ec08a5799`),
and `SAT2.tsv` (1,065 bytes; SHA-256
`412a8dcff14efc0fd900f81025dc680568a473495fe42c98bfeab586a05c8f0a`).
It independently verified the published target values and the exclusion of the
SAT aggregate footer.

## Backend

- 6,567 deterministic entities and 9,035 relations over all 29 source pages.
- 2,356 entities on ordinals 1–8 carry verified id-ID bindings; 4,211 later
  entities explicitly remain untranslated/null.
- Entity JSONL: 10,346,519 bytes; SHA-256
  `b6f70223a2073d44f3e95be67d831a20c6414f5a570ff3f51700fe24395fc45f`.
- Relation CSV: 1,182,589 bytes; SHA-256
  `b235f4d4d724c7fe8653dfd06b075b2225cc2d116f3b87d0fda950d47030159a`.
- Backend receipt: 20,168 bytes; SHA-256
  `48b365a1cfff67299f85c7ec912eabac9d100a1f6c3adc49fe83d091638eaeb7`.
- Translation ledger: 3,027 bytes; SHA-256
  `bcfb072e51c63f119e2a4f1dd87b81f945fa835bd1aaba53116ad3dbd1955003`.

## Reader and deterministic QA

- Reader: 38 files / 2,206,217 bytes.
- Canonical manifest: 3,739 bytes; SHA-256
  `357552b704242cab0cc5111c6756a5bfb04483d9c6dbe3e9d44ce2a10432357f`.
- Build receipt: 92,227 bytes; SHA-256
  `c05e9d275140f5100a5b134be64cec693c66e367c7ef5a201cd3c0ceb103c14c`.
- QA receipt: 75,254 bytes; SHA-256
  `9be37d79fb12255a0db3f2081e8e1c0a197e98c58f2af9ec7d90367c8a005387`.
- Aggregate census: eight translated pages; 4,446 source elements; 263 units;
  180 disclosures; 3,075 TeX spans; 390 IDs; 287 local references; 69
  fragments; 264 href-delta entries / 362 occurrences; 127 protected
  mathematical correction categories.
- The authority freeze, component freeze, localizers, backend, build, and QA
  passed two consecutive complete deterministic check-only replays with the
  exact identities above.

## Live layout and publication state

Live in-app-browser verification passed at 1280×720 and 390×844. Desktop used
a 1,265-px document client with a centered 1,152-px body at x=56.44; mobile
used a 375-px document client with a 351.11-px body at x=12. Both had zero
page-level horizontal overflow. All 802 MathJax containers rendered (795
delimited spans plus seven raw environments), with zero raw-TeX tokens and zero
console warnings/errors. All 10 images loaded with nonempty alternative text.
All 34 disclosures opened and collapsed correctly. The 1,030.57-px desktop
table reflowed to 334.33 px on mobile without clipping. Two mobile display
formulas exceed their own boxes by eight pixels and are correctly contained by
local horizontal scrollers; neither widens the viewport. Visual inspection of
the page head and widest table passed. Temporary browser state was restored.

Commit `830ddbc81b2066c0ac17438e03672de0dfca178c` (tree
`bd9af01b58fa3378337cdf09d777713999d03c59`) was pushed to `main`.
Workflow run `32550543678`, job `96976449448`, Pages deployment `6032990532`,
and deployment status `17151722242` completed successfully. The clean runner
replayed the deterministic backend, build, and QA gates before publishing.

Anonymous HTTPS readback checked every manifest row. Thirty-seven files matched
on the first sweep; `random/sample/BoxPlot.png` returned one transient HTTP 503
error document, then matched its exact 790 bytes and SHA-256 on the immediate
no-cache retry. The complete verified public inventory is therefore 38 files /
2,206,217 bytes with zero final size or hash mismatches. Anonymous raw-GitHub
readback at the accepted commit matched all 42 changed source, authority,
translation, backend, build, and control files / 11,814,221 bytes.

Public live desktop QA reproduced the local metrics, including 802 MathJax
containers, 10 loaded described images, 34 functional disclosures, 19 valid
current-page fragments, zero raw TeX, zero console messages, centered layout,
and no page overflow. Public mobile QA likewise had a 375/375-px document and
351/351-px body, no page overflow, a fully contained 13×13 table at 333/333 px
client/scroll width with zero clipped cells, and exactly two intended local
formula scrollers at 334/342 px. No console warnings or errors were emitted.
Temporary browser tabs and viewport overrides were closed/reset. No upstream
contact occurred.

Next source after closing publication: `random/sample/Normal.html`, ordinal 9
of 29.
