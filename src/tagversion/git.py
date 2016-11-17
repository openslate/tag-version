from __future__ import absolute_import, print_function

import sh
import shlex

import sys

from .exceptions import VersionError

INITIAL_VERSION = '0.0.0'

MAJOR = 0
MINOR = 1
PATCH = 2


class GitVersion(object):
    """
    Get and set git version tag
    """
    def __init__(self, args=None):
        self.args = args

    @property
    def version(self):
        try:
            command = sh.git(*shlex.split('describe --tags'))
        except sh.ErrorReturnCode_128:
            return None
        else:
            return command.stdout.decode('utf8').strip()

    def get_next_version(self, version):
        # split the version and int'ify major, minor, and patch
        split_version = version.split('-', 1)[0].split('.', 3)
        for i in range(3):
            split_version[i] = int(split_version[i])

        if self.args.major:
            split_version[MAJOR] += 1

            split_version[MINOR] = 0
            split_version[PATCH] = 0
        elif self.args.minor:
            split_version[MINOR] += 1

            split_version[PATCH] = 0
        elif self.args.patch:
            split_version[PATCH] += 1

        return split_version[:3]

    def bump(self):
        version = self.version
        if version:
            split_dashes = version.split('-')
            if len(split_dashes) == 1:
                raise VersionError('Is version={} already bumped?'.format(version))

            current_version = split_dashes[0]
        else:
            current_version = INITIAL_VERSION

        version = self.get_next_version(current_version)

        return version

    def check_bump(self):
        """
        Check to see if a bump request is being made
        """
        if not self.args.bump:
            return False

        return self.bump()

    def run(self):
        current_version = self.version

        try:
            bumped = self.check_bump()
        except VersionError as exc:
            print(exc)

            return 1

        status = 0

        if bumped is False:
            if current_version:
                print(self.version)
            else:
                next_version = self.get_next_version(INITIAL_VERSION)
                print(
                    'No version found, use --bump to set to {}'.format(self.stringify(next_version)), file=sys.stderr
                )

                status = 1
        else:
            version_str = self.stringify(bumped)
            sh.git('tag', version_str)

            print(version_str)

        return status

    def stringify(self, version):
        return '.'.join([str(x) for x in version])
