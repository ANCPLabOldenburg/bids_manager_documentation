/* The home page hero: seven kinds of recording drawn as particles from real
 * data, turning, scrolling and breathing, around BIDS Manager's own mark.
 * Scrolling carries every particle through the mark into the dataset it
 * writes, the tree written in the particles themselves; then the text appears,
 * and the sidecars beside the recordings fill in, field by field, each value
 * marked with where it came from.
 *
 * With effects off (the header's switch, or the system's reduced-motion
 * setting) the hero is one still frame and nothing moves; the dataset is shown
 * below it, already filled in. Without WebGL 2 the page keeps the drawn still.
 * Every frame starts from a cleared canvas: a fading trail (the background
 * painted over the last frame at partial opacity) never reaches the background
 * exactly in 8-bit colour and left a stain behind the forms. Slow machines are
 * noticed by their frame time: first the resolution goes, then half of the
 * particles. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var hero = document.querySelector('[data-hero]');
  if (!hero) return;
  var stage = hero.querySelector('.hero-sticky');
  var canvas = hero.querySelector('.hero-canvas');
  var labelsHost = hero.querySelector('.hero-labels');
  var treeHost = hero.querySelector('.hero-tree');
  var hudState = hero.querySelector('[data-hud-state]');
  var root = document.body.getAttribute('data-root') || './';
  var fxOn = function () { return doc.getAttribute('data-fx') === 'on'; };
  var stats = window.__hero = { frames: 0, avg: 0, worst: 0, level: 0, n: 0, mode: 'init' };

  var gl = canvas.getContext('webgl2', { alpha: false, antialias: false, premultipliedAlpha: false,
                                         preserveDrawingBuffer: true, powerPreference: 'default' });
  if (!gl) { stats.mode = 'no-webgl'; return; }

  /* ------------------------------------------------------------ data */
  var data = null;
  function parse(buf) {
    var dv = new DataView(buf), hl = dv.getUint32(0, true);
    var head = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 4, hl)));
    var n = head.n, o = 4 + hl;
    var x = new Int16Array(buf, o, n); o += 2 * n;
    var y = new Int16Array(buf, o, n); o += 2 * n;
    var z = new Int8Array(buf, o, n); o += n;
    var kind = new Uint8Array(buf, o, n); o += n;
    var seed = new Uint8Array(buf, o, n); o += n;
    var val = new Uint8Array(buf, o, n);
    return { head: head, n: n, x: x, y: y, z: z, kind: kind, seed: seed, val: val };
  }

  /* --------------------------------------------------------- shaders */
  var VS = [
    '#version 300 es', 'precision highp float;',
    'in vec2 aXY; in float aZ; in float aKind; in float aSeed; in float aVal; in vec2 aTgt;',
    'uniform vec2 uRes; uniform float uTime; uniform float uP; uniform vec3 uMarkB;',
    'uniform vec4 uC[8]; uniform vec3 uCol[8]; uniform float uDpr; uniform float uHover;',
    'uniform float uSize; uniform float uDark; uniform float uTextOn;',
    'out vec4 vCol;',
    'mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }',
    'void main() {',
    '  int k = int(aKind + 0.5);',
    '  vec4 C = uC[k];',
    '  vec3 p = vec3(aXY, aZ);',
    '  float t = uTime, bright = 1.0, alpha = 1.0, depth = 0.5;',
    '  if (k == 0 || k == 4) {',
    '    vec2 xz = rot(t * 0.30 + (k == 4 ? 2.1 : 0.0)) * vec2(p.x, p.z); p.x = xz.x; p.z = xz.y;',
    '    vec2 yz = rot(k == 4 ? -0.35 : 0.12) * vec2(p.y, p.z); p.y = yz.x; p.z = yz.y;',
    '    p.xy *= 1.0 / (1.0 - p.z * 0.26); depth = p.z * 0.5 + 0.5;',
    '    bright = 0.42 + 0.7 * depth;',
    '  } else if (k == 3 || k == 5) {',
    '    float x = fract(p.x * 0.5 + 0.5 - t * (k == 3 ? 0.030 : 0.045));',
    '    p.x = x * 2.0 - 1.0;',
    '    alpha *= smoothstep(0.0, 0.07, x) * smoothstep(1.0, 0.93, x);',
    '  } else if (k == 6) {',
    '    if (aVal > 0.97) { alpha *= 0.32; bright = 0.7; }',
    '    else { float d = aVal - fract(t * 0.05) * 0.95; bright = 0.45 + 1.5 * exp(-d * d * 1400.0); }',
    '  } else if (k == 2) {',
    '    bright = 0.55 + 0.6 * aVal * (0.85 + 0.15 * sin(t * 1.3 + aSeed * 6.283));',
    '  } else if (k == 1) {',
    '    p.y *= 1.0 + 0.04 * sin(t * 1.1 + p.x * 3.0);',
    '  } else if (k == 7) {',
    '    bright = 0.8 + 0.2 * sin(t * 0.9 + aSeed * 6.283);',
    '  }',
    '  vec2 idle = C.xy + p.xy * C.z;',
    '  float start = 0.04 + aSeed * 0.34 + float(k) * 0.01;',
    '  float q = smoothstep(start, start + 0.46, uP);',
    '  float ang = aSeed * 97.0 + t * 0.6;',
    '  vec2 hub = uC[7].xy + vec2(cos(ang), sin(ang)) * uC[7].z * (0.15 + 0.85 * fract(aSeed * 13.0));',
    '  float u = 1.0 - q;',
    '  vec2 pos = u * u * idle + 2.0 * u * q * hub + q * q * aTgt;',
    '  vec2 clip = pos / uRes * 2.0 - 1.0; clip.y = -clip.y;',
    '  gl_Position = vec4(clip, 0.0, 1.0);',
    '  float hov = uHover < -0.5 ? 1.0 : (abs(uHover - float(k)) < 0.5 ? 1.45 : 0.42);',
    '  hov = mix(hov, 1.0, q);',
    '  float size = uSize * (k == 0 ? 0.8 + 0.6 * aVal : 1.0) * ((k == 0 || k == 4) ? 0.7 + 0.6 * depth : 1.0);',
    '  if (k == 7) size *= 0.85;',
    '  size = mix(size, uSize * 0.8, q);',
    '  gl_PointSize = size * uDpr * (hov > 1.2 ? 1.2 : 1.0);',
    '  vec3 col = uCol[k];',
    '  if (k == 7) col = mix(uCol[7], uMarkB, aVal);',
    '  float a = alpha * 0.9 * mix(1.0, 0.0, uTextOn * q);',
    '  if (k == 2) bright = 0.6 + 0.7 * aVal;',
    '  // One palette in both themes: at night brightness lights the points; on',
    '  // paper it thins them, so the pastel itself is never darkened.',
    '  vCol = vec4(col, a * clamp(bright * hov, 0.22, 1.0));',
    '}'].join('\n');
  var FS = [
    '#version 300 es', 'precision highp float;',
    'in vec4 vCol; out vec4 o; uniform float uDark;',
    'void main() {',
    '  vec2 c = gl_PointCoord - 0.5; float r = length(c) * 2.0;',
    '  float a = smoothstep(1.0, 0.15, r);',
    '  o = vec4(vCol.rgb, vCol.a * a);',
    '}'].join('\n');

  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  function program(vs, fs) {
    var p = gl.createProgram();
    gl.attachShader(p, compile(gl.VERTEX_SHADER, vs));
    gl.attachShader(p, compile(gl.FRAGMENT_SHADER, fs));
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    return p;
  }
  var prog, U = {}, vao, tgtBuf;
  try { prog = program(VS, FS); }
  catch (e) { stats.mode = 'shader-error'; stats.error = String(e); return; }
  ['uRes', 'uTime', 'uP', 'uMarkB', 'uC', 'uCol', 'uDpr', 'uHover', 'uSize', 'uDark', 'uTextOn'].forEach(function (n) {
    U[n] = gl.getUniformLocation(prog, n);
  });

  function buffers() {
    vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    function attr(name, arr, size, type, norm) {
      var loc = gl.getAttribLocation(prog, name);
      var b = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, b);
      gl.bufferData(gl.ARRAY_BUFFER, arr, gl.STATIC_DRAW);
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc, size, type, norm, 0, 0);
      return b;
    }
    var xy = new Int16Array(data.n * 2);
    for (var i = 0; i < data.n; i++) { xy[2 * i] = data.x[i]; xy[2 * i + 1] = data.y[i]; }
    attr('aXY', xy, 2, gl.SHORT, true);
    attr('aZ', data.z, 1, gl.BYTE, true);
    attr('aKind', data.kind, 1, gl.UNSIGNED_BYTE, false);
    attr('aSeed', data.seed, 1, gl.UNSIGNED_BYTE, true);
    attr('aVal', data.val, 1, gl.UNSIGNED_BYTE, true);
    tgtBuf = attr('aTgt', new Float32Array(data.n * 2), 2, gl.FLOAT, false);
    gl.bindVertexArray(null);
  }

  /* ---------------------------------------------------------- layout */
  var W = 0, H = 0, dpr = 1, maxDpr = Math.min(window.devicePixelRatio || 1, 2);
  var centres = [], lines = [], narrow = false;
  function css(name) { return getComputedStyle(doc).getPropertyValue(name).trim(); }
  function hexRGB(h) {
    h = h.replace('#', '');
    if (h.length === 3) h = h.replace(/./g, '$&$&');
    var v = parseInt(h, 16);
    return [((v >> 16) & 255) / 255, ((v >> 8) & 255) / 255, (v & 255) / 255];
  }
  // The hero's own colour tokens: the pastels in dark, deeper hues on light paper.
  var KIND_VARS = ['--h-mri', '--h-mrs', '--h-pet', '--h-eeg', '--h-meg', '--h-physio', '--h-eye', '--h-mark-a'];

  function treeLines(head) {
    // The dataset's lines; on a narrow screen the subject and session prefix
    // of every file name becomes an ellipsis and the companions are left out.
    var ds = head.dataset;
    return ds.tree.map(function (l) {
      var folder = l.folder ? (l.folder + '      ').slice(0, 6) : (l.branch.indexOf('│') >= 0 ? '      ' : '');
      var name = narrow ? l.name.replace(/^sub-001_ses-01_/, '…_') : l.name;
      var more = (!narrow && l.more) ? '  ' + l.more : '';
      var json = l.json ? '  .json' : '';
      return { k: l.k, cls: l.cls || 'rec', branch: l.branch + folder, name: name, more: more, json: json,
               card: l.card || '', text: l.branch + folder + name + more + json };
    });
  }

  function layout() {
    var r = stage.getBoundingClientRect();
    W = Math.max(320, r.width); H = Math.max(320, r.height);
    narrow = W < 820;
    dpr = Math.min(maxDpr, stats.level >= 1 ? 1 : maxDpr);
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    var kinds = data.head.kinds.length;
    // The forms on an ellipse around the emblem, right of the text on a wide
    // screen, under it on a narrow one.
    var cx, cy, rx, ry, s;
    if (narrow) { cx = W / 2; cy = H * 0.745; rx = W * 0.37; ry = H * 0.155; s = Math.min(W * 0.085, H * 0.05); }
    else { cx = W * 0.705; cy = H * 0.5; rx = Math.min(W * 0.215, H * 0.48); ry = H * 0.335; s = Math.min(W * 0.05, H * 0.08); }
    centres = [];
    for (var k = 0; k < kinds; k++) {
      var a = -Math.PI / 2 + k / kinds * Math.PI * 2;
      var solid = data.head.kinds[k].solid;
      centres.push({ x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a), s: s * (solid ? 1.18 : 1.0) * (k === 6 ? 1.15 : 1) });
    }
    centres.push({ x: cx, y: cy, s: s * 1.25 });
    placeTree();
    placeLabels();
  }

  var treeBox = { x: 0, y: 0, w: 0, h: 0, fs: 12 };
  function placeTree() {
    lines = treeLines(data.head);
    var longest = lines.reduce(function (m, l) { return Math.max(m, l.text.length); }, 0);
    var margin = narrow ? 18 : Math.max(36, (W - 1320) / 2 + 36);
    // Room for the sidecar beside the tree on a wide screen, under it on a narrow one.
    var cardW = narrow ? 0 : Math.min(430, Math.max(320, W * 0.3));
    var avail = narrow ? W - 2 * margin : W - 2 * margin - cardW - 44;
    var fs = Math.max(7, Math.min(narrow ? 12 : 17, avail / (longest * 0.6)));
    var lh = fs * (narrow ? 1.7 : 1.8);
    var tw = longest * fs * 0.6, th = lines.length * lh;
    var x0 = narrow ? (W - tw) / 2 : margin;
    var y0 = Math.max(H * 0.2, (H - th) / 2 + H * 0.04);
    var end = hero.querySelector('.hero-end');
    if (narrow && end) {
      // The title first, the tree under it.
      end.style.left = margin + 'px'; end.style.right = margin + 'px'; end.style.top = '20px';
      y0 = 20 + end.offsetHeight + 16;
    }
    treeBox = { x: x0, y: y0, w: tw, h: th, fs: fs, cardX: narrow ? margin : x0 + tw + 44, cardY: narrow ? y0 + th + 18 : y0 - 8,
                cardW: narrow ? W - 2 * margin : Math.min(cardW, W - (x0 + tw + 44) - margin) };
    // The tree as text, then the pixels of each line become targets.
    var off = document.createElement('canvas');
    off.width = Math.ceil(W); off.height = Math.ceil(H);
    var c = off.getContext('2d');
    c.font = fs + 'px "JetBrains Mono", ui-monospace, monospace';
    c.textBaseline = 'middle';
    c.fillStyle = '#000';
    var pools = [];
    treeHost.innerHTML = '';
    treeHost.style.fontSize = fs + 'px';
    lines.forEach(function (l, i) {
      var y = y0 + i * lh + lh / 2;
      c.clearRect(0, 0, off.width, off.height);
      c.fillText(l.text, x0, y);
      var top = Math.max(0, Math.floor(y - fs)), hgt = Math.ceil(fs * 2);
      var img = c.getImageData(0, top, off.width, hgt).data, pts = [];
      for (var py = 0; py < hgt; py += 1) for (var px = Math.floor(x0); px < Math.min(off.width, x0 + tw + 4); px += 1) {
        if (img[(py * off.width + px) * 4 + 3] > 110) pts.push(px, top + py);
      }
      pools.push(pts);
      var el = document.createElement('div');
      el.className = 'tree-line tree-' + l.cls;
      el.style.left = x0 + 'px'; el.style.top = y + 'px';
      if (l.card) el.setAttribute('data-card', l.card);
      if (l.cls === 'rec') {
        el.innerHTML = '<span class="tl-branch">' + l.branch + '</span><span class="tl-file" style="--kc:var(' + KIND_VARS[l.k] + ')">' + l.name +
          '</span>' + (l.more ? '<span class="tl-more">' + l.more + '</span>' : '') + (l.json ? '<span class="tl-json">' + l.json + '</span>' : '');
      } else { el.textContent = l.text; }
      treeHost.appendChild(el);
    });
    if (end && !narrow) { end.style.left = x0 + 'px'; end.style.right = margin + 'px'; end.style.top = Math.max(16, y0 - 96) + 'px'; }
    if (cardEl) { cardEl.style.left = treeBox.cardX + 'px'; cardEl.style.top = treeBox.cardY + 'px'; cardEl.style.width = treeBox.cardW + 'px'; }
    // Which lines belong to which kind: a recording's own lines; the mark
    // fills the dataset's top lines.
    var byKind = {};
    lines.forEach(function (l, i) { (byKind[l.k] = byKind[l.k] || []).push(i); });
    var tgt = new Float32Array(data.n * 2);
    var counters = {};
    for (var i = 0; i < data.n; i++) {
      var k = data.kind[i], rows = byKind[k];
      var row = rows[(counters[k] = (counters[k] || 0) + 1) % rows.length];
      var pool = pools[row];
      if (!pool.length) { tgt[2 * i] = W / 2; tgt[2 * i + 1] = H / 2; continue; }
      var j = ((i * 2654435761) >>> 0) % (pool.length / 2);
      tgt[2 * i] = pool[2 * j] + (data.seed[i] / 255 - 0.5) * 0.9;
      tgt[2 * i + 1] = pool[2 * j + 1] + ((data.seed[i] * 7 % 255) / 255 - 0.5) * 0.9;
    }
    gl.bindBuffer(gl.ARRAY_BUFFER, tgtBuf);
    gl.bufferData(gl.ARRAY_BUFFER, tgt, gl.STATIC_DRAW);
  }

  /* ---------------------------------------------------------- sidecars */
  // Each card is a real sidecar of the sample: its fields appear one by one,
  // a placeholder an answer replaced is typed over, and every value says
  // where it came from.
  var cardEl = hero.querySelector('.hero-card');
  var SRC = { file: 'read from the recording', bm: 'written by BIDS Manager', you: 'your answer', todo: 'to answer' };
  var cardIdx = 0, cardTimer = 0, cardRun = 0;
  function fmt(v) {
    if (Array.isArray(v)) {
      var parts = v.slice(0, 3).map(function (x) { return JSON.stringify(x); });
      return '[' + parts.join(', ') + (v.length > 3 ? ', …' : '') + ']';
    }
    return JSON.stringify(v);
  }
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function cardHTML(cd, filled) {
    var rows = cd.rows.map(function (r, i) {
      var val = filled || !r.was ? fmt(r.value) : fmt(r.was);
      var src = filled || !r.was ? r.src : 'todo';
      return '<div class="hc-row' + (filled ? ' is-in' : '') + '" data-i="' + i + '"><span class="hc-kv"><span class="hc-key">"' + esc(r.key) + '":</span> ' +
        '<span class="hc-val src-' + src + '">' + esc(filled ? val : '') + '</span></span>' +
        '<i class="hc-src src-' + src + '">' + SRC[src] + '</i></div>';
    }).join('');
    return '<p class="hc-file"><span>' + esc(cd.file) + '</span></p><div class="hc-body">{' + rows + '}</div>';
  }
  function typeInto(el, text, done, run) {
    var n = 0, step = Math.max(1, Math.ceil(text.length / 28));
    (function tick() {
      if (run !== cardRun) return;
      n = Math.min(text.length, n + step);
      el.textContent = text.slice(0, n);
      if (n < text.length) setTimeout(tick, 22); else done();
    })();
  }
  function playCard(key) {
    var cd = data.head.dataset.cards[key];
    if (!cd || !cardEl) return;
    var run = ++cardRun;
    cardEl.innerHTML = cardHTML(cd, false);
    $$t('.tree-line').forEach(function (el) { el.classList.toggle('is-focus', el.getAttribute('data-card') === key); });
    var rows = cardEl.querySelectorAll('.hc-row');
    var i = 0;
    (function next() {
      if (run !== cardRun) return;
      if (i >= rows.length) { setTimeout(answer, 500); return; }
      var row = rows[i], r = cd.rows[i]; i++;
      row.classList.add('is-in');
      var v = row.querySelector('.hc-val');
      typeInto(v, r.was ? fmt(r.was) : fmt(r.value), function () { setTimeout(next, 120); }, run);
    })();
    function answer() {
      // The placeholders someone answered: typed over, marked as answers.
      var pending = [];
      cd.rows.forEach(function (r, j) { if (r.was) pending.push(j); });
      (function one() {
        if (run !== cardRun) return;
        if (!pending.length) { cardTimer = setTimeout(nextCard, 3200); return; }
        var j = pending.shift(), row = rows[j], r = cd.rows[j];
        var v = row.querySelector('.hc-val'), tag = row.querySelector('.hc-src');
        row.classList.add('is-answering');
        setTimeout(function () {
          if (run !== cardRun) return;
          v.className = 'hc-val src-' + r.src; tag.className = 'hc-src src-' + r.src; tag.textContent = SRC[r.src];
          typeInto(v, fmt(r.value), function () { row.classList.remove('is-answering'); setTimeout(one, 380); }, run);
        }, 420);
      })();
    }
  }
  function nextCard() {
    var order = data.head.dataset.order;
    cardIdx = (cardIdx + 1) % order.length;
    playCard(order[cardIdx]);
  }
  function startCards() { cardIdx = 0; playCard(data.head.dataset.order[0]); }
  function stopCards() { cardRun++; clearTimeout(cardTimer); if (cardEl) cardEl.innerHTML = '';
    $$t('.tree-line').forEach(function (el) { el.classList.remove('is-focus'); }); }
  function $$t(sel) { return [].slice.call(treeHost.querySelectorAll(sel)); }

  var extent = null;
  function extents() {
    // How far each form reaches below its centre (a turning form: its radius).
    var e = [], i, k;
    for (k = 0; k < 8; k++) e.push(0);
    for (i = 0; i < data.n; i++) {
      k = data.kind[i];
      var r = data.head.kinds[k] && data.head.kinds[k].solid ? Math.hypot(data.y[i], data.z[i] * 256) / 32000 : data.y[i] / 32000;
      if (r > e[k]) e[k] = r;
    }
    return e;
  }
  function placeLabels() {
    if (!extent) extent = extents();
    labelsHost.innerHTML = '';
    data.head.kinds.forEach(function (kd, k) {
      var c = centres[k];
      var el = document.createElement('div');
      el.className = 'hero-label';
      el.style.left = c.x + 'px'; el.style.top = (c.y + c.s * Math.min(1.25, extent[k] * (kd.solid ? 1.12 : 1.0)) + 16) + 'px';
      el.style.setProperty('--kc', 'var(' + KIND_VARS[k] + ')');
      el.innerHTML = '<b>' + kd.name + '</b><span>' + kd.folder + ' · _' + kd.suffix + '</span>';
      labelsHost.appendChild(el);
      kd._label = el;
    });
    var c = centres[centres.length - 1];
    var mark = document.createElement('div');
    mark.className = 'hero-label hero-label--mark';
    mark.style.left = c.x + 'px'; mark.style.top = (c.y + c.s * 0.95 + 14) + 'px';
    mark.innerHTML = '<b>BIDS Manager</b>';
    labelsHost.appendChild(mark);
  }

  /* ----------------------------------------------------------- state */
  var mouse = { x: -9999, y: -9999 }, hover = -1;
  var progress = 0, shown = false, running = false, last = 0, t0 = performance.now(), frozen = 0;
  function scrollProgress() {
    if (!fxOn()) return 0;
    var r = hero.getBoundingClientRect();
    var travel = r.height - stage.offsetHeight;
    if (travel <= 1) return 0;
    return Math.max(0, Math.min(1, -r.top / travel));
  }
  // The pointer only says which form is under it (its label shows its BIDS
  // folder and suffix); it moves nothing.
  function onMove(e) {
    var r = stage.getBoundingClientRect();
    var p = e.touches ? e.touches[0] : e;
    mouse.x = p.clientX - r.left; mouse.y = p.clientY - r.top;
  }
  stage.addEventListener('pointermove', onMove, { passive: true });
  stage.addEventListener('pointerleave', function () { mouse.x = mouse.y = -9999; });

  function nearest() {
    var best = -1, bd = 1e9;
    for (var k = 0; k < centres.length - 1; k++) {
      var c = centres[k], d = Math.hypot(mouse.x - c.x, mouse.y - c.y);
      if (d < c.s * 1.35 && d < bd) { bd = d; best = k; }
    }
    return best;
  }

  function colours() {
    var dark = doc.getAttribute('data-theme') === 'dark';
    var cols = [];
    KIND_VARS.forEach(function (v) { cols.push.apply(cols, hexRGB(css(v) || '#888888')); });
    return { dark: dark, cols: new Float32Array(cols), markB: hexRGB(css('--h-mark-b') || '#2f8f45'), bg: hexRGB(css('--bg') || '#000000') };
  }
  var pal = null;

  function render(now) {
    var t = (now - t0) / 1000;
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(pal.bg[0], pal.bg[1], pal.bg[2], 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(prog);
    gl.enable(gl.BLEND);
    // Plain alpha blending, so a crowd of points never adds up to white.
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    gl.uniform2f(U.uRes, W, H);
    gl.uniform1f(U.uTime, t);
    gl.uniform1f(U.uP, progress);
    gl.uniform3f(U.uMarkB, pal.markB[0], pal.markB[1], pal.markB[2]);
    var cs = new Float32Array(32);
    centres.forEach(function (c, i) { cs[4 * i] = c.x; cs[4 * i + 1] = c.y; cs[4 * i + 2] = c.s; });
    gl.uniform4fv(U.uC, cs);
    gl.uniform3fv(U.uCol, pal.cols);
    gl.uniform1f(U.uDpr, dpr);
    gl.uniform1f(U.uHover, hover);
    gl.uniform1f(U.uSize, narrow ? 1.7 : 2.1);
    gl.uniform1f(U.uDark, pal.dark ? 1 : 0);
    gl.uniform1f(U.uTextOn, shown ? 1 : 0);
    gl.bindVertexArray(vao);
    var count = stats.level >= 2 ? Math.floor(data.n / 2) : data.n;
    stats.n = count;
    gl.drawArrays(gl.POINTS, 0, count);
    gl.bindVertexArray(null);
  }

  function frame(now) {
    if (!running) return;
    requestAnimationFrame(frame);
    var dt = last ? now - last : 16; last = now;
    // Frame time, averaged; a slow machine steps down, never back up.
    if (stats.frames > 20) {
      stats.avg = stats.avg ? stats.avg * 0.95 + dt * 0.05 : dt;
      stats.worst = Math.max(stats.worst, dt);
      if (stats.frames > 90 && stats.avg > 26 && stats.level < 2 && now - frozen > 2500) {
        stats.level++; frozen = now; stats.avg = 0;
        if (stats.level === 1) layout();
      }
    }
    stats.frames++;
    var p = scrollProgress();
    progress += (p - progress) * 0.12;
    if (Math.abs(p - progress) < 0.0005) progress = p;
    hover = progress < 0.05 ? nearest() : -1;
    data.head.kinds.forEach(function (kd, k) { kd._label.classList.toggle('is-hot', hover === k); });
    var nowShown = progress > 0.9;
    if (nowShown !== shown) { shown = nowShown; hero.classList.toggle('is-converted', shown); if (shown) startCards(); else stopCards(); }
    hero.style.setProperty('--hp', progress.toFixed(3));
    if (hudState) hudState.textContent = progress < 0.04 ? 'raw recordings' : progress < 0.9 ? 'converting' : 'BIDS dataset';
    render(now);
  }

  function start() {
    if (running || !fxOn()) return;
    running = true; last = 0; stats.mode = 'live';
    requestAnimationFrame(frame);
  }
  function stop() { running = false; }
  function still() {
    // One frame, the forms as they are before scrolling: for effects off.
    stop(); stopCards(); progress = 0; hover = -1; shown = false;
    hero.classList.remove('is-converted');
    hero.style.setProperty('--hp', '0');
    stats.mode = 'still';
    render(t0 + 4200);
  }

  /* ------------------------------------------------------------ boot */
  var url = root + 'static/hero/hero.bin';
  Promise.all([
    fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); }),
    document.fonts && document.fonts.load ? document.fonts.load('16px "JetBrains Mono"') : Promise.resolve()
  ]).then(function (res) {
    data = parse(res[0]);
    buffers();
    pal = colours();
    layout();
    hero.classList.add('is-live');
    if (fxOn()) start(); else still();
    var vis = true;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        vis = es[0].isIntersecting;
        if (vis && fxOn()) start(); else stop();
      }, { threshold: 0 }).observe(hero);
    }
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else if (vis && fxOn()) start();
    });
    document.addEventListener('bm-fx', function (e) {
      if (e.detail.on) { layout(); start(); } else still();
    });
    new MutationObserver(function () { pal = colours(); if (!running) still(); })
      .observe(doc, { attributes: true, attributeFilter: ['data-theme'] });
    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () { layout(); if (!running) still(); }, 120);
    });
  }).catch(function (e) { stats.mode = 'error'; stats.error = String(e); });
})();
