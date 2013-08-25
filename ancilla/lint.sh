#!/bin/bash
cd ./ezhil
for i in `ls *.py`; do pychecker $i; done
cd ../
