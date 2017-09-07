#!/bin/sh -x
# Run this file to begin building ezhuthi package
cp -ar ../editor ./ezhuthi
find ./ -iname '*~' | xargs rm -vf
# after this step you can run usual
# python setup.py sdist build
# python setup.py sdist install
