# Decision log

## O006-D001 — Random-first source spine

Date: 2026-08-21  
Status: admitted

Select only chapters 5–8 of Kyle Siegrist's Random as the O006 source spine.
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
