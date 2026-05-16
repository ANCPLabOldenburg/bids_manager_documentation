/* =====================================================================
 * BIDS Manager documentation -- runtime
 *
 * Responsibilities:
 *   1. Inject shared partials (header / footer) from /partials/*.html so
 *      every page reuses the same chrome without duplication.
 *   2. Theme toggle (dark / light) + localStorage persistence.
 *   3. Highlight the current-page nav link.
 *   4. Scroll-reveal animation on .reveal elements.
 *   5. Interactive workflow flowchart on /intro.html (mode tabs, hover /
 *      click highlight, traveling dot).
 *
 * Each section is guarded so a page that does not use a feature does not
 * fire its code (e.g. the workflow only runs when the SVG is present).
 * ===================================================================== */

(async function bootDocs() {
  // ------------------------------------------------------------------
  // 1. Partial includes
  // ------------------------------------------------------------------
  const includes = Array.from(document.querySelectorAll("[data-include]"));
  await Promise.all(
    includes.map(async (el) => {
      const name = el.dataset.include;
      try {
        const resp = await fetch(`partials/${name}.html`, { cache: "no-cache" });
        if (!resp.ok) throw new Error(resp.statusText);
        const html = await resp.text();
        const tmp = document.createElement("template");
        tmp.innerHTML = html;
        el.replaceWith(tmp.content.cloneNode(true));
      } catch (err) {
        console.warn(`[docs] could not inject partial ${name}:`, err);
        el.replaceWith();
      }
    })
  );

  // After partials are in the DOM, wire all features below.
  initThemeToggle();
  highlightActiveNavLink();
  initScrollReveal();
  initWorkflowFlowchart();
})();


/* ====================================================================
 * Theme toggle
 * ================================================================== */

function initThemeToggle() {
  const root = document.documentElement;
  const toggle = document.querySelector(".theme-toggle");
  const stored = (() => {
    try { return window.localStorage.getItem("bidsmgr-docs-theme"); }
    catch { return null; }
  })();
  const prefersLight = window.matchMedia?.("(prefers-color-scheme: light)").matches;
  const initial = stored || (prefersLight ? "light" : "dark");

  function apply(theme) {
    root.dataset.theme = theme;
    if (toggle) {
      const isLight = theme === "light";
      toggle.textContent = isLight ? "Dark theme" : "Light theme";
      toggle.setAttribute("aria-pressed", String(isLight));
    }
    swapThemedImages(theme);
  }
  apply(initial);

  toggle?.addEventListener("click", () => {
    const next = root.dataset.theme === "light" ? "dark" : "light";
    try { window.localStorage.setItem("bidsmgr-docs-theme", next); }
    catch { /* ignore */ }
    apply(next);
  });
}


/* Swap any <img data-light="..."> between the dark default (src="...")
 * and the light variant (data-light="..."). Used by the hero rotation
 * and by any other themed screenshot we ship in the future. The
 * original dark URL is cached on the element the first time we touch
 * it so flipping back and forth between themes doesn't lose it. */
function swapThemedImages(theme) {
  document.querySelectorAll("img[data-light]").forEach((img) => {
    if (!img.dataset.dark) img.dataset.dark = img.getAttribute("src");
    const target = theme === "light" ? img.dataset.light : img.dataset.dark;
    if (img.getAttribute("src") !== target) img.setAttribute("src", target);
  });
}


/* ====================================================================
 * Active nav link highlight
 * ================================================================== */

function highlightActiveNavLink() {
  const here = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  document.querySelectorAll(".nav-links a").forEach((a) => {
    const href = (a.getAttribute("href") || "").toLowerCase();
    if (href === here || (here === "" && href === "index.html")) {
      a.classList.add("is-active");
    }
  });
}


/* ====================================================================
 * Scroll-reveal
 * ================================================================== */

function initScrollReveal() {
  const targets = document.querySelectorAll(
    ".section, .feature-card, .workflow-stage, .callout, .prose > h2, .prose > h3, .prose > p, .prose > ul, .prose > pre, .reveal"
  );
  targets.forEach((el) => el.classList.add("reveal"));

  if (!("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("is-visible"));
    return;
  }
  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add("is-visible");
        io.unobserve(e.target);
      }
    }),
    { threshold: 0.12 }
  );
  targets.forEach((el) => io.observe(el));
}


/* ====================================================================
 * Workflow flowchart (intro page)
 *
 * SVG markup includes a main path that visits every node + a hidden
 * traveling dot. We animate the dot's cx / cy by sampling
 * ``getPointAtLength`` on the path. Hovering / clicking nodes flips
 * descriptions in the side panel; the "mode" tabs swap the entire
 * description set so the same diagram tells three stories.
 * ================================================================== */

function initWorkflowFlowchart() {
  const svg = document.querySelector(".workflow-graph");
  if (!svg) return;
  const detail = document.querySelector("[data-workflow-detail]");
  const modesContainer = document.querySelector(".workflow-modes");
  if (!detail || !modesContainer) return;

  /* Three "stories" told by the same diagram. Keys must match the
   * data-node attribute on the SVG group nodes. */
  const STORIES = {
    engine: {
      raw:     ["Raw data",   "DICOM directories, EEG and MEG recordings, optional physio."],
      scan:    ["Schema scan", "<code>inventory/</code> walkers stamp each row with a <code>bids_guess_*</code> entity tuple drawn from the BIDS schema."],
      edit:    ["Plan edits",  "User overrides land in the inventory TSV. The same schema engine validates the entity set before conversion runs."],
      convert: ["Convert",    "Per-task dispatch: <code>Dcm2niixDirect</code>, <code>MneBidsBackend</code>, <code>PhysioDcmBackend</code> (vendored bidsphysio)."],
      fix:     ["Fix-ups",    "Field-maps re-named, <code>IntendedFor</code> resolved, <code>scans.tsv</code> stitched together."],
      inspect: ["Inspect",    "The Editor reads every sidecar against the same schema and reports missing / wrong / deprecated fields."],
      validate:["Validate",   "Two-layer: bidsmgr's schema audit plus the official <code>bidsschematools</code> validator (optional strict mode)."],
      bids:    ["BIDS",       "A schema-compliant dataset with provenance preserved in the <code>.bidsmgr/</code> event log."],
    },
    data: {
      raw:     ["Raw data",   "What you point the tool at: <code>raw/</code> with DICOM tree, EDF / BDF / FIF / MEG, plus PMU / BioPac when present."],
      scan:    ["inventory.tsv", "51 columns. One row per series or source file. Re-runnable + diff-able."],
      edit:    ["Per-row overrides", "Spreadsheet-style: cells override the schema guess for a series. Bulk-edit applies one value to a selection."],
      convert: ["NIfTI + sidecars", "BIDS layout under <code>bids/</code>, per-subject atomic rename from staging."],
      fix:     ["Cross-file metadata", "<code>fmap/*.json</code>, <code>scans.tsv</code>, <code>participants.tsv</code> populated from the inventory."],
      inspect: ["Sidecar audit", "Per-(datatype, suffix) schema view; missing required fields flagged inline."],
      validate:["Validation report", "Severity-tagged file list + folder rollups + dataset-level rules."],
      bids:    ["BIDS dataset", "Ready to share, archive, or feed into MNE / FSL / nipype / SPM pipelines."],
    },
    gui: {
      raw:     ["Raw data tree pane", "Left column of the Converter view. Browse the raw input root."],
      scan:    ["Scan button + inspection table", "Toolbar Scan kicks the worker; results populate the table in the middle."],
      edit:    ["Inspection table + Bulk edit", "Edit cells inline, multi-select then click Bulk edit to apply across rows."],
      convert: ["Run conversion button", "Right side of the toolbar. Spawns the converter worker, status chips update live."],
      fix:     ["Post-convert chain (Settings)", "Run metadata + validate as part of the conversion pipeline."],
      inspect: ["Editor sidecar form pane", "Switch to Editor, click a JSON. Schema-driven form + Tree view."],
      validate:["Editor validation pane", "Validate file / folder / dataset; severity chips at the top."],
      bids:    ["BIDS tree pane (Editor)", "Browse the converted dataset with per-file status badges."],
    },
  };

  let currentMode = "engine";
  let pinned = null;

  /* ---------- node interactivity ---------- */
  const nodes = Array.from(svg.querySelectorAll("[data-node]"));

  function describe(nodeKey) {
    const data = STORIES[currentMode]?.[nodeKey];
    if (!data) return;
    const [title, body] = data;
    detail.innerHTML = `
      <h3><span class="badge">${nodeKey}</span>${title}</h3>
      <p>${body}</p>
    `;
  }

  function activate(nodeKey) {
    nodes.forEach((n) => n.classList.toggle("is-active", n.dataset.node === nodeKey));
    describe(nodeKey);
  }

  nodes.forEach((n) => {
    const key = n.dataset.node;
    n.style.cursor = "pointer";
    n.addEventListener("mouseenter", () => { if (!pinned) activate(key); });
    n.addEventListener("focus",      () => { if (!pinned) activate(key); });
    n.addEventListener("click",      () => {
      pinned = pinned === key ? null : key;
      activate(key);
    });
  });

  /* ---------- mode tabs ---------- */
  modesContainer.querySelectorAll(".workflow-mode").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentMode = btn.dataset.mode;
      modesContainer.querySelectorAll(".workflow-mode").forEach((b) =>
        b.classList.toggle("is-active", b === btn)
      );
      const activeNode = nodes.find((n) => n.classList.contains("is-active"))?.dataset.node;
      if (activeNode) describe(activeNode);
    });
  });

  /* ---------- traveling dot ---------- */
  const mainPath = svg.querySelector("#wf-main-path");
  const dot = svg.querySelector(".wf-dot");
  if (mainPath && dot && !window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) {
    const length = mainPath.getTotalLength();
    let start = null;
    const duration = 9000;
    function step(ts) {
      if (start === null) start = ts;
      const progress = ((ts - start) % duration) / duration;
      const pt = mainPath.getPointAtLength(length * progress);
      dot.setAttribute("cx", pt.x.toFixed(2));
      dot.setAttribute("cy", pt.y.toFixed(2));
      requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* ---------- bootstrap with the first node selected ---------- */
  activate("raw");
}


