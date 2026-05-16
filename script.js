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
  initTabs();
  initInstallPipeline();
  initPageToc();
})();


/* ====================================================================
 * Page TOC (sticky sub-navigation on long pages)
 *
 * For any [.page-toc] block, observe the sections it links to and mark
 * the closest-to-top visible one as .is-active. Click already works
 * via plain anchor scrolling.
 * ================================================================== */

function initPageToc() {
  const toc = document.querySelector(".page-toc");
  if (!toc) return;
  const toggle  = toc.querySelector(".page-toc-toggle");
  const links   = Array.from(toc.querySelectorAll(".page-toc-link"));
  if (!links.length) return;

  /* ---------- open / closed state ---------- */
  const stored = (() => {
    try { return window.localStorage.getItem("bidsmgr-docs-toc-open"); }
    catch { return null; }
  })();
  const wideEnough = window.matchMedia?.("(min-width: 1200px)").matches;
  const initiallyOpen = stored !== null ? stored === "1" : wideEnough;

  function setOpen(open) {
    toc.classList.toggle("is-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", String(open));
    try { window.localStorage.setItem("bidsmgr-docs-toc-open", open ? "1" : "0"); }
    catch { /* ignore */ }
  }
  setOpen(initiallyOpen);

  toggle?.addEventListener("click", () => {
    setOpen(!toc.classList.contains("is-open"));
  });

  /* Esc closes the drawer (only when it's open and the toggle is focused
   * or focus is within the drawer). */
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && toc.classList.contains("is-open")) {
      setOpen(false);
      toggle?.focus();
    }
  });

  /* ---------- scroll-spy ---------- */
  const linkById = new Map();
  const sections = [];
  links.forEach((a) => {
    const id = (a.getAttribute("href") || "").replace(/^#/, "");
    const sec = id && document.getElementById(id);
    if (sec) {
      linkById.set(id, a);
      sections.push(sec);
    }
  });
  if (!sections.length) return;

  function setActive(id) {
    links.forEach((l) => l.classList.toggle("is-active", linkById.get(id) === l));
  }

  if (!("IntersectionObserver" in window)) {
    setActive(sections[0].id);
    return;
  }

  const visible = new Set();
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) visible.add(e.target);
        else visible.delete(e.target);
      });
      if (!visible.size) return;
      const closest = Array.from(visible).sort(
        (a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top
      )[0];
      if (closest) setActive(closest.id);
    },
    { rootMargin: "-110px 0px -55% 0px", threshold: 0 }
  );
  sections.forEach((s) => io.observe(s));
}


/* ====================================================================
 * Install pipeline (installation page)
 *
 * Drives the 7-step "what does the installer do?" visualization. Each
 * step cumulatively reveals one SVG layer; the active layer pulses; a
 * progress bar fills between auto-advances. Hover a chip to preview,
 * click a chip to pin, click Pause / Auto-play to toggle.
 *
 * Honours prefers-reduced-motion (skips the auto-advance loop).
 * ================================================================== */

function initInstallPipeline() {
  const pipe = document.querySelector("[data-pipeline]");
  if (!pipe) return;
  const chips    = Array.from(pipe.querySelectorAll(".pipeline-chip"));
  const layers   = Array.from(pipe.querySelectorAll(".stage-layer"));
  const detail   = pipe.querySelector("[data-pipeline-detail]");
  const progress = pipe.querySelector(".pipeline-progress");
  const playBtn  = pipe.querySelector("[data-pipeline-play]");
  if (!chips.length || !layers.length || !detail) return;

  const STEPS = [
    {
      title: "Create the install folder",
      body:  "A new <code class=\"inline\">~/BIDS-Manager/</code> directory is created in your home. Everything BIDS Manager needs lives inside it, fully isolated from the rest of your system."
    },
    {
      title: "Download portable Python 3.10",
      body:  "The installer downloads a portable Python 3.10 build matched to your OS and architecture. Apple Silicon and Linux x86_64 use a standalone build; Windows uses Python's official embeddable distribution. Your system Python is untouched."
    },
    {
      title: "Extract the runtime",
      body:  "The archive is unpacked under <code class=\"inline\">~/BIDS-Manager/</code> and <code class=\"inline\">pip</code> is bootstrapped. The runtime is now fully self-contained."
    },
    {
      title: "Create the virtual environment",
      body:  "A virtual environment is built at <code class=\"inline\">~/BIDS-Manager/env/</code>. This is where BIDS Manager and its dependencies will live, kept separate from any other Python tools you have."
    },
    {
      title: "pip install bids-manager",
      body:  "<code class=\"inline\">pip install bids-manager</code> runs inside the venv. PyQt6, mne-bids, dcm2niix, pydicom, bidsschematools, and the rest of the dependency tree are pulled in here."
    },
    {
      title: "Register a native launcher",
      body:  "A native launcher is created. Windows: Desktop + Start Menu shortcut. macOS: <code class=\"inline\">~/Applications/BIDS-Manager.app</code> bundle. Linux: application-menu entry with the BIDS Manager icon."
    },
    {
      title: "Write the uninstaller",
      body:  "An uninstaller is placed alongside the launcher. One double-click later, every file, the venv, every shortcut, all goes away. No leftover system changes to chase down."
    }
  ];

  const STEP_MS = 4200;
  let current  = 0;
  let pinned   = -1;
  let running  = true;
  let stepStart = performance.now();

  function render(idx) {
    chips.forEach((c, i) => {
      const on = i === idx;
      c.classList.toggle("is-active", on);
      c.setAttribute("aria-selected", String(on));
    });
    layers.forEach((l, i) => {
      l.classList.toggle("is-shown",   i <= idx);
      l.classList.toggle("is-current", i === idx);
    });
    /* Pull the active chip's --step-color / --step-glow into the
     * pipeline root so the progress bar gradient and the detail-step
     * eyebrow recolor along with the visualization. */
    const active = chips[idx];
    if (active) {
      const cs = getComputedStyle(active);
      const stepColor = cs.getPropertyValue("--step-color").trim();
      const stepGlow  = cs.getPropertyValue("--step-glow").trim();
      if (stepColor) pipe.style.setProperty("--current-step-color", stepColor);
      if (stepGlow)  pipe.style.setProperty("--current-step-glow",  stepGlow);
    }
    const s = STEPS[idx];
    detail.innerHTML = `
      <h3>
        <span class="detail-step">Step ${idx + 1} of ${STEPS.length}</span>
        <span class="detail-title">${s.title}</span>
      </h3>
      <p>${s.body}</p>
    `;
  }

  function tick(ts) {
    if (running) {
      const elapsed = ts - stepStart;
      const p = Math.min(elapsed / STEP_MS, 1);
      progress.style.setProperty("--progress", (p * 100).toFixed(1) + "%");
      if (p >= 1) {
        current = (current + 1) % STEPS.length;
        render(current);
        stepStart = ts;
      }
    }
    requestAnimationFrame(tick);
  }

  chips.forEach((chip, i) => {
    chip.addEventListener("click", () => {
      current = i;
      pinned = i;
      running = false;
      progress.style.setProperty("--progress", "0%");
      render(current);
      if (playBtn) playBtn.textContent = "Auto-play";
    });
    chip.addEventListener("mouseenter", () => {
      if (pinned < 0 && running) {
        running = false;
        render(i);
      }
    });
    chip.addEventListener("mouseleave", () => {
      if (pinned < 0) {
        running = true;
        stepStart = performance.now();
        render(current);
      }
    });
    chip.addEventListener("focus", () => {
      if (pinned < 0) render(i);
    });
  });

  if (playBtn) {
    playBtn.addEventListener("click", () => {
      if (running) {
        running = false;
        playBtn.textContent = "Auto-play";
      } else {
        pinned = -1;
        running = true;
        stepStart = performance.now();
        playBtn.textContent = "Pause";
      }
    });
  }

  render(0);

  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  if (!reducedMotion) {
    requestAnimationFrame(tick);
  } else if (playBtn) {
    running = false;
    playBtn.textContent = "Auto-play";
  }
}


/* ====================================================================
 * Tabs (per-OS sections on installation.html)
 *
 * Markup contract:
 *   <div class="tabs" data-tabs>
 *     <div class="tab-buttons"><button data-tab="key">...</button>...</div>
 *     <div class="tab-panel" data-panel="key">...</div>
 *     ...
 *   </div>
 *
 * Each [data-tabs] block is wired independently so the same page can
 * host several tab groups without interference.
 * ================================================================== */

function initTabs() {
  const osDefault = detectOsKey();

  document.querySelectorAll("[data-tabs]").forEach((group) => {
    const buttons = Array.from(group.querySelectorAll(".tab-btn"));
    const panels  = Array.from(group.querySelectorAll(".tab-panel"));
    if (!buttons.length || !panels.length) return;

    function activate(key) {
      buttons.forEach((b) => {
        const on = b.dataset.tab === key;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", String(on));
      });
      panels.forEach((p) => {
        p.classList.toggle("is-active", p.dataset.panel === key);
      });
    }

    buttons.forEach((b) => {
      b.addEventListener("click", () => activate(b.dataset.tab));
    });

    /* If the group exposes one of the known OS keys, preselect the
     * visitor's OS. Otherwise leave the markup default alone. */
    if (osDefault && buttons.some((b) => b.dataset.tab === osDefault)) {
      activate(osDefault);
    }
  });
}


/* Map navigator.userAgentData / navigator.platform to one of the three
 * keys used by the per-OS tab groups. Returns null if unrecognised. */
function detectOsKey() {
  const ua = `${navigator.userAgent || ""} ${navigator.platform || ""}`.toLowerCase();
  if (ua.includes("win")) return "windows";
  if (ua.includes("mac") || ua.includes("darwin")) return "macos";
  if (ua.includes("linux") || ua.includes("x11") || ua.includes("bsd")) return "linux";
  return null;
}


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


