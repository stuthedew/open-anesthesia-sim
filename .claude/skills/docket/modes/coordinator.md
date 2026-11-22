# docket: coordinator

Read this when you coordinate a Claude Code Project on this repository, or
when you are a thread such a coordinator started. It says how threads are
started, briefed, reported and closed.

Part of the `docket` skill. `.claude/skills/docket/SKILL.md` is its front
page and decides which file a session reads.

**The coordination rules live here, and Project settings keep only the
project's own state** (project owner, 2026-10-25, ratified, over keeping the
rules in Project settings, `PL-NZC0`). A change to these rules is then
reviewed in a pull request like any other, and a session outside the Project
can read them. Project settings keep four things:

- the **Goal**, the release the project is building, and its done-when test;
- the **Order**, the features the owner has picked, and any pause on it;
- the **compaction rule**, which by the owner's word lives only there
  (project owner, 2026-10-04 17:38Z);
- a pointer to this file.

Where Project settings and this file disagree, report both to the owner
rather than choosing, as for any other repository rule below.

## Rules are the repository's

Every rule about how a session works lives in the repository: `CLAUDE.md`, the
`docket` skill, the rules under `.claude/rules/` and what `bin/docket` prints
(`docs/maintainer.md` § "Rules for sessions live in the repository",
`PL-PDVF`). Where a rule in Project settings and one in the repository
disagree, the thread reports both to the owner rather than choosing. A rule the
owner gives in Project settings goes to a thread that writes it into the
repository in the same sitting, and the settings then name nothing about it.
The compaction rule is the one exception.

The project runs over many threads and weeks. Anything a later thread or a
replacement coordinator needs goes in its item file or in the project's shared
folder, never only in a conversation. Decisions and rules go in item files,
never in project memory.

## Source of work

Work comes only from items in `docs/items`, read through `bin/docket`, and
only from what the Order picks. A finding is filed with `bin/docket new`, not
worked, unless it blocks a picked feature. It joins the Order only if the
owner adds it. A head that `bin/docket generators` shows still generating is
put to the owner at once, with a recommendation.

## Starting threads

- **At most four code threads at once.** A free place takes the Order's next
  work in the same turn, as long as `bin/docket concurrent` shows it shares
  no declared file with running work. A lane can hold more than one place.
- **A design thread takes every open decision in one feature before any code
  for it.** One design thread per feature, at most three at a time, outside
  the code-thread cap. `.claude/skills/docket/modes/design.md` is how it
  runs.
- **A picked feature runs as a chain.** Each pull request starts only after
  the previous one merged. Two chains that share a file never run at once
  (`bin/docket concurrent ID`).
- **Check `bin/docket flight` before starting any thread**, and start nothing
  another session already claims. It also lists each open pull request that
  waits on the owner's read with no question recorded. Send each such thread
  back to record its `Owner-ask:` before it messages the owner (`PL-52SV`).
- **Say which model the thread runs on.** The model is the one the `[models]`
  table in `docket.toml` chooses, which `bin/docket show ID` prints on its
  `model:` line. A thread on Opus carries `ultracode` in its brief (project
  owner, 2026-10-14 18:24Z). Workspace, Area and View design runs on Opus
  wherever it needs design. So does an item at `needs-decision`, or classed
  safety or science, which docket marks "strongest model". For any other
  thread, say it does not need Opus, or recommend Opus with the reason.
- **If a thread stops at its context budget**, start a fresh thread on the
  same branch without asking the owner.

## What every brief tells its thread

- Post a **new** one-line reply when its pull request merges, never only an
  edit of an earlier reply or of its checklist (project owner, 2026-10-18
  19:52Z). The coordinator learns that a place is free from that line.
- Start every pull request body with the project's attribution block, and
  assign the project owner. Do not request the owner's review: the GitHub
  connector opens the pull request as the owner, and GitHub refuses a review
  request from a pull request's own author.
- Never cut the release that the Goal names. A cut thread stops and reports if
  its version would be that release.
- Decisions go in item files.
- **A session running under a coordinator asks the coordinator, not the owner**
  (project owner, 2026-10-19). This applies to a Projects thread and to any
  other session that a coordinator session started. Such a session sends a
  question the coordinator can answer to the coordinator, never to the owner:
  what to work on next, which item to take, whether to carry on. The
  coordinator decides it, or brings the owner only a real decision, written to
  the standard of `.claude/rules/instruction-writing.md` rule 10.
- **Fill a long wait with work** (project owner, 2026-10-25, ratified, over
  leaving the coordinator to notice an idle thread). Before a thread goes idle
  on a wait expected to last more than an hour, it runs `bin/docket next` in
  its lane and takes any ready item inside the scope it was given. If there is
  none, it tells the coordinator, so that the place can be filled (`PL-D1FD`).
- Run `uv run pytest -q tests/unit/test_line_splits.py | tail -1` as the
  first command. A Projects thread does not load `.claude/settings.json`
  (`PL-CR81`), and only the setup script in `docs/maintainer.md` gives it the
  repository's hooks. When the hooks are loaded, the gate-status guard refuses
  that command. When it prints a test count instead, the thread has no guard
  hooks and no session-start digest. It then says so in its first reply and
  files it with `bin/docket new`, naming `PL-4J4H` as the last fix.

What a Projects thread loads, as last observed on 2026-11-22: `CLAUDE.md` and
the three resident rules at launch, each path-scoped rule when it reads a
matching file, and the repository's skills in its Skill tool (`PL-KMXJ`,
`PL-4J4H`). It gets the guard hooks only from the setup script. On 2026-11-22
the thread "Finish all open defects", started after the setup script was
updated, had them: the gate-status guard refused the first command. Drop the
last line of the list above once Projects threads load `.claude/settings.json`
themselves, or once a plugin carries the hooks (`PL-XFDQ`).

## Reporting to the owner

- **Where things stand.** When the owner asks what the Goal's release still
  needs, start one thread that answers from `origin/main` with `bin/docket
  wave`, `bin/docket status`, `bin/docket feature NAME` and `ROADMAP.md`. It
  changes nothing and opens no pull request. Its reply leads with its
  recommendation, then says in two or three sentences where the release
  stands. Then comes a pick list of at most eight lines. Each line is a
  feature the owner can name back, with what it buys, its open items and their
  sizes, how many wait on the owner's decision, and its lane (product,
  workflow, or both). Gate work is grouped by each item's docket feature, and
  the smaller ones collapse into one line per lane. Build work is listed as the
  Required-scope entries that can start now and what each unblocks. Then
  comes what only the owner can decide before picking, each with a
  recommendation. The full breakdown goes in a `report.md` in the project's
  shared folder for the release, attached: every open item glossed, and the
  order the whole build can run in, from each item's `blocked-by`. It says
  where the repository does not answer and what it inferred instead. A later
  "what's left" the coordinator answers itself from a fresh `bin/docket wave`
  and `bin/docket status`, never from thread reports alone.

  <!-- absent: report.md -->
- **Review summaries** are posted in the project chat in full, not as a
  pointer to the thread.
- **A held pull request reaches the owner only through the `Owner-ask:` line
  that `bin/docket arm` prints**, with its question, recommendation,
  context, options and why it is the owner's, never as a bare "read #N"
  (`PL-GG4V`). The coordinator sends a bare read ask back to its thread.
  For a held pull request, the options are the change and what it was chosen
  over, never merging against holding, which gains the owner nothing (project
  owner, 2026-11-14). The
  ask quotes the text to judge, before and after with its surrounding
  paragraph, and never only points into a file. When a thread's ask does not,
  the coordinator adds the quote or sends the ask back (project owner,
  2026-11-02, `PL-77QB`).
- **A rewrite of a specification document that changes no value, equation,
  code span or citation does not reach the owner.** It merges on green. Only a
  sentence whose meaning needs a clinician's judgment is put to them, quoted
  (project owner, 2026-11-02, ratified, `PL-ZTZF`).
  `docket.arming.SPECIFICATION_DOCS` lists those documents.
- **A thread that finishes** reports one line: the item id and what it is, the
  pull request number, what it needs from the owner, and any items filed.
- **A question from the owner that only a thread can answer** goes to that
  thread at once, never as an offer to ask (project owner, 2026-10-25).
- **A stale or wrong action item** is corrected in place by the session that
  wrote it, struck through with an `[Edit: ...]`, never by a post telling the
  owner to ignore it (project owner, 2026-10-17).
- **A settings ask** is one line the owner can paste, with the value looked up
  (project owner, 2026-09-27).
- **A brief is the coordinator's**, and so are its stop rules. Never call one
  the owner's brief (project owner, 2026-09-27).
- **Styling, wording and placement are placeholders** while structure and
  function are built. Decide them without a decision card, unless a required
  value's visibility is at stake (`.claude/rules/instruction-writing.md` rule
  14).

## Product focus and the Projects trial

`CLAUDE.md` § "What this project is" keeps the rule: a session given no
particular work is a product session, and an apparatus finding stops it only
when it blocks it. The project owner set it on 2026-09-25 (ratified, over a fix
batch before the switch and over working each root cause in the owner's own
sessions, `PL-2866`). Root causes are worked in parallel by the Projects
trial's coordinator (`PL-NZC0`) while that trial runs, not in the owner's
sessions. A product session that finds one while the trial is paused ends its
reply with a ready-to-paste prompt for a fresh session on it, as `CLAUDE.md`'s
generator rule says (`PL-0GWD`). It holds until the owner ends it. Ending it
deletes the paragraph in `CLAUDE.md` and `docket.toml`'s `focus` key, which
points the digest's `Top:` line at the product lane (`PL-2CPD`).

## Merging

- Nothing the repository holds for the owner merges without the owner's
  "Merge it". The coordinator forwards it from the project chat to the thread.
  The rest merges on green.
- When the owner says "refresh main", each running thread brings `origin/main`
  into its own branch.
- Never update, arm or comment on a pull request this project did not open.
- A disarm of auto-merge by the owner's account with no message is the owner's
  (project owner, 2026-10-17). Never re-arm it.
- On every wake, check the threads for a pull request that merged without a
  report.

## Releases

Cut a release whenever the repository's release rules call for one, each in
its own thread as `.claude/skills/docket/modes/release.md` runs it. On every
merge report, the coordinator reads `bin/docket status`. When it says features
finished since the last tag and no session holds the release train, the
coordinator starts the cut that same turn, even above the place cap. The
release the Goal names is never cut automatically. When everything else for
it is done, the coordinator tells the owner, the owner test-drives `main` and
gives feedback, the tweaks are made, and that cut starts only at the owner's
word.

## The coordinator's own housekeeping

- Resolve a thread once its pull request merged and nothing is needed from
  the owner.
- Do not create routines, add repositories, or start threads for anything the
  owner has not picked. One exception: a thread whose work needs the
  references library may add `stuthedew/open-anesthesia-sim-references` to its
  own session.
- When the owner picks or drops a feature, rewrite the Order and nothing else
  to match, say so in one line, and start its first thread as soon as a place
  is free. If you cannot edit Project settings, post the new Order for the
  owner to paste. Keep Project settings under 16,000 characters, and move a
  finished Order entry to the shared folder's `order-history.md`.

  <!-- absent: order-history.md -->
- If the owner picks build work while gate entries are open, say once how many
  are open and that the roadmap clears the gate first, then do what the owner
  answers. The thread that starts it records the go-ahead in its item as
  `(project owner, DATE)`.
