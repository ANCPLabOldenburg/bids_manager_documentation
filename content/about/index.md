---
title: Why BIDS Manager exists
display_title: Why BIDS Manager *exists*
nav: Why it exists
kicker: About
lede: BIDS Manager converts raw recordings into a BIDS dataset, but converting is the smaller part of what it does. It is curation software, built for the work that turns a set of converted files into a dataset other people can use: describing it, checking it, correcting it, and keeping a record of what was done.
description: Why BIDS Manager exists, the problems in real labs it answers, and what curation means in practice in BIDS Manager.
---

## What a converter does, and what it leaves

A converter reads one format and writes another. Given a folder of DICOM files, dcm2niix writes NIfTI images and their sidecars; given an EEG recording, MNE-BIDS writes it into the BIDS layout. These tools are good at their job, and BIDS Manager uses them rather than writing its own.

What a converter cannot do is know what is not in the files, or notice what is wrong with them. In a lab, that is most of the work. Here are the same situations, with a converter alone and with BIDS Manager. Each happens on the sample data the course and the guides use; switch between the two to compare.

{{ ref.compare() }}

## What happens in real labs

**Metadata nobody records.** BIDS asks for facts no scanner or amplifier writes down: who made the dataset and under what licence, what the participant was asked to do, which electrode was the reference, how much tracer was injected and when. A converter leaves these out, or writes `n/a`, and the file looks complete. The answers exist, on a dose sheet beside the scanner, in a protocol document, in someone's memory; they need to be asked for once and written into every file that needs them.

**Sources that disagree.** One participant visits an MRI scanner, a PET camera and an EEG lab. The scanner names them by a hospital ID, the EEG folder by a code, the eye tracker not at all. Converted one by one, they become three subjects. A run that was aborted and repeated sits beside the good one; a fieldmap belongs to the second run, not the first; two series would get the same file name and one would overwrite the other.

**Identifiers left in the files.** Removing the name from a sidecar is easy to remember. The patient ID copied into a participants table, the birth date inside a spectroscopy file, a subject label made from initials, a face that can be rendered from a head scan: these are easy to miss.

**Mistakes that do not announce themselves.** None of the above makes a converter fail, and many of them pass validation. A dataset can be valid BIDS and still say something false about its recordings, or lose a recording, or link a fieldmap to nothing. They are found months later, by whoever analyses the data, or not at all.

**Work that is never finished.** Participants arrive over months. A table is curated, then a new batch comes in. A sidecar is corrected after a reviewer asks. Without a record of what was done, every round starts from the beginning, and nobody can say afterwards what changed.

## Metadata annotation: describing what the raw files don't capture

A BIDS dataset is more than its images and recordings: every one of them carries a sidecar, and the standard says which of its fields are required, recommended or optional, for each kind of file. A converter fills the fields it can read from the raw data. The rest, often the ones that matter most to whoever reuses the data, someone has to write: what the participant was asked to do, how the EEG was referenced, how much tracer was injected, who made the dataset and under what licence.

BIDS Manager treats that writing as part of the work, not as an afterthought:

- **It asks once, at the right level.** The dataset description for the whole dataset; a template for each kind of file (every `*_bold.json`, every `*_eeg.json`), written into every file of that kind; a value for one recording in **Properties**; dose sheets and participant spreadsheets imported as the lab keeps them.
- **It shows where every value comes from.** In the BIDS preview, before converting, and in the sidecar forms after, a value is marked as read from the recording, written by BIDS Manager, given by you, or still to answer.
- **It keeps what is missing visible.** A field nobody answered is written as a TODO placeholder rather than left out, so validation counts it and the sidecar search finds it, until someone replaces it.
- **It lets you correct afterwards.** The Editor shows every sidecar as a form of the standard's fields, with their levels, and finds and fixes a value across every file at once.

Here is one sidecar of the course's sample after chapter 10, each value tagged with where it came from:

{{ ref.hero_dataset("bold") }}

## What curation means in BIDS Manager

Curation is everything between the raw folder and a dataset you would hand to someone else. In BIDS Manager each part of it has a place:

| Curation task | Where it happens |
|---|---|
| See every recording before anything is written | The **scan table**: one row per recording, with the subject, session, task and BIDS name proposed for it, and the reason for each name. |
| Reconcile what the sources disagree about | Editing the table, **Bulk edit** for many rows at once, new subject numbers for a second batch, and the **Overview**, which compares subjects and points out what differs between them. |
| Give the facts the raw files don't capture | **Dataset metadata**: the dataset description, a template for each kind of file, a value for one recording in **Properties**; dose sheets and participant spreadsheets imported as they are. |
| See what is still unanswered | **TODO placeholders** in the fields the standard asks for that nobody answered, wherever a field can hold one, counted by validation until they are replaced. |
| See the dataset before it is written | The **BIDS preview**: every file the conversion will write, and each value in it coloured by where it comes from. |
| Check the result | **Validation** against the standard, each finding shown in the file and field it is about; the **quality check** of every anatomical and diffusion image. |
| Correct the dataset afterwards | The **Editor**: sidecars and tables as forms; renaming an entity, restructuring, sessions and deleting, each repairing every reference to the files it moves; finding values and fixing them in every file at once. |
| Keep identities out | Identifiers removed from every sidecar and spectroscopy file the conversion writes; **defacing** of anatomical images. |
| Keep a record | The **project**: every scan, every edit to the table (which **Undo** takes back), every change the Editor makes with the files as they were, and a log of each run (the newest 200), kept with the dataset. |

The course follows these steps in order on one sample dataset: [Learn BIDS Manager](/learn/).

## Who it is for

- **Researchers converting their own studies**, who want a dataset that is right without learning each converter's options.
- **People who look after data for a lab**, who convert the same kind of study again and again, and need to know what was done to each dataset.
- **Anyone preparing data to share**, on OpenNeuro or elsewhere, who has to remove identifiers and describe the dataset properly.
- **Anyone who inherits a dataset**, and needs to understand it, check it and correct it.

## What it does not do

BIDS Manager does not analyse data: it does not preprocess images or recordings, and the quality check is a screening, not a pipeline. It does not upload anything; datasets stay on your computer until you send them. And it does not replace looking at your data: it puts the data in front of you, and makes the decisions visible.

## Read on

- [Mistakes it catches](/about/mistakes/): the silent failures BIDS Manager is built to prevent, kind of data by kind of data.
- [The project](/about/project/): the engines it uses, what it does with your data, who makes it, and its licence.
