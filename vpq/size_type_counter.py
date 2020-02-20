"""
Collect the type/size information table across all the joblib pieces

arg1 - basedir of all the joblib pieces
arg2 - number of threads to use
"""
import sys
import glob
import joblib
import argparse
import pandas as pd
import matplotlib as plt
from multiprocessing import Pool

# can't use seaborn with this version of python... need to put in a ticket

from collections import Counter, defaultdict
from enum import Enum

class SV(Enum):
    DEL=0
    INS=1
    DUP=2
    INV=3

class GT(Enum):
    NON=3
    REF=0
    HET=1
    HOM=2
    UNK=4
    
SZBINS = ["(0,50]", "(50,100]", "(100,200]", "(200,300]", "(300,400]", 
          "(400,600]", "(600,800]", "(800,1k]", "(1k,2.5k]", 
          "(2.5k,5k]", ">5k"]

def size_bin(sz):
    """
    Bin a given size to a sizebin
    """
    if sz <= 50:
        return "(0,50]"
    elif sz <= 100:
        return "(50,100]"
    elif sz <= 200:
        return "(100,200]"
    elif sz <= 300:
        return "(200,300]"
    elif sz <= 400:
        return "(300,400]"
    elif sz <= 600:
        return "(400,600]"
    elif sz <= 800:
        return "(600,800]"
    elif sz <= 1000:
        return "(800,1k]"
    elif sz <= 2500:
        return "(1k,2.5k]"
    elif sz < 5000:
        return"(2.5k,5k]"
    else:
        return ">5k"

def open_jl(fn):
    """
    open/return joblib vcf2pd
    """
    return joblib.load(fn)

def split_by_type(data):
    """
    subset the data by types
    """
    for i in SV:
        yield i, data.loc[data["svtype"] == i.value]
  
def size_bin_counter(data, usemu=False):
    """
    Given a set of rows, calculate the sizebins
    """
    return Counter(data['szbin'])

def add_size_bin_column(data):
    """
    Add size bin column
    """
    data["szbin"] = data["svlen"].apply(size_bin)

def size_type_counter(data):
    """
    Single data frame size/type counting
    """
    cnt = {}
    for subtype, dat in split_by_type(data):
        cnt[subtype] = size_bin_counter(dat)
    return cnt

def proc_size_type_counter(fn):
    """
    process a single file to get the size_type count
    """
    data = open_jl(fn)["table"]
    add_size_bin_column(data)
    ret = size_type_counter(data)
    return ret

def multi_size_type_counter(files, threads=1):
    """
    Multiple data frame size/type counting
    """
    all_cnt = defaultdict(Counter)
    p = Pool(threads)
    for piece in p.map(proc_size_type_counter, files):
        for sv in piece:
            all_cnt[sv].update(piece[sv])
    return all_cnt

def format_size_type(data):
    """
    Pretty output
    """
    print("SV Type/Size Distribution")
    print("\t".join(["{:9s}".format('SIZE')] + [i.name for i in SV]))

    for key in SZBINS:
        print("\t".join(["{:9s}".format(key)] + ["{:,}".format(data[i][key]) for i in SV]))

def parse_args(args):
    parser = argparse.ArgumentParser(prog="type_counter", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vpd", nargs="+",
                        help="vcf2pd.jl files to parse")
    parser.add_argument("-t", "--threads", default=1, type=int,
                        help="Number of threads to use")
    return parser.parse_args(args)

if __name__ == '__main__':
    # Eventually I'll be able to glob this
    args = parse_args(sys.argv[1:])
    format_size_type(multi_size_type_counter(args.vpd, args.threads))

