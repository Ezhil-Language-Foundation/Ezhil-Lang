#!/usr/bin/env python

# This file is part of Python-Twitter example @ https://github.com/bear/python-twitter
# modified for being suitable to Ezhil-Language project needs.
# See file COPYING.PYTHON-TWITTER in the source directory for the terms of use.
# Typical use would be to run this program in a cron job.

'''Post a message to twitter'''

__author__ = ['dewitt@google.com','ezhillang@gmail.com']
_DEBUG = True
try:
    import configparser
except ImportError as _:
    import ConfigParser as configparser
import json
import getopt
import os
import sys
import twitter
import codecs
import random
from iyakki import MPRunner

USAGE = '''Usage: tweet [options] message

  This script posts a message to Twitter.

  Options:

    -h --help : print this help
    --consumer-key : the twitter consumer key
    --consumer-secret : the twitter consumer secret
    --access-key : the twitter access token key
    --access-secret : the twitter access token secret
    --encoding : the character set encoding used in input strings, e.g. "utf-8". [optional]

  Documentation:

  If either of the command line flags are not present, the environment
  variables TWEETUSERNAME and TWEETPASSWORD will then be checked for your
  consumer_key or consumer_secret, respectively.

  If neither the command line flags nor the environment variables are
  present, the .tweetrc file, if it exists, can be used to set the
  default consumer_key and consumer_secret.  The file should contain the
  following three lines, replacing *consumer_key* with your consumer key, and
  *consumer_secret* with your consumer secret:

  A skeletal .tweetrc file:

    [Tweet]
    consumer_key: *consumer_key*
    consumer_secret: *consumer_password*
    access_key: *access_key*
    access_secret: *access_password*

'''


def PrintUsageAndExit():
    print USAGE
    sys.exit(2)


def GetConsumerKeyEnv():
    return os.environ.get("TWEETUSERNAME", None)


def GetConsumerSecretEnv():
    return os.environ.get("TWEETPASSWORD", None)


def GetAccessKeyEnv():
    return os.environ.get("TWEETACCESSKEY", None)


def GetAccessSecretEnv():
    return os.environ.get("TWEETACCESSSECRET", None)


class TweetRc(object):
    def __init__(self):
        self._config = None

    def GetConsumerKey(self):
        return self._GetOption('consumer_key')

    def GetConsumerSecret(self):
        return self._GetOption('consumer_secret')

    def GetAccessKey(self):
        return self._GetOption('access_key')

    def GetAccessSecret(self):
        return self._GetOption('access_secret')

    def _GetOption(self, option):
        try:
            return self._GetConfig().get('Tweet', option)
        except:
            return None

    def _GetConfig(self):
        if not self._config:
            self._config = configparser.ConfigParser()
            self._config.read(os.path.expanduser('~/.tweetrc'))
        return self._config

class LastReply:
    FILENAME="ezhilbot.json"
    
    @staticmethod
    def get_id():
        with open(LastReply.FILENAME,"r") as fp:
            data = json.loads(fp.read())
        return int(data["refid"])
    
    @staticmethod
    def set_id(id):
        with open(LastReply.FILENAME,"w") as fp:
            datas = json.dumps({"refid":id})
            print(datas)
            fp.write(datas)
            fp.close()
        return
    
    @staticmethod
    def bootstrap():
        try:
            os.stat(LastReply.FILENAME)
        except Exception as ioe:
            LastReply.set_id(-1)

def escape_html(code):
    html_escape_table = {
            u"&amp;":u"&",
            u"&quot;":u'"',
            u"&apos;":u"'",
            u"&gt;":u">",
            u"&lt;":u"<",
            }
    for k,v in html_escape_table.items():
        code = code.replace(k,v)
    return code

def main():
    try:
        shortflags = 'h'
        longflags = ['help', 'consumer-key=', 'consumer-secret=',
                     'access-key=', 'access-secret=', 'encoding=']
        opts, args = getopt.gnu_getopt(sys.argv[1:], shortflags, longflags)
    except getopt.GetoptError as ioe:
         PrintUsageAndExit()
    consumer_keyflag = None
    consumer_secretflag = None
    access_keyflag = None
    access_secretflag = None
    encoding = None
    for o, a in opts:
        if o in ("-h", "--help"):
            PrintUsageAndExit()
        if o in ("--consumer-key"):
            consumer_keyflag = a
        if o in ("--consumer-secret"):
            consumer_secretflag = a
        if o in ("--access-key"):
            access_keyflag = a
        if o in ("--access-secret"):
            access_secretflag = a
        if o in ("--encoding"):
            encoding = a
    rc = TweetRc()
    consumer_key = consumer_keyflag or GetConsumerKeyEnv() or rc.GetConsumerKey()
    consumer_secret = consumer_secretflag or GetConsumerSecretEnv() or rc.GetConsumerSecret()
    access_key = access_keyflag or GetAccessKeyEnv() or rc.GetAccessKey()
    access_secret = access_secretflag or GetAccessSecretEnv() or rc.GetAccessSecret()
    if not consumer_key or not consumer_secret or not access_key or not access_secret:
        PrintUsageAndExit()
    api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                      access_token_key=access_key, access_token_secret=access_secret,
                      input_encoding=encoding)
    LastReply.bootstrap()
    id = LastReply.get_id()
    kwargs = {}
    if id > 0:
        kwargs = {"since_id":id}
    rep = api.GetMentions(**kwargs)
    
    for r in rep:
        print("Reply : id=%s,text=%s,user=%s"%(r.id,r.text,r.user.screen_name))
        code_msg = r.text
        user = r.user.screen_name
        try:
            code_msg = code_msg.replace(u"@ezhillang","")
            code_msg = escape_html(code_msg)
            process_ezhil(r.id,api,code_msg,user)
        except Exception as ioe:
            print("Executing reply %s failed\n"%ioe)
        if id < r.id:
            id = r.id
    else:
        print("Nothing since last tweet of ID=%d"%LastReply.get_id())
    LastReply.set_id(id)
    
def process_ezhil(id,api,code_msg,user):
    if user.find("ezhillang") >= 0:
        print("Skipping : %s"%user)
        return
    try:
        srcfilename = "tmpcode_%d.n"%random.randint(0,10000)
        with codecs.open(srcfilename,"w","UTF-8") as fp:
            fp.write(code_msg)
        
        runner = MPRunner(timeout=3) #run for 3s max.
        runner.run(srcfilename)
        runner.report()
        if not runner.is_success:
            status = api.PostUpdate(u"@%s : code failed execution for id=%d!"%(user,id))
            print(u"%s just posted: %s" % (status.user.name, status.text))
            return
        message = unicode(runner)
        message = u" ".join([u'@'+user,message])
        
        rev = []
        # section in chunks of 140
        for part in range(0,len(message),140):
            rev.append(message[part:min(part+140,len(message))])
        rev.reverse()
        
        for r in rev:
            status=api.PostUpdate(r)
            print(u"%s just posted: %s" % (status.user.name, status.text))
        
    except UnicodeDecodeError:
        print(u"Your message could not be encoded.  Perhaps it contains non-ASCII characters? ")
        print(u"Try explicitly specifying the encoding with the --encoding flag")
        return
    finally:
        if not _DEBUG: os.unlink(srcfilename)
    print(u"%s just posted: %s" % (status.user.name, status.text))

if __name__ == "__main__":
    main()
