from app import create_app
from gevent import monkey
from gevent.pywsgi import WSGIServer

# Patch all standard modules to be cooperative
monkey.patch_all()

app = create_app()

if __name__ == '__main__':
    # Use Gevent's WSGI server
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
