---
id: PL-9MK6
title: Cut v0.5.13 from the 18 items finished since v0.5.12
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
resource: release-train
added: 2026-09-26
payoff: the 18 items finished since v0.5.12 ship under their own number and stop being re-offered in every session digest, and v0.5.12's notes point at the two pull requests its tag holds but this release describes
verify: grep -q "^version = \"0.5.13\"" pyproject.toml
---

**Problem.** Cut v0.5.13 from the 18 items finished since v0.5.12

The project owner agreed on 2026-09-26 to the Projects trial coordinator's
recommendation to cut v0.5.13 once `PL-20DL` had merged and `PL-MT3R` had
closed ("Agree with release recs"; project owner, 2026-09-26, ratified, over
cutting before both had landed). `PL-MT3R` closed with `#1116` and `PL-20DL`
merged as `#1136` at 21:29 UTC, so the coordinator started the "Cut v0.5.13"
thread for it.

**What was checked at filing.** `git ls-remote --tags origin` shows v0.5.12 as
the annotated tag `297fdfde` peeling to `05559059`, the cut's own merge
(`#1115`), so the cut is not refused on an untagged predecessor. `bin/docket
flight` shows no release item claimed, and the project's thread list shows no
other thread cutting one. `bin/docket release --dry-run` named 16 finished
items, completing `remote-copy`, and they matched `main`'s own history: the 18
pull requests merged after `#1115`, plus `#1113` and `#1116`, which merged after
v0.5.12's notes were written and before its cut merged. Those two sit inside
v0.5.12's tag and are described here, on `PL-V065`'s precedent, as `PL-84Z4`
recorded. The ten other ids those pull requests lead are `dropped`, and a
dropped item ships in no release. `bin/docket generators` marks no head still
generating, and no open item carries `generator: live`.

**The version is a patch**, on both halves of `ROADMAP.md` § "Versioning
decision" as `PL-5ZLQ` restates them: nothing a learner can reach moved
(`git diff v0.5.12 origin/main` leaves `src/`, `tests/reference/`,
`docs/MODEL.md` and `README.md` untouched), and every minor from v0.6.0 up is
given to a milestone.

**v0.5.12's notes owe a pointer, and the cut writes it.** `#1113` (`PL-PB8V`)
and `#1116` (`PL-MT3R`) resolve to v0.5.12 under `git describe --contains`, and
its notes name neither. Once v0.5.13's tag is pushed, v0.5.12's span is no
longer the newest, so `tools/doc_check.py`'s `check_tag_span_covers_its_notes`
fails `make check` until those notes carry an `### also inside this tag's span`
section naming both. The v0.5.8 cut (`PL-8543`, `#957`) wrote v0.5.7's the same
way.

**Cut 2026-09-26, at 18 items.** The first `make release VERSION=0.5.13`
stamped 16. `PL-77DZ` (`#1132`, the `inert_splitter` citations) merged to
`main` minutes later, before anything here but the claim was pushed, so `main`
was merged in and the cut re-run, stamping 17. `PL-YFT4` (`#1140`, the prune
guard refusing a `git config` read) merged after the cut was pushed as `#1141`
and before its closure was, and `main` was merged into `#1141` from outside
this session, so the cut was re-run once more, at 18. Each re-run keeps the
notes naming everything `main` held when the cut was taken, rather than leaving
a pull request inside v0.5.13's tag for v0.5.14 to describe. The title and
payoff were corrected to match each time.

The second re-run did not take the route `docket check`'s advisory names. It
says to merge the base in and re-run `make release VERSION=0.5.13`, which
"reclaims what this cut already stamped"; with the cut's notes written, that
run exits 1 on "v0.5.13 shipped and carries no tag" and writes nothing, since
`cmd_release` resumes only a cut whose stamped items have no notes file. It
absorbed `PL-YFT4` once `docs/releases/v0.5.13.md` was removed, printing
"Resuming an interrupted cut of v0.5.13: 17 of these 18 item(s) were stamped".
Filed as `PL-2TDX`.

Every item already carried its `pr:`, so the notes cite 18 pull requests,
`#1110` to `#1140`, and nothing was read from history.
`tools/pr_body_check.py` found no squash body to recover. v0.5.12's notes gained
the `### also inside this tag's span` pointer for `#1113` and `#1116`, and the
`ROADMAP.md` row and baseline section say what the release was for. Filed
while cutting: `PL-08HR` (tag v0.5.13, the owner's step).
