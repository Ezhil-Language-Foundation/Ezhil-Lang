# -*- coding: utf-8 -*-
# (C) 2015 Muthiah Annamalai
# 
# This file is part of Ezhil Language test suite
# 

# setup the paths
from __future__ import print_function
import ezhiltests
from ezhiltests import TestEzhil, ezhil
from  ezhil.errors import ScannerException
from random import choice

# helper functions for testsuites
import unittest
from test import test_support

# this test suite contains negative tests, to trap the 
# correct error behavior of Ezhil language

class BadLexingTests(unittest.TestCase):
    TALETTERS = u'அ|ஆ|இ|ஈ|உ|ஊ|எ|ஏ|ஐ|ஒ|ஓ|ஔ|ஃ|க்|ச்|ட்|த்|ப்|ற்|ங்|ஞ்|ண்|ந்|ம்|ன்|ய்|ர்|ல்|வ்|ழ்|ள்|க|ச|ட|த|ப|ற|ஞ|ங|ண|ந|ம|ன|ய|ர|ல|வ|ழ|ள|ஜ|ஷ|ஸ|ஹ|க|கா|கி|கீ|கு|கூ|கெ|கே|கை|கொ|கோ|கௌ|ச|சா|சி|சீ|சு|சூ|செ|சே|சை|சொ|சோ|சௌ|ட|டா|டி|டீ|டு|டூ|டெ|டே|டை|டொ|டோ|டௌ|த|தா|தி|தீ|து|தூ|தெ|தே|தை|தொ|தோ|தௌ|ப|பா|பி|பீ|பு|பூ|பெ|பே|பை|பொ|போ|பௌ|ற|றா|றி|றீ|று|றூ|றெ|றே|றை|றொ|றோ|றௌ|ஞ|ஞா|ஞி|ஞீ|ஞு|ஞூ|ஞெ|ஞே|ஞை|ஞொ|ஞோ|ஞௌ|ங|ஙா|ஙி|ஙீ|ஙு|ஙூ|ஙெ|ஙே|ஙை|ஙொ|ஙோ|ஙௌ|ண|ணா|ணி|ணீ|ணு|ணூ|ணெ|ணே|ணை|ணொ|ணோ|ணௌ|ந|நா|நி|நீ|நு|நூ|நெ|நே|நை|நொ|நோ|நௌ|ம|மா|மி|மீ|மு|மூ|மெ|மே|மை|மொ|மோ|மௌ|ன|னா|னி|னீ|னு|னூ|னெ|னே|னை|னொ|னோ|னௌ|ய|யா|யி|யீ|யு|யூ|யெ|யே|யை|யொ|யோ|யௌ|ர|ரா|ரி|ரீ|ரு|ரூ|ரெ|ரே|ரை|ரொ|ரோ|ரௌ|ல|லா|லி|லீ|லு|லூ|லெ|லே|லை|லொ|லோ|லௌ|வ|வா|வி|வீ|வு|வூ|வெ|வே|வை|வொ|வோ|வௌ|ழ|ழா|ழி|ழீ|ழு|ழூ|ழெ|ழே|ழை|ழொ|ழோ|ழௌ|ள|ளா|ளி|ளீ|ளு|ளூ|ளெ|ளே|ளை|ளொ|ளோ|ளௌ|ௐ|ஜ|ஜா|ஜி|ஜீ|ஜு|ஜூ|ஜெ|ஜே|ஜை|ஜொ|ஜோ|ஜௌ|ஷ|ஷா|ஷி|ஷீ|ஷு|ஷூ|ஷெ|ஷே|ஷை|ஷொ|ஷோ|ஷௌ|ஸ|ஸா|ஸி|ஸீ|ஸு|ஸூ|ஸெ|ஸே|ஸை|ஸொ|ஸோ|ஸௌ|ஹ|ஹா|ஹி|ஹீ|ஹு|ஹூ|ஹெ|ஹே|ஹை|ஹொ|ஹோ|ஹௌ'.split('|')
    FORBIDDEN_FOR_IDENTIFIERS = [ u"é",u"€",u"$",u"#",u"~",u"λ",u"☺"]
    TOTAL = list()
    TOTAL.extend( TALETTERS )
    TOTAL.extend( FORBIDDEN_FOR_IDENTIFIERS )
    
    @staticmethod
    def pattgen(limit):
        for idx in xrange(limit):
            idlen = choice(range(2,8))
            newID = list()
            for idy in xrange(idlen):
                if choice([2,3])%2 == 0:
                    newID.append( choice( BadLexingTests.TOTAL ) )
                else:
                    newID.append(choice(BadLexingTests.FORBIDDEN_FOR_IDENTIFIERS))
            yield u"".join(newID)
        raise StopIteration

    @staticmethod
    def isNotForbidden( wrongID ):
        return all( filter( lambda x : not x in BadLexingTests.FORBIDDEN_FOR_IDENTIFIERS, wrongID ) )
    
    def test_id(self):
        for idx,wrongID in enumerate(BadLexingTests.pattgen( 2*choice([100,250,350]) )):
            flag = False
            try:
                print("Testing WrongID # %d"%idx,wrongID)                
                code = wrongID+u"= 1"
                TestEzhil(code).run()
            except Exception as e:
                flag = True # OK To error out
            if not flag:
                if BadLexingTests.isNotForbidden( wrongID ):
                    continue
                print(u"WRONG ID was not errored out =>",wrongID)
                raise Exception(u"WRONG ID was not errored out =>"+wrongID)
        return

if __name__ == "__main__":
    unittest.main()
