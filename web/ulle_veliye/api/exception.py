# -*- coding: utf-8 -*-

import sys
from django import http


class HandleExceptionsMiddleware(object):
    def process_exception(self, request, exception):
        print("exception has been raised", file=sys.stderr)
        # Get the exception info now, in case another exception is thrown later.
        if isinstance(exception, http.Http404):
            return self.handle_404(request, exception)
        else:
            print(exception)
            return self.handle_500(request, exception)
