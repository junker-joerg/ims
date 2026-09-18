// Render the two checked-in handbook sources as the PDFs shipped in the test ZIP.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
function dependency(name) {
  try { return require(name); }
  catch { return require(path.resolve(path.dirname(process.execPath), "../node_modules", name)); }
}
const { marked } = dependency("marked");
const { chromium } = dependency("playwright");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const handbook = path.join(root, "docs", "handbook");
const scratch = path.join(root, "tmp", "pdfs");

function browserExecutable() {
  const candidates = [
    process.env.IMS_PDF_CHROME,
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  ];
  const found = candidates.find(candidate => candidate && fs.existsSync(candidate));
  if (!found) throw new Error("Set IMS_PDF_CHROME to a local Chrome/Edge executable");
  return found;
}

const sources = [
  ["installation_test_package_windows.md", "IMS-Installation-Windows.pdf", 2],
  ["user_guide_test_package.md", "IMS-Bedienungsanleitung.pdf", 10],
];

function htmlFor(filename, expectedPages) {
  const markdown = fs.readFileSync(path.join(handbook, filename), "utf8");
  const parts = markdown.split("<!-- PAGE BREAK -->");
  if (parts.length !== expectedPages) {
    throw new Error(`${filename}: expected ${expectedPages} explicit pages, found ${parts.length}`);
  }
  const pages = parts.map((part, index) => `<article class="page page-${index + 1}">
    <main class="page-body">${marked.parse(part, { gfm: true })}</main>
    <footer>IMS 1995-2026 | Stand 18.09.2026 <span>${index + 1} / ${expectedPages}</span></footer>
  </article>`).join("\n");
  return `<!doctype html><html lang="de"><head><meta charset="utf-8">
    <base href="${pathToFileURL(handbook + path.sep).href}">
    <style>
      @page { size: A4; margin: 0; }
      * { box-sizing: border-box; }
      body { margin: 0; color: #203038; font-family: Arial, Helvetica, sans-serif; }
      .page { width: 210mm; height: 297mm; padding: 13mm 16mm 13mm; position: relative;
        page-break-after: always; break-after: page; border-top: 3mm solid #17624b; }
      .page:last-child { page-break-after: auto; break-after: auto; }
      .page-body { height: 260mm; overflow: hidden; font-size: 11pt; line-height: 1.42; }
      h1 { font-size: 20pt; color: #145840; margin: 0 0 5mm; }
      h2 { font-size: 17pt; color: #145840; margin: 0 0 6mm; }
      h3 { font-size: 12pt; margin: 4mm 0 2mm; }
      p { margin: 0 0 3.5mm; }
      ul, ol { padding-left: 6mm; margin: 2mm 0 3.5mm; }
      li { margin: 0 0 1.8mm; }
      a { color: #145840; text-decoration: none; }
      code { font-family: Consolas, monospace; font-size: 9.3pt; }
      table { border-collapse: collapse; width: 100%; font-size: 9.4pt; margin: 3mm 0 4mm; }
      th, td { border-bottom: 0.35pt solid #bed1c8; padding: 2mm 1.5mm; vertical-align: top; }
      th { background: #edf5f0; text-align: left; }
      img { display: block; width: 100%; height: 74mm; object-fit: contain; object-position: left center; margin: 3mm 0 2mm; }
      .page-1 img { height: 80mm; }
      .page-3 img { height: 70mm; }
      .page-4 img { height: 78mm; object-fit: cover; object-position: top; }
      .page-5 img { height: 90mm; object-fit: cover; object-position: top; }
      .page-6 img { height: 65mm; object-fit: cover; object-position: center 65%; }
      .page-7 img { height: 80mm; object-fit: cover; object-position: center 55%; }
      .page-8 img { height: 124mm; object-fit: cover; object-position: center bottom; }
      .page-9 img { height: 70mm; object-fit: contain; }
      .page-body > p:has(img) { margin: 0; }
      .page-body > p:has(img) + p { font-size: 8.5pt; color: #5a656b; margin-bottom: 4mm; }
      .install .page-body { font-size: 9.5pt; line-height: 1.28; }
      .install h1 { font-size: 16pt; margin-bottom: 3mm; }
      .install h2 { font-size: 14pt; margin-bottom: 3mm; }
      .install h3 { font-size: 11pt; margin: 2mm 0 1mm; }
      .install p { margin-bottom: 2.2mm; }
      .install ul, .install ol { margin: 1mm 0 2mm; }
      .install li { margin-bottom: 1mm; }
      .install table { font-size: 8.6pt; margin: 1mm 0 2mm; }
      .install th, .install td { padding: 1.2mm; }
      blockquote { margin: 1mm 0 2mm 4mm; border-left: 2pt solid #17624b; padding-left: 3mm; }
      footer { position: absolute; left: 16mm; right: 16mm; bottom: 6mm; border-top: 0.3pt solid #b8cfc3;
        padding-top: 2mm; color: #60706b; font-size: 7pt; }
      footer span { float: right; }
      .page-1 h1 + p { color: #53636a; font-size: 8pt; }
    </style></head><body class="${expectedPages === 2 ? "install" : "guide"}">${pages}</body></html>`;
}

async function main() {
  fs.mkdirSync(scratch, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: browserExecutable(),
  });
  try {
    for (const [source, output, count] of sources) {
      const htmlPath = path.join(scratch, `${path.parse(source).name}.html`);
      fs.writeFileSync(htmlPath, htmlFor(source, count));
      const page = await browser.newPage();
      await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
      await page.evaluate(async () => { await Promise.all(Array.from(document.images, image => image.decode())); });
      const overflows = await page.locator(".page-body").evaluateAll(nodes =>
        nodes.map((node, index) => ({ page: index + 1, overflow: node.scrollHeight - node.clientHeight }))
          .filter(item => item.overflow > 2));
      if (overflows.length) throw new Error(`${source}: content overflow ${JSON.stringify(overflows)}`);
      await page.pdf({ path: path.join(root, "output", "pdf", output), printBackground: true,
        preferCSSPageSize: true });
      await page.close();
      fs.unlinkSync(htmlPath);
      process.stdout.write(`${output}: ${count} pages, no overflow\n`);
    }
  } finally {
    await browser.close();
  }
}

await main();
