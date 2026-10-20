---
title: Advanced MRI
display_title: Advanced *MRI*
kicker: Guides
group: Kinds of data
lede: A larger Siemens study with the series that need care: what the scan leaves out and why, maps the scanner computes from a diffusion run, a sequence named one thing and acquired as another, and spectroscopy with its water reference.
description: Convert a Siemens MRI study with diffusion maps, spectroscopy and unusual sequences to BIDS with BIDS Manager.
time: 30 minutes
sample: Advanced MRI sample
measured: mri_advanced
---

::: before
- The advanced MRI sample is downloaded and unpacked ([Sample data](/start/sample-data/#mri-advanced)); it is 8 GB unpacked, most of it one raw spectroscopy series.
- You have converted the [MRI sample](/guides/mri/) or followed the course: this guide only covers what is new.
:::

## The sample

Three visits on a Siemens Prisma: `OL_3844` and `OL_3845` are one participant on two days, `OL_3846` another. Between them: T1-weighted, T2-weighted and FLAIR images, gradient-echo images made for neuromelanin, BOLD runs with their references and physiological logs, two diffusion runs with reversed-phase references and the maps the scanner computed, fieldmaps, and single-voxel spectroscopy with its water reference.

## What the scan leaves out

::: step Scan and read the left-out rows
Create a dataset named `mri_advanced_study` and scan the sample folder: {{ m("scan.rows") }} rows in {{ m("scan.seconds") }} seconds, {{ m("scan.included") }} of them to convert.

{{ figure("guide-adv-table", "The scan, scrolled to the diffusion series.") }}
:::

| Left out | Why |
|---|---|
| `AAHead_Scout_…` (several per visit) | Scout images for positioning the slices. |
| `PhoenixZIPReport` | The scanner's protocol report: DICOM, but no image. |
| `ses-pre_dir-ap_dwi_TENSOR` | The diffusion tensor the scanner computed: stored without an image, so nothing can be converted. |

Kept, although the scanner computed them: `…_dwi_FA`, `…_dwi_ColFA` and `…_dwi_TRACEW`. BIDS has names for these maps in `dwi/` (`FA`, `colFA`, `trace`), so they are converted beside the diffusion run. Untick them if your analysis recomputes them, as most do.

## A series named one thing and acquired as another

The series `ses-post_acq-grenm2mm_run-01_T1w` was named T1w by the operator. dcm2niix's guess, from its header strings, is `T2starw`. The parameter classifier reads how it was acquired and agrees with the operator, and **Why this name** shows why:

::: step Read the evidence
Select the row and scroll **Properties** to **Why this name**.

{{ figure("guide-adv-why", "Why this name for the neuromelanin gradient echo.") }}

A fast 3-D spoiled gradient echo with a magnetisation-transfer pulse before a short echo is a T1-weighted image of the kind made for neuromelanin. The classifier named it `anat/T1w` with `part-mag`, and listed dcm2niix's `T2starw` as the alternative. If your protocol calls it something else, change the suffix in the table.
:::

The same classifier names `ses-pre_T2w`, a SPACE sequence with an inversion pulse, **FLAIR**: the course explains that case ([Naming recordings](/learn/05-naming/)).

## Spectroscopy

`OL_3846` holds two spectroscopy series: the metabolite spectrum and its water reference, both proposed as `svs` runs 1 and 2. The reference is not a second run: select its row (its series name contains `type-ref`), set **suffix** to `mrsref` and clear **run**; clear **run** on the spectrum too. The course does the same on its sample ([Naming recordings](/learn/05-naming/)). After the conversion, the spectrum opens in the Editor as a spectrum ([Viewing data](/learn/12-viewing-data/#spectroscopy)).

## Convert and check

::: step Convert
Give the authors and licence in **Dataset metadata…** and click **Run conversion**. The sample converted in {{ m("convert.seconds") }} seconds into {{ m("converted.files") }} files; the second diffusion run alone is 8,775 DICOM files.
:::

::: step Look at the diffusion folder
In the Editor, open `sub-001/ses-pre/dwi/`. The run's `.bval` opens as its gradient table; the scanner's maps are files of their own beside it.

{{ figure("guide-adv-dwi", "The diffusion folder of session pre.") }}
:::

**Validate dataset** reports {{ m("converted.validation.ok") }} files valid, {{ m("converted.validation.warn") }} warnings and {{ m("converted.validation.err") }} errors.

## Identifiers and faces

The participants of this sample consented to their faces being shown. For your own data: the conversion removes the participant's identifiers from every sidecar and from the spectroscopy files; check `participants.tsv`, deface the anatomical images, and do not share `sourcedata/` ([Identifiers and privacy](/concepts/identifiers-and-privacy/)).
