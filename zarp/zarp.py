#!/usr/bin/env python
"""CLI runner for the ZARP RNA-Seq analysis pipeline."""

import logging

LOGGER = logging.getLogger(__name__)


class ZARP:
    """Interface for zarp workflow execution.
    Args:
        sample1: Path to single-end library or first mate file.
        sample2: Path to second mate file.
        out_dir: Path to directory where output is written to.

    Attributes:

    """
    def __init__(  # pylint: disable=too-many-arguments
        self,
        sample_1,
        sample_2,
        name,
        output_directory,
        organism,
        gtf,
        genome,
        init,
        read_orientation,
        adapter_3p,
        trim_polya,
        fragment_length_mean,
        fragment_length_sd,
        multimappers,
        soft_clip,
        no_inference,
        htsinfer_config,
        tool_packaging,
        profile,
        execution_mode,
        no_report,
        delete_files,
        run_description,
        run_identifier,
        logo,
        url,
        author,
        author_email,
    ):
        """Class constructor."""
        self.sample_1 = sample_1
        self.sample_2 = sample_2
        self.name = name
        self.output_directory = output_directory
        self.organism = organism
        self.gtf = gtf
        self.genome = genome
        self.init = init
        self.read_orientation = read_orientation
        self.adapter_3p = adapter_3p
        self.trim_polya = trim_polya
        self.fragment_length_mean = fragment_length_mean
        self.fragment_length_sd = fragment_length_sd
        self.multimappers = multimappers
        self.soft_clip = soft_clip
        self.no_inference = no_inference
        self.htsinfer_config = htsinfer_config
        self.tool_packaging = tool_packaging
        self.profile = profile
        self.execution_mode = execution_mode
        self.no_report = no_report
        self.delete_files = delete_files
        self.run_description = run_description
        self.run_identifier = run_identifier
        self.logo = logo
        self.url = url
        self.author = author
        self.author_email = author_email

    def evaluate(self):
        """Evaluate sample data."""
