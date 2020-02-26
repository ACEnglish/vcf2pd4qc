"""
Collect the Type by Size 
"""
import joblib
from collections import Counter, defaultdict
# import seaborn as sb can't use seaborn with this version of python... need to put in a ticket

from vpq import fchain
from vpq.utils import SV, SZBINS
from vpq.stats.stat import CMDStat
from vpq.stats.tools import add_sizebin_column, split_by_type, sizebin_type_counter

class SizebinTypeCounter(CMDStat):
    def __init__(self, args):
        super().__init__('sztypecnt', __doc__)
        args = self.parse_args(args)
        pipe = [joblib.load, add_sizebin_column, split_by_type, sizebin_type_counter]
        # Consolidate
        all_cnt = defaultdict(Counter)
        for piece in fchain(pipe, args.vpd, args.threads):
            for sv in piece:
                all_cnt[sv].update(piece[sv])
        self.output(all_cnt)

    def output(self, data):
        """
        Pretty output
        """
        print("SV Type/Size Distribution")
        print("\t".join(["{:9s}".format('SIZE')] + [i.name for i in SV]))

        for key in SZBINS:
            print("\t".join(["{:9s}".format(key)] + ["{:,}".format(data[i][key]) for i in SV]))
