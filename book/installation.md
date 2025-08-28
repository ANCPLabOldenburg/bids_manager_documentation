# Installation Guide
You can install BIDS-Manager in two different ways: one-click installer _(recommended)_ or manual installation _(for advanced users)_.

```{admonition} Required dependencies?
:class: tip

Both installation methods include all the depencies required to run the GUI and helper scripts. All core requirements are version pinned in [`pyproject.toml`](https://github.com/ANCPLabOldenburg/BIDS-Manager/blob/main/pyproject.toml) to ensure consistent installations. 
``` 


## One-click installers (recommended)

**1. Download the ZIP package:**  
* **[📦 One-click Installers](https://github.com/ANCPLabOldenburg/BIDS-Manager/raw/main/Installers/Installers.zip
)**

**2. **Extract** the ZIP file and run the script:**

| OS               | Script                        | How to Run                         |
|------------------|-------------------------------|------------------------------------|
| **Windows 10/11**| `install_bids_manager.bat`     | Double-click                        |
| **Linux**        | `install_bids_manager.sh`      | Allow execution and run the installer |


**3. (for Linux users) Allow script execution and run the installer:**

If you're working in Linux, you'll need first to allow the `.sh` script execution. This can be done in two different ways:

````{tab-set}
```{tab-item} Linux
Right click and select **"Open terminal here"** or open a terminal and use:

    cd /path/to/your/installer

Give execute permissions to the installer

    chmod +x install_bids_manager.sh

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


## Manual Installation (advanced)

**1. Create a virtual environment**

We strongly recommend using BIDS-Manager within a **virtual environment** to avoid conflicts with system dependencies.
The One-click installer automatically creates and manages a virtual environment, meanwhile the Manual Installation requires you to create one manually. If you want to learn more about virtual environments, [click here](../extra/environment.md).

```bash
# Navigate to your target directory and create a virtual environment
python3 -m venv <env_name>

# Activate the virtual environment
source <env_name>/bin/activate
# On Windows: <env_name>\Scripts\activate

```

**2. Install BIDS Manager from GitHub**

```bash
pip install bids-manager
```

## Installation completed! 🎉

After the installation finishes, you will find two **shortcuts** on your desktop:

| OS          | Launch                    | Uninstall                      |
|-------------|---------------------------|--------------------------------|
| **Windows** | `run_bidsmanager.bat`      | `uninstall_bidsmanager.bat`    |
| **Linux**   | _BIDS Manager_ (launcher)| _Uninstal BIDS Manager_ (configuration file)     |

