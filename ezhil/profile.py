#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2015 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Profiler for Ezhil language

import time
import sys

PYTHON3 = (sys.version[0] == '3')

# import collections
# FunctionProfileRecord 
#    name - str
#    start_time - list
#    end_time - list
#    self_time - list
#    ncalls - int
#    cum_time - list
#    total_time - float
#FunctionProfileRecord = collections.namedtuple(u'FunctionProfileRecord',\
#                                                   [u'name',u'start_time',u'end_time',u'cum_time',u'self_time',u'ncalls',u'total_time'])
class FunctionProfileRecord(object):
    def __init__(self,name,start_time,end_time,cum_time,self_time,ncalls,total_time):
        object.__init__(self)
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.cum_time = cum_time
        self.self_time =self_time
        self.self_time_running = 0 #self-time running deficit of all downstream calls
        self.ncalls =ncalls
        self.total_time = total_time
        self.total_self_time = 0
    
class Profiler(object):
    def __init__(self):
        object.__init__(self)
        self.call_stack = []
        self.function_records = {}
        self.add_function("profile")
    
    def calc_total_time(self):
        for fname,frec in self.function_records.items():
            frec.total_time = sum(frec.cum_time)
            frec.total_self_time = sum(frec.self_time)
        return
    
    def report_stats(self):
        self.calc_total_time()
        fnames = self.function_records.keys()
        frecs = self.function_records.values()
        
        if PYTHON3:
            fnames = list(fnames)
            frecs = list(frecs)
            frecs = sorted ( frecs , key = lambda rec_x: rec_x.total_time )
        else:
            frecs.sort( lambda rec_x,rec_y: cmp(rec_x.total_time,rec_y.total_time) )
        frecs.reverse()
        print(u"############# Ezhil Code Profile Report ##################")
        print(u"######## program completed in %g (s) ##############"%frecs[0].total_time)
        print(u" Function  | N  | Avg(Self)| Avg (Cum)| Total ")
        print(u"----------------------------------------------------------")
        for rec in frecs:
            rec.name = rec.name.strip()
            if len(rec.name) < 10:
                padded_name = rec.name + " "*(10-len(rec.name)-1)
            else:
                padded_name = rec.name[0:9]
            
            print(u"%10s | %3d| %5f | %3f | %5f"%(padded_name,rec.ncalls,\
                                                  (rec.total_self_time/rec.ncalls)/1e-3,\
                                                  (rec.total_time/rec.ncalls)/1e-3,rec.total_time/1e-3))
        print(u"##########################################################")
        return
    
    def add_function(self,fname):
        self.add_new_function(fname,time.time())
                
    def add_new_function(self,fname,start_time):
        if not self.function_records.get( fname, None):
            frec = FunctionProfileRecord(name = fname, \
                                             start_time = [start_time], \
                                             ncalls = 1, \
                                             end_time = [], \
                                             cum_time = [], \
                                             self_time = [0], \
                                             total_time = 0)
            self.function_records[fname] = frec
        else:
            frec = self.function_records[fname]
            frec.ncalls += 1
        self.call_stack.append(frec)
        frec.start_time.append( start_time )        
    
    def update_function(self,fname):
        self.update_function_on_return(fname,time.time())
        
    def update_function_on_return(self,fname,end_time):
        frec = self.function_records[fname]
        assert( frec == self.call_stack.pop() )
        frec.end_time.append( end_time )
        frec.cum_time.append( frec.end_time[-1] - frec.start_time[-1] )
        frec.self_time.append( frec.cum_time[-1] + frec.self_time_running )
        if len(self.call_stack) >= 1:
            prev_rec = self.call_stack[-1]
            prev_rec.self_time_running =  prev_rec.self_time_running - frec.cum_time[-1]
        return

if __name__ == u"__main__":
    pr = Profiler()
    pr.add_new_function('a',time.time())
    time.sleep(1)
    
    pr.add_new_function('b',time.time())
    time.sleep(2)
    pr.add_new_function('c',time.time())
    time.sleep(1)
    pr.update_function_on_return('c',time.time())
    time.sleep(1)
    pr.update_function_on_return('b',time.time())
    
    pr.add_new_function('b',time.time())
    time.sleep(2)
    pr.add_new_function('c',time.time())
    time.sleep(1)
    pr.update_function_on_return('c',time.time())
    time.sleep(1)
    pr.update_function_on_return('b',time.time())

    pr.update_function_on_return('a',time.time())
    
    pr.report_stats()
