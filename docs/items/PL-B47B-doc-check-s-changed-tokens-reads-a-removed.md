---
id: PL-B47B
title: doc_check's changed_tokens reads a removed heading off each removed line of the diff with REMOVED_HEADING_RE, so a removed setext heading yields no term for the close-out sweep and a removed line opening with # inside a fence yields one; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: the close-out sweep looks for a removed setext heading's words, and never for a fenced comment's
verify: grep -qF '"removed headings, ' tests/unit/test_doc_check.py
---

**Problem.** doc_check's changed_tokens reads a removed heading off each removed line of the diff with REMOVED_HEADING_RE, so a removed setext heading yields no term for the close-out sweep and a removed line opening with # inside a fence yields one; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
second half of `tools/doc_check.py`. `changed_tokens` reads a changed Markdown
document's `-U0` diff and takes each removed line `REMOVED_HEADING_RE` matches
for a removed heading, whose words become terms the close-out sweep looks for in
the other documents. A line of a diff is a line of the file's own format: a
setext heading spans its text line and its underline (CommonMark 0.31.2 § 4.3),
and a line opening with `#` inside a fence is code, not a heading (§ 4.5).

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0 over the file before and after. A guide loses a
setext heading and a fenced comment line:

~~~text
Setting up the checkout
-----------------------

```bash
# make sure the venv exists
```
~~~

`changed_tokens` gave the one term `make sure the venv exists`. markdown-it's
removed headings are `Setting up the checkout` alone. Latent: the 38 documents
`DOC_GLOBS` names hold no setext heading and no `#`-led line that is not a
heading.

**Why it matters.** The close-out sweep looks in the other documents for the words of every heading a change removed, so a removed setext heading's references go unlooked-for, and a fenced comment line sends the sweep after words no heading held.

**Generator check.** A member of `PL-R417`: a reader takes a physical line of a
diff for a statement of the Markdown it belongs to. `PL-0Y7J`, `PL-T1X0` and
`PL-V2HK`, all members, fixed other heading and definition readers; this one
reads the diff rather than the file, so none reached it.

**Done when.** `changed_tokens` takes a removed heading from
`markdown.headings` over the base and head copies, as `_changed_definitions`
reads Python through `read_logical_lines`, pinned by a `removed headings, ` case
in `PL-R417`'s guard for both forms, failing on today's reader.
