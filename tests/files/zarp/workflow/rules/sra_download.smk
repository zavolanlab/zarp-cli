"""Dummy version of Snakefile for downloading samples from SRA."""


localrules:
    dummy,
    all,


rule all:
    input:
        config["samples_out"],


rule dummy:
    output:
        config["samples_out"],
    shell:
        'echo "sample\tfq1" > {output}'

