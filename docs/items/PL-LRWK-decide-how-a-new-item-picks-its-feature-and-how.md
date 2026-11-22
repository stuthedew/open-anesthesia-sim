---
id: PL-LRWK
title: Decide how a new item picks its feature, and how features that belong together are found later
priority: P2
effort: M
status: done
classes: feature, planning
feature: feature-registry
touches: subprojects/docket/src/docket/feature_match.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/config.py, subprojects/docket/README.md, subprojects/docket/tests/test_feature_match.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_config.py, subprojects/docket/tests/test_portability.py, docs/features.toml, .claude/skills/docket/modes/capture.md, .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/release.md
added: 2026-11-22
closed: 2026-11-22
pr: 2205
tests: subprojects/docket/tests/test_feature_match.py::test_a_title_is_offered_the_features_whose_words_it_shares_strongest_first, subprojects/docket/tests/test_feature_match.py::test_retired_and_unlisted_names_are_never_offered, subprojects/docket/tests/test_feature_match.py::test_the_closest_features_are_paired_and_unrelated_ones_are_not, subprojects/docket/tests/test_feature_match.py::test_open_items_with_no_feature_are_matched_and_paired_only_on_a_shared_path, subprojects/docket/tests/test_feature_match.py::test_an_open_item_alone_in_its_feature_is_named, subprojects/docket/tests/test_checks.py::test_an_item_carrying_a_folded_feature_is_told_the_name_to_use, subprojects/docket/tests/test_config.py::test_a_folded_feature_redirects_only_to_a_described_one, subprojects/docket/tests/test_cli.py::test_new_redirects_a_folded_feature_and_suggests_one_when_none_is_given
---

**Problem.** Decide how a new item picks its feature, and how features that belong together are found later

The project owner asked, while `PL-Q3BN` built the feature registry and found
about 58 near-duplicate feature names among 211: how should a session decide
whether a new item joins an existing feature, starts a new one, or takes none,
and how are items that belong together found after the fact? Research best
practice and plan to implement it (project owner, 2026-11-22).

**What was read, 2026-11-22.**

1. Stack Overflow's tag guidance, "Best practices for tag lifecycle
   management" (last updated 2022-11-02), read in full: "strive to use existing
   tags as much as possible and only create new ones for unique topics", and
   "Starting too granular results in tag 'sprawl'". Each tag's excerpt "should
   include basic information about when to use the tag". Maintenance is
   finding "opportunities for tag consolidation via merges and synonyms", with
   one named owner; no cadence is given.
2. Jeff Atwood, "Tag Folksonomy and Tag Synonyms", Stack Overflow Blog,
   2010-08-01, read in full: a synonym silently remaps a non-preferred tag to
   its master tag, and single-use tags older than six months were culled.
3. Mario Barité, "Literary warrant", ISKO Encyclopedia of Knowledge
   Organization, 2026, first third read verbatim: warrant is the
   "justification for including terms in a knowledge organization system", and
   the entry reports ANSI/NISO Z39.19-2005 (R2010), p. 6, using literary
   warrant for that justification. Dewey's editorial rule considers a new
   number once about twenty works need it. The standard itself could not be
   read: NISO's site refuses automated fetching.
4. Runeson, Alexandersson and Nyholm, "Detection of duplicate defect reports
   using natural language processing", ICSE 2007, pp. 499-508,
   doi:10.1109/ICSE.2007.32, abstract only: text similarity found "about 2/3 of
   the duplicates", with little difference between variants.
5. Laney, Barovic and Moin, "Automated Duplicate Bug Report Detection in Large
   Open Bug Repositories", COMPSAC 2025, arXiv:2504.14797, most of the full
   text: its related work reports that information-retrieval ranking beat
   neural methods at producing a list of possible duplicates, while neural
   classifiers did better at a yes-or-no decision.

**What was measured, 2026-11-22**, with a plain word-overlap score (TF-IDF
over each feature's item titles, name and description), in a scratch script:

1. For 399 randomly chosen past items, leaving each out, the score ranked the
   item's own feature first for 47%, in the top three for 73% and in the top
   five for 82%.
2. For the 58 merges `PL-Q3BN` drafted by hand, it ranked the chosen target in
   the top three for 42 and the top five for 47. Its 40 most similar feature
   pairs held 10 of the 58 and several pairs the hand list missed, such as
   `owner-ask-refusals` and `review-hold`.

So the score is good enough to suggest and too weak to decide, which is the
split the duplicate-report literature draws.

Re-measured through the shipped `docket.feature_match`, whose inverse document
frequency is smoothed as log(1 + N/n): 48% first, 71% in the top three and 79%
in the top five over the same 399 items, and 43 of the 58 merges in the top
three, 51 in the top five.

**Recommendation (the session's, for the owner to approve).**

1. **At filing.** Join an existing feature when its description covers the
   work. Start a new one only for a goal at least two items share, named for
   what completes, with its description line. Give a lone finding no feature.
   `bin/docket new` with no `--feature` prints the three features whose items
   best match the title, as suggestions the session accepts or ignores.
2. **Folded names redirect.** A merged name stays in the registry as
   `old = { use = "new" }`, and `bin/docket new` and `check` answer "use new"
   for it, as a Stack Overflow synonym does.
3. **Later.** A new `bin/docket features --similar` lists the feature pairs
   whose items overlap most, the open items with no feature that match a
   feature or each other, and the open features with one item. It decides
   nothing. The triage skill's grooming pass runs it and records each merge
   it takes, and the release cut runs it once.

**Generator check.** None: this is new work the project owner asked for, not a
repair of a defect that recurs.

**Decided.** The project owner asked that every question needing him be
settled by researched best practice (project owner, 2026-11-22, "For items
that need me, research best practice for all"), so the recommendation above is
built as written, in `PL-Q3BN`'s pull request. One change from it: the
"later" list is `bin/docket feature --similar` rather than a new command, so
progress and regrouping stay under one command.
