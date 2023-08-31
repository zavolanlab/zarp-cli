"""Mappings and lists for ZARP and ZARP-cli models and tables."""

from typing import Dict, List

map_zarp_to_model: Dict = {
    "sample": "name",
    "organism": "source",
    "gtf": "annotations",
    "genome": "reference_sequences",
    "sd": "fragment_length_distribution_sd",
    "mean": "fragment_length_distribution_mean",
    "libtype": "read_orientation",
    "index_size": "star_sjdb_overhang",
    "kmer": "salmon_kmer_size",
    "fq1": "paths_1",
    "fq2": "paths_2",
    "fq1_3p": "adapter_3p_1",
    "fq2_3p": "adapter_3p_2",
    "fq1_5p": "adapter_5p_1",
    "fq2_5p": "adapter_5p_2",
    "fq1_polya_3p": "adapter_poly_3p_1",
    "fq2_polya_3p": "adapter_poly_3p_2",
    "fq1_polya_5p": "adapter_poly_5p_1",
    "fq2_polya_5p": "adapter_poly_5p_2",
    "seqmode": "sequencing_mode",
}

map_model_to_zarp: Dict = {v: k for k, v in map_zarp_to_model.items()}

map_model_to_sra_in: Dict = {
    "identifier": "sample",
}

map_sra_out_to_model: Dict = {
    "sample": "identifier",
    "fq1": "paths_1",
    "fq2": "paths_2",
}

columns_sra_in: List = list(map_model_to_sra_in.values())

columns_sra_out: List = columns_sra_in + [
    "fq1",
    "fq2",
]

columns_zarp_path: List = [
    "fq1",
    "fq2",
    "gtf",
    "genome",
]

columns_zarp: List = list(map_zarp_to_model.keys())

columns_model: List = list(map_zarp_to_model.values()) + [
    "assembly",
    "identifier",
    "source_sanitized",
    "type",
]
