---
title: The classifier
lede: How a scan decides what each MRI series is, from how it was acquired, and the evidence it weighs for every name. Every number and every rule here can be changed.
description: How BIDS Manager's parameter classifier names MRI series, its settings and its rulebook.
---

## What it does

A series name is typed by a person at the scanner and can be wrong; dcm2niix, the converter BIDS Manager uses for DICOM, guesses a BIDS name from a few strings in the header, and is wrong in ways that repeat: a contrast-enhanced T1w named as a plain T1w, ASL and its M0 scan confused, maps the scanner computed converted as data. The classifier names each MRI series from how it was acquired instead, and uses dcm2niix's guess as a second opinion. [How names are decided](/concepts/how-names-are-decided/) shows three real series judged all three ways, and where the classifier sits in the order of the scan's steps.

On 256 series checked by hand, from scanners of several vendors, it named 99.2 % right, against 89.1 % with the classifier off (dcm2niix's guess, the name patterns and the scan rules).

It names MR images only. Spectroscopy, PET and CT keep the names the other steps give them, and it never replaces a name in a datatype its rules do not cover.

## Where the idea comes from

Naming MRI series from their acquisition parameters is not new: dcm2niix's guess and earlier tools do it too. Part of the inspiration for BIDS Manager's classifier came from **SWIFTCAT**, a tool that converts mostly anatomical MRI to BIDS from acquisition parameters, developed by Marta Loureiro, Rita G. Nunes and Rita Reis Nunes (Evolutionary Systems and Biomedical Engineering Lab, LaSEEB, University of Lisbon) and Patricia Clement (Department of Medical Imaging, Ghent University Hospital, UZ Gent).

BIDS Manager's classifier is its own early implementation of this idea. It works well overall, and every name it gives can be checked and changed ([Seeing why](/reference/classifier/#seeing-why)). The SWIFTCAT team is putting a lot of effort into improving the approach for MRI, testing it on clinical and heterogeneous data. SWIFTCAT is not public yet: stay tuned for its release, which could also be plugged into BIDS Manager as a classification algorithm.

## How a series is named

1. **Each series is scored alone.** The scan reads the series' acquisition parameters from its DICOM header (echo, repetition and inversion times, flip angle, readout, number of volumes, b-values, phase encoding, a contrast agent, the ASL protocol, and the vendor's private fields where they say more). Each piece of evidence for or against a name adds its weight to that name's score, and the scores become a confidence between 0 and 1.
2. **The session is looked at as a whole.** A single-band reference sits immediately before its run with the same geometry; a few-volume EPI with the opposite phase encoding of a run is that run's fieldmap; two inversions of one gradient echo are an MP2RAGE; a phase series beside its magnitude twin is the same run's `part-phase`. These add evidence, and entities (`dir`, `inv`, `part`).
3. **The name is decided**, against dcm2niix's guess:

| When | The name used |
|---|---|
| Both agree | that name, confirmed |
| The classifier is sure (confidence at or above **Name without asking above**, 0.8) and they differ | the classifier's, and the row says what dcm2niix suggested |
| The classifier is unsure (between the two thresholds) | the one the series name agrees with, and the row is marked to check |
| The classifier has no opinion (below **Leave to the other opinions below**, 0.4) | the name the other steps gave (dcm2niix's guess, a scan rule without **Force**, or the series name), marked to check |

A forced scan rule (**Settings** > **Scan rules**) wins over all of this during a scan. Naming a table again later (below) does not know which rows a rule or a hand edit named, and can rename them.

## Seeing why

The **confidence** column of the Table view shows how sure the classifier was. Select a row and scroll **Properties** to **Why this name**: the evidence for and against the name, and the other names it considered with their confidence. [Naming recordings](/learn/05-naming/) goes through it on the course's sample.

## Switching it off

**Settings** > **Classification** > **Use the acquisition parameters**:

| Choice | What happens |
|---|---|
| **To name the series** (default) | as above |
| **Only to report** | the names come from the other steps (your scan rules, dcm2niix's guess, the series name), as before 1.5.0; the classifier's verdict is recorded and shown, but not used |
| **Not at all** | the classifier does not run |

The same from the command line: `bidsmgr-scan --classifier applied|shadow|off`.

## The settings

Every number the classifier tests is a setting: the two thresholds, the weight of each kind of evidence (parameters, series name, neighbouring series), and the ranges that tell contrasts apart (the inversion time of an MPRAGE, the echo time of a T2-weighted image, the number of volumes of a BOLD run, and so on). They are listed, with their ranges and defaults, under [Classification](/reference/settings/#classification) in Settings.

From the command line, the same settings are a JSON file:

```console
$ bidsmgr-scan --print-classifier-config > classifier.json
$ bidsmgr-scan /data/raw/my_study inventory.tsv --classifier-config classifier.json
$ bidsmgr-classify inventory.tsv --config classifier.json --json
```

`bidsmgr-classify` names the series of an existing `inventory.tsv` again from the features the scan cached, without reading any DICOM, so you can try a setting on a whole study in seconds. `--apply` writes the new names into `inventory.tsv`, including over names a forced scan rule or a hand edit gave: check those rows afterwards.

## The rules

What counts as evidence for each name is a file of rules, the rulebook. Each line is one piece of evidence: a feature of the acquisition or a word in the series name, a test, a weight (positive for the name, negative against), and the sentence **Why this name** shows. Ranges named after a setting take their values from the settings above.

**Settings** > **Classification** has **Export the rules...** and **Load rules...**: export the rulebook, change a weight or add a piece of evidence in the file, and load it back. Only what differs from the shipped rules is kept with your settings, so a later version of BIDS Manager still brings its own improvements to the rest.

### The shipped rules

The rules of BIDS Manager {{ version }}, name by name. Names under `exclude/` are what the classifier says should not be converted.

{{ ref.rulebook() }}
