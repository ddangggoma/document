#!/usr/bin/env python3
"""별첨 문서(src/standalone/trend-report.html)를 만든다.
초안 → 1차 검토 → 개선판 → 2차 검토 → 완성본의 흐름과, 단계마다 받은 피드백과 조치를 한 문서로 엮는다.

  python3 make_flow.py [부록_URL 별첨_URL 바이블_URL]

읽는 것: src/report-versions/v1~v3.html, docs/reviews/r1a·r1b·r2a·r2b.json, reports/actions.py
"""
import html, json, sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).parent
esc = html.escape
URL_GUIDE, URL_REPORT, URL_BIBLE = sys.argv[1:4] if len(sys.argv) >= 4 else ("trend-guide.html", "trend-report.html", "index.html")
ver = lambda v: (ROOT / "src" / "report-versions" / f"{v}.html").read_text(encoding="utf-8")
rev = lambda k: json.loads((ROOT / "docs" / "reviews" / f"{k}.json").read_text(encoding="utf-8"))
spec = importlib.util.spec_from_file_location("actions", ROOT / "reports" / "actions.py"); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)

REVIEWS = [  # (열쇠, 단계, 짧은 이름)
 ("r1a", "1차 검토", "싱크탱크 수석연구원"),
 ("r1b", "1차 검토", "연구소장 출신 기술 임원"),
 ("r2a", "2차 검토", "CEO 보좌 경영기획 임원"),
 ("r2b", "2차 검토", "교열 전문가"),
]
R = {k: rev(k) for k, _, _ in REVIEWS}
total = lambda d: (sum(s["score"] for s in d["scores"]), sum(s["max"] for s in d["scores"]))
STATUS_CLS = {"반영": "pos", "부분 반영": "", "미반영": "neg"}

def persona_block(key, name):
    d = R[key]; got, mx = total(d)
    rows = "".join(f"<tr><td>{esc(s['item'])}</td><td class=\"num-col\">{s['score']} / {s['max']}</td><td>{esc(s['reason'])}</td></tr>" for s in d["scores"])
    strengths = "".join(f"<li>{esc(x)}</li>" for x in d["strengths"])
    issues = ""
    for it in d["issues"]:
        st, note = A.ACTIONS[(key, it["id"])]
        after = "".join(f"<li>{esc(x)}</li>" for x in it["after"])
        issues += (f'<details class="issue"><summary><span class="mk">{it["id"]}</span><b>{esc(it["title"])}</b>'
                   f'<span class="tag {"neg" if it["level"] == "상" else ""}">중요도 {esc(it["level"])}</span><span class="tag {STATUS_CLS[st]}">{st}</span>'
                   f'<span class="issue-loc">{esc(it["where"])}</span></summary>'
                   f'<p><b>문제.</b> {esc(it["problem"])}</p><p><b>왜 문제인가.</b> {esc(it["why"])}</p>'
                   f'<div class="fix"><div class="b">{esc(it["before"]).replace(chr(10), "<br>")}</div><div class="g"><ul class="gj">{after}</ul></div>'
                   f'<div class="y act">{esc(note)}</div></div></details>')
    return (f'<div class="persona"><div class="persona-h"><div><h4>{esc(name)}</h4><p>{esc(d["persona"])}</p><p class="lens">본 것: {esc(d["lens"])}</p></div>'
            f'<div class="persona-score"><b>{got}</b><span>/ {mx}</span></div></div>'
            f'<p class="verdict">{esc(d["verdict"])}</p><p>{esc(d["overall"])}</p>'
            f'<div class="tbl"><table><thead><tr><th>항목</th><th>점수</th><th>사유</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<h5>잘된 점</h5><ul>{strengths}</ul><h5>지적 {len(d["issues"])}건과 조치</h5><p class="hint">제목을 누르면 고치기 전 문구, 검토자가 고친 문구, 작성자의 조치가 펼쳐진다.</p>{issues}</div>')

def log_rows():
    out = ""
    for key, stage, name in REVIEWS:
        for it in R[key]["issues"]:
            st, note = A.ACTIONS[(key, it["id"])]
            out += (f'<tr><td>{stage}</td><td>{esc(name)}</td><td class="num-col">{it["id"]}</td><td>{esc(it["level"])}</td><td>{esc(it["title"])}</td>'
                    f'<td><span class="tag {STATUS_CLS[st]}">{st}</span></td><td>{esc(note)}</td></tr>')
    return out
counts = {}
for key, _, _ in REVIEWS:
    for it in R[key]["issues"]:
        s = A.ACTIONS[(key, it["id"])][0]; counts[s] = counts.get(s, 0) + 1
n_issues = sum(counts.values())

def questions():
    out = ""
    for key, _, name in REVIEWS:
        for q in R[key].get("questions", []):
            out += f"<tr><td>{esc(name)}</td><td>{esc(q['q'])}</td><td>{esc(q['a'])}</td></tr>"
    return out

def steps():
    cards = [("초안", "작성자", "바이블의 원칙으로 처음 쓴 판", "#s1"),
             ("1차 검토", "두 페르소나", f"{total(R['r1a'])[0]}/{total(R['r1a'])[1]} · {total(R['r1b'])[0]}/{total(R['r1b'])[1]}", "#s2"),
             ("개선판", "작성자", "줄거리와 사례의 정확성을 고친 판", "#s3"),
             ("2차 검토", "다른 두 페르소나", f"{total(R['r2a'])[0]}/{total(R['r2a'])[1]} · {total(R['r2b'])[0]}/{total(R['r2b'])[1]}", "#s4"),
             ("완성본", "작성자", "읽히는 정도와 문장을 고친 판", "#final")]
    return '<ol class="flow">' + "".join(f'<li><a href="{h}"><b>{a}</b><span>{b}</span><small>{c}</small></a></li>' for a, b, c, h in cards) + "</ol>"

def bullets(items):
    return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

nums = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td><td>{esc(d)}</td></tr>" for a, b, c, d in A.NUMS)
N, DONE = len(A.NUMS), sum(1 for x in A.NUMS if x[3] == "확인")

nav = [("#final", "완성본"), ("#flow", "작성 과정"), ("#s2", "1차 검토"), ("#s4", "2차 검토"), ("#log", "피드백 대장"), ("#lessons", "얻은 원칙"), (URL_GUIDE, "부록: 쓰는 법"), (URL_BIBLE, "바이블")]
page = f'''<!-- title: AI 에이전트 R&D 동향 보고 -->
<header class="bar"><div class="bar-in"><a class="bar-name" href="#top">별첨: 동향 보고서가 완성되기까지</a>
<nav class="bar-nav" aria-label="이동">{"".join(f'<a href="{h}">{t}</a>' for h, t in nav)}</nav></div></header>
<main class="wrap">
<section class="sheet" id="top">
<div class="folio"><span>보고서 작성 바이블 · 별첨</span><span>동향 보고서 실례</span></div>
<header class="open">
  <div class="num" style="font-size:clamp(3.2rem,8vw,6rem);line-height:1">별첨</div>
  <div>
    <h2>AI 에이전트 R&D 자동화 동향 보고서: 초안에서 완성본까지</h2>
    <p class="stand">다음 주 경영회의에 올리는 참고 보고라는 상황을 두고 동향 보고서 한 편을 썼다. 초안을 쓰고, 서로 다른 눈을 가진 검토자 네 명에게 두 차례 검토받고, 그때마다 고쳤다. 완성본을 먼저 싣고, 단계마다 어떤 지적을 받아 무엇을 고쳤는지를 차례로 싣는다.</p>
  </div>
  <div class="gist">
    <h3>한눈에</h3>
    <ol>
      <li>줄거리는 세 부분. 개념과 현황, 분야별 사례, 한계와 인사이트.</li>
      <li>검토는 두 차례, 검토자는 네 명. 지적 {n_issues}건 가운데 반영 {counts.get("반영", 0)}건, 부분 반영 {counts.get("부분 반영", 0)}건, 미반영 {counts.get("미반영", 0)}건.</li>
      <li>완성본은 A4 4쪽, 표 2개. 같은 내용의 Word 파일이 저장소에 있다.</li>
      <li>수치 {N}건 가운데 원문을 직접 확인한 것은 {DONE}건. 보고 전 대조 필수.</li>
    </ol>
  </div>
</header>
<div class="prose">
<div class="box warn"><h4>검토자에 관하여</h4><p>검토자 네 명은 모두 <b>역할을 맡긴 가상의 검토자(AI)</b>이고, 각자 별도 세션에서 서로의 의견을 보지 않고 검토했다. 삼성글로벌리서치 수석연구원, 대기업 중앙연구소장 출신 기술 임원, CEO를 보좌하는 경영기획 임원, 교열 전문가의 눈을 빌렸다. 실제 기관이나 인물의 의견이 아니다.</p></div>
<div class="box warn"><h4>보고 전에 반드시 할 일</h4><ul>
<li>수치와 날짜는 2026년 11월 14일 웹 검색 결과의 요약을 근거로 했다. 별지 1의 □ 표시 수치를 원문에서 확인하고, 확인되지 않으면 삭제하거나 ‘(미대조)’로 표시한다.</li>
<li>대괄호 자리(당사 자동화 과제 수, 보고일)를 채운다.</li>
<li>표 2의 단계 판정은 공개 발표에 근거한 추정이다.</li>
</ul></div>
</div>
</section>

<section class="sheet" id="final">
<div class="folio"><span>별첨</span><span>완성본 (A4 4쪽)</span></div>
<div class="prose"><h3>완성본</h3><p>두 차례 검토를 반영한 마지막 판이다. 같은 내용의 Word 파일은 저장소의 <code>docs/AI에이전트_RnD자동화_동향보고.docx</code>다.</p></div>
{ver("v3")}
</section>

<section class="sheet" id="flow">
<div class="folio"><span>별첨</span><span>작성 과정</span></div>
<div class="prose">
<h3>작성 과정: 다섯 걸음</h3>
<p>한 번에 완성되는 보고서는 없다. 쓰는 사람과 읽는 사람의 눈이 다르기 때문이다. 이 보고서는 아래 순서로 만들었다. 검토 단계의 숫자는 검토자가 매긴 점수다.</p>
</div>
{steps()}
<div class="prose">
<h4>검토를 두 번으로 나눈 까닭</h4>
<p>큰 것부터 고친다는 퇴고의 원칙(바이블 8장)을 검토에도 적용했다. 1차 검토는 줄거리와 내용의 정확성을 봤고, 2차 검토는 읽히는 정도와 문장을 봤다. 줄거리가 바뀔 글의 문장을 먼저 다듬으면 헛일이 된다.</p>
</div>
</section>

<section class="sheet" id="s1">
<div class="folio"><span>별첨</span><span>1단계 초안</span></div>
<div class="prose">
<h3>1단계. 초안</h3>
<p>보고를 지시한 사람이 정한 줄거리(개념과 현황, 분야별 사례, 한계와 인사이트)를 그대로 절로 삼고, 바이블의 원칙대로 썼다.</p>
{bullets(A.DRAFT_NOTES)}
<details class="ver"><summary>초안 전문 보기 (A4 4쪽)</summary>{ver("v1")}</details>
</div>
</section>

<section class="sheet" id="s2">
<div class="folio"><span>별첨</span><span>2단계 1차 검토</span></div>
<div class="prose">
<h3>2단계. 1차 검토: 줄거리와 내용의 정확성</h3>
<p>두 검토자 모두 “그대로는 상정할 수 없고 보완하면 가능하다”고 판정했다. 한 사람은 짜임을, 한 사람은 사례의 조건을 짚었고, 인사이트의 근거 없는 수치는 두 사람이 따로 같은 곳을 지적했다.</p>
</div>
{persona_block("r1a", "싱크탱크 수석연구원")}
{persona_block("r1b", "연구소장 출신 기술 임원")}
</section>

<section class="sheet" id="s3">
<div class="folio"><span>별첨</span><span>3단계 개선판</span></div>
<div class="prose">
<h3>3단계. 개선판: 1차 검토로 고친 것</h3>
{bullets(A.V2_NOTES)}
<details class="ver"><summary>개선판 전문 보기 (A4 4쪽)</summary>{ver("v2")}</details>
</div>
</section>

<section class="sheet" id="s4">
<div class="folio"><span>별첨</span><span>4단계 2차 검토</span></div>
<div class="prose">
<h3>4단계. 2차 검토: 읽히는 정도와 문장</h3>
<p>{esc(A.R2_INTRO)}</p>
</div>
{persona_block("r2a", "CEO 보좌 경영기획 임원")}
{persona_block("r2b", "교열 전문가")}
</section>

<section class="sheet" id="s5">
<div class="folio"><span>별첨</span><span>5단계 완성본</span></div>
<div class="prose">
<h3>5단계. 완성본: 2차 검토로 고친 것</h3>
{bullets(A.V3_NOTES)}
<p>완성본은 <a href="#final">이 문서의 맨 앞</a>에 실었다.</p>
</div>
</section>

<section class="sheet" id="log">
<div class="folio"><span>별첨</span><span>피드백 대장</span></div>
<div class="prose">
<h3>피드백 대장: 지적 {n_issues}건과 조치</h3>
<p>받은 지적을 하나도 빠뜨리지 않고 적고, 반영했는지와 그 이유를 남겼다. 받아들이지 않은 지적에도 이유를 적는다. 검토자의 말이 늘 옳은 것은 아니고, 지면과 지시받은 줄거리라는 제약도 있다.</p>
<div class="tbl wide"><table>
<thead><tr><th>단계</th><th>검토자</th><th>번호</th><th>중요도</th><th>지적</th><th>조치</th><th>조치 내용</th></tr></thead>
<tbody>{log_rows()}</tbody></table></div>
</div>
</section>

<section class="sheet" id="lessons">
<div class="folio"><span>별첨</span><span>얻은 원칙</span></div>
<div class="prose">
<h3>이 과정에서 얻은 원칙</h3>
<ol class="rules">{"".join(f"<li><div><b>{a}</b><p>{b}</p></div></li>" for a, b in A.LESSONS)}</ol>
<div class="box tip"><h4>검토를 맡기는 법</h4><p>검토자에게 세 가지를 정해 주었다. 누구의 눈으로 읽을지(역할), 무엇을 볼지(관점. 다른 검토자가 볼 것은 빼 준다), 무엇을 돌려받을지(항목별 점수, 지적마다 고치기 전과 고친 뒤의 문구, 회의에서 던질 질문). 사람에게 검토를 부탁할 때에도 이 세 가지를 정해 주면 바로 쓸 수 있는 의견이 돌아온다. 검토자끼리는 서로의 의견을 보지 않게 했다. 따로 본 두 사람이 같은 곳을 짚으면 그곳은 반드시 고쳐야 하는 곳이다.</p></div>
</div>
</section>

<section class="sheet" id="annex">
<div class="folio"><span>별첨</span><span>별지</span></div>
<div class="prose">
<h3>별지 1. 수치별 출처와 원문 대조 ({N}건 중 {DONE}건 대조 완료)</h3>
<div class="tbl wide"><table>
<thead><tr><th>수치·사실</th><th>출처</th><th>등급</th><th>대조</th></tr></thead>
<tbody>{nums}</tbody>
<caption>‘확인’은 원문 페이지를 직접 열어 본 것. □는 검색 요약으로만 확인한 것. 대조하지 못한 수치는 보고 전에 삭제하거나 본문 같은 줄에 ‘(미대조)’ 표기.</caption></table></div>
<h3>별지 2. 검토자들이 던진 질문과 답</h3>
<p>검토자마다 회의에서 던질 질문을 적게 했다. 보고서가 답하지 못하는 질문은 무엇을 확인해야 하는지를 적었다. 보고 전에 이 답을 준비한다.</p>
<div class="tbl wide"><table>
<thead><tr><th>묻는 사람</th><th>질문</th><th>답</th></tr></thead>
<tbody>{questions()}</tbody></table></div>
</div>
</section>
</main>
'''
out = ROOT / "src" / "standalone" / "trend-report.html"
out.write_text(page, encoding="utf-8")
print(f"별첨 생성: 지적 {n_issues}건 {counts}, 수치 {N}건")
