import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'cloudendar.settings'

import django.core.handlers.wsgi

application = django.core.handler.wsgi.WSGIHandler()
