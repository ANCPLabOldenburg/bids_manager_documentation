# Media still to record

Every figure on this site is generated from the running application by
`tools/make_media.py`, so a screenshot cannot go stale. Two things that tool
cannot produce are a moving image and anything outside the app, and this file is
the list of them.

The placeholders and the red "video wanted" notes were **removed from the pages**
on 2026-09-07, at the user's request, so nothing half-finished is on display.
Each entry below records where the media belonged and what it was meant to show,
so it can be put back once recorded.

## How to put one back

1. Record it. `tools/make_media.py` has an `encode()` helper that assembles a
   frame sequence into an mp4; there is no ffmpeg on this machine, but the
   `imageio-ffmpeg` wheel carries a self-contained binary (see the module
   docstring). For anything where the pointer is the subject, record the screen.
2. Write the file to `assets/features/<id>_dark.mp4` and `_light.mp4`, or
   `_dark.png` and `_light.png` for a still.
3. Put a `<figure class="media-figure">` back at the line named below, using the
   `feature-video` component for a clip or `feature-shot` for a still, and give
   it the caption text recorded here.

---

## Stills that were never captured

These had no image at all: the figure was an empty placeholder box.

### `github_new_issue`

* **Page:** `about.html`, section `#issues`, under "How to open an issue"
* **Was at:** line 1017 before removal
* **Meant to show:** The New issue form. A title, a description of what you expected and what happened, and the version you are running are enough to start.

### `pet_timeactivity_curve`

* **Page:** `tutorial-pet.html`, section `#look`, under "Dynamic scans, and why the axis is in seconds"
* **Was at:** line 1018 before removal
* **Meant to show:** A time-activity curve. The x axis is seconds, so the uneven frame spacing is visible: short frames early while the tracer arrives, long frames late. This sample cannot demonstrate it, since it has a single frame.

### `convert_refusal`

* **Page:** `tutorial.html`, section `#step-collisions`, under "When it does not, the name turns red"
* **Was at:** line 1081 before removal
* **Meant to show:** The conversion refusing to start. The message names the filename two recordings are competing for and lists the source files behind them, so you know which rows to go back to. Nothing has been written at this point: the refusal happens before the first file is created, not part way through.

### `conversion_log`

* **Page:** `tutorial.html`, section `#step-report`, under "Read what the conversion reported"
* **Was at:** line 1498 before removal
* **Meant to show:** The log after a run that mostly succeeded. A converted row and a skipped row are both visible, and the skipped one carries its reason. Everything done on your behalf is recorded here, which is what lets you audit a conversion afterwards instead of taking it on trust.

## Clips wanted where a still is already doing the job

These figures DO have a real, current screenshot and are fine as they stand.
The note said a moving image would explain it better. Nothing is missing from
the page; this is a wish list.

### `tutorial-eeg.html` &rarr; `#metadata`

* **Under:** "The metadata an EDF file cannot hold."
* **Was at:** line 449 before removal
* **The still that is there now shows:** The EEG questions, in full. Every field in the table above, in the form. The red asterisk marks what BIDS requires, EEGReference , PowerLineFrequency and SoftwareFilters among them; the amber dot marks what it recommends. Each description is the standard's own wording rather than a paraphrase, and the questions every modality shares are asked once further up.
* **A clip would add:** A clip would show the green already-answered block opening, and a tooltip appearing with the standard's wording for a field.

### `tutorial-meg.html` &rarr; `#metadata`

* **Under:** "The short list MEG actually needs."
* **Was at:** line 397 before removal
* **The still that is there now shows:** The MEG questions, in full. Short, because the FIF file answered the rest. The red asterisk marks what BIDS requires, the amber dot what it recommends, and every description in the form is the standard's own wording. The fields every modality shares, institution and department among them, are asked once further up.
* **A clip would add:** A clip would show the MEG group being opened and a tooltip appearing with the standard's wording.

### `tutorial-mri.html` &rarr; `#metadata`

* **Under:** "The metadata, and how little of it MRI needs."
* **Was at:** line 434 before removal
* **The still that is there now shows:** Mostly already answered. For MRI the work is at the top of this dialog, in the questions every modality shares, and in the task descriptions. The acquisition parameters sit folded away in the green Already answered by the conversion blocks, shown so you can check them rather than type them again.
* **A clip would add:** A clip would show the green already-answered block opening on a BOLD section, which is the fastest way to convey how much is filled for you.

### `tutorial-multimodal.html` &rarr; `#metadata`

* **Under:** "The template gets longer, not more complicated."
* **Was at:** line 241 before removal
* **The still that is there now shows:** Shared above, specific below. The colour separation is the point: everything in the upper region is a statement about the study, everything below it a statement about one kind of recording.
* **A clip would add:** A clip would show scrolling from the shared region through several modality sections, which is what conveys that one dialog covers all of them.

### `tutorial-pet.html` &rarr; `#table`

* **Under:** "What the scan worked out but did not fill in"
* **Was at:** line 418 before removal
* **The still that is there now shows:** The properties panel for the PET row. The predicted path at the top updates as you edit, and the metadata below it is scoped to this recording alone: whatever you set here overrides the study-wide answer for this file only.
* **A clip would add:** A clip would show a dropdown opening with the value read from your own file at the top of the list.

### `tutorial-pet.html` &rarr; `#template`

* **Under:** "Open the form"
* **Was at:** line 535 before removal
* **The still that is there now shows:** The PET fields. A red asterisk marks what BIDS requires; an amber dot marks what it recommends. Every description in the form is the standard's own wording, so you are reading the specification while you fill it, not a paraphrase.
* **A clip would add:** A clip would show scrolling the four PET groups and a tooltip carrying the standard's wording for a field.

### `tutorial-pet.html` &rarr; `#blood`

* **Under:** "Attach the blood curves."
* **Was at:** line 674 before removal
* **The still that is there now shows:** Three curves, linked one at a time. Whole blood, plasma and parent fraction each get their own file and their own sampling method. Leave a curve you do not have unlinked.
* **A clip would add:** A clip would show a curve being linked and the resulting filename entity changing in the BIDS preview.

### `tutorial.html` &rarr; `#step-template`

* **Under:** "Values are typed, not just text"
* **Was at:** line 1180 before removal
* **The still that is there now shows:** The metadata template. Each section covers every file of one kind at once, so a question is answered once and written into all of them. Required fields carry a red asterisk. The green Already answered by the conversion block holds the fields the conversion fills by itself, shown so you can check them rather than type them again. Every description in the form is the BIDS standard's own wording, so what you read while answering is what the specification says.
* **A clip would add:** A clip would show what a still cannot: the green already-answered block opening, and a tooltip appearing with the standard's own wording for a field.

### `tutorial.html` &rarr; `#step-companions`

* **Under:** "Attach companion and blood files"
* **Was at:** line 1329 before removal
* **The still that is there now shows:** Attaching blood data to a PET run. The three curves the standard recognises, whole blood, plasma and parent fraction, are linked separately, and each is marked as manually drawn or taken by an autosampler. That answer is not cosmetic: it decides an entity in the filename, so the preview changes to recording-manual or recording-autosampler as you set it.
* **A clip would add:** A clip would show the consequence: linking a curve and setting it to autosampler changes the entity in the filename, which the BIDS preview updates to show.
