# -*- coding: utf-8 -*-
# (C) 2017 Ezhil Language Foundation
# This code is part of Ezhil editor 'Ezhuthi'

import os

def getResourceFile(*args):
    path = [get_resource_dir()]
    path.extend(args)
    return os.path.sep.join( path )

def get_resource_dir():
    dirname, filename = os.path.split(os.path.abspath(__file__))
    return os.path.sep.join([dirname,u'res'])
