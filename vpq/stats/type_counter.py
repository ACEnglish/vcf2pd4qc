"""
Count the SVTYPEs
"""
from collections import Counter

import joblib
# can't use seaborn with this version of python... need to put in a ticket

from vpq import fchain
from vpq.utils import SV
from vpq.stats.stat import CMDStat
from vpq.stats.tools import type_counter

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
        for i in SV:
            print('{name}\t{count:,}'.format(name=i.name, count=data["type_count"][i.value]))
