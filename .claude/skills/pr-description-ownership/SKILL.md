---
name: pr-description-ownership
description: Draft or revise a pull request (MR) description for an ECD or NTC ticket. The body opens with one plain sentence saying what changed for the user, then only the required Nautobot template fields.
---

# Write a PR description

The body opens with one sentence. A maintainer who knows the product and has never seen this
patch must know, from that sentence alone, what a user now sees. Return the Markdown body ready to paste.

Read the final diff. Use the ticket for the original problem, review comments for tradeoffs, and test results for claims that need evidence. When revising a draft, check that its claims still hold after the latest commits.

## Shape

Follow `.github/PULL_REQUEST_TEMPLATE.md` in the clone, with its headings in its order. The Nautobot template is:

```
# Closes #<issue>
# What's Changed
<ONE plain sentence>
Test status: `<exact command>` -> `<Ran N tests ... OK or FAILED line>`   (or: Not run: <reason>)
# Screenshots
<table, or N/A and the reason>
# TODO
<template checklist, exact text; tick only what this change did>
```

- **The sentence.** Plain English, 25 words at most, active voice. Say what the user sees now and what was wrong before. Put the operation first. No code names, file names, IDs, query counts, or tradeoffs in it.
- **Tradeoffs.** A tradeoff that could change the merge decision still matters. Keep it out of the sentence and say it in one line under "What's Changed" only if a reviewer must weigh it, and name the affected workload and the trigger. Distinguish a measured result from an expected effect.
- **Closes.** Link the issue the ticket names. If none is given, leave `# Closes #` empty and say so in the sentence.
- **Test status.** One line: the exact command and its result line. If a test did not run, write "Not run" and why. Never claim a pass you did not see.
- **Screenshots.** Keep every row of the before and after table. Show a before and after pair only if the two images differ. Drop a pair the UX check reports as identical, and say so in one line.
- **TODO.** Tick only what this change completed. The changelog fragment is `changes/<issue_or_PR_number>.<change_type>.md`.
- Do not add an authorship or co-author line.

## Never write

- A "User impact" or "How it was checked" block, a file inventory, a review-effort table, the agent's work history, or any section beyond the template's headings.
- Run, story, or tracker IDs.

## Example from a GraphQL performance fix

What's Changed: "Device lists with their VLANs now load in a fixed number of database queries, not one pair per device."
Tradeoff (only if a reviewer must weigh it): "Golden Config runs a VRF-to-VLAN query once per device. Its cost on that workload is not measured yet."
