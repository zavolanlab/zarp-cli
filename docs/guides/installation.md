# Installation

On this page, you will find out how to install _ZARP-cli_ on your system.

## Requirements

Installation requires the following:

- Linux (tested with Ubuntu 20.04; macOS has not been tested yet)
- [Conda][conda] (tested with `conda 22.11.1`)
- [Mamba][mamba] (tested with `mamba 1.3.0`)
- Possibly: [Singularity][singularity] (tested with `singularity 3.8.6`; see
  [comment below](#4-install-optional-dependencies))

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

Next, install the app and its dependencies with Mamba:

```sh
mamba env create -f environment.yml
```

### 4. Install optional dependencies

If you do not already have Singularity installed and have root privileges on
your machine, you can **install Singularity via Mamba**:

```sh
mamba env update -f environment.root.yml
```

If you would like to **contribute to _ZARP-cli_ development or run the packaged
tests**, you also want to further update your environment:

```sh
mamba env update -f environment.dev.yml
```

### 5. Activate environment

Finally, activate the Conda environment with:

```sh
conda activate zarp-cli
```

You should now be good to go to proceed with
[initiliaztion](./initialization.md).
