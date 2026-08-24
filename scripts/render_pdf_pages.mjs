#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

function parseArgs(values) {
  const parsed = {};
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (!value.startsWith("--")) throw new Error(`unexpected argument: ${value}`);
    const key = value.slice(2);
    if (key === "validate-only") {
      parsed[key] = true;
      continue;
    }
    const next = values[index + 1];
    if (!next || next.startsWith("--")) throw new Error(`missing value for --${key}`);
    parsed[key] = next;
    index += 1;
  }
  return parsed;
}

function sha256Bytes(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function loadInventory(filename) {
  const raw = fs.readFileSync(filename);
  const inventorySha256 = sha256Bytes(raw);
  let inventory;
  try {
    inventory = JSON.parse(raw.toString("utf8"));
  } catch (error) {
    throw new Error(`invalid UTF-8 JSON inventory: ${error.message}`);
  }
  if (inventory.schema !== "o006.random.pdf-render-inventory.v1") {
    throw new Error(`unexpected inventory schema: ${inventory.schema}`);
  }
  if (inventory.status !== "complete-29-of-29") {
    throw new Error(`unexpected inventory status: ${inventory.status}`);
  }
  if (inventory.source_documents !== 29 || !Array.isArray(inventory.documents) || inventory.documents.length !== 29) {
    throw new Error("inventory must contain exactly 29 source documents");
  }
  const paths = new Set();
  for (const [index, document] of inventory.documents.entries()) {
    const expectedOrdinal = index + 1;
    if (document.ordinal !== expectedOrdinal) {
      throw new Error(`non-contiguous inventory ordinal at row ${expectedOrdinal}`);
    }
    if (!Number.isInteger(document.ordinal)) throw new Error(`invalid ordinal at row ${expectedOrdinal}`);
    if (!['chapter', 'section'].includes(document.kind)) throw new Error(`invalid kind at row ${expectedOrdinal}`);
    if (typeof document.label !== "string" || !document.label.trim()) throw new Error(`missing label at row ${expectedOrdinal}`);
    if (!Number.isInteger(document.reader_bytes) || document.reader_bytes < 1) {
      throw new Error(`invalid reader byte count at row ${expectedOrdinal}`);
    }
    if (typeof document.reader_sha256 !== "string" || !/^[0-9a-f]{64}$/.test(document.reader_sha256)) {
      throw new Error(`invalid reader SHA-256 at row ${expectedOrdinal}`);
    }
    const relativePath = document.relative_path;
    if (
      typeof relativePath !== "string"
      || !relativePath.startsWith("random/")
      || !relativePath.endsWith(".html")
      || relativePath.includes("\\")
      || path.posix.normalize(relativePath) !== relativePath
      || relativePath.split("/").includes("..")
    ) {
      throw new Error(`unsafe or non-canonical relative path at row ${expectedOrdinal}: ${relativePath}`);
    }
    if (paths.has(relativePath)) throw new Error(`duplicate inventory path: ${relativePath}`);
    paths.add(relativePath);
  }
  for (const ordinal of [1, 10, 17, 23]) {
    if (inventory.documents[ordinal - 1].kind !== "chapter") {
      throw new Error(`ordinal ${ordinal} must remain a chapter heading`);
    }
  }
  return { inventory, inventorySha256 };
}

function pdfPageCount(python, pdfPath) {
  const script = "from pypdf import PdfReader; import sys; print(len(PdfReader(sys.argv[1]).pages))";
  const result = spawnSync(python, ["-c", script, pdfPath], {
    encoding: "utf8",
    windowsHide: true,
    maxBuffer: 1024 * 1024,
  });
  if (result.status !== 0) {
    throw new Error(`PDF page counter failed for ${pdfPath}: ${(result.stderr || "").slice(0, 1000)}`);
  }
  const count = Number.parseInt(result.stdout.trim(), 10);
  if (!Number.isInteger(count) || count < 1) throw new Error(`invalid PDF page count for ${pdfPath}`);
  return count;
}

function assertNoMathJaxRenderErrors(relativePath, audit) {
  if (
    !Number.isInteger(audit.mathjax_merrors)
    || audit.mathjax_merrors < 0
    || !Array.isArray(audit.mathjax_merror_diagnostics)
    || audit.mathjax_merror_diagnostics.length !== audit.mathjax_merrors
    || !Number.isInteger(audit.mathjax_silent_red_fallbacks)
    || audit.mathjax_silent_red_fallbacks < 0
    || !Array.isArray(audit.mathjax_silent_red_diagnostics)
    || audit.mathjax_silent_red_diagnostics.length !== audit.mathjax_silent_red_fallbacks
    || !Number.isInteger(audit.mathjax_render_errors)
    || audit.mathjax_render_errors !== audit.mathjax_merrors + audit.mathjax_silent_red_fallbacks
    || !Array.isArray(audit.mathjax_error_diagnostics)
    || audit.mathjax_error_diagnostics.length !== audit.mathjax_render_errors
  ) {
    throw new Error(`${relativePath}: invalid MathJax error audit result`);
  }
  if (audit.mathjax_render_errors > 0) {
    throw new Error(
      `${relativePath}: MathJax produced ${audit.mathjax_render_errors} render error(s) `
      + `(mjx-merror=${audit.mathjax_merrors}, `
      + `silent-red-fallback=${audit.mathjax_silent_red_fallbacks}) `
      + `${JSON.stringify(audit.mathjax_error_diagnostics)}`,
    );
  }
}

const args = parseArgs(process.argv.slice(2));
if (!args.inventory) throw new Error("missing --inventory");
const { inventory, inventorySha256 } = loadInventory(args.inventory);

if (args["validate-only"]) {
  process.stdout.write(JSON.stringify({
    schema: "o006.random.pdf-render-inventory-validation.v1",
    status: inventory.status,
    source_documents: inventory.source_documents,
    inventory_sha256: inventorySha256,
    documents: inventory.documents,
  }));
  process.exit(0);
}

for (const key of ["base-url", "output-dir", "playwright-dir", "chrome", "python"]) {
  if (!args[key]) throw new Error(`missing --${key}`);
}

const playwrightUrl = pathToFileURL(path.join(args["playwright-dir"], "index.mjs")).href;
const { chromium } = await import(playwrightUrl);

const printCss = String.raw`
  @page { size: A4; margin: 14mm 13mm 16mm 13mm; }
  html, body { background: #fff !important; }
  body:not(.ancillary) {
    box-sizing: border-box !important;
    width: 184mm !important;
    max-width: 184mm !important;
    margin: 0 !important;
    padding: 0 !important;
    color: #111 !important;
    font-size: 10.3pt !important;
    line-height: 1.40 !important;
  }
  body:not(.ancillary).o006-compact-document-reflow {
    line-height: 1.34 !important;
  }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  h2, h3, h4 { break-after: avoid-page; color: #15304a !important; }
  h2 { margin-top: 0; }
  p, li { orphans: 3; widows: 3; }
  details { display: block !important; }
  details > * { display: block !important; }
  div.unit.o006-terminal-unit { margin-top: 4px !important; margin-bottom: 0 !important; }
  div.unit.o006-terminal-unit > p,
  div.unit.o006-terminal-unit > ol { margin-block: 0.35em !important; }
  div.unit.o006-terminal-exercise-grid {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    column-gap: 1.5em;
    align-items: start;
    padding: 0.3em 0.45em;
  }
  div.unit.o006-terminal-exercise-grid > p,
  div.unit.o006-terminal-exercise-grid > ol { grid-column: 1; }
  div.unit.o006-terminal-exercise-grid > details {
    grid-column: 2;
    grid-row: 1 / span 2;
    margin: 0 !important;
  }
  details.o006-terminal-answer { margin-top: 0 !important; margin-bottom: 0 !important; }
  details.o006-terminal-answer > summary { margin-block: 0 !important; }
  details.o006-terminal-answer > ol { margin-block: 0.2em !important; }
  details.o006-terminal-answer > ol > li { break-inside: avoid-page; }
  details.o006-terminal-answer.o006-two-column-answer:not(.o006-grid-answer) > ol {
    columns: 2;
    column-gap: 2em;
  }
  header > .map { display: none !important; }
  footer { display: none !important; }
  summary { break-after: avoid-page; color: #284f71 !important; }
  figure, tr, pre, blockquote { break-inside: avoid-page; }
  div.scroll, div.data { max-width: 100% !important; overflow: visible !important; }
  mjx-container[display="true"] { break-inside: avoid-page; max-width: 100%; }
  img, svg, canvas { max-width: 100% !important; height: auto !important; }
  button { display: none !important; }
  a { color: #173f68 !important; text-decoration: none !important; }
  section.edition-notice[data-o006-edition-notice="v1"] { display: none !important; }
`;

const variancePrintCss = String.raw`
  #cmp1 details table {
    break-inside: avoid-page !important;
    page-break-inside: avoid !important;
  }
  #cmp3 > table,
  #cmp3 details table {
    width: 100% !important;
    table-layout: fixed !important;
    border-collapse: collapse !important;
    font-size: 8.7pt !important;
  }
  #cmp3 > table th,
  #cmp3 > table td,
  #cmp3 details table th,
  #cmp3 details table td {
    box-sizing: border-box !important;
    padding: 0.14em 0.24em !important;
    text-align: center !important;
    vertical-align: middle !important;
  }
  #cmp3 > table th,
  #cmp3 details table th {
    border-bottom: 0.45pt solid #8795a1 !important;
    line-height: 1.15 !important;
    white-space: normal !important;
  }
  #cmp3 > table tbody td,
  #cmp3 details table tbody td {
    border-bottom: 0.2pt solid #d9dfe4 !important;
  }
`;

fs.mkdirSync(args["output-dir"], { recursive: true });
const browser = await chromium.launch({
  executablePath: args.chrome,
  headless: true,
  args: ["--disable-gpu", "--font-render-hinting=none"],
});
const browserVersion = await browser.version();

const results = [];
let nextContentPage = 1;
const compactDocumentReflows = new Set([
  "random/point/Bayes.html",
  "random/interval/BivariateNormal.html",
  "random/hypothesis/Bernoulli.html",
]);
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const consoleProblems = [];
page.on("console", (message) => {
  if (["warning", "error"].includes(message.type())) {
    consoleProblems.push(`${message.type()}: ${message.text()}`);
  }
});
page.on("pageerror", (error) => consoleProblems.push(`pageerror: ${error.message}`));
try {
  for (const document of inventory.documents) {
    const {
      ordinal,
      relative_path: relativePath,
      label,
      kind,
      reader_bytes: expectedReaderBytes,
      reader_sha256: expectedReaderSha256,
    } = document;
    consoleProblems.length = 0;
    const url = `${args["base-url"].replace(/\/$/, "")}/${relativePath}`;
    const response = await page.goto(url, { waitUntil: "load", timeout: 60000 });
    if (!response || !response.ok()) throw new Error(`${relativePath}: HTTP load failed`);
    const readerBytes = await response.body();
    const readerSha256 = sha256Bytes(readerBytes);
    if (readerBytes.length !== expectedReaderBytes || readerSha256 !== expectedReaderSha256) {
      throw new Error(`${relativePath}: served reader bytes differ from the canonical inventory`);
    }
    await page.evaluate(async () => {
      if (globalThis.MathJax?.startup?.promise) await globalThis.MathJax.startup.promise;
      if (document.fonts?.ready) await document.fonts.ready;
    });
    await page.locator("details").evaluateAll((nodes) => {
      for (const node of nodes) node.open = true;
    });
    await page.locator("a[href]").evaluateAll((nodes) => {
      for (const node of nodes) {
        const destination = new URL(node.href, location.href);
        if (destination.origin !== location.origin) continue;
        if (destination.pathname === location.pathname && destination.hash) {
          node.setAttribute("href", destination.hash);
        } else {
          node.setAttribute("href", "https://doi.org/10.5281/zenodo.22059763");
        }
      }
    });
    const noticeEvidence = await page.evaluate(() => {
      const notices = [...document.querySelectorAll(
        'section.edition-notice[data-o006-edition-notice="v1"]',
      )];
      const notice = notices[0] || null;
      const text = notice ? String(notice.textContent || "").replace(/\s+/g, " ").trim() : "";
      const markup = notice ? notice.outerHTML.normalize("NFC") : "";
      const footers = [...document.querySelectorAll("footer")];
      const footerMaps = footers.reduce(
        (count, footer) => count + [...footer.children].filter(
          (child) => child.matches("ol.map, ul.map"),
        ).length,
        0,
      );
      const footerExtraElements = footers.flatMap((footer) =>
        [...footer.children]
          .filter((child) => !child.matches(
            'ol.map, ul.map, section.edition-notice[data-o006-edition-notice="v1"]',
          ))
          .map((child) => `${child.tagName}.${String(child.className || "")}`),
      );
      return {
        count: notices.length,
        text_characters: text.length,
        markup,
        footer_count: footers.length,
        footer_map_count: footerMaps,
        footer_extra_elements: footerExtraElements,
      };
    });
    if (noticeEvidence.count !== 1 || noticeEvidence.text_characters < 100 || !noticeEvidence.markup) {
      throw new Error(`${relativePath}: expected exactly one nonempty edition notice before PDF suppression`);
    }
    if (
      noticeEvidence.footer_count !== 1
      || noticeEvidence.footer_map_count !== 2
      || noticeEvidence.footer_extra_elements.length !== 0
    ) {
      throw new Error(
        `${relativePath}: footer contains content outside the two maps and edition notice `
        + `${JSON.stringify(noticeEvidence)}`,
      );
    }
    const noticeBytes = Buffer.from(noticeEvidence.markup, "utf8");
    const documentReflowProfile = compactDocumentReflows.has(relativePath)
      ? "compact-line-height-1.34"
      : "standard-line-height-1.40";
    const documentPrintCss = relativePath === "random/sample/Variance.html"
      ? `${printCss}\n${variancePrintCss}`
      : printCss;
    await page.addStyleTag({ content: documentPrintCss });
    const terminalReflow = await page.evaluate(async (reflowProfile) => {
      const normalizeText = (node) => String(node?.textContent || "").replace(/\s+/g, " ").trim();
      document.body.classList.toggle(
        "o006-compact-document-reflow",
        reflowProfile === "compact-line-height-1.34",
      );
      const units = [...document.querySelectorAll("div.unit")];
      const terminalUnit = units.at(-1) || null;
      if (!terminalUnit) {
        return {
          schema: "o006.random.pdf-terminal-reflow.v2",
          document_reflow_profile: reflowProfile,
          terminal_unit_marked: false,
          terminal_answer_marked: false,
          answer_columns: 1,
        };
      }
      terminalUnit.classList.add("o006-terminal-unit");
      const details = terminalUnit.querySelector(":scope > details:last-of-type");
      if (!details) {
        return {
          schema: "o006.random.pdf-terminal-reflow.v2",
          document_reflow_profile: reflowProfile,
          terminal_unit_marked: true,
          terminal_answer_marked: false,
          answer_columns: 1,
        };
      }
      details.classList.add("o006-terminal-answer");
      const directQuestions = terminalUnit.querySelector(":scope > ol.sub");
      const directAnswers = details.querySelector(":scope > ol.sub");
      const questions = directQuestions ? [...directQuestions.querySelectorAll(":scope > li")] : [];
      const answers = directAnswers ? [...directAnswers.querySelectorAll(":scope > li")] : [];
      const questionText = questions.map(normalizeText);
      const answerText = answers.map(normalizeText);
      const complexSelector = 'table, pre, figure, canvas, mjx-container[display="true"]';
      const hasComplexGridContent = Boolean(
        directQuestions?.querySelector(complexSelector) || directAnswers?.querySelector(complexSelector),
      );
      const gridEligibility = {
        exercise_id: /^exe/i.test(terminalUnit.id || ""),
        direct_lists: Boolean(directQuestions && directAnswers),
        positive_item_counts: questions.length > 0 && answers.length > 0,
        bounded_item_counts: questions.length <= 8 && answers.length <= 8,
        bounded_prose: [...questionText, ...answerText].every((text) => text.length <= 240),
        complex_block_content_absent: !hasComplexGridContent,
      };
      let useExerciseGrid = Object.values(gridEligibility).every(Boolean);
      const gridAlignment = questions.length === answers.length ? "paired-items" : "parallel-lists";
      let gridGeometry = {
        evaluated: false,
        pass: null,
        grid_width: null,
        question_width: null,
        answer_width: null,
        grid_scroll_overflow_px: null,
        question_scroll_overflow_px: null,
        answer_scroll_overflow_px: null,
        out_of_bounds_descendants: null,
      };
      if (useExerciseGrid) {
        terminalUnit.classList.add("o006-terminal-exercise-grid");
        details.classList.add("o006-grid-answer");
        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        const gridBox = terminalUnit.getBoundingClientRect();
        const questionBox = directQuestions.getBoundingClientRect();
        const answerBox = details.getBoundingClientRect();
        const visibleDescendants = [...terminalUnit.querySelectorAll("*")]
          .filter((element) => !element.closest("mjx-assistive-mml"))
          .filter((element) => {
            const style = getComputedStyle(element);
            return style.display !== "none" && style.visibility !== "hidden";
          });
        const outOfBounds = visibleDescendants.filter((element) => {
          const box = element.getBoundingClientRect();
          return box.left < gridBox.left - 1 || box.right > gridBox.right + 1;
        });
        gridGeometry = {
          evaluated: true,
          pass: false,
          grid_width: Math.round(gridBox.width),
          question_width: Math.round(questionBox.width),
          answer_width: Math.round(answerBox.width),
          grid_scroll_overflow_px: Math.max(0, terminalUnit.scrollWidth - terminalUnit.clientWidth),
          question_scroll_overflow_px: Math.max(0, directQuestions.scrollWidth - directQuestions.clientWidth),
          answer_scroll_overflow_px: Math.max(0, details.scrollWidth - details.clientWidth),
          out_of_bounds_descendants: outOfBounds.length,
        };
        gridGeometry.pass = (
          gridGeometry.grid_width >= 650
          && gridGeometry.question_width >= 300
          && gridGeometry.answer_width >= 300
          && gridGeometry.grid_scroll_overflow_px <= 1
          && gridGeometry.question_scroll_overflow_px <= 1
          && gridGeometry.answer_scroll_overflow_px <= 1
          && gridGeometry.out_of_bounds_descendants === 0
        );
        if (!gridGeometry.pass) {
          terminalUnit.classList.remove("o006-terminal-exercise-grid");
          details.classList.remove("o006-grid-answer");
          useExerciseGrid = false;
        }
      }
      const hasComplexAnswerContent = Boolean(details.querySelector(complexSelector));
      const useTwoColumns = (
        !useExerciseGrid
        && !hasComplexAnswerContent
        && answers.length >= 6
        && answerText.every((text) => text.length <= 80)
      );
      if (useTwoColumns) details.classList.add("o006-two-column-answer");
      return {
        schema: "o006.random.pdf-terminal-reflow.v2",
        document_reflow_profile: reflowProfile,
        terminal_unit_marked: true,
        terminal_answer_marked: true,
        terminal_question_items: questions.length,
        terminal_answer_items: answers.length,
        terminal_question_max_characters: Math.max(0, ...questionText.map((text) => text.length)),
        terminal_answer_max_characters: Math.max(0, ...answerText.map((text) => text.length)),
        terminal_exercise_grid: Boolean(useExerciseGrid),
        grid_alignment: useExerciseGrid ? gridAlignment : null,
        grid_eligibility: gridEligibility,
        grid_geometry: gridGeometry,
        answer_columns: useTwoColumns ? 2 : 1,
      };
    }, documentReflowProfile);
    const audit = await page.evaluate(() => {
      const text = document.body.innerText;
      const images = [...document.images];
      const normalizeDiagnostic = (value) => String(value || "").replace(/\s+/g, " ").trim();
      const explicitMathErrors = [...document.querySelectorAll("mjx-merror")];
      const explicitErrorContainers = new Set(
        explicitMathErrors.map((element) => element.closest("mjx-container")).filter(Boolean),
      );
      const mathErrorDiagnostics = explicitMathErrors
        .map((element, index) => {
          const dataError = normalizeDiagnostic(element.getAttribute("data-mjx-error"));
          const title = normalizeDiagnostic(element.getAttribute("title"));
          const ariaLabel = normalizeDiagnostic(element.getAttribute("aria-label"));
          const renderedText = normalizeDiagnostic(element.textContent);
          return {
            index: index + 1,
            kind: "mjx-merror",
            diagnostic: (dataError || title || ariaLabel || renderedText || "(diagnostic text absent)").slice(0, 4096),
            rendered_text: renderedText.slice(0, 4096),
          };
        });
      const isRed = (value) => normalizeDiagnostic(value).toLowerCase() === "red";
      const silentRedByContainer = new Map();
      const redMarkerCandidates = document.querySelectorAll([
        "mjx-container mtext[mathcolor]",
        "mjx-container svg[fill]",
        "mjx-container svg [fill]",
        "mjx-container svg[stroke]",
        "mjx-container svg [stroke]",
      ].join(", "));
      for (const element of redMarkerCandidates) {
        const container = element.closest("mjx-container");
        if (!container || explicitErrorContainers.has(container)) continue;
        const tag = element.tagName.toLowerCase();
        const markers = [];
        if (tag === "mtext" && isRed(element.getAttribute("mathcolor"))) {
          markers.push('mtext[mathcolor="red"]');
        }
        if (isRed(element.getAttribute("fill"))) markers.push(`${tag}[fill="red"]`);
        if (isRed(element.getAttribute("stroke"))) markers.push(`${tag}[stroke="red"]`);
        if (!markers.length) continue;
        if (!silentRedByContainer.has(container)) {
          silentRedByContainer.set(container, { markers: new Set(), redText: new Set() });
        }
        const evidence = silentRedByContainer.get(container);
        for (const marker of markers) evidence.markers.add(marker);
        if (tag === "mtext") {
          const redText = normalizeDiagnostic(element.textContent);
          if (redText) evidence.redText.add(redText);
        }
      }
      const silentRedDiagnostics = [...silentRedByContainer.entries()]
        .map(([container, evidence], index) => {
          const redText = [...evidence.redText].join(" | ");
          const containerText = normalizeDiagnostic(container.textContent);
          return {
            index: mathErrorDiagnostics.length + index + 1,
            kind: "silent-red-fallback",
            diagnostic: (redText || containerText || "(silent red fallback without text)").slice(0, 4096),
            rendered_text: containerText.slice(0, 4096),
            markers: [...evidence.markers].sort(),
          };
        });
      const mathJaxErrorDiagnostics = [...mathErrorDiagnostics, ...silentRedDiagnostics];
      const viewportWidth = document.documentElement.clientWidth;
      const printContentBox = document.body.getBoundingClientRect();
      const editionNotices = [...document.querySelectorAll(
        'section.edition-notice[data-o006-edition-notice="v1"]',
      )];
      const editionNoticeDisplay = editionNotices.length === 1
        ? getComputedStyle(editionNotices[0]).display
        : null;
      const footers = [...document.querySelectorAll("footer")];
      const hiddenFooters = footers.filter((footer) => getComputedStyle(footer).display === "none");
      const visiblePrintElements = [...document.querySelectorAll("body *")]
        .filter((element) => !element.closest("mjx-assistive-mml"))
        .filter((element) => {
          const style = getComputedStyle(element);
          return style.display !== "none" && style.visibility !== "hidden";
        })
        .map((element) => {
          const box = element.getBoundingClientRect();
          return {
            tag: element.tagName,
            id: element.id || "",
            className: typeof element.className === "string" ? element.className : "",
            left: Math.round(box.left),
            right: Math.round(box.right),
            width: Math.round(box.width),
            overflowX: getComputedStyle(element).overflowX,
          };
        });
      const visiblePrintScrollWidth = Math.round(Math.max(
        printContentBox.width,
        ...visiblePrintElements.map((item) => item.right - printContentBox.left),
      ));
      const wideElements = visiblePrintElements
        .filter(
          (item) => item.left < printContentBox.left - 1 || item.right > printContentBox.right + 1,
        )
        .sort((a, b) => b.right - a.right)
        .slice(0, 12);
      return {
        title: document.title,
        math_containers: document.querySelectorAll("mjx-container").length,
        mathjax_merrors: mathErrorDiagnostics.length,
        mathjax_merror_diagnostics: mathErrorDiagnostics,
        mathjax_silent_red_fallbacks: silentRedDiagnostics.length,
        mathjax_silent_red_diagnostics: silentRedDiagnostics,
        mathjax_render_errors: mathJaxErrorDiagnostics.length,
        mathjax_error_diagnostics: mathJaxErrorDiagnostics,
        details: document.querySelectorAll("details").length,
        open_details: document.querySelectorAll("details[open]").length,
        incomplete_images: images.filter((image) => !image.complete || image.naturalWidth === 0).length,
        raw_tex: /\\\(|\\\[|\\begin\{(?:align|align\*)\}/.test(text),
        page_overflow: wideElements.length > 0,
        viewport_width: viewportWidth,
        document_scroll_width: document.documentElement.scrollWidth,
        dom_body_scroll_width: document.body.scrollWidth,
        print_content_scroll_width: visiblePrintScrollWidth,
        print_content_left: Math.round(printContentBox.left),
        print_content_right: Math.round(printContentBox.right),
        print_content_width: Math.round(printContentBox.width),
        maximum_print_overflow_px: Math.max(
          0,
          ...wideElements.map((item) => Math.max(
            printContentBox.left - item.left,
            item.right - printContentBox.right,
          )),
        ),
        wide_elements: wideElements,
        edition_notice_count: editionNotices.length,
        edition_notice_computed_display: editionNoticeDisplay,
        edition_notice_hidden: editionNotices.length === 1 && editionNoticeDisplay === "none",
        footer_count: footers.length,
        hidden_footer_count: hiddenFooters.length,
      };
    });
    assertNoMathJaxRenderErrors(relativePath, audit);
    if (
      audit.edition_notice_count !== 1
      || audit.edition_notice_computed_display !== "none"
      || audit.edition_notice_hidden !== true
      || audit.footer_count !== 1
      || audit.hidden_footer_count !== 1
    ) {
      throw new Error(`${relativePath}: edition notice was not preserved and suppressed exactly once`);
    }
    if (audit.details !== audit.open_details) throw new Error(`${relativePath}: disclosures did not fully expand`);
    if (audit.incomplete_images || audit.raw_tex || audit.page_overflow || consoleProblems.length) {
      throw new Error(`${relativePath}: render audit failed ${JSON.stringify({ audit, consoleProblems })}`);
    }
    const filename = `${String(ordinal).padStart(2, "0")}-${path.basename(relativePath, ".html")}.pdf`;
    const pdfPath = path.join(args["output-dir"], filename);
    await page.pdf({
      path: pdfPath,
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
      tagged: true,
      outline: true,
    });
    const pdfBytes = fs.readFileSync(pdfPath);
    const pdfPages = pdfPageCount(args.python, pdfPath);
    const contentPageStart = nextContentPage;
    const contentPageEnd = contentPageStart + pdfPages - 1;
    results.push({
      ordinal,
      relative_path: relativePath,
      label,
      kind,
      reader_bytes: readerBytes.length,
      reader_sha256: readerSha256,
      filename,
      bytes: pdfBytes.length,
      sha256: sha256Bytes(pdfBytes),
      pdf_pages: pdfPages,
      content_page_start: contentPageStart,
      content_page_end: contentPageEnd,
      edition_notice_bytes: noticeBytes.length,
      edition_notice_sha256: sha256Bytes(noticeBytes),
      edition_notice_text_characters: noticeEvidence.text_characters,
      footer_map_count: noticeEvidence.footer_map_count,
      footer_extra_element_count: noticeEvidence.footer_extra_elements.length,
      terminal_reflow: terminalReflow,
      ...audit,
    });
    nextContentPage = contentPageEnd + 1;
  }
} finally {
  await page.close();
  await browser.close();
}

process.stdout.write(JSON.stringify({
  schema: "o006.random.pdf-render-result.v3",
  status: inventory.status,
  source_documents: inventory.source_documents,
  inventory_sha256: inventorySha256,
  content_physical_pages: nextContentPage - 1,
  browser_version: browserVersion,
  edition_notice_policy: {
    schema: "o006.random.pdf-notice-policy.v1",
    selector: 'section.edition-notice[data-o006-edition-notice="v1"]',
    consolidated_pdf_page: 2,
    source_notices_present: results.filter((row) => row.edition_notice_count === 1).length,
    source_notices_hidden_in_pdf: results.filter((row) => row.edition_notice_hidden === true).length,
    source_footers_present: results.filter((row) => row.footer_count === 1).length,
    source_footer_maps: results.reduce((count, row) => count + row.footer_map_count, 0),
    source_footer_extra_elements: results.reduce(
      (count, row) => count + row.footer_extra_element_count,
      0,
    ),
    source_footers_hidden_in_pdf: results.filter((row) => row.hidden_footer_count === 1).length,
    html_notices_preserved: true,
    per_document: results.map((row) => ({
      ordinal: row.ordinal,
      relative_path: row.relative_path,
      bytes: row.edition_notice_bytes,
      sha256: row.edition_notice_sha256,
      text_characters: row.edition_notice_text_characters,
      footer_maps: row.footer_map_count,
      footer_extra_elements: row.footer_extra_element_count,
    })),
  },
  documents: results,
}));
