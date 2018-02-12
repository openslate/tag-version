"""
tagversion Entrypoints
"""
import logging
import sys

from tagversion.argparse import ArgumentParser
from tagversion.git import GitVersion
from tagversion.write import WriteFile


def main():
    logging.basicConfig(level=logging.WARNING)

    parser = ArgumentParser()
    subcommand = parser.add_subparsers(dest='subcommand')

    GitVersion.setup_subparser(subcommand)
    WriteFile.setup_subparser(subcommand)

    args = parser.parse_args(default_subparser='version')

    command = args.cls(args)
    sys.exit(command.run())
