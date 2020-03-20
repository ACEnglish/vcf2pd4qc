"""
Collection of all the vpq stat command tools
"""
import argparse
from io import StringIO
from abc import ABC, abstractmethod
from collections import defaultdict, Counter, OrderedDict

import numpy as np
import pandas as pd

import vpq


class CMDStat(ABC):
    """
    ABC of a command stat line tool
    """
    pname = "CMDStat"

    def __init__(self):
        """
        Stats must have a name for the command line
        """

    @staticmethod
    def parse_args(mcls, args):
        """ parse args """
        parser = argparse.ArgumentParser(prog=mcls.pname, description=mcls.__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("vpd", nargs="+",
                            help="vcf2pd.jl files to parse")
        parser.add_argument("-t", "--threads", default=1, type=int,
                            help="Number of threads to use")
        return parser.parse_args(args)

    @classmethod
    @abstractmethod
    def cmd_line(cls, args):
        """
        Run the stat from command line
        """

    @abstractmethod
    def to_txt(self):
        """
        Convert the result to text
        """

    def write_table(self, fn):
        """
        Write self.to_txt()
        """
        with open(fn, 'w') as fh:
            fh.write(self.to_txt())


class TypeCounter(CMDStat):
    """ Count the SVTYPEs """
    pname = "typecnt"

    def __init__(self, vpds, threads=1):
        super().__init__()
        pipe = [vpq.jl_load,
                vpq.add_cnt_column,
                (vpq.groupcnt, {"key": "type_count", "group": ["svtype"]})
                ]
        # Consolidate
        self.result = pd.DataFrame(np.zeros(len(vpq.SV), dtype=int),
                                   columns=["cnt"],
                                   index=range(len(vpq.SV)))
        for piece in vpq.fchain(pipe, vpds, threads):
            self.result = self.result.add(piece["type_count"].fillna(0), axis=0)
        self.result = self.result.fillna(0)

    @classmethod
    def cmd_line(cls, args):
        """ Parse args and return init'd object """
        args = super().parse_args(cls, args)
        return cls(args.vpd, args.threads)

    def to_txt(self):
        """
        Format results to string
        """
        ret = StringIO()
        ret.write("##" + self.__doc__ + '\n')
        ret.write("#svtype\tcount\n")
        for i in vpq.SV:
            ret.write('{name}\t{count:,.0f}\n'.format(name=i.name, count=self.result.loc[i.value]["cnt"]))
        ret.seek(0)
        return ret.read()


class SizebinTypeCounter(CMDStat):
    """ Count the SVType by Sizebin """

    pname = "size_type_cnt"

    def __init__(self, vpds, threads=1):
        super().__init__()
        pipe = [vpq.jl_load,
                vpq.categorize_sv, # This allows for some pieces to still be around, but as zeros...
                vpq.add_cnt_column,
                vpq.add_sizebin_column,
                (vpq.groupcnt, {"key": "sztype_count", "group": ["szbin", "svtype"]})]
        # we have to make szbins a series so pd won't reorder it
        self.result = pd.MultiIndex.from_product([pd.Series(vpq.SZBINS), range(len(vpq.SV))]).to_frame()
        self.result["cnt"] = 0
        for _ in vpq.fchain(pipe, vpds, threads):
            self.result["cnt"] += _["sztype_count"].fillna(0)

    @classmethod
    def cmd_line(cls, args):
        """ Parse args and return init'd object """
        args = super().parse_args(cls, args)
        return cls(args.vpd, args.threads)

    def to_txt(self):
        """
        Pretty output
        """
        ret = StringIO()
        ret.write("##" + self.__doc__ + '\n')
        ret.write("#" + "\t".join(["{:9s}".format('SIZE')] + [i.name for i in vpq.SV]) + '\n')
        for key in vpq.SZBINS:
            ret.write("\t".join(["{:9s}".format(key)] + ["{:,.0f}".format(self.result.cnt[key][i.value]) for i in vpq.SV]) + '\n')
        ret.seek(0)
        return ret.read()


class SampleGTCounter(CMDStat):
    """ Per Sample GT Counts """

    pname = "sample_gt_cnt"

    def __init__(self, vpds, threads):
        super().__init__()
        pipe = [vpq.jl_load,
                vpq.sample_gt_count]
        self.result = defaultdict(Counter)
        # consolidate
        for piece in vpq.fchain(pipe, vpds, threads):
            for samp in piece["samples"]:
                self.result[samp].update(piece["sample_gt_count"][samp])

    @classmethod
    def cmd_line(cls, args):
        """ Parse args and return init'd object """
        args = super().parse_args(cls, args)
        return cls(args.vpd, args.threads)

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


class QualbinCounter(CMDStat):
    """ Quality score counts by bin """

    pname = "qualbin_cnt"

    def __init__(self, vpds, threads=1):
        super().__init__()
        pipe = [vpq.jl_load,
                vpq.add_cnt_column,
                vpq.add_qualbin_column,
                (vpq.groupcnt, {"key": "qualbin_count", "group": ["qualbin"]})
                ]
        # consolidate
        self.result = pd.DataFrame(np.zeros(len(vpq.QUALBINS), dtype=int),
                                   columns=["cnt"],
                                   index=vpq.QUALBINS)

        for piece in vpq.fchain(pipe, vpds, threads):
            self.result = self.result.add(piece["qualbin_count"].fillna(0), axis=0)
        self.result = self.result.fillna(0)

    @classmethod
    def cmd_line(cls, args):
        """ Parse args and return init'd object """
        args = super().parse_args(cls, args)
        return cls(args.vpd, args.threads)

    def to_txt(self):
        """ Pretty table """
        ret = StringIO()
        ret.write("##" + self.__doc__ + '\n')
        ret.write("#bin\tcount\n")
        for i in vpq.QUALBINS:
            ret.write("%s\t%d\n" % (i, self.result.loc[i]["cnt"]))
        ret.seek(0)
        return ret.read()

# inprogress
# class SVCountPerChromType(CMDStat):
#    """ Number of SVs per chromosome by type """

# Lookup of each of the commands for easy calling by stats_main
STATCMDs = OrderedDict()
STATCMDs["type_cnt"] = TypeCounter
STATCMDs["size_type_cnt"] = SizebinTypeCounter
STATCMDs["sample_gt_cnt"] = SampleGTCounter
STATCMDs["qualbin_cnt"] = QualbinCounter
