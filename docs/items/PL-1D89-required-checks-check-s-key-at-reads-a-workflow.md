---
id: PL-1D89
title: required_checks_check's _key_at reads a workflow key by splitting at its first colon without unquoting it, so a job key written in quotes reports its check name quotes and all, and a quoted name key is not read, leaving the job id as the check name; latent
status: untriaged
added: 2026-10-06
---

**Problem.** required_checks_check's _key_at reads a workflow key by splitting at its first colon without unquoting it, so a job key written in quotes reports its check name quotes and all, and a quoted name key is not read, leaving the job id as the check name; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`tools/required_checks_check.py`. `_jobs` takes each job's id and its `name:`
through `_key_at`, which splits a line at its first colon and keeps what comes
before it as written. A YAML key may be quoted (YAML 1.2.2 § 7.3), and both
GitHub and PyYAML read the key without its quotes. `triggers` and `steps` read
keys through `_key`, which unquotes; `_jobs` alone does not.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against PyYAML 6.0.3:

```text
on: pull_request
jobs:
  "lint":
    runs-on: x
  test:
    "name": Unit tests
    runs-on: x
```

`reporting_jobs` gave the first job the id and check name `"lint"`, quotes
included, and the second the check name `test`, where PyYAML reads the keys
`lint` and `name` and GitHub reports the checks `lint` and `Unit tests`. The
check then compares names GitHub never reports with the required list. Latent:
no tracked workflow quotes a key.

**Generator check.** Not a member of `PL-R417`: each key is one line, read
whole. The tab guard in `_jobs`, filed by the same sweep as a member, is a
different fault in the same walker; routing `_jobs` through `_keys` and
`_entry_key`, as `steps` reads, would fix both.

**Done when.** `_jobs` reads a quoted job key and a quoted `name:` key as
PyYAML does, pinned by a test with the input above.
