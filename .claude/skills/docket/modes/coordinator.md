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
  another session already claims.
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
- Decisions go in item files. The thread asks the coordinator, not the owner,
  what to work on next (`.claude/rules/instruction-writing.md` rule 10).

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
  that `bin/docket arm` prints**, in its decision or risk-review form, never
  as a bare "read #N". The coordinator sends a bare read ask back to its
  thread. When a hold has nothing to judge, ask for "Merge it" alone.
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
