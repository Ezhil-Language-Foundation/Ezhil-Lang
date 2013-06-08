#!/usr/bin/python

from ezhil_scanner import *
from ezhil_parser import *
from glob import glob
#["hello.n","fact.n","gcd.n"]:
for prog in glob("../ezhil_tests/*.n"):
        f = EzhilLex(prog)
        f.dump_tokens()
        fmap = dict(); bmap = dict();
        p = EzhilParser(f,fmap, bmap,True)
        ast = p.parse()
        raise Exception("Not implemented")
        env = Environment( call_stack, function_map, \
                           builtin_map, self.debug )
        env.call_function("__toplevel__") ##some context
        rval = ast.evaluate(env)
        print rval


