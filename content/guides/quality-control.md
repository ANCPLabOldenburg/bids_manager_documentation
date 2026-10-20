---
title: Reading the quality checks
display_title: Reading the quality *checks*
kicker: Guides
group: Viewing and quality
lede: Two real recordings with real problems, a BOLD run in which the participant moved and a resting MEG recording with a burst of muscle, and how the quality plots show each: what every plot measures, how to tell one kind of problem from another, and how the thresholds change what is flagged.
description: Interpret BIDS Manager's quality checks on real data: head motion in a BOLD run (framewise displacement, DVARS, slice spikes, carpet plot) and MEG artefacts with their thresholds.
time: 25 minutes
sample: A BOLD run with motion; MOUS MEG (Donders Institute)
---

::: before
- The quality check is for screening. It tells you where to look before an analysis; it does not replace a pipeline such as MRIQC or MEEGqc, and it never changes the data. How to run it is in [Checking image quality](/learn/13-image-quality/); every measure is defined in [Quality measures](/reference/quality-measures/).
- The two recordings: a BOLD run of an Oldenburg study (Siemens Prisma 3 T, multiband 4, 48 slices of 2.5 mm, TR 0.85 s, 1,224 volumes), and the resting MEG of participant A2004 of the MOUS dataset (CTF 275, 1200 Hz, 328 s).
:::

## Head motion in a BOLD run

### The whole run

Open the BOLD run in the Editor, switch on **Time course**, tick **QC**, and choose the plots under **Plots**: here framewise displacement, DVARS, slice spikes and the carpet plot. **Time axis** set to **Volume index** numbers the volumes as the viewer does.

{{ figure("g-qc-bold-run", "The run with motion, at volume 141: the slices of that volume out of line in the sagittal and coronal planes, and the same moment as a spike in every plot under the time course.") }}

Each plot answers its own question, and they are read together:

| Plot | It measures | On this run |
|---|---|---|
| **Framewise displacement** | how far the head moved from one volume to the next, in mm: the six motion parameters added up, the rotations as arcs on a 50 mm sphere | mean 0.236 mm, max 1.86 mm, 68 volumes above 0.5 mm |
| **DVARS** | how much the whole image changed from one volume to the next, in % of its mean; volumes above the box plot's fence are marked | median 3.65 %, fence 4.70 %, 87 volumes above it |
| **Slice spikes** | the slice that departs most from its own course, per volume, beyond what the whole volume did | 78 volumes above 6 |
| **Carpet plot** | every sampled voxel's signal over time, one row each, from the head's edge at the top to its centre at the bottom | vertical bands where the head moved |

The orange ticks above a plot mark the volumes over its threshold. The spikes do not come alone: they cluster around volumes 40, 141 to 153, 232, 290, 394 and 495 to 497, a few seconds each.

### Zoom in on one movement

{{ key("Ctrl") }} + scroll over the plots zooms in time around the pointer, {{ key("Shift") }} + scroll moves along the run, and the plain wheel steps through the volumes. A click on a plot goes to that volume. Zoomed to volumes 100 to 200, three volumes before the movement:

{{ figure("g-qc-bold-138", "Volume 138: the planes are clean and every plot is at its baseline.") }}

Volume 141, three volumes later:

{{ figure("g-qc-bold-141", "Volume 141: the slices acquired after the head moved no longer line up with those acquired before, a comb of stripes in the sagittal and coronal planes; framewise displacement is 1.86 mm.") }}

The slices of a volume are not acquired at once. Here they were taken in an interleaved order, four at a time (multiband 4), over 0.85 s. When the head moves halfway through, the slices taken after the movement sample the brain in another place than those taken before, and seen from the side the volume becomes a comb. That is why **slice spikes** is the plot that tells this kind of motion apart.

### Step through it

{{ clip("g-qc-bold-scrub", "Volumes 128 to 160, one at a time: stripes at 141 and 152; at 146 and 147 the head moves again but the slices stay in line.") }}

Read the plots together, volume by volume:

- **141 and 152**: framewise displacement, DVARS and slice spikes all jump, and the image breaks into stripes. The head moved during the volume. These volumes are damaged in themselves.
- **146 and 147**: framewise displacement is high again (1.2 and 1.26 mm) but slice spikes stays low and the image looks whole: the head moved between volumes more than during one. The volume is intact, but it sits in another place than its neighbours, and the signal of the volumes after a movement is still disturbed.
- **The carpet plot** shows each movement as a vertical band across many rows, darkest at the top, where voxels at the edge of the head move in and out of the brain.
- **The time course** of a single voxel jumps at the same volumes: a reason not to trust a voxel's signal at those moments.

### What to do with it

The check marks volumes; deciding what to do with them belongs to the analysis. Common answers are to model the motion parameters as regressors, to censor (scrub) the marked volumes and their neighbours, or to exclude a run whose share of marked volumes is too high. The threshold matters as much as the method. On this run:

| FD above | Volumes | Share of the run |
|---|---|---|
| 0.2 mm | 584 | 48 % |
| 0.3 mm | 235 | 19 % |
| 0.5 mm (the default) | 68 | 6 % |
| 0.9 mm | 17 | 1 % |

The thresholds are in **Settings** > **Quality control**: **FD worth a look above** (0.5 mm), **DVARS fence** (1.5 times the interquartile range), **Slice spike above** (6 robust standard deviations). Set them to what your analysis will use, so that what the check marks is what the analysis will remove. They are remembered, and apply to every run.

## Artefacts in an MEG recording

### The check at its defaults

Open the recording in the Editor, **Load signal**, and click **QC**. The check reads every sample once and judges each channel and each 2-second segment against the channels of its own type: magnetometers with magnetometers, gradiometers with gradiometers, EEG with EEG. Under **Plots**: the share of channels off in each segment, the muscle band, and the peak-to-peak amplitude. The **Beside** icon in the QC bar's corner puts the plots to the right of the traces, as here, rather than under them; the plots span the whole recording, and the stretch the traces show is the box on them.

{{ figure("g-qc-meg-default", "The resting MEG of MOUS participant A2004, magnetometers, 258 to 288 s, with the QC plots beside the traces at the defaults. A burst runs through these left central sensors at 270 to 273 s and again at 281 s; at most 11 % of the magnetometers are off: nothing is flagged.") }}

The traces show something at 270 s: a burst of fast activity across the sensors shown, and again at 281 s. The plots see it too, as a peak in each. But with the defaults it is not flagged, because each threshold asks for more:

| Parameter | Default | Asks |
|---|---|---|
| **Channel off in a segment beyond** | 4 times its level | a channel is off in a segment when its STD or peak-to-peak there is more than 4 times its own usual level |
| **Segment flagged when off on** | 0.20 of a type | a segment is flagged when 20 % of one type's channels are off |
| **Muscle above** | 4 z | the muscle band's share of the power (110 to 140 Hz), z-scored over time |

At 270 s the burst puts 11 % of the magnetometers beyond 4 times their level, and the muscle measure reaches 3.8: under both lines.

### Lower a threshold, and flag more

The parameters are in the advanced controls: **Settings...** in the QC bar opens them. Lower **Channel off in a segment beyond** to 2.5, click **Check again with these parameters**, then **Mark flagged segments bad**:

{{ clip("g-qc-meg-threshold", "Settings..., Channel off in a segment beyond from 4 to 2.5, Check again: the stretch at 270 s is flagged; Mark flagged segments bad lays it over the traces in red.") }}

{{ figure("g-qc-meg-2.5", "At 2.5, 44 % of the magnetometers are off at 270 s; the segments from 270 to 274 s are flagged, and marked bad they show in red across the traces, labelled BAD_noise.") }}

How much each step catches on this recording, magnetometers only:

| Channel off beyond | Flagged |
|---|---|
| 4 (the default) | nothing |
| 3 | 270 to 272 s |
| 2.5 | 270 to 274 s |
| 2 | 270 to 274 s and 280 to 282 s |

Lowering **Muscle above** from 4 to 3 instead flags the same two stretches, labelled as muscle:

{{ figure("g-qc-meg-muscle", "Channel off back at 4, Muscle above at 3: 270 to 274 s and 280 to 282 s flagged as muscle, and marked in red.") }}

The burst is fast, broad-band and on many sensors at once, as tensed jaw or neck muscles are: both lowered thresholds find it, from two directions.

### A threshold is not a finding

The same thresholds on the two other MOUS participants used here (A2047 and V1028, resting MEG too) flag nothing, even at 2: at most 18 % and 11 % of their magnetometers are off in any segment. Lowering a threshold does not make artefacts; it decides how large a departure has to be before you are asked to look. Choose it from what your analysis can tolerate, check the flagged stretches in the traces, and mark them only when the traces agree: **Mark as bad** in the QC bar (or **Mark flagged segments bad** in the advanced controls) marks them as bad segments labelled by why (`BAD_muscle`, `BAD_jump`, `BAD_noise`), and **Save to dataset** writes them into the run's `events.tsv`, as one step of the history.

### Channels the check suggests

The QC line also lists channels: on this recording **41 uncorrelated** magnetometers, left frontal and central sensors that follow the rest of their type less closely than **Channels follow their type above** asks (a correlation of 0.6). Set that parameter to 0 and none are suggested: the suggestion rests on that one criterion. A suggested channel is a reason to look at it in the traces and in **Report...**, not a verdict; **Mark suggested channels bad** marks them in the viewer, and only **Save to dataset** writes them into the run's `channels.tsv`.

The full list of parameters, with their ranges, is in [Viewers](/reference/viewers/) and [Settings](/reference/settings/#quality-control).

## Anatomical images

The anatomical check measures noise, contrast and artefacts of a T1w or T2w image against its own background and tissues, and lays maps of what it found over the image:

{{ clip("l13-qc-panel", "Check image quality on the course's T1w: the panel beside the planes, and its maps laid over the image in turn.") }}

Compare an image with the others of its protocol in the dataset (the **In this dataset** column), not with a fixed number: most measures depend on the scanner and the sequence. **Tools** > **Quality check...** runs it on every anatomical image at once and lists what stands out ([Checking image quality](/learn/13-image-quality/#check-every-image-at-once)).

::: note
The MEG figures use data from the MOUS dataset. Data were provided (in part) by the Donders Institute for Brain, Cognition and Behaviour. Schoffelen, J.-M., Oostenveld, R., Lam, N. H. L., Uddén, J., Hultén, A., & Hagoort, P. (2019). A 204-subject multimodal neuroimaging dataset to study language processing. *Scientific Data*, 6, 17.
:::
