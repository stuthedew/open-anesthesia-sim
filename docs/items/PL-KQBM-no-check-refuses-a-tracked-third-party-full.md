---
id: PL-KQBM
title: No check refuses a tracked third-party full text, such as a PDF, now that sessions can fetch from any host
status: untriaged
added: 2026-11-11
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
