#!/usr/bin/env python
"""
Main command for running stats
"""
import sys
import argparse
from collections import OrderedDict

import vpq

USAGE="""\
vpq stats v{0} - Run stats over joblibs
    CMDs:
{1}
""".format(vpq.VERSION,  
           "\n".join("        {0: <15}{1}".format(x,y.__doc__)
                    for x,y in vpq.STATCMDs.items())
          )

def stats_main(args):
    """
    Argument parsing
    """
    parser = argparse.ArgumentParser(prog="vpq stats", description=USAGE,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("cmd", metavar="CMD", choices=vpq.STATCMDs.keys(), type=str,
                        help="Command to execute")
    parser.add_argument("options", metavar="OPTIONS", nargs=argparse.REMAINDER,
                        help="Options to pass to the command")

    if len(args) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args(args)
    m_stat = vpq.STATCMDs[args.cmd].cmd_line(args.options)
    print(m_stat.to_txt())

