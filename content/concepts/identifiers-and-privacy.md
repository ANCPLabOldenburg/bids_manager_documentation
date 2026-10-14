---
title: Identifiers and privacy
lede: What in a dataset can identify a person, what BIDS Manager removes on its own, what it leaves, and what to check before a dataset leaves your hands.
description: Which identifiers BIDS Manager removes from a converted dataset, which remain, and what to check before sharing.
---

A BIDS dataset is meant to be shared. Raw data is not: DICOM headers carry the participant's name, birth date and patient ID, recording files carry what was typed into the acquisition software, and a head image carries a face. BIDS Manager removes what it can find on its own. You are still responsible for the dataset; the checks below are the ones that matter.

## What BIDS Manager removes

As the last step of converting each subject, from every sidecar the conversion writes:

| Removed | Kept, and why |
|---|---|
| The participant's name, ID, birth date, age, sex, weight and size | |
| The accession number of the visit | |
| The names of the referring, performing and requesting physicians and of the operator | |
| The department's address | `InstitutionName` and `InstitutionAddress`: the standard recommends them, and they describe the site, not the person |
| | The study and series identifiers (UIDs): they identify no one, and they are what traces an image back to its series |

MR spectroscopy needed its own pass: a NIfTI-MRS file carries its metadata inside the image file, where no sidecar step reaches, and the same identifiers are removed there, together with `OriginalFile`, the path of the source file on the converting computer.

## What it leaves, and you should check

| Where | What | What to do |
|---|---|---|
| `participants.tsv` | In {{ version }}, the conversion copies `given_name`, `family_name` and `patient_id` from the DICOM headers into it | Delete the three columns ([Sharing a dataset](/learn/14-sharing/)). Listed in [Known issues](/help/known-issues/). |
| Anatomical images | A face can be rendered from any head MRI, and from some PET | Deface them ([Defacing and skull stripping](/guides/defacing/)). The quality check reports **A face is visible**. |
| EEG and MEG recording files | Their headers can hold a name or a birth date, as typed at the recording | BIDS Manager does not change what a recording file holds. Check their headers, and anonymise at the source if needed. |
| Free text | A task description, a note, a README that names a person or a date | Read them. |
| Labels and file names | A subject label made from initials or a hospital number, a session named after a date | Rename them in the table before converting, or with **Rename entity...** after. The Converter's Overview flags task and other labels that differ for nearly every recording; it does not check subject or session labels, so read those yourself. |
| Dates | Acquisition dates and times in `_scans.tsv` and sidecars | Some data-sharing rules require shifting or removing them. |
| `sourcedata/` | The raw files, headers and all, when **Keep in sourcedata/** is set to copy or archive, and the images as they were before defacing if you chose to keep them there | Do not share `sourcedata/` from a dataset of people. |
| `.bidsmgr/` | The project's history, including the originals of the files an Editor operation rewrote, deleted or defaced, and the raw folder's path | Never share it. It is listed in `.bidsignore`. |

## The DICOM header viewer

The DICOM header viewer marks the identifying values and hides them until you turn on **Show identifying values**; a copied or exported header leaves them out unless you turn on **Include identifying values**.

## Before sharing

[Sharing a dataset](/learn/14-sharing/) goes through the steps on the course's sample: the Dashboard's **Ready to share** list, `participants.tsv`, defacing, the README and the citation file, and a last validation.
