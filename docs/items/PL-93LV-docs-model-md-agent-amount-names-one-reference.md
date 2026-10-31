---
id: PL-93LV
title: docs/MODEL.md § "Agent amount" names "One reference condition, where the model physically has two" without the § mark (PL-KZ99's conversion paragraph), so tools/doc_check.py advises on it every run and a rename of that Known-limitations entry would pass unreported
priority: P3
effort: S
status: ready
classes: docs, defect
touches: docs/MODEL.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-10-27
payoff: doc_check stops advising on the same sentence every run, and a rename of that Known-limitations entry is caught
verify: grep -qF '§ "One reference condition' docs/MODEL.md
---

**Problem.** docs/MODEL.md § "Agent amount" names "One reference condition, where the model physically has two" without the § mark (PL-KZ99's conversion paragraph), so tools/doc_check.py advises on it every run and a rename of that Known-limitations entry would pass unreported

**Reproduced 2026-10-31.** `python3 tools/doc_check.py check` exits 0 and
advises: `docs/MODEL.md` "One reference condition, where the model physically
has two" names a section without the mark. The sentence is in § "Agent amount",
in the paragraph on converting vapour to liquid.

**Why it matters.** The advisory fires on every run, which trains a reader to
skim doc_check's output where a real advisory also appears. And until the mark
is written, a rename of that Known-limitations entry would leave this pointer
dangling with no check firing.

**Done when.** The sentence writes § "One reference condition, where the model
physically has two", and doc_check no longer advises on it.

**Generator check.** One-off. The check that `PL-4FBP`'s line of work built
found it, so the fix held here (`PL-R4Y2`'s triage, 2026-10-31).
