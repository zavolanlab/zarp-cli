"""
Dummy version of Snakefile for downloading inferring RNA-Seq sample
metadata with HTSinfer.
"""


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

