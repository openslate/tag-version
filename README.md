# git-version

This utility makes semantic versioning of source code with git tags easy and consistent.

On a new project, `git-version` displays a friendly suggestion:

```
$ git-version
No version found, use --bump to set to 0.0.1
```

Upon using the `--bump` flag, the version is set:

```
$ git-version --bump
0.0.1
```

Attempting to bump a tagged revision will result in an error message:

```
$ git-version --bump
Is version=0.0.1 already bumped?
```

With no flags, the current version will be displayed:

```
$ git-version
0.0.1
```

And when modifications are made, `git-version` uses `git describe` to provide a unique version:

```
$ git-version
0.0.1-2-g5bd60a7
```

## Semantic versioning

The `--bump` flag will monotonically increase the version number.  By default, the patch version -- that is, the third number in the dotted sequence.  This can be explicitly specified by running `git-version --bump --patch`.

Similarly, the `--minor` or `--major` argument can be given to increment the minor or major versions respectively.


## Help text

```
$ git-version -h
usage: git-version [-h] [--bump] [--patch] [--minor] [--major]

optional arguments:
  -h, --help  show this help message and exit
  --bump      perform a version bump, by default the current version is
              displayed
  --patch     bump the patch version, this is the default bump if one is not
              specified
  --minor     bump the minor version and reset patch back to 0
  --major     bump the major version and reset minor and patch back to 0
```
