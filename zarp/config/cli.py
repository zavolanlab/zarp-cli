#!/usr/bin/env python3
import argparse
from pydantic import BaseModel
from pydantic_cli import run_and_exit


def parse_cli_args() -> argparse.Namespace:
    """
    Parses command line arguments.

    :returns: parsed CLI arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fq1")
    parser.add_argument("fq2")
    parser.add_argument("--name")
    parser.add_argument("--sra")
    parser.add_argument("--read_orientation")
    parser.add_argument("--adapter-3p")
    parser.add_argument("--no-inference")  # disable htsinfer
    parser.add_argument("--htsinfer-config")
    parser.add_argument("--tool-packaging")  # conda or singularity
    parser.add_argument("--profile")
    parser.add_argument("--dry-run")
    parser.add_argument("--execution-mode")  # dry-run, prepare-run and run
    parser.add_argument("---no-report")
    parser.add_argument("--delete-files")
    parser.add_argument("--out-dir")
    parser.add_argument("--fragment-length-mean") 
    parser.add_argument("--fragment-length-sd")
    parser.add_argument("--organism") 
    parser.add_argument("--trim-polya")
    parser.add_argument("--gtf")
    parser.add_argument("--genome") 
    parser.add_argument("---multimappers")
    parser.add_argument("--soft-clip")
    parser.add_argument("--pass-mode")
    parser.add_argument("--run-description")
    parser.add_argument("--run-identifier")
    parser.add_argument("--logo")
    parser.add_argument("--url")
    parser.add_argument("--author")
    parser.add_argument("--author-email")
    parser.add_argument("--init")
    
    args = parser.parse_args()

    
    
    return args