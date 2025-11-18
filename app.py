from flask import *
import datetime
from models.models import *
from routes.user_routes import user_bp
from routes.cidade_routes import city_bp
from routes.post_routes import post_bp
from routes.comentarios_routes import comentarios_bp


app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False

version = "v1"

#################################################
app.register_blueprint(user_bp, url_prefix = f"/api/{version}/user") # v1
app.register_blueprint(city_bp, url_prefix = f"/api/{version}/cidade") # v1
app.register_blueprint(post_bp, url_prefix = f"/api/{version}/post") # v1
app.register_blueprint(comentarios_bp, url_prefix = f"/api/{version}/comentarios") # v1

#################################################



@app.route('/')
def index():

    return 'No Ar...'


if __name__ == '__main__':
    app.run(debug=True)
