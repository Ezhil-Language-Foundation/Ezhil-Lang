# (C) 2013 Muthiah Annamalai
# 
# This file is part of Ezhil Language project
# 
import os
import tempfile

import ezhil

class TestEzhil:
    """ run a positive test, and make sure the interpreter doesn't gripe.
        currently there is no way to check the output of Ezhil """
    def __init__( self, ezhil_test_code ):
        self.filename = ''
        self.handle = -1
        self.success = False #was test run successful ?
        self._tested = False
        
        # dump stuff into a file
        [self.handle,self.filename] = tempfile.mkstemp()
        os.write( self.handle, ezhil_test_code )
        os.close( self.handle )

    def __enter__(self):
        return self
    
    def __exit__( self, *args ):
        pass
    
    def __del__( self ):
        # destructor
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
    def __init__(self, ezhil_test_code, exception, msg ):
        TestEzhil.__init__( self, ezhil_test_code )
        self.exception = exception
        self.message = msg
        
    def run( self ):
        """ this class expects to receive an exception on running the Ezhil interpreter,
            and when we match the exception message the test is supposed to pass
        """
        try:
            TestEzhil.run( self )
            self.success = False # we expected an exception
        except Exception as ex:
            self.success = False
            if self.exception:
                self.success = isinstance( ex, self.exception )
                print("We found an exception %s"%ex)
            
            if not self.success:
                raise Exception("Expected exception class %s was not found"%(self.exception,ex))
            
            print(ex)
            if self.message:
                self.success = True
                # check multiple messages
                for msg in self.message:
                    self.success = self.success and \
                        (( ex.message.find( msg ) >= 0 ) or \
                             len(filter(lambda x: x.find( msg ) >=0, ex.args )) > 0 )
            
            if not self.success:
                raise Exception("Expected message %s was not found. We found message %s"%(self.message,ex.message))
            
            return self.success

    @staticmethod
    def create_and_test( code, exception, msg ):
        with TestEzhilException(code,exception,msg) as tst:
            flag = tst.run()
            print(tst)
        return flag
