---
title: The project folder and undo
lede: Why BIDS Manager works on projects, what it keeps in a project's .bidsmgr folder, how undo works in the Converter and the Editor, and how to move, share or stop managing a project.
description: BIDS Manager projects, the .bidsmgr folder, scan tables, undo, and moving or sharing a project.
---

## Why a project

Converting a study is rarely done in one sitting. Participants arrive over months, a scan table needs a second look, a conversion is repeated after a fix, a sidecar is corrected after validation. A project keeps all of it with the dataset, in its own `.bidsmgr/` folder, so you can close BIDS Manager at any point and continue where you stopped, on this computer or another, and undo what you did.

The dataset itself stays an ordinary BIDS dataset. `.bidsmgr/` is listed in `.bidsignore`, so validators and analysis tools skip it. Everything in it is listed in [Files BIDS Manager writes](/reference/files/#the-bidsmgr-folder).

## Scan tables

Each scan of a raw folder into a project is saved as a **scan table**: the table of recordings (`inventory.tsv`), every edit you make to it, the dataset metadata you give, and where the raw data was. The Converter opens the newest; the **Scan table** list in its toolbar opens an earlier one. A new batch of participants is a new scan into the same project, and the conversion adds the new subjects to the dataset ([Converting](/learn/08-converting/) explains what happens to a subject that exists already).

`bidsmgr-project` lists a project's scan tables; `bidsmgr-convert` and `bidsmgr-metadata` take `--version` to use another one ([Command line](/reference/command-line/#bidsmgr-project)).

## Undo and the history

| Where | What Undo takes back | How far |
|---|---|---|
| The Converter's table | an edit: a cell, a bulk edit, an include, new subject numbers | every edit since the scan table was last converted, also after closing and reopening; Redo until BIDS Manager closes |
| The Editor's sidecar and table viewers | an edit of the file that is open, saved or not; in the sidecar viewer, undoing a saved change also writes the file back; in the table viewer, click **Save** again | while the file is open |

**Undo** and **Redo** are in each view's toolbar. In the Converter they are also on {{ key("Ctrl+Z") }} and {{ key("Ctrl+Shift+Z") }}; in the Editor, use the buttons.

Beyond that, every change an Editor tool makes, and every saved sidecar or text file, is an **operation** recorded in the project: a rename, a restructure, a deletion, a defacing, a fix applied to many files. Before an operation rewrites or deletes a file, its original is copied into `.bidsmgr/editor/originals/`; a renamed file is not copied, its old path is in the log. Saving in the table viewer writes the file directly and is not recorded. every write is atomic, and a failure part way rolls the whole operation back, so a file is never left half-written. `.bidsmgr/editor/operations.log` lists the operations, newest last, with the files each one touched.

::: note
In {{ version }}, the GUI has no command to undo a whole operation. A defacing is taken back with **Tools** > **Put the face back...**; for anything else, a rewritten or deleted file as it was is in `.bidsmgr/editor/originals/<operation>/`, under the operation's identifier in `operations.log`, and can be copied back by hand (a renamed file can be renamed back, from the old path in the log). See [Known issues](/help/known-issues/).
:::

A conversion is not undone either: it writes many files from scratch. To convert again, change the table and run the conversion again, with **Existing subjects** (**Settings** > **Convert**) set to update or replace what changed.

## Opening a dataset

| You open | It becomes |
|---|---|
| A project created by BIDS Manager | the project, as you left it |
| A BIDS dataset BIDS Manager has not seen | a project: from **Home** at once, from the Editor's **Open folder…** if you click **Open as project**. BIDS Manager adds `.bidsmgr/`, writes a `README` if there is none, adds its two folders to `.bidsignore` (creating it if needed), and fills **Name**, **BIDSVersion** and **DatasetType** into `dataset_description.json` if they are missing. Or, from the Editor, you can only view it. |
| Any other folder | a folder to view in the Editor: nothing is written into it, the viewers are read only and the restructuring tools are off |

From the command line, `bidsmgr-create <dataset>` does the same as **Open as project**; `bidsmgr-adopt <dataset>` adds only `.bidsmgr/`, with a record of every file as found, and changes nothing outside it. See [Adopting an existing BIDS dataset](/guides/adopting-a-dataset/).

## Moving a project

A project can be moved or copied as one folder, `.bidsmgr/` included. Two things refer to places outside it:

- **The raw data.** A scan table remembers where its raw folder was. If it has moved, the Converter's **Raw input** bar says **Moved**, and **Locate...** lets you point at the new place; BIDS Manager checks it is the same data by the series identifiers before using it.
- **Recent projects.** The list on Home remembers the old place. Open the project from its new place with **Open dataset folder...**, and remove the old entry from the list.

## Sharing a dataset

Share the dataset without `.bidsmgr/`: it holds the originals of every file you changed (including the faces you removed), and the path of your raw data. Copy everything but that folder, or use a tool that respects `.bidsignore`. [Sharing a dataset](/learn/14-sharing/) has the checks to make first.

## Stopping

To stop managing a dataset with BIDS Manager, delete its `.bidsmgr/` folder. The dataset is unaffected; its history, scan tables and logs are gone, so nothing can be undone after that.
