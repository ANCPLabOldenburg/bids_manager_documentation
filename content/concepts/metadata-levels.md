---
title: Metadata levels and TODO placeholders
lede: For every file, the standard says which metadata fields are required, recommended or optional. This page explains where each value in a converted dataset comes from, and what the TODO placeholders are for.
description: Requirement levels of BIDS metadata, where values come from, and TODO placeholders in BIDS Manager.
---

## Three levels, read for each file

The BIDS standard declares, for each kind of file, which sidecar fields it may have and at which level:

| Level | Means | If it is missing |
|---|---|---|
| **Required** | the file is not valid BIDS without it | an error |
| **Recommended** | the standard asks for it whenever it is known | a warning |
| **Optional** | it may be given | nothing |

The level depends on the file, not only on its datatype: a BOLD run must have `TaskName` and a T1w is not asked for one; `Authors` is recommended in `dataset_description.json` unless the dataset has a `CITATION.cff`, which then holds them. BIDS Manager reads the levels from the standard's schema for each file, and the Editor's sidecar form shows each field at its level.

## Where a value comes from

| Source | Examples |
|---|---|
| **The data itself**, read by the converter | the timing of a BOLD run, the echo times, the sampling frequency, the channel names, the PET frame times |
| **BIDS Manager**, from the table and your settings | the task name of a run, fieldmap links, a PET `TimeZero` derived from the series time, `participants.tsv` |
| **You**: Dataset metadata, a template per kind of file, per-row values in Properties | authors and licence, task descriptions, the institution, the EEG reference, PET doses |
| **A TODO placeholder** | anything the standard asks for that none of the above answered |

The Converter's [BIDS preview](/concepts/bids-preview/) colours each predicted value by these sources before you convert.

## TODO placeholders

A field the standard asks for and nobody answered is left out of a file by every converter. Left out, it is invisible: nothing in the file says that it should be there. BIDS Manager can write a placeholder into it instead: `TODO` (`["TODO"]` in a list), or `n/a` where the field accepts it. Each unanswered field is then in the file and easy to search for, and a text `TODO` is reported by validation as a warning (`bidsmgr.todo_placeholder`) until you replace it; a `["TODO"]` list and an `n/a` are not reported.

| Setting | Where |
|---|---|
| **Write TODO into missing fields**, on by default | **Settings** > **Convert** > post-convert chain, or `bidsmgr-metadata --fill-todos` |
| The scope: **Required fields only**, **Required and recommended fields** (default), or **Every declared field, including optional** | beside it, or `bidsmgr-metadata --fill-scope required|recommended|optional|none` |
| Write or take back placeholders later | the Editor's **Tools** > **Fix ups...** > **Unanswered metadata** > **Write TODOs** |

The dataset holds exactly what the setting says. A narrower scope takes back the placeholders outside it, and turning the option off takes them all back. Values you wrote, and the `n/a` placeholders, are never touched: an `n/a` BIDS Manager wrote stays.

Some fields never get a placeholder, because `TODO` there would itself be an error or would change what the dataset means: numbers, true or false, values from a fixed list, fields that name another file (`IntendedFor`, `AssociatedEmptyRoom`), and fields that link files (`B0FieldIdentifier`, `B0FieldSource`). They stay absent, and the metadata report (`.bidsmgr/metadata_report.json`) lists them.

::: warning
A `TODO` in a **required** field turns an error into a warning: the field exists, but its value is a placeholder. A dataset with no errors can therefore still have required fields to fill. Before sharing, search for `TODO` (the sidecar search finds it) or read the warnings.
:::

## Turning the counts into a finished dataset

Most warnings after a conversion are placeholders. Some you can answer once for the whole dataset (the institution, the authors); [Dataset metadata](/learn/07-metadata/) and the Editor's **Fix in all files** do that. Some differ per recording (a task description). Some cannot be answered for your data (a device serial number nobody wrote down); for those, take the placeholders back with a narrower scope, or delete the field in the sidecar's **Tree view**.
