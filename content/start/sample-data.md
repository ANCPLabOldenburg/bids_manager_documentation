---
title: Sample data
lede: Seven raw datasets to learn BIDS Manager on, each with a guide that converts it step by step. The course uses the multimodal sample; multimodal sample 2 is the same participant recorded coherently; the others show one kind of data in depth.
description: The BIDS Manager sample datasets, what each one shows, and where to download them.
---

## Which sample for what

| Sample | What it holds | Used in | Download |
|---|---|---|---|
| [Multimodal](#multimodal) | One participant: MRI, MR spectroscopy, PET, EEG, MEG and eye tracking | [The course](/learn/), [Multimodal guide](/guides/multimodal/), [Eye tracking](/guides/eye-tracking/) | {{ site.downloads.multimodal.size }} |
| [Multimodal 2](#multimodal-2) | The same recordings as one participant over four visits: one identity, real dates | [Multimodal guide](/guides/multimodal/) | {{ site.downloads.multimodal2.size }} |
| [MRI](#mri) | Two participants on a Siemens scanner, one of them in two sessions | [MRI guide](/guides/mri/) | {{ site.downloads.mri.size }} |
| [MRI, advanced](#mri-advanced) | Two participants, more sequences, spectroscopy and scanner-made maps | [Advanced MRI guide](/guides/mri-advanced/) | {{ site.downloads.mri_advanced.size }} |
| [PET](#pet) | One FDG phantom scan with blood curves and a dose sheet, and one ECAT scan | [PET guide](/guides/pet/) | {{ site.downloads.pet.size }} |
| [EEG](#eeg) | Two participants, fourteen motor-imagery runs each | [EEG guide](/guides/eeg/) | {{ site.downloads.eeg.size }} |
| [MEG](#meg) | Two participants, three recording days, with empty-room recordings | [MEG guide](/guides/meg/) | {{ site.downloads.meg.size }} |

Each sample is a zip. Unpack it anywhere you like, outside the folder you will create the BIDS dataset in: BIDS Manager reads the raw data and never writes into it.

::::: os
:::: macos
Double-click the zip in the Finder. Safari may unpack it for you after the download.
::::
:::: windows
Right-click the zip, choose **Extract All...**, and pick a folder. Do not work inside the zip: Windows shows its contents like a folder, but BIDS Manager cannot read from it.
::::
:::: linux
Run `unzip <file>.zip` in a terminal, or use your file manager's **Extract Here**.
::::
:::::

## Multimodal {#multimodal}

The course's dataset (version 3): one participant's folder with recordings from six kinds of acquisition, so one scan produces a genuinely multimodal scan table. Each source names the participant in its own way, which the course reconciles.

{{ download("multimodal", "Download the multimodal sample") }}

```text
raw/sub-001/
├── mri/          Siemens Prisma DICOM: T1w, FLAIR, a resting BOLD run with its
│                 single-band reference and physiological log, a fieldmap,
│                 a diffusion run and its reversed-phase reference, scouts
├── mrs/          single-voxel spectroscopy and its water reference
├── pet/          GE Advance DICOM, one FDG scan of a phantom
├── eeg/          two EDF recordings: rest and motor imagery
├── meg/          one Elekta Neuromag recording, rest, 30 s
└── eyetracking/  one binocular EyeLink recording
participants.csv  the participant's demographics
dose_sheet.csv    the PET fields no scanner records
```

| | |
|---|---|
| **Size** | {{ site.downloads.multimodal.size }} as a zip, {{ site.downloads.multimodal.unpacked }} unpacked |
| **Scan** | {{ m("scan.rows") }} rows, {{ m("scan.included") }} to convert |
| **Shows** | Reconciling one participant across sources, fieldmaps linked to the runs they correct, physiological recordings one table per sampling rate, spectroscopy, PET metadata from a dose sheet, eye tracking |
| **Note** | A composite: real recordings from different acquisitions in one participant's folder. The PET scan is of a phantom. The 4-D MRI series and the MEG recording are shortened; the BOLD run keeps its first 60 volumes and, since version 3, its physiological log the same 60 (version 2 kept all 100, so its trigger marked 40 volumes the image does not have). |
| **Sources and licences** | MRI and spectroscopy: the neuroimaging unit of the University of Oldenburg; the participant consented to their face being shown. PET: OpenNeuro PET brain phantoms ([10.70883/RGN3768](https://doi.org/10.70883/RGN3768)), CC BY 4.0. EEG: PhysioNet EEG Motor Movement/Imagery Database, ODC-By 1.0. Eye tracking: the eyelinkio test recording, BSD 3-Clause. The licence files are in the zip. |

## Multimodal 2 {#multimodal-2}

The same recordings as the multimodal sample, made coherent the way one participant is recorded in a real multimodal study: every file names the participant, `OL_3844`, in the field its format has for it, and every file was made on the day of its visit. Use it to see a multimodal study with nothing to reconcile but the session labels.

{{ download("multimodal2", "Download the multimodal sample 2") }}

```text
raw/sub-001/
├── mri/          visit 1, 14 Sep 2023: the MRI session of the multimodal sample
├── mrs/          visit 1: spectroscopy, the session's last two series
├── eyetracking/  visit 1: recording through the resting BOLD run
├── eeg/          visit 2, 21 Sep 2023: rest, then motor imagery
├── meg/          visit 3, 28 Sep 2023: rest, 30 s
└── pet/          visit 4, 5 Oct 2023: FDG, at another site
participants.csv  the participant's demographics, as the headers state them
dose_sheet.csv    the PET fields no scanner records, consistent with the dose
```

| | |
|---|---|
| **Size** | {{ site.downloads.multimodal2.size }} as a zip, {{ site.downloads.multimodal2.unpacked }} unpacked |
| **Scan** | 19 rows, 15 to convert; one subject, `sub-001`, for every recording |
| **Shows** | One identity across DICOM, EDF+ and FIF headers; an eye tracker given its folder's participant; sessions found per source from real dates, to name in the table; realistic PET dose values |
| **Note** | A composite made coherent: the recordings of the multimodal sample, with the identity fields and dates of the spectroscopy, PET, EEG, MEG and eye tracking changed to one participant and four visits (listed in its README). Every image, signal and spectrum is as recorded. The PET scan is of a phantom. |
| **Sources and licences** | As the multimodal sample. The licence files are in the zip. |

## MRI {#mri}

A small Siemens dataset in three folders, one per visit. Two of the visits are the same participant, so the scan proposes two subjects, the first with two sessions.

{{ download("mri", "Download the MRI sample") }}

| | |
|---|---|
| **Size** | {{ site.downloads.mri.size }} as a zip, {{ site.downloads.mri.unpacked }} unpacked |
| **Holds** | T1w, T2w, BOLD with its physiological log, diffusion, fieldmaps |
| **Shows** | Subjects and sessions found from the DICOM headers, physiological recordings, fieldmap links |
| **Source** | The neuroimaging unit of the University of Oldenburg |

## MRI, advanced {#mri-advanced}

A larger Siemens dataset with the sequences that need care: several anatomical contrasts, a BOLD run with its single-band reference, diffusion with the maps the scanner computes from it, fieldmap pairs, spectroscopy, and physiological logs.

{{ download("mri_advanced", "Download the advanced MRI sample") }}

| | |
|---|---|
| **Size** | {{ site.downloads.mri_advanced.size }} as a zip, {{ site.downloads.mri_advanced.unpacked }} unpacked. Most of it is one raw spectroscopy series. |
| **Holds** | T1w, T2w, T2starw, FLAIR, BOLD and SBRef, diffusion and its scanner-made maps, fieldmaps, spectroscopy, physiological logs |
| **Shows** | What the scan leaves out on its own and why, scanner-made diffusion maps, spectroscopy, the parameter classifier |
| **Source** | The neuroimaging unit of the University of Oldenburg. One participant consented to their face being shown, and the guide shows only that participant's anatomy. |

## PET {#pet}

One FDG scan of a brain phantom on a GE Advance, with the two blood curves drawn during it and the operator's dose record; and, in `extra_ecat/`, one scan in the ECAT format from a Siemens HRRT.

{{ download("pet", "Download the PET sample") }}

| | |
|---|---|
| **Size** | {{ site.downloads.pet.size }} as a zip, {{ site.downloads.pet.unpacked }} unpacked |
| **Holds** | 35 DICOM files, two PMOD blood curves (`.bld`), `dose_sheet.csv` and `dose.json`; one ECAT file with its own dose sheet |
| **Shows** | The PET fields no scanner records and how to supply them, blood data, the ECAT format |
| **Sources and licences** | Images: OpenNeuro PET brain phantoms ([10.70883/RGN3768](https://doi.org/10.70883/RGN3768)), CC BY 4.0. Blood curves: the PET2BIDS test data, MIT. |

## EEG {#eeg}

Two participants from the PhysioNet EEG Motor Movement/Imagery Database, fourteen EDF runs each: baselines with eyes open and closed, and motor execution and imagery tasks.

{{ download("eeg", "Download the EEG sample") }}

| | |
|---|---|
| **Size** | {{ site.downloads.eeg.size }} as a zip, {{ site.downloads.eeg.unpacked }} unpacked |
| **Holds** | `S001/` and `S002/`, each with `S00xR01.edf` to `S00xR14.edf` and their event files |
| **Shows** | File names that do not say the task (`R01`, `R02`), and naming the tasks yourself in the table; events, montages and the line frequency |
| **Source and licence** | [PhysioNet](https://physionet.org/content/eegmmidb/), ODC-By 1.0 |

## MEG {#meg}

Elekta Neuromag (MEGIN) recordings of two participants: a driving task in several runs, rest, and empty-room recordings before and after. Every recording is cropped to its first 25 seconds; channels, sampling rate, dates and file names are as recorded.

{{ download("meg", "Download the MEG sample") }}

| | |
|---|---|
| **Size** | {{ site.downloads.meg.size }} as a zip, {{ site.downloads.meg.unpacked }} unpacked |
| **Holds** | 23 recordings in three dated folders: `sub_us04rt22/220209/`, `sub_us04rt22/220215/`, `sub_ye07us06/220221/` |
| **Shows** | Sessions from the recording dates, empty-room recordings, runs and tasks from the file names |
| **Source** | The BIDS Manager MEG sample |

## Your own data

The guides work the same way on your own data. Keep a copy of the raw folder you scan: BIDS Manager does not change it, but the copy is what you will go back to if a conversion needs repeating.
