(function () {
  'use strict';
  var V = window.VOCAB || [];
  var PAGE = 60;
  var CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ';

  function norm(s) { return String(s).toLowerCase().replace(/[\s·\/\-~(),.]/g, ''); }
  function cho(s) {
    var out = '';
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i) - 0xAC00;
      out += (c >= 0 && c < 11172) ? CHO[Math.floor(c / 588)] : s[i];
    }
    return out;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // 검색용 색인: 표제어, 유사어, 나머지를 따로 두어 순위를 매긴다.
  V.forEach(function (e, i) {
    e.rank = i + 1;
    e._w = norm(e.w);
    e._s = e.syn.map(norm);
    e._alt = norm(e.alt || '');
    e._rest = norm(e.m + e.sub + e.cat + e.tip);
    e._cw = cho(e._w);
    e._cs = e._s.map(cho);
  });

  function score(e, q, isCho) {
    if (isCho) {
      if (e._cw.indexOf(q) === 0) return 5;
      if (e._cw.indexOf(q) > 0) return 4;
      for (var k = 0; k < e._cs.length; k++) if (e._cs[k].indexOf(q) >= 0) return 2;
      return 0;
    }
    if (e._w === q) return 6;
    if (e._w.indexOf(q) === 0) return 5;
    if (e._w.indexOf(q) > 0) return 4;
    for (var j = 0; j < e._s.length; j++) {
      if (e._s[j] === q) return 3.5;
      if (e._s[j].indexOf(q) >= 0) return 3;
    }
    // 용언은 어간으로도 찾는다: '늘다' → '늘어나다', '늘리다'
    if (q.length >= 2 && q.charAt(q.length - 1) === '다') {
      var st = q.slice(0, -1);
      if (e._w.indexOf(st) === 0) return 2.8;
      for (var k2 = 0; k2 < e._s.length; k2++) if (e._s[k2].indexOf(st) === 0) return 2.5;
    }
    if (e._alt.indexOf(q) >= 0) return 2;
    if (e._rest.indexOf(q) >= 0) return 1;
    return 0;
  }

  var state = { q: '', cat: '', tone: '', shown: PAGE };
  var $ = function (id) { return document.getElementById(id); };
  var input = $('dict-q'), list = $('dict-list'), more = $('dict-more'), meta = $('dict-count');
  if (!input) return;

  function hl(text, q) {
    var t = esc(text);
    if (!q || q.length < 1) return t;
    var i = text.toLowerCase().indexOf(q.toLowerCase());
    if (i < 0) return t;
    return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + q.length)) + '</mark>' + esc(text.slice(i + q.length));
  }

  function card(e, q) {
    var bars = '';
    var lv = Math.max(1, Math.ceil(e.f / 20));
    for (var i = 1; i <= 5; i++) bars += '<i' + (i <= lv ? ' class="on"' : '') + '></i>';
    var tone = e.tone === '긍정' ? ' pos' : e.tone === '부정' ? ' neg' : '';
    return '<article class="ent">' +
      '<div class="ent-h"><span class="ent-rank">' + e.rank + '</span><span class="ent-w">' + hl(e.w, q) + '</span>' +
      '<span class="ent-pos">' + esc(e.pos) + '</span><span class="tag' + tone + '">' + esc(e.tone) + '</span>' +
      '<span class="ent-f" title="사용 빈도 추정 ' + e.f + '/100" aria-label="사용 빈도 추정 ' + e.f + '점">' + bars + '</span></div>' +
      '<div class="ent-c">' + esc(e.cat) + ' › ' + esc(e.sub) + '</div>' +
      '<p class="ent-m">' + hl(e.m, q) + '</p>' +
      '<p class="ent-ex">' + esc(e.ex) + '</p>' +
      (e.alt ? '<p class="ent-alt"><b>이렇게 바꿉니다</b> ' + hl(e.alt, q) + '</p>' : '') +
      (e.tip ? '<p class="ent-tip"><b>주의</b> ' + esc(e.tip) + '</p>' : '') +
      '<div class="ent-syn">' + e.syn.map(function (s) { return '<button type="button" data-q="' + esc(s) + '">' + hl(s, q) + '</button>'; }).join('') + '</div>' +
      '</article>';
  }

  var current = [];
  function run() {
    var raw = state.q.trim(), q = norm(raw);
    var isCho = q.length > 0 && /^[ㄱ-ㅎ]+$/.test(q);
    var res = [];
    for (var i = 0; i < V.length; i++) {
      var e = V[i];
      if (state.cat && e.cat !== state.cat) continue;
      if (state.tone && e.tone !== state.tone) continue;
      if (!q) { res.push(e); continue; }
      var s = score(e, q, isCho);
      if (s > 0) { e._sc = s; res.push(e); }
    }
    // 검색어가 있으면 일치 정도 → 빈도 순, 없으면 빈도 순(원래 순서).
    if (q) res.sort(function (a, b) { return (b._sc - a._sc) || (a.rank - b.rank); });
    current = res;
    draw(raw);
  }
  function draw(raw) {
    var n = Math.min(state.shown, current.length);
    var html = '';
    for (var i = 0; i < n; i++) html += card(current[i], raw);
    list.innerHTML = html || '<p class="dict-empty">맞는 말이 없습니다. 단어의 일부(예: "증")나 초성(예: "ㅊㅈ"), 비슷한 말로 다시 찾아보십시오.</p>';
    meta.innerHTML = '<b>' + current.length.toLocaleString() + '</b>개 가운데 <b>' + n.toLocaleString() + '</b>개를 보고 있습니다';
    more.hidden = n >= current.length;
  }

  function chips(el, key, values) {
    el.innerHTML = values.map(function (v) {
      return '<button type="button" class="chip" data-v="' + esc(v[0]) + '" aria-pressed="' + (state[key] === v[0]) + '">' + esc(v[1]) + (v[2] != null ? '<i>' + v[2] + '</i>' : '') + '</button>';
    }).join('');
    el.onclick = function (ev) {
      var b = ev.target.closest('button'); if (!b) return;
      state[key] = b.dataset.v; state.shown = PAGE;
      el.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      run();
    };
  }
  var cats = {}, order = [];
  V.forEach(function (e) { if (!cats[e.cat]) { cats[e.cat] = 0; order.push(e.cat); } cats[e.cat]++; });
  order.sort(function (a, b) { return cats[b] - cats[a] || a.localeCompare(b, 'ko'); });
  chips($('dict-cats'), 'cat', [['', '모든 분류', V.length]].concat(order.map(function (c) { return [c, c, cats[c]]; })));
  chips($('dict-tones'), 'tone', [['', '모든 어감'], ['긍정', '긍정'], ['부정', '부정'], ['중립', '중립']]);

  var timer;
  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () { state.q = input.value; state.shown = PAGE; run(); }, 80);
  });
  $('dict-clear').addEventListener('click', function () { input.value = ''; state.q = ''; state.shown = PAGE; run(); input.focus(); });
  more.addEventListener('click', function () { state.shown += PAGE * 2; draw(state.q.trim()); });
  list.addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-q]'); if (!b) return;
    input.value = b.dataset.q; state.q = b.dataset.q; state.shown = PAGE; run();
    $('dict').scrollIntoView();
  });
  run();

  // 상단 길잡이: 지금 읽는 장 표시
  var links = Array.prototype.slice.call(document.querySelectorAll('.bar-nav a'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) {
          var on = a.getAttribute('href') === '#' + en.target.id;
          a.classList.toggle('on', on);
          if (on && a.scrollIntoView) a.parentNode.scrollLeft = a.offsetLeft - 60;
        });
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    document.querySelectorAll('section.sheet[id]').forEach(function (s) { io.observe(s); });
  }
})();
