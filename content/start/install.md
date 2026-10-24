---
title: Install BIDS Manager
nav: Install
display_title: Install *BIDS Manager*
kicker: Start
lede: One installer per system puts BIDS Manager and every converter it uses in one folder of your home directory, with a launcher, without administrator rights. If you already manage Python environments, install it from PyPI instead.
---

## Which way {#which-installer}

::: cards 2
- [**macOS installer** For macOS 11 or newer, on Apple silicon or Intel. Download, double-click, confirm.](#installers)
- [**Windows installer** For Windows 10 or 11 on an Intel or AMD PC, and Windows 11 on ARM.](#installers)
- [**Linux installer** For x86_64 or ARM64 Linux built on glibc (Ubuntu, Debian, Fedora, openSUSE, Arch...); run it from a terminal.](#installers)
- [**pip, uv or conda** For anyone who manages their own Python 3.10 to 3.14, on any of these systems.](#python)
:::

### Systems the installers cover {#systems}

The installers are built on [uv](https://docs.astral.sh/uv/), which fetches a Python made for your processor. That is what lets them cover more systems than before: the earlier installers carried one portable Python per system and ran on Apple silicon Macs, x86_64 Linux and x64 Windows only.

| System | Installer | State |
|---|---|---|
| macOS 11 or newer, Apple silicon (M1 and later) | macOS | tested |
| macOS 11 or newer, Intel | macOS | should work: it installs the Intel build, checked through Rosetta on an Apple silicon Mac, not yet on an Intel Mac |
| Windows 10 or 11, Intel or AMD (x64) | Windows | supported |
| Windows 11 on ARM | Windows | should work, not tested yet: it installs the x64 build, which Windows 11 runs through its emulation (Windows 10 on ARM cannot) |
| Linux on x86_64, built on glibc | Linux | supported |
| Linux on ARM64, built on glibc | Linux | should work, not tested yet |
| Linux built on musl (Alpine) | none | the window toolkit is not published for it; the installer says so and stops |

If an installer fails on a system marked "should work", [report it](/help/reporting/) with the end of `install.log`: that is how these become tested.

You need about 2.5 GB of free disk space and a network connection while installing. Any graphics card works; the 3-D view of the image viewer needs OpenGL 3.3, which every recent computer has.

## What the installer does

The three installers do the same five things. Choose your system to read its details:

{{ ref.installer_steps() }}

No administrator rights are needed, and nothing is installed outside that folder except the launcher. The installer uses only the uv it downloaded: a uv already on the computer is never called, and your own uv settings do not reach it.

## Run the installer {#installers}

::: step Download
{{ download("installers", "Download Installers.zip") }}

One zip for the three systems, with a folder for each.
:::

::::: step Run the installer for your system
:::: os
::: macos
1. Unzip the file and open the `MacOS` folder inside the `Installers` folder it makes.
2. Double-click `install_BIDS_Manager.command`.
3. macOS warns that the developer cannot be verified. Click **Done**, open **System Settings** > **Privacy & Security**, scroll to the security section and click **Open Anyway**, then double-click the script again.
4. A Terminal window opens, lists what the installer will do and asks `Continue? [Y/n]`. Press Return; allow a few minutes.

Prefer the terminal? Run `bash install_BIDS_Manager.command` in the folder: there is no Gatekeeper warning that way.
:::
::: windows
1. Unzip the file (right-click it, **Extract All...**) and open the `Windows` folder inside the `Installers` folder it makes.
2. Double-click `install_BIDS_Manager.bat`.
3. If SmartScreen says **Windows protected your PC**, click **More info**, then **Run anyway**.
4. A console window opens, lists what the installer will do and asks `Continue? [Y/n]`. Press Enter; allow a few minutes.

On an ARM computer the installer needs Windows 11, which runs the x64 build through its emulation.
:::
::: linux
1. Unzip the file: double-click it in the file manager, or run `unzip Installers.zip`. It makes a folder `Installers` with one folder per system.
2. Open a terminal in `Installers/Linux`. Most file managers offer **Open in Terminal** (or **Open Terminal Here**) when you right-click inside the folder; otherwise open a terminal and go there:

   ```console
   $ cd ~/Downloads/Installers/Linux
   ```
3. Run the installer, and press Return when it asks `Continue? [Y/n]`:

   ```console
   $ bash install_BIDS_Manager.sh
   ```

Other ways to run it:

- `./install_BIDS_Manager.sh` works too: the zip keeps the script executable. If the terminal says `Permission denied`, your unzip tool lost that mark; run `chmod +x install_BIDS_Manager.sh` first, or use `bash` as above, which never needs it.
- Not `sh install_BIDS_Manager.sh`: on Ubuntu and Debian `sh` is a smaller shell the installer is not written for.
- Double-clicking the script in a file manager usually opens it in a text editor instead of running it.

The installer needs `curl` or `wget`, `tar` and `gzip`, which nearly every Linux has. If the window toolkit needs system libraries your Linux lacks, the installer names them and gives the command to add them (on Ubuntu and Debian, for example, `sudo apt install libxcb-cursor0 libxkbcommon-x11-0 libegl1`). The commands such as `bidsmgr-scan` work without them.
:::
::::
:::::

::::: step Open BIDS Manager
:::: os
::: macos
BIDS Manager is in `~/Applications` as **BIDS-Manager**: open it from Launchpad, Spotlight or the Finder. To keep it in the Dock, right-click its icon, then **Options** > **Keep in Dock**. Its output is written to `~/BIDS-Manager/bidsmgr.log`.
:::
::: windows
Double-click the **BIDS-Manager** shortcut on the Desktop, or find it in the Start menu. A console window shows what it is doing; keep that window open while you work.
:::
::: linux
Open **BIDS Manager** from your application menu, or from the file on the Desktop. It starts in a terminal, which shows what it is doing.
:::
::::

The first start can take longer than later ones. A working installation opens on the **Home** view:

{{ figure("window-home", "BIDS Manager on first launch.") }}
:::::

### What is in the folder

Everything goes into `~/BIDS-Manager` (`%USERPROFILE%\BIDS-Manager` on Windows):

| Item | What it is |
|---|---|
| `uv/` | uv, checked against its published SHA-256 |
| `python/` | Python 3.10, downloaded by that uv |
| `env/` | the environment BIDS Manager runs in |
| `cache/` | uv's download cache, which makes updates quick |
| `installation.json` | what is installed, with which versions; **Check updates** reads it |
| `install.log` | what the last run of the installer did |
| `uninstall_BIDS_Manager` | the uninstaller (`.command`, `.bat` or `.sh`) |

plus the launcher: `BIDS-Manager.app` in `~/Applications` on macOS, shortcuts on the Desktop and in the Start menu on Windows, a menu entry and a Desktop file on Linux. Your datasets and your projects are not inside the folder, and your settings are kept elsewhere, so removing BIDS Manager touches none of them.

### Update {#update}

Click **Check updates** at the right of the status bar. When a newer release is out, BIDS Manager asks **Update now?**, closes, installs it with the installer's own uv and opens again; **What changed** opens this site's [Updates](/updates/) first. If a release needs a newer Python than your installation runs, the update moves the installation to that Python, and puts the previous one back if anything goes wrong.

Running the installer again does the same. It finds the installation and asks what to do:

```text
  [u] Update: install the newest BIDS Manager (default)
  [r] Reinstall: remove this installation and start again
  [x] Uninstall: remove BIDS Manager from this computer
  [a] Abort
```

**u** keeps the environment and installs the newest release into it, which takes a minute or two. **r** builds everything again, for an installation that no longer starts. Both ask you to close BIDS Manager first if it is running, because a program that is running cannot be replaced. An installation made by the earlier installers (1.x) is converted in place by **u**.

### Uninstall {#uninstall}

Choose **x** in the installer's menu, or run the uninstaller:

| System | Uninstaller |
|---|---|
| macOS | `Uninstall_BIDS_Manager.command` on the Desktop, or `~/BIDS-Manager/uninstall_BIDS_Manager.command` |
| Windows | the **Uninstall BIDS-Manager** shortcut on the Desktop or in the Start menu |
| Linux | **Uninstall BIDS Manager** in the application menu or on the Desktop |

It asks `Remove it? [y/N]`, and only **y** removes anything. It deletes the BIDS-Manager folder and every launcher; datasets and settings stay.

### Use the commands with an installer {#commands}

The installer keeps BIDS Manager in its own environment, so a new terminal does not know the `bidsmgr` commands. Activate the environment first:

:::: os
::: macos
```console
$ source ~/BIDS-Manager/env/bin/activate
$ bidsmgr-scan --help
```
:::
::: windows
In the Command Prompt:

```bat
> %USERPROFILE%\BIDS-Manager\env\Scripts\activate.bat
> bidsmgr-scan --help
```

In PowerShell:

```powershell
> & "$env:USERPROFILE\BIDS-Manager\env\Scripts\Activate.ps1"
> bidsmgr-scan --help
```
:::
::: linux
```console
$ source ~/BIDS-Manager/env/bin/activate
$ bidsmgr-scan --help
```
:::
::::

### For administrators and testing

The installers read a few environment variables, all optional:

| Variable | Effect |
|---|---|
| `BIDSMGR_INSTALL_DIR` | Install somewhere else (an absolute path to a folder of its own) |
| `BIDSMGR_PYTHON` | Another Python version (default `3.10`) |
| `BIDSMGR_PACKAGE` | What to install, for example `bids-manager==1.5.0` or a wheel file |
| `BIDSMGR_YES=1` | Take the default answer to every question (never uninstalls) |
| `BIDSMGR_NO_SHORTCUTS=1` | No app, menu entry or shortcuts |
| `BIDSMGR_UNINSTALL=1` | Remove BIDS Manager without asking |

## With pip, uv or conda {#python}

BIDS Manager is published on PyPI as `bids-manager` (in Python it is imported as `bidsmgr`). It needs Python 3.10 to 3.14, and brings dcm2niix and, on Python 3.10 to 3.13, niimath with it.

:::: os
::: macos
With [uv](https://docs.astral.sh/uv/), which fetches the Python it needs (`uv venv --seed` puts pip in the environment, which **Check updates** in BIDS Manager's status bar uses):

```console
$ uv venv --seed ~/bidsmgr-env --python 3.12
$ source ~/bidsmgr-env/bin/activate
$ uv pip install bids-manager
$ bidsmgr
```

With the Python you have (check it with `python3 --version`):

```console
$ python3 -m venv ~/bidsmgr-env
$ source ~/bidsmgr-env/bin/activate
$ pip install bids-manager
$ bidsmgr
```

With conda:

```console
$ conda create -n bidsmgr python=3.12
$ conda activate bidsmgr
$ pip install bids-manager
$ bidsmgr
```
:::
::: windows
With [uv](https://docs.astral.sh/uv/), in PowerShell (`uv venv --seed` puts pip in the environment, which **Check updates** in BIDS Manager's status bar uses):

```powershell
> uv venv --seed "$env:USERPROFILE\bidsmgr-env" --python 3.12
> & "$env:USERPROFILE\bidsmgr-env\Scripts\Activate.ps1"
> uv pip install bids-manager
> bidsmgr
```

With the Python you have (check it with `py --version`), in the Command Prompt:

```bat
> py -m venv %USERPROFILE%\bidsmgr-env
> %USERPROFILE%\bidsmgr-env\Scripts\activate.bat
> pip install bids-manager
> bidsmgr
```

With conda, in an Anaconda Prompt:

```bat
> conda create -n bidsmgr python=3.12
> conda activate bidsmgr
> pip install bids-manager
> bidsmgr
```

To read EyeLink `.edf` files, install the "Microsoft Visual C++ 2008 SP1 Redistributable (x64)" from Microsoft (it needs an administrator). Everything else works without it. The installer checks this for you and says so.
:::
::: linux
With [uv](https://docs.astral.sh/uv/), which fetches the Python it needs (`uv venv --seed` puts pip in the environment, which **Check updates** in BIDS Manager's status bar uses):

```console
$ uv venv --seed ~/bidsmgr-env --python 3.12
$ source ~/bidsmgr-env/bin/activate
$ uv pip install bids-manager
$ bidsmgr
```

With the Python you have (check it with `python3 --version`; on Debian and Ubuntu, `sudo apt install python3-venv` first):

```console
$ python3 -m venv ~/bidsmgr-env
$ source ~/bidsmgr-env/bin/activate
$ pip install bids-manager
$ bidsmgr
```

With conda:

```console
$ conda create -n bidsmgr python=3.12
$ conda activate bidsmgr
$ pip install bids-manager
$ bidsmgr
```

On a minimal system Qt may need `libxcb-cursor0` (`sudo apt install libxcb-cursor0`).
:::
::::

To upgrade, activate the environment and run `pip install --upgrade bids-manager` (or `uv pip install --upgrade bids-manager`).

::: note
On Python 3.14, niimath has no package yet. BIDS Manager installs and runs, but **Deface...** is greyed out with a tooltip saying why (unless a `niimath` program is on your PATH), and the quality check uses its own simpler brain masks instead of the brain networks and the registration. Python 3.10 to 3.13 have everything.
:::

## From the source

```console
$ git clone https://github.com/ANCPLabOldenburg/BIDS-Manager.git
$ cd BIDS-Manager
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install -e ".[dev]"
$ bidsmgr
```

`-e` installs it so that changes to the source take effect without reinstalling; `[dev]` adds the test tools.

## What comes with it

| For | Engine |
|---|---|
| MRI, MR spectroscopy and PET DICOM to NIfTI | dcm2niix, program included |
| EEG and MEG | MNE-BIDS, over MNE-Python |
| PET ECAT images, PET metadata and blood data | nibabel and PET2BIDS |
| MRI physiological recordings | BIDS Manager's own reader of Siemens CMRR logs, built in |
| Eye tracking | eyelinkio |
| Defacing, skull stripping, quality-check registration | niimath, program included (Python 3.10 to 3.13) |
| Brain masks and tissue classes | brainchop (mindgrab, robust_tissue); its networks, about 1.5 MB, are downloaded the first time they are used |
| Names and validation | the BIDS schema and validator, built in |

## If the installation fails

| What you see | What to do |
|---|---|
| The macOS script does nothing when double-clicked | Gatekeeper blocked it: follow step 2's **Open Anyway**, or run it from Terminal. |
| `Permission denied` when running `./install_BIDS_Manager.sh` | The unzip tool dropped the executable mark: run `chmod +x install_BIDS_Manager.sh`, or run it as `bash install_BIDS_Manager.sh`. |
| `[[: not found` or `Syntax error` on Linux | It was run with `sh`; run it with `bash`. |
| The Linux script stops at once | Its first lines say why: it needs `curl` or `wget`, `tar` and `gzip`; or the Linux uses the musl C library (Alpine), for which the window toolkit is not published. |
| The installer stops while downloading | It already tries a second time with the system's certificates, which networks that inspect HTTPS need. If it still stops, a firewall or proxy blocked it: read the end of `install.log` in the BIDS-Manager folder, and try again on another network. |
| `BIDS Manager is running. Close it` | Quit BIDS Manager (on Windows, close its console window too), then answer or run the installer again. |
| `pip` says no version of bids-manager is available | Your Python is older than 3.10 or newer than 3.14. Check with `python3 --version`; uv can fetch a suitable one. |
| BIDS Manager opens, then closes at once (Linux) | Qt cannot load its display plugin. Install the libraries the installer named (for example `libxcb-cursor0`), then start it from a terminal to read the message. |
| EyeLink files cannot be read (Windows) | The Visual C++ 2008 runtime is missing; install it (it needs an administrator), or read an `.asc` export of the recording instead. |
| BIDS Manager opens but **Deface...** is greyed out | You are on Python 3.14; see the note above. |

More in [Troubleshooting](/help/troubleshooting/).
