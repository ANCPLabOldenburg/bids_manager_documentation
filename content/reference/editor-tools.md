---
title: Editor tools
kicker: Reference
lede: What each entry of the Editor's Tools menu does. Every tool that changes files shows what it will change before it changes anything, and records what it did in the project.
description: The BIDS Manager Editor's Tools menu, tool by tool.
---

{{ figure("l11-tools-menu", "The Tools menu, grouped by purpose.") }}

**Delete...**, **Deface...**, **Remove the skull...**, **Add or remove an entity...** and **Sessions...** open on a **scope**: the selection in the tree, the whole dataset, one subject or one session, optionally narrowed to a datatype. **Find and replace a value...** and **References** let you choose the whole dataset, one subject or one session; the other tools work on the whole dataset. Most tools that act on particular files are also in the tree's right-click menu, on what was clicked: comparing, references, renaming, entities, sessions, the defacing tools and Delete. The descriptions in italics are the tools' own, as their tooltips in the menu give them.

## Look at the dataset

### Dashboard

*{{ ref.tool_tip("Dashboard") }}*

{{ figure("l14-dashboard", "The Dashboard.") }}

### Compare images...

Puts two NIfTI images side by side with one set of controls: the crosshair, the slice, the plane, the 3-D camera, the effects and the cut plane stay together. Any two images: raw and processed, two echoes, two subjects.

Images of different sizes can be compared: the crosshair follows the position in the scanner, not the voxel ([Viewing data](/learn/12-viewing-data/#compare-two-images)).

### Quality check...

*{{ ref.tool_tip("Quality check...") }}*

{{ figure("l13-qc-dialog", "The quality check of the whole dataset.") }}

## Check and repair

### Check coherence...

*{{ ref.tool_tip("Check coherence...") }}*

{{ figure("g-coherence", "Check coherence after files were changed outside BIDS Manager: four problems by kind, the safe repairs ticked.") }}

Runs on its own thread as soon as it opens; **Check again** runs it once more. Findings are grouped by kind; a repair that loses nothing comes ticked, one that overwrites a value comes unticked, and a finding with no repair is listed with the reason. **Select safe ones**, **Select all** and **Select none** set the ticks; **Repair** applies the ticked ones as one step. Every kind it finds, with cases: [Keeping a dataset consistent](/guides/consistency/#check-coherence).

### Scans and sessions tables...

*{{ ref.tool_tip("Scans and sessions tables...") }}*

{{ figure("g-tables", "Scans and sessions tables: the tables to write, with the rows each gains, keeps or loses.") }}

**Scans tables, one per session** and **Sessions tables, one per subject with sessions** choose what to write; **Write N tables** writes the ticked ones as one step. `acq_time` comes from the sidecar's `AcquisitionDateTime`, else from the date and time the scan read, else `n/a`. Rows, columns and values already there are kept. The same tables are written after every conversion while **Settings** > **Convert** > **Write scans and sessions tables** is on, and by `bidsmgr-metadata --tables-only`.

### Write sidecars from the recordings...

*{{ ref.tool_tip("Write sidecars from the recordings...") }}*

{{ figure("g-sidecars-dialog", "Sidecars from the recordings: the recordings, and the selected one's fields with where each was read.") }}

**Read from** sets whether the source data is converted again (only in a project that converted the dataset); the recording's header, your answers and the linking sidecars are always read. **Which sidecars** is **Missing ones** or **Also add to existing**; **Mark what is still unknown with TODO** is **Nothing**, **Required fields**, **Required and recommended** or **Every field the standard declares**; **Where** chooses the scope and a datatype. A field is listed under **Written**, **Already stated higher up, left to it**, **Found, not written: not valid in this BIDS version** or **Required, and nothing to read it from**. **Write N sidecars** writes the ticked ones as one step. In the tree's right-click: **Write its sidecar from the recording...**, **Complete its sidecar from the recording...**, and on a folder **Write missing sidecars here from the recordings...**. The same from a terminal: `bidsmgr-sidecars`. See [Writing sidecars from the recordings](/guides/sidecars/).

### References (IntendedFor, Sources...)...

*{{ ref.tool_tip("References (IntendedFor, Sources...)...") }}*

{{ figure("l11-references", "References: every link in the dataset, from both ends.") }}

### Fix ups...

*{{ ref.tool_tip("Fix ups...") }}*

{{ figure("l09-fixups", "Fix ups.") }}

### Ignored files...

*{{ ref.tool_tip("Ignored files...") }}*

{{ figure("g-ignore-list", "The ignore list: each line of .bidsignore with what it hides, and the dataset's files.") }}

Opens `.bidsignore` in the viewer as a list: each line with how many files it hides (click one to see them), **Remove line** ({{ key("Delete") }}), and a field to add a pattern, with the files it would hide shown while you type. On the right every file of the dataset, filtered by **Find a file** and **All**, **Ignored** or **Validated**, with **Ignore** and **Stop ignoring** for a selection. The tree's right-click offers **Ignore in validation** and **Stop ignoring** on what was clicked. How the patterns work, and cases: [Leaving files out of validation](/guides/ignoring-files/).

## Names and structure

Each of these follows the scans tables, `IntendedFor` and the other fields that name files. Cases for each, from merging two subjects to putting a dataset into sessions: [Fixing names and structure](/guides/names-and-structure/). **Rename entity...**, **Index widths...**, and **Find and replace a value...** across the whole dataset also update the participants and sessions tables, and `TaskName` where it was derived from the task label.

### Rename entity...

*{{ ref.tool_tip("Rename entity...") }}*

{{ figure("l11-rename", "Rename entity, for a task.") }}

### Find and replace a value...

*{{ ref.tool_tip("Find and replace a value...") }}*

### Index widths...

*{{ ref.tool_tip("Index widths...") }}*

### Add or remove an entity...

*{{ ref.tool_tip("Add or remove an entity...") }}*

Only the entities the standard allows for the selected files are offered; one it requires cannot be removed.

### Sessions...

*{{ ref.tool_tip("Sessions...") }}*

{{ figure("l11-sessions", "Sessions, removing the session of the course's sample.") }}

## Identifiable data

### Deface...

Removes the face from anatomical images, so the dataset can be shared without the participants being recognisable. It lists the images it will deface, and those it skips with the reason, before anything is written; the originals are kept in the project's `.bidsmgr/` folder.

{{ figure("l14-deface", "Deface.") }}

### Remove the skull...

Keeps only the brain, removing the face and everything else outside it. The result is a derivative, not raw data, and is written to `derivatives/bidsmgr-skullstrip/` (or, if you choose, over the original). **Include derivatives**, in this dialog and in **Deface...**, adds the images of the pipelines in `derivatives/`; a stripped derivative keeps its source's description plus `brain` ([Images in derivatives](/guides/defacing/#images-in-derivatives)).

### Compare with the original...

*{{ ref.tool_tip("Compare with the original...") }}*

### Put the face back...

Restores defaced images from the copies kept in the project's `.bidsmgr/` folder or in `sourcedata/`, however many edits came afterwards, and takes the defacing record out of the sidecar.

More on all four: [Defacing and skull stripping](/guides/defacing/).

### Anonymise metadata...

*{{ ref.tool_tip("Anonymise metadata...") }}*

{{ figure("g-anon-dialog", "Anonymise metadata: what by purpose, where, and every change before it is written.") }}

**What**: **Recommended**, **Strict** or **Custom**, and eight categories grouped by purpose (Names and IDs, Ages, Dates and times, The site, Devices, DICOM UIDs, Traces of the conversion, Photographs), each with its options and how many changes it makes. **Where**: the dataset's files at the top, and each subject and session, with **Find a subject**, **All** and **None**. **What changes**: the counts, and the changes **By kind**, **By file**, **To read by hand** and **Not changed here**; a file can be left out of the run with {{ key("Space") }} or its right-click. **Then delete the copies the Editor keeps for Undo** removes the identifiable originals once it is done. **Anonymise N files** writes it as one step. Opened from the tree's right-click, it starts on what was clicked. Every category and case: [Anonymising metadata](/guides/anonymising/).

## Remove

### Delete...

Deletes recordings, datatypes or sessions, and with them the `*_scans.tsv` rows, the `IntendedFor` entries, the participants row of a subject left with no data, and any folder left empty, in one operation. It starts on the tree selection; the whole dataset is deliberately not one of its scopes. A copy of every deleted file is kept in the project's `.bidsmgr/` folder.

{{ figure("l11-delete", "Delete, for the eye-tracking folder.") }}

An empty folder can be deleted the same way, from the tree's right-click.
