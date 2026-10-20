---
title: Validating in the Editor
chapter: 9
lede: Check the converted dataset against the BIDS standard, read each finding where it occurs, and fix the three errors the sample has, one in a form and two that only you can answer. The Editor is where you look at and change the dataset itself.
time: 15 minutes
sample: Multimodal sample v2
---

::: before
The sample is converted (chapter 8).
:::

## Open the Editor

Click **Editor** in the header. With a project open, the Editor shows that project's dataset.

{{ figure("editor-map", "The Editor on the converted sample, with the BOLD run's sidecar selected.") }}

From the top: the **toolbar** (open a folder, undo and redo, validate a file, a folder or the dataset, **Deep checks**, **Tools**, and the counts once validated); the **path bar**, with a chip saying how the folder is open (here **project**); then three panels: the **BIDS tree**, the **Viewer** in the middle, which shows whatever file you select, and **Validation** on the right.

## Validate the dataset

::: step Click Validate dataset
Click **Validate dataset** in the toolbar. **Deep checks**, on by default, makes it also open every image's header and every table's contents: slower, and it catches a truncated image or a header that disagrees with its sidecar. The sample takes a few seconds.

{{ clip("l09-validate", "Validating the dataset: the marks in the tree, the counts in the toolbar.") }}
:::

::: step Read the counts
The toolbar shows how many files are valid, and how many warnings and errors were found (a file can have several): **{{ m("converted.validation.ok") }} valid**, **{{ m("converted.validation.warn") }} warnings**, **{{ m("converted.validation.err") }} errors**. Click a count to list the findings concerned, grouped by kind, however large the dataset.

{{ figure("l09-toolbar", "The Editor's toolbar after validation.") }}

An **error** breaks the standard: a tool reading the dataset may fail on it. A **warning** marks something the standard recommends and the dataset lacks, or a TODO placeholder left to fill. Most of the sample's warnings are of the second kind.
:::

::: step Read the tree
Each file in the tree now has a mark: a tick when clean, a count of warnings or errors otherwise. Each folder adds up what is inside it, so you can follow the red count down to the file that has it.

{{ figure("l09-tree-badges", "The BIDS tree after validation.") }}
:::

## Read a finding

::: step Select a file
Click `sub-001_ses-01_task-rest_bold.json` in `func`. The Viewer shows the sidecar as a form (chapter 10), and the Validation panel shows its findings.

{{ figure("l09-validation-file", "The Validation panel for the BOLD run's sidecar.") }}

The panel has three sections: **Dataset** (findings about the dataset as a whole), **Folder** (about the folder the file is in) and **File**. Each finding is a card: the rule that fired, the **Field** it is about, **What is wrong**, **Why it matters**, and where in the standard the rule is **Defined in**.
:::

::: step Go to the field
Click the button on a card. For a TODO placeholder it reads **Set a real value**: the form scrolls to that field and marks it. For other findings about a field it reads **Fix**. **Highlight** in the File section marks every field (or table cell) the file's findings are about, all at once.
:::

The panel's dropdown narrows the list to errors only or warnings only, and **Worst first** sorts errors to the top. **Whole dataset** at the top of the panel lists every kind of finding once, with the number of files it fired on, and **Fix in all files** for findings that can be answered the same way everywhere.

{{ figure("l09-validation-dataset", "The Whole dataset view.") }}

## Fix the errors {#fix-the-errors}

Three errors: one in the PET sidecar, and one on each eye's recording of the eye tracker. The first is answered in a form; the other two need something only you know, written by hand.

### The PET reconstruction

{{ figure("l09-error", "The PET sidecar, with ReconMethodParameterUnits marked and its error in the Validation panel.") }}

The PET image was reconstructed by filtered back projection, which has no parameters. BIDS asks every PET sidecar to say which parameters the reconstruction had and in which units, `ReconMethodParameterLabels` and `ReconMethodParameterUnits`, and for a method without any, to say `["none"]`. The scanner's header does not hold them, and the sample's dose sheet says `none`, which this version does not read ([Known issues](/help/known-issues/#a-dose-sheets-none-is-read-as-empty)). So the labels hold a TODO placeholder (a warning) and the units are missing (the error).

::: step Go to the field
Select `pet/sub-001_ses-01_pet.json` in the tree. In the Validation panel, click **Fix** on the error: the form scrolls to `ReconMethodParameterUnits` and marks it.
:::

::: step Answer both fields
Type `none` into the empty entry of `ReconMethodParameterUnits`. Then, a few rows up, replace the `TODO` of `ReconMethodParameterLabels` with `none`. Click **Save** above the form.
:::

{{ clip("l09-fix", "Clicking Fix on the PET error, typing none for the units and the labels, saving, and validating again: two errors left.") }}

### The eye tracker's screen

{{ figure("l09-eye-error", "The first eye's recording, plotted, with its error: the events file of its run must say how the stimuli were shown.") }}

Gaze recorded on a screen means nothing without the screen: where its origin is, how far away, how large, at which resolution. BIDS asks for these four fields in the sidecar of the events file of the run the eye was recorded during, as `StimulusPresentation`. The sample's resting run has no events file, so the validator cannot find them, once per eye. (Its message shows `{path}` where the file's name should be: [Known issues](/help/known-issues/#the-eye-tracking-error-shows-its-template).)

No file BIDS Manager reads holds the screen, so the answer is yours: two small files in `sub-001/ses-01/beh/`, written in any text editor.

::: step Write the events file
`sub-001_ses-01_task-rest_events.tsv`, one row for the 199.6 seconds of rest (columns separated by tabs):

```text
onset	duration	trial_type
0	199.6	rest
```
:::

::: step Describe the screen
`sub-001_ses-01_task-rest_events.json`, with your lab's screen; the values here are an example:

```json
{
    "StimulusPresentation": {
        "ScreenDistance": 0.6,
        "ScreenOrigin": ["top", "left"],
        "ScreenResolution": [1920, 1080],
        "ScreenSize": [0.53, 0.3]
    }
}
```

`ScreenDistance` and `ScreenSize` are in metres, `ScreenResolution` in pixels, and `ScreenOrigin` says where the gaze coordinates start: the recording's sidecar says they are measured from the screen's top-left corner.
:::

::: note
**Tools** > **Fix ups...** offers to generate missing events files for the eye tracker too, but names them per eye (`..._recording-eye1_events.tsv`), which the standard does not allow: untick them ([Known issues](/help/known-issues/#fix-ups-proposes-events-files-eye-tracking-may-not-have)).
:::

### Validate again

Click **Validate dataset**. The count of errors is 0: **{{ m("fixed.validation.ok") }} valid** files and **{{ m("fixed.validation.warn") }} warnings**, most of them TODO placeholders, the subject of the next chapter.

## Deep checks, and the report

**Deep checks** in the toolbar, on by default, makes **Validate dataset** also read every NIfTI image's header and every table: turn it off for a quick check of names and sidecars while you work on a large dataset. **Validate file** and **Validate folder** follow it too. The conversion's own validation (chapter 8) ran with it. The conversion's validation (with **Write an HTML validation report** on) and `bidsmgr-validate --html` also write `validation_report.html` into the project's `.bidsmgr/` folder, a page you can send to a colleague; validating in the Editor does not write it.

## Fix ups

**Tools** > **Fix ups...** gathers repairs that apply to the whole dataset: what is missing before it can be shared, companion files the standard expects (`events.tsv`, `channels.tsv`), a `CITATION.cff` written from the dataset description, metadata repeated in every file that can move to one file at the top, and TODO placeholders to write or take back.

{{ figure("l09-fixups", "Fix up this dataset.") }}

## How a folder can be open

The chip at the end of the path bar says how the Editor has the folder open:

| Chip | Meaning |
|---|---|
| **project** | The open project: the Editor's tools and saved sidecars are recorded in its `.bidsmgr/` folder, with the files as they were. |
| **dataset** | A BIDS dataset that is not the open project, open for editing. Edits are recorded in its own `.bidsmgr/`. |
| **view only** | Open for looking only: nothing is written into the folder, and editing and the tools are off. |

**Open folder…** in the toolbar asks, for a BIDS dataset, whether to **Open as project** (the Converter switches to it too) or **View only**. A folder that is not BIDS opens for viewing only. **Back to multimodal_study** in the path bar returns to the project.

## Files that are not data

A dataset often keeps files the standard does not describe, such as session notes or a lab's own logs; validation reports each as not part of the dataset. Leave them out with the tree's right-click, **Ignore in validation**: [Leaving files out of validation](/guides/ignoring-files/).

::: recap
- The dataset validates with 0 errors and {{ m("fixed.validation.warn") }} warnings.
- The PET sidecar says its reconstruction had no parameters; the resting run's events file describes the eye tracker's screen.
- Next, the warnings: [Editing metadata](/learn/10-editing-metadata/).
:::
