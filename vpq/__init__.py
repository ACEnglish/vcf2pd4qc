"""
VPQ - Library for parsing VCFs to Pandas Dataframes for Quality Control
"""
from vpq.version import VERSION

from vpq.parsers import (
    VPQParsers
)

from vpq.pipeline import fchain

from vpq.stats import (
    STATCMDs,

    jl_load,

    GT,
    SV,

    SZBINS,
    SZBINMAX,
    SZBINTYPE,
    add_sizebin_column,

    QUALBINS,
    add_qualbin_column,

    add_cnt_column,
    groupcnt,

    split_by_type,
    sizebin_type_counter,
    sample_gt_count,
    qualbin_count,
)

__all__ = [
    'VERSION',
    'fchain',
    'VPQParsers',
    'jl_load',
    'GT',
    'SV',
    'SZBINS',
    'SZBINMAX',
    'SZBINTYPE',
    'add_sizebin_column',
    'QUALBINS',
    'add_qualbin_column',
    'add_cnt_column',
    'groupcnt',

    'STATCMDs',
    # will be removed
    'split_by_type',
    'sizebin_type_counter',
]
