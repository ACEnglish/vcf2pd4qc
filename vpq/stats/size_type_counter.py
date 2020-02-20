"""
Collect the type/size information table across all the joblib pieces
"""
import sys
import glob
import argparse
from enum import Enum
from multiprocessing import Pool
from collections import Counter, defaultdict
# import seaborn as sb can't use seaborn with this version of python... need to put in a ticket

import joblib
import pandas as pd
import matplotlib as plt

from vpq import fchain
import vpq.utils as vutils

def open_jl(fn):
    """
    open/return joblib vcf2pd
    """
    return joblib.load(fn)["table"]


def add_size_bin_column(data):
    """
    Add size bin column
    """
    data["szbin"] = data["svlen"].apply(vutils.size_bin)
    return data

def split_by_type(data):
    """
    subset the data by types
    """
    for i in vutils.SV:
        yield i, data.loc[data["svtype"] == i.value]
  
def size_bin_counter(data, usemu=False):
    """
    Given an interable of [(SV, dataframe),..]
    Create a dict with key of each SV and value a Counter over sizebins
    returns the dict
    """
    cnt = {}
    for subtype, dat in data:
        cnt[subtype] = Counter(dat["szbin"])
    return cnt

def format_size_type(data):
    """
    Pretty output
    """
    print("SV Type/Size Distribution")
    print("\t".join(["{:9s}".format('SIZE')] + [i.name for i in vutils.SV]))

    for key in vutils.SZBINS:
        print("\t".join(["{:9s}".format(key)] + ["{:,}".format(data[i][key]) for i in vutils.SV]))

def parse_args(args):
    parser = argparse.ArgumentParser(prog="type_counter", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vpd", nargs="+",
                        help="vcf2pd.jl files to parse")
    parser.add_argument("-t", "--threads", default=1, type=int,
                        help="Number of threads to use")
    return parser.parse_args(args)

def main(args):
    """ Collect the type/size information table across all the joblib pieces """
    args = parse_args(args)
    pipe = [open_jl, add_size_bin_column, split_by_type, size_bin_counter]
    # Consolidate
    all_cnt = defaultdict(Counter)
    for piece in fchain(pipe, args.vpd, args.threads):
        for sv in piece:
            all_cnt[sv].update(piece[sv])
    format_size_type(all_cnt)

