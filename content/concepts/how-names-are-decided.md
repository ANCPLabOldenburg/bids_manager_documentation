---
title: How names are decided
display_title: How names are *decided*
lede: Where each part of a proposed BIDS name comes from. For MRI, the datatype and suffix are decided from how each series was acquired, not from what someone called it, because a name typed at the scanner is the part of the raw data most often wrong.
description: How BIDS Manager proposes the subject, session, datatype, suffix, task and run of each recording, and why it names MRI series from their acquisition parameters.
---

A BIDS name is a list of entities followed by a suffix: `sub-001_ses-01_task-rest_run-1_bold.nii.gz`. A scan proposes each part separately, from what the raw data says. Every part can be changed in the scan table before converting; the name is then rebuilt from the parts, and the standard decides what is allowed.

## Why a name typed at the scanner cannot be trusted

A series name such as `ses-pre_T2w` is chosen by a person at the scanner console: whoever set up the protocol, or whoever copied it from another study and changed it. People make mistakes there, and the scanner never checks them. A protocol made from a T2-weighted one and changed into a FLAIR often keeps its old name; a copied protocol keeps the task of the study it came from; two sites spell the same sequence differently. A converter that names series from these strings writes the mistake into the dataset, under a name that looks right.

What the scanner records about how it acquired a series does not have that problem. The echo and repetition times, an inversion pulse and its time, the readout, the number of volumes, the diffusion gradients, the phase-encoding direction and the image type are written by the scanner from what it actually did. A FLAIR has an inversion long enough to null the fluid whatever its name says.

That is why BIDS Manager has its own **parameter classifier**. It reads those parameters for every MRI series, weighs the evidence for each possible name, and decides; the series name is one piece of evidence among many, with a modest weight. dcm2niix's guess, made from a few header strings, is kept as a second opinion: when the two agree the name is confirmed, and when they disagree the parameters win if they are sure.

The sample below is real: three series of the advanced MRI sample, each judged by its name alone, by dcm2niix's guess, and by its acquisition parameters.

{{ ref.naming_demo() }}

The first is the case this page is about: the operator called it `T2w`, the parameters show a FLAIR, and a converter that trusted the name would have written a FLAIR under a T2w name. In the second, dcm2niix's guess is the one that is wrong, and the parameters agree with the operator. In the third, everything agrees.

## The chain, in the order it runs

For each DICOM series of an MRI, the scan runs these steps. A later step replaces an earlier name only where it says so.

1. **Your scan rules with Force** (**Settings** > **Scan rules**). A rule matches the series name, by part of it or by a regular expression; the first matching rule wins, with confidence 0.95. Nothing later replaces it.
2. **dcm2niix's guess.** dcm2niix reads each series once, writing only the sidecar, and proposes a name from its header strings (confidence 0.85). Its answer is also kept as the second opinion for step 5.
3. **Your scan rules without Force**, for the series dcm2niix did not name (confidence 0.60).
4. **The name patterns**, for the series still without a name: the series name matched against common sequence names (`mprage`, `bold`, `dwi`, `flair`...), at confidence 0.40 or 0.45. Scouts and scanner reports are recognised here and left out.
5. **The parameter classifier** ([The classifier](/reference/classifier/)), with **Settings** > **Classification** > **Use the acquisition parameters** set to **To name the series** (the default). It scores every MR image series from its parameters, then looks at the session as a whole (a single-band reference before its run, a reversed-phase reference of a run, the two inversions of an MP2RAGE, a phase image beside its magnitude). Then it decides, against dcm2niix's guess:

   | When | The name used |
   |---|---|
   | The parameters and dcm2niix agree | that name, confirmed |
   | The parameters are sure (confidence 0.80 or more) and dcm2niix says otherwise | the parameters' name; the row notes dcm2niix's suggestion |
   | The parameters are unsure (0.40 to 0.80) | the parameters' name; but dcm2niix's when the series name agrees with dcm2niix, and the name from steps 1 to 4 when there is no dcm2niix guess and the series name says otherwise; marked to check |
   | The parameters have no opinion (below 0.40) | the name from steps 1 to 4 stays; marked to check |

   It names MR images in `anat`, `dwi`, `fmap`, `func` and `perf` only. It never replaces a name given by a forced scan rule, and leaves alone spectroscopy, PET, CT, the diffusion maps a scanner computes, and any series already named in another datatype. A contrast agent it finds is added as `ce-<agent>`.
6. **Header rules for particular series.** A diffusion series whose name marks it as a b0 reference, and which has fewer than half the volumes of the session's diffusion run, goes to `fmap` as `epi`. Spectroscopy is named from its header (`svs`, `mrsi`) unless dcm2niix or a scan rule named it; a water reference is named `svs` too, and you set `mrsref` yourself ([Naming recordings](/learn/05-naming/)). A PET series named by nothing else gets `pet` from its DICOM modality. A CT series and a series without an image (a report, a raw data object) are left out.
7. **Your exclusion rules** (**Settings** > **Scan rules**) leave out the series they match.

In short: a forced rule first; then the parameters, where they are sure or agree with dcm2niix; then dcm2niix's guess; then your other rules; then the name patterns. With the classifier set to **Only to report**, step 5 records its verdict in the **confidence** and **Why this name** of each row but names nothing; set to **Not at all**, it does not run.

## Seeing and changing the decision

The **confidence** column of the Table view shows how sure the decision was (green from 0.80, amber from 0.40, red below, by default). **Why this name**, in **Properties**, lists the evidence for and against the name, which step decided, and the other names considered, with **Use** buttons to switch to one of them ([Naming recordings](/learn/05-naming/)). Every threshold and weight is a setting, and the evidence rules can be exported, edited and loaded back ([The classifier](/reference/classifier/)).

## Subject

| Data | How the subject is found |
|---|---|
| MRI and PET DICOM | Series that share a patient ID, a given name or a family name in their headers are one participant; values an anonymiser writes, such as `ANONYMOUS`, are ignored. Subject labels are numbered in the order of the patient IDs: `sub-001`, `sub-002`. |
| EEG, MEG, eye tracking | A `sub-<label>` folder or file name, if there is one; otherwise the first folder under the raw folder (or, for a file directly in it, its name) tells the recordings of one participant apart. Subject labels are then numbered `sub-001`, `sub-002` in the order found, separately from those of the DICOM data. |

Different sources rarely agree on who a participant is: a scanner writes a pseudonym or a name, an EEG folder is named after a code. That is why the multimodal sample's scan proposes four subjects for one participant, and why the course's first edit sets them to one ([The scan table](/learn/04-scan-table/)). When a second batch of data comes back numbered from `sub-001` again, select its rows, right-click and choose **Give new subject numbers...**: each person gets the next free number, in order of acquisition, in one step you can undo.

## Session

| Data | How the session is found |
|---|---|
| MRI and PET DICOM | Per participant, each study (its identifier, date and time) is a session, when there is more than one; two studies on one day are two sessions. |
| EEG and MEG | A `ses-<label>` folder wins. Otherwise, per participant, recordings made on different days are different sessions. |

A participant scanned in one study (MRI and PET), or on one day (EEG and MEG), gets no session, unless you set one. A dataset may mix participants with and without sessions only if you want it to; the [Overview](/learn/06-checking-before-converting/) flags subjects without a session among subjects with sessions, and sessions on the same day.

## Task and run

| Data | How they are found |
|---|---|
| MRI | From the series name, when it says the task (for example `func-bold_task-rest` in the ReproIn convention, or `task-rest` anywhere). A repeated series of the same name gets a run number. |
| EEG, MEG | From the file name: `task-rest_run-1`, `task_rest_run_01`, or the part before `run`. A name like `S001R03` gives the run, and the task becomes the file name (`S001R03`), because nothing in it says what the task was: set it yourself. |

The task is the part a scan most often gets wrong for EEG and MEG, because file names were not written for it. Read the **task** column before converting.

## What is left out

Some series are not data: scout images, scanner reports, and maps the scanner computed (a diffusion tensor, a perfusion map). The scan unticks them and says why (hover the row, or show the **issues** column); the [Overview](/learn/06-checking-before-converting/) lists them. A scout, a report, a computed map, a CT series or a series without an image stays out of the conversion even when ticked; a repeated series the scan suspected of being aborted can be ticked and converted. The extra files dcm2niix writes beside a real image are dropped during the conversion (**Settings** > **Convert** > **Skip residual volumes**).

## What the standard decides

Whatever the source of a name, the schema of the standard checks it: which entities a datatype and suffix may have, in which order they are written, whether a value is a label (letters and digits) or an index (a number). A row whose name breaks the standard is marked as a warning or an error in the table, with the reason in **issues**, before anything is converted.
