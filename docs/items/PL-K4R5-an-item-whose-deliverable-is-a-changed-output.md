---
id: PL-K4R5
title: An item whose deliverable is a changed output string always REJECTs docket verify --self, because falsifies: can only be declared on the base's copy before the work
priority: P3
effort: S
status: untriaged
touches: subprojects/docket/src/docket, .claude/skills/docket
added: 2026-09-20
payoff: stops a correct close-out spending the owner's attention on an explained-away REJECT, every time an item changes what a command prints
---

**Problem.** An item whose deliverable is a changed output string always REJECTs docket verify --self, because falsifies: can only be declared on the base's copy before the work

**Why it matters.** `bin/docket verify --self` keeps four integrity checks
absolute, and "no existing assertion removed" is one of them - correctly, since
a session may re-scope its own commission but may not weaken what measures it.
The exemption is `falsifies:`, read from the base's copy of the item so that a
reviewer wrote it first, which is the whole worth of the field.

But a whole class of item cannot satisfy that. Where the deliverable *is* a
changed output string - `PL-FCM3` on 2026-09-20 is the worked example - the
test pinning the old string must change, and there is no arrangement of the
tests that keeps it. So:

- `bin/docket new` writes no `falsifies:`, and nothing in the capture rule
  suggests one.
- Triage could write it, but only by opening the test file and copying the
  exact assertion line, which is work done away from the work - the practice
  the `verify:` rules already identify as how every wrong command here came to
  exist.
- The session doing the work knows the string precisely, and is the one party
  forbidden to declare it.

The result is a `REJECT` on correct work, which the skill handles by telling
the session to report it. That is the right fallback and it is not free: it
spends the project owner's attention at every such item, and a `REJECT` that
is routinely explained away is the shape `CLAUDE.md` names as an advisory
being routed around.

**What is not being proposed.** Not relaxing the check, and not letting a
session declare its own exemption. Both are the thing the field exists to
prevent.

**Done when.** Either the gap is closed - something writes `falsifies:` at the
moment the class of item is recognised, before the work, or the check learns to
tell a *replaced* assertion from a deleted one - or the case is recorded as
accepted friction with its reasoning, so the next session meeting it stops
re-deriving this.

**Decision needed.** Whether this is worth closing at all. One count would
settle it: how many closed items removed or reworded an existing assertion, and
how many of those carried a `falsifies:`. It has not been run.

**`PL-K82G` already refused the fallback this leaves in place.** It is the item
that built `falsifies:`, closed in `v0.4.27`, and it weighed "leave it absolute
and document the `REJECT`" as one of four candidates and rejected it by name,
on `CLAUDE.md`'s "a check earns its place every run": *"a gate a correct
close-out trips, which the session is then expected to talk its way past, is
the defect that trains a reader to skim the block where a real failure is
printed."*

That is exactly what happened closing `PL-FCM3` on 2026-09-20, three releases
later. The field existed and was unusable: nothing on the capture or triage
path writes it, and the one party who knows the assertion string verbatim - the
session doing the work - is the party `front_matter_check` correctly forbids
from declaring it. So the close-out fell back to reporting the `REJECT` in a
reply, which is the disposition `PL-K82G` ruled out.

This is therefore not a re-opening of `PL-K82G`'s decision. Its reasoning is
accepted whole; what is reported is that the mechanism it built does not reach
the case it was built for unless somebody writes the field before the work, and
nothing yet does.
