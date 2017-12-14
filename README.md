# tag-version

This utility makes semantic versioning of source code with git tags easy and consistent.

This tool is mostly based around [git's `describe`](https://git-scm.com/docs/git-describe) subcommand with the addition including the branch name in the version string.


## Installation

```
pip install tag-version
```

More information at: https://pypi.python.org/pypi/tag-version


## Usage

On a new project, `tag-version` displays a friendly suggestion:

```
$ tag-version
No version found, use --bump to set to 0.0.1
```

Upon using the `--bump` flag, the version is set:

```
$ tag-version --bump
0.0.1
```

Attempting to bump a tagged revision will result in an error message:

```
$ tag-version --bump
Is version=0.0.1 already bumped?
```

With no flags, the current version will be displayed:

```
$ tag-version
0.0.1
```

And when commits are made on top of a tag, `tag-version` uses `git describe` to provide a unique version and appends the current branch:

```
$ tag-version
0.0.1-2-g5bd60a7-master
```

This is especially useful when branch names are descriptive and include an ID referring to an issue tracker:

```
$ tag-version
0.0.1-2-g5bd60a7-bugfix--482-modal-options
```

Appending the branch can be disabled with the `--no-branch` option:

```
$ tag-version --no-branch
0.0.1-2-g5bd60a7
```


## Semantic versioning

The `--bump` flag will monotonically increase the version number.  By default, the patch version -- that is, the third number in the dotted sequence.  This can be explicitly specified by running `tag-version --bump --patch`.

Similarly, the `--minor` or `--major` argument can be given to increment the minor or major versions respectively.


### Help text

```
$ tag-version version --help
usage: tag-version version [-h] [--bump] [--patch] [--minor] [--major]
                           [--set SET] [--no-branch]

optional arguments:
  -h, --help   show this help message and exit
  --bump       perform a version bump, by default the current version is
               displayed
  --patch      bump the patch version, this is the default bump if one is not
               specified
  --minor      bump the minor version and reset patch back to 0
  --major      bump the major version and reset minor and patch back to 0
  --set SET    set version to the given version
  --no-branch  do not append branch to the version when current commit is not
               tagged
```


## Write subcommand

Running `tag-version write <path>` will rewrite any `{{ version }}` tags in the given path with the current tag version.


### Help text

```
[berto@g6]$ tag-version write --help
usage: tag-version write [-h] [--branch] [--pattern PATTERN] path

positional arguments:
  path               path to the file to write version in

optional arguments:
  -h, --help         show this help message and exit
  --pattern PATTERN  a regex pattern to search and replace with the version,
                     default "(?P<start>.*?){{\s*version\s*}}(?P<content>.*)"
```
