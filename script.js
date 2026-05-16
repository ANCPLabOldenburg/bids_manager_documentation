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
  initCodeCopy();
  initDatasetOverview();
})();


/* ====================================================================
 * Dataset overview (tutorial.html)
 *
 * Drives the per-subject series breakdown. The tab row above the
 * overview swaps between OL_0001 / OL_0002 / OL_0003; clicking or
 * hovering a series row updates the detail panel on the right with
 * a description of what BIDS Manager does with that series.
 *
 * Series metadata is verified against the actual DICOM headers of
 * `/Users/karelo/Development/datasets/BIDS_Manager/raw_data/MRI/
 *  neuroimaging_unit_new` (see TUTORIAL_PLAN.md §2).
 * ================================================================== */

function initDatasetOverview() {
  const root = document.querySelector("[data-overview]");
  if (!root) return;
  const list   = root.querySelector("[data-series-list]");
  const detail = root.querySelector("[data-series-detail]");
  const tabs   = Array.from(root.querySelectorAll("[data-tab]"));
  if (!list || !detail || !tabs.length) return;

  /* ----- Datatype icon library ----- */

  const ICONS = {
    /* Crosshair / target: scout / localizer */
    scout: `<svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="9"/>
      <circle cx="12" cy="12" r="3"/>
      <path d="M12 1v4M12 19v4M1 12h4M19 12h4"/></svg>`,
    /* Brain-y outline: anat (T1w / T2w) */
    anat: `<svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 4c-3 0-5 2-5 4 0 1-1 2-2 3 0 2 2 3 2 4 0 3 2 5 5 5
               s5-2 5-5c0-1 2-2 2-4-1-1-2-2-2-3 0-2-2-4-5-4z"/>
      <path d="M12 4v16M9 9c1 1 2 1 3 0M9 15c1 1 2 1 3 0"/></svg>`,
    /* Wave / pulse: func (BOLD) */
    func: `<svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M2 14h3l2-7 3 14 3-10 2 6 2-3h5"/></svg>`,
    /* Compass cross: fmap (B0 field) */
    fmap: `<svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="9"/>
      <path d="M12 4v16M4 12h16M6 6l12 12M6 18l12-12"/></svg>`,
    /* Arrows in four directions: dwi (directional gradients) */
    dwi: `<svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 4v6M9 7l3-3 3 3"/>
      <path d="M12 20v-6M9 17l3 3 3-3"/>
      <path d="M4 12h6M7 9l-3 3 3 3"/>
      <path d="M20 12h-6M17 9l3 3-3 3"/></svg>`,
    /* ECG line: physio */
    physio: `<svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M2 12h4l2-5 3 10 3-7 2 4 2-2h4"/></svg>`,
    /* Document: structured report */
    sr: `<svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M6 3h9l4 4v14H6z"/>
      <path d="M15 3v4h4M9 12h7M9 16h7M9 8h3"/></svg>`,
  };

  /* ----- Series data (curated from real DICOM headers) ----- */

  const SERIES = {
    OL_0001: [
      { no: 1,  desc: "localizer_20ch_head-coil",    files: 2,  type: "scout",
        skipped: true,
        what: "Three-plane scout used by the operator to align the rest of the protocol. BIDS Manager skips it: a row stays in the inventory marked as 'scout', but no NIfTI is written." },
      { no: 2,  desc: "ses-pre_run-01_fmap",         files: 2,  type: "fmap",
        what: "Fieldmap magnitude image, run 01. Paired with series 3 (phase) for distortion correction.",
        bids: "sub-001/ses-pre/fmap/sub-001_ses-pre_run-01_magnitude1.nii.gz" },
      { no: 3,  desc: "ses-pre_run-01_fmap",         files: 1,  type: "fmap",
        what: "Fieldmap phase image, run 01. The phase-difference computation happens later in the fixups stage.",
        bids: "sub-001/ses-pre/fmap/sub-001_ses-pre_run-01_phasediff.nii.gz" },
      { no: 4,  desc: "ses-pre_task-sparse_bold",    files: 10, type: "func",
        what: "Task fMRI. The 'sparse' name in SeriesDescription is picked up by the schema-driven classifier as the BIDS task entity. You can rename it inline in Scene 4.",
        bids: "sub-001/ses-pre/func/sub-001_ses-pre_task-sparse_bold.nii.gz" },
      { no: 6,  desc: "ses-pre_T1w",                 files: 1,  type: "anat",
        what: "T1-weighted anatomical reference. The SeriesDescription already encodes the BIDS suffix, so the classifier maps it without user input.",
        bids: "sub-001/ses-pre/anat/sub-001_ses-pre_T1w.nii.gz" },
      { no: 7,  desc: "ses-pre_run-02_fmap",         files: 2,  type: "fmap",
        what: "Second fieldmap magnitude, run 02. IntendedFor will list the rest-BOLD acquired right after.",
        bids: "sub-001/ses-pre/fmap/sub-001_ses-pre_run-02_magnitude1.nii.gz" },
      { no: 8,  desc: "ses-pre_run-02_fmap",         files: 1,  type: "fmap",
        what: "Second fieldmap phase, run 02.",
        bids: "sub-001/ses-pre/fmap/sub-001_ses-pre_run-02_phasediff.nii.gz" },
      { no: 9,  desc: "ses-pre_task-rest_bold",      files: 20, type: "func",
        what: "Resting-state BOLD. 20 volumes. The fmap_run-02 pair is auto-attached via IntendedFor in the fixups stage.",
        bids: "sub-001/ses-pre/func/sub-001_ses-pre_task-rest_bold.nii.gz" },
      { no: 99, desc: "PhoenixZIPReport",            files: 6,  type: "sr",
        skipped: true,
        what: "Siemens scanner metadata report (SR DICOM, not image data). BIDS Manager skips it automatically." },
    ],
    OL_0002: [
      { no: 1, desc: "AAHead_Scout_64ch-head-coil",         files: 1, type: "scout",
        skipped: true,
        what: "Scout / localizer. Skipped." },
      { no: 2, desc: "AAHead_Scout_64ch-head-coil_MPR_sag", files: 1, type: "scout",
        skipped: true,
        what: "Sagittal MPR resample from the scout. Skipped." },
      { no: 3, desc: "AAHead_Scout_64ch-head-coil_MPR_cor", files: 1, type: "scout",
        skipped: true,
        what: "Coronal MPR resample from the scout. Skipped." },
      { no: 4, desc: "AAHead_Scout_64ch-head-coil_MPR_tra", files: 1, type: "scout",
        skipped: true,
        what: "Transverse MPR resample from the scout. Skipped. This subject's protocol stopped here, leaving no anatomical reference, which the validator will warn about." },
      { no: 5, desc: "ses-post_run-01_fmap",                files: 2, type: "fmap",
        what: "Fieldmap magnitude, run 01.",
        bids: "sub-002/ses-post/fmap/sub-002_ses-post_run-01_magnitude1.nii.gz" },
      { no: 6, desc: "ses-post_run-01_fmap",                files: 1, type: "fmap",
        what: "Fieldmap phase, run 01.",
        bids: "sub-002/ses-post/fmap/sub-002_ses-post_run-01_phasediff.nii.gz" },
      { no: 7, desc: "ses-post_task-mb_bold_SBRef",         files: 1, type: "func",
        what: "Single-band reference for the multiband BOLD that follows. BIDS Manager classifies it as _sbref.",
        bids: "sub-002/ses-post/func/sub-002_ses-post_task-mb_sbref.nii.gz" },
      { no: 8, desc: "ses-post_task-mb_bold",               files: 50, type: "func",
        what: "Multiband BOLD task. 50 volumes. The SBRef from series 7 is referenced in the sidecar via IntendedFor.",
        bids: "sub-002/ses-post/func/sub-002_ses-post_task-mb_bold.nii.gz" },
      { no: 10, desc: "ses-post_task-mb_bold_PhysioLog",    files: 1, type: "physio",
        what: "Siemens physio log for the BOLD. The PhysioDcmBackend (vendored bidsphysio) parses it into BIDS-compliant _physio.tsv.gz + .json.",
        bids: "sub-002/ses-post/func/sub-002_ses-post_task-mb_physio.tsv.gz" },
      { no: 99, desc: "PhoenixZIPReport",                   files: 3, type: "sr",
        skipped: true,
        what: "Siemens metadata SR. Skipped." },
    ],
    OL_0003: [
      { no: 1,  desc: "AAHead_Scout_64ch-head-coil",         files: 1,   type: "scout",
        skipped: true, what: "Scout. Skipped." },
      { no: 2,  desc: "AAHead_Scout_64ch-head-coil_MPR_sag", files: 1,   type: "scout",
        skipped: true, what: "Sagittal MPR resample. Skipped." },
      { no: 3,  desc: "AAHead_Scout_64ch-head-coil_MPR_cor", files: 1,   type: "scout",
        skipped: true, what: "Coronal MPR resample. Skipped." },
      { no: 4,  desc: "AAHead_Scout_64ch-head-coil_MPR_tra", files: 1,   type: "scout",
        skipped: true, what: "Transverse MPR resample. Skipped." },
      { no: 5,  desc: "acq-space_T2w",                        files: 1,   type: "anat",
        what: "T2-weighted anatomical (SPACE sequence). The acq-space label is picked up from the SeriesDescription.",
        bids: "sub-003/anat/sub-003_acq-space_T2w.nii.gz" },
      { no: 6,  desc: "task-dmaging_run-01_bold_SBRef",       files: 1,   type: "func",
        what: "SBRef for run 01 of the dmaging task.",
        bids: "sub-003/func/sub-003_task-dmaging_run-01_sbref.nii.gz" },
      { no: 7,  desc: "task-dmaging_run-01_bold",             files: 50,  type: "func",
        what: "Multiband BOLD, dmaging task, run 01.",
        bids: "sub-003/func/sub-003_task-dmaging_run-01_bold.nii.gz" },
      { no: 9,  desc: "task-dmaging_run-01_bold_PhysioLog",   files: 1,   type: "physio",
        what: "Physio log for run 01.",
        bids: "sub-003/func/sub-003_task-dmaging_run-01_physio.tsv.gz" },
      { no: 10, desc: "task-dmaging_run-02_bold_SBRef",       files: 1,   type: "func",
        what: "SBRef for run 02.",
        bids: "sub-003/func/sub-003_task-dmaging_run-02_sbref.nii.gz" },
      { no: 11, desc: "task-dmaging_run-02_bold",             files: 50,  type: "func",
        what: "Multiband BOLD, dmaging task, run 02.",
        bids: "sub-003/func/sub-003_task-dmaging_run-02_bold.nii.gz" },
      { no: 13, desc: "task-dmaging_run-02_bold_PhysioLog",   files: 1,   type: "physio",
        what: "Physio log for run 02.",
        bids: "sub-003/func/sub-003_task-dmaging_run-02_physio.tsv.gz" },
      { no: 14, desc: "task-uebung_bold_SBRef",               files: 1,   type: "func",
        what: "SBRef for the practice / uebung task.",
        bids: "sub-003/func/sub-003_task-uebung_sbref.nii.gz" },
      { no: 15, desc: "task-uebung_bold",                     files: 50,  type: "func",
        what: "Multiband BOLD, practice / uebung task.",
        bids: "sub-003/func/sub-003_task-uebung_bold.nii.gz" },
      { no: 17, desc: "acq-15_dir-ap_dwi",                    files: 117, type: "dwi",
        what: "Diffusion-weighted imaging, anterior-to-posterior phase-encoding, 15 directions (plus b=0 frames). 117 DICOMs = one per direction per volume.",
        bids: "sub-003/dwi/sub-003_acq-15_dir-AP_dwi.nii.gz" },
      { no: 18, desc: "acq-15b0_dir-ap_dwi",                  files: 1,   type: "dwi",
        what: "b=0 AP acquisition for the DWI. Stays in dwi/ as a reference volume.",
        bids: "sub-003/dwi/sub-003_acq-15b0_dir-AP_dwi.nii.gz" },
      { no: 19, desc: "acq-15_dir-pa_dwi",                    files: 1,   type: "dwi",
        what: "b=0 PA acquisition. The classifier reroutes this to fmap/_epi automatically because PA-direction b=0 in a DWI block is the standard distortion reference.",
        bids: "sub-003/fmap/sub-003_acq-15_dir-PA_epi.nii.gz" },
      { no: 99, desc: "PhoenixZIPReport",                     files: 8,   type: "sr",
        skipped: true, what: "Siemens metadata SR. Skipped." },
    ],
  };

  let currentSubject = "OL_0001";
  let currentIndex = 0;

  function renderList() {
    const rows = SERIES[currentSubject] || [];
    list.innerHTML = "";
    rows.forEach((s, i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "series-row";
      btn.setAttribute("data-type",    s.type);
      btn.setAttribute("data-index",   String(i));
      btn.setAttribute("role",         "option");
      btn.setAttribute("aria-selected", String(i === currentIndex));
      if (s.skipped) btn.setAttribute("data-skipped", "1");
      if (i === currentIndex) btn.classList.add("is-active");
      btn.innerHTML = `
        <span class="series-icon">${ICONS[s.type] || ICONS.sr}</span>
        <span class="series-meta">
          <span class="series-no">Series ${s.no} . ${s.files} file${s.files === 1 ? "" : "s"}</span>
          <span class="series-desc">${s.desc}</span>
        </span>
        <span class="series-chip">${s.skipped ? "skipped" : s.type}</span>
      `;
      btn.addEventListener("click",      () => { currentIndex = i; renderList(); renderDetail(); });
      btn.addEventListener("mouseenter", () => { renderDetail(i); });
      btn.addEventListener("mouseleave", () => { renderDetail(); });
      btn.addEventListener("focus",      () => { renderDetail(i); });
      list.appendChild(btn);
    });
  }

  function renderDetail(previewIdx) {
    const rows = SERIES[currentSubject] || [];
    const idx  = previewIdx ?? currentIndex;
    const s    = rows[idx];
    if (!s) { detail.innerHTML = ""; return; }
    /* Inherit the same colour as the row via the data-type custom prop
     * so the eyebrow / chip / hover ring stay in sync. */
    detail.style.setProperty("--series-color", `var(--${typeColorVar(s.type)})`);
    const eyebrow = s.skipped ? "Skipped"
                              : s.type.charAt(0).toUpperCase() + s.type.slice(1);
    detail.innerHTML = `
      <span class="series-detail-eyebrow">${eyebrow}</span>
      <h3>${s.desc}</h3>
      <p class="series-detail-meta">Series ${s.no} . ${s.files} DICOM file${s.files === 1 ? "" : "s"} . ${currentSubject}</p>
      <p>${s.what}</p>
      ${s.bids
        ? `<code class="series-detail-bids">${s.bids}</code>`
        : `<code class="series-detail-bids" style="color: var(--muted);">(not converted)</code>`}
    `;
  }

  /* Map a datatype to the matching --stepN variable name (defined in
   * the install pipeline palette). Keeps every coloured surface in
   * the docs speaking the same token. */
  function typeColorVar(type) {
    switch (type) {
      case "anat":   return "step1";
      case "func":   return "step5";
      case "fmap":   return "step4";
      case "dwi":    return "step3";
      case "physio": return "step2";
      default:       return "quiet";   /* scout / sr */
    }
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      currentSubject = tab.dataset.tab;
      currentIndex = 0;
      tabs.forEach((b) => {
        const on = b === tab;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", String(on));
      });
      renderList();
      renderDetail();
    });
  });

  renderList();
  renderDetail();
}


/* ====================================================================
 * Code copy-to-clipboard
 *
 * For every <pre class="code"> on the page, snapshot its plain-text
 * contents and inject a small "Copy" button. Click copies the cached
 * text via the async Clipboard API, with a document.execCommand
 * fallback for older browsers / non-secure contexts. The button
 * flashes "Copied!" (or "Failed") for 1.5 seconds.
 *
 * The snapshot is taken BEFORE the button is appended so the button's
 * own label is never copied along with the code.
 * ================================================================== */

function initCodeCopy() {
  const COPY_ICON = `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="9" y="9" width="12" height="12" rx="2"/>
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
    </svg>`;

  document.querySelectorAll("pre.code").forEach((pre) => {
    if (pre.dataset.copyReady) return;
    pre.dataset.copyReady = "1";

    // Snapshot the plain-text source before the button is added.
    pre.dataset.copyText = pre.textContent;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "code-copy";
    btn.setAttribute("aria-label", "Copy code to clipboard");
    btn.innerHTML = `${COPY_ICON}<span class="code-copy-label">Copy</span>`;
    pre.appendChild(btn);

    btn.addEventListener("click", () => copyFromPre(pre, btn));
  });

  async function copyFromPre(pre, btn) {
    const text = pre.dataset.copyText || "";
    let ok = false;
    if (navigator.clipboard?.writeText) {
      try { await navigator.clipboard.writeText(text); ok = true; }
      catch { /* fall through to legacy path */ }
    }
    if (!ok) ok = legacyCopy(text);
    flashCopy(btn, ok);
  }

  function legacyCopy(text) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "absolute";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand("copy"); } catch { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  function flashCopy(btn, ok) {
    const label = btn.querySelector(".code-copy-label");
    if (!label) return;
    label.textContent = ok ? "Copied!" : "Failed";
    btn.classList.toggle("is-copied", ok);
    btn.classList.toggle("is-failed", !ok);
    setTimeout(() => {
      label.textContent = "Copy";
      btn.classList.remove("is-copied", "is-failed");
    }, 1500);
  }
}


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


