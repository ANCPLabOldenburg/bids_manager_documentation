---
title: Settings
lede: Every setting in the Settings dialog, page by page, with what it does and its default. Open Settings with the gear at the right of the header.
description: Every BIDS Manager setting, page by page, with what it does and its default.
---

The pages are listed down the left of the dialog. A change applies when you click **Save**; **Restore Defaults** at the bottom puts back the defaults of every page, and **Restore defaults** inside a group puts back that group only; either is kept only if you then click **Save**. The settings are kept for your user account, not in a project ([where](/start/first-launch/#where-bids-manager-keeps-things)).

The tables below are generated from BIDS Manager {{ version }} itself: the labels, descriptions and defaults are the ones the dialog shows. A page longer than the dialog scrolls: its first figure shows it as it opens, and a figure of the page scrolled down sits under the heading of each part you reach by scrolling.

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

{{ figure("l03-settings-scan", "Settings, Scan page, at the top.") }}

{{ ref.settings("Scan", figures={
    "Leave out of proposed names": figure("settings-scan-leave-out-of-proposed-names", "Settings, Scan page, scrolled down: Leave out of proposed names, and Entities the sequence name decides.")}) }}

## Scan rules

Scan rules are kept with your other settings. `bidsmgr-scan --rules-file` reads rules of the same form from a JSON file you write, with a `user_hints` list and a `scan_exclusions` list ([The command line](/learn/15-command-line/)).

{{ figure("l03-settings-rules", "Settings, Scan rules page, at the top.") }}

{{ ref.settings("Scan rules", figures={
    "Custom sequence hints (MRI / DICOM only)": figure("settings-scan-rules-custom-sequence-hints", "Settings, Scan rules page, scrolled down: your own naming hints, and the built-in criteria of the MRI classifier.")}) }}

## Classification

The settings of the parameter classifier: what it does with what it finds, and every number it tests. [The classifier](/reference/classifier/) explains how they are used.

{{ figure("settings-classification", "Settings, Classification page, at the top.") }}

{{ ref.settings("Classification", figures={
    "Anatomical contrasts": figure("settings-classification-anatomical-contrasts", "Settings, Classification page, scrolled down: Anatomical contrasts."),
    "Gradient-echo contrasts": figure("settings-classification-gradient-echo-contrasts", "Settings, Classification page, scrolled down: Gradient-echo contrasts."),
    "Echoes and fieldmaps": figure("settings-classification-echoes-and-fieldmaps", "Settings, Classification page, scrolled down: Echoes and fieldmaps."),
    "Time series and diffusion": figure("settings-classification-time-series-and-diffusion", "Settings, Classification page, scrolled down: Time series and diffusion."),
    "Contrast agent and perfusion": figure("settings-classification-contrast-agent-and-perfusion", "Settings, Classification page, at the bottom: Contrast agent and perfusion, and the evidence rules.")}) }}

## Convert

{{ figure("l08-settings-convert", "Settings, Convert page, at the top.") }}

{{ ref.settings("Convert", figures={
    "Post-convert chain (run after every conversion)": figure("settings-convert-post-convert-chain", "Settings, Convert page, at the bottom: Source data and the post-convert chain.")}) }}

Two controls of the post-convert chain sit on the line of the box above them:

| Setting | What it does | Default |
|---|---|---|
| **In which fields** | Under **Write TODO into missing fields**: **Required fields only**, **Required and recommended fields**, or **Every declared field, including optional** ([Metadata levels and TODO placeholders](/concepts/metadata-levels/)) | Required and recommended fields |
| **Anonymise the metadata, last** | **Off**, **Recommended** or **Strict**: anonymises the dataset after everything else the conversion writes ([Anonymising metadata](/guides/anonymising/)) | Off |

## Validation

{{ figure("settings-validation", "Settings, Validation page.") }}

{{ ref.settings("Validation") }}

## Quality control

The methods and thresholds of the quality check. What each measure means is in [Quality measures](/reference/quality-measures/).

{{ figure("l13-settings-qc", "Settings, Quality control page, at the top.") }}

{{ ref.settings("Quality control", figures={
    "Functional time series (BOLD)": figure("settings-quality-control-functional-time-series", "Settings, Quality control page, scrolled down: Functional time series (BOLD)."),
    "Anatomical images": figure("settings-quality-control-anatomical-images", "Settings, Quality control page, scrolled down: Anatomical images."),
    "Diffusion": figure("settings-quality-control-diffusion", "Settings, Quality control page, scrolled down: Diffusion."),
    "MEG and EEG QC": figure("settings-quality-control-meg-and-eeg-qc", "Settings, Quality control page, at the bottom: MEG and EEG QC.")}) }}

## Viewer

{{ figure("settings-viewer", "Settings, Viewer page, at the top.") }}

{{ ref.settings("Viewer", figures={
    "Images": figure("settings-viewer-images", "Settings, Viewer page, scrolled down: Images."),
    "3-D": figure("settings-viewer-3-d", "Settings, Viewer page, at the bottom: 3-D, Signals and Remembered views.")}) }}

## Viewer shortcuts

Every key and mouse gesture of the viewers. Select an action, press the key in the box, then click **Set** (replace) or **Add** (a second key); **Unbind** removes it and **Default** restores it. A key used twice in the same viewer is reported under the table. **Export...** and **Import...** move a set of keys between computers. The keys as they are by default, for your system, are in [Viewers](/reference/viewers/).

{{ figure("settings-shortcuts", "Settings, Viewer shortcuts page.") }}
