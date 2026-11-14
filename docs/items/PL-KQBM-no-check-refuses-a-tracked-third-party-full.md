---
id: PL-KQBM
title: No check refuses a tracked third-party full text, such as a PDF, now that sessions can fetch from any host
priority: P3
effort: S
status: done
classes: infra
touches: tools/full_text_check.py, tests/unit/test_full_text_check.py, Makefile, .github/workflows/quality.yml, docs/references/README.md, docs/apparatus.md, docket.toml
added: 2026-11-11
closed: 2026-11-14
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

**Done, 2026-11-14.** `tools/full_text_check.py` fails when git tracks a file
whose name ends in a document extension, such as `.pdf`, `.epub`, `.djvu`,
`.mobi` or `.docx`, in any letter case, and the licensed-files list does not
name it. The list sits between two comment markers in
`docs/references/README.md` § "Redistribution". It is the only copy, so a file
is allowed in the same edit that records its licence. Each line gives the path
in backticks, a colon and the licence. The list is empty, because the
repository tracks no such file. A list line of another shape, or a missing
marker, fails the run, because the check cannot then say which files are
allowed. The tracked file list comes from `docket.vcs.tracked_files`, and the
README's path from `doc_check.REFERENCES`, so the tool adds no second reader of
either. `make check` and the floor section of `.github/workflows/quality.yml`
both run it with bare `python3`, and `docs/apparatus.md` lists it among the
floor commands. Text pasted from a source, and a figure or screenshot of
another party's page, cannot be told apart by extension and stay with the rule
in prose. The tests in `tests/unit/test_full_text_check.py` cover a tracked PDF,
a listed one, an untracked one, a malformed list line, a README without the
markers, and the real repository. Files checked in the docs sweep:
`docs/references/README.md`, `docs/apparatus.md`, `Makefile` and
`.github/workflows/quality.yml`.
