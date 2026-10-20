---
title: Identifiers and privacy
lede: What in a dataset can identify a person, what BIDS Manager removes on its own, what anonymising removes and why, and what to check before a dataset leaves your hands.
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

## What anonymising removes

The conversion keeps what describes the site and the scan, because analyses and provenance use it. Much of it can still narrow down who was scanned, where and when. **Anonymise metadata** (in the Editor's **Tools**, after a conversion in **Settings** > **Convert**, or `bidsmgr-anonymise`) removes it by category, each for a reason:

| Category | Why it identifies | What anonymising does |
|---|---|---|
| Names and IDs | Names, patient IDs, birth dates and contact details, the scanner's copy of sex, age, weight and height, and the names of the people who ran the session, in `participants.tsv`, sidecars and recording headers (EDF, FIF) | removes them |
| Ages | An exact age, or an age over 89, can single out a person in a small study | writes every age over 89 as 89, or (Strict) rounds every age down to a five-year bin |
| Dates and times | The day of a scan, with the site, often identifies the visit | moves every date of a participant back by one number of whole weeks, into 1902 to 1925, so intervals and weekdays stay; Strict also sets times of day to midnight |
| The site | The institution's address, and its name | writes the address (Strict: name, department and address) as `n/a` |
| Devices | A scanner's serial number and station name identify the site | replaces them by pseudonyms, the same for the same machine everywhere |
| DICOM UIDs | Many systems build them from the scanner's number and the second they were made | replaces them by pseudonyms, the same for the same UID everywhere, so they still link images to their series |
| Traces of the conversion | Every `.nii.gz` and `.tsv.gz` keeps the time it was written and its original file name; `OriginalFile` keeps a path on the converting computer | removes them |
| Photographs | EXIF metadata holds dates, places and devices | removes it; the pixels are untouched |

Free text (a protocol name, a study description) cannot be judged by a rule; anonymising lists it **to read by hand** and changes nothing in it. The recorded data are never changed. What each category changes on a real dataset, and how to choose: [Anonymising metadata](/guides/anonymising/).

## What it leaves, and you should check

| Where | What | What to do |
|---|---|---|
| `participants.tsv` | The metadata step copies `given_name`, `family_name` and `patient_id` from the DICOM headers into it | Anonymise after the last metadata run ([Anonymising metadata](/guides/anonymising/)), or turn on **Anonymise the metadata, last** in **Settings** > **Convert**. Listed in [Known issues](/help/known-issues/). |
| Anatomical images | A face can be rendered from any head MRI, and from some PET | Deface them ([Defacing and skull stripping](/guides/defacing/)). The quality check reports **A face is visible**. |
| EEG and MEG recording files | Their headers can hold a name or a birth date, as typed at the recording | Anonymising clears the names in EDF and FIF headers, moves a FIF recording's date with the participant's others, and writes an EDF start date as EDF's own anonymous date, 1 January 1985. Check other formats' headers, and anonymise at the source if needed. |
| Free text | A task description, a note, a README that names a person or a date | Read them; **To read by hand** in Anonymise metadata lists the free-text fields of the sidecars. |
| Labels and file names | A subject label made from initials or a hospital number, a session named after a date | Rename them in the table before converting, or with **Rename entity...** after. The Converter's Overview flags task and other labels that differ for nearly every recording; it does not check subject or session labels, so read those yourself. |
| `sourcedata/` | The raw files, headers and all, when **Keep in sourcedata/** is set to copy or archive, and the images as they were before defacing if you chose to keep them there | Do not share `sourcedata/` from a dataset of people. |
| `.bidsmgr/` | The project's history, including the originals of the files an Editor step rewrote, deleted, defaced or anonymised, the date shifts of the anonymisation, and the raw folder's path | Never share it. It is listed in `.bidsignore`. |

## The DICOM header viewer

The DICOM header viewer marks the identifying values and hides them until you turn on **Show identifying values**; a copied or exported header leaves them out unless you turn on **Include identifying values**.

## Before sharing

[Sharing a dataset](/learn/14-sharing/) goes through the steps on the course's sample: the Dashboard's **Ready to share** list, anonymising, defacing, the README and the citation file, and a last validation.
