"""
Parser for muCNV output
"""
import numpy

import vpq
from vpq.parsers.VCF2PD import VCF2PD


class muCNV2PD(VCF2PD):
    """ Parser for muCNT output """

    def __init__(self, vcf):
        super().__init__(vcf)
        self.cols, self.samples = self.make_header()

    def extract_sample(self, entry):
        """ Extract the GT and normalized depth for all the samples """
        gts = []
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
            dps.append(entry.samples[sample]["DP"])

        return gts, dps

    def make_header(self):
        """
        Given a vcf, make the dataframe header information
        returns columns [(name, type), ..], [samples, ...]
        """
        cols = [("chrom", str),
                ("start", int),
                ("end", int),
                ("svtype", numpy.uint8),
                ("svlen", int),
                ("ac", numpy.uint16),
                ("ns", numpy.uint16),
                ("af", numpy.float32),
                ("callrate", numpy.float16),
                ("okg_af", numpy.float32),
                ("dbvar", bool),
                ("lrepeat", str),
                ("rrepeat", str),
                ("imh_af", numpy.float32),
                ("gd_af", numpy.float32),
                ("dgv_lossfreq", numpy.float32),
                ("dgv_gainfreq", numpy.float32),
                ("hits_gene", bool)
                ]
        # Collecting sample header
        samples = [x for x in self.vcf.header.samples]
        cols.extend([(x + "_gt", numpy.uint8) for x in samples])
        cols.extend([(x + "_dp", numpy.float16) for x in samples])
        return cols, samples

    def parse_entry(self, entry):
        """
        Pull in all of the relevant information for an event
        """
        svtype = entry.info["SVTYPE"]
        # Convert STR to ENUM
        if svtype == "DEL":
            svtype = vpq.SV.DEL.value
        elif svtype == "INS":
            svtype = vpq.SV.INS.value
        elif svtype == "DUP":
            svtype = vpq.SV.DUP.value
        elif svtype == "INV":
            svtype = vpq.SV.INV.value
        else:
            print("UNK SVTYPE!! %s" % (str(entry)))

        cur = [entry.chrom,
               entry.start,
               entry.stop,
               svtype,
               entry.info["SVLEN"],
               entry.info["AC"],
               entry.info["NS"],
               entry.info["AF"][0],
               entry.info["CALLRATE"],
               entry.info["1000g_AF"] if "1000g_AF" in entry.info else -1,
               "dbVar_event" in entry.info,
               ",".join(entry.info["Repeats_type_left"]) if "Repeats_type_left" in entry.info else "",
               ",".join(entry.info["Repeats_type_right"]) if "Repeats_type_right" in entry.info else "",
               entry.info["IMH_AF"] if "IMH_AF" in entry.info else -1,
               entry.info["GD_AF"] if "GD_AF" in entry.info else -1,
               entry.info["DGV_LOSS_Frequency"] if "DGV_LOSS_Frequency" in entry.info else -1,
               entry.info["DGV_GAIN_Frequency"] if "DGV_GAIN_Frequency" in entry.info else -1,
               "Gene_name" in entry.info
               ]
        gts, dps = self.extract_sample(entry)
        cur.extend(gts)
        cur.extend(dps)
        return cur
