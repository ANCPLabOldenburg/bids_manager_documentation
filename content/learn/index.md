---
title: Learn BIDS Manager
nav: Overview
lede: Fifteen chapters that take one sample dataset from raw recordings to a dataset ready to share. Each chapter starts where the previous one stopped.
description: The BIDS Manager course, in fifteen chapters on the multimodal sample dataset.
---

## How the course works

The course uses one dataset from start to finish: the **multimodal sample**, a single participant's folder with MRI, MR spectroscopy, PET, EEG, MEG and eye-tracking recordings. Every figure and every number in the chapters comes from BIDS Manager {{ version }} running on that sample, so what you see on your screen should match what you read.

Work through the chapters in order. Each one says at the top what state it expects the project to be in, and ends with a short recap of what changed. If you come back after a break, the recap of the last chapter you finished tells you where you are.

::: before
- BIDS Manager is installed: [Install BIDS Manager](/start/install/).
- The multimodal sample is downloaded and unpacked: [Sample data](/start/sample-data/#multimodal).
- About three hours for the whole course, or 10 to 20 minutes per chapter.
:::

## The chapters

### Part 1. Before anything is converted

::: cards 2
- [**1. BIDS in ten minutes** What a BIDS dataset looks like: subjects, sessions, datatypes, file names, sidecars and tables.](/learn/01-bids/)
- [**2. Projects** Create the project the course works in, and learn what BIDS Manager keeps inside it.](/learn/02-projects/)
- [**3. Scanning raw data** Point a scan at the sample's raw folder and read what it found.](/learn/03-scanning/)
- [**4. The scan table** One row per recording: read it, edit it, and set many rows at once.](/learn/04-scan-table/)
- [**5. Naming recordings** How each recording gets its BIDS name, and how to change one.](/learn/05-naming/)
- [**6. Checking before you convert** See the dataset the conversion will write, and what differs between subjects.](/learn/06-checking-before-converting/)
:::

### Part 2. Converting

::: cards 2
- [**7. Metadata you provide** What no file records: authors, licence, task descriptions, PET doses, participants.](/learn/07-metadata/)
- [**8. Converting** Choose the conversion settings, run it, and read what it did.](/learn/08-converting/)
:::

### Part 3. Working on the dataset

::: cards 2
- [**9. Validating in the Editor** Check the dataset against the standard and go to each finding.](/learn/09-validating/)
- [**10. Editing metadata** Edit sidecars and tables, search them, and undo.](/learn/10-editing-metadata/)
- [**11. Changing a dataset's shape** Rename entities, add or remove them, create sessions, delete, and keep every reference right.](/learn/11-dataset-shape/)
- [**12. Viewing data** Images, time courses, signals and spectra in the viewers.](/learn/12-viewing-data/)
- [**13. Checking image quality** The fast quality check of anatomical, diffusion and functional images, and of MEG and EEG.](/learn/13-image-quality/)
:::

### Part 4. Finishing

::: cards 2
- [**14. Sharing a dataset** Remove what identifies a person, write the README and the citation, and check readiness.](/learn/14-sharing/)
- [**15. The command line** The same workflow with the `bidsmgr` commands, for scripts and servers.](/learn/15-command-line/)
:::

## When you want the reason, not the step

The chapters say what to do and what to check. Where a step depends on an idea worth understanding on its own, they link to a page under [Concepts](/concepts/): how names are decided, how fieldmaps are linked to the runs they correct, where metadata values come from, and what the project folder records. Every control the chapters mention is also listed in the [Reference](/reference/).
