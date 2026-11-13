#!/usr/bin/env python3
"""src/ 의 조각과 data/vocab.json 을 합쳐 index.html 한 파일로 만든다.

  python3 build.py            -> index.html (브라우저에서 바로 여는 완전한 문서)
  python3 build.py 조각.html   -> <head>/<body> 없는 조각도 함께 만든다 (게시용)
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
read = lambda p: p.read_text(encoding="utf-8")

vocab = json.loads(read(ROOT / "data" / "vocab.json"))
refs = json.loads(read(SRC / "refs.json"))

# 참고 자료: 번호를 매기고 목록을 만든다.
num, groups = {}, []
for r in refs:
    if "g" in r:
        groups.append((r["g"], []))
    else:
        num[r["id"]] = len(num) + 1
        groups[-1][1].append(r)
refs_html = ""
for g, items in groups:
    lis = "".join(
        f'<li id="ref-{r["id"]}" value="{num[r["id"]]}"><b>{r["t"]}</b><span>{r["s"]}</span>{r["n"]}</li>' for r in items)
    refs_html += f'<h3>{g}</h3><ol class="refs">{lis}</ol>'

body = "\n".join(read(p) for p in sorted((SRC / "chapters").glob("*.html")))
body = body.replace("{{REFS}}", refs_html)

def cite(m):
    key = m.group(1)
    if key not in num:
        raise SystemExit(f"참고 자료에 없는 열쇠: {key}")
    return f'<a href="#ref-{key}">{num[key]}</a>'
body = re.sub(r"\[\[([a-z0-9]+)\]\]", cite, body)
body = body.replace("{{VOCAB_COUNT}}", f"{len(vocab):,}").replace("{{REF_COUNT}}", str(len(num)))
assert "{{" not in body and "[[" not in body

page = read(SRC / "head.html")
page += "<style>\n" + read(SRC / "style.css") + "</style>\n" + body
page += "\n<script>window.VOCAB=" + json.dumps(vocab, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";</script>\n"
page += "<script>\n" + read(SRC / "app.js") + "</script>\n"

full = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + read(SRC / "head.html") + "</head>\n<body>\n" + page[len(read(SRC / "head.html")):] + "</body>\n</html>\n")
(ROOT / "index.html").write_text(full, encoding="utf-8")
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(page, encoding="utf-8")
print(f"index.html: {len(full.encode('utf-8')) / 1024:.0f} KB, 어휘 {len(vocab)}개, 참고 자료 {len(num)}종")
