# ZARP-cli

[![License][badge-license]][badge-url-license]
[![Build_status][badge-build-status]][badge-url-build-status]
[![Docs][badge-docs]][badge-url-docs]
[![Coverage][badge-coverage]][badge-url-coverage]
[![GitHub_tag][badge-github-tag]][badge-url-github-tag]
[![PyPI_release][badge-pypi]][badge-url-pypi]

**_ZARP 'em_** - RNA-Seq analysis made easy!

* Have a bunch of RNA-Seq samples and you wanna know what's in them? **_ZARP
'em!_**  
* Barry left you some samples to analyze and then went on vacation, again? **No
problem, _ZARP 'em!_**  
* You have an extensive SRA query with hundreds of runs and you don't know
where to start? **Easy - _ZARP 'em!_**

ZARP-cli uses the HTSinfer package to infer missing metadata and then runs the
ZARP RNA-Seq analysis pipeline on your samples. Impress your colleagues with
your sudden productivity boost. Or better yet, use the time saved to go on that
camping trip with Barry. Just make sure to guard your secret! :wink:

:pill: **_ZARP 'em_** - set it up once, benefit for a lifetime! :syringe:

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

Clone this repository and traverse into the app directory:

```sh
git clone git@github.com:zavolanlab/zarp-cli.git
cd zarp-cli
```

Install the app:

```sh
pip install .
```

> If you would like to contribute to ZARP-cli development, we recommend
> installing the app in editable mode:
>
> ```sh
> pip install -e .
> ```

Optionally, install required packages for testing and development:

```sh
pip install -r requirements_dev.txt
```

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

[contact]: <zavolab-biozentrum@unibas.ch>
[badge-build-status]: <https://github.com/zavolanlab/zarp-cli/actions/workflows/ci.yml/badge.svg>
[badge-coverage]: <https://codecov.io/gh/zavolanlab/zarp-cli/branch/dev/graph/badge.svg?branch=dev&token=0KQZYULZ88>
[badge-docs]: <https://readthedocs.org/projects/zarp-cli/badge/?version=latest>
[badge-github-tag]: <https://img.shields.io/github/v/tag/zavolanlab/zarp-cli?color=C39BD3>
[badge-license]: <https://img.shields.io/badge/license-Apache%202.0-blue.svg>
[badge-pypi]: <https://img.shields.io/pypi/v/zarp.svg?style=flat&color=C39BD3>
[badge-url-build-status]: <https://github.com/zavolanlab/zarp-cli/actions/workflows/ci.yml>
[badge-url-coverage]: <https://codecov.io/gh/zavolanlab/zarp-cli?branch=dev>
[badge-url-docs]: <https://zarp-cli.readthedocs.io/en/latest/?badge=latest>
[badge-url-github-tag]: <https://github.com/zavolanlab/zarp-cli/releases>
[badge-url-license]: <http://www.apache.org/licenses/LICENSE-2.0>
[badge-url-pypi]: <https://pypi.python.org/pypi/zarp>
[issue-tracker]: <https://github.com/zavolanlab/zarp-cli/issues>
