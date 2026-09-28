import argparse

import veriproof


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="veriproof",
        description="Tamper-evident forensic verification for everyday evidence media")
    parser.add_argument("--version", action="version", version=veriproof.__version__)
    sub = parser.add_subparsers(dest="cmd")
    v = sub.add_parser("verify", help="verify a media file (coming in M4)")
    v.add_argument("file")
    args = parser.parse_args(argv)
    if args.cmd == "verify":
        parser.exit(1, "verify: not implemented until M4\n")
    parser.print_help()
    return 0
