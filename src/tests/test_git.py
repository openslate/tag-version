from unittest import TestCase, mock

from tagversion.git import GitVersion, is_rc

RC_VERSION = '0.1.28rc1-1-g4fafe09-feature--skip-prefix-rows'


@mock.patch('tagversion.git.sh')
class GitTestCase(TestCase):
    def _get_args(self, **kwargs):
        args = mock.Mock(calver=False, major=False, minor=False, patch=False, prefix=None, rc=False)

        for k, v in kwargs.items():
            setattr(args, k, v)

        return args

    def _setup_version(self, *mocks, version=RC_VERSION):
        version_mock = mocks[0]
        version_mock.return_value = version

        return version_mock

    def _setup_git_describe(self, *mocks, version: str) -> None:
        sh_mock = mocks[-1]
        sh_mock.git.return_value.stdout = version.encode('utf8')

    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_bump_no_tag(self, *mocks):
        """
        Ensures bumping when there is no tag produces 0.0.1
        """
        version_mock = self._setup_version(*mocks, version='000000-master')

        args = self._get_args(patch=True)

        git_version = GitVersion(args)

        new_version = git_version.bump()

        self.assertEquals([0, 0, 1], new_version)


    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_bump_to_rc(self, *mocks):
        """
        Ensures bumping to an RC properly revs version
        """
        version_mock = self._setup_version(*mocks, version='0.1.27-16-g5befeb2-feature--skip-prefix-rows')

        args = self._get_args(patch=True, rc=True)

        git_version = GitVersion(args)

        new_version = git_version.bump()

        self.assertEquals([0, 1, '28rc1'], new_version)

    @mock.patch('tagversion.git.GitVersion.version', new_callable=mock.PropertyMock)
    def test_bump_rc(self, *mocks):
        """
        Ensures running bump results in a stable, non-rc, release
        """
        version_mock = self._setup_version(*mocks)

        args = self._get_args(patch=True)

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

        args = self._get_args(patch=True)

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

    def test_remove_project_prefix(self, *mocks):
        """
        When getting a tag with a prefix, remove the prefix
        """
        version_mock = self._setup_git_describe(*mocks, version='TestModule/0.0.1')

        args = self._get_args()

        git_version = GitVersion(args)

        self.assertEquals('0.0.1', git_version.version)

    def test_bump_project_prefix(self, *mocks):
        """
        When getting a tag with a prefix, remove the prefix
        """
        version_mock = self._setup_git_describe(*mocks, version='TestModule/0.0.1-16-g5befeb2')

        args = self._get_args(patch=True, prefix='TestModule/')

        git_version = GitVersion(args)
        new_version = git_version.bump()
        new_version_s = git_version.stringify(new_version)

        self.assertEquals('TestModule/0.0.2', new_version_s)
