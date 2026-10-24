---
id: PL-G84G
title: No check and no one-source-of-truth item covers a text fact restated under src/ (a unit label, a display name): tools/literal_home_check.py reads numbers only and PL-K88Z's inventory surveyed no strings; on 2026-10-24, 112 distinct short string literals sit in two or more modules under src/anesthesia_sim/, 12 of them unit-like
status: untriaged
feature: one-source-of-truth
added: 2026-10-24
---

**Problem.** No check and no one-source-of-truth item covers a text fact restated under src/ (a unit label, a display name): tools/literal_home_check.py reads numbers only and PL-K88Z's inventory surveyed no strings; on 2026-10-24, 112 distinct short string literals sit in two or more modules under src/anesthesia_sim/, 12 of them unit-like

**Measured 2026-10-24** on `main` at `345e8bb2`. The script below parsed every module under `src/anesthesia_sim/`, skipped docstrings, and collected each string literal of 1 to 40 characters on one line. 112 distinct strings occur in two or more modules. 12 of them look like units or clinical labels, by a loose pattern. Most of the 112 are message fragments and are not shared facts. The count only shows where to look; it is not a list of defects. The unit-like ones that appear in the most modules are `'s'` (5 modules), `'×MAC'`, `'L/min'` and `'volume_l'` (3 each), and `'%'`, `'h'` and `'circuit_volume_l'` (2 each). `PL-Q3G9` is one confirmed instance: the unit of the three flow controls.

**Why no existing item covers it.** `tools/literal_home_check.py` says that it holds "every number in `src/anesthesia_sim/`" to one home, so it does not read strings. `tools/fact_home_check.py` refuses an upper-case name defined in two *apparatus* files, not under `src/`. `PL-K88Z`'s four surveys covered numbers, run state, duplicated logic and configuration. The four check items (`PL-JS6P`, `PL-WM5P`, `PL-VWXL`, `PL-SH0W`) inherit those four shapes. A unit label, an axis label or a display name that is typed in two places is a value copied, but no planned check can find it.

**Decision for triage.** Decide between three options. The first is to extend `literal_home_check` to a defined class of strings, such as unit labels. The second is to add a unit type that carries its own label. The third is to leave strings to review. Choose by counting how many of the 12 unit-like strings are real second copies once each one is read.

Reproduce the count with this script, run as `.venv/bin/python -I script.py src/anesthesia_sim`:

```python
import ast, pathlib, re, collections, sys
root = pathlib.Path(sys.argv[1])
seen = collections.defaultdict(set)
for p in root.rglob("*.py"):
    tree = ast.parse(p.read_text())
    doc_ids = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body:
            f = n.body[0]
            if isinstance(f, ast.Expr) and isinstance(f.value, ast.Constant) and isinstance(f.value.value, str):
                doc_ids.add(id(f.value))
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc_ids:
            s = n.value.strip()
            if 1 <= len(s) <= 40 and "\n" not in s:
                seen[s].add(str(p.relative_to(root)))
unitish = re.compile(r"(mL|L/min|/min|mmHg|cmH2O|kPa|%|MAC|vol|kg|\bs\b|\bh\b|ppm|atm)", re.I)
multi = {s: f for s, f in seen.items() if len(f) > 1}
units = {s: f for s, f in multi.items() if unitish.search(s)}
print(len(multi), len(units))
```
