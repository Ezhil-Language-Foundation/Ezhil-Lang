#!/bin/bash -x
if [ -e ezhuthi.spec ]
then
    pyinstaller --windowed --log-level=DEBUG --icon=ezhil16.ico ezhuthi.spec
else
    pyinstaller --windowed --log-level=DEBUG --icon=ezhil16.ico ezhuthi.py
fi
cp -ar res/ ./examples ./xmlbook ./dist/ezhuthi/
cd dist/
BDIR=ezhil-`date +'%m%d%y'`
mkdir $BDIR
mv ezhuthi $BDIR
