---
id: PL-C38D
title: Bring Projects threads into the effort trial: each new thread draws high or xhigh at its start and its arm is recorded where the model review can read it, because threads do five in six of the implementation items and cloud sessions alone cannot reach an answer
status: done
feature: effort-trial
added: 2026-11-24
closed: 2026-11-24
pr: 2321
filed-pr: 2318
tests: tests/unit/test_effort_trial.py::test_a_projects_thread_writes_its_cap_into_the_given_settings, tests/unit/test_effort_trial.py::test_the_session_start_hook_in_a_projects_thread_caps_its_user_settings
---

**Problem.** Bring Projects threads into the effort trial: each new thread draws high or xhigh at its start and its arm is recorded where the model review can read it, because threads do five in six of the implementation items and cloud sessions alone cannot reach an answer

**Decided** (project owner, 2026-11-24, ratified, chosen on a card over keeping
the trial to cloud sessions and over stopping it): bring Projects threads into
the effort trial. The model review of 2026-11-24 (`PL-JT1C`) found that
threads merged 498 implementation items in 31 days against the cloud
sessions' 100, and that with threads in the trial a doubling in failed fixes
becomes detectable in about 2 to 6 months. This is new workflow machinery,
which the pause in `CLAUDE.md` § "What this project is" allows because the
owner asked for it.

**What the build has to settle.**

1. **How a thread draws and applies its arm.** A thread never reads
   `.claude/settings.local.json`, where the start hook writes the cap
   (`PL-CR81`). A thread can set its own level with the Projects tool
   `set_effort_level`, which this thread used on 2026-11-24. So the draw can
   be the hook's existing hash of the session id, printed for a thread as an
   instruction to set that level on its first turn. Check that the tool
   accepts both `high` and `xhigh`, and what happens when the owner or the
   coordinator has already set a level: that is a moved session, counted in
   the arm it drew (`PL-JT1C`, decision 1).
2. **Where the arm is recorded.** The review now reads arms from the
   harness's session events, which took four background readers about 25
   minutes for 139 sessions (`PL-JYC2`). With about five times as many
   sessions, recording the arm at the draw, for example as a ledger column,
   is the route to take. Build `PL-JYC2` with this item or before it.
3. **Safety-critical work.** The model review skill says never to randomize
   safety-critical work, and the owner's new cost rule gives that work a
   margin of zero (`PL-1WTY`). The hook draws an arm per session whatever the
   session works on. Decide whether a session that takes a safety-classed item
   leaves the trial at its strongest level, and how the review counts it.
4. **Analysis.** Threads are a different way of working, so origin (thread or
   cloud session) becomes a stratum beside split period and model, as the
   skill's effort monitoring step 5 already asks for the historical data.
   The trial's record in `docs/model-review.md` gets an amendment dated with
   the change, and thread items count only from that date, as Evans' staged
   design does (`PL-JT1C`, decision 7).

**Done when.** New threads draw an arm and run at it, the arm is recorded
where the review reads it, the trial's record carries the amendment, and the
model review skill's step 6 says how threads are counted.


**Built** (2026-11-24, this thread's pull request).

1. **How a thread draws and applies its arm.** The draw is unchanged: the hash
   of the hook's session id. The thread writes the cap into its user settings,
   `~/.claude/settings.json`, which a thread reads, instead of
   `.claude/settings.local.json`, which it never reads. Measured in this
   thread on 2026-11-24: a `maxEffortLevel` of `medium` written into the user
   settings moved `CLAUDE_EFFORT` from `high` to `medium` on the next tool
   call, and the same key in `.claude/settings.local.json` left it at `high`.
   Both probes were undone at once. The Projects effort tool was not used: its
   own description allows it only "when the user asks for it in their own
   words", never because a tool result suggests it, so a hook's printed arm
   cannot drive it. A cap only lowers a level, and this thread's session record
   shows `effort_level: high` set at creation, which outranks any level in
   settings (*Model configuration*, "Adjust effort level", order of sources,
   https://code.claude.com/docs/en/model-config, read 2026-11-24). So the
   `xhigh` arm needs threads started at `xhigh`, which is the owner's Threads
   setting in Project settings, General (*Claude Projects*, "Project settings
   reference", https://code.claude.com/docs/en/claude-projects, read
   2026-11-24). Until it is set, a thread drawn `xhigh` runs at `high`, and its
   digest line says that a cap cannot raise the start level.
   `thread_hooks.py` now merges its hooks onto a fresh read just before it
   writes, so a cap the trial's hook wrote in parallel survives.
2. **Where the arm is recorded.** `PL-JYC2`, built in the same pull request.
3. **Safety-critical work.** Left to `PL-RZMZ` (pull request #2320), which
   sets such work at `xhigh`, has a session in the `high` arm run `move`, and
   leaves safety- and science-classed items out of both arms by class. A
   thread can now run the same `move`, because its cap lives in a file it
   reads. Whichever pull request merges second makes the start mode's thread
   sentence say so.
4. **Analysis.** `docs/model-review.md` carries the dated amendment: threads
   from 2026-11-24, origin as a stratum, threads created earlier in neither
   arm, and a thread started below its arm counted in the arm it drew.
   `.claude/skills/model-review/SKILL.md` step 6 says the same.

Files checked in the doc sweep: `tools/effort_trial.py`,
`.claude/hooks/docket-digest.sh`, `.claude/hooks/thread_hooks.py`,
`docs/maintainer.md` (the effort trial paragraphs),
`docs/model-review.md` (the trial record),
`.claude/skills/model-review/SKILL.md` (refresh steps and effort monitoring).
