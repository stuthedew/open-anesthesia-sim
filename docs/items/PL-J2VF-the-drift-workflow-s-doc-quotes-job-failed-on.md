---
id: PL-J2VF
title: The drift workflow's doc-quotes job failed on main on 2026-11-09 and no item records it: docs/resident-instructions.md quotes a sentence about rules without a paths field that the Claude Code memory page no longer contains
status: untriaged
added: 2026-11-10
---

**Problem.** The drift workflow's doc-quotes job failed on main on 2026-11-09 and no item records it: docs/resident-instructions.md quotes a sentence about rules without a paths field that the Claude Code memory page no longer contains

**Checked 2026-11-10:** the session-start digest reports that the drift workflow's "doc-quotes" job failed on `main` in run #15 on 2026-11-09 (https://github.com/stuthedew/open-anesthesia-sim/actions/runs/42570703414). `docs/resident-instructions.md` quotes Claude Code's documentation: "Rules without a `paths` field are loaded unconditionally and apply to all files". The audit's reviewer ran `python3 tools/doc_quote_check.py`, which exited 1 and reported that the memory page on code.claude.com no longer contains that sentence. The filing session did not rerun it. No open item names the failure. The three other failing jobs in the digest are from run #11 on 2026-11-01, and `PL-CSK0`, `PL-R74V`, `PL-ZH36` and `PL-DPDG` (done 2026-11-02) record them; they read as failing because those monthly jobs have not run on `main` since.

**Done when.** The quote in `docs/resident-instructions.md` matches what the page says now, or the sentence states the fact without quoting, and the drift workflow's doc-quotes job passes on `main` when run by hand.
