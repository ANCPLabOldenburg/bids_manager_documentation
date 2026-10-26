---
title: Anonymising metadata
display_title: Anonymising *metadata*
kicker: Guides
group: Curating a dataset
lede: Remove what identifies a participant from every kind of file a dataset holds, sidecars, tables, recording headers and photographs, choosing what by purpose and where by subject and session, and read every change before it is written.
description: Anonymise a BIDS dataset's metadata with BIDS Manager: presets, categories, scope, dates shifted with their intervals kept, undo, and the command line.
time: 20 minutes
sample: Multimodal sample v3
---

::: before
- A converted dataset open in the Editor. The tutorial uses the course's sample in the state chapter 10 leaves it; the case on sessions uses MRI sample 1, which has two subjects.
- Anonymising changes metadata only. Faces are removed from the images with [Defacing](/guides/defacing/), and the recorded data (the image, the signal) are never changed.
:::

## What the converter leaves, and why it matters

A conversion writes what the scanner and the recording system wrote, and much of it can identify someone without being a name: the day of the scan, the time a recording started, the serial number of the scanner, the address of the site, a DICOM UID built from the scanner's number and the second it was made, the name of the person who ran a MEG session, the time stamp inside every compressed file. The conversion already leaves the participant's name, birth date, weight and height out of the sidecars ([Identifiers and privacy](/concepts/identifiers-and-privacy/)); what follows is the rest.

On the course's sample, the Recommended preset finds 128 changes in 32 files, among them:

| Where | What | Becomes |
|---|---|---|
| `participants.tsv` | `given_name`, `family_name`, `patient_id` | columns removed, with their entries in `participants.json` |
| `sub-001_ses-01_scans.tsv` | `acq_time` of the T1w, `2023-09-14T10:25:20.255000` | the same time of day on a day in 1902 to 1925, the same weekday |
| the FLAIR's sidecar | `DeviceSerialNumber` `"66080"`, `StationName` `"AWP66080"` | `device-...`, `station-...` |
| the FLAIR's sidecar | `StudyInstanceUID` `1.3.12.2.1107.5.2.43.66080...` | `2.25....` |
| the FLAIR's sidecar | `InstitutionAddress` | `"n/a"` |
| the MEG recording's header | the participant's name, the experimenter `Meg User (meg)`, the measurement date | removed; the date shifted |
| the EEG recording's EDF header | `Startdate 12-AUG-2009 X X BCI2000` | `Startdate X X X X`, and the start date written as `01.01.85`, the date EDF reserves for an anonymised recording |
| every `.tsv.gz` | the gzip header's time stamp and original file name | removed |

## Anonymise the course's sample

::: step Open Anonymise metadata
In the Editor choose **Tools** > **Anonymise metadata...**. The tree's right-click offers the same under **Identifiable data**, for what was clicked: a subject, a session, or the dataset.

{{ figure("g-anon-menu", "The tree's right-click on a subject: Anonymise metadata..., under Identifiable data, for this subject only.") }}

The dialog reads the dataset and lists every change before anything is written:

{{ figure("g-anon-dialog", "Anonymise metadata: What on the left, by purpose; Where below it; What changes on the right, by kind.") }}
:::

::: step Choose what: a preset, then categories
**What** groups eight categories by purpose: the participants, when it happened, the site and its equipment, traces in files. Each card says what it removes, has its own options, and shows how many changes it makes in this dataset.

**Recommended** keeps what analyses need: times of day, the site's name, exact ages up to 89. **Strict** keeps as little as still makes a valid dataset. Changing any card makes the choice **Custom**.

| Category | Recommended | Strict |
|---|---|---|
| Names and IDs: names, IDs, birth dates, contact details, the scanner's copy of sex, age, weight and height, the people who ran the session | removed | removed |
| Ages in `participants.tsv` | over 89 as 89 | five-year bins, and capped at 89 |
| Dates and times | dates moved back by one number of whole weeks per participant, times of day kept | the same, times set to midnight and the scanner's own time fields removed |
| The site | the address written as `n/a` | the name, department and address written as `n/a` |
| Devices: serial numbers, station names | pseudonyms, the same for the same machine everywhere | the same |
| DICOM UIDs | pseudonyms (`2.25....`), the same for the same UID everywhere | the same |
| Traces of the conversion: gzip headers, paths on the converting machine | removed | removed |
| Photographs: EXIF and text metadata | removed, pixels untouched | removed |

{{ figure("g-anon-strict", "Strict on the same dataset: more changes, because times go to midnight, the site's name goes too, and the age is binned.") }}
:::

::: step Choose where
**Where** lists the dataset's files at the top (`participants.tsv` and the like) and every subject with its sessions, each with how many files it holds. Untick what should stay as it is. A table that lists participants or sessions is changed only in the rows of those ticked.
:::

::: step Read the changes
**What changes** counts the changes, the files, the values to read by hand, and what cannot be changed here. Four views:

- **By kind**: every change under its category, with the value before and after, and the file.
- **By file**: every file and what changes in it.
- **To read by hand**: free text that may name someone and that no rule can judge, such as a protocol name or a study description. It is listed once per value, with the files it is in, and nothing in it is changed: open the files and edit them if they do name someone.
- **Not changed here**: what a format, or the folder it is in, does not let BIDS Manager rewrite.

{{ figure("g-anon-review", "To read by hand on the course's sample: protocol names, series descriptions and the study description, each with the files it is in.") }}

Search with **Find a field, a value or a file**.
:::

::: step Leave a file out if needed
In **By file**, select a file and press {{ key("Space") }}, or right-click it, to leave it out of this run. The counts follow.

{{ figure("g-anon-file", "By file: each file the run would rewrite.") }}
:::

::: step Anonymise
Click **Anonymise N files** and confirm. The whole run is one step of the Editor's history: **Undo** takes it back and **Redo** makes it again ([Undo, redo and the history](/guides/history/)). Each sidecar records what was done in `DeidentificationMethod`.

**Then delete the copies the Editor keeps for Undo** does what it says once the run is written: those copies are the identifiable originals, and a dataset shared or backed up with its `.bidsmgr/` folder still holds them. Ticked, nothing done before can be undone afterwards.
:::

::: step Check
Validate the dataset: anonymising keeps it valid. Open `participants.tsv` and a sidecar to see the result, and read **To read by hand** once more for anything a rule cannot catch.
:::

## How dates are moved

Every date of one participant moves back by the same number of whole weeks, chosen at random so that it lands in 1902 to 1925, the years the standard reserves for shifted dates. Because the number is the participant's own and is in whole weeks:

- the intervals between their sessions, and between their recordings in a session, stay exact;
- the weekday stays, which matters for designs where it does;
- another participant's dates move by another number, so two participants scanned the same day no longer look so.

One exception: the start date in an EDF header, which the format writes with a two-digit year, is set to `01.01.85`, the date the EDF specification reserves for an anonymised recording. The recording's `acq_time` in the scans table moves like the participant's other dates.

The numbers and the secret behind the pseudonyms are kept in `.bidsmgr/project/anonymise.json`, so a participant anonymised now and again later (a session converted next month) moves by the same number. Keep that file private: with it, the shift can be undone by anyone.

## Cases

### Share a whole dataset

Recommended, the whole dataset, and read **To read by hand**. Then validate, and share without `.bidsmgr/` and without `sourcedata/`, which are never changed.

### Publish openly

Strict: times of day go to midnight, the site's name goes, and ages fall into five-year bins. If an analysis needs the time of day (circadian effects, a scan before or after lunch), choose **Custom** and set **Dates and times** back to **Keep times of day**: everything else stays strict.

### Keep the real dates

For a dataset that stays inside your institution but goes to a colleague without the right to see names: untick **Dates and times**. Names, IDs, UIDs and devices are still handled.

### One subject, or one session, at a time

Right-click a subject or a session in the tree, then **Identifiable data** > **Anonymise metadata...**: **Where** opens with what was clicked. On MRI sample 1, the second session of the first subject alone:

{{ figure("g-anon-scope", "Where, on a dataset of two subjects: only ses-post of sub-001 and its row of the dataset's files. Its dates move by the number that sub-001's ses-pre will move by later.") }}

In a partial run, the identity columns of `participants.tsv` are written as `n/a` for the participants in the scope rather than removed, because the others still have values in them.

### Anonymise during the conversion

**Settings** > **Convert** > **Anonymise the metadata, last** (Off, Recommended or Strict) makes it the last step after every conversion, after the metadata step that writes `participants.tsv`.

{{ figure("l08-settings-chain", "Settings, Convert page: the post-convert chain, with Anonymise the metadata, last.") }}

Running the metadata step again on its own puts the name columns back into `participants.tsv`: anonymise after the last metadata run ([Known issues](/help/known-issues/#participants-tsv-holds-names-and-patient-ids)).

### From a script

```console
$ bidsmgr-anonymise /data/my_study --dry-run          # list every change, write nothing
$ bidsmgr-anonymise /data/my_study                    # Recommended, the whole dataset
$ bidsmgr-anonymise /data/my_study --preset strict --keep dates
$ bidsmgr-anonymise /data/my_study --participant-label 001 --session post
$ bidsmgr-convert inventory.tsv /data --anonymise recommended
$ bidsmgr-metadata /data/my_study --anonymise strict
```

`--keep` takes the categories to leave alone (`identity`, `ages`, `dates`, `site`, `devices`, `uids`, `traces`, `photos`); `--skip-dataset-files` leaves the files at the top alone; `--json` prints the plan for a script. A `--dry-run` remembers the date shifts it chose, so the real run makes exactly the changes it listed. Every option is in [Command line](/reference/command-line/).

## What anonymising does not do

- It does not remove faces: [Defacing](/guides/defacing/).
- It does not change the recorded data, and it does not judge free text: read **To read by hand**.
- It does not touch `.bidsmgr/` or `sourcedata/`: do not share them.
- It does not make a dataset anonymous in law. Whether a dataset may be shared, and how, is for your ethics approval and your data protection officer to say.
