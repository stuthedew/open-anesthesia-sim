---
id: PL-Y7WF
title: A Claude Code project resumes its threads by itself when the plan's five-hour usage window resets, so the PL-NZC0 trial project keeps spending each new window unattended unless it is paused or its instructions carry a stop time
status: untriaged
added: 2026-09-25
---

**Problem.** A Claude Code project resumes its threads by itself when the plan's five-hour usage window resets, so the PL-NZC0 trial project keeps spending each new window unattended unless it is paused or its instructions carry a stop time

**Source.** https://code.claude.com/docs/en/claude-projects, § "Usage and cost" (fetched 2026-09-25): "A thread that reaches your plan's limit waits and continues on its own when the limit resets, so work you left running starts using your next usage window without a message from you." **Pause** in **Project settings > General** "stops everything at once"; the trial's instructions (`PL-NZC0`) name no stop time. Found while writing the owner's time-boxed workflow-sweep project prompt, which carries one.
