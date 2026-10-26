---
title: First launch
lede: What BIDS Manager's graphical user interface (GUI) shows when it opens, how to move between its three views, and the settings worth setting before you start.
description: BIDS Manager's GUI on first launch, its three views, Settings, themes and font size.
---

## Open BIDS Manager

With an installer, open **BIDS-Manager** from your applications, as [Install](/start/install/) describes for each system. With pip, uv or conda, activate the environment and run:

```console
$ bidsmgr
```

`bidsmgr --project /path/to/dataset` opens straight into a project, and `bidsmgr --theme light` starts in another theme.

## The GUI

The first time, BIDS Manager opens on **Home**. Hover the numbers to see each part.

{{ figure("window-home", "The GUI on first launch, on Home.", hotspots=True) }}

The **header** runs across the top in every view. From left to right: the logo (click it for **About**: the version, the lab, the authors and the acknowledgements), the three views, and, once a project is open, the project switcher. At the right are the **Guide** switch, **Settings** (the gear) and the theme menu (the sun or the moon).

The **status bar** at the bottom says what BIDS Manager is doing, and holds the version number and **Check updates**.

## The three views

| View | What it is for |
|---|---|
| **Home** | Create a dataset, open one, reopen a recent project. Links to the documentation, a menu of sample datasets (for the course, take the multimodal sample from [Sample data](/start/sample-data/)), and **What's new**: a menu of each release's news, as BIDS Manager showed it when that release first opened, and the update notes. |
| **Converter** | Scan raw data, curate the scan table of what was found, set the metadata the raw files don't capture, and convert. |
| **Editor** | Validate the converted dataset, edit its sidecars and tables, change its shape, view every file and check the image quality. |

The Converter and the Editor work on a **project**: a BIDS dataset folder that BIDS Manager keeps a history in. Until one is open, the Converter says so and its controls are off. [Projects](/learn/02-projects/) creates the first one.

Once a project is open, its name appears in the header. Click it to switch to a recent project.

{{ figure("header", "The header, with a project open.", hotspots=True) }}

## Let the guide show you

Switch **Guide** on, in the header beside **Settings**, and BIDS Manager shows you the way. In the view you are in, it asks what you would like to do; then it rings the control to use and says, in a card beside it, what to do there.

{{ clip("s-guide", "The guide switched on in the Converter: Check and edit the table rings the table, a click on a row moves the card to Properties, and Next to Structure.") }}

- **It asks** when you switch it on, when you come to a view, and when you finish a task. The usual next step is tinted and says **Next step**; Return takes it. **Not now**, Escape or a click elsewhere closes the question, and a small **Guide: what next?** button stays to ask again.
- **A task is a few steps.** The card names the task and the step (**Check and edit the table · Step 1 of 4**), says what to do, and carries **All tasks**, **Previous** and **Next** (**Finish** on the last step). A step moves on by itself when you do what it asks: pick a folder, finish a scan, click a row. A task always starts at its first step, whatever you did before.
- **What it offers depends on the view.** Home: create a dataset, open one, reopen a recent project, practise on a sample. The Converter, once a table is open: scan new data, check and edit the table, one recording's metadata or the dataset's, many rows at once, the columns shown, convert, look at the dataset, the settings. The Editor: validate, fix what validation found, look at or edit a file, rename, sessions, delete recordings, remove identifying information, check image quality, repair sidecars and tables, undo a change.

{{ figure("guide-question", "What the guide offers in the Converter once a scan table is open, the usual next step tinted.") }}

{{ figure("guide-home", "The guide switched on at Home.") }}

The guide is off until you switch it on, and remembered from then on. It never takes a click from the window: everything under the ring works as usual, and a dialog you open hides it until you close it.

## Choose a theme

:::: columns
{{ figure("theme-menu", "The theme menu.") }}

<div class="col-text">

Click the sun or the moon at the right of the header. The menu lists every theme in four groups, each with a swatch of its colours, and marks the current one. The choice applies at once and is remembered.

**Settings** > **Display** offers the same list, and the changes you can make to any theme.

The figures on this site show **Dark** and **Light**, and follow the theme of this site: switch it with the button at the top right of this page.

</div>
::::

{{ ref.themes() }}

## Settings

Click the gear in the header. The pages are listed down the left; every change applies when you click **Save**, and **Restore Defaults** puts back what BIDS Manager starts with. Each page is described in [Settings](/reference/settings/).

{{ figure("settings-display", "Settings, Display page.") }}

Two settings on the **Display** page are worth setting now:

- **Font scale** makes all text larger or smaller, from **Compact (0.85x)** to **Extra large (1.50x)**. The figures on this site are taken at **Comfortable (1.15x)**.
- **Appearance** changes the theme you chose: its accent colour, a tint of the surfaces, the colour of the icons, and the colours of each kind of file in the file trees. A colour you pick yourself is kept separately for dark and for light themes, so one choice does not make the other unreadable.

## Where BIDS Manager keeps things

| What | Where |
|---|---|
| Your settings and recent projects | macOS: `~/Library/Preferences/com.bidsmgr.bidsmgr.plist`. Windows: the registry, under `HKEY_CURRENT_USER\Software\bidsmgr\bidsmgr`. Linux: `~/.config/bidsmgr/bidsmgr.conf`. |
| A project's history, scan tables and logs | inside the dataset, in its `.bidsmgr/` folder ([The project folder](/concepts/project-folder/)) |
| Logs of commands run outside a project | `~/.bidsmgr/logs/` (on Windows, `%USERPROFILE%\.bidsmgr\logs\`) |

Removing BIDS Manager does not remove the settings or touch your datasets.

## Updates

The first time a new version opens, it shows **What's new**: the features of every release since the one you had, in a list, and beside them a short animation of each. Click a feature to see it again. Coming from an older version, **Next** moves to the news of the release before; the menu at the top opens any release's news, and **Release notes** opens its card in [Updates](/updates/). Home's **What's new** menu opens the window at any time.

{{ figure("whats-new", "What's new in BIDS Manager 1.5.2, showing Sidecars written from the recordings.") }}

A few seconds after it opens, BIDS Manager asks PyPI whether a newer version exists. If one does, it says so and offers **What changed** (the release notes on this site), **Yes** (close, update and reopen) and **No**. Nothing about your data is sent. **Check updates** in the status bar asks again at any time.

The check is skipped when BIDS Manager runs from a source checkout. To turn it off everywhere, for example on a computer without internet access, set the environment variable `BIDSMGR_NO_UPDATE_CHECK=1`.

::: note
Updating from within the GUI installs the new version into the environment BIDS Manager runs in. With an installer that is the installer's own environment; with pip, uv or conda it is yours.
:::

## Next

Download a sample dataset from [Sample data](/start/sample-data/), then follow the [Quick start](/start/quick-start/), or begin the course with [BIDS in ten minutes](/learn/01-bids/).
