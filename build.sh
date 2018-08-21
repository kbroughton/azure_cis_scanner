#!/bin/bash
#git add HISTORY.rst
#git commit -m "Changelog for upcoming release 0.1.1."
# bumpversion  --verbose  --dry-run --message '[{now:%Y-%m-%d}]Jenkins Build {$BUILD_NUMBER}: {new_version}' patch  # patch could also be minor or major
bumpversion --verbose  --message '[{now:%Y-%m-%d}] {new_version}' patch
python setup.py sdist upload  # -url test  # behind prod by 1 git commit, but code is same.
python setup.py bdist_wheel upload  # -url test

# test pip install to new virtualenv
# https://gist.github.com/audreyr/5990987
git push origin master 
git push origin master --tags

python setup.py sdist upload  # -url prod
python setup.py bdist_wheel upload  # -url prod
