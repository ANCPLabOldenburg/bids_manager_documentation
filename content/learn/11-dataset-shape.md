---
title: Changing a dataset's shape
chapter: 11
lede: Rename an entity across the dataset, add or remove one, create or remove a session, delete recordings, and keep every reference pointing at the right file. Each tool shows exactly what it will do before it does anything, and every change is recorded in the project, with the files as they were.
time: 20 minutes
sample: Multimodal sample v2
---

::: before
The sample is validated and its metadata edited (chapters 9 and 10). This chapter opens each tool, reads its preview and closes it with **Cancel**: the course's dataset stays as it is, so the next chapters match what you see.
:::

## Why renaming a file is not enough

A file's name in a BIDS dataset is referenced from other files: the session's `_scans.tsv` lists it, a fieldmap's `IntendedFor` points at it, `participants.tsv` names its subject, and a sidecar's `TaskName` repeats its task. Renaming a file in your file manager breaks those links silently: the validator does not notice most of them. The Editor's tools rename, move and delete through all of them at once.

## The Tools menu

Click **Tools** in the Editor's toolbar.

{{ figure("l11-tools-menu", "The Editor's Tools menu.") }}

| Group | Tools |
|---|---|
| Look at the dataset | **Dashboard**, **Compare images...**, **Quality check...** |
| Check and repair | **Check coherence...**, **Scans and sessions tables...**, **References (IntendedFor, Sources...)...**, **Fix ups...**, **Ignored files...** |
| Names and structure | **Rename entity...**, **Find and replace a value...**, **Index widths...**, **Add or remove an entity...**, **Sessions...** |
| Identifiable data | **Deface...**, **Remove the skull...**, **Compare with the original...**, **Put the face back...**, **Anonymise metadata...** |
| Remove | **Delete...** |

The same actions, for the file or folder you click, are in the BIDS tree's right-click menu:

{{ figure("l11-tree-menu", "The BIDS tree's right-click menu on the resting EEG recording.") }}

**Rename entity...**, **Add or remove an entity...** and **Sessions...** open the same kind of dialog: what to change at the top, and below, **What this would do**, a tree of every file in the dataset that changes, with what it **Becomes**. Untick anything you want left alone. **Find and replace a value...** and **Index widths...** list their changes under **What would change**. **Preview at the side** puts the tree beside the controls instead of below them. Nothing is written until you click the dialog's main button.

## Rename an entity

::: step Open Rename entity
Choose **Tools** > **Rename entity...**. Set **Entity:** to **Task (task-)**, **Rename:** to `motorimagery`, and type `imagery` in **To:**.

{{ figure("l11-rename", "Renaming the task motorimagery to imagery.") }}

The dialog says it **Would change 5 file(s), 2 reference(s) in 2 file(s)**: the recording, its sidecar, its channels and events tables, and the references in the scans table and the sidecar's `TaskName`. Values are renamed as values, not as text, so renaming `run-1` never touches `run-10`.
:::

::: step Close it
Click **Cancel**. (**Rename** would apply it, as one operation in the project's history, with every file it changed kept as it was.)
:::

Renaming a **subject** also renames its folder and its row in `participants.tsv`. If the new label already exists, the dialog offers **Merge them into one subject**.

## Sessions

A session is both a folder and an entity, so creating or removing one moves files and renames them. The sample has one session, so it could do without one.

::: step Open Sessions
Choose **Tools** > **Sessions...** and set **Action:** to **Remove the session**.

{{ figure("l11-sessions", "Removing the session: every file of ses-01 moves up to the subject's folder.") }}

All 60 files of `ses-01` move to `sub-001/` and lose `ses-01` from their names, and 21 references in 5 files follow: the scans table's rows, `IntendedFor` and the sessions table. **Create a session** does the opposite, for files without one.
:::

::: step Close it
Click **Cancel**.
:::

**Add or remove an entity...** works the same way for any other entity the standard allows: add an `acq-` label to tell two acquisitions apart, or remove one that is no longer needed. The standard decides what is possible: an entity a kind of file may not carry is not offered, and one it must carry cannot be removed.

## Delete

**Delete...** removes recordings, datatypes, sessions or subjects, and repairs what pointed at them: the scans table's rows, `IntendedFor` entries, the subject's row in `participants.tsv`, and folders left empty.

{{ figure("l11-delete", "Delete, for the eye-tracking folder: the files and what is repaired with them.") }}

Delete asks for confirmation before it removes anything, and keeps a copy of every file it removes in the project's history. A folder left empty, by a move outside BIDS Manager for example, can be deleted the same way.

## References

**References (IntendedFor, Sources...)...** shows every link between files from both ends. Choose a field (`IntendedFor`, `AssociatedEmptyRoom`, `Sources`), pick a file on the left, and the right lists the files it may point at, ticked where it does.

{{ figure("l11-references", "References, for the fieldmap: it points at the BOLD run.") }}

**Use what the times imply** applies the conversion's own rule: a fieldmap serves only the kind of run it was made for, one with the run's shim settings comes first, and otherwise each run gets the last fieldmap acquired before it (or else the first one after it). This is how you find out whether a run has a fieldmap at all, and fix a link the conversion could not decide.

## Check coherence

**Check coherence...** looks for what is valid BIDS and still wrong: a scans row naming a file that is gone, a recording with no scans row, a missing sessions table, a participants row for a deleted subject, a link pointing at nothing, an index written at two widths, a value spelled two ways, a `TaskName` that does not match its task, an `IntendedFor` that disagrees with the acquisition times. It is what to run after files were renamed or deleted outside BIDS Manager.

{{ figure("l11-coherence", "Check coherence on the edited sample: one recording without a scans row.") }}

On the sample, after chapter 9 wrote the eye tracker's events file by hand, it finds one thing: that file has no row in the session's scans table, and the repair, ticked because it loses nothing, adds it. Nothing is changed until you click **Repair**, and each finding shows its exact change when selected. A dataset with problems of every kind, and what each repair does, is in [Keeping a dataset consistent](/guides/consistency/).

## Two more

- **Find and replace a value...** replaces one entity value everywhere it appears, within the whole dataset, a subject or a session.
- **Index widths...** gives every index the same width: `run-1` and `run-01` are both valid, but a dataset should use one.

## Undo, and the history

Every tool above, applied, is one step of the project's history, and so is every sidecar or table you save. **Undo** in the toolbar ({{ key("Ctrl+Z") }}) takes back the last step, files, references and folders together; **Redo** ({{ key("Ctrl+Shift+Z") }}) makes it again. Right-click either for the list of steps, newest first, and go back several at once ([Undo, redo and the history](/guides/history/)).

Each tool, in several real cases (one participant converted as two subjects, a label forgotten, a dataset put into sessions afterwards): [Fixing names and structure](/guides/names-and-structure/).

::: recap
- You have seen what every structure tool would do to the sample, and closed each with **Cancel**.
- The dataset is unchanged: still 0 errors and {{ m("edited.validation.warn") }} warnings.
- Next, look at the data itself: [Viewing data](/learn/12-viewing-data/).
:::
