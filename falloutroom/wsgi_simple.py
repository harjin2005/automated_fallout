import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'falloutroom.settings_production')

application = get_wsgi_application()

# Health check endpoint
def simple_app(environ, start_response):
    if environ['PATH_INFO'] == '/health':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'OK']
    else:
        return application(environ, start_response)
