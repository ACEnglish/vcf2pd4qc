"""
Collection of all the vpq stat command tools
"""
import joblib
import argparse
from io import StringIO
from abc import ABC, abstractmethod
from collections import defaultdict, Counter, OrderedDict

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

    @abstractmethod
    def to_txt(self):
        """
        Convert the result to text
        """
        pass
    
    def write_table(self, fn):
        """
        Write self.to_txt()
        """
        with open(fn, 'w') as fh:
            fh.write(self.to_txt())


class TypeCounter(CMDStat):
    """ Count the SVTYPEs """
    def __init__(self, args):
        super().__init__("typecnt", __doc__)
        args = self.parse_args(args)
        pipe = [joblib.load,
               vpq.type_counter]
        # Consolidate
        self.result = Counter()
        for piece in vpq.fchain(pipe, args.vpd, args.threads):
            self.result.update(piece)

    def to_txt(self):
        """
        Format results to string
        """
        ret = StringIO()
        ret.write("##" + self.__doc__ + '\n')
        ret.write("#svtype\tcount\n")
        for i in vpq.SV:
            ret.write('{name}\t{count:,}\n'.format(name=i.name, count=self.result["type_count"][i.value]))
        ret.seek(0)
        return ret.read()

class SizebinTypeCounter(CMDStat):
    """ Count the SVType by Sizebin """
    def __init__(self, args):
        super().__init__('sztypecnt', self.__doc__)
        args = self.parse_args(args)
        pipe = [joblib.load, 
               vpq.add_sizebin_column,
               vpq.split_by_type,
               vpq.sizebin_type_counter]
        # Consolidate
        self.result = defaultdict(Counter)
        for piece in vpq.fchain(pipe, args.vpd, args.threads):
            for sv, cnt in piece['sizebin_type_count'].items():
                self.result[sv].update(cnt)

    def to_txt(self):
        """
        Pretty output
        """
        ret = StringIO()
        ret.write("##" + self.__doc__ + '\n')
        ret.write("#" + "\t".join(["{:9s}".format('SIZE')] + [i.name for i in vpq.SV]) + '\n')
        for key in vpq.SZBINS:
            ret.write("\t".join(["{:9s}".format(key)] + ["{:,}".format(self.result[i][key]) for i in vpq.SV]) + '\n')
        ret.seek(0)
        return ret.read()

class SampleGTCount(CMDStat):
    """ Per Sample GT Counts """
    def __init__(self, args):
        super().__init__("sample_gt_cnt", self.__doc__)
        args = self.parse_args(args)
        pipe = [joblib.load,
               vpq.sample_gt_count]
        self.result = defaultdict(Counter)
        # consolidate
        for piece in vpq.fchain(pipe, args.vpd, args.threads):
            for samp in piece["samples"]:
                self.result[samp].update(piece["sample_gt_count"][samp])
       
    def to_txt(self):
        """
        Pretty table
        """
        ret = StringIO()
        ret.write("##" + self.__doc__ + '\n')
        ret.write("#samp")
        for i in vpq.GT:
            ret.write("\t" + i.name)
        ret.write('\n')
        for samp, dat in self.result.items():
            ret.write(samp)
            for g in vpq.GT:
                ret.write("\t%d" % (dat[g.value]))
            ret.write('\n')
        ret.seek(0)
        return ret.read()

# Lookup of each of the commands for easy calling by stats_main
STATCMDs = OrderedDict()
STATCMDs["type_cnt"] = TypeCounter
STATCMDs["size_type_cnt"] = SizebinTypeCounter
STATCMDs["sample_gt_cnt"] = SampleGTCount


