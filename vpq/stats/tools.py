from collections import Counter, OrderedDict

"""
Collection of methods that edit/extend vpq joblibs
"""
import vpq

def add_sizebin_column(data):
    """
    Add size bin column
    """
    data["table"]["szbin"] = data["table"]["svlen"].apply(vpq.size_bin)
    return data

def split_by_type(data):
    """
    subset the data by types
    """
    data["table_by_type"] = {i:data["table"].loc[data["table"]["svtype"] == i.value] 
                            for i in vpq.SV}
    return data

def type_counter(data):
    """
    Single data frame type counting
    """
    data["type_count"] = Counter(data["table"]["svtype"])
    return data

def sizebin_type_counter(data):
    """
    Create sizebin_type_count item
    """
    data["sizebin_type_count"] = {}
    for subtype, tab in data["table_by_type"].items():
        data["sizebin_type_count"][subtype] = Counter(tab["szbin"])
    return data

def sample_gt_count(data):
    """
    Per GT, count the number of alleles per sample genotyped as such
    """
    data["sample_gt_count"] = {}
    for i in data["samples"]:
        data["sample_gt_count"][i] = Counter(data["table"][i + "_gt"])
    return data
 
