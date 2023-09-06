# ZARP-cli

[![License][badge-license]][badge-url-license]
[![Build_status][badge-build-status]][badge-url-build-status]
[![Docs][badge-docs]][badge-url-docs]
[![Coverage][badge-coverage]][badge-url-coverage]
[![GitHub_tag][badge-github-tag]][badge-url-github-tag]

:pill: **_ZARP_** - RNA-Seq analysis made easy! :syringe:

## Synopsis

- You have a bunch of RNA-Seq samples and wanna know what's in them? **_ZARP
'em!_**  
- You have an extensive SRA query with hundreds of runs and you don't know
where to start? **Easy - _ZARP 'em!_**
- Barry left you some samples to analyze and then went on vacation, again? **No
problem, _ZARP 'em!_**  

ZARP-cli uses the HTSinfer package to infer missing metadata and then runs the
[ZARP RNA-Seq analysis pipeline][zarp] on your samples. Impress your colleagues
with your sudden productivity boost. Or better yet, use the time saved to go on
that camping trip with Barry. Just make sure to guard your secret! :wink:

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

## Quick installation

Quick installation requires the following:

- Linux with root permissions
- [`conda >= 22.11.1`][conda]
- [`mamba >=1.3.0`][mamba]

Execute the following commands:

```sh
git clone git@github.com:zavolanlab/zarp
git clone git@github.com:zavolanlab/zarp-cli.git
cd zarp-cli
mamba env create -f environment.yml
mamba env update -f environment.root.yml
conda activate zarp-cli
```

That's it - you can now use _ZARP-cli_!

### 5. Activate Conda environment

To activate the environment, run:

```sh
conda activate zarp-cli
```

You should now be good to go to proceed with initiliaztion and testing (see
section [Documentation](#documentation) below).

## Documentation

We have designed _ZARP-cli_ to be easy to use. However, there are still a lot
of ways in which execution can be tweaked. For the full documentation visit:  
<https://zavolanlab.github.io/zarp-cli>

## Versioning

The project adopts the [Semantic Versioning][semver] specification for
versioning. Currently the service is still in beta stage, so the API may change
and even break without further notice. However, we are planning to release a
`1.0.0` release as soon as we feel that the software is reasonably stable and 
"feature complete" for all of the major use cases we wish to cover.

## Contributing

This project lives off your contributions, be it in the form of bug reports,
feature requests, discussions, or fixes and other code changes. Please refer
to the [contributing guidelines](CONTRIBUTING.md) if you are interested to
contribute. Please mind the [code of conduct](CODE_OF_CONDUCT.md) for all
interactions with the community.

## Contact

For questions or suggestions regarding the code, please use the
[issue tracker][issue-tracker]. For any other inquiries, please contact us
by [email][contact].

&copy; 2021 [Zavolab, Biozentrum, University of Basel][zavolab]

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
[semver]: <https://semver.org/>
[zarp]: <https://github.com/zavolanlab/zarp>
[zavolab]: <https://www.biozentrum.unibas.ch/research/researchgroups/overview/unit/zavolan/research-group-mihaela-zavolan/>
