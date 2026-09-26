---
id: PL-RW3T
title: tools/doc_check.py's check_gate_parity matches a gate script by its path and not by the arguments it runs with, so a mode one gate runs and the other never does passes as covered: tools/pr_body_check.py --anchors ran only in make check from PL-73G8 until PL-3PH2, counted as covered in CI by pr-title.yml's --check, a different mode of the same script
status: untriaged
added: 2026-09-26
---

**Problem.** tools/doc_check.py's check_gate_parity matches a gate script by its path and not by the arguments it runs with, so a mode one gate runs and the other never does passes as covered: tools/pr_body_check.py --anchors ran only in make check from PL-73G8 until PL-3PH2, counted as covered in CI by pr-title.yml's --check, a different mode of the same script
