# run.py
from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from app import create_app

app = create_app()

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0')