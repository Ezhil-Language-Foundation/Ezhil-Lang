Ezhil-Lang
==========

[![Build Status](https://travis-ci.org/Ezhil-Language-Foundation/Ezhil-Lang.png)](https://travis-ci.org/Ezhil-Language-Foundation/Ezhil-Lang)

Introduction
------------

```text
எழில்: தமிழ் நிரலாக்க மொழி; முதன்முறை கணிப்பொறி நிரல் எழுதுகிற 
தமிழ் மாணவர்களுக்கு இது உதவும்.

எழில் மொழி - தமிழ் குழந்தைகளும், பள்ளி மற்றும் கல்லூரி மாணவர்களும் எளிதில் கற்றுக்கொள்ளும் வகையில் உருவாக்கப்பட்ட ஒரு கணினி நிரலாக்க மொழி.
எழில் ஒரு செயல்முறை நோக்கு - (Imperative ) கணினி மொழி. இதை ரூபி , பைதான் போன்ற மொழிகளின் நடையில் அமைக்கபட்டது.
எழில் மொழியில் நிபந்தனை கட்டளைகள், மடக்கு கட்டளைகள் என்றும்  எழுதலாம்; இதில் செயல்பாடுகள், செயல்குருகள் என்று கணினி நிரல்களை 
பிரிக்கலாம். எழில்  மென்பொருள் அத்தியாயம்  எண்  v0.8. பைதான் மொழி அடிப்படையில் உருவாக்கப்பட்டது.

Ezhil-Lang : (Ezhil, is a fun Tamil programming language for K-12) Ezhil is 
a procedural language with dynamic types, like Ruby/Python. Ezhil has a 
pascal-like syntax, with for-end, while-end, if-elseif-else-end statements,
break, continue and def-end for defining functions. Ezhil language is 
implemented in a handwritten scanner and parser using the Python programming 
language. Latest version of Ezhil-Language is v0.8.
```

Motivations
-----------

(English) ஆங்கிலம் அறியாதவர்கள் கணிப்பொறியை இயக்க உதவும்
எழில் உங்களுக்கு முதன்முறையாக நிரல்கள் எழுத உதவும்
திறமூல (Open Source) மென்பொருள்.
(Free) இலவசமாக பயன்படுத்தலாம்

Write Code in Tamil!
English language is not a pre-requisite
Write your first program in Ezhil
Free as in Open source

எழில் மொழியை எப்படி பயன்படுத்துவது (Usage)
-----------------------------------------

Currently Ezhil language is under development, and a little rough around the
edges. You may still try it out, by going to the git source repository,

```bash
cd ./ezhil-lang/
```

and then use one of the three modes,

1. Batch Mode
2. Interactive Mode
3. Web Mode

மொத்தமாக எழில் நிரல்களை இயக்க  | Batch Mode
-----------------------------------------------

```bash
$ ezhili ./ezhil_tests/hello.n 
பதிப்பி "வணக்கம்!"
பதிப்பி "எழில் அழைக்கிறது"

வணக்கம்!
எழில் அழைக்கிறது
```

where you should see the output above. For usage, try,

```bash
$ ezhili --help
usage: எழில் [-h] [-debug] [-tamilencoding TAMILENCODING] [-profile] [-stdin]
             [-stacksize STACKSIZE]
             [files [files ...]]

positional arguments:
  files

optional arguments:
  -h, --help            show this help message and exit
  -debug                enable debugging information on screen
  -tamilencoding TAMILENCODING
                        option to specify other file encodings; supported
                        encodings are TSCII, and UTF-8
  -profile              profile the input file(s)
  -stdin                read input from the standard input
  -stacksize STACKSIZE  default stack size for the Interpreter
```

உரையாடும் பானியில்  எழில் | Interactive Mode
-------------------------------------------

```bash
$ ezhili
எழில் 1>> 1 + 5
6
எழில் 2>> பதிப்பி "வணக்கம்! எழில் அழைக்கிறது"
வணக்கம்! எழில் அழைக்கிறது
எழில் 3>> exit()
```

வலை உலாவி வழி பயன்பாடு | Web Mode
------------------------------------

You can also run ezhil as a web service by launching the webserver,
$ ./webserver.sh
and open the webpage, <http://localhost:8080> in google-chrome or firefox,
to enter your program and evaluate it.

பைதான்  மொழியில்  இருந்து  பயன்படுத்த | Python Library
------------------------------------------------------

Ezhil Tamil programming Python package can be invoked from within the Python shell or IDLE on Windows, by simply typing,

```python
>>> import ezhil
>>> ezhil.start()
```

But to do all of this, you need to build and install the Python packages from this source, by,

```bash
cd ezhil-lang/ && python setup.py build
cd ezhil-lang/ && python setup.py install
```

Installation from Python Package Index is also recommended, following the commands,

```bash
pip install ezhil
```

மேலும்  எழில்  மொழியிற்கு பங்களிக்க | Learn more, and contribute
-------------------------------------------------------------

'''Rosetta Code''', the wiki platform for sharing standard algorithms, in
many programming languages, now hosts several algorithms in Ezhil.
You can find all of Ezhil programs there via <http://rosettacode.org/wiki/Category:Ezhil>

தரவிறக்கம் செய்ய | Download Ezhil
--------------------------------

If you would like to tryout the code, all you need
is a python interpreter, and the code from
<https://github.com/Ezhil-Language-Foundation/Ezhil-Lang.git>

Interesting features include support for recursion,
and an interactive interpreter. Ezhil supports a Turtle module
for simple on-screen graphics, similar to LOGO language from 1960s.

மேற்கோள்கள்  | References
-------------------------

Read Wikipedia article(s) on Ezhil,

1. (Tamil) <http://bit.ly/16MgU6U>
2. (English) <http://en.wikipedia.org/wiki/Ezhil_%28programming_language%29>

Scholarly articles on Ezhil include,

1. M. Annamalai, "Ezhil : A Tamil Programming Language," (2009). <http://arxiv.org/abs/0907.4960>
2. -do-, "Invitation to Ezhil: A Tamil Programming Language for Early Computer-Science Education," (2013). <http://arxiv.org/abs/1308.1733>

விருதுகள் | Awards
-----------------

சுந்தர ராமசாமி நினைவாக காலச்சுவடு அறக்கட்டளையால் நிறுவப்பட்ட‘கணிமை விருது’ 2014 ஆம் ஆண்டு முனைவர் முத்தையா அண்ணாமலைக்கு  வழங்கப்பட்டது.
அண்ணாமலை அமெரிக்காவில் பாஸ்டன் மாநிலத்தில் வாழ்ந்து வருகிறார். தனது எட்டு ஆண்டு உழைப்பில் ‘எழில்’ என்ற பெயரில் ஒரு கணினி
மொழியை உருவாக்கியுள்ளார். ஓர் ஆங்கிலச் சொல் கூட உபயோகிக்காது, தமிழ் மட்டுமே அறிந்தவர்கள்கூட இம்மொழியைப் பயன்படுத்த முடியும்.
இவ்வகை முயற்சிகள் இதற்குமுன் எடுக்கப்பட்டிருந்தாலும் அவை அதன் அடிப்படையைத் தாண்டி முன்னேறவில்லை என்பதும்,
இதுவே இவ்வாறாகத் தமிழுக்காக உருவாக்கப்பட்ட முதற் கணினி மொழி என்பதும் குறிப்பிட வேண்டியது.
இது இலவசமாகக் கிடைக்கிறது என்பது இதன் சிறப்பம்சம்.

முத்தையாவின் கணிமைச் சேவையைப் பாராட்டி 2014ஆம் ஆண்டுக்கான விருதை முனவர் வெங்கட்ரமணன் வழங்கினார்.

1. <http://www.kalachuvadu.com/issue-187/page71.asp>

Development notes
-----------------

Ezhil project is hosted on Thamizaa project, as well on Ezhil Language Foundation github pages.

Docker image building notes
---------------------

```bash
# from project root run the following to generate docker image
docker build -t ezhil-site .
```

Run using Docker run
--------------------

```bash 
# To run the server using docker run 
docker run \
--name ezhil-container \
-p 8080:8080 \
-v $(pwd)/dynamic/dist:/web \
-v $(pwd)/ezhil:/web/ezhil  \
ezhil-site
```

Run using Docker Compose
--------------

```bash
# using docker compose use the following from the project root
docker-compose up -d 
```

Apache Virtual host configuration
---------------------------------

```apache
# apache virtual host configuration
# change according to you setup 
<VirtualHost *:80>
    ServerName ezhil.kaniyam.ca.local

    ProxyPreserveHost On

    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/

    ErrorLog ${APACHE_LOG_DIR}/ezhil.kaniyam.error.log
    CustomLog ${APACHE_LOG_DIR}/ezhil.kaniyam.access.log combined
</VirtualHost>

```

Adding as a systemd Service
----------------------------
```bash 
# Install docker as a service first 
sudo systemctl enable docker 
sudo systemctl start docker 
# Update working directory with actual working directory for triggering service check for permission issues
sed -i "s|^WorkingDirectory=.*|WorkingDirectory=$(pwd)|" "ezhil-site.service"
# Copy ezhil-site.service file to install systemd service
sudo cp ./ezhil-site.service /etc/systemd/system/ezhil-site.service
# After copying the service file update daemon 
sudo systemctl daemon-reload
# Enable and start service 
sudo systemctl enable ezhil-site.service
sudo systemctl start ezhil-site.service
# Enable systemctl status 
sudo systemctl status ezhil-site.service
# Running good then all is fine 
# Otherwise 
jounalctl -xe
```
