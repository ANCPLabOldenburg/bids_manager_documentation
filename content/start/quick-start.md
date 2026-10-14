---
title: Quick start
lede: Convert the multimodal sample from its raw folder to a validated BIDS dataset in nine steps. Each step links to the chapter of the course that explains it.
description: Convert a sample dataset to BIDS with BIDS Manager in nine steps.
time: 15 minutes
sample: Multimodal sample v2
---

::: before
- BIDS Manager is installed and opens on **Home** ([Install](/start/install/)).
- The multimodal sample is downloaded and unpacked ([Sample data](/start/sample-data/#multimodal)).
:::

## From raw folder to BIDS

::: step Create a project
On **Home**, in **Create a new dataset**, type `quick_start` as the dataset name, choose where to create it with **Browse...** (not inside the sample's folder), and click **Create dataset**. The **Converter** opens on the new, empty dataset.

{{ figure("l02-create", "Create a new dataset, on Home.") }}

More in [Projects](/learn/02-projects/).
:::

::: step Choose the raw folder
In the Converter, click **change…** at the end of the **Raw input** bar and choose the sample's `raw` folder.
:::

::: step Scan
Click **Scan…**. After a few seconds the scan table lists {{ m("scan.rows") }} rows, one per recording: {{ m("scan.included") }} ticked to convert, and 4 left out on their own (three scout images and a scanner report).

{{ figure("l03-after-scan", "The Converter after the scan.") }}

More in [Scanning raw data](/learn/03-scanning/).
:::

::: step Set one subject
The sample is one participant, but each source names them in its own way, so the scan proposes several subjects. Click the first ticked row, {{ key("Shift+Click") }} the last, then {{ key("Ctrl+Click") }} the `PhoenixZIPReport` row to take it out again, so the {{ m("scan.included") }} rows to convert are selected. Click **Bulk edit…** under the table, choose **subject** in **Column:**, type `001` in **New value:**, and click **Apply to 4 row(s)**.

{{ figure("l04-bulk-dialog", "Bulk edit, setting the subject of the selected rows to 001.") }}

More in [The scan table](/learn/04-scan-table/).
:::

::: step Set one session
With the same rows selected, open **Bulk edit…** again, choose **session**, type `01`, and click **Apply to 15 row(s)**. Every BIDS name in the table now starts with `sub-001_ses-01_`.
:::

::: step Add the PET doses
BIDS requires facts about the PET injection that no scanner records. Click **Dataset metadata…** under the table, scroll to **PET dose file**, click **Import…** and choose `dose_sheet.csv` from the sample folder. Click **Save**.

More in [Metadata you provide](/learn/07-metadata/).
:::

::: step Convert
Click **Run conversion** at the right of the toolbar. The conversion writes the dataset, then the metadata, then validates it. When it is done, a message says **Conversion complete**. It took {{ m("quick_start.seconds") }} seconds from creating the project, here.

More in [Converting](/learn/08-converting/).
:::

::: step Validate in the Editor
Click **Editor** in the header, then **Validate dataset** in its toolbar. The dataset has {{ m("quick_start.files") }} files; the Editor reports {{ m("quick_start.validation.ok") }} files valid, {{ m("quick_start.validation.warn") }} warnings and {{ m("quick_start.validation.err") }} error.

The warnings are placeholders for what no file records (authors, task descriptions, the institution), each marked `TODO` in its file. The error is in BIDS Manager's own output: the PET row of the session's `_scans.tsv` has an acquisition time without a date.

More in [Validating in the Editor](/learn/09-validating/).
:::

::: step Fix the error
Select `sub-001_ses-01_scans.tsv` in the tree, double-click the PET row's `acq_time` cell (the last row), type `2009-10-02T09:28:23`, press {{ key("Enter") }} and click **Save** above the table. **Validate dataset** again: no errors.

How the course does it, with the reason for the date: [Validating in the Editor](/learn/09-validating/).
:::

## What you have

::: recap
- The raw folder is a BIDS dataset with one subject and one session, MRI, spectroscopy, PET, EEG, MEG and eye tracking, and no errors.
- The course does the same with every step explained, and goes on to the metadata, the shape of a dataset, the viewers, the quality check and sharing: [Learn BIDS Manager](/learn/).
:::
