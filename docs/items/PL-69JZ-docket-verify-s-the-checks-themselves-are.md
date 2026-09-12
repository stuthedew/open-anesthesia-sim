---
id: PL-69JZ
title: docket verify's 'the checks themselves are unedited' audit REJECTs every item whose declared work is editing a .claude rules file, since gate_paths includes .claude and touches is not consulted
priority: P2
effort: S
status: done
classes: defect, infra
feature: delegation
milestone: v0.4.14
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, docket.toml
added: 2026-09-07
closed: 2026-09-12
pr: 496
verify: uv run pytest subprojects/docket/tests/test_verify.py && grep -q 'def test_a_self_audit_reports_a_declared_gate_path_instead_of_refusing' subprojects/docket/tests/test_verify.py
---

**Problem.** docket verify's 'the checks themselves are unedited' audit REJECTs every item whose declared work is editing a .claude rules file, since gate_paths includes .claude and touches is not consulted

**Observed.** `bin/docket verify PL-X19T` on 2026-09-07, against a branch
whose whole job was rewriting three sentences in two `.claude/rules/*.md`
files and one brief - all four paths declared in the item's `touches`:

```
FAIL  the checks themselves are unedited - .claude/rules/expert-review.md, .claude/rules/sources-and-docstrings.md
REJECT
```

**Mechanism.** `subprojects/docket/src/docket/verify.py` collects the diff's
paths that fall inside `config.gate_paths` and fails the check if any do.
`gate_paths` defaults to `Makefile`, `pyproject.toml`, `.github`, `.claude`
and `docket.toml`, and this repository does not override it. The audit never
consults `touches`, so an item *assigned* to edit a rules file fails it by
construction. `feature: worker-instructions` holds 32 items and most of them
are that shape.

**Not the same bug as `PL-66PR`, though it lands on the same command.** That
one is the `touches` audit refusing a branch that carries a capture, and the
fix it proposes - exempt a new untriaged item file, which is mechanically
distinguishable - does nothing here. This branch failed both audits, for
unrelated reasons.

**The audit is right about the case it was built for**, which is what makes
this a design question rather than a bug to patch out. Its sentence in
`config.py` is exact: "a delegated diff that edits one has changed the thing
measuring it, so the measurement means nothing." For a delegated worker that
holds. A session working an instruction-writing item is not being measured by
the file it is editing - the rule it rewrites governs *replies*, not the
diff - but `verify` cannot see that difference, and "the paths are declared in
`touches`" is not the distinction either: `touches` is written by whoever
triaged the item, which on a delegated item is the same hand that would want
the exemption.

**Three routes, and the second is probably right.** (1) Exempt a gate path
that appears in the item's own `touches`, and say in the output that the audit
was voided for it - cheapest, and weakest. (2) Mark such items
`not-delegable:` with the reason, which is the field that already exists for
work no delegated check can prove, and leave the audit absolute - the REJECT
then never fires because the item never enters the lane. (3) Leave it, and
treat a REJECT on an instruction item as expected - which trains a reader to
skim a REJECT, and `CLAUDE.md` names that as the failure mode a check must not
have. Recommend (2), and note it costs a triage step per item rather than a
code change.

**Route (2) does not fix the case observed above** (noted 2026-09-08 from
`PL-S2L4`, which reaches the same two lists from the delegation end). Marking
such items `not-delegable:` keeps them out of `bin/docket delegable`, but
`cmd_verify` in `subprojects/docket/src/docket/cli.py` runs `verify_batch` on
whatever ids it is given and never consults `Item.delegability`. `PL-X19T` was
a session running the close-out audit on its own branch, not a delegated
worker, so the REJECT above fires again under (2) exactly as it did. What (2)
does buy is that `delegable` stops offering work the audit will refuse - which
is `PL-S2L4`'s subject, and which `PL-S2L4` proposes to get from
`Item.delegability` reading `gate_paths` rather than from a triage step per
item. That leaves this item with the narrower question it should have had:
what `bin/docket verify <id>` should report when a *non-delegated* session
audits its own branch against an item whose declared work is a gate path.

**Found.** `PL-X19T` (align the tier-3 absolute in the instruction files with
the practice), 2026-09-07, running the close-out audit on its own branch.

**Why it matters.** The audit fires on correct work and cannot tell it from the
thing it exists to catch. `feature: worker-instructions` holds 33 items and most
of them edit a `.claude` file, so for that whole feature a `REJECT` is the
expected result of a close-out audit - which trains a reader to skim the block
where the *protected-path* failure, the one that matters, is printed. That is
precisely the failure mode `CLAUDE.md` says a check must not have.

It has already been routed around rather than fixed. `bin/docket triage` now
prints, as a standing rule, that `touches` naming a gate path "makes the item
non-delegable for a second reason: `docket verify` fails any diff that edits the
checks, so offering the work would mean refusing it once done." The project has
absorbed the defect into its triage policy, which keeps delegated work out of
the trap and leaves a session auditing its own branch still in it.

**Decision needed.** What `bin/docket verify <id>` should report when a
*non-delegated* session audits its own branch against an item whose declared
work is a gate path. The three routes are in the section above; route (2) was
recommended and then shown not to reach this case, and `PL-S2L4` has since taken
the delegation half of it by making `Item.delegability` read `gate_paths`. So
what is open is narrower than when this was filed: either the audit learns to
distinguish a declared gate-path edit and says out loud that it voided itself
for one, or `verify` learns that it is auditing a non-delegated branch, or the
`REJECT` stands and is documented as expected for this class of item.

**Done when.** The question above is answered and the answer is implemented or
recorded - either the audit changes, with a test for what it still refuses, or
this item is `dropped` with the reasoning written down.

## Answered 2026-09-12 (project owner): an explicit self-audit mode

**The decision.** `bin/docket verify` gains `--self`, saying the caller is
auditing its own branch rather than reviewing a delegated one. In that mode the
four **commission** checks - `diff stayed inside touches`, `no protected path
modified`, `the checks themselves are unedited`, `item front matter unchanged` -
report as advisories: still run, still naming every path they found, with the
reason they are not refusing. The four **integrity** checks are untouched: no
suppression added, no assertion removed, the item's own command passes, the
project's own checks pass.

**Why that line and not another.** A session may legitimately re-scope its own
commission - it is the reviewer - but it may not weaken the thing that measures
it, and it may not skip the test. Route (1) of the three above (exempt a gate
path that appears in the item's own `touches`) was rejected for being both
weaker and narrower: `touches` is written by whoever triaged the item, so on a
delegated item it is the same hand that would want the exemption, and it does
nothing for the front-matter or batch-scope cases. Route (2) was already shown
not to reach a non-delegated session auditing its own branch. Route (3) is the
one `CLAUDE.md` names as the failure mode a check must not have.

**Three items, one fix.** `PL-B5YN` (front matter on every close-out) and
`PL-4LT9` (a batch branch audited as one item) are the same defect seen from
two other angles - `docket verify` unable to tell a delegated branch from a
self-audit - and all three close together.

**The policy this retires.** `bin/docket triage` prints, as a standing rule,
that a `touches` naming a gate path makes an item non-delegable "because
`docket verify` fails any diff that edits the checks, so offering the work
would mean refusing it once done". That is this defect absorbed into policy.
The delegation half of it stands on its own through `Item.delegability`
(`PL-S2L4`); what it no longer has to carry is the audit refusing correct work.
