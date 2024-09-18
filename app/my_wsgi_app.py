import re
from typing import Callable, List, Tuple, Optional
from wsgiref.types import WSGIEnvironment, StartResponse

class MyWsgiApp:

    def __init__(self, app_name: str):
        self.name = app_name
        self.static_urls = dict()
        self.dynamic_urls = dict()

    def match_dynamic_url(self, endpoint: str) -> Tuple[Optional[Callable], List[str]]:

        for path, func in self.dynamic_urls.items():

            pattern = re.sub(r'<(\w+)>', r'(?P<username>\\w+)', path)
            match = re.match(f"^{pattern}$", endpoint)
            if match:
                return func, list(match.groups())

        return None, []

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> List[bytes]:
        endpoint = environ.get('PATH_INFO')

        if endpoint == '/favicon.ico':
            start_response('204 No Content', [])

            return [b'']

        if endpoint in self.static_urls:
            start_response('200 OK', [('Content-Type', 'application/json')])
            func = self.static_urls[endpoint]
            return [bytes(func(), 'utf-8')]

        match, params = self.match_dynamic_url(endpoint)
        if match:
            start_response('200 OK', [('Content-Type', 'application/json')])
            func = match
            result = func(*params)

            return [bytes(result, 'utf-8')]
        else:
            start_response('404 Not Found', [])
            return [b'This page doesn\'t exist']

    def route(self, path: str):

        if '<' in path and '>' in path:
            def decorator(func: Callable):
                self.dynamic_urls[path] = func
                return func
        else:
            def decorator(func: Callable):
                self.static_urls[path] = func
                return func
        return decorator

    def run(self, host: str = 'localhost', port: int = 8080):
        try:
            from wsgiref.simple_server import make_server
            app = make_server(host, port, self)
            print(f'Serving on port {port}...')
            app.serve_forever()
        except KeyboardInterrupt:
            print('Goodbye.')
