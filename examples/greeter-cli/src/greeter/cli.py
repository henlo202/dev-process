import argparse
import sys

from greeter.core import GREETINGS, greeting


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="greet", description="Print a friendly greeting.")
    parser.add_argument("name", help="the name of the person to greet")
    parser.add_argument("--lang", choices=sorted(GREETINGS), default="en",
                        help="language of the greeting (default: en)")
    args = parser.parse_args(argv)
    try:
        print(greeting(args.name, args.lang))
    except ValueError as exc:
        print(f"greet: error: {exc}", file=sys.stderr)
        return 2
    return 0
