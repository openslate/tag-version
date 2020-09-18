from __future__ import absolute_import, print_function

from datetime import datetime
import json
import logging
import os
import re
import sh
import shlex

import sys

from .exceptions import BranchError, VersionError

'''
    Uses a slightly modified version of this regex
    https://regex101.com/r/E0iVVS/2
'''
SEMVER_RE = re.compile('''
                       ^(?P<VersionTripple>
                            (?P<Major>0|[1-9][0-9]*)\.
                            (?P<Minor>0|[1-9][0-9]*)\.
                            (?P<Patch>0|[1-9][0-9]*)
                        ){1}
                        (?P<Tags>(?:\-
                            (?P<Prerelease>
                                (?:(?=[0]{1}[0-9A-Za-z-]{0})(?:[0]{1})|(?=[1-9]{1}[0-9]*[A-Za-z]{0})(?:[0-9]+)|(?=[0-9]*[A-Za-z-]+[0-9A-Za-z-]*)(?:[0-9A-Za-z-]+)){1}(?:\.(?=[0]{1}[0-9A-Za-z-]{0})(?:[0]{1})|\.(?=[1-9]{1}[0-9]*[A-Za-z]{0})(?:[0-9]+)|\.(?=[0-9]*[A-Za-z-]+[0-9A-Za-z-]*)(?:[0-9A-Za-z-]+))*){1}
                            ){0,1}(?:\+
                            (?P<Build>
                                (?:[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*
                            ))
                        ){0,1})$
                       ''', re.VERBOSE)

RC_RE = re.compile(r'(?P<full_version>(?P<stable>.*)rc(?P<rc_number>\d+)).*')

INITIAL_VERSION = '0.0.0'

MAJOR = 0
MINOR = 1
PATCH = 2


def print_error(buf):
    print(buf, file=sys.stderr)


def is_calver(calver_version, calver_format):
    # ex: 201809.25 from 201809.25.1-rc
    d = '.'.join(calver_version.split('.', 2)[:2])
    try:
        datetime.strptime(d, calver_format)
    except AttributeError:
        return False
    except ValueError:
        return False
    else:
        return True


def is_semver(semver_version):
    return SEMVER_RE.match(semver_version) is not None


def is_rc(version):
    return (RC_RE.match(version) is not None) if version else False


class GitVersion(object):
    """
    Get and set git version tag
    """
    def __init__(self, args=None):
        self.args = args

    @property
    def logger(self):
        return logging.getLogger('{}.{}'.format(
            __name__,
            self.__class__.__name__))

    @property
    def branch(self):
        branch = os.environ.get('GIT_BRANCH')
        if branch is None:
            command = sh.git(*shlex.split('rev-parse --abbrev-ref HEAD'))
            lines = command.stdout.decode('utf8').strip().splitlines()
            branch = lines[0].strip()

            color_marker_idx = branch.find('\x1b')
            if color_marker_idx >= 0:
                self.logger.warning('found color marker in branch={}'.format(
                    branch.encode("utf8")))
                branch = branch[:color_marker_idx]

        # clean string to remove unwanted characters
        branch = branch.replace('/', '--')

        return branch

    @property
    def is_clean(self):
        """
        Returns whether the working copy is clean

        When there are uncommited changes in the working copy return False

        Returns:
            Boolean whether the working copy is clean
        """
        result = False

        command_l = 'git status --untracked --short'.split()
        command = getattr(sh, command_l[0])(command_l[1:])

        lines = command.stdout.decode('utf8').splitlines()
        for line in lines:
            line = line.rstrip()
            print_error('{}'.format(line))

        if not lines:
            result = True

        return result

    @property
    def is_calver(self):
        return(is_calver(self.version, self.args.calver_format))

    @property
    def is_semver(self):
        return(is_semver(self.version))

    @property
    def is_rc(self):
        return(is_rc(self.version))

    @property
    def version(self):
        try:
            command = sh.git(*shlex.split('describe --tags --always'))
        except sh.ErrorReturnCode_128:  # pylint: disable=E1101
            return None
        else:
            version = command.stdout.decode('utf8').strip()

            # if the branch flag was given,
            # check to see if we are on a tagged commit
            if self.args.branch:
                try:
                    command = sh.git(*shlex.split('describe --tags --exact-match'))
                except sh.ErrorReturnCode_128:  # pylint: disable=E1101
                    # not an exact match, so append the branch
                    version = '{}-{}'.format(version, self.branch)

            return version

    @classmethod
    def setup_subparser(cls, subcommand):
        parser = subcommand.add_parser('version', help=cls.__doc__)

        parser.set_defaults(cls=cls)
        parser.add_argument(
            '--bump', action='store_true',
            help='perform a version bump, by default the current version is displayed'
        )
        parser.add_argument(
            '-f', '--force', action='store_true',
            help='perform the operation even if the working copy is dirty'
        )
        parser.add_argument(
            '--patch', action='store_true', default=True,
            help='bump the patch version, this is the default bump if one is not specified'
        )
        parser.add_argument(
            '--minor', action='store_true',
            help='bump the minor version and reset patch back to 0'
        )
        parser.add_argument(
            '--major', action='store_true',
            help='bump the major version and reset minor and patch back to 0'
        )
        parser.add_argument(
            '--set',
            help='set version to the given version'
        )
        parser.add_argument(
            '--semver', action='store_true',
            help='only print out if the current tag is a semantic version, or exit 1'
        )
        parser.add_argument(
            '--calver', action='store_true',
            help='only print out if the current tag is a calendar version, or exit 1'
        )
        parser.add_argument(
            '--calver-format', action='store_true', default='%Y%m.%d',
            help='set the calver format (ex: \'%%Y%%m.%%d\')'
        )
        parser.add_argument(
            '--rc', action='store_true',
            help='when bumping, generate a release candidate tag instead of a proper version'
        )
        parser.add_argument(
            '-m', '--message',
            help='set the git tag message on the command line'
        )
        parser.add_argument(
            '--no-branch', action='store_false', dest='branch',
            help='do not append branch to the version when current commit is not tagged'
        )

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

    def get_split_version(self, version):
        """Split the provided version and int'ify major, minor, and patch"""
        split_version = version.split('-', 1)[0].split('.', 3)
        for i in range(3):
            split_version[i] = int(split_version[i])

        return split_version

    def get_next_calver_version(self, version):
        # split the current date
        now = datetime.now().strftime(self.args.calver_format)
        split_calver = now.split('.', 2)
        for i in range(2):
            split_calver[i] = int(split_calver[i])

        # don't allow major/minor
        if self.args.major:
            raise VersionError('''
                You can not bump to a major calver release.
                If you want to override this use `--set --force` instead
                ''')
        elif self.args.minor:
            raise VersionError('''
                You can not bump to a minor calver release.
                If you want to override this use `--set --force` instead
                ''')
        elif self.args.patch:
            # if there are existing tags from today, bump the patch on the last one
            # otherwise move to the new date
            todays_tags = sh.git(*shlex.split(f'tag --list {now}*'))

            if todays_tags:
                last_tag = sorted(todays_tags.split('\n'))[-1]
                last_tag_split = self.get_split_version(last_tag)

                if not is_rc(last_tag):
                    last_tag_split[PATCH] += 1

                split_calver.append(last_tag_split[PATCH])
            else:
                split_calver.append(0)

        return split_calver[:3]

    @staticmethod
    def get_next_rc_version(version):
        matches = RC_RE.match(version)

        current_rc = int(matches.group('rc_number'))
        next_rc = current_rc + 1

        # use the full_version match in order to remove any git version suffix
        full_version = matches.group('full_version')
        next_version = full_version.replace('rc{}'.format(current_rc), 'rc{}'.format(next_rc))

        return next_version.split('.')

    def bump(self):
        current_version = self.version
        current_is_rc = self.is_rc

        if current_version is None:
            print_error('No commits found - please commit something before bumping')
            return None

        if self.args.rc and current_is_rc:
            self.logger.info('Latest version is a release candidate, incrementing...')
            next_version = self.get_next_rc_version(current_version)
        elif self.args.calver:
            next_version = self.get_next_calver_version(current_version)
        else:
            # when this commit is an RC, don't bump any version number, just strip off the RC suffix
            if current_is_rc:
                matches = RC_RE.match(current_version)
                next_version = [int(x) for x in matches.group('stable').split('.')]
            else:
                split_dashes = current_version.split('-')

                if len(split_dashes) == 1:
                    raise VersionError(
                        'Is version={} already bumped?'.format(current_version))
                if len(split_dashes) == 2:
                    self.logger.info('No tags found, bumping initial version')
                    current_version = INITIAL_VERSION
                else:
                    current_version = split_dashes[0]

                next_version = self.get_next_version(current_version)

        if self.args.rc and not current_is_rc:
            self.logger.info('Latest version is not a release candidate, generating initial rc tag...')
            next_version[-1] = str(next_version[-1]) + 'rc1'

        return next_version

    def check_bump(self):
        """
        Check to see if a bump request is being made
        """
        if not self.args.bump:
            return False

        return self.bump()

    def check_set(self):
        """
        Check to see if the version is being set
        """
        if not self.args.set:
            return None

        # if there's a calver flag, can only set to a correct calver version
        if self.args.calver:
            if not is_calver(self.args.set, self.args.calver_format):
                raise VersionError(
                    'Trying to set a non-calver version: {}'.format(self.args.set))

        return self.args.set.split('.')

    def get_tag_command(self, new_version):
        tag_command = 'git tag -a '

        if self.args.message:
            tag_command += '-m {} '.format(json.dumps(self.args.message))

        tag_command += new_version
        return tag_command

    def run(self):
        if not self.is_clean and not self.args.force:
            print_error('Abort: working copy not clean.')

            return 1

        current_version = self.version

        # check to see if an explicit version is being set
        new_version = self.check_set()
        if not new_version:
            # otherwise, see if the version is being bumped
            try:
                new_version = self.check_bump()
            except VersionError as exc:
                print_error(exc)

                return 1

        status = 0

        if new_version is False:
            if current_version:
                print(self.version)
            else:
                next_version = self.get_next_version(INITIAL_VERSION)
                print_error('No version found, use --bump to set to {}'.format(
                    self.stringify(next_version)
                ))

                status = 1
        elif new_version is None:
            return 1
        else:
            version_str = self.stringify(new_version)
            tag_command = self.get_tag_command(version_str)
            os.system(tag_command)

            print(version_str)

        if self.args.rc:
            if not self.is_rc:
                return 1

        if self.args.semver:
            if not self.is_semver:
                return 1

        if self.args.calver:
            if not self.is_calver:
                return 1

        return status

    def stringify(self, version):
        return '.'.join([str(x) for x in version])
