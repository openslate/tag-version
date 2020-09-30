import re

from .exceptions import VersionError

"""
    Uses a slightly modified version of this regex
    https://regex101.com/r/E0iVVS/2
"""
SEMVER_RE = re.compile(
    """
                       ^(?P<prefix>.*/)?
                       (?P<version_triple>
                            (?P<major>0|[1-9][0-9]*)\.
                            (?P<minor>0|[1-9][0-9]*)\.?
                            (?P<patch>0|[1-9][0-9]*)?
                        ){1}
                        (?P<tags>(?:\-?
                            (?P<prerelease>
                                (?:(?=[0]{1}[0-9A-Za-z-]{0})(?:[0]{1})|(?=[1-9]{1}[0-9]*[A-Za-z]{0})(?:[0-9]+)|(?=[0-9]*[A-Za-z-]+[0-9A-Za-z-]*)(?:[0-9A-Za-z-]+)){1}(?:\.(?=[0]{1}[0-9A-Za-z-]{0})(?:[0]{1})|\.(?=[1-9]{1}[0-9]*[A-Za-z]{0})(?:[0-9]+)|\.(?=[0-9]*[A-Za-z-]+[0-9A-Za-z-]*)(?:[0-9A-Za-z-]+))*){1}
                            ){0,1}(?:\+
                            (?P<build>
                                (?:[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*
                            ))
                        ){0,1})$
                       """,
    re.VERBOSE,
)


class Version:
    def __init__(
        self,
        major="0",
        minor="0",
        patch="0",
        prefix=None,
        prerelease=None,
        tags=None,
        build=None,
        version_triple=None,
    ):
        """
        Args:
            version_triple: the dotted version number, e.g. '1.2.3'
            major: the first number in the triple, e.g. '1'
            minor: the second number in the triple, e.g. '2'
            patch: the third number in the triple, e.g. '3'
            prefix: the prefix prior to the version triple
            tags:
            prerelease: None
            build: None
        """
        self.version_triple = version_triple
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prefix = prefix
        self.tags = tags
        self.prerelease = prerelease
        self.build = build

    def __eq__(self, other):
        return str(self) == str(other)

    def __repr__(self):
        return f"<Version: {self}>"

    def __str__(self):
        return self.stringify()

    @classmethod
    def parse(cls, version_s: str) -> "Version":
        matches = SEMVER_RE.match(version_s)
        if not matches:
            raise VersionError(f"unable to parse version_s={version_s}")

        return Version(**matches.groupdict())

    def stringify(self, display_prefix: bool = True):
        version = f"{self.major}.{self.minor}.{self.patch}"

        if display_prefix and self.prefix:
            version = f"{self.prefix}{version}"

        if self.prerelease:
            version = f"{version}{self.prerelease}"

        return version
