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

def extract_sample(entry):
    """
    Extract the GT and normalized depth for all the samples
    """
    gts = []
    dps = []
    for sample in entry.samples:
        gt = entry.samples[sample]["GT"]
        if None in gt:
            gt = GT.NON.value
        elif gt == (0, 0):
            gt = GT.REF.value
        elif gt == (0, 1):
            gt = GT.HET.value
        elif gt == (1, 1):
            gt = GT.HOM.value
        else:
            gt = GT.UNK.value
        gts.append(gt)
        dps.append(entry.samples[sample]["DP"])
    
    return gts, dps

def make_header(v):
    """
    Given a vcf, make the dataframe header information
    returns columns [(name, type), ..], [samples, ...]
    """
    cols = [("chrom", str), 
            ("start", int),
            ("end", int),
            ("svtype", numpy.uint8),
            ("svlen", int),
            ("ac", numpy.uint16),
            ("ns", numpy.uint16),
            ("af", numpy.float32),
            ("callrate", numpy.float16),
            ("mustart", int),
            ("muend", int),
            ("mulen", int)]
    # Collecting sample header
    samples = [x for x in v.header.samples]
    cols.extend([(x + "_gt", numpy.uint8) for x in samples])
    cols.extend([(x + "_dp", numpy.float16) for x in samples])
    return cols, samples

def vcf_to_frame(m_vcf, cols, chrom=None, start=None, end=None):
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
        muBP_start, muBP_end = muBP(entry)
        svtype = entry.info["SVTYPE"]
        # Convert STR to ENUM
        if svtype == "DEL":
            svtype = SV.DEL.value
        elif svtype == "INS":
            svtype = SV.INS.value
        elif svtype == "DUP":
            svtype = SV.DUP.value
        elif svtype == "INV":
            svtype = SV.INV.value
        else:
            print("UNK SVTYPE!! %s" % (str(entry)))
        cur = [entry.chrom,
               entry.start, 
               entry.stop,
               svtype,
               entry.info["SVLEN"],
               entry.info["AC"],
               entry.info["NS"],
               entry.info["AF"][0],
               entry.info["CALLRATE"],
               muBP_start, muBP_end, abs(muBP_end - muBP_start)]
        gts, dps = extract_sample(entry)
        cur.extend(gts)
        cur.extend(dps)
        # type casting - I hate that I'm making the current row twice, could be improved
        data.append([t[1](x) for t,x in zip(cols, cur)])
    ret = pd.DataFrame(data, columns=[x[0] for x in cols]) 
    return ret


def parse_args(args):
    parser = argparse.ArgumentParser(prog="vcf2pd", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vcf_fn",
                        help="vcf to parse")
    parser.add_argument("-r", "--region", default=None,
                        help="CHROM:START-END to parse")
    parser.add_argument("-o", "--out", default="vcf2pd.jl",
                        help="Joblib file to write")
    return parser.parse_args(args)

    
def main(args):
    """
    Run the program
    """
    args = parse_args(args)
    vcf_fn = args.vcf_fn
    # We'll require regions to start
    if args.region is None:
        chrom, start, end = None, None, None
    else:
        chrom, other = args.region.split(':')
        start, end = [int(x) for x in other.split('-')]
        
    v = pysam.VariantFile(vcf_fn)
    cols, samples = make_header(v)
    data = {"table": vcf_to_frame(v, cols, chrom, start, end), "samples": samples}
    joblib.dump(data, args.out, compress=9)


if __name__ == '__main__':
    main(sys.argv[1:])

