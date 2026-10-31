---
id: PL-0BRY
title: Record what each blind generalist review pass found, finding by finding, and report per pass across merged simulator pull requests how many findings were fixed or filed and how many no earlier pass had named, so the monthly model review can check that each pass still finds real faults
priority: P2
effort: M
status: done
classes: infra
feature: review-panel
milestone: v0.6.9
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_arming.py, subprojects/docket/README.md, tools/blind_review.py, tools/blind_review_report.py, tests/unit/test_blind_review.py, tests/unit/test_blind_review_report.py, .claude/skills/docket/modes/close-out.md, .claude/skills/model-review/SKILL.md, docs/apparatus.md, docket.toml
added: 2026-10-26
closed: 2026-10-26
pr: 1857
payoff: each simulator pull request's blind review record says what each pass found and what happened to each finding, and one command reports per pass, across merged pull requests, how many findings were fixed or filed and how many no earlier pass had named
verify: grep -q 'blind_review_report' .claude/skills/model-review/SKILL.md && grep -q 'pass 1: blocking fixed' .claude/skills/docket/modes/close-out.md
---

**Problem.** Record what each blind generalist review pass found, finding by finding, and report per pass across merged simulator pull requests how many findings were fixed or filed and how many no earlier pass had named, so the monthly model review can check that each pass still finds real faults

**Asked for** (project owner, 2026-10-26, in their own words): "Can we track how often the generalist review agents fix things for first and if done second or additional runs so we can do intermittent analysis to make sure it's providing benefit?"

**What exists, measured 2026-10-26.** Close-out step 9 already asks for a trailer, `Blind-review: passes N, findings F, fixed X, filed Y, rejected Z`, and `bin/docket arm` reads its `passes` (`PL-HDRN`). Three things stop it from answering the owner's question.

- **It totals all passes together.** On a branch that ran two passes, nothing says which pass found what, or whether pass 2 found anything pass 1 missed. That second number is the one `PL-TBQS` used to justify the second pass, and it is the one a later analysis needs.
- **It does not reach `main`.** The squash commit's message is the pull request's body, not the branch's commits. So the trailer reaches `main` only when a session copies it into the body: 2 of the 28 records did. The model review's table (`.claude/skills/model-review/SKILL.md` § "Outcome measures", row "Review findings") says to read the trailer "on its squash commit", which therefore finds almost nothing.
- **Its counts can disagree with each other.** `#1829` records "findings 7, fixed 7, filed 1", eight outcomes for seven findings. The form cannot say whether a fault both passes named counts once or twice.

The records do survive, on each pull request's frozen head. GitHub keeps `refs/pull/<n>/head` after the branch is deleted (`vcs.orphaned`'s docstring measured 311 of 311 surviving, apart from `#297`-`#386`, which were deleted on request). Read from those heads, the 72 pull requests merged after `#1767` hold 28 records:

| Passes recorded | Pull requests | Findings | Fixed | Filed | Rejected | Pull requests with a fix or a filing |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 12 | 19 | 16 | 3 | 0 | 8 |
| 2 | 16 | 69 | 65 | 4 | 1 | 16 |

So the passes are finding things that sessions accept, but the two-pass rows cannot be split by pass.

**The design.**

1. **Record each finding, not totals.** The trailer becomes one entry per finding, grouped by pass: `Blind-review: pass 1: blocking fixed, optional rejected; pass 2: blocking fixed repeat, should-fix filed`. Each entry is the reviewer's own severity (`blocking`, `should-fix` or `optional`, from the brief's header line) and what happened to the finding (`fixed`, `filed` or `rejected`, as step 9 already defines them). `repeat` marks a finding that a lower-numbered pass also named. A pass that wrote `NO FINDINGS` is `pass 2: none`. The session already lists every finding with its outcome in the pull request body, so this is a transcription, not new judgment. The counts are then derived, so they cannot disagree, and the severity and the overlap come free.
2. **One parser, in `docket.arming`, beside `BLIND_REVIEW`.** It returns a record of the passes and their findings, or raises `ValueError` with the reason: passes out of order, a `repeat` in pass 1, an unknown word. It also reads the older totals form, as a record whose passes are known but whose findings are not split, because 28 records are in that form and branches in flight still write it. `arm` reads `passes` from it, so `BLIND_FORM` goes. Make `_newest_trailer` public, or add a `newest_blind_record`, so the report reads the newest record exactly as `arm` does.
3. **A report, `tools/blind_review_report.py`.** For each pull request merged into the default branch after `--since <number>` (default `1767`, the pull request after which `arm` held for a record), it does four things.
   - It reads the number from the subject with `vcs.subject_pull_request`.
   - It works out the passes owed from the merge commit's own diff with `docket.arming.blind_passes`. Generalise `tools/blind_review.py`'s `passes_owed` and `is_tooling_test` to take the two revisions, instead of reading `HEAD`.
   - It lists every `refs/pull/*/head` with one `git ls-remote`, as `tools/left_behind_check.py` does, and fetches those commits by hash, writing no ref. Fetching by hash worked against GitHub through the proxy on 2026-10-26; check that again before relying on it.
   - It reads the newest `Blind-review` trailer in `<head> ^<merge>^`.
   It prints a per-pass table from the split records: pull requests, findings, fixed or filed, `new` (fixed or filed and not a repeat), new and `blocking` or `should-fix`, rejected, and the number of pull requests with at least one new finding. Below that it prints the totals from the older records, which cannot be split. It lists by number every pull request it could not read: no head, a fetch that failed, a record that did not parse, a record of fewer passes than were owed, and a pull request that owed passes but has no record. It declines in a shallow clone, as `vcs.merged_pull_requests` does. Standard library only, under `python3`, unless parsing tests under `tests/` needs the newer grammar, in which case it runs under `uv run python` like `blind_count_command`.
4. **Close-out step 9** gives the new form, says what `repeat` means, and asks that each finding in the pull request body say which pass named it. `BLIND_ASK` gives the new form too.
5. **The model review** (`.claude/skills/model-review/SKILL.md`) does two things. Its "Review findings" row reads the report instead of the squash commit. A new section has each monthly run do the following.
   - Run the report twice: once since the last run's newest pull request, and once in total.
   - Write both tables into `docs/model-review.md`.
   - Compare the results against the bar below.
   It can also join a reviewed pull request's items to the table's "A fix that did not hold" row. That shows whether faults the passes missed came back as items, which is the measure the session's own judgment cannot bias.
6. **`docs/apparatus.md`** gets one line for the new tool.

**The bar for raising the second pass with the owner.** This is a placeholder set by the session that filed this item, for the owner to change. It decides only when the review brings the question to the owner. The owner still decides. Once 20 pull requests that owed two passes carry split records, the review counts pass 2's new findings marked `blocking` or `should-fix`. `PL-TBQS` chose the second pass because over 20 replayed pull requests runs 2 and 3 named 3 later-filed defects that run 1 missed. So fewer than 3 such findings across those 20 means pass 2 is finding less than the replay that justified it, and the review brings the owner the case for retiring it. Three or more keeps it, and the review says so in one line. For scale, `PL-TDV9` priced a pass at a median of $3.63, against $9.73 for a median item session. So a pass whose findings each spare one later item's session pays its own cost at about 0.37 new findings per pass. That figure assumes every such finding would otherwise have become an item, which overstates it, and it ignores what a learner loses to a wrong value in between.

**What "fixed" can and cannot show.** The session that wrote the code decides whether a finding is real, so the counts are its judgment, not a blind check's. `PL-TCBJ`'s blind checker agreed with 59 of the panel's 62 findings, which suggests the judgment is usually right, but the report should say whose judgment it is. Recording `repeat` does not make it possible to estimate how many faults both passes missed. A capture-recapture estimate would need more reviewers than this has. Briand, El Emam, Freimut and Laitenberger, IEEE Trans Softw Eng 2000;26(6):518-540 (doi:10.1109/32.852741), tested such estimates on real inspection data. They found none accurate enough with fewer than four inspectors, and found that they could underestimate badly. So the faults the passes miss are counted from the items filed later, through `reenters:`, and not estimated.

**Tests.** The parser: the new form, the older form, each refusal, and a `repeat` in pass 1. `arm`: update the four `Blind-review` tests in `subprojects/docket/tests/test_arming.py` to the new form, and keep one asserting that the older form still counts its passes. The report: a temporary repository with a fake remote holding `refs/pull/<n>/head`, covering a split record, an older record, a pull request that owed passes and has none, a head that cannot be fetched, and a merge that owed nothing.

**Owner's read.** The build edits the tests that pin `arm`'s answers, so its pull request waits on the owner's read (`Owner-read: needed`). It changes no simulator path, so it owes no blind pass of its own.

**Why it matters.** Each pass costs about a quarter of a median simulator item (`PL-TDV9`), and the second pass rests on exactly 3 defects in `PL-TBQS`'s replay, one of them a close call. Without a per-pass record, nobody can tell later whether either pass still finds what it was kept for. The pass would then go on being paid for, or be dropped, on impressions.

**Done when.** Each new `Blind-review` record lists every finding by pass, with its severity, its outcome and whether an earlier pass named it, and `bin/docket arm` reads it. `python3 tools/blind_review_report.py` prints the per-pass table for the pull requests merged after a given one, read from their heads on GitHub, and names every pull request it could not read. The model review runs it each month and compares it against the bar above.

**Generator check.** None. This is work the owner asked for in their own words on 2026-10-26. No mechanism is producing items like it. It also repairs one defect in what exists: the model review's "Review findings" row reads a trailer that the squash commit does not carry.
