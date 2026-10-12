/* Driftless Workforce Group — site behavior: menu toggle and the shared form handler. */
(function () {
  'use strict';

  // Set this to the Google Apps Script web app address (the "Forms" deployment) to make forms live.
  var ENDPOINT = (document.documentElement.getAttribute('data-endpoint') || '').trim();
  var PREVIEW = !!document.querySelector('meta[name="driftless-mode"][content="preview"]');
  var PHONE = (document.documentElement.getAttribute('data-phone') || '').trim();
  var MAX_FILE = 5 * 1024 * 1024;
  var FILE_TYPES = ['pdf', 'doc', 'docx', 'rtf', 'txt', 'odt'];

  // ---------- Menu ----------
  var menuBtn = document.querySelector('.menu-btn');
  var nav = document.getElementById('site-nav');
  if (menuBtn && nav) {
    var setOpen = function (open) {
      menuBtn.setAttribute('aria-expanded', String(open));
      nav.setAttribute('data-open', String(open));
    };
    var mq = window.matchMedia('(max-width: 1040px)');
    var sync = function () { if (mq.matches) setOpen(false); else nav.setAttribute('data-open', 'true'); };
    sync();
    if (mq.addEventListener) mq.addEventListener('change', sync);
    menuBtn.addEventListener('click', function () { setOpen(menuBtn.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menuBtn.getAttribute('aria-expanded') === 'true') { setOpen(false); menuBtn.focus(); }
    });
  }

  // ---------- Forms ----------
  var forms = document.querySelectorAll('form[data-form]');
  Array.prototype.forEach.call(forms, initForm);

  function initForm(form) {
    var started = Date.now();
    form.setAttribute('novalidate', '');
    if (!ENDPOINT && !PREVIEW) closedNotice(form, false);
    // Clear a field's error as soon as it is fixed.
    form.addEventListener('input', function (e) { var f = e.target.closest('.field'); if (f && f.classList.contains('has-error')) validateField(f); });
    form.addEventListener('change', function (e) { var f = e.target.closest('.field'); if (f && f.classList.contains('has-error')) validateField(f); });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var fields = form.querySelectorAll('.field');
      var problems = [];
      Array.prototype.forEach.call(fields, function (f) {
        var msg = validateField(f);
        if (msg) problems.push({ id: firstControlId(f), msg: msg });
      });
      showSummary(form, problems);
      if (problems.length) return;

      var btn = form.querySelector('button[type="submit"]');
      var label = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      clearFail(form);

      collect(form, started).then(function (payload) {
        if (!ENDPOINT) return PREVIEW ? { preview: true } : { closed: true };
        return fetch(ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain;charset=utf-8' },
          body: JSON.stringify(payload)
        }).then(function (r) { return r.json(); });
      }).then(function (res) {
        if (res && res.closed) return closedNotice(form, true);
        if (res && (res.ok || res.preview)) return done(form, !!res.preview);
        throw new Error((res && res.error) || 'not saved');
      }).catch(function () {
        fail(form);
      }).then(function () {
        if (btn) { btn.disabled = false; btn.textContent = label; }
      });
    });
  }

  function firstControlId(field) {
    var c = field.querySelector('input:not([type="hidden"]), select, textarea');
    return c ? c.id : '';
  }

  function validateField(field) {
    var msg = '';
    var optional = field.hasAttribute('data-optional');
    var kind = field.getAttribute('data-kind');
    var name = field.getAttribute('data-label') || 'this';
    if (kind === 'checks') {
      var any = field.querySelector('input[type="checkbox"]:checked');
      if (!any && !optional) msg = field.getAttribute('data-msg') || ('Choose at least one option for ' + name.toLowerCase() + '.');
    } else if (kind === 'consent') {
      var box = field.querySelector('input[type="checkbox"]');
      if (box && !box.checked) msg = field.getAttribute('data-msg') || 'Tick this box to continue.';
    } else if (kind === 'file') {
      var inp = field.querySelector('input[type="file"]');
      var file = inp && inp.files && inp.files[0];
      if (!file && !optional) msg = 'Attach a file.';
      if (file) {
        var ext = (file.name.split('.').pop() || '').toLowerCase();
        if (FILE_TYPES.indexOf(ext) < 0) msg = 'Attach a PDF or Word file.';
        else if (file.size > MAX_FILE) msg = 'That file is over 5 MB. Attach a smaller file.';
      }
    } else {
      var c = field.querySelector('input, select, textarea');
      var v = c ? c.value.trim() : '';
      if (!v && !optional) msg = field.getAttribute('data-msg') || ('Enter ' + name.toLowerCase() + '.');
      else if (v && c.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) msg = 'Enter an email address like name@company.com.';
      else if (v && c.type === 'tel' && v.replace(/\D/g, '').length < 10) msg = 'Enter a 10-digit phone number.';
      else if (v && c.getAttribute('pattern') && !new RegExp('^(?:' + c.getAttribute('pattern') + ')$').test(v)) msg = field.getAttribute('data-pattern-msg') || 'Check the format.';
      else if (v && c.type === 'number') {
        var n = Number(v), mn = c.min !== '' ? Number(c.min) : null, mx = c.max !== '' ? Number(c.max) : null;
        if (!isFinite(n) || (mn !== null && n < mn) || (mx !== null && n > mx)) msg = 'Enter a number from ' + c.min + ' to ' + c.max + '.';
      }
    }
    setError(field, msg);
    return msg;
  }

  function setError(field, msg) {
    var box = field.querySelector('.error-msg');
    var controls = field.querySelectorAll('input, select, textarea');
    if (msg) {
      field.classList.add('has-error');
      if (!box) {
        box = document.createElement('p');
        box.className = 'error-msg';
        box.id = (field.id || ('f' + Math.random().toString(36).slice(2))) + '-err';
        var hint = field.querySelector('.hint');
        var anchor = field.querySelector('.choices, .file-drop, .consent') || field.querySelector('input, select, textarea');
        if (hint && hint.nextSibling) field.insertBefore(box, hint.nextSibling); else field.insertBefore(box, anchor);
      }
      box.textContent = msg;
      Array.prototype.forEach.call(controls, function (c) {
        c.setAttribute('aria-invalid', 'true');
        addDescribed(c, box.id);
      });
    } else {
      field.classList.remove('has-error');
      Array.prototype.forEach.call(controls, function (c) { c.removeAttribute('aria-invalid'); if (box) removeDescribed(c, box.id); });
      if (box) box.remove();
    }
  }
  function addDescribed(c, id) { var d = (c.getAttribute('aria-describedby') || '').split(' ').filter(Boolean); if (d.indexOf(id) < 0) d.unshift(id); c.setAttribute('aria-describedby', d.join(' ')); }
  function removeDescribed(c, id) { var d = (c.getAttribute('aria-describedby') || '').split(' ').filter(function (x) { return x && x !== id; }); if (d.length) c.setAttribute('aria-describedby', d.join(' ')); else c.removeAttribute('aria-describedby'); }

  function showSummary(form, problems) {
    var old = form.querySelector('.error-summary');
    if (old) old.remove();
    if (!problems.length) return;
    var box = document.createElement('div');
    box.className = 'error-summary';
    box.setAttribute('role', 'alert');
    box.setAttribute('tabindex', '-1');
    var h = document.createElement('h3');
    h.textContent = problems.length === 1 ? 'One thing to fix before sending' : problems.length + ' things to fix before sending';
    box.appendChild(h);
    var ul = document.createElement('ul');
    problems.forEach(function (p) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + p.id;
      a.textContent = p.msg;
      a.addEventListener('click', function (e) { e.preventDefault(); var el = document.getElementById(p.id); if (el) { el.focus(); el.scrollIntoView({ block: 'center' }); } });
      li.appendChild(a);
      ul.appendChild(li);
    });
    box.appendChild(ul);
    form.insertBefore(box, form.firstChild);
    box.focus();
  }

  function collect(form, started) {
    var data = {};
    var file = null;
    Array.prototype.forEach.call(form.elements, function (el) {
      if (!el.name || el.disabled) return;
      if (el.type === 'file') { if (el.files && el.files[0]) file = el.files[0]; return; }
      if (el.type === 'checkbox') {
        if (el.getAttribute('data-single') === 'true') { data[el.name] = el.checked ? 'Yes' : 'No'; return; }
        if (!data[el.name]) data[el.name] = [];
        if (el.checked) data[el.name].push(el.value);
        return;
      }
      if (el.type === 'radio') { if (el.checked) data[el.name] = el.value; return; }
      data[el.name] = el.value.trim();
    });
    Object.keys(data).forEach(function (k) { if (Array.isArray(data[k])) data[k] = data[k].join(', '); });
    var payload = {
      form: form.getAttribute('data-form'),
      page: location.pathname.split('/').pop() || 'index.html',
      elapsed: Math.round((Date.now() - started) / 1000),
      fields: data
    };
    if (!file) return Promise.resolve(payload);
    return new Promise(function (resolve, reject) {
      var r = new FileReader();
      r.onload = function () {
        var s = String(r.result);
        payload.file = { name: file.name, type: file.type || 'application/octet-stream', data: s.slice(s.indexOf(',') + 1) };
        resolve(payload);
      };
      r.onerror = function () { reject(new Error('file')); };
      r.readAsDataURL(file);
    });
  }

  function done(form, preview) {
    var panel = document.getElementById(form.getAttribute('data-done'));
    if (!panel) return;
    form.hidden = true;
    panel.hidden = false;
    var note = panel.querySelector('.notice.preview');
    if (note) note.hidden = !preview;
    var h = panel.querySelector('h3');
    if (h) { h.setAttribute('tabindex', '-1'); h.focus(); }
  }

  function fail(form) {
    clearFail(form);
    var box = document.createElement('p');
    box.className = 'notice fail';
    box.setAttribute('role', 'alert');
    var alt = form.getAttribute('data-fallback');
    box.textContent = 'Something went wrong and your message was not sent. Please try again in a minute.' + (alt ? ' ' + alt : '');
    var actions = form.querySelector('.form-actions');
    form.insertBefore(box, actions);
  }
  // Until the forms backend is connected, the live site says so plainly and points to the phone.
  function closedNotice(form, focus) {
    var box = form.querySelector('.notice.closed');
    if (!box) {
      box = document.createElement('p');
      box.className = 'notice closed';
      box.setAttribute('role', 'status');
      box.setAttribute('tabindex', '-1');
      box.appendChild(document.createTextNode('Online requests open soon. Until then, please call or text Casey' + (PHONE ? ' at ' : '.')));
      if (PHONE) {
        var a = document.createElement('a');
        a.href = 'tel:+1' + PHONE.replace(/\D/g, '');
        a.textContent = PHONE;
        box.appendChild(a);
        box.appendChild(document.createTextNode('.'));
      }
      form.insertBefore(box, form.firstChild);
    }
    if (focus) { box.focus(); box.scrollIntoView({ block: 'center' }); }
  }
  function clearFail(form) { var b = form.querySelector('.notice.fail'); if (b) b.remove(); }

  // "Send another" buttons
  Array.prototype.forEach.call(document.querySelectorAll('[data-reset]'), function (b) {
    b.addEventListener('click', function () {
      var form = document.getElementById(b.getAttribute('data-reset'));
      var panel = b.closest('.form-done');
      if (!form || !panel) return;
      form.reset();
      panel.hidden = true;
      form.hidden = false;
      var first = form.querySelector('.field input, .field select, .field textarea');
      if (first) first.focus();
    });
  });
})();
