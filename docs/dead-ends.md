# Dead ends

Approaches that were tried here, measured, and refuted. One line each, with
the id that carries the full reasoning — `bin/docket show <id>` is the whole
retrieval path.

**The entry lines below are emitted into every session's context at start, and
a `SessionStart` hook's output is resent on every turn** — so they are budgeted
at 30 entries and 4,000 bytes by `tools/dead_ends.py`, which `make check` runs.
This preamble is not emitted and not budgeted: it is instructions for adding an
entry, which a session reading the entries never needs. That tool carries the
measurements behind the numbers.

**Edit this file one entry at a time — add one, merge two, remove one — and
never rewrite it as a whole.** Those are different operations and only the last is the
failure mode. Monolithic rewriting of an accumulated context is measured:
18,282 tokens to 122 in a single step, accuracy 66.7 to 57.1, while itemized
bullets with *incremental delta updates and periodic de-duplication* beat
rewriting by +10.6% on agent tasks (Agentic Context Engineering,
arXiv:2510.04618). Removing a single stale entry is the de-duplication half of
that prescription, not a violation of it.

**An entry joins this list only if a session would propose the approach before
opening any file** (project owner, 2026-10-19, ratified, `PL-5J1S`). That is a
proposal made in a reply or a design round, which no read precedes. An approach
proposed only while editing one part of the tree goes into a path-scoped rule
under `.claude/rules/` whose `paths:` cover that part, however much room this
list has. The budget is a cap, not a target to fill.
`.claude/rules/dead-ends-apparatus.md` holds the entries about the item store
and the tools.

**An entry leaves in one of two ways, and never by deletion alone.** It moves to
a place that still stops the approach at the moment a session would propose it:
a path-scoped rule, or a check or docstring that cites its id. Or, when its
question no longer exists, for example because the code it names was removed,
it is listed under "Retired" at the end of this file with the reason. Age is not
a reason: an old entry that still guards a live temptation stays.
`tools/dead_ends.py check --base origin/main` fails on an entry that left
without either record. Each grooming pass re-tests every entry against the
admission test above, and moves the ones that fail.

**When every entry must stay resident and each is already one line, bring the
owner the budget question.** State its cost: about one token per 4 bytes, on
every turn of every session. Dropping a lesson that is still needed is not an
answer.

**Why these are resident rather than grepped on demand.** Not because records
like this go unread — that is a finding about human lessons-learned systems and
its mechanism was tedium, which does not transfer to an agent. What transfers
is that nothing *triggers* a lookup: a test failure announces itself, a dead
end does not. A pointer read at session start does not fix that either, because
the proposal it should stop comes many turns later. A `SessionStart` hook's
output is resent on every turn, so these lines are present at the moment
somebody re-proposes the thing — which is the only moment they are worth
anything.

**Size warns; it never fails the build.** `tools/dead_ends.py` nudges at 80% of
either budget, naming the headroom and the repairs, so the decision arrives
with slack rather than being forced on whoever trips the cap mid-task.
`tests/unit/test_dead_ends.py` keeps the shipped file below the nudge, so a
session that adds an entry makes room for it in the same commit. Going over
warns louder and still does not go red. A blocked commit on an unrelated task
is how a session learns to raise the cap just to get moving, and a larger
budget is the owner's decision, put as above. Only a structural fault fails: an
entry citing an id that resolves to nothing, one wrapped across two lines, or a
bullet opening with a bolded title that is not in an entry's shape,
`- **approach** — why`, with nothing between the closing `**` and the dash.
All three are otherwise silent: the last is never emitted at all.

**What does not belong here.** An item dropped as a duplicate, as superseded,
or as out of scope. Those are ordinary queue outcomes and their `reason:` field
already records them. This file is for an approach whose *premise* was tested
and failed, where the refutation is a fact a future session would otherwise
have to rediscover by building the thing.

## Process claims that did not survive checking

- **Detecting duplicate captures by shared cited referents (item ids, shas, `#NNN`, paths)** — refuted 2026-09-16: fires on 84% of open items and ranks the true original in the top 3 for only 3 of 5 confirmed pairs; same-day narrowing is worse, 95%. This store is 86.1% cross-referenced, so referent overlap cannot separate a duplicate from an ordinary citation. Title terms are worse again. `PL-85NT`
- **A pull request template to make filing more reliable** — refuted 2026-09-20: the four-path search runs whether one exists or not, GitHub applies no template to an API-created body, and the harness reads one as layout and ignores its rules. 30 of 30 recent bodies already carry the id, the rationale and the verification claim. `PL-NDQD`
- **A cheaper model or lower effort for a subagent** — refused by the owner 2026-10-19: price, even zero, never justifies a setting that may be less correct. Reopen only on a measurement that it is no less correct at that task. `PL-2D28`
- **Working out a fact by hand where the repository already holds it** — refuted: a second regex or hand-written test of one predicate gave three heads 22, 15 and 26 items (PL-PVW2, PL-KGYT, PL-5DZ8), and sweeps alone never stopped them. Read the module that owns the fact, and make a check refuse the next copy. `PL-4S6C`

## Retired

Entries whose question no longer exists, each with the reason, in an entry's
shape. This section is not emitted and not budgeted. It is the record that
lets `tools/dead_ends.py check --base` accept an entry's removal.
