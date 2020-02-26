"""
Holds a lookup of all the known parsers
"""
from collections import OrderedDict

from vpq.parsers import (
    mucnv,
    skeleton,
    generic
)


VPQParsers = OrderedDict()
VPQParsers["skeleton"] = skeleton.skeleton
VPQParsers["muCNV"] =  mucnv.muCNV2PD
VPQParsers["generic"] =  generic.generic
