"""
Main command for running stats
"""
from collections import OrderedDict

import vpq

TOOLCMDs = OrderedDict()
TOOLCMDs["typecnt"] = vpq.stats.TypeCounter
TOOLCMDs["size_type_cnt"] = vpq.stats.SizebinTypeCounter
TOOLCMDs["sample_gt_cnt"] = vpq.stats.SampleGTCount

USAGE="""\
vpq stats v{0} - Run stats over joblibs
    CMDs:
        typecnt       {1}
        size_type_cnt {2}
        sample_gt_cnt {3}
""".format(vpq.VERSION, *[i.__doc__ for i in TOOLCMDs.values()])

def stats_main(args):
    """
    Argument parsing
    """
    parser = argparse.ArgumentParser(prog="vpq stats", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("cmd", metavar="CMD", choices=TOOLCMDs.keys(), type=str,
                        help="Command to execute")
    parser.add_argument("options", metavar="OPTIONS", nargs=argparse.REMAINDER,
                        help="Options to pass to the command")

    if len(args) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args(args)
    TOOLS[args.cmd](args.options)

