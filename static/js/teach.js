/* Interactive exercises of the BIDS chapter: build a file name, valid or not,
 * which folder, which sidecar values apply. Every fact comes from the page
 * (generated from the BIDS schema); without JavaScript the same facts are
 * shown as tables and answers. Everything works with the keyboard, and
 * nothing moves unless effects are on. */
(function () {
  'use strict';
  var doc = document.documentElement;
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function data(box) { var s = $('script[type="application/json"]', box); return s ? JSON.parse(s.textContent) : {}; }
  var still = function () { return doc.getAttribute('data-fx') === 'off' || doc.getAttribute('data-motion') === 'reduce'; };

  /* ------------------------------------------------ build a file name */
  $$('[data-teach="builder"]').forEach(function (box) {
    var d = data(box), kinds = d.kinds || [];
    var ui = el('div', 'tb-ui');
    var pick = el('div', 'tb-kinds'); pick.setAttribute('role', 'radiogroup'); pick.setAttribute('aria-label', 'Kind of file');
    var ents = el('div', 'tb-ents');
    var out = el('div', 'tb-out'); out.setAttribute('aria-live', 'polite');
    var path = el('p', 'tb-path');
    var name = el('p', 'tb-name');
    var note = el('p', 'tb-note');
    out.appendChild(path); out.appendChild(name); out.appendChild(note);
    ui.appendChild(pick); ui.appendChild(ents); ui.appendChild(out);
    box.appendChild(ui);
    var state = { k: 1, on: {}, val: {} };
    kinds.forEach(function (k, i) {
      var b = el('button', 'tb-kind', k.datatype + '/' + k.suffix);
      b.type = 'button'; b.setAttribute('role', 'radio'); b.title = k.label;
      b.addEventListener('click', function () { choose(i); });
      b.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); choose((i + 1) % kinds.length, true); }
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); choose((i - 1 + kinds.length) % kinds.length, true); }
      });
      pick.appendChild(b);
    });
    function choose(i, focus) {
      state.k = i;
      $$('.tb-kind', pick).forEach(function (b, j) { b.setAttribute('aria-checked', String(i === j)); b.tabIndex = i === j ? 0 : -1; });
      if (focus) $$('.tb-kind', pick)[i].focus();
      var k = kinds[i];
      ents.innerHTML = '';
      k.entities.filter(function (e) { return e.offer || e.required; }).forEach(function (e) {
        if (!(e.entity in state.on)) state.on[e.entity] = e.required || e.entity === 'session';
        if (!(e.entity in state.val)) state.val[e.entity] = e.example || '';
        var row = el('label', 'tb-ent' + (e.required ? ' is-required' : ''));
        var cb = el('input'); cb.type = 'checkbox'; cb.checked = e.required || state.on[e.entity]; cb.disabled = e.required;
        cb.setAttribute('aria-label', 'Use ' + e.name);
        var key = el('code', 'tb-key', e.key + '-');
        var inp = el('input', 'tb-val'); inp.type = 'text'; inp.value = state.val[e.entity]; inp.spellcheck = false;
        inp.setAttribute('aria-label', e.name + ' (' + (e.format === 'index' ? 'a number' : 'letters and digits') + ')');
        var hint = el('span', 'tb-hint', e.format === 'index' ? 'index' : 'label');
        if (e.required) hint.textContent += ', required';
        cb.addEventListener('change', function () { state.on[e.entity] = cb.checked; render(); });
        inp.addEventListener('input', function () { state.val[e.entity] = inp.value; if (!cb.checked && inp.value) { cb.checked = true; state.on[e.entity] = true; } render(); });
        row.appendChild(cb); row.appendChild(key); row.appendChild(inp); row.appendChild(hint);
        ents.appendChild(row);
      });
      render();
    }
    function render() {
      var k = kinds[state.k], parts = [], bad = [];
      k.entities.forEach(function (e) {
        if (!(e.offer || e.required)) return;
        var on = e.required || state.on[e.entity];
        if (!on) return;
        var v = state.val[e.entity] || '';
        var ok = new RegExp('^(' + e.pattern + ')$').test(v);
        if (!v) bad.push(e.name + ' needs a value');
        else if (!ok) bad.push(e.name + ' is ' + (e.format === 'index' ? 'an index: a number only' : 'a label: letters and digits only (no space, hyphen or underscore)'));
        parts.push({ key: e.key, v: v, ok: ok && !!v, entity: e.entity });
      });
      name.innerHTML = '';
      parts.forEach(function (p) {
        var t = el('span', 'tb-tok' + (p.ok ? '' : ' is-bad'));
        t.appendChild(el('span', 'tb-tk', p.key + '-')); t.appendChild(el('span', 'tb-tv', p.v || '?'));
        name.appendChild(t); name.appendChild(el('span', 'tb-sep', '_'));
      });
      name.appendChild(el('span', 'tb-suffix', k.suffix)); name.appendChild(el('span', 'tb-ext', k.extension));
      var sub = 'sub-' + (state.val.subject || '?'), ses = (state.on.session && state.val.session) ? 'ses-' + state.val.session + '/' : '';
      path.textContent = sub + '/' + ses + k.datatype + '/';
      note.className = 'tb-note ' + (bad.length ? 'is-bad' : 'is-ok');
      note.textContent = bad.length ? bad.join('. ') + '.' : 'A valid name. The entities are written in the standard’s order, whatever order you fill them in.';
    }
    box.classList.add('is-live');
    choose(1);
  });

  /* ------------------------------------------------- valid or not? */
  $$('[data-teach="quiz"]').forEach(function (box) {
    var score = $('.tq-score', box), right = 0, done = 0, items = $$('.tq-item', box);
    items.forEach(function (li) {
      var btns = $('.tq-buttons', li), ans = $('.tq-answer', li);
      btns.hidden = false;
      ans.classList.add('is-hidden');
      $$('button', btns).forEach(function (b) {
        b.addEventListener('click', function () {
          if (li.classList.contains('is-done')) return;
          var good = b.getAttribute('data-answer') === li.getAttribute('data-ok');
          li.classList.add('is-done', good ? 'is-right' : 'is-wrong');
          b.classList.add('is-chosen');
          $$('button', btns).forEach(function (x) { x.disabled = true; });
          ans.classList.remove('is-hidden'); ans.open = true;
          done++; if (good) right++;
          score.hidden = false;
          score.textContent = right + ' of ' + done + ' right' + (done === items.length ? '. All answered.' : '');
        });
      });
    });
    box.classList.add('is-live');
  });

  /* ---------------------------------------------------- which folder? */
  $$('[data-teach="place"]').forEach(function (box) {
    var d = data(box), files = d.place || [], i = 0, right = 0;
    var ui = el('div', 'tp-ui');
    var file = el('p', 'tp-file');
    var opts = el('div', 'tp-folders'); opts.setAttribute('role', 'group'); opts.setAttribute('aria-label', 'Folders');
    var msg = el('p', 'tp-msg'); msg.setAttribute('aria-live', 'polite');
    var next = el('button', 'tp-next', 'Next file'); next.type = 'button'; next.hidden = true;
    ui.appendChild(file); ui.appendChild(opts); ui.appendChild(msg); ui.appendChild(next);
    box.appendChild(ui);
    (d.folders || []).forEach(function (f) {
      var b = el('button', 'tp-folder', f + '/'); b.type = 'button'; b.setAttribute('data-f', f);
      b.addEventListener('click', function () { answer(f, b); });
      opts.appendChild(b);
    });
    function show() {
      var f = files[i];
      file.innerHTML = ''; file.appendChild(el('span', 'tp-label', 'File ' + (i + 1) + ' of ' + files.length)); file.appendChild(el('code', null, f.name));
      $$('.tp-folder', opts).forEach(function (b) { b.disabled = false; b.className = 'tp-folder'; });
      msg.textContent = ''; next.hidden = true;
    }
    function answer(f, b) {
      var want = files[i].folder, good = want.indexOf(f) >= 0;
      if (good) right++;
      b.classList.add(good ? 'is-right' : 'is-wrong');
      $$('.tp-folder', opts).forEach(function (x) { x.disabled = true; if (want.indexOf(x.getAttribute('data-f')) >= 0) x.classList.add('is-answer'); });
      msg.textContent = (good ? 'Right: ' : 'Not quite: ') + 'it goes in ' + want[0] + '/. ' +
        (i === files.length - 1 ? right + ' of ' + files.length + ' right.' : '');
      next.hidden = i === files.length - 1;
      if (!next.hidden) next.focus();
    }
    next.addEventListener('click', function () { i++; show(); $('.tp-folder', opts).focus(); });
    box.classList.add('is-live');
    show();
  });

  /* ------------------------------------------- which values apply? */
  $$('[data-teach="inherit"]').forEach(function (box) {
    var runs = $$('.ti-run', box), panels = $$('.ti-panel', box);
    function pick(id) {
      runs.forEach(function (r) { r.setAttribute('aria-pressed', String(r.getAttribute('data-ti') === id)); });
      panels.forEach(function (p) { p.hidden = p.getAttribute('data-for') !== id; });
      $$('.ti-file', box).forEach(function (f) {
        var t = f.getAttribute('data-ti');
        f.classList.toggle('is-used', t === 'top' || (t === 'sub01' && id === 'r01'));
      });
    }
    runs.forEach(function (r) { r.addEventListener('click', function () { pick(r.getAttribute('data-ti')); }); });
    box.classList.add('is-live');
    pick('r01');
  });
})();
