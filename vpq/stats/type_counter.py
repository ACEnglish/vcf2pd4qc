"""
Count the SVTYPEs
"""
from collections import Counter

import joblib
import pandas as pd
# can't use seaborn with this version of python... need to put in a ticket

from vpq import fchain
import vpq.utils as vutils
from vpq.stats.stat import CMDStat

# Can i move these to a library of functions...
# Would need to standardize their use
# data is always a dict with at-least {'table', 'samples'} keys... never remove that...
def type_counter(data):
    """
    Single data frame type counting
    """
    data["type_count"] = Counter(data["table"]["svtype"])
    return data

class TypeCounter(CMDStat):
    """ Count the SVTYPEs """
    def __init__(self, args):
        super().__init__("typecnt", __doc__)
        args = self.parse_args(args)
        pipe = [joblib.load, type_counter]
        # Consolidate
        all_cnt = Counter()
        for piece in fchain(pipe, args.vpd, args.threads):
            all_cnt.update(piece)
        self.output(all_cnt)

    def output(self, data):
        """
        Pretty print the results
        """
        print("All SVs")
        for i in vutils.SV:
            print('{name}\t{count:,}'.format(name=i.name, count=data["type_count"][i.value]))

       
def main():
    pass

def test():
    fns = ["/home/english/science/english/WhitePaper/Quintuplicates/biograph_results/dataframes/quint.chr10p11.1.jl"]
    x = TypeCounter(fns)
    
if __name__ == '__main__':
    test()
