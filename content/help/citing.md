---
title: Citing BIDS Manager
lede: If BIDS Manager helped you prepare a dataset, cite it in the paper and mention it in the dataset. Please cite the engines it uses as well.
description: How to cite BIDS Manager and the tools it uses.
---

## BIDS Manager

> López Vilaret, K. M. and Rieger, J. BIDS Manager (version {{ version }}). 2026. https://github.com/ANCPLabOldenburg/BIDS-Manager

```bibtex
@software{bids_manager,
  author  = {López Vilaret, Karel Mauricio and Rieger, Jochem},
  title   = {BIDS Manager},
  version = {{ '{' }}{{ version }}{{ '}' }},
  year    = {2026},
  url     = {https://github.com/ANCPLabOldenburg/BIDS-Manager}
}
```

Use the version you used: it is in BIDS Manager's status bar, and in the `GeneratedBy` entry of the dataset's `dataset_description.json`.

## In the dataset

BIDS Manager records itself in `dataset_description.json` under `GeneratedBy`. To say how the dataset should be cited, write `HowToAcknowledge` in the dataset description ([Metadata you provide](/learn/07-metadata/)), and a `CITATION.cff` with **Tools** > **Fix ups...** > **Write CITATION.cff** ([Sharing a dataset](/learn/14-sharing/)).

## The standard, and the tools your data went through

BIDS Manager converts and checks with other people's tools and follows a standard other people wrote; they deserve the credit for that part. Cite the original papers, as their authors ask. Every reference below was copied from the project's own citation file or "how to cite" page, or from the publisher's record of the paper (checked in October 2026). Where a tool has no paper, its software record is given, and the table says so.

### The standard

| Cite when | Reference |
|---|---|
| Any BIDS dataset | Gorgolewski, K. J., Auer, T., Calhoun, V. D., et al. (2016). The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments. *Scientific Data*, 3, 160044. [doi:10.1038/sdata.2016.44](https://doi.org/10.1038/sdata.2016.44) |
| The version of the specification | *The Brain Imaging Data Structure (BIDS) Specification* (Version 1.11.1). Zenodo. [doi:10.5281/zenodo.18703493](https://doi.org/10.5281/zenodo.18703493). Cite it by its title: its author list is several hundred names long. |
| MEG | Niso, G., Gorgolewski, K. J., Bock, E., Brooks, T. L., Flandin, G., Gramfort, A., Henson, R. N., Jas, M., Litvak, V., Moreau, J., Oostenveld, R., Schoffelen, J.-M., Tadel, F., Wexler, J., & Baillet, S. (2018). MEG-BIDS, the brain imaging data structure extended to magnetoencephalography. *Scientific Data*, 5, 180110. [doi:10.1038/sdata.2018.110](https://doi.org/10.1038/sdata.2018.110) |
| EEG | Pernet, C. R., Appelhoff, S., Gorgolewski, K. J., Flandin, G., Phillips, C., Delorme, A., & Oostenveld, R. (2019). EEG-BIDS, an extension to the brain imaging data structure for electroencephalography. *Scientific Data*, 6, 103. [doi:10.1038/s41597-019-0104-8](https://doi.org/10.1038/s41597-019-0104-8) |
| PET | Norgaard, M., Matheson, G. J., Hansen, H. D., et al. (2022). PET-BIDS, an extension to the brain imaging data structure for positron emission tomography. *Scientific Data*, 9, 65. [doi:10.1038/s41597-022-01164-1](https://doi.org/10.1038/s41597-022-01164-1) |
| PET, as the specification also asks | Knudsen, G. M., Ganz, M., Appelhoff, S., et al. (2020). Guidelines for the content and format of PET brain data in publications and archives: A consensus paper. *Journal of Cerebral Blood Flow & Metabolism*, 40(8), 1576-1585. [doi:10.1177/0271678X20905433](https://doi.org/10.1177/0271678X20905433) |
| MR spectroscopy | Bouchard, A. E., Wong, D., Bogner, W., Gau, R., Halchenko, Y. O., Lamb, D. G., Markiewicz, C. J., Mullins, P. G., Niso, G., Oeltzschner, G., BIDS Maintainers, Clarke, W. T., Wilson, M., & Mikkelsen, M. (2025). MRS-BIDS, an extension to the Brain Imaging Data Structure for magnetic resonance spectroscopy. *Scientific Data*, 12, 1384. [doi:10.1038/s41597-025-05543-2](https://doi.org/10.1038/s41597-025-05543-2) |
| Eye tracking | Szinte, M., Bach, D. R., Draschkow, D., Esteban, O., Gagl, B., Gau, R., Gregorova, K., Halchenko, Y. O., Huberty, S., Kling, S. M., Kulkarni, S., BIDS Maintainers, Markiewicz, C. J., Mikkelsen, M., Oostenveld, R., & Pfarr, J.-K. (2026). Eye-Tracking-BIDS: the Brain Imaging Data Structure extended to gaze position and pupil data. *bioRxiv*. [doi:10.64898/2026.02.03.703514](https://doi.org/10.64898/2026.02.03.703514). A preprint: no journal version yet. |
| Arterial spin labelling | Clement, P., Castellaro, M., Okell, T. W., et al. (2022). ASL-BIDS, the brain imaging data structure extension for arterial spin labeling. *Scientific Data*, 9, 543. [doi:10.1038/s41597-022-01615-9](https://doi.org/10.1038/s41597-022-01615-9) |
| Quantitative MRI (an MP2RAGE, for example) | Karakuzu, A., Appelhoff, S., Auer, T., Boudreau, M., Feingold, F., Khan, A. R., Lazari, A., Markiewicz, C., Mulder, M., Phillips, C., Salo, T., Stikov, N., Whitaker, K., & de Hollander, G. (2022). qMRI-BIDS: An extension to the brain imaging data structure for quantitative magnetic resonance imaging data. *Scientific Data*, 9, 517. [doi:10.1038/s41597-022-01571-4](https://doi.org/10.1038/s41597-022-01571-4) |

Physiological recordings are part of the core specification and have no paper of their own: the two references at the top cover them.

### Converting

| Cite when | Reference |
|---|---|
| MRI, MR spectroscopy or PET from DICOM | Li, X., Morgan, P. S., Ashburner, J., Smith, J., & Rorden, C. (2016). The first step for neuroimaging data analysis: DICOM to NIfTI conversion. *Journal of Neuroscience Methods*, 264, 47-56. [doi:10.1016/j.jneumeth.2016.03.001](https://doi.org/10.1016/j.jneumeth.2016.03.001) |
| EEG or MEG | Appelhoff, S., Sanderson, M., Brooks, T. L., van Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A. P., Larson, E., Gramfort, A., & Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. *Journal of Open Source Software*, 4(44), 1896. [doi:10.21105/joss.01896](https://doi.org/10.21105/joss.01896) |
| EEG or MEG (MNE-BIDS is built on MNE-Python) | Gramfort, A., Luessi, M., Larson, E., Engemann, D. A., Strohmeier, D., Brodbeck, C., Goj, R., Jas, M., Brooks, T., Parkkonen, L., & Hämäläinen, M. S. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, 7(267), 1-13. [doi:10.3389/fnins.2013.00267](https://doi.org/10.3389/fnins.2013.00267) |
| PET from ECAT, PET blood data | Galassi, A., Norgaard, M., Thomas, A. G., Gonzalez-Escamilla, G., Svarer, C., Rorden, C., Matheson, G. J., Knudsen, G. M., Innis, R. B., Ganz, M., Eierud, C., Bilgel, M., & Pernet, C. (2024). PET2BIDS: a library for converting Positron Emission Tomography data to BIDS. *Journal of Open Source Software*, 9(100), 6067. [doi:10.21105/joss.06067](https://doi.org/10.21105/joss.06067) |
| Physiological recordings of an MRI run converted before 1.5.2 (since 1.5.2 BIDS Manager reads the logs itself) | Velasco, P. (2021). *bidsphysio: Converts physio data to BIDS physiological recording* (Version 21.06.24) [Computer software]. Zenodo. [doi:10.5281/zenodo.5096588](https://doi.org/10.5281/zenodo.5096588). No paper: a software record. |
| Eye tracking from EyeLink EDF | Huberty, S. *eyelinkio* (Version 0.3.0) [Computer software]. [github.com/scott-huberty/eyelinkio](https://github.com/scott-huberty/eyelinkio). No paper and no software DOI: the repository. |
| Reading DICOM headers | Mason, D., et al. (2026). *pydicom/pydicom: Pydicom v3.0.2* [Computer software]. Zenodo. [doi:10.5281/zenodo.19119715](https://doi.org/10.5281/zenodo.19119715). No paper: a software record. |
| Reading and writing NIfTI, ECAT images | Markiewicz, C. J., Brett, M., Hanke, M., et al. *NiBabel* [Computer software]. Zenodo. [doi:10.5281/zenodo.591597](https://doi.org/10.5281/zenodo.591597). No paper: a software record. |

### Defacing, skull stripping and the quality check

| Cite when | Reference |
|---|---|
| Defacing, skull stripping, the quality check's registration | Rorden, C., Webster, M., Drake, C., Jenkinson, M., Clayden, J. D., Li, N., & Hanayik, T. (2024). niimath and fslmaths: Replication as a method to enhance popular neuroimaging tools. *Aperture Neuro*, 4. [doi:10.52294/001c.94384](https://doi.org/10.52294/001c.94384) |
| Brain masks and tissue classes (mindgrab, robust_tissue) | Masoud, M., Hu, F., & Plis, S. (2023). Brainchop: In-browser MRI volumetric segmentation and rendering. *Journal of Open Source Software*, 8(83), 5098. [doi:10.21105/joss.05098](https://doi.org/10.21105/joss.05098) |
| The quality check's template | Fonov, V. S., Evans, A. C., Botteron, K., Almli, C. R., McKinstry, R. C., Collins, D. L., & BDCG (2011). Unbiased average age-appropriate atlases for pediatric studies. *NeuroImage*, 54(1), 313-327. [doi:10.1016/j.neuroimage.2010.07.033](https://doi.org/10.1016/j.neuroimage.2010.07.033); and Fonov, V. S., Evans, A. C., McKinstry, R. C., Almli, C. R., & Collins, D. L. (2009). Unbiased nonlinear average age-appropriate brain templates from birth to adulthood. *NeuroImage*, 47(Suppl. 1), S102. [doi:10.1016/S1053-8119(09)70884-5](https://doi.org/10.1016/S1053-8119(09)70884-5) |
| The quality check's template files (from TemplateFlow) | Ciric, R., Thompson, W. H., Lorenz, R., Goncalves, M., MacNicol, E. E., Markiewicz, C. J., Halchenko, Y. O., Ghosh, S. S., Gorgolewski, K. J., Poldrack, R. A., & Esteban, O. (2022). TemplateFlow: FAIR-sharing of multi-scale, multi-species brain models. *Nature Methods*, 19(12), 1568-1571. [doi:10.1038/s41592-022-01681-2](https://doi.org/10.1038/s41592-022-01681-2) |
| The image quality measures, which follow MRIQC's definitions | Esteban, O., Birman, D., Schaer, M., Koyejo, O. O., Poldrack, R. A., & Gorgolewski, K. J. (2017). MRIQC: Advancing the automatic prediction of image quality in MRI from unseen sites. *PLOS ONE*, 12(9), e0184661. [doi:10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661) |

The quality check's explanations name the method behind each measure, with its paper ([Quality measures](/reference/quality-measures/)).
