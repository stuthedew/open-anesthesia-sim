---
id: PL-SK88
title: The in-flight answer needs a push to be true; a session-title read would close the window a push only shrinks
status: untriaged
added: 2026-09-02
---

**Problem.** `bin/docket flight`, `show` and `next` answer "is anybody already
on this item?" by reading refs, so an item is invisible until the session
working it has *pushed*. The `docket` skill's "Mode: start an item" already
hardened the reading side — `git fetch origin` then `bin/docket show <id>` —
and records that it still failed: "Observed 2026-09-01: a session checked, was
told nothing was in flight, and a branch carrying the item was pushed four
minutes later — the owner caught it, not the tooling." Observed again
2026-09-02, from the other side: this session was told `PL-007` had been
started elsewhere, and `show PL-007` marked nothing, because that session had
not pushed.

**Why it matters.** Two sessions doing one item costs a whole session plus a
merge conflict; `PL-PRHN` records exactly that happening on a triage pass. The
reading side cannot be hardened further — the skill's own words are that a
clean result means "nothing visible", never "nothing" — so what is left is
either to make sessions push sooner, which shrinks the window, or to read a
signal that does not depend on a push, which closes it.

**The alternative.** Sessions are already named after the item they work
(`CLAUDE.md`, "Name the work after the item"), and the harness can enumerate
other sessions and their titles. A pre-start check that read those titles
would see a session that has committed nothing at all, which no ref-based
answer can.

**What it costs, and why this is a question rather than a plan.**
`subprojects/docket/` is standard-library-only and has to answer in a bare or
offline checkout — that premise is why `flight` and `show` read refs the
checkout already holds rather than calling anything. A session-title read
cannot live in `docket` without breaking it. So the shape would be a check the
*session* runs before starting, with `docket` unchanged, and the design
question is whether a guard that exists only inside one harness is worth
having beside one that works everywhere.

**Done when.** A decision is recorded: either a session-title pre-start check
exists and the `docket` skill's start-an-item mode names it alongside the
fetch, or the option is recorded as rejected with the reason, so it is not
re-argued.
