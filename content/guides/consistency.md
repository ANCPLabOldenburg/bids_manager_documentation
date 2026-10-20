---
title: Keeping a dataset consistent
display_title: Keeping a dataset *consistent*
kicker: Guides
group: Curating a dataset
lede: A dataset can be legal BIDS and still contradict itself, once a file has been renamed in the file manager, a table deleted or a field typed by hand. Four tools find and repair what no validator reports, each change listed before it is written.
description: Check coherence, scans and sessions tables, references and fix ups in BIDS Manager: what each finds, what it repairs, and when to use which.
time: 20 minutes
sample: Multimodal sample v2
---

::: before
- A converted dataset open in the Editor as a project. The figures use the course's sample after three changes made outside BIDS Manager, as happens in real projects: the T1w and its sidecar renamed in the file manager from `acq-tfl3p2` to `acq-mprage`, the subject's sessions table deleted, and the BOLD run's `TaskName` typed by hand as `resting state`.
:::

## Four tools, four questions

| Tool | It answers | Repairs |
|---|---|---|
| **Check coherence...** | Do the files still describe the same dataset? Tables against files, references against files, names against fields | each problem, the safe ones ticked |
| **Scans and sessions tables...** | Does every session list its recordings, with when, and every subject its sessions? | writes or completes the tables |
| **References (IntendedFor, Sources...)...** | Which file points at which? | you tick the targets |
| **Fix ups...** | Is the dataset ready to share, are companion files, a citation file, shared fields where they belong? | each section its own button |

All four are in **Tools** under **Check and repair**. Each writes its changes as one step of the history ([Undo, redo and the history](/guides/history/)), and validation runs again afterwards if the dataset was validated.

## Check coherence

::: step Run the check
Choose **Tools** > **Check coherence...**. The check runs at once, in the background, and lists what it found, grouped by kind:

{{ figure("g-coherence", "Check coherence on the changed sample: four problems, what would repair each, and the three repairs that lose nothing ticked.") }}
:::

::: step Read each problem
Select a line to read below what disagrees and what the repair would change. On the changed sample:

| What disagrees | Repair | Ticked |
|---|---|---|
| The scans table names `anat/sub-001_ses-01_acq-tfl3p2_T1w.nii.gz`, which is not there; `..._acq-mprage_T1w.nii.gz` is, with no row: the same recording, renamed outside the application | point the row at the new name, keeping its time | yes |
| `beh/sub-001_ses-01_task-rest_events.tsv` is a recording, and the scans table has no row for it | add the row | yes |
| `sub-001` has one session and no sessions table | create `sub-001_sessions.tsv` with 1 row | yes |
| `TaskName` is "resting state", which does not derive to the `task-rest` in the filename | set `TaskName` to "rest" | no: you decide |

A repair that loses nothing comes ticked; one that overwrites something you may have meant comes unticked, to tick after reading it. **Select safe ones**, **Select all** and **Select none** set the ticks at once. A problem with no repair is listed with the reason, so you know about it.
:::

::: step Repair
Click **Repair**. Then **Check again** to see the list empty.
:::

Among the other problems it finds: a scans or sessions row naming a file or session that is gone; a subject with no row in `participants.tsv`, or a row with no subject; an `IntendedFor` pointing at a missing file or into another subject; a `B0FieldSource` that names no fieldmap; a sidecar or a companion table with no recording; one entity written at two widths (`run-1` and `run-01`) or in two letter cases; subjects with sessions beside subjects without; and a `CITATION.cff` that disagrees with `dataset_description.json`. The full list is in [Editor tools](/reference/editor-tools/#check-coherence).

## Scans and sessions tables

A `*_scans.tsv` in each session lists its recordings with `acq_time`, when each was acquired; a `*_sessions.tsv` for each subject with sessions lists them with when each began. The standard makes both optional, but they are where a dataset says when: an analysis of the order of runs, or of the time between sessions, reads them.

**Tools** > **Scans and sessions tables...** works out every table the dataset should have:

{{ figure("g-tables", "Scans and sessions tables on the changed sample: the tables to write, and under each the rows it gains, keeps or loses.") }}

- **Every recording the standard defines** gets a row, converted here or not: anatomical, functional, diffusion, fieldmaps, PET, MEG, EEG, spectroscopy, physiological and eye-tracking recordings, behavioural events alone.
- **One row per recording**: the parts of one recording (the echoes of a multi-echo run, the magnitude and phase of a fieldmap, the splits of a long MEG file, a `.bval` beside its image) share a time and are not listed as separate scans when the standard says they are one.
- **`acq_time` is a full date and time**, from the sidecar's `AcquisitionDateTime`, else from the date and time the scan read, else `n/a`: never a time without a date.
- **What is there stays.** Rows, columns and values already in a table are kept and only what is missing is added. A row goes only when it names nothing, or names a part of a recording that has its own row; the reason is listed under it.

On the changed sample it would add a row for the renamed T1w and remove the row of its old name; **Check coherence** instead moves the old row to the new name, keeping any column you added: for files renamed outside, run it first. Tick the tables to write, and click **Write N tables**. A conversion writes them by itself while **Settings** > **Convert** > **Write scans and sessions tables** is on (the default); for a dataset converted elsewhere, this is how to add them. From the command line: `bidsmgr-metadata <dataset> --tables-only`.

## References

**Tools** > **References (IntendedFor, Sources...)...** shows the fields that point from one file to another: `IntendedFor` (the runs a fieldmap corrects), `AssociatedEmptyRoom` (an MEG recording's empty-room recording), `Sources` and `RawSources` (what a derivative was made from), `AnatomicalImage`. Pick a file on the left, tick what it should point at on the right; only what the standard allows appears in either list. The tree's right-click opens it on the file clicked.

{{ figure("l11-references", "References: the fieldmap and the runs its IntendedFor names.") }}

Use it to correct a fieldmap paired with the wrong runs, to link an MEG recording to its empty room after converting them separately, or to check what a derivative says it came from. Fieldmaps are linked at conversion ([Fieldmap links](/concepts/fieldmap-links/)); this is for what came later.

## Fix ups

**Tools** > **Fix ups...** gathers repairs BIDS Manager can make on its own, each section with its own button:

| Section | What it does |
|---|---|
| **Ready to share** | BIDS Manager's own checks for handing a dataset to someone else: authorship, a licence, a README long enough to read, CHANGES, the participants table, no TODO left, no validation errors; opinions about sharing, not rules of the standard |
| **Missing companion files** | the tables and sidecars the standard associates with a recording (an `events.tsv` beside a task recording, a `channels.tsv` beside an electrophysiology recording, a `.json` sidecar): read from the recording where possible, else written as a stub validation keeps reporting until it is filled in |
| **Citation file** | writes `CITATION.cff` from `dataset_description.json`, moving the authors there, as the standard asks |
| **Repeated metadata** | a field with the same value in every file of a group, moved once to the level above, where inheritance applies it to all ([Inheritance](/concepts/inheritance/)) |
| **Unanswered metadata** | writes `TODO` into the fields still missing, at the levels you choose, so they are visible in the files |

{{ figure("l09-fixups", "Fix ups on the converted sample.") }}

For eye tracking, **Missing companion files** proposes an events file per eye that the standard does not allow; untick them ([Known issues](/help/known-issues/#fix-ups-proposes-events-files-eye-tracking-may-not-have)).

## Which tool, when

| Situation | Tool |
|---|---|
| Files renamed or deleted in the file manager | Check coherence |
| A dataset converted elsewhere, or by an older BIDS Manager, without scans tables | Scans and sessions tables |
| A session added to a subject later | Scans and sessions tables: its row in the sessions table |
| A fieldmap that corrects the wrong runs | References |
| An MEG recording and its empty room converted apart | References |
| Before sharing | Fix ups > Ready to share, then Check coherence, then validation |
| The same `RepetitionTime` in forty sidecars | Fix ups > Repeated metadata |
