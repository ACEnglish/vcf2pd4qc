import sys
import types
import logging

import concurrent.futures as cfuts
from functools import partial, reduce

def __reduce_wrapper(funcs, data, **kwargs):
    """
    This is a wrapper around reduce, which chains the functions
    We assume there must always be at least one argument
    """
    return reduce(lambda r, f: f(r, **kwargs), funcs, data)

def __partial_wrapper(funcs):
    """
    Wrap the reduce_wrapper in a partial so it may run multiple times
    (i.e. over multiple pieces of data)
    """
    return partial(__reduce_wrapper, funcs)

def pipeline(pipe, data, workers=1):
    """
    Runs chained functions over every piece of data.
    Yields results of chained functions called per data.

    pipe: list of [(function, kwargs), ...]
        - each function must be defined with at least `def foobar(data)`.
        - kwargs is a dictionary of other parameters the function may need. 
        - kwargs may be an empty dict if no parameters are needed (i.e. {})
    data: list data to process
        - data must be hashable
    workers: maximum number of ThreadPoolExecutor workers to create

    For example, the first yield of a 2 step pipe on the first piece of data is 
    equivalent to:
        pipe[1][0](
            pipe[0][0](data[0], **pipe[0][1]),
            **pipe[1][1]
        )
    """
    m_reduce = __partial_wrapper([partial(_[0], **_[1]) if isinstance(_, tuple) else _ for _ in pipe])
    with cfuts.ThreadPoolExecutor(max_workers=workers) as executor:
        # Start the load operations and mark each future with its arg
        future_results = {executor.submit(m_reduce, _): _ for _ in data}
        for future in cfuts.as_completed(future_results):
            my_name = future_results[future]
            try:
                cur_result = future.result()
            except Exception as exc:
                logging.critical('%r generated an exception: %s' % (my_name, exc))
                # how do we stop safely... just return, or raise the exception?
                continue
            yield cur_result

def test():
    """
    Simple test pipeline
    """
    import time
    import random
    import itertools

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
    
    def consolidate_resize(data):
        # put them all together
        ret = []
        for i in data:
            ret.extend(i)
        ret2  = []
        cur = []
        for i in ret:
            cur.append(i)
            if len(cur) == 3:
                ret2.append(cur)
                cur = []
        if cur:
            ret2.append(cur)
        return ret2
    
    data = range(10)
    pipe = [(f1, {"f1arg": 'a'}),
            (f2, {"f2arg": 'boop'}),
            f3,
            ]
    
    for i in pipeline(pipe, data, workers=int(sys.argv[1])):
        print("collected %r" % (i))

def test2():
    def gen(data):
        for i in range(10):
            yield i
    pipe = [gen, print]
    for i in pipeline(pipe, [0]): print(i)

if __name__ == '__main__':
    test()


