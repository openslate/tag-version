from unittest import TestCase, mock

from tagversion.git import GitVersion, is_rc

RC_VERSION = '0.1.28rc1-1-g4fafe09-feature--skip-prefix-rows'


@mock.patch('tagversion.git.sh')
class GitTestCase(TestCase):
    def _setup_version(self, *mocks, version=RC_VERSION):
        version_mock = mocks[0]
        version_mock.return_value = version

        return version_mock

    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_bump_no_tag(self, *mocks):
        """
        Ensures bumping when there is no tag produces 0.0.1
        """
        version_mock = self._setup_version(*mocks, version='000000-master')

        args = mock.Mock(calver=False, major=False, minor=False, patch=True, rc=False)

        git_version = GitVersion(args)

        new_version = git_version.bump()

        self.assertEquals([0, 0, 1], new_version)


    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_bump_to_rc(self, *mocks):
        """
        Ensures bumping to an RC properly revs version
        """
        version_mock = self._setup_version(*mocks, version='0.1.27-16-g5befeb2-feature--skip-prefix-rows')

        args = mock.Mock(calver=False, major=False, minor=False, patch=True, rc=True)

        git_version = GitVersion(args)

        new_version = git_version.bump()

        self.assertEquals([0, 1, '28rc1'], new_version)

    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_bump_rc(self, *mocks):
        """
        Ensures running bump results in a stable, non-rc, release
        """
        version_mock = self._setup_version(*mocks)

        args = mock.Mock(calver=False, major=False, minor=False, patch=True, rc=False)

        git_version = GitVersion(args)

        self.assertEquals(version_mock.return_value, git_version.version)

        new_version = git_version.bump()

        self.assertEquals([0, 1, 28], new_version)

    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_bump_rc_to_stable(self, *mocks):
        """
        Ensures running bump results in a stable, non-rc, release
        """
        version_mock = self._setup_version(*mocks, version='0.1.28rc2')

        args = mock.Mock(calver=False, major=False, minor=False, patch=True, rc=False)

        git_version = GitVersion(args)

        self.assertEquals(version_mock.return_value, git_version.version)

        new_version = git_version.bump()

        self.assertEquals([0, 1, 28], new_version)

    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_bump_rev_rc(self, *mocks):
        """
        Ensures running bump --rc on an RC results in a proper rc tag
        """
        version_mock = self._setup_version(*mocks)

        args = mock.Mock(rc=True)

        git_version = GitVersion(args)

        self.assertEquals(version_mock.return_value, git_version.version)

        new_version = git_version.bump()

        self.assertEquals(['0', '1', '28rc2'], new_version)

    def test_get_next_rc_version(self, *mocks):
        """
        Ensures git version stuff is removed from next version
        """
        next_version = GitVersion.get_next_rc_version(RC_VERSION)

        self.assertEquals(['0', '1', '28rc2'], next_version)

    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_is_rc(self, *mocks):
        """
        Ensures RC is properly detected
        """
        self.assertEquals(True, is_rc(RC_VERSION))
