---
id: PL-G8ZN
title: docket.frontmatter's keys and quoted raise Unread on a first-column ... line, where YAML reads a document-end marker and PyYAML 6.0.3 reads the front matter above it whole, so fixture_id_check joins none of that block's escaped line breaks - a malformed PL-K7QXZ passes and a well-formed PL-K7QX is reported as PL-K7 - and every other reader of the block declines it; latent (found closing PL-YPLM)
status: untriaged
touches: subprojects/docket/src/docket/frontmatter.py, subprojects/docket/tests/test_frontmatter.py, subprojects/docket/tests/test_frontmatter_reference.py, tests/unit/test_fixture_id_check.py
added: 2026-10-12
---

**Problem.** docket.frontmatter's keys and quoted raise Unread on a first-column ... line, where YAML reads a document-end marker and PyYAML 6.0.3 reads the front matter above it whole, so fixture_id_check joins none of that block's escaped line breaks - a malformed PL-K7QXZ passes and a well-formed PL-K7QX is reported as PL-K7 - and every other reader of the block declines it; latent (found closing PL-YPLM)

**Found 2026-10-12 closing `PL-YPLM`**, whose brief named this form as the
old `_front_matter_joins` closing on `...`. Since `PL-S4JL` the joins find the
front matter through `docket.frontmatter.closing`, which closes on `---` alone,
and take each double-quoted scalar from `docket.frontmatter.quoted`. A
first-column `...` line between the last key and the closing `---` is a YAML
document-end marker (YAML 1.2.2 § 9.1.2): PyYAML 6.0.3 reads every key above
it, and only blank and comment lines may follow it in one document. `keys`
and `quoted` raise `Unread` on it instead ("`...` sits at the first column and
opens no key"), so `_front_matter_joins` joins nothing in the block and the
file is read as written.

**Reproduced 2026-10-12** on `claude/workflow-group-five-ii7jua` from `main`
at `5d12a89f`, under python3 3.14.7, with a skill whose front matter is
`name: x`, a `description:` double-quoted scalar carried over an escaped line
break, `...`, then `---`:

```text
description: "see PL-K7QX\    PyYAML: see PL-K7QXZ   fixture_id_check: nothing
  Z"
description: "see PL-K7\      PyYAML: see PL-K7QX    fixture_id_check: PL-K7
  QX"
```

A `# done` comment line after the `...` reads the same. Latent: no front
matter under `.claude/` holds a `...` line.

**Why it matters.** The first row is the check passing the malformed id it
exists to refuse, silently; the second fails `make check` on a well-formed one.
And every reader of `keys` and `quoted` is refused a front matter YAML reads
whole.

**Done when.** `keys` and `quoted` read a first-column `...` as the end of the
YAML document - its keys above read, a block with anything but blank or
comment lines after it declined as `Unread` - and a test pins both rows above
in `tests/unit/test_fixture_id_check.py`, with the reference test holding the
form to PyYAML.
