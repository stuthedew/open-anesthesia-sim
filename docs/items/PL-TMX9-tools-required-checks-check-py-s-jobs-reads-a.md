---
id: PL-TMX9
title: tools/required_checks_check.py's _jobs reads a job's name: from the key's line alone, so a name YAML continues - a block scalar header, or a plain scalar carried onto the next line - is read as its header or first line, and the check name reconciled against the required list is not the one GitHub reports
status: untriaged
feature: one-answer
touches: tools/required_checks_check.py, tests/unit
added: 2026-10-04
---

**Problem.** tools/required_checks_check.py's _jobs reads a job's name: from the key's line alone, so a name YAML continues - a block scalar header, or a plain scalar carried onto the next line - is read as its header or first line, and the check name reconciled against the required list is not the one GitHub reports

**Found 2026-10-04, building `PL-R417`'s YAML slice (`#1339`).** `_jobs` reads
a job's display name as `line.strip().split(":", 1)[1].strip().strip("'\"")`,
the key's line alone. `name: >` is read as the check name `>`, and `name:
Long` over an indented `title` as `Long`, where YAML hands GitHub `Long
title` (YAML 1.2.2 § 7.3.3, § 8.1). Latent: every `name:` under `.github/`
sits on one line today. The sweep in `PL-R417`'s brief named `_triggers` in
this file and missed this reader.

**Why it matters.** Branch protection matches a required check by name, so a
misread name reports a requirement orphaned, or a job unrequired, that is
neither; the failure is loud, but it names the wrong thing.

**Generator check.** A member of `PL-R417`, which was told: the reader takes a
physical line for a value YAML continues, the fact that head names. Not a
recurrence of `PL-6P6H`, which `bin/docket new` matched it to by the shared
`tests/unit` path: that item is doc_check's `workflow_commands`, fixed in
`#1339`, and this is a second reader of the same fact in another tool.

**Done when.** A `name:` value YAML continues past the key's line is read
whole or refused by name (an `Undecidable`, as the file's other refusals are),
pinned by a `required checks, a job name ...` case in `PL-R417`'s guard.
