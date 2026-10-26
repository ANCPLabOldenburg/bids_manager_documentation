---
title: Troubleshooting
lede: What to do when something does not work, by what you see. If your problem is not here, look at Known issues, then report it.
description: Solutions to common BIDS Manager problems, by symptom.
---

Most answers start with the log. The Converter's **Log** shows the current run; its history icon lists the logs of earlier runs (the newest 200), kept in the project's `.bidsmgr/logs/`. A subject whose conversion failed has its reason in `.bidsmgr/errors/`. Started from a terminal, `bidsmgr -v` (or `-vv`) prints more.

## Installing and starting

| What you see | What to do |
|---|---|
| The macOS installer does nothing when double-clicked | Gatekeeper blocked it: **System Settings** > **Privacy & Security** > **Open Anyway**, or run it from Terminal ([Install](/start/install/)). |
| Windows says it protected your PC | **More info**, then **Run anyway**. |
| `pip` finds no version of bids-manager | Your Python is older than 3.10 or newer than 3.14. |
| On Linux, BIDS Manager does not open and the terminal mentions the `xcb` plugin | Install `libxcb-cursor0` (Debian, Ubuntu) or `xcb-util-cursor` (Fedora). |
| The first start is slow | Python compiles BIDS Manager the first time it runs. Later starts are faster. |
| **Deface** is greyed out | You are on Python 3.14, for which niimath has no package yet. |

## Scanning

| What you see | What to do |
|---|---|
| The Converter's controls are off | Open or create a project on Home first: the Converter works inside a project. |
| A recording is missing from the table | BIDS Manager decides from the contents, not the names, so a file it cannot read is not a row. EEG and MEG files are read with MNE, in the formats listed in [What data can it convert?](/help/faq/#what-data-can-it-convert); export anything else to EDF or BrainVision first. A BrainVision recording needs its `.vhdr`, `.vmrk` and `.eeg` together. |
| One participant appears as several subjects | Expected when the sources name them differently. Set the subject with **Bulk edit...** ([The scan table](/learn/04-scan-table/)). |
| A row is unticked and I did not do it | The scan left it out on purpose; hover the row, or show the **issues** column with **Manage columns…**, to read why (a scout, a report, a computed map, a duplicate). Such a row stays out even if you tick it. |
| **Raw input** says **Moved** | The raw data is no longer where it was scanned. Click **Locate...** and choose its new place. |
| The scan is slow | A network drive is read file by file; copy the data to a local disk first. **Settings** > **Scan** > **Parallel workers** reads several files at once. |

## Converting

| What you see | What to do |
|---|---|
| The conversion refuses to start, naming two rows | Two rows would get the same file name. Give one of them a `run`, an `acq`, or untick it. |
| The finished message says subjects failed | The reason for each is in `.bidsmgr/errors/` and in the Log. The other subjects converted. |
| A subject that exists already was not converted again | **Existing subjects** is set to skip, the default. Choose update or replace in **Settings** > **Convert** to convert it again. |
| The conversion refuses to keep source data | The disk cannot hold the copies. Free space, or choose one archive per series, or turn **Keep in sourcedata/** off. |
| On Windows, a spectroscopy series fails | BIDS Manager brings a build of dcm2niix that can convert it, and uses it on its own. If it still fails, report it with the log. |
| On Windows, data or a project on a network drive does not convert | Update to 1.5.2 or later: files are copied where Windows will not follow a link on a share, and a drive letter is kept as you wrote it. If the Log says the drive is not connected, connect it (or open the folder through its network path) and run the conversion again. |
| A run's physiology shows one ECG column or a flat trigger | It was converted before 1.5.2. Delete the run's `_physio` files in the Editor and run the conversion again ([Updates](/updates/#v152)). |

## Validating and editing

| What you see | What to do |
|---|---|
| Over a hundred warnings | Most are TODO placeholders for what the raw files don't capture ([Metadata levels and TODO placeholders](/concepts/metadata-levels/)). Filter by errors first. |
| A finding about a field I cannot see in the file | Findings about a recording's metadata are about its sidecar; **Fix** opens the sidecar at the field. |
| The tree does not show `.bidsignore` or `.bidsmgr` | Hidden files are hidden by default: **Settings** > **Display** > **Editor tree**. |
| The viewers are read only and the tools are off | The folder is open to view only. Open it as a project to edit it. |

## Viewing and checking

| What you see | What to do |
|---|---|
| There is no 3-D layout | The 3-D view needs OpenGL 3.3. On a remote desktop or a virtual machine it may not be available. |
| An EEG or MEG file shows only its header | Click **Load signal**: the data is read only when you ask. |
| The quality check says it used its own masks | brainchop or niimath could not run: on Python 3.14, or offline the first time (the brain models are downloaded once). The results are still computed, with less precise masks. |
| The quality check says the air was not measured | The image is defaced, skull-stripped or has a zeroed background: the air would say nothing about noise. |
