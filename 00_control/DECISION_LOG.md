# Decision log

## O006-D001 — Random source admitted for this edition

Date: 2026-08-21  
Status: admitted for edition production; curriculum admission remains open

Select only chapters 5–8 of Kyle Siegrist's Random as this edition's bounded
source corpus.
Reason: direct editable semantic HTML + TeX; reproducible static-serving build;
public exercises and answer disclosures; strong proofs through sufficiency and
completeness; classical interval estimation, testing, and introductory Bayes.

## O006-D002 — STAT 415 not admitted as the spine

Date: 2026-08-21  
Status: rejected under current evidence

Penn State STAT 415 is more tightly aligned and cheaper in raw word count, but
the official public surface is generated Quarto output.  No public QMD project,
configuration, or source archive was proved, and graded assignments are in
private Canvas.  Translating the generated site would require reconstructing
source and independently authoring assessment closure, violating the hard gate.
The explicit reversal conditions are recorded in `CURRENT_STATE.md`.

## O006-D003 — bounded original bridge

Date: 2026-08-21  
Status: required

Author a linear-model-inference bridge after the admitted Random core.  Keep a
large-sample-theory bridge conditional on the final role specification.  Do not
pad the course with material already owned by probability or stochastic-
process roles.

## O006-D004 — component rights are not inferred from proximity

Date: 2026-08-21  
Status: controlling

Text and first-party source may be adapted under the Random licence notice.
MathJax and credited CC0 assets retain their own licences.  Unclear third-party
photos and datasets are not copied into the public reader without a separate
grant.  Linking/provenance is not a claim of redistribution rights.

## O006-D005 — source-grounded exercise designation

Date: 2026-08-21  
Status: controlling

Designate a source unit as exercise-like when its native first-paragraph class
is `app` or `stat`, or when a true ancestor `h1`–`h4` source heading contains
the whole word `exercise` or `exercises`, case-insensitively. The exact union is
260 of 760 units: 123 satisfy both criteria, 95 only the section criterion, 42
only the native-unit criterion, and 500 neither. The earlier figures 165, 255,
and 258 are superseded because they respectively omitted exercise sections,
traversed a generic rather than section ancestry, or silently excluded two
units under “Exercises and Special Cases.”

## O006-D006 — additive readable layout

Date: 2026-08-21  
Status: controlling

Keep the official `Screen.css` byte-exact in authority and append one bounded
reader-only stylesheet block. At desktop widths of at least 801 px the article
is centered and capped at 72 rem; at 800 px and below the layout remains fluid
and wide media or data containers scroll rather than forcing page overflow.
The build and QA receipts bind the authority bytes, appendix bytes, and result.

## O006-D007 — honest incremental publication

Date: 2026-08-21  
Status: controlling

Publish substantial verified checkpoints to the one discoverable edition
repository without calling a partial reader complete. The first boundary is
three contiguous pages (3/29), the full locale-neutral backend catalogue, the
exact source/right witnesses needed to replay it, and a deterministic Pages
workflow. Continue production immediately from LLN after public verification.

## O006-D008 — LLN is the next publication boundary

Date: 2026-08-21
Status: controlling

The completed law-of-large-numbers page is a coherent theorem/exercise unit
and advances the contiguous reader to 4/29 pages. Publish this verified
four-page boundary immediately, including its locale-bound backend, rather
than withholding a working reader until the next chapter subsection. Continue
from `random/sample/CLT.html` after public-byte and live-render verification;
do not describe the partial edition as the complete course.

## O006-D009 — edition completion is independent of curriculum admission

Date: 2026-08-21
Status: controlling

Complete the full bounded Indonesian Random edition already undertaken even if
the curriculum-selection root later assigns C140 to STAT 415 or a different
composite.  The edition is independently worthwhile, but its completion and
the work already invested are not evidence that it is the best curricular
spine.  Curriculum admission remains a separate comparative decision governed
by role fit, source/build closure, public assessment closure, overlap, and
fourteen-language cost.  Do not switch sources or abandon this edition because
of that later decision.

## O006-D010 — final component-separated C140 selection

Date: 2026-08-21
Status: controlling; supersedes D001/D002 only as curriculum selection

Complete this repository's full 29-page Random Indonesian edition, but do not
use it as C140's narrative spine. The final C140 architecture is the complete
Penn State STAT 415 landing/index plus Lessons 00–12, exactly Random's
`point/Sufficient.html`, and one original CC BY-SA 4.0 rigor, simulation,
multiple-regression, and mastery companion. Keep the Random edition and Penn
State reconstruction in separate paths/repositories. The exact component,
rights, production, publication, and terminal boundaries are in
`C140_CONFIGURED_ARCHITECTURE_2026-08-21.md`.

## O006-D011 — publish the CLT boundary

Date: 2026-08-21
Status: completed

Treat the first five contiguous pages through CLT as a substantial theorem and
assessment boundary. After exact topology/math/link QA and two deterministic
replays, publish it immediately. Commit
`79d6adf164a28ba4ba6c9894397ff8cd4d6286df` deployed successfully; anonymous
readback matched 28/28 files and live desktop/mobile QA rendered 394/394 CLT
expressions without page-level overflow. Continue at Variance.

## O006-D012 — publish the Variance boundary

Date: 2026-08-22
Status: completed

Treat the first six contiguous pages through sample variance as a substantial
instructional and correction boundary. Variance alone contains 827 source
elements, 47 units, 39 disclosed derivations/answers, and 583 delimited TeX
spans; its independently recomputed formula, answer, data-summary, domain, and
reference repairs are exact and declared. The six-page reader and 1,411 bound
backend entities passed two deterministic replays plus local desktop/mobile
rendering. Commit `ee74fbbd813eec05963eb586fd9be41acb7ebe83` deployed
successfully through workflow `32542434389` and Pages deployment `6031730044`.
Anonymous readback matched all 29 files / 1,986,156 bytes, and the live desktop
and mobile page rendered 586/586 expressions without page-level overflow or
console messages. Continue at `random/sample/OrderStatistics.html`.

## O006-D013 — publish the OrderStatistics boundary

Date: 2026-08-22
Status: completed

Treat the first seven contiguous pages through order statistics as a
substantial instructional and correction boundary. OrderStatistics adds 846
source elements, 51 units, 34 disclosed derivations/answers, 569 TeX spans,
one required image, and 48 exact declared mathematical repairs. The reader and
1,785 bound backend entities passed two deterministic replays plus live
desktop/mobile rendering. Publish the 31-file reader immediately, anonymously
verify every manifest byte and the live page, then continue at
`random/sample/Covariance.html` without describing the partial edition as
complete.

Commit `fd340e9f9a834584216a6480dd104c5bcbe4c66c` deployed successfully through
workflow `32546766027` and Pages deployment `6032396193`. Anonymous readback
matched all 31 files / 2,055,914 bytes. Public desktop/mobile QA rendered all
569 expressions and five images with no raw TeX, console messages, or
page-level overflow. The preceding run `32546700625` failed before deployment
because the clean runner lacked the ignored BoxPlot authority copy; force-adding
that exact manifest-bound file closed the reproducibility defect without
changing reader bytes.
