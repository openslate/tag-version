from unittest import TestCase, mock

from tagversion.version import Version


class VersionTestCase(TestCase):
    def test_parse_semver(self, *mocks):
        """Ensure a basic semver is parsed"""

        version = Version.parse("0.0.1")

        self.assertEquals(Version(major=0, minor=0, patch=1), version)

    def test_parse_semver_with_prefix(self, *mocks):
        """Ensure a basic semver is parsed"""

        version = Version.parse("TestModule/0.0.1")

        self.assertEquals(
            Version(major=0, minor=0, patch=1, prefix="TestModule/"), version
        )

        self.assertEquals("TestModule/0.0.1", str(version))
