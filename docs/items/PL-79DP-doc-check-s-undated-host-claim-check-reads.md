---
id: PL-79DP
title: doc_check's undated host-claim check reads block as a refusal in its Markdown sense too, so a sentence holding a project's URL and 'its block reading' or 'a code block' is refused as an undated claim that the host was blocked; found writing PL-0C2S's test docstring
priority: P3
effort: S
status: done
classes: defect
feature: host-reachability
milestone: v0.5.24
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-11 triage pass
added: 2026-10-10
closed: 2026-10-12
pr: 1454
payoff: make check stops refusing a true sentence that cites a Markdown project's URL beside a code block, so nobody rewords correct prose to get past the host-claim check
verify: grep -q 'def test_block_beside_a_host_is_an_advisory_rather_than_refused' tests/unit/test_doc_check.py && grep -q 'def test_a_word_only_a_refusal_has_beside_a_block_is_still_refused' tests/unit/test_doc_check.py
reenters: PL-GPJ7
---

**Problem.** doc_check's undated host-claim check reads block as a refusal in its Markdown sense too, so a sentence holding a project's URL and 'its block reading' or 'a code block' is refused as an undated claim that the host was blocked; found writing PL-0C2S's test docstring

**Reproduced 2026-10-10**, writing `PL-0C2S`'s test. A docstring sentence
naming markdown-it-py's repository URL and "the reference its block reading is
held to" failed `python3 tools/doc_check.py check` with "names `github.com`
beside a refusal in a sentence that carries no date". `HOST_REFUSAL_RE` reads
`block`, `blocks` and `blocked` at a word boundary, and in this tree the word
is also the Markdown noun, a fenced or code block. The sentence was reworded to
drop the URL, so nothing in the tree fails on it now.

**Re-confirmed 2026-10-11** on main at `16a20a4f`, under python3 3.13.16:
`_undated_host_claims` reports `github.com` in "Held to
https://github.com/executablebooks/markdown-it-py, the reference its block
reading is held to." and in "The example from github.com sits in a code block
below.", exactly as it reports the real claim "github.com is blocked here."
The tree passes today only because the one sentence that tripped it was
reworded.

**Why it matters.** It is a hard gate refusing correct work: `make check`
fails a sentence that makes no claim about a host, and the writer's way out
is to reword true prose or drop a citation's URL, which is what happened
here. "Block" is ordinary vocabulary in a tree that documents a Markdown
reader, so the next citation of a Markdown project's repository beside its
block grammar meets the same refusal.

**Generator check.** An instance of `PL-GPJ7`'s fact - whether a sentence
makes the claim a hard gate checks, when the gate recognises it by wording -
filed after that head closed (2026-09-26, `spent`). `check_host_claims` came
with `PL-CLW5` on 2026-10-06 and refuses on a word rather than on a syntax the
writer put there, the shape `PL-GPJ7`'s fix moved every gate it then knew off.
The first post-close instance found; three would record that fix as not
holding. Not a member of `PL-R417`: the sentence is read whole.

**Route, measured 2026-10-12.** Across the tree, dated sentences and the
dated records included, 139 sentences named a host beside a word
`HOST_REFUSAL_RE` read. In 4 the only such word was `block` or `blocks`, and 2
of those were real claims - an egress block, a policy that blocks a host -
while 2 named a block of text. Narrowing the word list would have let through
as many true claims as it freed false ones, so the item's second route was
taken, the one `PL-GPJ7` took for its gates. `HOST_REFUSAL_RE` keeps `blocked`
and `blocking`, which only a refusal says, and a new `HOST_BLOCK_RE` reads
`block` and `blocks`: a sentence whose only refusal is one of them is an
advisory naming the word and both readings, never an error.
`test_block_beside_a_host_is_an_advisory_rather_than_refused` pins the two
Markdown readings and the two claims, and
`test_a_word_only_a_refusal_has_beside_a_block_is_still_refused` pins an
undated `blocked` beside a code block. `verify:` had named a test for the
narrowing route ("is no host claim"); it now names these two.

**Done when.** A sentence that uses "block" as Markdown's noun beside a host -
a code block, a fenced block, a block reading - is not refused as an undated
host claim, while an undated "github.com is blocked" still is; a test pins
both. Narrowing what reads as a refusal and demoting the ambiguous wording to
an advisory, as `PL-GPJ7` did for its gates, both meet this.
