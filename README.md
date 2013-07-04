Ezhil-Lang
==========

Ezhil-Lang : எழில் - ஒரு தமிழ் நிரலாக்க மொழி; தமிழ் மாணவர்களுக்கு இது முதன் முரை கணிப்பொரி நிரல் ஏழுதுவதர்கு உதவும் (Ezhil, is a fun Tamil programming language for K-12)
Ezhil is a procedural language with dynamic types,
like Ruby/Python. Ezhil has a pascal-like syntax,
with for-end, while-end, if-elseif-else-end statements,
break, continue and def-end for defining functions.

Ezhil language is implemented in a handwritten scanner
and parser using the Python programming language in
about 1500LOC.

If you would like to tryout the code, all you need
is a python interpreter, and the code from 
https://github.com/arcturusannamalai/Ezhil-Lang/archive/latest.zip

Read Wikipedia article on Ezhil (Tamil) http://ta.wikipedia.org/w/index.php?title=%E0%AE%8E%E0%AE%B4%E0%AE%BF%E0%AE%B2%E0%AF%8D_%28%E0%AE%A8%E0%AE%BF%E0%AE%B0%E0%AE%B2%E0%AE%BE%E0%AE%95%E0%AF%8D%E0%AE%95_%E0%AE%AE%E0%AF%8A%E0%AE%B4%E0%AE%BF%29

or (English) http://en.wikipedia.org/wiki/Ezhil_%28programming_language%29

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
