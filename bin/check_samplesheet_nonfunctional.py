#!/usr/bin/env python

import os
import sys
import errno
import argparse

def parse_args(args=None):
    Description = 'Reformat nf-core/bactmap samplesheet file and check its contents.'
    Epilog = """Example usage: python check_samplesheet.py <FILE_IN> <FILE_OUT>"""

    parser = argparse.ArgumentParser(description=Description, epilog=Epilog)
    parser.add_argument('FILE_IN', help="Input samplesheet file.")
    parser.add_argument('FILE_OUT', help="Output file.")
    return parser.parse_args(args)


def make_dir(path):
    if not len(path) == 0:
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


def print_error(error,line):
    print("ERROR: Please check samplesheet -> {}\nLine: '{}'".format(error,line.strip()))
    sys.exit(1)


def check_samplesheet(FileIn,FileOut):
    ## Check header
    HEADER = ['sample', 'fasta']
    fin = open(FileIn,'r')
    header = fin.readline().strip().split(',')
    if header != HEADER:
        print("ERROR: Please check samplesheet header -> {} != {}".format(','.join(header),','.join(HEADER)))
        sys.exit(1)

    sampleRunDict = {}
    while True:
        line = fin.readline()
        if line:
            lspl = [x.strip() for x in line.strip().split(',')]

            ## Check valid number of columns per row
            if len(lspl) != len(header):
                print_error("Invalid number of columns (minimum = {})!".format(len(header)),line)

            numCols = len([x for x in lspl if x])
            if numCols < 2:
                print_error("Invalid number of populated columns (minimum = 2)!",line)

            ## Check sample name entries
            sample,fastaFiles = lspl[0],lspl[1]
            if sample:
                if sample.find(' ') != -1:
                    print_error("Sample entry contains spaces!",line)
            else:
                print_error("Sample entry has not been specified!",line)

            ## Check Fasta file extension
            for fastaf in fastaFiles:
                if fastaf:
                    if fastaf.find(' ') != -1:
                        print_error("Fasta file contains spaces!",line)
                    if fastaf[-6:] != '.fasta' and fastaf[-3:] != '.fa' and fastaf[-4:] != '.fna':
                        print_error("Fasta file does not have extension '.fasta' or '.fa' or '.fna'!",line)

            ## Auto-detect paired-end/single-end
            sample_info = []                                                ## [single_end, is_sra, is_ftp, fastq_1, fastq_2, md5_1, md5_2]
            fasta = fastaFiles
            if sample and fasta:                              ## Paired-end short reads
                sample_info = ['1', '0', '0', fasta, '', '']
            else:
                print_error("Invalid combination of columns provided!",line)

            if sample not in sampleRunDict:
                sampleRunDict[sample] = [sample_info]
            else:
                if sample_info in sampleRunDict[sample]:
                    print_error("Samplesheet contains duplicate rows!",line)
                else:
                    sampleRunDict[sample].append(sample_info)
        else:
            fin.close()
            break

    ## Write validated samplesheet with appropriate columns
    if len(sampleRunDict) > 0:
        OutDir = os.path.dirname(FileOut)
        make_dir(OutDir)
        fout = open(FileOut,'w')
        fout.write(','.join(['sample_id', 'fasta']) + '\n')
        for sample in sorted(sampleRunDict.keys()):

            ## Check that multiple runs of the same sample are of the same datatype
            if not all(x[:2] == sampleRunDict[sample][0][:2] for x in sampleRunDict[sample]):
                print_error("Multiple runs of a sample must be of the same datatype","Sample: {}".format(sample))

            if len(sampleRunDict[sample]) > 1:
                for idx,val in enumerate(sampleRunDict[sample]):
                    fout.write(','.join(["{}_T{}".format(sample,idx+1)] + val) + '\n')
            else:
                fout.write(','.join(["{}".format(sample)] + sampleRunDict[sample][0]) + '\n')
        fout.close()


def main(args=None):
    args = parse_args(args)
    check_samplesheet(args.FILE_IN,args.FILE_OUT)


if __name__ == '__main__':
    sys.exit(main())
