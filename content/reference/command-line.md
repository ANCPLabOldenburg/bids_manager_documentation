---
title: Command line
lede: Every command and every option, generated from BIDS Manager {{ version }} itself. For how they fit together, see the course's chapter on the command line.
description: Every BIDS Manager command and option.
---

The commands are installed with BIDS Manager. With the installers, activate its environment first ([Install](/start/install/#commands)); with pip, uv or conda, activate yours. `--help` after any command prints the same list as below. How to use them together, on the course's sample: [The command line](/learn/15-command-line/).

## Options several commands share

| Option | On | What it does |
|---|---|---|
| `--project DATASET` | scan, convert, metadata | Works on a project: the scan is saved as a new scan table of it, the conversion builds its active scan table into it, the metadata step reads both from it. |
| `--version ID` | convert, metadata | Uses this scan table of the project instead of the active one (`bidsmgr-project` lists them). |
| `-j N` | scan, convert, qc | How many files are read, series converted or images checked at the same time. |
| `--log-file PATH`, `--no-log-file` | scan, convert, metadata, validate | Where the log of the run is written; by default `<dataset>/.bidsmgr/logs/`, or `~/.bidsmgr/logs/` outside a dataset. |


## bidsmgr {#bidsmgr}

Opens the GUI.

{{ ref.usage("bidsmgr") }}

{{ ref.cli("bidsmgr") }}

## bidsmgr-create {#bidsmgr-create}

Creates a project: a new BIDS dataset folder with `dataset_description.json`, `README` and `.bidsignore`, and the project's `.bidsmgr/` folder. Given an existing BIDS folder, it adds whichever of these are missing and the `.bidsmgr/` folder. To take over a dataset without changing its files, use `bidsmgr-adopt`.

```console
$ bidsmgr-create /data/bids/my_study --name "My study"
```

{{ ref.usage("bidsmgr-create") }}

{{ ref.cli("bidsmgr-create") }}

## bidsmgr-adopt {#bidsmgr-adopt}

Makes an existing BIDS dataset a project, so the changes you make to it are recorded with the files as they were. Its files are left as they are; only in a git repository is `.bidsmgr/` added to `.gitignore`.

```console
$ bidsmgr-adopt /data/bids/ds000117
```

{{ ref.usage("bidsmgr-adopt") }}

{{ ref.cli("bidsmgr-adopt") }}

## bidsmgr-project {#bidsmgr-project}

Lists a project's scan tables. The active one, marked `*`, is what `--project` uses in the other commands unless `--version` names another.

```console
$ bidsmgr-project /data/bids/my_study
```

{{ ref.usage("bidsmgr-project") }}

{{ ref.cli("bidsmgr-project") }}

## bidsmgr-scan {#bidsmgr-scan}

Scans a raw folder into a scan table (`inventory.tsv`): one row per recording, with its proposed BIDS name. With `--project`, it is saved as a new scan table of the project.

```console
$ bidsmgr-scan /data/raw/my_study --project /data/bids/my_study -j 8
```

{{ ref.usage("bidsmgr-scan") }}

{{ ref.cli("bidsmgr-scan") }}

## bidsmgr-classify {#bidsmgr-classify}

Names the MRI series of a scan table again from their acquisition parameters, using the features the scan cached (no DICOM is read), and says why. Use it to try classifier settings on a table.

```console
$ bidsmgr-classify inventory.tsv --config classifier.json --json
```

{{ ref.usage("bidsmgr-classify") }}

{{ ref.cli("bidsmgr-classify") }}

## bidsmgr-rebuild {#bidsmgr-rebuild}

Rebuilds the BIDS names of `inventory.tsv` after you edited it in a spreadsheet. The `entities` column is the source of the names.

```console
$ bidsmgr-rebuild inventory.tsv --dry-run
```

{{ ref.usage("bidsmgr-rebuild") }}

{{ ref.cli("bidsmgr-rebuild") }}

## bidsmgr-convert {#bidsmgr-convert}

Converts `inventory.tsv`, or a project's active scan table, into the BIDS dataset.

```console
$ bidsmgr-convert --project /data/bids/my_study -j 8
```

{{ ref.usage("bidsmgr-convert") }}

{{ ref.cli("bidsmgr-convert") }}

## bidsmgr-metadata {#bidsmgr-metadata}

Writes the dataset's metadata after a conversion: `participants.tsv`, the `_scans.tsv` tables, the fields that can be derived, and, with `--fill-todos` or `--fill-scope`, TODO placeholders for what is still missing.

```console
$ bidsmgr-metadata --project /data/bids/my_study --fill-todos
```

{{ ref.usage("bidsmgr-metadata") }}

{{ ref.cli("bidsmgr-metadata") }}

## bidsmgr-validate {#bidsmgr-validate}

Validates a dataset against the BIDS standard.

```console
$ bidsmgr-validate /data/bids/my_study --strict --html
```

{{ ref.usage("bidsmgr-validate") }}

{{ ref.cli("bidsmgr-validate") }}

## bidsmgr-deface {#bidsmgr-deface}

Removes the face from anatomical images, or keeps the brain only.

```console
$ bidsmgr-deface /data/bids/my_study
```

{{ ref.usage("bidsmgr-deface") }}

{{ ref.cli("bidsmgr-deface") }}

## bidsmgr-anonymise {#bidsmgr-anonymise}

Anonymises a dataset's metadata, as **Tools** > **Anonymise metadata...** does ([Anonymising metadata](/guides/anonymising/)). `--dry-run` lists every change and writes nothing.

```console
$ bidsmgr-anonymise /data/bids/my_study --dry-run
$ bidsmgr-anonymise /data/bids/my_study --preset strict --keep dates
```

{{ ref.usage("bidsmgr-anonymise") }}

{{ ref.cli("bidsmgr-anonymise") }}

## bidsmgr-qc {#bidsmgr-qc}

Runs the fast quality check of anatomical and diffusion images and writes the results to `derivatives/bidsmgr-qc/`.

```console
$ bidsmgr-qc /data/bids/my_study --datatype anat dwi -j 4
```

{{ ref.usage("bidsmgr-qc") }}

{{ ref.cli("bidsmgr-qc") }}

## bidsmgr-view {#bidsmgr-view}

Opens an image in the viewer, or renders it to a picture file without a window.

```console
$ bidsmgr-view T1w.nii.gz --render t1.png
```

{{ ref.usage("bidsmgr-view") }}

{{ ref.cli("bidsmgr-view") }}
