# docket: release

Read this when freezing a milestone's debt gate, or when there is finished work
to ship.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

## Mode: freeze a milestone's debt gate

Triggered by scoping a milestone — scoping is the act that freezes the list,
**except for a milestone scoped out of turn, whose gate freezes when the
milestone before it ships.** That exception is `ROADMAP.md` § "The debt gate" →
"The cadence"'s rather than this file's, and the timeline row for the gate names
the release the freeze waits for. It exists because a gate holds the
*preceding* milestone's findings: freezing it while that milestone is still
unimplemented produces a gate holding none of what it is for, and sends those
findings to the next gate instead. v0.4.26 and v0.6.0 are both in that state.
The rest of the cadence is unchanged — the list still clears before
implementation begins, and the milestone's own section still carries the heading
the frozen list goes under, empty of entries until the day. Whether the trigger
itself should be reworded is `PL-KKRP`'s; do not reword it here.

```bash
bin/docket gate --feature teachable-case
```

That is the whole decidable pass: every open debt item in the store, split by
whether it carries the milestone's feature, with effort totals for each.
Recording Gate 0 by hand meant reading 48 items and applying the rule to each;
do not repeat that. **The feature is a first cut, not the rule.** What the
milestone clears itself is what its `Required scope` names (`ROADMAP.md` §
"Debt inside the milestone's own scope"), and the two differ in both
directions - Gate 2's list did on four entries on 2026-09-23 - so write that
group's heading from `Required scope`. `bin/docket wave` reads the frozen list
against the same rule afterwards (`PL-RFHH`).

**Sweep the frozen list for staleness before clearing it.** That is beat 3 of
`ROADMAP.md`'s cadence and the first thing to happen once the list exists. A
`verify:` command tests for the presence of the fix and never for the presence
of the fault, so an entry whose problem was solved another way fails forever and
reads as outstanding work — and nothing in the store marks it, so it is ranked,
offered by `bin/docket next`, and counted into this gate. The one pass that has
run found 12 of 134 items dead and 31 more overtaken, 32% of the lane, and a
churn advisory was built, measured against its verdicts and rejected, so there
is no mechanical substitute (`PL-LKGL`). Read each frozen entry against the
tree, drop what no longer reproduces with its `reason`, and correct the briefs
that overstate what is left. **File the pass as its own item under `feature:
gate-staleness-sweep`, and do not look for a standing one** — an item named as
the instrument can close, and the next gate's session then reads `done`
(`PL-D8KW`). `PL-6ZQY`, the one pass that has run, carries a 134-item map whose
verification phase never finished; nothing in it may be acted on without
re-checking against the tree.

**Recorded debt is cleared before a new milestone begins.** `ROADMAP.md` §
"The debt gate" is the rule: open items classed `defect`, `safety`, `science`,
`refactor` or `perf`, and anything at `needs-decision`, reach `done` — or
`dropped` with a reason — before milestone work starts. `feature` and
`planning` items are not debt. Process work is debt once its mechanism is live
and unreliable, not while it is still being built; that case is classed
`defect` like any other, so the class carries the rule.

The command computes and decides nothing. Whether an item is *really* debt,
whether the gate should open, and what goes into `ROADMAP.md` are yours —
transcribe the two lists into the milestone's own section with the date they
were frozen, per `ROADMAP.md` § "Recording it". The list is frozen at that
moment; a finding made afterwards goes to the next gate unless the problem it
describes predates the freeze, or is `P0`, `safety` or `science`.

## Mode: ship a release

**A release is cut under a claimed release item, filed first** (`PL-331V`).
`new --resource` writes `resource: release-train` onto the item, so the branch
that claims it holds the release train, and a second session's `new
--resource` or cut is refused while it does. Once a cut is wanted, before
asking the owner to confirm the version:

```bash
git fetch origin
bin/docket new --resource release-train "Cut vX.Y.Z from the N items finished since vA.B.C"
git add docs/items/ID-*.md && git commit -m "ID: file the release"  # the capture alone
bin/docket claim ID                  # its pull request opens as a draft, per start.md
bin/docket release X.Y.Z --dry-run   # a rival holder or cut surfaces here
```

The dry run names the version the filing did: without one, a manual-version
project prints the finished items and stops before any guard runs.

Exit 3 from `new` means the train is held, and the message says by whom.
**By another branch:** wait for its release to merge; if that branch is
abandoned, run `bin/docket stranded` before dropping the ref. **By this
branch, through the item it names:** cut under that item rather than filing
again - claiming it anew where its claim lapsed or was yielded.

**Close the release item after the cut, never before it.** A closed item
releases its claim, so closing it first makes the cut refuse. After `make
release` and the edits below, close it in its own commit (`bin/docket set ID
--status done --closed YYYY-MM-DD`, per the close-out) and mark the pull
request ready in that push, as `start.md` has it for any claimed item. It
carries no `milestone:` and ships in no release: its `resource:
release-train` keeps it out of every later release's count and notes, so the
cut it closed is never offered again as the next release (`PL-KRS6`).

**Offer this; do not wait to be asked — when the session is about what to do
next.** The session-start digest says when there is enough finished work to be
worth raising, and the release itself takes no arguments: the store already
knows what has shipped and what has not, so there is nothing for the owner to
look up and asking them to is pure friction.

Where the digest says `No release to offer` instead, the version a bump would
arrive at is one `ROADMAP.md` has already given to a milestone ahead of the
current one and not yet finished — placed on the release train, scoped in a
section, or both — and the line names what holds it. There is nothing to raise then: the beat printed
under it is the work, and cutting the version anyway would ship a milestone
under its own name with most of it missing. `bin/docket status` prints that
refusal in the same words off the same verdict, and `docket wave`'s `Reserved`
line is the whole set of numbers the plan has spent rather than the one that
collided — which is the evidence behind either refusal, and the thing to read
before arguing that some other number is free.

But the digest says it in *every* session, including the ones where it is
beside the point. Offer it when the owner is choosing what to work on or has
just finished something. Not in a design round, a triage pass, a
question about one mechanism, or a review of one change — there it is noise appended to a reply
that was about something else, and it quietly converts ideation into
implementation, which `.claude/skills/docket/SKILL.md` § "The two modes this queue serves"
says not to do.

Raise it the way a colleague would: what got done, what it completes, what the
version would be, and a question.

> "PL-010 and PL-011 landed, so chart-readout is finished — four items. That
> makes a natural v0.2.4. Want me to cut it?"

```bash
docket status                    # includes what is releasable
bin/docket release --dry-run     # the notes and the bump, without writing
make release VERSION=0.3.0       # cut it
```

**Cut it with `make release`, never `bin/docket release` on its own.** The
tool writes the new version into `pyproject.toml` and stops, but `uv.lock`
records the project's own version too, so the next `make check` fails on `uv
sync --locked` with the tree half-updated and the reason unrelated to the
release. That happened on both releases the command has existed for. `make
release` runs `bin/docket release` and then `uv lock`, which is the whole
mechanical half.

**Every bullet cites its pull request, because the closure carried the number
before it merged.** A closure once landed with an empty `pr` and the cut read
the merge subjects to fill it before rendering, which shipped a bullet naming
no pull request whenever the reading could not answer - 128 bullets across 22
releases before it was first repaired (`PL-W7WL`). Since `PL-HMZZ` the number
is written on the closing branch and the pull request's own check refuses a
closure without it, so the cut reads nothing from history and has nothing to
write first. A bullet still citing no pull request is a closure that reached
the base past that check; `bin/docket record N --merge SHA` writes the number
onto it and restates the bullet, and `docket check` names both.

**It stops there, and the last thing it prints is what is left.** `ROADMAP.md`
needs a version-table row, the `current baseline` mark moved onto it, and a
baseline section — release prose that says what the release was *for*, which
nothing generates. `bin/docket release` names each statement that is now
stale, with its line number. Make those edits, then run `make check`: that is
what proves they landed, and running it any earlier fails on edits nobody has
been asked for yet.

**Recover any pull request body a merge dropped, in the same pull request**
(`PL-3PH2`). The squash commit's body on `main` is the record of each pull
request's body, and a merge client can still send an empty one; the offline
check names each squash commit that lost its body and has no file under
`docs/pr-bodies/`, or says none did. Before `make check`, with `origin` just
fetched:

```bash
python3 tools/pr_body_check.py            # the verdict
python3 tools/pr_body_check.py --recover  # only where it named any
```

`--recover` reads the public API with no token and writes one file per body,
which `make check`'s `--anchors` then holds to its squash commit. Commit them
with the release's other edits: they ride its pull request, and `bin/docket
verify` counts each as a `record` rather than as work outside `touches`. A body
the API could not serve is named and left, and the next release picks it up.

This project names its version rather than incrementing it, so `VERSION=` is
required; `bin/docket release --dry-run` prints the mechanical guess for
reference.

`docket.toml` sets `version_policy = "manual"` here, so the version is named
rather than inferred — `ROADMAP.md` § "Versioning decision" is why: the number
marks the capability boundary a release crosses, which no class label carries.
The dry run still prints the mechanical guess, as a reference point and not an
answer.

`release` stops before tagging on purpose: review the bump and the generated
notes, then commit and tag. It **refuses to cut a release while the previous
one is untagged**, because a release cut without a tag leaves a permanent gap
— `git describe --contains` resolves nothing across its span — and the gap
cannot be repaired with confidence once the history has moved on.

It **also refuses to cut a release another session already has** (`PL-66FP`,
two sessions cut v0.3.7 independently), on any of three facts, and it
fetches first so all are current:

- **The default branch already holds the version** — its `docs/releases/`
  notes file or its version field. Another session's release has merged, so
  the work is `git merge origin/main` and then asking again what is left.
- **An unmerged ref is carrying a cut** — of any version, not only this one,
  because two releases under different numbers stamp `milestone:` onto an
  overlapping set of items and the second to merge claims work the first
  shipped. The message names the ref and the date the notes were written; that
  date is what separates a live session from a branch nobody will merge, and
  it is yours to read. Wait for a live one; for an abandoned one run
  `bin/docket stranded` before dropping the ref.
- **Another branch holds the release train** — a live claim on its release
  item that orders ahead of this branch's, with nothing cut yet. Named with
  its item and claim date; the same two remedies apply.

Last, it refuses a branch that **holds no train claim itself**, so each
refusal above still refuses for its own reason: file and claim as above, or
stamp an existing release item with `bin/docket set ID --resource
release-train`, commit the stamp, and claim it (or `git push`, where it is
claimed already) - a claim holds the train only from the committed, pushed
copy. A release item already closed on the branch has released its claim, and
the refusal says so; one whose claim lapsed or was yielded is named, with the
claim that revives it.

**A cut that was interrupted is resumed, never cut again under a new number.**
The stamps go into the items one file at a time and the notes are written after
the whole loop, so a lost container leaves work stamped for a release that has
no notes. Re-run the same number — `make release VERSION=0.3.0` — and it picks
those items back up and cuts the whole release; the `Resuming an interrupted
cut of v0.3.0` line it prints says how many were already stamped, and the total
under it should match what the dry run said. Naming a *different* version is
refused, because two numbers over one unfinished cut leave both sets of notes
permanently wrong about the same items. Where nobody re-runs it, `docket check`
reports the release whose notes were never written (`PL-1MKQ`).

The digest's `Releasable:` line and `status`'s `Unreleased:` line say the same
thing instead of offering a release, so the second session never raises one,
and a `release` naming no version says it in place of asking for one
(`PL-53Y6`). **No read here sees a
session that has pushed nothing**, so a clean answer still means "nothing
visible", never "nothing" — which is why the session check under **Mode: start an item**, in
`.claude/skills/docket/modes/start.md`, is worth running before offering a release too.

**Never ask the owner to "tag vX.Y.Z". Paste the commands, filled in. The tag
line finds the release's cut itself - the commit that added its notes file -
so nothing is left to fill and nothing turns on when it is run:**

```bash
git fetch origin main
git tag -a v0.3.0 "$(git log --first-parent --diff-filter=A --format=%H origin/main -- docs/releases/v0.3.0.md)" -m "v0.3.0"
git push origin v0.3.0
```

Every time, not only the first. Asking for a tag without them makes the owner
reconstruct three commands at the moment they are trying to do something else.
`bin/docket release` prints them, filled in for the version it cut, at the end
of every cut; paste those rather than editing these. Run before the release has
merged, the lookup finds nothing and `git tag` refuses with `Failed to resolve
''`; run after another merge, it still tags the cut, where `origin/main` would
have tagged that merge (`PL-VYK1`). The line holds no angle-bracket
placeholder, which is the one thing a pull request body silently eats
(`PL-1DN9`).

**Do not try to push the tag yourself first - it fails, and it fails
convincingly (`PL-N936`).** `git push --dry-run` reports `[new tag]` and the
real push then dies with `send-pack: unexpected disconnect`, ending on
`Everything up-to-date` while `git ls-remote --tags` shows nothing. Branch
pushes from the same session work throughout, so this is tag refs specifically,
and it is the same family as `PL-TFWR`'s branch deletion: an operation a
session will reasonably attempt, that does not look like it failed. The tag is
the owner's to run.

**Say the tag is outstanding until they confirm it, and check rather than
assume.** `bin/docket release` refuses to cut the next release while the
previous one is untagged, and `tools/doc_check.py` will not catch the gap - the
baseline-tag advisory was removed in v0.3.4 because a local checkout cannot
tell a release never tagged from one tagged since it last fetched. So nothing
in the tree reports it; `git ls-remote --tags origin` is what answers.

File the outstanding tag as `Tag v0.3.0 on ...`, the title every tag step has
carried. `status` reads that title, and once the clone holds the tag it marks
the item `[TAGGED: v0.3.0 exists - close it]` rather than offering it as work;
a tag step titled otherwise is offered as work after the tag exists
(`PL-53Y6`).
