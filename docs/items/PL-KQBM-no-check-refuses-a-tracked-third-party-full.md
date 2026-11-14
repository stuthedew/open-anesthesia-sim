---
id: PL-KQBM
title: No check refuses a tracked third-party full text, such as a PDF, now that sessions can fetch from any host
priority: P3
effort: S
status: ready
classes: infra
touches: tools, Makefile
added: 2026-11-11
payoff: a publisher's full text cannot be committed and redistributed by accident
verify: grep -q 'full_text_check' Makefile
---

**Problem.** No check refuses a tracked third-party full text, such as a PDF, now that sessions can fetch from any host

**Where this came from.** `PL-6VZF` opened the session network to any host on
2026-11-10. One of its two conditions is that nothing fetched from a third
party is committed: no full text, figure or screenshot of another party's
page. `docs/references/README.md` § "Redistribution" states the rule in
prose, and `git ls-files` showed no tracked PDF on 2026-11-10. No check
refuses one. This repository held two publisher-copyright PDFs until
2026-09-06 (`PL-SHG5`).

**What a check could decide.** A tracked file with a document extension such
as `.pdf`, `.epub` or `.djvu`, outside a short list of files whose licence
the README records. Text pasted from a source is not decidable, and stays
with the rule.

**Before building it.** A new check is a new workflow mechanism, so the
generator pause in `CLAUDE.md` applies unless the owner asks for it.

**Why it matters.** A third party's full text committed here would be redistributed by every clone and fork, against `docs/references/README.md` § "Redistribution" and the condition `PL-6VZF` set when it opened the network. Prose alone did not stop it before: two publisher PDFs sat in the tree until 2026-09-06 (`PL-SHG5`).

**Done when.** A check wired into `make check` fails when a tracked file has a document extension such as `.pdf`, `.epub` or `.djvu` and is not on a list of files whose licence `docs/references/README.md` records.

**Blocked on the generator pause.** A new check is a new workflow mechanism, which `CLAUDE.md` holds while a workflow-lane head carries `generator: live`. `PL-J1ZM` is that head on 2026-11-11. The pause lifted on 2026-11-14, when the owner stopped `PL-J1ZM` and its `generator:` became `spent`.

**Generator check.** A one-off: a rule stated in prose with no check, and one earlier instance (`PL-SHG5`). No head's `misread:` states which tracked files are a third party's text.
