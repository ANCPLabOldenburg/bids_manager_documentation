---
title: Undo, redo and the history
display_title: Undo, redo and the *history*
kicker: Guides
group: Curating a dataset
lede: Every change the Editor makes to a dataset is one step of its history, kept with the files as they were. Undo walks back through it, Redo walks forward again, and the history lists every step to go back several at once.
description: Undo and redo in BIDS Manager's Editor: what is recorded, the history list, several steps at once, changes made outside the app, and freeing the space.
time: 10 minutes
sample: Multimodal sample v3
---

::: before
- A dataset open in the Editor as a project. A folder opened **View only** has no history: nothing is written into it.
:::

## What is a step

One action is one step, however many files it touches: a rename that moves 40 files and rewrites 12 references, a deletion with its repairs, a fix applied to a hundred sidecars, an anonymisation, an ignore, a saved sidecar or table. What is recorded:

| Recorded | Not recorded |
|---|---|
| Saving a sidecar, a table, a text file, `CITATION.cff` in the viewer | Edits not saved yet: they have their own undo, in the open file |
| Rename, add or remove an entity, sessions, index widths, find and replace | The conversion itself |
| Delete, with its repairs; a folder created or removed | Changes made in another program |
| Fix ups, Check coherence's repairs, References, Scans and sessions tables | |
| Ignoring and bringing back files | |
| Anonymise, deface and put the face back | |
| Bad channels and segments saved from the viewer | |

## Undo and redo

**Undo** and **Redo** are in the Editor's toolbar, with {{ key("Ctrl+Z") }} and {{ key("Ctrl+Shift+Z") }}. Hovering them says what they would do. Undo first takes back the edits of the open file that are not saved yet; once there are none, it takes back the dataset's last step. Redo makes the last undone step again, until a new change is made: a new step clears what was left to redo.

## The history

Right-click **Undo** (or **Redo**) for the steps it would walk through, newest first, each with when it was made and, when it touched several, how many files:

{{ figure("g-history-menu", "The history after renaming a task, ignoring a folder of notes and anonymising: newest first, with when each was made.") }}

Click a step to undo it and every step after it. BIDS Manager first lists what will be undone, with how many files in all, and asks.

## Cases

### Undo a rename that went wrong

The rename of a subject touched 40 files and the participants table: one **Undo** puts every file back under its old name, the references as they were, and the row of `participants.tsv`. Folders the rename created and emptied are removed; folders it emptied are made again.

### Go back to before an afternoon's work

Right-click **Undo** and click the first step of the afternoon. Every step after it is undone in one go, after the list and the question.

### A file was changed by hand after the step

If a file of the step changed afterwards, by hand or by another program, the question says so and names the files: undoing replaces those changes too. Cancel, and copy them aside first if you want to keep them.

### Free the space, or share the project

The history keeps a copy of every file a step changed, in `.bidsmgr/editor/originals/`, until it can no longer be undone. After an anonymisation, those copies are the identifiable originals. **Anonymise metadata...** offers to delete them once it is done (**Then delete the copies the Editor keeps for Undo**); nothing before can be undone afterwards. Either way, never share `.bidsmgr/`: [The project folder](/concepts/project-folder/).

## Where it is kept

The steps are listed in `.bidsmgr/editor/operations.log` (and the undone ones in `redo.log`), and the copies of the files in `.bidsmgr/editor/originals/<step>/`. They are plain files: a project folder copied to another computer keeps its history.
