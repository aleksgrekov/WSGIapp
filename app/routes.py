import json
from my_wsgi_app import MyWsgiApp


application = MyWsgiApp(__name__)


@application.route("/hello")
def say_hello():
    return json.dumps({"response": "Hello, world!"}, indent=4)


@application.route("/hello/<name>")
def say_hello_with_name(name: str):
    return json.dumps({"response": f"Hello, {name}!"}, indent=4)

