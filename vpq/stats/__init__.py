import sys
import argparse
from collections import OrderedDict

from vpq.stats import (
    type_counter,
    size_type_counter
)

VERSION="0.0.1-dev"

TOOLS = OrderedDict()
TOOLS["type_counter"] = type_counter.main
TOOLS["size_type_counter"] = size_type_counter.main

USAGE = """\
vpq stats v{0} - Run stats over joblibs
    CMDs:
        type_counter      {1}
        size_type_counter {2}
""".format(VERSION, *[i.__doc__ for i in TOOLS.values()])

def stats_main(args):
    """
    Argument parsing
    """
    parser = argparse.ArgumentParser(prog="vpq stats", description=USAGE,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("cmd", metavar="CMD", choices=TOOLS.keys(), type=str,
                        help="Command to execute")
    parser.add_argument("options", metavar="OPTIONS", nargs=argparse.REMAINDER,
                        help="Options to pass to the command")

    if len(args) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args(args)
    TOOLS[args.cmd](args.options)

