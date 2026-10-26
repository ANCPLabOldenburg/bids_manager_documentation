---
title: Fixing names and structure
display_title: Fixing names and *structure*
kicker: Guides
group: Curating a dataset
lede: Rename a subject, a session or a task; merge two subjects that are one person; put a dataset into sessions or take it out; add the label you forgot; write every run the same way; delete what does not belong. Every reference to a file follows it, and every change is one step to undo.
description: Rename entities, merge subjects, create and remove sessions, add or remove entities, index widths, find and replace and delete in BIDS Manager's Editor, with real cases.
time: 25 minutes
sample: MRI sample 1, multimodal sample v3
---

::: before
- A converted dataset open in the Editor as a project. The cases use MRI sample 1 (two subjects, the first in the sessions pre and post) and the course's multimodal sample.
:::

## Why not rename in the file manager

A BIDS name is written in several places at once. Renaming `sub-002` touches the folder, every file name under it, the subject's scans tables, its row of `participants.tsv`, every fieldmap's `IntendedFor`, and any `bids::` link that names one of its files. A file manager renames one of these; the validator then reports nothing about the rest, because each file on its own is still legal. The Editor's tools change all of them together, show every change before it is written, and record it as one step to undo ([Undo, redo and the history](/guides/history/)). If a rename has already happened outside, [Check coherence](/guides/consistency/#check-coherence) finds what it left behind.

| To... | Tool |
|---|---|
| change a value everywhere: a subject's ID, a task, a session, an acquisition label | **Rename entity...** |
| change a value in part of the dataset | **Find and replace a value...** |
| make two subjects one | **Rename entity...** with **Merge them into one subject** |
| add a label (`acq-`, `run-`, `ce-`...) or take one off | **Add or remove an entity...** |
| put recordings into a session, or take them out | **Sessions...** |
| write `run-1` and `run-01` the same way | **Index widths...** |
| delete recordings, datatypes, sessions, subjects or empty folders | **Delete...** |

All are in **Tools** under **Names and structure** and **Remove**, and on the tree's right-click for what was clicked.

## Case: one participant, converted as two subjects

The scanning unit registered the follow-up visit of the first participant under a new ID, and the conversion made it a second subject. In MRI sample 1, `sub-002` should be the third session of `sub-001`.

::: step Put sub-002 into a session
Select `sub-002` in the tree and choose **Tools** > **Sessions...**, **Create a session**, value `followup`. Every file moves into `sub-002/ses-followup/` and takes `ses-followup` in its name; the scans table moves with them.

{{ figure("g-names-session", "Sessions, Create a session for sub-002: every file moves into ses-followup.") }}
:::

::: step Rename the subject onto the other
Choose **Tools** > **Rename entity...**, **Subject (sub-)**, rename `002` to `001`. `sub-001` exists, so **Merge them into one subject** appears. Tick it: the session moves under `sub-001`, the scans tables join, and the two rows of `participants.tsv` fold into one that keeps every value either states. The button becomes **Merge**.

{{ figure("g-names-merge", "Rename subject sub-002 to sub-001 with Merge them into one subject: 31 files, one participants row folded, 12 references in 3 files.") }}
:::

::: step Check
One subject, three sessions:

{{ figure("g-names-merged", "After the merge: sub-001 with ses-followup, ses-post and ses-pre.") }}

Validate, and run **Check coherence**: the sessions table now lists three sessions with when each began. A merge cannot be undone by renaming back, since nothing says which files were whose; **Undo** can.
:::

Two subjects merge only if their files do not collide: when both have a `T1w` in the same place, the merge is refused and names the files, because one of them needs another name first (a session, as above, or an `acq` or `run` label).

## Case: rename a task everywhere

The EEG recordings of the course's sample were converted as `task-motorimagery`; the lab calls it `imagery`. **Tools** > **Rename entity...**, **Task (task-)**, `motorimagery` to `imagery`:

{{ figure("l11-rename", "Rename entity, task motorimagery to imagery: every file that moves and every reference that follows.") }}

The files, their events and channels tables, the scans rows and `TaskName` follow. `TaskName` is changed only where it was the task label written out: a `TaskName` such as "Motor imagery, left and right hand" is left as you wrote it.

## Case: two spellings of one label

The first batch was converted with `acq-tfl3p2`, later ones with `acq-mprage`, and both now exist. **Tools** > **Find and replace a value...** replaces one value of one entity inside the scope you choose (the whole dataset, a subject, or one session of a subject), listing each value with how many files carry it, with the files, scans rows and references that follow:

{{ figure("w-find-replace", "Find and replace: acq-tfl3p2 becomes acq-mprage, with the scans row that follows.") }}

Use **Rename entity...** to change a value everywhere, **Find and replace** to change it in part of the dataset.

## Case: a label you forgot

Two kinds of functional run were converted without the `acq` label that tells them apart, so they were numbered as runs of one acquisition. Select their files in the tree, then **Tools** > **Add or remove an entity...**, **Add or change an entity**, `acq`, `mb8`:

{{ figure("w-add-entity", "Add or remove an entity: acq-mb8 added to the functional runs.") }}

Only entities the standard allows for every selected file are offered (no `echo` on EEG), the value is checked against the entity's format (`run` must be a number), and the standard decides where the entity goes in each name, whatever order you type. Sidecars and companion files travel with their recording; a file shared by several recordings, such as an inherited sidecar, stays. **Remove an entity** offers only what the standard does not require: a BOLD run cannot lose its `task`.

## Case: put a whole dataset into sessions

A study converted without sessions gains a second visit. Select every subject, **Tools** > **Sessions...**, **Create a session**, `1`: every file moves into `ses-1`. Convert the second visit as `ses-2`. **Remove the session** does the reverse for a subject with one session: its files move up and lose `ses-` from their names, and the scans rows fold into the subject's table.

## Case: run-1 beside run-01

Recordings from two converters, or two batches, write runs at different widths. The standard accepts both, but a dataset that mixes them sorts badly and confuses scripts. **Tools** > **Index widths...** shows, for each index entity (`run`, `echo`, `flip`, `inv`, `split`, `chunk`), the widths in use, and writes them all at the width you choose:

{{ figure("w-index-widths", "Index widths on the advanced MRI sample: every run written with two digits.") }}

To have the next scans propose one width from the start, set it in **Settings** > **Scan** > **Index width in proposed names**.

## Case: delete what does not belong

Select files, folders, a datatype, a session or a subject in the tree, and choose **Delete...** on the right-click (or **Tools** > **Delete...**):

{{ figure("l11-delete", "Delete, for the eye-tracking folder, with the scans rows that go with it.") }}

A picked file takes its companions with it (the sidecar, the events table, the other files of a fieldmap). One operation also removes the scans rows, the `IntendedFor` entries that named the files, the participants row of a subject left with nothing, and the folders the deletion empties. Every deleted file is kept for **Undo**. The dataset itself, `dataset_description.json` and the project's `.bidsmgr/` folder cannot be deleted.

An empty folder, such as a datatype folder left behind by a move outside the app, can be deleted the same way: right-click it, **Delete...**.

## After any of these

Validate the dataset. Changing names changes nothing the validator would otherwise report, but it is the moment to see the dataset as a whole again. If files were also moved outside BIDS Manager in the meantime, run **Check coherence**.
