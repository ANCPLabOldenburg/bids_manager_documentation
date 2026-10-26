---
title: Updates
lede: What changed in each release of BIDS Manager, newest first, and what to know before you upgrade.
description: Release notes for BIDS Manager, newest first.
---

To upgrade, use **Check updates** in BIDS Manager's status bar, run the installer again, or run `pip install --upgrade bids-manager` in your environment ([Install](/start/install/)). The version numbers are those of the [releases on PyPI](https://pypi.org/project/bids-manager/#history). Each change is marked:

<p class="rel-legend"><span class="rel-kind k-new">New</span> <span class="rel-kind k-fix">Fixed</span> <span class="rel-kind k-note">Changed</span></p>

::: release 1.5.2 | October 2026 | v152

A guide that shows you which button to press next; physiology from Siemens scanners with every ECG lead and the scanner trigger, aligned with the image; the first volumes of a run left out on request; entity values and subject labels taken from what the scanner was told; data and projects on network drives; sidecars written again from the recordings; and defacing and skull stripping for derivatives. The first time 1.5.2 opens, a new **What's new** window plays a short animation of each feature of the releases you did not have yet, then the 1.5.0 news if you come from an earlier version; Home's **What's new** menu opens the news of any release.

{{ clip("u-whats-new", "The What's new window of 1.5.2: the guide, the physiology of a CMRR log, then Sidecars written from the recordings, picked from the list.") }}

<p class="rel-kind k-new">New</p>

- **A guide that shows you what to press.** Switch **Guide** on in the header, beside **Settings**. It asks what you would like to do and lists the tasks of the view you are in: on Home, start a new dataset or carry on with one; in the Converter, scan raw data, check and edit the table, edit one recording's metadata, convert; in the Editor, validate, look at or edit a file, rename a subject or a session, delete recordings, remove identifying information, check image quality, undo a change. Pick a task and the guide rings the control to use, says what to do there, and moves to the next step by itself when you have done it. **Previous** and **Next** step through by hand, and **All tasks** goes back to the list. It asks again when you open a view and when a task is finished; **Not now** closes it. It is off until you switch it on. See [First launch](/start/first-launch/#let-the-guide-show-you).

{{ figure("guide-question", "The guide in the Converter, with a scan table open: the tasks it can walk you through here, the usual next one tinted.", number=False) }}

{{ figure("guide-step", "Check and edit the table, step 1 of 4: the table ringed, and what to do there.", number=False) }}

- **Physiology from Siemens scanners, every ECG lead and the trigger.** The Siemens CMRR sequences log the physiology of a run with it: the pulse, the breathing, up to four ECG leads, and when every volume was acquired. BIDS Manager now reads these logs itself. Each ECG lead is a column of its own, and the scanner trigger is a column that is 1 at the first sample of every volume of the image and 0 elsewhere, always the last column. BIDS asks for one sampling rate per file and the signals are recorded at three (ECG 400 Hz, pulse 200 Hz, breathing 50 Hz), so **Settings** > **Convert** > **Physiology** offers three ways to write them, all valid BIDS: one table per sampling rate, each with the trigger (the default); or **one table for the run**, the four ECG leads, the pulse, the breathing and the trigger last, with the slower signals either interpolated between their samples or kept as recorded (`n/a` in the rows between their samples, nothing computed). In the Editor, **Visualize** on a physiology table shows the four leads, the pulse, the breathing and the trigger together (`--physio-layout`). See [Converting](/learn/08-converting/#check-the-conversion-settings).

{{ figure("l08-settings-physio", "Settings, Convert: dummy volumes, how a physiological log is written, and cropping it to the run.", number=False) }}

{{ figure("l12-physio", "The BOLD run's ECG table with Visualize: four leads, then the pulse and the breathing, each with the scanner trigger.", number=False) }}

- **Physiology aligned with the image by the scanner's own timings.** The log records when each volume was acquired, and volume 1 of the image is volume 1 of the log (checked to the millisecond on nine real runs of 50 to 1,225 volumes). So the trigger marks exactly the image's volumes, and `StartTime` gives the time of the table's first sample from the first volume. **Crop to the run** keeps only the samples from the first volume to the end of the last (`--physio-align`). When dummy volumes are removed from the image they are removed from the log too: the trigger and `StartTime` start at the first volume kept, so the physiology stays aligned with the image. A run stopped by hand ends in a volume the scanner did not finish; the image leaves it out, and so does the trigger. A log recorded with no sensor attached still gives the trigger alone. A log knows the run it was recorded with by how they were acquired, so renaming either in the table does not separate them, and the log's **Properties** name its run.

{{ figure("l07-dummy-physio", "Properties of the BOLD run's physiological log: the run it was recorded with, and the 4 dummy volumes removed from both.", number=False) }}

- **Leave out the first volumes of a run.** Many sites record a few volumes at the start of each functional run before the signal is steady, and an analysis leaves them out. **Settings** > **Convert** > **Dummy volumes** sets how many to remove from every functional run when it is converted, and a run can have its own number in **Properties** (`0` keeps all of its volumes). The sidecar records how many were removed (`NumberOfVolumesDiscardedByUser`), the run's time in its sidecar and in the scans table becomes that of its first volume kept, its events move by the time the removed volumes took, and its physiological log starts at the same volume. Also `--drop-volumes` and the scan table's `drop_volumes` column. See [Converting](/learn/08-converting/#check-the-conversion-settings).

{{ figure("l07-dummy-volumes", "Properties of the BOLD run: 4 dummy volumes for this run, where Default would take the number in Settings.", number=False) }}

- **Keep the entity values the MRI operator chose.** Operators often name a series with BIDS entities, such as `func_task-nback_acq-mb4_run-02`, sometimes on purpose against what the scanner would suggest. Tick entities in **Settings** > **Scan** > **Entities the sequence name decides** (`task`, `acq`, `ce`, `rec`, `dir`, `run`, `echo` and more), and where the series description or protocol name gives a value for one, that value is used instead of BIDS Manager's own estimate, as long as it is valid for the entity and the recording. An entity the name does not mention keeps the estimate. Subject and session never come from a series name, because a typo would move a recording to another person (`--name-entity`). See [Scanning](/learn/03-scanning/#settings-that-change-a-scan).

{{ figure("l03-settings-name-entities", "Settings, Scan: the entities whose value the series name decides, where the operator wrote one.", number=False) }}

- **Subject labels from the participant's ID or name.** Subjects are numbered by default (`sub-001`). **Settings** > **Scan** > **Subject labels** takes the label from the DICOM header instead: the patient ID, the given name or the family name, made into a valid label (`OL_3844` becomes `sub-OL3844`, `Müller` becomes `sub-Muller`). A participant whose field is empty or anonymised is numbered, and two participants whose values give the same label are kept apart (`Smith`, `Smith2`). Which recordings belong to one participant is decided as before: only the label changes. A label is part of every file name, so for a dataset you will share, choose the patient ID rather than a name (`--subject-from`).

{{ figure("l03-settings-subjects", "Settings, Scan, Subject labels: numbers, or the patient ID, the given name or the family name from the DICOM header.", number=False) }}

- **Data and projects on network drives.** Raw data or a project on a network drive now converts on Windows, on a drive letter mapped to a share or a `\\server\share` path. The conversion gathers each series into a folder of file links, and Windows does not follow a link stored on a network share, so dcm2niix found no images there; a series on a share is now copied to a local temporary folder instead. Mapped drive letters are kept as you wrote them, a network timeout fails only the series it hit, and a drive that is not connected is reported as such. On macOS and Linux nothing changes: a network drive already worked.
- **Sidecars from the recordings.** A sidecar lost or never written is written again from what is still there: the data it was converted from (converted again in a temporary folder), the file's own header (a NIfTI image's timing, an EEG or MEG recording's acquisition), your answers and the sidecars that link to it, never over a value a sidecar holds. Every field is shown with where it was read; the values follow the BIDS version chosen in **Settings** > **Validation**; any image or recording BIDS Manager reads gets one, named the BIDS way or not. **Also add to existing** completes the sidecars you have. **Tools** > **Check and repair** > **Write sidecars from the recordings...**, the tree's right-click, and `bidsmgr-sidecars`. See [Writing sidecars from the recordings](/guides/sidecars/).

{{ figure("g-sidecars-dialog", "Sidecars from the recordings for a BOLD run whose sidecar was deleted: every field with where it was read.", number=False) }}

- **Defacing and skull stripping in derivatives.** A preprocessed image carries the face of the scan it came from, such as fMRIPrep's `desc-preproc_T1w`. Tick **Include derivatives** in **Tools** > **Deface...** or **Remove the skull...** and the images in `derivatives/` are offered too, grouped by pipeline. A stripped one goes to `derivatives/bidsmgr-skullstrip/` with its description plus `brain` (`desc-preproc` becomes `desc-preprocbrain`), and masks and segmentations are left alone (`bidsmgr-deface --include-derivatives`). See [Defacing and skull stripping](/guides/defacing/#images-in-derivatives).

{{ figure("g-strip-derivatives", "Remove the skull with Include derivatives ticked: the raw images, and fMRIPrep's preprocessed T1w, grouped by where they are.", number=False) }}

<p class="rel-kind k-fix">Fixed</p>

- **The four ECG leads of a CMRR log are four columns.** They were written as one column four times too long, the leads interleaved, and the trigger was a constant 1, a flat line.
- **Acquisition values land in the recording's sidecar only.** With dataset or datatype values in the recording metadata file, `bidsmgr-metadata` wrote fields such as `Manufacturer`, `EEGReference` and `InstitutionName` into every sidecar beside an EEG or MEG recording: its events, channels, electrodes and coordinate system, and the physiology and eye-tracking sidecars. The GUI's **Dataset metadata** was not affected ([issue 187](https://github.com/ANCPLabOldenburg/BIDS-Manager/issues/187)).

<p class="rel-kind k-note">Changed</p>

- **A physiological log is one table per sampling rate** by default: `_recording-ecg_`, `_recording-cardiac_` and `_recording-respiratory_physio.tsv.gz`, each with the trigger last. 1.5.1 wrote one table per signal, the trigger on its own.
- The scan table has one more column, `drop_volumes` (67 in all).
- **Two multimodal samples in Home's sample menu.** The multimodal sample is version 3: its BOLD run's physiological log is cut to the run's 60 volumes, as the image is. [Multimodal sample 2](/start/sample-data/#multimodal-2) holds the same recordings as one participant over four visits, with one identity in every file and real dates.
- **An eye tracker joins its folder's participant.** An EyeLink file names no participant, so the scan gave it a subject of its own every time. It now takes the subject of its `sub-` folder when everything else in that folder was given one and the same subject, and keeps a number of its own otherwise, so two people are never put together by the scan.
- **What's new knows where you come from.** It shows the news of every release since the version that last ran, one after the other, and keeps each release's news in a menu, in the window and on Home.

<p class="rel-kind k-note">Before you upgrade</p>

- **Physiology converted before 1.5.2** has the ECG leads merged and a flat trigger. To write it again, delete the run's `_physio` files in the Editor (right-click, **Delete this recording...**), then run the conversion again: with **Existing subjects** on **Skip**, the default, only what is missing is written ([Converting](/learn/08-converting/#check-the-conversion-settings)).

:::

::: release 1.5.1 | October 2026 | v151

Anonymisation chosen by purpose and by subject, scans and sessions tables for every kind of recording, granular control over what validation leaves out, an Undo and Redo that walk the whole history, and installers that need no administrator rights. Validation also checks more than before, so read **Before you upgrade** at the end of this card.

<p class="rel-kind k-new">New</p>

- **Anonymise metadata.** **Tools** > **Anonymise metadata...** in the Editor removes what identifies a participant from the dataset's metadata, in every kind of file: sidecars, tables, recording headers, photographs. You choose what by purpose (names and IDs, ages, dates and times, the site, devices, DICOM UIDs, traces of the conversion, photographs) and where (the files at the top, subjects, sessions), and every change is listed before anything is written. Dates are shifted, not removed: every date of a participant moves back by one number of whole weeks, so intervals and weekdays are kept. The recorded data are never changed, and the whole run is one step you can undo and redo. Also after every conversion (**Settings** > **Convert**, **Anonymise the metadata, last:**) and from a terminal (`bidsmgr-anonymise`). See [Anonymising metadata](/guides/anonymising/).

{{ figure("g-anon-dialog", "Anonymise metadata: what to remove by purpose, where, and every change it would make.", number=False) }}

- **Scans and sessions tables for every recording.** A session's `_scans.tsv` now lists every file the standard counts as a recording, whatever its datatype and whether BIDS Manager converted it: behaviour, eye tracking and fNIRS included. Each subject with sessions gets a `_sessions.tsv` with when each session began. **Tools** > **Scans and sessions tables...** writes them for a dataset that has none or whose tables have fallen behind, without touching the rows and columns already there. On by default after a conversion (**Write scans and sessions tables**). See [Keeping a dataset consistent](/guides/consistency/).
- **Leaving files out of validation, file by file.** Right-click a file or folder in the BIDS tree, **Ignore in validation**, and choose how widely: this file, with its sidecar, its folder, the same name in every subject, or every file of an extension the standard does not use, each with the number of files it hides. **Stop ignoring** brings back any selection in one step. Ignored files are dimmed in the tree, and **Tools** > **Ignored files...** lists every line of `.bidsignore` with what it hides. See [Leaving files out of validation](/guides/ignoring-files/).

{{ figure("g-ignore-menu", "Ignore in validation, on one file: each way to ignore it, with how many files it would hide.", number=False) }}

- **Undo and Redo walk the whole history.** Right-click **Undo** or **Redo** to list the steps, newest first, and go back or forward several at once. An undo removes the folders the step created and puts back the ones it removed. See [Undo, redo and the history](/guides/history/).

{{ figure("g-history-menu", "Right-clicking Undo: the steps of the history, newest first.", number=False) }}

- **Leave entities out of proposed names.** **Settings** > **Scan**, **Leave out of proposed names**: tick an entity such as `acq-` and the scan stops adding it, except where the standard requires it or where it is what tells two recordings apart. A scan table already open is offered the change as one step (`bidsmgr-scan --drop-entity`).
- **Check coherence** says what the **Scans and sessions tables** tool would add, groups its findings by kind, pairs a file renamed outside BIDS Manager with the row that still names the old file, and ticks only the repairs that lose nothing. See [Keeping a dataset consistent](/guides/consistency/).

{{ figure("g-coherence", "Check coherence after a T1w was renamed in the file manager: the row paired with the new name, a missing scans row and sessions table, and a TaskName to review.", number=False) }}

- **Empty folders can be deleted** from the BIDS tree's right-click menu.
- **Installers 2.0**, built on uv: no administrator rights, everything in one folder in your home, and more systems than before: Intel Macs as well as Apple silicon, Linux on ARM64 as well as x86_64, Windows 11 on ARM as well as x64. Intel Macs were checked through Rosetta, and Linux and Windows on ARM are not tested yet ([Install](/start/install/#systems)). Running the installer again updates; its menu also uninstalls. **Check updates** uses the installer's own tools, and moves to a newer Python when a release needs one.

<p class="rel-kind k-fix">Fixed</p>

- **The preview stays in front on macOS.** Clicking anything inside the preview window (the shortcuts list, the quality check) sent it behind the main window.
- **Undo leaves no empty folder.** Undoing a subject's rename or merge left an empty `sub-` folder behind.
- **A series' time is its first image's.** The scan kept the acquisition time of whichever file it read first, a minute late on a long diffusion run; it now keeps the earliest, as the converter does.
- **The PET row of a scans table has its date.** The time without a date listed under 1.5.0's known issues is gone.
- **Missing samples of a physiological recording are written `n/a`**, the standard's word for them, instead of `nan`, which validation read as a value of the wrong type. The viewers read both as a gap.
- **A trace's colour can go back to its channel type.** With one channel type in a recording, a colour once chosen in **Line style** could not be undone.
- **Validate file and Validate folder follow Deep checks.** They checked headers only in the dataset-wide validation.
- **Skull stripping from the Mac app.** With the 2.0.0 and 2.0.1 installers, the app started under Rosetta, and skull stripping failed. The app now starts natively.

<p class="rel-kind k-note">Changed</p>

- **Deep checks** is on by default.
- **Validation checks more:** the format of values (times, URIs, `bids::` links), coordinate system files, compressed tables against their sidecar's columns, and eye tracking's screen description; a `bids::` link that points at nothing is reported. It no longer reports a dataset-level `dwi.bval` as misplaced, nor raw-data fields as missing in a derivatives dataset. A thousand files in one folder validate in 18 seconds rather than 65.
- **Long lists stay fast.** The lists of errors, warnings and valid files are drawn as one list with a search: 287,000 findings on 21,663 files open in under a fifth of a second.
- **No placeholder where a field's format forbids one.** A time, a URI or a list of units cannot hold `TODO`; such a field is left out, and validation reports it as missing if the standard requires it.
- **Fix ups' metadata step** is one step of the history.
- The full-colour app icon is the default header logo.
- Once a day at most, BIDS Manager asks for a star on GitHub. **Star on GitHub** ends the requests for good; a switch in the dialog and in **Settings** > **Display** turns them off.

<p class="rel-kind k-note">Before you upgrade</p>

- **Validation may find errors it did not before**, in a dataset that was clean in 1.5.0: eye tracking without its screen description, and required fields a placeholder used to fill. The BIDS project's own validator (bids-validator) reported them already. [Validating in the Editor](/learn/09-validating/) shows how to answer both.
- **Running the metadata step again adds rows and tables**: scans rows for recordings it did not list before, and sessions tables. Rows and columns you added are kept.

:::

::: release 1.5.0 | October 2026 | v150 | Major release

One viewer for every kind of image and recording, a quality check of every anatomical and diffusion image, MRI series named from how they were acquired, and a preview of the dataset before it is written. Some of these change what a conversion writes, so read **Before you upgrade** at the end of this card.

<p class="rel-kind k-new">New</p>

- **A preview of the dataset before it is converted.** The panel left of the table, titled by the view it shows, has a third view, **BIDS preview**, that lists every file the conversion and the metadata step will write, as each converter names them. Select a file to see its predicted content, each value coloured by where it comes from: the scan, BIDS Manager, your own answers, the converter, or a TODO placeholder. The preview runs the conversion's own steps on what the scan found, and a test converts the multimodal sample and requires every predicted file and value to match. See [Checking before you convert](/learn/06-checking-before-converting/).

{{ figure("l06-preview-json", "The BIDS preview: every file the conversion will write, and the predicted content of a sidecar, each value coloured by where it comes from.", number=False) }}

- **An Overview in place of the table.** **Inspection** has two views, **Table** and **Overview**. The Overview counts what was found, compares subjects with each other (a recording most subjects have and one lacks, an extra one, a label spelled two ways, a label that looks like a name or an ID, sessions on the same day, two recordings claiming one name), and draws a grid of subjects by kind of recording. **Show** on a finding opens the table on its rows.

{{ figure("l06-overview-before", "The Overview of the multimodal sample: counts, findings worth a look, and the grid of subjects by kind of recording.", number=False) }}

- **Two more views beside the table.** **Structure** is the tree it was; **Recordings** lists each kind of recording across subjects, with one checkbox to leave a kind out everywhere. Right-click in either for the table's row menu.

{{ figure("l06-recordings", "The Recordings view: each kind of recording, and which subjects have it.", number=False) }}

- **One viewer for every kind of image and recording.** Images, PET, spectroscopy, physiological recordings, EEG and MEG now open in one viewer with one set of controls: layouts (one plane, three planes, a large view with small ones, a mosaic, 3-D), overlays and atlases, the time course of a 4-D image with its events, physiological recordings and quality plots aligned beneath it, MEG and EEG with an overview bar, filters, butterfly and scale bars, bad channels and segments written to the dataset in one step, and spectra with automatic phase. How you last looked at each kind of image is remembered. See [Viewing data](/learn/12-viewing-data/).

{{ clip("t-mri-layouts", "The layouts of the image viewer, one after the other: one plane, three planes, a large view, a mosaic, 3-D, and Planes + 3-D.") }}

- **The 3-D view** renders on the graphics card, with overlays, the crosshair, picking, and six clip planes that crop or cut away.

{{ clip("t-mri-clip", "Clip planes in the 3-D view: an axial cut through the crosshair, a sagittal cut, and the corner cut at the crosshair.") }}

- **`bidsmgr-view`** opens any image from a terminal, and `--render` writes a picture of it without opening a window, which works on a server. **Save** > **Show the command line...** in the viewer writes the command that reproduces what is on screen.
- **A fast quality check of anatomical and diffusion images.** Noise and contrast, artefacts in the air around the head, tissue separation, bias, coverage, smoothness, a face still present; for diffusion, the gradient table (flipped directions included), motion, slice dropouts and spikes. It runs in seconds with tools BIDS Manager already brings, docks beside the image, and explains every measure where it is shown. From the viewer's **QC** menu, **Tools** > **Quality check...** in the Editor, after a conversion, or with `bidsmgr-qc`. Every method and threshold is a setting. See [Checking image quality](/learn/13-image-quality/).

{{ clip("l13-qc-panel", "The quality check of an anatomical image, docked beside it.") }}

- **MRI series are named from how they were acquired.** A new classifier reads the echo, repetition and inversion times, the flip angle, the readout, the number of volumes, the b-values, the phase encoding, a contrast agent and the protocol, scores every possible name, looks at the session as a whole (single-band references, reversed-phase references, magnitude and phase parts), and decides. On 256 hand-checked series it named 99.2 % right, against 89.1 % before. The table gains a confidence column, and **Why this name** in **Properties** shows the evidence and the alternatives. It names MR images only, never spectroscopy or PET. Every number it tests is a setting under **Settings** > **Classification**, and `bidsmgr-classify` scores a table again. See [The classifier](/reference/classifier/).

{{ figure("guide-adv-why", "Why this name, in Properties: the evidence the classifier weighed for a series, and the names it considered.", number=False) }}

- **Fieldmap links that fMRIPrep finds.** Fieldmaps are linked to the runs they correct with `B0FieldIdentifier` and `B0FieldSource` as well as `IntendedFor`, grouped the way sdcflows expects. The targets are chosen by shim settings, then by time, and can be changed per fieldmap in **Properties**. See [Fieldmap links](/concepts/fieldmap-links/).

{{ figure("guide-mri-fmap", "A fieldmap's Corrects these runs, in Properties: the runs it will be linked to, which you can change.", number=False) }}

- **Eye tracking.** SR Research EyeLink recordings (`.edf`, `.asc`) convert to BIDS physiological recordings and events, one pair per eye, with the calibration, and can be paired with the run they were recorded during. See [Eye tracking](/guides/eye-tracking/).

{{ figure("guide-eye-plot", "An EyeLink recording converted and drawn in the signal viewer: gaze position and pupil size.", number=False) }}

- **A DICOM header viewer**, in the Editor and from the raw tree and the table: search the header, list the frames of an enhanced file, compare two files, and save the header as text or JSON without its identifiers.

{{ figure("l05-dicom", "The DICOM header viewer, with its search.", number=False) }}

- **Source data.** The conversion can copy each subject's raw files into the dataset's `sourcedata/` folder, as they are or as one archive per series, with a checksum list (**Settings** > **Convert**, or `--sourcedata`).

{{ figure("l08-settings-convert", "Settings, Convert page, where the source-data copy is chosen.", number=False) }}

- **A log of every run.** Each scan, conversion, metadata step and validation writes a log into the project's `.bidsmgr/logs/` folder; the history icon of the Log lists them.

{{ figure("l03-log", "The Log after a scan.", number=False) }}

- **New subject numbers** for a second batch that came back numbered from `sub-001` again: right-click its rows, **Give new subject numbers...**, in one step you can undo.
- **A preview for every kind of row**: fieldmaps as their three files, physiological recordings, spectroscopy as a spectrum, PET, ECAT, EEG and MEG.

{{ figure("l05-preview", "Preview the image: one series converted aside and shown before anything is written.", number=False) }}

- **The Editor opens any folder.** A BIDS dataset can be opened as the project, or only viewed; any other folder opens to view only, and nothing is written into it.

{{ figure("guide-adopt-view", "A BIDS dataset opened to view only: the path bar says so.", number=False) }}

- **Documents in the Editor.** README, CHANGES and Markdown files are shown the way a repository shows them, and text files can be edited; `.bval` and `.bvec` files show the gradient table (directions on a hemisphere, the b-value of each volume, and a table of volumes).

{{ figure("l12-gradients", "A diffusion run's .bval file shown as its gradient table.", number=False) }}

- **Search in sidecars**, by field name, value or description.

{{ figure("l10-search", "Searching a sidecar: only the fields that match stay.", number=False) }}

- **Nineteen themes**, in four groups, each tested for contrast; your own accent, tint, icon style and file colours over any of them. The GUI uses Inter and JetBrains Mono, which come with BIDS Manager, so it looks the same on every system.

{{ figure("theme-menu", "The theme menu.", number=False) }}



<p class="rel-kind k-fix">Fixed</p>

- **TODO placeholders follow the setting.** The scope you chose for placeholders was not saved, unticking the option still wrote them, and a narrower scope never took back what a wider one had written. The dataset now holds exactly what the setting says; your own values and `n/a` are never touched.
- **Each file is asked only for what applies to it.** Requirement levels are read from the standard for each file: a T1w without a task is not asked for `TaskName`, and `Authors` is not asked for when the dataset has a `CITATION.cff`. No placeholder is written into a field that names a file, which made every MEG recording fail validation on `AssociatedEmptyRoom`.
- **Spectroscopy sidecars get their repairs, answers and placeholders.** The lists of datatypes predated `mrs`; they are now read from the standard.
- **2-D slices are drawn to scale.** A scan with thick slices looked flattened, because slices were fitted by voxel count rather than in millimetres.
- **A scan remembers where its data is.** Choosing another raw folder could overwrite the open scan's record of where its data was. Moved data is now detected, and **Locate...** relinks it by series.

<p class="rel-kind k-note">Changed</p>

- The Converter's bottom panel is the Log alone: the old preview tree and the one-line statistics are replaced by the BIDS preview and the Overview.
- Side panels fold from a strip along their edge; panels are drawn as cards, and every divider has a grip.
- The scan table has 66 columns: the fieldmap targets and three classification columns are added at the end.
- `bidsmgr-metadata --fill-scope` accepts `none`.
- New dependencies, installed with BIDS Manager: SciPy, and eyelinkio for eye tracking. On Windows the EyeLink reader needs the Microsoft Visual C++ 2008 runtime, which the Windows installer adds.

<p class="rel-kind k-note">Before you upgrade</p>

- **Some MRI series get a different name than in 1.4.1**, because the classifier is applied by default. To keep the old names, set **Use the acquisition parameters** under **Settings** > **Classification** to **Only to report** or **Not at all**, or scan with `--classifier shadow`.
- **Fieldmaps carry `B0FieldIdentifier` and `B0FieldSource`.** `bidsmgr-convert --no-b0-field-identifier` writes `IntendedFor` alone, as before.
- **Placeholders are removed when the option is off.** With **Write TODO into missing fields** off, the metadata step removes the TODOs an earlier run wrote.
- The issues known in 1.5.0 are listed, with what to do about each, in [Known issues](/help/known-issues/).

:::

::: release 1.4.1 | September 2026 | v141

<p class="rel-kind k-new">New</p>

- **Physiological recordings open in the signal viewer.** A `*_physio.tsv.gz` is a table of numbers, and reading it as one answers nothing about the shape of the trace. It now has a **Visualize** button that opens the same viewer MEG and EEG use, with the same filters, the same spectrum and the same controls. Whether a file gets the button is decided by its sidecar rather than by its name, so a table of onsets is not offered a viewer it would have nothing to draw in.

{{ figure("l12-physio", "A run's physiological recording drawn with Visualize (in 1.5.0).", number=False) }}

- **All of this run.** BIDS splits a run's physiological data by the `recording` entity, so the cardiac trace, the belt and the trigger are three files describing one acquisition. One button loads the lot onto the fastest one's grid, each at its own `StartTime`, which is the only way to see whether the trigger lines up with the belt.
- **A viewer for MR spectroscopy.** An `mrs/` file is a NIfTI by container only: its data block is a complex free induction decay, and slices would show nothing. It now opens as a spectrum, with labelled metabolite positions, the chemical shift axis the right way round, line broadening, phasing, per-repeat stepping and the free induction decay as a second page.

{{ clip("t-mrs", "The spectrum viewer (in 1.5.0): phase turned by hand and set back with Auto phase, line broadening, and the FID.") }}

- **Line thickness and a colour per channel type**, with **Reset defaults**. Colouring by type is what makes a multi-channel view readable, and every type present in a recording now has a swatch you can change. The reset restores the shipped colours, which are theme-aware rather than fixed.
- **Fit all** puts a whole recording in the viewer in one click, on physiological recordings and spectra.
- **Dragging a trace moves through the recording**, one pixel of drag to one pixel of signal, instead of sliding the drawn segment and leaving blank space behind it.
- **Bulk edit removes any entity the schema permits**, not only acquisition, and it applies **row by row**. Select the whole study and ask for the acquisition label to go: it comes off every row that has one and is allowed to lose it, and the rest are left alone instead of the edit being refused. A `_bold` keeps its `task` because the standard requires one; an anatomical row can lose it. The dialog says how many rows it will touch before you tick anything. The Editor's **Add or remove an entity** tool follows the same rule, file by file.

{{ figure("w-bulk-remove", "Bulk edit removing the acquisition label from every row that has one (in 1.5.0).", number=False) }}

- **An entity can be taken off one row** from the Properties panel. Each entity that carries a value and is allowed to go has a remove button beside it; required ones have none.
- **The scan table opens in a sensible column order**: subject, format, session, datatype, suffix, BIDS name, sequence. A layout you have already arranged is left alone, and **Reset defaults** in Manage columns puts that order back whenever you want it.
- **The PET dose file is in the per-file panel**, inside the PET section and above blood sampling, so the fields it filled are the next thing on screen rather than in another dialog.
- **`bidsmgr-convert --pet-metadata`** reads dose and tracer metadata as JSON, flat for the whole conversion or keyed by subject. It accepts the shape pypet2bids uses, wrapper and all, so a file written for that tool works unmodified. Keys BIDS does not define are reported and dropped, never written.
- **Four Editor tools for what a validator cannot see.** **Check coherence** looks for mistakes that are valid BIDS and still wrong: a scans row naming a file that is gone, a participants row for a deleted subject, a link pointing at nothing, an index written at two widths, a value spelled two ways, a `TaskName` that does not match its task, an `IntendedFor` that disagrees with the acquisition times. Each finding shows its exact change and nothing is written until you click **Repair**. **References** shows every pointer in the dataset from both ends, which is how you find out whether a run has a fieldmap at all. **Find and replace a value** changes an entity value across the dataset, a subject or a session, and **Index widths** sets one width per index, refusing a padding that would fuse two runs into one name.

{{ figure("l11-coherence", "Check coherence on the course's converted sample (in 1.5.0).", number=False) }}

- **The Tools menu is grouped by purpose**, under six headings from *Look at the dataset* to *History*, and the tree's right-click menu uses the same groups. Headings rather than sub-menus, so every tool is still one click away.

{{ figure("l11-tools-menu", "The Tools menu, grouped by purpose (in 1.5.0).", number=False) }}

- **Tools open on a scope you choose.** Add or remove an entity, Sessions, Delete, Deface and Remove the skull used to need a tree selection first. They now offer the selection, the whole dataset, one subject or one session, narrowed to a datatype if you like, so putting every anatomical scan into a session no longer means selecting them all by hand.
- **The preview can sit beside the controls** instead of under them, in every tool that has one. One button flips it, and the choice is remembered per tool.
- **Every viewer can be made narrow.** Toolbars wrap onto a second row instead of pinning the viewer at their full width or hiding controls behind a sideways scrollbar.

<p class="rel-kind k-fix">Fixed</p>

- **A dropped sample is drawn as a break, not as a zero.** Physiological files arrive full of gaps, and drawing one as a measurement of zero puts a spike to the floor of a trace that sits nowhere near zero, which reads as an artefact in the data.
- **Opening a long recording no longer starts it zoomed into its first fraction.** The time window, the scroll and the scale are measured in the recording's own terms, so they are reset when a new one is loaded: a ten-second window carried onto a forty-minute recording opened it at its first 0.4 per cent.
- **Spectroscopy converts instead of being set aside.** It carries no image pixels, so it used to be excluded with the report objects. dcm2niix writes NIfTI-MRS and `mrs` is a BIDS datatype, so it is now a real file in `mrs/`.
- **Spectroscopy converts on Windows.** The released Windows build of dcm2niix is killed by the operating system on a spectroscopy series before it writes anything: it runs out of the stack its build reserves, and it says nothing on the way out. BIDS Manager now carries a Windows build of the same converter with enough stack, and uses it only when the released one is killed in exactly that way, so every other conversion still runs on the released build. It is removed again once the fix, which has been submitted upstream, reaches a release.
- **Spectroscopy is recognised from the DICOM header**, not only from the converter's guess. The standard MR Spectroscopy storage class, a `SPECTROSCOPY` image type, and Siemens' own spectroscopy storage are all read directly, so a spectroscopy series lands in `mrs/` even where the converter cannot help, and a sequence name that looks functional no longer sends it to `func/`.
- **Spectroscopy exported under the standard storage class was classified as nothing.** For those series dcm2niix writes the series *time* where the series identifier belongs, so its classification could not be matched back to the series it described. BIDS Manager now notices an identifier that is not one and matches on the series description instead, but only when that description names a single series, since two runs of one protocol share one.
- **Windows: classification works in deep folders, and fieldmaps are named correctly again.** A DICOM folder only a little under the Windows path limit holds files well past it, because vendor filenames are long. The converter's classifier could then open none of them, every series fell back to guessing from its name, and a fieldmap's magnitude image came out as `phasediff` on Windows while macOS and Linux said `magnitude1`. Folders are now handed over in the form Windows accepts at any length, and the classifier no longer spends a sixty-character identifier on each file it writes.
- **A converter that dies now says so.** When the classifier gets nothing back from a folder that had series to classify, the scan log names the folder, how many series went unclassified, and the exit code in words rather than as a number. Before, it read as a successful scan that had quietly classified nothing.
- **A derivative row no longer empties the bulk edit menu.** Selecting one row the standard has no rule for, such as a scanner-derived diffusion map, alongside ordinary rows took every entity out of the list, acquisition included.
- **Patient identifiers are removed from every sidecar in the dataset**, not only from PET. Name, identifier, date of birth, age, sex, height and weight are taken out as the last step of a conversion; the UIDs stay, because they trace an image back to its series and identify nobody. Spectroscopy needed its own pass, because NIfTI-MRS carries its metadata inside the image where no sidecar pass reaches.
- **Eight diffusion derivative files that silently stopped converting** under a newer dcm2niix, whose label for them changed to one the classifier read as a decision not to emit anything.
- **PET `TimeZero` is right on 22 of 23 test conversions**, up from 13. It is derived from the series time rather than the acquisition time, because the frame start times are computed as the difference between the two: taking the wrong one puts every frame out by the gap between them.
- **The Standard window tick in the spectrum viewer moves the view**, which it did not: it recomputed the range and left the view where it was, so the tick looked like it did nothing.
- **Spectroscopy passes validation.** dcm2niix writes `InversionTime: 0` for a spectroscopy series that has no inversion pulse, and the standard requires the field to be above zero wherever it appears, so every converted spectrum carried an error. A zero there means "not done" and is now removed, from the sidecar and from the NIfTI-MRS header it would otherwise be copied back from. A real inversion time is kept.
- **Channel names line up with their traces.** The names were spaced evenly down the viewer while the plot spaced the traces, so by the eighth channel a name sat a whole trace below its signal. Names are now placed where the plot draws each trace, and a name too long for the column is shortened in the middle, with the full name on hover.
- **Two fieldmap acquisitions no longer merge into one row.** Siemens XA scanners write no acquisition time, and the rows were grouped by the clock, so both acquisitions fell into one group and the conversion wrote six images, three of them under the converter's own collision names instead of BIDS ones. They are now told apart by their image types repeating, which needs no clock.
- **A phase-difference fieldmap is named `phasediff`, not `phase2`.** The suffix is now decided from the echo times in the sidecar, as the standard defines it, rather than from the converter's filename, which names the echo the image came from.
- **`IntendedFor` pairs each fieldmap with the runs that follow it**, not with every run in the session. Times written in the ISO form were misread, so `2026-09-17T09:33:59` came back as 20:26:00, and every comparison built on it was wrong without saying so.
- **No more `*_scans.tsv` rows for `.DS_Store`**, `Thumbs.db` or other files that are not recordings. Any dataset that had been opened on a Mac picked them up.
- **A physiological recording's label is valid BIDS.** The Siemens channel `external_trigger` became `recording-external_trigger`, and because the underscore separates entities, every tool that reads BIDS names saw a different file from the one written. It is now `recording-externalTrigger`.
- **A row the classifier excluded says why.** A third of the excluded rows in our test data sat unticked with an empty issues cell.
- **BIDS Manager no longer freezes after a scan or during a conversion.** Neither was the scan or the conversion itself. After a scan, loading the result blocked for 606 ms and now takes 173. During a conversion, the file trees re-registered every folder in the dataset with the operating system twice a second; they now register only what changed, and draw a folder when it is opened rather than all at once.
- **A folder that was open stays drawn after the tree refreshes**, instead of coming back as one blank row, and a click anywhere on a folder's row opens or closes it rather than only a click on its small arrow.
- **At a large font size, dialog text no longer runs over its own controls**, and the scan table's columns are sized from the text they show rather than from fixed numbers.

<p class="rel-kind k-note">Changed</p>

- **Trace thickness is automatic, and fixed at one pixel above two traces.** This is a measurement rather than a preference: a wider line cannot use the fast path a one-pixel line uses, and on a page of twenty channels that is 88 ms of drawing per frame against 13. A drag pays it on every frame. With one or two traces on screen the wider line costs nothing noticeable and is used, and the Line dialog says which case you are in instead of offering a number it would ignore.
- **`dcm2niix` is pinned to one exact version, 1.0.20260724.** The range used to allow 1.0.20260416 too, and that version cannot convert spectroscopy at all: run over the same study, it wrote 19 images and no spectra where the pinned version writes 21. An installation made while the older version satisfied the range kept it through every later upgrade, which is why spectroscopy appeared to work on one machine and not another.
- **The scan table's columns say what they hold.** One word was doing three jobs. A *modality* is how data was acquired (`mri`, `eeg`, `meg`, `pet`), a *datatype* is the folder it lands in (`anat`, `func`), and a *suffix* is what the recording is (`T1w`, `bold`), and the columns now use each word only for its own thing: `modality`, `datatype`, `sequence_kind`, `bids_name`, `bids_path`, `issues` and `participant_id`. **A scan table saved by an earlier version cannot be read**; opening one says so and asks for a new scan, rather than failing on whichever old column is touched first.

:::

::: release 1.4.0 | September 2026 | v140 | Major release

A head scan contains a face, and a face can be rendered from one. BIDS Manager can now remove it, during the conversion itself or afterwards, keep the original so the operation can be undone, and show you the before and the after side by side so you can confirm that the face went and the brain did not.

<p class="rel-kind k-new">New</p>

- **Defacing, in three places.** Tick **Deface** in Settings and every conversion removes faces from anatomical and PET images before the subject is written, so the identifiable image never enters the dataset at all. Or do it afterwards, from **Tools** > **Deface** on a whole dataset or a selection, or by right-clicking any image in the tree. Same engine in all three; only the moment differs. The engine is [niimath](https://github.com/rordenlab/niimath), whose program ships inside BIDS Manager, so there is no FSL, no FreeSurfer and no ANTs to arrange.

{{ figure("l14-deface", "Remove faces, for a whole dataset (in 1.5.0).", number=False) }}

- **Skull stripping, and it writes a derivative.** **Tools** > **Remove the skull** keeps only the brain, using either the [mindgrab](https://github.com/niivue/niivue/tree/main/packages/nv-ext-brain2print) network run through [brainchop](https://github.com/neuroneural/brainchop-cli), or a mask from the same atlas the defacer uses. The result goes to `derivatives/bidsmgr-skullstrip/` as `desc-brain`, with the `dataset_description.json` that makes the folder a real derivative dataset, and **your raw scan is left exactly as it is**. A skull-stripped image is not raw data, and a raw tree that quietly contains one is a dataset nobody can interpret. Overwriting in place is offered, and is not the default.
- **A synchronised before-and-after viewer.** Every defacing tool tells you to inspect the result and then leaves you to find your own viewer. This one is built in: two images side by side, driven as one. The crosshair, the slice, the plane, the volume, the 4-D graph, the 3-D camera, the rendering effect and the cut plane all stay together, so what you see is the difference between the two images rather than the difference between two viewers.

{{ clip("l14-deface-compare", "Before and after defacing, side by side, turning together (in 1.5.0).") }}

- **Compare any two images, not only a defacing pair.** **Tools** > **Compare images** puts any two NIfTI files side by side: raw against preprocessed, two echoes, a derivative against the scan it came from, one subject against another. Images of different sizes work too, because the crosshair is matched by position in the scanner rather than by voxel index.

{{ clip("l12-compare", "Compare images: the T1w and the FLAIR side by side (in 1.5.0).") }}

- **Choosing an image no longer sends you to the file dialog.** The picker lists the dataset's own images, in the dataset's own shape, with a filter whose words can come in any order: `014 t1` finds `sub-014/…/sub-014_T1w.nii.gz`. Derivatives are listed too, since comparing one against its source is the common case, and **Browse** is still there for a file from outside the dataset.
- **Putting the face back.** **Tools** > **Put the face back** works however many changes came afterwards, restoring from the copy kept in `.bidsmgr/` or in `sourcedata/`, and taking the deidentification entries back out of the sidecar so the image can be defaced again later.
- **The viewer opens in the layout you left it in.** The plane and the view mode are remembered between sessions, and a new scan opens in the multi-planar view, or the multi-planar 3-D view where there is a GPU, rather than on a single slice.

<p class="rel-kind k-fix">Fixed</p>

- **Checkboxes follow the theme.** An unstyled checkbox fell back to the platform control, which does not know about the palette: in the dark theme a plain unchecked box painted a light grey block that read as disabled, or as already ticked. Every checkbox and radio button in BIDS Manager now takes its colours from the theme, in every state.
- **A wide figure in the documentation sat half its width off to the left** and was clipped at the edge of the browser window.

<p class="rel-kind k-note">Changed</p>

- **Convert provenance moved to the dataset root.** It used to be written into a hidden folder inside every subject, which cost more than it was worth: deleting a subject removed every recording and left the folder standing, because BIDS Manager's own state is excluded from a deletion. It now lives with everything else BIDS Manager writes, at `.bidsmgr/provenance/`. Datasets converted by an earlier version still have theirs in the subject folder, and the Editor's delete now clears those too.
- The defacing and skull-stripping engines are ordinary dependencies rather than optional extras, because these features are reached from the GUI and somebody who installed by double-clicking an installer has no terminal in which to add one. On Python 3.14 the defacing engine has no wheel yet, so the menu entry is greyed out with the reason; everything else is unaffected.

[The defacing guide](/guides/defacing/)

:::

::: release 1.3.0 | September 2026 | v130 | Major release

The Editor stops being a place you look at a converted dataset and becomes a place you can change its shape. Entities can be added and removed, sessions created and dissolved, and recordings deleted, and every one of those carries the files that point at them along with it.

<p class="rel-kind k-new">New</p>

- **Add or remove an entity.** A recording can gain a label it should have had, or lose one it never needed: an `acq-` to tell two protocols apart, a `run-` that was only ever going to be one run. Only entities the standard permits for that kind of file are offered, so an EEG recording is never offered `echo-`, and a `_bold` is never allowed to lose its `task-`, because a file without one has no reading. The new entity is placed where the standard puts it rather than where you typed it.

{{ figure("w-add-entity", "Add or remove an entity: acq-mb8 added to the functional runs (in 1.5.0).", number=False) }}

- **Sessions can be created and dissolved.** A session is a folder and a label at the same time, which is why moving recordings into or out of one by hand goes wrong so easily. Now it is one action: pick the recordings, name the session, and the folder, the filenames, the `*_scans.tsv` and every reference move together. Taking the last session out again works the same way.

{{ figure("l11-sessions", "Sessions, set to remove the session (in 1.5.0).", number=False) }}

- **Delete recordings, datatypes and sessions.** Deleting the files is the easy half. What leaves a dataset broken is everything still naming them, so the same step removes the `*_scans.tsv` rows, the `IntendedFor` entries, the participants row of a subject with nothing left, and any folder the deletion empties. A sidecar that sat above several recordings and now describes none of them goes too.

{{ figure("l11-delete", "Delete from the dataset, with the scans rows that go with it (in 1.5.0).", number=False) }}

- **Everything is one step in the project's history.** A deletion that touches forty files is one entry in the Editor's history, not forty, with every file as it was kept in `.bidsmgr/` (the GUI has no command to undo it: [Known issues](/help/known-issues/)).
- **The preview looks like your dataset.** Before any of this happens you see what it would do, arranged the way the data is: subject, then session, then datatype, then files. Untick anything you want left alone. What follows automatically, the table rows and the references, is listed but not offered as a choice, because a half-applied cross-reference is worse than either outcome.

<p class="rel-kind k-fix">Fixed</p>

- **Renaming from a right-click now offers what you clicked.** Choosing to rename a subject from one file used to tick every file that subject has, across every datatype. It now starts with that recording and the files that belong to it, and widening is a click away.
- **Choosing to merge no longer discards your selection.** Narrowing a rename and then ticking "merge them into one subject" silently reselected everything.
- **Merging two subjects leaves nothing behind.** The folder that was merged away used to survive as an empty shell. Anything inside it that was not named after the subject, an inherited sidecar, a note you left, stayed with it, and the sidecar then described recordings that had moved. All of it now travels, and the record of how the merged subject was converted is kept beside the target's own rather than overwriting it.
- **A rename now carries everything that names the old value.** Renaming a task left `TaskName` in the sidecar saying the old one. Renaming a session left `*_sessions.tsv` listing a session that no longer existed. Fieldmap and empty-room pointers, and the `Sources` fields that record what a file was derived from, were left aimed at names nothing had. None of that was reported by any validator, which is what made it worth finding.
- **Renaming a subject fixes the whole reference, not half of it.** Where a pointer was written in the `bids::` form, the file name was updated and the folder in the same path was not, leaving a reference that resolved to nothing.

<p class="rel-kind k-note">Changed</p>

- **The power-line frequency is no longer guessed.** When nothing stated one, EEG and MEG sidecars used to be written with `PowerLineFrequency` set to 50. That is correct in Europe and wrong across most of the Americas and in western Japan, and nothing in the file distinguished it from a value somebody had measured. Filtering at 50 on 60 Hz data leaves the interference exactly where it was. The field is now written as `n/a` unless the recording's own header, the scan table, or your metadata template supplies a value. That is still valid, and it is true. **If your recordings are 50 Hz, state it once** in Dataset metadata and every recording will carry it.
- Deleting is deliberately limited to what sits inside a subject. The dataset description and the Editor's own history are not removable from the GUI, because losing either turns a dataset back into an ordinary folder.

:::

::: release 1.2.6 - 1.2.6.1 | September 2026 | v126 | Major release

<span id="v1261"></span>

The largest release since 1.0. A whole modality arrives, and the form that asks you for metadata stopped being written by hand and started being built from the standard itself.

<p class="rel-kind k-new">New</p>

- **PET support.** Positron emission tomography is now a first-class modality. PET studies scan, convert and validate alongside everything else, from either of the two formats scanners produce: DICOM, and the ECAT files that Siemens HRRT and older CTI systems write.   **Hybrid studies convert in one pass.** On a PET/MR study the MR half is ordinary anatomical and functional data, and BIDS Manager converts it in the same run. On a PET/CT study the CT half is set aside with a note explaining why: BIDS has no place for CT in a raw dataset yet.

{{ figure("guide-pet-blood", "A PET run's blood sampling, both curves attached (in 1.5.0).", number=False) }}

- **The metadata a scanner cannot know.** A PET sidecar needs around forty fields, and the scanner header holds about half of them. It records how the image was reconstructed, but not how much tracer was injected, in what form, or when. Those now have a home: a Tracer, Radiochemistry, Acquisition and Reconstruction block in Dataset metadata, with per-scan overrides in the properties panel, and the same inherit-from-the-dataset behaviour the EEG and MEG fields already have.
- **The scan reads what it can and proposes it.** Tracer, radionuclide, injected dose and reconstruction settings are read out of the source and offered as suggestions beside the fields they inform. They are never filled in silently, because a vendor writes these as free text and a wrong tracer is worse than a blank one.
- **Bring your dose table.** If the radiochemistry already exists as a spreadsheet, point `bidsmgr-convert --pet-spreadsheet` at it. Column names are matched loosely, so `Injected Dose` and `injected_radioactivity` both work.

- **A recording can state any field its file may carry.** If the standard declares a field for that datatype and suffix, the form offers it, at its real requirement level, with the standard's own description on hover.

{{ figure("l07-template-bold", "The template for every BOLD run's sidecar (in 1.5.0).", number=False) }}

- **What the conversion already answers is folded away.** The scan runs the converter once, quietly, and reads what came out, so the form can separate the fields that will be filled for you from the ones only you can answer. The settled block is still editable: correcting a value there is how you tell BIDS Manager its header was wrong.
- **The BIDS version you choose is honoured everywhere.** Not only in validation. It decides which fields the form asks for, which entities a filename may carry, and what is written into `dataset_description.json`.
- **Answers take the shape the standard declares.** A field typed as a number reaches the sidecar as a number and an array of numbers as an array of numbers, whether you typed it into the form or into a cell in the table.

<p class="rel-kind k-fix">Fixed</p>

- **Scans no longer skip DICOM files with dots in their names.** Philips exports name each file after its internal identifier, and GE Signa uses a `.img` ending. Both are ordinary DICOM, and both were being passed over, whatever the modality. If a past scan of a Philips or GE dataset came back emptier than expected, it is worth rescanning.
- **Patient details are stripped from PET sidecars.** Name, identifier, birth date and referring physician are removed on conversion. The study and series identifiers stay, so an image can still be traced back to the series it came from.
- **Numbers typed into the metadata form stay numbers.** A list of numbers, frame times or reconstruction parameters, was being stored as a list of text. Worse, opening the form and saving it rewrote values the conversion had already got right, so filling in the metadata could *add* errors to a sidecar that had been correct. Both are fixed, and a template already saved that way is repaired the next time it is applied: nothing has to be typed in again.
- **A blood table's sidecar is named for the sampling it belongs to.** BIDS requires the `recording` entity on both the table and its sidecar. It was being written on the table only, which left a valid table beside a sidecar that no tool could match to it.
- **Acquisition times with a missing leading zero are repaired.** A converter can write `11:22:1.995`, which is not a time any validator will accept, and it was copied on into `scans.tsv`, so one slip was reported twice.
- **One project's metadata stays inside that project.** Answers given for one dataset no longer follow you into the next.
- **Windows: the settled metadata block is filled in again.** On Windows, "Already answered by the conversion" came up empty for every MRI kind, while the same dataset filled it on macOS and Linux. The values were never missing from the data. The pass that measures them works inside a folder whose path could run past the length Windows allows, and the converter does not fail gracefully there: it stops without a message, and a measurement nobody could take looked the same as a measurement there was nothing to take. Those paths are now short and of fixed length. If that block came up empty for you, rescanning fills it.
- **Windows: the converter is found however you started BIDS Manager.** The dcm2niix that ships with the Python package carries a different name on Windows, and BIDS Manager looked only for the other one. Started from an activated environment a fallback found it anyway; started from a desktop shortcut or a bundled interpreter it did not, and both the classifier that proposes BIDS names and the pass that measures metadata were skipped without saying so.
- **A series whose output does not name itself is no longer dropped.** On some acquisitions, a Siemens XA30 localiser among them, the converter writes an identifier into the sidecar that does not match the one the series carries. Those outputs belonged to no row and their measurements were lost. Each is now attributed to the series it was actually converted from.
- **A dropdown inside a folded section is wide enough to read.** A menu field sized itself while it was still hidden, so a value the conversion had answered could appear as a stub too narrow to show its own text.
- **A path too long for Windows now says so.** The one failure that produced no message at all now reports the limit and the length of the path that exceeded it, so the next time it happens it is a message rather than a silence.

<p class="rel-kind k-note">Changed</p>

- The scan table gained five read-only columns carrying the PET details read from the source. They are appended, so every existing column keeps its position. In the GUI those values are offered inside the fields they inform rather than shown as columns.
- `pet2bids` is a new dependency, installed with BIDS Manager. Nothing to do on your side.
- A dataset's name now means one thing. It is the folder name, stated once when the project is created, and the GUI says what a rename would affect rather than silently keeping two answers.

:::

::: release 1.2.5 | 26 July 2026 | v125

<p class="rel-kind k-new">New</p>

- **A GPU 3-D volume renderer for NIfTI images.** The Editor's image viewer can now render a volume in interactive 3-D, in the spirit of MRIcroGL, straight on your graphics card. Load an image, switch to the **3D** or **Multi-Planar 3D** view, and orbit, zoom and pan a fully shaded volume in real time. It brings a lot to the viewer:   **A dozen looks.** Pick a rendering effect and material: Standard and Matte surfaces, Juicy shiny, Glass, X-ray, Jelly, Skull, maximum-intensity projection, Edges, opacity peeling, Shell and Topography, each with its own adjustable parameters.

{{ clip("t-mri-effects", "The 3-D effects, one after the other (in 1.5.0).") }}

- **Lighting you control**, with matcap materials (Shiny White, Clay, Bone, Titanium, Gold, Blue) and ambient, diffuse, specular and shininess sliders.
- **Cut into the volume.** An oblique clip plane and a slicer cut at any angle, with keyboard shortcuts, and a cut-face overlay shows a clean windowed cross-section at the cut while the shaded volume fills the space behind it, so a ventricle reads as real depth rather than a flat dark hole.
- **Always know your orientation.** An orientation cube and shared RAS / radiological toggles keep the 2-D slices and the 3-D render in agreement.
- **Colour-FA diffusion maps** (RGB NIfTIs) load and render in 3-D as well.

<p class="rel-kind k-fix">Fixed</p>

- **Colour-FA (RGB) NIfTIs now open.** Diffusion colour-FA maps that previously failed to load now open correctly.
- **Smoother scrolling on Linux.** Mouse-wheel zoom and {{ key("Shift+Scroll") }} slice navigation in the 3-D view were fixed on Linux.
- **A scan crash on Windows with Python 3.14.** A parallel worker-pool crash during scanning was worked around, so scans complete reliably there.
- **Rounded popup corners on Windows and Linux (1.2.5.2).** Combo dropdowns, hover tooltips and menus now render clean, fully transparent rounded corners on Windows and Linux, instead of showing a black square behind the rounded border. The popups are made transparent before their window is created, so the operating system draws them correctly on every platform.

:::

::: release 1.2.4.2 | 23 July 2026 | v1242

<p class="rel-kind k-new">New</p>

- **A much-improved NIfTI image viewer.** Inspecting a `.nii` / `.nii.gz` volume in the Editor is now far more comfortable, and images load in canonical RAS orientation so anatomy is shown the right way round:   **Scroll through the volume** with the mouse wheel or a trackpad, in both the single-slice view and the **Multi-Planar** view (formerly Tri-view). It steps smoothly in either direction. Horizontal scroll, or holding `H` while scrolling, moves through time in 4-D images.
- **Anatomical orientation labels** (L/R, A/P, S/I) are drawn around each slice, so you always know which way you are looking. Toggle them with the "Orientation labels" button or the `O` key.
- **Keyboard shortcuts** for everything, active when the viewer has focus: `A` / `S` / `C` switch the axial, sagittal and coronal views, `M` opens Multi view, `G` opens the time-series graph, and `O` toggles the labels. A "Shortcuts" button lists every gesture and key.
- The time-series graph now opens compact and stays resizable, so it no longer crowds the image.

<p class="rel-kind k-note">Changed</p>

- **Rounded hover tooltips.** The small pop-up hints that appear when you hover over a control now have rounded corners, matching the rest of the GUI.

<p class="rel-kind k-fix">Fixed</p>

- **No more crash on exit.** A Qt shutdown issue that could crash BIDS Manager when closing the NIfTI viewer or quitting was fixed.

:::

::: release 1.2.4.1 | 21 July 2026 | v1241

<p class="rel-kind k-fix">Fixed</p>

- **A sturdier copy-path menu, plus "Open in Folder".** The right-click menu in the Editor's BIDS tree was hardened, and a new **Open in Folder** action reveals the selected file or folder directly in your system file browser.

:::

::: release 1.2.4 | 21 July 2026 | v124

<p class="rel-kind k-new">New</p>

- **Faster, more precise validation.** The Editor's validation now runs on the standalone `bidsval` engine. A **Deep checks** toggle additionally reads file headers and contents for a thorough pass, while the quick structural pass keeps live editing responsive.
- **Jump straight to a problem.** When a check finds an issue, a fix / highlight button takes you to exactly where you edit it: it navigates to and tints the offending JSON field, the bad TSV cell (every one), or the matching entry in the Tree view.

{{ clip("l09-fix", "Going to the field a finding is about (in 1.5.0).") }}

- **Copy paths from the BIDS tree.** Right-click any file or folder in the Editor tree to copy its path.

:::

::: release 1.2.3 | 8 June 2026 | v123

<p class="rel-kind k-new">New</p>

- **Preview a spectrum before converting.** The Converter's scan table gained a per-row **Compute PSD** button, so you can check the power spectrum of an EEG, MEG or NIRS recording before you convert it.

<p class="rel-kind k-note">Changed</p>

- **Sensible defaults out of the box.** The scan probe and the full post-convert chain (metadata, validation, and the HTML report) are now on by default.
- **Removed the unused "Default dataset slug" setting.** In the project-first model the dataset name always follows the project folder, so the field was dead.

:::

::: release 1.2.2 | 7 June 2026 | v122

<p class="rel-kind k-new">New</p>

- **An MEG / EEG signal viewer in the Editor.** Click a recording to see a metadata card, then **Load signal** for an interactive time-series viewer: channel picking, filtering, resampling, a built-in power-spectrum (PSD) view, and a BIDS-native events overlay.

<p class="rel-kind k-fix">Fixed</p>

- **Huge tables open instantly.** TSV files now load on a background thread, so even very large or very wide tables appear without freezing BIDS Manager.
- **Validator corrections**, including multi-rate physio files that were previously flagged by mistake.

:::

::: release 1.2.1 | 6 June 2026 | v121

<p class="rel-kind k-new">New</p>

- **A `--project` option across the CLI**, plus undo / redo in the Editor and a project switcher in the header.
- **Force-EDF conversion** for EEG (re-encode to EDF on the way in).
- **Phenotype and participants codebooks.** Sibling `.json` descriptions flow into the BIDS metadata (descriptions, levels, units).
- **Unsupported formats are now visible.** Recordings in formats BIDS Manager cannot read appear as clearly-excluded rows during a scan instead of silently disappearing.

:::

::: release 1.2.0 | 5 June 2026 | v120

<p class="rel-kind k-new">New</p>

- **A project-first workspace.** A Home tab lets you create, open, or reopen recent dataset workspaces, and every curation is saved as a resumable, versioned project so you can stop and pick up later.
- **Merge-aware incremental conversion.** Re-running a conversion updates only what changed, with an on-existing policy (skip, update, replace, or error).
- **Live revalidation, project isolation, and live file trees** that update as you work.

Earlier releases (the 1.0.x and 1.1.x lines) predate these notes. See the [PyPI release history](https://pypi.org/project/bids-manager/#history) and the [GitHub repository](https://github.com/ANCPLabOldenburg/BIDS-Manager) for the full record.

:::
