---
id: PL-RW3T
title: tools/doc_check.py's check_gate_parity matches a gate script by its path and not by the arguments it runs with, so a mode one gate runs and the other never does passes as covered: tools/pr_body_check.py --anchors ran only in make check from PL-73G8 until PL-3PH2, counted as covered in CI by pr-title.yml's --check, a different mode of the same script
status: untriaged
added: 2026-09-26
---

**Problem.** tools/doc_check.py's check_gate_parity matches a gate script by its path and not by the arguments it runs with, so a mode one gate runs and the other never does passes as covered: tools/pr_body_check.py --anchors ran only in make check from PL-73G8 until PL-3PH2, counted as covered in CI by pr-title.yml's --check, a different mode of the same script

**Reach, measured 2026-09-26 on `claude/pr-body-storage-cnnpme`.** Comparing
the script invocations in `Makefile` against `quality.yml` and `pr-title.yml`
by script *and* arguments: once `PL-3PH2` added `--anchors` to `quality.yml`,
the only mode-level differences left are `pr_title_check.py --discover` and
`pr_record_check.py --discover`, which are the local stand-ins for what CI
reads from the event, so no live instance remains. The defect is the rule's
blindness to the next one: a mode added to one gate passes parity whenever
any other mode of the same script runs in the other.
