#!/usr/bin/env python3
"""분류별 어휘 파일을 합쳐 data/vocab.json 을 만든다. 중복을 없애고 2,000개로 맞춘 뒤 빈도순으로 정렬한다."""
import json, sys, re, collections
from pathlib import Path
src = Path(sys.argv[1]); TARGET = 2000
KEYS = ["w","pos","cat","sub","tone","m","syn","ex","tip","alt","f"]
norm = lambda s: re.sub(r"[\s·/\-~(),.]", "", s).lower()
seen, items, dups = {}, [], []
for p in sorted(src.glob("A*.json"), key=lambda p: int(p.stem[1:])):
    for e in json.loads(p.read_text(encoding="utf-8")):
        assert all(k in e for k in KEYS), (p.name, e.get("w"))
        k = norm(e["w"])
        if k in seen: dups.append((e["w"], seen[k], p.stem)); continue
        seen[k] = p.stem; items.append({k2: e[k2] for k2 in KEYS})
print("합계", len(items), "중복 제거", len(dups), dups[:20])
by = collections.defaultdict(list)
for e in items: by[e["cat"]].append(e)
total = len(items); keep = []
quota = {c: round(TARGET * len(v) / total) for c, v in by.items()}
diff = TARGET - sum(quota.values())
for c in sorted(quota, key=lambda c: -len(by[c]))[:abs(diff)]: quota[c] += 1 if diff > 0 else -1
for c, v in by.items():
    v.sort(key=lambda e: -e["f"]); keep += v[:quota[c]]
assert len(keep) == TARGET
# 팀별 추가 묶음(T*.json)은 2,000개와 별도로 덧붙인다.
have = {norm(e["w"]) for e in keep}
for p in sorted(src.glob("T*.json")):
    for e in json.loads(p.read_text(encoding="utf-8")):
        if norm(e["w"]) in have: continue
        have.add(norm(e["w"])); keep.append({k2: e[k2] for k2 in KEYS})
keep.sort(key=lambda e: (-e["f"], e["w"]))
print("최종", len(keep))
Path("data/vocab.json").write_text(json.dumps(keep, ensure_ascii=False, indent=0), encoding="utf-8")
print({c: quota[c] for c in quota})
print("tone", collections.Counter(e["tone"] for e in keep))
print("상위 30:", [e["w"] for e in keep[:30]])
bad = [e["w"] for e in keep if re.search(r"(함|임|됨|음)\.?$", e["m"].strip()) or re.search(r"(함|임|됨)\.?$", e["ex"].strip())]
print("명사형 종결 의심", len(bad), bad[:10])
print("f 분포", collections.Counter(e["f"]//10*10 for e in keep))
