"""
Collection of all the vpq stat command tools
"""
import sys
import joblib
import argparse
from abc import ABC, abstractmethod
from collections import defaultdict, Counter

import vpq

class CMDStat(ABC):
    """
    ABC of a command stat line tool
    """
    def __init__(self, pname, doc):
        """
        Stats must have a name for the command line
        """
        self.pname = pname
        self.doc = doc
    
    def parse_args(self, args):
        """ parse args """
        parser = argparse.ArgumentParser(prog=self.pname, description=self.doc,
        formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("vpd", nargs="+",
                            help="vcf2pd.jl files to parse")
        parser.add_argument("-t", "--threads", default=1, type=int,
                            help="Number of threads to use")
        return parser.parse_args(args)

class SampleGTCount(CMDStat):
    
    def __init__(self, args):
        super().__init__("sample_gt_cnt", __doc__)
        args = self.parse_args(args)
        pipe = [joblib.load, vpq.sample_gt_count]
        all_cnt = defaultdict(Counter)
        # consolidate
        for piece in vpq.fchain(pipe, args.vpd, args.threads):
            for samp in piece["samples"]:
                all_cnt[samp].update(piece["sample_gt_count"][samp])
        self.output(all_cnt)  
       
    def output(self, all_cnt):
        """
        Pretty table
        """
        sys.stdout.write("samp")
        for i in vpq.GT:
            sys.stdout.write("\t" + i.name)
        sys.stdout.write('\n')
        for samp, dat in all_cnt.items():
            sys.stdout.write(samp)
            for g in vpq.GT:
                sys.stdout.write("\t%d" % (dat[g.value]))
            sys.stdout.write('\n')
