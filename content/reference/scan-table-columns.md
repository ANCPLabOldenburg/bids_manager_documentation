---
title: Scan table columns
lede: What each column of the scan table holds, in the Table view and in the tab-separated file a scan writes, `inventory.tsv`.
description: Every column of the BIDS Manager scan table and of inventory.tsv.
---

The scan table is one table with one row per recording. The Converter shows it in the Table view; a scan from the command line writes it as a tab-separated file you name (the GUI calls it `inventory.tsv`), and a project keeps it in `.bidsmgr/project/scans/<scan>/inventory.tsv`. The two are the same table: the Table view shows a selection of the file's columns, some under shorter names.

Three words mean three things in the scan table, as in BIDS: the **modality** is how the data was acquired (`mri`, `eeg`, `meg`, `pet`), the **datatype** is the folder it lands in (`anat`, `func`, `eeg`), and the **suffix** is what the recording is (`T1w`, `bold`, `eeg`).

## In the Table view

**Manage columns...** under the table shows, hides and reorders these; the columns marked **Always** cannot be hidden. **Editable** columns can be changed in the table, in **Properties** or with **Bulk edit...**. The descriptions are the ones **Manage columns** shows. Where the file names a column differently, its name in the file is written beneath it.

{{ ref.table("columns", [["header", "Column"], ["editable", "Editable"], ["shown", "Shown at first"], ["description", "What it holds"]], under={"header": "tsv"}) }}

## Only in the file

These columns are in `inventory.tsv` but not in the table. They are what BIDS Manager uses behind the scenes, and what a script can read.

| Column | What it holds |
|---|---|
| `subject` | The subject as found in the source: for DICOM the given name in the header's patient name, for EEG and MEG the label found in the path. The BIDS label is in `participant_id`. |
| `entities` | Every entity of the row as JSON, such as `{"subject": "001", "session": "01", "task": "rest"}`. **The BIDS name is built from this column**: edit it, then run `bidsmgr-rebuild`. |
| `bids_path` | Where the row goes inside its subject folder: the datatype folder and file name for DICOM rows, the base name for other rows and after `bidsmgr-rebuild`. |
| `series_uid`, `study_instance_uid` | The DICOM series and study identifiers. |
| `rep` | The repeat number when the same series was acquired more than once. |
| `study_time` | The time of the study, from the header. |
| `bids_guess_classifier`, `bids_guess_datatype`, `bids_guess_entities`, `bids_guess_skip` | Which classifier named the row, and what it proposed. `bids_guess_skip` is true for a row it decided not to convert. |
| `classification_confidence`, `classification_alternatives`, `classification_evidence` | The parameter classifier's confidence, the other names it considered, and the evidence for its choice. **Why this name** in **Properties** shows them. |
| `fieldmap_targets` | The runs a fieldmap row corrects, when you chose them in **Properties**. |
| `probe_n_files`, `probe_extensions` | What a probe conversion wrote for the row (**Settings** > **Scan**). |
| `tracer_suggestion`, `radionuclide_suggestion`, `recon_method_suggestion`, `recon_filter_suggestion`, `injected_dose_suggestion` | PET values read from the header, offered in the dataset metadata and in **Properties**. A suggestion is never written unless you take it. |
| `montage_suggestion`, `manufacturer_suggestion` | For EEG and MEG, the montage whose channel names match best, and the manufacturer from the header or the file format. Suggestions too. |
| `n_times`, `recording_time`, `has_positions` | For EEG and MEG: the number of samples, the start of the recording, and whether the file holds sensor positions. |

Columns whose names start with `_` are kept for BIDS Manager's own use inside a project and are not written by `bidsmgr-scan`.

## Editing the file

A spreadsheet program can edit `inventory.tsv`, as long as it saves it as tab-separated text. Change the `entities` column (the session, the task, the run), the `include` column (`1` or `0`), or the `datatype` and suffix, then run:

```console
$ bidsmgr-rebuild inventory.tsv
```

`bidsmgr-convert` rebuilds the names itself before converting, so a table you edited and did not rebuild still converts under the names its entities say. Change `participant_id` and `entities` together: see [Known issues](/help/known-issues/).

An `inventory.tsv` written by BIDS Manager before 1.4.1 uses older column names and cannot be read; scan the raw data again.
