Ezhil-Lang API
==============
Following functions are available from Ezhil language API


String Methods
==============
0. "" - create strings;  ஆ = "ஆடு"
1. நீளம் - length of string; நீளம்(அ)
2. + - join two strings; அ  + ஆ
3. சரம்\_கண்டுபிடி - find if one needle string is within other haystack - சரம்\_கண்டுபிடி( முக்கனி , "வாழை" ) 
4. சரம்\_இடமாற்று - search and replace; சரம்\_இடமாற்று(  முக்கனி , "வாழை", "கொய்யா")

பட்டியல் (List) Methods
=======================
0. பட்டியல்() - list - create a empty list; same as using [].
1. பின்இணை - append an element to list; பின்இணை( ப , 15 )
2. வரிசைப்படுத்து  - sort list in place; வரிசைப்படுத்து( ப )
3. எடு (\_\_getitem\_\_) - get element from list at position; எடு( x, 0 ) or  x[0]
4. நீளம் (length) - get number of elements in list; நீளம்( ப )
5. தலைகீழ்( ப ) - reverse order of elements in list, inplace; தலைகீழ்( ப )
6. நீட்டிக்க( ப1 , ப2  ) - extend the list with contents of another list; 
7. நுழைக்க( x, 0, -5 ) - insert into list 'x' at position 0, value -5
8. வை (set item) -  set, i.e. x[0] = pi()

Dict Methods
============


File Methods
============
1. கோப்பை\_திற - file_open - open file to read or write; கோ = கோப்பை\_திற("/proc/cpuinfo"); for writing a file - fp = கோப்பை_திற( "names.txt","w")
2. கோப்பை\_படி - file_read - reads content of file with a object obtained from, and returns a string; see example __filedemo.n__  கோப்பை\_படி( கோ )
3. கோப்பை\_எழுது - write to a file;   கோப்பை_எழுது( fp,வரி )
4. கோப்பை\_மூடு - close file - use object from கோப்பை\_மூடு( கோ )

System Methods
==============
1. date()
2. 
3. 
4. 

Math
====
0. pi
1. sin
2. cos
3. tan
4. sqrt
