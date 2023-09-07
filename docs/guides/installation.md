# Installation

On this page, you will find out how to install _ZARP-cli_ on your system.

## Requirements

Installation requires the following:

- Linux (tested with Ubuntu 20.04; macOS has not been tested yet)
- [Conda][conda] (tested with `conda 22.11.1`)
- [Mamba][mamba] (tested with `mamba 1.3.0`)
- [Singularity][singularity] (tested with `singularity 3.8.6`; not required
  if you have root permissions on the machine you would like to install
  _ZARP-cli_ on; in that case choose one of the `.root.` environment file
  flavors [below](#3-install-app-dependencies))

> Other versions, especially older ones, are not guaranteed to work.

## Installation steps

### 1. Clone ZARP

Clone the [ZARP workflow repository][zarp] with:

```sh
git clone git@github.com:zavolanlab/zarp
# or: git clone https://github.com/zavolanlab/zarp.git
```

### 2. Clone ZARP-cli

Clone the [ZARP-cli repository][zarp-cli] and traverse into it with:

```sh
git clone git@github.com:zavolanlab/zarp-cli.git
# or: git clone https://github.com/zavolanlab/zarp-cli.git
cd zarp-cli
```

### 3. Install app & dependencies

In the next step, you need to install the app with its dependencies. For that
purpose, there exist four different environment files. Use this decision matrix
to pick the most suitable one for you:

| I have root privileges on the machine | I want to run pre-packaged tests | Environment file to use &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; |
|:---:|:---:| --- |
| | | `install/environment.yml` |
| :check_mark: | | `install/environment.root.yml` |
| | :check_mark: | `install/environment.dev.yml` |
| :check_mark: | :check_mark: | `install/environment.dev.root.yml` |

To set up the environment execute the call below, but do not forget to replace
the placeholder `ENVIRONMENT` with the appropriate file from the table above:

```sh
mamba env create -f ENVIRONMENT
```

### 4. Activate environment

Finally, activate the Conda environment with:

```sh
conda activate zarp-cli
```

You should now be good to go to proceed with
[initiliaztion](./initialization.md).
