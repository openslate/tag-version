from __future__ import absolute_import

import re

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .git import GitVersion

DEFAULT_VERSION_PATTERN = r"(?P<start>.*?){{\s*version\s*}}(?P<content>.*)"


def get_version_re(pattern):
    return re.compile(pattern, re.DOTALL)


class WriteFile(object):
    """
    Write version into a file
    """

    def __init__(self, args):
        self.args = args

    @classmethod
    def setup_subparser(cls, subcommand):
        parser = subcommand.add_parser("write", help=cls.__doc__)

        parser.set_defaults(cls=cls)
        parser.add_argument(
            "--pattern",
            default=DEFAULT_VERSION_PATTERN,
            help='a regex pattern to search and replace with the version, default "{}"'.format(
                DEFAULT_VERSION_PATTERN
            ),
        )
        parser.add_argument(
            "--no-branch",
            action="store_false",
            dest="branch",
            help="do not append branch to the version when current commit is not tagged",
        )
        parser.add_argument("path", help="path to the file to write version in")

    def run(self):
        version = GitVersion(self.args).version
        version_re = get_version_re(self.args.pattern)

        buf = StringIO()
        with open(self.args.path, "r") as fh:
            content = fh.read()
            while content:
                matches = version_re.match(content)
                if matches:
                    buf.write(matches.group("start"))
                    buf.write(version.stringify())

                    content = matches.group("content")
                else:
                    buf.write(content)
                    break

        with open(self.args.path, "w") as fh:
            fh.write(buf.getvalue())
