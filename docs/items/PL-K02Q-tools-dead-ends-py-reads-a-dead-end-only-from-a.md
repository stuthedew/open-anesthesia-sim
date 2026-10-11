---
id: PL-K02Q
title: tools/dead_ends.py reads a dead end only from a bullet opening with a dash at column 0, so one written with a star or plus bullet, or indented one to three spaces, is neither shown in the session-start digest nor checked, with nothing reported; latent
priority: P3
effort: S
status: ready
classes: defect
touches: tools/dead_ends.py, tests/unit/test_dead_ends.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-06
payoff: A dead end written in any bullet form CommonMark opens reaches the digest and the id check, or is refused by name, instead of vanishing
verify: grep -q 'def test_an_entry_in_every_bullet_form_is_read_or_refused' tests/unit/test_dead_ends.py
---

**Problem.** tools/dead_ends.py reads a dead end only from a bullet opening with a dash at column 0, so one written with a star or plus bullet, or indented one to three spaces, is neither shown in the session-start digest nor checked, with nothing reported; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing
`tools/dead_ends.py`. `ENTRY` and `OPENING` anchor on a dash and a space at the
start of the line. CommonMark 0.31.2 opens a bullet list item with a dash, a
plus or a star, after up to three spaces of indentation (§ 5.2), so each of
those forms is the same entry to a reader of `docs/dead-ends.md`.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15:

```text
* **Star bullet** - written with a star.
  - **Indented two** - indented two spaces.
+ **Plus bullet** - written with a plus.
```

`entries` returned nothing for each and `check` reported nothing, where the
same entry led by a dash at column 0 is emitted. Latent: every tracked entry is
written with a dash at column 0.

**Re-confirmed 2026-10-11** on main at `16a20a4f`: each form above, citing an
id no item carries, gives `entries` nothing and `check` nothing, where the same
entry led by a dash at column 0 is emitted and its id refused. No line of
`docs/dead-ends.md` opens in another form, so it stays latent.

**Why it matters.** A dead end written in any other bullet form is dropped from
the session-start digest with nothing said, so the refuted approach it records
reaches no session and the ids it cites go unchecked: a partial reading handed
over as the whole file, which the apparatus floor refuses.

**Generator check.** Not a member of `PL-R417`: each form is one line, read
whole and not matched. `PL-QFFF`, open, is the same pattern missing an entry
whose title is followed by a parenthetical; one fix to `ENTRY` should take
both. The fact misread is which line opens a Markdown list item; no head's
`misread:` states it, and `PL-QFFF` (ready) shares the pattern rather than the
fact, so this is a one-off, worth one pass with it.

**Done when.** `dead_ends` reads an entry in every bullet form CommonMark gives
one, or refuses an unread bullet by name as `PL-F5B9` does for a wrapped title,
pinned by a test for each form above.
