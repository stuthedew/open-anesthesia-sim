---
id: PL-VRMK
title: 27 of the gate's 112 open entries declare docs/MODEL.md, so a quarter of Gate 1 can only be worked one item at a time
status: untriaged
added: 2026-09-06
---

**Problem.** Counted 2026-09-06 against the frozen Gate 1 list: of its 112 open
entries, 27 name `docs/MODEL.md` in `touches`. `docket concurrent` treats a
shared path as contention, so those 27 mutually exclude one another and appear
in each other's "Cannot run alongside" list. The gate's science half is
therefore serial by declaration, whatever the owner's session budget - a
session asked for three concurrent gate items can be offered at most one of
them.

**Why it matters.** The beat is clearing the gate, and the science entries are
the expensive part of it - the ones wanting the strongest model at high effort.
Serializing them is the single largest limit on how fast the gate closes. It is
also only partly real: most of these items add or correct one section of
`docs/MODEL.md` and would merge cleanly against a different section, so the
declaration is coarser than the actual contention. `concurrent` cannot see that,
because `touches` has no unit smaller than a file.

**Where.** `docs/items/*.md` `touches:` fields; the comparison is in
`subprojects/docket/src/docket/` (whatever `concurrent` reads). `docs/MODEL.md`
is the contended file.

**Done when.** Either the contention is real and the answer is sequencing
advice - `concurrent` says which of the 27 to land first rather than refusing
all but one - or it is not, and `touches` gains a sub-file unit (a heading, a
section anchor) that lets two items in different sections of `docs/MODEL.md`
run together. Decide which before building either.
