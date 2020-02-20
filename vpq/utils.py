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
 
