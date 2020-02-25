import numpy

import vpq.utils as vtils
from vpq.parsers.VCF2PD import VCF2PD


class muCNV2PD(VCF2PD):
    
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
                gt = vtils.GT.NON.value
            elif gt == (0, 0):
                gt = vtils.GT.REF.value
            elif gt == (0, 1):
                gt = vtils.GT.HET.value
            elif gt == (1, 1):
                gt = vtils.GT.HOM.value
            else:
                gt = vtils.GT.UNK.value
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
                ("mustart", int),
                ("muend", int),
                ("mulen", int)]
        # Collecting sample header
        samples = [x for x in self.vcf.header.samples]
        cols.extend([(x + "_gt", numpy.uint8) for x in samples])
        cols.extend([(x + "_dp", numpy.float16) for x in samples])
        return cols, samples

    def parse_entry(self, entry):
        """
        Pull in all of the relevant information for an event
        """
        muBP_start, muBP_end = muBP(entry)
        svtype = entry.info["SVTYPE"]
        # Convert STR to ENUM
        if svtype == "DEL":
            svtype = vutil.SV.DEL.value
        elif svtype == "INS":
            svtype = vutil.SV.INS.value
        elif svtype == "DUP":
            svtype = vutil.SV.DUP.value
        elif svtype == "INV":
            svtype = vutil.SV.INV.value
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
               muBP_start, muBP_end, abs(muBP_end - muBP_start)]
        gts, dps = extract_sample(entry)
        cur.extend(gts)
        cur.extend(dps)
        return cur
