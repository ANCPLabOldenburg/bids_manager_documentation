---
title: Editing metadata
chapter: 10
lede: Edit a sidecar as a form that knows the standard, or as the plain tree of keys the file holds; search it; edit a table; and undo. The course answers two of the sample's TODO placeholders, the task description and the instructions of the resting run.
time: 15 minutes
sample: Multimodal sample v2
---

::: before
The dataset validates with 0 errors (chapter 9).
:::

## The sidecar form

Select `sub-001_ses-01_task-rest_bold.json` in the BIDS tree. The Viewer shows it in the **BIDS view**: every field the file holds and every field the standard declares for a BOLD run, in one list.

{{ figure("l10-sidecar-bids", "The BOLD run's sidecar in the BIDS view.") }}

- The bar at the left of each field is its level: **required**, **recommended**, **optional** or **deprecated**, as the legend says. The label under the search names the rule set the form follows (`schema · func/bold`).
- Each field's control follows its type: a dropdown for a field with a list of allowed values, a number field for a number, a list for an array. Hover a field's name for the standard's description of it.
- The dropdown beside the views chooses what is listed: what is in the file and what the standard declares (the default), only what is in the file, or only what is missing.
- The line at the bottom counts the fields, how many declared ones are missing, and the findings.

**Tree view** shows the same file as keys and values, exactly as stored, and lets you add a field or a subfield, or delete one.

{{ figure("l10-sidecar-tree", "The same sidecar in the Tree view.") }}

## Fill in the task description

::: step Find the field
Click in the search field above the form, or press {{ key("Ctrl+F") }}, and type `TaskDesc`. Only the fields whose name, value or description match remain, with a count.

{{ figure("l10-search", "Searching the sidecar.") }}
:::

::: step Type the description
Click the **TaskDescription** field, select the placeholder `TODO`, and type a description. The course uses: `Resting state with the eyes open, looking at a fixation cross.` The toolbar now says **1 unsaved change**.

{{ figure("l10-edit", "The description typed, before saving.") }}
:::

::: step Save
Click **Save**. The file is written, and the change is recorded in the project's history, with the file as it was before.
:::

{{ clip("l10-edit-save", "Finding TaskDescription, typing it, and saving.") }}

Answer **Instructions** the same way (the course uses `Keep your eyes on the cross and let your mind wander.`).

::: tip
By default, an edit waits for **Save**. **Settings** > **Display** > **Editor saving** saves each field as you leave it instead; every save is still recorded in the project's history.
:::

::: check
Click **Validate dataset**. The dataset still has 0 errors, and {{ m("edited.validation.warn") }} warnings instead of {{ m("fixed.validation.warn") }}: two placeholders fewer.
:::

## Apply a field to other files

Right-click a field in the form for two more actions:

- **Apply this field to other files** writes the same value into the same field of other files you choose: the institution of every recording, say.
- **Where does this value come from?** says which layer of the dataset holds the value, when the sidecar inherits it from a file higher up.

## Tables

Select `participants.tsv` at the top of the tree. The Viewer shows it as a table you can edit.

{{ figure("l10-tsv", "participants.tsv in the table viewer.") }}

Double-click a cell to edit it; **+ Add row**, **− Delete row**, **+ Add column** and **− Delete column** change its shape. Changes wait for **Save**, as in the form. A very long table opens read-only after its first rows, and says so.

The sample's `participants.tsv` holds three columns that identify the participant: `given_name`, `family_name` and `patient_id`, copied from the DICOM header. Chapter 14 removes them, with everything else that identifies, before the dataset is shared.

A table whose sidecar gives a sampling frequency, such as a physiological recording (`_physio.tsv.gz`), has a **Visualize** button that opens it in the signal viewer (chapter 12).

## Undo and redo

**Undo** and **Redo** in the toolbar ({{ key("Ctrl+Z") }}, {{ key("Ctrl+Shift+Z") }}) first step through the edits of the sidecar or table that is open and not saved yet. While you type in a field, {{ key("Ctrl+Z") }} undoes the typing in that field only.

Every save, of a sidecar, a table, a README or another text file, is a step of the project's history, with the file as it was before. Once nothing is left unsaved, **Undo** takes back the last saved step and writes the file as it was; right-click **Undo** for every step, newest first ([Undo, redo and the history](/guides/history/)).

::: recap
- The BOLD run's sidecar has a task description and instructions.
- Both saves are steps of the project's history, which **Undo** walks back.
- Next, the tools that change file names and folders: [Changing a dataset's shape](/learn/11-dataset-shape/).
:::
