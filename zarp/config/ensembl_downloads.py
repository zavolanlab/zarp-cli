#!/usr/bin/env python

"""Genome resource builder.

Given a species code, download genome and annotation
information from ENSEMBL.

Args:
   species(str): species name or taxon id
   out_dir(int): output directory
   genome(str): name of genome sequence file
   annotation(str): name of anno file
"""

import argparse
import os
import re
import subprocess
from collections import defaultdict
import requests


class GenResDownloader:
    """Download genome and annotation from EMSEMBL."""

    # ENSEMBL data servers/end points
    server = "https://rest.ensembl.org"
    info = "/info/species/"
    assembly = "/info/assembly/"

    ftp_server = "http://ftp.ensembl.org/pub/"
    dna_dir_path = ["fasta", "dna"]
    anno_type = "gff3"
    anno_path = anno_type + "/"

    def __init__(self, in_species):
        """Generate object.

        Creates a downloader object for the species of interest.

        Args:
            species(int or str): Taxon ID or species name.

        Returns:
            GenResDownloader instance.
        """
        self.in_species = in_species
        self.release = ""
        self.taxon_id = ""
        self.species_name = ""
        self.chr_length = {}

    def verify_species_data(self):
        """Verify that there is data about the species of interest.

        Check whether data for the species of interest in available
        in the current release of ENSEMBL.

        Raises:
            AttributeError: Species name not understood.
            AttributeError: Release number not found.
            AttributeError: Taxon id not found.
            AttributeError: Species name not found.
            KeyError: Misformatted species table.

        """
        # check that the input is species name or taxon ID
        search_field = ""
        species_indicator = ""
        if isinstance(self.in_species, int):
            # input parameter is probably taxon id
            search_field = 'taxon_id'
            species_indicator = str(self.in_species)
        elif re.search(r'^[a-zA-Z]+_[a-zA-Z]+$', self.in_species):
            # input parameter is probably species name
            search_field = 'name'
            species_indicator = self.in_species.lower()
        else:
            # input parameter not understood
            mssg = f'"{self.in_species}" not understood. '
            mssg += 'Should be a species name or taxon ID.'
            raise AttributeError(mssg)

        # get the ENSEMBL species info table
        url = self.server + self.info
        response = requests.get(url,
                                headers={"Content-Type": "application/json"})
        species_table = response.json()

        # look for the information we need
        if 'species' not in species_table.keys():
            mssg = "Misformatted species table: "
            mssg += "does not contain the 'species' key"
            raise KeyError(mssg)

        for item in species_table['species']:
            if isinstance(item, dict) and search_field in item.keys():
                if item[search_field].lower() == species_indicator:
                    if 'release' in item.keys():
                        self.release = item['release']
                    if 'taxon_id' in item.keys():
                        self.taxon_id = item['taxon_id']
                    if 'name' in item.keys():
                        self.species_name = item['name']

        if not self.release or not self.taxon_id or not self.species_name:
            mssg = f"{self.in_species}: "
            mssg += "Release version or taxon id or species name "
            mssg += "not found in species table"
            raise AttributeError(mssg)

    def compile_genome_parts(self):
        """Gather chromosome info for this species.

        Extract the chromosome IDs for this species,
        and get the chromosome lengths.

        Raises:
            AttributeError: No karyotype given in the species record.
        """
        if not self.species_name:
            self.verify_species_data()

        url = self.server + self.assembly + self.species_name
        response = requests.get(url,
                                headers={"Content-Type": "application/json"})
        species_info = response.json()
        if 'karyotype' not in species_info.keys():
            mssg = f'No karyotype found for "{self.species_name}"'
            raise AttributeError(mssg)
        if 'top_level_region' not in species_info.keys():
            mssg = 'No "top_level_region" dictionary '
            mssg += f'for "{self.species_name}"'
            raise AttributeError(mssg)

        self.chr_length = defaultdict(int)
        for item in species_info['top_level_region']:
            if 'coord_system' not in item.keys():
                mssg = "Cannot recognize region type in {item}"
                raise AttributeError(mssg)
            if item['coord_system'] == 'chromosome':
                if 'name' not in item.keys():
                    mssg = "No chromosome name in {item}"
                    raise AttributeError(mssg)
                if 'length' not in item.keys():
                    mssg = "No chromosome length in {item}"
                    raise AttributeError(mssg)
                self.chr_length[item['name']] = item['length']

    def check_chr(self, chromosome, file_name):
        """Check legnth of the downloaded sequence.

        Check whether the chromosome sequence that was
        downloaded has the expected length.

        Args:
            chromosome (str): Name of chromosome.
            file_name (str): Name of gzipped seq file.

        Returns:
            chr_ok (bool): lengths match?.

        Raises:
            ValueError: No length available for chromosome.
            ValueError: Sequence file not found.
        """
        if chromosome not in self.chr_length:
            raise ValueError(f'No {chromosome} length data')
        if not os.path.exists(file_name):
            raise ValueError(f'No such file {file_name} exists')
        # unzip file and count letters
        cmd = ['gunzip', '-c', f'{file_name}']
        nr_letters = 0
        with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
            for line in proc.stdout:
                # decode byte to characters
                line = line.decode()
                if line[0] == ">":
                    continue
                # for some reason the newline seems
                # to not be removed by strip()
                # so we use regex
                line = re.sub(r'[^a-zA-Z]', '', line)
                nr_letters += len(line)
            proc.wait()
            if proc.returncode != 0:
                mssg = f'Problem when gunzipping {file_name}'
                raise ValueError(mssg)

        return nr_letters == self.chr_length[chromosome]

    def get_genome(self, out_dir, file_name):
        """Download chromosome sequence data.

        Extract the chromosome sequences for this species,
        concatenate them into a single genome sequence,
        save to a file.

        Args:
            out_dir (str): Output directory.
            file_name (str): Name of genome file.

        Raises:
            ValueError: List of files not found on server.
            ValueError: Cannot find/parse sequence file name.
            ValueError: Could not get chr file of correct len.
        """
        if not self.chr_length:
            self.compile_genome_parts()

        # create output directory if it does not exist
        os.makedirs(out_dir, exist_ok=True)

        url = self.ftp_server + f'release-{self.release}/'
        url += f'{self.dna_dir_path[0]}/{self.species_name}/'
        url += f'{self.dna_dir_path[1]}/'
        files = []

        # get the content of fasta/{species}/dna dir
        mssg = requests.get(url)

        # parse out file names
        result = True
        suffix = mssg.text
        while result:
            result = re.search(r'<a href="([^>"]+)">(.*)', suffix, re.DOTALL)
            if result:
                (prefix, suffix) = (result.group(1), result.group(2))
                files.append(prefix)

        # if available, save the soft-masked sequences
        # otherwise the standard chromosome sequences
        prefix = [x for x in files if re.search("dna_sm.chr", x)]
        suffix = [x for x in files if re.search("dna.chr", x)]
        files = suffix
        if len(prefix) >= len(suffix):
            files = prefix

        # save bits of the file name structure
        # to then request chromosome files
        if not files:
            raise ValueError(f'No chromosome files found in {url}')
        result = re.search(r"^(\S+chromosome\.)\S+(\.fa\S*)$", files[0])
        if not result:
            raise ValueError(f"Cannot parse file name in {files[0]}")
        (prefix, suffix) = (result.group(1), result.group(2))

        # download chromosome files
        files = []
        for k in self.chr_length:
            # make at most 3 tries to get a sequence of expected length
            mssg = False
            tries = 0
            print(f'Getting sequence of {k}')
            chr_name = prefix + f'{k}' + suffix
            fname = out_dir + "/" + chr_name
            while not mssg and tries < 3:
                tries += 1
                # get sequence
                result = requests.get(url + chr_name)
                # save in the output dir
                with open(fname, 'wb') as outf:
                    outf.write(result.content)
                mssg = self.check_chr(k, fname)
            if not mssg:
                # we have to quit
                # clean up files we got so far
                for chr_name in files:
                    os.system(f'rm {chr_name}')
                mssg = f'Could not get correct sequence for {k}'
                raise ValueError(mssg)
            files.append(fname)

        if files:
            # concatenate all chromosome sequences
            cmd = "gunzip -c " + " ".join(files)
            cmd += f" > {out_dir}/{file_name}; "
            cmd += "rm " + " ".join(files) + "; "
            cmd += f"gzip {out_dir}/{file_name}"
            os.system(cmd)
            print(f"Done saving/gzipping {file_name}")

    def get_annotation(self, out_dir, file_name):
        """Get annotation info for the species.

        Extract the gff annotation for the species.

        Args:
            out_dir (str): Directory where data should be placed.
            file_name (str): File name where data should be placed.

        Raises:
            ValueError: Cannot find/parse annotation file name.
        """
        if not self.chr_length:
            self.compile_genome_parts()

        # create output directory if it does not exist
        os.makedirs(out_dir, exist_ok=True)

        url = self.ftp_server + f'release-{self.release}/'
        url += self.anno_path
        url += f'{self.species_name}/'
        files = []

        # get annotation directory content
        mssg = requests.get(url)

        # determine which files we want to download
        pattern = True
        suffix = mssg.text
        while pattern:
            pattern = re.search(r'<a href="([^>"]+)">(.*)', suffix, re.DOTALL)
            if pattern:
                (prefix, suffix) = (pattern.group(1), pattern.group(2))
                files.append(prefix)

        files = [x for x in files if re.search(r"\.chromosome", x)]

        # save bits of file name structure
        # to then request chromosome files
        if not files:
            raise ValueError(f'No chromosome annotations found in {url}')
        pattern = rf"^(\S+chromosome\.)\S+(\.{self.anno_type}\S*)$"
        result = re.search(pattern, files[0])
        if result:
            (prefix, suffix) = (result.group(1), result.group(2))
        else:
            raise ValueError(f"Cannot parse file name in {files[0]}")

        # download annotations
        files = []
        for k in self.chr_length:
            print(f'Getting annotation of {k}')
            chr_name = prefix + f'{k}' + suffix
            result = requests.get(url + chr_name)
            fname = out_dir + "/" + chr_name
            files.append(fname)
            with open(fname, 'wb') as outf:
                outf.write(result.content)

        # concatenate annotation files
        if files:
            cmd = "gunzip -c " + " ".join(files)
            cmd += f" > {out_dir}/{file_name}; "
            cmd += "rm " + " ".join(files) + "; "
            cmd += f"gzip {out_dir}/{file_name}"
            os.system(cmd)
            print(f"Done saving/gzipping {file_name}")


def main(raw_args=None):
    """Get genome sequence and annotation info a species.

    Args:
        species (int or str): Taxon ID or species name.
        outdir (str): Directory where data should be placed.

    Returns:
        None

    Raises:
        ValueError: Cannot find/parse sequence file name.
    """
    parser = argparse.ArgumentParser(description='Download species data.')
    parser.add_argument('-s', dest='species', action='store', required=True,
                        help="Taxon id or species name")
    parser.add_argument('-o', dest='outdir', action='store', required=True,
                        help="Output directory")
    parser.add_argument('-g', dest='genome', action='store', required=True,
                        help="Name of genome file")
    parser.add_argument('-a', dest='annotation', action='store', required=True,
                        help="Name of annotation file")

    args = parser.parse_args(raw_args)

    # create output file if not there already
    os.makedirs(args.outdir, exist_ok=True)

    # create downloader object
    worker = GenResDownloader(args.species)

    # get genome data
    worker.get_genome(args.outdir, args.genome)

    # get annotation data
    worker.get_annotation(args.outdir, args.annotation)


if __name__ == '__main__':
    main()
