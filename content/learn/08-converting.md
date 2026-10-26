---
title: Converting
chapter: 8
lede: Choose how the conversion writes the dataset, run it, and read what it did. The conversion writes every included row under its BIDS name, links fieldmaps to the runs they correct, removes identifying fields, and then fills in the metadata and validates the result.
time: 10 minutes
sample: Multimodal sample v3
---

::: before
The scan table is curated and the dataset metadata is saved (chapters 4 to 7).
:::

## Check the conversion settings

The conversion follows **Settings** > **Convert**. The defaults suit the course; read what they do before your first real study.

{{ figure("l08-settings-convert", "Settings, Convert page: the conversion itself.") }}

| Setting | What it decides |
|---|---|
| **Existing subjects** | What happens when a subject is already in the dataset. **Skip** (the default) keeps the files there and adds only new ones, which is how you add a second session or another participant safely. **Update** replaces files whose content changed, **Replace** backs up and replaces colliding files, **Error** stops instead. |
| **Curated metadata** | **Keep curated metadata**: a re-conversion merges sidecars field by field instead of overwriting what you edited in the Editor. |
| **Residuals** | **Skip residual volumes**: dcm2niix sometimes writes extra copies of a series beside the real one; they are dropped. |
| **Fieldmap links** | How a fieldmap's `IntendedFor` names the runs it corrects: BIDS URIs (`bids::sub-01/...`) or paths from the subject. With **Also write B0FieldIdentifier and B0FieldSource**, the newer pairing is written too. [Fieldmap links and fMRIPrep](/concepts/fieldmap-links/) says which each fMRIPrep version reads. |
| **Force EDF** | **Re-encode EEG to EDF** instead of keeping the source format. |
| **Dummy volumes** | How many volumes to leave out at the start of every functional run, while the signal is not yet steady. **None** by default. A run's own number in **Properties** wins (below). |
| **Physiology** | How a Siemens physiological log is written. **One table per sampling rate, as recorded** (the default), or one table for the run at the fastest rate, the slower channels either **interpolated** or **as recorded** with `n/a` between their samples. All three are valid BIDS. **Crop to the run** keeps only the samples recorded while the run was acquired. A log with no signal (no sensor attached) becomes the trigger alone. |
| **Deface** | **Remove faces from anatomical and PET images** before the subject is written, with the engine you choose. Chapter 14 covers defacing after conversion instead. |

{{ figure("l08-settings-physio", "Settings, Convert page: Dummy volumes and Physiology.") }}

A run can have its own number of dummy volumes: select its row in the scan table and set **Dummy volumes** in **Properties**. **Default** takes the number in Settings; `0` keeps every volume of this run whatever the default. The conversion then removes those volumes from the image, records how many in the sidecar (`NumberOfVolumesDiscardedByUser`), gives the run the time of its first volume kept (in the sidecar and in the scans table, as BIDS defines a run's time), moves its events by the time the removed volumes took, and starts the physiological log recorded with it at the same volume. The course leaves every volume in.

:::: columns
{{ figure("l07-dummy-volumes", "Properties of the BOLD run: 4 dummy volumes for this run.") }}

<div class="col-text">

The section says whether the number is the default or the run's own, and how many volumes the run has (here 60). The scan table's `drop_volumes` column holds the same number, so a script can set it too (`bidsmgr-convert --drop-volumes N` sets the default).

</div>
::::

The log has no number of its own: it follows the run it was recorded with. BIDS Manager finds that run from the acquisition (a log's series is named after its run's and is written when the run ends), so a run renamed in the table keeps its log. The log's **Properties** say which run and how many volumes go:

{{ figure("l07-dummy-physio", "Properties of the BOLD run's physiological log: the 4 volumes of the run it follows.") }}

Further down, **Source data** and the **Post-convert chain**:

{{ figure("l08-settings-chain", "Settings, Convert page: source data and what runs after the conversion.") }}

- **Keep in sourcedata/** copies each subject's raw files into the dataset's `sourcedata/` folder, as they are or as one archive per series. Off by default: DICOM headers carry names and birth dates, so a dataset with `sourcedata/` is not ready to share.
- The **Post-convert chain** runs after every conversion:
  - **Generate metadata**: `participants.tsv`, `CHANGES`, the fields the standard requires that can be derived. Under it, **Write scans and sessions tables** (a `_scans.tsv` per session listing every recording with when it was acquired, a `_sessions.tsv` per subject with sessions), **Write TODO into missing fields** (the placeholders of chapter 7, **In which fields** chooses how far they go), and, off by default, **Generate missing companion files** and **Write CITATION.cff from the dataset description**.
  - **Anonymise the metadata, last**: **Off** by default; **Recommended** or **Strict** anonymise the dataset after everything else has been written ([Anonymising metadata](/guides/anonymising/)).
  - **Validate the dataset**, with **Deep checks (slower)** and **Write an HTML validation report**, and optionally **Check image quality**.

Click **Save** if you changed anything, or **Cancel**.

## Run the conversion

::: step Run it
Click **Run conversion** at the right of the toolbar. While it runs, the button reads **Stop conversion**; a stop lets the series already running finish, discards the subject in progress, and keeps the subjects already written.

{{ clip("l08-convert", "Running the conversion of the sample: the output tree fills, the metadata and validation run after it, and a message says where the dataset was written.") }}

The sample converts in a few seconds; the metadata and validation after it take a few more.
:::

::: step Read the message
When the chain is done, a message says **Conversion complete** and where the output was written. A conversion where a subject failed says so instead, and the reason is in the project's `.bidsmgr/errors/` folder.
:::

::: step Read the Log
The Log has one section per step: **Conversion**, **Metadata** and **Validation**, each with its time.

{{ figure("l08-log", "The end of the Log after the conversion.") }}

The sample's Log reads, in full:

```text
Conversion  ·  17:28  ·  studies
Writing edited inventory back to /tmp/studies/multimodal_study/.bidsmgr/project/scans/0001__raw/inventory.tsv
Converting → /tmp/studies (n_jobs=1)
bidsmgr 1.5.0 @ <where BIDS Manager is installed> | platform=darwin py=3.10.11
auto-loaded recording-metadata scaffold /tmp/studies/multimodal_study/.bidsmgr/project/scans/0001__raw/inventory.tsv.recording_meta.json
committed sub-001 to /tmp/studies/multimodal_study/sub-001
convert summary: 1 new, 0 merged into existing
Conversion completed

Metadata  ·  17:28
Running metadata on /tmp/studies
Metadata completed

Validation  ·  17:28
Validating /tmp/studies
```

`committed sub-001` means the subject was written into the dataset in one move: BIDS Manager converts each subject in a staging folder first and moves it into place only when every file of it is ready, so an interrupted conversion never leaves half a subject behind. `1 new, 0 merged` says the subject was new to the dataset. The history icon in the Log's corner lists every log of the project; each is also a file in `.bidsmgr/logs/`.
:::

::: check
- The **Output data tree** shows `sub-001/ses-01` with nine datatype folders.
- The project folder holds {{ m("converted.files") }} files outside `.bidsmgr/`.
:::

{{ figure("l08-output-tree", "The output data tree after the conversion.") }}

## What the conversion did, besides converting

The conversion log in `.bidsmgr/logs/` has the details. For the sample, it shows the conversion:

- renamed dcm2niix's pieces of the fieldmap to `magnitude1`, `magnitude2` and `phasediff`;
- linked the phase-difference fieldmap to the BOLD run, and the reversed-phase diffusion reference to the diffusion run, with `IntendedFor` and a shared `B0FieldIdentifier`;
- wrote the BOLD run's physiological log as one `_physio.tsv.gz` per sampling rate: the four ECG leads at 400 Hz (`_recording-ecg_`), the pulse at 200 Hz (`_recording-cardiac_`) and the breathing at 50 Hz (`_recording-respiratory_`), each with the scanner trigger as its last column, 1 at the start of every volume; and both eyes of the eye tracker into their own files;
- wrote the PET fields the DICOM header holds but dcm2niix does not copy, and the dose sheet's fields;
- removed seven identifying fields (the participant's name, ID, birth date, age, sex, size and weight) from every MRI sidecar, and six from the header inside each spectroscopy file.

The metadata step then wrote `participants.tsv` from the participants spreadsheet, the session's `_scans.tsv` (one row per recording, each with its acquisition date and time), the subject's `_sessions.tsv`, `CHANGES`, and {{ m("todo.inserted") }} TODO placeholders across {{ m("todo.files") }} files.

::: different
- **Conversion finished with errors.** A subject failed; the others were written. Open `.bidsmgr/errors/` in the project for the subject's log.
- **Nothing was converted.** No row is ticked, or the raw folder has moved since the scan (the Raw input bar then says **Moved**).
- **The dataset already had this subject, and nothing changed.** That is **Skip** at work. Choose **Update** in Settings > Convert to replace files whose content changed.
:::

::: recap
- The dataset holds `sub-001/ses-01` in nine datatypes, with `participants.tsv`, the scans table and the metadata.
- It has been validated once, at the end of the conversion. Next, read that validation in the [Editor](/learn/09-validating/).
:::
