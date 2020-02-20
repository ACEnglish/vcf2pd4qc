"""
Count the SVTYPEs
"""
import sys
import glob
import joblib
import argparse
# can't use seaborn with this version of python... need to put in a ticket

from collections import Counter

from vpq import fchain
import vpq.utils as vutils

def open_jl(fn):
    return joblib.load(fn)["table"]

def type_counter(data):
    """
    Single data frame type counting
    """
    return Counter(data["svtype"])

def format_type(data):
    """
    Pretty print the results
    """
    print("All SVs")
    for i in vutils.SV:
        print('{name}\t{count:,}'.format(name=i.name, count=data[i.value]))

def parse_args(args):
    parser = argparse.ArgumentParser(prog="type_counter", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("vpd", nargs="+",
                        help="vcf2pd.jl files to parse")
    parser.add_argument("-t", "--threads", default=1, type=int,
                        help="Number of threads to use")
    return parser.parse_args(args)

def main(args):
    """ Count the SVTYPEs """
    args = parse_args(args)
    pipe = [open_jl, type_counter]
    # Consolidate
    all_cnt = Counter()
    for piece in fchain(pipe, args.vpd, args.threads):
        all_cnt.update(piece)
    format_type(all_cnt)
    
