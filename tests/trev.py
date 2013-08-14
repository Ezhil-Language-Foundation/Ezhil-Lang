# -*- coding:utf-8 -*-
import codecs, sys, re
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

from tamil import get_letters, reverse_word

print get_letters(u"இந்த")
print u"".join(get_letters(u"இந்த"))
for word in u"இந்த (C) tamil முத்தையா அண்ணாமலை 2013 இந்த ஒரு எழில் தமிழ் நிரலாக்க மொழி உதாரணம்".split():
    print reverse_word(word)

print reverse_word(u"இந்த (C) tamil முத்தையா அண்ணாமலை 2013 இந்த ஒரு எழில் தமிழ் நிரலாக்க மொழி உதாரணம்")
