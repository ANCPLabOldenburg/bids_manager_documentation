# Editor Tab
The second tab in BIDS-Manager is the `Editor`. It lets your preview and edit metada (`.json` and `.tsv` files) and imaging data (DICOMS, NIfTI volumes...).

<img src="../static/editor/00_general_alt.png" alt="general" width="600px" align="center">

## Load your dataset
Go to the top menu and click `File`, in the dropdown select `Open BIDS...`, then a file browser will appear. Navigate to the **root or absolute folder** of your BIDS dataset (the top-level directory that contains all subfolders).

<img src="../static/editor/01_open.png" alt="openbids" width="250px" align="center">

 <br>

Once you've load your dataset, **BIDStatistic** will show you a summary of your dataset, such as total amount of subject, total amount of files. And from each subject, the amout of sessions and sequence types.

<img src="../static/editor/01_bidstatistic.png" alt="bidstatistic" width="250px" align="center">

 <br>

## BIDSplorer
Once you've loaded your dataset, you can use BIDSplorer to easily navigate through your dataset subfolders and view different type of files and sequence types.

<img src="../static/editor/02_bidsplorer.png" alt="bidsplorer" width="250px" align="center">

 <br>

* **Metadata:** Double-click on the `json` and `tsv` files to open them. Then, you can scroll through their contents and make edits:
  * For `json` files, you can easily `Add` and `Delete Fields`.
  * For `tsv` file, you can `Add` and `Remove` `Columns` and `Rows`.
  * Changes can be saved with the `Save` button (it overwrites the original file).

<img src="../static/editor/02_metadata.png" alt="metadata" width="700px" align="center">

 <br>


* **Hidden folders**: BIDSplorer also let you access hidden folders such as:
  * `.bids_manager`: it contains the following tsv files:
    * _subject_mapping.tsv_: simple list of all subjects, without age and gender.
    * _subject_summary.tsv_: all data scanned, metada and sequences types, and the rules to include it or not.
  * `.heudiconv`: stores the the conversion heuristics files.

 <br>

   
* **Sequence type view:** BIDSplorer can open NIfTI images (`nii`/`.nii.gz`) across different sequence types (anat, func, fmap, dwi). You can:
  * Inspect the three orthogonal planes: `Axial`, `Coronal`, `Sagittal`.
  
<img src="../static/editor_gifs/1_planes.gif" alt="planes" width="600px">
 <br>


  * Navigate `Slices`
<img src="../static/editor_gifs/2_slices.gif" alt="slices" width="600px">

  * Adjust `brightness` and `contrast` to improve visibility
<img src="../static/editor_gifs/3_brightness_contrast.gif" alt="brightness_contrast" width="600px">


  * next
*   files can be opened with BIDSplorer as well. You can freely inspect voxel values with the `Volume` toggle, switch between views (Sagittal, Coronal or Axial). You may also adjust the brightness and contrast.

<img src="../static/editor/02_anatomical.png" alt="anatomical" width="300px" align="center">

 <br>
*  **Graph view:** some files include a `Graph` option (top-up), which allows you to see the signal over time. Usse the `Volume` toggle to scroll throught different time points of the signal. The graph below will help you spot "jumps" or irregularities caused by participant movement or scanner errors.

<img src="../static/editor/02_graph.png" alt="graph" width="500px" align="center">

  * **Neighbors:** Increse the `scope` option (bottom-down) to inlcude neighboring voxels, making it easier to identify localized artifacts. You may additionally increase the dot size and even remove the dot from the neighboring graphs.

<img src="../static/editor/02_nhb.png" alt="nhb" width="500px" align="center">


```{admonition} Next section
:class: tip

In the next section we will get see how to use the different tools of the Editor tab to rename batches of files, add fieldmap images to function images, and more.

``` 

