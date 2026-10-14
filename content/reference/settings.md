---
title: Settings
lede: Every setting in the Settings dialog, page by page, with what it does and its default. Open Settings with the gear at the right of the header.
description: Every BIDS Manager setting, page by page, with what it does and its default.
---

The pages are listed down the left of the dialog. A change applies when you click **Save**; **Restore Defaults** at the bottom puts back the defaults of every page, and **Restore defaults** inside a group puts back that group only; either is kept only if you then click **Save**. The settings are kept for your user account, not in a project ([where](/start/first-launch/#where-bids-manager-keeps-things)).

The tables below are generated from BIDS Manager {{ version }} itself: the labels, descriptions and defaults are the ones the dialog shows.

## BIDS version

{{ figure("settings-bids-version", "Settings, BIDS version page.") }}

{{ ref.settings("BIDS version") }}

## Display

{{ figure("settings-display", "Settings, Display page.") }}

{{ ref.settings("Display") }}

## System

{{ figure("settings-system", "Settings, System page.") }}

{{ ref.settings("System") }}

## Scan

{{ figure("l03-settings-scan", "Settings, Scan page.") }}

{{ ref.settings("Scan") }}

## Scan rules

Scan rules are kept with your other settings. `bidsmgr-scan --rules-file` reads rules of the same form from a JSON file you write, with a `user_hints` list and a `scan_exclusions` list ([The command line](/learn/15-command-line/)).

{{ figure("l03-settings-rules", "Settings, Scan rules page.") }}

{{ ref.settings("Scan rules") }}

## Classification

The settings of the parameter classifier: what it does with what it finds, and every number it tests. [The classifier](/reference/classifier/) explains how they are used.

{{ figure("settings-classification", "Settings, Classification page.") }}

{{ ref.settings("Classification") }}

## Convert

{{ figure("l08-settings-convert", "Settings, Convert page.") }}

{{ ref.settings("Convert") }}

## Validation

{{ figure("settings-validation", "Settings, Validation page.") }}

{{ ref.settings("Validation") }}

## Quality control

The methods and thresholds of the quality check. What each measure means is in [Quality measures](/reference/quality-measures/).

{{ figure("l13-settings-qc", "Settings, Quality control page.") }}

{{ ref.settings("Quality control") }}

## Viewer

{{ figure("settings-viewer", "Settings, Viewer page.") }}

{{ ref.settings("Viewer") }}

## Viewer shortcuts

Every key and mouse gesture of the viewers. Select an action, press the key in the box, then click **Set** (replace) or **Add** (a second key); **Unbind** removes it and **Default** restores it. A key used twice in the same viewer is reported under the table. **Export...** and **Import...** move a set of keys between computers. The keys as they are by default, for your system, are in [Viewers](/reference/viewers/).

{{ figure("settings-shortcuts", "Settings, Viewer shortcuts page.") }}
