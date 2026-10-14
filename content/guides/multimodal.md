---
title: Several kinds of data at once
display_title: Several kinds of data *at once*
kicker: Guides
lede: Convert one participant's MRI, MR spectroscopy, PET, EEG, MEG and eye tracking in one project. What is particular to a study with several modalities, and where the course covers each step.
description: Convert a multimodal study (MRI, spectroscopy, PET, EEG, MEG, eye tracking) to one BIDS dataset with BIDS Manager.
time: 10 minutes to read, the course to do
sample: Multimodal sample v2
---

The course works on exactly this case, on the multimodal sample: [Learn BIDS Manager](/learn/). This page collects what is particular to converting several kinds of data into one dataset.

## One scan for everything

A single scan reads the whole raw folder: DICOM for MRI, spectroscopy and PET, EDF for EEG, FIF for MEG, EDF again for the eye tracker (recognised by its contents, not its extension). The scan table has one row per recording, whatever its kind, and the conversion sends each row to the engine for its format, in one pass ([Scanning raw data](/learn/03-scanning/)).

{{ figure("home-curate", "The course's sample after curation: one subject, one session, every kind of recording.", hotspots=False) }}

## One participant, several identities

Each source says who was recorded in its own way. DICOM headers carry a patient ID and name, which group the MRI series; the PET scanner had its own; EEG, MEG and eye-tracking files usually carry nothing, so the folder names the subject. The scan therefore proposes several subjects for one person. Setting the **subject** column (and the **session**) with **Bulk edit…** reconciles them in two edits ([The scan table](/learn/04-scan-table/)).

Check the **subject** column of every row afterwards: the identity of an eye-tracking recording is taken from its folder, like EEG and MEG.

## Sessions

Sessions are found per source, from DICOM studies and dates and from recording dates, so a multimodal visit can come out as several sessions. Decide what a session means in your study (one visit, one day, one condition) and set it the same way for every kind of recording. The [Overview](/learn/06-checking-before-converting/) points out subjects with and without sessions, and sessions on the same day.

## Metadata per kind of file

**Dataset metadata…** asks only what applies to the kinds of file present: EEG reference and montage only with EEG, MEG questions only with MEG, the PET dose file only with PET. The dataset description and the participants spreadsheet apply to everything ([Metadata you provide](/learn/07-metadata/)).

## Linked across modalities

- **Fieldmaps** are linked to the BOLD and diffusion runs they correct ([Fieldmap links](/concepts/fieldmap-links/)).
- **Physiological recordings** of an MRI run sit beside the run.
- **An eye tracker** can be paired with the run it was recorded during ([Converting eye tracking](/guides/eye-tracking/)).
- **The spectroscopy voxel** can be shown on the participant's anatomical image in the viewer ([Viewing data](/learn/12-viewing-data/#spectroscopy)).

## PET with CT or MRI

A PET/MR study converts in one pass, the MR series as anatomical and functional runs beside the PET. The CT half of a PET/CT study is left out with a reason: BIDS has no datatype for CT.
