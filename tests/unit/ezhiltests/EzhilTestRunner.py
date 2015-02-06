# (C) 2013 Muthiah Annamalai
# 
# This file is part of Ezhil Language project
# 
import os, codecs, sys
import tempfile
from glob import glob

import ezhil
from ezhil import TimeoutException

class TestEzhil:
    """ run a positive test, and make sure the interpreter doesn't gripe.
        currently there is no way to check the output of Ezhil """
    def __init__( self, ezhil_test_code ):
        self.filename = ''        
        self.success = False #was test run successful ?
        self._tested = False
        self.filename = self.create_tmp_file(ezhil_test_code)
        
    def create_tmp_file(self,contents=u""):
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
            ezhil.EzhilFileExecuter( self.filename , False, False )
            self.success = True
        except Exception as ex:
            print("Ezhil Interpreter stopped with the exception ....")            
            print( ex.message, ex.args )
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
    def __init__(self, ezhil_test_code, exception, msg, dbg = False, partial = False ):
        TestEzhil.__init__( self, ezhil_test_code )
        self.exception = exception
        self.message = msg
        self.dbg = dbg
        self.partial = partial
        
    def run( self ):
        """ this class expects to receive an exception on running the Ezhil interpreter,
            and when we match the exception message the test is supposed to pass
        """
        print "\n"*3
        try:
            self._tested = True
            ezhil.EzhilFileExecuter( self.filename , self.dbg, False )
            self.success = False # we expected an exception
        except Exception as ex:
            if self.partial:
                return True
            
            self.success = False # we expected a particular kind of exception
            if self.exception:
                self.success = isinstance( ex, self.exception )
                print(">>>>>>>>>>>> We found an exception \n %s \n"%ex)
            
            if not self.success:
                raise Exception("Expected exception class %s was not found"%(self.exception,ex))
            
            print( u"### EXCEPTION ==> \n %s"%unicode(ex) )
            if self.message:
                self.success = True
                # check multiple messages
                if not isinstance(self.message, list):
                    self.message = [self.message]
                
                for msg in self.message:
                    print self.success
                    print "### testing ",unicode(msg)
                    self.success = self.success and \
                        (( ex.message.find( msg ) >= 0 ) or \
                             len(filter(lambda x: x.find( msg ) >=0, ex.args )) > 0 or unicode(ex).find( msg ) >= 0 )
                    print self.success
            
            if not self.success and not self.partial:
                print "######## TEST FAILED #############"
                print self.success,self.partial
                print(u"ACTUAL == %s"%unicode(ex))
                print(u"EXPECTED == %s"%unicode(self.message))
                raise Exception(u"Expected message %s was not found. We found message %s"%(self.message,unicode(ex)))            
            return self.success
        raise Exception(u"Expected message %s was not found.",str(self.exception))

    @staticmethod
    def create_and_test_spl( code, exception, msg):
        with TestEzhilException(code,exception,msg,True) as tst:
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
            print("Ezhil Interpreter stopped with the exception ....")
            print( ex.message, ex.args )
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
        print("\n******* beginning to run Ezhil test with timeout = %d(s)*******"%(self.timeout))
        self._tested = True
        self.success = False
        try:
            #redirect output = True, when you need a TIMEOUT
            ezhil.EzhilFileExecuter(self.filename,debug=False,redirectop=True,TIMEOUT=self.timeout)
        except TimeoutException as tex:
            self.success = True #expected to raise an exception
        except Exception as ex:
            print("Ezhil Interpreter stopped with the exception ....")
            print( ex.message, ex.args )
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
