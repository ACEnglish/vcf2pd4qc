"""
Count the SVTYPEs
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
 
def type_counter(data):
    """
    Single data frame type counting
    """
    return Counter(data["svtype"])

def proc_type_counter(fn):
    """
    process a single file to get the size_type count
    """
    data = joblib.load(fn)["table"]
    return type_counter(data)

def multi_type_counter(files, threads=1):
    """
    Multiple file type counting
    """
    all_cnt = Counter()
    p = Pool(threads)
    for piece in p.map(proc_type_counter, files):
        all_cnt.update(piece)
    return all_cnt

def format_type(data):
    """
    Pretty print the results
    """
    print("All SVs")
    for i in SV:
        print('{name}\t{count:,}'.format(name=i.name, count=data[i.value]))

def parse_args(args):
    parser = argparse.ArgumentParser(prog="type_counter", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vpd", nargs="+",
                        help="vcf2pd.jl files to parse")
    parser.add_argument("-t", "--threads", default=1, type=int,
                        help="Number of threads to use")
    return parser.parse_args(args)

def test():
    files = ["/users/u233287/mucnv_ccdg/dataframes/CCDG.chr1p13.2.jl",
             "/users/u233287/mucnv_ccdg/dataframes/CCDG.chr12q13.3.jl"]
    format_type(multi_type_counter(files, 1))


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    format_type(multi_type_counter(args.vpd, args.threads))
    
    
