---
id: PL-CGSS
title: The drift interpreter job reports success identically whether it tested a newer CPython or the pinned one, so its green proves nothing on its own
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
milestone: v0.3.1
touches: .github/workflows/drift.yml
added: 2026-09-02
closed: 2026-09-02
pr: 245
verify: grep -q 'reach past the pin' .github/workflows/drift.yml && grep -q 'PINNED_MINOR' .github/workflows/drift.yml
---

**Problem.** `drift.yml`'s `interpreter` job installs `python-version: '3.x'`,
which resolves to the newest stable CPython the runner offers. On the first
real run - `workflow_dispatch`, 2026-09-02, run 33695140322 - that was **CPython
3.14.7**, and `.python-version` pins **3.14.7**. The job relaxed
`requires-python`, removed `.python-version`, resolved 64 packages, passed 1165
tests, and reported success having tested *exactly the interpreter the project
already pins*.

That is correct behaviour and the wrong report. `3.x` is the right request -
when 3.15 ships it will resolve there and the job will genuinely test past the
pin. But today there is nothing newer, and the job's green is identical in both
cases. A reader seeing it assumes the newest interpreter was exercised.

**Why it matters.** This is the shape `PL-71P4` closed one instance of: a check
that passes without having tested what it claims. The job's own comment says it
relaxes the bound "rather than letting the job silently test the pinned
version", and that is precisely what happened - the relaxation worked, and the
runner had nothing newer to offer.

It is worse here than an ordinary uninformative pass, because the whole purpose
of `drift.yml` is to be the thing that notices. `ROADMAP.md`'s "Keeping the
toolchain current" says the schedule notices and the owner decides. If a green
`interpreter` job cannot distinguish "the next CPython works" from "the next
CPython does not exist", then for most of each year it is reporting nothing
while looking like it reported something - and the year it matters is the year
nobody re-reads the logs to check which case it was.

**Where.** `.github/workflows/drift.yml`, the `interpreter` job.

**Approach.** Capture the pinned minor before `.python-version` is deleted, and
after resolution compare it against what was actually installed. Say which case
this run was, in the log and in the job summary. Never fail on it: "no newer
interpreter exists" is the expected state for most of a release cycle, and
failing would make the job red for a year at a time, which is the routed-around
outcome `PL-ZBJ0` warned about and `CLAUDE.md`'s retirement test forbids.

**Found.** 2026-09-02, reading the logs of the first `drift` run - the manual
run recommended precisely because a scheduled workflow cannot be exercised from
a pull request. The verification found a real defect on its first use, which is
the argument for having asked for it.

**Done when.** The `interpreter` job states whether the interpreter it tested is
newer than the pinned one, in a form a reader sees without opening the logs, and
does not fail when it is not.

**Closed 2026-09-02.** The job now records `PINNED_MINOR` before removing
`.python-version`, and a step after resolution compares it against the resolved
interpreter and writes one of two verdicts to `$GITHUB_STEP_SUMMARY`:

- *tested past the pin* - names both versions and says the result is meaningful;
- *nothing newer exists yet* - names the version and says plainly that the run
  confirms the pin still works and nothing more.

**The second reading is also the trigger for raising the bound.** When it starts
saying "tested past the pin" and stays green, `requires-python`'s upper bound
can move - which is the decision `ROADMAP.md` reserves for the owner, now with
evidence attached rather than a guess.

**Also confirmed by the same run, and needing nothing.** `uv pip list
--outdated` named only `binaryornot`, `chardet` and `pydantic-core` - all
transitive, all held back by `cookiecutter`'s own pins rather than by this
project's bounds. Neither `flet` nor `pydantic` appeared, so no Flet 1.0 and no
pydantic 3 exists yet and the bound-crossing migration is not yet available.
The step did its job.
