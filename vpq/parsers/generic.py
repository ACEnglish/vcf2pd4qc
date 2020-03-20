"""
Generic vcf parser - more functional than skeleton, but also assumes a "clean" vcf
"""
import numpy

import vpq
from vpq.parsers.VCF2PD import VCF2PD


class generic(VCF2PD):
    """ Parse generic VCF """

    def __init__(self, vcf):
        super().__init__(vcf)
        self.cols, self.samples = self.make_header()

    def make_header(self):
        """
        Given a vcf, make the dataframe header information
        returns columns [(name, type), ..], [samples, ...]
        """
        cols = [("chrom", str),
                ("start", int),
                ("end", int),
                ("qual", numpy.uint8),
                ("filt", str),
                ("svtype", numpy.uint8),
                ("svlen", int)]

        # Collecting sample header
        samples = [x for x in self.vcf.header.samples]
        cols.extend([(x + "_gt", numpy.uint8) for x in samples])
        cols.extend([(x + "_gq", numpy.uint8) for x in samples])
        cols.extend([(x + "_dp", numpy.int) for x in samples])
        return cols, samples

    def extract_sample(self, entry):
        """ Extract the GT, GQ and DP for all the samples """
        gts = []
        gqs = []
        dps = []
        for sample in entry.samples:
            gt = entry.samples[sample]["GT"]
            if None in gt:
                gt = vpq.GT.NON.value
            elif gt == (0, 0):
                gt = vpq.GT.REF.value
            elif gt == (0, 1):
                gt = vpq.GT.HET.value
            elif gt == (1, 1):
                gt = vpq.GT.HOM.value
            else:
                gt = vpq.GT.UNK.value
            gts.append(gt)
            q = entry.samples[sample]["GQ"]
            gqs.append(q if q else 99)
            d = entry.samples[sample]["DP"]
            dps.append(d if d else 0)

        return gts, gqs, dps

    def parse_entry(self, entry):
        """ Parse very minimal information from a vcf to make a pd """
        # If someone made SVTYPE= some number 0-len(SV), this would cause an issue for
        # the last part of below if statement
        svtype = entry.info["SVTYPE"] if "SVTYPE" in entry.info else vpq.SV.NON.value
        svlen = entry.info["SVLEN"] if "SVLEN" in entry.info else 0
        # Convert STR to ENUM
        if svtype == "DEL":
            svtype = vpq.SV.DEL.value
        elif svtype == "INS":
            svtype = vpq.SV.INS.value
        elif svtype == "DUP":
            svtype = vpq.SV.DUP.value
        elif svtype == "INV":
            svtype = vpq.SV.INV.value
        elif svtype not in vpq.SV:
            svtype = vpq.SV.UNK.value
        ret = [entry.chrom, entry.start, entry.stop, entry.qual, ";".join(entry.filter.keys()), svtype, svlen]
        gts, gqs, dps = self.extract_sample(entry)
        ret.extend(gts)
        ret.extend(gqs)
        ret.extend(dps)
        return ret
