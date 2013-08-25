Ezhil-Lang
==========

Ezhil-Lang : எழில் - ஒரு தமிழ் நிரலாக்க மொழி; தமிழ் மாணவர்களுக்கு இது முதல்முறை கணிப்பொறி நிரல் ஏழுத உதவும் (Ezhil, is a fun Tamil programming language for K-12)
Ezhil is a procedural language with dynamic types,
like Ruby/Python. Ezhil has a pascal-like syntax,
with for-end, while-end, if-elseif-else-end statements,
break, continue and def-end for defining functions.

Ezhil language is implemented in a handwritten scanner
and parser using the Python programming language. Latest version of Ezhil-Language is v0.6.

If you would like to tryout the code, all you need
is a python interpreter, and the code from 
https://github.com/arcturusannamalai/Ezhil-Lang/archive/latest.zip

Interesting features include support for recursion,
and an interactive interpreter. Ezhil supports a Turtle module
for simple on-screen graphics, similar to LOGO language from 1960s.

REFERENCES
==========
Read Wikipedia article(s) on Ezhil,

1. (Tamil) http://bit.ly/16MgU6U
2. (English) http://en.wikipedia.org/wiki/Ezhil_%28programming_language%29

Scholarly articles on Ezhil include,

1. M. Annamalai, "Ezhil : A Tamil Programming Language," (2009). http://arxiv.org/abs/0907.4960
2. -do-, "Invitation to Ezhil: A Tamil Programming Language for Early Computer-Science Education," (2013). http://arxiv.org/abs/1308.1733


USAGE
=====

Currently Ezhil language is under development, and a little rough around the
edges. You may still try it out, by going to the git source repository,

$ cd ./ezhil-lang/

and then use one of the three modes,

1. Batch Mode
2. Interactive Mode
3. Web Mode

Batch Mode
==========
```bash
$ ./ez ./ezhil_tests/hello.n 
பதிப்பி "வணக்கம்!"
பதிப்பி "எழில் அழைக்கிறது"

வணக்கம்!
எழில் அழைக்கிறது
```

where you should see the output above. For usage, try,
```bash
$ ./ez --help
usage:  [-h] [-debug] [-stdin] [files [files ...]]

positional arguments:
  files

optional arguments:
  -h, --help  show this help message and exit
  -debug      enable debugging information on screen
  -stdin      read input from the standard input
```

Interactive Mode
================
```bash
$ ./ez
எழில் 1>> 1 + 5
6
எழில் 2>> பதிப்பி "வணக்கம்! எழில் அழைக்கிறது"
வணக்கம்! எழில் அழைக்கிறது
எழில் 3>> exit()
```

Web Mode
========
You can also run ezhil as a web service by launching the webserver,
$ ./webserver.sh
and open the webpage, http://localhost:8080 in google-chrome or firefox,
to enter your program and evaluate it.

Python Library
==============
Ezhil Tamil programming Python package can be invoked from within the Python shell or IDLE on Windows, by simply typing,
```python
>> import ezhil
>> ezhil.start()
```

But to do all of this, you need to build and install the Python packages from this source, by,
```bash
$ cd ezhil-lang/ && python setup.py build
$ cd ezhil-lang/ && python setup.py install
```
