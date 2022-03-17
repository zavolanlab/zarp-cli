#!/usr/bin/env python                                                           
"""Genomic resource builder."""

import argparse
import os
import re
import requests
import sys
from collections import defaultdict

# ENSEMBL data servers/end points
server = "https://rest.ensembl.org"
info = "/info/species/"
assembly = "/info/assembly/"

ftp_server = "http://ftp.ensembl.org/pub/"
dna_dir_path = ["fasta", "dna"]
anno_type = "gff3"
anno_path = anno_type + "/"

def verify_species_data(server, info, species):
    """Verify that there is data about the species of interest.

    Check whether data for the species of interest in available
    in the current release of ENSEMBL. 

    Args:
        server (string): Root of the data path.
        info (str): Type of data that we want.
        species(int or str): Taxon ID or species name.

    Returns:
        tuple: Release number, taxon id, species name.

    Raises:
        requests.exceptions.HTTPError: Request cannot be satisfied.
        AttributeError: Species name not understood.

    """

    # check that the input is species name or taxon ID 
    search_field = ""
    try:
        if(type(species) == int):
            # input parameter is taxon id
            search_field = 'taxon_id'
            species = str(species)
        elif(re.search('^[a-zA-Z]+\_[a-zA-Z]+$', species)):
            # input parameter is species name
            search_field = 'name'
            species = species.lower()
        else:
            # input parameter not understood
            raise AttributeError(f'"{species}" not understood. Should be a species name or taxon ID.')

    except AttributeError as err:
        raise
        
    # get the ENSEMBL species info table
    try:
        response = requests.get(server+info, headers={ "Content-Type" : "application/json"})
        response.raise_for_status()
        species_table = response.json()
    except requests.exceptions.HTTPError as e: 
        raise

    # look for the information we need
    (release, taxon_id, name) = ("", "", "")
    for item in species_table['species']:
        if search_field not in item.keys():
            continue
        if item[search_field] == species:
            if 'release' in item.keys():
                release = item['release']
            if 'taxon_id' in item.keys():
                taxon_id = item['taxon_id']
            if 'name' in item.keys():
                name = item['name']

    return (release, taxon_id, name)


def compile_genome_parts(server, assembly, species):
    """Gather chromosome info for this species.

    Extract the chromosome IDs for this species,
    and get the chromosome lengths. 

    Args:
        server (string): Root of the data path.
        assembly (str): Type of data that we want.
        species(int or str): Taxon ID or species name.

    Returns:
        dict(int): Dictionary of chromosome lenghts.

    Raises:
        requests.exceptions.HTTPError: Request cannot be satisfied.
        AttributeError: No karyotype given in the species record.

    """
    
    try:
        response = requests.get(server+assembly+str(species), headers={ "Content-Type" : "application/json"})
        response.raise_for_status()
        species_info = response.json()
        if not species_info['karyotype']:
            raise AttributeError(f'No karyotype found for "{species}".')
        else:
            data = defaultdict(int)
            for item in species_info['top_level_region']:
                if(item['coord_system'] == 'chromosome'):
                    data[item['name']] = item['length']
            return data
    except requests.exceptions.HTTPError as e: 
        raise 

def get_genome_parts(ftp_server, dna_dir_path, release, species, chrs, outdir):
    """Download chromosome sequence data.

    Extract the chromosome sequences for this species,
    concatenate them into a single genome sequence,
    save to a file. 

    Args:
        ftp_server (string): Root of the data path.
        dna_dir_path (list): Type of data that we want (fasta & dna).
        release (int): Release version.
        species (int or str): Taxon ID or species name.
        chrs (dict): Chromosome and lengths.
        outdir (str): Directory for the output.
        
    Returns:
        None.

    Raises:
        ValueError: Cannot find/parse sequence file name.

    """    

    url = ftp_server + f'release-{release}/{dna_dir_path[0]}/{species}/{dna_dir_path[1]}/'
    files = []
    
    # get a list of files in fasta/{species}/dna dir
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as err:
        raise

    # parse the directory content to determine the files we want to download
    result = True
    r = response.text
    while result:
        result = re.search('<a href=\"([^\>\"]+)\">([\s\S]*)$', r)
        if result:
            (link, rest) = (result.group(1), result.group(2))
            files.append(link)
            r = rest

    # if available, save the soft-masked sequences
    # otherwise the standard chromosome sequences
    sm_files = [x for x in files if re.search("dna_sm\.chromosome", x)]
    nm_files = [x for x in files if re.search("dna\.chromosome", x)]
    if(len(sm_files) >= len(nm_files)):
        files = sm_files
    else:
        files = nm_files

    # save bits of the file name structure
    # to then request chromosome files
    if(files):
        file_root = re.search("^(\S+chromosome\.)\S+(\.fa\S*)$", files[0])
        if(file_root):
            (prefix, suffix) = (file_root.group(1), file_root.group(2))
        else:
            raise ValueError(f"Cannot parse file name in {files[0]}")
    else:
        raise ValueError(f"Cannot find sequence files") 

    # download chromosome files
    files = []
    for k in chrs:
        print(f'Getting sequence of {k}')
        chr_name = prefix + f'{k}' + suffix
        
        # get sequence
        try:
            chr_req = requests.get(url + chr_name)
            chr_req.raise_for_status()
        except Exception as err:
            raise
        # save in the output dir
        fname = outdir + "/" + chr_name
        files.append(fname)
        with open(fname, 'wb') as outf:
            outf.write(chr_req.content)

    return files

def get_annotation(ftp_server, anno_path, release, species, chrs, outdir):
    """Get annotation info for this species.

    Extract the gff annotation for this species.

    Args:
        ftp_server (string): Root of the data path.
        anno_part (str): Type of data that we want (e.g. gff3).
        release (int): Release number.
        species (int or str): Taxon ID or species name.
        chrs (dict): Dictionary of chromosome lengths.
        outdir (str): Directory where data should be placed.

    Returns:
        None

    Raises:
        ValueError: Cannot find/parse sequence file name.

    """

    url = ftp_server + f'release-{release}/' + anno_path + f'{species}/'
    files = []

    # get list of files in the annotation directory
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as err:
        raise
        
    # determine which files we want to download
    result = True
    r = response.text
    while result:
        result = re.search('<a href=\"([^\>\"]+)\">([\s\S]*)$', r)
        if result:
            (link, rest) = (result.group(1), result.group(2))
            files.append(link)
            r = rest

    files = [x for x in files if re.search("\.chromosome", x)]

    # save bits of file name structure
    # to then request chromosome files
    if(files):
        file_root = re.search(rf"^(\S+chromosome\.)\S+(\.{anno_type}\S*)$", files[0])
        if(file_root):
            (prefix, suffix) = (file_root.group(1), file_root.group(2))
        else:
            raise ValueError(f"Cannot parse file name in {files[0]}")
    else:
        raise ValueError(f"Cannot find sequence files") 

    # download annotations
    files = []
    for k in chrs:
        print(f'Getting annotation of {k}')
        chr_name = prefix + f'{k}' + suffix
        chr_req = requests.get(url + chr_name)
        fname = outdir + "/" + chr_name
        files.append(fname)
        with open(fname, 'wb') as outf:
            outf.write(chr_req.content)
    
    return files

def main(raw_args=None):
    """Get genome sequence and annotation info a species.

    Args:
        species (int or str): Taxon ID or species name.
        outdir (str): Directory where data should be placed.
        genome (str): Genome sequence file name.
        annotation (str): Annotation file name.

    Raises:
        argparse.ArgumentError: Cannot parse arguments
        requests.Exception.HTTPError: Cannot download doc
        AttributeError: Parameters not understood
        Exception: Other errors

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
    try:
        args = parser.parse_args(raw_args)
    except argparse.ArgumentError as err:
        sys.exit(err)
    
    # create output file if not there already
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # check that information about our species of interest
    # exists in the current ENSEMBL release
    try:
        species_info = verify_species_data(server, info, args.species)
    except (requests.exceptions.HTTPError, AttributeError) as err:
        sys.exit(err)

    # get karyotype and chromosome lengths
    try:
        chrs = compile_genome_parts(server, assembly, args.species)
    except requests.exceptions.HTTPError as e:
        sys.exit(err)

    # download chromosome sequence data
    try:
        seq_files = get_genome_parts(ftp_server, dna_dir_path, 
                                     species_info[0], species_info[2], 
                                     chrs, args.outdir)
    except Exception as err:
        sys.exit(err)
    
    # concatenate chromosome sequences
    try:
        cmd = "gunzip -c " + " ".join(seq_files) + f" > {args.outdir}/{args.genome}; "
        cmd += "rm " + " ".join(seq_files) + "; "
        cmd += f"gzip {args.outdir}/{args.genome}"
        os.system(cmd)
    except Exception as err:
        sys.exit(err)
        
    # download annotation data
    try:
        anno_files = get_annotation(ftp_server, anno_path, 
                                    species_info[0], species_info[2], 
                                    chrs, args.outdir)
    except Exception as err:
        sys.exit(err)
   
    # concatenate annotation files
    try:
        cmd = "gunzip -c " + " ".join(anno_files) + f" > {args.outdir}/{args.annotation}; "
        cmd += "rm " + " ".join(anno_files) + "; "
        cmd += f"gzip {args.outdir}/{args.annotation}"
        os.system(cmd)
    except Exception as err:
        sys.exit(err)

if __name__ == '__main__':
    main()

