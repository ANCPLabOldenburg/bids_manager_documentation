---
title: Reporting a problem
lede: Questions, problems and ideas go to the BIDS Manager issue tracker on GitHub; mistakes in these pages go to the documentation's own tracker, which the link at the end of every page opens. This page says what to include so we can act on it.
description: How to report a problem, ask a question or suggest a feature for BIDS Manager.
---

<div class="btn-row"><a class="btn btn--primary" href="{{ site.repo }}/issues/new">Open an issue</a> <a class="btn btn--secondary" href="{{ site.repo }}/issues">Browse existing issues</a></div>

You need a free GitHub account and nothing else. If you would rather not write in public, open an issue with as little detail as you like and say so; we will find another way.

Before writing, search the existing issues and [Known issues](/help/known-issues/): the answer may be there.

## Something went wrong

A crash, a refusal, a conversion that produced the wrong thing, or something that looked right and was not. Include:

- what you did, what you expected, and what happened instead;
- the version (in the status bar, or **About**, from the logo) and your system (macOS, Windows or Linux, and its version);
- the kind of data and its format, for example "PET ECAT" or "EEG BrainVision";
- the message, copied as text rather than as a photo;
- the log of the run: the Converter's Log has a history icon that lists the logs of earlier runs (the newest 200), and the files are in the project's `.bidsmgr/logs/`. A subject whose conversion failed has its reason in `.bidsmgr/errors/` (a subject held back by **Existing subjects** is only named in the Log).

::: warning
Logs and messages can contain file paths, and paths can contain names. Read what you attach, and never attach raw data or a dataset of people. If we need data to reproduce a problem, we will ask how it can be shared safely.
:::

## These pages are wrong or unclear

A step that does not match what you see, a number that no longer holds, a figure of a part of the GUI that has changed, or an explanation that assumes something you were never told. Every page has **Report a problem with this page** at its end, which opens an issue with the page's address filled in. Say which section, and what you expected to read there.

## You want something it does not do

A format it does not read, a step of your lab's workflow you still do by hand, a control in the wrong place for the way you work. Describe what you are trying to end up with rather than the feature you imagine: it tells us more, and sometimes there is already a way.

## You have a question

Ask it as an issue. A question that was not answered by these pages is also a report about these pages.
