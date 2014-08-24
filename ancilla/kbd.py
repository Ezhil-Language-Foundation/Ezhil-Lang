# (C) 2013 Muthiah Annamalai
# 
# Licensed under GPL Version 3

# you need to install Ezhil package from py-py
from ezhil.tamil import *

print uyirmei_letters[0]

def output( ta_letter, kw_tag ):
    print u"".join([u"""<input type="button" name="btn_kw_""",kw_tag,"""" value='""",ta_letter,"""' onClick="appendText('""",ta_letter,u"""')"; />"""])

def newline():
    return "<BR />"

#print uyir - vowels
print "<!-- uyir -->"
for pos,ta_letters in enumerate(uyir_letters):
    output( ta_letters, u"uyir_"+ str(pos))

output( ayudha_letter, u"ayudham" )

#print mei - consonants
print "<!-- mei -->"
for pos,ta_letters in enumerate(mei_letters):
    print ta_letters
    output( ta_letters, u"mei_"+ str(pos))

# print uyirmei
print "<!-- uyirmei -->"
for pos,ta_letters in enumerate(uyirmei_letters):
    print ta_letters
    output( ta_letters, "uyirmei_"+ str(pos))
    if ( pos%11 == 0 ):
        print newline()
    
