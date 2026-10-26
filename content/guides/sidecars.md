---
title: Writing sidecars from the recordings
display_title: Writing *sidecars* from the recordings
kicker: Guides
group: Curating a dataset
lede: A sidecar deleted by accident, a dataset that never had them, or sidecars that lack fields their recordings could give. BIDS Manager writes them again from what is still there, field by field, and says where it read each one.
description: Write missing .json sidecars, or complete existing ones, from the source data, the file's own header, your answers and the sidecars that link to it, in the Editor or with bidsmgr-sidecars.
time: 10 minutes
sample: Multimodal sample v3
---

::: before
- A dataset open in the Editor as a project. The figures use the course's sample after chapter 10, with the BOLD run's sidecar deleted.
:::

## What it reads

Every `.json` sidecar describes one recording: its timing, its scanner, its task. When one is lost, most of what it held is still somewhere. BIDS Manager reads it from five places, the most complete first, and never writes over a value a sidecar already holds:

| Read from | What it gives |
|---|---|
| **Source data** | The data the recording was converted from, converted again in a temporary folder with the conversion's own code: everything dcm2niix and the physiology, PET and eye-tracking converters read from the original files. Only in a project that converted the dataset; the dataset itself is not touched. |
| **File header** | The recording file itself: a NIfTI's timing, the header inside a spectroscopy file, everything MNE-BIDS reads from an EEG or MEG recording. |
| **Your answers** | What you gave in this project: a metadata template, a dataset or per-recording value, a cell of the scan table. |
| **Other sidecars** | The sidecars that link to this one, such as the fieldmap intended for this run. |
| **File name** | What the name says, such as the task, as the metadata step does. |

What none of them knows can be marked with a **Placeholder** (`TODO`), as the metadata step marks it. The phase-encoding direction's sign is never guessed from a header: only the source data gives it.

## Write a missing sidecar

::: step Right-click the recording
In the BIDS tree, right-click the recording whose sidecar is missing and choose **Write its sidecar from the recording...** (on a folder, **Write missing sidecars here from the recordings...**; on a recording that has its sidecar, **Complete its sidecar from the recording...**). For the whole dataset, **Tools** > **Check and repair** > **Write sidecars from the recordings...** opens the same tool.
:::

:::: columns
{{ figure("g-sidecars-menu", "The tree's right-click on the BOLD run, whose sidecar is missing.") }}

<div class="col-text">

The entry sits under **Check and repair** with **References...** and **Ignore in validation**. In a folder opened **View only** it is greyed out, because nothing may be written there.

</div>
::::

::: step Read what would be written
The dialog reads the recording at once, in the background, and lists every field it would write with where it read it:

{{ figure("g-sidecars-dialog", "Sidecars from the recordings for the BOLD run: one new sidecar, every field with where it was read.") }}

At the left, what it reads and which sidecars: **The data it was converted from** (on in a project that converted the dataset), **Missing ones** or **Also add to existing**, and how far to **Mark what is still unknown with TODO**. In the middle, the recordings it would write for, each with a tick box. At the right, the selected recording's fields, in up to four groups:

- **Written**: the fields it will write, each with the place it was read.
- **Already stated higher up, left to it**: a value a sidecar at a higher level (one for every run of a task, say) already gives this recording, so it is not repeated, unless the source data or your answers disagree.
- **Found, not written: not valid in this BIDS version**: a value the version chosen in **Settings** > **Validation** does not allow. It is shown so you can fill it in by hand.
- **Required, and nothing to read it from**: what the standard requires and no place knew.
:::

::: step Write it
Click **Write 1 sidecar**. The sidecars are written as one step of the Editor's history: **Undo** removes them ([Undo, redo and the history](/guides/history/)). Validate the dataset to see the result.
:::

## Complete the sidecars you have

**Also add to existing** includes the recordings that have a sidecar: each keeps every value it holds and gains what it lacks, and a `TODO` is replaced by a value that was found. With **Where** set to **The whole dataset**, the dialog reads every recording:

{{ figure("g-sidecars-complete", "The whole dataset with Also add to existing: nothing to add to the sidecars that are there, and the deleted one new.") }}

On the course's sample, every other sidecar already holds what its recording says: a dataset converted by BIDS Manager has nothing to gain. The tool earns its keep on a dataset converted by an older version or another tool, or one whose sidecars were edited by hand.

## How much comes back

On the course's sample after chapter 10, with the sidecars of its {{ m("sidecars.source.deleted") }} recordings deleted, validation finds {{ m("sidecars.source.before.err") }} errors. Written again from the source data, {{ m("sidecars.source.after.err") }} remain: the PET's reconstruction parameter labels and units, which no file holds and chapter 9 writes by hand. From the headers alone, as for a dataset converted elsewhere, {{ m("sidecars.headers.after.err") }} remain, each a field only the source data held: fill them in the sidecar viewer, or answer them in the project and write again.

## Files outside BIDS naming

Any image or recording BIDS Manager reads gets a sidecar, named the BIDS way or not: a `T1.nii.gz` beside the data, a `_defaced` copy, a file in an extra folder or in `derivatives/`. Its sidecar is written beside it, named after it. What the file is recorded as decides which fields apply: its BIDS name if it has one, otherwise a suffix in its name, its datatype folder, or a guess from the file itself (a 4-D image, a PET image, a MEG format). Names that are not BIDS names are shown in italics, and a **Read as** row under the fields lets you correct the guess.

## From a terminal

`bidsmgr-sidecars` does the same without the window. It plans first and prints the plan; `--dry-run` stops there.

```console
$ bidsmgr-sidecars /data/bids/my_study --dry-run
my_study: 1 new sidecar, 0 added to, BIDS 1.11.1, source data converted again
  new  sub-001/ses-01/func/sub-001_ses-01_task-rest_bold.json  [func/bold, BIDS name]  76 fields: source data 74, other sidecars 1, file name 1
  21 recordings already have their sidecar (--complete adds what they lack)
$ bidsmgr-sidecars /data/bids/my_study sub-001/ses-01/func
$ bidsmgr-sidecars /data/bids/my_study --complete --fill-scope recommended
```

`--no-source` reads the files alone, `--fields` prints every field with where it was read, `--kind PATH=DATATYPE/SUFFIX` says what a file outside BIDS naming is, and `--schema` chooses the BIDS version. Written, the change is one step of the Editor's history, undoable from the Editor. Every option: [Command line](/reference/command-line/#bidsmgr-sidecars).

::: check
- The recording's row in the tree has a sidecar again, and **Validate dataset** no longer reports the fields it lacked.
- In the sidecar viewer, the fields you see are the ones the dialog listed under **Written**.
:::
