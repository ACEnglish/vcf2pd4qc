from abc import ABC, abstractmethod

class VCF2PD(ABC):
    """
    Abstract Base Class for VCF2PD parsers
    """
    def __init__(self, vcf):
        self.vcf = vcf
        self.cols, self.samples = None, None
    
    @abstractmethod
    def make_header(self):
        """
        Using self.vcf, create the column headers for the dataframes.
        Given a vcf, parse the header for samples
        returns a tuple
            cols = list of [(column names, dtypes ), ...]
            samples = list of [samplename, ...] to parse
        """
        pass
    
    @abstractmethod
    def parse_entry(self, entry):
        """
        Parse a single vcf entry, and turn it into a list values 
        """
        pass



