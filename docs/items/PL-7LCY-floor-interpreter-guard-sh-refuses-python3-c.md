---
id: PL-7LCY
title: floor-interpreter-guard.sh refuses python3 -c reading a JSON parameter file under src/anesthesia_sim/data/, because it matches the tree name in the command text rather than whether 3.14 source is parsed, so correct read-only work is refused (a false refusal, the opposite direction to PL-61FT's spelling gaps)
status: untriaged
added: 2026-09-26
---

**Problem.** floor-interpreter-guard.sh refuses python3 -c reading a JSON parameter file under src/anesthesia_sim/data/, because it matches the tree name in the command text rather than whether 3.14 source is parsed, so correct read-only work is refused (a false refusal, the opposite direction to PL-61FT's spelling gaps)

**Met 2026-09-26 in ordinary work on `PL-WMCJ`:** `python3 -c "import json; d=json.load(open('src/anesthesia_sim/data/agents/sevoflurane.json')) ..."` was refused with the PEP 758 message, though it parses no Python source; the same read spelled as a heredoc passed moments earlier. Routed around with `grep`, so it blocked nothing. Evidence for `PL-61FT`'s open design decision, which records that none of its twelve members was met in ordinary work.
