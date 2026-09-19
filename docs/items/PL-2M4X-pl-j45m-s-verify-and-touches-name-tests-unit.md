---
id: PL-2M4X
title: PL-J45M's verify and touches name tests/unit/test_docket_digest_hook.py, a shell-hook test file that cannot exercise release.py, so its pytest half proves the wrong tree and a worker would edit the wrong file
priority: P3
effort: S
status: done
classes: defect, infra
feature: queue-hygiene
touches: docs/items/PL-J45M-release-due-s-second-arrangement-is-positional.md
added: 2026-09-16
closed: 2026-09-19
pr: 690
verify: ! grep -qE '^(touches|verify):.*test_docket_digest_hook' docs/items/PL-J45M-release-due-s-second-arrangement-is-positional.md && grep -qE '^touches:.*src/docket/roadmap\.py' docs/items/PL-J45M-release-due-s-second-arrangement-is-positional.md && grep -qF 'supported = plan.beat != IMPLEMENT or plan.own_scope is not None' docs/items/PL-J45M-release-due-s-second-arrangement-is-positional.md
---

**Problem.** PL-J45M's verify and touches name tests/unit/test_docket_digest_hook.py, a shell-hook test file that cannot exercise release.py, so its pytest half proves the wrong tree and a worker would edit the wrong file

**Found 2026-09-16 while closing `PL-VFD8` and `PL-188T`**, which had the same
wrong path and were corrected as part of that work.
`tests/unit/test_docket_digest_hook.py` tests `.claude/hooks/docket-digest.sh`
end to end against real git fixtures; its own docstring says the digest itself
"is `bin/docket digest`, tested with the rest of that package". It imports no
`docket` module and holds no `release_offer` test, so the pytest half of
`PL-J45M`'s command cannot fail for the reason the item is about. The release
tests are in `subprojects/docket/tests/test_release.py`.

**Not vacuous, which is why this is `S` rather than urgent.** The command's
second half - `! grep -q "supported = plan.beat != IMPLEMENT or plan.own_scope
is not None" subprojects/docket/src/docket/release.py` - is a real
specification and still exits 1 today, so the command as a whole fails
correctly. What is wrong is the half the skill's paired shape exists for: "the
pytest half proves the file's suite healthy", and here it proves a different
suite's health. `touches` is the more expensive half of the error - a worker
commissioned on `PL-J45M` would be told its test file is the shell-hook one,
and `docket verify` reads `touches` to decide whether a delegated branch
exceeded its commission.

**Why it matters.** `docket verify` reads `touches` as the allowlist for a
delegated diff - `verify.py:692` keeps the changed paths `_within` does not
match, by exact path or directory prefix - and the "diff stayed inside
`touches`" check it builds from that is advisory only under `--self`. For a
delegated worker it is a plain REJECT. `PL-J45M` is offered by `bin/docket
delegable` today, at P3, with the wrong command printed verbatim beneath it, so
this is not untidy prose: it is the commission a cheaper model is handed, and a
worker doing exactly what was commissioned is refused for having done it.

The omission costs more than the wrong path does. `_release_due` - the
classifier `PL-J45M` is about - is at `roadmap.py:1310`; `release.py` names it
only in the comment at `:550` that codes around it. `PL-J45M`'s own "Done when"
asks for that classifier fixed and the `supported` workaround removed, which is
`roadmap.py`, `release.py` and `subprojects/docket/tests/test_release.py`, and
`touches` declares one of the three. (`test_roadmap.py:404` pins the second
arrangement's passing case and `:1236` asserts `RELEASE` on the same fixture;
whether either joins the list is a reading of the fix rather than of this
correction. The `supported` line the brief cites at `release.py:551` now sits at
`:558`, `PL-VFD8` having rewritten the guard around it.)

The pytest half is wrong in the other direction: it cannot fail at all.
`tests/unit/test_docket_digest_hook.py` imports `subprocess`, `sys` and
`pathlib` and no `docket` module, the string `release` does not occur in it, and
its fixtures leave the store empty so `digest` prints nothing - "these tests are
about the branch line", as its own docstring says. It does load `release.py`
transitively, because `bin/docket` runs the package and `docket.cli` imports
`docket.release`, so an import-time break there would silence the hook; that is
the whole of its reach into the module, and it is blind to `release_offer`'s
behaviour, which is the entirety of what `PL-J45M` is about. The suite passes on
the tree the item exists to change and would pass on the tree after it, which is
the one shape "run the command and watch it fail" was adopted to catch.

**The same wrong path stands in four other open items**, and this one does not
scope itself to them: `PL-2M5T` in `touches`, `PL-FT3M` in `verify`, `PL-4PC5`
and `PL-Z85N` in both. (`PL-YKXQ` names it in both and is right to - its work is
the hook itself.) Each needs its own subject read to say what would prove it.
The class is wider than this file and has a mechanical rule - six violations,
no false positives - which is `PL-6YL1`, filed separately on `PL-RWBV`'s
batch-and-mechanize precedent rather than folded in here.

**Done when.** `PL-J45M`'s `touches` names
`subprojects/docket/src/docket/roadmap.py`, where `_release_due` actually is,
alongside `release.py` and `subprojects/docket/tests/test_release.py`; its
`verify` runs that release suite - `subprojects/docket/tests/test_release.py` by
that path - rather than the hook one; the command has been run and watched fail
for the right reason; and the `! grep` half is left exactly as written, it being
what keeps the item from reading as closeable while `_release_due`'s positional
classifier stands.

**Re-pointed by `PL-6TP8`, 2026-09-19.** The `touches` correction stands under
either answer to `PL-6TP8`'s shape half: `PL-J45M` declares `roadmap.py`,
`release.py` and `subprojects/docket/tests/test_release.py`. The pytest half is
the contract's second obligation failing - a clause proving a different tree's
health - and it is replaced by the release suite if the field keeps
prerequisite clauses, or removed if it does not, leaving the `! grep` that is
the specification.

**Decided 2026-09-19, later the same day.** The shape half was ratified: the
pytest half of `PL-J45M`'s command is removed rather than replaced, leaving
the `! grep` that is the specification, and the `touches` correction stands.
This item's own `verify:` still pins `test_release.py` as a `verify:` target,
which that shape does not produce, so rewrite it first when starting this.

**Closed 2026-09-19 under `PL-2T03`, in the session that closed `PL-J45M`.**
`PL-J45M`'s `touches` now declares `subprojects/docket/src/docket/roadmap.py`,
`subprojects/docket/src/docket/release.py` and
`subprojects/docket/tests/test_release.py`, and its `verify:` is the `! grep`
alone - the discriminator, per the shape half of `PL-6TP8` ratified the same
day - which was run before the work (exit 1) and after it (exit 0). This
item's own command was rewritten first, as the note above asks: it no longer
pins `test_release.py` as a `verify:` target and carries no prerequisite
clause of its own. The four other items closed in the same session lost their
pytest halves the same way, as the repair-as-started rule has it.
