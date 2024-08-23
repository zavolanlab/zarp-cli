# Examples

This section provides a growing collection of examples that demonstrate how to
use _ZARP-cli_ in various scenarios.

!!! info "Prerequisites"
    
    The examples below assume that you have already [installed](./installation.md) and [initialized](./initialization.md) _ZARP-cli.

## Process samples deposited to SRA

Let's have ZARP-cli fetch two samples from SRA, infer all necessary metadata,
fetch the corresponding genome annotations and start a _ZARP_ workflow run on
them:

```sh
zarp SRR23590181 SRR23529108
```

??? tip "I want to verify the inferred metadata first!"

    Set the `--execution-mode` parameter to `PREPARE_RUN` to run _ZARP-cli_ up
    until the point of the actual _ZARP_ workflow execution:

    ```sh
    zarp --execution-mode=PREPARE_RUN SRR23590181 SRR23529108 
    ```

!!! info "More please!"

    You will find a description of more elaborate use cases in the [ZARP
    publication](https://doi.org/10.12688/f1000research.149237.1) and the
    accompanying [supplementary materials][zarp-supplementary], published on
    [Zenodo][zenodo]. The latter include detailed instructions, all necessary
    input files and a selection of reference output files to validate your runs
    against.