## This Python file uses the following encoding: utf-8
##
## (C) 2013 Sathia N Mahadevan <msathia@gmail.com>
## Licensed under GPL Version 3

import codecs, sys, re
from tamil import *

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

## Split a tamil-unicode stream into
## tamil characters (individuals).
def get_tamil_letters_array( word ):
	prev = u''
	ta_letters = []
        for c in word:
		if c in uyir_letters or c == ayudha_letter:
			ta_letters.append(prev+c)
			prev = u''
		elif c in agaram_letters or c in sanskrit_letters:
			if prev != u'':
				ta_letters.append(prev)
			prev = c
		elif c in accent_symbols:
			ta_letters.append(prev+c)
			prev = u''
              
		else:
			if prev != u'':
				ta_letters.append(prev+c)
				prev = u''
			elif ord(c) < 256:
				# plain-old ascii
				ta_letters.append( c )
			else:
				assert False #unknown/expected state
	if prev != u'': #if prev is not null it is $c
		ta_letters.append( prev )
	return ta_letters



word3=[]
word2=[]
word = raw_input("enter tamil word:")
word2= word.decode('utf-8')
print "Given word in Unicode"+word2
word3=get_tamil_letters_array(word2)
print word3
word3.reverse()
print u"".join(word3)









