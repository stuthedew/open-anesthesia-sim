---
id: PL-WX79
title: doc_check reads a rule's or skill's YAML front matter as Markdown in four readers - check_citations and check_quoted_sources read it as one setext heading so a backtick or quotation one key leaves open pairs with the next key's, _host_claim_texts lets the next key date a key's host claim and a fence-shaped block-scalar line hide the body's claims, _without_code pairs that fence with the body's first, and _removed_headings reads the front matter as a heading - so a front matter's citations and claims are misread and a body's can go unread; live in form
priority: P3
effort: M
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, subprojects/docket/src/docket/frontmatter.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-10
payoff: a rule's or skill's front matter is read key by key and its body as Markdown, so neither misreads the other's citations, claims or code
verify: grep -qF '"citations, a stray backtick in one front-matter key pairs with nothing in the next"' tests/unit/test_doc_check.py && grep -qF '"host claims, a front matter key is dated by no other key"' tests/unit/test_doc_check.py && grep -qF '"math, a fence-shaped line in a front matter opens no fence"' tests/unit/test_doc_check.py && grep -qF '"removed headings, a front matter is no heading"' tests/unit/test_doc_check.py
---

**Problem.** doc_check reads a rule's or skill's YAML front matter as Markdown in four readers - check_citations and check_quoted_sources read it as one setext heading so a backtick or quotation one key leaves open pairs with the next key's, _host_claim_texts lets the next key date a key's host claim and a fence-shaped block-scalar line hide the body's claims, _without_code pairs that fence with the body's first, and _removed_headings reads the front matter as a heading - so a front matter's citations and claims are misread and a body's can go unread; live in form

**Found 2026-10-10 in `PL-R417`'s closing sweep** (link 23), by the auditors of
`tools/doc_check.py`'s second and third parts.
CommonMark reads a front matter's keys as one paragraph that its closing `---`
underlines as a setext heading (CommonMark 0.31.2 § 4.3), and a fence-shaped
line inside a block scalar opens a fence (§ 4.5) that runs past the front
matter's close. In YAML 1.2.2 each key is its own statement and a block
scalar's lines are its content (§ 8.1). `PL-2MLT` gave `docket.instructions`
the front matter key by key through `docket.frontmatter.keys` and the body from
the line after it; these four readers came before it or were written after it
without it:

- `check_citations` and `check_quoted_sources` read the documents whole, front
  matter included, so a stray backtick in one key's value pairs with the next
  key's and the code span read is the text between them.
- `_host_claim_texts`, new in `#1387`, yields the front matter with the body,
  so the next key's date dates a key's host claim, and a fence-shaped line in a
  block scalar hides every claim in the body up to its first fence.
- `_without_code` pairs that fence the same way, so prose TeX in the body is
  blanked; `PL-WTQ1` skipped the front matter's lines from reporting but still
  reads them for pairing.
- `_removed_headings`, new in `#1388`, reports the whole front matter as a
  removed heading whenever a key changes.

**Reproduced 2026-10-10** on `main` at `75e1700d`, under python3 3.11.17 and
3.13.16, against PyYAML 6.0.3 and ruamel.yaml 0.19.1 (each key one value) and
cmark-gfm 0.29 (the body's paragraph rendered as written). Each block below is
a whole rule or skill file; the first is read with no error, where the same
file without the stray backtick reports the missing path:

````text
---
name: demo
description: Run the demo whenever the owner asks; a ` alone marks nothing
when: the owner names `docs/gone.md` as the reason
---

---
description: |
  ```
  quoted
---

Body writes \(x\) here.

```
code
```
````

The second gives `_without_code` one fence pair over the body's prose and no
error, where the same file without the fence-shaped line reports both
delimiters; with a host claim in place of the TeX, `_host_claim_texts` reports
nothing.

Live in form: `.claude/skills/docket/SKILL.md` and
`.claude/skills/run-the-app/SKILL.md` are read as setext headings by
`_removed_headings`, so any edit to either front matter adds a term the
candidates list was not asked for. No front matter in the tree holds a stray
backtick, a host claim or a fence-shaped line.

**Why it matters.** Rules and skills are the documents a session reads
as instructions, so a path one cites that the tree no longer holds misdirects
the session that follows it, and these readers either miss the citation or
misread the next key's text as part of it. And `_removed_headings` hands the
close-out sweep a skill's whole front matter as a term whenever one of its keys
changes, a search no document can answer.

**Generator check.** A member of `PL-R417`: the reader takes a physical line
for a statement its format continues, the fact that head names. It is the gap
closed `PL-CZ28`'s and `PL-2MLT`'s fixes left, in readers those fixes did not
reach.

**Done when.** Each of the four reads a document's front matter through
`docket.frontmatter` (each key's value its own statement) and its Markdown body
from the line after the front matter closes, with a test per reader on a form
above.
