"""Unit tests for module `zarp.config.ensembl_downloads`."""

import gzip
import importlib.util
from pathlib import Path
import sys
import tempfile

import pytest

from zarp.config.ensembl_downloads import (
    main,
    GenResDownloader
)

# Test parameters
MAIN_FILE = Path(__file__).parents[2].absolute() / "zarp" /"config"/ "ensembl_downloads.py"

def test_main_as_script():
    """Run as script."""
    spec = importlib.util.spec_from_file_location('__main__', MAIN_FILE)
    module = importlib.util.module_from_spec(spec)
    with pytest.raises(SystemExit):
        spec.loader.exec_module(module)

class TestMain:
    """Test `main()` function."""

    def test_main(self):
        """Call without args."""
        with pytest.raises(SystemExit):
            main()

    def test_main_with_args(self, monkeypatch):
        """Call with args."""
        monkeypatch.setattr(
            sys, 'argv', [
                'ensembl_downloads',
                '-s', 'caenorhabditis_elegans',
                '-o', '.',
                '-g', 'caenorhabditis_elegans_genome.fa',
                'a', 'caenorhabditis_elegans_annotation.gff3'
            ]
        )
        assert main() is None


class  TestVerifySpeciesData:
    """Test verify_species_data() function."""

    def test_taxon_id_argument(self):
        """Call with taxon ID."""
        assert GenResDownloader(6239).verify_species_data() is None

    def test_species_name_argument(self):
        """Call with species name."""
         assert GenResDownloader('caenorhabidtis_elegans').verify_species_data()  is None
        
    def test_incorrect_argument_format(self):
        """Call with incorrect species name."""
        with pytest.raises(KeyError):
            gd = GenResDownloader('c_elegans')
            assert gd.verify_species_data()

    def test_incorrect_argument(self):
        """Call with incorrect species argument."""
        with pytest.raises(AttributeError):
            gd = GenResDownloader('celegans')
            assert gd.verify_species_data()

    def test_correct_taxon_id_download(self):
        """Call with correct argument."""
        gd = GenResDownloader(9606)
        assert gd.species_name == 'homo_sapiens'

    def test_correct_species_name_download(self):
        """Call with correct argument."""
        gd = GenResDownloader('homo_sapiens')
        assert str(gd.taxon_id) == '9606'


class TestCompileGenomeParts(self):
    """Test compile_genome_parts() function."""

    def test_correct_params(self):
        """Call with a correctly constructed object."""
        gd = GenResDownloader('caenorhabditis_elegans')
        gd.species_name = 'caenorhabditis_elegans'
        gd.taxon_id = '6239'
        gd.release = '105'

        assert gd.compile_genome_parts() is None

    def test_incorrect_params(self):
        """Call with a incorrectly constructed object."""
        gd = GenResDownloader('caenorhabditis_elegans')
        gd.species_name = 'c_elegans'
 
       with pytest.raises(AttributeError):
           gd.compile_genome_parts()


class TestCheckChr(self):
    """Test that chromosomes have expected length."""

    def test_no_len_data(self):
        """Call without chromosome length data from server."""
        gd = GenResDownloader("caenorhabditis_elegans")

        with pytest.raises(ValueError):
            gd.check_chr("I", "I.fa.gz")

    def test_no_seq_data(self):
        """Call without sequence file."""
        gd = GenResDownloader("caenorhabditis_elegans")
        gd.chr_length["I"] = 0

        with pytest.raises(ValueError):
            gd.check_chr("I", "I.fa.gz")

    def test_incorrect_file_type(self):
        """Call with incorrect file type."""
        gd = GenResDownloader("caenorhabditis_elegans")

        with tempfile.NamedTemporaryFile() as ftmp:
            ftmp.write('Nothing')
            with pytest.raises(ValueError):
                gd.check_chr("I", f.name)

    def test_mismatch_data(self):
        """Call without chromosome length data from server."""
        gd = GenResDownloader("caenorhabditis_elegans")
        gd.chr_length["I"] = 10

        with tempfile.NamedTemporaryFile() as ftmp:
            content = b">I\n\n"
            with gzip.open(ftmp.name+".gz", "wb") as oftmp:
                oftmp.write(content)
                assert gd.check_chr("I", oftmp.name) == False

    def test_mismatch_data(self):
        """Call without chromosome length data from server."""
        gd = GenResDownloader("caenorhabditis_elegans")
        gd.chr_length["I"] = 4

        with tempfile.NamedTemporaryFile() as ftmp:
            content = b">I\nACGT\n"
            with gzip.open(ftmp.name+".gz", "wb") as oftmp:
                oftmp.write(content)
                assert gd.check_chr("I", oftmp.name) == True


class TestGetGenome(self):
    """Test the download of genome sequence data."""

    def test_correct_run(self):
        """Check a correct run."""
        gd = GenResDownloader("caenorhabditis_elegans")
        gd.species_name = 'caenorhabditis_elegans'
        gd.taxon_id = '6239'
        gd.release = '105'
        with tempfile.NamedTemporaryFile() as tfile:
            tdir_name = Path(tfile).parents[1]
            assert gd.get_genome(tdir_name, tfile.name) is None

    def test_incorrect_species_run(self):
        """Check an incorrect species run."""
        gd = GenResDownloader("caenorhabditis_elegans")
        gd.species_name = 'c_elegans'
        gd.release = '105'
        with tempfile.NamedTemporaryFile() as tfile:
            tdir_name = Path(tfile).parents[1]

            with pytest.raises(ValueError):
                gd.get_genome(tdir_name, tfile.name)


class TestGetGenome(self):
    """Test the download of annotation data."""

    def test_correct_run(self):
        """Check a correct run."""
        gd = GenResDownloader("caenorhabditis_elegans")
        gd.species_name = 'caenorhabditis_elegans'
        gd.taxon_id = '6239'
        gd.release = '105'
        with tempfile.NamedTemporaryFile() as tfile:
            tdir_name = Path(tfile).parents[1]
            assert gd.get_annotation(tdir_name, tfile.name) is None

    def test_incorrect_species_run(self):
        """Check an incorrect species run."""
        gd = GenResDownloader("caenorhabditis_elegans")
        gd.species_name = 'c_elegans'
        gd.release = '105'
        with tempfile.NamedTemporaryFile() as tfile:
            tdir_name = Path(tfile).parents[1]

            with pytest.raises(ValueError):
                gd.get_annotation(tdir_name, tfile.name)
