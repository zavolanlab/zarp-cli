"""Mappings and lists for ZARP and ZARP-cli models and tables."""

map_zarp_to_model = {
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

map_model_to_zarp = {v: k for k, v in map_zarp_to_model.items()}

map_model_to_sra_in = {
    "identifier": "sample",
}

map_sra_out_to_model = {
    "sample": "identifier",
    "fq1": "paths_1",
    "fq2": "paths_2",
}

columns_sra_in = list(map_model_to_sra_in.values())

columns_sra_out = columns_sra_in + [
    "fq1",
    "fq2",
]

columns_zarp_path = [
    "fq1",
    "fq2",
    "gtf",
    "genome",
]

columns_zarp = list(map_zarp_to_model.keys())

columns_model = list(map_zarp_to_model.values()) + [
    "identifier",
    "type",
]
