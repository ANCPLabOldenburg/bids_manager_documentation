---
title: The project
display_title: The *project*
kicker: About
lede: The engines BIDS Manager drives, what it does with your data, who makes it, and the terms under which you may use it.
description: The engines BIDS Manager uses, privacy, its authors and its licence.
---

## The engines it uses

Converting a file format is a solved problem, and BIDS Manager does not solve it again. It drives established tools, installs them with itself (on Python 3.14, niimath excepted: it has no package there yet), and does the work around them: deciding what each is asked to do, filling what each leaves out, and checking the result.

| Engine | Used for |
|---|---|
| [dcm2niix](https://github.com/rordenlab/dcm2niix) | MRI, MR spectroscopy and PET DICOM to NIfTI |
| [MNE-BIDS](https://mne.tools/mne-bids/) | EEG and MEG |
| [nibabel](https://nipy.org/nibabel/) | PET ECAT images to NIfTI, and reading NIfTI for the viewers and the quality check |
| [PET2BIDS](https://github.com/openneuropet/PET2BIDS) | ECAT headers, the PET DICOM fields dcm2niix leaves out, and PMOD blood data |
| [bidsphysio](https://github.com/cbinyu/bidsphysio) | the physiological recordings Siemens scanners store with an MRI run |
| [eyelinkio](https://github.com/scott-huberty/eyelinkio) | reading EyeLink EDF recordings (BIDS Manager writes the BIDS files, and reads ASC itself) |
| [niimath](https://github.com/rordenlab/niimath) | defacing, skull stripping, and the quality check's registration |
| [brainchop](https://github.com/neuroneural/brainchop-cli) | brain masks and tissue classes, for skull stripping and the quality check |
| The [BIDS schema](https://github.com/bids-standard/bids-specification) | every name, entity, field and requirement level |

## Your data stays on your computer

BIDS Manager reads your data from your disk and writes it back to your disk. There is no account, no upload and no cloud service, and it contains no analytics: it does not report what you convert or that you use it. PET2BIDS reports usage from its own conversion commands; BIDS Manager uses only its readers, which report nothing.

It uses the network for a few things, and sends nothing about your data with any of them: the update check at start-up, installing an update when you accept one, the download of a brain model the first time one runs, a BIDS schema version it does not ship when you ask for one, and on Linux a missing system library ([details](/learn/14-sharing/#what-leaves-your-computer)).

## Who makes it

| | |
|---|---|
| **Karel López Vilaret** | Lead developer |
| **Jochem Rieger** | Head of the Applied Neurocognitive Psychology lab, University of Oldenburg |

With thanks to Jorge Bosch-Bayard, Erdal Karaca, Pablo Alexis Olguín Baxman, Amirhussein Abdolalizadeh Saleh, Tina Schmitt, Andreas Spiegler and Shari Hiltner.

## Licence and source

BIDS Manager is released under the [MIT licence]({{ site.repo }}/blob/main/LICENSE). The source code is on [GitHub]({{ site.repo }}), and the package on [PyPI]({{ site.pypi }}). The engines it installs keep their own licences. To cite it, see [Citing](/help/citing/); to report a problem or ask for a feature, see [Reporting](/help/reporting/).
