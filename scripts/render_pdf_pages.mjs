#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const args = Object.fromEntries(
  process.argv.slice(2).reduce((rows, value, index, all) => {
    if (value.startsWith("--")) rows.push([value.slice(2), all[index + 1]]);
    return rows;
  }, []),
);

for (const key of ["base-url", "output-dir", "playwright-dir", "chrome"]) {
  if (!args[key]) throw new Error(`missing --${key}`);
}

const playwrightUrl = pathToFileURL(path.join(args["playwright-dir"], "index.mjs")).href;
const { chromium } = await import(playwrightUrl);

const documents = [
  [1, "random/sample/index.html", "5. Sampel Acak"],
  [2, "random/sample/Introduction.html", "Pengantar Sampel Acak"],
  [3, "random/sample/Mean.html", "Rata-rata Sampel"],
  [4, "random/sample/LLN.html", "Hukum Bilangan Besar"],
  [5, "random/sample/CLT.html", "Teorema Limit Pusat"],
  [6, "random/sample/Variance.html", "Varians Sampel"],
  [7, "random/sample/OrderStatistics.html", "Statistik Urutan"],
  [8, "random/sample/Covariance.html", "Kovarians dan Korelasi Sampel"],
  [9, "random/sample/Normal.html", "Sampel Normal"],
  [10, "random/point/index.html", "6. Pendugaan Titik"],
  [11, "random/point/Estimators.html", "Penduga"],
  [12, "random/point/Moments.html", "Metode Momen"],
  [13, "random/point/Likelihood.html", "Kemungkinan Maksimum"],
  [14, "random/point/Bayes.html", "Pendugaan Bayes"],
  [15, "random/point/Unbiased.html", "Penduga Tak Bias Terbaik"],
];

const printCss = String.raw`
  @page { size: A4; margin: 15mm 14mm 18mm 14mm; }
  html, body { background: #fff !important; }
  body:not(.ancillary) {
    box-sizing: border-box !important;
    width: auto !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
    color: #111 !important;
    font-size: 10.4pt !important;
    line-height: 1.42 !important;
  }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  h2, h3, h4 { break-after: avoid-page; color: #15304a !important; }
  h2 { margin-top: 0; }
  p, li { orphans: 3; widows: 3; }
  details { display: block !important; }
  details > * { display: block !important; }
  summary { break-after: avoid-page; color: #284f71 !important; }
  figure, tr, pre, blockquote { break-inside: avoid-page; }
  div.scroll, div.data { max-width: 100% !important; overflow: visible !important; }
  mjx-container[display="true"] { break-inside: avoid-page; max-width: 100%; }
  img, svg, canvas { max-width: 100% !important; height: auto !important; }
  button { display: none !important; }
  a { color: #173f68 !important; text-decoration: none !important; }
  .edition-notice { break-inside: avoid-page; }
`;

fs.mkdirSync(args["output-dir"], { recursive: true });
const browser = await chromium.launch({
  executablePath: args.chrome,
  headless: true,
  args: ["--disable-gpu", "--font-render-hinting=none"],
});
const browserVersion = await browser.version();

const results = [];
try {
  for (const [ordinal, relativePath, label] of documents) {
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
    const consoleProblems = [];
    page.on("console", (message) => {
      if (["warning", "error"].includes(message.type())) {
        consoleProblems.push(`${message.type()}: ${message.text()}`);
      }
    });
    page.on("pageerror", (error) => consoleProblems.push(`pageerror: ${error.message}`));
    const url = `${args["base-url"].replace(/\/$/, "")}/${relativePath}`;
    const response = await page.goto(url, { waitUntil: "load", timeout: 60000 });
    if (!response || !response.ok()) throw new Error(`${relativePath}: HTTP load failed`);
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
    await page.addStyleTag({ content: printCss });
    const audit = await page.evaluate(() => {
      const text = document.body.innerText;
      const images = [...document.images];
      const viewportWidth = document.documentElement.clientWidth;
      const wideElements = [...document.querySelectorAll("body *")]
        .filter((element) => !element.closest("mjx-assistive-mml"))
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
        })
        .filter((item) => item.left < -1 || item.right > viewportWidth + 1)
        .sort((a, b) => b.right - a.right)
        .slice(0, 12);
      return {
        title: document.title,
        mathContainers: document.querySelectorAll("mjx-container").length,
        details: document.querySelectorAll("details").length,
        openDetails: document.querySelectorAll("details[open]").length,
        incompleteImages: images.filter((image) => !image.complete || image.naturalWidth === 0).length,
        rawTex: /\\\(|\\\[|\\begin\{(?:align|align\*)\}/.test(text),
        pageOverflow: wideElements.length > 0,
        viewportWidth,
        documentScrollWidth: document.documentElement.scrollWidth,
        wideElements,
      };
    });
    if (audit.details !== audit.openDetails) throw new Error(`${relativePath}: disclosures did not fully expand`);
    if (audit.incompleteImages || audit.rawTex || audit.pageOverflow || consoleProblems.length) {
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
    results.push({ ordinal, relativePath, label, filename, bytes: fs.statSync(pdfPath).size, ...audit });
    await page.close();
  }
} finally {
  await browser.close();
}

process.stdout.write(JSON.stringify({ browserVersion, documents: results }));
