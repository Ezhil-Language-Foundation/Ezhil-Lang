#!/bin/bash -x
pyinstaller --windowed --log-level DEBUG --add-data "res/editor.glade:res" --add-data "examples/untitled.n:examples" --add-data "res/img/ezhil_square_2015_128px.png:res/img" --icon ezhil16.ico ezhuthi.py

pyinstaller --log-level DEBUG --icon ezhil16.ico bin/ezhili.py

