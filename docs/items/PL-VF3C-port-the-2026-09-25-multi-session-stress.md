---
id: PL-VF3C
title: Port the 2026-09-25 multi-session stress harness into subprojects/docket/tests as a regression suite: each reproduced violation a named scenario test, the seeded random interleavings behind a slow marker, and a fake forge that can say merged and closed as well as open
priority: P3
effort: M
status: blocked
classes: test, infra
feature: workflow-stress-2026-09
touches: subprojects/docket/tests/test_multisession.py, subprojects/docket/tests/conftest.py
blocked-by: PL-GPJ7, PL-HMZZ, PL-MB2W, PL-PVW2, PL-QHCW, PL-XBV4
added: 2026-09-25
---

**Problem.** Port the 2026-09-25 multi-session stress harness into subprojects/docket/tests as a regression suite: each reproduced violation a named scenario test, the seeded random interleavings behind a slow marker, and a fake forge that can say merged and closed as well as open

The harness (`harness.py` in the evidence archive, one stdlib file) builds a bare origin, a clone playing GitHub (squash-merge with `(#N)` subjects, branch deletion, closing), and N session clones, dates every commit from a world clock, and fakes pull-request state through `open_pull_requests_command`. It found eight violations across 19 scenarios and 180 seeded random steps; three were already filed (PL-X3NY, PL-QSGX, PL-WX87-adjacent). Today every one of those was found by a session stumbling on it during other work: 85% of apparatus defects filed 2026-09-15..25 were found while working another apparatus item.

**Why it matters.** Class B (distributed-state inference) is 26% of apparatus defect inflow and 12 of the 35 generator heads. A defect found by CI in bulk costs one fix; the same defect found by sessions arrives as one item per session that trips it.

**Done when.** The scenario matrix runs under `pytest` in the docket suite with each V1-V8 reproduction as a named test (xfail until its item closes), and a seeded random run is available behind a marker.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Triage, 2026-09-25.**
- Re-confirmed 2026-09-25 against 46954a81: `subprojects/docket/tests/` holds no `test_multisession.py` and no `conftest.py`, and nothing registers a `slow` marker (`pyproject.toml` has `addopts = "-ra"` only). The one multi-clone fixture is `test_claiming.py`'s private `_Remote`/`_Clone`: a bare origin and dated clones, with no forge clone, squash merge or fake pull-request state. The harness is the archive's `sim/harness.py`, 1,209 lines driving `bin/docket` as a subprocess. #1015-#1017 changed the claim and rename reads its scenarios drive, so each V1-V8 expectation is re-run against the current tree before it is pinned.
- **Blocked by the generator pause.** This is a new check, not a fix. It adds a scenario matrix held as xfail tests and a seeded random run whose findings become items, which is the kind of mechanism `CLAUDE.md` § "What this project is" holds while any open item carries `generator: live`. It fixes no generator's mechanism and no defect in what exists; it finds members.
- The part that serves generator work needs no lift and does not wait here. Each member's own **Done when** already asks for "a test holds scenario X" (`PL-1X56`, `PL-ZLJ9`, `PL-Y48N`), so the member fixes build the multi-clone world as they need it, starting from `_Remote`/`_Clone`.
- `blocked-by` names the six items carrying `generator: live` that day. Check that `bin/docket generators` marks no head "still generating" before unblocking, rather than this list. Building it sooner is the owner's call, made by asking (`PL-6Q9L`).
- For the design, once unblocked: with `-ra`, every xfail prints a summary line on every run until its item closes, which is a check firing without changing a decision.
- **Generator check.** One-off. It is infrastructure proposed for the distributed-state heads' members (`PL-XBV4`, `PL-MB2W`, the claim-integrity items), not an instance of a misread fact.
