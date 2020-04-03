"""
Collection of methods that edit/extend/organize vpq joblibs
"""
import os
import sys
from enum import Enum
from collections import Counter

import joblib
from pandas.api.types import CategoricalDtype

import vpq


SZBINS = ["[0,50)", "[50,100)", "[100,200)", "[200,300)", "[300,400)",
          "[400,600)", "[600,800)", "[800,1k)", "[1k,2.5k)",
          "[2.5k,5k)", ">=5k"]
SZBINMAX = [50, 100, 200, 300, 400, 600, 800, 1000, 2500, 5000, sys.maxsize]
SZBINTYPE = CategoricalDtype(categories=SZBINS, ordered=True)

QUALBINS = [f"[{x},{x+10})" for x in range(0, 100, 10)] + [">=100"]
QUALBINTYPE = CategoricalDtype(categories=QUALBINS, ordered=True)

HG19TYPE = CategoricalDtype(categories=[str(x) for x in range(1, 23)] + ["X", "Y"], ordered=True)
GRCH38TYPE = CategoricalDtype(categories=["chr" + str(x) for x in range(1, 23)] + ["chrX", "chrY"], ordered=True)


class GT(Enum):
    """ Genotypes """
    NON = 3
    REF = 0
    HET = 1
    HOM = 2
    UNK = 4


class SV(Enum):
    """ SVtypes """
    DEL = 0
    INS = 1
    DUP = 2
    INV = 3
    NON = 4  # Not and SV, SVTYPE
    UNK = 5  # Unknown SVTYPE


def jl_load(data):
    """
    returns either a freshly opend filename
    or an already opened vpd joblib
    """
    if isinstance(data, str) and os.path.exists(data):
        ret = joblib.load(data)
        if ret["table"].shape[0] == 0:
            raise Exception("joblib %s is empty. skipping" % (data))
        return ret
    if isinstance(data, dict) and "samples" in data and "table" in data:
        return data
    raise TypeError("jl_load doesn't recognize input %s" % str(data))


def get_sizebin(sz):
    """
    Bin a given size
    """
    sz = abs(sz)
    for key, maxval in zip(SZBINS, SZBINMAX):
        if sz <= maxval:
            return key
    return None


def add_sizebin_column(data):
    """
    Add size bin column
    """
    data["table"]["szbin"] = data["table"]["svlen"].apply(get_sizebin).astype(SZBINTYPE)
    return data


def categorize_sv(data):
    """
    Make SV fields categorical
    """
    svtype = CategoricalDtype(categories=range(len(vpq.SV)), ordered=True)
    data["table"]['svtype'] = data["table"]["svtype"].astype(svtype)
    return data


def categorize_gt(data):
    """
    Make GT fields categorical
    """
    gttype = CategoricalDtype(categories=range(len(vpq.GT)), ordered=True)
    for samp in data["table"]["gttype"]:
        data["table"][samp + "_gt"] = data["table"][samp + "_gt"].astype(gttype)
    return data


def add_qualbin_column(data):
    """
    Add qualbin column to table
    """
    def qualbin(qual):
        """
        Bin a given qual
        """
        for idx, i in enumerate(range(0, 100, 10)):
            if qual < i + 10:
                return QUALBINS[idx]
        return QUALBINS[-1]

    data["table"]["qualbin"] = data["table"]["qual"].apply(qualbin).astype(QUALBINTYPE)
    return data


def add_cnt_column(data):
    """
    Add a cnt column for group counting
    """
    data["table"]["cnt"] = 1
    return data


def groupcnt(data, key, group):
    """
    Create a new dataframe in data with key equal to the groupby.count result
    """
    data[key] = data["table"].groupby(group).count()["cnt"]
    return data


def sample_gt_count(data):
    """
    Per GT, count the number of alleles per sample genotyped as such
    """
    data["sample_gt_count"] = {}
    for i in data["samples"]:
        data["sample_gt_count"][i] = Counter(data["table"][i + "_gt"])
    return data
