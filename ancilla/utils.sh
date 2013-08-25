#!/bin/bash -x
python setup.py sdist
python setup.py build
sudo python setup.py install
cd ./api_docs && ./generate_doc.sh

