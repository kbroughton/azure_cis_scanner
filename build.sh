#!/bin/bash
#git add HISTORY.rst
#git commit -m "Changelog for upcoming release 0.1.1."
# bumpversion  --verbose  --dry-run --message '[{now:%Y-%m-%d}]Jenkins Build {$BUILD_NUMBER}: {new_version}' patch  # patch could also be minor or major
bumpversion  --message '[{now:%Y-%m-%d}] {new_version}' patch
python setup.py sdist upload
python setup.py bdist_wheel upload
git push origin master --tags
