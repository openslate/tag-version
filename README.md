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


## Monorepo support

There is initial support for independently versioning different components within a monorepo structure.  Support is using a convention where a component's version is prefixed with the name of the component.  For example, a monorepo may have a component named `api`.  Tags for api changes can be prefixed with the name of the component, for example, `api/1.2.3`.


## Special formats

In some cases it's necessary to output the version in different formats.  For instance, using tag-version to produce a Docker tag will break docker if a monorepo version as described above is used (docker does not like slashes in the tag).  To get a version that is docker-compatible, use the command:

```
tag-version version --format docker
```

### JSON format

In the event that using the command's output for further processing within another piece of code is desires, the JSON format provides the version in a machine-usable format:

```
$ tag-version version --format json
{"version_triple": "0.1.0", "major": "0", "minor": "1", "patch": "0", "prefix": "", "prefix_separator": "", "tags": "rc5-1-g2e13a96-feature--handle-monorepo-project-tag", "prerelease": "rc5-1-g2e13a96-feature--handle-monorepo-project-tag", "prerelease_separator": "", "build": ""}
```


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


## Release Candidates

To generate a release candidate tag, add the `--rc` flag to your `tag-version --bump` invocation:

```
tag-version --bump --rc
```

If the latest version if already a release candidate, then bumping with `--rc`
will increment the release candidate number.

Meanwhile if the latest version is a proper release, adding `--rc` will first
bump the version according to the specified flags (e.g `--minor`) then append `-rc1`.


### Example Usage

```
# latest tag: 0.0.1
tag-version --bump --minor --rc
# latest tag: 0.1.0-rc1
tag-version --bump --rc
# latest tag: 0.1.0-rc2
tag-version --bump
# latest tag: 0.1.0
```

### Tag Version Development

Development is done w/ Docker and `compose-flow`

First you setup some default evn vars
```compose-flow -e local env edit```

```
CF_ENV=local
PYPI_PASSWORD=
PYPI_USERNAME=
```

Then to build the container
```compose-flow -e local compose build```

Then to shell into the container
```compose-flow -e local compose run --rm app /bin/bash```


Testing can then be ran via pytest 
```compose-flow -e local compose run --rm app /bin/bash -c pytest```