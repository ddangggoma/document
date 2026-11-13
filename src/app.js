(function () {
  'use strict';
  var CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ';
  var PAGE = 40;
  // 찾아가는 길: 묶음 → 분류 → 소분류 → 낱말
  var GROUPS = [
    ['평가를 전할 때', [
      ['성과·긍정 평가', '좋은 결과를 과장 없이 전하는 말'],
      ['문제·위험·부정 평가', '나쁜 소식과 위험을 정확히 전하는 말']]],
    ['변화와 논리를 이을 때', [
      ['변화·추이·수량 표현', '늘고 줄고 머무는 것을 수치에 맞게 쓰는 말'],
      ['논리·연결·강조 표현', '원인, 결과, 대조, 조건을 잇는 말']]],
    ['할 일과 판단을 말할 때', [
      ['실행·절차·일정', '누가 언제 무엇을 하는지 밝히는 말'],
      ['판단·전망·제안', '확신의 정도를 구별해 의견을 내는 말']]],
    ['분야 용어를 찾을 때', [
      ['경영·전략·조직 용어', '전략, 사업 구조, 조직과 인사'],
      ['재무·회계·투자 용어', '손익, 자금, 원가, 투자 지표'],
      ['시장·고객·영업·생산 용어', '시장과 고객, 영업, 생산과 공급망'],
      ['기술·디지털·ESG·법무 용어', '디지털, 지속가능경영, 계약과 규제']]],
    ['기술전략팀이 찾을 때', [
      ['기술전략 용어', '로드맵, 과제 관리, 기술 확보, 특허, 사업화']]],
    ['고쳐 쓸 말을 찾을 때', [
      ['순화·교정 대상 표현', '번역투, 어려운 한자어, 군더더기, 헷갈리는 말']]]
  ];

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
  function hl(text, q) {
    if (!q) return esc(text);
    var i = text.toLowerCase().indexOf(q.toLowerCase());
    if (i < 0) return esc(text);
    return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + q.length)) + '</mark>' + esc(text.slice(i + q.length));
  }
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function transition(fn) {
    if (document.startViewTransition && !reduced) document.startViewTransition(fn); else fn();
  }

  /* ── <vocab-browser>: 어휘 사전 ── */
  class VocabBrowser extends HTMLElement {
    connectedCallback() {
      if (this._on) return; this._on = true;
      var start = this.init.bind(this);
      // 첫 화면을 막지 않도록 한가할 때 자료를 읽는다. 사전이 화면에 가까워지면 바로 읽는다.
      if ('requestIdleCallback' in window) requestIdleCallback(start, { timeout: 1500 }); else setTimeout(start, 200);
      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { io.disconnect(); start(); } }, { rootMargin: '1200px' });
        io.observe(this);
      }
    }

    init() {
      if (this.V) return;
      var src = document.getElementById(this.getAttribute('data-src') || 'vocab-data');
      var V = this.V = JSON.parse(src.textContent);
      var catOf = {}, tree = this.tree = {};
      GROUPS.forEach(function (g) { g[1].forEach(function (c) { catOf[c[0]] = g[0]; tree[c[0]] = { n: 0, subs: {}, order: [] }; }); });
      V.forEach(function (e, i) {
        e.rank = i + 1;
        e._w = norm(e.w); e._s = e.syn.map(norm); e._alt = norm(e.alt || '');
        e._rest = norm(e.m + e.sub + e.cat + e.tip);
        e._cw = cho(e._w); e._cs = e._s.map(cho);
        var t = tree[e.cat] || (tree[e.cat] = { n: 0, subs: {}, order: [] });
        t.n++;
        if (!t.subs[e.sub]) { t.subs[e.sub] = 0; t.order.push(e.sub); }
        t.subs[e.sub]++;
      });
      this.catOf = catOf;
      this.state = { q: '', cat: '', sub: '', tone: '', sort: 'f', shown: PAGE };
      this.current = [];
      this.render();
      this.run();
    }

    render() {
      var self = this, tree = this.tree, n = 0;
      var nav = '<button type="button" class="vb-node vb-root" data-cat="" aria-current="true">전체 <i>' + this.V.length.toLocaleString() + '</i></button>';
      GROUPS.forEach(function (g) {
        nav += '<div class="vb-group"><h4>' + esc(g[0]) + '</h4><ul>';
        g[1].forEach(function (c) {
          var t = tree[c[0]]; if (!t || !t.n) return;
          var id = 'vb-sub-' + (n++);
          nav += '<li><button type="button" class="vb-node" data-cat="' + esc(c[0]) + '" aria-expanded="false" aria-controls="' + id + '"><span>' + esc(c[0]) + '<small>' + esc(c[1]) + '</small></span><i>' + t.n + '</i></button>' +
            '<ul class="vb-subs" id="' + id + '" hidden>' + t.order.map(function (s) {
              return '<li><button type="button" class="vb-leaf" data-cat="' + esc(c[0]) + '" data-sub="' + esc(s) + '">' + esc(s) + ' <i>' + t.subs[s] + '</i></button></li>';
            }).join('') + '</ul></li>';
        });
        nav += '</ul></div>';
      });
      this.innerHTML =
        '<details class="vb-side"><summary>분류에서 찾아가기</summary><nav class="vb-tree" aria-label="분류">' + nav + '</nav></details>' +
        '<div class="vb-main">' +
          '<div class="vb-tools">' +
            '<label class="dict-search" for="dict-q"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>' +
            '<input id="dict-q" type="search" placeholder="낱말, 비슷한 말, 초성으로 찾기" autocomplete="off" aria-label="어휘 검색"><button type="button" id="dict-clear">지우기</button></label>' +
            '<nav class="vb-crumb" aria-label="현재 위치"></nav>' +
            '<div class="vb-filters"><div class="chips" role="group" aria-label="어감">' +
              ['', '긍정', '부정', '중립'].map(function (t) { return '<button type="button" class="chip" data-tone="' + t + '" aria-pressed="' + (t === '') + '">' + (t || '모든 어감') + '</button>'; }).join('') +
            '</div><div class="chips" role="group" aria-label="정렬">' +
              '<button type="button" class="chip" data-sort="f" aria-pressed="true">많이 쓰는 순</button><button type="button" class="chip" data-sort="a" aria-pressed="false">가나다순</button>' +
            '</div></div>' +
            '<p class="vb-count" aria-live="polite"></p>' +
          '</div>' +
          '<div class="dict-list"></div><div class="vb-sentinel" aria-hidden="true"></div>' +
          '<button type="button" class="dict-more" hidden>더 보기</button>' +
        '</div>';

      var $ = function (s) { return self.querySelector(s); };
      this.el = { side: $('.vb-side'), input: $('#dict-q'), crumb: $('.vb-crumb'), count: $('.vb-count'), list: $('.dict-list'), more: $('.dict-more'), sentinel: $('.vb-sentinel') };
      // 넓은 화면에서는 분류 나무를 늘 펼쳐 둔다.
      var wide = matchMedia('(min-width: 62rem)');
      var sync = function () { self.el.side.open = wide.matches; };
      sync(); if (wide.addEventListener) wide.addEventListener('change', sync);
      this.wide = wide;

      var timer;
      this.el.input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(function () { self.state.q = self.el.input.value; self.state.shown = PAGE; self.run(); }, 90);
      });
      this.addEventListener('click', function (ev) {
        var b = ev.target.closest('button'); if (!b || !self.contains(b)) return;
        var d = b.dataset, st = self.state;
        if (b.id === 'dict-clear') { self.el.input.value = ''; st.q = ''; self.el.input.focus(); }
        else if ('sub' in d) { st.cat = d.cat; st.sub = d.sub; if (!wide.matches) self.el.side.open = false; }
        else if ('cat' in d) { st.sub = ''; st.cat = d.cat; }
        else if ('tone' in d) st.tone = d.tone;
        else if ('sort' in d) st.sort = d.sort;
        else if ('q' in d) { self.el.input.value = d.q; st.q = d.q; st.cat = ''; st.sub = ''; self.scrollIntoView(); }
        else if ('all' in d) { st.cat = ''; st.sub = ''; }
        else if (b === self.el.more) { st.shown += PAGE; self.draw(); return; }
        else return;
        st.shown = PAGE;
        transition(function () { self.run(); });
      });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
          if (es[0].isIntersecting && self.state.shown < self.current.length) { self.state.shown += PAGE; self.draw(); }
        }, { rootMargin: '600px' }).observe(this.el.sentinel);
      }
    }

    score(e, q, isCho) {
      var i;
      if (isCho) {
        if (e._cw.indexOf(q) === 0) return 5;
        if (e._cw.indexOf(q) > 0) return 4;
        for (i = 0; i < e._cs.length; i++) if (e._cs[i].indexOf(q) >= 0) return 2;
        return 0;
      }
      if (e._w === q) return 6;
      if (e._w.indexOf(q) === 0) return 5;
      if (e._w.indexOf(q) > 0) return 4;
      for (i = 0; i < e._s.length; i++) { if (e._s[i] === q) return 3.5; if (e._s[i].indexOf(q) >= 0) return 3; }
      // 용언은 어간으로도 찾는다: '늘다' → '늘어나다', '늘리다'
      if (q.length >= 2 && q.charAt(q.length - 1) === '다') {
        var stem = q.slice(0, -1);
        if (e._w.indexOf(stem) === 0) return 2.8;
        for (i = 0; i < e._s.length; i++) if (e._s[i].indexOf(stem) === 0) return 2.5;
      }
      if (e._alt.indexOf(q) >= 0) return 2;
      if (e._rest.indexOf(q) >= 0) return 1;
      return 0;
    }

    run() {
      var st = this.state, V = this.V, q = norm(st.q.trim());
      var isCho = q.length > 0 && /^[ㄱ-ㅎ]+$/.test(q), res = [], outside = 0;
      for (var i = 0; i < V.length; i++) {
        var e = V[i], s = q ? this.score(e, q, isCho) : 1;
        if (!s) continue;
        if (st.tone && e.tone !== st.tone) continue;
        if ((st.cat && e.cat !== st.cat) || (st.sub && e.sub !== st.sub)) { outside++; continue; }
        e._sc = s; res.push(e);
      }
      if (st.sort === 'a') res.sort(function (a, b) { return a.w.localeCompare(b.w, 'ko'); });
      else if (q) res.sort(function (a, b) { return (b._sc - a._sc) || (a.rank - b.rank); });
      this.current = res; this.outside = outside;
      this.syncNav(); this.draw();
    }

    syncNav() {
      var st = this.state, self = this;
      this.querySelectorAll('.vb-node').forEach(function (b) {
        var on = b.dataset.cat === st.cat;
        if (b.classList.contains('vb-root')) { b.setAttribute('aria-current', String(!st.cat)); return; }
        b.setAttribute('aria-expanded', String(on));
        b.setAttribute('aria-current', String(on && !st.sub));
        document.getElementById(b.getAttribute('aria-controls')).hidden = !on;
      });
      this.querySelectorAll('.vb-leaf').forEach(function (b) { b.setAttribute('aria-current', String(b.dataset.cat === st.cat && b.dataset.sub === st.sub)); });
      this.querySelectorAll('[data-tone]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.tone === st.tone)); });
      this.querySelectorAll('[data-sort]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.sort === st.sort)); });
      var c = '<button type="button" data-all="1">전체</button>';
      if (st.cat) {
        c += '<span>' + esc(self.catOf[st.cat] || '') + '</span><button type="button" data-cat="' + esc(st.cat) + '" data-crumb="1">' + esc(st.cat) + '</button>';
        if (st.sub) c += '<b>' + esc(st.sub) + '</b>';
      }
      this.el.crumb.innerHTML = c;
    }

    card(e, q) {
      var bars = '', lv = Math.max(1, Math.ceil(e.f / 20));
      for (var i = 1; i <= 5; i++) bars += '<i' + (i <= lv ? ' class="on"' : '') + '></i>';
      var tone = e.tone === '긍정' ? ' pos' : e.tone === '부정' ? ' neg' : '';
      return '<article class="ent">' +
        '<div class="ent-h"><span class="ent-rank">' + e.rank + '</span><span class="ent-w">' + hl(e.w, q) + '</span>' +
        '<span class="ent-pos">' + esc(e.pos) + '</span><span class="tag' + tone + '">' + esc(e.tone) + '</span>' +
        '<span class="ent-f" title="사용 빈도 추정 ' + e.f + '/100" aria-label="사용 빈도 추정 ' + e.f + '점">' + bars + '</span></div>' +
        '<div class="ent-c"><button type="button" data-cat="' + esc(e.cat) + '">' + esc(e.cat) + '</button> › <button type="button" data-cat="' + esc(e.cat) + '" data-sub="' + esc(e.sub) + '">' + esc(e.sub) + '</button></div>' +
        '<p class="ent-m">' + hl(e.m, q) + '</p>' +
        '<p class="ent-ex">' + esc(e.ex) + '</p>' +
        (e.alt ? '<p class="ent-alt"><b>이렇게 바꿉니다</b> ' + hl(e.alt, q) + '</p>' : '') +
        (e.tip ? '<p class="ent-tip"><b>주의</b> ' + esc(e.tip) + '</p>' : '') +
        '<div class="ent-syn">' + e.syn.map(function (s) { return '<button type="button" data-q="' + esc(s) + '">' + hl(s, q) + '</button>'; }).join('') + '</div>' +
        '</article>';
    }

    draw() {
      var st = this.state, cur = this.current, q = st.q.trim();
      var n = Math.min(st.shown, cur.length), html = '';
      for (var i = 0; i < n; i++) html += this.card(cur[i], q);
      this.el.list.innerHTML = html || '<p class="dict-empty">맞는 말이 없습니다. 낱말의 일부(예: “증”)나 초성(예: “ㅊㅈ”), 비슷한 말로 다시 찾아보십시오.</p>';
      var where = st.sub || st.cat;
      var msg = (where ? '‘' + esc(where) + '’에서 ' : '') + '<b>' + cur.length.toLocaleString() + '</b>개';
      if (q && where && this.outside) msg += ' · 다른 분류에 ' + this.outside.toLocaleString() + '개 더 있습니다 <button type="button" data-all="1">전체에서 보기</button>';
      this.el.count.innerHTML = msg;
      this.el.more.hidden = n >= cur.length;
    }
  }
  if (window.customElements && !customElements.get('vocab-browser')) customElements.define('vocab-browser', VocabBrowser);

  /* ── 출처 번호를 누르면 그 자리에서 참고 자료를 보여 준다 (Popover API) ── */
  var pop = document.getElementById('ref-pop'), popY = 0;
  if (pop && 'showPopover' in pop) {
    document.addEventListener('click', function (ev) {
      var a = ev.target.closest('sup.ref a, .note cite a'); if (!a) return;
      var li = document.getElementById(a.getAttribute('href').slice(1)); if (!li) return;
      ev.preventDefault();
      pop.innerHTML = '<div class="ref-pop-n">참고 자료 ' + esc(a.textContent) + '</div>' + li.innerHTML + '<a class="ref-pop-go" href="' + a.getAttribute('href') + '">목록에서 보기</a>';
      pop.showPopover(); popY = scrollY;
      var r = a.getBoundingClientRect(), w = pop.offsetWidth, h = pop.offsetHeight;
      var x = Math.max(12, Math.min(r.left - 20, innerWidth - w - 12));
      var y = r.bottom + 8 + h > innerHeight ? Math.max(12, r.top - h - 8) : r.bottom + 8;
      pop.style.left = x + 'px'; pop.style.top = y + 'px';
    });
    pop.addEventListener('click', function (ev) { if (ev.target.closest('a')) pop.hidePopover(); });
    addEventListener('scroll', function () { if (Math.abs(scrollY - popY) > 80 && pop.matches(':popover-open')) pop.hidePopover(); }, { passive: true });
  }

  /* ── 상단 길잡이: 지금 읽는 장 표시 ── */
  var links = Array.prototype.slice.call(document.querySelectorAll('.bar-nav a'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (a) {
          var on = a.getAttribute('href') === '#' + en.target.id;
          a.classList.toggle('on', on);
          if (on) a.parentNode.scrollLeft = a.offsetLeft - 60;
        });
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    document.querySelectorAll('section.sheet[id]').forEach(function (s) { io.observe(s); });
  }
})();
