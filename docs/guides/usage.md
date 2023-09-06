# Usage

## How does the _ZARP-cli_ work?

The `zarp` command accepts two kinds of arguments:

- **Positional arguments**: All positional arguments are interpreted as _sample
  references_, which can be paths to local RNA-Seq library files, paths to
  sample tables, or "run identifiers" assigned by either the [Sequence Read
  Archive (SRA)][sra], the [DNA Data Bank of Japan (DDBJ)][ddbj], or the
  [European Nucleotide Archive (ENA)][ena]. See [below](#sample-references) for
  a detailed description of the sample reference syntax.
- **Command-line options**: Optional arguments of the form `--optional-arg`,
  which either modify _ZARP-cli_'s behavior or assign sample-, run- or user-
  specific metadata globally to all samples of a given _ZARP-cli_ run. See
  below for a more detailed description of [command-line
  options](#command-line-options).

## Sample references

The table below gives an overview of the supported basic sample reference
types:

| Type | Note | Examples |
| ---- | ---- | -------- |
| **Path to local RNA-Seq library** | Both absolute and relative paths are supported | `/path/to/library_1.fq.gz`, `library_2.fq.gz` |
| **Path to local _ZARP_ sample table** | Both absolute and relative paths are supported | `table:/path/to/sample/table_1.tsv`, `table:table_2.tsv` |
| **SRA/DDBJ/ENA identifier** | Valid identifiers need to be matched by the following regular expression: `(E|D|S)RR[0-9]{6,}` | `SRR123456`, `DRR7654321` |

The above basic types can further be amended by the following syntax fragments
for further annotation:

| Syntax | Description | Examples |
| ------ | ----------- | -------- |
| `PATH,PATH` | Exactly two paths, separated by a comma and no white space, signify the two separate files for a **paired-ended sequencing library**; absolute and relative paths and mixes thereof are supported | `/tmp/m1.fq.gz,/tmp/m2.fq.gz`, `mate_1.fq.gz,mate_2.fq.gz`, `mate_1.fq.gz,/tmp/m2.fq.gz` |
| `NAME@REF` | A string separated from a _non-table_ sample reference via the <kbd>@</kbd> specifies a **sample name** (if not provided, a sanitized form of the base name of the file path is used) | `se_sample@lib.fq.gz`, `pe_sample@m1.fq.gz,m2.fq.gz`, `remote_sample@ERR11223344` |

!!! tip "Different sample references can of course be mixed and matched to your heart's content!"

## Command-line options

Available command-line parameters are grouped into the following sections:

| Section | Description |
| ------- | ----------- |
| **General** | Next to sample references (the only _required_ parameters!), these currently include the verbosity level and an option to provide a custom configuration file |
| **Run modes** | These parameters execute _ZARP-cli_ in special modes, e.g., for initialization or to display the help screen |
| **Sample-specific** | These parameters modify globally set metadata for all samples of a run, unless overridden inside provided sample tables |
| **Run-specific** | These parameters modify the behavior of _ZARP-cli_ or set metadata to describe runs |
| **User-specific** | These parameters that will be included in the _ZARP_ report, if available |

A complete listing of all available CLI options can easily be printed to the
screen, together with detailed descriptions, with the following command and
will therefore not be repeated here:

```sh
zarp --help
```

## Using the API

Next to using _ZARP-cli_'s eponymous command-line interface, you can also
integrate _ZARP-cli_'s functionalities into your Python projects via its API.

The main entry point for _ZARP-cli_'s high-level functionalities is the 
[`zarp.zarp.ZARP`](../docstring/zarp.md#class-zarp) class.

A basic code snippet to trigger _ZARP_ runs in your code might look like this:

```py
from zarp.zarp import ZARP

# set up ZARP-cli configuration and attach sample references (not shown)

zarp = ZARP(config=config)
zarp.set_up_run()
samples = zarp.process_samples()
zarp.execute_run(samples=samples)
```

??? info "Configuring `zarp.zarp.ZARP`"

    To configure `zarp.zarp.ZARP`, have a look at the 
    [`zarp.config.parser.ConfigParser`](../docstring/config.parser.md#class-configparser)
    class and the
    [`zarp.config.models.Config`](../docstring/config.models.md#class-config)
    model.

**A reference to the entire _ZARP-cli_ API is provided in the [API
overview](../docstring/README.md).**
