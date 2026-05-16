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
  initGuiTour();
  initTutorialScenes();
})();


/* ====================================================================
 * GUI tour (tutorial.html, #gui-tour)
 *
 * Click a numbered marker on the screenshot to open the matching
 * popover bubble in place. Clicking the same marker again, another
 * marker, anywhere outside, or pressing Esc dismisses. Only one
 * popover at a time per tour.
 *
 * Independent per-tour state lets the Converter and Editor tours
 * coexist on the same page without leakage.
 * ================================================================== */

function initGuiTour() {
  const tours = Array.from(document.querySelectorAll("[data-tour]"));
  if (!tours.length) return;

  tours.forEach((tour) => {
    const anchors = Array.from(tour.querySelectorAll(".gui-tour-anchor"));
    if (!anchors.length) return;

    let openAnchor = null;

    function close() {
      if (!openAnchor) return;
      openAnchor.querySelector(".gui-tour-marker")?.classList.remove("is-active");
      openAnchor.querySelector(".gui-tour-pop")?.classList.remove("is-shown");
      openAnchor = null;
    }

    function open(anchor) {
      if (openAnchor === anchor) { close(); return; }
      close();
      anchor.querySelector(".gui-tour-marker")?.classList.add("is-active");
      anchor.querySelector(".gui-tour-pop")?.classList.add("is-shown");
      openAnchor = anchor;
    }

    anchors.forEach((anchor) => {
      const marker = anchor.querySelector(".gui-tour-marker");
      const pop    = anchor.querySelector(".gui-tour-pop");
      marker?.addEventListener("click", (e) => {
        e.stopPropagation();
        open(anchor);
      });
      /* Clicking inside the popover should not bubble up to the
       * document-level close handler. */
      pop?.addEventListener("click", (e) => e.stopPropagation());
    });

    /* Click anywhere else in the document (or in the tour but not
     * on a marker / popover) closes the open popover. */
    document.addEventListener("click", (e) => {
      if (!openAnchor) return;
      if (openAnchor.contains(e.target)) return;
      close();
    });

    /* Esc closes whichever popover is open. */
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && openAnchor) close();
    });
  });
}


/* ====================================================================
 * Tutorial scenes (tutorial.html, #scenes)
 *
 * State machine + per-scene animation players. Markup contract:
 *
 *   <div class="scene-stage" data-scenes>
 *     <ol class="scene-progress"><button data-scene-jump="N">...</ol>
 *     <button data-scene-prev>...</button>
 *     <button data-scene-next>...</button>
 *     <button data-scene-play>...</button>
 *     <button data-scene-replay>...</button>
 *     <span data-scene-counter>...</span>
 *     <article class="scene" data-scene="N" data-scene-key="...">
 *       <!-- mock(s) -->
 *     </article>
 *   </div>
 *
 * Each scene's player is keyed by the scene's data-scene attribute in
 * SCENE_PLAYERS. A play token guards against stale awaits: every new
 * activation increments the token, and async steps short-circuit when
 * their captured token no longer matches.
 *
 * Honours prefers-reduced-motion: skips the animation and jumps the
 * mock to its final state.
 * ================================================================== */

function initTutorialScenes() {
  const stage = document.querySelector("[data-scenes]");
  if (!stage) return;

  const scenes  = Array.from(stage.querySelectorAll(".scene[data-scene]"));
  const dots    = Array.from(stage.querySelectorAll("[data-scene-jump]"));
  const prevBtn = stage.querySelector("[data-scene-prev]");
  const nextBtn = stage.querySelector("[data-scene-next]");
  const playBtn = stage.querySelector("[data-scene-play]");
  const replayBtn = stage.querySelector("[data-scene-replay]");
  const counter = stage.querySelector("[data-scene-counter]");
  if (!scenes.length) return;

  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  let current = 0;
  /* Manual stepping is the default. Auto-advance is off so the
   * visitor reads each scene's explanation and clicks Next / Replay
   * at their own pace. Pressing Play turns it on. */
  let autoplay = false;
  let advanceTimer = null;
  let playToken = 0;

  /* ----------------- helpers ----------------- */

  function delay(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  /* Token-guarded await. Resolves immediately if `cancelled()` fires
   * during the wait so a stale player gives up its turn. */
  function pause(ms, cancelled) {
    return new Promise((resolve) => {
      const t = setTimeout(() => resolve(false), ms);
      const tick = setInterval(() => {
        if (cancelled()) { clearTimeout(t); clearInterval(tick); resolve(true); }
      }, 50);
      setTimeout(() => clearInterval(tick), ms + 60);
    });
  }

  async function typeInto(el, text, cancelled, perChar = 32) {
    el.textContent = "";
    el.classList.add("is-typing");
    for (let i = 1; i <= text.length; i++) {
      if (cancelled()) return;
      el.textContent = text.slice(0, i);
      await delay(perChar);
    }
    el.classList.remove("is-typing");
  }

  async function tweenInt(el, from, to, duration, cancelled) {
    const start = performance.now();
    return new Promise((resolve) => {
      function step(now) {
        if (cancelled()) { resolve(); return; }
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);   /* ease-out cubic */
        const v = Math.round(from + (to - from) * eased);
        el.textContent = String(v);
        if (t < 1) requestAnimationFrame(step);
        else resolve();
      }
      requestAnimationFrame(step);
    });
  }

  /* ----------------- per-scene reset + play ----------------- */

  function reset(sceneEl) {
    const idx = parseInt(sceneEl.dataset.scene, 10);
    const r = SCENE_RESETS[idx];
    if (r) r(sceneEl);
  }

  function playScene(sceneEl) {
    const idx = parseInt(sceneEl.dataset.scene, 10);
    const myToken = ++playToken;
    const cancelled = () => playToken !== myToken;
    const player = SCENE_PLAYERS[idx];
    if (!player) return Promise.resolve();
    return player(sceneEl, cancelled).catch(() => {});
  }

  const UNSET_GLYPH = "○";  /* ○ */
  const OK_GLYPH    = "✓";  /* ✓ */

  const SCENE_RESETS = {
    1(el) {
      const raw      = el.querySelector('[data-mock="raw"]');
      const bids     = el.querySelector('[data-mock="bids"]');
      const rawGlyph = el.querySelector('[data-mock="raw-glyph"]');
      const bidGlyph = el.querySelector('[data-mock="bids-glyph"]');
      const scan     = el.querySelector('[data-mock="scan-btn"]');
      if (raw)  { raw.textContent  = "";  raw.classList.remove("is-typing"); }
      if (bids) { bids.textContent = "";  bids.classList.remove("is-typing"); }
      if (rawGlyph) { rawGlyph.textContent = UNSET_GLYPH; rawGlyph.classList.remove("is-ok"); }
      if (bidGlyph) { bidGlyph.textContent = UNSET_GLYPH; bidGlyph.classList.remove("is-ok"); }
      if (scan) scan.classList.add("is-disabled");
    },
    2(el) {
      el.querySelector('[data-mock="spinner"]')?.classList.remove("is-spinning");
      const status = el.querySelector('[data-mock="status"]');
      if (status) status.textContent = "Idle";
      ["chip-valid","chip-warn","chip-err","chip-skip",
       "count-subj","count-series","count-dcm"]
        .forEach((k) => {
          const x = el.querySelector(`[data-mock="${k}"]`);
          if (x) x.textContent = "0";
        });
    },
    3(el) {
      el.querySelectorAll(".mock-row").forEach((r) => r.classList.remove("is-visible"));
    },
    4(el) {
      el.querySelectorAll(".mock-row").forEach((r) => r.classList.add("is-visible"));
      const cell      = el.querySelector('[data-mock="task-cell"]');
      const preview   = el.querySelector('[data-mock="preview-path"]');
      const basename  = el.querySelector('[data-mock="row-basename"]');
      const propsTask = el.querySelector('[data-mock="props-task"]');
      const propsEnt  = el.querySelector('[data-mock="props-task-ent"]');
      const propsPin  = el.querySelector('[data-mock="props-task-pin"]');
      if (cell)      { cell.textContent      = "sparse"; cell.classList.remove("is-editing"); }
      if (basename)   basename.textContent  = "sub-001_ses-pre_task-sparse_bold";
      if (preview)    preview.textContent   =
        "sub-001/ses-pre/func/sub-001_ses-pre_task-sparse_bold.nii.gz";
      if (propsTask)  propsTask.value       = "sparse";
      if (propsEnt)   propsEnt.textContent  = "task-sparse";
      if (propsPin)   propsPin.textContent  = "sparse";
    },
    5(el) {
      el.querySelectorAll(".mock-row").forEach((r) => r.classList.add("is-visible"));
      /* Selection state and bulk-edit values reset to 'pre'. */
      el.querySelectorAll('[data-mock="bulk-row"]')
        .forEach((r) => r.classList.remove("is-selected"));
      el.querySelectorAll('[data-mock="bulk-ses"]')
        .forEach((s) => { s.textContent = "pre"; });
      const bn1 = el.querySelector('[data-mock="bulk-bn-1"]');
      const bn2 = el.querySelector('[data-mock="bulk-bn-2"]');
      const bn3 = el.querySelector('[data-mock="bulk-bn-3"]');
      if (bn1) bn1.textContent = "sub-001_ses-pre_T1w";
      if (bn2) bn2.textContent = "sub-001_ses-pre_task-rest_bold";
      if (bn3) bn3.textContent = "sub-001_ses-pre_run-01_magnitude1";
      const dialog = el.querySelector('[data-mock="bulk-dialog"]');
      if (dialog) dialog.classList.remove("is-shown");
      const input = el.querySelector('[data-mock="bulk-input"]');
      if (input) { input.value = ""; input.classList.remove("is-typing"); }
      el.querySelector('[data-mock="bulk-btn"]')?.classList.remove("is-pressed");
      const propsSes = el.querySelector('[data-mock="bulk-props-ses"]');
      if (propsSes) propsSes.value = "pre";
    },
    6(el) {
      const counter = el.querySelector('[data-mock="conv-counter"]');
      if (counter) counter.textContent = "0";
      const status = el.querySelector('[data-mock="conv-status"]');
      if (status) status.textContent = "Converting...";
      const stage = el.querySelector('[data-mock="conv-stage"]');
      if (stage) stage.textContent = "BIDS 1.10.0 . converting series 0 / 21";
      el.querySelector('[data-mock="conv-spinner"]')?.classList.add("is-spinning");
      const log = el.querySelector('[data-mock="log"]');
      if (log) log.innerHTML = "";
    },
    7(el) {
      const form = el.querySelector('[data-mock="sidecar-form"]');
      if (form) form.innerHTML = "";
    },
    8(el) {
      /* Reset crosshair positions to centre. */
      el.querySelectorAll(".mock-crosshair").forEach((line) => {
        line.style.transform = "";
      });
    },
    9(el) {
      const list = el.querySelector('[data-mock="val-list"]');
      if (list) list.innerHTML = "";
      ["val-err","val-warn","val-hint"].forEach((k) => {
        const x = el.querySelector(`[data-mock="${k}"]`);
        if (x) x.textContent = "0";
      });
      const summary = el.querySelector('[data-mock="val-summary"]');
      if (summary) summary.textContent = "Ready";
      el.querySelector('[data-mock="val-spinner"]')?.classList.remove("is-spinning");
    },
  };

  const SCENE_PLAYERS = {
    /* ---------- Scene 1. Pick folders. ---------- */
    async 1(el, cancelled) {
      const raw      = el.querySelector('[data-mock="raw"]');
      const bids     = el.querySelector('[data-mock="bids"]');
      const rawGlyph = el.querySelector('[data-mock="raw-glyph"]');
      const bidGlyph = el.querySelector('[data-mock="bids-glyph"]');
      const scan     = el.querySelector('[data-mock="scan-btn"]');
      if (!raw || !bids) return;
      if (reducedMotion) {
        raw.textContent  = "~/Downloads/neuroimaging_unit_new";
        bids.textContent = "~/Documents/bids_export";
        if (rawGlyph) { rawGlyph.textContent = OK_GLYPH; rawGlyph.classList.add("is-ok"); }
        if (bidGlyph) { bidGlyph.textContent = OK_GLYPH; bidGlyph.classList.add("is-ok"); }
        scan?.classList.remove("is-disabled");
        return;
      }
      await delay(280);
      if (cancelled()) return;
      await typeInto(raw,  "~/Downloads/neuroimaging_unit_new", cancelled, 28);
      if (cancelled()) return;
      if (rawGlyph) { rawGlyph.textContent = OK_GLYPH; rawGlyph.classList.add("is-ok"); }
      await delay(400);
      if (cancelled()) return;
      await typeInto(bids, "~/Documents/bids_export",           cancelled, 28);
      if (cancelled()) return;
      if (bidGlyph) { bidGlyph.textContent = OK_GLYPH; bidGlyph.classList.add("is-ok"); }
      scan?.classList.remove("is-disabled");
    },

    /* ---------- Scene 2. Run a scan. ----------
     * Chip targets match what bidsmgr-scan would produce on the
     * example dataset: 30 valid, 1 warning, 0 error, 6 skipped. */
    async 2(el, cancelled) {
      const spinner = el.querySelector('[data-mock="spinner"]');
      const status  = el.querySelector('[data-mock="status"]');
      const valid   = el.querySelector('[data-mock="chip-valid"]');
      const warn    = el.querySelector('[data-mock="chip-warn"]');
      const err     = el.querySelector('[data-mock="chip-err"]');
      const skip    = el.querySelector('[data-mock="chip-skip"]');
      const subj    = el.querySelector('[data-mock="count-subj"]');
      const series  = el.querySelector('[data-mock="count-series"]');
      const dcm     = el.querySelector('[data-mock="count-dcm"]');

      /* Real bidsmgr-scan counts on this dataset:
       *   inventory rows: 33
       *   keepers (include=1): 21
       *   dropped (always-exclude pattern): 12
       *   warnings / errors at scan time: 0 / 0
       *   subjects clustered: 2 (sub-001 spans 2 sessions, sub-002 1)
       *   DICOM files walked: 394 */
      if (reducedMotion) {
        if (status) status.textContent = "Done.";
        if (valid)  valid.textContent  = "21";
        if (warn)   warn.textContent   = "0";
        if (err)    err.textContent    = "0";
        if (skip)   skip.textContent   = "12";
        if (subj)   subj.textContent   = "2";
        if (series) series.textContent = "33";
        if (dcm)    dcm.textContent    = "394";
        return;
      }

      spinner?.classList.add("is-spinning");
      const messages = [
        "Walking ~/Downloads/neuroimaging_unit_new...",
        "Found 394 DICOMs across 3 folders",
        "Clustering folders by PatientID...",
        "Reading SeriesInstanceUID for every series...",
        "Stamping bids_guess_* entities from SeriesDescription...",
        "Done.",
      ];
      for (const msg of messages) {
        if (cancelled()) return;
        if (status) status.textContent = msg;
        if (msg.startsWith("Found")) {
          await tweenInt(dcm, 0, 394, 900, cancelled);
        } else if (msg.startsWith("Clustering")) {
          await tweenInt(subj, 0, 2, 600, cancelled);
        } else if (msg.startsWith("Reading")) {
          await tweenInt(series, 0, 33, 700, cancelled);
        }
        await delay(700);
      }
      if (cancelled()) return;
      spinner?.classList.remove("is-spinning");
      await Promise.all([
        tweenInt(valid, 0, 21, 800, cancelled),
        tweenInt(warn,  0,  0, 200, cancelled),
        tweenInt(err,   0,  0, 200, cancelled),
        tweenInt(skip,  0, 12, 700, cancelled),
      ]);
    },

    /* ---------- Scene 3. Inspect the inventory table. ---------- */
    async 3(el, cancelled) {
      const rows = Array.from(el.querySelectorAll(".mock-row"));
      if (reducedMotion) {
        rows.forEach((r) => r.classList.add("is-visible"));
        return;
      }
      for (const r of rows) {
        if (cancelled()) return;
        r.classList.add("is-visible");
        await delay(60);
      }
    },

    /* ---------- Scene 4. Override a row inline.
     * Animates the task cell from 'sparse' -> '' -> 'motor'. The
     * properties pane's task input, the predicted-path preview, the
     * row's basename, and the BIDS preview strip all update in step
     * (everything stays consistent like in the real GUI). */
    async 4(el, cancelled) {
      const cell      = el.querySelector('[data-mock="task-cell"]');
      const basename  = el.querySelector('[data-mock="row-basename"]');
      const preview   = el.querySelector('[data-mock="preview-path"]');
      const propsTask = el.querySelector('[data-mock="props-task"]');
      const propsEnt  = el.querySelector('[data-mock="props-task-ent"]');
      const propsPin  = el.querySelector('[data-mock="props-task-pin"]');
      if (!cell) return;

      function setTask(task) {
        const display = task || "...";
        const bn      = `sub-001_ses-pre_task-${display}_bold`;
        if (basename)  basename.textContent  = bn;
        if (preview)   preview.textContent   = `sub-001/ses-pre/func/${bn}.nii.gz`;
        if (propsTask) propsTask.value       = task;
        if (propsEnt)  propsEnt.textContent  = `task-${display}`;
        if (propsPin)  propsPin.textContent  = display;
      }

      if (reducedMotion) {
        cell.textContent = "motor";
        setTask("motor");
        return;
      }

      await delay(500);
      if (cancelled()) return;
      cell.classList.add("is-editing");
      await delay(500);
      if (cancelled()) return;
      for (let i = "sparse".length; i > 0; i--) {
        if (cancelled()) return;
        cell.textContent = "sparse".slice(0, i - 1);
        setTask(cell.textContent);
        await delay(60);
      }
      await delay(200);
      if (cancelled()) return;
      const target = "motor";
      for (let i = 1; i <= target.length; i++) {
        if (cancelled()) return;
        cell.textContent = target.slice(0, i);
        setTask(cell.textContent);
        await delay(90);
      }
      await delay(400);
      if (cancelled()) return;
      cell.classList.remove("is-editing");
    },

    /* ---------- Scene 5. Bulk-edit across rows.
     * Selects 3 OL_0001 rows, opens the Bulk-edit dialog, types
     * 'baseline' as the new session, and applies. */
    async 5(el, cancelled) {
      const rows    = Array.from(el.querySelectorAll('[data-mock="bulk-row"]'));
      const button  = el.querySelector('[data-mock="bulk-btn"]');
      const dialog  = el.querySelector('[data-mock="bulk-dialog"]');
      const input   = el.querySelector('[data-mock="bulk-input"]');
      const sesEls  = Array.from(el.querySelectorAll('[data-mock="bulk-ses"]'));
      const bn1 = el.querySelector('[data-mock="bulk-bn-1"]');
      const bn2 = el.querySelector('[data-mock="bulk-bn-2"]');
      const bn3 = el.querySelector('[data-mock="bulk-bn-3"]');

      const propsSes = el.querySelector('[data-mock="bulk-props-ses"]');

      function applySession(value) {
        sesEls.forEach((s) => { s.textContent = value; });
        if (bn1) bn1.textContent = `sub-001_ses-${value}_T1w`;
        if (bn2) bn2.textContent = `sub-001_ses-${value}_task-rest_bold`;
        if (bn3) bn3.textContent = `sub-001_ses-${value}_run-01_magnitude1`;
        if (propsSes) propsSes.value = value;
      }

      if (reducedMotion) {
        rows.forEach((r) => r.classList.add("is-selected"));
        applySession("baseline");
        return;
      }

      await delay(400);
      if (cancelled()) return;
      /* Multi-select rows one at a time (shift-click feel). */
      for (const r of rows) {
        if (cancelled()) return;
        r.classList.add("is-selected");
        await delay(280);
      }
      await delay(300);
      if (cancelled()) return;
      button?.classList.add("is-pressed");
      await delay(180);
      button?.classList.remove("is-pressed");
      dialog?.classList.add("is-shown");
      await delay(400);
      if (cancelled()) return;
      if (input) {
        input.classList.add("is-typing");
        input.focus({ preventScroll: true });
        const target = "baseline";
        for (let i = 1; i <= target.length; i++) {
          if (cancelled()) return;
          input.value = target.slice(0, i);
          await delay(70);
        }
        input.classList.remove("is-typing");
      }
      await delay(450);
      if (cancelled()) return;
      /* Apply: all 3 session cells flip to 'baseline'. */
      applySession("baseline");
      await delay(250);
      dialog?.classList.remove("is-shown");
    },

    /* ---------- Scene 6. Run the conversion.
     * Identical to the real GUI's conversion flow: no fake per-subject
     * progress bars (the real app doesn't have them yet). Instead the
     * spinner spins, the toolbar status text streams, the Log dock tab
     * scrolls through realistic engine output, and a counter ticks up
     * in the Properties pane + status bar. */
    async 6(el, cancelled) {
      const counter = el.querySelector('[data-mock="conv-counter"]');
      const status  = el.querySelector('[data-mock="conv-status"]');
      const stage   = el.querySelector('[data-mock="conv-stage"]');
      const spinner = el.querySelector('[data-mock="conv-spinner"]');
      const log     = el.querySelector('[data-mock="log"]');

      /* Real `bidsmgr-convert -v` output on this dataset, condensed.
       * 21 keeper rows total (33 inventory rows - 12 always-excluded
       * scout / Phoenix SR). Counter target is 21 by the end. */
      const LOG = [
        ["scan",  "bidsmgr 1.0.1 . platform=darwin py=3.10.11",                                 0],
        ["scan",  "in-memory rebuild reconciled 15 rows from entities JSON",                    0],
        ["stage", "[sub-001] staging at /tmp/.tmp_bidsmgr/sub-001/",                            0],
        ["stage", "[sub-001/ses-pre] dcm2niix: anat/sub-001_ses-pre_acq-tfl3p2_T1w.nii.gz",     1],
        ["stage", "[sub-001/ses-pre] dcm2niix: func/sub-001_ses-pre_task-rest_bold.nii.gz",     1],
        ["stage", "[sub-001/ses-pre] dcm2niix: func/sub-001_ses-pre_task-sparse_bold.nii.gz",   1],
        ["stage", "[sub-001/ses-pre] dcm2niix: fmap/sub-001_ses-pre_acq-fm2_run-1_magnitude1",  1],
        ["stage", "[sub-001/ses-pre] dcm2niix: fmap/sub-001_ses-pre_acq-fm2_run-1_phase2",      1],
        ["stage", "[sub-001/ses-pre] dcm2niix: fmap/sub-001_ses-pre_acq-fm2_run-2_magnitude1",  1],
        ["stage", "[sub-001/ses-pre] dcm2niix: fmap/sub-001_ses-pre_acq-fm2_run-2_phase2",      1],
        ["stage", "[sub-001/ses-post] dcm2niix: func/sub-001_ses-post_task-mb_sbref.nii.gz",    1],
        ["stage", "[sub-001/ses-post] dcm2niix: func/sub-001_ses-post_task-mb_bold.nii.gz",     1],
        ["stage", "[sub-001/ses-post] physio: func/sub-001_ses-post_task-mb_physio.tsv.gz",     1],
        ["stage", "[sub-001/ses-post] dcm2niix: fmap/sub-001_ses-post_acq-fm2_magnitude1",      1],
        ["stage", "[sub-001/ses-post] dcm2niix: fmap/sub-001_ses-post_acq-fm2_phase2",          1],
        ["fixup", "fmap rename: _e1 -> _magnitude1, _e2 -> _magnitude2, _e2_ph -> _phase2  [18 renames]", 0],
        ["fixup", "IntendedFor: wrote 1 entries into sub-001_ses-post_acq-fm2_{magnitude1,magnitude2,phase2}.json", 0],
        ["fixup", "IntendedFor: wrote 2 entries into sub-001_ses-pre_acq-fm2_run-{1,2}_{magnitude1,magnitude2,phase2}.json", 0],
        ["done",  "committed sub-001 to bids_export/neuroimaging_unit_new/sub-001",             0],
        ["stage", "[sub-002] staging at /tmp/.tmp_bidsmgr/sub-002/",                            0],
        ["stage", "[sub-002] dcm2niix: anat/sub-002_acq-space_T2w.nii.gz",                      1],
        ["stage", "[sub-002] dcm2niix: func/sub-002_task-dmaging_run-1_bold.nii.gz",            2],
        ["stage", "[sub-002] dcm2niix: func/sub-002_task-dmaging_run-2_bold.nii.gz",            2],
        ["stage", "[sub-002] dcm2niix: func/sub-002_task-uebung_bold.nii.gz",                   2],
        ["stage", "[sub-002] physio: 2 PhysioLog series (Saving physio data x2)",               0],
        ["stage", "[sub-002] dcm2niix: dwi/sub-002_acq-epse2_dir-AP_dwi.nii.gz  (+ .bval / .bvec)", 1],
        ["fixup", "classifier: acq-15_dir-PA b0 rerouted to fmap/_epi",                         0],
        ["fixup", "IntendedFor: wrote 3 entries into sub-002_acq-epse2_dir-AP_epi.json",        0],
        ["done",  "committed sub-002 to bids_export/neuroimaging_unit_new/sub-002",             0],
        ["done",  "21 series -> BIDS . validate to see 6 missing TaskName errors",              0],
      ];

      function appendLine(tag, msg) {
        if (!log) return;
        const line = document.createElement("span");
        line.className = `mock-log-line log-tag-${tag}`;
        line.textContent = msg + "\n";
        log.appendChild(line);
        log.scrollTop = log.scrollHeight;
      }

      if (reducedMotion) {
        if (status)  status.textContent  = "Done.";
        if (counter) counter.textContent = "21";
        if (stage)   stage.textContent   = "BIDS 1.10.0 . converted 21 / 21 series";
        spinner?.classList.remove("is-spinning");
        LOG.forEach(([t, m]) => appendLine(t, m));
        return;
      }

      spinner?.classList.add("is-spinning");
      let done = 0;
      for (const [tag, msg, delta] of LOG) {
        if (cancelled()) return;
        appendLine(tag, msg);
        done += delta;
        if (counter) counter.textContent = String(done);
        if (stage)   stage.textContent   = done < 30
          ? `BIDS 1.10.0 . converting series ${done} / 21`
          : "BIDS 1.10.0 . converted 21 / 21 series";
        if (status) {
          if      (tag === "stage") status.textContent = "Running dcm2niix...";
          else if (tag === "fixup") status.textContent = "Cross-file fixups...";
          else if (tag === "warn")  status.textContent = "Warning logged";
          else if (tag === "done"  && done >= 21) status.textContent = "Done.";
        }
        await delay(310);
      }
      if (cancelled()) return;
      spinner?.classList.remove("is-spinning");
    },

    /* ---------- Scene 7. Open the result in the Editor.
     * Streams the schema-aware sidecar form rows for the OL_0001
     * T1w.json. Each row carries its kind (req / rec / opt / dep)
     * which colors the 4-px stripe on the left, mirroring the real
     * SidecarFormPane. Value-type also matters: str vs num drives
     * the syntax-coloured value styling. */
    async 7(el, cancelled) {
      const form = el.querySelector('[data-mock="sidecar-form"]');
      if (!form) return;
      /* Real-ish content from the OL_0001 T1w.json. The 'kind'
       * mirrors the BIDS schema's level field; the 'type' picks the
       * .val.str / .val.num class. */
      const ROWS = [
        ["Modality",                "MR",                       "req", "str"],
        ["MagneticFieldStrength",   "3",                        "rec", "num"],
        ["Manufacturer",            "Siemens Healthineers",     "rec", "str"],
        ["ManufacturersModelName",  "MAGNETOM Prisma",          "rec", "str"],
        ["InstitutionName",         "University of Oldenburg",  "rec", "str"],
        ["DeviceSerialNumber",      "66080",                    "rec", "str"],
        ["SoftwareVersions",        "syngo MR XA31A",           "rec", "str"],
        ["BodyPartExamined",        "BRAIN",                    "rec", "str"],
        ["ScanningSequence",        "GR\\IR",                   "rec", "str"],
        ["SequenceVariant",         "SK\\SP\\MP",               "rec", "str"],
        ["EchoTime",                "0.00237",                  "rec", "num"],
        ["InversionTime",           "0.9",                      "rec", "num"],
        ["FlipAngle",               "8",                        "rec", "num"],
        ["RepetitionTime",          "2.3",                      "rec", "num"],
        ["PhaseEncodingDirection",  "j-",                       "opt", "str"],
        ["AcquisitionDateTime",     "2025-05-26T07:16:29",      "opt", "str"],
        ["AcquisitionDuration",     "300",                      "dep", "num"],
      ];
      form.innerHTML = "";
      const drop = (k, v, kind, type) => {
        const row = document.createElement("div");
        row.className = `sc-field ${kind}`;
        row.innerHTML = `
          <span class="req-mark" aria-hidden="true"></span>
          <span class="key">"${k}"</span>
          <span class="val ${type}">${escapeHtml(v)}</span>
        `;
        form.appendChild(row);
      };

      if (reducedMotion) {
        ROWS.forEach(([k, v, kind, type]) => drop(k, v, kind, type));
        return;
      }
      for (const [k, v, kind, type] of ROWS) {
        if (cancelled()) return;
        drop(k, v, kind, type);
        await delay(100);
      }
    },

    /* ---------- Scene 8. Inspect a NIfTI tri-view.
     * Sweeps the shared crosshair so each tile's lines move in
     * concert, mimicking the synced cursor in the real viewer. */
    async 8(el, cancelled) {
      const tiles = Array.from(el.querySelectorAll(".mock-nifti-tile"));
      if (reducedMotion || !tiles.length) return;

      const start = performance.now();
      const DURATION = 7600;
      return new Promise((resolve) => {
        function step(now) {
          if (cancelled()) { resolve(); return; }
          const t = ((now - start) % DURATION) / DURATION;
          /* Smooth back-and-forth across the brain, 12 px max range. */
          const dx = Math.sin(t * Math.PI * 2) * 12;
          const dy = Math.cos(t * Math.PI * 2) * 8;
          tiles.forEach((tile) => {
            const lines = tile.querySelectorAll(".mock-crosshair");
            if (lines[0]) lines[0].setAttribute("transform", `translate(${dx} 0)`);
            if (lines[1]) lines[1].setAttribute("transform", `translate(0 ${dy})`);
          });
          /* Run for one full cycle as the scene's "play" duration. */
          if (now - start < DURATION) requestAnimationFrame(step);
          else resolve();
        }
        requestAnimationFrame(step);
      });
    },

    /* ---------- Scene 9. Validate the dataset.
     * Spinner + 'Validating...' for a beat; then severity chips tween
     * to 0 errors / 1 warning / 2 hints, and three issue rows appear
     * one at a time matching what bidsmgr-validate emits on this
     * specific dataset. */
    async 9(el, cancelled) {
      const btn      = el.querySelector('[data-mock="validate-btn"]');
      const spinner  = el.querySelector('[data-mock="val-spinner"]');
      const summary  = el.querySelector('[data-mock="val-summary"]');
      const errEl    = el.querySelector('[data-mock="val-err"]');
      const warnEl   = el.querySelector('[data-mock="val-warn"]');
      const hintEl   = el.querySelector('[data-mock="val-hint"]');
      const list     = el.querySelector('[data-mock="val-list"]');

      /* Real validate.log output: 6 errors total, one per task BOLD
       * sidecar (all six are missing the required TaskName field).
       * Each file also misses 4 recommended fields (Instructions,
       * TaskDescription, CogAtlasID, CogPOID) but those don't get
       * promoted to errors in non-strict mode. The list below
       * shows the representative samples; the chip count uses 6. */
      const ISSUES = [
        { sev: "err", icon: "✕",
          title: "sub-001_ses-pre_task-rest_bold.json: missing required TaskName",
          desc:  "<code>bids.required_sidecar_field_missing</code>. The BIDS schema requires <code>TaskName</code> on every BOLD sidecar. Click the row to open the file; the Editor's auto-fill button will set it from the BIDS task entity.",
          target: "sub-001/ses-pre/func/" },
        { sev: "err", icon: "✕",
          title: "sub-001_ses-pre_task-sparse_bold.json: missing required TaskName",
          desc:  "<code>bids.required_sidecar_field_missing</code>. Same fix path: open the sidecar, click <em>Auto-fill</em>.",
          target: "sub-001/ses-pre/func/" },
        { sev: "err", icon: "✕",
          title: "sub-001_ses-post_task-mb_bold.json: missing required TaskName",
          desc:  "<code>bids.required_sidecar_field_missing</code>. The session-post multiband task fails the same rule.",
          target: "sub-001/ses-post/func/" },
        { sev: "err", icon: "✕",
          title: "sub-002_task-dmaging_run-1_bold.json: missing required TaskName",
          desc:  "<code>bids.required_sidecar_field_missing</code>. The two dmaging runs and the uebung task all share this finding.",
          target: "sub-002/func/" },
        { sev: "err", icon: "✕",
          title: "sub-002_task-dmaging_run-2_bold.json: missing required TaskName",
          desc:  "<code>bids.required_sidecar_field_missing</code>.",
          target: "sub-002/func/" },
        { sev: "err", icon: "✕",
          title: "sub-002_task-uebung_bold.json: missing required TaskName",
          desc:  "<code>bids.required_sidecar_field_missing</code>.",
          target: "sub-002/func/" },
      ];

      function addIssue(it) {
        const li = document.createElement("li");
        li.className = "mock-val-row";
        li.setAttribute("data-sev", it.sev);
        li.innerHTML = `
          <span class="mock-val-icon">${it.icon}</span>
          <div>
            <div class="mock-val-title">${escapeHtml(it.title)}</div>
            <div class="mock-val-desc">${it.desc}</div>
          </div>
          <span class="mock-val-target">${escapeHtml(it.target)}</span>
        `;
        list.appendChild(li);
        requestAnimationFrame(() => li.classList.add("is-visible"));
      }

      if (reducedMotion) {
        if (errEl)   errEl.textContent   = "6";
        if (warnEl)  warnEl.textContent  = "0";
        if (hintEl)  hintEl.textContent  = "0";
        if (summary) summary.textContent = "6 errors";
        spinner?.classList.remove("is-spinning");
        if (list) { list.innerHTML = ""; ISSUES.forEach(addIssue); }
        return;
      }

      btn?.classList.add("is-pressed");
      spinner?.classList.add("is-spinning");
      if (summary) summary.textContent = "Validating dataset...";
      await delay(900);
      if (cancelled()) return;

      btn?.classList.remove("is-pressed");
      if (summary) summary.textContent = "6 errors";
      await Promise.all([
        tweenInt(errEl,  0, 6, 800, cancelled),
        tweenInt(warnEl, 0, 0, 200, cancelled),
        tweenInt(hintEl, 0, 0, 200, cancelled),
      ]);
      spinner?.classList.remove("is-spinning");
      if (!list) return;
      list.innerHTML = "";
      for (const it of ISSUES) {
        if (cancelled()) return;
        addIssue(it);
        await delay(420);
      }
    },
  };

  /* Minimal HTML escape for log lines (text content uses textContent
   * elsewhere; the bulk reduced-motion path uses innerHTML). */
  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }

  /* ----------------- activation + navigation ----------------- */

  function activate(idx, opts = {}) {
    if (idx < 0 || idx >= scenes.length) return;
    current = idx;
    scenes.forEach((s, i) => {
      if (i === idx) s.setAttribute("data-active", "");
      else           s.removeAttribute("data-active");
    });
    dots.forEach((d) => {
      const target = parseInt(d.dataset.sceneJump, 10) - 1;
      const on = target === idx;
      d.classList.toggle("is-active", on);
      d.setAttribute("aria-selected", String(on));
    });
    if (counter) {
      const strong = counter.querySelector("strong");
      if (strong) strong.textContent = String(idx + 1);
    }
    if (prevBtn) prevBtn.disabled = idx === 0;
    if (nextBtn) nextBtn.disabled = idx === scenes.length - 1;

    reset(scenes[idx]);
    cancelAdvance();
    if (!opts.silent) {
      playScene(scenes[idx]).then(() => {
        if (autoplay && current === idx && idx < scenes.length - 1) {
          advanceTimer = setTimeout(() => activate(idx + 1), 2400);
        }
      });
    }
  }

  function cancelAdvance() {
    if (advanceTimer) { clearTimeout(advanceTimer); advanceTimer = null; }
  }

  function setAutoplay(on) {
    autoplay = on;
    if (playBtn) playBtn.textContent = on ? "Pause" : "Play";
    if (!on) cancelAdvance();
  }

  /* --- wire controls --- */
  dots.forEach((d) => {
    d.addEventListener("click", () => {
      if (d.classList.contains("is-locked")) return;
      const target = parseInt(d.dataset.sceneJump, 10) - 1;
      activate(target);
    });
  });
  prevBtn?.addEventListener("click", () => activate(current - 1));
  nextBtn?.addEventListener("click", () => activate(current + 1));
  playBtn?.addEventListener("click", () => {
    setAutoplay(!autoplay);
    if (autoplay) activate(current);  // restart current animation
  });
  replayBtn?.addEventListener("click", () => activate(current));

  /* Keyboard: left / right arrows step scenes when focus is in the
   * scene stage. */
  stage.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (e.key === "ArrowLeft")  { activate(current - 1); }
    if (e.key === "ArrowRight") { activate(current + 1); }
  });

  /* Defer the first play until the scenes section enters the
   * viewport, so visitors don't burn animation cycles offscreen. */
  if ("IntersectionObserver" in window) {
    let started = false;
    const io = new IntersectionObserver((entries) => {
      if (started) return;
      entries.forEach((e) => {
        if (e.isIntersecting) {
          started = true;
          activate(0);
          io.disconnect();
        }
      });
    }, { threshold: 0.18 });
    io.observe(stage);
  } else {
    activate(0);
  }

  setAutoplay(false);   /* manual stepping by default */
}


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

  /* Real CLI output: OL_0001 + OL_0002 cluster as sub-001 (same
   * PatientID, two sessions), OL_0003 stands alone as sub-002.
   * Basenames are verbatim from `bidsmgr-convert` on this dataset. */
  const SERIES = {
    OL_0001: [
      { no: 1,  desc: "localizer_20ch_head-coil",    files: 2,  type: "scout",
        skipped: true,
        what: "Three-plane scout used by the operator to align the rest of the protocol. BIDS Manager auto-excludes the row from conversion; the classifier confidence is 0.0 (always-exclude pattern)." },
      { no: 2,  desc: "ses-pre_run-01_fmap",         files: 2,  type: "fmap",
        what: "Fieldmap magnitude image, run 01. Pairs with series 3 (phase) for distortion correction. The classifier assigns acq-fm2 + run-1 + magnitude1 entities automatically (confidence 0.85).",
        bids: "sub-001/ses-pre/fmap/sub-001_ses-pre_acq-fm2_run-1_magnitude1.nii.gz" },
      { no: 3,  desc: "ses-pre_run-01_fmap",         files: 1,  type: "fmap",
        what: "Fieldmap phase image, run 01. The fmap fix-up stage in convert renames the second echo's _ph file to _phase2.",
        bids: "sub-001/ses-pre/fmap/sub-001_ses-pre_acq-fm2_run-1_phase2.nii.gz" },
      { no: 4,  desc: "ses-pre_task-sparse_bold",    files: 10, type: "func",
        what: "Task fMRI. The 'sparse' label in SeriesDescription becomes the BIDS task entity. Classifier confidence is 0.4 because 'sparse' is a free-text task name; you can confirm or rename inline in Scene 4.",
        bids: "sub-001/ses-pre/func/sub-001_ses-pre_task-sparse_bold.nii.gz" },
      { no: 6,  desc: "ses-pre_T1w",                 files: 1,  type: "anat",
        what: "T1-weighted anatomical reference. The classifier adds acq-tfl3p2 from the sequence dictionary so the BIDS basename carries the protocol fingerprint.",
        bids: "sub-001/ses-pre/anat/sub-001_ses-pre_acq-tfl3p2_T1w.nii.gz" },
      { no: 7,  desc: "ses-pre_run-02_fmap",         files: 2,  type: "fmap",
        what: "Second fieldmap magnitude, run 02. IntendedFor lists the rest-BOLD acquired right after; the convert log shows '2 entries' for this run.",
        bids: "sub-001/ses-pre/fmap/sub-001_ses-pre_acq-fm2_run-2_magnitude1.nii.gz" },
      { no: 8,  desc: "ses-pre_run-02_fmap",         files: 1,  type: "fmap",
        what: "Second fieldmap phase, run 02.",
        bids: "sub-001/ses-pre/fmap/sub-001_ses-pre_acq-fm2_run-2_phase2.nii.gz" },
      { no: 9,  desc: "ses-pre_task-rest_bold",      files: 20, type: "func",
        what: "Resting-state BOLD, 20 volumes. The run-02 fmap pair is auto-attached via IntendedFor in the fixups stage.",
        bids: "sub-001/ses-pre/func/sub-001_ses-pre_task-rest_bold.nii.gz" },
      { no: 99, desc: "PhoenixZIPReport",            files: 6,  type: "sr",
        skipped: true,
        what: "Siemens scanner metadata report (SR DICOM, not image data). Always-excluded by the classifier." },
    ],
    OL_0002: [
      { no: 1, desc: "AAHead_Scout_64ch-head-coil",         files: 1, type: "scout",
        skipped: true, what: "Scout / localizer. Always-excluded." },
      { no: 2, desc: "AAHead_Scout_64ch-head-coil_MPR_sag", files: 1, type: "scout",
        skipped: true, what: "Sagittal MPR resample from the scout. Always-excluded." },
      { no: 3, desc: "AAHead_Scout_64ch-head-coil_MPR_cor", files: 1, type: "scout",
        skipped: true, what: "Coronal MPR resample from the scout. Always-excluded." },
      { no: 4, desc: "AAHead_Scout_64ch-head-coil_MPR_tra", files: 1, type: "scout",
        skipped: true, what: "Transverse MPR resample from the scout. Always-excluded." },
      { no: 5, desc: "ses-post_run-01_fmap",                files: 2, type: "fmap",
        what: "Fieldmap magnitude, run 01. Same patient as OL_0001 so this row lands under sub-001 / ses-post (clustered by PatientID).",
        bids: "sub-001/ses-post/fmap/sub-001_ses-post_acq-fm2_magnitude1.nii.gz" },
      { no: 6, desc: "ses-post_run-01_fmap",                files: 1, type: "fmap",
        what: "Fieldmap phase, run 01.",
        bids: "sub-001/ses-post/fmap/sub-001_ses-post_acq-fm2_phase2.nii.gz" },
      { no: 7, desc: "ses-post_task-mb_bold_SBRef",         files: 1, type: "func",
        what: "Single-band reference for the multiband BOLD that follows. Classifier maps it to _sbref.",
        bids: "sub-001/ses-post/func/sub-001_ses-post_task-mb_sbref.nii.gz" },
      { no: 8, desc: "ses-post_task-mb_bold",               files: 50, type: "func",
        what: "Multiband BOLD task. 50 volumes. The fmap_run-01 pair is auto-attached via IntendedFor.",
        bids: "sub-001/ses-post/func/sub-001_ses-post_task-mb_bold.nii.gz" },
      { no: 10, desc: "ses-post_task-mb_bold_PhysioLog",    files: 1, type: "physio",
        what: "Siemens physio log. The PhysioDcmBackend (vendored bidsphysio) parses it into BIDS-compliant _physio.tsv.gz + .json. The convert log prints 'Saving physio data' per series.",
        bids: "sub-001/ses-post/func/sub-001_ses-post_task-mb_physio.tsv.gz" },
      { no: 99, desc: "PhoenixZIPReport",                   files: 3, type: "sr",
        skipped: true, what: "Siemens metadata SR. Always-excluded." },
    ],
    OL_0003: [
      { no: 1,  desc: "AAHead_Scout_64ch-head-coil",         files: 1,   type: "scout",
        skipped: true, what: "Scout. Always-excluded." },
      { no: 2,  desc: "AAHead_Scout_64ch-head-coil_MPR_sag", files: 1,   type: "scout",
        skipped: true, what: "Sagittal MPR resample. Always-excluded." },
      { no: 3,  desc: "AAHead_Scout_64ch-head-coil_MPR_cor", files: 1,   type: "scout",
        skipped: true, what: "Coronal MPR resample. Always-excluded." },
      { no: 4,  desc: "AAHead_Scout_64ch-head-coil_MPR_tra", files: 1,   type: "scout",
        skipped: true, what: "Transverse MPR resample. Always-excluded." },
      { no: 5,  desc: "acq-space_T2w",                        files: 1,   type: "anat",
        what: "T2-weighted anatomical (SPACE sequence). The acq-space label is parsed straight from the SeriesDescription.",
        bids: "sub-002/anat/sub-002_acq-space_T2w.nii.gz" },
      { no: 6,  desc: "task-dmaging_run-01_bold_SBRef",       files: 1,   type: "func",
        what: "SBRef for run 01 of the dmaging task.",
        bids: "sub-002/func/sub-002_task-dmaging_run-1_sbref.nii.gz" },
      { no: 7,  desc: "task-dmaging_run-01_bold",             files: 50,  type: "func",
        what: "Multiband BOLD, dmaging task, run 01. Confidence is 0.4 because 'dmaging' is a free-text task name worth reviewing.",
        bids: "sub-002/func/sub-002_task-dmaging_run-1_bold.nii.gz" },
      { no: 9,  desc: "task-dmaging_run-01_bold_PhysioLog",   files: 1,   type: "physio",
        what: "Physio log for run 01.",
        bids: "sub-002/func/sub-002_task-dmaging_run-1_physio.tsv.gz" },
      { no: 10, desc: "task-dmaging_run-02_bold_SBRef",       files: 1,   type: "func",
        what: "SBRef for run 02.",
        bids: "sub-002/func/sub-002_task-dmaging_run-2_sbref.nii.gz" },
      { no: 11, desc: "task-dmaging_run-02_bold",             files: 50,  type: "func",
        what: "Multiband BOLD, dmaging task, run 02.",
        bids: "sub-002/func/sub-002_task-dmaging_run-2_bold.nii.gz" },
      { no: 13, desc: "task-dmaging_run-02_bold_PhysioLog",   files: 1,   type: "physio",
        what: "Physio log for run 02.",
        bids: "sub-002/func/sub-002_task-dmaging_run-2_physio.tsv.gz" },
      { no: 14, desc: "task-uebung_bold_SBRef",               files: 1,   type: "func",
        what: "SBRef for the practice (uebung) task.",
        bids: "sub-002/func/sub-002_task-uebung_sbref.nii.gz" },
      { no: 15, desc: "task-uebung_bold",                     files: 50,  type: "func",
        what: "Multiband BOLD, practice task.",
        bids: "sub-002/func/sub-002_task-uebung_bold.nii.gz" },
      { no: 17, desc: "acq-15_dir-ap_dwi",                    files: 117, type: "dwi",
        what: "Diffusion-weighted imaging, anterior-to-posterior phase-encoding, 15 directions plus b=0 frames. 117 DICOMs in one series; the converter writes the matched .bval / .bvec files alongside the NIfTI.",
        bids: "sub-002/dwi/sub-002_acq-epse2_dir-AP_dwi.nii.gz" },
      { no: 18, desc: "acq-15b0_dir-ap_dwi",                  files: 1,   type: "dwi",
        what: "b=0 AP acquisition. Stays in dwi/ as a reference volume.",
        bids: "sub-002/dwi/sub-002_acq-epse2b0_dir-AP_dwi.nii.gz" },
      { no: 19, desc: "acq-15_dir-pa_dwi",                    files: 1,   type: "dwi",
        what: "b=0 PA acquisition. The classifier reroutes this to fmap/_epi: a PA b=0 in a DWI block is the standard distortion reference. The convert log shows the reroute under 'rerouted to fmap/epi'.",
        bids: "sub-002/fmap/sub-002_acq-epse2_dir-AP_epi.nii.gz" },
      { no: 99, desc: "PhoenixZIPReport",                     files: 8,   type: "sr",
        skipped: true, what: "Siemens metadata SR. Always-excluded." },
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


