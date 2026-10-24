# PL-TCBJ SZZ candidate list and shuffle: recovered records

These files were recovered on 2026-10-24 from the transcript of
`session_01JQuNZNYNK5kqZyBxjguXe6`, read through the `list_events` and
`get_event` tools. The original scripts and outputs lived in that session's
container at `/tmp/claude-0/-home-user-open-anesthesia-sim/45eaf3d4-ced3-51a4-9eec-9faf4f65f319/scratchpad/`,
which no longer exists. Each script below is the session's own text, copied
verbatim from the tool call that wrote or ran it.

## Git ref

All git commands in the session ran against `origin/main` as it stood in that
container. At 16:44:29 UTC its head was
`2f0101bb7` ("PL-Q3G9, PL-G84G, PL-0B22: file three gaps in the
one-source-of-truth inventory (#1722)"), with 2042 commits, of which 1604 have a
subject ending in `(#N)`. That output is in `count-main-commits.output.txt`. The
only fetch the session made before this (16:43:11 UTC) fetched
`claude/triage-cvv9wo`, not `main`. The session's own branch was
`claude/pl-tcbj-5fmfla`.

## Files and source events

Each step has a `.cmd.sh` file with the full command, verbatim, and an
`.output.txt` file with its tool result, verbatim. A step whose command held a
Python heredoc also has that heredoc saved as a `.py` file.
`_meta.json` maps each step to its command event, time and result event.

| Step | Files | Command event | Time (UTC) | Result event |
| --- | --- | --- | --- | --- |
| Explore the item population | `explore-population.*` | `0eee23ec-bb80-4867-9b36-8f080b426629` | 16:44:18 | `86a5534a-52e8-449d-b008-d5a6e19626c1` |
| Count main's commits; record the ref | `count-main-commits.*` | `b4477be4-dc73-4469-aed9-7ebe6d1a2d1c` | 16:44:29 | `738498e5-f23d-4219-ab01-daba1908e69c` |
| Write and run the SZZ pass | `szz.py`, `run-szz.*` | `106f4d91-0d2f-4ad2-8e18-9c4814d48e57` | 16:44:42 | `00a7039d-df68-468e-b4b2-34b1cd7ed928` |
| Exploratory filter of the blame rows | `filter-top-blame.*` | `8ed6808d-86cf-4503-b327-7122e16c00e2` | 16:47:01 | `bcc12cf9-4fff-41bd-b7af-9f2f74960e0c` |
| Build the candidate list (`candidates.tsv`) | `candidates.*` | `08b57a58-5ca7-4dd2-be09-9d11b3708845` | 16:47:36 | `0d445a1a-2418-49e6-89dd-efa9b13d77c7` |
| Seeded shuffle, positions 1-24 printed | `shuffle.*` | `f892c2f1-db77-4b90-8382-f4c8e5c19f7e` | 16:50:35 | `eb0c466c-1566-4a01-aa38-98a9b9823aec` |
| Seeded shuffle again, positions 25-44 printed | `shuffle-25-44.*` | `cb91b82d-038b-4350-9178-9e937eb95340` | 17:08:01 | `a26acfd1-4288-4b15-9b7f-7ad6e9a002d2` |

`run-szz.output.txt` reads `1082 194`. That is 1082 items in the population and
194 of them with at least one blamed introducing commit.

`order-output.txt` collects the candidate list, both shuffle printouts, and the
full 72-PR order. **Positions 45 to 72 were never printed by the session.** They
come from re-running `shuffle.py`'s logic here on the 73 recovered candidate
rows. That reproduction matches every position the session did print (1 to 44).

## How the recovered procedure works

1. **Population.** `szz.py` reads every `docs/items/*.md`. It keeps an item when
   its `classes` contain `defect` or `safety`, do not contain `anticipated`, and
   its `status` is `done`. Items classed `test` or `infra` are not removed here.
   `candidates.py` removes them later.
2. **Fix commits.** A commit on `origin/main` counts as a fix for an item when
   the item's id appears anywhere in the subject before the first colon
   (`^[^:]*\bID\b`). A subject that names several ids counts for each one, and
   the id does not have to come first.
3. **Blame.** For each fix commit, the pass runs
   `git diff -U0 sha^ sha -- src/anesthesia_sim/`. For each hunk that removes or
   changes at least one old line, it runs
   `git blame --porcelain -L start,end sha^ -- oldpath` on those lines. Only
   `src/anesthesia_sim/` is considered, and a file the fix deleted is still
   blamed. Blamed lines are counted per introducing commit across all of an
   item's fixes. Only the top four introducing commits per item are kept
   (`most_common(4)`).
4. **Candidate rules** (`candidates.py`). An introducing commit is a candidate
   for an item when all of these hold:
   - its subject ends in `(#N)`, which gives the pull request number;
   - the item's id does not appear in its subject;
   - it is the item's top-blamed commit, or it has at least 2 blamed lines;
   - the item file was first added to `origin/main` strictly after the
     introducing commit's committer time. Both times are `%ct`. The add time is
     the earliest `--diff-filter=A` commit for the item file on `origin/main`.
5. **Grouping.** Candidates are grouped by pull request, which gives 73 pull
   requests. Each row records the blamed commit, the lines added and deleted
   under `src/anesthesia_sim/`, the total lines changed over all paths, and the
   items with their blamed line counts.
6. **Shuffle.** Rows whose total changed lines over all paths exceed 6000 are
   dropped. Only #588 (23444 lines) is dropped, which leaves 72. The rest are
   shuffled in `candidates.tsv` file order with `random.Random(20261024)`.

## Related records not recovered here

- The protocol was committed at `61a0cf63d`.
- The answer key commit is `cda493678`. It is not present in this checkout,
  because its branch was squash-merged as #1727 (`1ff587b5c`). No fetch was made
  to get it, since a fetch writes refs.
