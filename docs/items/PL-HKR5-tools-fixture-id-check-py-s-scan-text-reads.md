---
id: PL-HKR5
title: tools/fixture_id_check.py's scan_text reads every .claude file but a .sh one a physical line at a time, so an id that a TOML multi-line string's line-ending backslash, a YAML front matter's escaped line break in a double-quoted scalar, or a fenced bash sample's backslash-newline carries across two lines is judged in fragments - a valid id refused, an unmintable one passed - forms PL-WG6S's .sh fix left out; latent
priority: P3
effort: M
status: done
classes: defect
feature: one-answer
touches: tools/fixture_id_check.py, tests/unit/test_doc_check.py, docs/ARCHITECTURE.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
closed: 2026-10-10
pr: 1390
payoff: an id a TOML string, a front matter quoted value or a fenced shell sample carries across lines is judged whole, so a valid one is not refused and an unmintable one does not pass
verify: grep -qF '"fixture ids, an id a fenced shell sample joins"' tests/unit/test_doc_check.py && grep -qF '"fixture ids, an id a TOML multi-line string joins"' tests/unit/test_doc_check.py && grep -qF '"fixture ids, an id a front matter quoted scalar joins"' tests/unit/test_doc_check.py
---

**Problem.** tools/fixture_id_check.py's scan_text reads every .claude file but a .sh one a physical line at a time, so an id that a TOML multi-line string's line-ending backslash, a YAML front matter's escaped line break in a double-quoted scalar, or a fenced bash sample's backslash-newline carries across two lines is judged in fragments - a valid id refused, an unmintable one passed - forms PL-WG6S's .sh fix left out; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
smaller tools. `PL-WG6S` made `scan_text` read a `.sh` file as bash reads it,
through `docket.shell.joined_text`, and reads everything else under `.claude/` a
physical line at a time on the ground, stated in its comment, that Markdown and
JSON join no token. Three formats `.claude/` holds do: a TOML 1.0 multi-line
basic string, where a line-ending backslash trims the newline and the
whitespace after it (`.claude/hooks/ruff.toml` is the TOML file there); a YAML
1.2.2 double-quoted scalar in a Markdown file's front matter, where an escaped
line break is excluded from the content (§ 7.3.1; a skill's `description:` is
one, and the harness shows it to sessions); and a fenced bash sample in
Markdown, where POSIX § 2.2.1 removes a backslash-newline.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against `tomllib`, PyYAML and bash 5.2.21 and dash. Each format carried a
valid id split after `PL-K7` and an unmintable one split after `PL-`:

```text
note = """see PL-K7\
  QX for why"""
bad = """PL-\
  AAAA"""

description: "... PL-K7\
  QX, or PL-\
  AAAA."

bin/docket show PL-K7\
QX
bin/docket set PL-\
AAAA --priority P2
```

In each, `scan_text` reported `PL-K7` as malformed and said nothing of the
second id; `tomllib` read `PL-K7QX` and `PL-AAAA`, PyYAML the same, and both
shells handed the command `PL-K7QX` and `PL-AAAA`. So a valid id is refused,
and a malformed one passes, which is the silent half the check exists to catch.
Latent: no TOML file under `.claude/` holds a multi-line string, both skill
descriptions are one-line plain scalars, and the nine backslash-ended lines in
`.claude/` fences all break after a space, so none splits an id.

**Reproduced 2026-10-10 at triage** on this branch at `b6b9c382`, whose readers are `main`'s at `fe2e5132`: over the three samples,
written to a TOML file, a Markdown file's front matter and a Markdown fence,
`scan_text` reported `PL-K7` as malformed in each and said nothing of the
unmintable `PL-AAAA`.

**Why it matters.** `tools/fixture_id_check.py` keeps an id the store can never
mint out of `.claude/`, where sessions read an example as the grammar of an id.
Read a physical line at a time, an id one of these forms carries across lines
is refused when it is valid and passed when it is not, which is the silent half
the check exists to catch.

**Generator check.** A member of `PL-R417`: the reader judges a physical line
where the format joins a token across two. It is the form `PL-WG6S`, a member,
left out, on its own stated premise that only shell joins one.

**Done when.** `scan_text` reads a fenced shell sample through `docket.fences`
and `docket.shell.joined_text`, as it reads a `.sh` file, and reads or declines
by name a TOML multi-line string with a line-ending backslash and a front-matter
double-quoted scalar a line ends inside with a backslash, each pinned by a
`fixture ids, ` case in `PL-R417`'s guard that fails on today's reader; the
comment that says Markdown and JSON join no token says what does.

**Built 2026-10-10 (`#1390`).** `scan_text` reads each file through `_joined`,
which takes out what its format joins across a line break and keeps each
character's origin: a `.sh` file and a fenced shell sample in Markdown through
`docket.fences` and `docket.shell.joined_text`; a TOML multi-line basic
string's line-ending backslash, with the whitespace and newlines after it, as
`tomllib` reads it; and an escaped line break in a double-quoted scalar of a
Markdown file's front matter, with the next line's leading blanks, as PyYAML
6.0.1 reads it. A single-quoted or plain scalar and a TOML literal string join
nothing. Three `fixture ids, ` cases in `PL-R417`'s guard pin the three forms,
each failing on `main`'s check, and the docstring that said Markdown and JSON
join no token now names what does.
