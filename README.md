# ZARP-cli

[![License][badge-license]][badge-url-license]
[![Build_status][badge-build-status]][badge-url-build-status]
[![Docs][badge-docs]][badge-url-docs]
[![Coverage][badge-coverage]][badge-url-coverage]
[![GitHub_tag][badge-github-tag]][badge-url-github-tag]

:pill: **_ZARP_** - RNA-Seq analysis made easy! :syringe:

## Synopsis

- Have a bunch of RNA-Seq samples and you wanna know what's in them? **_ZARP
'em!_**  
- You have an extensive SRA query with hundreds of runs and you don't know
where to start? **Easy - _ZARP 'em!_**
- Barry left you some samples to analyze and then went on vacation, again? **No
problem, _ZARP 'em!_**  

ZARP-cli uses the HTSinfer package to infer missing metadata and then runs the
[ZARP RNA-Seq analysis pipeline][zarp] on your samples. Impress your colleagues
with your sudden productivity boost. Or better yet, use the time saved to go on
that camping trip with Barry. Just make sure to guard your secret! :wink:

Kindly brought to you by the [Zavolab][zavolab].

## Basic usage

```sh
zarp [-h] [--init] [--verbosity {DEBUG,INFO,WARN,ERROR,CRITICAL}] [--version]
        PATH/ID [PATH/ID ...]

# Examples
zarp --init  # set up user defaults for ZARP
zarp sample_1.fq.gz /path/to/sample_2.fq.gz  # ZARP two single-end libraries
zarp my_sample@abcdefgh.fq.gz  # assign a sample name
zarp mate_1.fq.gz,mate_2.fq.gz  # ZARP one paired-end library
zarp table:table.tsv  # ZARP all samples from a sample table
zarp SRR0123456789 my_other_sample@SRR0123456789  # ZARP SRA runs
zarp \
    sample_1.fq.gz /path/to/sample_2.fq.gz \
    my_sample@adcdefgh.fg.gz \
    mate_1.fq.gz,mate_2.fq.gz \
    table:table.tsv \
    SRR0123456789 my_other_sample@SRR0123456789  # ZARP everything at once!
```

## Installation

### Requirements

Installation requires the following:

- Linux (tested with Ubuntu 20.04)
- [Conda][conda] (tested with `conda 22.11.1`)
- [Mamba][mamba] (tested with `mamba 1.3.0`)
- Possibly: [Singularity][singularity] (tested with `singularity 3.8.6`; see
  [comment below](#4-install-optional-dependencies))

> Other versions are not guaranteed to work as expected.

### 1. Clone ZARP

Clone the ZARP workflow repository:

```sh
git clone git@github.com:zavolanlab/zarp
# or: git clone https://github.com/zavolanlab/zarp.git
```

### 2. Clone ZARP-cli

Clone this repository and traverse into the app directory:

```sh
git clone git@github.com:zavolanlab/zarp-cli.git
# or: git clone https://github.com/zavolanlab/zarp-cli.git
cd zarp-cli
```

### 3. Install the app

Install the app with Mamba:

```sh
mamba env create -f environment.yml
```

### 4. Install optional dependencies

If you do not already have Singularity installed and have root privileges on
your machine, you can install Singularity via Mamba:

```sh
mamba env update -f environment.root.yml
```

Optionally, install required packages for testing and development:

```sh
mamba env update -f environment.dev.yml
```

### 5. Activate Conda environment

To activate the environment, run:

```sh
conda activate zarp-cli
```

You should now be good to go to proceed with initiliaztion and testing (see
section [Documentation](#documentation) below).

## Documentation

We have designed _ZARP-cli_ to be easy to use. However, there are still a lot
of ways in which execution can be tweaked. For the full documentation of
features visit:  
<https://zavolanlab.github.io/zarp-cli>

## Contributing

This project lives off your contributions, be it in the form of bug reports,
feature requests, discussions, or fixes and other code changes. Please refer
to the [contributing guidelines](CONTRIBUTING.md) if you are interested to
contribute. Please mind the [code of conduct](CODE_OF_CONDUCT.md) for all
interactions with the community.

## Contact

For questions or suggestions regarding the code, please use the
[issue tracker][issue-tracker]. For any other inquiries, please contact us
by email: <zavolab-biozentrum@unibas.ch>

&copy; 2021 [Zavolab, Biozentrum, University of Basel][contact]

[conda]: <https://docs.conda.io/projects/conda/en/latest/index.html>
[contact]: <zavolab-biozentrum@unibas.ch>
[badge-build-status]: <https://github.com/zavolanlab/zarp-cli/actions/workflows/tests.yml/badge.svg>
[badge-coverage]: <https://codecov.io/gh/zavolanlab/zarp-cli/branch/dev/graph/badge.svg?branch=dev&token=0KQZYULZ88>
[badge-docs]: <https://github.com/zavolanlab/zarp-cli/actions/workflows/docs.yml/badge.svg>
[badge-github-tag]: <https://img.shields.io/github/v/tag/zavolanlab/zarp-cli?color=C39BD3>
[badge-license]: <https://img.shields.io/badge/license-Apache%202.0-blue.svg>
[badge-url-build-status]: <https://github.com/zavolanlab/zarp-cli/actions/workflows/tests.yml>
[badge-url-coverage]: <https://codecov.io/gh/zavolanlab/zarp-cli?branch=dev>
[badge-url-docs]: <https://zavolanlab.github.io/zarp-cli>
[badge-url-github-tag]: <https://github.com/zavolanlab/zarp-cli/releases>
[badge-url-license]: <http://www.apache.org/licenses/LICENSE-2.0>
[issue-tracker]: <https://github.com/zavolanlab/zarp-cli/issues>
[mamba]: <https://github.com/mamba-org/mamba>
[singularity]: <https://sylabs.io/singularity/>
[zarp]: <https://github.com/zavolanlab/zarp>
[zavolab]: <https://www.biozentrum.unibas.ch/research/researchgroups/overview/unit/zavolan/research-group-mihaela-zavolan/>
