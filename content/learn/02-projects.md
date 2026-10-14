---
title: Projects
chapter: 2
lede: Create the project the course works in. A project is a BIDS dataset folder that BIDS Manager manages, so it keeps every scan, every edit and every log of that dataset inside it.
time: 10 minutes
sample: Multimodal sample v2
---

::: before
- BIDS Manager is open on its **Home** view.
- You know where you want the course's dataset to live. The figures use `/tmp/studies`; any folder you can write to works.
:::

## What a project is

In BIDS Manager everything happens inside a **project**: the folder of one BIDS dataset. The Converter writes into it and nowhere else, and the Editor shows it. Besides the dataset's own files, the project holds a hidden folder, `.bidsmgr/`, where BIDS Manager keeps what it needs to resume your work: the scans you made, the edits to each scan's table (which you can undo), the logs, and a record of every change made in the Editor, with the files as they were.

You create a project once per dataset. Scanning raw data a second time (another participant, another day of recording) adds to the same project.

## Create the project

::: step Type a name for the dataset
On **Home**, in **Create a new dataset**, type `multimodal_study` in the name field. The name becomes the folder's name and the dataset's `Name` in `dataset_description.json`.

{{ figure("l02-create", "The Create a new dataset card, filled in.") }}

Use letters, digits, hyphens and underscores. A name with a space is refused, and BIDS Manager offers the same name with underscores instead.
:::

::: step Choose where it goes
The second field shows the folder the dataset is created in. Click **Browse…** to choose another one in your system's folder dialog. The new project is the folder `multimodal_study` inside it.
:::

::: step Create it
Click **Create dataset**. BIDS Manager creates the folder, writes the first files of the dataset into it, and opens the **Converter**.

{{ figure("l02-after-create", "The Converter of the new, empty project.") }}

The header now shows the project's name, and **BIDS output** is the project folder. It is locked there: everything the Converter writes goes into this project.
:::

::: check
- The header shows `multimodal_study` beside the three views.
- **BIDS output** reads `/tmp/studies/multimodal_study` (or your own folder).
- The **Output data tree** shows `multimodal_study` with `dataset_description.json` and `README`.
:::

## What was created

A new project is already a valid, empty BIDS dataset:

```text
multimodal_study/
├── dataset_description.json     Name, BIDSVersion 1.11.1, DatasetType raw
├── README                       a first README for you to replace
├── .bidsignore                  tells validators to skip BIDS Manager's own folders
└── .bidsmgr/
    └── project/                 the project's record: its scans and the edits to them
```

As you work, `.bidsmgr/` gains `logs/` (one log per scan, conversion, metadata pass and validation), `provenance/` (what each subject was converted from) and the validation reports. Everything in it is described in [Files BIDS Manager writes](/reference/files/). Leave it in place: it is what makes the work resumable, and `.bidsignore` keeps it out of the way of analysis tools.

## Switch between projects

The project's name in the header is the **project switcher**. Click it to see the open project with its folder, and **Open or create another... (Home)**. Projects you opened before are listed there too, so you can switch without going back to Home.

{{ figure("l02-switcher", "The project switcher's menu.") }}

**Home** keeps the same list under **Recent projects**. Double-click a project to reopen it. Select several ({{ key("Shift+Click") }} for a range, {{ key("Ctrl+Click") }} for one more) to take them off the list with **Remove from list**, which deletes nothing, or to delete them from the disk with **Delete from disk...**, which asks first and never touches the project that is open.

## Open a dataset you already have

**Open dataset folder...** on Home opens a folder in one of three ways, depending on what it holds:

| The folder is | What happens |
|---|---|
| A BIDS dataset, or empty | It opens as a project. BIDS Manager adds its `.bidsmgr/` folder, adds a `README`, `.bidsignore` or `dataset_description.json` if the dataset has none, adds its own two folders to an existing `.bidsignore`, and fills **Name**, **BIDSVersion** and **DatasetType** in `dataset_description.json` if they are missing. Nothing else changes. |
| Any other folder | BIDS Manager asks first: **View in the Editor** opens it read-only and writes nothing into it; **Make it a project** adds the files above so you can convert into it and edit it. |

Opening an existing dataset is covered in detail in the guide [Adopting an existing BIDS dataset](/guides/adopting-a-dataset/).

## Undo in a project

Every change you make in the Converter's table is recorded in the project, so **Undo** ({{ key("Ctrl+Z") }}) takes back table edits one at a time, also after closing and reopening BIDS Manager, back to the last conversion; **Redo** ({{ key("Ctrl+Shift+Z") }}) works until you close BIDS Manager or make a new edit. The Editor records every change it makes to the dataset's files, with the files as they were; the GUI cannot undo those changes, only the edits in the open sidecar or table before they are saved. [The project folder and undo](/concepts/project-folder/) explains what is kept and for how long.

::: recap
- The project `multimodal_study` exists, with `dataset_description.json`, `README`, `.bidsignore` and `.bidsmgr/`.
- The Converter is open on it, with **BIDS output** locked to the project.
- Nothing has been scanned yet. Next, [Scanning raw data](/learn/03-scanning/).
:::
