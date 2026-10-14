---
title: Viewers
lede: Which viewer opens each kind of file, what is in its toolbar, and every key and mouse gesture, written for your system.
description: The BIDS Manager viewers: which file opens where, the toolbars, and every keyboard shortcut and mouse gesture.
---

## Which file opens where

The Editor picks the viewer from the file's name and folder, without reading the file (DICOM is the one exception: its first bytes are read).

| File | Opens in |
|---|---|
| `.nii`, `.nii.gz`, `.mgz`, `.mgh` | the image viewer: slices, 3-D, time course |
| `.nii`, `.nii.gz` in `mrs/` with an MRS suffix (`svs`, `mrsref`, ...) | the spectrum viewer |
| `.fif`, `.edf`, `.bdf`, `.gdf`, `.set`, `.vhdr`, `.con`, `.sqd`, `.kdf`, `.mef`, `.nwb`, and the folders `.ds` and `.mff` | the signal viewer, after a header card with **Load signal** |
| `.tsv`, `.tsv.gz` whose sidecar gives a sampling frequency | the table viewer, with **Visualize** to open it in the signal viewer |
| other `.tsv`, `.tsv.gz` | the table viewer |
| `.json` | the sidecar form (**BIDS view**) and **Tree view** |
| `.bval`, `.bvec` | the gradient table |
| `CITATION.cff` | a form of its fields |
| `README`, `CHANGES`, `LICENSE`, `.txt`, `.md` and other text | the document viewer; Markdown is shown rendered |
| `.png`, `.jpg`, `.svg` and other pictures | the picture viewer |
| a DICOM file, whatever its name | the DICOM header viewer |
| anything else | a description of the file, with **Open with the system's app** |

A BrainVision recording opens from its `.vhdr`, not from its `.eeg` or `.vmrk`.

## The image viewer

The toolbar, from left to right: the layout; **Time course** (for a 4-D image); **Slice**; **Volume** and **Play** for a 4-D image; **QC** (the quality check and the maps of a series); **Tools** (overlays, the header and sidecar, the next run, echo, session or subject, a fieldmap of this image drawn over it); **Save** (a screenshot, a mosaic figure, a preset, a scene, the command line); and at the right the keyboard icon, which lists the shortcuts. **Advanced controls** is the strip on the right edge of the images ({{ key("Ctrl+I") }}). Comparing two images is in the Editor's **Tools** > **Compare images...**.

**Advanced controls** opens a column with every control, in sections: the layers (each image and overlay, its colour map, window, gamma and opacity), the slice views, the layout, and for 3-D its look, the clip planes and the lighting.

The viewer remembers how you last looked at each kind of image: a BOLD run opens with its time course, a T1w with what you set for anatomical images. **Restore every viewer default...** puts back the defaults.

### Keys

{{ ref.keys("volume") }}

### Mouse, on a slice

{{ ref.gestures("slice") }}

### Mouse, in 3-D

{{ ref.gestures("render") }}

## The signal viewer

For MEG, EEG and physiological recordings. The toolbar sets how many channels are shown, the scaling, the time span and the filter; **Advanced controls** chooses the channel type or single channels, and **Events** there (or {{ key("E") }}) draws the task's events over the traces; **QC** checks the recording channel by channel; **Annotate** marks bad channels and segments; **PSD** opens the power spectrum. The overview bar at the bottom shows the whole recording; drag in it to move.

**Save to dataset** writes the bad channels into the `status` column of the recording's `channels.tsv`, and the bad segments as `BAD_` rows of its `events.tsv` (which MNE-BIDS reads back as annotations), as one operation recorded in the project. The task's own events are kept.

### Keys

{{ ref.keys("signal") }}

### Mouse

{{ ref.gestures("traces") }}

## The spectrum viewer

For MR spectroscopy. The spectrum is drawn against chemical shift in ppm, from right to left, with the main metabolites marked; **FID** shows the signal over time. **Advanced controls** sets the line broadening, the phase (or **Auto phase**), which repeat is shown, and the reference; **On anatomy** shows the voxel on the participant's anatomical image.

### Keys

{{ ref.keys("spectrum") }}

## Saving what you see

| From **Save** | Writes |
|---|---|
| **Save a screenshot...** | a PNG of the viewer as it is |
| **Save a mosaic figure...** | a grid of slices, at one to four times the screen's resolution |
| **Save the look as a preset...** | the layout, display options, time course and 3-D look, to apply to another image (the colour map and window are kept by a scene, not a preset) |
| **Save a scene in this dataset...** | what is shown and how, in the project's `.bidsmgr/viz/scenes/`, to open again later |
| **Show the command line...** | the `bidsmgr-view` command that opens the same view, or renders it to a file |

A preset or a scene applies only what an image has: a time-course setting is ignored on an anatomical image.

## From the command line

`bidsmgr-view` opens an image, a scene or an overlay in the viewer without the rest of BIDS Manager. With `--render` it draws the view into a PNG with no window at all, which works on a server.

```console
$ bidsmgr-view sub-001/ses-01/anat/sub-001_ses-01_acq-tfl3p2_T1w.nii.gz
$ bidsmgr-view T1w.nii.gz --render t1.png --planes axial coronal --height 400
```

Every option is in [Command line](/reference/command-line/#bidsmgr-view).
