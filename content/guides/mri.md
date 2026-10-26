---
title: Converting MRI
display_title: Converting *MRI*
kicker: Guides
group: Kinds of data
lede: Convert a small Siemens study with two participants, one of them scanned twice, with fieldmaps, functional runs and their physiological logs, diffusion, and the series a scanner adds that are not data.
description: Convert a Siemens MRI study to BIDS with BIDS Manager, on the MRI sample dataset.
time: 25 minutes
sample: MRI sample
measured: mri
---

::: before
- BIDS Manager is installed and you know your way around the GUI ([First launch](/start/first-launch/)).
- The MRI sample is downloaded and unpacked ([Sample data](/start/sample-data/#mri)).
- The course explains each step in more detail; this guide is the MRI-specific route through them.
:::

## The sample

Three folders of DICOM files, one per visit, named by the scanner's series identifiers:

```text
MRI_sample_data_neuroimging_unit_oldenburg_2/
├── OL_0001/   a T1w, two fieldmaps, two BOLD runs (sparse and rest)
├── OL_0002/   a fieldmap, a multiband BOLD run with its single-band reference and physiological log
└── OL_0003/   a T2-weighted SPACE, two runs of one task and a practice run, each with a reference,
               a diffusion run with its two reversed-phase references
```

The series are named in the convention many sites use: `ses-pre_T1w`, `task-dmaging_run-01_bold`. BIDS Manager reads those names, but it also reads how each series was acquired, and decides from both.

::: warning
The participants of this sample did not consent to their faces being shown, so this guide shows tables and trees, not images of heads. Deface anatomical images like these before you share them ([Defacing and skull stripping](/guides/defacing/)).
:::

## Scan

::: step Create a project and scan
On **Home**, create a dataset named `mri_study`. In the Converter, choose the sample folder in **Raw input** and click **Scan…**. The scan took {{ m("scan.seconds") }} seconds here.

{{ figure("guide-mri-table", "The scan table after the scan.") }}
:::

::: step Read what it found
The table has {{ m("scan.rows") }} rows: {{ m("scan.included") }} to convert, and the rest left out on their own, with the reason in the **issues** column (show it with **Manage columns…**):

| Left out | Why |
|---|---|
| `AAHead_Scout_…`, `localizer_…` | Scout images, for positioning; BIDS has no place for them. |
| `PhoenixZIPReport` | The scanner's protocol report: no image in it. |

Tick a row to convert it anyway, if your study needs it.
:::

## Subjects and sessions

The folders `OL_0001` and `OL_0002` carry the same patient identifier, so the scan makes them one subject, `sub-001`, with two sessions; it takes the labels `pre` and `post` from the series names. `OL_0003` is another person, `sub-002`, with no session.

::: step Look at the Overview
Click **Overview** at the top of the Inspection panel. It points out two things worth a decision:

{{ figure("guide-mri-overview", "The Overview of the MRI sample.") }}

- `sub-002` has no session while `sub-001` has two. BIDS allows it, but a dataset is easier to use when every subject has the same structure. If `sub-002` belongs to the `pre` condition, set its **session** to `pre` with **Bulk edit…**; if it does not, leave it.
- Both sessions of `sub-001` were recorded on the same day. If they are one visit, give every row of `sub-001` one session label; if they are two conditions of one day, as here, keep them.
:::

The course explains the same decisions on its own sample: [The scan table](/learn/04-scan-table/).

## Fieldmaps

Session `pre` has two fieldmaps and two BOLD runs. Each fieldmap is written as three files (two magnitudes and the phase difference) and linked to the runs it corrects: runs with the same shim settings first, otherwise by time, each run to the last fieldmap acquired before it (or the first one after it, if none came before).

::: step Check which runs a fieldmap corrects
Select the row `ses-pre_run-02_fmap`. **Corrects these runs** in **Properties** shows the run it will be linked to, ticked, and why.

{{ figure("guide-mri-fmap", "Properties of the second fieldmap of session pre.") }}

Tick or untick a run to choose yourself. Only tick runs of the same subject and session: the list also offers others (see [Known issues](/help/known-issues/)).
:::

The diffusion run of `sub-002` has two reversed-phase references (`acq-15b0_dir-ap` and `acq-15_dir-pa`); both become `fmap/…_epi` files linked to the diffusion run, which is what QSIPrep and fMRIPrep read. Why both links are written, and what each version of fMRIPrep reads: [Fieldmap links and fMRIPrep](/concepts/fieldmap-links/).

## Physiological logs

The series `…_PhysioLog` hold what the scanner recorded during a run. Here no pulse oximeter, breathing belt or ECG was attached, so they hold only when each volume was acquired. Each becomes a `_physio.tsv.gz` beside its run holding the trigger alone: 1 at the start of every volume, on the scanner's clock (400 Hz), with a sidecar giving the rate and the start time. Where sensors are attached, their signals come with it, one table per sampling rate ([Converting](/learn/08-converting/#check-the-conversion-settings)). They open in the Editor as tables, and **Visualize** draws them ([Viewing data](/learn/12-viewing-data/#physiological-recordings)).

{{ figure("guide-mri-physio", "The log of a dmaging run with Visualize: the scanner trigger alone, a mark at every volume.") }}

## Describe and convert

::: step Give the dataset's authors and licence
Click **Dataset metadata…**, fill **Authors** and **License** in the dataset description, and, under the template for `func` `bold`, **TaskDescription** for each task you know. Click **Save** ([Metadata you provide](/learn/07-metadata/)).
:::

::: step Convert
Click **Run conversion**. The sample converted in {{ m("convert.seconds") }} seconds, metadata and validation included, into {{ m("converted.files") }} files.
:::

## Validate

Open the **Editor** and click **Validate dataset**. The sample reports {{ m("converted.validation.ok") }} files valid, {{ m("converted.validation.warn") }} warnings and {{ m("converted.validation.err") }} errors.

{{ figure("guide-mri-editor", "The converted sample in the Editor, validated.") }}

The warnings are of three kinds:

| Warning | What to do |
|---|---|
| A TODO placeholder ({{ m("converted.todo.inserted") }} in {{ m("converted.todo.files") }} files) | Fill what you know: the department, the task descriptions and instructions. |
| `EVENTS_TSV_MISSING` on a task run | A task run should have an `events.tsv`. Add the events of your task, or ignore it for a resting run. |
| `B0_FIELD_SOURCE_RECOMMENDED` | A run without a fieldmap, in a subject that has fieldmaps: the functional runs of `sub-002`, whose only fieldmaps are for its diffusion run. Nothing to do unless a fieldmap covers them. |

## In your own MRI data

- **Check the names the scan proposes**, especially for sequences your site names its own way. The **confidence** column and **Why this name** in **Properties** show how sure the classifier is and why ([The classifier](/reference/classifier/)).
- **Use scan rules** for a site convention you meet in every study: leave out a sequence by name, or name one yourself (**Settings** > **Scan rules**).
- **Check the fieldmap links** before converting, in **Properties**.
- **Repeated series** of one task get run numbers; an aborted run is still there, unticked or not: the **Highlight aborts** button under the table marks the likely ones.
- **Deface** before sharing.
