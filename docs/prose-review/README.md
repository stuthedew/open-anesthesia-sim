# Records of the prose review

The project owner removed the copy editor on 2026-11-14 (`PL-GL45`), with its
agents, the blind judge, its test set of rejected and gold-standard paragraphs,
and the records of its runs. Four tests under `PL-J1ZM` showed that it did not
change how sessions write. Git history holds the removed files. A session now
checks the text it writes itself, at close-out step 8 in
`.claude/skills/docket/modes/close-out.md`, and runs
`python3 tools/new_prose.py --compare` there to find a fact that an edit
dropped.

This folder keeps three records that nothing reads but a session:

- `model-reverse-outline.tsv` is a reverse outline of `docs/MODEL.md` as it
  stood at commit `50af1a2e` on 2026-11-10. It has one row for each
  paragraph, list, table, code block and heading, with the reader who needs
  it, what kind of text it is and where it would best live. `PL-9RLM` says
  how it was made.
- `model-description-draft.md` is a draft of the model's description for a
  clinician, written from that outline for the project owner to read
  (`PL-B07T`). It is not the specification, which is `docs/MODEL.md`.
- `short-instructions-test-2026-11-11.md` keeps the texts of one test of
  shorter standing instructions. `PL-J1ZM` records the test's design,
  criteria and result.
