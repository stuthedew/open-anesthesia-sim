---
id: PL-CLVM
title: The early wash-in comparison states desflurane's worst early point as +2.10 SD in test_published_wash_in_and_elimination.py's docstring table and docs/MODEL.md, but as +2.11 SD in the comment above the regression band's ceiling
status: untriaged
added: 2026-10-18
---

**Problem.** The early wash-in comparison states desflurane's worst early point as +2.10 SD in test_published_wash_in_and_elimination.py's docstring table and docs/MODEL.md, but as +2.11 SD in the comment above the regression band's ceiling

**Where.** `tests/reference/test_published_wash_in_and_elimination.py` has the
table row "+2.10 SD at 10 min" in the early wash-in test's docstring, and the
same row in `docs/MODEL.md`'s early wash-in table. The comment that opens
"The top of that regression band" says the worst point was +2.11 SD when the
comparison was first run. One of them is rounded differently or stale. The
fix reruns the comparison at the shipped defaults and states one value in all
three places. It is in `docs/MODEL.md`, on the clinical floor, so it is filed
rather than fixed in place.

**Found by** the `PL-PRCS` design round's trial review of #1526's prose,
2026-10-18.
