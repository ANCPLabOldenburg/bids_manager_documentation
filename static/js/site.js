/* BIDS Manager documentation: behaviour.
 * Everything here is an enhancement: every page reads complete without it,
 * and with Effects off nothing moves. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var root = document.body.getAttribute('data-root') || './';
  /* Motion is on only with effects on: on by default, switched off in the
     header (remembered), or by ?motion=reduce. */
  var reduce = function () {
    return doc.getAttribute('data-fx') === 'off' || doc.getAttribute('data-motion') === 'reduce';
  };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  function $(sel, el) { return (el || document).querySelector(sel); }
  function $$(sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); }

  /* ------------------------------------------------------------ theme */
  function applyTheme(pref) {
    var dark = pref === 'dark' || (pref === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    doc.setAttribute('data-theme', dark ? 'dark' : 'light');
    doc.setAttribute('data-theme-pref', pref);
    $$('[data-set-theme]').forEach(function (b) {
      b.setAttribute('aria-checked', String(b.getAttribute('data-set-theme') === pref));
    });
    document.dispatchEvent(new CustomEvent('bm-theme', { detail: dark ? 'dark' : 'light' }));
  }
  (function themeSwitch() {
    var btn = $('[data-theme-button]'), menu = $('.theme-menu');
    if (!btn || !menu) return;
    applyTheme(doc.getAttribute('data-theme-pref') || 'system');
    function close() { menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); }
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = menu.hidden;
      menu.hidden = !open; btn.setAttribute('aria-expanded', String(open));
      if (open) { var cur = $('[aria-checked="true"]', menu) || $('button', menu); cur.focus(); }
    });
    menu.addEventListener('click', function (e) {
      var b = e.target.closest('[data-set-theme]');
      if (!b) return;
      var pref = b.getAttribute('data-set-theme');
      store.set('bm-theme', pref); applyTheme(pref); close(); btn.focus();
    });
    menu.addEventListener('keydown', function (e) {
      var items = $$('button', menu), i = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
      if (e.key === 'Escape') { close(); btn.focus(); }
    });
    document.addEventListener('click', close);
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
      if ((doc.getAttribute('data-theme-pref') || 'system') === 'system') applyTheme('system');
    });
  })();

  /* ---------------------------------------------------------- effects */
  (function fxSwitch() {
    var b = $('[data-fx-toggle]');
    if (!b) return;
    function paint() {
      var on = doc.getAttribute('data-fx') === 'on';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      var st = $('[data-fx-state]', b);
      if (st) st.textContent = on ? 'on' : 'off';
      b.title = on ? 'Effects are on: click to stop the animations' : 'Effects are off: click to turn the animations on';
    }
    b.addEventListener('click', function () {
      var on = doc.getAttribute('data-fx') !== 'on';
      doc.setAttribute('data-fx', on ? 'on' : 'off');
      store.set('bm-fx', on ? 'on' : 'off');
      paint();
      document.dispatchEvent(new CustomEvent('bm-fx', { detail: { on: on } }));
    });
    paint();
  })();

  /* ------------------------------------------- the home page's flow */
  (function flow() {
    $$('[data-flow]').forEach(function (box) {
      var steps = $$('[data-flow-step]', box), figs = $$('.flow-view .fig', box);
      function show(i) {
        steps.forEach(function (s, j) { s.classList.toggle('is-active', i === j); s.setAttribute('aria-current', i === j ? 'step' : 'false'); });
        figs.forEach(function (f, j) { f.classList.toggle('is-shown', i === j); });
      }
      steps.forEach(function (s, i) {
        s.setAttribute('tabindex', '0');
        s.addEventListener('click', function (e) { if (e.target.closest('a')) return; show(i); });
        s.addEventListener('mouseenter', function () { show(i); });
        s.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(i); } });
      });
      show(0);
    });
  })();

  /* ---------------------------------------------- decoding kickers */
  (function decode() {
    if (reduce() || !('IntersectionObserver' in window)) return;
    var glyphs = 'abcdefghijklmnopqrstuvwxyz0123456789-_/';
    var items = $$('.home-kicker, .decode');
    if (!items.length) return;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        var node = e.target, text = node.getAttribute('data-text') || node.textContent;
        node.setAttribute('data-text', text);
        node.setAttribute('aria-label', text);
        var start = performance.now(), dur = 700;
        (function step(t) {
          var p = Math.min(1, (t - start) / dur), out = '';
          for (var i = 0; i < text.length; i++) {
            var c = text[i];
            out += (c === ' ' || i / text.length < p) ? c : glyphs[(Math.random() * glyphs.length) | 0];
          }
          node.textContent = out;
          if (p < 1 && doc.getAttribute('data-fx') === 'on') requestAnimationFrame(step); else node.textContent = text;
        })(start);
      });
    }, { threshold: 0.6 });
    items.forEach(function (el) { io.observe(el); });
  })();

  /* ------------------------------------------------- keys per platform */
  // Every key is written for both systems in the page; keep only the
  // reader's: the system chosen in an OS tab, else the one detected. On a
  // system we cannot tell, both stay. The "(Control-click on a Mac)" notes
  // after a right-click are kept on a Mac and where the system is unknown.
  function keyOS() {
    var chosen = store.get('bm-os');
    if (chosen === 'macos') return 'mac';
    if (chosen === 'windows' || chosen === 'linux') return chosen;
    return doc.getAttribute('data-os') || 'unknown';
  }
  function showKeys() {
    var os = keyOS();
    $$('.keys[data-mac]').forEach(function (k) {
      if (!k._both) k._both = k.innerHTML;
      if (os === 'mac') {
        k.innerHTML = '<kbd class="key"></kbd>';
        k.firstChild.textContent = k.getAttribute('data-mac');
        k.firstChild.title = k.getAttribute('data-mac-name') || '';
      } else if (os === 'windows' || os === 'linux') {
        k.innerHTML = '<kbd class="key"></kbd>';
        k.firstChild.textContent = k.getAttribute('data-other');
      } else {
        k.innerHTML = k._both;
      }
    });
    $$('kbd.search-key[data-mac]').forEach(function (k) {
      k.textContent = os === 'mac' ? k.getAttribute('data-mac') : (os === 'windows' || os === 'linux')
        ? k.getAttribute('data-other') : k.getAttribute('data-mac') + ' / ' + k.getAttribute('data-other');
    });
    $$('.mac-click').forEach(function (n) { n.hidden = os === 'windows' || os === 'linux'; });
  }
  showKeys();
  document.addEventListener('bm-os', showKeys);

  /* ------------------------------------------------------- navigation */
  (function navToggle() {
    var t = $('.nav-toggle'), side = $('#sidebar');
    if (!t) return;
    if (!side) {
      // A page without a sidebar (the home page): the drawer holds the sections alone.
      side = document.createElement('aside');
      side.className = 'sidebar sidebar--sections'; side.id = 'sidebar';
      side.setAttribute('aria-label', 'Sections');
      side.innerHTML = '<div class="sidebar-inner"></div>';
      document.body.appendChild(side);
    }
    // Narrow screens: the header's sections live at the top of the drawer.
    var header = $('.header-nav');
    if (header) {
      var box = document.createElement('div');
      box.className = 'mobile-sections';
      box.innerHTML = header.innerHTML;
      $('.sidebar-inner', side).insertBefore(box, $('.sidebar-inner', side).firstChild);
    }
    t.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      t.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', function (e) {
      if (document.body.classList.contains('nav-open') && !e.target.closest('#sidebar') && !e.target.closest('.nav-toggle')) {
        document.body.classList.remove('nav-open'); t.setAttribute('aria-expanded', 'false');
      }
    });
    var cur = $('.sidebar .is-current', side);
    if (cur && cur.scrollIntoView && side.scrollHeight > side.clientHeight) {
      var top = cur.offsetTop - side.clientHeight / 3;
      side.scrollTop = Math.max(0, top);
    }
  })();

  /* ----------------------------------------------------- on this page */
  (function tocSpy() {
    var toc = $('.toc');
    if (!toc) return;
    var links = $$('a', toc);
    var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); })
      .filter(Boolean);
    function update() {
      var y = window.scrollY + 120, current = null;
      targets.forEach(function (t) { if (t.getBoundingClientRect().top + window.scrollY <= y) current = t; });
      links.forEach(function (a) { a.classList.toggle('is-active', current && a.getAttribute('href') === '#' + current.id); });
      // A wide figure passing the column: the list steps aside.
      var band = toc.getBoundingClientRect(), covered = false;
      $$('.fig--wide').forEach(function (f) {
        var r = f.getBoundingClientRect();
        if (r.right > band.left && r.bottom > band.top + 40 && r.top < Math.min(band.bottom, window.innerHeight)) covered = true;
      });
      toc.classList.toggle('is-covered', covered);
    }
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(function () { update(); ticking = false; }); }
    }, { passive: true });
    window.addEventListener('resize', update);
    update();
  })();

  /* ---------------------------------------------------------- OS tabs */
  (function osTabs() {
    var labels = { macos: 'macOS', windows: 'Windows', linux: 'Linux' };
    var mine = { mac: 'macos', windows: 'windows', linux: 'linux' }[doc.getAttribute('data-os')] || 'macos';
    var chosen = store.get('bm-os') || mine;
    function select(os) {
      // What the installer does, for this system; with effects on, its
      // steps fill in one after the other.
      $$('[data-installer]').forEach(function (box) {
        $$('.is-os button', box).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-os') === os)); });
        $$('.is-steps-text', box).forEach(function (t) { t.hidden = t.getAttribute('data-os') !== os; });
        var steps = $$('.is-step', box);
        steps.forEach(function (st) { st.classList.remove('is-on'); });
        steps.forEach(function (st, i) {
          if (reduce()) st.classList.add('is-on');
          else setTimeout(function () { st.classList.add('is-on'); }, 90 + 260 * i);
        });
      });
      $$('.os-tabs').forEach(function (group) {
        var panels = $$(':scope > .os-panel', group);
        var has = panels.some(function (p) { return p.getAttribute('data-os') === os; });
        var pick = has ? os : panels[0].getAttribute('data-os');
        panels.forEach(function (p) { p.hidden = p.getAttribute('data-os') !== pick; });
        $$(':scope > .os-tablist button', group).forEach(function (b) {
          var on = b.getAttribute('data-os') === pick;
          b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1;
        });
      });
    }
    $$('.os-tabs').forEach(function (group, gi) {
      var list = document.createElement('div');
      list.className = 'os-tablist'; list.setAttribute('role', 'tablist');
      $$(':scope > .os-panel', group).forEach(function (p, i) {
        var os = p.getAttribute('data-os'), b = document.createElement('button');
        b.type = 'button'; b.setAttribute('role', 'tab'); b.setAttribute('data-os', os);
        b.id = 'os-' + gi + '-' + os; p.setAttribute('role', 'tabpanel'); p.setAttribute('aria-labelledby', b.id);
        b.textContent = labels[os] || os;
        b.addEventListener('click', function () { store.set('bm-os', os); select(os); document.dispatchEvent(new CustomEvent('bm-os')); });
        b.addEventListener('keydown', function (e) {
          var bs = $$('button', list), j = bs.indexOf(b);
          if (e.key === 'ArrowRight') { bs[(j + 1) % bs.length].click(); bs[(j + 1) % bs.length].focus(); }
          if (e.key === 'ArrowLeft') { bs[(j - 1 + bs.length) % bs.length].click(); bs[(j - 1 + bs.length) % bs.length].focus(); }
        });
        list.appendChild(b);
      });
      group.insertBefore(list, group.firstChild);
    });
    $$('[data-installer] .is-os button').forEach(function (b) {
      b.addEventListener('click', function () { var os = b.getAttribute('data-os'); store.set('bm-os', os); select(os); document.dispatchEvent(new CustomEvent('bm-os')); });
    });
    select(chosen);
  })();

  /* ------------------------------------------------------------- copy */
  $$('.code-copy').forEach(function (b) {
    b.addEventListener('click', function () {
      var pre = b.parentNode.querySelector('pre');
      var cmds = $$('.cmd', pre);
      var text = cmds.length ? cmds.map(function (c) { return c.textContent; }).join('\n') : pre.textContent;
      var done = function () {
        b.textContent = 'Copied'; b.classList.add('is-done');
        setTimeout(function () { b.textContent = 'Copy'; b.classList.remove('is-done'); }, 1600);
      };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
    });
  });

  /* --------------------------------------------------- glossary tips */
  (function tips() {
    var bubble = null;
    function show(a) {
      if (!bubble) { bubble = document.createElement('div'); bubble.className = 'tip-bubble'; bubble.setAttribute('role', 'tooltip'); document.body.appendChild(bubble); }
      bubble.textContent = a.getAttribute('data-tip');
      var r = a.getBoundingClientRect();
      bubble.style.left = Math.max(12, Math.min(window.innerWidth - 332, r.left + window.scrollX)) + 'px';
      bubble.style.top = (r.bottom + window.scrollY + 8) + 'px';
      requestAnimationFrame(function () { bubble.classList.add('is-shown'); });
    }
    function hide() { if (bubble) bubble.classList.remove('is-shown'); }
    $$('.term[data-tip]').forEach(function (a) {
      a.addEventListener('mouseenter', function () { show(a); });
      a.addEventListener('focus', function () { show(a); });
      a.addEventListener('mouseleave', hide); a.addEventListener('blur', hide);
    });
  })();

  /* --------------------------------------------------------- hotspots */
  (function hotspots() {
    $$('.fig.has-hotspots').forEach(function (fig) {
      var media = $('.fig-media', fig);
      var spot = document.createElement('div'); spot.className = 'spot'; media.appendChild(spot);
      var label = document.createElement('div'); label.className = 'spot-label'; media.appendChild(label);
      function on(n) {
        var hs = $('.hs[data-n="' + n + '"]', fig);
        if (!hs) return;
        var r = hs.getAttribute('data-rect').split(',').map(parseFloat);
        spot.style.left = (r[0] * 100) + '%'; spot.style.top = (r[1] * 100) + '%';
        spot.style.width = (r[2] * 100) + '%'; spot.style.height = (r[3] * 100) + '%';
        spot.classList.add('is-on');
        var text = $('.fig-legend li[data-n="' + n + '"] .hs-text', fig);
        label.textContent = hs.getAttribute('aria-label').replace(/^\d+: /, '');
        var mx = parseFloat(hs.getAttribute('data-mx')), my = parseFloat(hs.getAttribute('data-my'));
        // Below the marker, or above it near the bottom (anchored by its lower
        // edge, so a label that wraps to two lines never covers the marker);
        // measured, then kept inside the figure on both sides.
        if (my > 80) { label.style.top = 'auto'; label.style.bottom = 'calc(' + (100 - my) + '% + 16px)'; }
        else { label.style.bottom = 'auto'; label.style.top = 'calc(' + my + '% + 16px)'; }
        label.style.left = '0px';
        var mw = media.clientWidth, lw = label.offsetWidth;
        label.style.left = Math.max(8, Math.min(mx / 100 * mw - 12, mw - lw - 8)) + 'px';
        label.classList.add('is-on');
        $$('.hs', fig).forEach(function (h) { h.classList.toggle('is-on', h === hs); });
        $$('.fig-legend li', fig).forEach(function (li) { li.classList.toggle('is-on', li.getAttribute('data-n') === String(n)); });
      }
      function off() {
        spot.classList.remove('is-on'); label.classList.remove('is-on');
        $$('.hs, .fig-legend li', fig).forEach(function (el) { el.classList.remove('is-on'); });
      }
      $$('.hs', fig).forEach(function (hs) {
        var n = hs.getAttribute('data-n');
        hs.addEventListener('mouseenter', function () { on(n); });
        hs.addEventListener('focus', function () { on(n); });
        hs.addEventListener('mouseleave', off); hs.addEventListener('blur', off);
        hs.addEventListener('click', function (e) { e.stopPropagation(); on(n); });
      });
      $$('.fig-legend li', fig).forEach(function (li) {
        var n = li.getAttribute('data-n');
        li.addEventListener('mouseenter', function () { on(n); });
        li.addEventListener('mouseleave', off);
        li.addEventListener('click', function () { on(n); });
      });
      // A figure drawn too small for its markers (a toolbar strip on a phone)
      // hides them: overlapping markers cannot be told apart or clicked. The
      // legend below still shows each region.
      function crowd() {
        var pts = $$('.hs', fig).map(function (h) { var r = h.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; });
        var tight = false;
        for (var i = 0; i < pts.length && !tight; i++) for (var j = i + 1; j < pts.length; j++) {
          if (Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]) < 24) { tight = true; break; }
        }
        fig.classList.toggle('hs-crowded', tight);
      }
      fig.classList.remove('hs-crowded'); crowd();
      var crt; window.addEventListener('resize', function () { clearTimeout(crt); crt = setTimeout(function () { fig.classList.remove('hs-crowded'); crowd(); }, 150); });
      if (!reduce() && 'IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            if (e.isIntersecting) {
              $$('.hs', fig).forEach(function (hs, i) { setTimeout(function () { hs.classList.add('pulse'); }, 120 * i); });
              io.disconnect();
            }
          });
        }, { threshold: 0.5 });
        io.observe(fig);
      }
    });
  })();

  /* --------------------------------------------- converter alone, or not */
  $$('[data-compare]').forEach(function (box) {
    var btns = $$('.cmp-switch button', box);
    function side(which) {
      box.setAttribute('data-side', which);
      btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-side') === which)); });
    }
    btns.forEach(function (b) { b.addEventListener('click', function () { side(b.getAttribute('data-side')); }); });
    side('alone');
  });

  /* ------------------------------------------------------- workflow */
  // Follow one kind of recording through the stages: the steps that kind
  // goes through stay lit, the others fade; with effects on, the stages
  // light one after the other.
  $$('[data-workflow]').forEach(function (box) {
    var btns = $$('.wf-kinds button', box), steps = $$('.wf-step', box), stages = $$('.wf-stage', box);
    function follow(kind) {
      btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-kind') === kind)); });
      box.setAttribute('data-follow', kind || '');
      steps.forEach(function (st) {
        var on = !kind || (' ' + st.getAttribute('data-kinds') + ' ').indexOf(' ' + kind + ' ') >= 0;
        st.classList.toggle('is-off', !on);
      });
      if (!reduce()) {
        stages.forEach(function (sg, i) {
          sg.classList.remove('is-lit'); void sg.offsetWidth;
          setTimeout(function () { sg.classList.add('is-lit'); }, 160 * i);
        });
      }
    }
    btns.forEach(function (b) { b.addEventListener('click', function () { follow(b.getAttribute('data-kind')); }); });
    follow('');
  });

  /* ------------------------------------------- tabs of worked examples */
  // A tab list over panels (the series judged three ways, and any other
  // [data-judge] or [data-tabs] component): without JavaScript every panel
  // shows, one after the other.
  $$('[data-judge], [data-tabs]').forEach(function (box) {
    var tabs = $$('[role=tab]', box), panels = $$('[role=tabpanel]', box);
    function show(i, focus) {
      tabs.forEach(function (t, j) { t.setAttribute('aria-selected', String(i === j)); t.tabIndex = i === j ? 0 : -1; });
      panels.forEach(function (p, j) {
        if (i === j) { p.removeAttribute('data-hidden'); p.classList.remove('is-entering'); void p.offsetWidth; p.classList.add('is-entering'); }
        else p.setAttribute('data-hidden', '');
      });
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(i); });
      t.addEventListener('keydown', function (e) {
        var k = e.key, n = tabs.length;
        if (k === 'ArrowRight' || k === 'ArrowDown') { e.preventDefault(); show((i + 1) % n, true); }
        if (k === 'ArrowLeft' || k === 'ArrowUp') { e.preventDefault(); show((i - 1 + n) % n, true); }
        if (k === 'Home') { e.preventDefault(); show(0, true); }
        if (k === 'End') { e.preventDefault(); show(n - 1, true); }
      });
    });
    show(0);
  });

  /* ------------------------------------------------------------ clips */
  (function clips() {
    function fmt(t) { t = Math.max(0, Math.floor(t)); return Math.floor(t / 60) + ':' + ('0' + (t % 60)).slice(-2); }
    $$('.fig--clip').forEach(function (fig) {
      var player = $('.player', fig), big = $('.pl-big', fig), play = $('.pl-play', fig);
      var track = $('.pl-track', fig), fill = $('.pl-fill', fig), time = $('.pl-time', fig), speed = $('.pl-speed', fig);
      var chapters = [];
      try { chapters = JSON.parse(fig.getAttribute('data-chapters') || '[]'); } catch (e) {}
      player.hidden = false;
      function video() { return $$('video', fig).filter(function (v) { return v.offsetParent !== null; })[0] || $('video', fig); }
      var loop = video().hasAttribute('data-loop');
      var chapList = null;
      if (chapters.length) {
        var marks = $('.pl-marks', fig), dur = parseFloat(fig.getAttribute('data-duration')) || 1;
        chapList = document.createElement('ul'); chapList.className = 'chapters';
        chapters.forEach(function (c, i) {
          if (i) { var m = document.createElement('i'); m.style.left = (100 * c.t / dur) + '%'; marks.appendChild(m); }
          var li = document.createElement('li'), b = document.createElement('button');
          b.type = 'button'; b.textContent = c.title;
          b.addEventListener('click', function () { var v = video(); v.currentTime = c.t; start(); });
          li.appendChild(b); chapList.appendChild(li);
        });
        var cap = $('figcaption', fig);
        if (cap) cap.appendChild(chapList); else fig.appendChild(chapList);
      }
      function start() {
        var v = video();
        if (v.preload === 'none') v.preload = 'auto';
        var p = v.play(); if (p && p.catch) p.catch(function () {});
      }
      function pause() { video().pause(); }
      $$('video', fig).forEach(function (v) {
        v.loop = loop;
        v.addEventListener('play', function () { fig.classList.add('is-playing', 'has-played'); fig.classList.remove('is-paused'); play.setAttribute('aria-label', 'Pause'); });
        v.addEventListener('pause', function () { fig.classList.remove('is-playing'); fig.classList.add('is-paused'); play.setAttribute('aria-label', 'Play'); });
        v.addEventListener('timeupdate', function () {
          var d = v.duration || parseFloat(fig.getAttribute('data-duration')) || 1;
          fill.style.width = (100 * v.currentTime / d) + '%';
          time.textContent = fmt(v.currentTime);
          track.setAttribute('aria-valuenow', v.currentTime.toFixed(1));
          if (chapList) {
            var cur = 0; chapters.forEach(function (c, i) { if (v.currentTime >= c.t) cur = i; });
            $$('button', chapList).forEach(function (b, i) { b.classList.toggle('is-current', i === cur); });
          }
        });
      });
      big.addEventListener('click', function (e) { e.stopPropagation(); start(); });
      play.addEventListener('click', function (e) { e.stopPropagation(); var v = video(); if (v.paused) start(); else pause(); });
      $('.fig-media', fig).addEventListener('click', function (e) {
        if (e.target.closest('.player')) return;
        var v = video(); if (v.paused) start(); else pause();
      });
      function seek(clientX) {
        var r = track.getBoundingClientRect(), v = video();
        var d = v.duration || parseFloat(fig.getAttribute('data-duration'));
        v.currentTime = Math.max(0, Math.min(1, (clientX - r.left) / r.width)) * d;
      }
      track.addEventListener('pointerdown', function (e) {
        e.stopPropagation(); seek(e.clientX); track.setPointerCapture(e.pointerId);
        var move = function (ev) { seek(ev.clientX); };
        track.addEventListener('pointermove', move);
        track.addEventListener('pointerup', function upd() { track.removeEventListener('pointermove', move); track.removeEventListener('pointerup', upd); });
      });
      track.addEventListener('keydown', function (e) {
        var v = video();
        if (e.key === 'ArrowRight') { v.currentTime += 2; e.preventDefault(); }
        if (e.key === 'ArrowLeft') { v.currentTime -= 2; e.preventDefault(); }
      });
      var rates = [1, 0.5, 2];
      speed.addEventListener('click', function (e) {
        e.stopPropagation();
        var v = video(), i = (rates.indexOf(v.playbackRate) + 1) % rates.length;
        $$('video', fig).forEach(function (x) { x.playbackRate = rates[i]; });
        speed.textContent = rates[i] + '×';
      });
      document.addEventListener('bm-theme', function () {
        var was = $$('video', fig).some(function (v) { return !v.paused; });
        var t = 0; $$('video', fig).forEach(function (v) { if (!v.paused || v.currentTime) t = Math.max(t, v.currentTime); v.pause(); });
        var v = video(); if (t) { v.preload = 'auto'; v.currentTime = t; }
        if (was) start();
      });
      // Short clips play while in view; longer ones wait. Nothing moves with reduced motion.
      if (loop && !reduce() && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
          es.forEach(function (e) { if (e.isIntersecting) start(); else if (!video().paused) pause(); });
        }, { threshold: 0.6 }).observe(fig);
      }
    });
  })();

  /* --------------------------------------------------------- lightbox */
  (function lightbox() {
    var box = $('.lightbox'); if (!box) return;
    var body = $('.lightbox-body', box), last = null;
    function open(fig) {
      var pic = $$('picture', fig).filter(function (p) { return p.offsetParent !== null; })[0];
      if (!pic) return;
      last = document.activeElement;
      body.innerHTML = '';
      var clone = pic.cloneNode(true), img = $('img', clone);
      img.removeAttribute('loading');
      $$('source', clone).forEach(function (s) { s.removeAttribute('sizes'); s.setAttribute('sizes', img.getAttribute('width') + 'px'); });
      img.style.width = Math.min(parseInt(img.getAttribute('width'), 10), window.innerWidth * 0.96) + 'px';
      body.appendChild(clone);
      box.hidden = false; requestAnimationFrame(function () { box.classList.add('is-open'); });
      $('.lightbox-close', box).focus();
    }
    function close() { box.classList.remove('is-open'); setTimeout(function () { box.hidden = true; body.innerHTML = ''; }, 200); if (last) last.focus(); }
    $$('.fig-zoom').forEach(function (b) { b.addEventListener('click', function (e) { e.stopPropagation(); open(b.closest('.fig')); }); });
    $$('.fig:not(.fig--clip) .fig-media picture').forEach(function (p) {
      p.style.cursor = 'zoom-in';
      p.addEventListener('click', function () { open(p.closest('.fig')); });
    });
    $('.lightbox-close', box).addEventListener('click', close);
    box.addEventListener('click', function (e) { if (e.target === box) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !box.hidden) close(); });
  })();

  /* ----------------------------------------------------------- search */
  (function search() {
    var dlg = $('.search'); if (!dlg) return;
    var input = $('input', dlg), list = $('.search-results', dlg), empty = $('.search-empty', dlg);
    var index = null, sel = 0, last = null;
    function load() {
      if (index) return Promise.resolve(index);
      return fetch(root + 'static/search-index.json').then(function (r) { return r.json(); })
        .then(function (d) { index = d.map(function (e) { e.lt = (e.p + ' ' + e.h).toLowerCase(); e.lx = e.t.toLowerCase(); return e; }); return index; });
    }
    function open() {
      last = document.activeElement; dlg.hidden = false;
      requestAnimationFrame(function () { dlg.classList.add('is-open'); });
      input.value = ''; render([]); input.focus(); load();
    }
    function close() { dlg.classList.remove('is-open'); setTimeout(function () { dlg.hidden = true; }, 160); if (last) last.focus(); }
    function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    function mark(s, words) {
      var out = esc(s);
      words.forEach(function (w) { if (w.length > 1) out = out.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); });
      return out;
    }
    function snippet(text, words) {
      var lx = text.toLowerCase(), at = -1;
      words.forEach(function (w) { var i = lx.indexOf(w); if (i >= 0 && (at < 0 || i < at)) at = i; });
      if (at < 0) return text.slice(0, 160);
      var s = Math.max(0, at - 50);
      return (s ? '… ' : '') + text.slice(s, s + 170);
    }
    function query(q) {
      var words = q.toLowerCase().split(/\s+/).filter(Boolean);
      if (!words.length || !index) return [];
      var hits = [];
      index.forEach(function (e) {
        var score = 0, ok = true;
        words.forEach(function (w) {
          var inT = e.lt.indexOf(w) >= 0, inX = e.lx.indexOf(w) >= 0;
          if (!inT && !inX) ok = false;
          score += (inT ? 10 : 0) + (inX ? 1 : 0);
          if (e.h.toLowerCase().indexOf(w) === 0) score += 6;
        });
        if (ok) hits.push([score, e]);
      });
      hits.sort(function (a, b) { return b[0] - a[0]; });
      return hits.slice(0, 12).map(function (h) { return h[1]; });
    }
    function render(hits) {
      var words = input.value.toLowerCase().split(/\s+/).filter(Boolean);
      list.innerHTML = hits.map(function (e, i) {
        return '<li role="option"><a href="' + root + e.u + '"' + (i === 0 ? ' aria-selected="true"' : '') + '>' +
          '<span class="r-path">' + esc(e.s + ' / ' + e.p) + '</span>' +
          '<span class="r-title">' + mark(e.h || e.p, words) + '</span>' +
          '<span class="r-text">' + mark(snippet(e.t, words), words) + '</span></a></li>';
      }).join('');
      empty.hidden = !(input.value.trim() && !hits.length);
      sel = 0;
    }
    function move(d) {
      var as = $$('a', list); if (!as.length) return;
      as[sel].removeAttribute('aria-selected'); sel = (sel + d + as.length) % as.length;
      as[sel].setAttribute('aria-selected', 'true'); as[sel].scrollIntoView({ block: 'nearest' });
    }
    input.addEventListener('input', function () { load().then(function () { render(query(input.value)); }); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      if (e.key === 'Enter') { var a = $$('a', list)[sel]; if (a) location.href = a.href; }
      if (e.key === 'Escape') close();
    });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
    $$('[data-search-open]').forEach(function (b) { b.addEventListener('click', open); });
    document.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); if (dlg.hidden) open(); else close(); }
      if (e.key === '/' && dlg.hidden && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); open(); }
    });
  })();

  /* ----------------------------------------------- chapter progress */
  (function progress() {
    var key = 'bm-progress';
    var done = {};
    try { done = JSON.parse(store.get(key) || '{}'); } catch (e) {}
    function paint() {
      $$('[data-progress-key]').forEach(function (a) { a.classList.toggle('is-done', !!done[a.getAttribute('data-progress-key')]); });
      $$('[data-mark-done]').forEach(function (b) {
        var on = !!done[b.getAttribute('data-mark-done')];
        b.classList.toggle('is-done', on);
        $('[data-done-label]', b).textContent = on ? 'Done. Click to mark as not done' : 'Mark this chapter as done';
      });
    }
    $$('[data-mark-done]').forEach(function (b) {
      b.addEventListener('click', function () {
        var k = b.getAttribute('data-mark-done');
        if (done[k]) delete done[k]; else done[k] = 1;
        store.set(key, JSON.stringify(done)); paint();
      });
    });
    paint();
  })();

  /* ----------------------------------------------------------- reveal */
  (function reveal() {
    if (reduce() || !('IntersectionObserver' in window)) return;
    var items = $$('.fig, .cards, .reveal-on-scroll');
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0 });
    items.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight) return;  // already on screen: never hidden
      el.classList.add('reveal'); io.observe(el);
    });
  })();
})();
