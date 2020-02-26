
import sys
import joblib

# PER sample GT frequencies 
sys.stdout.write("samp")
for i in GT:
    sys.stdout.write("\t" + i.name)
sys.stdout.write("\n")
for i in samps:
    sys.stdout.write(i)
    mcnt = Counter(data[i + "_gt"])
    for k in GT:
        sys.stdout.write("\t%d" % (mcnt[k.value]))
    sys.stdout.write("\n")
