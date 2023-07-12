from unittest import TestCase, mock

from tagversion.git import GitVersion, is_rc
from tagversion.version import Version

RC_VERSION = "0.1.28rc1-1-g4fafe09-feature--skip-prefix-rows"


@mock.patch("tagversion.git.sh")
@mock.patch("tagversion.git.GitVersion.get_git_tag_version")
class GitTestCase(TestCase):
    def _get_args(self, **kwargs):
        args = mock.Mock(
            calver=False,
            major=False,
            minor=False,
            patch=False,
            prefix=None,
            prefix_separator=None,
            rc=False,
            display_prefix=True,
            format="default",
        )

        for k, v in kwargs.items():
            setattr(args, k, v)

        return args

    def _setup_version(self, *mocks, version=RC_VERSION):
        version_mock = mocks[-2]
        version_mock.return_value = version

        return version_mock

    def _setup_git_describe(self, *mocks, version: str) -> None:
        sh_mock = mocks[-1]
        sh_mock.git.return_value.stdout = version.encode("utf8")

    def test_bump_no_tag(self, *mocks):
        """
        Ensures bumping when there is no tag produces 0.0.1
        """
        version_mock = self._setup_version(*mocks, version="000000-master")

        args = self._get_args(patch=True)

        git_version = GitVersion(args)

        new_version = git_version.bump()

        self.assertEqual("0.0.1", str(new_version))

    def test_bump_rc(self, *mocks):
        """
        Ensures running bump results in a stable, non-rc, release
        """
        version_mock = self._setup_version(
            *mocks, version="0.1.28rc1-1-g4fafe09-feature--skip-prefix-rows"
        )

        args = self._get_args()

        git_version = GitVersion(args)

        self.assertEqual(version_mock.return_value, git_version.version)

        new_version = git_version.bump()

        self.assertEqual("0.1.28", str(new_version))

    def test_bump_rc_to_stable(self, *mocks):
        """
        Ensures running bump results in a stable, non-rc, release
        """
        version_mock = self._setup_version(*mocks, version="0.1.28rc2")

        args = self._get_args()

        git_version = GitVersion(args)

        self.assertEqual(version_mock.return_value, git_version.version)

        new_version = git_version.bump()

        self.assertEqual("0.1.28", str(new_version))

    def test_bump_rev_rc(self, *mocks):
        """
        Ensures running bump --rc on an RC results in a proper rc tag
        """
        version_mock = self._setup_version(*mocks)

        args = self._get_args(rc=True)

        git_version = GitVersion(args)

        self.assertEqual(version_mock.return_value, git_version.version)

        new_version = git_version.bump()

        self.assertEqual("0.1.28rc2", new_version)

    def test_get_next_rc_version(self, *mocks):
        """
        Ensures git version stuff is removed from next version
        """
        next_version = GitVersion.get_next_rc_version(RC_VERSION)

        self.assertEqual(["0", "1", "28rc2"], next_version)

    def test_is_rc(self, *mocks):
        """
        Ensures RC is properly detected
        """
        self.assertEqual(True, is_rc(RC_VERSION))

    def test_bump_project_prefix(self, *mocks):
        """
        When bumping a tag with a prefix, include the prefix
        """
        version_mock = self._setup_version(
            *mocks, version="TestModule/0.0.1-16-g5befeb2"
        )

        args = self._get_args(patch=True)

        git_version = GitVersion(args)
        new_version = git_version.bump()
        new_version_s = git_version.stringify(new_version)

        self.assertEqual("TestModule/0.0.2", new_version_s)

    def test_bump_project_set_prefix(self, *mocks):
        """
        when bumping a tag and a prefix is specified, use the specified prefix
        """
        version_mock = self._setup_version(
            *mocks, version="TestModule/0.0.1-16-g5befeb2"
        )

        args = self._get_args(patch=True, prefix="NewPrefix")

        git_version = GitVersion(args)
        new_version = git_version.bump()

        new_version_s = git_version.stringify(new_version)

        self.assertEqual("NewPrefix/0.0.2", new_version_s)

    def test_set(self, *mocks):
        """Ensure checking for a version being set parses the version"""
        args = self._get_args(set="1.2.3")
        git_version = GitVersion(args)

        new_version = git_version.check_set()

        self.assertEqual("1", new_version.major)
        self.assertEqual("2", new_version.minor)
        self.assertEqual("3", new_version.patch)

    def test_stringify_change_prefix_separator(self, *mocks):
        """
        Ensure the prefix separator can be changed
        """
        version_mock = self._setup_version(
            *mocks, version="TestModule/0.0.1-16-g5befeb2"
        )

        args = self._get_args(prefix_separator="-")

        git_version = GitVersion(args)
        new_version_s = git_version.stringify(git_version.version)

        self.assertEqual("TestModule-0.0.1-16-g5befeb2", new_version_s)
