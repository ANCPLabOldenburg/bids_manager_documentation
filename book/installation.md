# Installation Guide
You can install BIDS-Manager by using our installers. 

```{admonition} Required dependencies?
:class: tip

The installation method includes all the depencies required to run the GUI and helper scripts. All core requirements are version pinned in [`pyproject.toml`](https://github.com/ANCPLabOldenburg/BIDS-Manager/blob/main/pyproject.toml) to ensure consistent installations. 
```

## Installers

```{admonition} What does the installer do?
:class: dropdown

The installer is intended to make the installation process simple and easy, while ensuring every dependency and requierement is installed. So, users don't need any technical expertise. This is what is happening in the background:
1. Creates a BIDS_MANAGER folder in you user/home directory.
2. Downloads a compressed embeded python 3.10 (ensures compatibily). BIDS-Manager will only work in python 3.10. We, will give support to latest python versions in th future.
3. Decompresses the embeded python.
4. Ensures that pip library is working correctly.
5. Creates an environment using the embeded python 3.10
6. pip install bids-manager in that environment.
7. Creates shortcut scripts in your desktop to launch or unistall the BIDS_Manager app. 
```

* **Download the ZIP package:** **[📦 Installers](https://github.com/ANCPLabOldenburg/BIDS-Manager/raw/main/Installers/Installers.zip
)**

* **Extract the ZIP file and run the script:** After extracting the ZIP, you will see one subfolder per operating system. Each subfolder contains a specific installation script: 
<br>


| OS               | Script                        | How to Run                         |
|------------------|-------------------------------|------------------------------------|
| **Windows 10/11**| `install_bids_manager.bat`     | Double-click and `Run` in the Security Warning         |
| **Linux**        | `install_bids_manager.sh`      | Allow execution (see below) and run the installer |
| **MacOS**        | `install_bids_manager.command`      | Allow execution (see below) and run the installer |

<img src="../static/install/folders.png" alt="folders" width="250px" align="center">

<br>

## Allow script execution and run the installer for Linux and MacOS users

### **Linux systems:**

If you're working in Linux, you'll need first to allow the `.sh` script execution. This can be done in two different ways:

````{tab-set}
```{tab-item} Linux
Right click and select **"Open terminal here"** or open a terminal and use:

    cd /path/to/your/installer

Give execute permissions to the installer

    chmod +x install_bids_manager.sh


Or alternatively

    chmod 755 install_bids_manager.sh

Run the installer

    ./install_bids_manager.sh


```

```{tab-item} XFCE systems

Allow "execute" option in XFCE systems

    xfconf-query --channel thunar --property /misc-exec-shell-scripts-by-default --create --type bool --set true

Give execute permissions to the installer

    chmod +x install_bids_manager.sh

Or alternatively

    chmod 755 install_bids_manager.sh

Run the installer

    ./install_bids_manager.sh

```
````

<br>

### **MacOS systems:**
  
Because the installer is not from the App Store, macOS will initially block it.

* Double-click `install_bids_manager.command` will open a warning ⚠️ dialog. Cick `Done`.

<img src="../static/install/mac_1.png" alt="mac-error" width="250px" align="center">

<br>
  
* Open `System Settings` and scroll until `Privacy & Security`.

<img src="../static/install/mac_2.png" alt="mac-settings" width="450px" align="center">

<br>

* In the `Security` section, you should now see a mesage about the blocked attempt. Click `Open Anyways` to allow it.
  
<img src="../static/install/mac_3.png" alt="mac-security" width="450px" align="center">

<br>

<!--
commented out!
## Manual Installation (advanced)

**1. Create a virtual environment**

We strongly recommend using BIDS-Manager within a **virtual environment** to avoid conflicts with system dependencies.
The One-click installer automatically creates and manages a virtual environment, meanwhile the Manual Installation requires you to create one manually. If you want to learn more about virtual environments, [click here](../extra/environment.md).

```bash
# Navigate to your target directory and create a virtual environment
python3 -m venv <env_name>

# Activate the virtual environment
source <env_name>/bin/activate
# On Windows: .\<env_name>\Scripts\activate

```

**2. Install BIDS Manager from GitHub**

```bash
pip install bids-manager
```
-->

## Installation completed! 🎉

After the installation finishes, you will find two **shortcuts** on your desktop:

| OS          | Launch                    | Uninstall                      |
|-------------|---------------------------|--------------------------------|
| **Windows** | `run_bidsmanager.bat`      | `uninstall_bidsmanager.bat`    |
| **Linux**   | `BIDS Manager` | `Uninstall BIDS Manager`    |
| **MacOS**   | `BIDSManager.command` | `Uninstall BIDSManager.command`  |

* _To open the app, double click on the launcher._
* _First time to launch will take a minute. For the next times that you open the app, the initialization will be faster._
* _To uninstall the app, double click on the uninstall launcher._

## Where is BIDS-Manager installed? 🤨

```{admonition} Installation paths
You can find your BIDS_MANGER installed in the following full paths:

**Windows:**

    C:\Users\<your_user>\BIDS_MANAGER

**Linux:**

    /home/<your_user>/BIDS_MANAGER


**MacOS:**

    /Users/<your_user>/BIDS_MANAGER

```
## What if you don't like GUIs and want to work with commands in the python environment where BIDS-Manager is installed? 🤨

### Activate the environment
The installer automatically creates and manages a virtual environment ([learn more about virtual environments](../extra/environment.md)). If you want to manually activate the environment from a terminal or command prompt you can use the following full paths:


```{admonition} Environment activation full path

**Windows:**

    \Users\<your user>\BIDS_MANAGER\env\Scripts\activate


**Linux:**

    source home/<your user>/BIDS_MANAGER/env/bin/activate


**MacOS:**

    source Users/<your user>/BIDS_MANAGER/env/bin/activate


```

After activation the following commands become available:

- `bids-manager` – main GUI combining conversion and editing tools (similar to the desktop launcher)
- `dicom-inventory` – generate `subject_summary.tsv` from a DICOM directory
- `build-heuristic` – create a HeuDiConv heuristic from the TSV
- `run-heudiconv` – run HeuDiConv using the generated heuristic
- `post-conv-renamer` – rename fieldmap files after conversion and organize/write the IntendedFor fields in the metadata

