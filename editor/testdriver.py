#!/usr/bin/env python
##This Python file uses the following encoding: utf-8
##
## (C) 2017 Ezhil Language Foundation
## Licensed under GPL Version 3
from __future__ import print_function
import re
import ezhuthi
import sys
import os
import multiprocessing
import gi
gi.require_version('Gtk','3.0')

from gi.repository import Gtk, GObject, GLib, Pango

def custom_exit(*x):
    Gtk.main_quit()
    #ed = ezhuthi.Editor.get_instance()
    #ed.window.destroy()
    return None

def start_tests():
    test_files = re.split("\s+","""package/examples/armstrong.n
    package/examples/array0.n
    package/examples/array1.n
    package/examples/array2.n
    package/examples/array_nd.n
    package/examples/array_wr.n
    package/examples/bernoulli_number.n
    package/examples/bf0.n
    package/examples/binary.n
    package/examples/bincoeff.n
    package/examples/bitwiseops.n
    package/examples/bmi.n
    package/examples/boolean.n
    package/examples/boolean_demorgan.n
    package/examples/boolean_fcns.n
    package/examples/bubblesort.n
    package/examples/caesar.n
    package/examples/calc2.n
    package/examples/calc_asmd.n
    package/examples/calendar_days.n
    package/examples/centerofmass.n
    package/examples/cg_square.n
    package/examples/change.n
    package/examples/constfold.n
    package/examples/convert2kelvin.n
    package/examples/datetime.n
    package/examples/demoif.n
    package/examples/dict.n
    package/examples/dict_rw.n
    package/examples/dict_ta.n
    package/examples/douglasfir.n
    package/examples/dowhile.n
    package/examples/dyna.n
    package/examples/envchecks.n
    package/examples/eval0.n
    package/examples/eval1.n
    package/examples/even_odd.n
    package/examples/fact.n
    package/examples/factorial.n
    package/examples/fern.n
    package/examples/fibo.n
    package/examples/fibo2.n
    package/examples/filedemo.n
    package/examples/filerw.n
    package/examples/find.n
    package/examples/floatpthole.n
    package/examples/foo.n
    package/examples/ford.n
    package/examples/ford2.n
    package/examples/foreach.n
    package/examples/foriter.n
    package/examples/fornested.n
    package/examples/friends.n
    package/examples/fruity.n
    package/examples/full_adder.n
    package/examples/gcd.n
    package/examples/gigo.n
    package/examples/globalvars.n
    package/examples/hailstone.n
    package/examples/half_adder.n
    package/examples/hanoi.n
    package/examples/hello.n
    package/examples/hello2.n
    package/examples/hexadecimal.n
    package/examples/hist.n
    package/examples/hist_of_C.n
    package/examples/histogram.n
    package/examples/hola.n
    package/examples/if0.n
    package/examples/if1.n
    package/examples/if2.n
    package/examples/ifchain.n
    package/examples/ifnested.n
    package/examples/ifparse.n
    package/examples/il.n
    package/examples/isbalanced.n
    package/examples/json_demo.n
    package/examples/keyword_notes.n
    package/examples/kuvippu.n
    package/examples/lcmgcd.n
    package/examples/letters.n
    package/examples/lex2.n
    package/examples/lisp0.n
    package/examples/list.n
    package/examples/list_ta.n
    package/examples/listmt.n
    package/examples/logical_not.n
    package/examples/logo.n
    package/examples/loopupdate.n
    package/examples/magic_coins.n
    package/examples/mangalyaan.n
    package/examples/maram.n
    package/examples/math_arithprogression.n
    package/examples/math_complex.n
    package/examples/math_geomprogression.n
    package/examples/math_goldenratio.n
    package/examples/math_harmonicseries.n
    package/examples/math_horner.n
    package/examples/mathipeedu.n
    package/examples/max_wo_compare.n
    package/examples/ml.n
    package/examples/multiline_string.n
    package/examples/name_var.n
    package/examples/neuron.n
    package/examples/oklex.n
    package/examples/only.n
    package/examples/optional.n
    package/examples/palindromes.n
    package/examples/partition_estimate.n
    package/examples/pattern_basic.n
    package/examples/pattiyal.n
    package/examples/piglatin.n
    package/examples/powers_of_two.n
    package/examples/predicates.n
    package/examples/prime.n
    package/examples/printtest.n
    package/examples/py1.n
    package/examples/quadroots.n
    package/examples/ranges.n
    package/examples/reverse.n
    package/examples/reverse_stack.n
    package/examples/rich_poor.n
    package/examples/rndclr.n
    package/examples/rot13.n
    package/examples/select_case2.n
    package/examples/sexpr.n
    package/examples/sine_qua_non.n
    package/examples/sort.n
    package/examples/speedoflight.n
    package/examples/split_text.n
    package/examples/staircase_light.n
    package/examples/string_demo.n
    package/examples/strings.n
    package/examples/strrev.n
    package/examples/sum_of_digits.n
    package/examples/ta247.n
    package/examples/ta_sort.n
    package/examples/ta_strings.n
    package/examples/tables.n
    package/examples/tamil1.n
    package/examples/tamil2.n
    package/examples/tamil_letters.n
    package/examples/tamil_months.n
    package/examples/tamil_tha.n
    package/examples/thodarpattiyal.n
    package/examples/tictok.n
    package/examples/tower_of_hanoi.n
    package/examples/trials.n
    package/examples/unaryop.n
    package/examples/unop.n
    package/examples/urldemo.n
    package/examples/vannakm.n
    package/examples/varavu_selavu.n
    package/examples/windoze.n""")
    assert(len(test_files) > 150)
    total_files = len(test_files)
    passed = 0
    actual_exit = sys.exit
    sys.exit = custom_exit
    ed = ezhuthi.Editor()
    for test in test_files:
        #print("Running -> %s"%test)
        try:
            ed.autorun = True
            ed.filename = test
            ed.load_file()
            ed.do_autorun()
            Gtk.main()
            print("%s -> OK"%test)
            passed += 1
        except Exception as e:
            print("Test case %s failed with error %s"%(test,str(e)))
    sys.exit = actual_exit
    sys.exit( passed != total_files ) #exit 0 is success

if __name__ == u"__main__":
    # show preference for user locale.
    if ( os.getenv('LANG','en_US.utf8').lower().find("ta") == -1 ):
        os.putenv('LANG','ta_IN.utf8')
    multiprocessing.freeze_support()
    GObject.threads_init()
    start_tests()
