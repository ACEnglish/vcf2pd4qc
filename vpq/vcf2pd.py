#!/usr/bin/env python
# coding: utf-8
"""
Convert a vcf into a dataframe
"""
import sys
import argparse
from collections import Counter

import numpy
import pysam
import joblib
import pandas as pd

from vpq.utils import GT, SV
from vpq.parsers import VPQParsers

def vcf_to_frame(m_converter, m_vcf, cols, chrom=None, start=None, end=None):
    """
    Pull in all of the relevant information for parsing the SVs
    """
    # Fetch every entry over the region
    if chrom is not None:
        fetch = m_vcf.fetch(chrom, start, end)
    else:
        fetch = m_vcf
    
    data = []
    for entry in fetch:
        if chrom is not None and not (start <= entry.pos < end):
            continue # start must be in region - prevent duplicated entries
        cur = m_converter.parse_entry(entry)
        data.append([t[1](x) for t,x in zip(m_converter.cols, cur)])

    ret = pd.DataFrame(data, columns=[x[0] for x in m_converter.cols]) 
    return ret


def parse_args(args):
    parser = argparse.ArgumentParser(prog="vcf2pd", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vcf_fn",
                        help="vcf to parse")
    parser.add_argument("-r", "--regions", default=None,
                        help="Bed File of chrom, start, end, name to create")
    parser.add_argument("-o", "--out", default="vcf2pd.jl",
                        help="Joblib file outfile suffix ('chrname.jl' may be appended from -r)")
    parser.add_argument("-p", "--parser", choices=VPQParsers.keys(), default='skeleton',
                        help="Column parsing object")
    return parser.parse_args(args)

    
def vcf2pd_main(args):
    """
    Run the program
    """
    args = parse_args(args)
    vcf_fn = args.vcf_fn
    # We'll require regions to start
    regions = []
    if args.regions is None:
        regions.append[(None, None, None, 'all')]
    else:
        with open(args.regions, 'r') as fh:
            for line in fh:
                data = line.strip().split('\t')
                data[1] = int(data[1])
                data[2] = int(data[2])
                regions.append(data[:4])
        
    v = pysam.VariantFile(vcf_fn)
    m_converter = VPQParsers[args.parser](v) # Something I'll figure out how to get...?
    cols, samples = m_converter.make_header()
    for chrom, start, end, name in regions:
        data = {"table": vcf_to_frame(m_converter, v, cols, chrom, start, end), "samples": samples}
        if name is not None:
            oname = "%s%s%s.jl" % (args.out, chrom, name)
        else:
            oname = args.out + ".jl"
        joblib.dump(data, oname, compress=9)

