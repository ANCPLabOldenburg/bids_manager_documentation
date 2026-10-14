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

{{ figure("l11-coherence", "Check coherence on the course's sample.") }}

::: warning
In {{ version }}, Check coherence lists a MEG recording's `coordsystem.json` as a sidecar without a recording, ticked for deletion. Untick it ([Known issues](/help/known-issues/)).
:::

### References (IntendedFor, Sources...)...

*{{ ref.tool_tip("References (IntendedFor, Sources...)...") }}*

{{ figure("l11-references", "References: every link in the dataset, from both ends.") }}

### Fix ups...

*{{ ref.tool_tip("Fix ups...") }}*

{{ figure("l09-fixups", "Fix ups.") }}

## Names and structure

Each of these follows the scans tables, `IntendedFor` and the other fields that name files. **Rename entity...**, **Index widths...**, and **Find and replace a value...** across the whole dataset also update the participants and sessions tables, and `TaskName` where it was derived from the task label.

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

Keeps only the brain, removing the face and everything else outside it. The result is a derivative, not raw data, and is written to `derivatives/bidsmgr-skullstrip/` (or, if you choose, over the original).

### Compare with the original...

*{{ ref.tool_tip("Compare with the original...") }}*

### Put the face back...

Restores defaced images from the copies kept in the project's `.bidsmgr/` folder or in `sourcedata/`, however many edits came afterwards, and takes the defacing record out of the sidecar.

More on all four: [Defacing and skull stripping](/guides/defacing/).

## Remove

### Delete...

Deletes recordings, datatypes or sessions, and with them the `*_scans.tsv` rows, the `IntendedFor` entries, the participants row of a subject left with no data, and any folder left empty, in one operation. It starts on the tree selection; the whole dataset is deliberately not one of its scopes. A copy of every deleted file is kept in the project's `.bidsmgr/` folder.

{{ figure("l11-delete", "Delete, for the eye-tracking folder.") }}
