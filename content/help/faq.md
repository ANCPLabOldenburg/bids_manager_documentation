---
title: Questions
lede: Short answers to the questions people ask first, each with a link to where the answer is explained.
description: Frequently asked questions about BIDS Manager.
---

## Before you start

### Do I need to know Python or the command line?

No. Everything can be done in the GUI. The commands exist for scripts and servers ([The command line](/learn/15-command-line/)).

### What data can it convert?

MRI and MR spectroscopy from DICOM; PET from DICOM and ECAT, with blood data; EEG from EDF, BDF, BrainVision, EEGLAB and GDF files and EGI MFF folders (the last two are not formats BIDS accepts, so they are converted to EDF with **Settings** > **Convert** > **Force EDF**); MEG from Elekta and MEGIN FIF, CTF and KIT; the physiological recordings Siemens scanners store with an MRI run; and EyeLink eye tracking. Spectroscopy, PET and eye tracking follow the latest version of the standard.

### Does it change my raw data?

No. BIDS Manager reads the raw folder and writes only into the project. Keep a copy of your raw data anyway: it is what you would convert again from.

## Converting

### Can I add participants later?

Yes. Scan the new data into the same project: each scan is kept as its own scan table, and the conversion adds the new subjects to the dataset. **Existing subjects** in **Settings** > **Convert** decides what happens to a subject that is already there; the default keeps its files and adds only what is new ([Converting](/learn/08-converting/)).

### Our scanner names its sequences in its own way. Will the names be right?

MRI series are named from how they were acquired, not only from their names, and each name comes with the evidence for it ([The classifier](/reference/classifier/)). For your site's own conventions, write scan rules once (**Settings** > **Scan rules**): they apply to every scan. Whatever is proposed, you can change it in the table before converting.

### Can I open a dataset converted with another tool?

Yes. **Open dataset folder…** on Home opens any BIDS dataset as a project; to only look at one, use **Open folder…** in the Editor and click **View only** ([Adopting an existing BIDS dataset](/guides/adopting-a-dataset/)).

### Which version of BIDS does it write?

The newest it knows, BIDS 1.11.1 in BIDS Manager {{ version }}. **Settings** > **BIDS version** can choose an earlier one for writing and validating.

## Working with it

### Does it work without a network, or on a server?

Yes. It needs the network only to install, to check for updates and install one you accept, to download a brain model the first time one runs, to fetch a BIDS schema version it does not ship (`--schema`), and on Linux to fetch the `libxcb-cursor0` library if the system lacks it. On a server without a display, use the commands; `bidsmgr-view --render` draws images to files ([What leaves your computer](/learn/14-sharing/#what-leaves-your-computer)).

### Is anything sent to anyone?

No data, ever. See [About](/about/project/#your-data-stays-on-your-computer).

### How do I take back a change?

In the Converter, **Undo**. In the Editor, see [The project folder and undo](/concepts/project-folder/).

### What does a TODO in my dataset mean?

A field the standard asks for that no file answered. Replace it with the real value, or take the placeholders back ([Metadata levels and TODO placeholders](/concepts/metadata-levels/)).

### Will fMRIPrep use my fieldmaps?

Yes, with the default settings, in every version ([Fieldmap links and fMRIPrep](/concepts/fieldmap-links/)).

### Is it free?

Yes, under the MIT licence. Please [cite it](/help/citing/) if it helped you.
