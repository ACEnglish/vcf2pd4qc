"""
Simple test pipeline
"""
import sys
import time
import random
import itertools

import vpq

# Functions to call
def f1(data, f1arg=None):
    return ["would be opening " + str(data) + " with " + str(f1arg)]

def f2(data, f2arg=None):
    # lets shuffle the results
    time.sleep(random.randint(0, 1))
    return data + ["And I altered it with " + str(f2arg)]
    
def f3(data):
    # add this to the end
    return data + ['all the way?']
 
def main():
    # build an fchain
    data = range(10)
    pipe = [(f1, {"f1arg": 'a'}),
            (f2, {"f2arg": 'boop'}),
            f3]
    threads = 2 if len(sys.argv) == 1 else int(sys.argv[1])
    for i in vpq.fchain(pipe, data, workers=threads):
        print("collected %r" % (i))

if __name__ == '__main__':
    main()
