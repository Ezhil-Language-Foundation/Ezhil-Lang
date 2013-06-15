Ezhil-Lang
==========

Ezhil-Lang : எழில் - ஒரு தமிழ் நிரலாக்க மொழி; தமிழ் மாணவர்களுக்கு இது முதன் முரை கணிப்பொரி நிரல் ஏழுதுவதர்கு உதவும் (Ezhil, is a fun Tamil programming language for K-12)
Exprs is a procedural language with dynamic types,
like Ruby/Python. Exprs has a pascal-like syntax,
with for-end, while-end, if-elseif-else-end statements,
break, continue and def-end for defining functions.

This language is implemented in a handwritten scanner
and parser using the Python programming language in
about 1500LOC.

If you would like to tryout the code, all you need
is a python interpreter, and the code from 
http://omega.uta.edu/~mxa6471/exprs.tar.gz

Interesting features include support for recursion,
and an interactive interpreter. Ezhil supports a Turtle module
for simple on-screen graphics, similar to LOGO language from 1960s.

USAGE
=====

Currently Ezhil language is under development, and a little rough around the
edges. You may still try it out, by going to the git source repository,

$ cd ./ezhil-lang/

and then typing, 

$ ./ez ./ezhil_tests/hello.n 
பதிப்பி "வணக்கம்!"
பதிப்பி "நக்கீரண்  அழைக்கிரது"


வணக்கம்!
நக்கீரண்  அழைக்கிரது

where you should see the output above. For usage, try,

$ ./ez 
usage: ./ez <filename1> .. 
