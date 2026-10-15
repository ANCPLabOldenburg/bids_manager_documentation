---
title: Style guide
display_title: Style *guide*
lede: Every component of the documentation, built once and shown here, in the identity the site shares with its theme: grained paper and ink by day, grained night by night, one pastel palette in both. This page is not linked from the site.
kicker: Internal
time: 5 minutes
sample: The multimodal sample
---

## Identity

The site is printed matter. By day: grey, granular paper, ink, a dark brown for marks and an emerald for links and actions. By night: greyish-black paper with the same grain, light ink, a lighter brown and a lighter emerald. Both themes give each colour the same role and the same hue family, each step checked for contrast on its own paper.

<div class="sg-swatches">
<span style="background:var(--bg)">bg</span>
<span style="background:var(--bg-elev)">elevated</span>
<span style="background:var(--bg-sunk)">sunk</span>
<span style="background:var(--ink);color:var(--bg)">ink</span>
<span style="background:var(--ink-2);color:var(--bg)">ink 2</span>
<span style="background:var(--accent);color:var(--bg)">accent</span>
</div>

<div class="sg-swatches">
<span style="background:var(--k-mri);color:var(--bg)">MRI</span>
<span style="background:var(--k-mrs);color:var(--bg)">MRS</span>
<span style="background:var(--k-pet);color:var(--bg)">PET</span>
<span style="background:var(--k-eeg);color:var(--bg)">EEG</span>
<span style="background:var(--k-meg);color:var(--bg)">MEG</span>
<span style="background:var(--k-physio);color:var(--bg)">physio</span>
<span style="background:var(--k-eye);color:var(--bg)">eye</span>
</div>

Three typefaces: Instrument Serif for titles, numerals and the large quiet words; Inter for reading; JetBrains Mono for file names, kickers and labels.

The pastels are the same in both themes. They fill, mark and underline; they never carry text, except dark ink on a pastel chip (contrast 8.5:1 or more on every pastel). Text is ink in both themes. The paper's grain is one layer fixed to the browser window, over everything, that never takes a click.

The interactive pieces, each usable with the keyboard, complete without JavaScript and still with Effects off: the series judged three ways ([How names are decided](/concepts/how-names-are-decided/)), the four exercises of [BIDS in ten minutes](/learn/01-bids/), the workflow ([home](/#underneath)), the installer's steps ([Install](/start/install/)), and the comparison on [About](/about/).

<p class="kicker">A kicker, in mono between two diamonds</p>

<hr class="sep" aria-hidden="true">

The one separator: a hairline across with a short brown mark at its start. It opens the sections of the home page, the footer and every section's first page.

<div class="sg-ornaments">
<div class="medallion" aria-hidden="true"><span>07</span></div>
</div>

A chapter's number, in a thin ring.

## Typography

Body text is Inter at 17 pixels with a line height of 1.65, set to a measure of about 68 characters. **Bold** marks GUI labels exactly as BIDS Manager writes them, such as **Run conversion**. File names, paths and values are in code type: `sub-01_ses-01_T1w.nii.gz`, `participants.tsv`, `--probe-convert`. A [[sidecar]] is a JSON file beside a data file; hovering the dotted term shows its definition.

### A third-level heading

Keys are written the way the reader's system names them: {{ key("Ctrl+Z") }} undoes, {{ key("Ctrl+Shift+Z") }} redoes, {{ key("Ctrl+K") }} opens search.

1. A numbered list item.
2. A second item, with enough words in it to wrap onto a second line so the hanging indent can be checked.

- A bulleted item.
- Another.

## Steps

::: step Open the BIDS preview
Click **BIDS preview** at the top of the panel beside the table. The panel's title changes to **BIDS preview**.

The tree now shows every file the conversion will write.
:::

::: step Expand a subject
Click a subject's row anywhere to fold it open. Folders show their files; a file written only sometimes is dim and italic.
:::

::: step Check the sidecar
Select a JSON file. Its predicted content appears below the tree, every value coloured by where it comes from.
:::

## Callouts

::: note
A note adds something useful that is not essential.
:::

::: tip
A tip saves the reader time.
:::

::: important
Important marks something that changes the result.
:::

::: warning
A warning marks something that can lose work or data.
:::

::: before
The project from chapter 2 is open, and the multimodal sample is unpacked.
:::

::: check
- The scan table shows 19 rows.
- Three rows are left out.
:::

::: different
If the table is empty, the scan did not finish: read the last lines of the **Log**.
:::

::: recap
The project now holds one scan table with 19 rows. Nothing has been written to the dataset yet.
:::

## A figure with hotspots

{{ figure("converter-map", "The Converter after a scan of the multimodal sample.") }}

{{ figure("header", "The header with a project open.") }}

## Code

```console
$ bidsmgr-scan raw/ inventory.tsv --probe-convert -j 4
Scan complete: 19 row(s) -> inventory.tsv
```

```json
{
  "Name": "multimodal_study",
  "BIDSVersion": "1.11.1"
}
```

## Operating systems

:::: os
::: macos
Double-click `install_BIDS_Manager.command` in the `MacOS` folder.
:::
::: windows
Double-click `install_BIDS_Manager.bat` in the `Windows` folder.
:::
::: linux
Run `./install_BIDS_Manager.sh` in a terminal.
:::
::::

## A table

| Modality | Source format | Converted by |
|---|---|---|
| MRI | DICOM | dcm2niix |
| PET | DICOM, ECAT 7 | dcm2niix, nibabel |
| EEG | EDF, BDF, BrainVision, EEGLAB | MNE-BIDS |

## Cards

::: cards 3
- [**Install** Get BIDS Manager on your computer.](/start/install/)
- [**Learn** Fifteen chapters, from raw data to a shared dataset.](/learn/)
- [**Reference** Every setting, column, command and key.](/reference/)
:::

## Disclosure

::: details What the scan reads
Every DICOM header, the EEG and MEG headers, and the eye-tracking file's header. It writes nothing into the raw folder.
:::

## Buttons

<div class="btn-row"><a class="btn btn--primary" href="/start/install/">Install BIDS Manager</a><a class="btn btn--secondary" href="/learn/">Start the course</a><a class="btn btn--quiet" href="/reference/">Reference</a></div>

## A video

{{ clip("l03-scan", "Clicking Scan… on the multimodal sample.") }}

## Terms

A term in double brackets links to the glossary and shows its definition on hover: a [[scan table]] row, a [[TODO]] [[placeholder]].

## A release

::: release 9.9.9 | Month Year | sg-release

<p class="rel-kind k-new">New</p>

- **A new feature**, and why it matters.

<p class="rel-kind k-fix">Fixed</p>

- **A defect**, what went wrong and what happens now.
:::
