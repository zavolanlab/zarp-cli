# Initialization

You will need to configure _ZARP-cli_ **once** to set some defaults. On this
page, you will find out everything about the initialization process.

## Configuring _ZARP-cli_

The following simple command triggers the _ZARP-cli_ initialization mode:

```bash
zarp --init
```

An interactive screen will guide you through the process. Read
[on](#configuration-options) to find out more about what each of the available
options and suggested defaults mean.

??? question "Where is the configuration stored?"

    The initialization process creates a `.zarp/` directory in your home
    directory and populates a configuration file with user defaults in
    `~/.zarp/user.yaml`.

??? question "I did not specify the `--init` option - why am I in init mode?"

    You may have inadvertently deleted or renamed the `~/.zarp/` directory or
    the _ZARP-cli_ configuration file expected at `~/.zarp/user.yaml`. If this
    file is absent or inaccessible, _ZARP-cli_ will trigger the initialization
    mode, even if it was started in normal mode.


## Configuration options

The following configuration options are available.

!!! tip "Press <kbd>Enter</kbd> to keep the suggested default"

| Option | Description | Default |
| ------ | ----------- | ------- |
| `working_directory` | Root directory for _ZARP-cli_ runs; needs to be writable | `$HOME/.zarp` |
| `zarp_directory` | Path to the local copy of the [ZARP workflow repository][zarp] | `../zarp` relative to the location of the ZARP-cli repository |
| `execution_mode` | Trigger a full _ZARP-cli_ run (`RUN`), a dry run (`DRY_RUN`; external tools are not actually run, only logs what _would be_ run; useful for testing) or prepare a _ZARP_ run (`PREPARE_RUN`; _ZARP-cli_ is run normally, including all external tools, up until the point of the execution of the actual _ZARP_ workflow; use to manually check metadata table before execution)  | `RUN` |
| `cores` | Number of CPU cores that Snakemake is run with when executing _ZARP_ and the auxiliary workflows (fetching libraries from [SRA][sra], inferring metadata) | `1` |
| `dependency_embedding` | Whether Snakemake should use `CONDA` or containers (`SINGULARITY`) to manage dependencies of each workflow step/rule (note that the auxiliary workflows currently have restrictions on which dependency embedding strategy can be used; if an unsupported scheme is suggested, a warning is emitted and the other one is enabled by default) | `CONDA` |
| `genome_assemblies_map` | A headerless 3-column semicolon-separated mapping table of organism/source trivial names (e.g., `homo_sapiens`), optional comma-separated aliases such as NCBI taxon IDs and/or organism/source short names (e.g., `7227,dmelanogaster`) and a corresponding genome assembly name (e.g., `GRCm39`); a table in the required format is shipped with _ZARP_cli_ in the location provided in the default location; which can be amended with additional aliases; note that for [`genomepy`][genomepy] to be able to pull genome annotations for organisms/sources that [HTSinfer][htsinfer] inferred, NCBI taxon ID aliases are _required_  | `./data/genome_assemblies.map` relative to the location of the ZARP-cli repository |
| `resources_version` | Whether to always download the latest available version of genome annotations for a given organism/source from Ensembl (enter `None`; default) or whether to use a specific version of the corresponding Ensembl database (e.g., `100`); note that the different Ensembl databases (e.g., for fungi, plants) use a different versioning scheme, so pinning a particular database version may lead to unexpected outcomes | `None` |
| `rule_config` | A configuration file for the _ZARP_ workflow that sets specific parameters for each workflow step ("rule"); see [ZARP][zarp] documentation for details | `None` |
| `profile` | Path to [Snakemake profile][snakemake-profiles] to be used for the _ZARP_ workflow. Use this to optimize _ZARP_ for your specific compute environment |
| `fragment_length_distribution_mean` | HTSinfer currently is unable to infer the mean of the fragment length distribution of RNA-seq libraries; however, this value is required for tools [`kallisto`][kallisto] and [`salmon`][salmon] -which are executed as part of _ZARP_- when run on single-ended libraries only (for paired-ended libraries, the tools are able to infer this parameter from the data); the value provided here is used as a fallback if the value was not determined experimentally (e.g., with [Bioanalyzer][bioanalyzer] instruments) and provided via a sample table | `300` |
| `fragment_length_distribution_sd` | Analogous to `fragment_length_distribution_mean` above, but this parameter is for the _standard deviation_ of the fragment length distribution | `100` |
| `author` | Name of the person or organization executing the _ZARP-cli_ runs; will be added to the _ZARP_ report | `None` |
| `email` | Email of the person or organization executing the _ZARP-cli_ runs; will be added to the _ZARP_ report | `None` |
| `url` | URL of the person or organization executing the _ZARP-cli_ runs; will be added to the _ZARP_ report | `None` |
| `logo` | Logo (file path or URL) of the person or organization executing the _ZARP-cli_ runs; will be added to the _ZARP_ report | `None` |

## Modifying configuration settings

There are two ways in which you can **permanently change the default
configuration settings**:

- **Re-run `zarp --init`**  
  Suggested defaults are now taken from the current
  contents of `~/.zarp/user.yaml`, which will then be overridden with the
  values supplied during the interactive initialization mode
- **Edit configuration file in a text editor**  
  Simply edit the `~/.zarp/user.yaml` file in a text editor; however, make sure
  that only valid values are provided, as inputs are not checked

Additionally, there are ways in which you can **modify configuration settings
dynamically**:

- **Providing a custom configuration file**  
  It is possible to specify a custom configuration file via the `--config-file`
  CLI parameter; this could be a copy of an old/alternative `~/.zarp/user.yaml`
  file or a subset with only some of the parameters; however, the format has
  to strictly follow that of the default configuration file in order for the
  custom configuration file contents to take effect
- **Setting individual CLI arguments**  
  _ZARP-cli_ provides a range of run-specific [CLI parameters](./usage.md)
  that, when specified, will override the default configuration settings for a
  given run
- **Setting sample-specific parameters in sample tables**
  _ZARP-cli_'s ability to process sample table allows setting of most sample-
  specific parameters via _ZARP_ sample tables

??? Note "Configuration setting precedence"

    The ability to provide configuration settings in various ways requires
    us to resolve conflicting settings in a predictable and user-friendly
    manner. In _ZARP-cli_ configuration settings are applied iteratively, with
    values sourced from a current iteration overriding those from any previous
    iterations. The following configuration sources are applied successively:
    
    - Defaults hardwired in the code **(lowest precedence!)**
    - Contents of default configuration file at `~/.zarp/user.yaml`
    - Contents of custom configuration file supplied via `--config-file`, if
    provided
    - [CLI arguments](./usage.md) for individual run- and sample-specific
    parameters, if provided
    - Sample-specific parameters specified in sample tables **(highest
    precendence!)**
