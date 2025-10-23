# Tools
The `Editor` tab also has some extra `Tools` to help you to manage your BIDS dataset.

<img src="../static/tools/0_tab.png" alt="tab" width="300px" align="center">


## Batch Rename
Use batch rules to rename files in a batch.
1. Click on `Add Rule` to create a new `Pattern` and `Replacement` pair.
2. Choose the `Scope`: _Entire dataset_ or _Selected subjects_.
3. Click `Preview` to see the original name (left) and the new name (right).
4. `Apply` once you're satisfied.

<img src="../static/tools/1_batch_rename.png" alt="rename" width="700px" align="center">

```{warning} 
Your renamed files might not be BIDS-compliant!
```

## Set Intended For
Link the **fieldmap (fmap)** images of a subject to the functional images they should correct.

<!--
by writting the `IntendedFor` field in the field map's `JSON`.
-->

1. `Fieldmap images` (left-window): Choose the subjects that you want to correct. The _IntendedFor_ field of their _json_ files will be edited.
2. `Functional images` (right-window): Select one or more functional images and click on `Add` to correct the fieldmap images. This is created automatically.

4. Click `Save` so BIDS-Manager writes the chosen Function image path in the field map's `JSON`. A pop-up will confirm you that `IntendedFor` was updated.


<img src="../static/tools/2_intended_for.png" alt="intended" width="700px" align="center">
   
* _To correct any error, click on the functional image in the middle and click on `Remove`._

## Refresh Scans.tsv
Scans the BIDS dataset and updates participants' _sub-XXX_scans.tsv_ in case something got erased or added to the converted dataset.

## Edit .bidsignore
Add patterns for files and folders you don't want some BIDS-compliant analysis to include.

<img src="../static/tools/4_ignore.png" alt="ignore" width="700px" align="center">


