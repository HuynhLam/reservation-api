from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from reservation.resources import app as api
from example_client.client import app as client

application = DispatcherMiddleware(api, {
    '/example_client': client
})
if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)