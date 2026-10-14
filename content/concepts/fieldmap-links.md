---
title: Fieldmap links and fMRIPrep
lede: How BIDS Manager links each fieldmap to the runs it corrects, which form of the link each version of fMRIPrep reads, and how to choose the targets yourself.
description: How BIDS Manager writes IntendedFor, B0FieldIdentifier and B0FieldSource, and what fMRIPrep and QSIPrep read.
---

## Why fieldmaps need links

A fieldmap measures how the magnetic field was distorted during a session, so that the functional, diffusion and perfusion images taken in it can be corrected. A preprocessing tool such as fMRIPrep or QSIPrep corrects a run only if the dataset says which fieldmap belongs to it. If it does not, the tool still runs, and the run is left uncorrected without an error.

BIDS has two ways to say it:

| | Written in | Says |
|---|---|---|
| `IntendedFor` | the fieldmap's sidecar | the runs this fieldmap corrects, as a list of paths |
| `B0FieldIdentifier` and `B0FieldSource` | the fieldmap's sidecar, and each run's | the fieldmap's name, and the name of the fieldmap each run is corrected with |

BIDS Manager writes both, by default.

## What each version of fMRIPrep reads

fMRIPrep finds fieldmaps through sdcflows. We tested the link forms against the sdcflows of each range of fMRIPrep releases:

| Link | fMRIPrep 23.1 to 24.1 | fMRIPrep 25.1 and later |
|---|---|---|
| `B0FieldIdentifier` and `B0FieldSource` | linked | linked |
| `IntendedFor` with a path from the subject, `ses-01/func/...` | linked | linked |
| `IntendedFor` as a BIDS URI, `bids::sub-01/ses-01/func/...` | **not linked** | linked |
| `IntendedFor` without the session, `func/...`, in a dataset with sessions | not linked | not linked |

Because `B0FieldIdentifier` and `B0FieldSource` work everywhere, a dataset with them is corrected by every version, whichever form `IntendedFor` takes. If you turn them off, choose the path form of `IntendedFor` for fMRIPrep 24.1 and older.

| Setting | Where | Default |
|---|---|---|
| **Fieldmap links** | **Settings** > **Convert**, or `bidsmgr-convert --intended-for uri|relative` | BIDS URIs |
| **Also write B0FieldIdentifier and B0FieldSource** | **Settings** > **Convert**, or `bidsmgr-convert --no-b0-field-identifier` to turn off | on |

## Which runs a fieldmap corrects

For each fieldmap, BIDS Manager chooses the BOLD, diffusion and ASL runs of the same session, in this order:

1. the runs acquired with the **same shim settings** as the fieldmap, since a new shim changes the field it measured;
2. otherwise, by **time**: each run takes the last fieldmap acquired before it, or else the first one after it;
3. otherwise every run, with the reason given.

A reversed-phase reference recorded with the diffusion sequence corrects the diffusion run only. A fieldmap that no run is matched to (a second fieldmap after the runs, when an earlier one exists, for example) corrects nothing and gets no link.

Before converting, select a fieldmap row in the Converter: **Corrects these runs** in **Properties** lists the BOLD, diffusion and ASL runs with the ones it will correct ticked, and says why. Tick or untick a run to choose yourself (the section then says **your own choice**); the same is in the row's right-click menu, with **Let BIDS Manager choose again**.

## How a fieldmap is grouped

sdcflows reads one fieldmap from several files, and refuses some combinations without saying so. BIDS Manager therefore gives one `B0FieldIdentifier` to:

- every file of one acquisition: a gradient-echo fieldmap's magnitudes and phase difference, or the magnitude part of an EPI reference (its phase part carries no link);
- both directions of a reversed-phase pair (`dir-AP` and `dir-PA`);
- a reference recorded in **one** direction only, together with the nearest run phase-encoded the other way (that run's single-band reference if it has one, else the run). An estimate needs two directions; a group of one is dropped, and fMRIPrep then does not fall back to `IntendedFor`.

A phase image (`part-phase`) carries no link, and no TODO placeholder is ever written into `B0FieldIdentifier` or `B0FieldSource`: a `TODO` in two files would link them.

## Checking the links

After converting, **Tools** > **References (IntendedFor, Sources...)...** in the Editor lists every link of the dataset from both ends, so you can see which runs have a fieldmap and which do not. **Check coherence** reports an `IntendedFor` that disagrees with the acquisition times.

On the course's sample, the phase-difference fieldmap corrects the BOLD run, and the reversed-phase reference corrects the diffusion run.
