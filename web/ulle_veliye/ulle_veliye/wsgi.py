"""
WSGI config for ulle_veliye project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ulle_veliye.settings")

application = get_wsgi_application()
