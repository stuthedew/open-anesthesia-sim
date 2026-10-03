---
id: PL-9KHK
title: bin/docket arm's read ask says what the ask opens with, so sessions open the reply with the summary and close on a bare 'read #N', the line the owner acts on
priority: P2
effort: S
status: done
classes: docs
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py
added: 2026-10-03
closed: 2026-10-03
pr: 1307
payoff: the owner's read of a held pull request is asked for in the line they act on, naming only what is theirs to judge
verify: grep -q 'def test_a_read_hold_puts_its_ask_in_the_closing_block_line' subprojects/docket/tests/test_cli.py
---

**Problem.** `bin/docket arm`'s read hold tells a session what the ask for the
owner's read *opens* with (`arming.READ_ASK`, `PL-8XQS`), and sessions do
exactly that: they open the reply with the summary, then close it on a bare
"read #N and merge" - the one line the owner acts on.

**What was asked.** Stuart, 2026-10-03, on `#1304`: "you aren't supposed to
just tell me to read a pull request. Remember? You are supposed to give me a
summary of something specific you want me to review. Don't have to review
housekeeping stuff", and then "Multiple other sessions are missing it. How do
we fix it?"

**The mechanism.** Sessions follow `READ_ASK` to the letter: the plain-language
summary and the points to judge open the reply, and the reply then closes under
`.claude/rules/instruction-writing.md` rule 14 with a line reading "Read #N and
merge". That closing line is what the owner acts on, so the ask that reaches
them is the bare "read the pull request" the summary was built to replace.
Every later reply repeats that line - a CI-green notice, a check-in, the reply
after a compaction - and the summary was never in it. The points themselves
took in housekeeping: an expected audit refusal, an internal structure choice,
each framed as a decision taken on the owner's behalf, which is what
`READ_ASK`'s first example invited.

**Evidence, 2026-10-03.** Three sessions got a read hold with `READ_ASK`
printed, and each closed on a bare ask:

- this session, `#1304` (`PL-Q9LK`): the summary and three points in the body,
  "Read #1304 and reply 'merge'" in the closing block, repeated in the two
  replies after it;
- `PL-8H2R`'s session, `#1305`: "In plain terms" and "For you to judge" 1-4 in
  the body, then "Read #1305 (the PL-8H2R fix) and merge it or comment";
- `PL-4ZK8`'s session, `#1299`: its closing block, as the harness summarised
  it, "read and merge PR #1299 (or say 'merge it')".

The instruction was present and obeyed; what it said pointed at the wrong line.

**Why it matters.** The owner asked on 2026-09-27 for every pre-merge read to
arrive as a summary of what is theirs to judge (`PL-8XQS`). The line that
reaches them still asks them to read the whole pull request, housekeeping
included, so each held pull request costs them the read a session was meant to
do for them, while the summary that would have spared it sits in a paragraph
they do not act on.

**Done when.** The read hold's ask names the closing block's own line and
refuses "read #N", is repeated whole in every later reply that still waits on
it, runs the points most important first and limits them to what matters to
the owner, sends housekeeping to what needs no review, stays short, and covers
a pull request with no point to judge - held by
`test_a_read_hold_puts_its_ask_in_the_closing_block_line`.

**Fix.** `READ_ASK` names the closing block's own line as where the ask goes. It
keeps the summary, the numbered points and the no-review clause, limits the
points to what is the owner's - a clinical value or a `docs/MODEL.md`
statement, what a learner sees, how sessions work, a departure from what they
asked for - and sends housekeeping (tests, docstrings, filed items, audit
notes, the apparatus's internals) to the no-review clause. Where no point is
theirs, the line says so and asks for the merge word alone.

**Carrier.** Kept in `READ_ASK`, over a resident line in rule 14: the
instruction already arrives minutes before the ask is written and was followed,
so the defect was its wording, and a resident line would charge every session
for it. A Stop hook was refused too: whether a closing line names points to
judge is prose, and deciding it is the judgment half `CLAUDE.md` refuses to
script.

**Falsified if.** The next three sessions that get a read hold after this
merges still close on a bare "read #N" ask, read from each one's last reply and
not from `needs_action`, which the harness writes as its own summary. The
wording is then not enough, and the next carrier is a resident line in rule 14.

**Generator check.** Not a generator: one wording defect in `READ_ASK`, and it
explains no other item.

**Built (2026-10-03).** `READ_ASK` now says to ask for the read in the closing
block's own line, never as "read #N", repeated whole in every later reply that
still waits on it: the plain-language summary, the points that are the owner's,
and one no-review clause where housekeeping goes; with no point to judge, it
says so and asks for the merge word alone. The comment above it records why.
`test_a_read_hold_puts_its_ask_in_the_closing_block_line` pins the order of
those parts, and `PL-8XQS`'s test, which checks the line is printed once no
claim holds the branch, passes unchanged.

**Revised in review (2026-10-03).** Asked whether anything on the housekeeping
list was wanted after all, the owner answered on `#1307`: "it's not that I
don't want to see things. It's just hard to know what's important in long text.
Relevant or important stuff." So the need is salience, not exclusion: the
points now run most important first and are chosen by what matters to the
owner rather than by whose decision each is, a risk to what already works joins
the list, and the line is kept short enough to take in at a glance. Housekeeping
still appears, in the one no-review clause.
