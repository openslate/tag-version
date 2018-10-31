#!/bin/bash
set -e

version=$(tag-version)

tag-version write --pattern "(?P<start>.*?)0.0.0(?P<content>.*)" setup.py

rc=0
python setup.py sdist || rc=$?
git checkout setup.py

if [ "${rc}" != "0" ]; then
    echo "error building source distribution"
    exit ${rc}
fi;

twine upload dist/*${version}*
