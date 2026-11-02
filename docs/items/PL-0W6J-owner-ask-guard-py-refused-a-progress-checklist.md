---
id: PL-0W6J
title: owner_ask_guard.py refused a progress checklist that quoted the hold it now lets through: wait for your read, inside quote marks in a sentence naming a PR
status: untriaged
added: 2026-11-02
---

**Problem.** owner_ask_guard.py refused a progress checklist that quoted the hold it now lets through: wait for your read, inside quote marks in a sentence naming a PR

**Where this came from.** On 2026-11-02 the thread building `PL-VHMS` posted a
progress checklist line: `PL-VHMS: guard lets "each/both will wait for your
read" through when no PR is named; tests pass`. The guard refused it. The hold
sat inside quote marks, as a mention, and the sentence named a pull request
("PR"), so the `PL-VHMS` exemption did not apply. `PL-XR8B` already skips a
hand-off just after a quote mark, but `HOLD_FOR_YOUR_READ` has no such
lookbehind. The line was reworded. Whether a quoted hold should be skipped the
same way is the question.
