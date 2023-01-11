"""Unit tests for ``:mod:zarp.config.args``."""

import argparse

import pytest

from zarp.config.args import ArgParser
from zarp.config.enums import (
    DependencyEmbeddingStrategies,
    ExecModes,
    OutputFileGroups,
)

VALID_SAMPLE_REF = "SRR1234567"


class TestArgParser:
    """Test ``:cls:zarp.config.args.ArgParser`` class."""

    def test_constructor_without_args(self):
        """Test class constructor without args."""
        parser = ArgParser()
        assert parser.args is None
        assert not hasattr(parser, "parser")

    def test_constructor_with_args(self):
        """Test class constructor with args."""
        args = ["path1", "path2"]
        parser = ArgParser(args=args)
        assert parser.args == args
        assert not hasattr(parser, "parser")

    def test_set_parser(self):
        """Test method ``.set_parser()``."""
        parser = ArgParser()
        assert not hasattr(parser, "parser")
        parser.set_parser()
        assert hasattr(parser, "parser")
        assert isinstance(parser.parser, argparse.ArgumentParser)

    def test_set_arguments(self):
        """Test method ``.set_arguments()``."""
        parser = ArgParser()
        parser.set_parser()
        parser.set_arguments()
        assert len(parser.parser._action_groups) == 7

    def test_parse_arguments_no_args(self):
        """Test method ``.parse_arguments()`` with no arguments."""
        args = []
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        assert not hasattr(parser, "args_parsed")
        parser.parse_arguments()
        assert hasattr(parser, "args_parsed")

    def test_parse_arguments_help_option(self):
        """Test method ``.parse_arguments()`` with option `--help`."""
        args = ["--help"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        with pytest.raises(SystemExit) as exc:
            parser.parse_arguments()
        assert exc.value.code == 0

    def test_parse_arguments_version_option(self):
        """Test method ``.parse_arguments()`` with option `--version`."""
        args = ["--version"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        with pytest.raises(SystemExit) as exc:
            parser.parse_arguments()
        assert exc.value.code == 0

    def test_parse_arguments_sample_ref(self):
        """Test method ``.parse_arguments()`` with sample reference."""
        args = [VALID_SAMPLE_REF]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        assert parser.args_parsed.sample_references == [VALID_SAMPLE_REF]

    def test_parse_arguments_invalid_option(self):
        """Test method ``.parse_arguments()`` with invalid argument."""
        args = ["--not-an-argument"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        with pytest.raises(SystemExit) as exc:
            parser.parse_arguments()
        assert exc.value.code == 2

    def test_process_arguments_required_args_missing(self):
        """Test method ``.process_arguments()`` with no arguments."""
        args = []
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        with pytest.raises(SystemExit) as exc:
            parser.process_arguments()
        assert exc.value.code == 1

    @pytest.mark.parametrize(
        "test_input", ["CONFIG", "LOGS", "RESULTS", "TEMPORARY"]
    )
    def test_process_arguments_cleanup_strategy_individual(self, test_input):
        """Test method ``.process_arguments()``.

        Use different individual arguments for option `--cleanup-strategy`.
        """
        args = [VALID_SAMPLE_REF, "--cleanup-strategy", test_input]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert parser.args_parsed.cleanup_strategy == [
            OutputFileGroups[test_input]
        ]

    def test_process_arguments_cleanup_strategy_all(self):
        """Test method ``.process_arguments()``.

        Use argument `ALL` for option `--cleanup-strategy`.
        """
        args = [VALID_SAMPLE_REF, "--cleanup-strategy", "ALL"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert parser.args_parsed.cleanup_strategy == [
            item for item in OutputFileGroups
        ]

    def test_process_arguments_cleanup_strategy_none(self):
        """Test method ``.process_arguments()``.

        Use argument `NONE` for option `--cleanup-strategy`.
        """
        args = [VALID_SAMPLE_REF, "--cleanup-strategy", "NONE"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert parser.args_parsed.cleanup_strategy == []

    def test_process_arguments_cleanup_strategy_combo(self):
        """Test method ``.process_arguments()``.

        Use a combination of different arguments for option
        '--cleanup-strategy'.
        """
        args = [
            VALID_SAMPLE_REF,
            "--cleanup-strategy",
            "CONFIG",
            "--cleanup-strategy",
            "LOGS",
            "--cleanup-strategy",
            "RESULTS",
            "--cleanup-strategy",
            "TEMPORARY",
        ]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()

    def test_process_arguments_cleanup_strategy_combo_invalid(self):
        """Test method ``.process_arguments()``.

        Use an invalid combination of different arguments for option
        '--cleanup-strategy'.
        """
        args = [
            VALID_SAMPLE_REF,
            "--cleanup-strategy",
            "CONFIG",
            "--cleanup-strategy",
            "ALL",
        ]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        with pytest.raises(SystemExit) as exc:
            parser.process_arguments()
        assert exc.value.code == 1

    @pytest.mark.parametrize(
        "test_input",
        ["DRY_RUN", "PREPARE_RUN", "RUN"],
    )
    def test_process_arguments_execution_mode(self, test_input):
        """Test method ``.process_arguments()``.

        Use different arguments for option `--execution-mode`.
        """
        args = [VALID_SAMPLE_REF, "--execution-mode", test_input]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert parser.args_parsed.execution_mode == ExecModes[test_input]

    @pytest.mark.parametrize(
        "test_input",
        ["CONDA", "SINGULARITY"],
    )
    def test_process_arguments_dependency_embedding(self, test_input):
        """Test method ``.process_arguments()``.

        Use different arguments for option `--dependency-embedding`.
        """
        args = [VALID_SAMPLE_REF, "--dependency-embedding", test_input]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert (
            parser.args_parsed.dependency_embedding
            == DependencyEmbeddingStrategies[test_input]
        )

    def test_process_arguments_source_int(self):
        """Test method ``.process_arguments()``.

        Use an integer identifier for option `--source`.
        """
        args = [VALID_SAMPLE_REF, "--source", "12345"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert isinstance(parser.args_parsed.source, int)
        assert parser.args_parsed.source == 12345

    def test_process_arguments_source_str(self):
        """Test method ``.process_arguments()``.

        Use a string identifier for option `--source`.
        """
        args = [VALID_SAMPLE_REF, "--source", "Homo sapiens"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert isinstance(parser.args_parsed.source, str)
        assert parser.args_parsed.source == "Homo sapiens"

    @pytest.mark.parametrize(
        "arg_name,arg_var",
        [
            ("--adapter-3p", "adapter_3p"),
            ("--adapter-5p", "adapter_5p"),
            ("--adapter-poly-3p", "adapter_poly_3p"),
            ("--adapter-poly-5p", "adapter_poly_5p"),
        ],
    )
    def test_process_arguments_adapt_single(self, arg_name, arg_var):
        """Test method ``.process_arguments()``.

        Use a single sequence for the different types of adapter options.
        """
        sequence = ("ACGTACGT", None)
        args = [VALID_SAMPLE_REF, arg_name, sequence[0]]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert getattr(parser.args_parsed, arg_var) == sequence

    @pytest.mark.parametrize(
        "arg_name,arg_var",
        [
            ("--adapter-3p", "adapter_3p"),
            ("--adapter-5p", "adapter_5p"),
            ("--adapter-poly-3p", "adapter_poly_3p"),
            ("--adapter-poly-5p", "adapter_poly_5p"),
        ],
    )
    def test_process_arguments_adapt_first_mate(self, arg_name, arg_var):
        """Test method ``.process_arguments()``.

        Use a single sequence for the first mates for the different types of
        adapter options.
        """
        sequence = ("ACGTACGT", None)
        args = [VALID_SAMPLE_REF, arg_name, f"{sequence[0]},"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert getattr(parser.args_parsed, arg_var) == sequence

    @pytest.mark.parametrize(
        "arg_name,arg_var",
        [
            ("--adapter-3p", "adapter_3p"),
            ("--adapter-5p", "adapter_5p"),
            ("--adapter-poly-3p", "adapter_poly_3p"),
            ("--adapter-poly-5p", "adapter_poly_5p"),
        ],
    )
    def test_process_arguments_adapt_second_mate(self, arg_name, arg_var):
        """Test method ``.process_arguments()``.

        Use a single sequence for the second mates for the different types of
        adapter options.
        """
        sequence = (None, "TGCATGCA")
        args = [VALID_SAMPLE_REF, arg_name, f",{sequence[1]}"]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert getattr(parser.args_parsed, arg_var) == sequence

    @pytest.mark.parametrize(
        "arg_name,arg_var",
        [
            ("--adapter-3p", "adapter_3p"),
            ("--adapter-5p", "adapter_5p"),
            ("--adapter-poly-3p", "adapter_poly_3p"),
            ("--adapter-poly-5p", "adapter_poly_5p"),
        ],
    )
    def test_process_arguments_adapt_paired(self, arg_name, arg_var):
        """Test method ``.process_arguments()``.

        Use two different sequences the different types of adapter options.
        """
        sequence = ("ACGTACGT", "TGCATGCA")
        args = [VALID_SAMPLE_REF, arg_name, ",".join(sequence)]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        assert getattr(parser.args_parsed, arg_var) == sequence

    def test_set_argument_groups(self):
        """Test method ``.set_argument_groups()``.

        Check for the presence of the various argument groups.
        """
        KEYS = set(["sample", "run", "user"])
        args = [VALID_SAMPLE_REF]
        parser = ArgParser(args=args)
        parser.set_parser()
        parser.set_arguments()
        parser.parse_arguments()
        parser.process_arguments()
        parser.set_argument_groups()
        assert all(item in parser.args_parsed.grouped for item in KEYS)
