---
title: Checking image quality
chapter: 13
lede: Run the fast quality check on an anatomical image, read the plots under a BOLD run, check every image of the dataset at once, and look at an MEG recording's channels. The checks run on your computer in seconds and change nothing in the data.
time: 20 minutes
sample: Multimodal sample v2
---

::: before
The Editor is open on the converted sample (chapter 12).
:::

## What the quality check is

The quality check measures what can be measured on one image without a full processing pipeline: noise and contrast, artefacts in the air around the head, how the tissues separate, coverage and smoothness, and for diffusion the gradient table, motion and slice dropouts. It follows the definitions of MRIQC where they apply, and every measure is explained where it is shown (hover it, or click its info icon) and in [Quality measures](/reference/quality-measures/).

It is for screening: an image that looks wrong in the numbers is worth looking at. It does not replace looking at the images.

## Check an anatomical image

::: step Open the T1w and check it
Select the T1w in the Editor, then choose **QC** > **Check image quality** in the viewer's toolbar. The quality panel opens beside the planes; the check takes about half a minute on the sample's T1w. The first check on a computer also downloads the two brain models it uses, about 1.5 MB.

{{ clip("l13-qc-panel", "The quality check of the T1w beside the Planes + 3-D layout, laying its masks and tissue classes over the image.") }}
:::

::: step Read the panel
From the top:

- what was checked and how: the brain was found with `mindgrab`, the tissues with `robust_tissue`, the registration with `niimath`;
- **On the image**: the masks and maps the check made, each a checkbox that lays it over the image (brain mask, head mask, the air measured, CSF, grey and white matter, the bias field, the face region);
- the **findings**, each with **Show**: on the sample, **A face is visible**, because the sidecar records no defacing and the face region holds tissue. Chapter 14 deals with it;
- the **Measures**, grouped (noise and contrast, artefacts, tissues, coverage and smoothness), each with its value and its explanation.
:::

The air around the head is measured only in images that are not defaced, not skull-stripped and not set to zero by the scanner, because in those it says nothing about noise.

## The QC plots of a BOLD run

Select the BOLD run, turn on **Time course**, and tick **QC** in its header. **Plots** chooses which plots appear under the time course, aligned with it in time:

{{ clip("l13-bold-qc", "The BOLD run's QC plots under its time course, following the run as it plays.") }}

| Plot | What it shows |
|---|---|
| Framewise displacement | How far the head moved from one volume to the next, in millimetres |
| Translation, Rotation | The head's position over the run |
| DVARS | How much the whole image changed from one volume to the next |
| Outlier voxels | The share of voxels far from their usual value, per volume |
| Slice spikes | A slice whose signal jumps away from its own course in one volume, brighter or darker |
| Global signal | The mean over the head, per volume |
| Carpet plot | Every voxel's time course as a row, so a sudden change shows as a vertical band |

**QC** in the viewer's toolbar also offers maps of the whole run: **Temporal SNR**, **Standard deviation** and **Mean image**.

The sample's resting run is short and still: every plot stays near its baseline. On a run where the participant moved, the plots and the image tell the same story at the same volume:

{{ figure("g-qc-bold-141", "Another study's BOLD run at the volume where the head moved: the slices out of line, and a spike in every plot under the time course.") }}

How to read each plot on that run, tell motion between volumes from motion during one, and choose a threshold: [Reading the quality checks](/guides/quality-control/).

## Check every image at once

**Tools** > **Quality check...** checks every anatomical and diffusion image of the dataset and lists them with their findings and main measures. Click **Check**; **At once** sets how many images are checked in parallel.

{{ figure("l13-qc-dialog", "The quality check of the whole dataset.") }}

Double-click an image to open it in the viewer with its full report. The results are saved in `derivatives/bidsmgr-qc/` in the dataset, so they are not computed twice. The conversion can run the same check at its end (**Settings** > **Convert** > **Check image quality**).

## MEG and EEG

In the signal viewer, **QC** checks the recording channel by channel, per segment: channels much noisier or flatter than the others of their type, line noise, segments where many channels jump, and muscle activity. **Plots** chooses what is drawn beside the traces; **Mark as bad** turns a finding into a bad channel or segment, which **Save to dataset** writes.

{{ figure("g-qc-meg-2.5", "The quality check of a resting MEG recording of the MOUS dataset, its plots beside the traces: a burst at 270 s flagged and marked bad, in red across the traces.") }}

What is flagged depends on the check's thresholds, which **Settings...** in the QC bar opens. On that recording, the burst at 270 s is not flagged with the defaults and is with **Channel off in a segment beyond** lowered from 4 to 2.5: [Reading the quality checks](/guides/quality-control/#artefacts-in-an-meg-recording) goes through it. The course's own MEG recording is 30 seconds of a cropped sample, too short for the check to show much.

## Settings

**Settings** > **Quality control** holds when QC runs (**Run QC when a file opens**), the methods (brain mask, tissue classes, registration), and the thresholds of every check, each with its range. The values are in [Settings](/reference/settings/#quality-control).

{{ figure("l13-settings-qc", "Settings, Quality control page.") }}

::: recap
- The T1w, the FLAIR and the diffusion run are checked; the results are in `derivatives/bidsmgr-qc/`.
- The check found the faces of the anatomical images, which the next chapter removes. Next, [Sharing a dataset](/learn/14-sharing/).
:::
