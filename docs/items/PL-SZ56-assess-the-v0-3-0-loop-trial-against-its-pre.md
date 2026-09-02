---
id: PL-SZ56
title: Assess the v0.3.0 loop trial against its pre-registered readouts
priority: P2
effort: S
status: ready
classes: infra
feature: planning-cadence
touches: docs/releases/v0.3.0.md, ROADMAP.md
added: 2026-09-02
verify: grep -q "Loop trial" docs/releases/v0.3.0.md
---

**Problem.** v0.2.8's claim is not that the tooling exists but that *the
development loop is reliable enough to run two long scientific milestones
through*. Nothing tests that claim. v0.3.0 is the natural test case — nine
frozen entries, mixed sizes, both `M` entries already carrying decided
designs, so it exercises the loop rather than the design work that would
confound it — and the project owner approved using it as one (2026-09-02).

**Why it matters, and why the numbers are frozen here rather than gathered
later.** Assessing one's own process after the fact produces a narrative,
because the criteria get chosen once the outcome is known. This project already
refuses that standard for scientific claims; a workflow claim it will act on
for two milestones deserves the same treatment. So the readouts, the t=0
values, and the thresholds are recorded *before* v0.3.0's first entry starts,
and the close-out compares against what is written here rather than against
what turns out to be flattering.

**Baseline, measured 2026-09-02 on `main` at `02a6d0d`.** Windows are tag to
tag; the v0.2.8 window is `v0.2.7`..`v0.2.8`, 2026-08-30 to 2026-09-01.

1. **Product churn against apparatus churn.** `src/` moved by `+3/-3` across
   v0.2.8 (the three comments its release note names) while `.claude/`,
   `tools/`, `subprojects/`, `bin/` and `Makefile` moved by `+8093/-1370`.
   The preceding v0.2.7 ran the other way: `src/` `+94/-10` against apparatus
   `+482/-29`. Commands:
   `git diff --shortstat v0.2.8..v0.3.0 -- src/ tests/` and
   `git diff --shortstat v0.2.8..v0.3.0 -- .claude/ tools/ subprojects/ bin/ Makefile`.
   *Threshold:* v0.3.0 fails this readout if apparatus lines changed exceed
   `src/` plus `tests/` lines changed. Seven of the nine entries touch `src/`
   directly, so a release that still comes out apparatus-heavy is measuring
   the apparatus becoming the work.
2. **Net queue change.** Over the v0.2.8 window the store took in 141 items
   and closed 104: **net +37**, against 70 shipped. The `safety`/`science`
   subset — the Gate 1 seed — was 9 filed, 5 still open.
   *Threshold:* net ≤ 0 means the loop converges; +1 to +20 is acceptable for
   a release clearing inherited debt; above +20 the loop generates work faster
   than it clears it and the two milestones after this one are at risk.
   *Stated confound:* v0.2.8's +37 includes a one-off repository-wide review
   that filed 65 items on 2026-08-30 alone. v0.3.0 has no such review planned,
   so a lower number is partly expected and the comparison is weak in v0.3.0's
   favour. Say so in the close-out rather than claiming the improvement.
3. **Escaped defects.** An item classed `defect` filed during the v0.3.0
   window whose `touches` names a file an *already-closed* v0.3.0 entry
   changed — i.e. the gates passed work that was wrong.
   *Threshold:* zero against a `safety`-classed entry (`PL-026`, `PL-0MLQ`,
   `PL-NV9W`). One is a finding that the gates did not do their job on exactly
   the class they exist for. No v0.2.8 baseline was computed; this readout is
   absolute rather than comparative, and that is a limitation to state.
4. **Stranded items.** `bin/docket stranded`. **t=0 is 0**, and that is a
   number this session created: it was 3 on the morning of 2026-09-02
   (`PL-D1ZY`, `PL-N092`, `PL-Y4Q4`), each on a branch with no open pull
   request and one deletion from lost.
   *Threshold (amended 2026-09-02, before v0.3.0's first entry):* zero items
   stranded on a branch with **no open pull request and no commit in the last
   48 hours**. A live session's branch appearing in `stranded` is expected and
   is not a finding — the command says so itself, and `bin/docket flight` adds
   that "a live session and a branch nobody will merge look the same here; the
   age is what separates them". The failure is a branch nobody will merge,
   which is what the three recovered this morning were.

   *Why it was amended rather than left frozen.* As first written the
   threshold was "0 at every check", which fires on normal parallel work: a
   second session had an open triage branch within the hour, and the original
   wording scored that a failure. An instrument that fires on ordinary
   operation measures nothing, and the amendment narrows what counts rather
   than relaxing it. It is recorded here with its date and reason, and made
   before the first entry started, because an assessment criterion changed
   *after* seeing the outcome is the retrofit this whole item exists to
   prevent. Any further amendment gets the same treatment or it is not one.
5. **Digest self-reported blindness.** The session-start digest's "N refs
   could not be compared with origin/main on the history this checkout holds"
   line. **t=0: firing in every session**, naming 2 refs on 2026-09-02, which
   degrades the ranking answer six commands give.
   *Threshold:* the line stops firing, or `PL-K2ZK` (deepen the clone once so
   the in-flight read answers instead of declining) is closed with its reason.
   A digest that declines to answer in every session of a release is not a
   loop that is reliable enough for two milestones.

The resident-instruction line count is deliberately **not** pre-registered
here: `tools/doc_check.py` already prints it on every `make check` run and
reports its own delta against `origin/main`, so it needs no protocol. It stood
at 505 lines on 2026-09-02 after `PL-D1ZY`.

**Two confounds to record now rather than discover at close-out.** First,
`PL-L9JS` (eight open items carry a `verify:` command that passes without
their work) is itself a Gate 0 entry, so the trial repairs one of its own
instruments mid-run: verify-command reliability measured at close-out is not
measuring the same thing it measured at the start. Second, `bin/docket check`
reported four live grooming advisories at t=0, one of them that `PL-0MLQ` —
the entry `next` will offer first — carries a `verify:` command selecting no
test. The instruments are partly miscalibrated at t=0 and the close-out should
say so rather than reading their output as clean.

**Deliberately not built: a command for this.** Every readout above comes from
an existing `bin/docket` subcommand or a one-line `git diff --shortstat`.
Building `bin/docket vitals` to measure whether the project is overbuilding
workflow apparatus would be the failure mode under test arriving through the
door marked "measurement", and `CLAUDE.md`'s gate for new tooling is whether it
will genuinely run again — which the v0.3.0 run is the evidence for, not a
prediction to act on now. Gate 1, 2 and 3 will each want this readout; if the
trial shows the numbers were worth having, the command is built then, with a
shape the trial has argued for. Filing that possibility as an item now would
put unworkable work in the queue.

**Where.** A `## Loop trial` section in `docs/releases/v0.3.0.md`, written as
part of cutting the release.

**Do this at close-out, not before.** Started when v0.3.0's last gate entry is
`done` or `dropped` and before the tag is pushed, so the answer lands in the
release notes rather than after them.

**Done when.** `docs/releases/v0.3.0.md` carries a `## Loop trial` section
giving each of the five readouts above its measured v0.3.0 value against the
frozen t=0 value and threshold, a pass/fail per readout with the two confounds
stated, and one paragraph answering the only question that matters: whether
v0.2.8's claim — that the loop is reliable enough to run two long scientific
milestones through — held, and what to change before v0.4.0 if it did not.
