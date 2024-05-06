#!/usr/bin/env python

import os
import sys
import errno
import argparse


def parse_args(args=None):
    Description = 'Reformat samplesheet and check its contents for fasta files.'
    Epilog = """Example usage: python check_samplesheet.py <FILE_IN> <FILE_OUT>"""

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument('FILE_IN', help="Input samplesheet file.")
    parser.add_argument('FILE_OUT', help="Output file.")
    return parser.parse_args(args)


def make_dir(path):
    if path:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


def print_error(error, line):
    print("ERROR: Please check samplesheet -> {}\nLine: '{}'".format(error, line.strip()))
    sys.exit(1)


def check_samplesheet(FileIn, FileOut):
    # Expected header
    HEADER = ['sample', 'fasta']
    fin = open(FileIn, 'r')
    header = fin.readline().strip().split(',')
    if header != HEADER:
        print("ERROR: Please check samplesheet header -> {} != {}".format(','.join(header),','.join(HEADER)))
        sys.exit(1)

    sampleRunDict = {}
    while True:
        line = fin.readline()
        if not line:
            break
        lspl = [x.strip() for x in line.strip().split(',')]

        # Validate number of columns and if they match expected
        if len(lspl) != len(HEADER):
            print_error("Invalid number of columns!", line)

        sample, fasta = lspl
        if not sample:
            print_error("Sample name is missing!", line)

        if ' ' in sample:
            print_error("Sample name contains spaces!", line)

        if ' ' in fasta:
            print_error("Fasta filename contains spaces!", line)

        if not any(fasta.endswith(ext) for ext in ['.fasta', '.fna', '.fa']):
            print_error("Fasta file has an invalid extension. Expected .fasta, .fna, or .fa", line)

        # Add to dictionary, check for duplicates
        if sample not in sampleRunDict:
            sampleRunDict[sample] = [fasta]
        elif fasta in sampleRunDict[sample]:
            print_error("Samplesheet contains duplicate rows!", line)
        else:
            sampleRunDict[sample].append(fasta)

    fin.close()

    # Write the validated samplesheet with appropriate columns
    if sampleRunDict:
        OutDir = os.path.dirname(FileOut)
        make_dir(OutDir)
        fout = open(FileOut, 'w')
        fout.write(','.join(HEADER) + '\n')  # Write header
        for sample, fasta_files in sampleRunDict.items():
            for fasta in fasta_files:
                fout.write(f'{sample},{fasta}\n')  # Write data
        fout.close()


def main(args=None):
    args = parse_args(args)
    check_samplesheet(args.FILE_IN, args.FILE_OUT)


if __name__ == '__main__':
    sys.exit(main())
