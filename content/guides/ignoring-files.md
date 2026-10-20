---
title: Leaving files out of validation
display_title: Leaving files out of *validation*
kicker: Guides
group: Curating a dataset
lede: A dataset often keeps files the standard does not describe, such as session notes, the scanner's logs or a folder of documents. The ignore list leaves them out of validation, one file, one kind of file or one folder at a time, and brings them back as easily.
description: Leave files out of BIDS validation with .bidsignore in BIDS Manager: from the tree, by pattern, in the ignore list, and how to bring files back.
time: 10 minutes
sample: MRI sample 1
---

::: before
- A converted dataset open in the Editor and validated. The figures use MRI sample 1 (two subjects, the first in two sessions) with what labs often keep beside the data: a notes file in each session, the scanner's physiological logs next to two BOLD runs, and a `notes/` folder.
:::

## What ignoring does

The standard lets a dataset name files the validator should skip, in a file at its root called `.bidsignore`, one pattern per line, in the same notation as `.gitignore`. A file it matches is still in the dataset, is still copied and shared with it; it is only not validated, so it stops being reported as "not part of the dataset".

Ignore only what is not data the standard describes. A recording with a wrong name is not fixed by ignoring it: rename it ([Fixing names and structure](/guides/names-and-structure/)).

Some places are never validated, whatever `.bidsignore` says: `sourcedata/`, `code/`, `stimuli/`, `log/` and hidden files and folders.

## Ignore from the tree

::: step Right-click what to leave out
Validated, the dataset reports seven errors: the three notes files, the two logs and the two documents in `notes/`. Right-click one session's notes file, then **Ignore in validation**. Each way of ignoring it says how many files it covers:

{{ figure("g-ignore-menu", "Ignore in validation on sub-001_ses-pre_notes.txt: this file, its whole folder, or the same name in every subject and session.") }}

| Choice | Writes | Covers |
|---|---|---|
| **This file** | `/sub-001/ses-pre/sub-001_ses-pre_notes.txt` | that file only |
| **The whole folder sub-001/ses-pre/** | `/sub-001/ses-pre/` | everything in the session: here 21 files, recordings included, which is rarely what you want |
| **The same name in every subject and session** | `/sub-*/ses-*/sub-*_ses-*_notes.txt` | every session's notes file: 2 here |

The menu offers only the choices that differ: one that would cover exactly the same files as a shorter one is left out. Other picks offer other choices: **With its sidecar** for a file with a `.json` of the same name, **Every .log file** (`*.log`) for a file whose extension the standard does not use, **This folder** for a folder, **These 2 files** for a selection.
:::

::: step Read the count before choosing
The same name in every subject and session covers 2 files, not 3: `sub-002` has no sessions, so its `sub-002_notes.txt` does not have the name the pattern describes. Ignore it on its own (**This file**) or pick the three notes files together, which offers a pattern for each layout.
:::

::: step See what is ignored
Choose. The line is added to `.bidsignore`, validation runs again, and the tree draws every ignored file and folder dimmed and in italics; hovering one says which line hides it.

{{ figure("g-ignore-tree", "The tree after ignoring the session notes, the logs (*.log) and the notes folder: drawn dimmed and in italics, no longer counted.") }}

Each change of the ignore list is one step of the Editor's history: **Undo** takes it back ([Undo, redo and the history](/guides/history/)).
:::

## The ignore list

**Tools** > **Ignored files...**, or **Ignored files...** at the end of the Ignore in validation menu, opens the list in the centre:

{{ figure("g-ignore-list", "The ignore list: each line of .bidsignore with how many files it hides, and every file of the dataset with the line that ignores it.") }}

- **On the left, the lines** of `.bidsignore` and how many files each hides now. Click a line to show only its files on the right. Select lines and click **Remove line**, or press {{ key("Delete") }}, to remove them. Type a pattern under the list and click **Add**: the files it would hide are shown while you type.
- **On the right, the files** of the dataset. **Find a file** filters them; **All**, **Ignored** and **Validated** show part of them; **Ignored by** names the line. Select files and click **Ignore** or **Stop ignoring**: the same choices as in the tree.
- The lines BIDS Manager needs (`.bidsmgr/`, `.tmp_bidsmgr/`) are shown as already ignored.

## Bring files back

Right-click files that are ignored, one or several, and choose **Stop ignoring**:

{{ figure("g-ignore-stop", "Right-click on the two physiological logs, both hidden by *.log: Stop ignoring these 2 files.") }}

What it writes depends on the lines that hide them:

- A line that hides nothing but the picked files is removed.
- A line that also hides other files stays, and an exception is added for each picked file (`!/sub-001/ses-pre/func/sub-001_ses-pre_task-rest_physio.log`), so the rest stays ignored.
- A file inside an ignored folder cannot be brought back by an exception: in the `.gitignore` notation, which the validator follows, nothing inside an ignored folder can be re-included. For such a file the menu offers **Remove a line instead**, naming the line and how many files it hides.

## Cases

### A notes file in every session

Pick one, **Ignore in validation** > **The same name in every subject and session**. One line covers every session, now and in sessions converted later.

### The scanner's logs, or a lab's own format

**Every .log file** (or `.mat`, `.csv`...) adds `*.log`. Prefer it to listing files: a run converted later is covered too.

### A folder of documents

Right-click the folder: **This folder** adds `/notes/`. A folder that holds code or stimuli belongs in `code/` or `stimuli/`, which are never validated: moving it there is better than ignoring it.

### A pattern by hand

In the ignore list, type it under the lines: `**/*_notes.txt` matches the notes at any depth, `/sub-*/anat/*.txt` text files in any subject's `anat/`. The files it would hide appear while you type, before **Add**.

### Undo an ignore

**Undo** in the toolbar, or right-click **Undo** for the list of steps: an ignore is listed as **Ignore in validation: ...**.

## From a text editor

`.bidsignore` is a plain text file: edit it in any editor, then **Validate dataset**. A line starting with `/` is anchored at the dataset's root, `*` matches within a name, `**` across folders, a line ending in `/` is a folder, and a line starting with `!` is an exception. Lines starting with `#` are comments.
