import json
import re

from .exceptions import PrereleaseError, VersionError

"""
Uses a slightly modified version of this regex
https://regex101.com/r/E0iVVS/2

copied to:

https://regex101.com/r/NpbTSw/4
"""
SEMVER_RE = re.compile(
    r"""
    ^(?:(?P<prefix>.*)(?P<prefix_separator>.*/))?
    (?P<version_triple>
        (?P<major>0|[1-9][0-9]*)\.
        (?P<minor>0|[1-9][0-9]*)\.?
        (?P<patch>0|[1-9][0-9]*)?
    ){0,1}
    (?P<tags>(?:
        (?P<prerelease_separator>\-?)
        (?P<prerelease>
            (?:(?=[0]{1}[0-9A-Za-z-]{0})(?:[0]{1})|(?=[1-9]{1}[0-9]*[A-Za-z]{0})(?:[0-9]+)|(?=[0-9]*[A-Za-z-]+[0-9A-Za-z-]*)(?:[0-9A-Za-z-_]+)){1}(?:\.(?=[0]{1}[0-9A-Za-z-]{0})(?:[0]{1})|\.(?=[1-9]{1}[0-9]*[A-Za-z]{0})(?:[0-9]+)|\.(?=[0-9]*[A-Za-z-]+[0-9A-Za-z-]*)(?:[0-9A-Za-z-]+))*){1}
        ){0,1}(?:\+
        (?P<build>
            (?:[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*
        ))
    ){0,1})$
    """,
    re.VERBOSE,
)

RC_RE = re.compile(
    r"(?P<full_version>(?P<stable>.*)(?P<prerelease>rc(?P<rc_number>\d+))).*"
)


class Version:
    def __init__(
        self,
        major="0",
        minor="0",
        patch="0",
        prefix=None,
        prefix_separator=None,
        prerelease=None,
        prerelease_separator=None,
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
        self.prefix = prefix or ""
        self.prefix_separator = prefix_separator or ""
        self.tags = tags
        self.prerelease = prerelease or ""
        self.prerelease_separator = prerelease_separator or ""
        self.build = build or ""

    def __eq__(self, other):
        return str(self) == str(other)

    def __repr__(self):
        return f"<Version: {self}>"

    def __str__(self):
        return self.stringify()

    def bump(
        self,
        bump_major: bool = False,
        bump_minor: bool = False,
        bump_patch: bool = False,
        bump_prerelease: bool = False,
    ):
        if bump_major:
            self.major = f"{int(self.major)+1}"

        if bump_minor:
            self.minor = f"{int(self.minor)+1}"

        if bump_patch:
            self.patch = f"{int(self.patch)+1}"

        if bump_prerelease:
            if self.prerelease and self.prerelease.startswith("rc"):
                matches = RC_RE.match(self.prerelease)
                if not matches:
                    raise PrereleaseError()

                self.prerelease = f"rc{int(matches.group('rc_number'))+1}"
            else:
                self.prerelease_separator = ""
                self.prerelease = "rc1"

        # when everything is False and the version is a prerelease, drop the prerelease
        if self.prerelease and not bump_prerelease:
            self.prerelease_separator = ""
            self.prerelease = None

    def copy(self) -> "Version":
        new_version = Version()
        new_version.__dict__ = self.__dict__.copy()

        return new_version

    def _get_semver(self) -> str:
        """
        Returns the major.minor.patch component
        """
        version = ""
        if None not in (self.major, self.minor, self.patch):
            version = f"{self.major}.{self.minor}"
            if self.patch:
                version = f"{version}.{self.patch}"

        return version

    @property
    def is_prerelease(self):
        """
        Returns whether this contains a semantic version and no tags
        """
        return self.is_semver and self.tags != ""

    @property
    def is_rc(self):
        return self.prerelease and self.prerelease.startswith("rc")

    @property
    def is_release(self):
        """
        Returns whether this contains a semantic version and no tags
        """
        return self.is_semver and self.tags is None

    @property
    def is_semver(self) -> bool:
        """
        Returns whether contains a semantic version
        """
        return None not in (self.major, self.minor, self.patch)

    @property
    def is_unreleased(self) -> bool:
        """
        Returns whether this doesn't contain a semantic version and tags
        """
        return not self.is_semver and self.tags != ""

    @classmethod
    def parse(cls, version_s: str) -> "Version":
        matches = SEMVER_RE.match(version_s)
        if not matches:
            raise VersionError(f"unable to parse version_s={version_s}")

        return Version(**matches.groupdict())

    def stringify(self, format: str = "default", args: object = None) -> str:
        stringify_method = getattr(self, f"stringify_{format}")

        return stringify_method(args=args)

    def stringify_default(self, args: object = None) -> str:
        version = self._get_semver()

        display_prefix = args.display_prefix if args else True
        if display_prefix and self.prefix:
            version = f"{self.prefix}{self.prefix_separator}{version}"

        if self.prerelease:
            version = f"{version}{self.prerelease_separator}{self.prerelease}"

        return version

    def stringify_docker(self, args: object = None) -> str:
        version = self._get_semver()
        prefix_separator = "-"

        # replace the slash separator with
        display_prefix = args.display_prefix if args else True
        if display_prefix and self.prefix:
            version = f"{self.prefix}{prefix_separator}{version}"

        if self.prerelease:
            version = f"{version}{self.prerelease_separator}{self.prerelease}"

        return version

    def stringify_json(self, args: object = None) -> str:
        """Returns the parsed version as a JSON string"""
        return json.dumps(self.__dict__)

    def stringify_sugar(self, args: object = None):
        version = self._get_semver()

        if self.build:
            version = f"{version}-{self.build}"

        if self.prerelease:
            version = f"{version}{self.prerelease_separator or ''}{self.prerelease}"

        return version
