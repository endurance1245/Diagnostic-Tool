from flask_cors import CORS
from blueprint.apis import dag_blueprint
from blueprint.test_html import blueprint_html
import flask
app = flask.Flask(__name__)
app.register_blueprint(dag_blueprint)
app.register_blueprint(blueprint_html)
app.secret_key = "diagnostictoolcapmaign12345677654321"

CORS(app)
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
