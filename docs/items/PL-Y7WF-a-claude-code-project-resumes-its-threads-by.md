---
id: PL-Y7WF
title: A Claude Code project resumes its threads by itself when the plan's five-hour usage window resets, so the PL-NZC0 trial project keeps spending each new window unattended unless it is paused or its instructions carry a stop time
priority: P2
effort: S
status: needs-decision
classes: session-cost
feature: projects-trial
touches: docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
---

**Problem.** A Claude Code project resumes its threads by itself when the plan's five-hour usage window resets, so the PL-NZC0 trial project keeps spending each new window unattended unless it is paused or its instructions carry a stop time

**Source.** https://code.claude.com/docs/en/claude-projects, § "Usage and cost" (fetched 2026-09-25): "A thread that reaches your plan's limit waits and continues on its own when the limit resets, so work you left running starts using your next usage window without a message from you." **Pause** in **Project settings > General** "stops everything at once"; the trial's instructions (`PL-NZC0`) name no stop time. Found while writing the owner's time-boxed workflow-sweep project prompt, which carries one.

**Re-read 2026-09-26.** The page carries that sentence word for word. Its §
"A thread hit the usage limit" adds that a thread or the project conversation
at "your plan's five-hour or weekly limit ... keeps retrying on its own and
continues when the limit resets", and "If you'd rather it not use your next
usage window, click **Stop** in the thread, or pause the project to hold every
thread." **Pause** is one of three controls "at the bottom of **Project
settings > General**". Only a thread a routine started does not wait, and the
trial's instructions forbid routines. Those instructions, as `PL-NZC0`
records them, still name no time: their "Stop and wait for me when" line lists
a decision, a red `main`, a check failing twice and the context budget, and a
grep of the verbatim block for a clock time or "UTC" finds nothing.

**Why it matters.** The trial runs to a condition, not a date, across many
sittings, so every five-hour window that resets while the owner is away goes
to it. The weekly limit it draws on is the one the owner's product sessions
need: on 2026-09-26 the trial's coordinator and a triage session outside the
trial both read `rate_limit_info` `seven_day`, `allowed_warning`. A window the
trial spends unwatched is one the product focus of 2026-09-25 does not get.

**Generator check.** One-off. The fact misread is an external behaviour
nothing in the tree models: a Projects thread waiting at a plan limit resumes
on its own when the limit resets. The trial's instructions were written
without it, no other item reads it, and no head's `misread:` states it
(`bin/docket generators --misread`, 2026-09-26).

**Decision needed.** How the trial stops spending while the owner is away:
pause the project at the end of each sitting, or a stop line in its project
instructions. Only the owner can reach **Project settings**.

**Recommendation:** pause at the end of each sitting. Pause is enforced and
immediate: "Every running thread and the conversation are interrupted, no new
threads start, routines don't run", and it is the docs' own remedy for this
case. A stop line is weaker on three counts the same page states. Project
instructions are "Text sent to each new thread", which Claude follows and
nothing enforces. An edit to them reaches "new threads, not threads already
running", so it misses whatever is running when the window resets. And a
waiting thread is retried by the harness, not by the model, so it is already
spending the new window when its instructions next get a say, and it stops at
a clock time only if it happens to read a clock. A stop time would also need
rewriting every sitting, since the trial has no end date: the same
per-sitting act as Pause, without its force. What Pause costs: it is a step to
remember at the moment of leaving; each interrupted thread needs a message to
go on; and a thread whose sandbox cannot resume "continues from a fresh clone,
so uncommitted changes can be lost", which `CLAUDE.md`'s commit-and-push-as-you-go
rule limits to the last unpushed step. The steps, checked against the docs on
2026-09-26:

1. At the end of each sitting, open the "Fix generators" project at
   claude.ai/code or in the desktop app, click the gear icon in the project
   header to open **Project settings**, go to **General**, and click **Pause**
   at the bottom. Worked: a banner above the project's message box offers
   **Resume**, and the project accepts no messages until it is clicked.
2. To start the next sitting, click **Resume** on that banner, or in the same
   place in **Project settings > General**. Then open each thread that was
   working, from its card in the conversation or its row in **Overview**, and
   send it a message in its own message box, such as `continue`: "a paused
   thread continues when you send it a message after that".

The alternative, if the owner prefers it, is this line at the end of
**Project settings > Memory > Project instructions**, with the time rewritten
each sitting: `Stop time: HH:MM UTC today. Before each new step, run date -u;
once it is past, push, report one line, and start nothing new.`

**Done when.** The owner's answer is recorded under the question, dated and
with its kind. Under the recommendation nothing in the tree changes; under the
alternative, the line is in the trial's project instructions and in the
verbatim copy `PL-NZC0` records.
