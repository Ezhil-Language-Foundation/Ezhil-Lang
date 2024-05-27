# (C) 2013 Muthiah Annamalai
# 
# This file is part of Ezhil Language project
# 
import os
import sys
import codecs
import tempfile
from glob import glob
import traceback

import ezhil
import unittest
from ezhil import TimeoutException

PYTHON3 = (sys.version[0] == '3')
if PYTHON3:
    str = str

class QuietTestCase(unittest.TestCase):
    """ run quiet unit-tests without verbosity """
    def __init__(self,*args):
        unittest.TestCase.__init__(self,*args)
        self.debug = False
    
    def get_filename(self):
        raise Exception("Abstract method of class")
        
    def setUp(self):
        self.old = sys.stdout
        self.olderr = sys.stderr
        sys.stdout = codecs.open(self.get_filename(),'w','utf-8')
        sys.stderr = codecs.open("err_"+self.get_filename(),'w','utf-8')
    
    def tearDown(self):
        sys.stdout.close()
        sys.stderr.close()

        sys.stdout = self.old
        sys.stdout = self.olderr

        if self.debug:
            print("############### STDOUT #################")
            fp = codecs.open(self.get_filename(),"r","utf-8")
            print((fp.read()))
            fp.close()
            print("################ STDERR #################")
            fp = codecs.open("err_"+self.get_filename(),"r","utf-8")
            print((fp.read()))
            fp.close()
            print("################ END QUIET TEST ##########")
        
        os.unlink(self.get_filename())
        os.unlink("err_"+self.get_filename())
        
class TestEzhil:
    """ run a positive test, and make sure the interpreter doesn't gripe.
        currently there is no way to check the output of Ezhil """
    def __init__( self, ezhil_test_code ):
        self.filename = ''        
        self.success = False #was test run successful ?
        self._tested = False
        self.filename = self.create_tmp_file(ezhil_test_code)
        self.debug = False
        
    def create_tmp_file(self,contents=""):
        # dump stuff into a unique temporary file - refactor to write multiple
        # files from the class.
        handle = -1
        [handle,filename] = tempfile.mkstemp()
        os.close( handle )
        fp = codecs.open( filename, 'w', 'utf-8')
        fp.write( contents )
        fp.close(  )
        return filename
    
    def __enter__(self):
        return self
    
    def __exit__( self, *args ):
        pass
    
    def __del__( self ):
        # destructor - delete temporary file
        os.unlink( self.filename )
        
    def __str__(self):
        if ( self._tested ):
            return "******* test completed with status "+str(self.success)+" *********"
        return "******* test not yet run ********"
        
    def run( self ):
        """ run the interpreter """
        print("\n******* beginning to run Ezhil test *******")
        self._tested = True
        try:
            ezhil.EzhilFileExecuter( file_input = self.filename , debug=False, redirectop=False )
            self.success = True
        except Exception as ex:
            traceback.print_stack()
            print("Ezhil Interpreter stopped with the exception ....")            
            print(( ex.message, ex.args ))
            raise ex
        finally:
            print("********* completed Ezhil test *********")
            pass
        return self.success
    
    @staticmethod
    def create_and_test( code ):        
        with TestEzhil(code) as tst:
            flag = tst.run()
            print(tst)
        return flag
    
class TestEzhilException( TestEzhil ):
    """ check if the Ezhil Interpreter raises an exception of same class as @exception
    while running the @ezhil_test_code; you can also check for message @msg being contained
    in the exception. Empty (None) values for either argument will bypass the check. Not checking
    either will result in default error """
    def __init__(self, ezhil_test_code, exception, msg, debug = False, partial = False, safe_mode=False ):
        TestEzhil.__init__( self, ezhil_test_code )
        self.exception = exception
        self.message = msg
        self.debug = debug
        self.partial = partial
        self.safe_mode = safe_mode
        
    def run( self ):
        """ this class expects to receive an exception on running the Ezhil interpreter,
            and when we match the exception message the test is supposed to pass
        """
        print(("\n"*3))
        try:
            self._tested = True
            ezhil.EzhilFileExecuter( file_input=self.filename , debug=self.debug, redirectop=False, TIMEOUT=None,safe_mode=self.safe_mode )
            self.success = False # we expected an exception
        except Exception as ex:
            if self.partial:
                return True
            
            self.success = False # we expected a particular kind of exception
            if self.exception:
                self.success = isinstance( ex, self.exception )
                if ( self.debug ): print((">>>>>>>>>>>> We found an exception \n %s \n"%ex))
            
            if not self.success:
                traceback.print_stack()
                raise Exception("Expected exception class %s was not found; instead %s was received."%(self.exception,ex))
            
            if ( self.debug ): print(( "### EXCEPTION ==> \n %s"%str(ex) ))
            if self.message:
                self.success = True
                # check multiple messages
                if not isinstance(self.message, list):
                    self.message = [self.message]
                
                for msg in self.message:
                    if ( self.debug ): print((self.success))
                    if ( self.debug ): print(("### testing ",str(msg)))
                    self.success = self.success and \
                        (( str(ex).find( msg ) >= 0 ) or \
                             len([x for x in ex.args if x.find( msg ) >=0]) > 0 or str(ex).find( msg ) >= 0 )
                    if ( self.debug ): print((self.success))
            
            if not self.success and not self.partial:
                print("######## TEST FAILED #############")
                print((self.success,self.partial))
                print(("ACTUAL == %s"%str(ex)))
                print(("EXPECTED == %s"%str(self.message)))
                raise Exception("Expected message %s was not found. We found message %s"%(self.message,str(ex)))            
            return self.success
        raise Exception("Expected message %s was not found.",str(self.exception))

    @staticmethod
    def create_and_test_spl_safe_mode( code, exception, msg):
        with TestEzhilException(code,exception,msg,debug=False,safe_mode=True) as tst:
            flag = tst.run()
            print(tst)
        return flag
        
    @staticmethod
    def create_and_test_spl( code, exception, msg):
        with TestEzhilException(code,exception,msg,debug=False) as tst:
            flag = tst.run()
            print(tst)
        return flag
    @staticmethod
    def create_and_test( code, exception, msg,partial=False ):
        with TestEzhilException(code,exception,msg,partial=partial) as tst:
            flag = tst.run()
            print(tst)
        return flag 

class TestInteractiveEzhil(TestEzhil):
    """ run a positive test, and make sure the CLI interpreter doesn't gripe.
        currently there is no way to check the output of Ezhil."""
    def __init__( self, ezhil_test_code ):
        TestEzhil.__init__( self, ezhil_test_code )
        self.actual_stdin = sys.stdin;
        self.actual_stdout = sys.stdout;
        sys.stdin = open(self.filename)
        #self.out_filename = self.create_tmp_file() #create a empty file
        #sys.stdout = codecs.open(self.filename,"w","utf-8")
    
    def __del__( self ):
        TestEzhil.__del__(self)
        sys.stdin = self.actual_stdin
    
    def run( self ):
        """ run the interpreter """
        print("\n******* beginning to run Ezhil test *******")
        self._tested = True
        try:
            # re-routed stdin will feed the interpreter input
            ezhil.start()
            self.success = True
        except Exception as ex:
            traceback.print_stack()            
            if ( self.debug ): print("Ezhil Interpreter stopped with the exception ....")
            if ( self.debug ): print(( ex.message, ex.args ))
            raise ex
        finally:
            print("********* completed Ezhil test *********")
            pass
        return self.success
    
    @staticmethod
    def create_and_test( code ):        
        with TestInteractiveEzhil(code) as tst:
            flag = tst.run()
            print(tst)
        return flag

class TestTimeoutEzhil(TestEzhil):
    """ run a positive test, to ensure the web interface evaluator 
    can timeout after the given number of seconds."""
    
    def __init__( self, ezhil_test_code, timeout = 20 ):
        TestEzhil.__init__( self, ezhil_test_code )
        self.timeout = timeout

    def run( self ):
        """ run the interpreter """
        print(("\n******* beginning to run Ezhil test with timeout = %d(s)*******"%(self.timeout)))
        self._tested = True
        self.success = False
        try:
            #redirect output = True, when you need a TIMEOUT
            ezhil.EzhilFileExecuter(self.filename,debug=False,redirectop=False,TIMEOUT=self.timeout)
        except TimeoutException as tex:
            self.success = True #expected to raise an exception
        except Exception as ex:
            if ( self.debug ): print("Ezhil Interpreter stopped with the exception ....")
            if ( self.debug ): print(( ex.message, ex.args ))
            raise ex
        finally:
            print("********* completed Ezhil test *********")
            # cleanup process files
            for fileName in glob("*.out"):
                os.unlink( fileName )
            pass
        return self.success
    
    @staticmethod
    def create_and_test( code, timeout ):        
        with TestTimeoutEzhil(code,timeout) as tst:
            flag = tst.run()
            print(tst)
        return flag
