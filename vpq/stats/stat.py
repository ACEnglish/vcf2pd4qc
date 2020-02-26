import argparse
from abc import ABC, abstractmethod

from vpq import fchain
import vpq.utils as vutils

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

