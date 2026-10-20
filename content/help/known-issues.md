---
title: Known issues
lede: Problems in BIDS Manager {{ version }} that we know about, what you will see, and what to do until they are fixed. The pages of this site that meet one of them link here.
description: Known issues in the current BIDS Manager release, with workarounds.
---

Found something not listed here? [Report it](/help/reporting/).

## In the converted dataset

### participants.tsv holds names and patient IDs

**What you see.** After the metadata step (a conversion from the GUI, or `bidsmgr-metadata`), `participants.tsv` has the columns `given_name`, `family_name` and `patient_id`, copied from the DICOM headers. A converted MEG recording also keeps the participant's name and birthday, and the experimenter, in its header. Running the metadata step again after anonymising puts the three columns back.

**What to do.** Anonymise after the last metadata run: **Tools** > **Anonymise metadata...** removes the columns, their entries in `participants.json` and the names in recording headers ([Anonymising metadata](/guides/anonymising/)). Or turn on **Settings** > **Convert** > **Anonymise the metadata, last**, so every conversion ends with it. `.bidsmgr/` (scan tables, and the copies kept for Undo) and a `sourcedata/` copy are never changed: do not share them.

### A dose sheet's `none` is read as empty

**What you see.** A PET dose sheet that gives `none` for `ReconMethodParameterLabels` and `ReconMethodParameterUnits` (what BIDS asks for when a reconstruction has no parameters) does not fill them: the import takes fewer fields than the sheet has (7 of 9 on the samples), `ReconMethodParameterLabels` gets a TODO placeholder, and validation reports an error because `ReconMethodParameterUnits` is missing.

**What to do.** After converting, set both fields to `["none"]` in the PET sidecar: [Validating in the Editor](/learn/09-validating/#fix-the-errors) does it with the finding's **Fix** button.

### EEG and MEG names lose `acq` and `rec`, and `run-01` becomes `run-1`

**What you see.** MNE-BIDS is given only the subject, session, task and run of a recording, so an `acq-` or `rec-` entity set in the table is not in the converted name, and a run is written without its leading zeros. The metadata you set for that recording may then not reach its sidecar. The BIDS preview marks such rows.

**What to do.** Avoid `acq` and `rec` on EEG and MEG rows for now, and add them after converting with **Tools** > **Add or remove an entity...**; **Tools** > **Index widths...** gives runs their leading zero back.

### Files dcm2niix splits off keep dcm2niix's names

**What you see.** Some series are written as several files under dcm2niix's own endings (`_e1`, `_e2`, `_ph`, `_real`, `_fieldmaphz`, `_ADC`), which are not BIDS names; validation lists them as not part of the dataset. ASL series also miss fields no scanner records.

**What to do.** Rename or delete those files in the Editor, and fill the ASL fields in their sidecars.

### A series the scan cannot name is skipped quietly

**What you see.** A series that no step could name stays ticked with an empty name; the table marks it as an error, but the conversion leaves it out without a line in the Log.

**What to do.** Check the Overview before converting: it lists them. Name them in the table, or untick them.

### Fix ups proposes events files eye tracking may not have

**What you see.** **Generate missing companion files** (in **Settings** > **Convert**, off by default, and in **Tools** > **Fix ups...**, ticked) proposes one events file per eye, `..._recording-eye1_events.tsv` and `..._recording-eye2_events.tsv`. The standard does not allow `recording` on an events file, so validation reports both.

**What to do.** Untick them, or delete them. What eye tracking does need is the run's own events file in `beh/` with the screen described in its sidecar: [Validating in the Editor](/learn/09-validating/#fix-the-errors) writes it.

### The eye-tracking error shows its template

The validation message for an eye-tracking recording whose events file lacks `StimulusPresentation` reads "... the events file associated with {path} ({associations.events.path}) must have ...", with the braces unfilled. The file it is about is the one the finding is listed under.

### Smaller things in the output

- `dataset_description.json` > `GeneratedBy` > `Container` > `Tag` holds dcm2niix's usage line rather than a version.
- A scans table written by 1.5.0 keeps a PET time without a date, because existing values are kept; type the date in front of it, or `n/a`.

## In the Editor

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

The tooltip of **Settings** > **Convert** > **Write an HTML validation report** says it is written beside the dataset; it is written to `.bidsmgr/validation_report.html` inside it.

### At a large font size in a small window

At font scale **Comfortable (1.15x)** or larger, in a window narrower than about 1600 pixels, the Converter's panels reach their minimum widths and **Properties** cuts its fields short; some message boxes cut their buttons' text. Fold the side panels you are not using, make the window wider, or use a smaller font scale.

### The image viewer's shortcut list misses two keys

The list under the keyboard icon (or {{ key("F1") }}) of the image and spectrum viewers does not show **Advanced controls** ({{ key("Ctrl+I") }}) and **Save a screenshot...** ({{ key("Ctrl+Shift+S") }}), which work. [Viewers](/reference/viewers/) lists every key.

## On some systems

### Python 3.14: no defacing

niimath has no package for Python 3.14 yet. BIDS Manager installs and runs; **Deface** is greyed out with a tooltip saying why, and the quality check uses its own faster, less precise methods for the brain mask, the tissue classes and the registration. Use Python 3.10 to 3.13, or the installers, which use 3.10.

### Windows: EyeLink files need a Microsoft runtime

Reading EyeLink `.edf` files directly needs the Microsoft Visual C++ 2008 runtime, which installing needs an administrator. The Windows installer checks and says so at its end; it does not install it. Without it, an `.asc` export of the recording (SR Research's `edf2asc`, or EyeLink Data Viewer) is read instead. The same fallback applies on ARM64 Linux, where the EDF reader is not available.
