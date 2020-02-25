from collections import OrderedDict

from vpq.parsers import (
    mucnv,
    skeleton,
    generic
)

from vpq.parsers.VCF2PD import VCF2PD

VPQParsers = OrderedDict()
VPQParsers["skeleton"] = skeleton.skeleton
VPQParsers["muCNV"] =  mucnv.muCNV2PD
VPQParsers["generic"] =  generic.generic

__all__ = [
    'VPQParsers',
    'VCF2PD'
]
