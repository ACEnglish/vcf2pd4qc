from vpq.parsers.VCF2PD import VCF2PD

class skeleton(VCF2PD):
    """ Parse very minimal information from a vcf to make a pd """
    
    def __init__(self, vcf):
        super().__init__(vcf)
        self.cols, self.samples = self.make_header()
        
    def make_header(self):
        """ Parse very minimal information from a vcf to make a pd """
        cols = [("chrom", str),
                ("start", int),
                ("end", int)]
        samples = []
        return cols, samples
        
    def parse_entry(self, entry):
        """ Parse very minimal information from a vcf to make a pd """
        return [entry.chrom, entry.start, entry.stop]    
    
