#!/usr/bin/env python3
"""A4 발간물 형식의 보고서를 HTML 조각, Word 파일, 검토용 글로 만든다.

보고서 내용은 dict 하나다.
  title, sub, meta, series, summary: [(이름표, 글)], pages: [{"blocks": [...], "notes": [...]}]
블록
  ("h", 절 제목) / ("head", 헤드 메시지) / ("b", 항목, [하위 항목…])
  ("table", 표 제목, [머리글…], [[칸…]…], [열 너비 mm…]) / ("note", 글)
문장 속 {n} 은 그 쪽의 n번째 주석 번호다.
"""
import html, re
from pathlib import Path

esc = html.escape
def _h(t):
    return re.sub(r"\{(\d)\}", lambda m: f"<sup>{m.group(1)})</sup>", esc(t))

# ───────── HTML ─────────
def to_html(doc, label="보고서"):
    def table(cap, head, rows, widths):
        th = "".join(f"<th>{esc(x)}</th>" for x in head)
        tr = "".join("<tr>" + "".join(f"<td>{_h(c)}</td>" for c in r) + "</tr>" for r in rows)
        cols = "".join(f'<col style="width:{w / sum(widths) * 100:.1f}%">' for w in widths)
        return f'<table class="w-tbl w-tbl2"><caption>{esc(cap)}</caption><colgroup>{cols}</colgroup><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'
    def page(i, pg):
        out = []
        if i == 0:
            out.append(f'<div class="w-title"><h3>{esc(doc["title"])}</h3><p class="w-sub">{esc(doc["sub"])}</p><p class="w-meta">{esc(doc["meta"])}</p></div>')
            out.append('<div class="w-sum"><b>요약</b><ul>' + "".join(f"<li><em>{esc(a)}</em>{esc(b)}</li>" for a, b in doc["summary"]) + "</ul></div>")
        open_ul = False
        for blk in pg["blocks"]:
            k = blk[0]
            if k != "b" and open_ul: out.append("</ul>"); open_ul = False
            if k == "h": out.append(f'<h4 class="w-h">{esc(blk[1])}</h4>')
            elif k == "head": out.append(f'<p class="w-head">{esc(blk[1])}</p>')
            elif k == "table": out.append(table(*blk[1:]))
            elif k == "note": out.append(f'<p class="w-note">{esc(blk[1])}</p>')
            else:
                if not open_ul: out.append('<ul class="w">'); open_ul = True
                sub = "<ul>" + "".join(f"<li>{_h(s)}</li>" for s in blk[2]) + "</ul>" if len(blk) > 2 and blk[2] else ""
                out.append(f"<li>{_h(blk[1])}{sub}</li>")
        if open_ul: out.append("</ul>")
        notes = '<ol class="w-fn">' + "".join(f"<li>{esc(n)}</li>" for n in pg.get("notes", [])) + "</ol>" if pg.get("notes") else ""
        return (f'<div class="a4"><div class="a4-in"><div class="w-run"><span>{esc(doc["series"])}</span><span>{esc(doc["title"])}</span></div>'
                + "".join(out) + f'</div><div class="a4-foot">{notes}<p class="w-pg">- {i + 1} -</p></div></div>')
    return f'<div class="a4-wrap" aria-label="{esc(label)}">' + "".join(page(i, p) for i, p in enumerate(doc["pages"])) + "</div>"

# ───────── 검토용 글 ─────────
def to_text(doc):
    L = [f"제목: {doc['title']}", f"부제: {doc['sub']}", doc["meta"], "", "[요약]"]
    L += [f"□ ({a}) {b}" for a, b in doc["summary"]]
    for i, pg in enumerate(doc["pages"], 1):
        L.append(f"\n──────── {i}쪽 ────────")
        for blk in pg["blocks"]:
            k = blk[0]
            if k == "h": L.append(f"\n## {blk[1]}")
            elif k == "head": L.append(f"\n▣ {blk[1]}")
            elif k == "note": L.append(f"\n※ {blk[1]}")
            elif k == "table":
                L.append(f"\n<{blk[1]}>"); L.append(" | ".join(blk[2])); L += [" | ".join(r) for r in blk[3]]
            else:
                L.append(f"□ {blk[1]}"); L += [f"   - {s}" for s in (blk[2] if len(blk) > 2 else [])]
        if pg.get("notes"):
            L.append("[주석] " + " / ".join(f"{k}) {n}" for k, n in enumerate(pg["notes"], 1)))
    return "\n".join(L) + "\n"

# ───────── Word ─────────
def to_docx(doc, path):
    from docx import Document
    from docx.shared import Pt, Mm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    BLUE, INK, GREY = RGBColor(0x1B, 0x3F, 0xC4), RGBColor(0x14, 0x1B, 0x2B), RGBColor(0x50, 0x5A, 0x6B)
    FONT = "맑은 고딕"
    d = Document(); sec = d.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.left_margin = sec.right_margin = Mm(20); sec.top_margin = Mm(18); sec.bottom_margin = Mm(16)
    st = d.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10)
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
        s = OxmlElement("w:shd"); s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), hexcolor)
        cell._element.get_or_add_tcPr().append(s)
    def border(p, side, size, color):
        b = OxmlElement("w:pBdr"); e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(size)); e.set(qn("w:space"), "2"); e.set(qn("w:color"), color)
        b.append(e); p._p.get_or_add_pPr().append(b)
    def para(before=0, after=0, indent=0, hang=0):
        p = d.add_paragraph(); f = p.paragraph_format
        f.space_before, f.space_after = Pt(before), Pt(after)
        if indent: f.left_indent = Mm(indent)
        if hang: f.first_line_indent = Mm(-hang)
        return p
    def cell_text(cell, text, bold=False, size=9, color=None, center=False):
        p = cell.paragraphs[0]; p.paragraph_format.line_spacing = 1.1
        if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rich(p, text, bold=bold, size=size, color=color)

    p = para(); run(p, doc["series"], bold=True, size=9, color=BLUE); border(p, "bottom", 18, "1B3FC4")
    p = para(before=10); run(p, doc["title"], bold=True, size=18, color=INK)
    p = para(before=2); run(p, doc["sub"], size=11.5, color=GREY)
    p = para(before=3, after=7); run(p, doc["meta"], size=9, color=GREY)
    t = d.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = "Table Grid"
    c = t.rows[0].cells[0]; shade(c, "F1F3F8"); cell_text(c, "요약", bold=True, size=10, color=BLUE)
    for a, b in doc["summary"]:
        q = c.add_paragraph(); f = q.paragraph_format; f.left_indent = Mm(4); f.first_line_indent = Mm(-4); f.line_spacing = 1.18
        run(q, "□ ", size=9.5); run(q, f"({a}) ", bold=True, size=9.5); run(q, b, size=9.5)

    for i, pg in enumerate(doc["pages"]):
        for blk in pg["blocks"]:
            k = blk[0]
            if k == "h":
                p = para(before=11, after=3); run(p, blk[1], bold=True, size=13, color=BLUE); border(p, "bottom", 8, "1B3FC4")
            elif k == "head":
                p = para(before=7, after=3); run(p, "▣ " + blk[1], bold=True, size=10.5, color=INK)
            elif k == "note":
                p = para(before=8); run(p, "※ " + blk[1], size=8.5, color=GREY); border(p, "top", 6, "9AA3B2")
            elif k == "table":
                _, cap, head, rows, widths = blk
                p = para(before=4, after=2); run(p, cap, bold=True, size=9, color=GREY)
                t = d.add_table(rows=1, cols=len(head)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
                for j, hh in enumerate(head):
                    shade(t.rows[0].cells[j], "E3E9FA"); cell_text(t.rows[0].cells[j], hh, bold=True, center=True)
                for r in rows:
                    cells = t.add_row().cells
                    for j, v in enumerate(r): cell_text(cells[j], v, bold=(j == 0))
                for r in t.rows:
                    for j, w in enumerate(widths): r.cells[j].width = Mm(w)
                para(after=2)
            else:
                p = para(before=1.5, indent=5, hang=5); run(p, "□ "); rich(p, blk[1])
                for s in (blk[2] if len(blk) > 2 else []):
                    q = para(indent=10, hang=4); run(q, "- ", color=GREY); rich(q, s, color=GREY)
        if pg.get("notes"):
            p = para(before=6); border(p, "top", 4, "9AA3B2")
            for k2, n in enumerate(pg["notes"], 1):
                if k2 > 1: p = para()
                run(p, f"{k2}) {n}", size=8, color=GREY)
        if i < len(doc["pages"]) - 1: d.add_page_break()
    fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run(); r.font.size = Pt(8.5)
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tag)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
        r._r.append(e)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    d.save(path)
