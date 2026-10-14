---
title: Known issues
lede: Problems in BIDS Manager {{ version }} that we know about, what you will see, and what to do until they are fixed. The pages of this site that meet one of them link here.
description: Known issues in the current BIDS Manager release, with workarounds.
---

Found something not listed here? [Report it](/help/reporting/).

## In the converted dataset

### The PET row of a scans table has a time without a date

**What you see.** Validation reports one error in the session's `_scans.tsv`: the PET row's `acq_time` is a time such as `09:28:23.000000`, without a date. It happens with scanners whose PET header records an acquisition time but no acquisition date (the multimodal and PET samples' GE Advance).

**What to do.** Open the scans table in the Editor and type the date in front of the time, from the study date (`2009-10-02T09:28:23` on the samples), or `n/a`. [Validating in the Editor](/learn/09-validating/#fix-the-error) shows it step by step.

### participants.tsv holds names and patient IDs

**What you see.** After a conversion from the GUI, `participants.tsv` has the columns `given_name`, `family_name` and `patient_id`, copied from the DICOM headers. The sidecars and spectroscopy headers have had these removed; the scan tables in `.bidsmgr/`, and a `sourcedata/` copy if you keep one, still hold them.

**What to do.** Delete the three columns (and their entries in `participants.json`) before sharing, as in [Sharing a dataset](/learn/14-sharing/#what-is-left-participants-tsv).

### A dose sheet's `none` is read as empty

**What you see.** A PET dose sheet that gives `none` for `ReconMethodParameterLabels` and `ReconMethodParameterUnits` (what BIDS asks for when a reconstruction has no parameters) does not fill them: the import says it took fewer fields than the sheet has, and the sidecar gets a TODO placeholder, or nothing if placeholders are off.

**What to do.** After converting, set both fields to `["none"]` in the PET sidecar ([Editing metadata](/learn/10-editing-metadata/)).

### EEG and MEG names lose `acq` and `rec`, and `run-01` becomes `run-1`

**What you see.** MNE-BIDS is given only the subject, session, task and run of a recording, so an `acq-` or `rec-` entity set in the table is not in the converted name, and a run is written without its leading zeros. The metadata you set for that recording may then not reach its sidecar. The BIDS preview marks such rows.

**What to do.** Avoid `acq` and `rec` on EEG and MEG rows for now, and add them after converting with **Tools** > **Add or remove an entity...**; **Tools** > **Index widths...** gives runs their leading zero back.

### Files dcm2niix splits off keep dcm2niix's names

**What you see.** Some series are written as several files under dcm2niix's own endings (`_e1`, `_e2`, `_ph`, `_real`, `_fieldmaphz`, `_ADC`), which are not BIDS names; validation lists them as not part of the dataset. ASL series also miss fields no scanner records.

**What to do.** Rename or delete those files in the Editor, and fill the ASL fields in their sidecars.

### A series the scan cannot name is skipped quietly

**What you see.** A series that no step could name stays ticked with an empty name; the table marks it as an error, but the conversion leaves it out without a line in the Log.

**What to do.** Check the Overview before converting: it lists them. Name them in the table, or untick them.

### Smaller things in the output

- An eye tracker's physiological events get an `events.tsv` stub from **Generate missing companion files**; delete it.
- Scans tables list the `.bval` and `.bvec` files of a diffusion run as well as its image; delete those rows if a tool complains.
- `dataset_description.json` > `GeneratedBy` > `Container` > `Tag` holds dcm2niix's usage line rather than a version.

## In the Editor

### An operation cannot be undone from the GUI

**What you see.** The Editor records every operation (a rename, a restructure, a deletion, a fix applied to many files, a saved file) with the files as they were, and several of its dialogs say the change can be undone. **Undo** in the toolbar, however, only steps back through the edits of the sidecar or table that is open. A defacing can be taken back with **Tools** > **Put the face back...**; other operations cannot be undone from the GUI.

**What to do.** Read each tool's preview before applying it. To restore a file by hand, find the operation in `.bidsmgr/editor/operations.log` and copy the file back from `.bidsmgr/editor/originals/<operation>/` ([The project folder and undo](/concepts/project-folder/)).

### Check coherence offers to delete a MEG coordinate file

**What you see.** **Check coherence** lists the `..._coordsystem.json` of a MEG or EEG recording as a sidecar with no recording, ticked for deletion. It is a required file of a MEG dataset.

**What to do.** Untick it before clicking **Repair**.

### The Whole dataset view never shows its summary

The summary line of the Validation panel's **Whole dataset** view ("N findings in M kinds") is not shown. The list below it is complete.

## In the table and the commands

### `bidsmgr-rebuild --from columns` drops a DICOM row's task and run

**What you see.** After editing `inventory.tsv` in a spreadsheet and rebuilding from the columns, a BOLD run loses its task (an invalid name) and repeated series lose their run numbers. The scan keeps a DICOM row's task and run only in the `entities` column.

**What to do.** Rebuild from the entities, the default: `bidsmgr-rebuild inventory.tsv`. Edit the `entities` column, or curate in the GUI.

### A hand-edited subject must be changed in two columns

**What you see.** In an `inventory.tsv` edited outside BIDS Manager, changing the subject in `entities` but not in `participant_id` (or the reverse) converts files named for one subject into the other subject's folder, without a warning. The GUI always changes both.

**What to do.** Change both columns together, or edit in the GUI.

### An entity value that breaks the standard is only a warning

**What you see.** A value such as `run-a`, or a session with a space, is accepted in the table; the row is marked as a warning, and the name carries the bad value.

**What to do.** Read the **issues** of every row marked as a warning before converting.

## In the GUI

### The finished message counts failed subjects wrong

When subjects fail, the message at the end of a conversion says "1 subject(s) failed" whatever the number. The Log and `.bidsmgr/errors/` have the full list.

### The HTML validation report is in `.bidsmgr/`

**Settings** > **Convert** says the HTML report is written beside the dataset; it is written to `.bidsmgr/validation_report.html` inside it.

### At a large font size in a small window

At font scale **Comfortable (1.15x)** or larger, in a window narrower than about 1600 pixels, the Converter's panels reach their minimum widths and **Properties** cuts its fields short; some message boxes cut their buttons' text. Fold the side panels you are not using, make the window wider, or use a smaller font scale.

### The image viewer's shortcut list misses three keys

The list under the keyboard icon (or {{ key("F1") }}) of the image and spectrum viewers does not show **Advanced controls** ({{ key("Ctrl+I") }}), **Save a screenshot...** ({{ key("Ctrl+Shift+S") }}) and **Restore every viewer default...**, which work. [Viewers](/reference/viewers/) lists every key.

## On some systems

### Python 3.14: no defacing

niimath has no package for Python 3.14 yet. BIDS Manager installs and runs; **Deface** is greyed out with a tooltip saying why, and the quality check uses its own faster, less precise methods for the brain mask, the tissue classes and the registration. Use Python 3.10 to 3.13, or the installers, which use 3.10.

### Windows: EyeLink files need a Microsoft runtime

Reading EyeLink `.edf` files directly needs the Microsoft Visual C++ 2008 runtime. The Windows installer adds it; with pip, uv or conda, install it yourself ([Install](/start/install/)). Without it, an `.asc` export of the recording (SR Research's `edf2asc`) is read instead.
