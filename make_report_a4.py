#!/usr/bin/env python3
"""동향 보고서 A4 4쪽판을 만든다. 같은 내용으로 HTML 조각과 Word 파일을 낸다.

  python3 make_report_a4.py   ->  src/trend-report-a4.html, docs/AI에이전트_RnD자동화_동향보고.docx

내용은 PAGES 한 곳에만 적는다.
  ("h", 절 제목) / ("head", 헤드 메시지) / ("b", 항목, [하위 항목…]) / ("fig",) / ("table",) / ("note", 글)
  문장 속 {n} 은 그 쪽의 n번째 주석 번호다.
"""
import html, re
from pathlib import Path

ROOT = Path(__file__).parent
TITLE = "AI 에이전트, 코드·설계부터 ‘업무 흐름 위임’ 이행 시작"
SUB = "과제별 자동화 이후의 변화와 당사가 먼저 갖출 것"
META = "참고 보고(결정 요청 부재) · 기술전략팀 · 2026. 11. [보고일]"
SERIES = "기술전략 이슈 보고"

SUMMARY = [
 ("변화", "에이전트가 맡는 과제 길이, 1년 새 1시간대 → 약 12시간(독립 평가). 적용 분야는 코드에서 설계·실험으로 확산"),
 ("한계", "실행은 가속, 검증은 정체. 공개된 효과 수치는 대부분 회사 발표, 독립 검증된 R&D 생산성 수치는 미확인"),
 ("위치", "당사는 4단계 중 2단계(과제 자동화). 선도 AI 연구소도 3단계 초입, 국내 주요 기업은 선언·계획 단계"),
 ("시사점", "자동화된 과제를 잇기 전에 권한 설계 → 기준선 측정 → 검증 체계 → 비용 한도 순으로 정비"),
 ("다음 결정", "2027년 1분기 재보고 시 시범 과제 범위와 비용 한도안의 상정 여부 판단"),
]

STEPS = [  # 그림 1
 ("1단계", "도구 보조", "사람이 작업 중 AI에 묻고 답을 받아 쓰는 형태", "작성자", "기업 다수"),
 ("2단계", "과제 자동화", "정해진 과제 하나를 AI가 처음부터 끝까지 수행", "과제 정의, 결과 확인", "당사 · 국내 제조사의 설계 최적화"),
 ("3단계", "업무 흐름 위임", "자동화된 과제 여럿을 에이전트가 이어서 수행", "목표 설정, 검토·승인", "선도 AI 연구소의 코드·연구 실행 영역"),
 ("4단계", "자율 연구", "연구 질문 설정과 결과 해석까지 AI가 수행", "감독", "도달 기업 미확인"),
]
ORDER = [  # 표 1
 ("1", "권한 설계", "되돌릴 수 없는 사고를 막는 조건. 과제 연결 이전 완료 대상", "[부서], [분기]"),
 ("2", "효과 측정 기준선", "도입 뒤에는 잴 수 없는 항목. 현행 과제의 소요 기간·재작업률 확보", "[부서], [분기]"),
 ("3", "검증 체계", "과제별 평가 세트와 사람 승인 지점. 승인은 되돌릴 수 없는 행동에 한정", "[부서], [분기]"),
 ("4", "비용 한도", "1인당·과제당 한도와 모델 등급 배정 규칙. 시범 운영 착수 시 적용", "[부서], [분기]"),
 ("병행", "기여 기록", "특허는 사람의 실질적 기여를 요구. 연구 노트 절차에 반영", "[부서], [분기]"),
]

PAGES = [
 {"blocks": [
   ("h", "1. 무엇이 달라졌나"),
   ("head", "에이전트가 맡는 일의 단위가 ‘작업’에서 ‘과제’로 확대"),
   ("b", "에이전트가 절반의 확률로 완수하는 과제 길이, 2025년 초 1시간대 → 2026년 초 약 12시간(독립 평가){1}",
        ["80% 성공 기준으로는 약 1.5시간, 높은 신뢰가 필요한 업무에 맡길 수 있는 길이는 아직 짧은 수준",
         "측정 대상은 소프트웨어 과제, 다른 분야에 그대로 적용하기에는 한계"]),
   ("b", "OpenAI, 숙련 연구자가 며칠 걸릴 연구 과제를 AI가 완수하는 단계에 도달했다고 발표(2026년 9월, 회사 발표, 외부 미검증)", []),
   ("head", "적용 분야가 코드에서 설계와 실험으로 확산"),
   ("b", "코드: 전문 개발자의 90%가 주 1회 이상 코딩 에이전트 사용(설문){2}",
        ["Google은 신규 코드의 75%, Anthropic은 병합 코드의 80% 이상을 AI가 작성(회사 발표){3}",
         "두 수치는 정의가 달라 직접 비교 불가, 개발 속도 향상과 동일시 불가"]),
   ("b", "설계: 반도체 설계 도구 3사가 2026년에 모두 에이전트형 제품 발표",
        ["삼성전자, HBM4 개발 리드타임 약 50% 단축(회사 발표, 기준선 미공개)"]),
   ("b", "실험: 자율 실험실은 투자 약정과 계획 단계, 가동 성과 수치는 미공개",
        ["Lilly·NVIDIA 최대 10억 달러 공동 연구소 발표, LG AI연구원 2026년 말 가동 계획(회사 발표)"]),
  ],
  "notes": ["METR, 과제 길이 측정(2026. 5.). 숙련자가 걸리는 시간으로 잰 과제 길이", "JetBrains 개발자 조사(2026. 5.~7.)", "Google Cloud Next(2026. 4.), Anthropic Institute(2026. 5. 기준)"]},
 {"blocks": [
   ("head", "병목이 ‘실행’에서 ‘검증’으로 이동"),
   ("b", "코드 산출은 증가, 전달은 정체(공급사 분석). AI는 조직의 기존 강점과 약점을 증폭(설문){1}", []),
   ("b", "연구 에이전트의 정확도, 데이터 분석 85.5%·문헌 조사 82.1%인 반면 종합·해석은 57.9%(개발사 측 평가){2}", []),
   ("b", "근거는 소프트웨어 개발 중심, 설계·실험 분야의 근거는 미확인", []),
   ("h", "2. 어디까지 왔나"),
   ("head", "R&D 자동화 4단계: 당사는 2단계, 선도 기업도 3단계 초입"),
   ("fig",),
   ("b", "3단계 진입은 AI 연구소의 코드·연구 실행 영역에 한정, 근거는 모두 회사 발표", []),
   ("b", "기업 전반은 실험 단계: 에이전트 확대 적용은 어느 기능에서도 10% 이하(설문), 에이전트 프로젝트의 40% 이상이 2027년 말까지 취소될 전망{3}", []),
   ("b", "2단계에서 3단계로 넘어갈 때 필요한 것은 모델 성능보다 검증·권한·비용 통제라는 판단", []),
   ("head", "최근 화제가 된 사례: 실행은 통과, 연구 판단은 미달"),
   ("b", "AI Scientist(Sakana AI 외): AI가 쓴 논문 3편 중 1편이 학회 워크숍 심사 통과(2026년 3월, 학술지 게재). 본 학회 수준에는 미달", []),
   ("b", "AI co-scientist(Google): 가설 생성 AI의 제안이 시험관 실험으로 확인(2026년 5월, 학술지 게재)", []),
   ("b", "열린 연구 과제 독립 평가: 에이전트가 코드 작성과 실험은 사람 도움 없이 완수, 연구 결과물은 6점 만점에 2점과 1점(2026년 7월, 대상 2편)", []),
   ("b", "Cadence·NVIDIA: 반도체 설계 검증 5주 → 약 하루(공급사 발표, 독립 비교 기준 부재)", []),
   ("b", "LG AI연구원: 후보 물질 42만여 개에서 하루 만에 소재 후보 도출(회사 발표, 탐색 단계의 속도)", []),
  ],
  "notes": ["LinearB(풀 리퀘스트 810만 건 분석), DORA 2025(약 5,000명 설문)", "Kosmos 논문(2025. 11.)", "McKinsey(2025. 11.), Gartner(2025. 6.)"]},
 {"blocks": [
   ("h", "3. 무엇을 조심해야 하나"),
   ("head", "연구 활동의 단계마다 맡길 수 있는 범위가 다름"),
   ("b", "맡길 수 있는 일: 문헌 조사, 데이터 분석, 계산 실험, 문서 초안. 공통점은 결과의 자동 채점 가능", []),
   ("b", "보조로 쓸 일: 가설 제시, 설계 최적화. 채택 판단은 연구자 몫", []),
   ("b", "사람이 쥘 일: 종합·해석, 연구 방향 판단. 물리 실험의 자동화는 관찰 대상", []),
   ("head", "효과는 과장되기 쉽고, 사고는 넓은 권한에서 발생"),
   ("b", "생산성의 엄밀한 측정 부재: 숙련 개발자 작업 속도 약 19% 저하(2025년 자료, 독립 평가){1}",
        ["측정 기관은 현재는 더 빨라졌을 가능성을 인정, 다만 크기에 대한 증거는 미약하다는 입장"]),
   ("b", "과장 사례: AI의 수학 미해결 문제 풀이 발표 삭제(2025년 10월), 신소재 발견 44% 증가 논문의 철회 요청(2025년 5월)", []),
   ("b", "사고 사례: 에이전트가 운영 데이터베이스와 백업을 9초 만에 삭제(2026년 4월), 보안 평가 중 격리 환경 이탈(2026년 7월){2}",
        ["공통 원인은 필요 이상으로 넓은 권한"]),
   ("b", "비용: Uber, 연간 AI 코딩 예산을 4월에 소진하고 1인당 월 1,500달러 한도 도입(보도)", []),
   ("head", "국내는 선언·계획 단계, 규제 부담은 당분간 제한적"),
   ("b", "삼성전자, 3월 설계~제조 에이전트 통합 전략 발표·9월 ‘에이전틱 시프트’ 포럼 개최. SK하이닉스, 2월 AI 기반 R&D 전환 선언(회사 발표)", []),
   ("b", "정부, 2030년 연구 생산성 2배 목표(K-문샷). 2027년 AI 예산안 9.4조 원(국회 심의 중)", []),
   ("b", "인공지능기본법 2026년 1월 시행, 제재는 유예 중. 사내 연구용 에이전트는 고영향 범주 밖일 가능성(법무 확인 필요)", []),
   ("b", "특허 발명자는 사람만 인정(미국·한국·유럽), 에이전트 작업에서 사람의 기여 기록 필요", []),
   ("head", "인력은 감원보다 역할 이동"),
   ("b", "엔지니어의 역할, 작성에서 검토·승인으로 이동. 대형 기술기업의 신규 졸업자 채용은 2019년 대비 약 65% 낮은 수준(보도, 경기 요인 미분리)", []),
   ("b", "R&D 조직의 인력 영향을 엄밀하게 잰 연구는 미확인", []),
  ],
  "notes": ["METR 무작위 대조 실험(2025. 7. 발표), 후속 공지(2026)", "피해 기업 창업자 공개 글, 보안 매체 보도(양사 인정)"]},
 {"blocks": [
   ("h", "4. 당사에 주는 뜻"),
   ("head", "당사는 2단계, 쟁점은 격차보다 이행 순서"),
   ("b", "당사 과제별 자동화는 [ ]건 완료·[ ]건 진행, 4단계 중 2단계", []),
   ("b", "과제별 자동화로 쌓은 절차, 데이터, 도구 연결은 3단계의 바탕", []),
   ("b", "자동화된 과제를 잇기 전에 아래 순서로 정비 필요", []),
   ("table",),
   ("head", "전망이 갈려도 유효한 준비부터"),
   ("b", "세 경우 상정: 가속(연구 판단까지 자동화), 실행만 가속(기준), 조정(비용·사고로 도입 축소)", []),
   ("b", "권한 설계, 기준선 측정, 기여 기록은 세 경우 모두 유효", []),
   ("b", "과제 연결 범위와 실험 설비 투자는 신호를 확인한 뒤 결정", []),
   ("head", "지켜볼 신호와 다음 결정"),
   ("b", "외부 신호: 독립 검증된 R&D 기간 단축 수치 공개, 자율 실험실 가동 성과, 주요 기업의 사용 한도 확산", []),
   ("b", "내부 신호: 자동화 과제의 사람 검토 시간 비중 [ ]%, 과제당 AI 사용 비용 [ ]원", []),
   ("b", "이번 보고의 결정 요청 사항은 부재", []),
   ("b", "2027년 1분기 재보고 시 시범 과제 범위와 비용 한도안의 상정 여부 판단 예정",
        ["그 전까지 [담당 부서]가 권한 설계 현황과 기준선 측정 결과 준비"]),
   ("note", "이 보고서의 수치 40건 가운데 원문 대조를 마친 것은 1건. 나머지는 보고 전 대조 대상이며 목록은 별지에 수록. 4단계 위치는 공개 발표에 근거한 추정."),
  ],
  "notes": []},
]

SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
esc = html.escape
def h_txt(t):
    return re.sub(r"\{(\d)\}", lambda m: f"<sup>{m.group(1)})</sup>", esc(t))

# ───────── HTML ─────────
def fig_html():
    cols = "".join(
        f'<div class="st st{i+1}{" me" if i == 1 else ""}"><b>{a}</b><strong>{b}</strong><p>{esc(c)}</p><dl><dt>사람의 역할</dt><dd>{esc(d)}</dd><dt>현재 위치(추정)</dt><dd>{esc(e)}</dd></dl></div>'
        for i, (a, b, c, d, e) in enumerate(STEPS))
    return f'<figure class="w-fig"><figcaption>그림 1. R&D 자동화 4단계와 현재 위치</figcaption><div class="steps">{cols}</div></figure>'
def table_html():
    rows = "".join(f"<tr><td>{a}</td><td>{esc(b)}</td><td>{esc(c)}</td><td>{esc(d)}</td></tr>" for a, b, c, d in ORDER)
    return f'<table class="w-tbl"><caption>표 1. 과제 연결 전 정비 순서</caption><thead><tr><th>순위</th><th>갖출 것</th><th>이 순서인 이유</th><th>담당·시기</th></tr></thead><tbody>{rows}</tbody></table>'

def page_html(i, pg):
    out = []
    if i == 0:
        out.append(f'<div class="w-title"><h3>{esc(TITLE)}</h3><p class="w-sub">{esc(SUB)}</p><p class="w-meta">{esc(META)}</p></div>')
        out.append('<div class="w-sum"><b>요약</b><ul>' + "".join(f"<li><em>{a}</em>{esc(b)}</li>" for a, b in SUMMARY) + "</ul></div>")
    open_ul = False
    for blk in pg["blocks"]:
        kind = blk[0]
        if kind != "b" and open_ul: out.append("</ul>"); open_ul = False
        if kind == "h": out.append(f'<h4 class="w-h">{esc(blk[1])}</h4>')
        elif kind == "head": out.append(f'<p class="w-head">{esc(blk[1])}</p>')
        elif kind == "fig": out.append(fig_html())
        elif kind == "table": out.append(table_html())
        elif kind == "note": out.append(f'<p class="w-note">{esc(blk[1])}</p>')
        else:
            if not open_ul: out.append('<ul class="w">'); open_ul = True
            sub = "<ul>" + "".join(f"<li>{h_txt(s)}</li>" for s in blk[2]) + "</ul>" if blk[2] else ""
            out.append(f"<li>{h_txt(blk[1])}{sub}</li>")
    if open_ul: out.append("</ul>")
    notes = '<ol class="w-fn">' + "".join(f"<li>{esc(n)}</li>" for n in pg["notes"]) + "</ol>" if pg["notes"] else ""
    return (f'<div class="a4"><div class="a4-in"><div class="w-run"><span>{SERIES}</span><span>{esc(TITLE)}</span></div>'
            + "".join(out) + f'</div><div class="a4-foot">{notes}<p class="w-pg">- {i+1} -</p></div></div>')

frag = '<div class="a4-wrap" aria-label="동향 보고서 A4 4쪽판">' + "".join(page_html(i, p) for i, p in enumerate(PAGES)) + "</div>"
(ROOT / "src" / "trend-report-a4.html").write_text(frag, encoding="utf-8")

# ───────── Word ─────────
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BLUE, INK, GREY = RGBColor(0x1B, 0x3F, 0xC4), RGBColor(0x14, 0x1B, 0x2B), RGBColor(0x50, 0x5A, 0x6B)
FONT = "맑은 고딕"
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Mm(210), Mm(297)
sec.left_margin = sec.right_margin = Mm(20); sec.top_margin = Mm(18); sec.bottom_margin = Mm(16)
st = doc.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
st.paragraph_format.space_after = Pt(0); st.paragraph_format.line_spacing = 1.22

def run(p, text, bold=False, size=None, color=None, sup=False):
    r = p.add_run(text); r.bold = bold
    if size: r.font.size = Pt(size)
    if color is not None: r.font.color.rgb = color
    r.font.superscript = sup
    r.font.name = FONT; r._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    return r
def rich(p, text, **kw):
    for part in re.split(r"(\{\d\})", text):
        if re.fullmatch(r"\{\d\}", part): run(p, part[1] + ")", sup=True, **kw)
        elif part: run(p, part, **kw)
def shade(cell, hexcolor):
    tcPr = cell._element.get_or_add_tcPr(); s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), hexcolor); tcPr.append(s)
def border(p, side="bottom", size=12, color="141B2B"):
    pPr = p._p.get_or_add_pPr(); b = OxmlElement("w:pBdr"); e = OxmlElement(f"w:{side}")
    e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(size)); e.set(qn("w:space"), "2"); e.set(qn("w:color"), color)
    b.append(e); pPr.append(b)
def para(space_before=0, space_after=0, indent=0, hang=0, align=None):
    p = doc.add_paragraph(); f = p.paragraph_format
    f.space_before, f.space_after = Pt(space_before), Pt(space_after)
    if indent: f.left_indent = Mm(indent)
    if hang: f.first_line_indent = Mm(-hang)
    if align: p.alignment = align
    return p
def cell_text(cell, text, bold=False, size=9, color=None, align=None):
    p = cell.paragraphs[0]; p.paragraph_format.line_spacing = 1.1
    if align: p.alignment = align
    run(p, text, bold=bold, size=size, color=color); return p

# 머리띠
p = para(); run(p, SERIES, bold=True, size=9, color=BLUE); border(p, "bottom", 18, "1B3FC4")
p = para(space_before=10); run(p, TITLE, bold=True, size=18, color=INK)
p = para(space_before=2); run(p, SUB, size=11.5, color=GREY)
p = para(space_before=3, space_after=7); run(p, META, size=9, color=GREY)
# 요약 상자
t = doc.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = "Table Grid"
c = t.rows[0].cells[0]; shade(c, "F1F3F8")
cell_text(c, "요약", bold=True, size=10, color=BLUE)
for a, b in SUMMARY:
    q = c.add_paragraph(); q.paragraph_format.left_indent = Mm(4); q.paragraph_format.first_line_indent = Mm(-4); q.paragraph_format.line_spacing = 1.18
    run(q, "□ ", size=9.5); run(q, f"({a}) ", bold=True, size=9.5); run(q, b, size=9.5)

def fig_docx():
    p = para(space_before=4, space_after=2); run(p, "그림 1. R&D 자동화 4단계와 현재 위치", bold=True, size=9, color=GREY)
    t = doc.add_table(rows=3, cols=4); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (a, b, c, d, e) in enumerate(STEPS):
        top = t.rows[0].cells[i]; shade(top, "1B3FC4" if i == 1 else "E3E9FA")
        cell_text(top, f"{a}  {b}", bold=True, size=9.5, color=RGBColor(255, 255, 255) if i == 1 else INK, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_text(t.rows[1].cells[i], c, size=8.5)
        cc = t.rows[2].cells[i]; q = cc.paragraphs[0]; q.paragraph_format.line_spacing = 1.1
        run(q, "사람의 역할: ", bold=True, size=8.5); run(q, d, size=8.5)
        q = cc.add_paragraph(); q.paragraph_format.line_spacing = 1.1
        run(q, "현재 위치(추정): ", bold=True, size=8.5); run(q, e, size=8.5, bold=(i == 1), color=BLUE if i == 1 else None)
    para(space_after=2)
def table_docx():
    p = para(space_before=4, space_after=2); run(p, "표 1. 과제 연결 전 정비 순서", bold=True, size=9, color=GREY)
    t = doc.add_table(rows=1, cols=4); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = [Mm(13), Mm(32), Mm(95), Mm(30)]
    for i, hh in enumerate(["순위", "갖출 것", "이 순서인 이유", "담당·시기"]):
        shade(t.rows[0].cells[i], "E3E9FA"); cell_text(t.rows[0].cells[i], hh, bold=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    for row in ORDER:
        cells = t.add_row().cells
        for i, v in enumerate(row): cell_text(cells[i], v, bold=(i == 1), size=9, align=WD_ALIGN_PARAGRAPH.CENTER if i in (0, 3) else None)
    for r in t.rows:
        for i, w in enumerate(widths): r.cells[i].width = w
    para(space_after=2)

for i, pg in enumerate(PAGES):
    for blk in pg["blocks"]:
        kind = blk[0]
        if kind == "h":
            p = para(space_before=11, space_after=3); run(p, blk[1], bold=True, size=13, color=BLUE); border(p, "bottom", 8, "1B3FC4")
        elif kind == "head":
            p = para(space_before=7, space_after=3); run(p, "▣ " + blk[1], bold=True, size=10.5, color=INK)
        elif kind == "fig": fig_docx()
        elif kind == "table": table_docx()
        elif kind == "note":
            p = para(space_before=8); run(p, "※ " + blk[1], size=8.5, color=GREY); border(p, "top", 6, "9AA3B2")
        else:
            p = para(space_before=1.5, indent=5, hang=5); run(p, "□ "); rich(p, blk[1])
            for s in blk[2]:
                q = para(indent=10, hang=4); run(q, "- ", color=GREY); rich(q, s, color=GREY)
    if pg["notes"]:
        p = para(space_before=6); border(p, "top", 4, "9AA3B2")
        for k, n in enumerate(pg["notes"], 1):
            if k > 1: p = para()
            run(p, f"{k}) {n}", size=8, color=GREY)
    if i < len(PAGES) - 1: doc.add_page_break()

# 바닥글 쪽 번호
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run(); r.font.size = Pt(8.5)
for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
    if tag:
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tag)
    else:
        e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
    r._r.append(e)
(ROOT / "docs").mkdir(exist_ok=True)
out = ROOT / "docs" / "AI에이전트_RnD자동화_동향보고.docx"
doc.save(out)
print("HTML 조각과 Word 파일 생성:", out.name)
