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

    # version parser for managing versions
    version_parser = subcommand.add_parser('bump', help=GitVersion.__doc__)
    version_parser.set_defaults(cls=GitVersion)
    version_parser.add_argument(
        '--bump', action='store_true',
        help='perform a version bump, by default the current version is displayed'
    )
    version_parser.add_argument(
        '--patch', action='store_true', default=True,
        help='bump the patch version, this is the default bump if one is not specified'
    )
    version_parser.add_argument(
        '--minor', action='store_true',
        help='bump the minor version and reset patch back to 0'
    )
    version_parser.add_argument(
        '--major', action='store_true',
        help='bump the major version and reset minor and patch back to 0'
    )

    write_parser = subcommand.add_parser('write', help=WriteFile.__doc__)
    write_parser.set_defaults(cls=WriteFile)
    write_parser.add_argument(
        'path', help='path to the file to write version in'
    )

    parser.set_default_subparser('bump')
    args = parser.parse_args()

    command = args.cls(args)
    sys.exit(command.run())
