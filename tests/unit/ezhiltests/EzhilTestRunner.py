import os
import tempfile

class TestEzhil:
    """ run a positive test, and make sure the interpreter doesn't gripe.
        currently there is no way to check the output of Ezhil """
    def __init__( self, ezhil_test_code ):
        self.filename = ''
        self.handle = -1
        self.success = False #was test run successful ?

        # dump stuff into a file
        [self.handle,self.filename] = tempfile.mkstemp()
        os.write( self.handle, ezhil_test_code )
        os.close( self.handle )
        
    def __del__( self ):
        # destructor
        os.unlink( self.filename )
        
    def run( self ):
        """ run the interpreter """
        try:
            ezhil.EzhilFileExecuter( self.filename , False, True )
            self.success = True
        except ex:
            print("Ezhil Interpreter stopped with the exception ....")
            print( ex )
            raise ex
        finally:
            pass
        return self.success
    

class TestEzhilException( TestEzhil ):
    def __init__(self, ezhil_test_code, exception, msg ):
        super(TestEzhil,self).__init__( ezhil_test_code )
        self.exception = exception
        self.message = msg

    def run( self ):
        """ this class expects to receive an exception on running the Ezhil interpreter,
            and when we match the exception message the test is supposed to pass
        """
        try:
            super( TestEzhil, self ).run( )
            self.success = False # we expected an exception
        except ex:
            self.success = True
            if self.exception:
                self.success = isinstance( ex, self.exception )
                print "We found an exception %s"%ex
            
            if not self.success:                
                raise Exception("Expected exception class %s was not found"%(self.exception,ex))
            
            if not self.message:
                self.success = ( ex.message.find( self.message ) >= 0 )
                
            
            if not self.success:
                raise Exception("Expected message %s was not found. We found message %s"%(self.message,ex.message))
            return self.success
        
            
