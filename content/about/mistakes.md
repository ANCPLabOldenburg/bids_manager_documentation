---
title: Mistakes it catches
display_title: Mistakes it *catches*
kicker: About
lede: The costly conversions are the ones that succeed, produce a dataset that looks right, and are wrong. Each of these happens without any warning when a converter is used alone. Here is what BIDS Manager does about each.
description: The silent failures of converting neuroimaging and electrophysiology data, and what BIDS Manager does about each.
---
## Whatever the data

| What goes wrong | What BIDS Manager does |
|---|---|
| Two recordings get the same file name, and the second overwrites the first | Works out every file name before converting, numbers genuine repeats, and refuses to convert while two rows still share a name |
| One participant appears as several subjects, because each source names them differently | Shows every recording with its subject in one table, where the disagreement is visible and fixed by editing a column |
| A dataset is shared with names in its headers, or with faces in its images | Removes identifiers from every sidecar and spectroscopy file the conversion writes, and defaces anatomical images during or after the conversion |
| A recording is renamed or deleted, and a scans table or a fieldmap still names it | Repairs the scans tables, the references in sidecars, the participants table and empty folders in the same step |

## MRI

| What goes wrong | What BIDS Manager does |
|---|---|
| A fieldmap without links: valid, and never applied | Links it to the runs it corrects, in the forms every fMRIPrep version reads |
| A scanner report or a computed map that is not an image fails to convert, and looks like a failed conversion | Recognises that there is no image in it and leaves it out, with the reason |
| dcm2niix writes extra single-volume copies beside a run, which a pipeline can read as data | Leaves them out by default, with a setting to keep them |

## EEG and MEG

| What goes wrong | What BIDS Manager does |
|---|---|
| A required field is written as `n/a` because the converter cannot know it, and looks answered | Asks for it once for the study |
| The heart, eye and trigger channels arrive typed as EEG | Takes a mapping of channel names to types once, for the whole study, and writes it into every `channels.tsv` |
| A study-wide answer overwrites a fact the converter read from the file | Offers what it detected as a suggestion, and writes it only where you accept it |

## PET

| What goes wrong | What BIDS Manager does |
|---|---|
| The doses BIDS requires are on a sheet, not in any file | Reads your dose sheet, or asks for each value with the standard's description |
| The time every frame is measured from is taken from the wrong clock | Derives it from the series time, from which the frame times are computed |
