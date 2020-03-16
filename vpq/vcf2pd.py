#!/usr/bin/env python
# coding: utf-8
"""
Convert a vcf into a dataframe
"""
import argparse

import pysam
import joblib
import pandas as pd

import vpq


def vcf_to_frame(m_converter, chrom=None, start=None, end=None):
    """
    Pull in all of the relevant information for parsing the SVs
    """
    # Fetch every entry over the region
    m_vcf = m_converter.vcf
    if chrom is not None:
        fetch = m_vcf.fetch(chrom, start, end)
    else:
        fetch = m_vcf

    data = []
    for entry in fetch:
        if chrom is not None and not start <= entry.pos < end:
            continue  # start must be in region - prevent duplicated entries
        cur = m_converter.parse_entry(entry)
        data.append([t[1](x) for t, x in zip(m_converter.cols, cur)])

    ret = pd.DataFrame(data, columns=[x[0] for x in m_converter.cols])
    return ret


def parse_args(args):
    """
    argparse
    """
    parser = argparse.ArgumentParser(prog="vcf2pd", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vcf_fn",
                        help="vcf to parse")
    parser.add_argument("-r", "--regions", default=None,
                        help="Bed File of chrom, start, end, name to create")
    parser.add_argument("-o", "--out", default="vcf2pd.jl",
                        help="Joblib file outfile suffix ('chrname.jl' may be appended from -r)")
    parser.add_argument("-p", "--parser", choices=vpq.VPQParsers.keys(), default='skeleton',
                        help="Column parsing object")
    parser.add_argument("-t", "--threads", default=1, type=int,
                        help="When regions are provided, allow up to threads workers")
    return parser.parse_args(args)


def task(item):
    """
    Given a task item, do the work
    task item is a dictionary of {"input":input.vcf, "parser": parsername, "output":outputname, "chrom", "start", "end"}
    """
    v = pysam.VariantFile(item["input"]) # pylint: disable=no-member
    m_converter = vpq.VPQParsers[item["parser"]](v)  # Something I'll figure out how to get...?
    cols, samples = m_converter.make_header()
    data = {"table": vcf_to_frame(m_converter, item["chrom"], item["start"], item["end"]), "samples": samples}
    joblib.dump(data, item["output"], compress=9)


def vcf2pd_main(args):
    """
    Run the program
    """
    args = parse_args(args)
    vcf_fn = args.vcf_fn
    # We'll require regions to start
    regions = []
    if args.regions is None:
        regions.append((None, None, None, 'all'))
    else:
        with open(args.regions, 'r') as fh:
            for line in fh:
                data = line.strip().split('\t')
                data[1] = int(data[1])
                data[2] = int(data[2])
                regions.append(data[:4])
    items = []
    for chrom, start, end, name in regions:
        if name is not None:
            oname = "%s%s%s.jl" % (args.out, chrom, name)
        else:
            oname = args.out + ".jl"
        items.append({"input": vcf_fn, "parser": args.parser, "output": oname,
                      "chrom": chrom, "start": start, "end": end})
    # must iterate once to ensure we got the results made
    [_  for _ in vpq.fchain([task], items, args.threads)]
