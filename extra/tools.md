# Tools
The `Editor` tab also has some extra `Tools` to help you to manage your BIDS dataset.

## Batch Rename
Use batch rules to rename files in a batch.
1. Click on `Add Rule` to create a new `Pattern` and `Replacement` pair.
2. Choose the `Scope`: _Entire dataset_ or _Selected subjects_.
3. Click `Preview` to see the original name (left) and the new name (right).
4. `Apply` once you're satisfied.


```{warning} 
Your renamed files might not be BIDS-compliant!
```

## Set Intended For
Link **fieldmap (fmap)** images to the functional images they should correct by writting the `IntendedFor` field in the field map's `JSON`.
1. Pick the field map's `JSON` (left window) that carries the `IntenderFor`. 
2. Select one or more Functional images (right window) and click on `Add`. The list is created automatically.
3. Click `Save` so BIDS-Manager writes the chosen Function image path in the field map's `JSON`. A pop-up will confirm you that `IntendedFor` was updated.
*. _To correct any error, click on the middle functional image and click on `Remove`._

## Refresh Scans.tsv
Scans the BIDS dataset and updates participants' _sub-XXX_scans.tsv_ in case something got erased or added to the converted dataset.

## Edit .bidsignore
Add patterns for files and folders you don't want some BIDS-compliant analysis to include.



```{warning} 
Ask Karel
```

