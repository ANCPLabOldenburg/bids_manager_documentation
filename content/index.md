---
title: BIDS Manager
template: home
description: BIDS Manager converts and curates MRI, MR spectroscopy, PET, EEG, MEG, physiological and eye-tracking recordings into a BIDS dataset, then validates, views, checks and edits it.
hero_kicker: BIDS Manager
hero_title: From raw recordings to a *curated* BIDS dataset
hero_lede: BIDS Manager reads your raw MRI, PET, MR spectroscopy, EEG, MEG, physiological and eye-tracking recordings, names each one by the BIDS standard, helps you describe what the raw files don't capture, and stays with you after the conversion, in its GUI or from the command line.
hero_lede_short: Reads your raw recordings, names each one by the BIDS standard, helps you describe them, and stays with you after the conversion.
---

<section class="home-section home-intro" aria-label="What BIDS Manager is">
<p class="lead">BIDS Manager is curation software for brain imaging and electrophysiology data. <span>It reads a folder of raw recordings, shows you what it found and the name the standard gives each one, lets you correct and describe them, converts them with the established tools, and then helps you validate, view, check and edit the dataset that results. You do not need to write code.</span></p>
</section>

<section class="home-section hero-result-section" aria-labelledby="the-result">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">00</div>
<div>
<p class="home-kicker">The result</p>
<h2 id="the-result">Every file named, every sidecar <em>described</em></h2>
<p class="section-lede">The course's sample after it was converted and described: each recording under its BIDS name, with the JSON sidecar beside it. In a sidecar, every value says where it came from: read from the recording, written by BIDS Manager, your answer, or a placeholder still to answer.</p>
</div>
</div>
{{ ref.hero_dataset("bold") }}
</section>

<section class="home-section" aria-labelledby="how-it-works">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">01</div>
<div>
<p class="home-kicker">How it works</p>
<h2 id="how-it-works">Four stages, each a part of the <em>GUI</em></h2>
<p class="section-lede">You move through the same four stages for every study. Select a stage to see where it happens in BIDS Manager.</p>
</div>
<p class="margin-note"><b>In the margin</b>Every figure on this site is a picture of BIDS Manager itself, working on the sample datasets you can download.</p>
</div>
<div class="flow" data-flow>
<ol class="flow-steps">
<li class="flow-step is-active" data-flow-step="0"><span class="flow-num">1</span><h3>Scan the raw data</h3><p>Point BIDS Manager at a folder of DICOM series, EEG, MEG and eye-tracking files. It reads every header, groups the files by participant and session, and proposes a BIDS name for each recording.</p><a href="/learn/03-scanning/">Scanning raw data</a></li>
<li class="flow-step" data-flow-step="1"><span class="flow-num">2</span><h3>Curate in the table</h3><p>Each recording is a row. Correct a subject, a session or a task, leave a series out, and compare subjects in the Overview before anything is written.</p><a href="/learn/04-scan-table/">The scan table</a></li>
<li class="flow-step" data-flow-step="2"><span class="flow-num">3</span><h3>Describe and convert</h3><p>Give the metadata the raw files don't capture, see the dataset in the BIDS preview, then convert: images, recordings and tables under their BIDS names, with the links between fieldmaps and the runs they correct.</p><a href="/learn/07-metadata/">Metadata you provide</a></li>
<li class="flow-step" data-flow-step="3"><span class="flow-num">4</span><h3>Check and edit in the Editor</h3><p>Validate the dataset against the BIDS standard, go to each finding, edit sidecars and tables, view images and signals, and run a fast quality check.</p><a href="/learn/09-validating/">Validating in the Editor</a></li>
</ol>
<div class="flow-view">
{{ figure("home-scan", "", hotspots=False, size="flow") }}
{{ figure("home-curate", "", hotspots=False, size="flow") }}
{{ figure("home-convert", "", hotspots=False, size="flow") }}
{{ figure("home-editor", "", hotspots=False, size="flow") }}
</div>
</div>
</section>

<section class="home-section" aria-labelledby="underneath">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">02</div>
<div>
<p class="home-kicker">What runs underneath</p>
<h2 id="underneath">Established tools, and the work <em>around</em> them</h2>
<p class="section-lede">Converting a file format is a solved problem, and BIDS Manager does not solve it again: each kind of recording goes to the tool built for it. What BIDS Manager adds is everything around them. Pick a kind of recording to follow its path.</p>
</div>
</div>
{{ ref.workflow() }}
</section>

<section class="home-section" aria-labelledby="named-from-parameters">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">03</div>
<div>
<p class="home-kicker">How series are named</p>
<h2 id="named-from-parameters">Named from how it was acquired, not from what it was <em>called</em></h2>
<p class="section-lede">A series name is typed by a person at the scanner, and people make mistakes there: a protocol changed from a T2-weighted image into a FLAIR keeps its old name, a copied protocol keeps another study's task. BIDS Manager reads what the scanner recorded about how it acquired each MRI series (echo and repetition times, an inversion, the readout, the diffusion gradients, the phase encoding, the image type) and names the series from that, with dcm2niix's guess as a second opinion. On 256 series checked by hand it named 99.2 % right, against 89.1 % without it.</p>
</div>
<p class="margin-note"><b>Read more</b><a href="/concepts/how-names-are-decided/">How names are decided</a>: three real series judged by their name, by dcm2niix and by their parameters, and the order in which every step of a scan runs.</p>
</div>
</section>

<section class="home-section" aria-labelledby="what-it-reads">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">04</div>
<div>
<p class="home-kicker">What it reads</p>
<h2 id="what-it-reads">Many kinds of recording, <em>one</em> scan</h2>
<p class="section-lede">A single scan handles a folder that mixes all of these (PET blood curves are not scanned: you attach them to their PET run in **Properties**). Each is converted by the tool built for it, which BIDS Manager installs and drives.</p>
</div>
<p class="margin-note"><b>The engines</b>dcm2niix, MNE-BIDS, nibabel and PET2BIDS do the converting, eyelinkio reads EyeLink files, and BIDS Manager reads Siemens physiological logs itself. BIDS Manager decides what each is asked to do, and repairs what each leaves behind.</p>
</div>
<ul class="kinds">
<li style="--kc: var(--k-mri)"><h3>MRI</h3><p>Anatomy, functional runs with their references, diffusion and fieldmaps.</p><dl><dt>From</dt><dd>DICOM from Siemens, Philips, GE, Canon and others</dd><dt>To</dt><dd>NIfTI in <code>anat</code>, <code>func</code>, <code>dwi</code>, <code>fmap</code>, <code>perf</code></dd><dt>With</dt><dd>dcm2niix</dd></dl></li>
<li style="--kc: var(--k-mrs)"><h3>MR spectroscopy</h3><p>Single-voxel spectra and their water references.</p><dl><dt>From</dt><dd>Siemens DICOM</dd><dt>To</dt><dd>NIfTI-MRS in <code>mrs</code></dd><dt>With</dt><dd>dcm2niix</dd></dl></li>
<li style="--kc: var(--k-pet)"><h3>PET</h3><p>Dynamic and static scans, with the doses and blood data no scanner records.</p><dl><dt>From</dt><dd>DICOM, ECAT 7, PMOD blood curves</dd><dt>To</dt><dd>NIfTI and blood tables in <code>pet</code></dd><dt>With</dt><dd>dcm2niix, nibabel, PET2BIDS</dd></dl></li>
<li style="--kc: var(--k-eeg)"><h3>EEG</h3><p>Recordings with their channels, events, montage and reference.</p><dl><dt>From</dt><dd>EDF, BDF, BrainVision, EEGLAB, GDF, EGI MFF</dd><dt>To</dt><dd>The original format (EDF, BDF, BrainVision or EEGLAB) in <code>eeg</code>, or EDF when re-encoding is on</dd><dt>With</dt><dd>MNE-BIDS</dd></dl></li>
<li style="--kc: var(--k-meg)"><h3>MEG</h3><p>Task, rest and empty-room recordings, with sessions from their dates.</p><dl><dt>From</dt><dd>Elekta/MEGIN FIF, CTF, KIT</dd><dt>To</dt><dd>The original format in <code>meg</code></dd><dt>With</dt><dd>MNE-BIDS</dd></dl></li>
<li style="--kc: var(--k-physio)"><h3>Physiology</h3><p>The heartbeat, pulse, breathing and triggers recorded with an MRI run.</p><dl><dt>From</dt><dd>The physiological log DICOM (PhysioLog) that Siemens CMRR sequences store with the run</dd><dt>To</dt><dd><code>_physio.tsv.gz</code> beside the run, one table per sampling rate or one for the run</dd><dt>With</dt><dd>BIDS Manager's own reader</dd></dl></li>
<li style="--kc: var(--k-eye)"><h3>Eye tracking</h3><p>Gaze and pupil per eye, with the calibration, paired with the run they belong to.</p><dl><dt>From</dt><dd>SR Research EyeLink EDF and ASC</dd><dt>To</dt><dd><code>_physio.tsv.gz</code> per eye</dd><dt>With</dt><dd>eyelinkio for EDF; BIDS Manager reads ASC itself</dd></dl></li>
</ul>
</section>

<section class="home-section" aria-labelledby="curation">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">05</div>
<div>
<p class="home-kicker">Why it exists</p>
<h2 id="curation">Curation, not only <em>conversion</em></h2>
<p class="section-lede">A converter turns files into files. A dataset others can use also needs the facts the raw files don't capture, names that agree across sources, no identifiers left behind, and a way to check all of it.</p>
</div>
<p class="margin-note"><b>Read more</b><a href="/about/">Why BIDS Manager exists</a>, and what curation means in practice.</p>
</div>
<div class="curation">
<div><span class="roman">i.</span><h3>A table between the raw data and the dataset</h3><p>Every recording is a row you can read and correct before anything is written: subjects that disagree across sources, a task the file name does not say, a run that was aborted.</p></div>
<div><span class="roman">ii.</span><h3>Metadata nobody records</h3><p>Authors, task descriptions, the EEG reference, the PET dose: asked once, for the dataset or each kind of file, and marked TODO where still missing.</p></div>
<div><span class="roman">iii.</span><h3>Checked, and kept</h3><p>Validation against the standard, a quality check of every anatomical and diffusion image, identifiers removed, and every change recorded in the project so the work can be resumed and traced.</p></div>
</div>
</section>

<section class="home-section" aria-labelledby="where-to-start">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">06</div>
<div>
<p class="home-kicker">Where to start</p>
<h2 id="where-to-start">Pick the path that <em>fits</em> you</h2>
</div>
</div>
<div class="cards start-cards" data-cols="3">
<a class="card" href="/learn/01-bids/"><span class="card-title">New to BIDS</span><span>Start with BIDS in ten minutes: what a dataset looks like and how its files are named. Then follow the course.</span></a>
<a class="card" href="/start/quick-start/"><span class="card-title">New to BIDS Manager</span><span>Install it, download the multimodal sample, and take it from raw files to a valid dataset in about fifteen minutes.</span></a>
<a class="card" href="/guides/"><span class="card-title">Converting your own data</span><span>Go to the guide for your kind of recording: MRI, PET, EEG, MEG, eye tracking, or several at once.</span></a>
</div>
</section>

<section class="home-section" aria-labelledby="cite">
<hr class="sep" aria-hidden="true">
<div class="home-head">
<div class="home-num" aria-hidden="true">07</div>
<div>
<p class="home-kicker">Cite</p>
<h2 id="cite">If BIDS Manager helped your <em>work</em></h2>
<p class="section-lede">Please cite the software, and the engines it relies on, which deserve the credit for the converting.</p>
<div class="btn-row cite-box"><a class="btn btn--secondary" href="/help/citing/">How to cite BIDS Manager</a> <a class="btn btn--quiet" href="/updates/">What changed in each release</a></div>
</div>
</div>
</section>
