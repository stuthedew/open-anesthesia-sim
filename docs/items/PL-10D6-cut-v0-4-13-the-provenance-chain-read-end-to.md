---
id: PL-10D6
title: "Cut v0.4.13: the provenance chain read end to end, the Flet decision recorded, and doc-consistency-checks completed"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases
added: 2026-09-12
closed: 2026-09-12
pr: 495
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.13"' pyproject.toml && test -f docs/releases/v0.4.13.md
---

**Problem.** Cut v0.4.13: the provenance chain read end to end, the Flet decision recorded, and doc-consistency-checks completed

**Why it matters.** Eleven items had landed since v0.4.12 and `doc-consistency-checks`
had completed, which is past the point where release notes can be written from
memory rather than from the store.

**The version is 0.4.13, chosen rather than incremented** (this session, on the
project owner's delegation of 2026-09-12: "make a version. You decide").
`ROADMAP.md`'s "Versioning decision" says the number marks the capability
boundary a release crosses. **This one crosses none.** No equation, parameter,
unit, numerical method, solver step or interface element moved;
`src/anesthesia_sim/core/` is byte-identical to v0.4.12, and
`src/anesthesia_sim/data/` changes only in what its entries say about their own
numbers. All eleven items are provenance, documentation, tooling or a recorded
decision.

The one argument for going higher was the Flet decision, and it does not hold:
`PL-QXSB` *decided* to leave Flet and scoped the port as v0.5.1, and `PL-55DH`'s
spike is explicitly disposable and touches no shipped `app/` module. A decision
to change toolkits later is not a capability crossed now, and numbering it as
one would say a user-visible thing changed when none did - the same false
precision this project refuses for a displayed value. v0.5.0 was never a
candidate: it is scoped, gated, and its gate stands at 56 of 152.

**What was done.** `make release VERSION=0.4.13`, which bumped `pyproject.toml`,
relocked `uv.lock`, wrote `docs/releases/v0.4.13.md` and stamped the eleven
items. Then the three things it names as owed by hand: the version-table row,
moving the `current baseline` mark off v0.4.12, and the baseline section - the
prose saying what the release was *for*, which nothing generates.

**Preconditions checked before cutting**, both of which `bin/docket release`
refuses on: v0.4.12 is tagged on the remote (`git ls-remote --tags`), and no
other session is cutting - `list_sessions` showed one session running, this
one, with the rest archived. That check is `PL-66FP`'s, two sessions having cut
v0.3.7 within the hour.

**The tag is outstanding and is the project owner's to push**, `PL-N936` having
established that a session's tag push fails while reporting success.
