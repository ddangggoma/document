#!/usr/bin/env python3
"""reports/v*.py 의 각 판을 HTML 조각, 검토용 글, Word 파일로 만든다.

  python3 make_versions.py [글_폴더]
    src/report-versions/v1.html …   화면에 싣는 조각
    글_폴더/v1.txt …                 검토자에게 주는 글 (폴더를 주었을 때)
    docs/AI에이전트_RnD자동화_동향보고.docx   마지막 판의 Word 파일
"""
import importlib.util, sys
from pathlib import Path
import report_a4

ROOT = Path(__file__).parent
out = ROOT / "src" / "report-versions"; out.mkdir(parents=True, exist_ok=True)
txt = Path(sys.argv[1]) if len(sys.argv) > 1 else None
docs = []
for p in sorted((ROOT / "reports").glob("v*.py")):
    spec = importlib.util.spec_from_file_location(p.stem, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    docs.append((p.stem, m.DOC))
    (out / f"{p.stem}.html").write_text(report_a4.to_html(m.DOC, p.stem), encoding="utf-8")
    if txt:
        txt.mkdir(parents=True, exist_ok=True); (txt / f"{p.stem}.txt").write_text(report_a4.to_text(m.DOC), encoding="utf-8")
    print(p.stem, len(m.DOC["pages"]), "쪽")
report_a4.to_docx(docs[-1][1], ROOT / "docs" / "AI에이전트_RnD자동화_동향보고.docx")
print("Word:", docs[-1][0])
