# Installation

On this page, you will find out how to install _ZARP-cli_ on your system.

## Requirements

Installation requires the following:

- Linux (tested with Ubuntu 24.04)
- [Conda][conda] (tested with `conda 24.11.3`)
- **Recommended:** [Apptainer][apptainer] (tested with `apptainer 1.3.6`; only
  required for dependency embedding strategy `APPTAINER`)

!!! warning "Other versions, especially older ones, are not guaranteed to work!"

??? question "How do I install Apptainer?"

    Please follow the [official documentation][apptainer-docs] to install
    Apptainer (formerly Singularity) globally and configure its permissions.
    To test whether your Apptainer configuration is adequate, you can check
    whether the following commands complete without errors:

    ```sh
    apptainer pull docker://alpine:latest
    apptainer run alpine_latest.sif echo "Hello from Apptainer"
    ```

??? tip "Wanna run _ZARP_ on your HPC cluster?"

    _ZARP_ should be able to run on a sufficiently powered (32+GB RAM), modern
    laptop for most samples. However, if you want to analyze large samples, or
    a large number of samples, we recommend connecting _ZARP_ to an HPC
    cluster.

    In that case, you will need to make sure that compatible versions of at
    least one of Conda and Apptainer (when using dependency embedding
    strategies `CONDA` and `APPTAINER`, respectively) are installed and
    properly configured on each machine of the cluster, including the head
    node(s). Reach out to your systems administrator to set this up for you.

    Once Conda and/or Apptainer are set up, follow the [_ZARP_
    documentation][zarp-docs] to use, create or extend the necessary
    Snakemake execution [profiles][snakemake-profiles] to connect _ZARP_
    runs to your HPC cluster.

    Note that _ZARP-cli_ installs the Snakemake 8+ plugin
    `snakemake-executor-plugin-cluster-generic` required for HPC cluster
    execution by default.

## Installation steps

### 1. Clone _ZARP_

Clone the [_ZARP_ workflow repository][zarp] with:

```sh
git clone git@github.com:zavolanlab/zarp
# or: git clone https://github.com/zavolanlab/zarp.git
```

### 2. Clone _ZARP-cli_

Clone the [_ZARP-cli_ repository][zarp-cli] and traverse into it with:

```sh
git clone git@github.com:zavolanlab/zarp-cli.git
# or: git clone https://github.com/zavolanlab/zarp-cli.git
cd zarp-cli
```

### 3. Set up environment

In the next step, you need to install the app with its dependencies. For that
purpose, there exist two different "environment files". Use this decision
matrix to pick the most suitable one for you:

| I want to run pre-packaged tests | Environment file to use &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; |
|:---:| --- |
| | `install/environment.yml` |
| :check_mark: | `install/environment.dev.yml` |

To set up the environment, execute the call below, but do not forget to replace
the placeholder `ENVIRONMENT` with the appropriate file from the table above:

```sh
conda env create -f ENVIRONMENT
```

### 4. Activate environment

Finally, activate the Conda environment with:

```sh
conda activate zarp-cli
```

You should now be good to go to proceed with
[initialization](./initialization.md).
