---
id: PL-GVDP
title: rules_paths_check.entries reads a paths: glob's trailing comment as part of the glob - '- "/src/**" # why' is reported unanchored with a garbled replacement, and '- /src/foo.md # was /scr/' as pointing at nothing, where YAML 1.2.2 6.6 strips the comment and reads /src/**; loud rather than silent, and latent since no rule writes one (found building PL-PPNV)
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/rules_paths_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-05
payoff: a comment after a paths: glob no longer makes the rules check refuse a sound rule and offer a replacement glob that names nothing
verify: grep -q 'def test_a_comment_after_a_glob_is_not_part_of_it' tests/unit/test_rules_paths_check.py
recurrences: 2026-10-06 PL-BM8T withdrawn 2026-10-06 PL-R417
---

**Problem.** rules_paths_check.entries reads a paths: glob's trailing comment as part of the glob - '- "/src/**" # why' is reported unanchored with a garbled replacement, and '- /src/foo.md # was /scr/' as pointing at nothing, where YAML 1.2.2 6.6 strips the comment and reads /src/**; loud rather than silent, and latent since no rule writes one (found building PL-PPNV)

**Not a recurrence of `PL-PPNV`.** `docket new` matched it there on the
`touches` the two share. `PL-PPNV` is where an over-indented `- ` line ends a
glob; this is where one line's glob ends, at a comment, which `entries` reads a
different way and gets wrong in a different place: `_unquote` takes the glob
from the text after `- ` or `paths:` with its comment still on it.

**Reproduced 2026-10-05** under Python 3.11.15, on the `PL-PPNV` branch, against
PyYAML 6.0.3's reading of the same text (YAML 1.2.2 § 6.6 ends a value at a
`#` that white space precedes):

```
front matter                    entries reads             PyYAML reads
  - "/src/**" # why             '"/src/**" # why'         '/src/**'
  - /src/foo.md # was /scr/     '/src/foo.md # was /scr/' '/src/foo.md'
paths: "/src/**" # why          '"/src/**" # why'         '/src/**'
```

`problems` then reports the first as unanchored, offering `/"/src/**" # why` as
the fix, and the second as pointing at nothing. Both are loud, so no rule passes
on them, but each is a false answer about a sound rule. No rule in
`.claude/rules/` writes a comment after a glob today (25 globs, measured the
same day), so it is latent.

**Re-run at triage, 2026-10-05,** on `main` at `b67dace8`, which holds
`PL-PPNV`: a rule whose `paths:` holds `- "/src/**" # why` and
`- /src/foo.md # was /scr/` over a tree holding `src/foo.md` gave `entries`
both comments inside the globs, and `problems` reported the first as matching
at any depth, offering `/"/src/**" # why`, and the second as pointing at
nothing, its nearest existing path `src`. Still holds.

**Why it matters.** `rules_paths_check` is the one check that a path-scoped
rule reaches the files it names, and a comment beside a glob is the natural
place to say why the glob reads as it does. Written there, it makes the check
refuse a sound rule, and the replacement it offers is a glob naming a quoted
path that exists nowhere - one a session following the message would commit,
so the rule then loads for nothing.

**Generator check.** Not a member of `PL-R417`, which recorded it beside
rather than in itself at link 13: the fact misread is where a YAML scalar ends
on its own line, at a `#` that white space precedes (YAML 1.2.2 § 6.6), not
where a statement continued across lines ends. The head's guard holds
`rules paths, a comment between two items` and `pull request trigger, an on:
key carrying a comment`, a comment on a line of its own and on a key's line,
each read for where a value continues; neither is a comment after a value. No
head's `misread:` states this fact, and no other open brief names a comment
read into a scalar (searched 2026-10-05), so a one-off.

**Done when.** `entries` ends a glob at a `#` that white space precedes and no
quotation holds, for a `- ` item and for a glob on the `paths:` line, and keeps
a `#` inside quotes or one no space precedes as the glob's; a test in
`tests/unit/test_rules_paths_check.py` reads the three forms above as PyYAML
reads them, and fails on today's reader.
