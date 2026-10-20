---
title: The command line
chapter: 15
lede: Every step of the course has a command. Use them to convert on a server without a display, to repeat a conversion in a script, or to convert the project you curated in the GUI.
time: 15 minutes
sample: Multimodal sample v2
---

::: before
- A terminal where the `bidsmgr` commands work. With the installers, see [Install](/start/install/#commands) for how to reach them; with pip, uv or conda, activate the environment.
- The project `multimodal_study` from the course, curated and described (chapters 2 to 7).
:::

## The commands

| Command | What it does | In the GUI |
|---|---|---|
| `bidsmgr` | Opens the GUI | |
| `bidsmgr-create` | Creates a project | Home > Create a new dataset |
| `bidsmgr-adopt` | Makes an existing BIDS dataset a project | Home > Open dataset folder |
| `bidsmgr-project` | Lists a project's scan tables | Scan table, in the Converter |
| `bidsmgr-scan` | Scans raw data into a scan table (`inventory.tsv`) | Scan… |
| `bidsmgr-classify` | Names MRI series again from their acquisition parameters | Settings > Classification |
| `bidsmgr-rebuild` | Rebuilds the BIDS names of an edited `inventory.tsv` | Editing the table |
| `bidsmgr-convert` | Converts a scan table | Run conversion |
| `bidsmgr-metadata` | Writes the dataset's metadata and TODO placeholders | the post-convert chain |
| `bidsmgr-validate` | Validates a dataset | Validate dataset |
| `bidsmgr-deface` | Removes faces, or keeps the brain only | Tools > Deface |
| `bidsmgr-anonymise` | Anonymises the metadata | Tools > Anonymise metadata |
| `bidsmgr-qc` | Runs the quality check | Tools > Quality check |
| `bidsmgr-view` | Opens an image in the viewer, or renders it to a file | the viewer |

`--help` on any of them lists its options; every option is in [Command line](/reference/command-line/).

## Convert the course's project

The project keeps the scan table and every edit you made to it in the GUI, so the commands can pick up where the GUI left off. `--project` names the project folder.

::: step List the project's scan tables
```console
$ bidsmgr-project /tmp/studies/multimodal_study
Project: /tmp/studies/multimodal_study
  1 scan version(s); active = latest:
  * 0001__raw  [curating]  19 rows  source=raw  raw=/tmp/studies/BIDS_Manager_multimodal_sample_v2/raw
```
The table marked `*` is the one the other commands use, unless `--version` names another.
:::

::: step Convert it
```console
$ bidsmgr-convert --project /tmp/studies/multimodal_study -j 4
```
The conversion replays the edits recorded in the project (one subject, one session, the spectroscopy names) and the PET dose values saved with the scan table. The description and the participants file are written by the next step, `bidsmgr-metadata`. `-j 4` converts four series at a time. It took {{ m("cli.convert_seconds") }} seconds on the sample.
:::

::: step Write the metadata
```console
$ bidsmgr-metadata --project /tmp/studies/multimodal_study --fill-todos
  TODO placeholders inserted: 63 fields across 7 files
```
`--fill-todos` writes the TODO placeholders the GUI's default post-convert chain writes; `--fill-scope required|recommended|optional` chooses how far they go. The step also writes the scans and sessions tables (`--no-tables` leaves them out), and `--anonymise recommended` or `strict` anonymises the dataset last, as **Settings** > **Convert** does in the GUI.
:::

::: step Validate
```console
$ bidsmgr-validate /tmp/studies/multimodal_study --strict --html
=== /tmp/studies/multimodal_study ===
  severity: ERR  (ok=26 warn=114 err=3)
```
`--strict` runs the deep checks and `--html` writes `validation_report.html` into the project's `.bidsmgr/` folder. The result is the GUI's, file for file: the same {{ m("cli.project_convert_files") }} files, the same three errors (chapter 9 fixes them).
:::

::: note
Without `--fill-todos`, the same dataset reports {{ m("cli.without_fill_todos.err") }} errors instead of 3: the PET's `ReconMethodParameterLabels` is then missing rather than holding a TODO. A TODO in a required field is still a field to fill.
:::

## From raw data to BIDS in a script

For a study you convert the same way every time, the whole workflow can run without the GUI:

```console
$ bidsmgr-create /data/bids/my_study --name "My study"
$ bidsmgr-scan /data/raw/my_study --project /data/bids/my_study -j 8
$ bidsmgr-convert --project /data/bids/my_study -j 8 --pet-spreadsheet dose_sheet.csv
$ bidsmgr-metadata --project /data/bids/my_study --participants participants.csv --fill-todos --anonymise recommended
$ bidsmgr-validate /data/bids/my_study --strict --html
```

What the GUI lets you do between the scan and the conversion (reconcile subjects, rename a task, leave a series out), a script does with rules and in `inventory.tsv`. Three ways:

- **Scan rules** in a JSON file (`bidsmgr-scan --rules-file rules.json`): leave out series by name and give your own names to series, applied at every scan. **Settings** > **Scan rules** keeps rules of the same form in BIDS Manager's own settings, but cannot save them to a file; write the JSON by hand (`bidsmgr-scan --help` shows its form).
- **Leave entities out of every name** with `bidsmgr-scan --drop-entity acq` (the same as **Settings** > **Scan** > **Leave out of proposed names**).
- **Edit `inventory.tsv`**, a tab-separated table, then run `bidsmgr-rebuild` to rebuild the names. The `entities` column holds every row's entities as JSON and is what the names are built from: edit it, and run `bidsmgr-rebuild inventory.tsv` (the default, `--from entities`).

::: warning
`bidsmgr-rebuild --from columns` rebuilds the entities from the `session`, `task` and `run` columns instead. In {{ version }}, a scan leaves those columns empty for DICOM rows, so rebuilding from columns removes their task and run: a BOLD run loses its task. Edit the `entities` column, or curate in the GUI. See [Known issues](/help/known-issues/).
:::

## Without a project

The commands also work on a free-standing `inventory.tsv` and output folder, which suits one-off conversions:

```console
$ bidsmgr-scan /data/raw/my_study inventory.tsv -j 8
$ bidsmgr-convert inventory.tsv /data/bids --raw-root /data/raw/my_study -j 8
$ bidsmgr-metadata /data/bids/my_study --fill-todos
$ bidsmgr-validate /data/bids/my_study
```

The dataset folder is named after the raw folder (in lower case) unless `bidsmgr-scan --dataset` names it. For a dataset converted elsewhere, `bidsmgr-metadata <dataset> --tables-only` writes its scans and sessions tables and nothing else. Without a project, nothing records your edits and there are no scan versions; for anything you will come back to, use a project.

## Viewing and checking from the command line

```console
$ bidsmgr-view sub-001/ses-01/anat/sub-001_ses-01_acq-tfl3p2_T1w.nii.gz --layout multi
$ bidsmgr-view T1w.nii.gz --render t1.png --planes axial coronal --height 400
$ bidsmgr-qc /tmp/studies/multimodal_study --datatype anat dwi -j 4
```

`--render` draws the image to a file without opening a window, which works on a server. **Save** > **Show the command line...** in the viewer writes the `bidsmgr-view` command that reproduces what is on screen.

::: recap
- You can convert a project you curated in the GUI, or run the whole workflow in a script.
- That is the course. For your own data, the [Guides](/guides/) go through each kind of recording on its own sample, and the [Reference](/reference/) lists every setting, column and option.
:::
