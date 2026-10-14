---
title: How values are inherited
lede: Two kinds of inheritance decide what a sidecar ends up holding. The standard's own rule, by which a file higher in the dataset applies to the files below it, and the order in which BIDS Manager applies your answers before converting.
description: The BIDS inheritance principle, and how BIDS Manager applies dataset, per-kind and per-row metadata.
---

## Your answers, before converting

You can give BIDS Manager a metadata value at three levels. A narrower one wins:

| Level | Where you set it | Applies to |
|---|---|---|
| The dataset | **Dataset metadata...** under the Table view | every recording the field applies to |
| A kind of file | **Dataset metadata...**, the template for one datatype and suffix (for example `func` `bold`) | every recording of that kind |
| One recording | **Properties**, with the row selected | that recording only |

In **Properties**, a field you have not set on the row shows the value it inherits, dimmed. Typing a value sets it for that row; clearing it, or typing the inherited value again, returns the row to inheriting, so a later change at the dataset level reaches it.

A template field can say **differs per recording** when the files disagree (two BOLD runs with different repetition times): the conversion then writes each file's own value, and typing one there would give them all the same.

What the data itself says (read by the converter) is not overridden by a level above unless you type a value for that field: the template shows such a field with the value the conversion will write, and **read from the data** where it cannot know yet.

## The standard's rule, after converting

BIDS lets a sidecar higher in the folder tree apply to every matching file below it. A `task-rest_bold.json` at the top of the dataset applies to every `*_task-rest_bold.nii.gz` of every subject and session; a sidecar beside a file, with more entities in its name, overrides it field by field.

```text
task-rest_bold.json                                   {"TaskName": "rest", "RepetitionTime": 2.0}
sub-001/ses-01/func/sub-001_ses-01_task-rest_bold.json  {"RepetitionTime": 1.5}
```

The run above has `TaskName` `rest` from the top file and `RepetitionTime` 1.5 from its own.

Validation applies this rule: a field answered at the top is not reported missing in the files below.

## Moving shared fields up

A converter writes every field into every file's own sidecar, so a dataset of 40 BOLD runs repeats the same `TaskDescription` 40 times. **Tools** > **Fix ups...** > **Repeated metadata** > **Move shared fields up** finds the fields with the same value in every file of a group, and moves them into one sidecar higher up, where inheritance applies them to all. Only fields that are identical everywhere are offered, so the move cannot change what any file states. It is one operation, recorded in the project with the files as they were.

It is optional: a dataset where every sidecar holds everything is equally valid, and easier to read one file at a time.
