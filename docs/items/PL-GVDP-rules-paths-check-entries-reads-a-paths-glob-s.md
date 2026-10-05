---
id: PL-GVDP
title: rules_paths_check.entries reads a paths: glob's trailing comment as part of the glob - '- "/src/**" # why' is reported unanchored with a garbled replacement, and '- /src/foo.md # was /scr/' as pointing at nothing, where YAML 1.2.2 6.6 strips the comment and reads /src/**; loud rather than silent, and latent since no rule writes one (found building PL-PPNV)
status: untriaged
added: 2026-10-05
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
