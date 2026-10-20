---
title: Files BIDS Manager writes
lede: What a project folder holds after a conversion, file by file: the dataset itself, and the .bidsmgr folder where BIDS Manager keeps its history, scan tables, logs and reports.
description: Every file and folder BIDS Manager writes into a dataset and its .bidsmgr folder.
---

## The dataset

| File or folder | Written by | What it is |
|---|---|---|
| `dataset_description.json` | creating the project; the conversion; the metadata step | The dataset's name, BIDS version, authors, licence, and what generated it. |
| `README`, `CHANGES` | creating the project (README); the metadata step (both) | A starting README to replace with a description of the dataset, and a change log. |
| `.bidsignore` | creating the project; the Editor's ignore list | Tells validators to ignore `.bidsmgr/` and the conversion's scratch folder, and the files you leave out of validation ([Leaving files out of validation](/guides/ignoring-files/)). |
| `participants.tsv`, `participants.json` | the metadata step | One row per subject, and the description of each column. |
| `sub-<label>/[ses-<label>/]<datatype>/` | the conversion | The recordings, each with its sidecar and companion files. |
| `sub-<label>/[ses-<label>/]sub-<label>[_ses-<label>]_scans.tsv` | the metadata step; **Tools** > **Scans and sessions tables...** | Each recording of the session, of every datatype the standard defines, with its acquisition date and time (`n/a` when not known). |
| `sub-<label>/sub-<label>_sessions.tsv` | the same, for a subject with sessions | Each session of the subject with when it began. |
| `task-<label>_bold.json` and other sidecars at the top | **Tools** > **Fix ups...** > **Move shared fields up** | Sidecars shared by many files ([inheritance](/concepts/inheritance/)). |
| `phenotype/` | the metadata step, with a phenotype spreadsheet | Questionnaires and measures, one table per instrument. |
| `CITATION.cff` | **Tools** > **Fix ups...**; `bidsmgr-metadata --write-citation`; the post-conversion setting | How to cite the dataset, from its description. Optional. |
| `sourcedata/` | the conversion, when **Keep in sourcedata/** is on | The raw files of each subject, as they were or as one archive per series, with a `manifest.tsv` of checksums. |
| `derivatives/bidsmgr-qc/` | the quality check | Its results, per image, so they are not computed twice. |
| `derivatives/bidsmgr-skullstrip/` | **Tools** > **Remove the skull...** | Skull-stripped images, as a derivative dataset. |

## The .bidsmgr folder

BIDS Manager's own folder in the dataset. It is listed in `.bidsignore`, so validators skip it, and it is what makes scans resumable and every change traceable. Leave it out when you share the dataset ([Sharing a dataset](/learn/14-sharing/)).

```text
.bidsmgr/
├── project/
│   ├── meta.json                  the project: name, BIDS Manager and BIDS versions, creation time
│   ├── events.jsonl               what happened to the project, one event per line
│   ├── anonymise.json             the date shift of each participant and the secret behind the pseudonyms
│   └── scans/
│       └── 0001__raw/             one scan table
│           ├── inventory.tsv      the scan table, as last saved
│           ├── inventory.tsv.recording_meta.json   the dataset metadata you gave
│           ├── events.jsonl       every edit made to this table, for Undo
│           ├── version.json       where the raw data was, and the table's state
│           └── ...                the scan's caches (series files, features)
├── editor/
│   ├── operations.log             every change made in the Editor, one step per line
│   ├── redo.log                   the steps undone, for Redo
│   └── originals/                 the files as they were before each step
├── logs/                          one log per scan, conversion, metadata step and validation
├── provenance/                    per subject: what the conversion did, with which tools
├── errors/                        per subject, when its conversion failed: the reason
├── backup/                        files an update conversion replaced
├── merged/<source>/               the history of a subject merged into another
├── adopted_manifest.json          for an adopted dataset: every file as it was found
├── accepted_findings.json         validation findings you accepted
├── viz/scenes/                    viewer scenes you saved
├── metadata_report.json           what the metadata step filled, and every TODO it wrote
├── validation_report.json         the last validation's findings
└── validation_report.html         the same, as a page to read or send
```

During a conversion each subject is written into `.tmp_bidsmgr/sub-<label>/` in the dataset first, and moved into place only when it converted completely. The folder is removed afterwards; if you find one, a conversion was interrupted, and it can be deleted.

## Outside the dataset

| What | Where |
|---|---|
| Your settings and recent projects | your user account ([First launch](/start/first-launch/#where-bids-manager-keeps-things)) |
| Logs of commands run outside a project | `~/.bidsmgr/logs/` |
| A scan without a project | the scan table file you name, with its caches beside it (`inventory.tsv.files_by_uid.json.gz` and similar) |

BIDS Manager writes nothing into the raw folder you scan.
