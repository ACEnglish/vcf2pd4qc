#!/usr/bin/env python
"""
Main entry point for the sub commands
"""
import sys
import argparse

import vpq
from vpq.vcf2pd import vcf2pd_main
from vpq.stats_main import stats_main

VERSION="0.0.1-dev"

USAGE = """\
vcf2pd4qc v%s - Library that assists the analysis of VCF files
    CMDs:
        vcf2pd           Convert vcf to joblib
        stats            Run stats over joblibs
        version          Print the version and exit
""" % vpq.VERSION

def version(args):
    """Print the version"""
    print("vcf2pd5qc v%s" % VERSION)

TOOLS =  {"vcf2pd": vcf2pd_main,
          "stats": stats_main,
          "version": version}

def parseArgs():
    """
    Argument parsing
    """
    parser = argparse.ArgumentParser(prog="vpq", description=USAGE,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("cmd", metavar="CMD", choices=TOOLS.keys(), type=str,
                        help="Command to execute")
    parser.add_argument("options", metavar="OPTIONS", nargs=argparse.REMAINDER,
                        help="Options to pass to the command")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    
    TOOLS[args.cmd](args.options)

if __name__ == '__main__':
    parseArgs()
