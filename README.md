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
zarp sample_1.fq.gz /path/to/sample_2.fq.gz  # ZARP two single-end libraries
zarp my_sample:abcdefgh.fq.gz  # assign a human-readable sample name
zarp mate_1.fq.gz,mate_2.fq.gz  # ZARP one paired-end library
zarp table.tsv  # ZARP all samples from a sample table
zarp SRR0123456789 SRR0123456789  # ZARP SRA runs
zarp \
    sample_1.fq.gz /path/to/sample_2.fq.gz \
    my_sample:adcdefgh.fg.gz \
    mate_1.fq.gz,mate_2.fq.gz \
    table.tsv \
    SRR0123456789 SRR0123456789  # ZARP everything at once!
```

## Parameters

```console
Positional arguments:
  PATH/ID               paths to individual samples, ZARP sample tables and/or
                        SRA identifiers; see online documentation for details
                        (default: None)

Run-specific arguments:
  Use these arguments to overwrite defaults set up during initiation; see
  online documentation for details

ZARP-CLI arguments:
  Arguments not passed on to the analysis pipeline

  -h, --help            show this help message and exit
  --init                edit user-level default parameters and exit (default:
                        False)
  --verbosity {DEBUG,INFO,WARN,ERROR,CRITICAL}
                        logging verbosity level (default: INFO)
  --version             show version information and exit
```

## Installation

TBA

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

[badge-build-status]: <https://travis-ci.com/zavolanlab/zarp-cli.svg?branch=dev>
[badge-coverage]: <https://img.shields.io/coveralls/github/zavolanlab/zarp-cli>
[badge-docs]: <https://readthedocs.org/projects/zarp-cli/badge/?version=latest>
[badge-github-tag]: <https://img.shields.io/github/v/tag/zavolanlab/zarp-cli?color=C39BD3>
[badge-license]: <https://img.shields.io/badge/license-Apache%202.0-blue.svg>
[badge-pypi]: <https://img.shields.io/pypi/v/zarp-cli.svg?style=flat&color=C39BD3>
[badge-url-build-status]: <https://travis-ci.com/zavolanlab/zarp-cli>
[badge-url-coverage]: <https://coveralls.io/github/zavolanlab/zarp-cli>
[badge-url-docs]: <https://zarp-cli.readthedocs.io/en/latest/?badge=latest>
[badge-url-github-tag]: <https://github.com/zavolanlab/zarp-cli/releases>
[badge-url-license]: <http://www.apache.org/licenses/LICENSE-2.0>
[badge-url-pypi]: <https://pypi.python.org/pypi/zarp-cli>
[contact]: <https://zavolan.biozentrum.unibas.ch/>
[issue-tracker]: <https://github.com/zavolanlab/htsinfer/issues>
