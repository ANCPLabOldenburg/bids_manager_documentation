---
title: Quality measures
lede: Every measure, plot and map of the fast quality check, with how it is computed and how to read it. The same explanations appear in BIDS Manager when you hover a measure or click its info icon.
description: The measures of the BIDS Manager quality check of anatomical, diffusion and functional images.
---

The quality check is for screening: a value far from the others of the same protocol is a reason to look at the image. Most measures depend on the scanner, the sequence and the field of view, so compare an image with the others of its protocol in your dataset (the **In this dataset** column of the quality panel), not with a fixed number. How to run the check is in [Checking image quality](/learn/13-image-quality/); its methods and thresholds are settings ([Settings](/reference/settings/#quality-control)).

Where a measure follows a definition of MRIQC, the explanation says how the two compare.

## Anatomical images

How the check works: the brain is found with `mindgrab` and the tissues with `robust_tissue` (both from brainchop), and the image is registered to a template with `niimath`. Each runs in its own process; where one cannot run, a faster, more approximate method written in Python takes its place and the panel says so. The air around the head is measured only in images that are not defaced, not skull-stripped and not set to zero by the scanner.

### Noise and contrast

{{ ref.qc_intro("group.anat.noise") }}

{{ ref.qc_group("anat_noise") }}

### Artefacts

{{ ref.qc_intro("group.anat.artefacts") }}

{{ ref.qc_group("anat_artefacts") }}

### Tissues

{{ ref.qc_intro("group.anat.tissues") }}

{{ ref.qc_group("anat_tissues") }}

### Coverage and smoothness

{{ ref.qc_intro("group.anat.coverage") }}

{{ ref.qc_group("anat_coverage") }}

## Diffusion images

### Gradient table

{{ ref.qc_intro("group.dwi.gradients") }}

{{ ref.qc_group("dwi_gradients") }}

### Motion

{{ ref.qc_intro("group.dwi.motion") }}

{{ ref.qc_group("dwi_motion") }}

### Noise and contrast {#dwi-noise}

{{ ref.qc_intro("group.dwi.noise") }}

{{ ref.qc_group("dwi_noise") }}

### Artefacts {#dwi-artefacts}

{{ ref.qc_intro("group.dwi.artefacts") }}

{{ ref.qc_group("dwi_artefacts") }}

### Diffusion

{{ ref.qc_intro("group.dwi.diffusion") }}

{{ ref.qc_group("dwi_diffusion") }}

### Plots {#dwi-plots}

{{ ref.qc_group("dwi_plots") }}

## Functional time series

The plots under the time course of a 4-D image, and the maps of the whole run in the viewer's **QC** menu.

### Plots {#bold-plots}

{{ ref.qc_group("bold_plots") }}

### Maps

{{ ref.qc_group("bold_maps") }}

## MEG and EEG

The signal viewer's **QC** checks a recording channel by channel and segment by segment, and compares each channel only with the others of its type (magnetometers with magnetometers, EEG with EEG). It marks flat channels, channels louder than the others of their type that also do not follow them, and channels at a normal level that do not follow their type (by the standard deviation, the peak-to-peak amplitude and the correlation with the others), the power at the line frequency, segments where many channels jump at once, and muscle activity. Each finding can be turned into a bad channel or segment with **Mark as bad**. The thresholds are under **Settings** > **Quality control** > **MEG and EEG QC** ([Settings](/reference/settings/#quality-control)).
