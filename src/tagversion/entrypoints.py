"""
tagversion Entrypoints
"""
import sys

from tagversion.argparse import ArgumentParser
from tagversion.git import GitVersion
from tagversion.write import WriteFile


def main():
    parser = ArgumentParser()
    subcommand = parser.add_subparsers(dest='subcommand')

    GitVersion.setup_subparser(subcommand)
    WriteFile.setup_subparser(subcommand)

    args = parser.parse_args(default_subparser='bump')

    command = args.cls(args)
    sys.exit(command.run())
