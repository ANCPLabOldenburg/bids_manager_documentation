---
title: Install BIDS Manager
nav: Install
display_title: Install *BIDS Manager*
kicker: Start
lede: One installer per system puts BIDS Manager and every converter it uses in one folder of your home directory, with a launcher. If you already manage Python environments, install it from PyPI instead.
---

## Which way {#which-installer}

::: cards 2
- [**macOS installer** For a Mac with Apple silicon (M1 and later). Download, double-click, confirm.](#installers)
- [**Windows installer** For a 64-bit Intel or AMD PC with Windows 10 or 11.](#installers)
- [**Linux installer** For an x86_64 PC; run it from a terminal.](#installers)
- [**pip, uv or conda** For a Mac with an Intel processor, ARM Windows or Linux, and anyone who manages their own Python 3.10 to 3.14.](#python)
:::

You need about 2.5 GB of free disk space and a network connection while installing. Any graphics card works; the 3-D view of the image viewer needs OpenGL 3.3, which every recent computer has.

## What the installer does

The three installers do the same five things. Choose your system to read its details:

{{ ref.installer_steps() }}

Nothing is installed outside that folder, except on Windows the Microsoft Visual C++ 2008 runtime the EyeLink reader may need, which Windows installs system-wide and the uninstaller leaves in place.

## Run the installer {#installers}

::: step Download
{{ download("installers", "Download Installers.zip") }}

One zip for the three systems, with a folder for each.
:::

::::: step Run the installer for your system
:::: os
::: macos
1. Unzip the file and open the `MacOS` folder.
2. Double-click `install_BIDS_Manager.command`.
3. macOS warns that the developer cannot be verified. Click **Done**, open **System Settings** > **Privacy & Security**, scroll to the security section and click **Open Anyway**, then double-click the script again.
4. A Terminal window opens. Type `y` and press Return when it asks to continue; allow a few minutes.

Prefer the terminal? Run `./install_BIDS_Manager.command` in the folder: there is no Gatekeeper warning that way.
:::
::: windows
1. Unzip the file and open the `Windows` folder.
2. Double-click `install_BIDS_Manager.bat`.
3. If SmartScreen says **Windows protected your PC**, click **More info**, then **Run anyway**.
4. A console window opens. Type `y` and press Enter when it asks to continue. If it needs the Visual C++ runtime for EyeLink files, Windows asks for permission; if that is refused, everything else works, and the installer says how to add it later.
:::
::: linux
1. Unzip the file and open a terminal in the `Linux` folder. The installer needs `unzip` and `wget` (on Debian and Ubuntu: `sudo apt install unzip wget`).
2. Make the script executable and run it, and answer `y` when it asks to continue:

   ```console
   $ chmod +x install_BIDS_Manager.sh
   $ ./install_BIDS_Manager.sh
   ```

On XFCE, Thunar does not run scripts on double-click; run it from the terminal.
:::
::::
:::::

::::: step Open BIDS Manager
:::: os
::: macos
BIDS Manager is in `~/Applications` as **BIDS-Manager**: open it from Launchpad, Spotlight or the Finder. Its output is written to `~/BIDS-Manager/bidsmgr.log`.
:::
::: windows
Double-click the **BIDS-Manager** shortcut on the Desktop, or find it in the Start menu. It opens in a console window that shows its progress; keep that window open while you work.
:::
::: linux
Open **BIDS-Manager** from your application menu, or from the shortcut on the Desktop. It starts in a terminal, which shows its progress.
:::
::::

The first start can take longer than later ones. A working installation opens on the **Home** view:

{{ figure("window-home", "BIDS Manager on first launch.") }}
:::::

### Where it is installed, and how to remove it

| System | Installed in | Remove with |
|---|---|---|
| macOS | `~/BIDS-Manager/` and `~/Applications/BIDS-Manager.app` | `~/BIDS-Manager/uninstall_BIDS_Manager.command` |
| Windows | `%USERPROFILE%\BIDS-Manager\` | the **Uninstall BIDS-Manager** shortcut, or `uninstall_BIDS_Manager.bat` in that folder |
| Linux | `~/BIDS-Manager/` | the **Uninstall BIDS-Manager** menu entry, or `~/BIDS-Manager/uninstall_BIDS_Manager.sh` |

The folder also holds `install.log`, the installer's own log. Your datasets and projects are not inside it, and removing BIDS Manager does not touch them.

### Upgrade

Click **Check updates** at the right of the status bar: when a newer version is out, BIDS Manager offers to install it into the environment it runs in. From a terminal, activate the installer's environment (below) and run `pip install --upgrade bids-manager`.

Running the installer again finds the existing installation and asks: **u** to upgrade, **r** to reinstall from scratch, **a** to stop. In this version **u** keeps the version you have ([Known issues](/help/known-issues/)); **r** installs the newest version from scratch, and your settings, kept outside the folder, stay.

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

To read EyeLink `.edf` files, install the "Microsoft Visual C++ 2008 SP1 Redistributable (x64)" from Microsoft, which the installer would otherwise add. Everything else works without it.
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
| MRI physiological recordings | bidsphysio, built in |
| Eye tracking | eyelinkio |
| Defacing, skull stripping, quality-check registration | niimath, program included (Python 3.10 to 3.13) |
| Brain masks and tissue classes | brainchop (mindgrab, robust_tissue); its networks, about 1.5 MB, are downloaded the first time they are used |
| Names and validation | the BIDS schema and validator, built in |

## If the installation fails

| What you see | What to do |
|---|---|
| The macOS script does nothing when double-clicked | Gatekeeper blocked it: follow step 2's **Open Anyway**, or run it from Terminal. |
| The Linux script stops at once | It needs `unzip` and `wget`; install them and run it again. |
| `pip` says no version of bids-manager is available | Your Python is older than 3.10 or newer than 3.14. Check with `python3 --version`; uv can fetch a suitable one. |
| The installer stops while downloading | A firewall or proxy blocked it. Read the end of `install.log` in the BIDS-Manager folder, and try again on another network. |
| BIDS Manager opens, then closes at once (Linux) | Qt cannot load its display plugin. Install `libxcb-cursor0`, then start it from a terminal to read the message. |
| EyeLink files cannot be read (Windows) | The Visual C++ 2008 runtime is missing; install it as above, or read an `.asc` export of the recording instead. |
| BIDS Manager opens but **Deface...** is greyed out | You are on Python 3.14; see the note above. |

More in [Troubleshooting](/help/troubleshooting/).
