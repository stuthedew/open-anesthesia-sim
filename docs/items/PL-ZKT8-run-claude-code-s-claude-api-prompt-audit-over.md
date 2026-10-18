---
id: PL-ZKT8
title: Run Claude Code's /claude-api prompt-audit over the resident instructions and the docket skill against Opus 5.5, and bring its proposed diff to the owner hunk by hunk
priority: P2
effort: M
status: ready
classes: session-cost
feature: model-evidence
touches: CLAUDE.md, .claude/rules, .claude/skills/docket
added: 2026-10-17
payoff: instructions written for older models stop costing tool rounds and accuracy on Opus 5.5, with every change approved by the owner
verify: grep -q '^### Owner answers' docs/items/PL-ZKT8-run-claude-code-s-claude-api-prompt-audit-over.md
---

**Problem.** Run Claude Code's /claude-api prompt-audit over the resident instructions and the docket skill against Opus 5.5, and bring its proposed diff to the owner hunk by hunk

**Why it matters.** Anthropic's "Optimizing for cost and intelligence" page
says to audit prompts "against the model you run now, and again whenever you
change models"
(https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence,
§ "Audit prompts against the current model"). The owner moved this project's
hard work to Opus 5.5 on 2026-10-14. The page measured two kinds of stale
text. A newer model follows over-instruction such as "verify twice" or a
mandatory step-by-step procedure too literally, which adds tool rounds and
cost. Contradictions and retired settings cost accuracy. "The same patterns
tend to appear in tool descriptions and skills."

The resident set (`CLAUDE.md` and the three unscoped rules) measured 84,789
characters on 2026-10-17. Cached reads of it cost little, so the payoff is in
behaviour rather than size. The installed Claude Code (2.1.302) carries
`prompt-audit [<path>]`. The owner agreed to run it on 2026-10-17 (ratified,
in session_016Hv97dHUS9f4zXzkt2bU2E).

**How.** Run it in a fresh session from the repository root, over `CLAUDE.md`,
`.claude/rules/` and `.claude/skills/docket/`. Bring the proposed diff to the
owner hunk by hunk, with what the audit left alone. Many of these rules are
ones the owner specified, so a hunk that changes one needs a compelling
argument, and the session says so beside it. Apply only the hunks the owner
approves, each routed by `CLAUDE.md`'s rule for behaviour changes.

**Done when.** The audit's findings and the owner's answer to each are
recorded below under `## Audit result`, and the approved hunks are merged.

**Generator check.** Not a member of a head: one audit, prompted by one model change.

## Audit result

**Run 2026-10-18** with Claude Code 2.1.302's `/claude-api prompt-audit`,
against Claude Opus 5.5. Five subagents each audited one part of the scope,
following the bundled `shared/prompt-audit.md` and the Opus 5.5 section of
`shared/model-migration.md`. The scope was `CLAUDE.md`, all 15 files under
`.claude/rules/`, and the `docket` skill's `SKILL.md` and 8 mode files.

**What it found.** The files carry almost none of the patterns written for
older models. There is no capitalised MUST or CRITICAL, no thinking
scaffold, no word cap and no update suppressor. Every prohibition the
workers checked gives its reason or names its incident, so they kept them.
The findings are of another kind: a file that kept an older rule after
`CLAUDE.md` or another file moved on. There are 38 proposed hunks at high or
medium confidence, and 25 findings flagged without an edit. All 38 hunks
apply together with `git apply --check` against `d73fee0e63b4`.

**The owner's answer to each hunk is pending.** It goes under `### Owner answers` below when given. A hunk marked SPECIFIED
changes a rule the owner wrote in their own words, and its reason is given.

| Hunk | Where | Conf. | Kind | What it changes |
|---|---|---|---|---|
| A1 | `CLAUDE.md:315` | high | ratified | Suspends standing approval only while a workflow-lane item is `generator: live`, matching the 2026-10-17 narrowing at line 54 |
| A2 | `CLAUDE.md:191,197` | medium | - | Names "the ask-gate" where two sentences say "this", because later blocks now sit between them and the gate |
| A3 | `CLAUDE.md:639` | medium | ratified | Drops "Since 2026-10-03" and splits the sentence |
| A4 | `CLAUDE.md:274` | medium | - | Dates the 81,048-115,320 token compaction floor to its measurement |
| B1 | `citation-drift.md:26` | high | - | The docket skill is `SKILL.md` and 8 mode files, not "seven files" |
| B2+B5 | `citing-sources.md:200-203` | high | - | Removes "stays Trusted", which contradicts line 28's `Custom`, and dates the poppler claim |
| B3 | `instruction-writing.md:159-162` | medium | SPECIFIED | Drops `git fetch origin` from rule 14's refresh, because `flight` and `stranded` fetch for themselves since `PL-QSGX`. The owner specified a refresh before every closing block, and that outcome is unchanged |
| B4 | `citation-drift.md:108-115` | medium | - | Removes a paragraph about an earlier draft of itself; `tools/fixture_id_check.py` enforces the rule |
| B6 | `apparatus-standard.md:39-42` | medium | ratified | Rules out `xhigh` as well as `max` for apparatus subagents, after the 2026-10-17 choice of `high` (`PL-SW0B`) |
| B7 | `citing-sources.md:75-77` | medium | - | States the two meanings of a bare 403 in the present tense |
| B8 | `citing-sources.md:99-108` | medium | - | Rewrites "what has changed" as present rules; the ban on routing around the gateway stays whole |
| B9 | `citing-sources.md:116-126` | medium | - | Shortens the 2026-09-04 host-failure history to the two routes it justifies (the most optional hunk) |
| C1 | `ui-reader.md:34` | high | - | Drops "the tutorial paragraph is the thing being removed"; `PL-6580` removed it |
| C2 | `capture.md:21` | high | - | "The one above" points at `.claude/skills/docket/modes/ideas.md` § "Mode: turn an idea into work", which moved in the skill split |
| C3 | `ideas.md:44` | medium | - | Replaces a worked example that files a history buffer, a design `run-is-its-definition.md` forbids |
| C4 | `ui-color.md:32` | medium | unrecorded | Removes the Flet spelling; only Qt remains under `app/` |
| C5 | `SKILL.md:21` | medium | - | Keeps the 5,000-token compaction cap and its reason, and cuts the 93,454-character history |
| C6 | `SKILL.md:86` | medium | - | Drops "Nothing was cut in the move ... verbatim", which later edits made untrue |
| C7 | `SKILL.md:3` | medium | - | Trigger description as categories of intent, adding close-out, gate freeze, design rounds and housekeeping (614 to 620 characters) |
| C8 | `capture.md:84,125,149,191,219` | medium | - | Five "now / used to / no longer" phrases restated as the current rule |
| D1 | `release.md:233` | high | - | `release` stops before the commit and the workflow tags, not "commit and tag" (`PL-2FY6`, `PL-N936`) |
| D2 | `picking.md:292` | high | - | Four compounding-friction tests, not three |
| D3 | `start.md:295` | high | - | A long session resets in place with `/compact` (`PL-YJG1`), not "start fresh" |
| D4 | `picking.md:175` | high | - | Adds the product-focus exception, `docket next product` (`PL-2866`) |
| D5 | `release.md:58` | high | - | Two staleness sweeps have run (`PL-6ZQY`, `PL-C4W8`), not one |
| D6 | `close-out.md:108` | high | - | Drops the claim that a gate's remaining entries are all simulator work |
| D7 | `release.md:328` | high | - | Tag range "since v0.5.20", now that tags run to v0.5.25 |
| D8 | `start.md:11,21` | medium | - | Drops the separate `git fetch origin`, since `show` fetches (`PL-XBV4`); keeps the 2026-09-01 incident |
| D9 | `start.md:38` | medium | - | Splits the 16-line exit-4 sentence; keeps every id, the disarm and the `git push` ban |
| D10 | `release.md:335` | medium | - | Removes the tag-step history that line 289 already states as a rule |
| D11 | `picking.md:260` | medium | - | Payoff rule in the present tense: required for items added from 2026-09-20 |
| D12 | `picking.md:168` | medium | - | Drops "now" from the lane-line sentence |
| E1 | `triage.md:601` | high | unrecorded | Points at `CLAUDE.md`'s four friction tests instead of listing three |
| E2 | `triage.md:516` | high | - | Dates "14 of the 179 closed items" to 2026-09-04 |
| E3 | `triage.md:333` | high | - | Dates "all six commands" to 2026-08-30 |
| E5 | `triage.md:409` | medium | - | Removes the dated `-k` refusal paragraph, which the admitted-shapes list covers |
| E6 | `triage.md:474` | medium | - | One current rule in place of "the `pytest` half is now refused" |
| E7 | `triage.md:40` | medium | - | What `IN FLIGHT` means, without "now" and "used to" |

**Flagged, no hunk.** These need a decision rather than an edit:

- B10: rule 1's "Phase 1 in detail" and the scope note's "never mention phases" read as opposite instructions.
- B11: `CLAUDE.md`'s cheap ideation mode and rule 14's refresh before every reply pull against each other.
- B12: the `tests/` exception in `apparatus-standard.md` never loads on `tests/` paths. A fix would loosen a standard.
- E4: triage's "escalate only a `P0` or friction, nothing else" omits the live-generator ending that `CLAUDE.md` requires.
- D13: close-out's adversarial review is an over-verification re-test candidate, but it rests on `#784`'s measured failure, so it stays.
- A9: `docs/maintainer.md:71-77` names Fable 5.1 and Opus 5 where lines 164-232 say Opus 5.5. This is outside the audit's scope.
- Copies of the stale "three friction tests" are in `docs/WORKING_NOTES.md`, and of "flight does not fetch" in `docs/resident-instructions.md`. Each goes with D2 and E1, or with B3 and D8, if those are taken.

The other low-confidence flags (A5-A8, B13-B14, C9-C12, D14-D15, E8-E10)
are dated wording or minor drift with no proposed edit.

### Owner answers

**2026-10-18: apply all 38 hunks** (project owner, 2026-10-18, ratified,
over taking only the high-confidence ones). This includes B3, which reopens
the refresh rule the owner specified on 2026-09-19. The outcome they
specified, a refresh before every closing block, is unchanged. Only the
`git fetch origin` step goes, because `flight` and `stranded` fetch for
themselves.

The four flags that need a decision (B10, B11, E4 and A9) were not answered
here and stay open on this item.
