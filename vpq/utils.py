from enum import Enum

class GT(Enum):
    NON=3
    REF=0
    HET=1
    HOM=2
    UNK=4

class SV(Enum):
    DEL=0
    INS=1
    DUP=2
    INV=3
    NON=4 # Not and SV, SVTYPE
    UNK=5 # Unknown SVTYPE
 
SZBINS = ["(0,50]", "(50,100]", "(100,200]", "(200,300]", "(300,400]", 
          "(400,600]", "(600,800]", "(800,1k]", "(1k,2.5k]", 
          "(2.5k,5k]", ">5k"]

def size_bin(sz):
    """
    Bin a given size
    """
    sz = abs(sz)
    if sz <= 50:
        return "(0,50]"
    elif sz <= 100:
        return "(50,100]"
    elif sz <= 200:
        return "(100,200]"
    elif sz <= 300:
        return "(200,300]"
    elif sz <= 400:
        return "(300,400]"
    elif sz <= 600:
        return "(400,600]"
    elif sz <= 800:
        return "(600,800]"
    elif sz <= 1000:
        return "(800,1k]"
    elif sz <= 2500:
        return "(1k,2.5k]"
    elif sz < 5000:
        return"(2.5k,5k]"
    else:
        return ">5k"


