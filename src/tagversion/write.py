from __future__ import absolute_import

import re

from StringIO import StringIO

from .git import GitVersion

VERSION_RE = re.compile(r'(?P<start>.*?){{\s*version\s*}}(?P<content>.*)', re.DOTALL)


class WriteFile(object):
    """
    Write version into a file
    """
    def __init__(self, args):
        self.args = args

    def run(self):
        version = GitVersion().version

        buf = StringIO()
        with open(self.args.path, 'r') as fh:
            content = fh.read()
            while content:
                matches = VERSION_RE.match(content)
                if matches:
                    buf.write(matches.group('start'))
                    buf.write(version)

                    content = matches.group('content')
                else:
                    buf.write(content)
                    break

        with open(self.args.path, 'w') as fh:
            fh.write(buf.getvalue())
