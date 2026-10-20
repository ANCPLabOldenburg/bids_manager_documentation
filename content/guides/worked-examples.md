---
title: Worked examples
display_title: Worked *examples*
kicker: Guides
group: Recipes
lede: Short recipes for what comes up in real studies, each with the tool that does it and what to check afterwards: the table, Properties and bulk edit before converting, and scan rules and templates for what repeats from study to study. The Editor's tools have guides of their own.
description: Practical recipes for BIDS Manager: bulk edits, scan rules, metadata templates and the Editor's tools.
time: 20 minutes
---

::: before
The course's chapters 4 to 11 introduce every tool used here; these recipes put them to work on situations the course does not meet.
:::

## Before converting: the table and Properties

### Give several runs the same task at once

**The situation.** The file names of an EEG study say nothing about the task (`S001R04.edf`), so the scan uses the file name as the task.

**What to do.** Select the rows of one task, across participants ({{ key("Ctrl+Click") }} adds a row), click **Bulk edit…**, choose **task**, type the task's name, and click **Apply to N row(s)**. Do the same for each task, then for the runs ([Converting EEG](/guides/eeg/) does it for 28 recordings).

{{ figure("guide-eeg-bulk", "Bulk edit naming one task for six rows of two participants.") }}

### Take a label off every row that has one

**The situation.** The scan added an `acq` label to MRI series from their protocol names, and your study does not need them.

**What to do.** Select the rows, open **Bulk edit…**, choose the entity in **Column:**, and tick **Remove this entity from the rows that have it**. **What would change** lists each name now and after; rows without the label, and rows that are not allowed to lose it, are left alone.

{{ figure("w-bulk-remove", "Bulk edit taking the acquisition label off the MRI rows.") }}

### Number a second batch of participants

**The situation.** A second batch of data comes back numbered from `sub-001` again, and would collide with the first.

**What to do.** Select the new batch's rows, right-click, and choose **Give new subject numbers...**: each person gets the next free number, in order of acquisition, in one step you can undo.

{{ figure("l05-row-menu", "The row menu, with Give new subject numbers.") }}

### Answer a field for one recording only

**The situation.** One participant's EEG used a different reference from the rest.

**What to do.** Select that row; in **Properties**, under **MINIMAL METADATA**, set the field for that recording. It overrides the dataset's answer for that row only; clearing it gives the row the dataset's answer again ([Metadata you provide](/learn/07-metadata/)).

{{ figure("l07-properties-minimal", "Properties of one row: the values that apply to that recording.") }}

## For what repeats: scan rules and templates

### Name a sequence your scanner calls something odd

**The situation.** Your site's localiser or your custom sequence has a name no tool recognises, and you name it by hand in every study.

**What to do.** In **Settings** > **Scan rules**, add a row under **Custom sequence hints**: the patterns that match the series name (comma-separated), the datatype and suffix it should get, and optionally the task. Tick **Force** only if the rule must win over everything else, the parameter classifier and dcm2niix included; without it, the rule names only series dcm2niix did not, and the parameter classifier can still rename them ([How names are decided](/concepts/how-names-are-decided/#the-chain-in-the-order-it-runs)). Every later scan applies it.

{{ figure("l03-settings-rules", "Settings, Scan rules: hints for naming series, and series to leave out.") }}

### Leave a series out of every scan

**The situation.** Your protocol records a test series, or a vendor's report, that never belongs in the dataset.

**What to do.** Add a row under **Scan exclusions**: a pattern, whether it matches the series name or the file path, and whether it is plain text or a regular expression. Matching series are left out of every scan, with a note saying which rule did it; to convert one again, take the rule out and scan again.

For scripts, the same rules are a JSON file that `bidsmgr-scan --rules-file rules.json` reads:

```json
{
  "user_hints": [
    {"patterns": ["mprage_custom"], "datatype": "anat", "suffix": "T1w", "match_mode": "substring", "force": false}
  ],
  "scan_exclusions": [
    {"pattern": "QA_phantom", "target": "sequence", "match_mode": "substring"}
  ]
}
```

### Answer the same field for every file of a kind

**The situation.** Every BOLD run of the study shares a task description and instructions, and every EEG recording the same cap.

**What to do.** In **Dataset metadata…**, open the template for that kind of file (**every \*_bold.json**, **every \*_eeg.json**) and answer the fields there. The answer is written into every file of that kind at the next conversion, and the template is kept with the scan table.

{{ figure("l07-template-bold", "The template for every BOLD sidecar.") }}

## After converting: the Editor's tools

The Editor's tools have their own guides, each made of cases like these:

| The situation | Guide |
|---|---|
| One acquisition label spelled two ways; runs written `run-1` and `run-01`; a label forgotten; a dataset to put into sessions; one participant converted as two subjects | [Fixing names and structure](/guides/names-and-structure/) |
| Files renamed outside BIDS Manager; scans tables missing; a fieldmap pointing at the wrong runs; before sharing | [Keeping a dataset consistent](/guides/consistency/) |
| Notes, logs and documents reported as not part of the dataset | [Leaving files out of validation](/guides/ignoring-files/) |
| Names, dates and devices to remove before sharing | [Anonymising metadata](/guides/anonymising/) |
| A change to take back | [Undo, redo and the history](/guides/history/) |

### Find every placeholder still to answer

**The situation.** Before sharing, every TODO must be gone.

**What to do.** **Validate dataset** counts them among the warnings, one finding per field, each with **Set a real value**; in a sidecar, the search box finds `TODO` in every field at once ([Editing metadata](/learn/10-editing-metadata/)). **Tools** > **Fix ups...** > **Ready to share** says how many fields still hold one.

{{ figure("l10-search", "Searching a sidecar: only the fields that match stay.") }}
